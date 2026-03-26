> **Korean (canonical):** [VERSIONING_POLICY.md](VERSIONING_POLICY.md)

# Superconducting Magnet Stack Versioning Policy

## Purpose

Align user expectations between version numbers and practical implementation maturity.
This document formalizes the interpretation note already present in `README.md`.

## Interpretation Principles

- `0.x.y` means research/design scaffold stage.
- The current stack is not a full process/lab replacement; it is a screening-oriented design kernel.
- Version bumps prioritize "contract stability + extension breadth" over absolute product completeness.

## Current Release Interpretation

- `0.1.x`: minimal contracts + readiness skeleton
- `0.2.x`: L4 `engine_ref` integration and CLI execution path
- `0.3.x` ~ `0.5.x`: research scaffold expansion (geometry/ac_loss/quench/joint/uniformity/fatigue/screening)
- `0.9.0`: broad integrated research-scaffold release (not a production-grade full solver)

## Recommended Bump Criteria

- **Patch (`x.y.Z`)**: doc consistency, minor math adjustments, test reinforcement
- **Minor (`x.Y.z`)**: new research layers/contracts, expanded CLI/adapter behavior
- **Major (`X.y.z`)**: breaking contract change or product-positioning change

## Message Template

Keep this sentence in release notes/README:

`This release expands a research/design scaffold and does not target high-fidelity process/lab replacement.`

