#!/usr/bin/env python3
"""Run real full-mix diagnostics and summarize first-row ownership misses."""

from collections import Counter
import csv
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "real_note_ownership.out"
ERROR = ROOT / "build" / "real_note_ownership.err"
ATTRIBUTES = ROOT / "build" / "real_note_ownership.tsv"
MISS_RE = re.compile(
    r"^(?P<id>\S+) (?P<family>[^/]+)/(?P<source>\S+) (?P<note>[^:]+): "
    r"expected-row ownership missing first-row=(?P<actual>\S+)"
)


def report_existing() -> int:
    if not ATTRIBUTES.is_file():
        print(f"missing attributes: {ATTRIBUTES}", file=sys.stderr)
        return 1
    with ATTRIBUTES.open(encoding="utf-8", newline="") as attributes_file:
        reader = csv.DictReader(attributes_file, delimiter="\t")
        rows = list(reader)
    print("attribute_columns=" + ",".join(reader.fieldnames or []))
    printed = set()
    for row in rows:
        family = row["family"]
        if row["first_row"] != family or family in printed:
            continue
        printed.add(family)
        print("primary " + family + " sample=" + row["sample_id"] +
              " source=" + row["source"] + " note=" + row["expected_note"] +
              " row=" + row["first_row"] + " label=" + row["row_label"])
    return 0


def report_shard_errors() -> int:
    lines = []
    for path in sorted((ROOT / "build").glob("detector_real_note_full_mix_shard_*.err")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "expected" in line or "ownership" in line:
                lines.append(line)
    print(f"shard_diagnostic_lines={len(lines)}")
    for line in lines[:80]:
        print(line)
    return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--report":
        return report_existing()
    if len(sys.argv) == 2 and sys.argv[1] == "--shard-errors":
        return report_shard_errors()
    if len(sys.argv) != 1:
        print("usage: analyze_real_note_ownership.py [--report|--shard-errors]", file=sys.stderr)
        return 2
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX": "1",
        "MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES": "1",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES": "999999",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT": "0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT": "100",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV": str(ATTRIBUTES),
    })
    completed = subprocess.run(
        [str(ROOT / "build" / "analyzer_real_note_samples")],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    OUTPUT.write_text(completed.stdout, encoding="utf-8")
    ERROR.write_text(completed.stderr, encoding="utf-8")

    routes: Counter[str] = Counter()
    visual_routes: Counter[str] = Counter()
    examples: dict[str, str] = {}
    seen_samples: set[str] = set()
    with ATTRIBUTES.open(encoding="utf-8", newline="") as attributes_file:
        for row in csv.DictReader(attributes_file, delimiter="\t"):
            sample_id = row["sample_id"]
            if sample_id in seen_samples:
                continue
            seen_samples.add(sample_id)
            expected = row["family"]
            source = row["source"]
            actual = row["first_row"]
            visual_actual = row["visual_first_row"]
            key = f"{expected}/{source}->{actual}"
            visual_key = f"{expected}/{source}->{visual_actual}"
            if actual != expected:
                routes[key] += 1
                examples.setdefault(key, sample_id)
            if visual_actual != expected:
                visual_routes[visual_key] += 1

    print(f"real_note_ownership: exit={completed.returncode} diagnostics={ERROR}")
    print(f"first_row_misses={sum(routes.values())} routes={len(routes)}")
    for route, count in routes.most_common(20):
        print(f"{count:4d} {route}")
        print(f"     sample={examples[route]}")
    print(f"visual_first_row_misses={sum(visual_routes.values())} routes={len(visual_routes)}")
    for route, count in visual_routes.most_common(20):
        print(f"{count:4d} {route}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
