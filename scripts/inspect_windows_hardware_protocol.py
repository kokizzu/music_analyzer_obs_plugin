#!/usr/bin/env python3
"""Print the small set of native Windows hardware protocol call sites."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = tuple(
    source
    for source in sorted((ROOT / "src").glob("windows_*") )
    if source.suffix in {".cpp", ".hpp", ".h"}
)
COMMIT_HELPER = ROOT / "scripts" / "commit_windows_hardware.py"
KEYWORDS = (
    "windows_midi_output_name_matches",
    "midiOutGetNumDevs",
    "midiOutOpen",
    "midiOutShortMsg",
    "Bluetooth",
    "fret zealot",
    "fretzealot",
    "LiteJam",
    "lite jam",
    "send_scale",
    "still_present",
)


def main() -> int:
    for source in SOURCES:
        print(f"=== {source.relative_to(ROOT)} ===")
        lines = source.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            if any(keyword.lower() in line.lower() for keyword in KEYWORDS):
                print(f"{number}: {line}")
    print(f"=== {COMMIT_HELPER.relative_to(ROOT)} ===")
    for number, line in enumerate(COMMIT_HELPER.read_text(encoding="utf-8").splitlines(), 1):
        if any(keyword in line for keyword in ("FILES", "inspect_windows", "test_windows")):
            print(f"{number}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
