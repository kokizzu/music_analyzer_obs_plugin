#!/usr/bin/env python3
"""Create a label-only IRMAS routing manifest without copying source WAV files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import os
from pathlib import Path


LABELS = {
    "cel": ("other", "cello"), "cla": ("other", "clarinet"), "flu": ("other", "flute"),
    "gac": ("guitar", "acoustic-guitar"), "gel": ("guitar", "electric-guitar"),
    "org": ("piano", "organ"), "pia": ("piano", "piano"), "sax": ("other", "saxophone"),
    "tru": ("other", "trumpet"), "vio": ("other", "violin"), "voi": ("vocals", "voice"),
}


def labels_for(wav: Path, root: Path) -> list[str]:
    label_file = wav.with_suffix(".txt")
    if label_file.is_file():
        return [line.strip().lower() for line in label_file.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip().lower() in LABELS]
    relative_parts = wav.relative_to(root).parts
    return [part.lower() for part in relative_parts if part.lower() in LABELS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-per-label", type=int, default=48)
    parser.add_argument("--minimum-samples", type=int, default=1)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    limit = max(0, args.max_per_label)
    by_label: dict[str, list[Path]] = defaultdict(list)
    for wav in sorted(root.rglob("*.wav")):
        for label in labels_for(wav, root):
            by_label[label].append(wav)
    rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    for label in sorted(by_label):
        for wav in by_label[label][:limit or None]:
            family, source = LABELS[label]
            rows.append({
                "sample_id": f"irmas_{label}_{wav.stem}", "family": family,
                "nsynth_family": "irmas", "source": f"irmas/{source}",
                "midi": "60", "note": "label-only", "path": os.path.relpath(wav, output),
            })
            counts[label] += 1
    if len(rows) < max(0, args.minimum_samples):
        raise SystemExit(f"expected at least {args.minimum_samples} labelled IRMAS samples, got {len(rows)}")
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "manifest.tsv"
    with manifest.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=("sample_id", "family", "nsynth_family", "source", "midi", "note", "path"), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / ".irmas-manifest-counts").write_text(
        " ".join(f"{label}={counts[label]}" for label in sorted(counts)) + "\n", encoding="utf-8")
    print(f"prepare_irmas_manifest: samples={len(rows)} manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
