#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_drum_debug_rows.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    log_text = (
        "analyzer_drum_samples: debug 100ms tom/zero-denom.wav expected tom "
        "(kick=0.00 snare=0.90* hihat=0.00 crash=0.00 tom=0.60* ride=0.00 rim=0.00) "
        "[snare band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/1.00 shape=1 level=0.90 | "
        "tom band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/1.00 shape=1 level=0.60 | "
        "transient=2.00 onset=1.50 energy=0.20/0.70/0.10 "
        "body=1.00/0.00/2.00 crack=0.10 upper_tom=0.00 body_shape=2]"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "drum_debug.err"
        log_path.write_text(log_text, encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--expected",
                "tom",
                "--focus",
                "tom",
                "--against",
                "snare",
                "--examples",
                "2",
                str(log_path),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    output = completed.stdout
    require(output, "rows=1 primary=snare=1")
    require(output, "snare: 1")
    require(output, "tom/snare level: avg=0.67")
    require(output, "tom/snare body: n/a")
    require(output, "examples: tom/zero-denom.wav")
    if "100000" in output:
        raise AssertionError(f"expected zero-denominator ratios to be skipped:\n{output}")
    print("test_analyze_drum_debug_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
