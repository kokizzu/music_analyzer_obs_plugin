#!/usr/bin/env python3
"""List MDB low-level snare candidates selected by weak concurrent kick evidence."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "build" / "mdb_drums_windows.log"
EXPECTED = re.compile(r"E-GMD window (.+?) sample (\d+) expected (.+?):")
SNARE = re.compile(
    r"SNARE band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d) level=([0-9.]+)(\*)?"
)
KICK = re.compile(
    r"BASS DRUM band=([0-9.]+) seg=([0-9.]+) shape=([0-9.]+) "
    r"trig=([0-9.]+)/([0-9.]+) supported=(\d) level=([0-9.]+)(\*)?"
)
TAIL = re.compile(r"rms=([0-9.]+).*?transient=([0-9.]+) onset=([0-9.]+)")


def main() -> int:
    true_positive = 0
    false_positive = 0
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        expected = EXPECTED.search(line)
        snare = SNARE.search(line)
        kick = KICK.search(line)
        tail = TAIL.search(line)
        if expected is None or snare is None or kick is None or tail is None:
            continue
        snare_active = snare.group(8) == "*"
        snare_level = float(snare.group(7))
        kick_ratio = float(kick.group(4)) / max(float(kick.group(5)), 1.0e-6)
        if snare_active or snare_level > 0.30 or kick_ratio > 4.356:
            continue
        expected_snare = "snare" in expected.group(3).lower()
        if expected_snare:
            true_positive += 1
        else:
            false_positive += 1
        snare_ratio = float(snare.group(4)) / max(float(snare.group(5)), 1.0e-6)
        print(
            f"expected={expected.group(3)} recording={expected.group(1)} sample={expected.group(2)} "
            f"snare_band={snare.group(1)} seg={snare.group(2)} shape={snare.group(3)} "
            f"snare_trigger={snare.group(4)}/{snare.group(5)} ratio={snare_ratio:.2f} "
            f"kick_ratio={kick_ratio:.2f} rms={tail.group(1)} transient={tail.group(2)} onset={tail.group(3)}"
        )
    print(f"snare_candidates_tp={true_positive}")
    print(f"snare_candidates_fp={false_positive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
