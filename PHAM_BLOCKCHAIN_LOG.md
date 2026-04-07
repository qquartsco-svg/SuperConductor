# PHAM_BLOCKCHAIN_LOG

## 2026-04-08

- aligned `VERSION`, `pyproject.toml`, README/README_EN, and changelog with `__version__ = "1.0.0"`
- documented the five-layer superconducting magnet foundation:
  - material database / critical state / pinning / strain effects
  - quench dynamics / protection system
  - AC-loss decomposition / multiphysics rollup
  - sensitivity / uncertainty / fault tolerance
  - application presets
- added release hygiene checks and generated-artifact cleanup
- expanded the SHA-256 signature manifest to cover the full release surface while excluding generated caches

## 2026-03-27

- added superconducting magnet research scaffold layers
  - `coil_geometry`
  - `ac_loss`
  - `quench_propagation`
  - `joint_resistance`
  - `field_uniformity`
  - `mechanical_fatigue`
  - `material_screening`
  - `splice_topology`
  - `ramp_profile`
- added package-root-independent test bootstrap
- added SHA-256 manifest verification flow
- aligned README / README_EN / VERSION / pyproject metadata with current research-foundation scope
- expanded README/README_EN with concept-heavy onboarding for unfamiliar readers
- documented full design workflow and extension usage scenarios
- added deterministic signature manifest generator (`scripts/generate_signature.py`)
