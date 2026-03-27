"""
sensitivity_analysis.py — 파라미터 민감도 분석  (v1.0)

방법론
──────
1. 유한차분 (1차 전방 차분) 민감도 지수
   ∂Y/∂X_i ≈ (Y(X + h·eᵢ) − Y(X)) / h
   정규화: S_i = (X_i/Y) × (∂Y/∂X_i)   [탄성 민감도]

2. 전역 Morris 스크리닝 (단순화 버전)
   EE_i = |Y(X + Δ·eᵢ) − Y(X)| / Δ
   μᵢ* = mean(|EEᵢ|)   [영향도 순위]

3. 설계 최적화 방향 추론
   |S_i| > 임계치 → 중요 파라미터
   S_i > 0 → Y 증가 방향 = X_i 증가
   S_i < 0 → Y 증가 방향 = X_i 감소

대상 출력 지표
───────────────
- Jc(T, B)  : 임계전류밀도 (성능)
- T_cs      : 전류공유 온도 (열 마진)
- MIIT      : 보호 마진
- peak T    : 핫스팟 온도

참조
──────
Saltelli et al. (2008) "Global Sensitivity Analysis", Wiley
Morris (1991) Technometrics 33, 161

stdlib only — no external dependencies.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    SensitivityReport, SensitivityResult,
)


# ─────────────────────────────────────────────────────────────────────────────
# 핵심 민감도 계산
# ─────────────────────────────────────────────────────────────────────────────

def finite_difference_sensitivity(
    func: Callable[..., float],
    base_params: Dict[str, float],
    h_frac: float = 0.01,
) -> Dict[str, float]:
    """유한차분 1차 민감도 지수 (탄성 민감도 S_i = ∂lnY/∂lnXᵢ).

    h_frac: 섭동 비율 (기본값 1%)
    반환: {param_name: S_i}
    """
    y_base = func(**base_params)
    if abs(y_base) < 1e-30:
        return {k: 0.0 for k in base_params}

    sensitivities: Dict[str, float] = {}
    for key, val in base_params.items():
        if val == 0.0:
            sensitivities[key] = 0.0
            continue
        h = abs(val) * h_frac
        perturbed = dict(base_params)
        perturbed[key] = val + h
        y_pert = func(**perturbed)
        dy_dx = (y_pert - y_base) / h
        # 탄성 민감도: S_i = (X/Y) × dY/dX
        sensitivities[key] = (val / y_base) * dy_dx

    return sensitivities


def morris_screening(
    func: Callable[..., float],
    base_params: Dict[str, float],
    delta_frac: float = 0.10,
) -> Dict[str, float]:
    """Morris 초등 효과 (Elementary Effect) 스크리닝.

    delta_frac: 단계 크기 비율 (기본값 10%)
    반환: {param_name: μ_star (평균 절댓값 EE)}
    """
    ee: Dict[str, float] = {}
    y_base = func(**base_params)

    for key, val in base_params.items():
        delta = abs(val) * delta_frac if val != 0.0 else delta_frac
        perturbed = dict(base_params)
        perturbed[key] = val + delta
        y_pert = func(**perturbed)
        ee[key] = abs((y_pert - y_base) / delta)

    return ee


# ─────────────────────────────────────────────────────────────────────────────
# Jc 민감도 분석
# ─────────────────────────────────────────────────────────────────────────────

def _jc_proxy(
    jc_77k: float,
    temp_k: float,
    tc_k: float,
    field_t: float,
    bc2_t: float,
    anisotropy: float,
) -> float:
    """Jc 간략 프록시 (민감도 분석용)."""
    b_frac = min(0.999, field_t / max(1.0, bc2_t))
    t_frac = min(0.999, temp_k / max(1.0, tc_k))
    jc = jc_77k * (1.0 - t_frac) * (1.0 - b_frac) / max(0.1, anisotropy)
    return max(0.01, jc)


def jc_sensitivity(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> Dict[str, float]:
    """Jc에 대한 파라미터 민감도 분석."""
    base = {
        "jc_77k":     material.jc_a_per_mm2_77k,
        "temp_k":     cryo.operating_temp_k,
        "tc_k":       material.tc_k,
        "field_t":    design.target_field_t,
        "bc2_t":      material.bc2_t,
        "anisotropy": material.anisotropy,
    }
    return finite_difference_sensitivity(_jc_proxy, base)


# ─────────────────────────────────────────────────────────────────────────────
# MIIT 민감도 분석
# ─────────────────────────────────────────────────────────────────────────────

def _miit_proxy(
    current_a: float,
    inductance_h: float,
    dump_resistance_ohm: float,
    detection_delay_s: float,
) -> float:
    """MIIT 간략 프록시."""
    tau = inductance_h / max(1e-9, dump_resistance_ohm)
    return (current_a ** 2) * (detection_delay_s + tau / 2.0)


def miit_sensitivity(
    design: MagnetDesign,
    dump_resistance_ohm: float = 0.5,
    detection_delay_s: float = 0.020,
) -> Dict[str, float]:
    """MIIT에 대한 파라미터 민감도."""
    base = {
        "current_a":          design.operating_current_a,
        "inductance_h":       design.inductance_h,
        "dump_resistance_ohm": dump_resistance_ohm,
        "detection_delay_s":  detection_delay_s,
    }
    return finite_difference_sensitivity(_miit_proxy, base)


# ─────────────────────────────────────────────────────────────────────────────
# 열 마진 민감도 분석
# ─────────────────────────────────────────────────────────────────────────────

def _thermal_margin_proxy(
    temp_k: float,
    tc_k: float,
    jc_77k: float,
    field_t: float,
    bc2_t: float,
    current_density: float,
) -> float:
    """T_cs 열 마진 프록시: ΔT = T_cs − T_bath."""
    b_frac = min(0.999, field_t / max(1.0, bc2_t))
    jc0_b = jc_77k * (1.0 - b_frac)
    if jc0_b <= 0:
        return 0.0
    t_cs = tc_k * (1.0 - current_density / jc0_b)
    return max(0.0, t_cs - temp_k)


def thermal_margin_sensitivity(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> Dict[str, float]:
    """T_cs 열 마진에 대한 파라미터 민감도."""
    j_op = design.operating_current_a / max(1e-12, design.conductor_cross_section_mm2)
    base = {
        "temp_k":          cryo.operating_temp_k,
        "tc_k":            material.tc_k,
        "jc_77k":          material.jc_a_per_mm2_77k,
        "field_t":         design.target_field_t,
        "bc2_t":           material.bc2_t,
        "current_density": j_op,
    }
    return finite_difference_sensitivity(_thermal_margin_proxy, base)


# ─────────────────────────────────────────────────────────────────────────────
# 종합 민감도 보고서
# ─────────────────────────────────────────────────────────────────────────────

def assess_sensitivity(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    dump_resistance_ohm: float = 0.5,
    detection_delay_s: float = 0.020,
    top_n: int = 3,
) -> SensitivityReport:
    """Jc·MIIT·열마진 3개 출력에 대한 종합 민감도 분석.

    반환값:
    - results: {output_name: SensitivityResult}
    - top_parameters: 가장 영향력 큰 파라미터 top_n
    - recommendations: 설계 개선 방향
    """
    # Jc 민감도
    jc_sens = jc_sensitivity(material, cryo, design)
    jc_morris = morris_screening(
        _jc_proxy,
        {
            "jc_77k": material.jc_a_per_mm2_77k,
            "temp_k": cryo.operating_temp_k,
            "tc_k": material.tc_k,
            "field_t": design.target_field_t,
            "bc2_t": material.bc2_t,
            "anisotropy": material.anisotropy,
        },
    )

    # MIIT 민감도
    miit_sens = miit_sensitivity(design, dump_resistance_ohm, detection_delay_s)

    # 열 마진 민감도
    th_sens = thermal_margin_sensitivity(material, cryo, design)

    # SensitivityResult 빌드
    results: Dict[str, SensitivityResult] = {}

    def _dominant(sens: Dict[str, float]) -> str:
        if not sens:
            return "unknown"
        return max(sens, key=lambda k: abs(sens[k]))

    results["jc"] = SensitivityResult(
        output_name="Jc [A/mm²]",
        sensitivities=jc_sens,
        morris_ee=jc_morris,
        dominant_param=_dominant(jc_sens),
    )
    results["miit"] = SensitivityResult(
        output_name="MIIT [A²s]",
        sensitivities=miit_sens,
        morris_ee={},
        dominant_param=_dominant(miit_sens),
    )
    results["thermal_margin"] = SensitivityResult(
        output_name="T_cs − T_bath [K]",
        sensitivities=th_sens,
        morris_ee={},
        dominant_param=_dominant(th_sens),
    )

    # 전체 파라미터 중요도 순위 (|S| 합산)
    importance: Dict[str, float] = {}
    for sr in results.values():
        for param, s_val in sr.sensitivities.items():
            importance[param] = importance.get(param, 0.0) + abs(s_val)

    top_params = sorted(importance, key=lambda k: -importance[k])[:top_n]

    # 권고
    recs: List[str] = []
    jc_dom = results["jc"].dominant_param
    miit_dom = results["miit"].dominant_param
    th_dom = results["thermal_margin"].dominant_param

    if jc_dom in ("temp_k", "tc_k"):
        recs.append(f"Jc 최대화: 운전 온도 ↓ 또는 고Tc 재료 선택 ({jc_dom} 민감도 최고).")
    if jc_dom == "field_t":
        recs.append("Jc: 운전 자기장 ↓ 또는 고Bc2 재료 (field-driven Jc degradation).")
    if miit_dom == "dump_resistance_ohm":
        recs.append("MIIT 감소: 덤프 저항 ↑ (MIIT에 가장 큰 영향).")
    if miit_dom == "detection_delay_s":
        recs.append("MIIT 감소: 퀀치 검출 속도 ↑ (지연 시간 단축).")
    if th_dom == "field_t":
        recs.append("열 마진: 운전 자기장 ↓ → T_cs ↑ → 더 큰 마진.")
    if not recs:
        recs.append("민감도 분포 균형적. 복수 파라미터 동시 최적화 권장.")

    return SensitivityReport(
        results=results,
        top_parameters=top_params,
        recommendations=recs,
    )
