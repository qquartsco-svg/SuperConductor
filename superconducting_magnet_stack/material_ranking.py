from __future__ import annotations

from .contracts import (
    CryoProfile,
    MagnetDesign,
    MaterialCandidate,
    MaterialCandidateRank,
    MaterialRankingReport,
)
from .material_screening import assess_material_screening


def rank_material_candidates(
    materials: list[MaterialCandidate],
    cryo: CryoProfile,
    design: MagnetDesign,
) -> MaterialRankingReport:
    if not materials:
        raise ValueError("materials must contain at least one candidate")

    ranked = []
    for material in materials:
        report = assess_material_screening(material, cryo, design)
        ranked.append(
            MaterialCandidateRank(
                name=material.name,
                screening_score=report.screening_score,
                operating_margin_index=report.operating_margin_index,
                rank=0,
                recommendation=report.recommendation,
            )
        )

    ranked.sort(
        key=lambda item: (item.screening_score, item.operating_margin_index, item.name),
        reverse=True,
    )

    final_ranking = [
        MaterialCandidateRank(
            name=item.name,
            screening_score=item.screening_score,
            operating_margin_index=item.operating_margin_index,
            rank=index + 1,
            recommendation=item.recommendation,
        )
        for index, item in enumerate(ranked)
    ]

    top = final_ranking[0]
    if top.screening_score >= 0.7:
        rec = "advance_best_candidate_to_next_design_iteration"
    elif top.screening_score >= 0.45:
        rec = "keep_top_candidates_and_collect_more_material_data"
    else:
        rec = "no_candidate_is_ready_for_the_current_field_temperature_window"

    return MaterialRankingReport(
        best_candidate=top.name,
        ranking=final_ranking,
        recommendation=rec,
    )
