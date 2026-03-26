from __future__ import annotations

from .contracts import MagnetDesign, SpliceTopologyReport


def estimate_splice_count(design: MagnetDesign) -> int:
    return max(1, int(round(design.inductance_h * 2 + design.target_field_t / 8.0)))


def topology_penalty_index(design: MagnetDesign) -> float:
    splice_count = estimate_splice_count(design)
    stress_penalty = min(1.0, design.stress_mpa / 250.0) * 0.25
    return max(0.0, min(1.0, splice_count / 12.0 + stress_penalty))


def assess_splice_topology(design: MagnetDesign) -> SpliceTopologyReport:
    splice_count = estimate_splice_count(design)
    penalty = topology_penalty_index(design)

    if penalty >= 0.7:
        rec = "reduce_splice_count_or_rework_joint_topology"
    elif penalty >= 0.4:
        rec = "track_splice_layout_in_next_mechanical_pass"
    else:
        rec = "splice topology is acceptable for preliminary design"

    return SpliceTopologyReport(
        splice_count=splice_count,
        topology_penalty_index=penalty,
        recommendation=rec,
    )
