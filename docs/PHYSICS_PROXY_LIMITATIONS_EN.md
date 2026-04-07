> **English.** Korean (정본): [PHYSICS_PROXY_LIMITATIONS.md](PHYSICS_PROXY_LIMITATIONS.md)

# Physics Proxy Limitations

## Purpose

Explicitly document that the core equations are screening-oriented proxies, not high-fidelity physics solvers.

## Core Limits

- `Jc_derated = Jc0 * (1 - T/Tc) * (1 - B/Bc2) / anisotropy` is a coarse approximation.
- Real `Jc(B,T,epsilon)` behavior is strongly nonlinear and material-family dependent.
- Use this equation for relative screening, not absolute performance certification.

## Omega Weighting Limits

- Current `omega_total = 0.4*material + 0.35*thermal + 0.25*quench` is an MVP policy weighting.
- Target domains (Fusion/MRI/Lab magnet) may require different weighting profiles.
- Profile-based weighting policies are recommended as a next step.

## v1.0.0 Layer Limitations

- `critical_state`, `pinning`, and `strain_effects` are proxies, not replacements for material-specific experimental curves.
- `quench_dynamics` and `protection_system` do not replace protection relays, safety certification, or hardware validation.
- `multiphysics_engine` is an integrated screening rollup across thermal/electromagnetic/mechanical effects; it is not a FEM/FEA solver.
- `uncertainty_quantification` gives a first-order range sense under input perturbations, not a fully validated statistical uncertainty model.
- `application_presets` provide LHC/HL-LHC/SPARC/MRI/SMES-style comparison baselines, not guaranteed design constants.

## Recommended Usage

- Early candidate filtering (pre-screening)
- Sensitivity direction checks (temperature/field/current/stress)
- Narrowing expensive high-fidelity analysis scope

## Not Recommended

- Absolute critical-threshold guarantees
- Final machine protection decisions as sole evidence
- Standalone regulatory/qualification proof
