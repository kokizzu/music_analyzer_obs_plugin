#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_drum_active_false_patterns.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def load_script_module():
    spec = importlib.util.spec_from_file_location("find_drum_active_false_patterns_for_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("failed to load find_drum_active_false_patterns.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_script_module()
    ratio_row = {
        "hihat_seg": "14.248",
        "hihat_shape_score": "50.0",
        "rim_shape_score": "2.0",
        "ride_seg": "7.124",
        "ride_shape_score": "3.0",
    }
    module.add_ratios(ratio_row)
    if ratio_row.get("hihat_rim_shape_score_ratio") != "7.124000000":
        raise AssertionError(f"hihat/rim runtime ratio mismatch: {ratio_row}")
    if ratio_row.get("ride_hihat_shape_score_ratio") != "0.500000000":
        raise AssertionError(f"ride/hihat runtime ratio mismatch: {ratio_row}")

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
    require(output, "ranked active false suppression opportunities")
    require(output, "attribute-level candidates; validate runtime changes with the full drum gate")
    require(output, "near_protected is closest true-active miss-count/normalized-gap; lower is riskier")
    require(output, "candidate kick->snare +2 rows=2 -0 rows=0 foreign=0 rows=0 protected_true_snare=2")
    require(output, "cap_samples=true 2->2 false 2->0 route 2->0 foreign 0->0")

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
                "--row-examples",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "false-active examples:")
    require(output, "kick/a.wav kick->snare")

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
                "1",
                "--limit",
                "4",
                "--exclude-fields",
                "kick_level,body_shape",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=2 rows=2")
    if "kick_level" in output or "body_shape" in output:
        raise AssertionError(f"excluded field appeared in output:\n{output}")

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
    require(output, "nearest kick->snare +2 rows=2 -1 rows=1 foreign=0 rows=0 protected_true_snare=3")
    require(output, "cap_samples=true 3->2 false 2->0 route 2->0 foreign 0->0")

    foreign_active_rows = rows + [
        "tom/foreign.wav\ttom\ttom\t0\t0.80\t0.12\t0.08\t0.92\t18\t4.0\t1.0\t0.56\t5\t2.0\t1.0\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1\t0\t0\t0\t1",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        table = pathlib.Path(tmpdir) / "foreign.tsv"
        table.write_text(header + "\n" + "\n".join(foreign_active_rows) + "\n", encoding="utf-8")
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
    require(output, "foreign_active=1 rows=1")
    require(output, "nearest over-budget rules:")
    require(output, "+2 rows=2 -0 rows=0 foreign=1 rows=1")
    require(output, "foreign active examples:")
    require(output, "tom/foreign.wav tom->snare")
    require(output, "nearest kick->snare +2 rows=2 -0 rows=0 foreign=1 rows=1 protected_true_snare=2")
    require(output, "cap_samples=true 2->2 false 3->0 route 2->0 foreign 1->0")

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
    require(output, "near_protected=1miss/0.02")
    require(output, "snare/near-a.wav snare->snare")
    require(output, "low=0.83 <= 0.81 +0.02")

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
                "--min-near-protected-score",
                "0.05",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "route kick->snare positives=2 rows=2 protected_true_snare=2 rows=2")
    require(output, "nearest guarded rules:")
    require(output, "nearest kick->snare +2 rows=2 -0 rows=0 foreign=0 rows=0 protected_true_snare=2 near_protected=1miss/0.02")
    require(output, "cap_samples=true 2->2 false 2->0 route 2->0 foreign 0->0")
    if "candidate kick->snare" in output:
        raise AssertionError(f"near-protected candidate should be guarded:\n{output}")
    print("test_find_drum_active_false_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
