"""
pinning.py — 보텍스 피닝 / 플럭스 크리프 / 비가역선  (v1.0)

물리 모델
──────────
피닝 에너지 (Anderson-Kim):
  U₀ = Jc × B × V_bundle
  V_bundle ~ (ξ_ab² × λ_ab)   [집단 피닝 부피, 결맞음 길이 기반]

플럭스 크리프 (Anderson-Kim 열적 활성화):
  dJc/dt / Jc = -(kB·T / U₀) × f₀ × exp(-U₀/kBT)
  Jc(t) = Jc0 × [1 - (kBT/U₀) × ln(t/t₀)]
  t₀ ~ 1 s (정규화 기준)

비가역선 Hirr(T)
  LTS  : Hirr(T) ≈ Bc2(T)         [강한 피닝]
  REBCO: Hirr(T) = Hirr0 × (1−T/Tc)^1.5    [Houghton 경험식]
  BSCCO: Hirr(T) = Hirr0 × (1−T/Tc)²·exp(-kT/(Φ₀·d·λ²))  [2D 팬케이크 녹음]

참조
──────
Anderson (1962) Phys. Rev. Lett. 9, 309
Kim et al. (1963) Phys. Rev. Lett. 11, 196
Houghton et al. (1989) Phys. Rev. B 40, 6763
"""
from __future__ import annotations

import math

from .contracts import CryoProfile, MagnetDesign, MaterialRecord, PinningResult

_KB  = 1.380649e-23   # J/K  Boltzmann
_PHI0 = 2.067833848e-15  # Wb  자속 양자


# ─────────────────────────────────────────────────────────────────────────────
# 피닝 에너지
# ─────────────────────────────────────────────────────────────────────────────

def vortex_pinning_energy_j(
    jc_a_per_m2: float,
    field_t: float,
    bundle_volume_m3: float = 1e-27,
) -> float:
    """보텍스 피닝 에너지 U₀ = Jc × B × V_bundle  (J).

    bundle_volume_m3: 집단 피닝 부피
      NbTi  ~ 1e-27 m³  (ξ ~ 4 nm, λ ~ 100 nm)
      Nb3Sn ~ 5e-28 m³  (ξ ~ 3 nm)
      REBCO ~ 1e-28 m³  (ξ_ab ~ 1.5 nm)
    """
    return max(0.0, jc_a_per_m2 * max(0.0, field_t) * bundle_volume_m3)


# ─────────────────────────────────────────────────────────────────────────────
# Anderson-Kim 플럭스 크리프
# ─────────────────────────────────────────────────────────────────────────────

def anderson_kim_creep_rate(
    pinning_energy_j: float,
    temp_k: float,
    attempt_freq_hz: float = 1e11,
) -> float:
    """플럭스 크리프율 dJc/dt / Jc0  (s⁻¹).

    rate = (kBT / U₀) × f₀ × exp(-U₀ / kBT)
    """
    if pinning_energy_j <= 0.0 or temp_k <= 0.0:
        return 0.0
    kbt = _KB * temp_k
    exponent = pinning_energy_j / kbt
    # exp 오버플로우 방지
    if exponent > 600:
        return 0.0
    rate = (kbt / pinning_energy_j) * attempt_freq_hz * math.exp(-exponent)
    return rate


def jc_after_creep(
    jc0_a_per_m2: float,
    pinning_energy_j: float,
    temp_k: float,
    elapsed_s: float,
    t0_s: float = 1.0,
) -> float:
    """Anderson-Kim 로그 크리프: Jc(t) = Jc0 × [1 - (kBT/U₀)×ln(t/t₀)]  (A/m²).

    elapsed_s: 경과 시간 (s)
    t0_s: 정규화 기준 시간 (1 s 전형)
    """
    if pinning_energy_j <= 0.0 or elapsed_s <= 0.0 or temp_k <= 0.0:
        return jc0_a_per_m2
    if elapsed_s < t0_s:
        return jc0_a_per_m2
    kbt = _KB * temp_k
    creep_factor = (kbt / pinning_energy_j) * math.log(elapsed_s / t0_s)
    return max(0.0, jc0_a_per_m2 * (1.0 - creep_factor))


# ─────────────────────────────────────────────────────────────────────────────
# 비가역선 Hirr(T)
# ─────────────────────────────────────────────────────────────────────────────

def irreversibility_field_t(
    record: MaterialRecord,
    temp_k: float,
) -> float:
    """비가역선 Hirr(T) (T).

    LTS  : Hirr ≈ Bc2(T)  (강한 피닝 → 비가역선 ≈ 상한임계선)
    HTS  : Houghton 경험식 Hirr = Bc20 × (1−T/Tc)^n
    BSCCO: 2D 팬케이크 녹음으로 Hirr << Bc2
    MgB2 : LTS처럼 처리
    """
    from .material_database import bc2_at_temp

    if temp_k >= record.tc0_k:
        return 0.0
    t = temp_k / record.tc0_k

    if record.conductor_family == "LTS":
        # LTS: 비가역선 ≈ Bc2(T)
        return bc2_at_temp(record, temp_k)

    elif record.conductor_family == "MTS":
        # MgB2: LTS-like
        return bc2_at_temp(record, temp_k) * 0.85  # 약간 낮음

    elif record.name in ("BSCCO-2212", "BSCCO-2223"):
        # 2D 팬케이크 녹음 — 급격한 Hirr 감쇠
        # Hirr(T) = Bc20 × (1 - T/Tc)^2.5
        hirr = record.bc20_t * ((1.0 - t) ** 2.5)
        return hirr

    else:
        # REBCO: Houghton 경험식 n=1.5
        hirr = record.bc20_t * ((1.0 - t) ** 1.5)
        return hirr


# ─────────────────────────────────────────────────────────────────────────────
# 종합 피닝 평가
# ─────────────────────────────────────────────────────────────────────────────

def assess_pinning(
    record: MaterialRecord,
    cryo: CryoProfile,
    design: MagnetDesign,
    elapsed_s: float = 3.156e7,    # 기본: 1년
) -> PinningResult:
    """보텍스 피닝 / 플럭스 크리프 / 비가역선 종합 평가.

    elapsed_s: 운전 후 경과 시간 (초) — 크리프로 인한 Jc 감쇠 추정
    """
    from .material_database import jc_critical_surface

    temp_k  = cryo.operating_temp_k
    field_t = design.target_field_t

    jc0 = jc_critical_surface(record, temp_k, field_t)
    jc0_si = jc0 * 1.0e6   # A/m²

    # 패밀리별 대표 피닝 부피 (m³)
    v_bundle = {
        "NbTi":      1.0e-27,
        "Nb3Sn":     5.0e-28,
        "REBCO":     1.0e-28,
        "BSCCO-2212": 5.0e-29,
        "BSCCO-2223": 5.0e-29,
        "MgB2":      2.0e-27,
    }.get(record.name, 1.0e-27)

    u0 = vortex_pinning_energy_j(jc0_si, field_t, v_bundle)
    creep_rate = anderson_kim_creep_rate(u0, temp_k)
    jc_creep = jc_after_creep(jc0_si, u0, temp_k, elapsed_s)
    hirr = irreversibility_field_t(record, temp_k)
    above_irr = field_t > hirr

    return PinningResult(
        pinning_energy_j=u0,
        flux_creep_rate_normalized=creep_rate,
        jc_after_creep_a_per_mm2=jc_creep * 1e-6,
        irreversibility_field_t=hirr,
        is_above_irreversibility_line=above_irr,
    )
