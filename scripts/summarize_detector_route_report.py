#!/usr/bin/env python3
"""Summarize actionable detector route candidates from the full route report."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re


SECTION_RE = re.compile(
    r"^(?P<section>(?:ownership_miss|visual_row_confusion|row_confusion):\S+|route \S+|bucket \S+)"
)
NOTE_CANDIDATE_RE = re.compile(
    r"^(?P<rule>.+?): pos=(?P<pos_samples>\d+)/(?:\d+) rows=(?P<pos_rows>\d+) "
    r"neg=(?P<neg_samples>\d+)/(?:\d+) rows=(?P<neg_rows>\d+)"
    r"(?: foreign_miss=(?P<foreign_samples>\d+)/(?:\d+) rows=(?P<foreign_rows>\d+))?"
    r"(?: side_rows=\d+ net_rows=-?\d+ gain_per_side=(?:inf|-?\d+(?:\.\d+)?))?"
    r"(?: pos_groups=(?P<pos_groups>\S+))?"
    r"(?: pos_sources=(?P<pos_sources>\S+))?"
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
GUITAR_CANDIDATE_RE = re.compile(
    r"^\+(?P<pos_samples>\d+) rows=(?P<pos_rows>\d+) "
    r"-(?P<neg_samples>\d+) rows=(?P<neg_rows>\d+) :: (?P<rule>.+)$"
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
POSITIVE_SAMPLE_PROFILE_RE = re.compile(
    r"^positive sample profile: groups=(?P<groups>\S+) sources=(?P<sources>\S+)"
)
SAMPLE_SENSITIVE_KINDS = {"low-false", "near-miss", "guitar"}
GUITAR_CHORD_MISS_RE = re.compile(r"^bucket chord_miss:(?P<quality>[^:]+):")
RAW_ROOT_THIRD_FIFTH_RE = re.compile(
    r"raw\(root/third/fifth\)=(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)"
)
GUITAR_NO_QUALITY_THIRD_NAMES = {"pow", "sus2", "sus4"}
GUITAR_MISSING_NOTE_EVIDENCE_SUPPORTS = (
    "visible0_analysis0_smooth0_rootvis0",
)
GUITAR_MISSING_NOTE_EVIDENCE_RULE_MARKERS = (
    "analysis_pc_count<=0",
    "analysis_tones<=0",
    "smooth_pc_count<=0",
    "smooth_tones<=0",
)
GUITAR_MISSING_QUALITY_TONE_RULE_MARKERS = (
    "analysis_third<=",
    "display_primary_analysis_third<=",
    "melodic_probe_third<=",
    "display_primary_melodic_probe_third<=",
    "evidence_class=power_only_ambiguous",
    "evidence_class=third_missing",
    "analysis_missing_tones=fifth,third",
    "analysis_missing_tones=third",
    "smooth_missing_tones=fifth,third",
    "smooth_missing_tones=third",
)
GUITAR_WEAK_QUALITY_TONE_RULE_MARKERS = (
    "probe_third<=",
    "display_primary_probe_third<=",
)
GUITAR_EXAMPLE_THIRD_EVIDENCE_FLOOR = 0.06


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
    rule_groups: str = dataclasses.field(default="", compare=False)
    rule_sources: str = dataclasses.field(default="", compare=False)
    profile_groups: str = dataclasses.field(default="", compare=False)
    profile_sources: str = dataclasses.field(default="", compare=False)
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
    section_profile_groups = ""
    section_profile_sources = ""
    note_candidate_kind = ""
    last_candidate_index: int | None = None
    example_candidate_index: int | None = None
    example_indent = "        "

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
            if line.startswith(example_indent) and stripped:
                append_example(example_candidate_index, stripped)
                continue
            example_candidate_index = None
            example_indent = "        "

        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group("section")
            section_profile_groups = ""
            section_profile_sources = ""
            note_candidate_kind = ""

        profile_match = POSITIVE_SAMPLE_PROFILE_RE.match(stripped)
        if profile_match:
            section_profile_groups = profile_match.group("groups")
            section_profile_sources = profile_match.group("sources")
            continue

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
            example_indent = "        "
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
                        rule_groups=match.group("pos_groups") or "",
                        rule_sources=match.group("pos_sources") or "",
                        profile_groups=section_profile_groups,
                        profile_sources=section_profile_sources,
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
            continue

        if section.startswith("bucket ") and line.startswith("  +"):
            match = GUITAR_CANDIDATE_RE.match(stripped)
            if match:
                index = append_candidate(
                    Candidate(
                        kind="guitar",
                        section=section,
                        rule=match.group("rule"),
                        pos_samples=int(match.group("pos_samples")),
                        pos_rows=int(match.group("pos_rows")),
                        neg_samples=int(match.group("neg_samples")),
                        neg_rows=int(match.group("neg_rows")),
                    )
                )
                example_candidate_index = index
                example_indent = "    "
            continue

    return [
        candidate
        for candidate in candidates
        if not (candidate.kind == "shadow" and candidate.section in blocked_shadow_routes)
    ]


def candidate_sort_key(candidate: Candidate) -> tuple[int, float, int, int, int, str]:
    kind_priority = {"low-false": 0, "shadow": 1, "near-miss": 2, "guitar": 3, "drum": 4}.get(
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
    if guitar_missing_note_evidence(candidate):
        reasons.append("missing_note_evidence")
    elif guitar_quality_tone_missing(candidate):
        reasons.append("missing_quality_tone")
    if candidate.kind in SAMPLE_SENSITIVE_KINDS:
        if 0 < candidate.pos_samples < min_actionable_samples:
            reasons.append(f"low_samples<{min_actionable_samples}")
    if candidate.kind in {"low-false", "near-miss"}:
        if not candidate.source_safe:
            if candidate.source_rows_reported:
                reasons.append(f"cross_source_rows={candidate.source_conflict_rows}")
            else:
                reasons.append("unknown_source_side_effects")
    return reasons


def guitar_chord_miss_quality(candidate: Candidate) -> str:
    if candidate.kind != "guitar":
        return ""
    match = GUITAR_CHORD_MISS_RE.match(candidate.section)
    if not match:
        return ""
    return match.group("quality")


def guitar_quality_requires_third(quality: str) -> bool:
    if not quality:
        return False
    quality_names = {name for name in quality.split("/") if name}
    if not quality_names:
        return False
    return any(name not in GUITAR_NO_QUALITY_THIRD_NAMES for name in quality_names)


def guitar_examples_have_no_visible_analysis(candidate: Candidate) -> bool:
    if not candidate.examples:
        return False
    for example in candidate.examples:
        if "analysis=--" not in example or "visible=--" not in example:
            return False
    return True


def guitar_missing_note_evidence(candidate: Candidate) -> bool:
    if not guitar_chord_miss_quality(candidate):
        return False

    if any(marker in candidate.section for marker in GUITAR_MISSING_NOTE_EVIDENCE_SUPPORTS):
        return True

    compact_rule = candidate.rule.replace(" ", "")
    if any(
        marker.replace(" ", "") in compact_rule
        for marker in GUITAR_MISSING_NOTE_EVIDENCE_RULE_MARKERS
    ):
        return True
    return guitar_examples_have_no_visible_analysis(candidate)


def guitar_example_third_levels(candidate: Candidate) -> list[float]:
    third_levels: list[float] = []
    for example in candidate.examples:
        match = RAW_ROOT_THIRD_FIFTH_RE.search(example)
        if match:
            third_levels.append(float(match.group(2)))
    return third_levels


def guitar_examples_have_weak_third(candidate: Candidate) -> bool:
    third_levels = guitar_example_third_levels(candidate)
    return bool(third_levels) and max(third_levels) < GUITAR_EXAMPLE_THIRD_EVIDENCE_FLOOR


def guitar_quality_tone_missing(candidate: Candidate) -> bool:
    quality = guitar_chord_miss_quality(candidate)
    if not guitar_quality_requires_third(quality):
        return False

    compact_rule = candidate.rule.replace(" ", "")
    if any(
        marker.replace(" ", "") in compact_rule
        for marker in GUITAR_MISSING_QUALITY_TONE_RULE_MARKERS
    ):
        return True
    if any(
        marker.replace(" ", "") in compact_rule
        for marker in GUITAR_WEAK_QUALITY_TONE_RULE_MARKERS
    ):
        return guitar_examples_have_weak_third(candidate)

    return guitar_examples_have_weak_third(candidate)


def candidate_additional_samples_needed(
    candidate: Candidate, min_actionable_samples: int
) -> int:
    if candidate.kind not in SAMPLE_SENSITIVE_KINDS:
        return 0
    if candidate.pos_samples <= 0 or candidate.pos_samples >= min_actionable_samples:
        return 0
    return min_actionable_samples - candidate.pos_samples


def block_reason_summary(
    candidates: list[Candidate], min_actionable_samples: int
) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        for reason in candidate_block_reasons(candidate, min_actionable_samples):
            if reason.startswith("cross_source_rows="):
                reason = "cross_source_rows"
            counts[reason] = counts.get(reason, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def format_candidate(candidate: Candidate, min_actionable_samples: int) -> str:
    utility = (
        f"side_rows={candidate.side_effect_rows} "
        f"net_rows={candidate.net_rows} "
        f"gain_per_side={format_gain_ratio(candidate)}"
    )
    source_utility = ""
    positive_utility = ""
    if candidate.rule_groups:
        positive_utility += f" pos_groups={candidate.rule_groups}"
    if candidate.rule_sources:
        positive_utility += f" pos_sources={candidate.rule_sources}"
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
    if candidate.kind == "guitar":
        return (
            f"{candidate.kind} {candidate.section} "
            f"+recordings={candidate.pos_samples} +rows={candidate.pos_rows} "
            f"-recordings={candidate.neg_samples} -rows={candidate.neg_rows} "
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
        f"{positive_utility}{source_utility}{block_utility} :: {candidate.rule}"
    )


def compact_example(example: str) -> str:
    tokens = example.split()
    if not tokens:
        return "--"
    useful_prefixes = (
        "expected=",
        "guitar=",
        "support=",
        "raw(root/third/fifth)=",
        "analysis=",
        "visible=",
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


def example_sample_id(example: str) -> str:
    tokens = example.split()
    return tokens[0] if tokens else ""


SAMPLE_GROUP_RE = re.compile(r"^(?P<group>.+?)_\d{3}(?:[-_].*)?$")


def sample_group(sample_id: str) -> str:
    pathless = sample_id.rsplit("/", 1)[-1]
    stem = pathless.rsplit(".", 1)[0]
    match = SAMPLE_GROUP_RE.match(stem)
    if match:
        return match.group("group")
    return stem or "--"


@dataclasses.dataclass
class CoverageRouteCluster:
    section: str
    candidates: int = 0
    best_observed_samples: int = 0
    min_needed_samples: int = 0
    total_net_rows: int = 0
    sample_ids: list[str] = dataclasses.field(default_factory=list)
    sample_groups: dict[str, int] = dataclasses.field(default_factory=dict)
    rule_groups: str = ""
    rule_sources: str = ""
    profile_groups: str = ""
    profile_sources: str = ""


def coverage_route_clusters(
    candidates: list[Candidate], min_actionable_samples: int
) -> list[CoverageRouteCluster]:
    clusters: dict[str, CoverageRouteCluster] = {}
    seen_samples: dict[str, set[str]] = {}
    for candidate in candidates:
        needed = candidate_additional_samples_needed(candidate, min_actionable_samples)
        if needed <= 0:
            continue
        cluster = clusters.setdefault(
            candidate.section,
            CoverageRouteCluster(section=candidate.section, min_needed_samples=needed),
        )
        cluster.candidates += 1
        cluster.best_observed_samples = max(
            cluster.best_observed_samples, candidate.pos_samples
        )
        cluster.min_needed_samples = min(cluster.min_needed_samples, needed)
        cluster.total_net_rows += candidate.net_rows
        if candidate.rule_groups and candidate.rule_groups != "--" and not cluster.rule_groups:
            cluster.rule_groups = candidate.rule_groups
        if candidate.rule_sources and candidate.rule_sources != "--" and not cluster.rule_sources:
            cluster.rule_sources = candidate.rule_sources
        if candidate.profile_groups and not cluster.profile_groups:
            cluster.profile_groups = candidate.profile_groups
        if candidate.profile_sources and not cluster.profile_sources:
            cluster.profile_sources = candidate.profile_sources

        sample_seen = seen_samples.setdefault(candidate.section, set())
        for example in candidate.examples:
            sample_id = example_sample_id(example)
            if not sample_id or sample_id in sample_seen:
                continue
            sample_seen.add(sample_id)
            cluster.sample_ids.append(sample_id)
            group = sample_group(sample_id)
            cluster.sample_groups[group] = cluster.sample_groups.get(group, 0) + 1

    return sorted(
        clusters.values(),
        key=lambda cluster: (
            cluster.min_needed_samples,
            -cluster.best_observed_samples,
            -cluster.total_net_rows,
            cluster.section,
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=pathlib.Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--example-limit", type=int, default=2)
    parser.add_argument("--ranked-example-limit", type=int, default=1)
    parser.add_argument("--coverage-route-limit", type=int, default=8)
    parser.add_argument("--coverage-group-limit", type=int, default=4)
    parser.add_argument("--min-actionable-samples", type=int, default=5)
    args = parser.parse_args()

    candidates = sorted(parse_report(args.report), key=candidate_sort_key)
    low_false = [candidate for candidate in candidates if candidate.kind == "low-false"]
    shadow = [candidate for candidate in candidates if candidate.kind == "shadow"]
    near_miss = [candidate for candidate in candidates if candidate.kind == "near-miss"]
    guitar = [candidate for candidate in candidates if candidate.kind == "guitar"]
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
        if not candidate_block_reasons(candidate, args.min_actionable_samples)
    ]
    coverage_blocked = [
        candidate
        for candidate in source_safe_positive_net
        if candidate_additional_samples_needed(candidate, args.min_actionable_samples) > 0
    ]

    print(
        "detector_route_summary: "
        f"candidates={len(candidates)} low_false={len(low_false)} "
        f"shadow={len(shadow)} near_miss={len(near_miss)} guitar={len(guitar)} "
        f"drum={len(drum)} "
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
    blocked_reasons = block_reason_summary(candidates, args.min_actionable_samples)
    if blocked_reasons:
        print(
            "  blocked-reason summary "
            + " ".join(f"{reason}={count}" for reason, count in blocked_reasons)
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
        clusters = coverage_route_clusters(
            sorted(coverage_blocked, key=actionable_sort_key),
            args.min_actionable_samples,
        )
        if clusters:
            print("  coverage-route clusters")
            for cluster in clusters[: max(0, args.coverage_route_limit)]:
                examples = ",".join(
                    cluster.sample_ids[: max(0, args.example_limit)]
                )
                example_text = f" examples={examples}" if examples else ""
                groups = cluster.rule_groups or ",".join(
                    f"{group}={count}"
                    for group, count in sorted(
                        cluster.sample_groups.items(),
                        key=lambda item: (-item[1], item[0]),
                    )[: max(0, args.coverage_group_limit)]
                )
                group_text = f" groups={groups}" if groups else ""
                source_text = (
                    f" sources={cluster.rule_sources}"
                    if cluster.rule_sources else ""
                )
                bucket_group_text = (
                    f" bucket_groups={cluster.profile_groups}"
                    if cluster.profile_groups else ""
                )
                bucket_source_text = (
                    f" bucket_sources={cluster.profile_sources}"
                    if cluster.profile_sources else ""
                )
                print(
                    "    "
                    f"coverage_route {cluster.section} "
                    f"candidates={cluster.candidates} "
                    f"best_observed_samples={cluster.best_observed_samples} "
                    f"min_need_samples={cluster.min_needed_samples} "
                    f"total_net_rows={cluster.total_net_rows}"
                    f"{example_text}"
                    f"{group_text}"
                    f"{source_text}"
                    f"{bucket_group_text}"
                    f"{bucket_source_text}"
                )

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
        if candidate in actionable_set:
            for example in candidate.examples[: max(0, args.ranked_example_limit)]:
                print(f"    example {compact_example(example)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
