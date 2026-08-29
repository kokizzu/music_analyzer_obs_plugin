#!/usr/bin/env python3
"""Summarize full-mix vocal ownership misses from the repeatable audit output."""

from __future__ import annotations

from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "build" / "real_note_vocal_audit.out"


def main() -> int:
    if not AUDIT.is_file():
        raise SystemExit("missing vocal audit; run make audit-real-note-vocals first")
    lines = AUDIT.read_text(encoding="utf-8", errors="replace").splitlines()
    misses = [line for line in lines if "expected-row ownership missing" in line]
    print(f"audit={AUDIT} ownership_misses={len(misses)}")
    corpus_counts = Counter("vocalset" if line.startswith("vocalset_") else "vocadito" for line in misses)
    row_counts = Counter(line.split("first-row=", 1)[1].split(" ", 1)[0] for line in misses)
    print("by-corpus=" + " ".join(f"{name}:{count}" for name, count in sorted(corpus_counts.items())))
    print("by-first-row=" + " ".join(f"{name}:{count}" for name, count in sorted(row_counts.items())))
    for line in misses:
        print(line)
    for line in lines:
        if line.startswith("analyzer_real_note_samples full-mix:"):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
