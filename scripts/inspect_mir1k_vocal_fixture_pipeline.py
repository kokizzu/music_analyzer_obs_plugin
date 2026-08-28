#!/usr/bin/env python3
"""Show the MIR-1K fixture manifest and generic real-note harness contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    ROOT / "scripts" / "sync_mir1k_vocal_test_fixtures.py",
    ROOT / "tests" / "fixtures" / "mir1k_clean_vocals" / "manifest.tsv",
    ROOT / "build" / "mir1k_vocal_full_mix_attributes.tsv",
    ROOT / "tests" / "analyzer_real_note_samples.cpp",
)
NEEDLES = ("manifest", "MIR", "REAL_NOTE", "sample_root", "required_samples", "ATTRIBUTE")


def main() -> int:
    for path in PATHS:
        print(f"=== {path.relative_to(ROOT)} ===")
        if not path.exists():
            print("missing")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if path.name == "manifest.tsv" or path.name.endswith("attributes.tsv"):
            for line in lines[:24]:
                print(line)
            print(f"rows: {max(0, len(lines) - 1)}")
            continue
        if path.name == "analyzer_real_note_samples.cpp":
            printed: set[int] = set()
            for number, line in enumerate(lines, start=1):
                if not any(marker in line for marker in
                           ("required_samples", "attribute_path_env", "attribute_export")):
                    continue
                for index in range(max(0, number - 4), min(len(lines), number + 6)):
                    if index in printed:
                        continue
                    printed.add(index)
                    print(f"{index + 1:5}: {lines[index]}")
                print()
            continue
        for number, line in enumerate(lines, start=1):
            if not any(needle.lower() in line.lower() for needle in NEEDLES):
                continue
            for index in range(max(0, number - 3), min(len(lines), number + 7)):
                print(f"{index + 1:5}: {lines[index]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
