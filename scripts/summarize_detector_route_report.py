#!/usr/bin/env python3
"""Summarize actionable detector route candidates from the full route report."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re


SECTION_RE = re.compile(
    r"^(?P<section>(?:ownership_miss|visual_row_confusion|row_confusion):\S+|route \S+)"
)
NOTE_CANDIDATE_RE = re.compile(
    r"^(?P<rule>.+?): pos=(?P<pos_samples>\d+)/(?:\d+) rows=(?P<pos_rows>\d+) "
    r"neg=(?P<neg_samples>\d+)/(?:\d+) rows=(?P<neg_rows>\d+)"
    r"(?: foreign_miss=(?P<foreign_samples>\d+)/(?:\d+) rows=(?P<foreign_rows>\d+))?"
)
DRUM_CANDIDATE_RE = re.compile(
    r"^\+(?P<pos_rows>\d+) rows=\d+ -(?P<neg_rows>\d+) rows=\d+ "
    r"foreign=(?P<foreign_samples>\d+) rows=(?P<foreign_rows>\d+) "
    r"new-active=(?P<new_active_samples>\d+) rows=(?P<new_active_rows>\d+) "
    r"primary-break=(?P<primary_break_samples>\d+) rows=(?P<primary_break_rows>\d+)"
    r"(?: side_rows=\d+ net_rows=-?\d+ gain_per_side=(?:inf|\d+(?:\.\d+)?))? :: "
    r"(?P<rule>.+)$"
)
SHADOW_THRESHOLD_RE = re.compile(
    r"^protected=(?P<protected_rows>\d+)/(?:\d+) extras=(?P<extra_rows>\d+)/(?:\d+) "
    r"(?P<rule>.+)$"
)
SHADOW_SIMULATION_RE = re.compile(
    r"^(?P<rule>[^: ]+):(?P<extra_rows>\d+)/(?P<protected_rows>\d+)$"
)


@dataclasses.dataclass(frozen=True)
class Candidate:
    kind: str
    section: str
    rule: str
    pos_rows: int
    neg_rows: int
    pos_samples: int = 0
    neg_samples: int = 0
    foreign_rows: int = 0
    new_active_rows: int = 0
    primary_break_rows: int = 0

    @property
    def side_effect_rows(self) -> int:
        return self.neg_rows + self.foreign_rows + self.new_active_rows + self.primary_break_rows

    @property
    def net_rows(self) -> int:
        return self.pos_rows - self.side_effect_rows

    @property
    def gain_per_side_effect_row(self) -> float:
        if self.side_effect_rows <= 0:
            return float("inf")
        return self.pos_rows / self.side_effect_rows


def parse_report(path: pathlib.Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[Candidate] = set()
    section = ""
    note_candidate_kind = ""

    def append_candidate(candidate: Candidate) -> None:
        if candidate in seen:
            return
        seen.add(candidate)
        candidates.append(candidate)

    def parse_shadow_candidate(stripped: str) -> Candidate | None:
        if "->same-pitch " not in stripped or " simulation=" not in stripped or " threshold=" not in stripped:
            return None

        route = stripped.split(" extras=", 1)[0]
        simulation = stripped.split(" simulation=", 1)[1].split(" threshold=", 1)[0]
        threshold = stripped.split(" threshold=", 1)[1].split(" simulation_net_hits=", 1)[0]

        if threshold != "none":
            match = SHADOW_THRESHOLD_RE.match(threshold)
            if not match:
                return None
            rule = re.sub(r" net_hits=.*$", "", match.group("rule"))
            if simulation != "none":
                rule = f"threshold {rule}; simulation={simulation}"
            else:
                rule = f"threshold {rule}"
            return Candidate(
                kind="shadow",
                section=route,
                rule=rule,
                pos_rows=int(match.group("extra_rows")),
                neg_rows=int(match.group("protected_rows")),
            )

        if simulation == "none":
            return None
        match = SHADOW_SIMULATION_RE.match(simulation)
        if not match:
            return None
        return Candidate(
            kind="shadow",
            section=route,
            rule=f"simulation {match.group('rule')}",
            pos_rows=int(match.group("extra_rows")),
            neg_rows=int(match.group("protected_rows")),
        )

    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.rstrip()
        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group("section")
            note_candidate_kind = ""

        stripped = line.strip()
        if stripped == "low-false candidate rules:":
            note_candidate_kind = "low-false"
            continue
        if stripped.startswith("nearest over-budget"):
            note_candidate_kind = "near-miss"
            continue
        if note_candidate_kind and (
            stripped.startswith("highest-coverage")
            or (line and not line.startswith(" "))
        ):
            note_candidate_kind = ""

        if note_candidate_kind and line.startswith("    ") and stripped and stripped != "--":
            match = NOTE_CANDIDATE_RE.match(stripped)
            if match:
                append_candidate(
                    Candidate(
                        kind=note_candidate_kind,
                        section=section,
                        rule=match.group("rule"),
                        pos_samples=int(match.group("pos_samples")),
                        pos_rows=int(match.group("pos_rows")),
                        neg_samples=int(match.group("neg_samples")),
                        neg_rows=int(match.group("neg_rows")),
                        foreign_rows=int(match.group("foreign_rows") or 0),
                    )
                )
            continue

        shadow_candidate = parse_shadow_candidate(stripped)
        if shadow_candidate:
            append_candidate(shadow_candidate)
            continue

        if section.startswith("route ") and line.startswith("  +"):
            match = DRUM_CANDIDATE_RE.match(stripped)
            if match:
                append_candidate(
                    Candidate(
                        kind="drum",
                        section=section,
                        rule=match.group("rule"),
                        pos_rows=int(match.group("pos_rows")),
                        neg_rows=int(match.group("neg_rows")),
                        foreign_rows=int(match.group("foreign_rows")),
                        new_active_rows=int(match.group("new_active_rows")),
                        primary_break_rows=int(match.group("primary_break_rows")),
                    )
                )

    return candidates


def candidate_sort_key(candidate: Candidate) -> tuple[int, float, int, int, int, str]:
    kind_priority = {"low-false": 0, "shadow": 1, "near-miss": 2, "drum": 3}.get(
        candidate.kind, 4
    )
    return (
        kind_priority,
        -candidate.gain_per_side_effect_row,
        -candidate.net_rows,
        candidate.side_effect_rows,
        -candidate.pos_rows,
        candidate.section,
    )


def format_gain_ratio(candidate: Candidate) -> str:
    ratio = candidate.gain_per_side_effect_row
    if ratio == float("inf"):
        return "inf"
    return f"{ratio:.2f}"


def format_candidate(candidate: Candidate) -> str:
    utility = (
        f"side_rows={candidate.side_effect_rows} "
        f"net_rows={candidate.net_rows} "
        f"gain_per_side={format_gain_ratio(candidate)}"
    )
    if candidate.kind == "drum":
        return (
            f"{candidate.kind} {candidate.section} "
            f"+rows={candidate.pos_rows} -rows={candidate.neg_rows} "
            f"foreign_rows={candidate.foreign_rows} new_active_rows={candidate.new_active_rows} "
            f"primary_break_rows={candidate.primary_break_rows} "
            f"{utility} :: {candidate.rule}"
        )
    if candidate.kind == "shadow":
        return (
            f"{candidate.kind} {candidate.section} "
            f"+rows={candidate.pos_rows} protected_rows={candidate.neg_rows} "
            f"{utility} :: {candidate.rule}"
        )
    return (
        f"{candidate.kind} {candidate.section} "
        f"+samples={candidate.pos_samples} +rows={candidate.pos_rows} "
        f"-samples={candidate.neg_samples} -rows={candidate.neg_rows} "
        f"foreign_rows={candidate.foreign_rows} {utility} :: {candidate.rule}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=pathlib.Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    candidates = sorted(parse_report(args.report), key=candidate_sort_key)
    low_false = [candidate for candidate in candidates if candidate.kind == "low-false"]
    shadow = [candidate for candidate in candidates if candidate.kind == "shadow"]
    near_miss = [candidate for candidate in candidates if candidate.kind == "near-miss"]
    drum = [candidate for candidate in candidates if candidate.kind == "drum"]
    positive_net = [candidate for candidate in candidates if candidate.net_rows > 0]
    gain_ge_1 = [candidate for candidate in candidates if candidate.gain_per_side_effect_row >= 1.0]

    print(
        "detector_route_summary: "
        f"candidates={len(candidates)} low_false={len(low_false)} "
        f"shadow={len(shadow)} near_miss={len(near_miss)} drum={len(drum)} "
        f"positive_net={len(positive_net)} gain_ge_1={len(gain_ge_1)}"
    )
    if not candidates:
        print("  --")
        return 0

    for candidate in candidates[: max(0, args.limit)]:
        print("  " + format_candidate(candidate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
