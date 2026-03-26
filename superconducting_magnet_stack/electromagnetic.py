from .contracts import MagnetDesign


def operating_current_density_a_per_mm2(design: MagnetDesign) -> float:
    return design.operating_current_a / max(1e-6, design.conductor_cross_section_mm2)


def magnetic_stress_risk(design: MagnetDesign) -> float:
    # Normalized coarse risk. >250 MPa treated as high-risk region.
    return max(0.0, min(1.0, design.stress_mpa / 250.0))

