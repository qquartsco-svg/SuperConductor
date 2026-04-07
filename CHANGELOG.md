# Changelog

## 1.0.0

- aligned package metadata, README/README_EN, and release hygiene with the implemented `__version__ = "1.0.0"`
- promoted the stack from a narrow `0.9.0` material-ranking scaffold to a five-layer superconducting magnet foundation:
  - Layer 1: material database, critical-state, pinning, and strain-effects proxies
  - Layer 2: RK4 quench dynamics and protection-system screening
  - Layer 3: AC-loss decomposition and multiphysics rollup
  - Layer 4: sensitivity, uncertainty, and fault-tolerance research tools
  - Layer 5: application presets for LHC/HL-LHC/SPARC/MRI/SMES-style scenarios
- added release hygiene scripts for package identity checks, generated-cache cleanup, and one-command release checking
- expanded SHA-256 signature generation to cover the full source/documentation release surface while excluding generated artifacts

## 0.9.0

- added CLI material-candidate comparison mode via `--compare-materials`
- added compare payload adapter: `superconducting.magnet.material_ranking`
- added example payload for multi-candidate ranking
- expanded regression coverage for compare payload and CLI-facing ranking flow

## 0.8.0

- added multi-candidate material comparison scaffold:
  - `material_ranking`
  - `MaterialCandidateRank`
  - `MaterialRankingReport`
- added `compare_material_candidates()` pipeline helper
- expanded regression coverage for candidate ranking and comparison

## 0.7.0

- added deeper research scaffold layers:
  - `splice_matrix`
  - `ramp_dynamics`
- expanded `run_material_research_assessment()` to include splice-matrix and dynamic-ramp reports
- added regression coverage for the new research outputs

## 0.6.1

- added contract-level validation for non-physical inputs in:
  - `MaterialCandidate`
  - `CryoProfile`
  - `MagnetDesign`
- added regression tests for invalid input rejection
- refreshed README / README_EN verification counts and release text

## 0.6.0

- expanded README/README_EN with deeper concept explanations for unfamiliar readers
- added step-by-step design workflow and extension usage scenarios
- clarified scope/non-goals and practical integration boundaries
- added deterministic signature manifest generator (`scripts/generate_signature.py`)
- added publish runbook for `qquartsco-svg/SuperConductor`

## 0.5.0

- added material-research scaffold layers:
  - `material_screening`
  - `splice_topology`
  - `ramp_profile`
- added `run_material_research_assessment()`
- expanded the README to describe the next material research step from superconducting magnet design
- added integrity documentation and SHA-256 verification workflow

## 0.4.0

- added extended research scaffold layers:
  - `joint_resistance`
  - `field_uniformity`
  - `mechanical_fatigue`
- added `run_extended_research_assessment()`
- expanded tests and README to describe the next superconducting magnet research step

## 0.3.0

- added research-foundation scaffold layers:
  - `coil_geometry`
  - `ac_loss`
  - `quench_propagation`
- added `run_research_foundation_assessment()`
- expanded tests to cover research scaffold reports
- clarified the stack as a superconducting magnet research/design foundation rather than a full superconductivity platform

## 0.2.0

- Added `engine_ref` adapter: `superconducting.magnet.readiness`.
- Added JSON CLI entrypoint: `sc-magnet-assess`.
- Added sample payload for `design_workspace` style invocation.
- Added adapter-level test coverage.
- Added `tests/conftest.py` for package-root-independent test collection.
- Added `.gitignore` and clarified observer semantics in README / README_EN.

## 0.1.0

- Initial independent stack skeleton.
- Core contracts, material/thermal/safety/observer/pipeline modules.
- Basic readiness and quench assessment tests.
