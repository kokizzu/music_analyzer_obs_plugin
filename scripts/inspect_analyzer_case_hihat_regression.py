#!/usr/bin/env python3
"""Print the melodic full-mix hi-hat regression case and final hi-hat routes."""

from pathlib import Path


def print_matches(path: Path, terms: tuple[str, ...], context: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if any(term.lower() in line.lower() for term in terms):
            seen.update(range(max(0, index - context), min(len(lines), index + context + 1)))
    print(f"== {path} ==")
    for index in sorted(seen):
        print(f"{index + 1:5}: {lines[index]}")


def main() -> None:
    case_lines = Path("tests/analyzer_cases.cpp").read_text(encoding="utf-8").splitlines()
    print("== tests/analyzer_cases.cpp:1-105 ==")
    for index, line in enumerate(case_lines[:105], 1):
        print(f"{index:5}: {line}")
    print_matches(
        Path("tests/analyzer_cases.cpp"),
        ("melodic full mix no drums", "expected HIHAT inactive", "expect_no_drums",
         "add_harmonic_note", "make_harmonic_notes"),
        16,
    )
    print_matches(
        Path("src/analyzer.hpp"),
        ("drum_debug_trigger_scores", "drum_debug_rule_flags", "drum_debug"),
        4,
    )
    print_matches(
        Path("src/analyzer.cpp"),
        (
            "final_real_mix",
            "full_mix_idle_hihat_floor",
            "DrumDebugHighLocalHihatRecovery",
            "const bool drum_transient",
        ),
        10,
    )


if __name__ == "__main__":
    main()
