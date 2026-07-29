#!/usr/bin/env python3
"""Compare two drum gate matrix summaries or raw analyzer logs."""

from __future__ import annotations

import argparse
import pathlib
import re
from dataclasses import dataclass, field


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
MATRIX_RE = re.compile(r"^analyzer_drum_samples: (?P<kind>active|primary) matrix$")
RAW_ROW_RE = re.compile(r"^\s*expected\s+(?P<expected>\w+)\s+(?P<counts>.+)$")
SUMMARY_ROW_RE = re.compile(
    r"^(?P<kind>active|primary) expected (?P<expected>\w+): "
    r"hit=(?P<hit>\d+)/(?P<total>\d+).*? "
    r"off_target=(?P<off_target>\d+) "
    r"top_off_target=(?P<top>.+)$"
)
SAMPLE_RE = re.compile(
    r"^sample (?P<label>kick|snare|hihat|crash|tom|ride|rim): "
    r"recall=(?P<recall_hit>\d+)/(?P<recall_total>\d+) [0-9.]+% "
    r"primary=(?P<primary_hit>\d+)/(?P<primary_total>\d+) [0-9.]+% "
    r"precision=(?P<precision_hit>\d+)/(?P<precision_total>\d+) [0-9.]+% "
    r"false=(?P<false>\d+)$"
)


@dataclass
class ParsedSummary:
    samples: dict[str, dict[str, int]] = field(default_factory=dict)
    matrices: dict[str, dict[str, dict[str, int]]] = field(
        default_factory=lambda: {"active": {}, "primary": {}}
    )
    approximate_matrices: bool = False


def parse_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for token in text.split():
        if "=" not in token:
            continue
        label, value = token.split("=", 1)
        try:
            counts[label] = int(value)
        except ValueError:
            continue
    return counts


def parse_summary(path: pathlib.Path) -> ParsedSummary:
    parsed = ParsedSummary()
    current_kind: str | None = None
    for line in path.read_text(errors="replace").splitlines():
        sample_match = SAMPLE_RE.match(line)
        if sample_match:
            parsed.samples[sample_match.group("label")] = {
                field_name: int(sample_match.group(field_name))
                for field_name in (
                    "recall_hit",
                    "recall_total",
                    "primary_hit",
                    "primary_total",
                    "precision_hit",
                    "precision_total",
                    "false",
                )
            }
            continue

        matrix_match = MATRIX_RE.match(line)
        if matrix_match:
            current_kind = matrix_match.group("kind")
            continue
        raw_row_match = RAW_ROW_RE.match(line)
        if current_kind and raw_row_match:
            parsed.matrices[current_kind][raw_row_match.group("expected")] = parse_counts(
                raw_row_match.group("counts")
            )
            continue

        summary_row_match = SUMMARY_ROW_RE.match(line)
        if summary_row_match:
            parsed.approximate_matrices = True
            kind = summary_row_match.group("kind")
            expected = summary_row_match.group("expected")
            hit = int(summary_row_match.group("hit"))
            total = int(summary_row_match.group("total"))
            off_target = int(summary_row_match.group("off_target"))
            counts = {expected: hit}
            top_counts = parse_counts(summary_row_match.group("top"))
            counts.update(top_counts)
            residual = total - hit - sum(top_counts.values())
            if residual > 0:
                counts["other_off_target"] = residual
            elif off_target == 0:
                counts.setdefault(expected, hit)
            parsed.matrices[kind][expected] = counts
    return parsed


def delta_text(before: int, after: int) -> str:
    delta = after - before
    sign = "+" if delta > 0 else ""
    return f"{before}->{after} ({sign}{delta})"


def sample_lines(before: ParsedSummary, after: ParsedSummary) -> list[str]:
    lines: list[str] = []
    for category in CATEGORIES:
        base = before.samples.get(category)
        candidate = after.samples.get(category)
        if not base or not candidate:
            continue
        changed = any(
            base[field_name] != candidate[field_name]
            for field_name in ("recall_hit", "primary_hit", "precision_total", "false")
        )
        if not changed:
            continue
        lines.append(
            f"sample {category}: "
            f"recall {base['recall_hit']}/{base['recall_total']}->"
            f"{candidate['recall_hit']}/{candidate['recall_total']} "
            f"({candidate['recall_hit'] - base['recall_hit']:+d}) "
            f"primary {base['primary_hit']}/{base['primary_total']}->"
            f"{candidate['primary_hit']}/{candidate['primary_total']} "
            f"({candidate['primary_hit'] - base['primary_hit']:+d}) "
            f"false {delta_text(base['false'], candidate['false'])}"
        )
    return lines


def matrix_route_lines(before: ParsedSummary, after: ParsedSummary) -> list[str]:
    lines: list[str] = []
    for kind in ("active", "primary"):
        before_matrix = before.matrices[kind]
        after_matrix = after.matrices[kind]
        for expected in CATEGORIES:
            before_counts = before_matrix.get(expected, {})
            after_counts = after_matrix.get(expected, {})
            for detected in sorted(set(before_counts) | set(after_counts)):
                if detected == expected:
                    continue
                before_count = before_counts.get(detected, 0)
                after_count = after_counts.get(detected, 0)
                if before_count == after_count:
                    continue
                lines.append(
                    f"{kind} route {expected}->{detected}: "
                    f"{delta_text(before_count, after_count)}"
                )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=pathlib.Path)
    parser.add_argument("after", type=pathlib.Path)
    args = parser.parse_args()

    before = parse_summary(args.before)
    after = parse_summary(args.after)

    print(f"drum gate summary comparison: before={args.before} after={args.after}")
    if before.approximate_matrices or after.approximate_matrices:
        print("matrix route comparison uses summarized top-off-target rows where raw matrices are unavailable")

    lines = sample_lines(before, after) + matrix_route_lines(before, after)
    if not lines:
        print("no drum gate metric changes")
        return 0
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
