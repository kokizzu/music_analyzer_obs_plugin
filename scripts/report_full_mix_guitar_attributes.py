#!/usr/bin/env python3
"""Export and summarize per-fixture full-mix guitar routing attributes."""

import argparse
import csv
import os
import subprocess
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attack", action="store_true")
    attack = parser.parse_args().attack
    root = Path(__file__).resolve().parent.parent
    phase = "attack" if attack else "settled"
    output = root / "build" / (
        "full_mix_guitar_attack_attributes_shard_0.tsv" if attack else "full_mix_guitar_attributes_shard_0.tsv"
    )
    environment = os.environ.copy()
    environment.update(
        MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
        MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
        MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER="guitar",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="4",
        MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="0",
        MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
        MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(output),
    )
    if attack:
        environment["MUSIC_ANALYZER_REAL_NOTE_ATTACK_ATTRIBUTE_EXPORT"] = "1"
    subprocess.run([str(root / "build" / "analyzer_real_note_samples")], cwd=root, env=environment, check=True)

    fixtures: dict[str, dict[str, str]] = {}
    with output.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            fixtures.setdefault(row["sample_id"], row)
    raw = Counter(row["first_row"] for row in fixtures.values())
    visual = Counter(row["visual_first_row"] for row in fixtures.values())
    print(f"phase={phase} fixtures={len(fixtures)} raw=" +
          " ".join(f"{row}={count}" for row, count in raw.most_common()))
    print("visual=" + " ".join(f"{row}={count}" for row, count in visual.most_common()))
    guitar_to_piano = [
        row for row in fixtures.values()
        if row["first_row"] == "guitar" and row["visual_first_row"] == "piano"
    ]
    source_counts = Counter(row["source"] for row in guitar_to_piano)
    print(f"raw-guitar visual-piano={len(guitar_to_piano)} sources=" +
          " ".join(f"{source}={count}" for source, count in source_counts.most_common()))
    for row in guitar_to_piano[:12]:
        print(
            f"  {row['sample_id']} {row['expected_note']} "
            f"guitar={float(row['guitar_visual_level']):.3f} "
            f"piano={float(row['piano_visual_level']):.3f}"
        )


if __name__ == "__main__":
    main()
