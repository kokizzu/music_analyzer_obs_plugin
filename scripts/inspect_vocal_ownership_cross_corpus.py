#!/usr/bin/env python3
"""Compare exact-pitch vocal ownership outcomes across labelled corpora."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


OWNER_ALIASES = {"keys": "keyboard", "piano": "keyboard", "vocal": "vocal", "vocals": "vocal"}
OWNER_ORDER = ("keyboard", "other", "guitar", "amb", "vocal", "none")


def normalized_owner(value: str) -> str:
    return OWNER_ALIASES.get(value, value or "none")


def exact_candidate(row: dict[str, str]) -> bool:
    try:
        return int(row.get("debug_midi", "")) == int(row.get("expected_midi", ""))
    except ValueError:
        return False


def summarize(inputs: list[tuple[str, Path]]) -> list[tuple[str, str, int, int, int, int]]:
    counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for corpus, path in inputs:
        with path.open(encoding="utf-8", newline="") as source:
            rows = csv.DictReader(source, delimiter="\t")
            required = {"family", "status", "expected_midi", "debug_midi", "debug_owner"}
            missing = required - set(rows.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
            for row in rows:
                if row["family"] != "vocals":
                    continue
                owner = normalized_owner(row["debug_owner"]) if exact_candidate(row) else "none"
                counts[corpus, owner]["total"] += 1
                if row["status"] == "ownership_miss":
                    counts[corpus, owner]["ownership_miss"] += 1
                elif row["status"] == "hit":
                    counts[corpus, owner]["hit"] += 1
                else:
                    counts[corpus, owner]["other"] += 1
    result: list[tuple[str, str, int, int, int, int]] = []
    for (corpus, owner), counter in sorted(counts.items()):
        result.append((corpus, owner, counter["ownership_miss"], counter["hit"], counter["other"], counter["total"]))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, metavar="CORPUS=TSV")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    inputs: list[tuple[str, Path]] = []
    for value in args.input:
        try:
            corpus, text_path = value.split("=", 1)
        except ValueError:
            parser.error(f"invalid --input `{value}`; expected CORPUS=TSV")
        inputs.append((corpus, Path(text_path)))
    try:
        rows = summarize(inputs)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    target = args.output
    if target is None:
        writer = csv.writer(__import__("sys").stdout, delimiter="\t", lineterminator="\n")
        writer.writerow(("corpus", "owner", "ownership_misses", "protected_hits", "other", "exact_candidates"))
        writer.writerows(rows)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t")
            writer.writerow(("corpus", "owner", "ownership_misses", "protected_hits", "other", "exact_candidates"))
            writer.writerows(rows)
        print(f"inspect_vocal_ownership_cross_corpus: wrote {target} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
