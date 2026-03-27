from .contracts import (
    # Original
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
    # Layer 1 — Physics Foundation
    MaterialRecord,
    CriticalStateResult,
    PinningResult,
    StrainEffectsResult,
    # Layer 2 — Transient Dynamics
    QuenchDynamicsState,
    QuenchDynamicsReport,
    ProtectionSystemReport,
    # Layer 3 — Multi-Physics
    SCState,
    MultiphysicsReport,
    ACLossDecompositionReport,
    # Layer 4 — Research Tools
    SensitivityResult,
    SensitivityReport,
    UncertaintyReport,
    FaultToleranceReport,
    # Layer 5 — Application Presets
    ApplicationPreset,
    PresetComparisonReport,
)

# ── Original modules ──────────────────────────────────────────────────────────
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

# ── Layer 1 — Physics Foundation ─────────────────────────────────────────────
from .material_database import (
    get_material,
    list_materials,
    bc2_at_temp,
    jc_critical_surface,
)
from .critical_state import (
    ej_power_law,
    bean_jc_profile,
    kim_jc_profile,
    power_law_state,
)
from .pinning import (
    vortex_pinning_energy_j,
    anderson_kim_creep_rate,
    jc_after_creep,
    irreversibility_field_t,
    assess_pinning,
)
from .strain_effects import (
    ekin_devantay_s,
    rebco_jc_strain_factor,
    jc_with_strain,
    assess_strain_effects,
)

# ── Layer 2 — Transient Dynamics ─────────────────────────────────────────────
from .quench_dynamics import simulate_quench_rk4
from .protection_system import (
    miit_exponential_decay,
    optimal_dump_resistance,
    assess_protection_system,
)

# ── Layer 3 — Multi-Physics ───────────────────────────────────────────────────
from .ac_loss_decomposition import assess_ac_loss_decomposition
from .multiphysics_engine import simulate_multiphysics

# ── Layer 4 — Research Tools ──────────────────────────────────────────────────
from .sensitivity_analysis import assess_sensitivity
from .uncertainty_quantification import assess_uncertainty
from .fault_tolerance import assess_fault_tolerance

# ── Layer 5 — Application Presets ────────────────────────────────────────────
from .application_presets import (
    get_preset,
    list_presets,
    compare_presets,
    get_lhc_dipole_preset,
    get_hl_lhc_quadrupole_preset,
    get_sparc_tf_preset,
    get_mri_preset,
    get_smes_preset,
)

__all__ = [
    # contracts — original
    "ACLossReport", "BuildReadinessReport", "CoilGeometryReport",
    "CryoProfile", "FieldUniformityReport", "JointResistanceReport",
    "MagnetDesign", "MechanicalFatigueReport", "MaterialScreeningReport",
    "MaterialCandidateRank", "MaterialRankingReport", "MaterialCandidate",
    "QuenchPropagationReport", "QuenchRiskReport", "RampDynamicsReport",
    "RampProfileReport", "SpliceMatrixReport", "SpliceTopologyReport",
    # contracts — Layer 1
    "MaterialRecord", "CriticalStateResult", "PinningResult", "StrainEffectsResult",
    # contracts — Layer 2
    "QuenchDynamicsState", "QuenchDynamicsReport", "ProtectionSystemReport",
    # contracts — Layer 3
    "SCState", "MultiphysicsReport", "ACLossDecompositionReport",
    # contracts — Layer 4
    "SensitivityResult", "SensitivityReport", "UncertaintyReport", "FaultToleranceReport",
    # contracts — Layer 5
    "ApplicationPreset", "PresetComparisonReport",
    # original functions
    "assess_ac_loss", "assess_coil_geometry", "assess_field_uniformity",
    "assess_joint_resistance", "assess_mechanical_fatigue", "assess_material_screening",
    "rank_material_candidates", "assess_quench_propagation", "assess_readiness",
    "assess_ramp_dynamics", "assess_ramp_profile", "assess_splice_matrix",
    "assess_splice_topology", "evaluate_quench_risk",
    "run_extended_research_assessment", "compare_material_candidates",
    "run_material_research_assessment", "run_magnet_design_assessment",
    "run_research_foundation_assessment",
    # Layer 1 functions
    "get_material", "list_materials", "bc2_at_temp", "jc_critical_surface",
    "ej_power_law", "bean_jc_profile", "kim_jc_profile", "power_law_state",
    "vortex_pinning_energy_j", "anderson_kim_creep_rate", "jc_after_creep",
    "irreversibility_field_t", "assess_pinning",
    "ekin_devantay_s", "rebco_jc_strain_factor", "jc_with_strain", "assess_strain_effects",
    # Layer 2 functions
    "simulate_quench_rk4",
    "miit_exponential_decay", "optimal_dump_resistance", "assess_protection_system",
    # Layer 3 functions
    "assess_ac_loss_decomposition", "simulate_multiphysics",
    # Layer 4 functions
    "assess_sensitivity", "assess_uncertainty", "assess_fault_tolerance",
    # Layer 5 functions
    "get_preset", "list_presets", "compare_presets",
    "get_lhc_dipole_preset", "get_hl_lhc_quadrupole_preset",
    "get_sparc_tf_preset", "get_mri_preset", "get_smes_preset",
]

__version__ = "1.0.0"
