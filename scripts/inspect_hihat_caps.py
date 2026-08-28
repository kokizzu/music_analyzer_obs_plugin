#!/usr/bin/env python3
"""Print every final-arbitration cap or recovery that changes the hi-hat level."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"
NEEDLES = ("cap_drum_level(HiHat", "boost_drum_level(HiHat", "promote_drum_primary(HiHat")


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print("## generated-GM hi-hat conditions")
    for index, line in enumerate(lines):
        if "generated_gm_drum_source" not in line:
            continue
        context = "\n".join(lines[max(0, index - 6):min(len(lines), index + 14)])
        if "HiHat" not in context:
            continue
        for number in range(max(0, index - 6), min(len(lines), index + 14)):
            print(f"{number + 1}: {lines[number]}")

    print("## hi-hat cap conditions")
    for index, line in enumerate(lines):
        if "cap_drum_level(HiHat" not in line:
            continue
        for number in range(max(0, index - 14), min(len(lines), index + 3)):
            print(f"{number + 1}: {lines[number]}")

    print("## cap helper")
    for index, line in enumerate(lines):
        if "cap_drum_level" not in line or "=" not in line:
            continue
        for number in range(max(0, index - 3), min(len(lines), index + 12)):
            print(f"{number + 1}: {lines[number]}")
        break


if __name__ == "__main__":
    main()
