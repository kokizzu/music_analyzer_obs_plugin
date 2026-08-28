#!/usr/bin/env python3
"""Summarize the sharded AG-PT expected-note evaluation for the accuracy report."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUMMARY = re.compile(r"usable\s+(?P<usable>\d+).*?guitar\s+(?P<hits>\d+)/(?P<total>\d+)")


def parse_shard(path: Path) -> tuple[int, int, int]:
    match = SUMMARY.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError(f"missing real-note summary in {path}")
    return tuple(int(match.group(name)) for name in ("usable", "hits", "total"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-samples", required=True, type=int)
    parser.add_argument("shards", nargs="+", type=Path)
    args = parser.parse_args()

    usable = hits = total = 0
    for shard in args.shards:
        shard_usable, shard_hits, shard_total = parse_shard(shard)
        if shard_usable != shard_total:
            raise ValueError(f"inconsistent usable/total count in {shard}: {shard_usable}/{shard_total}")
        usable += shard_usable
        hits += shard_hits
        total += shard_total
    if usable < args.minimum_samples or total < args.minimum_samples:
        raise ValueError(f"only {usable} AG-PT samples; need {args.minimum_samples}")
    if hits > total:
        raise ValueError("AG-PT hits exceed total")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "corpus\tmetric\taccurate\ttotal\tremaining\n"
        f"AG-PT\texpected exact-MIDI guitar note\t{hits}\t{total}\t{total - hits}\n",
        encoding="utf-8",
    )
    print(f"summarize_agpt_guitar_evaluation: {hits}/{total} ({total - hits} remaining)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
