#!/usr/bin/env python3
"""Compare MIR-1K expected-note vocal candidates against protected rows."""

from __future__ import annotations

import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path


MIR = Path("build/mir1k_vocal_full_mix_attributes.tsv")
PROTECTED = Path("build/real_note_full_mix_attributes.tsv")
NUMERIC = ("debug_conf", "vocal_score", "spectral_level", "pitch_confidence", "periodicity",
           "fit_error", "centroid", "slope", "noise", "partial2", "partial3", "partial4",
           "partial5")


def truth(row: dict[str, str], name: str) -> bool:
    return row.get(name, "") == "1"


def integer(row: dict[str, str], name: str) -> int | None:
    try:
        return int(row.get(name, ""))
    except ValueError:
        return None


def number(row: dict[str, str], name: str) -> float | None:
    try:
        return float(row.get(name, ""))
    except ValueError:
        return None


def expected_candidates(path: Path, protected: bool) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("mode") != "full_mix":
            continue
        if protected and row.get("family") == "vocals":
            continue
        if not protected and row.get("family") != "vocals":
            continue
        if integer(row, "debug_midi") != integer(row, "expected_midi"):
            continue
        selected.append(row)
    return selected


def report(label: str, rows: list[dict[str, str]]) -> None:
    print(f"{label}: expected-note candidates={len(rows)}")
    print("  owner=" + " ".join(f"{name}={count}" for name, count in
                                sorted(Counter(row.get("debug_owner", "") for row in rows).items())))
    print("  profile=" + " ".join(f"{name}={count}" for name, count in sorted(Counter(
        ("tone" if truth(row, "vocal_tone_profile") else "no-tone") +
        ("+poly-reject" if truth(row, "vocal_rejected_polyphony") else "")
        for row in rows).items())))
    for profile_name, filtered in (
        ("tone+poly-reject", [row for row in rows if truth(row, "vocal_tone_profile") and
                                truth(row, "vocal_rejected_polyphony")]),
        ("tone-accepted", [row for row in rows if truth(row, "vocal_tone_profile") and
                           not truth(row, "vocal_rejected_polyphony")]),
    ):
        print(f"  {profile_name}: rows={len(filtered)} samples={len({row['sample_id'] for row in filtered})}")
        if not filtered:
            continue
        values = []
        for key in NUMERIC:
            samples = [value for row in filtered if (value := number(row, key)) is not None]
            if samples:
                values.append(f"{key}={statistics.median(samples):.3f}")
        print("    medians " + " ".join(values))


def main() -> int:
    if not MIR.is_file() or not PROTECTED.is_file():
        raise SystemExit("missing attribute TSV; run make collect-mir1k-vocal-full-mix-attributes and make analyze-real-note-attributes")
    mir = expected_candidates(MIR, protected=False)
    protected = expected_candidates(PROTECTED, protected=True)
    report("MIR-1K vocals", mir)
    report("MIR-1K missed vocal candidates", [row for row in mir if not truth(row, "detected_expected_row")])
    report("protected non-vocals", protected)

    mir_rejected = {row["sample_id"] for row in mir if truth(row, "vocal_tone_profile") and
                    truth(row, "vocal_rejected_polyphony")}
    protected_rejected = [row for row in protected if truth(row, "vocal_tone_profile") and
                          truth(row, "vocal_rejected_polyphony")]
    print(f"candidate gate removal: MIR samples={len(mir_rejected)} protected rows={len(protected_rejected)}")
    print("protected-by-family=" + " ".join(
        f"{name}={count}" for name, count in sorted(Counter(row["family"] for row in protected_rejected).items())))

    print("vocal-score candidate sweep (MIR missed samples / protected rows)")
    for threshold in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        mir_samples = {
            row["sample_id"] for row in mir
            if not truth(row, "detected_expected_row") and (number(row, "vocal_score") or 0.0) >= threshold
        }
        protected_rows = [
            row for row in protected if (number(row, "vocal_score") or 0.0) >= threshold
        ]
        print(f"  >= {threshold:.2f}: mir={len(mir_samples)}/62 protected={len(protected_rows)}")

    mir_octave = [
        row for row in mir if not truth(row, "detected_expected_row") and
        integer(row, "debug_midi") == (integer(row, "expected_midi") or 0) + 12
    ]
    protected_octave = [
        row for row in protected if integer(row, "debug_midi") ==
        (integer(row, "expected_midi") or 0) + 12
    ]
    print(f"octave-up candidate rows: mir={len(mir_octave)} samples={len({row['sample_id'] for row in mir_octave})} "
          f"protected={len(protected_octave)}")
    for threshold in (0.15, 0.25, 0.35, 0.45, 0.55, 0.65):
        mir_samples = {
            row["sample_id"] for row in mir_octave
            if (number(row, "raw_expected_ratio") or 0.0) >= threshold
        }
        protected_rows = [
            row for row in protected_octave
            if (number(row, "raw_expected_ratio") or 0.0) >= threshold
        ]
        print(f"  fundamental >= {threshold:.2f}: mir={len(mir_samples)} protected={len(protected_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
