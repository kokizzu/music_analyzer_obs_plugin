#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_detector_route_report.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {needle!r} in:\n{text}")


def main() -> int:
    report = """candidate rules are attribute selectors; rerun gates
row_confusion:piano/electronic->amb positives=186 samples/636 rows protected_hits=2209 samples/22357 rows foreign_misses=0 samples/0 rows
  low-false candidate rules:
    debug_conf<=0.542 AND partial3>=2.46 AND partial5<=0.02: pos=23/186 rows=44 neg=15/2209 rows=29 neg_sources=piano/electronic=27,other/acoustic=2
    debug_conf<=0.542 AND partial3>=2.46 AND slope>=0.655: pos=23/186 rows=44 neg=16/2209 rows=29 neg_sources=piano/electronic=24,other/acoustic=5
  highest-coverage candidate rules:
    debug_conf<=0.542 AND partial3>=2.46 AND partial5<=0.02: pos=23/186 rows=44 neg=15/2209 rows=29 neg_sources=piano/electronic=27,other/acoustic=2
route snare->tom positives=492 rows=492 protected_correct=13126 rows=13126
  +24 rows=24 -5 rows=5 foreign=4 rows=4 new-active=0 rows=0 primary-break=4 rows=4 :: hihat_band>=24.633 AND tom_level>=0.981
  +21 rows=21 -7 rows=7 foreign=6 rows=6 new-active=1 rows=1 primary-break=6 rows=6 :: hihat_band>=24.633 AND tom_seg<=225.582
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "3"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

    output = result.stdout
    require(output, "detector_route_summary: candidates=4 low_false=2 drum=2")
    require(
        output,
        "low-false row_confusion:piano/electronic->amb +samples=23 +rows=44 -samples=15 -rows=29",
    )
    require(
        output,
        "drum route snare->tom +rows=24 -rows=5 foreign_rows=4 new_active_rows=0 primary_break_rows=4",
    )
    if output.index("low-false row_confusion") > output.index("drum route snare->tom"):
        raise AssertionError(f"expected low-false candidates before drum routes:\n{output}")

    print("test_summarize_detector_route_report: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
