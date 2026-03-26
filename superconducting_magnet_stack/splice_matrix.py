from __future__ import annotations

from .contracts import MagnetDesign, SpliceMatrixReport
from .splice_topology import estimate_splice_count


def matrix_complexity_index(design: MagnetDesign) -> float:
    splice_count = estimate_splice_count(design)
    inductive_pressure = min(1.0, design.inductance_h / 8.0) * 0.4
    splice_pressure = min(1.0, splice_count / 10.0) * 0.6
    return max(0.0, min(1.0, inductive_pressure + splice_pressure))


def current_imbalance_risk_index(design: MagnetDesign) -> float:
    splice_count = estimate_splice_count(design)
    current_pressure = min(1.0, design.operating_current_a / 1200.0) * 0.45
    stress_pressure = min(1.0, design.stress_mpa / 250.0) * 0.2
    topology_pressure = min(1.0, splice_count / 12.0) * 0.35
    return max(0.0, min(1.0, current_pressure + stress_pressure + topology_pressure))


def assess_splice_matrix(design: MagnetDesign) -> SpliceMatrixReport:
    complexity = matrix_complexity_index(design)
    imbalance = current_imbalance_risk_index(design)

    if imbalance >= 0.7:
        rec = "simplify_splice_matrix_and_add_current_balancing_margin"
    elif complexity >= 0.5:
        rec = "track_splice_matrix_layout_in_next_joint_design_pass"
    else:
        rec = "splice matrix is acceptable for preliminary screening"

    return SpliceMatrixReport(
        matrix_complexity_index=complexity,
        current_imbalance_risk_index=imbalance,
        recommendation=rec,
    )
