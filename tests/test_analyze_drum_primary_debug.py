#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_drum_primary_debug.py"


def run_analysis(log_text: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "drum_primary_debug.err"
        log_path.write_text(log_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(log_path)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    output = run_analysis(
        "\n".join(
            [
                "analyzer_drum_samples: primary miss 100ms tom/001.wav expected tom got kick "
                "(kick=0.96* snare=0.00 hihat=0.00 crash=0.00 tom=0.71* ride=0.00 rim=0.00) "
                "[kick band=4.00 seg=5.00 shape_score=6.00 trigger=1.60/0.60 shape=1 level=0.96 | "
                "snare band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
                "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
                "crash band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
                "tom band=8.00 seg=10.00 shape_score=7.20 trigger=1.10/1.40 shape=1 level=0.71 | "
                "ride band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
                "rim band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
                "transient=2.10 onset=1.70 energy=0.58/0.32/0.10]",
                "analyzer_drum_samples: primary miss 100ms tom/002.wav expected tom got ambiguous "
                "(kick=0.80* snare=0.00 hihat=0.00 crash=0.00 tom=0.80* ride=0.00 rim=0.00) "
                "[kick band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/0.60 shape=1 level=0.80 | "
                "tom band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/0.60 shape=1 level=0.80 | "
                "transient=2.00 onset=1.50 energy=0.33/0.33/0.34]",
            ]
        )
    )
    require(output, "drum: 2 primary misses")
    require(output, "tom -> ambiguous: 1")
    require(output, "tom -> kick: 1")
    require(output, "band        expected/got avg=2.00")
    require(output, "expected shape supported: 1/1")
    require(output, "avg energy low/mid/high=0.58/0.32/0.10")
    print("test_analyze_drum_primary_debug: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
