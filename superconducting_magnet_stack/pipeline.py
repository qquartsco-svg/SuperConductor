from .ac_loss import assess_ac_loss
from .coil_geometry import assess_coil_geometry
from .contracts import (
    ACLossReport,
    BuildReadinessReport,
    CoilGeometryReport,
    CryoProfile,
    FieldUniformityReport,
    JointResistanceReport,
    MagnetDesign,
    MechanicalFatigueReport,
    MaterialScreeningReport,
    MaterialRankingReport,
    MaterialCandidate,
    QuenchPropagationReport,
    QuenchRiskReport,
    RampDynamicsReport,
    RampProfileReport,
    SpliceMatrixReport,
    SpliceTopologyReport,
)
from .field_uniformity import assess_field_uniformity
from .joint_resistance import assess_joint_resistance
from .material_screening import assess_material_screening
from .material_ranking import rank_material_candidates
from .observer import assess_readiness
from .mechanical_fatigue import assess_mechanical_fatigue
from .quench_propagation import assess_quench_propagation
from .ramp_dynamics import assess_ramp_dynamics
from .ramp_profile import assess_ramp_profile
from .safety import evaluate_quench_risk
from .splice_matrix import assess_splice_matrix
from .splice_topology import assess_splice_topology


def run_magnet_design_assessment(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
) -> tuple[BuildReadinessReport, QuenchRiskReport]:
    readiness = assess_readiness(material, cryo, design)
    quench = evaluate_quench_risk(material, cryo, design)
    return readiness, quench


def run_research_foundation_assessment(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    ac_sweep_hz: float = 5.0,
) -> tuple[
    BuildReadinessReport,
    QuenchRiskReport,
    CoilGeometryReport,
    ACLossReport,
    QuenchPropagationReport,
]:
    readiness, quench = run_magnet_design_assessment(material, cryo, design)
    geometry = assess_coil_geometry(design)
    ac_loss = assess_ac_loss(material, cryo, design, sweep_hz=ac_sweep_hz)
    propagation = assess_quench_propagation(material, cryo, design)
    return readiness, quench, geometry, ac_loss, propagation


def run_extended_research_assessment(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    ac_sweep_hz: float = 5.0,
) -> tuple[
    BuildReadinessReport,
    QuenchRiskReport,
    CoilGeometryReport,
    ACLossReport,
    QuenchPropagationReport,
    JointResistanceReport,
    FieldUniformityReport,
    MechanicalFatigueReport,
]:
    readiness, quench, geometry, ac_loss, propagation = run_research_foundation_assessment(
        material,
        cryo,
        design,
        ac_sweep_hz=ac_sweep_hz,
    )
    joint = assess_joint_resistance(design, cryo)
    uniformity = assess_field_uniformity(design)
    fatigue = assess_mechanical_fatigue(design)
    return readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue


def run_material_research_assessment(
    material: MaterialCandidate,
    cryo: CryoProfile,
    design: MagnetDesign,
    *,
    ac_sweep_hz: float = 5.0,
) -> tuple[
    BuildReadinessReport,
    QuenchRiskReport,
    CoilGeometryReport,
    ACLossReport,
    QuenchPropagationReport,
    JointResistanceReport,
    FieldUniformityReport,
    MechanicalFatigueReport,
    MaterialScreeningReport,
    SpliceTopologyReport,
    RampProfileReport,
    SpliceMatrixReport,
    RampDynamicsReport,
]:
    readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue = run_extended_research_assessment(
        material,
        cryo,
        design,
        ac_sweep_hz=ac_sweep_hz,
    )
    screening = assess_material_screening(material, cryo, design)
    splice = assess_splice_topology(design)
    ramp = assess_ramp_profile(design)
    splice_matrix = assess_splice_matrix(design)
    ramp_dynamics = assess_ramp_dynamics(design)
    return (
        readiness,
        quench,
        geometry,
        ac_loss,
        propagation,
        joint,
        uniformity,
        fatigue,
        screening,
        splice,
        ramp,
        splice_matrix,
        ramp_dynamics,
    )


def compare_material_candidates(
    materials: list[MaterialCandidate],
    cryo: CryoProfile,
    design: MagnetDesign,
) -> MaterialRankingReport:
    return rank_material_candidates(materials, cryo, design)
