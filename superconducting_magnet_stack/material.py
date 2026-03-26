from .contracts import MaterialCandidate


def jc_derated(material: MaterialCandidate, temp_k: float, field_t: float) -> float:
    # Coarse design-time derating, not a high-fidelity physical solver.
    temp_factor = max(0.0, 1.0 - temp_k / max(1e-6, material.tc_k))
    field_factor = max(0.0, 1.0 - field_t / max(1e-6, material.bc2_t))
    return material.jc_a_per_mm2_77k * temp_factor * field_factor / max(1.0, material.anisotropy)


def omega_material(material: MaterialCandidate, temp_k: float, field_t: float) -> float:
    jc = jc_derated(material, temp_k, field_t)
    baseline = max(1e-6, material.jc_a_per_mm2_77k)
    return max(0.0, min(1.0, jc / baseline))

