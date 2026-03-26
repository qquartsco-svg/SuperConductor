> **Korean (canonical):** [PHYSICS_PROXY_LIMITATIONS.md](PHYSICS_PROXY_LIMITATIONS.md)

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

## Recommended Usage

- Early candidate filtering (pre-screening)
- Sensitivity direction checks (temperature/field/current/stress)
- Narrowing expensive high-fidelity analysis scope

## Not Recommended

- Absolute critical-threshold guarantees
- Final machine protection decisions as sole evidence
- Standalone regulatory/qualification proof

