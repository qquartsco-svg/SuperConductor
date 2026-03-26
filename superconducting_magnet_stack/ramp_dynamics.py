from __future__ import annotations

from .contracts import MagnetDesign, RampDynamicsReport
from .ramp_profile import nominal_ramp_rate_t_per_s


def induced_voltage_v(design: MagnetDesign) -> float:
    # Coarse proxy: V ~ L * dI/dt, with dI/dt inferred from target field ramp pressure.
    ramp_rate = nominal_ramp_rate_t_per_s(design)
    current_ramp_a_per_s = ramp_rate * max(10.0, design.operating_current_a / max(1.0, design.target_field_t + 1.0))
    return max(0.0, design.inductance_h * current_ramp_a_per_s)


def dynamic_heating_index(design: MagnetDesign) -> float:
    voltage = induced_voltage_v(design)
    energy_pressure = min(1.0, design.stored_energy_j / 400000.0) * 0.35
    voltage_pressure = min(1.0, voltage / 1200.0) * 0.65
    return max(0.0, min(1.0, energy_pressure + voltage_pressure))


def stability_window_index(design: MagnetDesign) -> float:
    heating = dynamic_heating_index(design)
    stress_penalty = min(1.0, design.stress_mpa / 250.0) * 0.2
    return max(0.0, min(1.0, 1.0 - min(1.0, heating + stress_penalty)))


def assess_ramp_dynamics(design: MagnetDesign) -> RampDynamicsReport:
    voltage = induced_voltage_v(design)
    heating = dynamic_heating_index(design)
    window = stability_window_index(design)

    if window <= 0.3:
        rec = "slow_ramp_and_validate_time_domain_stability"
    elif heating >= 0.45:
        rec = "track_dynamic_heating_against_protection_window"
    else:
        rec = "ramp dynamics are acceptable for preliminary study"

    return RampDynamicsReport(
        induced_voltage_v=voltage,
        dynamic_heating_index=heating,
        stability_window_index=window,
        recommendation=rec,
    )
