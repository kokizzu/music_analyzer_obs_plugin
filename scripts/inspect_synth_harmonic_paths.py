#!/usr/bin/env python3
"""Print existing full-mix low-synth harmonic suppression paths."""

from __future__ import annotations

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "analyzer.cpp"
TERMS = ("low_synth", "synth_harmonic", "harmonic_prune", "full_mix_low_synth")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    starts = []
    for index, line in enumerate(lines):
        if any(term in line for term in TERMS):
            if not starts or index - starts[-1] > 30:
                starts.append(index)
    for start in starts[:20]:
        print(f"# {SOURCE.name}:{start + 1}")
        for index in range(start, min(len(lines), start + 40)):
            print(f"{index + 1}: {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
