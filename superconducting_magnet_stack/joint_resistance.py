from __future__ import annotations

from .contracts import CryoProfile, JointResistanceReport, MagnetDesign


def estimate_joint_resistance_n_ohm(design: MagnetDesign, cryo: CryoProfile) -> float:
    # Coarse screening proxy only.
    current_factor = design.operating_current_a / 1000.0
    thermal_factor = 1.0 + max(0.0, cryo.operating_temp_k - 4.2) / 40.0
    stress_factor = 1.0 + design.stress_mpa / 500.0
    return max(5.0, 25.0 * current_factor * thermal_factor * stress_factor)


def resistive_heating_w(design: MagnetDesign, joint_resistance_n_ohm: float) -> float:
    resistance_ohm = joint_resistance_n_ohm * 1e-9
    return (design.operating_current_a ** 2) * resistance_ohm


def stability_penalty_index(heating_w: float, cryo: CryoProfile) -> float:
    capacity = max(1e-6, cryo.cooling_capacity_w)
    return max(0.0, min(1.0, heating_w / capacity))


def assess_joint_resistance(design: MagnetDesign, cryo: CryoProfile) -> JointResistanceReport:
    resistance = estimate_joint_resistance_n_ohm(design, cryo)
    heating = resistive_heating_w(design, resistance)
    penalty = stability_penalty_index(heating, cryo)

    if penalty >= 0.5:
        rec = "reduce_joint_resistance_and_expand_local_cooling_margin"
    elif penalty >= 0.25:
        rec = "monitor_joint_heating_under_nominal_current"
    else:
        rec = "joint_resistance_is_acceptable_for_preliminary_design"

    return JointResistanceReport(
        joint_resistance_n_ohm=resistance,
        resistive_heating_w=heating,
        stability_penalty_index=penalty,
        recommendation=rec,
    )
