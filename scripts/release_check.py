from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    run([sys.executable, "scripts/verify_package_identity.py"])
    run([sys.executable, "scripts/verify_signature.py"])
    run([sys.executable, "-m", "pytest", "tests", "-q"])
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
