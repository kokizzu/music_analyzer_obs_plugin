#!/usr/bin/env python3
"""Record the cross-corpus decision for a BabySlakh drum calibration pass."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUMMARY = re.compile(
    r"drum hits (?P<hits>\d+)/(?P<events>\d+), drum precision (?P<precision>[0-9.]+)%.*?"
    r"recall by category .*?crash:(?P<crash_hits>\d+)/(?P<crash_total>\d+)-\d+/"
    r"tom:(?P<tom_hits>\d+)/(?P<tom_total>\d+)-\d+/"
    r"ride:(?P<ride_hits>\d+)/(?P<ride_total>\d+)-\d+",
)


def summary(path: Path) -> dict[str, str]:
    match = SUMMARY.search(path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        raise ValueError(f"{path}: missing analyzer_egmd drum summary")
    return match.groupdict()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mdb", required=True, type=Path)
    parser.add_argument("--star", required=True, type=Path)
    parser.add_argument("--babyslakh", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    mdb, star, baby = (summary(path) for path in (args.mdb, args.star, args.babyslakh))

    # BabySlakh has no crash/ride recovery and near-zero Tom recovery, while
    # MDB's active defect is precision.  A global sensitivity increase lacks a
    # shared no-regression direction, so retain the detector pending a class-
    # specific candidate that is independently measured on all three corpora.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "babyslakh_drum_calibration_audit: decision=retain_current_detector "
        "candidate=none "
        f"mdb={mdb['hits']}/{mdb['events']} precision={mdb['precision']} "
        f"star={star['hits']}/{star['events']} precision={star['precision']} "
        f"babyslakh={baby['hits']}/{baby['events']} precision={baby['precision']} "
        f"crash={baby['crash_hits']}/{baby['crash_total']} "
        f"tom={baby['tom_hits']}/{baby['tom_total']} "
        f"ride={baby['ride_hits']}/{baby['ride_total']}\n",
        encoding="utf-8",
    )
    print(f"audit_babyslakh_drum_calibration: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
