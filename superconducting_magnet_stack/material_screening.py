from __future__ import annotations

from .contracts import CryoProfile, MagnetDesign, MaterialCandidate, MaterialScreeningReport
from .material import omega_material


def operating_margin_index(material: MaterialCandidate, cryo: CryoProfile, design: MagnetDesign) -> float:
    temp_margin = max(0.0, 1.0 - cryo.operating_temp_k / max(1e-6, material.tc_k))
    field_margin = max(0.0, 1.0 - design.target_field_t / max(1e-6, material.bc2_t))
    return max(0.0, min(1.0, 0.55 * temp_margin + 0.45 * field_margin))


def screening_score(material: MaterialCandidate, cryo: CryoProfile, design: MagnetDesign) -> float:
    base = omega_material(material, cryo.operating_temp_k, design.target_field_t)
    margin = operating_margin_index(material, cryo, design)
    return max(0.0, min(1.0, 0.6 * base + 0.4 * margin))


def assess_material_screening(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> MaterialScreeningReport:
    margin = operating_margin_index(material, cryo, design)
    score = screening_score(material, cryo, design)

    if score < 0.4:
        rec = "screen_out_or_shift_to_lower_field_temperature_window"
    elif score < 0.7:
        rec = "keep_as_secondary_candidate_and_collect_more_material_data"
    else:
        rec = "candidate_is_good_for_next_design_iteration"

    return MaterialScreeningReport(
        screening_score=score,
        operating_margin_index=margin,
        recommendation=rec,
    )
