from __future__ import annotations

from typing import Any, Dict

from .contracts import CryoProfile, MagnetDesign, MaterialCandidate
from .pipeline import compare_material_candidates, run_magnet_design_assessment

ENGINE_REF = "superconducting.magnet.readiness"
COMPARE_ENGINE_REF = "superconducting.magnet.material_ranking"


def _build_cryo_and_design(payload: Dict[str, Any]) -> tuple[CryoProfile, MagnetDesign]:
    cryo_data = payload["cryo"]
    design_data = payload["design"]

    cryo = CryoProfile(
        operating_temp_k=float(cryo_data["operating_temp_k"]),
        heat_load_w=float(cryo_data["heat_load_w"]),
        cooling_capacity_w=float(cryo_data["cooling_capacity_w"]),
    )
    design = MagnetDesign(
        target_field_t=float(design_data["target_field_t"]),
        operating_current_a=float(design_data["operating_current_a"]),
        conductor_cross_section_mm2=float(design_data["conductor_cross_section_mm2"]),
        inductance_h=float(design_data["inductance_h"]),
        stored_energy_j=float(design_data["stored_energy_j"]),
        stress_mpa=float(design_data["stress_mpa"]),
    )
    return cryo, design


def _build_material(material_data: Dict[str, Any]) -> MaterialCandidate:
    return MaterialCandidate(
        name=material_data["name"],
        tc_k=float(material_data["tc_k"]),
        jc_a_per_mm2_77k=float(material_data["jc_a_per_mm2_77k"]),
        bc2_t=float(material_data["bc2_t"]),
        anisotropy=float(material_data.get("anisotropy", 1.0)),
    )


def run_engine_ref_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    material = _build_material(payload["material"])
    cryo, design = _build_cryo_and_design(payload)

    readiness, quench = run_magnet_design_assessment(material, cryo, design)
    return {
        "engine_ref": ENGINE_REF,
        "omega": readiness.omega_total,
        "verdict": readiness.verdict,
        "quench_severity": quench.severity,
        "evidence": {
            **readiness.evidence,
            "omega_material": readiness.omega_material,
            "omega_thermal": readiness.omega_thermal,
            "omega_quench": readiness.omega_quench,
            "quench_recommendation": quench.recommendation,
        },
    }


def run_material_compare_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    materials_data = payload["materials"]
    if not isinstance(materials_data, list) or not materials_data:
        raise ValueError("materials must be a non-empty list")

    materials = [_build_material(item) for item in materials_data]
    cryo, design = _build_cryo_and_design(payload)
    ranking = compare_material_candidates(materials, cryo, design)
    return {
        "engine_ref": COMPARE_ENGINE_REF,
        "best_candidate": ranking.best_candidate,
        "recommendation": ranking.recommendation,
        "ranking": [
            {
                "rank": item.rank,
                "name": item.name,
                "screening_score": item.screening_score,
                "operating_margin_index": item.operating_margin_index,
                "recommendation": item.recommendation,
            }
            for item in ranking.ranking
        ],
    }
