from __future__ import annotations

from .contracts import FieldUniformityReport, MagnetDesign


def field_uniformity_index(design: MagnetDesign) -> float:
    stress_penalty = min(1.0, design.stress_mpa / 300.0) * 0.2
    energy_penalty = min(1.0, design.stored_energy_j / 400000.0) * 0.15
    baseline = 0.92 - stress_penalty - energy_penalty
    return max(0.0, min(1.0, baseline))


def fringe_field_index(design: MagnetDesign) -> float:
    return max(0.0, min(1.0, 0.25 + 0.5 * min(1.0, design.target_field_t / 25.0)))


def assess_field_uniformity(design: MagnetDesign) -> FieldUniformityReport:
    uniformity = field_uniformity_index(design)
    fringe = fringe_field_index(design)

    if uniformity < 0.7:
        rec = "review_coil_shape_and_shimming_strategy"
    elif fringe > 0.7:
        rec = "add_fringe_field_containment_to_next_design_pass"
    else:
        rec = "field_uniformity_is_acceptable_for_preliminary_screening"

    return FieldUniformityReport(
        field_uniformity_index=uniformity,
        fringe_field_index=fringe,
        recommendation=rec,
    )
