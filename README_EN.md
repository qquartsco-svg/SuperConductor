> **English.** Korean (정본): [README.md](README.md)

# Superconducting Magnet Stack

This is not a one-shot “all-superconductor” engine.
It is an L1 independent stack focused on **superconducting magnet design, evaluation, and readiness verdicts**.

Version: `1.0.0`

One-line definition:
**a design kernel that converts material + cryogenic + electromagnetic/mechanical + quench risk into one readiness omega verdict**.

Interpretation note:
`1.0.0` should be read as a stabilized five-layer superconducting magnet research/design foundation, not as a finished plant/lab replacement platform.

Detailed docs:

- version policy: [docs/VERSIONING_POLICY_EN.md](docs/VERSIONING_POLICY_EN.md)
- physics proxy limits: [docs/PHYSICS_PROXY_LIMITATIONS_EN.md](docs/PHYSICS_PROXY_LIMITATIONS_EN.md)
- quench layered model: [docs/QUENCH_LAYER_MODEL_EN.md](docs/QUENCH_LAYER_MODEL_EN.md)

## Philosophy Alignment

- Applies the 00_BRAIN pattern: **physics kernelization + layered expansion**
- Targets design-time evaluation from candidate material parameters
- stdlib-only, independent packaging, test-first

## What this stack does / does not do

What it does:

- Quickly screens candidate magnet designs from material/cryo/design inputs
- Produces quench-aware readiness evidence for design decisions
- Exposes a stable `engine_ref` contract for `design_workspace`

What it does not do:

- New material discovery (DFT/lab replacement)
- High-fidelity multiphysics simulation replacement
- Manufacturing/process/qualification toolchain replacement

## Initial Layers

- `contracts`: `MaterialCandidate`, `CryoProfile`, `MagnetDesign`, `QuenchRiskReport`, `BuildReadinessReport`
- `material`: `Tc/Jc/Bc2` derating + `omega_material`
- `thermal`: cooling margin + `omega_thermal`
- `safety`: quench index + severity/recommendation
- `observer`: `omega_total` + verdict (`HEALTHY/STABLE/FRAGILE/CRITICAL`)
- `pipeline`: `run_magnet_design_assessment()`
- `engine_ref_adapter`: payload runner for `superconducting.magnet.readiness`
- `cli`: `sc-magnet-assess --input-json ... --json`

## Research foundation extensions

This stack is still not “all superconductivity research,”
but it now includes three scaffold layers that can serve as a realistic next step for
superconducting magnet research:
These expansion lines started as an early scaffold around `v0.3.0` and have been extended incrementally through `1.0.0`.

- `coil_geometry`: winding length, fill proxy, hoop-load index
- `ac_loss`: dynamic sweep AC-loss screening
- `quench_propagation`: NZPV proxy, hotspot risk, dump-window screening
- `joint_resistance`: joint-resistance and local heating screening
- `field_uniformity`: field uniformity / fringe-field proxy
- `mechanical_fatigue`: repeated ramp-load and fatigue-risk screening
- `material_screening`: candidate operating-margin and screening score
- `splice_topology`: splice count and topology penalty
- `ramp_profile`: ramp rate and dynamic stability penalty
- `splice_matrix`: splice-matrix complexity and current-imbalance risk
- `ramp_dynamics`: induced voltage, dynamic heating, and stability-window screening
- `material_ranking`: a screening layer that compares and ranks multiple candidate materials under the same design point

## v1.0.0 Five-Layer Structure

The point of `1.0.0` is not “all superconductivity solved.” It means the stack now has a stable five-layer foundation for reading superconducting magnets as a research/design system.

| Layer | Modules | Role |
|---|---|---|
| Layer 1 — Physics Foundation | `material_database`, `critical_state`, `pinning`, `strain_effects` | material families, critical-state proxies, vortex pinning, strain derating |
| Layer 2 — Transient Dynamics | `quench_dynamics`, `protection_system` | RK4 quench dynamics, MIIT/dump resistor/protection screening |
| Layer 3 — Multi-Physics | `ac_loss_decomposition`, `multiphysics_engine` | AC-loss decomposition and thermal/electromagnetic/mechanical proxy rollup |
| Layer 4 — Research Tools | `sensitivity_analysis`, `uncertainty_quantification`, `fault_tolerance` | sensitivity, uncertainty, and fault-tolerance screening |
| Layer 5 — Application Presets | `application_presets` | LHC/HL-LHC/SPARC/MRI/SMES-style reference comparisons |

These layers do not replace high-fidelity FEM or lab qualification. They provide a lower-level readiness language for MRF, Space Gate, Fusion, MRI, SMES, and other engines that need strong magnetic-field infrastructure.

So the most natural research path from here is:

1. coil / winding geometry
2. AC loss
3. quench propagation
4. joint resistance / field uniformity / fatigue
5. material screening / splice topology / ramp stability
6. splice matrix / ramp dynamics
7. material candidate ranking
8. critical-state / pinning / strain effects
9. quench dynamics / protection system
10. multiphysics / uncertainty / fault tolerance
11. application preset comparison

## Recommended design workflow

1. **Define material** via `MaterialCandidate` (`Tc/Jc/Bc2/anisotropy`)  
2. **Define operating point** via `CryoProfile` (temperature/heat-load/cooling-capacity)  
3. **Define magnet design** via `MagnetDesign` (field/current/cross-section/stress)  
4. **Run base verdict** via `run_magnet_design_assessment()`  
5. **Expand research scaffold** across AC-loss/NZPV/joint/uniformity/fatigue/screening  
6. **Integrate in L4** with `superconducting.magnet.readiness`
7. **Inspect v1 layers** through critical-state/pinning/strain/quench dynamics/protection/multiphysics/uncertainty/presets as needed

## Core concept notes (for new readers)

- `Tc`: critical temperature boundary
- `Jc`: critical current-density boundary
- `jc_a_per_mm2_77k` field note:
  - the name follows an HTS-friendly reference convention
  - in this stack, treat it as a **reference Jc input** for cross-candidate screening
- `Bc2`: high-field critical boundary indicator
- `quench`: normal-zone transition with thermal runaway risk
- `omega`: normalized 0..1 design health index
- `verdict`: `HEALTHY/STABLE/FRAGILE/CRITICAL`

## Core Equations (coarse design model)

- `Jc_derated = Jc0 * (1 - T/Tc) * (1 - B/Bc2) / anisotropy`
- `omega_total = 0.4*omega_material + 0.35*omega_thermal + 0.25*omega_quench`
- `omega_quench = 1 - quench_index`

This model is for architecture/design tradeoff evaluation, not lab-grade replacement.

## What `observer` means here

The `observer` in this stack is not a live sensor daemon.
In the current implementation it is a **design aggregation layer** that watches three computed axes
and collapses them into one readiness verdict:

- `material`
- `thermal`
- `safety (quench)`

So this observer should be read as:
**a readiness observer for candidate magnet designs**, not as a plant-floor monitoring runtime.

By contrast, the `pipeline` is the **execution orchestration layer** that calls the evaluation stages in order
and returns a bundled result set.
In short:

- `observer` = readiness aggregation / verdict
- `pipeline` = staged execution flow

## Quench expansion structure

Quench evaluation is intentionally layered:

1. base screening: `safety` (`quench_index`)
2. propagation layer: `quench_propagation` (NZPV/hotspot proxy)
3. local heating layer: `joint_resistance`
4. dump/ramp window layer: `ramp_profile` and `ramp_dynamics`

So quench is not modeled as one scalar only; it is structured to expand across propagation/local-heating/protection-window views.

## Quick Start

```python
from superconducting_magnet_stack import (
    MaterialCandidate, CryoProfile, MagnetDesign, run_magnet_design_assessment
)

material = MaterialCandidate("REBCO-like", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4)
cryo = CryoProfile(operating_temp_k=20.0, heat_load_w=12.0, cooling_capacity_w=30.0)
design = MagnetDesign(
    target_field_t=20.0,
    operating_current_a=600.0,
    conductor_cross_section_mm2=8.0,
    inductance_h=1.2,
    stored_energy_j=216000.0,
    stress_mpa=140.0,
)

readiness, quench = run_magnet_design_assessment(material, cryo, design)
print(readiness.verdict, readiness.omega_total)
print(quench.severity, quench.quench_index)
```

To inspect the research-foundation layer in one call:

```python
from superconducting_magnet_stack import run_research_foundation_assessment

reports = run_research_foundation_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation = reports
print(geometry.hoop_load_index, ac_loss.loss_w_per_m, propagation.nzpv_m_per_s)
```

To inspect the extended research layer in one call:

```python
from superconducting_magnet_stack import run_extended_research_assessment

reports = run_extended_research_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue = reports
print(joint.joint_resistance_n_ohm, uniformity.field_uniformity_index, fatigue.fatigue_risk_index)
```

To inspect the material-research foundation in one call:

```python
from superconducting_magnet_stack import run_material_research_assessment

reports = run_material_research_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue, screening, splice, ramp, splice_matrix, ramp_dynamics = reports
print(screening.screening_score, splice.splice_count, ramp.ramp_rate_t_per_s)
print(splice_matrix.current_imbalance_risk_index, ramp_dynamics.stability_window_index)
```

Candidate comparison:

```python
from superconducting_magnet_stack import compare_material_candidates

candidates = [
    MaterialCandidate("CandidateA", tc_k=82.0, jc_a_per_mm2_77k=250.0, bc2_t=100.0, anisotropy=1.5),
    MaterialCandidate("CandidateB", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4),
]
ranking = compare_material_candidates(candidates, cryo, design)
print(ranking.best_candidate)
for item in ranking.ranking:
    print(item.rank, item.name, item.screening_score)
```

Important:

- `material_ranking` is not an absolute optimizer or final material selector.
- In the current implementation it should be read as a **same-condition screening/ranking aid** under one cryogenic and design point.

CLI candidate comparison:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli \
  --input-json examples/material_compare_payload.json \
  --compare-materials \
  --json
```

## Test

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m pytest tests/ -q --tb=no
```

Current local verification baseline:

- inside the package root: `99 passed`
- outside the package root: collection works after adding `tests/conftest.py`
- coverage:
  - core: contracts/material/thermal/safety/observer/pipeline/engine_ref/cli
  - foundation scaffold: geometry/ac_loss/quench_propagation
  - extended scaffold: joint/uniformity/fatigue
  - material scaffold: screening/splice/ramp/splice_matrix/ramp_dynamics/ranking
  - v1 physics/dynamics: material_database/critical_state/pinning/strain/quench_dynamics/protection
  - v1 research tools: multiphysics/uncertainty/sensitivity/fault_tolerance/application_presets

Contract safety guard:

- `MaterialCandidate`, `CryoProfile`, and `MagnetDesign` now reject non-physical inputs at the contract layer.
- Examples:
  - empty material name
  - negative operating temperature
  - zero-or-negative conductor cross-section
- These now fail fast with `ValueError` instead of flowing into misleading screening math.

## Changelog / Integrity

- change summary: [CHANGELOG.md](CHANGELOG.md)
- integrity note: [BLOCKCHAIN_INFO.md](BLOCKCHAIN_INFO.md)
- continuity log: [PHAM_BLOCKCHAIN_LOG.md](PHAM_BLOCKCHAIN_LOG.md)
- SHA-256 manifest: [SIGNATURE.sha256](SIGNATURE.sha256)

Important:

- the word "blockchain" here does not mean a distributed consensus network
- in this repository it refers to an **integrity and continuity documentation pattern**
- actual verification is done through the SHA-256 manifest and verification script

Verification:

```bash
python3 scripts/verify_signature.py
```

Release gate:

```bash
python3 scripts/release_check.py
```

Regenerate signature manifest:

```bash
python3 scripts/generate_signature.py
python3 scripts/verify_signature.py
```

## design_workspace Integration (L4)

- proposed `engine_ref`: `superconducting.magnet.readiness`
- compare `engine_ref`: `superconducting.magnet.material_ranking`
- payload contract:
  - `material`: `name`, `tc_k`, `jc_a_per_mm2_77k`, `bc2_t`, `anisotropy?`
  - `cryo`: `operating_temp_k`, `heat_load_w`, `cooling_capacity_w`
  - `design`: `target_field_t`, `operating_current_a`, `conductor_cross_section_mm2`, `inductance_h`, `stored_energy_j`, `stress_mpa`

CLI:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli --input-json examples/sample_payload.json --json
```

Candidate comparison CLI:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli --input-json examples/material_compare_payload.json --compare-materials --json
```

## Extension usage scenarios

- **FusionCore coupling**: screen high-field magnet options by operating temperature and stress margin
- **StarCraft/L4 coupling**: append magnet readiness after power/thermal/memory/HBM scenario branches
- **Pre-lab design studies**: run quick parameter sensitivity checks before expensive experiments
- **Decision automation**: gate workflows from `verdict` and `quench_recommendation`

## GitHub publish guide (qquartsco-svg/SuperConductor)

```bash
cd _staging/Superconducting_Magnet_Stack
git init
git add .
git commit -m "Release Superconducting Magnet Stack v1.0.0"
git branch -M main
git remote add origin https://github.com/qquartsco-svg/SuperConductor.git
git push -u origin main
```
