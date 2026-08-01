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
  nearest over-budget single-condition candidate rules:
    slope>=0.203: pos=20/22 rows=47 neg=202/254 rows=616 foreign_miss=75/93 rows=242 neg_sources=vocals/example=45 foreign_sources=vocals/other=19
      positive examples:
        sample expected=D#3 debug=D#3 owner=other
route snare->tom positives=492 rows=492 protected_correct=13126 rows=13126
  +24 rows=24 -5 rows=5 foreign=4 rows=4 new-active=0 rows=0 primary-break=4 rows=4 side_rows=13 net_rows=11 gain_per_side=1.85 :: hihat_band>=24.633 AND tom_level>=0.981
  +21 rows=21 -7 rows=7 foreign=6 rows=6 new-active=1 rows=1 primary-break=6 rows=6 side_rows=20 net_rows=1 gain_per_side=1.05 :: hihat_band>=24.633 AND tom_seg<=225.582
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "route_report.txt"
        path.write_text(report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--limit", "5"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

    output = result.stdout
    require(
        output,
        "detector_route_summary: candidates=5 low_false=2 near_miss=1 drum=2 positive_net=4 gain_ge_1=4",
    )
    require(
        output,
        "low-false row_confusion:piano/electronic->amb +samples=23 +rows=44 -samples=15 -rows=29 foreign_rows=0 side_rows=29 net_rows=15 gain_per_side=1.52",
    )
    require(
        output,
        "near-miss row_confusion:piano/electronic->amb +samples=20 +rows=47 -samples=202 -rows=616 foreign_rows=242 side_rows=858 net_rows=-811 gain_per_side=0.05",
    )
    require(
        output,
        "drum route snare->tom +rows=24 -rows=5 foreign_rows=4 new_active_rows=0 primary_break_rows=4 side_rows=13 net_rows=11 gain_per_side=1.85",
    )
    if output.index("low-false row_confusion") > output.index("drum route snare->tom"):
        raise AssertionError(f"expected low-false candidates before drum routes:\n{output}")
    if output.index("near-miss row_confusion") > output.index("drum route snare->tom"):
        raise AssertionError(f"expected near-miss candidates before drum routes:\n{output}")

    print("test_summarize_detector_route_report: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
