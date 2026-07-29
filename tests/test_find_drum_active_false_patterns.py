#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_drum_active_false_patterns.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    header = (
        "sample\texpected\tgot\tbody_shape\tlow\tmid\thigh\tkick_level\tkick_seg\tkick_trigger\t"
        "kick_threshold\tsnare_level\tsnare_seg\tsnare_trigger\tsnare_threshold\thihat_level\t"
        "hihat_seg\thihat_trigger\thihat_threshold\tcrash_level\tcrash_seg\tcrash_trigger\t"
        "crash_threshold\ttom_level\ttom_seg\ttom_trigger\ttom_threshold\tride_level\t"
        "ride_seg\tride_trigger\tride_threshold\trim_level\trim_seg\trim_trigger\trim_threshold"
    )
    rows = [
        "kick/a.wav\tkick\tkick\t0\t0.80\t0.12\t0.08\t0.92\t18\t4.0\t1.0\t0.56\t5\t2.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "kick/b.wav\tkick\tkick\t0\t0.78\t0.14\t0.08\t0.88\t16\t3.8\t1.0\t0.62\t6\t2.3\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/a.wav\tsnare\tsnare\t1\t0.18\t0.62\t0.20\t0.05\t2\t0.2\t1.0\t0.90\t24\t4.2\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0.20\t8\t0.8\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/b.wav\tsnare\tsnare\t1\t0.16\t0.64\t0.20\t0.04\t2\t0.2\t1.0\t0.84\t22\t3.9\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0.15\t7\t0.7\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "tom/a.wav\ttom\ttom\t1\t0.24\t0.58\t0.18\t0.04\t3\t0.2\t1.0\t0.18\t8\t0.8\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0.88\t20\t4.0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "drum.tsv"
        table.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(table),
                "--route",
                "kick->snare",
                "--min-positive-samples",
                "2",
                "--max-protected-samples",
                "0",
                "--max-conditions",
                "2",
                "--show-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum active false pattern candidates: rows=5 extra_protected_rows=0 threshold=0.30 routes=1")
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=2 rows=2")
    require(output, "+2 rows=2 -0 rows=0")
    require(output, "false-active examples:")

    extra_protected_rows = [
        "snare/extra.wav\tsnare\tsnare\t0\t0.79\t0.13\t0.08\t0.90\t17\t3.9\t1.0\t0.60\t6\t2.1\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "drum.tsv"
        extra = pathlib.Path(tmpdir) / "extra.tsv"
        table.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
        extra.write_text(header + "\n" + "\n".join(extra_protected_rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(table),
                "--extra-protected-rows",
                str(extra),
                "--route",
                "kick->snare",
                "--min-positive-samples",
                "2",
                "--max-protected-samples",
                "0",
                "--max-conditions",
                "1",
                "--show-examples",
                "1",
                "--show-near-misses",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "drum active false pattern candidates: rows=5 extra_protected_rows=1 threshold=0.30 routes=1")
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=3 rows=3")
    require(output, "nearest over-budget rules:")
    require(output, "snare/extra.wav snare->snare")

    guarded_rows = [
        "kick/near-a.wav\tkick\tkick\t1\t0.80\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.60\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "kick/near-b.wav\tkick\tkick\t1\t0.81\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.60\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/near-a.wav\tsnare\tsnare\t1\t0.779\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.60\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/near-b.wav\tsnare\tsnare\t1\t0.778\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.60\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "guarded.tsv"
        table.write_text(header + "\n" + "\n".join(guarded_rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(table),
                "--route",
                "kick->snare",
                "--min-positive-samples",
                "2",
                "--max-protected-samples",
                "0",
                "--max-conditions",
                "1",
                "--protected-margin",
                "0.03",
                "--show-near-misses",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=2 rows=2")
    require(output, "nearest over-budget rules:")
    require(output, "+2 rows=2 -2 rows=2")

    accepted_near_rows = [
        "kick/near-a.wav\tkick\tkick\t1\t0.80\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.60\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "kick/near-b.wav\tkick\tkick\t1\t0.81\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.61\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/near-a.wav\tsnare\tsnare\t1\t0.83\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.90\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
        "snare/near-b.wav\tsnare\tsnare\t1\t0.84\t0.10\t0.10\t0.50\t10\t1.0\t1.0\t0.88\t10\t1.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "accepted-near.tsv"
        table.write_text(header + "\n" + "\n".join(accepted_near_rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(table),
                "--route",
                "kick->snare",
                "--min-positive-samples",
                "2",
                "--max-protected-samples",
                "0",
                "--max-conditions",
                "1",
                "--protected-margin",
                "0",
                "--show-near-misses",
                "1",
                "--limit",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=2 rows=2")
    require(output, "nearest protected true-active near misses:")
    require(output, "snare/near-a.wav snare->snare")
    require(output, "low=0.83 <= 0.81 +0.02")
    print("test_find_drum_active_false_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
