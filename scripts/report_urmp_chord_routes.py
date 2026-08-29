#!/usr/bin/env python3
"""Summarize whether URMP chord misses have corroborating local row labels."""

import csv
from collections import Counter, defaultdict

from report_urmp_chord_cases import ATTRIBUTES, MANIFEST, chord_tokens, expected_chord


LOCAL_COLUMNS = ("guitar_chord", "keyboard_chord", "other_chord")


def main() -> int:
    pitches_by_path: dict[str, set[int]] = defaultdict(set)
    path_by_id: dict[str, str] = {}
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            pitches_by_path[row["path"]].add(int(row["midi"]) % 12)
            path_by_id[row["id"]] = row["path"]

    rows_by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    fields: list[str] = []
    with ATTRIBUTES.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = reader.fieldnames or []
        for row in reader:
            path = path_by_id.get(row["sample_id"])
            if path is not None:
                rows_by_path[path].append(row)

    totals: Counter[str] = Counter()
    global_hits: Counter[str] = Counter()
    local_hits: Counter[str] = Counter()
    recoverable: Counter[str] = Counter()
    examples: list[tuple[str, str, str, str]] = []
    for path, pitches in sorted(pitches_by_path.items()):
        expected = expected_chord(pitches)
        if expected is None:
            continue
        label, quality = expected
        rows = rows_by_path[path]
        global_labels = set().union(*(chord_tokens(row.get("global_chord", "")) for row in rows))
        local_labels = set().union(
            *(chord_tokens(row.get(column, "")) for row in rows for column in LOCAL_COLUMNS)
        )
        totals[quality] += 1
        if label in global_labels:
            global_hits[quality] += 1
        if label in local_labels:
            local_hits[quality] += 1
        if label not in global_labels and label in local_labels:
            recoverable[quality] += 1
            if len(examples) < 16:
                examples.append((label, " ".join(sorted(global_labels)) or "--",
                                 " ".join(sorted(local_labels)), path))

    total = sum(totals.values())
    print(f"urmp-exact-chords={total}")
    print("attribute-columns=" + " ".join(fields))
    print("quality global local recoverable")
    for quality in sorted(totals):
        print(f"{quality} {global_hits[quality]}/{totals[quality]} "
              f"{local_hits[quality]}/{totals[quality]} "
              f"{recoverable[quality]}/{totals[quality]}")
    print(f"global-missed-local-exact={sum(recoverable.values())}/{total}")
    print("examples=")
    for label, global_labels, local_labels, path in examples:
        print(f"{label}\tglobal={global_labels}\tlocal={local_labels}\t{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
