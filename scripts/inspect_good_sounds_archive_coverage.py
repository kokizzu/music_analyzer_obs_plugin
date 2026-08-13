#!/usr/bin/env python3
"""Summarize labelled Good Sounds samples available in a cached archive.

This reads only the embedded SQLite catalogue and ZIP name table.  It does
not extract audio, create fixtures, or validate the multi-gigabyte archive.
"""

from __future__ import annotations

import argparse
import collections
from pathlib import Path
import shutil
import sqlite3
import tempfile
import zipfile

import prepare_good_sounds_samples as prepared


def available_samples(archive_path: Path) -> tuple[list[dict[str, object]], int, int]:
    with zipfile.ZipFile(archive_path) as archive, tempfile.TemporaryDirectory() as temp_name:
        database_member = prepared.find_database_member(archive)
        database_path = Path(temp_name) / Path(database_member).name
        with archive.open(database_member) as source, database_path.open("wb") as target:
            shutil.copyfileobj(source, target)

        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        samples, skipped_rows = prepared.prepare_rows(connection)
        connection.close()
        exact, folded, by_basename = prepared.normalized_names(archive)

        available = []
        missing_audio = 0
        for sample in samples:
            member = prepared.find_audio_member(
                exact, folded, by_basename, sample["filename"], sample["pack"]
            )
            if member is None:
                missing_audio += 1
                continue
            available.append(sample)
    return available, skipped_rows, missing_audio


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--top", type=int, default=24)
    args = parser.parse_args()

    if not args.archive.is_file():
        raise SystemExit(f"missing archive: {args.archive}")
    samples, skipped_rows, missing_audio = available_samples(args.archive)
    selected_sources = set(args.source)
    if selected_sources:
        samples = [sample for sample in samples if sample["source"] in selected_sources]

    by_family_source: collections.Counter[tuple[str, str]] = collections.Counter()
    by_source_note: dict[str, set[str]] = collections.defaultdict(set)
    for sample in samples:
        family = str(sample["family"])
        source = str(sample["source"])
        by_family_source[(family, source)] += 1
        by_source_note[source].add(str(sample["note"]))

    print(
        "good_sounds_archive_coverage: "
        f"available={len(samples)} skipped_catalogue={skipped_rows} missing_audio={missing_audio}"
    )
    for (family, source), count in by_family_source.most_common(max(0, args.top)):
        print(
            f"  {family}/{source} samples={count} "
            f"distinct_notes={len(by_source_note[source])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
