#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_drum_rule_grid.py"


DETAILS = (
    "kick band=1.00 seg=1.00 shape_score={kick_shape:.2f} trigger=1.00/0.60 "
    "shape=1 level={kick_level:.2f} | "
    "snare band=1.00 seg=1.00 shape_score={snare_shape:.2f} trigger=0.20/1.40 "
    "shape=1 level={snare_level:.2f} | "
    "hihat band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/1.40 shape=0 level=0.00 | "
    "crash band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/1.40 shape=0 level=0.00 | "
    "tom band=2.00 seg=2.00 shape_score={tom_shape:.2f} trigger=3.00/1.40 "
    "shape=1 level={tom_level:.2f} | "
    "ride band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/1.40 shape=0 level=0.00 | "
    "rim band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/1.40 shape=0 level=0.00 | "
    "transient=5.00 onset=5.00 energy=0.40/0.50/0.10 body=0.60/0.40/1.40 "
    "crack=0.01 upper_tom=0.30 body_shape=4"
)


def row(sample, expected, *, kick_level, snare_level, tom_level, kick_shape, snare_shape, tom_shape):
    details = DETAILS.format(
        kick_level=kick_level,
        snare_level=snare_level,
        tom_level=tom_level,
        kick_shape=kick_shape,
        snare_shape=snare_shape,
        tom_shape=tom_shape,
    )
    return f"analyzer_drum_samples: debug 100ms {sample} expected {expected} ({details}) [{details}]"


def run_evaluator(extra_args):
    log_text = "\n".join(
        [
            row(
                "tom/001.wav",
                "tom",
                kick_level=0.72,
                snare_level=0.10,
                tom_level=0.50,
                kick_shape=1.00,
                snare_shape=0.70,
                tom_shape=1.30,
            ),
            row(
                "kick/001.wav",
                "kick",
                kick_level=0.90,
                snare_level=0.10,
                tom_level=0.20,
                kick_shape=1.20,
                snare_shape=0.30,
                tom_shape=0.50,
            ),
            row(
                "snare/001.wav",
                "snare",
                kick_level=0.10,
                snare_level=0.90,
                tom_level=0.20,
                kick_shape=0.30,
                snare_shape=1.20,
                tom_shape=0.50,
            ),
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "drum_debug.err"
        log_path.write_text(log_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(log_path), *extra_args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout


def require(text, needle):
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main():
    output = run_evaluator(
        [
            "--snare-ratios",
            "1.00",
            "--kick-ratios",
            "1.00",
            "--mid-low-ratios",
            "0.75",
            "--active-bias",
            "--mul",
            "1.50",
            "--add",
            "0.10",
            "--top",
            "1",
        ]
    )
    require(output, "baseline tom=0 kick=1 snare=1 total=2")
    require(output, "tom=1 (+1) kick=1 (+0) snare=1 (+0) total=3 (+1)")

    filtered = run_evaluator(
        [
            "--snare-ratios",
            "1.00",
            "--kick-ratios",
            "1.00",
            "--mid-low-ratios",
            "0.75",
            "--min-total-gain",
            "2",
        ]
    )
    require(filtered, "baseline tom=0 kick=1 snare=1 total=2")
    require(filtered, "no candidates")

    print("test_evaluate_drum_rule_grid: ok")


if __name__ == "__main__":
    raise SystemExit(main())
