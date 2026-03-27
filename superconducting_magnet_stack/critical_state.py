"""
critical_state.py — Bean / Kim / E-J 임계상태 모델  (v1.0)

모델 개요
──────────
Bean 모델  : Jc = const (자기장 무관)
             균일한 차폐전류 → 완전침투 자화 M = -Jc·d/3
Kim 모델   : Jc = Jc0 / (1 + B/B0)
             자기장 증가 시 Jc 감쇠
E-J 멱함수 : E/Ec = (J/Jc)^n
             n값이 낮을수록 플럭스 크리프 심화

히스테리시스 손실 (Bean, 완전침투 이후)
  Q = (4/3) × μ₀ × Jc × d² × ΔB  [J/m³ per cycle]

참조
──────
Bean (1962) Phys. Rev. Lett. 8, 250
Kim et al. (1963) Phys. Rev. Lett. 11, 196
Norris (1970) J. Phys. D 3, 489
"""
from __future__ import annotations

import math

from .contracts import CriticalStateResult, MaterialCandidate

_MU0 = 4.0 * math.pi * 1e-7   # H/m
_EC  = 1.0e-4                  # V/m  (표준 임계전류 기준)


# ─────────────────────────────────────────────────────────────────────────────
# E-J 멱함수
# ─────────────────────────────────────────────────────────────────────────────

def ej_power_law(
    j_a_per_m2: float,
    jc_a_per_m2: float,
    n_value: float,
    ec_v_per_m: float = _EC,
) -> float:
    """E-J 멱함수: E = Ec × (J/Jc)^n  [V/m].

    n값 가이드:
      NbTi   : 50~100 (날카로운 전이)
      Nb3Sn  : 20~40  (중간 플럭스 크리프)
      REBCO  : 20~30  (HTS 플럭스 크리프)
    """
    if jc_a_per_m2 <= 0.0:
        return ec_v_per_m
    ratio = max(0.0, j_a_per_m2 / jc_a_per_m2)
    return ec_v_per_m * (ratio ** n_value)


# ─────────────────────────────────────────────────────────────────────────────
# 히스테리시스 손실
# ─────────────────────────────────────────────────────────────────────────────

def hysteresis_loss_bean(
    jc_a_per_mm2: float,
    filament_radius_m: float,
    delta_b_t: float,
) -> float:
    """Bean 모델 히스테리시스 손실 (J/m³ per half-cycle).

    Q_hyst = (4/3) × μ₀ × Jc × d × ΔB  [d = filament_radius × 2]
    완전침투 이후 영역에서 유효.
    """
    jc_si = jc_a_per_mm2 * 1.0e6   # A/mm² → A/m²
    d = 2.0 * filament_radius_m
    return (4.0 / 3.0) * _MU0 * jc_si * d * max(0.0, delta_b_t)


# ─────────────────────────────────────────────────────────────────────────────
# Bean 모델
# ─────────────────────────────────────────────────────────────────────────────

def bean_jc_profile(
    jc_a_per_mm2: float,
    filament_radius_m: float,
    applied_field_t: float,
) -> CriticalStateResult:
    """Bean 임계상태 모델 — Jc = const.

    침투 깊이: d* = H_app / Jc  (H_app < H* = Jc·d/2 이면 부분침투)
    자화: M = -Jc·d*(1 - H_app/H*)/2  [부분침투]
         M = -Jc·d/3                   [완전침투, H_app ≥ H*]
    """
    jc_si = jc_a_per_mm2 * 1.0e6
    H_app = applied_field_t / _MU0
    H_star = jc_si * filament_radius_m   # 완전침투 임계 자기장

    if H_star <= 0.0:
        return CriticalStateResult(
            model="Bean", jc_local_a_per_mm2=jc_a_per_mm2,
            penetration_depth_m=0.0, magnetization_a_per_m=0.0,
            hysteresis_loss_j_per_m3=0.0, e_field_v_per_m=_EC,
        )

    if H_app >= H_star:
        # 완전침투
        d_star = filament_radius_m
        M = -jc_si * filament_radius_m / 3.0
        fully_penetrated = True
    else:
        # 부분침투
        d_star = H_app / jc_si
        M = -jc_si * d_star * (1.0 - H_app / H_star) / 2.0
        fully_penetrated = False

    Q = (4.0 / 3.0) * _MU0 * jc_si * filament_radius_m * applied_field_t if fully_penetrated else 0.0

    return CriticalStateResult(
        model="Bean",
        jc_local_a_per_mm2=jc_a_per_mm2,
        penetration_depth_m=d_star,
        magnetization_a_per_m=M,
        hysteresis_loss_j_per_m3=max(0.0, Q),
        e_field_v_per_m=_EC,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Kim 모델
# ─────────────────────────────────────────────────────────────────────────────

def kim_jc_profile(
    jc0_a_per_mm2: float,
    b0_t: float,
    filament_radius_m: float,
    applied_field_t: float,
) -> CriticalStateResult:
    """Kim 임계상태 모델 — Jc = Jc0 / (1 + B/B0).

    b0_t: Kim 파라미터 (재료별 경험값)
      NbTi  : ~0.3 T
      Nb3Sn : ~0.5 T
      REBCO : ~5.0 T
    """
    jc_local = jc0_a_per_mm2 / (1.0 + max(0.0, applied_field_t) / max(1e-6, b0_t))
    jc_si = jc_local * 1.0e6
    H_app = applied_field_t / _MU0
    H_star = jc_si * filament_radius_m

    d_star = min(filament_radius_m, H_app / jc_si) if jc_si > 0.0 else 0.0
    full = d_star >= filament_radius_m
    M = -jc_si * filament_radius_m / 3.0 if full else -jc_si * d_star * 0.5

    Q = (4.0 / 3.0) * _MU0 * jc_si * filament_radius_m * applied_field_t if full else 0.0
    e = ej_power_law(jc_si, jc_si, n_value=30.0)

    return CriticalStateResult(
        model="Kim",
        jc_local_a_per_mm2=jc_local,
        penetration_depth_m=d_star,
        magnetization_a_per_m=M,
        hysteresis_loss_j_per_m3=max(0.0, Q),
        e_field_v_per_m=e,
    )


# ─────────────────────────────────────────────────────────────────────────────
# E-J 멱함수 임계상태
# ─────────────────────────────────────────────────────────────────────────────

def power_law_state(
    material: MaterialCandidate,
    operating_current_density_a_per_mm2: float,
    applied_field_t: float,
    filament_radius_m: float,
    n_value: float = 30.0,
) -> CriticalStateResult:
    """E-J 멱함수 기반 — 운전 전류밀도에서의 E 필드와 자화 계산."""
    t_op = 4.2   # 대표 운전 온도 (K), 간략화
    b_frac = min(0.999, applied_field_t / material.bc2_t)
    t_frac = min(0.999, t_op / material.tc_k)
    jc_local = material.jc_a_per_mm2_77k * (1.0 - t_frac) * (1.0 - b_frac) / material.anisotropy

    j_op = operating_current_density_a_per_mm2
    e_field = ej_power_law(j_op * 1e6, jc_local * 1e6, n_value)

    # Bean 모델로 자화/손실 추정
    bean = bean_jc_profile(jc_local, filament_radius_m, applied_field_t)

    return CriticalStateResult(
        model="PowerLaw",
        jc_local_a_per_mm2=jc_local,
        penetration_depth_m=bean.penetration_depth_m,
        magnetization_a_per_m=bean.magnetization_a_per_m,
        hysteresis_loss_j_per_m3=bean.hysteresis_loss_j_per_m3,
        e_field_v_per_m=e_field,
    )
