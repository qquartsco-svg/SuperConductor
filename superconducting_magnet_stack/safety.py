from .contracts import CryoProfile, MagnetDesign, MaterialCandidate, QuenchRiskReport
from .electromagnetic import magnetic_stress_risk, operating_current_density_a_per_mm2
from .material import jc_derated
from .thermal import omega_thermal


def evaluate_quench_risk(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> QuenchRiskReport:
    jc_limit = jc_derated(material, cryo.operating_temp_k, design.target_field_t)
    j_operating = operating_current_density_a_per_mm2(design)
    current_over = 0.0 if jc_limit <= 0 else max(0.0, j_operating / jc_limit - 1.0)
    thermal_penalty = 1.0 - omega_thermal(cryo)
    stress_penalty = magnetic_stress_risk(design)
    quench_index = max(0.0, min(1.0, 0.5 * min(1.0, current_over) + 0.3 * thermal_penalty + 0.2 * stress_penalty))

    if quench_index >= 0.85:
        severity = "critical"
        rec = "immediate_ramp_down_and_dump_resistor_check"
    elif quench_index >= 0.65:
        severity = "high"
        rec = "reduce_current_and_increase_thermal_margin"
    elif quench_index >= 0.4:
        severity = "medium"
        rec = "monitor_hotspot_and_joint_resistance"
    else:
        severity = "low"
        rec = "continue_operation_with_periodic_verification"
    return QuenchRiskReport(quench_index=quench_index, severity=severity, recommendation=rec)

