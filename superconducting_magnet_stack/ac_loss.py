from __future__ import annotations

from .contracts import ACLossReport, CryoProfile, MagnetDesign, MaterialCandidate


def estimate_ac_loss_w_per_m(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    sweep_hz: float,
) -> float:
    # Coarse proxy for screening studies only.
    normalized_field = design.target_field_t / max(1e-6, material.bc2_t)
    normalized_temp = cryo.operating_temp_k / max(1e-6, material.tc_k)
    base = 0.12 * max(0.0, sweep_hz)
    return base * (1.0 + 2.2 * normalized_field) * (1.0 + 1.6 * normalized_temp)


def cooling_penalty_index(loss_w_per_m: float, cryo: CryoProfile) -> float:
    capacity = max(1e-6, cryo.cooling_capacity_w)
    return max(0.0, min(1.0, loss_w_per_m / capacity))


def assess_ac_loss(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    sweep_hz: float = 5.0,
) -> ACLossReport:
    loss = estimate_ac_loss_w_per_m(material, cryo, design, sweep_hz=sweep_hz)
    penalty = cooling_penalty_index(loss, cryo)

    if penalty >= 0.6:
        rec = "reduce_ramp_rate_or_expand_cooling_capacity"
    elif penalty >= 0.3:
        rec = "track_ac_loss_during_dynamic_field_scenarios"
    else:
        rec = "ac_loss_is_acceptable_for_preliminary_screening"

    return ACLossReport(
        sweep_hz=sweep_hz,
        loss_w_per_m=loss,
        cooling_penalty_index=penalty,
        recommendation=rec,
    )
