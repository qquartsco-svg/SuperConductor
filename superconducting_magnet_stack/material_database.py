"""
material_database.py — 6대 초전도 패밀리 물성 데이터베이스  (v1.0)

지원 재료
──────────
NbTi      : LTS, 입자가속기 쌍극자/사극자 표준 (LHC 메인 코일)
Nb3Sn     : LTS, 고자기장 응용 (HL-LHC, ITER TF-lead)
REBCO     : HTS, 융합로 TF코일·SMES (SPARC, K-DEMO)
BSCCO-2212: HTS, 고자기장 삽입코일 (>25 T 하이브리드)
BSCCO-2223: HTS, 전력케이블·전류리드 (모노필라멘트 테이프)
MgB2      : MTS, MRI·온보드 자기냉각 (가볍고 경제적)

물성 출처
──────────
NbTi   : Bottura (1999) IEEE Trans. Appl. Supercond. 9, 1521
Nb3Sn  : Summers et al. (1991) IEEE Trans. Magn. 27, 2041
REBCO  : Fietz et al. (2002) Physica C 372, 1200 · AMSC datasheet
BSCCO  : Malozemoff et al. (2012) chapter in HTS Conductors
MgB2   : Tomsic et al. (2007) Physica C 456, 203

stdlib only — no external dependencies.
"""
from __future__ import annotations

import math
from typing import Dict, Optional

from .contracts import MaterialCandidate, MaterialRecord


# ─────────────────────────────────────────────────────────────────────────────
# 레지스트리
# ─────────────────────────────────────────────────────────────────────────────

_REGISTRY: Dict[str, MaterialRecord] = {
    "NbTi": MaterialRecord(
        name="NbTi",
        tc0_k=9.3,
        bc20_t=14.5,
        jc_ref_a_per_mm2=3000.0,
        jc_ref_temp_k=4.2,
        jc_ref_field_t=5.0,
        anisotropy_factor=1.0,
        strain_sensitivity_c=900.0,
        conductor_family="LTS",
        typical_filament_dia_um=6.0,
        cu_sc_ratio=1.8,
    ),
    "Nb3Sn": MaterialRecord(
        name="Nb3Sn",
        tc0_k=18.3,
        bc20_t=28.0,
        jc_ref_a_per_mm2=2500.0,
        jc_ref_temp_k=4.2,
        jc_ref_field_t=12.0,
        anisotropy_factor=1.0,
        strain_sensitivity_c=920.0,
        conductor_family="LTS",
        typical_filament_dia_um=3.0,
        cu_sc_ratio=1.5,
    ),
    "REBCO": MaterialRecord(
        name="REBCO",
        tc0_k=92.0,
        bc20_t=120.0,
        jc_ref_a_per_mm2=500.0,
        jc_ref_temp_k=77.0,
        jc_ref_field_t=0.0,
        anisotropy_factor=5.0,
        strain_sensitivity_c=0.0,          # 테이프: 폴리노미얼 모델 사용
        conductor_family="HTS",
        typical_filament_dia_um=1.0,       # 코팅 두께 기준
        cu_sc_ratio=2.0,
    ),
    "BSCCO-2212": MaterialRecord(
        name="BSCCO-2212",
        tc0_k=95.0,
        bc20_t=250.0,
        jc_ref_a_per_mm2=200.0,
        jc_ref_temp_k=4.2,
        jc_ref_field_t=20.0,
        anisotropy_factor=50.0,
        strain_sensitivity_c=0.0,
        conductor_family="HTS",
        typical_filament_dia_um=8.0,
        cu_sc_ratio=3.0,
    ),
    "BSCCO-2223": MaterialRecord(
        name="BSCCO-2223",
        tc0_k=110.0,
        bc20_t=200.0,
        jc_ref_a_per_mm2=150.0,
        jc_ref_temp_k=77.0,
        jc_ref_field_t=0.0,
        anisotropy_factor=40.0,
        strain_sensitivity_c=0.0,
        conductor_family="HTS",
        typical_filament_dia_um=4.0,
        cu_sc_ratio=2.5,
    ),
    "MgB2": MaterialRecord(
        name="MgB2",
        tc0_k=39.0,
        bc20_t=15.0,
        jc_ref_a_per_mm2=800.0,
        jc_ref_temp_k=4.2,
        jc_ref_field_t=5.0,
        anisotropy_factor=4.0,
        strain_sensitivity_c=0.0,
        conductor_family="MTS",
        typical_filament_dia_um=20.0,
        cu_sc_ratio=2.0,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# 공개 API
# ─────────────────────────────────────────────────────────────────────────────

def get_material(name: str) -> MaterialRecord:
    """재료 이름으로 MaterialRecord 반환. 없으면 ValueError."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unknown material '{name}'. Available: {available}")
    return _REGISTRY[name]


def list_materials() -> list[str]:
    """사용 가능한 재료 이름 목록 반환."""
    return sorted(_REGISTRY.keys())


def to_material_candidate(record: MaterialRecord) -> MaterialCandidate:
    """MaterialRecord → MaterialCandidate 변환 (기존 assess_* 함수와 호환)."""
    return MaterialCandidate(
        name=record.name,
        tc_k=record.tc0_k,
        jc_a_per_mm2_77k=record.jc_ref_a_per_mm2,
        bc2_t=record.bc20_t,
        anisotropy=record.anisotropy_factor,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 임계면 물리 함수
# ─────────────────────────────────────────────────────────────────────────────

def bc2_at_temp(record: MaterialRecord, temp_k: float) -> float:
    """상한임계자기장 Bc2(T) 계산 (T).

    LTS  : Bc2(T) = Bc20 × (1 − (T/Tc0)²)       [Werthamer-Helfand-Hohenberg 근사]
    HTS  : Bc2(T) = Bc20 × (1 − T/Tc0)^1.5      [REBCO/BSCCO 경험적 지수]
    MgB2 : Bc2(T) = Bc20 × (1 − (T/Tc0)^1.7)    [이방성 Bc2_ab 기준]
    """
    t = max(0.0, min(1.0 - 1e-9, temp_k / record.tc0_k))
    if record.conductor_family == "LTS":
        return record.bc20_t * (1.0 - t * t)
    elif record.conductor_family == "MTS":
        return record.bc20_t * (1.0 - t ** 1.7)
    else:  # HTS
        return record.bc20_t * (1.0 - t ** 1.5)


def tc_at_field(record: MaterialRecord, field_t: float) -> float:
    """자기장 하 임계온도 Tc(B) 계산 (K).

    역산: Bc2(Tc(B)) = B → Tc 풀이
    LTS  : Tc(B) = Tc0 × sqrt(1 − B/Bc20)
    HTS  : Tc(B) = Tc0 × (1 − B/Bc20)^(2/3)
    MgB2 : Tc(B) = Tc0 × (1 − B/Bc20)^(1/1.7)
    """
    b_frac = max(0.0, min(0.9999, field_t / record.bc20_t))
    if record.conductor_family == "LTS":
        return record.tc0_k * math.sqrt(1.0 - b_frac)
    elif record.conductor_family == "MTS":
        return record.tc0_k * (1.0 - b_frac) ** (1.0 / 1.7)
    else:
        return record.tc0_k * (1.0 - b_frac) ** (2.0 / 3.0)


def jc_critical_surface(
    record: MaterialRecord,
    temp_k: float,
    field_t: float,
    strain_epsilon: float = 0.0,
) -> float:
    """임계면 Jc(T, B, ε) 계산 (A/mm²).

    각 패밀리별 파라미터화:

    NbTi  : Bottura (1999) — C₀/B × bᵅ × (1-b)ᵝ × (1-t²)ᵞ
             C0=2.32e4 A·T/mm², α=0.57, β=0.9, γ=2.3
    Nb3Sn : Summers (1991) — C/√B × b⁰·⁵ × (1-b)² × (1-t²)²
             strain 보정: s(ε) 포함
    REBCO : 경험적 멱함수 — Jc0 × (1-T/Tc)^1.5 × (1-B/Bc2)^0.5
    BSCCO : 지수형 — Jc0 × (1-T/Tc)^2 × exp(-B/B_char)
    MgB2  : Jc0 × exp(-B/B0) × (1-T/Tc)^1.5  [B0=4T, B‖c]
    """
    if temp_k <= 0.0 or field_t < 0.0:
        return 0.0

    bc2 = bc2_at_temp(record, temp_k)
    if bc2 <= 0.0 or field_t >= bc2:
        return 0.0
    if temp_k >= record.tc0_k:
        return 0.0

    t = temp_k / record.tc0_k        # 환산 온도
    b = field_t / bc2                 # 환산 자기장

    if record.name == "NbTi":
        # Bottura 파라미터화
        C0 = 2.32e4  # A·T/mm²
        alpha, beta, gamma = 0.57, 0.9, 2.3
        if field_t < 0.01:
            field_t = 0.01  # 0-field 발산 방지
        jc = (C0 / field_t) * (b ** alpha) * ((1.0 - b) ** beta) * ((1.0 - t * t) ** gamma)
        # Ekin 변형률 보정
        if abs(strain_epsilon) > 1e-6:
            from .strain_effects import _ekin_s_nbti  # type: ignore[attr-defined]
            jc *= _ekin_s_nbti(strain_epsilon)
        return max(0.0, jc)

    elif record.name == "Nb3Sn":
        # Summers 파라미터화
        C = 1.8e4  # A·T^0.5/mm²
        if field_t < 0.01:
            field_t = 0.01
        jc = (C / math.sqrt(field_t)) * (b ** 0.5) * ((1.0 - b) ** 2.0) * ((1.0 - t * t) ** 2.0)
        # Ekin 변형률 보정 (strain_effects에서 s(ε) 계산)
        if abs(strain_epsilon) > 1e-6 and record.strain_sensitivity_c > 0:
            from .strain_effects import ekin_devantay_s
            s_eps = ekin_devantay_s(strain_epsilon, epsilon_0m=-0.003)
            jc *= math.sqrt(max(0.0, s_eps))
        return max(0.0, jc)

    elif record.name == "REBCO":
        # 경험적 멱함수 (c축 전송방향)
        jc0 = record.jc_ref_a_per_mm2
        jc = jc0 * ((1.0 - t) ** 1.5) * ((1.0 - b) ** 0.5)
        # 폴리노미얼 변형률 보정
        if abs(strain_epsilon) > 1e-6:
            from .strain_effects import rebco_jc_strain_factor
            jc *= rebco_jc_strain_factor(strain_epsilon)
        return max(0.0, jc)

    elif record.name in ("BSCCO-2212", "BSCCO-2223"):
        # 2D 팬케이크 와류 — 지수형 감쇠
        jc0 = record.jc_ref_a_per_mm2
        b_char = record.bc20_t * 0.05  # 특성 자기장 (경험적)
        field_eff = max(field_t, 0.001)
        jc = jc0 * ((1.0 - t) ** 2.0) * math.exp(-field_eff / b_char)
        return max(0.0, jc)

    elif record.name == "MgB2":
        # 지수형 플럭스 피닝 (Bc‖c 기준)
        jc0 = record.jc_ref_a_per_mm2
        B0 = 4.0  # T, 특성 자기장
        field_eff = max(field_t, 0.001)
        jc = jc0 * math.exp(-field_eff / B0) * ((1.0 - t) ** 1.5)
        return max(0.0, jc)

    else:
        # 범용 쌍선형 derating
        jc0 = record.jc_ref_a_per_mm2
        return max(0.0, jc0 * (1.0 - t) * (1.0 - b) / record.anisotropy_factor)
