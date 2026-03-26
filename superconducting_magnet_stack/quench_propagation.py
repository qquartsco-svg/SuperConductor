from __future__ import annotations

from .contracts import CryoProfile, MagnetDesign, MaterialCandidate, QuenchPropagationReport
from .material import jc_derated


def estimate_nzpv_m_per_s(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> float:
    jc = jc_derated(material, cryo.operating_temp_k, design.target_field_t)
    current_density = design.operating_current_a / max(1e-6, design.conductor_cross_section_mm2)
    loading = current_density / max(1e-6, jc) if jc > 0 else 1.5
    margin = max(0.05, 1.0 - min(1.0, loading))
    return max(0.05, 6.0 * margin * (1.0 - cryo.operating_temp_k / max(1e-6, material.tc_k / 1.4)))


def hotspot_risk_index(nzpv_m_per_s: float, design: MagnetDesign) -> float:
    propagation_protection = min(1.0, nzpv_m_per_s / 5.0)
    energy_pressure = min(1.0, design.stored_energy_j / 300000.0)
    return max(0.0, min(1.0, 0.65 * (1.0 - propagation_protection) + 0.35 * energy_pressure))


def estimate_dump_window_s(design: MagnetDesign) -> float:
    return max(0.02, min(10.0, design.inductance_h * max(1.0, design.operating_current_a) / max(1.0, design.stored_energy_j / 50.0)))


def assess_quench_propagation(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> QuenchPropagationReport:
    nzpv = estimate_nzpv_m_per_s(material, cryo, design)
    hotspot = hotspot_risk_index(nzpv, design)
    dump_window = estimate_dump_window_s(design)

    if hotspot >= 0.7:
        rec = "tighten_dump_window_and_expand_quench_detection_coverage"
    elif hotspot >= 0.4:
        rec = "validate_quench_propagation_with_time_domain_model"
    else:
        rec = "propagation_margin_is_acceptable_for_preliminary_study"

    return QuenchPropagationReport(
        nzpv_m_per_s=nzpv,
        hotspot_risk_index=hotspot,
        dump_window_s=dump_window,
        recommendation=rec,
    )
