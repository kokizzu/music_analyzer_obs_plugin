#!/usr/bin/env python3
"""Export and summarize per-fixture full-mix ownership attributes."""

import csv
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARD_COUNT = 4


def arguments() -> tuple[str, int, tuple[int, ...]]:
    family = "bass"
    all_shards = False
    shard_count = DEFAULT_SHARD_COUNT
    shard_index = 0
    for argument in sys.argv[1:]:
        if argument == "--all-shards":
            all_shards = True
        elif argument.startswith("--shard-count="):
            shard_count = int(argument.removeprefix("--shard-count="))
        elif argument.startswith("--shard-index="):
            shard_index = int(argument.removeprefix("--shard-index="))
        elif argument in {"bass", "guitar", "piano", "vocals", "other"}:
            family = argument
        else:
            raise ValueError(f"unknown argument: {argument}")
    if shard_count < 1 or shard_index < 0 or shard_index >= shard_count:
        raise ValueError("invalid shard count or index")
    return family, shard_count, tuple(range(shard_count)) if all_shards else (shard_index,)


def main() -> int:
    family, shard_count, shard_indexes = arguments()
    environment = os.environ.copy()
    fixtures: dict[str, dict[str, str]] = {}

    def run_shard(shard_index: int) -> Path:
        output = ROOT / "build" / f"full_mix_{family}_attributes_{shard_count}_{shard_index}.tsv"
        shard_environment = environment.copy()
        shard_environment.update(
            MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED="1",
            MUSIC_ANALYZER_REAL_NOTE_FULL_MIX="1",
            MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER=family,
            MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=str(shard_count),
            MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=str(shard_index),
            MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="999999",
            MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=str(output),
        )
        subprocess.run([str(ROOT / "build" / "analyzer_real_note_samples")], cwd=ROOT,
                       env=shard_environment, check=True)
        return output

    with ThreadPoolExecutor(max_workers=len(shard_indexes)) as executor:
        outputs = list(executor.map(run_shard, shard_indexes))
    for output in outputs:
        with output.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                fixtures.setdefault(row["sample_id"], row)
    raw = Counter(row["first_row"] for row in fixtures.values())
    visual = Counter(row["visual_first_row"] for row in fixtures.values())
    print("family=" + family + " fixtures=" + str(len(fixtures)) + " raw=" +
          " ".join(f"{name}={count}" for name, count in raw.most_common()))
    print("visual=" + " ".join(f"{name}={count}" for name, count in visual.most_common()))
    for row in fixtures.values():
        if row["visual_first_row"] == family:
            continue
        print(
            f"  {row['sample_id']} expected={row['expected_note']} "
            f"raw={row['first_row']} visual={row['visual_first_row']} "
            f"bass={float(row['bass_visual_level']):.3f} "
            f"piano={float(row['piano_visual_level']):.3f} "
            f"guitar={float(row['guitar_visual_level']):.3f} "
            f"owner={row['debug_owner']} conf={float(row['debug_conf'] or 0.0):.3f} "
            f"scores={float(row['bass_score'] or 0.0):.3f},{float(row['keyboard_score'] or 0.0):.3f},"
            f"{float(row['guitar_score'] or 0.0):.3f} "
            + " ".join(
                f"{key}={row[key]}"
                for key in sorted(row)
                if key.startswith("debug_") and row[key] not in {"", "0", "0.0", "0.000000"}
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
