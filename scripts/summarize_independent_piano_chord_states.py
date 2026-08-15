#!/usr/bin/env python3
"""Compare runtime-visible chord states across labelled piano corpora.

This is evidence mining only: it reports states shared by every input corpus
and never promotes a state to a detector rule.  A state contains only fields
available to the chord selector (candidate pitch-class count and its debug
cluster/template/selection counters), while correctness remains annotation
derived.
"""

from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path
import re


DEBUG_RE = re.compile(
    r"clusters=(?P<clusters>\d+)\s+templates=(?P<templates>\d+)\s+conflicts=(?P<conflicts>\d+)\s+selected=(?P<selected>\d+)"
)


def labels(value: str) -> set[str]:
    return {item for item in value.replace("=", ",").split(",") if item and item != "--"}


def state(row: dict[str, str]) -> tuple[int, int, int, int, int]:
    match = DEBUG_RE.fullmatch(row.get("chord_debug", "").strip())
    if not match:
        raise ValueError(f"invalid chord_debug state: {row.get('chord_debug', '')!r}")
    return (
        len(labels(row.get("detected_chord_pcs", ""))),
        int(match["clusters"]),
        int(match["templates"]),
        int(match["conflicts"]),
        int(match["selected"]),
    )


def load(path: Path) -> dict[tuple[int, int, int, int, int], collections.Counter[str]]:
    required = {
        "expected_chords", "chord_hit", "keyboard_chord", "detected_chord_pcs", "chord_debug",
        "missing_pcs", "extra_pcs",
    }
    result: dict[tuple[int, int, int, int, int], collections.Counter[str]] = collections.defaultdict(collections.Counter)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = set(reader.fieldnames or ())
        missing = required - fields
        if missing:
            raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
        for row in reader:
            if not labels(row["expected_chords"]):
                continue
            counts = result[state(row)]
            counts["total"] += 1
            if row["chord_hit"] == "1":
                counts["hit"] += 1
            elif not labels(row["keyboard_chord"]):
                counts["no_label"] += 1
                if row["missing_pcs"] in {"", "--"} and row["extra_pcs"] in {"", "--"}:
                    counts["no_label_complete_pcs"] += 1
            else:
                counts["wrong_label"] += 1
    if not result:
        raise ValueError(f"{path}: no eligible chord rows")
    return result


def render(paths: list[Path], min_per_corpus: int, limit: int) -> list[str]:
    loaded = [(path, load(path)) for path in paths]
    shared = set.intersection(*(set(states) for _, states in loaded))
    candidates = [
        item for item in shared
        if all(states[item]["total"] >= min_per_corpus for _, states in loaded)
        and any(states[item]["no_label"] for _, states in loaded)
    ]
    candidates.sort(key=lambda item: sum(states[item]["no_label"] for _, states in loaded), reverse=True)
    complete_recovery = [
        item for item in candidates
        if all(
            states[item]["no_label"] > 0
            and states[item]["no_label_complete_pcs"] == states[item]["no_label"]
            for _, states in loaded
        )
    ]
    lines = [
        f"independent_piano_chord_states: corpora={len(loaded)} "
        f"shared_no_label_states={len(candidates)} complete_pcs_recovery_candidates={len(complete_recovery)}"
    ]
    for item in candidates[:limit]:
        pcs, clusters, templates, conflicts, selected = item
        pieces = [
            f"pcs={pcs} clusters={clusters} templates={templates} conflicts={conflicts} selected={selected}"
        ]
        for path, states in loaded:
            counts = states[item]
            pieces.append(
                f"{path.name}:hit/no_label/complete_pcs/wrong="
                f"{counts['hit']}/{counts['no_label']}/{counts['no_label_complete_pcs']}/{counts['wrong_label']}"
            )
        lines.append("  " + " ".join(pieces))
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--min-per-corpus", type=int, default=2)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)
    if len(args.inputs) < 2:
        parser.error("provide at least two independent corpus TSVs")
    try:
        print("\n".join(render(args.inputs, max(1, args.min_per_corpus), max(1, args.limit))))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
