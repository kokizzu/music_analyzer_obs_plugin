#!/usr/bin/env python3
"""Validate the prepared compact-IDMT bass fixture metadata."""

from __future__ import annotations

from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "build/idmt_bass_single_track_fixture"


def main() -> int:
    rows = (FIXTURE / "manifest.tsv").read_text(encoding="utf-8").splitlines()
    if not rows or rows[0] != "id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath":
        raise AssertionError("invalid IDMT bass fixture manifest header")
    samples = rows[1:]
    if len(samples) < 700:
        raise AssertionError(f"expected at least 700 annotated bass clips, got {len(samples)}")
    midis = [int(row.split("\t")[4]) for row in samples]
    if min(midis) > 28 or max(midis) < 67:
        raise AssertionError(f"unexpected bass MIDI coverage: {min(midis)}-{max(midis)}")
    metadata = (FIXTURE / "metadata.tsv").read_text(encoding="utf-8").splitlines()[1:]
    styles = Counter(row.split("\t")[5] for row in metadata)
    if len(styles) < 5:
        raise AssertionError(f"expected five plucking styles, got {sorted(styles)}")
    for row in samples:
        clip = FIXTURE / row.split("\t")[6]
        if not clip.is_file() or clip.stat().st_size == 0:
            raise AssertionError(f"missing or empty clip: {clip}")
    print(f"test_prepare_idmt_bass_single_track_fixture: ok ({len(samples)} clips, styles={dict(styles)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
