from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple


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
    stored_energy_j: float = 0.0
    stress_mpa: float = 0.0
    coil_length_m: float = 1.0
    operating_temp_k: float = 4.2  # 보조 필드 (StrainEffectsResult 호환)

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


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 — Physics Foundation  (v1.0)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MaterialRecord:
    """재료 데이터베이스 레코드 — 6대 초전도 패밀리 물성 저장."""
    name: str
    tc0_k: float                  # 무자장 임계온도 (K)
    bc20_t: float                 # T=0 상한임계자기장 (T)
    jc_ref_a_per_mm2: float       # 기준 임계전류밀도 (A/mm²)
    jc_ref_temp_k: float          # 기준 온도 (K)
    jc_ref_field_t: float         # 기준 자기장 (T)
    anisotropy_factor: float      # Bc2_ab / Bc2_c
    strain_sensitivity_c: float   # Ekin C 파라미터 (무차원)
    conductor_family: str         # "LTS" | "HTS"
    typical_filament_dia_um: float
    cu_sc_ratio: float

    def __post_init__(self) -> None:
        if self.tc0_k <= 0:
            raise ValueError("tc0_k must be > 0")
        if self.bc20_t <= 0:
            raise ValueError("bc20_t must be > 0")
        if self.jc_ref_a_per_mm2 <= 0:
            raise ValueError("jc_ref_a_per_mm2 must be > 0")


@dataclass(frozen=True)
class CriticalStateResult:
    """Bean/Kim/E-J 임계상태 모델 결과."""
    model: str                           # "Bean" | "Kim" | "PowerLaw"
    jc_local_a_per_mm2: float
    penetration_depth_m: float           # 자속 침투 깊이
    magnetization_a_per_m: float         # M = -Jc·d/3 (완전침투)
    hysteresis_loss_j_per_m3: float      # 반주기당 히스테리시스 손실
    e_field_v_per_m: float               # E-J 멱함수: 운전점에서의 E 필드


@dataclass(frozen=True)
class PinningResult:
    """보텍스 피닝 / 플럭스 크리프 분석 결과."""
    pinning_energy_j: float              # U0 (J)
    flux_creep_rate_normalized: float    # dJc/dt / Jc0 (s⁻¹)
    jc_after_creep_a_per_mm2: float      # 지정 시간 후 Jc
    irreversibility_field_t: float       # Hirr(T) (T)
    is_above_irreversibility_line: bool  # B_op > Hirr → Jc=0


@dataclass(frozen=True)
class StrainEffectsResult:
    """변형률 의존 물성 분석 결과."""
    epsilon_applied: float               # 인가 변형률 (무차원)
    epsilon_effective: float             # 유효 변형률 (ε - ε₀ₘ)
    s_epsilon: float                     # Ekin s(ε) [0,1]
    jc_strain_factor: float              # Jc(ε)/Jc(0) ∈ [0,1]
    tc_strain_k: float                   # Tc*(ε) (K)
    bc2_strain_t: float                  # Bc2*(ε) (T)
    is_irreversible: bool                # ε > ε_irr
    recommendation: str


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 — Transient Dynamics  (v1.1)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class QuenchDynamicsState:
    """RK4 퀀치 시뮬레이션 단일 스텝 상태."""
    time_s: float
    temp_k: float
    nz_length_m: float
    nz_velocity_m_per_s: float
    joule_power_w_per_m3: float
    cooling_power_w_per_m3: float
    miit_integral_a2s: float


@dataclass(frozen=True)
class QuenchDynamicsReport:
    """1D RK4 퀀치 전파 시뮬레이션 결과."""
    peak_hotspot_temp_k: float
    time_to_peak_s: float
    final_nz_length_m: float
    miit_value_a2s: float
    miit_limit_a2s: float
    is_destructive: bool
    trajectory: List[QuenchDynamicsState]
    recommendation: str


@dataclass(frozen=True)
class ProtectionSystemReport:
    """퀀치 보호 시스템 분석 결과."""
    optimal_dump_resistance_ohm: float
    current_decay_tau_s: float
    peak_dump_voltage_v: float
    estimated_hotspot_temp_k: float
    miit_total_a2s: float
    detection_delay_budget_s: float
    is_protected: bool
    recommendation: str


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3 — Multi-Physics Coupling  (v1.2)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SCState:
    """연성 다물리 RK4 상태 벡터 [T, I, ε, L_nz]."""
    time_s: float
    temp_k: float
    current_a: float
    strain: float
    nz_length_m: float


@dataclass(frozen=True)
class MultiphysicsReport:
    """전자기-열-기계 연성 시뮬레이션 결과."""
    peak_temp_k: float
    peak_strain: float
    final_current_a: float
    final_nz_length_m: float
    miit_total_a2s: float
    time_to_peak_s: float
    is_destructive: bool
    thermal_margin_ok: bool
    strain_margin_ok: bool
    trajectory: List[SCState]
    recommendation: str


@dataclass(frozen=True)
class ACLossDecompositionReport:
    """AC 손실 분해 분석 결과 (히스테리시스 / 와전류 / 결합)."""
    frequency_hz: float
    db_dt_t_per_s: float
    hysteretic_loss_w_per_m: float
    eddy_current_loss_w_per_m: float
    coupling_loss_w_per_m: float
    total_ac_loss_w_per_m: float
    dominant_mechanism: str            # "hysteretic" | "eddy" | "coupling"
    cooling_penalty_index: float
    recommendation: str


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 — Research Tools  (v1.3)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SensitivityResult:
    """단일 출력 지표에 대한 파라미터 민감도 결과."""
    output_name: str
    sensitivities: Dict[str, float]      # {param: S_i} 탄성 민감도
    morris_ee: Dict[str, float]          # {param: μ*} Morris EE
    dominant_param: str                  # 가장 영향력 큰 파라미터


@dataclass(frozen=True)
class SensitivityReport:
    """Jc·MIIT·열마진 3출력 종합 민감도 보고서."""
    results: Dict[str, SensitivityResult]   # {output_name: SensitivityResult}
    top_parameters: List[str]               # 중요도 상위 N
    recommendations: List[str]


@dataclass(frozen=True)
class UncertaintyReport:
    """Monte Carlo 불확실도 정량화 결과."""
    n_samples: int
    jc_stats: Dict[str, float]              # mean, std, P05, P50, P95, cv
    miit_stats: Dict[str, float]
    thermal_margin_stats: Dict[str, float]
    jc_reliability: bool
    miit_reliability: bool
    thermal_margin_reliability: bool
    highest_risk_parameter: str
    recommendations: List[str]


@dataclass(frozen=True)
class FaultToleranceReport:
    """Coffin-Manson 피로 수명 / MTBF / 결함 허용성 결과."""
    coffin_manson_cycles: float
    estimated_lifetime_years: float
    safety_factors: Dict[str, float]     # {SF_Jc, SF_T, SF_MIIT}
    mtbf_years: float
    reliability_1yr: float
    reliability_10yr: float
    critical_failure_modes: List[str]
    overall_assessment: str              # "ACCEPTABLE" | "MARGINAL" | "HIGH_RISK" | "CRITICAL"
    recommendation: str


# ─────────────────────────────────────────────────────────────────────────────
# Layer 5 — Application Presets  (v1.4)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ApplicationPreset:
    """참조 설계 프리셋 (LHC dipole, HL-LHC, Fusion TF, MRI, SMES)."""
    name: str
    material: MaterialCandidate
    cryo: CryoProfile
    design: MagnetDesign
    description: str
    target_application: str
    key_challenges: List[str]


@dataclass(frozen=True)
class PresetComparisonReport:
    """응용 사례 프리셋 간 비교 결과."""
    preset_names: List[str]
    comparison_table: List[Dict]         # [{name, material, field_t, ...}]
    best_jc_preset: str
    best_field_preset: str
    highest_energy_preset: str
    summary: str
