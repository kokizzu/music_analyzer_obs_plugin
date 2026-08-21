#!/usr/bin/env python3
"""Search a deliberately narrow causal Beat This! display gate.

Beat This! produces beat timestamps rather than a calibrated confidence.  The
number of usable beat intervals is a possible conservative proxy, but it may
only be considered when it suppresses every observed wrong output in both
real-tempo continuous replays and still leaves a meaningful number of outputs.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re


ROW_RE = re.compile(r"^Beat This rolling tempo diag\t(?P<fields>.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Row:
    intervals: int
    hit: bool


def rows(path: Path) -> list[Row]:
    result: list[Row] = []
    for match in ROW_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
        fields = dict(part.split("=", 1) for part in match["fields"].split("\t") if "=" in part)
        try:
            intervals = int(fields["intervals"])
            status = fields["status"]
        except (KeyError, ValueError) as error:
            raise ValueError(f"{path}: malformed Beat This continuous row") from error
        if intervals < 0 or status not in {"hit", "miss"}:
            raise ValueError(f"{path}: invalid Beat This continuous row")
        result.append(Row(intervals, status == "hit"))
    if not result:
        raise ValueError(f"{path}: no Beat This continuous rows")
    return result


def counts(rows_to_count: list[Row], minimum_intervals: int) -> tuple[int, int]:
    selected = [row for row in rows_to_count if row.intervals >= minimum_intervals]
    return sum(row.hit for row in selected), sum(not row.hit for row in selected)


def render(ballroom_path: Path, filobass_path: Path, minimum_per_corpus: int) -> list[str]:
    ballroom = rows(ballroom_path)
    filobass = rows(filobass_path)
    choices: list[tuple[int, int, int, int, int]] = []
    for threshold in range(max(row.intervals for row in ballroom + filobass) + 1):
        ballroom_hit, ballroom_wrong = counts(ballroom, threshold)
        filobass_hit, filobass_wrong = counts(filobass, threshold)
        if ballroom_wrong == 0 and filobass_wrong == 0 and ballroom_hit >= minimum_per_corpus and filobass_hit >= minimum_per_corpus:
            choices.append((ballroom_hit + filobass_hit, threshold, ballroom_hit, filobass_hit, 1))
    if choices:
        _, threshold, ballroom_hit, filobass_hit, eligible = max(choices)
    else:
        threshold = -1
        ballroom_hit = filobass_hit = eligible = 0
    baseline_ballroom_hit, baseline_ballroom_wrong = counts(ballroom, 0)
    baseline_filobass_hit, baseline_filobass_wrong = counts(filobass, 0)
    return [
        "beat_this_continuous_interval_gate: "
        f"baseline_ballroom_correct={baseline_ballroom_hit}/{len(ballroom)} baseline_ballroom_wrong={baseline_ballroom_wrong} "
        f"baseline_filobass_correct={baseline_filobass_hit}/{len(filobass)} baseline_filobass_wrong={baseline_filobass_wrong}",
        "beat_this_continuous_interval_gate: "
        f"minimum_intervals={threshold} ballroom_correct={ballroom_hit}/{ballroom_hit} ballroom_wrong=0 "
        f"filobass_correct={filobass_hit}/{filobass_hit} filobass_wrong=0 minimum_per_corpus={minimum_per_corpus} eligible={eligible}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ballroom", type=Path)
    parser.add_argument("filobass", type=Path)
    parser.add_argument("--minimum-per-corpus", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.minimum_per_corpus <= 0:
        parser.error("--minimum-per-corpus must be positive")
    try:
        rendered = "\n".join(render(args.ballroom, args.filobass, args.minimum_per_corpus)) + "\n"
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"beat_this_continuous_interval_gate: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
