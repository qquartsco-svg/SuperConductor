"""
uncertainty_quantification.py — 불확실성 정량화  (v1.0)

방법론
──────
1. Monte Carlo 시뮬레이션 (중심극한정리 기반)
   파라미터 불확실성 → 출력 분포 → 통계

2. 제조 산포 모델링
   가우시안 분포: X ~ N(μ, σ²)
   σ_rel = σ/μ (상대 표준편차)
   제조 공차: Jc ±15%, d_filament ±5%, RRR ±30%

3. 신뢰 구간 추정
   95% CI: [mean − 1.96σ, mean + 1.96σ]
   5th percentile (P05), 95th percentile (P95)

4. 신뢰도 (Reliability)
   P(Y > Y_limit) = 안전 마진 초과 확률
   P(Y < Y_safe) = 설계 기준 충족 확률

참조
──────
Saltelli et al. (2004) "Sensitivity Analysis in Practice", Wiley
Haldar & Mahadevan (2000) "Probability, Reliability, and Statistical Methods"

stdlib only — no external dependencies (math, random 만 사용).
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    UncertaintyReport,
)


# ─────────────────────────────────────────────────────────────────────────────
# 박스-뮬러 정규 난수 (stdlib only)
# ─────────────────────────────────────────────────────────────────────────────

def _normal_sample(mu: float, sigma: float, rng: random.Random) -> float:
    """Box-Muller 정규 분포 샘플링."""
    u1 = max(1e-15, rng.random())
    u2 = rng.random()
    z  = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z


def _truncated_normal(
    mu: float,
    sigma: float,
    lo: float,
    hi: float,
    rng: random.Random,
    max_tries: int = 20,
) -> float:
    """절단 정규분포 (물리적으로 유효한 범위로 제한)."""
    for _ in range(max_tries):
        x = _normal_sample(mu, sigma, rng)
        if lo <= x <= hi:
            return x
    return mu  # fallback


# ─────────────────────────────────────────────────────────────────────────────
# 통계 계산
# ─────────────────────────────────────────────────────────────────────────────

def _statistics(samples: List[float]) -> Dict[str, float]:
    """기본 통계: mean, std, P05, P50, P95, reliability_above_zero."""
    n = len(samples)
    if n == 0:
        return {}
    mean = sum(samples) / n
    var  = sum((x - mean) ** 2 for x in samples) / max(1, n - 1)
    std  = math.sqrt(var)
    sorted_s = sorted(samples)
    p05 = sorted_s[max(0, int(0.05 * n) - 1)]
    p50 = sorted_s[int(0.50 * n) - 1]
    p95 = sorted_s[min(n - 1, int(0.95 * n))]
    cv  = std / abs(mean) if abs(mean) > 1e-15 else 0.0
    return {
        "mean": mean,
        "std":  std,
        "cv":   cv,   # 변동계수 (coefficient of variation)
        "P05":  p05,
        "P50":  p50,
        "P95":  p95,
    }


def _reliability(samples: List[float], threshold: float, above: bool = True) -> float:
    """신뢰도 P(X > threshold) 또는 P(X < threshold)."""
    if not samples:
        return 0.0
    if above:
        return sum(1 for x in samples if x > threshold) / len(samples)
    return sum(1 for x in samples if x < threshold) / len(samples)


# ─────────────────────────────────────────────────────────────────────────────
# Jc Monte Carlo
# ─────────────────────────────────────────────────────────────────────────────

def mc_jc_uncertainty(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    n_samples: int = 500,
    seed: int = 42,
    jc_rel_sigma: float = 0.15,   # Jc ±15%
    temp_abs_sigma: float = 0.2,  # 온도 ±0.2 K
    field_rel_sigma: float = 0.02, # 자기장 ±2%
) -> Dict[str, float]:
    """Jc 불확실성 Monte Carlo 분석.

    파라미터 산포 → Jc 분포 → 통계 반환
    """
    rng = random.Random(seed)
    samples: List[float] = []

    jc_ref  = material.jc_a_per_mm2_77k
    t_op    = cryo.operating_temp_k
    b_op    = design.target_field_t
    tc_k    = material.tc_k
    bc2_t   = material.bc2_t
    aniso   = material.anisotropy

    for _ in range(n_samples):
        jc_s  = _truncated_normal(jc_ref,  jc_ref  * jc_rel_sigma,  jc_ref * 0.3, jc_ref * 2.0, rng)
        t_s   = _truncated_normal(t_op,    temp_abs_sigma,           1.8,  tc_k * 0.99, rng)
        b_s   = _truncated_normal(b_op,    b_op * field_rel_sigma,   0.1,  bc2_t * 0.99, rng)

        b_frac = min(0.999, b_s / bc2_t)
        t_frac = min(0.999, t_s / tc_k)
        jc = jc_s * (1.0 - t_frac) * (1.0 - b_frac) / max(0.1, aniso)
        samples.append(max(0.0, jc))

    return _statistics(samples)


# ─────────────────────────────────────────────────────────────────────────────
# MIIT Monte Carlo
# ─────────────────────────────────────────────────────────────────────────────

def mc_miit_uncertainty(
    design: MagnetDesign,
    *,
    n_samples: int = 500,
    seed: int = 123,
    current_rel_sigma: float = 0.02,   # 전류 ±2%
    inductance_rel_sigma: float = 0.05,  # 인덕턴스 ±5%
    dump_resistance_ohm: float = 0.5,
    dump_resistance_rel_sigma: float = 0.10,  # 덤프 저항 ±10%
    detection_delay_s: float = 0.020,
    detection_delay_abs_sigma: float = 0.005,  # 검출 지연 ±5 ms
) -> Dict[str, float]:
    """MIIT 불확실성 Monte Carlo 분석."""
    rng = random.Random(seed)
    samples: List[float] = []

    I0 = design.operating_current_a
    L  = design.inductance_h

    for _ in range(n_samples):
        I_s  = _truncated_normal(I0, I0 * current_rel_sigma, I0 * 0.5, I0 * 1.5, rng)
        L_s  = _truncated_normal(L,  L  * inductance_rel_sigma, L * 0.5, L * 2.0, rng)
        R_s  = _truncated_normal(dump_resistance_ohm, dump_resistance_ohm * dump_resistance_rel_sigma,
                                  0.01, dump_resistance_ohm * 3.0, rng)
        td_s = _truncated_normal(detection_delay_s, detection_delay_abs_sigma, 0.001, 0.5, rng)

        tau  = L_s / max(1e-9, R_s)
        miit = (I_s ** 2) * (td_s + tau / 2.0)
        samples.append(max(0.0, miit))

    return _statistics(samples)


# ─────────────────────────────────────────────────────────────────────────────
# 열 마진 Monte Carlo
# ─────────────────────────────────────────────────────────────────────────────

def mc_thermal_margin_uncertainty(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    n_samples: int = 500,
    seed: int = 77,
    temp_abs_sigma: float = 0.3,
    jc_rel_sigma: float = 0.10,
    current_rel_sigma: float = 0.02,
) -> Dict[str, float]:
    """전류공유 온도 불확실성 Monte Carlo 분석."""
    rng = random.Random(seed)
    samples: List[float] = []

    t_op = cryo.operating_temp_k
    I0   = design.operating_current_a
    A    = design.conductor_cross_section_mm2
    tc_k = material.tc_k
    bc2  = material.bc2_t
    jc0  = material.jc_a_per_mm2_77k
    B_op = design.target_field_t

    for _ in range(n_samples):
        t_s  = _truncated_normal(t_op, temp_abs_sigma, 1.8, tc_k * 0.99, rng)
        I_s  = _truncated_normal(I0, I0 * current_rel_sigma, I0 * 0.5, I0 * 2.0, rng)
        jc_s = _truncated_normal(jc0, jc0 * jc_rel_sigma, jc0 * 0.3, jc0 * 2.0, rng)

        j_op = I_s / max(1e-12, A)
        b_frac = min(0.999, B_op / bc2)
        jc0_b = jc_s * (1.0 - b_frac)
        if jc0_b > 0:
            t_cs = tc_k * (1.0 - j_op / jc0_b)
            margin = max(0.0, min(tc_k, t_cs) - t_s)
        else:
            margin = 0.0
        samples.append(margin)

    return _statistics(samples)


# ─────────────────────────────────────────────────────────────────────────────
# 종합 불확실성 분석
# ─────────────────────────────────────────────────────────────────────────────

def assess_uncertainty(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    n_samples: int = 500,
    seed: int = 42,
    miit_limit_a2s: float = 30.0e6,
    thermal_margin_min_k: float = 1.0,
    jc_min_a_per_mm2: float = 100.0,
) -> UncertaintyReport:
    """3개 출력(Jc, MIIT, 열마진) 종합 불확실성 정량화.

    Monte Carlo n_samples 샘플로 분포 추정.
    신뢰도(reliability) = 설계 기준 충족 확률 계산.
    """
    jc_stats    = mc_jc_uncertainty(material, cryo, design, n_samples=n_samples, seed=seed)
    miit_stats  = mc_miit_uncertainty(design, n_samples=n_samples, seed=seed + 1)
    tm_stats    = mc_thermal_margin_uncertainty(material, cryo, design, n_samples=n_samples, seed=seed + 2)

    # 신뢰도 계산: P05(최악 케이스 기준)
    jc_reliable  = jc_stats.get("P05", 0.0) > jc_min_a_per_mm2
    miit_reliable = miit_stats.get("P95", 1e99) < miit_limit_a2s  # 95th percentile이 한계 이하
    tm_reliable  = tm_stats.get("P05", 0.0) > thermal_margin_min_k

    # 변동계수 기반 위험 순위
    cv_jc  = jc_stats.get("cv", 0.0)
    cv_mit = miit_stats.get("cv", 0.0)
    cv_tm  = tm_stats.get("cv", 0.0)

    risks = {"Jc": cv_jc, "MIIT": cv_mit, "thermal_margin": cv_tm}
    highest_risk = max(risks, key=lambda k: risks[k])

    # 권고
    recs: List[str] = []
    if not jc_reliable:
        recs.append(f"Jc 5th percentile ({jc_stats.get('P05', 0):.1f} A/mm²) < 최소 기준 {jc_min_a_per_mm2} A/mm². "
                    f"필라멘트 균일도 향상 필요.")
    if not miit_reliable:
        recs.append(f"MIIT P95 ({miit_stats.get('P95', 0)/1e6:.1f} MA²s) > 한계 {miit_limit_a2s/1e6:.0f} MA²s. "
                    f"보호 마진 강화 필요.")
    if not tm_reliable:
        recs.append(f"열 마진 P05 ({tm_stats.get('P05', 0):.2f} K) < {thermal_margin_min_k} K. "
                    f"운전 전류 감소 또는 냉각 강화 권장.")
    if cv_jc > 0.20:
        recs.append(f"Jc 변동계수 {cv_jc*100:.0f}% 과대 — 제조 공정 균일화 필요.")
    if not recs:
        recs.append("불확실성 허용 범위 내. 현재 설계 로버스트성 적절.")

    return UncertaintyReport(
        n_samples=n_samples,
        jc_stats=jc_stats,
        miit_stats=miit_stats,
        thermal_margin_stats=tm_stats,
        jc_reliability=jc_reliable,
        miit_reliability=miit_reliable,
        thermal_margin_reliability=tm_reliable,
        highest_risk_parameter=highest_risk,
        recommendations=recs,
    )
