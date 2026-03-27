"""
multiphysics_engine.py — 전자기-열-기계 결합 RK4 시뮬레이션  (v1.0)

결합 상태 벡터 SCState(T, I, ε, L_nz)
──────────────────────────────────────

dT/dt  = [ρₑ(T,ε)·J² − h_eff·(T − T_bath)] / (ρ_m·Cₚ(T))
         - 열적 상태: 줄 가열 vs. 냉각 균형

dI/dt  = −R_total(T, L_nz) × I / L
         - 전류: 회로 방정식 (덤프 저항 + 정상영역 저항)

dε/dt  = α_thermal × (dT/dt) + σ_Lorentz / E_modulus
         - 기계: 열팽창 + Lorentz 응력 변형률
         σ_Lorentz ≈ μ₀ × J × B × r_coil

dL_nz/dt = 2 × v_nz(T, I, ε)
         - 정상영역 전파 속도 (변형률 Jc 보정 포함)

참조
──────
Wilson (1983) §7, OUP
Bottura (2000) IEEE Trans. Appl. Supercond. 10, 1063
Nijhuis et al. (2004) Supercond. Sci. Tech. 17, 1 (CICC 결합)

stdlib only — no external dependencies.
"""
from __future__ import annotations

import math
from typing import List

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    MultiphysicsReport, QuenchDynamicsState, SCState,
)
from .quench_dynamics import (
    heat_capacity_composite, nz_velocity_adiabatic,
    resistivity_cu_matrix, current_sharing_temperature_k,
)
from .strain_effects import ekin_devantay_s, rebco_jc_strain_factor, _ekin_s_nbti

_MU0 = 4.0 * math.pi * 1e-7


# ─────────────────────────────────────────────────────────────────────────────
# 보조 함수
# ─────────────────────────────────────────────────────────────────────────────

def _strain_jc_factor(material_name: str, epsilon: float) -> float:
    """재료별 변형률 보정 계수."""
    if material_name == "Nb3Sn":
        s = ekin_devantay_s(epsilon)
        return math.sqrt(max(0.0, s))
    elif material_name == "REBCO":
        return max(0.0, rebco_jc_strain_factor(epsilon))
    elif material_name == "NbTi":
        return max(0.0, _ekin_s_nbti(epsilon))
    return 1.0


def _nz_resistance_ohm(
    temp_k: float,
    nz_length_m: float,
    current_a: float,
    conductor_cross_section_m2: float,
    rrr: float,
    cu_fraction: float,
) -> float:
    """정상영역(NZ) 저항 계산 [Ω].

    R_nz = ρₑ(T) × L_nz / (A_cond × f_Cu)
    Cu 행렬만 전류 전도 (SC는 정상영역에서 저항성)
    """
    rho_e = resistivity_cu_matrix(temp_k, rrr)
    a_cu = conductor_cross_section_m2 * cu_fraction
    if a_cu <= 0.0:
        return 0.0
    return rho_e * nz_length_m / a_cu


# ─────────────────────────────────────────────────────────────────────────────
# 4-변수 결합 미분
# ─────────────────────────────────────────────────────────────────────────────

def _sc_derivatives(
    state: SCState,
    *,
    material_name: str,
    t_bath_k: float,
    h_eff: float,
    rrr: float,
    cu_fraction: float,
    inductance_h: float,
    dump_resistance_ohm: float,
    conductor_cross_section_m2: float,
    jc_op_a_per_m2: float,
    t_cs_k: float,
    field_t: float,
    r_coil_m: float,
    e_modulus_pa: float,
    alpha_thermal: float,
    is_dumping: bool,
) -> SCState:
    """SCState 4-변수 결합 미분 반환."""
    T  = state.temp_k
    I  = state.current_a
    eps = state.strain
    L_nz = state.nz_length_m

    # ── 전기저항 ──────────────────────────────────────────
    rho_e    = resistivity_cu_matrix(T, rrr)
    rho_m_cp = heat_capacity_composite(T, cu_fraction, 1.0 - cu_fraction)
    a_m2 = conductor_cross_section_m2

    J_now = I / max(1e-12, a_m2)   # A/m²

    # ── dT/dt ─────────────────────────────────────────────
    joule   = rho_e * J_now ** 2
    cooling = h_eff * max(0.0, T - t_bath_k)
    dT_dt = (joule - cooling) / max(1e-10, rho_m_cp)

    # ── 정상영역 저항 ─────────────────────────────────────
    R_nz = _nz_resistance_ohm(T, max(0.0, L_nz), I, a_m2, rrr, cu_fraction)
    R_total = R_nz + (dump_resistance_ohm if is_dumping else 0.0)

    # ── dI/dt ─────────────────────────────────────────────
    dI_dt = -(R_total * I) / max(1e-9, inductance_h)

    # ── dε/dt (열팽창 + Lorentz) ──────────────────────────
    # σ_Lorentz ≈ μ₀ × J × B × r_coil (단순 Hoop 응력 근사)
    sigma_lorentz = _MU0 * J_now * field_t * r_coil_m
    deps_dt = alpha_thermal * dT_dt + sigma_lorentz / max(1e6, e_modulus_pa)

    # ── dL_nz/dt ─────────────────────────────────────────
    jc_factor = _strain_jc_factor(material_name, eps)
    jc_local  = jc_op_a_per_m2 * jc_factor
    # T_cs 변형률 보정 (보수적: strain → Jc ↓ → T_cs ↓)
    t_cs_eff  = t_cs_k * (jc_factor ** 0.5)
    v_nz = nz_velocity_adiabatic(J_now, rho_e, rho_m_cp, t_cs_eff, t_bath_k)
    dLnz_dt = 2.0 * v_nz

    return SCState(
        time_s=0.0,           # 사용하지 않는 필드
        temp_k=dT_dt,
        current_a=dI_dt,
        strain=deps_dt,
        nz_length_m=dLnz_dt,
    )


def _rk4_step(
    state: SCState,
    dt: float,
    **kwargs,
) -> SCState:
    """SCState RK4 단일 스텝."""
    def deriv(s):
        return _sc_derivatives(s, **kwargs)

    k1 = deriv(state)
    k2 = deriv(SCState(
        time_s=state.time_s + dt / 2,
        temp_k=state.temp_k + dt / 2 * k1.temp_k,
        current_a=state.current_a + dt / 2 * k1.current_a,
        strain=state.strain + dt / 2 * k1.strain,
        nz_length_m=state.nz_length_m + dt / 2 * k1.nz_length_m,
    ))
    k3 = deriv(SCState(
        time_s=state.time_s + dt / 2,
        temp_k=state.temp_k + dt / 2 * k2.temp_k,
        current_a=state.current_a + dt / 2 * k2.current_a,
        strain=state.strain + dt / 2 * k2.strain,
        nz_length_m=state.nz_length_m + dt / 2 * k2.nz_length_m,
    ))
    k4 = deriv(SCState(
        time_s=state.time_s + dt,
        temp_k=state.temp_k + dt * k3.temp_k,
        current_a=state.current_a + dt * k3.current_a,
        strain=state.strain + dt * k3.strain,
        nz_length_m=state.nz_length_m + dt * k3.nz_length_m,
    ))

    new_T   = state.temp_k    + dt * (k1.temp_k    + 2*k2.temp_k    + 2*k3.temp_k    + k4.temp_k)    / 6.0
    new_I   = state.current_a + dt * (k1.current_a + 2*k2.current_a + 2*k3.current_a + k4.current_a) / 6.0
    new_eps = state.strain    + dt * (k1.strain    + 2*k2.strain    + 2*k3.strain    + k4.strain)    / 6.0
    new_Lnz = state.nz_length_m + dt * (k1.nz_length_m + 2*k2.nz_length_m + 2*k3.nz_length_m + k4.nz_length_m) / 6.0

    return SCState(
        time_s=state.time_s + dt,
        temp_k=new_T,
        current_a=max(0.0, new_I),
        strain=new_eps,
        nz_length_m=max(0.0, new_Lnz),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 결합 멀티피직스 시뮬레이션
# ─────────────────────────────────────────────────────────────────────────────

def simulate_multiphysics(
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
    h_eff_w_per_m3_k: float = 1000.0,
    miit_limit_a2s: float = 30.0e6,
    r_coil_m: float = 0.15,
    e_modulus_pa: float = 100.0e9,   # Nb3Sn: ~150 GPa, NbTi: ~80 GPa
    alpha_thermal: float = 7e-6,     # 열팽창계수 [1/K], Cu ~17e-6, Nb3Sn ~7e-6
    initial_strain: float = 0.0,
) -> MultiphysicsReport:
    """전자기-열-기계 결합 RK4 시뮬레이션.

    결합 상태 벡터: [T, I, ε, L_nz]
    전류 감쇠는 R_nz(T, L_nz) + R_dump 으로 자기 정합적으로 계산.
    변형률은 열팽창 + Lorentz 응력 누적.
    """
    t_bath = cryo.operating_temp_k
    I0     = design.operating_current_a
    L      = design.inductance_h
    A_mm2  = design.conductor_cross_section_mm2
    A_m2   = max(1e-12, A_mm2 * 1e-6)
    B_op   = design.target_field_t

    j_op_mm2 = I0 / max(1e-12, A_mm2)
    j_op_m2  = j_op_mm2 * 1e6

    t_cs = current_sharing_temperature_k(material, j_op_mm2, B_op, t_bath)

    # 초기 상태
    state = SCState(
        time_s=0.0,
        temp_k=t_bath + 0.1,
        current_a=I0,
        strain=initial_strain,
        nz_length_m=0.001,
    )

    trajectory: List[SCState] = []
    miit = 0.0
    peak_temp = state.temp_k
    peak_strain = abs(state.strain)
    time_to_peak = 0.0

    steps = int(t_max_s / dt_s) + 1

    for step in range(steps):
        t_cur = step * dt_s
        is_dumping = (t_cur >= dump_delay_s)

        # RK4
        state = _rk4_step(
            state,
            dt_s,
            material_name=material.name,
            t_bath_k=t_bath,
            h_eff=h_eff_w_per_m3_k,
            rrr=rrr,
            cu_fraction=cu_fraction,
            inductance_h=L,
            dump_resistance_ohm=dump_resistance_ohm,
            conductor_cross_section_m2=A_m2,
            jc_op_a_per_m2=j_op_m2,
            t_cs_k=t_cs,
            field_t=B_op,
            r_coil_m=r_coil_m,
            e_modulus_pa=e_modulus_pa,
            alpha_thermal=alpha_thermal,
            is_dumping=is_dumping,
        )

        # 물리적 하한
        state = SCState(
            time_s=t_cur + dt_s,
            temp_k=max(t_bath, state.temp_k),
            current_a=max(0.0, state.current_a),
            strain=state.strain,
            nz_length_m=max(0.0, state.nz_length_m),
        )

        # MIIT 누적
        miit += (state.current_a ** 2) * dt_s

        # 최고값 추적
        if state.temp_k > peak_temp:
            peak_temp = state.temp_k
            time_to_peak = t_cur + dt_s
        if abs(state.strain) > peak_strain:
            peak_strain = abs(state.strain)

        # 기록 (200포인트 목표)
        if step % max(1, steps // 200) == 0 or step == steps - 1:
            trajectory.append(SCState(
                time_s=round(t_cur + dt_s, 6),
                temp_k=round(state.temp_k, 3),
                current_a=round(state.current_a, 3),
                strain=round(state.strain, 8),
                nz_length_m=round(state.nz_length_m, 6),
            ))

        # 조기 종료: 전류 소진 + 냉각 복귀
        if state.current_a < I0 * 0.001 and state.temp_k < t_bath + 0.5:
            break

    is_destructive = miit > miit_limit_a2s

    # NbTi/REBCO: 300 K, Nb3Sn: 200 K 기준
    t_limit = 200.0 if material.name == "Nb3Sn" else 300.0
    thermal_ok = peak_temp < t_limit

    # 변형률 한계: Nb3Sn 0.5%, REBCO 0.45%, NbTi 0.3%
    irr_strain = {"Nb3Sn": 0.005, "REBCO": 0.0045, "NbTi": 0.003}.get(material.name, 0.006)
    strain_ok = peak_strain < irr_strain

    if is_destructive:
        rec = (f"파괴 위험: MIIT={miit/1e6:.1f} MA²s. "
               f"덤프 저항 ↑ 또는 검출 지연 ↓ 필요.")
    elif not thermal_ok:
        rec = (f"열적 위험: T_peak={peak_temp:.0f} K > 한계 {t_limit:.0f} K. "
               f"냉각 강화 또는 덤프 가속 필요.")
    elif not strain_ok:
        rec = (f"기계적 위험: ε_peak={peak_strain*100:.3f}% > 비가역 한계 {irr_strain*100:.2f}%. "
               f"사전압축 조정 또는 코일 지지 강화 필요.")
    else:
        rec = (f"결합 시뮬레이션 정상: T_peak={peak_temp:.1f} K, "
               f"ε_peak={peak_strain*1e4:.1f}×10⁻⁴, MIIT={miit/1e6:.2f} MA²s.")

    return MultiphysicsReport(
        peak_temp_k=round(peak_temp, 2),
        peak_strain=round(peak_strain, 8),
        final_current_a=round(state.current_a, 3),
        final_nz_length_m=round(state.nz_length_m, 4),
        miit_total_a2s=round(miit, 2),
        time_to_peak_s=round(time_to_peak, 5),
        is_destructive=is_destructive,
        thermal_margin_ok=thermal_ok,
        strain_margin_ok=strain_ok,
        trajectory=trajectory,
        recommendation=rec,
    )
