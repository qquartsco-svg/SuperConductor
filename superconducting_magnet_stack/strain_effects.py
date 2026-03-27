"""
strain_effects.py — 변형률 의존 초전도 물성  (v1.0)

모델 개요
──────────
Nb3Sn  : Ekin-Devantay-Berger 변형률 함수 s(ε)
          Jc(ε,T,B) = Jc(T,B)|₀ × √s(ε)
REBCO  : 경험적 폴리노미얼 Jc(ε)/Jc(0)
          Jc(ε)/Jc(0) = 1 + a₁ε + a₂ε²  (비가역 한계 이하)
NbTi   : Ekin 이차형 근사 s(ε) ~ 1 - C×ε²

임계 변형률 (비가역)
  Nb3Sn : ε_irr ≈ 0.50%  (취성, 브리틀 세라믹 필라멘트)
  REBCO : ε_irr ≈ 0.45%  (금속 기판 덕분에 연성)
  NbTi  : ε_irr ≈ 0.30%  (연성, Jc 회복 불가 영역)

참조
──────
Ekin & Bray (1983) Cryogenics 23, 654
Devantay et al. (1981) J. Mater. Sci. 16, 2145
Fujita et al. (2019) IEEE Trans. Appl. Supercond. 29, 8400405
"""
from __future__ import annotations

import math

from .contracts import MaterialCandidate, MaterialRecord, StrainEffectsResult

# 기본 비가역 변형률 한계
_IRR_NB3SN = 0.005   # 0.50%
_IRR_REBCO = 0.0045  # 0.45%
_IRR_NBTI  = 0.003   # 0.30%
_IRR_DEFAULT = 0.006


# ─────────────────────────────────────────────────────────────────────────────
# NbTi 내부 도우미 (material_database.py에서 import)
# ─────────────────────────────────────────────────────────────────────────────

def _ekin_s_nbti(epsilon: float, c_nbti: float = 900.0) -> float:
    """NbTi Ekin 이차형 — s(ε) = 1 - C×ε²  [비가역 이하에서만 유효]."""
    irr = _IRR_NBTI
    if abs(epsilon) > irr:
        return 0.0
    return max(0.0, 1.0 - c_nbti * epsilon ** 2)


# ─────────────────────────────────────────────────────────────────────────────
# Nb3Sn: Ekin-Devantay-Berger
# ─────────────────────────────────────────────────────────────────────────────

def ekin_devantay_s(
    epsilon_applied: float,
    epsilon_0m: float = -0.003,
    epsilon_irr: float = _IRR_NB3SN,
    c1: float = 900.0,
    c2: float = 800.0,
    u: float = 1.7,
) -> float:
    """Ekin-Devantay-Berger s(ε) 함수 for Nb3Sn.

    s(ε) = 1 - C₁|ε_eff|^u - C₂ε_eff²    [ε < ε_irr]
    s(ε) = 0                                [ε ≥ ε_irr]

    epsilon_0m: 내재 예압축 (강철 지지대 → -0.3% 전형)
    C₁=900, C₂=800, u=1.7 — Devantay 1981 평균값
    """
    eps_eff = epsilon_applied - epsilon_0m
    if abs(eps_eff) >= epsilon_irr:
        return 0.0
    s = 1.0 - c1 * (abs(eps_eff) ** u) - c2 * (eps_eff ** 2)
    return max(0.0, s)


# ─────────────────────────────────────────────────────────────────────────────
# REBCO: 경험적 폴리노미얼
# ─────────────────────────────────────────────────────────────────────────────

def rebco_jc_strain_factor(
    epsilon: float,
    a1: float = 1.0,
    a2: float = -2.0e4,
    a3: float = 0.0,
    epsilon_irr: float = _IRR_REBCO,
) -> float:
    """REBCO Jc(ε)/Jc(0) 폴리노미얼 근사 (c축 변형 기준).

    Jc(ε)/Jc(0) = 1 + a₁ε + a₂ε²
    ε_irr = 0.45% — 초과 시 비가역 손상
    Fujita et al. (2019) 계수 기반.
    """
    if abs(epsilon) > epsilon_irr:
        return 0.0
    factor = 1.0 + a1 * epsilon + a2 * epsilon ** 2 + a3 * epsilon ** 3
    return max(0.0, min(1.5, factor))  # 비물리적 증폭 제한


# ─────────────────────────────────────────────────────────────────────────────
# 변형률 하 임계면 (Nb3Sn — Tc*, Bc2* 수정)
# ─────────────────────────────────────────────────────────────────────────────

def tc_strain_nb3sn(
    tc0_k: float,
    s_epsilon: float,
) -> float:
    """Nb3Sn Tc*(ε) = Tc0_max × s(ε)^(1/3)."""
    return tc0_k * (max(0.0, s_epsilon) ** (1.0 / 3.0))


def bc2_strain_nb3sn(
    bc20_t: float,
    s_epsilon: float,
    temp_k: float,
    tc_star_k: float,
) -> float:
    """Nb3Sn Bc2*(ε,T) = Bc20_max × s(ε) × (1 − (T/Tc*)²)."""
    if tc_star_k <= 0.0 or temp_k >= tc_star_k:
        return 0.0
    t_star = temp_k / tc_star_k
    return bc20_t * max(0.0, s_epsilon) * (1.0 - t_star * t_star)


# ─────────────────────────────────────────────────────────────────────────────
# 범용 dispatch
# ─────────────────────────────────────────────────────────────────────────────

def jc_with_strain(
    record: MaterialRecord,
    jc0_a_per_mm2: float,
    temp_k: float,
    field_t: float,
    epsilon: float,
    epsilon_0m: float = -0.003,
) -> float:
    """패밀리별 변형률 보정 Jc 반환 (A/mm²)."""
    name = record.name

    if name == "Nb3Sn":
        s = ekin_devantay_s(epsilon, epsilon_0m=epsilon_0m)
        return jc0_a_per_mm2 * math.sqrt(max(0.0, s))

    elif name == "REBCO":
        return jc0_a_per_mm2 * rebco_jc_strain_factor(epsilon)

    elif name == "NbTi":
        return jc0_a_per_mm2 * _ekin_s_nbti(epsilon)

    else:
        # BSCCO, MgB2: 변형률 민감도 낮음 — 무시
        return jc0_a_per_mm2


def assess_strain_effects(
    record: MaterialRecord,
    design: "MagnetDesign",  # type: ignore[name-defined]
    epsilon_applied: float,
    epsilon_0m: float = -0.003,
) -> StrainEffectsResult:
    """변형률이 Jc/Tc/Bc2에 미치는 영향 종합 평가."""
    from .contracts import MagnetDesign  # 지연 import
    name = record.name

    if name == "Nb3Sn":
        s_eps = ekin_devantay_s(epsilon_applied, epsilon_0m=epsilon_0m)
        eps_eff = epsilon_applied - epsilon_0m
        irr_exceeded = abs(eps_eff) >= _IRR_NB3SN
        jc_factor = math.sqrt(max(0.0, s_eps)) if not irr_exceeded else 0.0
        tc_star = tc_strain_nb3sn(record.tc0_k, s_eps)
        bc2_star = bc2_strain_nb3sn(record.bc20_t, s_eps, design.operating_temp_k if hasattr(design, 'operating_temp_k') else 4.2, tc_star)
        rec = "변형률 허용 범위 내" if not irr_exceeded else "비가역 손상 — 코일 재권선 필요"

    elif name == "REBCO":
        s_eps = rebco_jc_strain_factor(epsilon_applied)
        eps_eff = epsilon_applied
        irr_exceeded = abs(epsilon_applied) >= _IRR_REBCO
        jc_factor = s_eps if not irr_exceeded else 0.0
        tc_star = record.tc0_k * (jc_factor ** 0.1) if jc_factor > 0 else 0.0
        bc2_star = record.bc20_t * jc_factor
        rec = "REBCO 변형률 허용" if not irr_exceeded else "비가역 손상 — 테이프 교체 필요"

    elif name == "NbTi":
        s_eps = _ekin_s_nbti(epsilon_applied)
        eps_eff = epsilon_applied
        irr_exceeded = abs(epsilon_applied) >= _IRR_NBTI
        jc_factor = s_eps
        tc_star = record.tc0_k * (s_eps ** 0.2)
        bc2_star = record.bc20_t * s_eps
        rec = "NbTi 연성 — 변형률 영향 미미" if not irr_exceeded else "비가역 영역 진입"

    else:
        s_eps = 1.0
        eps_eff = epsilon_applied
        irr_exceeded = abs(epsilon_applied) > _IRR_DEFAULT
        jc_factor = 1.0
        tc_star = record.tc0_k
        bc2_star = record.bc20_t
        rec = "변형률 민감도 낮음"

    return StrainEffectsResult(
        epsilon_applied=epsilon_applied,
        epsilon_effective=eps_eff,
        s_epsilon=s_eps,
        jc_strain_factor=jc_factor,
        tc_strain_k=tc_star,
        bc2_strain_t=bc2_star,
        is_irreversible=irr_exceeded,
        recommendation=rec,
    )
