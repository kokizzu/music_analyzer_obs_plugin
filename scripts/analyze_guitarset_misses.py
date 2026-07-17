#!/usr/bin/env python3
import collections
import re
import sys


MISS_RE = re.compile(
    r"chord opportunity `([^`]*)`, detected global `([^`]*)`, key `([^`]*)`, "
    r"guitar `([^`]*)`, other `([^`]*)`"
    r"(?:, expected pc `([^`]*)`, guitar pc `([^`]*)`, guitar cells `([^`]*)`)?"
)
ROOT_RE = re.compile(r"([A-G]#?)")
NOTE_TO_PC = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}
PC_TO_NOTE = {value: key for key, value in NOTE_TO_PC.items()}
QUALITY_INTERVALS = {
    "maj": (0, 4, 7),
    "m": (0, 3, 7),
    "pow": (0, 7),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "dim7": (0, 3, 6, 9),
    "m7b5": (0, 3, 6, 10),
    "add9": (0, 2, 4, 7),
    "9": (0, 2, 4, 7, 10),
    "maj9": (0, 2, 4, 7, 11),
    "m9": (0, 2, 3, 7, 10),
}


def root(label: str) -> str:
    if not label or label == "--":
        return "--"
    match = ROOT_RE.match(label)
    return match.group(1) if match else "?"


def quality(label: str) -> str:
    if not label or label == "--":
        return "--"
    note = root(label)
    suffix = label[len(note) :]
    return suffix or "maj"


def components(text: str, sep: str) -> list[str]:
    if not text or text == "--":
        return []
    return text.split(sep)


def plain_major_minor(label: str) -> bool:
    return re.fullmatch(r"[A-G]#?m?", label) is not None


def parse_pitch_classes(text) -> set[int]:
    if not text or text == "--":
        return set()
    result = set()
    for item in text.split(","):
        note = item.strip()
        if note in NOTE_TO_PC:
            result.add(NOTE_TO_PC[note])
    return result


def label_pitch_classes(label: str) -> set[int]:
    note = root(label)
    if note not in NOTE_TO_PC:
        return set()
    intervals = QUALITY_INTERVALS.get(quality(label))
    if intervals is None:
        return set()
    root_pc = NOTE_TO_PC[note]
    return {(root_pc + interval) % 12 for interval in intervals}


def note_list(pitch_classes: set[int]) -> str:
    return ",".join(PC_TO_NOTE[pitch_class] for pitch_class in sorted(pitch_classes)) or "--"


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "build/guitarset_verbose.log"
    misses = []
    with open(path, errors="ignore") as handle:
        for line in handle:
            match = MISS_RE.search(line)
            if match:
                misses.append(match.groups())

    by_expected_quality: collections.Counter[str] = collections.Counter()
    matching_root_by_quality: collections.Counter[str] = collections.Counter()
    quality_pairs: collections.Counter[tuple[str, str]] = collections.Counter()
    same_root_label_pairs: collections.Counter[tuple[str, str]] = collections.Counter()
    full_expected_tones_by_quality: collections.Counter[str] = collections.Counter()
    expected_tone_coverage_sum: collections.Counter[str] = collections.Counter()
    missing_tone_sets: collections.Counter[tuple[str, str]] = collections.Counter()
    plain_to_power = []
    plain_to_power_third_state: collections.Counter[str] = collections.Counter()
    has_grid_diagnostics = False

    for opportunity, _global, _key, guitar, _other, _expected_pc, guitar_pc, _guitar_cells in misses:
        expected = components(opportunity, "/")
        detected = components(guitar, "=")
        expected_quality = "/".join(sorted({quality(label) for label in expected}))
        by_expected_quality[expected_quality] += 1

        expected_roots = {root(label) for label in expected}
        detected_roots = {root(label) for label in detected}
        if expected_roots & detected_roots:
            matching_root_by_quality[expected_quality] += 1
            quality_pairs[
                (expected_quality, ",".join(sorted({quality(label) for label in detected})))
            ] += 1
            for expected_label in expected:
                expected_root = root(expected_label)
                for detected_label in detected:
                    if root(detected_label) == expected_root:
                        same_root_label_pairs[(expected_label, detected_label)] += 1

        guitar_pitch_classes = parse_pitch_classes(guitar_pc)
        if guitar_pc is not None:
            has_grid_diagnostics = True
            best_coverage = 0.0
            best_missing: set[int] = set()
            for expected_label in expected:
                expected_pitch_classes = label_pitch_classes(expected_label)
                if not expected_pitch_classes:
                    continue
                present = expected_pitch_classes & guitar_pitch_classes
                coverage = len(present) / len(expected_pitch_classes)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_missing = expected_pitch_classes - guitar_pitch_classes
                if expected_pitch_classes <= guitar_pitch_classes:
                    full_expected_tones_by_quality[expected_quality] += 1
                    best_coverage = 1.0
                    best_missing = set()
                    break
            expected_tone_coverage_sum[expected_quality] += best_coverage
            if best_missing:
                missing_tone_sets[(expected_quality, note_list(best_missing))] += 1

        for expected_label in expected:
            if not plain_major_minor(expected_label):
                continue
            expected_power = f"{root(expected_label)}pow"
            for detected_label in detected:
                if detected_label == expected_power:
                    plain_to_power.append((expected_label, detected_label))
                    expected_root = NOTE_TO_PC.get(root(expected_label))
                    if expected_root is None:
                        continue
                    major_third = (expected_root + 4) % 12
                    minor_third = (expected_root + 3) % 12
                    if quality(expected_label) == "m":
                        expected_third = minor_third
                        competing_third = major_third
                    else:
                        expected_third = major_third
                        competing_third = minor_third
                    expected_present = expected_third in guitar_pitch_classes
                    competing_present = competing_third in guitar_pitch_classes
                    if expected_present and competing_present:
                        plain_to_power_third_state["both_thirds_active"] += 1
                    elif expected_present:
                        plain_to_power_third_state["expected_third_active"] += 1
                    elif competing_present:
                        plain_to_power_third_state["wrong_third_active"] += 1
                    else:
                        plain_to_power_third_state["third_missing"] += 1

    print(f"misses {len(misses)}")
    print("by expected quality")
    for key, value in by_expected_quality.most_common(20):
        print(f"{value} {key} right_root {matching_root_by_quality[key]}")
    print("top expected->detected quality pairs with matching root")
    for (expected_quality, detected_quality), value in quality_pairs.most_common(30):
        print(f"{value} {expected_quality} => {detected_quality}")
    print("top same-root expected->detected labels")
    for (expected_label, detected_label), value in same_root_label_pairs.most_common(30):
        print(f"{value} {expected_label} => {detected_label}")
    if has_grid_diagnostics:
        print("expected tones present in guitar grid")
        for key, total in by_expected_quality.most_common(20):
            full = full_expected_tones_by_quality[key]
            average = expected_tone_coverage_sum[key] / total if total else 0.0
            print(f"{full}/{total} {key} avg_tone_coverage {average:.2f}")
        print("top missing expected tone sets")
        for (expected_quality, missing), value in missing_tone_sets.most_common(20):
            print(f"{value} {expected_quality} missing {missing}")
    print(f"same_root_plain_major_minor_to_power {len(plain_to_power)}")
    if plain_to_power_third_state:
        print("plain_to_power_third_state")
        for key, value in plain_to_power_third_state.most_common():
            print(f"{key} {value}")
    for expected_label, detected_label in plain_to_power[:80]:
        print(f"{expected_label} -> {detected_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
