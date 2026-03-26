from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SIGNATURE.sha256"

SIGNED_FILES = [
    "README.md",
    "README_EN.md",
    "CHANGELOG.md",
    "BLOCKCHAIN_INFO.md",
    "PHAM_BLOCKCHAIN_LOG.md",
    "pyproject.toml",
    "VERSION",
    "examples/sample_payload.json",
    "examples/material_compare_payload.json",
    "superconducting_magnet_stack/__init__.py",
    "superconducting_magnet_stack/contracts.py",
    "superconducting_magnet_stack/material.py",
    "superconducting_magnet_stack/thermal.py",
    "superconducting_magnet_stack/electromagnetic.py",
    "superconducting_magnet_stack/safety.py",
    "superconducting_magnet_stack/observer.py",
    "superconducting_magnet_stack/pipeline.py",
    "superconducting_magnet_stack/engine_ref_adapter.py",
    "superconducting_magnet_stack/cli.py",
    "superconducting_magnet_stack/coil_geometry.py",
    "superconducting_magnet_stack/ac_loss.py",
    "superconducting_magnet_stack/quench_propagation.py",
    "superconducting_magnet_stack/joint_resistance.py",
    "superconducting_magnet_stack/field_uniformity.py",
    "superconducting_magnet_stack/mechanical_fatigue.py",
    "superconducting_magnet_stack/material_screening.py",
    "superconducting_magnet_stack/material_ranking.py",
    "superconducting_magnet_stack/splice_topology.py",
    "superconducting_magnet_stack/splice_matrix.py",
    "superconducting_magnet_stack/ramp_dynamics.py",
    "superconducting_magnet_stack/ramp_profile.py",
    "tests/test_superconducting_magnet_stack.py",
    "tests/conftest.py",
    "scripts/verify_signature.py",
    "scripts/generate_signature.py",
]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    lines = []
    for rel in SIGNED_FILES:
        target = ROOT / rel
        if not target.exists():
            raise FileNotFoundError(f"missing signed file: {rel}")
        lines.append(f"{sha256_of(target)}  {rel}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"updated {MANIFEST.name} with {len(lines)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
