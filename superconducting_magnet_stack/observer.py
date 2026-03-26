from .contracts import BuildReadinessReport, CryoProfile, MagnetDesign, MaterialCandidate
from .material import omega_material
from .safety import evaluate_quench_risk
from .thermal import omega_thermal


def assess_readiness(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> BuildReadinessReport:
    om = omega_material(material, cryo.operating_temp_k, design.target_field_t)
    ot = omega_thermal(cryo)
    qr = evaluate_quench_risk(material, cryo, design)
    oq = 1.0 - qr.quench_index
    omega_total = 0.4 * om + 0.35 * ot + 0.25 * oq

    if omega_total >= 0.80:
        verdict = "HEALTHY"
    elif omega_total >= 0.60:
        verdict = "STABLE"
    elif omega_total >= 0.40:
        verdict = "FRAGILE"
    else:
        verdict = "CRITICAL"

    return BuildReadinessReport(
        omega_material=om,
        omega_thermal=ot,
        omega_quench=oq,
        omega_total=omega_total,
        verdict=verdict,
        evidence={
            "target_field_t": design.target_field_t,
            "operating_temp_k": cryo.operating_temp_k,
            "quench_index": qr.quench_index,
        },
    )

