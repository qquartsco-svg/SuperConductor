from __future__ import annotations

from .contracts import MagnetDesign, RampProfileReport


def nominal_ramp_rate_t_per_s(design: MagnetDesign) -> float:
    return max(0.01, min(5.0, design.target_field_t / max(1.0, design.inductance_h * 40.0)))


def ramp_stability_penalty_index(design: MagnetDesign) -> float:
    rate = nominal_ramp_rate_t_per_s(design)
    stored_energy_penalty = min(1.0, design.stored_energy_j / 350000.0) * 0.35
    rate_penalty = min(1.0, rate / 2.0) * 0.65
    return max(0.0, min(1.0, rate_penalty + stored_energy_penalty))


def assess_ramp_profile(design: MagnetDesign) -> RampProfileReport:
    rate = nominal_ramp_rate_t_per_s(design)
    penalty = ramp_stability_penalty_index(design)

    if penalty >= 0.7:
        rec = "slow_ramp_profile_and_validate_dynamic_stability"
    elif penalty >= 0.4:
        rec = "track_ramp_rate_against_ac_loss_and_quench_margin"
    else:
        rec = "ramp profile is acceptable for preliminary operation study"

    return RampProfileReport(
        ramp_rate_t_per_s=rate,
        stability_penalty_index=penalty,
        recommendation=rec,
    )
