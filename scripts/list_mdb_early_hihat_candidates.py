#!/usr/bin/env python3
"""List low-onset MDB hi-hat recovery candidates from verbose analyzer output."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "mdb_drums_windows.log"
EXPECTED = re.compile(r"E-GMD window (.+?) sample (\d+) expected (.+?):")
HAT = re.compile(
    r"HIHAT band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d) level=([0-9.]+)(\*)?"
)
RIDE = re.compile(
    r"RIDE band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d) level=([0-9.]+)(\*)?"
)
TAIL = re.compile(r"rms=([0-9.]+).*?transient=([0-9.]+) onset=([0-9.]+)")


def main() -> int:
    candidates = 0
    false_positives = 0
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        expected = EXPECTED.search(line)
        hat = HAT.search(line)
        tail = TAIL.search(line)
        if expected is None or hat is None or tail is None:
            continue
        onset = float(tail.group(3))
        level = float(hat.group(7))
        active = hat.group(8) == "*"
        if onset > 2.49 or level > 0.30 or active:
            continue
        wants_hat = "hihat" in expected.group(3).lower()
        if wants_hat:
            candidates += 1
        else:
            false_positives += 1
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"hat_band={hat.group(1)} seg={hat.group(2)} shape={hat.group(3)} "
            f"trigger={hat.group(4)}/{hat.group(5)} supported={hat.group(6)} level={hat.group(7)} "
            f"rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"early_hihat_missed_positives={candidates}")
    print(f"early_hihat_false_positive_windows={false_positives}")
    print("== high-rms missed hi-hat candidates ==")
    candidates = 0
    false_positives = 0
    for line in lines:
        expected = EXPECTED.search(line)
        hat = HAT.search(line)
        tail = TAIL.search(line)
        if expected is None or hat is None or tail is None:
            continue
        rms = float(tail.group(1))
        level = float(hat.group(7))
        active = hat.group(8) == "*"
        if rms < 0.2953 or level > 0.30 or active:
            continue
        wants_hat = "hihat" in expected.group(3).lower()
        if wants_hat:
            candidates += 1
        else:
            false_positives += 1
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"hat_band={hat.group(1)} seg={hat.group(2)} shape={hat.group(3)} "
            f"trigger={hat.group(4)}/{hat.group(5)} supported={hat.group(6)} level={hat.group(7)} "
            f"rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"high_rms_hihat_missed_positives={candidates}")
    print(f"high_rms_hihat_false_positive_windows={false_positives}")
    print("== extreme-trigger missed hi-hat candidates ==")
    candidates = 0
    false_positives = 0
    for line in lines:
        expected = EXPECTED.search(line)
        hat = HAT.search(line)
        tail = TAIL.search(line)
        if expected is None or hat is None or tail is None:
            continue
        trigger_ratio = float(hat.group(4)) / max(float(hat.group(5)), 1.0e-6)
        level = float(hat.group(7))
        active = hat.group(8) == "*"
        if trigger_ratio < 101.1 or level > 0.30 or active:
            continue
        wants_hat = "hihat" in expected.group(3).lower()
        if wants_hat:
            candidates += 1
        else:
            false_positives += 1
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"hat_band={hat.group(1)} seg={hat.group(2)} shape={hat.group(3)} "
            f"trigger={hat.group(4)}/{hat.group(5)} supported={hat.group(6)} level={hat.group(7)} "
            f"rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"extreme_trigger_hihat_missed_positives={candidates}")
    print(f"extreme_trigger_hihat_false_positive_windows={false_positives}")
    print("== quiet-ride missed hi-hat candidates ==")
    candidates = 0
    false_positives = 0
    for line in lines:
        expected = EXPECTED.search(line)
        hat = HAT.search(line)
        ride = RIDE.search(line)
        tail = TAIL.search(line)
        if expected is None or hat is None or ride is None or tail is None:
            continue
        level = float(hat.group(7))
        active = hat.group(8) == "*"
        if float(ride.group(2)) > 1.15 or level > 0.30 or active:
            continue
        wants_hat = "hihat" in expected.group(3).lower()
        if wants_hat:
            candidates += 1
        else:
            false_positives += 1
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"hat_band={hat.group(1)} seg={hat.group(2)} shape={hat.group(3)} "
            f"trigger={hat.group(4)}/{hat.group(5)} supported={hat.group(6)} level={hat.group(7)} "
            f"ride_seg={ride.group(2)} rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"quiet_ride_hihat_missed_positives={candidates}")
    print(f"quiet_ride_hihat_false_positive_windows={false_positives}")
    print("== broad-local hi-hat candidates ==")
    candidates = 0
    false_positives = 0
    for line in lines:
        expected = EXPECTED.search(line)
        hat = HAT.search(line)
        tail = TAIL.search(line)
        if expected is None or hat is None or tail is None:
            continue
        level = float(hat.group(7))
        active = hat.group(8) == "*"
        trigger_ratio = float(hat.group(4)) / max(float(hat.group(5)), 1.0e-6)
        if (active or level > 0.30 or trigger_ratio < 3.30 or
                float(hat.group(1)) < 3.0 or float(tail.group(2)) >= 1.55):
            continue
        wants_hat = "hihat" in expected.group(3).lower()
        if wants_hat:
            candidates += 1
        else:
            false_positives += 1
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"hat_band={hat.group(1)} seg={hat.group(2)} shape={hat.group(3)} "
            f"trigger={hat.group(4)}/{hat.group(5)} ratio={trigger_ratio:.2f} level={hat.group(7)} "
            f"rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"broad_local_hihat_missed_positives={candidates}")
    print(f"broad_local_hihat_false_positive_windows={false_positives}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
