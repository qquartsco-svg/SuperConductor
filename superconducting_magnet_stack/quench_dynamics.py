"""
quench_dynamics.py — 1D RK4 퀀치 전파 시뮬레이션  (v1.1)

지배방정식 (단일노드 집중 모델)
───────────────────────────────
dT/dt = [ρₑ(T)·J² − h_eff·(T − T_bath)] / [ρ_m·Cₚ(T)]
dL_nz/dt = 2·v_nz(T, I)

여기서:
  ρₑ(T)  : Cu 행렬 전기저항률 (Ω·m) — 선형 근사 (T > 20 K)
  J       : 운전 전류밀도 (A/m²)
  h_eff   : 유효 냉각계수 (W/m³·K)
  ρ_m·Cₚ : 복합 체적열용량 (J/m³·K) — 멱함수 근사
  v_nz   : 정상영역 전파 속도 (m/s) — 단열 근사

MIIT 적분
──────────
MIIT = ∫₀^t_dump I(t)² dt  [A²·s]
지수 감쇠 근사: I(t) = I₀·exp(−t/τ), τ = L/R_dump
MIIT = I₀²·(t_detect + τ/2)

손상 기준
──────────
NbTi, REBCO: T_hotspot < 300 K  → MIIT_limit ~ 30 MA²·s
Nb3Sn      : T_hotspot < 200 K  → 취성 세라믹 보호 필요

참조
──────
Wilson (1983) "Superconducting Magnets" Ch.7, OUP
Iwasa (2009) "Case Studies in Superconducting Magnets" 2nd ed.

stdlib only — no external dependencies.
"""
from __future__ import annotations

import math
from typing import List, Optional

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    QuenchDynamicsReport, QuenchDynamicsState,
)

# 물리 상수
_RHO_CU_300 = 1.72e-8   # Ω·m  (300 K에서 Cu 전기저항률)
_RHO_MASS_CU = 8960.0   # kg/m³ (Cu 밀도)


# ─────────────────────────────────────────────────────────────────────────────
# 재료 물성 함수
# ─────────────────────────────────────────────────────────────────────────────

def resistivity_cu_matrix(temp_k: float, rrr: float = 100.0) -> float:
    """Cu 행렬 전기저항률 ρₑ(T) [Ω·m].

    선형 근사 (T > 10 K):  ρ = ρ₀ × T / (RRR × 273)
    저온 잔류저항: ρ_min = ρ₀ / RRR (T → 0 극한)
    """
    rho_min = _RHO_CU_300 / rrr
    rho_linear = _RHO_CU_300 * max(4.2, temp_k) / 273.0
    return max(rho_min, rho_linear / rrr)


def heat_capacity_composite(
    temp_k: float,
    cu_fraction: float = 0.7,
    sc_fraction: float = 0.3,
) -> float:
    """복합 체적열용량 ρ_m·Cₚ(T) [J/m³·K].

    Cu: Cₚ(T) ≈ 0.93 × T^0.8  [J/kg·K, 극저온 범위 경험식]
    SC: 비슷한 질량 → Cu 비례 근사
    """
    t = max(4.2, temp_k)
    cp_cu = 0.93 * (t ** 0.8)       # J/kg·K
    rho_m = cu_fraction * _RHO_MASS_CU + sc_fraction * 8900.0  # kg/m³ (Nb density ~8900)
    return rho_m * cp_cu


def current_sharing_temperature_k(
    material: MaterialCandidate,
    j_op_a_per_mm2: float,
    field_t: float,
    t_bath_k: float,
) -> float:
    """전류공유 온도 T_cs — Jc(T_cs) = J_op.

    단순 역산: T_cs = Tc × (1 − J_op/Jc0_ref) + 보정
    정확한 값은 Jc(T) 곡선을 역산해야 하지만 선형 근사로 빠르게 추정.
    """
    b_frac = min(0.999, field_t / material.bc2_t)
    jc_at_bath = material.jc_a_per_mm2_77k * (1.0 - t_bath_k / material.tc_k) * (1.0 - b_frac)
    jc_at_bath = max(1e-6, jc_at_bath)

    if j_op_a_per_mm2 >= jc_at_bath:
        return t_bath_k  # 이미 전류공유 중

    # Jc(T) = Jc0 × (1 - T/Tc) × (1 - B/Bc2) 의 역산
    # J_op = Jc0 × (1 - T_cs/Tc) × (1 - b_frac)
    # T_cs = Tc × (1 - J_op / (Jc0 × (1 - b_frac)))
    jc0_b = material.jc_a_per_mm2_77k * (1.0 - b_frac)
    if jc0_b <= 0.0:
        return t_bath_k
    t_cs = material.tc_k * (1.0 - j_op_a_per_mm2 / jc0_b)
    return max(t_bath_k, min(material.tc_k, t_cs))


def nz_velocity_adiabatic(
    j_op_a_per_m2: float,
    rho_e: float,
    rho_m_cp: float,
    t_cs_k: float,
    t_bath_k: float,
) -> float:
    """단열 NZPV 근사 v_nz [m/s].

    v_nz = J × √(ρₑ / (ρ_m·Cₚ × (T_cs − T_bath)))

    이 식은 온도 전선이 단열적으로 전파할 때의 속도를 나타낸다.
    실제 값은 열전도도에 따라 더 낮을 수 있다.
    """
    delta_t = max(0.1, t_cs_k - t_bath_k)
    if rho_m_cp <= 0.0 or rho_e <= 0.0:
        return 0.0
    v = j_op_a_per_m2 * math.sqrt(rho_e / (rho_m_cp * delta_t))
    return max(0.0, min(50.0, v))   # 물리적 상한 50 m/s 클램프


# ─────────────────────────────────────────────────────────────────────────────
# RK4 퀀치 시뮬레이션
# ─────────────────────────────────────────────────────────────────────────────

def _dT_dt(
    temp_k: float,
    j_op_a_per_m2: float,
    t_bath_k: float,
    h_eff: float,
    rrr: float,
    cu_fraction: float,
) -> float:
    """dT/dt [K/s] — 단일 노드 열평형."""
    rho_e    = resistivity_cu_matrix(temp_k, rrr)
    rho_m_cp = heat_capacity_composite(temp_k, cu_fraction, 1.0 - cu_fraction)
    if rho_m_cp <= 0.0:
        return 0.0
    joule   = rho_e * j_op_a_per_m2 ** 2
    cooling = h_eff * max(0.0, temp_k - t_bath_k)
    return (joule - cooling) / rho_m_cp


def simulate_quench_rk4(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    dt_s: float = 1e-3,
    t_max_s: float = 1.0,
    dump_delay_s: float = 0.020,
    dump_resistance_ohm: float = 0.5,
    rrr: float = 100.0,
    cu_fraction: float = 0.7,
    miit_limit_a2s: float = 30.0e6,   # 30 MA²·s
    h_eff_w_per_m3_k: float = 1000.0, # 유효 냉각계수 (W/m³·K)
) -> QuenchDynamicsReport:
    """1D RK4 퀀치 전파 시뮬레이션.

    단계:
    1. 퀀치 개시 (t=0): T = T_bath
    2. 전류 유지 (t < dump_delay_s)
    3. dump_delay 후 전류 지수 감쇠
    4. T_hotspot 추적 + MIIT 누적
    """
    t_bath = cryo.operating_temp_k
    field_t = design.target_field_t
    I0 = design.operating_current_a
    A_mm2 = design.conductor_cross_section_mm2
    A_m2 = A_mm2 * 1e-6
    L = design.inductance_h

    if A_m2 <= 0.0:
        A_m2 = 1e-6

    j_op_mm2 = I0 / A_mm2             # A/mm²
    j_op_m2  = j_op_mm2 * 1e6        # A/m²

    # 전류공유 온도
    t_cs = current_sharing_temperature_k(material, j_op_mm2, field_t, t_bath)

    tau_dump = L / max(1e-6, dump_resistance_ohm)

    # 초기 상태
    temp    = t_bath + 0.1  # 약간 높은 초기 온도 (퀀치 씨앗)
    nz_len  = 0.001          # 1 mm 초기 정상영역
    miit    = 0.0
    I_curr  = I0
    t_cur   = 0.0

    trajectory: List[QuenchDynamicsState] = []
    peak_temp = temp
    time_to_peak = 0.0

    steps = int(t_max_s / dt_s) + 1

    for step in range(steps):
        t_cur = step * dt_s

        # 전류 계산: dump 이후 지수 감쇠
        if t_cur >= dump_delay_s:
            t_since_dump = t_cur - dump_delay_s
            I_curr = I0 * math.exp(-t_since_dump / max(1e-6, tau_dump))
        else:
            I_curr = I0

        # 현재 J (A/m²)
        j_now = I_curr / A_m2

        # RK4
        k1 = _dT_dt(temp,               j_now, t_bath, h_eff_w_per_m3_k, rrr, cu_fraction)
        k2 = _dT_dt(temp + dt_s/2 * k1, j_now, t_bath, h_eff_w_per_m3_k, rrr, cu_fraction)
        k3 = _dT_dt(temp + dt_s/2 * k2, j_now, t_bath, h_eff_w_per_m3_k, rrr, cu_fraction)
        k4 = _dT_dt(temp + dt_s    * k3, j_now, t_bath, h_eff_w_per_m3_k, rrr, cu_fraction)
        dT = (k1 + 2*k2 + 2*k3 + k4) / 6.0
        temp += dT * dt_s
        temp  = max(t_bath, temp)

        # NZPV 계산
        rho_e    = resistivity_cu_matrix(temp, rrr)
        rho_m_cp = heat_capacity_composite(temp, cu_fraction, 1.0 - cu_fraction)
        v_nz = nz_velocity_adiabatic(j_now, rho_e, rho_m_cp, t_cs, t_bath)
        nz_len += 2.0 * v_nz * dt_s

        # MIIT 누적 (사다리꼴 근사)
        miit += (I_curr ** 2) * dt_s

        # Joule & cooling power per m³
        joule_pw = rho_e * j_now ** 2
        cool_pw  = h_eff_w_per_m3_k * max(0.0, temp - t_bath)

        # 기록 (10스텝마다 + 마지막)
        if step % max(1, steps // 200) == 0 or step == steps - 1:
            trajectory.append(QuenchDynamicsState(
                time_s=round(t_cur, 6),
                temp_k=round(temp, 3),
                nz_length_m=round(nz_len, 6),
                nz_velocity_m_per_s=round(v_nz, 4),
                joule_power_w_per_m3=round(joule_pw, 2),
                cooling_power_w_per_m3=round(cool_pw, 2),
                miit_integral_a2s=round(miit, 2),
            ))

        # 최고 온도 추적
        if temp > peak_temp:
            peak_temp = temp
            time_to_peak = t_cur

        # 수렴 확인: 온도가 안정화되면 조기 종료
        if t_cur > dump_delay_s + 5 * tau_dump and temp < t_bath + 1.0:
            break

    is_destructive = miit > miit_limit_a2s

    if is_destructive:
        rec = (f"파괴 위험: MIIT={miit/1e6:.1f} MA²s > 한계 {miit_limit_a2s/1e6:.1f} MA²s. "
               f"덤프 저항 증가 또는 검출 지연 단축 필요.")
    elif peak_temp > 200.0:
        rec = f"최고온도 {peak_temp:.0f} K — Nb3Sn 취성 한계(200K) 근접. 보호 마진 확인 필요."
    else:
        rec = f"안전 범위 내: T_peak={peak_temp:.1f} K, MIIT={miit/1e6:.2f} MA²s."

    return QuenchDynamicsReport(
        peak_hotspot_temp_k=round(peak_temp, 2),
        time_to_peak_s=round(time_to_peak, 5),
        final_nz_length_m=round(nz_len, 4),
        miit_value_a2s=round(miit, 2),
        miit_limit_a2s=miit_limit_a2s,
        is_destructive=is_destructive,
        trajectory=trajectory,
        recommendation=rec,
    )
