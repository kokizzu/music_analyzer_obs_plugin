#!/usr/bin/env python3
"""Print the real-drum fixture runner's selection policy and source roots."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNNER = ROOT / "tests" / "analyzer_real_drum_samples.cpp"
WRAPPER = ROOT / "scripts" / "test_real_drum_samples.sh"


def print_matches(lines: list[str], marker: str, context: int = 2) -> None:
    for index, line in enumerate(lines):
        if marker not in line:
            continue
        start = max(0, index - context)
        end = min(len(lines), index + context + 1)
        for line_number in range(start, end):
            print(f"{line_number + 1:6} {lines[line_number]}")
        print()


def main() -> int:
    lines = RUNNER.read_text(encoding="utf-8").splitlines()
    print(f"runner={RUNNER.relative_to(ROOT)}")
    for marker in (
        "kDefaultRoot",
        "kMaximumSamplesPerCategory",
        "manifest.tsv",
        "MUSIC_ANALYZER_REAL_DRUM_ROOT",
        "kMaximumCasesPerClass",
        "source",
        "signatures",
        "one-shot",
        "last_snapshot",
        "drum_debug",
        "reported_misses",
        "REPORT_MISSES",
    ):
        print_matches(lines, marker)
    print(f"wrapper={WRAPPER.relative_to(ROOT)}")
    for line_number, line in enumerate(WRAPPER.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{line_number:6} {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
