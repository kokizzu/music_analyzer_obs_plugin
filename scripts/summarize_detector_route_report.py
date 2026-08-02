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
    r"(?: side_rows=\d+ net_rows=-?\d+ gain_per_side=(?:inf|-?\d+(?:\.\d+)?))?"
    r"(?: neg_same_source_rows=(?P<neg_same_source_rows>\d+))?"
    r"(?: neg_cross_source_rows=(?P<neg_cross_source_rows>\d+))?"
    r"(?: foreign_cross_source_rows=(?P<foreign_cross_source_rows>\d+))?"
    r"(?: neg_sources=(?P<neg_sources>\S+))?"
    r"(?: foreign_sources=(?P<foreign_sources>\S+))?"
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
COMPACT_SHADOW_ROUTE_RE = re.compile(
    r"^(?P<route>\S+->same-pitch \S+) extras=(?P<extra_rows>\d+)/(?:\d+) "
    r"protected=(?P<protected_rows>\d+)/(?:\d+) simulation=(?P<simulation>\S+) "
    r"threshold=(?P<threshold>.+)$"
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
    neg_same_source_rows: int = 0
    neg_cross_source_rows: int = 0
    foreign_cross_source_rows: int = 0
    source_rows_reported: bool = False
    neg_sources: str = ""
    foreign_sources: str = ""
    examples: tuple[str, ...] = dataclasses.field(default_factory=tuple, compare=False)

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

    @property
    def source_conflict_rows(self) -> int:
        return self.neg_cross_source_rows + self.foreign_cross_source_rows

    @property
    def has_exact_source_rows(self) -> bool:
        return bool(
            self.neg_same_source_rows
            or self.neg_cross_source_rows
            or self.foreign_cross_source_rows
        )

    @property
    def source_safe(self) -> bool:
        if self.kind not in {"low-false", "near-miss"}:
            return True
        if self.side_effect_rows == 0:
            return True
        return self.source_rows_reported and self.source_conflict_rows == 0


def parse_report(path: pathlib.Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[Candidate] = set()
    indexes: dict[Candidate, int] = {}
    blocked_shadow_routes: set[str] = set()
    section = ""
    note_candidate_kind = ""
    last_candidate_index: int | None = None
    example_candidate_index: int | None = None

    def append_candidate(candidate: Candidate) -> int | None:
        nonlocal last_candidate_index
        if candidate in seen:
            last_candidate_index = indexes.get(candidate)
            return last_candidate_index
        seen.add(candidate)
        indexes[candidate] = len(candidates)
        candidates.append(candidate)
        last_candidate_index = len(candidates) - 1
        return last_candidate_index

    def append_example(index: int, example: str) -> None:
        candidate = candidates[index]
        if example in candidate.examples:
            return
        candidates[index] = dataclasses.replace(
            candidate, examples=candidate.examples + (example,)
        )

    def normalize_shadow_threshold(raw_threshold: str) -> str:
        return (
            raw_threshold.split(" simulation_net_hits=", 1)[0]
            .split(" guarded=", 1)[0]
            .strip()
        )

    def parse_shadow_candidate(stripped: str) -> Candidate | None:
        match = COMPACT_SHADOW_ROUTE_RE.match(stripped)
        if not match:
            return None

        route = match.group("route")
        simulation = match.group("simulation")
        threshold = normalize_shadow_threshold(match.group("threshold"))
        guarded = stripped.split(" guarded=", 1)[1].split()[0] if " guarded=" in stripped else ""

        if threshold != "none":
            match = SHADOW_THRESHOLD_RE.match(threshold)
            if not match:
                return None
            rule = re.sub(r" net_hits=.*$", "", match.group("rule"))
            if simulation != "none":
                rule = f"threshold {rule}; simulation={simulation}"
            else:
                rule = f"threshold {rule}"
            if guarded:
                rule = f"{rule}; guarded={guarded}"
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
        rule = f"simulation {match.group('rule')}"
        if guarded:
            rule = f"{rule}; guarded={guarded}"
        return Candidate(
            kind="shadow",
            section=route,
            rule=rule,
            pos_rows=int(match.group("extra_rows")),
            neg_rows=int(match.group("protected_rows")),
        )

    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if example_candidate_index is not None:
            if line.startswith("        ") and stripped:
                append_example(example_candidate_index, stripped)
                continue
            example_candidate_index = None

        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group("section")
            note_candidate_kind = ""

        if stripped == "low-false candidate rules:":
            note_candidate_kind = "low-false"
            last_candidate_index = None
            continue
        if stripped.startswith("nearest over-budget"):
            note_candidate_kind = "near-miss"
            last_candidate_index = None
            continue
        if stripped == "positive examples:" and last_candidate_index is not None:
            example_candidate_index = last_candidate_index
            continue
        if note_candidate_kind and (
            stripped.startswith("highest-coverage")
            or (line and not line.startswith(" "))
        ):
            note_candidate_kind = ""
            last_candidate_index = None

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
                        neg_same_source_rows=int(
                            match.group("neg_same_source_rows") or 0
                        ),
                        neg_cross_source_rows=int(
                            match.group("neg_cross_source_rows") or 0
                        ),
                        foreign_cross_source_rows=int(
                            match.group("foreign_cross_source_rows") or 0
                        ),
                        source_rows_reported=bool(
                            match.group("neg_same_source_rows") is not None
                            or match.group("neg_cross_source_rows") is not None
                            or match.group("foreign_cross_source_rows") is not None
                        ),
                        neg_sources=match.group("neg_sources") or "",
                        foreign_sources=match.group("foreign_sources") or "",
                    )
                )
            continue

        shadow_candidate = parse_shadow_candidate(stripped)
        if shadow_candidate:
            append_candidate(shadow_candidate)
            continue
        shadow_route_match = COMPACT_SHADOW_ROUTE_RE.match(stripped)
        if shadow_route_match:
            extra_rows = int(shadow_route_match.group("extra_rows"))
            protected_rows = int(shadow_route_match.group("protected_rows"))
            threshold = normalize_shadow_threshold(shadow_route_match.group("threshold"))
            simulation = shadow_route_match.group("simulation")
            if extra_rows > 0 and protected_rows > 0 and threshold == "none" and simulation == "none":
                blocked_shadow_routes.add(shadow_route_match.group("route"))
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

    return [
        candidate
        for candidate in candidates
        if not (candidate.kind == "shadow" and candidate.section in blocked_shadow_routes)
    ]


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


def actionable_sort_key(candidate: Candidate) -> tuple[int, int, float, int, int, str]:
    return (
        candidate.source_conflict_rows,
        -candidate.net_rows,
        -candidate.gain_per_side_effect_row,
        candidate.side_effect_rows,
        -candidate.pos_rows,
        candidate.section,
    )


def format_gain_ratio(candidate: Candidate) -> str:
    ratio = candidate.gain_per_side_effect_row
    if ratio == float("inf"):
        return "inf"
    return f"{ratio:.2f}"


def candidate_block_reasons(
    candidate: Candidate, min_actionable_samples: int
) -> list[str]:
    reasons: list[str] = []
    if candidate.net_rows <= 0:
        reasons.append("negative_net")
    if candidate.kind in {"low-false", "near-miss"}:
        if 0 < candidate.pos_samples < min_actionable_samples:
            reasons.append(f"low_samples<{min_actionable_samples}")
        if not candidate.source_safe:
            if candidate.source_rows_reported:
                reasons.append(f"cross_source_rows={candidate.source_conflict_rows}")
            else:
                reasons.append("unknown_source_side_effects")
    return reasons


def candidate_additional_samples_needed(
    candidate: Candidate, min_actionable_samples: int
) -> int:
    if candidate.kind not in {"low-false", "near-miss"}:
        return 0
    if candidate.pos_samples <= 0 or candidate.pos_samples >= min_actionable_samples:
        return 0
    return min_actionable_samples - candidate.pos_samples


def format_candidate(candidate: Candidate, min_actionable_samples: int) -> str:
    utility = (
        f"side_rows={candidate.side_effect_rows} "
        f"net_rows={candidate.net_rows} "
        f"gain_per_side={format_gain_ratio(candidate)}"
    )
    source_utility = ""
    if candidate.neg_sources:
        source_utility += f" neg_sources={candidate.neg_sources}"
    if candidate.foreign_sources:
        source_utility += f" foreign_sources={candidate.foreign_sources}"
    exact_source_utility = ""
    if candidate.has_exact_source_rows:
        exact_source_utility = (
            f" neg_same_source_rows={candidate.neg_same_source_rows}"
            f" neg_cross_source_rows={candidate.neg_cross_source_rows}"
            f" foreign_cross_source_rows={candidate.foreign_cross_source_rows}"
        )
    block_reasons = candidate_block_reasons(candidate, min_actionable_samples)
    block_utility = f" blocked_by={','.join(block_reasons)}" if block_reasons else ""
    if candidate.kind == "drum":
        return (
            f"{candidate.kind} {candidate.section} "
            f"+rows={candidate.pos_rows} -rows={candidate.neg_rows} "
            f"foreign_rows={candidate.foreign_rows} new_active_rows={candidate.new_active_rows} "
            f"primary_break_rows={candidate.primary_break_rows} "
            f"{utility}{block_utility} :: {candidate.rule}"
        )
    if candidate.kind == "shadow":
        return (
            f"{candidate.kind} {candidate.section} "
            f"+rows={candidate.pos_rows} protected_rows={candidate.neg_rows} "
            f"{utility}{block_utility} :: {candidate.rule}"
        )
    return (
        f"{candidate.kind} {candidate.section} "
        f"+samples={candidate.pos_samples} +rows={candidate.pos_rows} "
        f"-samples={candidate.neg_samples} -rows={candidate.neg_rows} "
        f"foreign_rows={candidate.foreign_rows} {utility}{exact_source_utility}"
        f"{source_utility}{block_utility} :: {candidate.rule}"
    )


def compact_example(example: str) -> str:
    tokens = example.split()
    if not tokens:
        return "--"
    useful_prefixes = (
        "expected=",
        "debug=",
        "owner=",
        "delta=",
        "reason=",
        "first_row=",
        "strongest=",
        "scores(",
        "spec=",
        "pitch=",
        "per=",
        "fit=",
        "cent=",
        "raw_best=",
        "raw_rank=",
    )
    kept = [tokens[0]]
    kept.extend(token for token in tokens[1:] if token.startswith(useful_prefixes))
    return " ".join(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=pathlib.Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--example-limit", type=int, default=2)
    parser.add_argument("--min-actionable-samples", type=int, default=5)
    args = parser.parse_args()

    candidates = sorted(parse_report(args.report), key=candidate_sort_key)
    low_false = [candidate for candidate in candidates if candidate.kind == "low-false"]
    shadow = [candidate for candidate in candidates if candidate.kind == "shadow"]
    near_miss = [candidate for candidate in candidates if candidate.kind == "near-miss"]
    drum = [candidate for candidate in candidates if candidate.kind == "drum"]
    positive_net = [candidate for candidate in candidates if candidate.net_rows > 0]
    gain_ge_1 = [candidate for candidate in candidates if candidate.gain_per_side_effect_row >= 1.0]
    source_safe_positive_net = [
        candidate
        for candidate in positive_net
        if candidate.source_safe
    ]
    actionable = [
        candidate
        for candidate in source_safe_positive_net
        if candidate.pos_samples == 0 or candidate.pos_samples >= args.min_actionable_samples
    ]
    coverage_blocked = [
        candidate
        for candidate in source_safe_positive_net
        if candidate_additional_samples_needed(candidate, args.min_actionable_samples) > 0
    ]

    print(
        "detector_route_summary: "
        f"candidates={len(candidates)} low_false={len(low_false)} "
        f"shadow={len(shadow)} near_miss={len(near_miss)} drum={len(drum)} "
        f"positive_net={len(positive_net)} gain_ge_1={len(gain_ge_1)} "
        f"source_safe_positive_net={len(source_safe_positive_net)} "
        f"actionable={len(actionable)} coverage_blocked={len(coverage_blocked)}"
    )
    if not candidates:
        print("  --")
        return 0
    if not actionable:
        print(
            "  no actionable candidates "
            f"(min_actionable_samples={args.min_actionable_samples}); showing diagnostics"
        )
    if coverage_blocked:
        print(
            "  coverage-blocked candidates need more positive samples before detector changes"
        )
        for candidate in sorted(coverage_blocked, key=actionable_sort_key)[
            : max(0, args.limit)
        ]:
            needed = candidate_additional_samples_needed(
                candidate, args.min_actionable_samples
            )
            print(
                "    "
                f"coverage_need {candidate.kind} {candidate.section} "
                f"observed_samples={candidate.pos_samples} need_samples={needed} "
                f"+rows={candidate.pos_rows} side_rows={candidate.side_effect_rows} "
                f"net_rows={candidate.net_rows} gain_per_side={format_gain_ratio(candidate)} "
                f":: {candidate.rule}"
            )
            for example in candidate.examples[: max(0, args.example_limit)]:
                print(f"      example {compact_example(example)}")

    actionable_set = set(actionable)
    ranked_candidates = (
        sorted(actionable, key=actionable_sort_key)
        + [
            candidate
            for candidate in sorted(positive_net, key=actionable_sort_key)
            if candidate not in actionable_set
        ]
        + [candidate for candidate in candidates if candidate.net_rows <= 0]
    )

    for candidate in ranked_candidates[: max(0, args.limit)]:
        print("  " + format_candidate(candidate, args.min_actionable_samples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
