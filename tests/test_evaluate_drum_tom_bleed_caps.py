#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_drum_tom_bleed_caps.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "debug.err"
        log_path.write_text(
            "\n".join(
                [
                    "analyzer_drum_samples: debug 100ms snare/001.wav expected snare "
                    "(kick=0.00 snare=0.90* hihat=0.00 crash=0.00 tom=0.80* ride=0.00 rim=0.00) "
                    "[kick band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "snare band=6.00 seg=6.00 shape_score=6.00 trigger=3.00/1.42 shape=1 level=0.90 | "
                    "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "crash band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "tom band=5.00 seg=5.00 shape_score=5.00 trigger=2.50/1.42 shape=1 level=0.80 | "
                    "ride band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "rim band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "transient=2.00 onset=2.00 energy=0.20/0.60/0.20 "
                    "body=2.00/10.00/12.00 crack=2.40 upper_tom=8.00 body_shape=4]",
                    "analyzer_drum_samples: debug 100ms tom/001.wav expected tom "
                    "(kick=0.00 snare=0.70* hihat=0.00 crash=0.00 tom=0.90* ride=0.00 rim=0.00) "
                    "[kick band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "snare band=5.00 seg=5.00 shape_score=5.00 trigger=2.00/1.42 shape=1 level=0.70 | "
                    "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "crash band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "tom band=8.00 seg=8.00 shape_score=8.00 trigger=4.00/1.42 shape=1 level=0.90 | "
                    "ride band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "rim band=1.00 seg=1.00 shape_score=1.00 trigger=1.00/1.42 shape=0 level=0.00 | "
                    "transient=2.00 onset=2.00 energy=0.20/0.60/0.20 "
                    "body=2.00/10.00/18.00 crack=1.00 upper_tom=10.00 body_shape=4]",
                ]
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(log_path), "--rule", "snare_crack_clear"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    assert "rows=2" in output
    assert "rule=snare_crack_clear" in output
    assert "false_tom=1->0" in output
    assert "tom_hit=1->1" in output
    print("test_evaluate_drum_tom_bleed_caps: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
