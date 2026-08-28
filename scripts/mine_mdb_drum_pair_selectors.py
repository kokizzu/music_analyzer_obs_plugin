#!/usr/bin/env python3
"""Mine small two-condition zero-false-positive MDB drum recovery selectors."""

from dataclasses import dataclass
from itertools import combinations

from mine_mdb_drum_selectors import CATEGORIES, read_events


@dataclass(frozen=True)
class Condition:
    feature: str
    direction: str
    threshold: float
    positive_indexes: frozenset[int]
    negative_indexes: frozenset[int]

    def text(self) -> str:
        return f"{self.feature}{self.direction}{self.threshold:.4g}"


def matching_indexes(events, indexes, feature: str, direction: str, threshold: float) -> frozenset[int]:
    return frozenset(
        index for index in indexes
        if (events[index].values[feature] <= threshold if direction == "<="
            else events[index].values[feature] >= threshold)
    )


def conditions(events, category: str) -> list[Condition]:
    positives = [
        index for index, event in enumerate(events)
        if category in event.expected and not event.active[category] and event.levels[category] <= 0.30
    ]
    negatives = [
        index for index, event in enumerate(events)
        if category not in event.expected and not event.active[category] and event.levels[category] <= 0.30
    ]
    candidates: list[Condition] = []
    seen: set[tuple[frozenset[int], frozenset[int]]] = set()
    for feature in events[0].values:
        thresholds = sorted({events[index].values[feature] for index in positives + negatives})
        for direction in ("<=", ">="):
            for threshold in thresholds:
                matched_positive = matching_indexes(events, positives, feature, direction, threshold)
                matched_negative = matching_indexes(events, negatives, feature, direction, threshold)
                if len(matched_positive) < 3 or len(matched_negative) > 4:
                    continue
                signature = (matched_positive, matched_negative)
                if signature in seen:
                    continue
                seen.add(signature)
                candidates.append(Condition(
                    feature, direction, threshold, matched_positive, matched_negative))
    candidates.sort(key=lambda item: (-len(item.positive_indexes), len(item.negative_indexes), item.text()))
    return candidates[:48]


def main() -> int:
    events = read_events()
    print(f"mdb_drum_pair_selector_events={len(events)}")
    for category in CATEGORIES:
        options = conditions(events, category)
        found = []
        for first, second in combinations(options, 2):
            true_positive = first.positive_indexes & second.positive_indexes
            false_positive = first.negative_indexes & second.negative_indexes
            if len(true_positive) >= 3 and not false_positive:
                found.append((len(true_positive), first, second, true_positive))
        found.sort(key=lambda item: (-item[0], item[1].text(), item[2].text()))
        print(f"{category}_pair_candidates={len(found)}")
        for matched, first, second, indexes in found[:5]:
            samples = ",".join(f"{events[index].recording}@{events[index].sample}" for index in sorted(indexes))
            trigger_values = [events[index].values[f"{category}_trigger_ratio"] for index in indexes]
            level_values = [events[index].levels[category] for index in indexes]
            transient_values = [events[index].values["transient"] for index in indexes]
            print(
                f"pair category={category} {first.text()} AND {second.text()} "
                f"tp={matched} fp=0 trigger={min(trigger_values):.3g}-{max(trigger_values):.3g} "
                f"level={min(level_values):.2f}-{max(level_values):.2f} "
                f"transient={min(transient_values):.3g}-{max(transient_values):.3g} examples={samples}"
            )
    return 0


if __name__ == "__main__":
    main()
