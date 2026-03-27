"""
application_presets.py — 실제 응용 사례 프리셋  (v1.0)

5가지 대표 응용 사례
──────────────────────
1. LHC 이극 자석 (NbTi, 8.33 T, 4.2 K)
   - CERN LHC 가속기 주 쌍극 자석
   - 1232개 자석, 각 14.3 m

2. HL-LHC 쿼드루폴 (Nb3Sn, 12 T, 1.9 K)
   - High-Luminosity LHC 업그레이드
   - MQXF 내부 트리플렛 쿼드루폴

3. SPARC 토카막 TF 코일 (REBCO, 20 T, 20 K)
   - MIT/CFS 소형 고자기장 핵융합로
   - REBCO REBCO HTS 덕분에 20 K 운전 가능

4. MgB2 MRI 자석 (MgB2, 1.5 T, 20 K)
   - 상압 냉각 (GM 냉동기, 액체 헬륨 불필요)
   - 병원용 1.5T / 3T MRI 시스템

5. SMES 에너지 저장 (NbTi, 6 T, 4.2 K)
   - Superconducting Magnetic Energy Storage
   - 전력망 주파수 안정화용

참조
──────
Evans & Bryant (2008) "LHC Machine" JINST 3 S08001
Zlobin et al. (2015) "Nb3Sn Quadrupoles for HL-LHC" IEEE TAS 25
Whyte et al. (2020) "Tokamaks from Attached to Detached" NF 60
Sumption et al. (2015) "MgB2 for MRI" IEEE TAS 25
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .contracts import (
    ApplicationPreset, CryoProfile, MagnetDesign, MaterialCandidate,
    PresetComparisonReport,
)


# ─────────────────────────────────────────────────────────────────────────────
# 프리셋 정의
# ─────────────────────────────────────────────────────────────────────────────

def get_lhc_dipole_preset() -> ApplicationPreset:
    """CERN LHC 이극 자석 프리셋 (NbTi)."""
    material = MaterialCandidate(
        name="NbTi",
        jc_a_per_mm2_77k=3000.0,
        tc_k=9.2,
        bc2_t=14.5,
        anisotropy=1.0,
    )
    cryo = CryoProfile(
        operating_temp_k=4.2,
        cooling_capacity_w=100.0,
        heat_load_w=30.0,
    )
    design = MagnetDesign(
        target_field_t=8.33,
        operating_current_a=11850.0,
        inductance_h=0.11,
        conductor_cross_section_mm2=27.0,
        coil_length_m=14.3,
    )
    return ApplicationPreset(
        name="LHC Main Dipole (MB)",
        material=material,
        cryo=cryo,
        design=design,
        description=(
            "CERN LHC 8.33 T NbTi 이극 자석. "
            "1232개 × 14.3 m. 27 mm² 케이블 단면적. "
            "1.9 K (He II) 운전으로 Jc 향상."
        ),
        target_application="가속기 편향 자석",
        key_challenges=[
            "8.33 T 고자기장에서 NbTi 임계전류 마진",
            "전체 27 km 링의 ±1ppm 자기장 균일도",
            "연간 1~2회 쿨다운/워밍업 피로 수명",
        ],
    )


def get_hl_lhc_quadrupole_preset() -> ApplicationPreset:
    """HL-LHC 내부 트리플렛 쿼드루폴 (Nb3Sn)."""
    material = MaterialCandidate(
        name="Nb3Sn",
        jc_a_per_mm2_77k=2500.0,
        tc_k=18.3,
        bc2_t=28.0,
        anisotropy=1.0,
    )
    cryo = CryoProfile(
        operating_temp_k=1.9,
        cooling_capacity_w=50.0,
        heat_load_w=10.0,
    )
    design = MagnetDesign(
        target_field_t=12.0,
        operating_current_a=16470.0,
        inductance_h=0.25,
        conductor_cross_section_mm2=22.0,
        coil_length_m=7.15,
    )
    return ApplicationPreset(
        name="HL-LHC MQXF Quadrupole",
        material=material,
        cryo=cryo,
        design=design,
        description=(
            "High-Luminosity LHC 내부 쿼드루폴. "
            "Nb3Sn 12 T, 1.9 K. Rutherford 케이블. "
            "HL-LHC 루미노시티 × 10 달성의 핵심."
        ),
        target_application="가속기 집속 쿼드루폴",
        key_challenges=[
            "Nb3Sn 취성 — 코일 와인딩 후 열처리 필요",
            "12 T 운전 중 변형률 관리 (ε < 0.5%)",
            "LHC 호환 설치 크기 제약",
        ],
    )


def get_sparc_tf_preset() -> ApplicationPreset:
    """MIT/CFS SPARC 토카막 TF 코일 (REBCO HTS)."""
    material = MaterialCandidate(
        name="REBCO",
        jc_a_per_mm2_77k=500.0,
        tc_k=92.0,
        bc2_t=120.0,
        anisotropy=5.0,
    )
    cryo = CryoProfile(
        operating_temp_k=20.0,
        cooling_capacity_w=5000.0,
        heat_load_w=1500.0,
    )
    design = MagnetDesign(
        target_field_t=20.0,
        operating_current_a=40000.0,
        inductance_h=15.0,
        conductor_cross_section_mm2=40.0,
        coil_length_m=8.0,
    )
    return ApplicationPreset(
        name="SPARC TF Coil (REBCO)",
        material=material,
        cryo=cryo,
        design=design,
        description=(
            "MIT SPARC 소형 핵융합로 토로이달 자기장 코일. "
            "REBCO 20 T HTS. GM 냉동기 20 K 운전 가능. "
            "R=1.85 m, a=0.57 m, B₀=12.2 T 중심자기장."
        ),
        target_application="핵융합 토카막 TF 코일",
        key_challenges=[
            "20 T 고자기장에서 REBCO 이방성 (c축 배향)",
            "플라즈마 파열(disruption) 시 퀀치 보호",
            "고방사선 환경 장기 열화",
        ],
    )


def get_mri_preset() -> ApplicationPreset:
    """MgB2 병원용 MRI 자석."""
    material = MaterialCandidate(
        name="MgB2",
        jc_a_per_mm2_77k=800.0,
        tc_k=39.0,
        bc2_t=15.0,
        anisotropy=2.0,
    )
    cryo = CryoProfile(
        operating_temp_k=20.0,
        cooling_capacity_w=20.0,
        heat_load_w=5.0,
    )
    design = MagnetDesign(
        target_field_t=1.5,
        operating_current_a=200.0,
        inductance_h=80.0,
        conductor_cross_section_mm2=3.5,
        coil_length_m=1.2,
    )
    return ApplicationPreset(
        name="MgB2 Conduction-Cooled MRI (1.5T)",
        material=material,
        cryo=cryo,
        design=design,
        description=(
            "MgB2 1.5 T 전도 냉각 MRI 자석. "
            "GM 냉동기 20 K, 액체 헬륨 불필요. "
            "병원 설치 및 유지보수 비용 대폭 절감."
        ),
        target_application="의료용 MRI 시스템",
        key_challenges=[
            "1.5 T 균일도 < 5 ppm (FOV 50 cm)",
            "20 K 운전 중 Jc 감쇠 관리",
            "퀀치 시 자기장 안전 소멸 (환자 보호)",
        ],
    )


def get_smes_preset() -> ApplicationPreset:
    """NbTi SMES 에너지 저장 시스템."""
    material = MaterialCandidate(
        name="NbTi",
        jc_a_per_mm2_77k=3000.0,
        tc_k=9.2,
        bc2_t=14.5,
        anisotropy=1.0,
    )
    cryo = CryoProfile(
        operating_temp_k=4.2,
        cooling_capacity_w=500.0,
        heat_load_w=150.0,
    )
    design = MagnetDesign(
        target_field_t=6.0,
        operating_current_a=3000.0,
        inductance_h=200.0,
        conductor_cross_section_mm2=20.0,
        coil_length_m=100.0,
    )
    return ApplicationPreset(
        name="NbTi SMES (100 MJ class)",
        material=material,
        cryo=cryo,
        design=design,
        description=(
            "100 MJ급 NbTi 초전도 에너지 저장 장치. "
            "E = ½LI² = ½×200×3000² = 900 MJ 수준. "
            "전력망 주파수 안정화, UPS, 순간 전압 보상."
        ),
        target_application="전력망 에너지 저장 (SMES)",
        key_challenges=[
            "고인덕턴스(200 H) 퀀치 보호 — 덤프 에너지 분산",
            "장기(20년+) 운전 AC 손실 최소화",
            "냉각 시스템 신뢰성 (MTBF > 10년)",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 프리셋 레지스트리
# ─────────────────────────────────────────────────────────────────────────────

_PRESET_REGISTRY: Dict[str, ApplicationPreset] = {}


def _ensure_registry() -> None:
    global _PRESET_REGISTRY
    if not _PRESET_REGISTRY:
        _PRESET_REGISTRY = {
            "lhc_dipole":       get_lhc_dipole_preset(),
            "hl_lhc_quad":      get_hl_lhc_quadrupole_preset(),
            "sparc_tf":         get_sparc_tf_preset(),
            "mri_mgb2":         get_mri_preset(),
            "smes":             get_smes_preset(),
        }


def get_preset(name: str) -> Optional[ApplicationPreset]:
    """이름으로 프리셋 반환. 없으면 None."""
    _ensure_registry()
    return _PRESET_REGISTRY.get(name)


def list_presets() -> List[str]:
    """사용 가능한 프리셋 이름 목록."""
    _ensure_registry()
    return list(_PRESET_REGISTRY.keys())


# ─────────────────────────────────────────────────────────────────────────────
# 비교 분석
# ─────────────────────────────────────────────────────────────────────────────

def compare_presets(
    preset_names: Optional[List[str]] = None,
) -> PresetComparisonReport:
    """여러 프리셋 간 핵심 성능 지표 비교.

    비교 지표:
    - Jc @ 운전점 [A/mm²]
    - 저장 에너지 E = ½LI² [MJ]
    - 운전 자기장 [T]
    - 운전 온도 [K]
    - 냉각 방식 (He-4, He-II, 전도 냉각)
    """
    _ensure_registry()
    names = preset_names or list(_PRESET_REGISTRY.keys())

    rows: List[Dict] = []
    for name in names:
        p = _PRESET_REGISTRY.get(name)
        if p is None:
            continue

        mat  = p.material
        cryo = p.cryo
        des  = p.design

        # Jc 운전점 추정
        b_frac = min(0.999, des.target_field_t / max(1.0, mat.bc2_t))
        t_frac = min(0.999, cryo.operating_temp_k / max(1.0, mat.tc_k))
        jc_op  = mat.jc_a_per_mm2_77k * (1.0 - t_frac) * (1.0 - b_frac) / max(0.1, mat.anisotropy)

        # 저장 에너지 [MJ]
        energy_mj = 0.5 * des.inductance_h * (des.operating_current_a ** 2) / 1e6

        # 냉각 방식
        t_op = cryo.operating_temp_k
        if t_op < 2.5:
            cooling = "He-II (초유동 헬륨)"
        elif t_op < 5.0:
            cooling = "He-4 (액체 헬륨)"
        elif t_op < 25.0:
            cooling = "전도 냉각 (GM/PT 냉동기)"
        else:
            cooling = "LN2 (액체 질소) 냉각"

        rows.append({
            "name":         name,
            "preset_name":  p.name,
            "material":     mat.name,
            "field_t":      des.target_field_t,
            "temp_k":       t_op,
            "jc_op_a_per_mm2": round(jc_op, 1),
            "energy_mj":    round(energy_mj, 2),
            "cooling":      cooling,
            "application":  p.target_application,
        })

    # 최고 성능 식별
    if rows:
        best_jc    = max(rows, key=lambda r: r["jc_op_a_per_mm2"])
        best_field = max(rows, key=lambda r: r["field_t"])
        best_energy = max(rows, key=lambda r: r["energy_mj"])
    else:
        best_jc = best_field = best_energy = {}

    summary = (
        f"비교 완료 {len(rows)}개 프리셋. "
        f"최고 Jc: {best_jc.get('preset_name', '-')} "
        f"({best_jc.get('jc_op_a_per_mm2', 0):.0f} A/mm²). "
        f"최고 자기장: {best_field.get('preset_name', '-')} "
        f"({best_field.get('field_t', 0):.1f} T). "
        f"최대 에너지: {best_energy.get('preset_name', '-')} "
        f"({best_energy.get('energy_mj', 0):.0f} MJ)."
    )

    return PresetComparisonReport(
        preset_names=names,
        comparison_table=rows,
        best_jc_preset=best_jc.get("name", ""),
        best_field_preset=best_field.get("name", ""),
        highest_energy_preset=best_energy.get("name", ""),
        summary=summary,
    )
