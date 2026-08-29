#!/usr/bin/env python3
"""Summarize completed full-mix fixture shard results for detector tuning."""

from collections import Counter
from pathlib import Path
import re


ROW = re.compile(r"(bass|guitar|piano|vocals|other)\[([^]]+)\]")
ROUTE = re.compile(r"([\w/-]+)->(\w+)=(\d+)")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    shards = sorted((root / "build").glob("real_note_full_mix_shard_*.out"))
    if not shards:
        raise SystemExit("no full-mix shard output; run make test-real-note-samples-full-mix first")

    rows = ("bass", "guitar", "piano", "vocals", "other")
    confusion: dict[str, Counter[str]] = {row: Counter() for row in rows}
    raw_confusion: dict[str, Counter[str]] = {row: Counter() for row in rows}
    routes: Counter[str] = Counter()
    for shard in shards:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if " row-confusion:" in line and "source-routes" not in line and "visual-" not in line:
                for expected, cells in ROW.findall(line):
                    for cell in cells.split(","):
                        observed, count = cell.split("=", maxsplit=1)
                        raw_confusion[expected][observed] += int(count)
            if "visual-row-confusion:" in line and "source-routes" not in line:
                for expected, cells in ROW.findall(line):
                    for cell in cells.split(","):
                        observed, count = cell.split("=", maxsplit=1)
                        confusion[expected][observed] += int(count)
            if "visual-row-confusion-source-routes:" in line:
                for source, observed, count in ROUTE.findall(line):
                    routes[f"{source}->{observed}"] += int(count)

    total = sum(sum(cells.values()) for cells in confusion.values())
    correct = sum(confusion[row][row] for row in confusion)
    print(f"visual-first-row={correct}/{total} ({correct * 100 // total}%)")
    for expected, cells in confusion.items():
        row_total = sum(cells.values())
        raw_correct = raw_confusion[expected][expected]
        print(f"{expected}: raw={raw_correct}/{row_total} ({raw_correct * 100 // row_total}%) "
              f"visual={cells[expected]}/{row_total} ({cells[expected] * 100 // row_total}%) "
              + " ".join(f"{observed}={count}" for observed, count in cells.most_common()))
    print("largest visual source routes:")
    for route, count in routes.most_common(20):
        print(f"{route}={count}")


if __name__ == "__main__":
    main()
