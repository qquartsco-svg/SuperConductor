> **Korean (canonical):** [QUENCH_LAYER_MODEL.md](QUENCH_LAYER_MODEL.md)

# Quench Layer Model

## Purpose

Document quench evaluation as a layered model rather than a single scalar.

## Layered Structure

1. **Base Screening (`safety`)**
   - computes initial risk via `quench_index`
   - provides immediate direction through `severity/recommendation`

2. **Propagation Layer (`quench_propagation`)**
   - decomposes risk with NZPV/hotspot proxies
   - captures dynamic spread tendency beyond one score

3. **Local Heating Layer (`joint_resistance`)**
   - identifies local vulnerabilities around joint resistance/heating
   - supports same-current design weakness comparison

4. **Protection Window Layer (`ramp_profile`, `ramp_dynamics`)**
   - combines ramp rate/induced voltage/dynamic heating for protection-window checks
   - supports dump-window sensitivity reasoning

## Output Interpretation

- Current implementation is screening-oriented, not a protection relay replacement.
- Use these outputs for candidate comparison and design prioritization, not absolute safety proof.

## Next Extensions

- application-specific protection policies (Fusion/MRI/Lab)
- stronger coupling between joint hotspot and propagation layers
- richer dump resistor / energy extraction modeling

