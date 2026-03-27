"""
protection_system.py — 퀀치 보호 시스템 분석  (v1.1)

설계 문제
──────────
1. 최적 덤프 저항 R_dump 결정
   - R_dump ↑ → 빠른 전류 감쇠 → MIIT ↓ → T_hotspot ↓  (좋음)
   - R_dump ↑ → V_peak = I₀ × R_dump ↑           (절연 한계 제약)
   최적: R_dump_opt = V_limit / I₀

2. MIIT 기반 최고 온도 추정
   지수 감쇠 근사: MIIT = I₀² × (t_detect + L/(2R))
   gamma(T) = ∫₀ᵀ [ρ_m·Cₚ(T') / ρₑ(T')] dT' = MIIT → T 수치 역산

3. 검출 지연 허용 예산
   최고 온도 한계 → MIIT_limit → t_detect_max 역산
   delta_MIIT_per_s = I₀²

참조
──────
Wilson (1983) "Superconducting Magnets" §7.3, OUP
Iwasa (2009) §5.4 MIIT Protection Criterion
"""
from __future__ import annotations

import math

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    ProtectionSystemReport,
)
from .quench_dynamics import heat_capacity_composite, resistivity_cu_matrix

# 손상 온도 기준
_T_LIMIT_NBTI    = 300.0   # K  (연성 — 300 K까지 허용)
_T_LIMIT_NB3SN   = 200.0   # K  (취성 세라믹 — 200 K 한계)
_T_LIMIT_DEFAULT = 300.0   # K


# ─────────────────────────────────────────────────────────────────────────────
# MIIT 계산
# ─────────────────────────────────────────────────────────────────────────────

def miit_exponential_decay(
    current_a: float,
    inductance_h: float,
    dump_resistance_ohm: float,
    detection_delay_s: float = 0.020,
) -> float:
    """지수 감쇠 근사 MIIT = I₀² × (t_detect + L/(2R))  [A²·s].

    완전한 MIIT 공식:
      전류: I(t) = I₀ × exp(−t/τ),  τ = L/R
      MIIT = I₀²·t_detect + ∫₀^∞ I₀²·exp(−2t/τ) dt
           = I₀²·(t_detect + τ/2)
    """
    tau = inductance_h / max(1e-9, dump_resistance_ohm)
    return (current_a ** 2) * (detection_delay_s + tau / 2.0)


def optimal_dump_resistance(
    inductance_h: float,
    operating_current_a: float,
    voltage_limit_v: float = 1000.0,
) -> float:
    """최적 덤프 저항 R_opt = V_limit / I₀  [Ω].

    전압 한계가 절연 내력으로 R_dump를 제한한다.
    """
    if operating_current_a <= 0.0:
        return voltage_limit_v
    return voltage_limit_v / operating_current_a


# ─────────────────────────────────────────────────────────────────────────────
# MIIT → T_hotspot 수치 역산
# ─────────────────────────────────────────────────────────────────────────────

def _gamma_integrand(temp_k: float, cu_fraction: float, rrr: float) -> float:
    """gamma(T) 피적분함수: ρ_m·Cₚ(T) / ρₑ(T)  [A²·s/m⁴]."""
    rho_e    = resistivity_cu_matrix(temp_k, rrr)
    rho_m_cp = heat_capacity_composite(temp_k, cu_fraction, 1.0 - cu_fraction)
    if rho_e <= 0.0:
        return 0.0
    return rho_m_cp / rho_e


def hotspot_temp_from_miit(
    miit_a2s: float,
    t_bath_k: float,
    cu_fraction: float = 0.7,
    rrr: float = 100.0,
    t_max_search_k: float = 1000.0,
    n_steps: int = 200,
) -> float:
    """MIIT → T_hotspot 수치 역산 (사다리꼴 적분).

    gamma(T_hotspot) = MIIT / A_conductor²
    γ(T) = ∫_{T_bath}^T [ρ_m·Cₚ(T') / ρₑ(T')] dT'
    단위: A²·s/m⁴ × m⁴ = A²·s
    주의: miit_a2s는 A²·s (MIIT 그대로), 전류밀도 보정 없음
    """
    # 온도 탐색: T_bath에서 t_max_search_k까지
    dT = (t_max_search_k - t_bath_k) / n_steps
    gamma_accum = 0.0
    prev_val = _gamma_integrand(t_bath_k, cu_fraction, rrr)
    T_prev = t_bath_k

    for i in range(1, n_steps + 1):
        T_cur = t_bath_k + i * dT
        cur_val = _gamma_integrand(T_cur, cu_fraction, rrr)
        gamma_accum += (prev_val + cur_val) / 2.0 * dT

        # MIIT 단위 정규화: gamma는 J/(Ω·m³) 단위 — A²·s/m⁴
        # MIIT_effective = gamma × A² (m⁴)
        # 여기서는 단순 비교를 위해 miit_a2s를 m⁴ 면적 없이 직접 비교
        # A_conductor = 1 mm² = 1e-6 m²  기준으로 정규화
        miit_norm = miit_a2s / (1e-6) ** 2  # A²·s/m⁴ 단위로 변환
        if gamma_accum >= miit_norm:
            return T_prev + (miit_norm - (gamma_accum - (prev_val + cur_val) / 2.0 * dT)) / max(1e-30, (prev_val + cur_val) / 2.0) * dT

        prev_val = cur_val
        T_prev = T_cur

    return t_max_search_k


# ─────────────────────────────────────────────────────────────────────────────
# 종합 평가
# ─────────────────────────────────────────────────────────────────────────────

def assess_protection_system(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    detection_delay_s: float = 0.020,
    voltage_limit_v: float = 1000.0,
    hotspot_limit_k: float = 300.0,
    cu_fraction: float = 0.7,
    rrr: float = 100.0,
) -> ProtectionSystemReport:
    """퀀치 보호 시스템 종합 분석.

    1. 최적 덤프 저항 계산
    2. MIIT 추정 (지수 감쇠 근사)
    3. 최고 핫스팟 온도 추정
    4. 검출 지연 허용 예산 계산
    5. 보호 판정
    """
    I0 = design.operating_current_a
    L  = design.inductance_h

    R_opt   = optimal_dump_resistance(L, I0, voltage_limit_v)
    tau     = L / max(1e-9, R_opt)
    V_peak  = I0 * R_opt

    miit_total = miit_exponential_decay(I0, L, R_opt, detection_delay_s)

    # T_hotspot 추정 — 간단 근사 (Wilson 경험식)
    # T_hotspot ≈ T_bath + (MIIT / (I0² × tau_thermal))
    # 더 정확한 역산은 hotspot_temp_from_miit 사용
    # 여기서는 빠른 근사 사용
    tau_thermal = 0.5 * heat_capacity_composite(50.0, cu_fraction, 1.0 - cu_fraction) / max(1e-30, resistivity_cu_matrix(50.0, rrr) * (I0 / max(1e-12, design.conductor_cross_section_mm2 * 1e-6)) ** 2)
    tau_thermal = max(0.01, min(tau_thermal, 100.0))
    T_rise = miit_total / max(1.0, I0 ** 2 * tau_thermal / 300.0)
    T_hotspot = cryo.operating_temp_k + min(T_rise, 1000.0)

    # 검출 지연 예산: MIIT_limit에서 역산
    # MIIT_limit = I₀² × (t_detect_max + τ/2)
    # t_detect_max = MIIT_limit / I₀² - τ/2
    miit_limit_estimate = hotspot_limit_k * I0 ** 2 * tau / 500.0  # 경험적 스케일링
    t_budget = (miit_limit_estimate / max(1.0, I0 ** 2)) - tau / 2.0
    t_budget = max(0.0, t_budget)

    is_protected = T_hotspot < hotspot_limit_k and miit_total < miit_limit_estimate

    if not is_protected:
        rec = (f"보호 불충분: T_hotspot≈{T_hotspot:.0f} K (한계 {hotspot_limit_k:.0f} K). "
               f"R_dump={R_opt:.3f} Ω 증가 또는 검출 지연 단축 필요.")
    elif detection_delay_s > t_budget:
        rec = (f"검출 지연 {detection_delay_s*1e3:.0f} ms > 허용 예산 {t_budget*1e3:.0f} ms. "
               f"검출 속도 개선 필요.")
    else:
        rec = (f"보호 설계 적절: T_hotspot≈{T_hotspot:.0f} K, "
               f"R_dump={R_opt:.3f} Ω, V_peak={V_peak:.0f} V.")

    return ProtectionSystemReport(
        optimal_dump_resistance_ohm=round(R_opt, 4),
        current_decay_tau_s=round(tau, 4),
        peak_dump_voltage_v=round(V_peak, 1),
        estimated_hotspot_temp_k=round(T_hotspot, 1),
        miit_total_a2s=round(miit_total, 2),
        detection_delay_budget_s=round(t_budget, 4),
        is_protected=is_protected,
        recommendation=rec,
    )
