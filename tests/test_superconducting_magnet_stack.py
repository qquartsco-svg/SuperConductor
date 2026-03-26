import pytest

from superconducting_magnet_stack import (
    assess_ac_loss,
    assess_coil_geometry,
    assess_field_uniformity,
    assess_joint_resistance,
    assess_mechanical_fatigue,
    assess_material_screening,
    compare_material_candidates,
    assess_quench_propagation,
    assess_ramp_dynamics,
    assess_ramp_profile,
    rank_material_candidates,
    assess_splice_topology,
    assess_splice_matrix,
    CryoProfile,
    MagnetDesign,
    MaterialCandidate,
    assess_readiness,
    evaluate_quench_risk,
    run_extended_research_assessment,
    run_material_research_assessment,
    run_magnet_design_assessment,
    run_research_foundation_assessment,
)
from superconducting_magnet_stack.engine_ref_adapter import (
    COMPARE_ENGINE_REF,
    ENGINE_REF,
    run_engine_ref_payload,
    run_material_compare_payload,
)


def _sample() -> tuple[MaterialCandidate, CryoProfile, MagnetDesign]:
    material = MaterialCandidate(
        name="REBCO-like",
        tc_k=92.0,
        jc_a_per_mm2_77k=300.0,
        bc2_t=120.0,
        anisotropy=1.4,
    )
    cryo = CryoProfile(operating_temp_k=20.0, heat_load_w=12.0, cooling_capacity_w=30.0)
    design = MagnetDesign(
        target_field_t=20.0,
        operating_current_a=600.0,
        conductor_cross_section_mm2=8.0,
        inductance_h=1.2,
        stored_energy_j=216000.0,
        stress_mpa=140.0,
    )
    return material, cryo, design


def test_readiness_range_and_verdict() -> None:
    material, cryo, design = _sample()
    report = assess_readiness(material, cryo, design)
    assert 0.0 <= report.omega_total <= 1.0
    assert report.verdict in {"HEALTHY", "STABLE", "FRAGILE", "CRITICAL"}


def test_quench_report_shape() -> None:
    material, cryo, design = _sample()
    qr = evaluate_quench_risk(material, cryo, design)
    assert 0.0 <= qr.quench_index <= 1.0
    assert qr.severity in {"low", "medium", "high", "critical"}
    assert isinstance(qr.recommendation, str) and qr.recommendation


def test_pipeline_returns_both_reports() -> None:
    material, cryo, design = _sample()
    readiness, quench = run_magnet_design_assessment(material, cryo, design)
    assert readiness.evidence["target_field_t"] == 20.0
    assert quench.quench_index >= 0.0


def test_engine_ref_payload_result_shape() -> None:
    payload = {
        "material": {
            "name": "REBCO-like",
            "tc_k": 92.0,
            "jc_a_per_mm2_77k": 300.0,
            "bc2_t": 120.0,
            "anisotropy": 1.4,
        },
        "cryo": {
            "operating_temp_k": 20.0,
            "heat_load_w": 12.0,
            "cooling_capacity_w": 30.0,
        },
        "design": {
            "target_field_t": 20.0,
            "operating_current_a": 600.0,
            "conductor_cross_section_mm2": 8.0,
            "inductance_h": 1.2,
            "stored_energy_j": 216000.0,
            "stress_mpa": 140.0,
        },
    }
    out = run_engine_ref_payload(payload)
    assert out["engine_ref"] == ENGINE_REF
    assert out["verdict"] in {"HEALTHY", "STABLE", "FRAGILE", "CRITICAL"}
    assert 0.0 <= out["omega"] <= 1.0


def test_material_compare_payload_result_shape() -> None:
    payload = {
        "materials": [
            {"name": "CandidateA", "tc_k": 82.0, "jc_a_per_mm2_77k": 250.0, "bc2_t": 100.0, "anisotropy": 1.5},
            {"name": "CandidateB", "tc_k": 92.0, "jc_a_per_mm2_77k": 300.0, "bc2_t": 120.0, "anisotropy": 1.4},
        ],
        "cryo": {
            "operating_temp_k": 20.0,
            "heat_load_w": 12.0,
            "cooling_capacity_w": 30.0,
        },
        "design": {
            "target_field_t": 20.0,
            "operating_current_a": 600.0,
            "conductor_cross_section_mm2": 8.0,
            "inductance_h": 1.2,
            "stored_energy_j": 216000.0,
            "stress_mpa": 140.0,
        },
    }
    out = run_material_compare_payload(payload)
    assert out["engine_ref"] == COMPARE_ENGINE_REF
    assert out["best_candidate"] == "CandidateB"
    assert len(out["ranking"]) == 2
    assert out["ranking"][0]["screening_score"] >= out["ranking"][1]["screening_score"]


def test_research_foundation_reports_have_valid_ranges() -> None:
    material, cryo, design = _sample()
    geometry = assess_coil_geometry(design)
    ac_loss = assess_ac_loss(material, cryo, design, sweep_hz=10.0)
    propagation = assess_quench_propagation(material, cryo, design)

    assert 0.0 <= geometry.winding_window_fill <= 1.0
    assert geometry.mean_turn_length_m > 0.0
    assert 0.0 <= geometry.hoop_load_index <= 1.0
    assert ac_loss.loss_w_per_m >= 0.0
    assert 0.0 <= ac_loss.cooling_penalty_index <= 1.0
    assert propagation.nzpv_m_per_s > 0.0
    assert 0.0 <= propagation.hotspot_risk_index <= 1.0
    assert propagation.dump_window_s > 0.0


def test_research_foundation_pipeline_returns_all_layers() -> None:
    material, cryo, design = _sample()
    readiness, quench, geometry, ac_loss, propagation = run_research_foundation_assessment(
        material,
        cryo,
        design,
        ac_sweep_hz=8.0,
    )

    assert readiness.verdict in {"HEALTHY", "STABLE", "FRAGILE", "CRITICAL"}
    assert quench.severity in {"low", "medium", "high", "critical"}
    assert geometry.recommendation
    assert ac_loss.recommendation
    assert propagation.recommendation


def test_extended_research_reports_have_valid_ranges() -> None:
    material, cryo, design = _sample()
    joint = assess_joint_resistance(design, cryo)
    uniformity = assess_field_uniformity(design)
    fatigue = assess_mechanical_fatigue(design)

    assert joint.joint_resistance_n_ohm > 0.0
    assert joint.resistive_heating_w >= 0.0
    assert 0.0 <= joint.stability_penalty_index <= 1.0
    assert 0.0 <= uniformity.field_uniformity_index <= 1.0
    assert 0.0 <= uniformity.fringe_field_index <= 1.0
    assert 0.0 <= fatigue.cycle_load_index <= 1.0
    assert 0.0 <= fatigue.fatigue_risk_index <= 1.0


def test_extended_research_pipeline_returns_all_layers() -> None:
    material, cryo, design = _sample()
    reports = run_extended_research_assessment(material, cryo, design, ac_sweep_hz=8.0)
    assert len(reports) == 8
    readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue = reports
    assert readiness.verdict in {"HEALTHY", "STABLE", "FRAGILE", "CRITICAL"}
    assert quench.recommendation
    assert geometry.recommendation
    assert ac_loss.recommendation
    assert propagation.recommendation
    assert joint.recommendation
    assert uniformity.recommendation
    assert fatigue.recommendation


def test_material_research_reports_have_valid_ranges() -> None:
    material, cryo, design = _sample()
    screening = assess_material_screening(material, cryo, design)
    splice = assess_splice_topology(design)
    ramp = assess_ramp_profile(design)
    splice_matrix = assess_splice_matrix(design)
    ramp_dynamics = assess_ramp_dynamics(design)

    assert 0.0 <= screening.screening_score <= 1.0
    assert 0.0 <= screening.operating_margin_index <= 1.0
    assert splice.splice_count >= 1
    assert 0.0 <= splice.topology_penalty_index <= 1.0
    assert ramp.ramp_rate_t_per_s > 0.0
    assert 0.0 <= ramp.stability_penalty_index <= 1.0
    assert 0.0 <= splice_matrix.matrix_complexity_index <= 1.0
    assert 0.0 <= splice_matrix.current_imbalance_risk_index <= 1.0
    assert ramp_dynamics.induced_voltage_v >= 0.0
    assert 0.0 <= ramp_dynamics.dynamic_heating_index <= 1.0
    assert 0.0 <= ramp_dynamics.stability_window_index <= 1.0


def test_material_research_pipeline_returns_all_layers() -> None:
    material, cryo, design = _sample()
    reports = run_material_research_assessment(material, cryo, design, ac_sweep_hz=8.0)
    assert len(reports) == 13
    _, _, _, _, _, _, _, _, screening, splice, ramp, splice_matrix, ramp_dynamics = reports
    assert screening.recommendation
    assert splice.recommendation
    assert ramp.recommendation
    assert splice_matrix.recommendation
    assert ramp_dynamics.recommendation


def test_contracts_reject_non_physical_inputs() -> None:
    with pytest.raises(ValueError):
        MaterialCandidate(
            name="",
            tc_k=92.0,
            jc_a_per_mm2_77k=300.0,
            bc2_t=120.0,
            anisotropy=1.4,
        )
    with pytest.raises(ValueError):
        CryoProfile(operating_temp_k=-1.0, heat_load_w=12.0, cooling_capacity_w=30.0)
    with pytest.raises(ValueError):
        MagnetDesign(
            target_field_t=20.0,
            operating_current_a=600.0,
            conductor_cross_section_mm2=0.0,
            inductance_h=1.2,
            stored_energy_j=216000.0,
            stress_mpa=140.0,
        )


def test_material_candidate_ranking_orders_candidates() -> None:
    _, cryo, design = _sample()
    candidates = [
        MaterialCandidate("LowMargin", tc_k=55.0, jc_a_per_mm2_77k=180.0, bc2_t=55.0, anisotropy=1.8),
        MaterialCandidate("MidMargin", tc_k=78.0, jc_a_per_mm2_77k=240.0, bc2_t=90.0, anisotropy=1.5),
        MaterialCandidate("HighMargin", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4),
    ]
    ranking = rank_material_candidates(candidates, cryo, design)
    assert ranking.best_candidate == "HighMargin"
    assert [item.rank for item in ranking.ranking] == [1, 2, 3]
    assert ranking.ranking[0].screening_score >= ranking.ranking[1].screening_score >= ranking.ranking[2].screening_score


def test_pipeline_material_candidate_comparison() -> None:
    _, cryo, design = _sample()
    candidates = [
        MaterialCandidate("CandidateA", tc_k=82.0, jc_a_per_mm2_77k=250.0, bc2_t=100.0, anisotropy=1.5),
        MaterialCandidate("CandidateB", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4),
    ]
    ranking = compare_material_candidates(candidates, cryo, design)
    assert ranking.best_candidate == "CandidateB"
    assert ranking.recommendation
