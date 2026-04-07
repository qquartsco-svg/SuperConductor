from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SIGNATURE.sha256"

INCLUDE_SUFFIXES = {".md", ".py", ".toml", ".json"}
INCLUDE_NAMES = {"VERSION", "LICENSE"}
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
}


def should_sign(path: Path) -> bool:
    rel_parts = set(path.relative_to(ROOT).parts)
    if rel_parts & EXCLUDED_PARTS:
        return False
    if any(part.endswith(".egg-info") for part in rel_parts):
        return False
    if path.name == MANIFEST.name:
        return False
    return path.name in INCLUDE_NAMES or path.suffix in INCLUDE_SUFFIXES


def signed_files() -> list[Path]:
    return sorted(
        (path for path in ROOT.rglob("*") if path.is_file() and should_sign(path)),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    lines = []
    for target in signed_files():
        rel = target.relative_to(ROOT).as_posix()
        lines.append(f"{sha256_of(target)}  {rel}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"updated {MANIFEST.name} with {len(lines)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
