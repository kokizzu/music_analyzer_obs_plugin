#!/usr/bin/env python3
"""Plan and remove confirmed zero-byte accidental top-level artifacts."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "build" / "suspicious-empty-artifacts.json"
NAMES = ("=0.04", "=0.163", "=0.713", "=1.137", "absent@4", "guitar", "ride", "tom")


def plan() -> int:
    selected = []
    for name in NAMES:
        path = ROOT / name
        if path.exists() and path.is_file() and path.stat().st_size == 0:
            selected.append({"name": name, "bytes": 0})
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(selected, indent=2) + "\n", encoding="utf-8")
    print(f"plan={PLAN}")
    for item in selected:
        print(f"delete={ROOT / item['name']} bytes={item['bytes']}")
    if not selected:
        print("delete=(none)")
    return 0


def apply() -> int:
    if not PLAN.exists():
        raise SystemExit(f"missing cleanup plan: {PLAN}; run the plan target first")
    selected = json.loads(PLAN.read_text(encoding="utf-8"))
    for item in selected:
        path = ROOT / item["name"]
        if not path.exists() or not path.is_file() or path.stat().st_size != item["bytes"]:
            raise SystemExit(f"cleanup plan changed or target is no longer empty: {path}")
    for item in selected:
        path = ROOT / item["name"]
        path.unlink()
        print(f"deleted={path}")
    return 0


if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
    raise SystemExit("usage: cleanup_suspicious_empty_artifacts.py plan|apply")
sys.exit(plan() if sys.argv[1] == "plan" else apply())
