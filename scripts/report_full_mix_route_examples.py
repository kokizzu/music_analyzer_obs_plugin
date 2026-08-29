#!/usr/bin/env python3
"""Show representative expected-family to displayed-row cases from shard output."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = sorted((ROOT / "build").glob("real_note_full_mix_shard_*.out"))
EXPECTED = re.compile(r"family=([a-z]+)", re.IGNORECASE)
DISPLAYED = re.compile(r"first-row=([a-z]+)", re.IGNORECASE)
SOURCE = re.compile(r"source=([^\s]+)", re.IGNORECASE)


def main() -> int:
    if not OUTPUTS:
        raise SystemExit("no real-note full-mix shard output found; run make test-real-note-samples-full-mix first")

    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for output in OUTPUTS:
        for line in output.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("route-example "):
                continue
            expected = EXPECTED.search(line)
            displayed = DISPLAYED.search(line)
            if not expected or not displayed:
                continue
            key = (expected.group(1).lower(), displayed.group(1).lower())
            if len(examples[key]) >= 3:
                continue
            source = SOURCE.search(line)
            source_text = source.group(1) if source else "unknown"
            examples[key].append(f"source={source_text} {line}")

    if not examples:
        needle = "for (std::size_t row_index = 0; row_index < rows.size(); ++row_index)"
        for source in (ROOT / "tests" / "analyzer_real_note_samples.cpp",):
            lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
            matches = [index for index, line in enumerate(lines) if needle in line]
            if not matches:
                continue
            print(f"harness={source.relative_to(ROOT)} matches={len(matches)}")
            index = matches[0]
            for context in range(index, min(len(lines), index + 200)):
                print(f"{source.relative_to(ROOT)}:{context + 1}: {lines[context]}")
            return 0
        print("no parseable per-row output or harness reporter found")
        return 0

    for (expected, displayed), rows in sorted(examples.items()):
        print(f"route={expected}->{displayed} examples={len(rows)}")
        for row in rows:
            print(f"  {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
