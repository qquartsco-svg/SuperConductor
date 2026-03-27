"""
fault_tolerance.py — 결함 허용성 분석 / 피로 수명 / MTBF  (v1.0)

세 가지 분석
──────────────
1. Coffin-Manson 피로 수명
   N_f = C × (Δε_p)^(-m)
   Δε_p: 소성 변형률 진폭 (피크-투-피크 / 2)
   C: 연성 계수 (재료별), m: 피로 지수 (~0.5~0.7)

   NbTi  : C = 0.5, m = 0.6  (연성, 높은 수명)
   Nb3Sn : C = 0.2, m = 0.5  (취성 세라믹, 낮은 수명)
   REBCO : C = 0.4, m = 0.55 (금속 기판 덕분에 중간)
   MgB2  : C = 0.3, m = 0.55

2. 안전 계수 (Safety Factor)
   SF_Jc   = Jc_op / Jc_min
   SF_T    = T_limit / T_hotspot
   SF_MIIT = MIIT_limit / MIIT_actual

3. MTBF / 신뢰도 추정
   지수 분포 근사: R(t) = exp(−t/MTBF)
   MTBF 추정: 사이클 수 × 사이클 당 평균 시간
   퀀치 확률: P_quench_per_cycle (경험적)

4. 단일 실패점 (SPoF) 분석
   결함 모드별 영향도 매핑
   임계 경로 식별

참조
──────
Coffin (1954) Trans. ASME 76, 931
Manson (1953) NACA TN-2933
Ekin et al. (2006) Cryogenics 46, 588 (초전도 피로)
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from .contracts import (
    CryoProfile, MagnetDesign, MaterialCandidate,
    FaultToleranceReport,
)


# 재료별 Coffin-Manson 계수 {name: (C, m)}
_CM_PARAMS: Dict[str, Tuple[float, float]] = {
    "NbTi":      (0.50, 0.60),
    "Nb3Sn":     (0.20, 0.50),
    "REBCO":     (0.40, 0.55),
    "BSCCO-2212": (0.15, 0.50),
    "BSCCO-2223": (0.15, 0.50),
    "MgB2":      (0.30, 0.55),
}

# 재료별 임계 변형률 (비가역)
_IRR_STRAIN: Dict[str, float] = {
    "NbTi":      0.003,
    "Nb3Sn":     0.005,
    "REBCO":     0.0045,
    "BSCCO-2212": 0.003,
    "BSCCO-2223": 0.003,
    "MgB2":      0.004,
}

# 쿨다운/워밍업 열사이클 당 열 변형률 [1 사이클]
_THERMAL_STRAIN_PER_CYCLE: Dict[str, float] = {
    "NbTi":      0.0015,   # 4.2 K → 300 K 열팽창 × 2 (왕복)
    "Nb3Sn":     0.0012,
    "REBCO":     0.0010,
    "BSCCO-2212": 0.0008,
    "BSCCO-2223": 0.0008,
    "MgB2":      0.0013,
}


# ─────────────────────────────────────────────────────────────────────────────
# Coffin-Manson 피로 수명
# ─────────────────────────────────────────────────────────────────────────────

def coffin_manson_fatigue_cycles(
    material_name: str,
    strain_amplitude: float,
) -> float:
    """Coffin-Manson 피로 수명 N_f [사이클].

    N_f = C × (Δε)^(-m)
    strain_amplitude: 소성 변형률 진폭 (Δε/2)
    """
    C, m = _CM_PARAMS.get(material_name, (0.30, 0.55))
    if strain_amplitude <= 0.0:
        return float("inf")
    nf = C * (strain_amplitude ** (-m))
    return max(1.0, nf)


def thermal_cycle_lifetime(
    material_name: str,
    cycles_per_year: float = 2.0,
) -> Dict[str, float]:
    """열사이클(쿨다운/워밍업) 기반 피로 수명 추정.

    cycles_per_year: 연간 열사이클 횟수 (실험용: 10~50, 가속기: 1~2)
    """
    strain_amp = _THERMAL_STRAIN_PER_CYCLE.get(material_name, 0.001)
    nf = coffin_manson_fatigue_cycles(material_name, strain_amp)
    years = nf / max(0.1, cycles_per_year)
    return {
        "strain_amplitude": strain_amp,
        "n_cycles_to_failure": nf,
        "estimated_years": min(years, 1e6),  # 물리적 상한
    }


# ─────────────────────────────────────────────────────────────────────────────
# 안전 계수
# ─────────────────────────────────────────────────────────────────────────────

def safety_factors(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    jc_op_a_per_mm2: float,
    hotspot_temp_k: float,
    miit_actual_a2s: float,
    miit_limit_a2s: float = 30.0e6,
    t_hotspot_limit_k: float = 300.0,
    jc_min_fraction: float = 0.30,  # Jc_op > 30% × Jc_77K 기준
) -> Dict[str, float]:
    """세 가지 안전 계수 계산.

    SF_Jc: 전류 마진
    SF_T : 핫스팟 온도 마진
    SF_MIIT: 보호 마진
    """
    # Jc 기준 (77 K, 0 T 대비)
    jc_ref = material.jc_a_per_mm2_77k * jc_min_fraction
    sf_jc = jc_op_a_per_mm2 / max(1e-6, jc_ref)

    # 온도 마진
    sf_t = t_hotspot_limit_k / max(1.0, hotspot_temp_k)

    # MIIT 마진
    sf_miit = miit_limit_a2s / max(1.0, miit_actual_a2s)

    return {
        "SF_Jc":   round(sf_jc, 3),
        "SF_T":    round(sf_t, 3),
        "SF_MIIT": round(sf_miit, 3),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MTBF / 신뢰도
# ─────────────────────────────────────────────────────────────────────────────

def mtbf_estimate(
    n_quench_per_year: float = 0.5,
    thermal_cycle_lifetime_years: float = 50.0,
    component_mtbf_hours: float = 100_000.0,  # 전원 공급, 냉각기 등 외부 부품
) -> Dict[str, float]:
    """MTBF 추정 (초전도 마그넷 시스템).

    MTBF_quench  = 1 / λ_quench  (퀀치율의 역수)
    MTBF_total   = 조화 평균 (직렬 실패 모드)
    R(t=1yr)     = exp(−1/MTBF_total)
    """
    # 퀀치 MTBF (년)
    mtbf_quench_yr = 1.0 / max(1e-6, n_quench_per_year)

    # 피로 수명 (등가 MTBF로 취급)
    mtbf_fatigue_yr = thermal_cycle_lifetime_years

    # 외부 부품 MTBF (시간 → 년)
    mtbf_ext_yr = component_mtbf_hours / 8760.0

    # 직렬 시스템: λ_total = Σλᵢ
    lambda_total = (1.0 / mtbf_quench_yr +
                    1.0 / max(1.0, mtbf_fatigue_yr) +
                    1.0 / max(1.0, mtbf_ext_yr))
    mtbf_total_yr = 1.0 / lambda_total

    # 1년 신뢰도
    r_1yr = math.exp(-1.0 / max(0.01, mtbf_total_yr))
    # 10년 신뢰도
    r_10yr = math.exp(-10.0 / max(0.01, mtbf_total_yr))

    return {
        "mtbf_quench_years":   round(mtbf_quench_yr, 2),
        "mtbf_fatigue_years":  round(mtbf_fatigue_yr, 1),
        "mtbf_total_years":    round(mtbf_total_yr, 2),
        "reliability_1yr":     round(r_1yr, 4),
        "reliability_10yr":    round(r_10yr, 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 단일 실패점 (SPoF) 분석
# ─────────────────────────────────────────────────────────────────────────────

def single_point_of_failure_analysis(
    material_name: str,
    design: MagnetDesign,
    hotspot_temp_k: float,
    miit_actual_a2s: float,
) -> List[Dict[str, str]]:
    """주요 실패 모드 및 임계 경로 식별.

    반환: [{"mode": ..., "severity": ..., "mitigation": ...}]
    """
    failures: List[Dict[str, str]] = []

    # 1. 필라멘트 비가역 손상
    irr = _IRR_STRAIN.get(material_name, 0.005)
    failures.append({
        "mode": f"필라멘트 비가역 손상 (ε > {irr*100:.2f}%)",
        "severity": "CRITICAL" if material_name in ("Nb3Sn", "BSCCO-2212", "BSCCO-2223") else "HIGH",
        "mitigation": "사전압축 최적화, 코일 지지 강화, 변형률 모니터링",
    })

    # 2. 퀀치 검출 실패
    failures.append({
        "mode": "퀀치 검출 실패 (전압 임계값 드리프트)",
        "severity": "CRITICAL",
        "mitigation": "중복 검출 채널 (전압+온도), 주기적 캘리브레이션",
    })

    # 3. 핫스팟 과열
    t_limit = 200.0 if material_name == "Nb3Sn" else 300.0
    if hotspot_temp_k > t_limit * 0.7:
        failures.append({
            "mode": f"핫스팟 과열 ({hotspot_temp_k:.0f} K → 한계 {t_limit:.0f} K의 {hotspot_temp_k/t_limit*100:.0f}%)",
            "severity": "HIGH",
            "mitigation": "덤프 저항 증가, 검출 속도 향상, 열 전도 경로 개선",
        })

    # 4. MIIT 초과
    if miit_actual_a2s > 20e6:
        failures.append({
            "mode": f"MIIT 과대 ({miit_actual_a2s/1e6:.1f} MA²s — 30 MA²s 한계의 {miit_actual_a2s/30e6*100:.0f}%)",
            "severity": "HIGH" if miit_actual_a2s < 30e6 else "CRITICAL",
            "mitigation": "덤프 저항 ↑, 인덕턴스 분할 (분할 퀀치 보호)",
        })

    # 5. 냉각 시스템 실패
    failures.append({
        "mode": "냉각 시스템 실패 (He 누설 또는 압축기 정지)",
        "severity": "CRITICAL",
        "mitigation": "이중 냉각 루프, 온도 트립 인터록, 비상 덤프 자동화",
    })

    # 6. 절연 파괴 (턴-투-턴)
    v_peak = design.operating_current_a * (design.inductance_h / max(0.001, design.inductance_h)) * 100
    failures.append({
        "mode": "턴-간 절연 파괴 (V_peak 과대)",
        "severity": "MEDIUM",
        "mitigation": "전압 한계 1 kV 이하 유지, 덤프 저항 분산",
    })

    return failures


# ─────────────────────────────────────────────────────────────────────────────
# 종합 결함 허용성 보고서
# ─────────────────────────────────────────────────────────────────────────────

def assess_fault_tolerance(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    hotspot_temp_k: float = 50.0,
    miit_actual_a2s: float = 5.0e6,
    strain_amplitude: float = 0.001,
    n_quench_per_year: float = 0.5,
    thermal_cycles_per_year: float = 2.0,
) -> FaultToleranceReport:
    """결함 허용성 종합 분석.

    Coffin-Manson 피로 수명 + 안전 계수 + MTBF + SPoF 분석
    """
    # Jc 운전점 추정
    b_frac = min(0.999, design.target_field_t / max(1.0, material.bc2_t))
    t_frac = min(0.999, cryo.operating_temp_k / max(1.0, material.tc_k))
    jc_op  = material.jc_a_per_mm2_77k * (1.0 - t_frac) * (1.0 - b_frac) / max(0.1, material.anisotropy)

    # 피로 수명
    fatigue = thermal_cycle_lifetime(material.name, thermal_cycles_per_year)

    # 안전 계수
    t_limit = 200.0 if material.name == "Nb3Sn" else 300.0
    sf = safety_factors(
        material, cryo, design,
        jc_op_a_per_mm2=jc_op,
        hotspot_temp_k=hotspot_temp_k,
        miit_actual_a2s=miit_actual_a2s,
        t_hotspot_limit_k=t_limit,
    )

    # MTBF
    mtbf = mtbf_estimate(n_quench_per_year, fatigue["estimated_years"])

    # SPoF
    spof = single_point_of_failure_analysis(
        material.name, design, hotspot_temp_k, miit_actual_a2s
    )

    # 전체 판정
    critical_spof = [f for f in spof if f["severity"] == "CRITICAL"]
    all_sf_ok = all(v >= 1.5 for v in sf.values())  # SF ≥ 1.5 기준

    if critical_spof and not all_sf_ok:
        overall = "CRITICAL"
        rec = (f"결함 허용성 불충분: 임계 실패 모드 {len(critical_spof)}개, "
               f"안전계수 미달. 즉각적인 설계 수정 필요.")
    elif critical_spof:
        overall = "HIGH_RISK"
        rec = (f"임계 실패 모드 {len(critical_spof)}개 존재 (안전계수는 충족). "
               f"보호 시스템 중복성 강화 권장.")
    elif not all_sf_ok:
        overall = "MARGINAL"
        rec = "안전계수 일부 미달. 마진 확대 또는 운전 조건 완화 권장."
    else:
        overall = "ACCEPTABLE"
        rec = (f"결함 허용성 양호: SF_min={min(sf.values()):.2f}, "
               f"MTBF≈{mtbf['mtbf_total_years']:.1f}년, "
               f"피로 수명≈{fatigue['n_cycles_to_failure']:.0f}사이클.")

    return FaultToleranceReport(
        coffin_manson_cycles=fatigue["n_cycles_to_failure"],
        estimated_lifetime_years=fatigue["estimated_years"],
        safety_factors=sf,
        mtbf_years=mtbf["mtbf_total_years"],
        reliability_1yr=mtbf["reliability_1yr"],
        reliability_10yr=mtbf["reliability_10yr"],
        critical_failure_modes=[f["mode"] for f in critical_spof],
        overall_assessment=overall,
        recommendation=rec,
    )
