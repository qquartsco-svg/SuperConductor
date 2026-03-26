from __future__ import annotations

from .contracts import CoilGeometryReport, MagnetDesign


def mean_turn_length_m(design: MagnetDesign) -> float:
    # Coarse proxy: higher field and stress usually imply a larger or more reinforced winding path.
    return max(0.5, 0.8 + 0.03 * design.target_field_t + 0.001 * design.stress_mpa)


def winding_window_fill(design: MagnetDesign) -> float:
    # Coarse design fill proxy from current density pressure on the conductor area.
    fill = design.operating_current_a / max(1.0, design.conductor_cross_section_mm2 * 140.0)
    return max(0.0, min(1.0, fill))


def hoop_load_index(design: MagnetDesign) -> float:
    return max(0.0, min(1.0, (design.target_field_t / 25.0) * 0.6 + (design.stress_mpa / 250.0) * 0.4))


def assess_coil_geometry(design: MagnetDesign) -> CoilGeometryReport:
    fill = winding_window_fill(design)
    mtl = mean_turn_length_m(design)
    hoop = hoop_load_index(design)

    if hoop >= 0.8:
        rec = "increase_structural_margin_and_reduce_field_per_turn"
    elif fill >= 0.75:
        rec = "review_winding_pack_fill_and_cooling_channels"
    else:
        rec = "geometry_is_acceptable_for_preliminary_trade_study"

    return CoilGeometryReport(
        winding_window_fill=fill,
        mean_turn_length_m=mtl,
        hoop_load_index=hoop,
        recommendation=rec,
    )
