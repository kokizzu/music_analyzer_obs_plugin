#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_drum_attribute_patterns.py"
sys.path.insert(0, str(ROOT / "scripts"))

import find_drum_attribute_patterns as patterns


def details(
    *,
    kick_level: float,
    snare_level: float,
    tom_level: float,
    low: float = 0.40,
    mid: float = 0.50,
    high: float = 0.10,
    body_shape: int = 4,
) -> str:
    return (
        "kick band=1.00 seg=1.00 shape_score=1.00 trigger=2.00/1.00 "
        f"shape=1 level={kick_level:.2f} | "
        "snare band=1.00 seg=1.00 shape_score=1.00 trigger=2.00/1.00 "
        f"shape=1 level={snare_level:.2f} | "
        "hihat band=0.20 seg=0.20 shape_score=0.20 trigger=0.20/1.40 shape=0 level=0.00 | "
        "crash band=0.20 seg=0.20 shape_score=0.20 trigger=0.20/1.40 shape=0 level=0.00 | "
        "tom band=1.00 seg=1.00 shape_score=1.00 trigger=2.00/1.00 "
        f"shape=1 level={tom_level:.2f} | "
        "ride band=0.20 seg=0.20 shape_score=0.20 trigger=0.20/1.40 shape=0 level=0.00 | "
        "rim band=0.20 seg=0.20 shape_score=0.20 trigger=0.20/1.40 shape=0 level=0.00 | "
        f"transient=5.00 onset=5.00 energy={low:.2f}/{mid:.2f}/{high:.2f} "
        f"body=0.60/0.50/1.40 crack=0.02 upper_tom=0.30 body_shape={body_shape}"
    )


def row(sample: str, expected: str, detail_text: str, *, merged_expected: bool = False) -> str:
    merged = " merged_expected=1" if merged_expected else " merged_expected=0"
    return (
        f"analyzer_drum_samples: debug 100ms {sample} expected {expected} "
        f"({detail_text}) [{detail_text}{merged}]"
    )


def tsv_header() -> list[str]:
    fields = [
        "sample",
        "expected",
        "got",
        "energy_low",
        "energy_mid",
        "energy_high",
        "kick_body",
        "snare_body",
        "tom_body",
        "snare_crack",
        "upper_tom_body",
        "body_shape",
    ]
    for drum in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim"):
        for field in ("band", "seg", "shape_score", "trigger", "threshold", "shape", "level"):
            fields.append(f"{drum}_{field}")
    fields.append("merged_expected")
    return fields


def tsv_row(
    sample: str,
    expected: str,
    got: str,
    *,
    kick_level: float,
    snare_level: float,
    tom_level: float,
    high: float = 0.10,
    merged_expected: bool = False,
) -> str:
    values: dict[str, str] = {
        "sample": sample,
        "expected": expected,
        "got": got,
        "energy_low": "0.40",
        "energy_mid": "0.50",
        "energy_high": f"{high:.2f}",
        "kick_body": "0.60",
        "snare_body": "0.50",
        "tom_body": "1.40",
        "snare_crack": "0.02",
        "upper_tom_body": "0.30",
        "body_shape": "4",
        "merged_expected": "1" if merged_expected else "0",
    }
    for drum, level in (
        ("kick", kick_level),
        ("snare", snare_level),
        ("tom", tom_level),
        ("hihat", 0.0),
        ("crash", 0.0),
        ("ride", 0.0),
        ("rim", 0.0),
    ):
        values[f"{drum}_band"] = "1.00" if drum in {"kick", "snare", "tom"} else "0.20"
        values[f"{drum}_seg"] = values[f"{drum}_band"]
        values[f"{drum}_shape_score"] = values[f"{drum}_band"]
        values[f"{drum}_trigger"] = "2.00" if drum in {"kick", "snare", "tom"} else "0.20"
        values[f"{drum}_threshold"] = "1.00" if drum in {"kick", "snare", "tom"} else "1.40"
        values[f"{drum}_shape"] = "1" if drum in {"kick", "snare", "tom"} else "0"
        values[f"{drum}_level"] = f"{level:.2f}"
    return "\t".join(values[field] for field in tsv_header())


def run_patterns(
    *paths: pathlib.Path, include_merged_rows: bool = False, row_examples: int = 1,
    max_conditions: int = 3, route_name: str = "tom->kick", show_near_misses: int = 0,
    min_route_positive_samples: int = 0, min_route_positive_rows: int = 0,
    use_top_routes: bool = False, top_routes: int = 5, jobs: int = 1,
    profile_fields: int = 0, max_new_active_samples: int | None = None,
    max_primary_break_samples: int | None = None,
    require_positive_sources: tuple[str, ...] = (),
) -> str:
    command = [
        sys.executable,
        str(SCRIPT),
        *(str(path) for path in paths),
        "--min-positive-samples",
        "2",
        "--max-negative-samples",
        "0",
        "--max-conditions",
        str(max_conditions),
        "--row-examples",
        str(row_examples),
        "--jobs",
        str(jobs),
    ]
    if use_top_routes:
        command.extend(["--top-routes", str(top_routes)])
    else:
        command.extend(["--route", route_name])
    if min_route_positive_samples > 0:
        command.extend(["--min-route-positive-samples", str(min_route_positive_samples)])
    if min_route_positive_rows > 0:
        command.extend(["--min-route-positive-rows", str(min_route_positive_rows)])
    if show_near_misses > 0:
        command.extend(["--show-near-misses", str(show_near_misses)])
    if profile_fields > 0:
        command.extend(["--profile-fields", str(profile_fields)])
    if max_new_active_samples is not None:
        command.extend(["--max-new-active-samples", str(max_new_active_samples)])
    if max_primary_break_samples is not None:
        command.extend(["--max-primary-break-samples", str(max_primary_break_samples)])
    if include_merged_rows:
        command.append("--include-merged-rows")
    for source in require_positive_sources:
        command.extend(["--require-positive-source", source])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def main() -> int:
    assert not patterns.constraints_compatible(
        (patterns.numeric_pattern("tom_level", "<=", 0.8).constraint,),
        patterns.numeric_pattern("tom_level", ">=", 0.8).constraint,
    )
    assert patterns.constraints_compatible(
        (patterns.numeric_pattern("tom_level", ">=", 0.7).constraint,),
        patterns.numeric_pattern("tom_level", "<=", 0.9).constraint,
    )
    assert not patterns.constraints_compatible(
        (patterns.numeric_pattern("snare_trigger", "<=", 1.0).constraint,),
        patterns.numeric_pattern("snare_trigger", "<=", 2.0).constraint,
    )
    assert not patterns.constraints_compatible(
        (patterns.category_pattern("body_shape", "2").constraint,),
        patterns.category_pattern("body_shape", "4").constraint,
    )
    field_list = patterns.numeric_fields(
        [
            {
                "sample": "hihat/alias.wav",
                "expected": "hihat",
                "hihat_seg": "12.0",
                "hihat_shape_score": "12.0",
                "crash_hihat_seg_ratio": "0.80",
                "crash_hihat_shape_score_ratio": "0.80",
                "rim_shape_score": "4.0",
                "hihat_rim_shape_score_ratio": "3.0",
            }
        ]
    )
    assert "hihat_seg" in field_list
    assert "crash_hihat_seg_ratio" in field_list
    assert "rim_shape_score" in field_list
    assert "hihat_rim_shape_score_ratio" in field_list
    assert "hihat_shape_score" not in field_list
    assert "crash_hihat_shape_score_ratio" not in field_list

    rows = [
        row("tom/001.wav", "tom", details(kick_level=0.90, snare_level=0.10, tom_level=0.60)),
        row("tom/002.wav", "tom", details(kick_level=0.88, snare_level=0.10, tom_level=0.58)),
        row(
            "tom/merged.wav",
            "tom",
            details(kick_level=0.91, snare_level=0.10, tom_level=0.59),
            merged_expected=True,
        ),
        row("snare/miss.wav", "snare", details(kick_level=0.88, snare_level=0.10, tom_level=0.20)),
        row("tom/ok.wav", "tom", details(kick_level=0.50, snare_level=0.10, tom_level=0.95, high=0.50)),
        row("kick/ok.wav", "kick", details(kick_level=0.95, snare_level=0.10, tom_level=0.20, high=0.50)),
        row("snare/ok.wav", "snare", details(kick_level=0.10, snare_level=0.95, tom_level=0.20, high=0.50)),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "drum.err"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        output = run_patterns(path)

        tsv_path = pathlib.Path(tmpdir) / "drum.tsv"
        tsv_path.write_text(
            "\n".join(
                [
                    "\t".join(tsv_header()),
                    tsv_row("tom/001.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.60),
                    tsv_row("tom/002.wav", "tom", "kick", kick_level=0.88, snare_level=0.10, tom_level=0.58),
                    tsv_row(
                        "tom/merged.wav",
                        "tom",
                        "kick",
                        kick_level=0.91,
                        snare_level=0.10,
                        tom_level=0.59,
                        merged_expected=True,
                    ),
                    tsv_row("snare/miss.wav", "snare", "kick", kick_level=0.88, snare_level=0.10, tom_level=0.20),
                    tsv_row("tom/ok.wav", "tom", "tom", kick_level=0.50, snare_level=0.10, tom_level=0.95, high=0.50),
                    tsv_row("kick/ok.wav", "kick", "kick", kick_level=0.95, snare_level=0.10, tom_level=0.20, high=0.50),
                    tsv_row("snare/ok.wav", "snare", "snare", kick_level=0.10, snare_level=0.95, tom_level=0.20, high=0.50),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        tsv_output = run_patterns(tsv_path)
        tsv_profile_output = run_patterns(tsv_path, row_examples=0, profile_fields=3)
        tsv_output_one_condition = run_patterns(tsv_path, max_conditions=1)
        tsv_output_with_merged = run_patterns(tsv_path, include_merged_rows=True)

        unsafe_side_effect_path = pathlib.Path(tmpdir) / "unsafe_side_effect.tsv"
        unsafe_side_effect_path.write_text(
            "\n".join(
                [
                    "\t".join(tsv_header()),
                    tsv_row("tom/001.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.20),
                    tsv_row("tom/002.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.20),
                    tsv_row("snare/miss.wav", "snare", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.20),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        unsafe_side_effect_output = run_patterns(
            unsafe_side_effect_path,
            row_examples=0,
            show_near_misses=1,
            max_new_active_samples=0,
            max_primary_break_samples=0,
        )

        tsv_path_2 = pathlib.Path(tmpdir) / "drum_second.tsv"
        tsv_path_2.write_text(
            "\n".join(
                [
                    "\t".join(tsv_header()),
                    tsv_row("tom/001.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.60),
                    tsv_row("kick/ok.wav", "kick", "kick", kick_level=0.95, snare_level=0.10, tom_level=0.20),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        multi_tsv_output = run_patterns(tsv_path, tsv_path_2, row_examples=4)
        multi_source_required_output = run_patterns(
            tsv_path,
            tsv_path_2,
            row_examples=0,
            require_positive_sources=("drum", "drum_second"),
        )
        zero_denominator_path = pathlib.Path(tmpdir) / "zero_denominator.tsv"
        zero_denominator_path.write_text(
            "\n".join(
                [
                    "\t".join(tsv_header()),
                    tsv_row("tom/zero_1.wav", "tom", "snare", kick_level=0.0, snare_level=0.90, tom_level=0.60),
                    tsv_row("tom/zero_2.wav", "tom", "snare", kick_level=0.0, snare_level=0.88, tom_level=0.58),
                    tsv_row("tom/ok.wav", "tom", "tom", kick_level=0.0, snare_level=0.10, tom_level=0.95),
                    tsv_row("snare/ok.wav", "snare", "snare", kick_level=0.0, snare_level=0.95, tom_level=0.20),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        zero_denominator_output = run_patterns(zero_denominator_path, route_name="tom->snare")
        near_miss_path = pathlib.Path(tmpdir) / "near_miss.tsv"
        near_miss_path.write_text(
            "\n".join(
                [
                    "\t".join(tsv_header()),
                    tsv_row("tom/near_1.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.60),
                    tsv_row("tom/near_2.wav", "tom", "kick", kick_level=0.90, snare_level=0.10, tom_level=0.60),
                    tsv_row("tom/protected.wav", "tom", "tom", kick_level=0.90, snare_level=0.10, tom_level=0.60),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        near_miss_output = run_patterns(near_miss_path, row_examples=0, show_near_misses=2)
        skipped_route_output = run_patterns(
            near_miss_path,
            row_examples=0,
            min_route_positive_samples=3,
        )
        top_route_filtered_output = run_patterns(
            near_miss_path,
            row_examples=0,
            use_top_routes=True,
            top_routes=4,
            min_route_positive_samples=2,
        )
        top_route_empty_output = run_patterns(
            near_miss_path,
            row_examples=0,
            use_top_routes=True,
            top_routes=4,
            min_route_positive_samples=10,
        )
        serial_top_routes_output = run_patterns(
            tsv_path,
            row_examples=0,
            use_top_routes=True,
            top_routes=4,
        )
        parallel_top_routes_output = run_patterns(
            tsv_path,
            row_examples=0,
            use_top_routes=True,
            top_routes=4,
            jobs=2,
        )

    assert "route tom->kick positives=2 rows=2 protected_correct=4 rows=4" in output
    assert "protecting merged expected-credit rows=1; pass --include-merged-rows to mine them" in output
    assert "protected_by_expected=kick=1 snare=1 tom=2" in output
    assert "+2 rows=2 -0 rows=0" in output
    assert "foreign=1 rows=1 new-active=1 rows=1" in output
    assert "primary-break=1 rows=1" in output
    assert "tom/001.wav tom->kick" in output
    assert "snare/miss.wav snare->kick" in output
    assert "route tom->kick positives=2 rows=2 protected_correct=4 rows=4" in tsv_output
    assert "protecting merged expected-credit rows=1; pass --include-merged-rows to mine them" in tsv_output
    assert "protected_by_expected=kick=1 snare=1 tom=2" in tsv_output
    assert "numeric attribute profile:" in tsv_profile_output
    assert "tom_level" in tsv_profile_output
    assert "pos=0.59 [0.58..0.6]" in tsv_profile_output
    assert "category attribute profile:" in tsv_profile_output
    assert "body_shape=4 enrich=0.000 pos=2/2 protected=4/4" in tsv_profile_output
    assert "route tom->kick positives=2 rows=2 protected_correct=0 rows=0" in unsafe_side_effect_output
    assert "\n  --\n" in unsafe_side_effect_output
    assert "nearest over-budget single-condition candidate rules:" in unsafe_side_effect_output
    assert "new-active=1 rows=1" in unsafe_side_effect_output
    assert "primary-break=1 rows=1" in unsafe_side_effect_output
    assert "side_rows=3 net_rows=-1 gain_per_side=0.67" in unsafe_side_effect_output
    assert "+2 rows=2 -0 rows=0" in tsv_output
    assert "route tom->kick positives=2 rows=2 protected_correct=4 rows=4" in tsv_output_one_condition
    assert "\n  --\n" in tsv_output_one_condition
    assert " AND " not in tsv_output_one_condition
    assert "foreign=1 rows=1 new-active=1 rows=1" in tsv_output
    assert "primary-break=1 rows=1" in tsv_output
    assert "side_rows=3 net_rows=-1 gain_per_side=0.67" in tsv_output
    assert "tom/001.wav tom->kick" in tsv_output
    assert "snare/miss.wav snare->kick" in tsv_output
    assert "route tom->kick positives=3 rows=3 protected_correct=3 rows=3" in tsv_output_with_merged
    assert "route tom->kick positives=3 rows=3 protected_correct=5 rows=5" in multi_tsv_output
    assert "drum:tom/001.wav tom->kick" in multi_tsv_output
    assert "drum_second:tom/001.wav tom->kick" in multi_tsv_output
    assert "sources=drum,drum_second" in multi_source_required_output
    assert "route tom->snare positives=2 rows=2" in zero_denominator_output
    assert "1000000000" not in zero_denominator_output
    assert "snare_kick_level_ratio" not in zero_denominator_output
    assert "route tom->kick positives=2 rows=2 protected_correct=1 rows=1" in near_miss_output
    assert "\n  --\n" in near_miss_output
    assert "nearest over-budget single-condition candidate rules:" in near_miss_output
    assert "+2 rows=2 -1 rows=1" in near_miss_output
    assert "side_rows=1 net_rows=1 gain_per_side=2.00" in near_miss_output
    assert (
        "route tom->kick skipped: positives=2 rows=2 "
        "below min-route-positive-samples=3 min-route-positive-rows=0"
    ) in skipped_route_output
    assert "route tom->kick positives=" not in skipped_route_output
    assert "route tom->kick" in top_route_filtered_output
    assert "no routes matched the route-level positive thresholds" in top_route_empty_output
    assert parallel_top_routes_output == serial_top_routes_output
    print("test_find_drum_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
