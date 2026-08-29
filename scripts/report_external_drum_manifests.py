#!/usr/bin/env python3
"""List reusable external drum manifests without placing media in the repository."""

from collections import Counter
from pathlib import Path


ROOT = Path("/media/kyz/sshflashtor/InstrumentSamples")


def manifest_counts(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    try:
        rows = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return counts
    if not rows:
        return counts
    columns = rows[0].split("\t")
    try:
        category_index = columns.index("category")
    except ValueError:
        return counts
    for row in rows[1:]:
        fields = row.split("\t")
        if len(fields) == len(columns):
            counts[fields[category_index]] += 1
    return counts


def main() -> int:
    print(f"root={ROOT}")
    if not ROOT.is_dir():
        print("status=missing")
        return 1
    manifests = sorted(ROOT.glob("*/manifest.tsv"))
    print(f"manifests={len(manifests)}")
    for manifest in manifests:
        counts = manifest_counts(manifest)
        if not counts:
            continue
        drum_count = sum(counts[category] for category in ("kick", "snare", "hihat", "tom", "crash", "ride", "rim"))
        if drum_count:
            formatted = " ".join(f"{category}={counts[category]}" for category in sorted(counts) if counts[category])
            print(f"{manifest.parent.relative_to(ROOT)} rows={sum(counts.values())} drum={drum_count} {formatted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
