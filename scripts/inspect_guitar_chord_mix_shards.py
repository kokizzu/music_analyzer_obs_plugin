#!/usr/bin/env python3
"""Summarize incorrect primary guitar-chord labels from shard output."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
FIELD = re.compile(r"([A-Za-z_]+)=([^\s]+)")
KEYWORDS = ("chord", "expected", "primary", "detected", "label")


def is_miss(line: str) -> bool:
    lowered = line.lower()
    if not any(keyword in lowered for keyword in KEYWORDS):
        return False
    return any(token in lowered for token in ("miss", "fail", "wrong", "false", "primary=0", "hit=0"))


def main() -> int:
    files = sorted((ROOT / "build").glob("guitar_chord_mix_samples_shard_*.out"))
    if not files:
        raise SystemExit("no guitar chord shard outputs found; run test-guitar-chord-mix-samples-parallel first")
    fields = Counter()
    misses: list[str] = []
    samples: list[str] = []
    for path in files:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            for key, value in FIELD.findall(line):
                if key.lower() in {"expected", "detected", "primary", "chord", "label"}:
                    fields[f"{key}={value}"] += 1
            if is_miss(line):
                misses.append(f"{path.name}: {line}")
            elif any(keyword in line.lower() for keyword in KEYWORDS):
                samples.append(f"{path.name}: {line}")
    print(f"shards: {len(files)}")
    print("chord fields:")
    for item, count in fields.most_common(80):
        print(f"  {count:4} {item}")
    print(f"candidate misses: {len(misses)}")
    for line in misses[:160]:
        print(line)
    if not misses:
        print("representative chord lines:")
        for line in samples[:160]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
