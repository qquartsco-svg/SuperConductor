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
    MaterialCandidateRank,
    MaterialRankingReport,
    MaterialCandidate,
    QuenchPropagationReport,
    QuenchRiskReport,
    RampDynamicsReport,
    RampProfileReport,
    SpliceMatrixReport,
    SpliceTopologyReport,
)
from .ac_loss import assess_ac_loss
from .coil_geometry import assess_coil_geometry
from .field_uniformity import assess_field_uniformity
from .joint_resistance import assess_joint_resistance
from .material_screening import assess_material_screening
from .material_ranking import rank_material_candidates
from .observer import assess_readiness
from .mechanical_fatigue import assess_mechanical_fatigue
from .pipeline import (
    run_extended_research_assessment,
    run_material_research_assessment,
    run_magnet_design_assessment,
    run_research_foundation_assessment,
    compare_material_candidates,
)
from .quench_propagation import assess_quench_propagation
from .ramp_dynamics import assess_ramp_dynamics
from .ramp_profile import assess_ramp_profile
from .safety import evaluate_quench_risk
from .splice_matrix import assess_splice_matrix
from .splice_topology import assess_splice_topology

__all__ = [
    "ACLossReport",
    "BuildReadinessReport",
    "CoilGeometryReport",
    "CryoProfile",
    "FieldUniformityReport",
    "JointResistanceReport",
    "MagnetDesign",
    "MechanicalFatigueReport",
    "MaterialCandidateRank",
    "MaterialRankingReport",
    "MaterialScreeningReport",
    "MaterialCandidate",
    "QuenchPropagationReport",
    "QuenchRiskReport",
    "RampDynamicsReport",
    "RampProfileReport",
    "SpliceMatrixReport",
    "SpliceTopologyReport",
    "assess_ac_loss",
    "assess_coil_geometry",
    "assess_field_uniformity",
    "assess_joint_resistance",
    "assess_mechanical_fatigue",
    "assess_material_screening",
    "rank_material_candidates",
    "assess_quench_propagation",
    "assess_readiness",
    "assess_ramp_dynamics",
    "assess_ramp_profile",
    "assess_splice_matrix",
    "assess_splice_topology",
    "evaluate_quench_risk",
    "run_extended_research_assessment",
    "compare_material_candidates",
    "run_material_research_assessment",
    "run_magnet_design_assessment",
    "run_research_foundation_assessment",
]

__version__ = "0.9.0"
