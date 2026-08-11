#!/usr/bin/env python3
"""Summarize the reproducible URMP missed-isolated-note diagnostics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys


MISS = re.compile(
    r"^URMP track (?P<recording>.+) #(?P<track>\d+) (?P<instrument>[a-z]+) "
    r"at (?P<time>[\d.]+)s: expected (?P<pitch>[A-G]#?\d+), detected "
    r"bass `[^`]*`, key `[^`]*`, guitar `[^`]*`, vocal `[^`]*`, "
    r"other `(?P<detected>[^`]*)`$"
)
TRAIT = re.compile(
    r"^URMP traits (?P<recording>.+) #(?P<track>\d+) (?P<instrument>[a-z]+) "
    r"at (?P<time>[\d.]+)s: expected (?P<pitch>[A-G]#?\d+), "
    r"(?:isolated grids (?P<isolated>.*?), )?candidates "
    r"(?P<candidates>.*), (?:full-mix )?grids "
)
CONFIRMED_TRAIT = re.compile(
    r"^URMP confirmed isolated .* #\d+ (?P<instrument>[a-z]+) at .* expected "
    r"(?P<pitch>[A-G]#?\d+), exact (?P<exact>[01]), grids "
)
NOTE = re.compile(r"^(?P<pitch_class>[A-G]#?)(?P<octave>\d+)$")
CANDIDATE = re.compile(
    r"^(?P<pitch>[A-G]#?\d+)/(?P<owner>[a-z]+):(?P<power>\d+)%@(?P<score>\d+)$"
)


def trait_key(match: re.Match[str]) -> tuple[str, str, str, str, str]:
    return (
        match["recording"],
        match["track"],
        match["instrument"],
        match["time"],
        match["pitch"],
    )


def first_note(label: str) -> str | None:
    for token in label.split():
        if NOTE.fullmatch(token):
            return token
    return None


def candidate_details(expected: str, candidates: str) -> tuple[int, int, int] | None:
    for index, token in enumerate(candidates.split(), start=1):
        match = CANDIDATE.fullmatch(token)
        if match is not None and match["pitch"] == expected:
            return index, int(match["power"]), int(match["score"])
    return None


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
    selected_by_trait: dict[tuple[str, str, str, str, str], str] = {}
    candidate_ranks: Counter[int] = Counter()
    candidate_present_details: list[tuple[int, int, int, str, str, str]] = []
    confirmed_trait_total = 0
    confirmed_trait_exact = 0
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        matched = MISS.match(line)
        if matched:
            misses[(matched["instrument"], matched["pitch"])] += 1
            selected_by_trait[trait_key(matched)] = matched["detected"]
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
            details = candidate_details(trait["pitch"], trait["candidates"])
            if details is not None:
                rank, power, score = details
                trait_expected_candidate += 1
                trait_recoverable[(trait["instrument"], trait["pitch"])] += 1
                candidate_ranks[rank] += 1
                selected = first_note(selected_by_trait.get(trait_key(trait), ""))
                candidate_present_details.append(
                    (rank, -score, -power, trait["instrument"], trait["pitch"], selected or "--")
                )
            continue
        confirmed = CONFIRMED_TRAIT.match(line)
        if confirmed:
            confirmed_trait_total += 1
            confirmed_trait_exact += int(confirmed["exact"])

    print(f"URMP isolated-note misses: {sum(misses.values())}")
    print("count\tinstrument\tpitch")
    for (instrument, pitch), count in sorted(
        misses.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"{count}\t{instrument}\t{pitch}")
    if trait_total:
        percent = trait_expected_candidate * 100.0 / trait_total
        print(
            "URMP missed tracks whose independent full-mix candidate pass includes the expected exact pitch: "
            f"{trait_expected_candidate}/{trait_total} ({percent:.1f}%)"
        )
        if trait_isolated_blank or trait_isolated_nonempty:
            print(
                "URMP missed-track isolated other row: "
                f"empty {trait_isolated_blank}/{trait_total}, "
                f"nonempty {trait_isolated_nonempty}/{trait_total}"
            )
        if candidate_ranks:
            top_one = candidate_ranks[1]
            top_three = sum(count for rank, count in candidate_ranks.items() if rank <= 3)
            print(
                "URMP independent full-mix expected candidate rank among sampled misses: "
                f"top-1 {top_one}/{trait_total}, top-3 {top_three}/{trait_total}, "
                f"any {trait_expected_candidate}/{trait_total}"
            )
            print("count\tcandidate_rank")
            for rank, count in sorted(candidate_ranks.items()):
                print(f"{count}\t{rank}")
            print(
                "rank\tfull_mix_expected_score\tfull_mix_expected_power\t"
                "instrument\texpected\tisolated_other"
            )
            for rank, negative_score, negative_power, instrument, pitch, selected in sorted(
                candidate_present_details
            ):
                print(
                    f"{rank}\t{-negative_score}\t{-negative_power}\t{instrument}\t{pitch}\t{selected}"
                )
    if confirmed_trait_total:
        percent = confirmed_trait_exact * 100.0 / confirmed_trait_total
        print(
            "URMP sampled first-frame misses recovered after three confirmation frames: "
            f"{confirmed_trait_exact}/{confirmed_trait_total} ({percent:.1f}%)"
        )
        print("recoverable_count\tinstrument\tpitch")
        for (instrument, pitch), count in sorted(
            trait_recoverable.items(), key=lambda item: (-item[1], item[0])
        )[:40]:
            print(f"{count}\t{instrument}\t{pitch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
