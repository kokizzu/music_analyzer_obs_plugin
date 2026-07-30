#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_drum_tom_bleed_caps.py"


def run_script(path: pathlib.Path) -> str:
    try:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--rule", "snare_crack_clear"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stdout or "")
        sys.stderr.write(exc.stderr or "")
        raise
    return completed.stdout


def assert_expected_summary(output: str) -> None:
    assert "rows=2" in output
    assert "rule=snare_crack_clear" in output
    assert "false_tom=1->0" in output
    assert "tom_hit=1->1" in output


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
        tsv_path = pathlib.Path(tmpdir) / "rows.tsv"
        tsv_path.write_text(
            "\n".join(
                [
                    "sample\texpected\tgot\tenergy_low\tenergy_mid\tenergy_high\t"
                    "kick_body\tsnare_body\ttom_body\tsnare_crack\tupper_tom_body\tbody_shape\t"
                    "kick_band\tkick_seg\tkick_shape_score\tkick_trigger\tkick_threshold\tkick_shape\tkick_level\t"
                    "snare_band\tsnare_seg\tsnare_shape_score\tsnare_trigger\tsnare_threshold\tsnare_shape\tsnare_level\t"
                    "hihat_band\thihat_seg\thihat_shape_score\thihat_trigger\thihat_threshold\thihat_shape\thihat_level\t"
                    "crash_band\tcrash_seg\tcrash_shape_score\tcrash_trigger\tcrash_threshold\tcrash_shape\tcrash_level\t"
                    "tom_band\ttom_seg\ttom_shape_score\ttom_trigger\ttom_threshold\ttom_shape\ttom_level\t"
                    "ride_band\tride_seg\tride_shape_score\tride_trigger\tride_threshold\tride_shape\tride_level\t"
                    "rim_band\trim_seg\trim_shape_score\trim_trigger\trim_threshold\trim_shape\trim_level",
                    "snare/001.wav\tsnare\tsnare\t0.20\t0.60\t0.20\t"
                    "2.00\t10.00\t12.00\t2.40\t8.00\t4\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "6.00\t6.00\t6.00\t3.00\t1.42\t1\t0.90\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "5.00\t5.00\t5.00\t2.50\t1.42\t1\t0.80\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00",
                    "tom/001.wav\ttom\ttom\t0.20\t0.60\t0.20\t"
                    "2.00\t10.00\t18.00\t1.00\t10.00\t4\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "5.00\t5.00\t5.00\t2.00\t1.42\t1\t0.70\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "8.00\t8.00\t8.00\t4.00\t1.42\t1\t0.90\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00\t"
                    "1.00\t1.00\t1.00\t1.00\t1.42\t0\t0.00",
                ]
            ),
            encoding="utf-8",
        )
        assert_expected_summary(run_script(log_path))
        assert_expected_summary(run_script(tsv_path))
    print("test_evaluate_drum_tom_bleed_caps: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
