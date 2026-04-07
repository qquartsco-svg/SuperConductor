from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def remove_path(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return 1


def main() -> int:
    removed = 0
    for name in ("__pycache__", ".pytest_cache", ".DS_Store"):
        for path in ROOT.rglob(name):
            removed += remove_path(path)
    for path in ROOT.rglob("*.egg-info"):
        removed += remove_path(path)
    print(f"removed={removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
