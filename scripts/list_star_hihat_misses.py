#!/usr/bin/env python3
"""Print the annotated STAR hi-hat windows that are still inactive."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "star_drums_verbose_windows.log"
WINDOW = re.compile(r"E-GMD window .*? expected (.+?):")
HAT = re.compile(
    r"HIHAT band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d) level=([0-9.]+)(\*)?"
)
TAIL = re.compile(r"transient=([0-9.]+)")


def main() -> int:
    missed = []
    candidate_true_positive = 0
    candidate_false_positive = 0
    candidate_false_lines = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        expected = WINDOW.search(line)
        hat = HAT.search(line)
        transient = TAIL.search(line)
        if expected is None or hat is None or transient is None:
            continue
        expects_hihat = "hihat" in expected.group(1).lower()
        active = hat.group(8) == "*"
        if expects_hihat and not active:
            missed.append(line)
        trigger_ratio = float(hat.group(4)) / max(float(hat.group(5)), 1.0e-6)
        candidate = (
            not active and float(hat.group(7)) <= 0.30 and
            float(hat.group(1)) >= 3.06 and trigger_ratio >= 3.32 and
            float(transient.group(1)) < 1.55
        )
        if candidate and expects_hihat:
            candidate_true_positive += 1
        elif candidate:
            candidate_false_positive += 1
            candidate_false_lines.append(line)
    print(f"star_hihat_misses={len(missed)}")
    for line in missed:
        print(line)
    print(f"star_compact_hihat_candidate_tp={candidate_true_positive}")
    print(f"star_compact_hihat_candidate_fp={candidate_false_positive}")
    for line in candidate_false_lines:
        print(f"false_candidate {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
