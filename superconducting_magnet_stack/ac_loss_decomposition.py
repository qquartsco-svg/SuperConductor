"""
ac_loss_decomposition.py — AC 손실 분해 분석  (v1.2)

세 가지 손실 메커니즘
──────────────────────
1. 히스테리시스 손실 (Bean 모델)
   Q_hyst = (4/3)·μ₀·Jc·d_f·ΔB
   P_hyst = Q_hyst × f  [W/m³ filament]

2. 와전류 손실 (Cu 행렬)
   P_eddy = (π²/6)·σ_Cu·d_s²·(dB/dt)²  [W/m³ strand]

3. 결합 손실 (Twisted filaments 간)
   P_couple = (π²/2μ₀)·(lₚ/2π)²·n_c·(dB/dt)²
   여기서 n_c: 결합 시간 상수 (s)
     n_c = μ₀·(lₚ/2π)² / (2ρ_matrix·(1+2η)/(1-η))
     η = SC 체적분율

참조
──────
Norris (1970) J. Phys. D 3, 489  (히스테리시스)
Morgan (1970) J. Appl. Phys. 41, 3673  (와전류)
Carr (1983) "AC Loss and Macroscopic Theory of Superconductors"  (결합)
"""
from __future__ import annotations

import math

from .contracts import (
    ACLossDecompositionReport, CryoProfile, MagnetDesign, MaterialCandidate,
)

_MU0 = 4.0 * math.pi * 1e-7


# ─────────────────────────────────────────────────────────────────────────────
# 개별 손실 계산
# ─────────────────────────────────────────────────────────────────────────────

def hysteretic_loss_w_per_m(
    jc_a_per_mm2: float,
    filament_dia_m: float,
    field_sweep_t: float,
    frequency_hz: float,
    sc_volume_fraction: float = 0.3,
) -> float:
    """히스테리시스 손실 [W/m conductor].

    P_hyst = f × (4/3) × μ₀ × Jc × d_f × ΔB × A_filaments/A_total
    d_f = filament_dia (반지름이 아닌 지름)
    """
    jc_si = jc_a_per_mm2 * 1.0e6
    d_f   = filament_dia_m
    q_hyst_per_m3 = (4.0 / 3.0) * _MU0 * jc_si * d_f * max(0.0, field_sweep_t)
    # W/m³ filament → W/m conductor (sc 체적분율 보정, 도체 1m² 단면 기준)
    p_w_per_m = q_hyst_per_m3 * frequency_hz * sc_volume_fraction
    return max(0.0, p_w_per_m)


def eddy_current_loss_w_per_m(
    rho_matrix_ohm_m: float,
    strand_dia_m: float,
    db_dt_t_per_s: float,
    cu_fraction: float = 0.7,
) -> float:
    """와전류 손실 [W/m conductor].

    P_eddy = (π²/6) × σ_Cu × d_s² × (dB/dt)²  × V_Cu/V_total
    σ_Cu = 1/ρ_Cu
    """
    if rho_matrix_ohm_m <= 0.0:
        return 0.0
    sigma_cu = 1.0 / rho_matrix_ohm_m
    p_eddy_m3 = (math.pi ** 2 / 6.0) * sigma_cu * strand_dia_m ** 2 * db_dt_t_per_s ** 2
    return max(0.0, p_eddy_m3 * cu_fraction)


def coupling_loss_w_per_m(
    twist_pitch_m: float,
    db_dt_t_per_s: float,
    rho_matrix_ohm_m: float,
    sc_volume_fraction: float = 0.3,
    cu_fraction: float = 0.7,
) -> float:
    """결합 손실 [W/m conductor].

    n_c = μ₀·(lₚ/2π)² / (2·ρ_eff·(1+2η)/(1-η))
    P_couple = (π²/2μ₀) × (lₚ/2π)² × n_c × (dB/dt)²

    η = SC 체적분율
    """
    eta = sc_volume_fraction
    if rho_matrix_ohm_m <= 0.0 or (1.0 - eta) < 1e-6:
        return 0.0
    lp_eff = twist_pitch_m / (2.0 * math.pi)
    coupling_factor = (1.0 + 2.0 * eta) / (1.0 - eta)
    n_c = _MU0 * lp_eff ** 2 / (2.0 * rho_matrix_ohm_m * coupling_factor)
    p_couple = (math.pi ** 2 / (2.0 * _MU0)) * lp_eff ** 2 * n_c * db_dt_t_per_s ** 2
    return max(0.0, p_couple)


# ─────────────────────────────────────────────────────────────────────────────
# 종합 평가
# ─────────────────────────────────────────────────────────────────────────────

def assess_ac_loss_decomposition(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    frequency_hz: float = 5.0,
    filament_dia_m: float = 6e-6,
    strand_dia_m: float = 0.85e-3,
    twist_pitch_m: float = 0.025,
    cu_fraction: float = 0.7,
    rrr: float = 100.0,
) -> ACLossDecompositionReport:
    """AC 손실 세 성분 분해 분석.

    dB/dt ≈ ΔB / (1/f) = ΔB × f  (정현파 스윕 근사)
    ΔB = target_field / 2  (0 → peak → 0 반주기)
    """
    from .quench_dynamics import resistivity_cu_matrix

    delta_b = design.target_field_t / 2.0
    db_dt   = delta_b * frequency_hz  # T/s

    rho_cu = resistivity_cu_matrix(cryo.operating_temp_k, rrr)

    # Jc 추정 (운전점)
    b_frac = min(0.999, design.target_field_t / material.bc2_t)
    t_frac = min(0.999, cryo.operating_temp_k / material.tc_k)
    jc_op  = material.jc_a_per_mm2_77k * (1.0 - t_frac) * (1.0 - b_frac) / material.anisotropy
    jc_op  = max(1.0, jc_op)

    sc_frac = 1.0 - cu_fraction

    p_hyst   = hysteretic_loss_w_per_m(jc_op, filament_dia_m, delta_b, frequency_hz, sc_frac)
    p_eddy   = eddy_current_loss_w_per_m(rho_cu, strand_dia_m, db_dt, cu_fraction)
    p_couple = coupling_loss_w_per_m(twist_pitch_m, db_dt, rho_cu, sc_frac, cu_fraction)
    p_total  = p_hyst + p_eddy + p_couple

    # 지배 메커니즘
    mechanisms = {"hysteretic": p_hyst, "eddy": p_eddy, "coupling": p_couple}
    dominant = max(mechanisms, key=lambda k: mechanisms[k])

    # 냉각 패널티
    margin = cryo.cooling_capacity_w - cryo.heat_load_w
    penalty = min(1.0, p_total / max(0.1, margin)) if margin > 0 else 1.0

    if penalty > 0.8:
        rec = f"AC 손실 {p_total:.3f} W/m 과대 — 주요: {dominant}. 선재 세분화 또는 꼬임 피치 단축 검토."
    elif dominant == "hysteretic":
        rec = f"히스테리시스 지배 ({p_hyst:.3f} W/m) — 필라멘트 세분화(직경 감소)로 저감 가능."
    elif dominant == "coupling":
        rec = f"결합 손실 지배 ({p_couple:.3f} W/m) — 꼬임 피치 단축 권장."
    else:
        rec = f"와전류 지배 ({p_eddy:.3f} W/m) — 행렬 저항 증가 또는 Cu 분율 감소 검토."

    return ACLossDecompositionReport(
        frequency_hz=frequency_hz,
        db_dt_t_per_s=round(db_dt, 4),
        hysteretic_loss_w_per_m=round(p_hyst, 6),
        eddy_current_loss_w_per_m=round(p_eddy, 6),
        coupling_loss_w_per_m=round(p_couple, 6),
        total_ac_loss_w_per_m=round(p_total, 6),
        dominant_mechanism=dominant,
        cooling_penalty_index=round(penalty, 4),
        recommendation=rec,
    )
