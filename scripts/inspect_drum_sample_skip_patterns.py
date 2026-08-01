#!/usr/bin/env python3
"""Inspect skipped drum sample names by rejection reason."""

from __future__ import annotations

import argparse
import collections
import re
import shutil
import sys
from pathlib import Path

import prepare_drum_samples


TOKEN_RE = re.compile(r"[a-z][a-z0-9]{1,}", re.I)


class CollectingSkipAudit:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def record(self, kind: str, reason: str, label: str) -> None:
        self.rows.append((kind, reason, label))


def compact_label(label: str, max_parts: int = 5) -> str:
    archive, separator, member = label.partition("!")
    if separator:
        return f"{compact_label(archive, max_parts)}!{compact_label(member, max_parts)}"
    parts = Path(label).parts
    if len(parts) <= max_parts:
        return label
    return "/".join(parts[-max_parts:])


def label_stem(label: str) -> str:
    return Path(label.split("!")[-1]).stem.lower()


def token_counts(rows: list[tuple[str, str, str]]) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for _kind, _reason, label in rows:
        for token in TOKEN_RE.findall(label_stem(label)):
            counts[token.lower()] += 1
    return counts


def stem_counts(rows: list[tuple[str, str, str]]) -> collections.Counter[str]:
    return collections.Counter(label_stem(label) for _kind, _reason, label in rows)


def print_counter(title: str, counts: collections.Counter[str], top: int) -> None:
    values = counts.most_common(max(0, top))
    if not values:
        print(f"{title} --")
        return
    print(f"{title} " + " ".join(f"{key}={value}" for key, value in values))


def print_examples(title: str, rows: list[tuple[str, str, str]], top: int) -> None:
    examples = [compact_label(label) for _kind, _reason, label in rows[: max(0, top)]]
    print(f"{title} " + (" | ".join(examples) if examples else "--"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="/media/kyz/sshflashtor/DrumSamples")
    parser.add_argument("--unrar", default="unrar")
    parser.add_argument("--source-filter", default="")
    parser.add_argument("--skip-label-filter", default="",
                        help="only report skipped rows whose archive/member label matches this regex")
    parser.add_argument("--skip-reason", action="append", default=[],
                        help="only report this skipped reason; may be passed multiple times")
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--no-archives", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_dir():
        print(f"inspect_drum_sample_skip_patterns: skipped; missing {source}")
        return 0

    try:
        source_filter = re.compile(args.source_filter, re.I) if args.source_filter else None
        skip_label_filter = re.compile(args.skip_label_filter, re.I) if args.skip_label_filter else None
    except re.error as exc:
        raise SystemExit(f"inspect_drum_sample_skip_patterns: invalid regex: {exc}") from exc
    unrar = shutil.which(args.unrar) if args.unrar else None
    audit = CollectingSkipAudit()
    candidates = prepare_drum_samples.all_candidates(
        source,
        unrar=unrar,
        include_archives=not args.no_archives,
        source_filter=source_filter,
        audit=audit,
    )
    _ = candidates

    skip_reasons = set(args.skip_reason)
    if skip_label_filter or skip_reasons:
        audit.rows = [
            row for row in audit.rows
            if (not skip_label_filter or skip_label_filter.search(row[2]))
            and (not skip_reasons or row[1] in skip_reasons)
        ]

    by_reason: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    by_kind: collections.Counter[str] = collections.Counter()
    for row in audit.rows:
        kind, reason, _label = row
        by_reason[reason].append(row)
        by_kind[kind] += 1

    reason_counts = collections.Counter({reason: len(rows) for reason, rows in by_reason.items()})
    print(
        "inspect_drum_sample_skip_patterns: "
        f"skipped={len(audit.rows)} plain={by_kind['plain']} zip={by_kind['zip']} "
        f"rar={by_kind['rar']} source={source}"
    )
    print_counter("skip reasons", reason_counts, len(prepare_drum_samples.SKIP_REASONS))
    for reason in prepare_drum_samples.SKIP_REASONS:
        rows = by_reason.get(reason, [])
        print(f"reason {reason} rows={len(rows)}")
        print_counter(f"  tokens", token_counts(rows), args.top)
        print_counter(f"  stems", stem_counts(rows), args.top)
        print_examples(f"  examples", rows, min(args.top, 6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
