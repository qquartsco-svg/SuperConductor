from dataclasses import dataclass, field
from typing import Dict, Literal


@dataclass(frozen=True)
class MaterialCandidate:
    name: str
    tc_k: float
    jc_a_per_mm2_77k: float
    bc2_t: float
    anisotropy: float = 1.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be a non-empty material identifier")
        if self.tc_k <= 0.0:
            raise ValueError("tc_k must be > 0")
        if self.jc_a_per_mm2_77k <= 0.0:
            raise ValueError("jc_a_per_mm2_77k must be > 0")
        if self.bc2_t <= 0.0:
            raise ValueError("bc2_t must be > 0")
        if self.anisotropy <= 0.0:
            raise ValueError("anisotropy must be > 0")


@dataclass(frozen=True)
class CryoProfile:
    operating_temp_k: float
    heat_load_w: float
    cooling_capacity_w: float

    def __post_init__(self) -> None:
        if self.operating_temp_k < 0.0:
            raise ValueError("operating_temp_k must be >= 0")
        if self.heat_load_w < 0.0:
            raise ValueError("heat_load_w must be >= 0")
        if self.cooling_capacity_w < 0.0:
            raise ValueError("cooling_capacity_w must be >= 0")


@dataclass(frozen=True)
class MagnetDesign:
    target_field_t: float
    operating_current_a: float
    conductor_cross_section_mm2: float
    inductance_h: float
    stored_energy_j: float
    stress_mpa: float

    def __post_init__(self) -> None:
        if self.target_field_t < 0.0:
            raise ValueError("target_field_t must be >= 0")
        if self.operating_current_a < 0.0:
            raise ValueError("operating_current_a must be >= 0")
        if self.conductor_cross_section_mm2 <= 0.0:
            raise ValueError("conductor_cross_section_mm2 must be > 0")
        if self.inductance_h <= 0.0:
            raise ValueError("inductance_h must be > 0")
        if self.stored_energy_j < 0.0:
            raise ValueError("stored_energy_j must be >= 0")
        if self.stress_mpa < 0.0:
            raise ValueError("stress_mpa must be >= 0")


@dataclass(frozen=True)
class QuenchRiskReport:
    quench_index: float
    severity: Literal["low", "medium", "high", "critical"]
    recommendation: str


@dataclass(frozen=True)
class BuildReadinessReport:
    omega_material: float
    omega_thermal: float
    omega_quench: float
    omega_total: float
    verdict: Literal["HEALTHY", "STABLE", "FRAGILE", "CRITICAL"]
    evidence: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class CoilGeometryReport:
    winding_window_fill: float
    mean_turn_length_m: float
    hoop_load_index: float
    recommendation: str


@dataclass(frozen=True)
class ACLossReport:
    sweep_hz: float
    loss_w_per_m: float
    cooling_penalty_index: float
    recommendation: str


@dataclass(frozen=True)
class QuenchPropagationReport:
    nzpv_m_per_s: float
    hotspot_risk_index: float
    dump_window_s: float
    recommendation: str


@dataclass(frozen=True)
class JointResistanceReport:
    joint_resistance_n_ohm: float
    resistive_heating_w: float
    stability_penalty_index: float
    recommendation: str


@dataclass(frozen=True)
class FieldUniformityReport:
    field_uniformity_index: float
    fringe_field_index: float
    recommendation: str


@dataclass(frozen=True)
class MechanicalFatigueReport:
    cycle_load_index: float
    fatigue_risk_index: float
    recommendation: str


@dataclass(frozen=True)
class MaterialScreeningReport:
    screening_score: float
    operating_margin_index: float
    recommendation: str


@dataclass(frozen=True)
class MaterialCandidateRank:
    name: str
    screening_score: float
    operating_margin_index: float
    rank: int
    recommendation: str


@dataclass(frozen=True)
class MaterialRankingReport:
    best_candidate: str
    ranking: list[MaterialCandidateRank]
    recommendation: str


@dataclass(frozen=True)
class SpliceTopologyReport:
    splice_count: int
    topology_penalty_index: float
    recommendation: str


@dataclass(frozen=True)
class RampProfileReport:
    ramp_rate_t_per_s: float
    stability_penalty_index: float
    recommendation: str


@dataclass(frozen=True)
class SpliceMatrixReport:
    matrix_complexity_index: float
    current_imbalance_risk_index: float
    recommendation: str


@dataclass(frozen=True)
class RampDynamicsReport:
    induced_voltage_v: float
    dynamic_heating_index: float
    stability_window_index: float
    recommendation: str
