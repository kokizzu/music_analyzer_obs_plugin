#!/usr/bin/env python3
"""Print every vocal-candidate insertion path used by the full-mix grid."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    hits = [index for index, line in enumerate(lines)
            if "vocal_candidates" in line or "kEnableMeasuredHighSopranoVocalMirror" in line]
    for hit in hits:
        print(f"== {hit + 1} ==")
        for index in range(max(0, hit - 7), min(len(lines), hit + 8)):
            print(f"{index + 1}: {lines[index]}")


if __name__ == "__main__":
    main()
