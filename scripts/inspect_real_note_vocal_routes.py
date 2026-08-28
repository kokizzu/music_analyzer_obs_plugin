#!/usr/bin/env python3
"""Show sample-level vocal routing evidence from cached full-mix shards."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    matched: list[str] = []
    for path in sorted((ROOT / "build").glob("detector_real_note_full_mix_shard_*.out")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            lower = line.lower()
            if "vocal" in lower and ("sample" in lower or "failure" in lower or "expected" in lower):
                matched.append(f"{path.name}: {line}")
    print(f"vocal route evidence lines: {len(matched)}")
    for line in matched[:80]:
        print(line)


if __name__ == "__main__":
    main()
