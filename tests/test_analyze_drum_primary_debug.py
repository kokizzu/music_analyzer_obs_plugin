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


def run_dump(
    log_text: str,
    *,
    include_debug_rows: bool = False,
    include_merged_debug_rows: bool = False,
) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "drum_primary_debug.err"
        log_path.write_text(log_text, encoding="utf-8")
        command = [sys.executable, str(SCRIPT), str(log_path), "--dump-rows", "--expected", "tom"]
        if include_debug_rows:
            command.append("--include-debug-rows")
        if include_merged_debug_rows:
            command.append("--include-merged-debug-rows")
        completed = subprocess.run(
            command,
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


def tsv_rows(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line]
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:]]


def main() -> int:
    log_text = "\n".join(
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
            "transient=2.10 onset=1.70 energy=0.58/0.32/0.10 "
            "body=4.00/2.00/8.00 crack=0.50 upper_tom=3.00 body_shape=4 rule_flags=0x13 merged_expected=1]",
            "analyzer_drum_samples: merged debug 100ms tom/001.wav#merged expected tom "
            "(kick=0.72* snare=0.00 hihat=0.00 crash=0.00 tom=0.92* ride=0.00 rim=0.00) "
            "[kick band=6.00 seg=7.00 shape_score=8.00 trigger=1.90/0.60 shape=1 level=0.72 | "
            "snare band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "crash band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "tom band=9.00 seg=11.00 shape_score=8.20 trigger=1.80/1.40 shape=1 level=0.92 | "
            "ride band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "rim band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "transient=1.80 onset=1.20 energy=0.46/0.50/0.04 "
            "body=6.00/2.00/9.00 crack=0.40 upper_tom=4.00 body_shape=4 rule_flags=0x12 merged_expected=1]",
            "analyzer_drum_samples: debug 100ms tom/001.wav expected tom "
            "(kick=0.96* snare=0.00 hihat=0.00 crash=0.00 tom=0.71* ride=0.00 rim=0.00) "
            "[kick band=4.00 seg=5.00 shape_score=6.00 trigger=1.60/0.60 shape=1 level=0.96 | "
            "snare band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "crash band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "tom band=8.00 seg=10.00 shape_score=7.20 trigger=1.10/1.40 shape=1 level=0.71 | "
            "ride band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "rim band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "transient=2.10 onset=1.70 energy=0.58/0.32/0.10 "
            "body=4.00/2.00/8.00 crack=0.50 upper_tom=3.00 body_shape=4 rule_flags=0x13 merged_expected=1]",
            "analyzer_drum_samples: primary miss 100ms tom/002.wav expected tom got ambiguous "
            "(kick=0.80* snare=0.00 hihat=0.00 crash=0.00 tom=0.80* ride=0.00 rim=0.00) "
            "[kick band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/0.60 shape=1 level=0.80 | "
            "tom band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/0.60 shape=1 level=0.80 | "
            "transient=2.00 onset=1.50 energy=0.33/0.33/0.34 "
            "body=2.00/2.00/2.00 crack=0.25 upper_tom=1.00 body_shape=4]",
            "analyzer_drum_samples: debug 100ms tom/ok.wav expected tom "
            "(kick=0.10 snare=0.00 hihat=0.00 crash=0.00 tom=0.95* ride=0.00 rim=0.00) "
            "[kick band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.10 | "
            "snare band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "crash band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "tom band=3.00 seg=3.00 shape_score=3.00 trigger=2.00/1.00 shape=1 level=0.95 | "
            "ride band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "rim band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "transient=2.00 onset=1.50 energy=0.20/0.70/0.10 "
            "body=1.00/1.00/3.00 crack=0.10 upper_tom=1.00 body_shape=4]",
            "analyzer_drum_samples: debug 100ms tom/accepted_by_analyzer.wav expected tom "
            "(kick=0.99* snare=0.00 hihat=0.00 crash=0.00 tom=0.80* ride=0.00 rim=0.00) "
            "[kick band=3.00 seg=3.00 shape_score=3.00 trigger=2.00/1.00 shape=1 level=0.99 | "
            "snare band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "hihat band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "crash band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "tom band=3.00 seg=3.00 shape_score=3.00 trigger=2.00/1.00 shape=1 level=0.80 | "
            "ride band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "rim band=1.00 seg=1.00 shape_score=1.00 trigger=0.20/1.40 shape=0 level=0.00 | "
            "transient=2.00 onset=1.50 energy=0.40/0.50/0.10 "
            "body=3.00/1.00/3.00 crack=0.10 upper_tom=1.00 body_shape=4]",
            "analyzer_drum_samples: primary miss 100ms snare/zero-denom.wav expected snare got tom "
            "(kick=0.00 snare=0.60* hihat=0.00 crash=0.00 tom=0.90* ride=0.00 rim=0.00) "
            "[snare band=2.00 seg=2.00 shape_score=2.00 trigger=1.00/1.00 shape=1 level=0.60 | "
            "tom band=0.00 seg=0.00 shape_score=0.00 trigger=0.00/0.00 shape=1 level=0.90 | "
            "transient=2.00 onset=1.50 energy=0.20/0.70/0.10 "
            "body=1.00/2.00/0.00 crack=0.10 upper_tom=0.00 body_shape=2]",
        ]
    )
    output = run_analysis(log_text)
    dumped = run_dump(log_text)
    dumped_with_correct = run_dump(log_text, include_debug_rows=True)
    dumped_with_merged = run_dump(log_text, include_merged_debug_rows=True)
    require(output, "overall primary misses")
    require(output, "expected snare: tom=1")
    require(output, "expected tom: ambiguous=1 kick=1")
    require(output, "drum: 3 primary misses")
    require(output, "tom -> ambiguous: 1")
    require(output, "tom -> kick: 1")
    require(output, "snare -> tom: 1")
    require(output, "examples: tom/001.wav")
    require(output, "band        expected/got avg=2.00")
    require(output, "expected shape supported: 1/1")
    require(output, "expected active but lower: 1/1")
    require(output, "avg energy low/mid/high=0.58/0.32/0.10")
    require(output, "tom/snare body: avg=4.00")
    require(output, "body_shape: 4=1")
    require(output, "near-level ties: 0/1")
    require(dumped, "sample\texpected\tgot\tenergy_low\tenergy_mid\tenergy_high\tkick_body")
    require(dumped, "\trule_flags\tflag_generated_gm_source\tflag_one_shot_source")
    require(dumped, "\tmerged_expected\n")
    require(dumped, "tom/001.wav\ttom\tkick\t0.580000\t0.320000\t0.100000\t4.000000\t2.000000\t8.000000")
    require(dumped, "\t0x13\t1\t1\t0\t0\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1\n")
    require(dumped, "tom/002.wav\ttom\tambiguous\t0.330000\t0.330000\t0.340000")
    require(dumped_with_correct, "tom/ok.wav\ttom\ttom\t0.200000\t0.700000\t0.100000\t1.000000\t1.000000\t3.000000")
    require(
        dumped_with_correct,
        "tom/accepted_by_analyzer.wav\ttom\ttom\t0.400000\t0.500000\t0.100000\t3.000000\t1.000000\t3.000000",
    )
    dumped_rows = {row["sample"]: row for row in tsv_rows(dumped)}
    if dumped_rows["tom/001.wav"]["merged_expected"] != "1":
        raise AssertionError(f"expected tom/001.wav merged_expected=1:\n{dumped}")
    if dumped_rows["tom/002.wav"]["merged_expected"] != "0":
        raise AssertionError(f"expected tom/002.wav merged_expected=0:\n{dumped}")
    dumped_with_correct_rows = {row["sample"]: row for row in tsv_rows(dumped_with_correct)}
    if dumped_with_correct_rows["tom/ok.wav"]["merged_expected"] != "0":
        raise AssertionError(f"expected tom/ok.wav merged_expected=0:\n{dumped_with_correct}")
    if dumped_with_correct_rows["tom/accepted_by_analyzer.wav"]["got"] != "tom":
        raise AssertionError(f"expected debug-only primary hit to keep analyzer expected label:\n{dumped_with_correct}")
    if dumped_with_correct.count("tom/001.wav\ttom\tkick") != 1:
        raise AssertionError(f"expected primary miss sample to be dumped once:\n{dumped_with_correct}")
    if "tom/001.wav#merged" in dumped_with_correct:
        raise AssertionError(f"merged debug rows must be opt-in:\n{dumped_with_correct}")
    require(
        dumped_with_merged,
        "tom/001.wav#merged\ttom\ttom\t0.460000\t0.500000\t0.040000\t6.000000\t2.000000\t9.000000",
    )
    dumped_with_merged_rows = {row["sample"]: row for row in tsv_rows(dumped_with_merged)}
    if dumped_with_merged_rows["tom/001.wav#merged"]["merged_expected"] != "1":
        raise AssertionError(f"expected merged frame row to preserve merged_expected=1:\n{dumped_with_merged}")
    if "100000" in output:
        raise AssertionError(f"expected zero-denominator ratios to be skipped:\n{output}")
    print("test_analyze_drum_primary_debug: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
