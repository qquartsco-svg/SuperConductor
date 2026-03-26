from __future__ import annotations

from .contracts import MechanicalFatigueReport, MagnetDesign


def cycle_load_index(design: MagnetDesign) -> float:
    stress_term = min(1.0, design.stress_mpa / 250.0)
    energy_term = min(1.0, design.stored_energy_j / 300000.0)
    return max(0.0, min(1.0, 0.7 * stress_term + 0.3 * energy_term))


def fatigue_risk_index(design: MagnetDesign) -> float:
    cycle = cycle_load_index(design)
    inductive_penalty = min(1.0, design.inductance_h / 5.0) * 0.2
    return max(0.0, min(1.0, 0.8 * cycle + inductive_penalty))


def assess_mechanical_fatigue(design: MagnetDesign) -> MechanicalFatigueReport:
    cycle = cycle_load_index(design)
    risk = fatigue_risk_index(design)

    if risk >= 0.7:
        rec = "increase_structural_margin_and_plan_cycle_life_validation"
    elif risk >= 0.4:
        rec = "track fatigue under repeated ramp scenarios"
    else:
        rec = "fatigue risk is acceptable for preliminary design study"

    return MechanicalFatigueReport(
        cycle_load_index=cycle,
        fatigue_risk_index=risk,
        recommendation=rec,
    )
