#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_drum_rule_flags.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    header = (
        "sample\texpected\tgot\tkick_level\tsnare_level\thihat_level\tcrash_level\ttom_level\t"
        "ride_level\trim_level\tflag_one_shot_source\tflag_real_track_source\t"
        "flag_tom_kick_primary_recovery\tflag_protected_tom_kick_primary_recovery\t"
        "flag_strong_low_kick_tom_bleed\tflag_saturated_kick_tom_bleed\t"
        "flag_high_band_kick_body_tom_bleed"
    )
    rows = [
        "kick/a.wav\tkick\tkick\t0.95\t0.10\t0\t0\t0.62\t0\t0\t1\t0\t1\t0\t0\t1\t1",
        "kick/b.wav\tkick\tkick\t0.90\t0.10\t0\t0\t0.66\t0\t0\t1\t0\t1\t0\t0\t1\t1",
        "tom/a.wav\ttom\ttom\t0.20\t0.10\t0\t0\t0.91\t0\t0\t0\t1\t1\t1\t0\t0\t0",
        "tom/b.wav\ttom\ttom\t0.18\t0.10\t0\t0\t0.88\t0\t0\t0\t1\t0\t0\t0\t0\t0",
        "snare/a.wav\tsnare\tsnare\t0.15\t0.92\t0\t0\t0.40\t0\t0\t0\t1\t0\t0\t1\t0\t0",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "drums.tsv"
        table.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(table),
                "--route",
                "kick:tom",
                "--threshold",
                "0.30",
                "--examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum rule flag summary: rows=5 threshold=0.30 source=")
    require(output, "route kick->tom false=2 protected_true_tom=2")
    require(output, "false_level_med=0.640 protected_level_med=0.895")
    require(output, "flag_saturated_kick_tom_bleed=2/2 100.0%")
    require(output, "flag_high_band_kick_body_tom_bleed=2/2 100.0%")
    require(output, "flag_protected_tom_kick_primary_recovery=1/2 50.0%")
    require(
        output,
        "flag_saturated_kick_tom_bleed=false 2/2 100.0% protected 0/2 0.0%",
    )
    require(output, "sample=kick/a.wav got=kick tom_level=0.620 kick_level=0.950")
    print("test_summarize_drum_rule_flags: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
