#!/usr/bin/env python3
"""Export and summarize per-fixture full-mix bass routing attributes."""

import csv
import os
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "full_mix_bass_attributes_shard_0.tsv"


def main() -> int:
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER="bass",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="4",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="0",
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(OUTPUT),
    )
    subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                   env=environment, check=True)

    fixtures: dict[str, dict[str, str]] = {}
    with OUTPUT.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            fixtures.setdefault(row["sample_id"], row)
    raw = Counter(row["first_row"] for row in fixtures.values())
    visual = Counter(row["visual_first_row"] for row in fixtures.values())
    print("fixtures=" + str(len(fixtures)) + " raw=" +
          " ".join(f"{name}={count}" for name, count in raw.most_common()))
    print("visual=" + " ".join(f"{name}={count}" for name, count in visual.most_common()))
    for row in fixtures.values():
        if row["visual_first_row"] == "bass":
            continue
        print(
            f"  {row['sample_id']} expected={row['expected_note']} "
            f"raw={row['first_row']} visual={row['visual_first_row']} "
            f"bass={float(row['bass_visual_level']):.3f} "
            f"piano={float(row['piano_visual_level']):.3f} "
            f"guitar={float(row['guitar_visual_level']):.3f} "
            f"owner={row['debug_owner']} conf={float(row['debug_conf']):.3f} "
            f"scores={float(row['bass_score']):.3f},{float(row['keyboard_score']):.3f},"
            f"{float(row['guitar_score']):.3f} "
            + " ".join(
                f"{key}={row[key]}"
                for key in sorted(row)
                if key.startswith("bass_debug_") and row[key] not in {"0", "0.0", "0.000000"}
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
