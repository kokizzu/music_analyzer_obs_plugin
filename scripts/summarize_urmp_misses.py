#!/usr/bin/env python3
"""Summarize the reproducible URMP missed-isolated-note diagnostics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys


MISS = re.compile(
    r"^URMP track .* #\d+ (?P<instrument>[a-z]+) at .* expected "
    r"(?P<pitch>[A-G]#?\d+),"
)
TRAIT = re.compile(
    r"^URMP traits .* #\d+ (?P<instrument>[a-z]+) at .* expected "
    r"(?P<pitch>[A-G]#?\d+), (?:isolated grids (?P<isolated>.*?), )?candidates "
    r"(?P<candidates>.*), (?:full-mix )?grids "
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} MEASUREMENT_OUTPUT", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    if not source.is_file():
        print(f"missing URMP measurement output: {source}", file=sys.stderr)
        return 2

    misses: Counter[tuple[str, str]] = Counter()
    trait_total = 0
    trait_expected_candidate = 0
    trait_recoverable: Counter[tuple[str, str]] = Counter()
    trait_isolated_blank = 0
    trait_isolated_nonempty = 0
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        matched = MISS.match(line)
        if matched:
            misses[(matched["instrument"], matched["pitch"])] += 1
            continue
        trait = TRAIT.match(line)
        if trait:
            trait_total += 1
            isolated = trait["isolated"]
            if isolated:
                other = re.search(r"\bother\[(?P<pitches>[^]]*)\]", isolated)
                if other:
                    if other["pitches"] == "--":
                        trait_isolated_blank += 1
                    else:
                        trait_isolated_nonempty += 1
            if re.search(rf"(?:^|\s){re.escape(trait['pitch'])}/", trait["candidates"]):
                trait_expected_candidate += 1
                trait_recoverable[(trait["instrument"], trait["pitch"])] += 1

    print(f"URMP isolated-note misses: {sum(misses.values())}")
    print("count\tinstrument\tpitch")
    for (instrument, pitch), count in sorted(
        misses.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"{count}\t{instrument}\t{pitch}")
    if trait_total:
        percent = trait_expected_candidate * 100.0 / trait_total
        print(
            "URMP missed tracks whose full-mix candidate pass includes the expected exact pitch: "
            f"{trait_expected_candidate}/{trait_total} ({percent:.1f}%)"
        )
        if trait_isolated_blank or trait_isolated_nonempty:
            print(
                "URMP missed-track isolated other row: "
                f"empty {trait_isolated_blank}/{trait_total}, "
                f"nonempty {trait_isolated_nonempty}/{trait_total}"
            )
        print("recoverable_count\tinstrument\tpitch")
        for (instrument, pitch), count in sorted(
            trait_recoverable.items(), key=lambda item: (-item[1], item[0])
        )[:40]:
            print(f"{count}\t{instrument}\t{pitch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
