from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "superconducting_magnet_stack"

REQUIRED = [
    ROOT / "pyproject.toml",
    ROOT / "VERSION",
    ROOT / "README.md",
    ROOT / "README_EN.md",
    ROOT / "CHANGELOG.md",
    ROOT / "BLOCKCHAIN_INFO.md",
    ROOT / "PHAM_BLOCKCHAIN_LOG.md",
    ROOT / "docs" / "VERSIONING_POLICY.md",
    ROOT / "docs" / "PHYSICS_PROXY_LIMITATIONS.md",
    ROOT / "docs" / "QUENCH_LAYER_MODEL.md",
    PACKAGE / "__init__.py",
    PACKAGE / "contracts.py",
    PACKAGE / "pipeline.py",
    PACKAGE / "critical_state.py",
    PACKAGE / "pinning.py",
    PACKAGE / "strain_effects.py",
    PACKAGE / "quench_dynamics.py",
    PACKAGE / "protection_system.py",
    PACKAGE / "multiphysics_engine.py",
    PACKAGE / "uncertainty_quantification.py",
    PACKAGE / "application_presets.py",
    ROOT / "tests" / "test_superconducting_magnet_stack.py",
    ROOT / "tests" / "test_physics_foundation.py",
]


def read_version_from_pyproject() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        raise ValueError("pyproject.toml missing project version")
    return match.group(1)


def read_version_from_init() -> str:
    text = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        raise ValueError("__init__.py missing __version__")
    return match.group(1)


def main() -> int:
    missing = [p.relative_to(ROOT).as_posix() for p in REQUIRED if not p.exists()]
    if missing:
        print("Missing required files:")
        for item in missing:
            print(f"  - {item}")
        return 1

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject_version = read_version_from_pyproject()
    init_version = read_version_from_init()
    if len({version, pyproject_version, init_version}) != 1:
        print("Version mismatch:")
        print(f"  VERSION: {version}")
        print(f"  pyproject.toml: {pyproject_version}")
        print(f"  __init__.py: {init_version}")
        return 1

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
    expected = f"Version: `{version}`"
    if expected not in readme or expected not in readme_en:
        print(f"README version marker missing: {expected}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
