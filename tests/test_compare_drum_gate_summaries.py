#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compare_drum_gate_summaries.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    before_text = """
sample metrics usable=858 skipped=0
sample kick: recall=156/160 97.50% primary=151/160 94.38% precision=156/310 50.32% false=154
sample tom: recall=139/160 86.88% primary=119/160 74.38% precision=139/388 35.82% false=249
active expected kick: hit=156/273 hit_share=57.14% off_target=117 top_off_target=tom=86 snare=21 hihat=5 rim=3
active expected tom: hit=139/351 hit_share=39.60% off_target=212 top_off_target=snare=108 kick=60 hihat=21 rim=10
primary expected kick: hit=151/160 hit_share=94.38% off_target=9 top_off_target=snare=5 tom=4
primary expected tom: hit=119/160 hit_share=74.38% off_target=41 top_off_target=snare=26 kick=6 rim=3 ambiguous=2
""".strip()
    after_text = """
sample metrics usable=858 skipped=0
sample kick: recall=156/160 97.50% primary=153/160 95.62% precision=156/310 50.32% false=154
sample tom: recall=128/160 80.00% primary=106/160 66.25% precision=128/329 38.91% false=201
active expected kick: hit=156/239 hit_share=65.27% off_target=83 top_off_target=tom=52 snare=21 hihat=5 rim=3
active expected tom: hit=128/340 hit_share=37.65% off_target=212 top_off_target=snare=108 kick=60 hihat=21 rim=10
primary expected kick: hit=153/160 hit_share=95.62% off_target=7 top_off_target=snare=5 tom=2
primary expected tom: hit=106/160 hit_share=66.25% off_target=54 top_off_target=snare=30 kick=11 ambiguous=4 none=4
""".strip()
    with tempfile.TemporaryDirectory() as tmpdir:
        before = pathlib.Path(tmpdir) / "before.txt"
        after = pathlib.Path(tmpdir) / "after.txt"
        before.write_text(before_text, encoding="utf-8")
        after.write_text(after_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(before), str(after)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum gate summary comparison: before=")
    require(output, "matrix route comparison uses summarized top-off-target rows")
    require(output, "sample tom: recall 139/160->128/160 (-11) primary 119/160->106/160 (-13) false 249->201 (-48)")
    require(output, "active route kick->tom: 86->52 (-34)")
    require(output, "primary route tom->kick: 6->11 (+5)")

    raw_before = """
analyzer_drum_samples: active matrix
  expected kick  kick=3 snare=1 tom=2
analyzer_drum_samples: primary matrix
  expected kick  kick=2 snare=1 tom=1
""".strip()
    raw_after = """
analyzer_drum_samples: active matrix
  expected kick  kick=3 snare=1 tom=0
analyzer_drum_samples: primary matrix
  expected kick  kick=3 snare=0 tom=1
""".strip()
    with tempfile.TemporaryDirectory() as tmpdir:
        before = pathlib.Path(tmpdir) / "before.out"
        after = pathlib.Path(tmpdir) / "after.out"
        before.write_text(raw_before, encoding="utf-8")
        after.write_text(raw_after, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(before), str(after)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "active route kick->tom: 2->0 (-2)")
    require(output, "primary route kick->snare: 1->0 (-1)")
    print("test_compare_drum_gate_summaries: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
