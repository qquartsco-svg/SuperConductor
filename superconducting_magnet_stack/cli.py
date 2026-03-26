from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from .engine_ref_adapter import run_engine_ref_payload, run_material_compare_payload


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Superconducting magnet readiness assessment CLI")
    p.add_argument("--input-json", required=True, help="Path to payload json (material/cryo/design)")
    p.add_argument(
        "--compare-materials",
        action="store_true",
        help="Treat input as a materials[] candidate comparison payload",
    )
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    return p


def _load_payload(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("input payload must be a JSON object")
    return data


def main() -> int:
    args = _parser().parse_args()
    payload = _load_payload(args.input_json)
    if args.compare_materials:
        result = run_material_compare_payload(payload)
    else:
        result = run_engine_ref_payload(payload)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        if args.compare_materials:
            print(f"[{result['engine_ref']}] best={result['best_candidate']}")
            print(result["recommendation"])
        else:
            print(f"[{result['engine_ref']}] verdict={result['verdict']} omega={result['omega']:.3f}")
            print(f"quench={result['quench_severity']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
