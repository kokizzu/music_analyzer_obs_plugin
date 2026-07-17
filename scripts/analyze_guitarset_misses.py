#!/usr/bin/env python3
import collections
import re
import sys


MISS_RE = re.compile(
    r"chord opportunity `([^`]*)`, detected global `([^`]*)`, key `([^`]*)`, "
    r"guitar `([^`]*)`, other `([^`]*)`"
)
ROOT_RE = re.compile(r"([A-G]#?)")


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
    plain_to_power = []

    for opportunity, _global, _key, guitar, _other in misses:
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
            if not plain_major_minor(expected_label):
                continue
            expected_power = f"{root(expected_label)}pow"
            for detected_label in detected:
                if detected_label == expected_power:
                    plain_to_power.append((expected_label, detected_label))

    print(f"misses {len(misses)}")
    print("by expected quality")
    for key, value in by_expected_quality.most_common(20):
        print(f"{value} {key} right_root {matching_root_by_quality[key]}")
    print("top expected->detected quality pairs with matching root")
    for (expected_quality, detected_quality), value in quality_pairs.most_common(30):
        print(f"{value} {expected_quality} => {detected_quality}")
    print(f"same_root_plain_major_minor_to_power {len(plain_to_power)}")
    for expected_label, detected_label in plain_to_power[:80]:
        print(f"{expected_label} -> {detected_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
