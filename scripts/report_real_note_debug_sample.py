#!/usr/bin/env python3
"""Print any opt-in real-note debug sample records from shard outputs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    outputs = sorted((ROOT / "build").glob("real_note_full_mix_shard_*.out"))
    matches: list[str] = []
    for output in outputs:
        matches.extend(line for line in output.read_text(encoding="utf-8", errors="replace").splitlines()
                       if line.startswith("debug sample="))
    if not matches:
        source = ROOT / "tests" / "analyzer_real_note_samples.cpp"
        lines = source.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if "family_filter_env" not in line:
                continue
            for context in range(max(0, index - 4), min(len(lines), index + 5)):
                print(f"{source.relative_to(ROOT)}:{context + 1}: {lines[context]}")
            return 0
        raise SystemExit("no debug sample records or harness configuration found")
    for line in matches:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
