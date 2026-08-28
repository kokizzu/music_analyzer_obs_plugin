#!/usr/bin/env python3
"""Print the narrow IsolatedOther candidate/envelope handoff in analyzer.cpp."""

from pathlib import Path


SOURCE = Path("src/analyzer.cpp")
SECTIONS = (
    ("void smooth_note_grid_envelope(", 82),
    ("void set_instrument_note_set(", 155),
    ("kMonophonicOtherQuietRecoveryFloor", 6),
    ("kMonophonicOtherImmediateConfirmFloor", 6),
    ("const std::array<bool, kNoteProbeCount> *other_allowed_midis", 240),
    ("set_instrument_note_set(snapshot.other_notes", 95),
)


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    emitted: set[int] = set()
    for needle, context in SECTIONS:
        index = next((position for position, line in enumerate(lines) if needle in line), None)
        if index is None:
            continue
        start = max(0, index - 8)
        end = min(len(lines), index + context + 1)
        if any(position in emitted for position in range(start, end)):
            continue
        emitted.update(range(start, end))
        print(f"--- {SOURCE}:{index + 1} ---")
        for position in range(start, end):
            print(f"{position + 1:5}: {lines[position]}")


if __name__ == "__main__":
    main()
