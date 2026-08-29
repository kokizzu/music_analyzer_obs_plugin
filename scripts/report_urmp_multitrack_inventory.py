#!/usr/bin/env python3
"""Report the externally cached URMP multitrack corpus without scanning Git media."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CORPUS_LINK = REPOSITORY_ROOT / "build" / "urmp_multitrack_samples"


def instrument_from_name(path: Path) -> str | None:
    match = re.search(r"(?:AuSep|Notes|F0s)_\d+_([^_]+)_", path.name)
    return match.group(1) if match else None


def main() -> int:
    if not CORPUS_LINK.is_symlink():
        print(f"status=missing link={CORPUS_LINK}")
        return 1

    target = CORPUS_LINK.resolve(strict=False)
    root = CORPUS_LINK / "urmp_yourmt3_16k"
    if not root.is_dir():
        print(f"link-target={target}")
        print(f"status=missing audio-root={root}")
        return 1

    pieces = sorted(path for path in root.iterdir() if path.is_dir())
    mixes = sorted(root.rglob("AuMix_*.wav"))
    stems = sorted(root.rglob("AuSep_*.wav"))
    notes = sorted(root.rglob("Notes_*.txt"))
    f0s = sorted(root.rglob("F0s_*.txt"))
    midi = sorted(root.rglob("Sco_*.mid"))
    score_notes = sorted(root.rglob("Sco_*.notes.json"))
    instruments = Counter(instrument for path in stems if (instrument := instrument_from_name(path)))

    print("dataset=URMP multitrack real-instrument corpus")
    print(f"link={CORPUS_LINK}")
    print(f"external-root={root}")
    print(f"pieces={len(pieces)}")
    print(f"mixtures={len(mixes)}")
    print(f"isolated-stems={len(stems)}")
    print(f"note-annotations={len(notes)}")
    print(f"f0-annotations={len(f0s)}")
    print(f"midi-scores={len(midi)}")
    print(f"json-note-scores={len(score_notes)}")
    print("instrument-stems=" + ",".join(f"{name}={count}" for name, count in sorted(instruments.items())))

    example = notes[0] if notes else None
    if example:
        lines = [line.strip() for line in example.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(f"annotation-example={example.relative_to(root)}")
        print(f"annotation-first={lines[0] if lines else '<empty>'}")
    if score_notes:
        try:
            payload = json.loads(score_notes[0].read_text(encoding="utf-8"))
            print("json-annotation-type=" + type(payload).__name__)
        except json.JSONDecodeError:
            print("json-annotation-type=invalid")

    print("storage=external-only; Git stores neither audio nor annotations")
    print("status=ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
