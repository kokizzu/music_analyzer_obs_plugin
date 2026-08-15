#!/usr/bin/env python3
"""Validate the MAESTRO ZIP structure before preparing a measured subset.

The subset preparer opens every selected WAV/MIDI member through ``zipfile``;
that path verifies the member CRC as bytes are extracted.  Scanning every
member of the 101-GB archive here would duplicate that work and delay the
first labelled measurement for hours.  This preflight instead proves that the
ZIP central directory is readable and that enough paired source members exist
for the requested subset.
"""

import argparse
from pathlib import Path
import zipfile

from prepare_maps_piano_samples import collect_pairs, normalized_kind_set


def validate(archive: Path, kinds: str, min_pairs: int) -> int:
    if not archive.is_file():
        raise ValueError(f"missing archive: {archive}")
    try:
        with zipfile.ZipFile(archive) as zipped:
            infos = zipped.infolist()
            if not infos:
                raise ValueError("empty ZIP central directory")
            pairs = collect_pairs(archive, normalized_kind_set(kinds))
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError(f"invalid ZIP structure: {error}") from error
    if len(pairs) < min_pairs:
        raise ValueError(
            f"expected at least {min_pairs} paired WAV/MIDI members for {kinds}, got {len(pairs)}"
        )
    print(
        "validate_maestro_subset_archive: "
        f"members={len(infos)} pairs={len(pairs)} kinds={kinds} archive={archive}"
    )
    return len(pairs)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate MAESTRO subset ZIP structure and paired members.")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--kinds", default="OTHER")
    parser.add_argument("--min-pairs", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        validate(args.archive, args.kinds, max(1, args.min_pairs))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
