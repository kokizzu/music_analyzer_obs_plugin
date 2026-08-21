#!/usr/bin/env python3
"""Preflight FSD50K Rimshot labels without downloading its audio partitions."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import re
import zipfile


# FSD50K labels include upward-propagated AudioSet ancestors.  These are the
# only companions permitted for an otherwise isolated Rimshot clip.
RIMSHOT_ANCESTORS = {
    "Rimshot", "Snare drum", "Drum", "Drum kit", "Percussion", "Music",
    "Musical instrument",
}


def member(archive: zipfile.ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"{archive.filename}: expected one {suffix}, found {len(matches)}")
    return matches[0]


def csv_rows(archive: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    with archive.open(member(archive, suffix)) as source:
        return list(csv.DictReader(io.TextIOWrapper(source, encoding="utf-8")))


def clip_metadata(archive: zipfile.ZipFile, split: str) -> dict[str, dict[str, object]]:
    with archive.open(member(archive, f"{split}_clips_info_FSD50K.json")) as source:
        raw = json.load(io.TextIOWrapper(source, encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{archive.filename}: invalid {split} clip metadata")
    return {str(key): value for key, value in raw.items() if isinstance(value, dict)}


def is_permissive_cc(value: object) -> bool:
    text = str(value or "").casefold().replace(" ", "").replace("-", "")
    restricted = any(marker in text for marker in ("ccbync", "ccbynd", "noncommercial", "noderivatives"))
    return "cc0" in text or ("creativecommons" in text or "ccby" in text) and not restricted


def candidates(rows: list[dict[str, str]], metadata: dict[str, dict[str, object]]) -> list[tuple[str, bool, str]]:
    result = []
    for row in rows:
        labels = {label.strip() for label in row.get("labels", "").split(",") if label.strip()}
        if "Rimshot" not in labels or not labels <= RIMSHOT_ANCESTORS:
            continue
        filename = row.get("fname", "")
        info = metadata.get(filename, {})
        licence = str(info.get("license", info.get("licence", "unknown")))
        result.append((filename, is_permissive_cc(licence), licence))
    return sorted(result)


def rimshot_labelled_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if "rimshot" in row.get("labels", "").casefold().replace(" ", "")
    ]


def render(ground_truth: Path, metadata: Path) -> list[str]:
    with zipfile.ZipFile(ground_truth) as labels_archive, zipfile.ZipFile(metadata) as metadata_archive:
        rows = {split: csv_rows(labels_archive, f"{split}.csv") for split in ("dev", "eval")}
        vocabulary = csv_rows(labels_archive, "vocabulary.csv")
        info = {split: clip_metadata(metadata_archive, split) for split in ("dev", "eval")}
    selected = {split: candidates(rows[split], info[split]) for split in rows}
    labelled = {split: rimshot_labelled_rows(rows[split]) for split in rows}
    total = sum(len(items) for items in selected.values())
    permissive = sum(allowed for items in selected.values() for _, allowed, _ in items)
    labelled_total = sum(len(items) for items in labelled.values())
    lines = [
        "fsd50k_rim_metadata: "
        f"rimshot_labelled_rows={labelled_total} pure_rimshot_candidates={total} permissive_cc_candidates={permissive} "
        f"dev={len(selected['dev'])} eval={len(selected['eval'])}",
        "fsd50k_rim_metadata: "
        "audio_requirement=FSD50K.eval_audio (6.2 GB) for any selected eval candidates; "
        "dev audio is 24.7 GB",
    ]
    for row in vocabulary:
        rendered = " ".join(row.values())
        if re.search(r"\brimshot\b", rendered, flags=re.IGNORECASE):
            lines.append(f"  vocabulary_rim_entry={rendered}")
    for split in ("eval", "dev"):
        for row in labelled[split][:12]:
            lines.append(
                f"  labelled split={split} id={row.get('fname', '--')} labels={row.get('labels', '--')}"
            )
        for filename, allowed, licence in selected[split]:
            lines.append(
                f"  candidate split={split} id={filename} permissive_cc={int(allowed)} licence={licence or 'unknown'}"
            )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ground_truth", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        rendered = "\n".join(render(args.ground_truth, args.metadata)) + "\n"
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"fsd50k_rim_metadata: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
