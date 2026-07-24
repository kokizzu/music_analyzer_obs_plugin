#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_drum_attribute_patterns.py"


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
    *paths: pathlib.Path, include_merged_rows: bool = False, row_examples: int = 1
) -> str:
    command = [
        sys.executable,
        str(SCRIPT),
        *(str(path) for path in paths),
        "--route",
        "tom->kick",
        "--min-positive-samples",
        "2",
        "--max-negative-samples",
        "0",
        "--max-conditions",
        "3",
        "--row-examples",
        str(row_examples),
    ]
    if include_merged_rows:
        command.append("--include-merged-rows")
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
        tsv_output_with_merged = run_patterns(tsv_path, include_merged_rows=True)

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

    assert "route tom->kick positives=2 rows=2 protected_correct=3 rows=3" in output
    assert "ignored merged expected-credit rows=1" in output
    assert "protected_by_expected=kick=1 snare=1 tom=1" in output
    assert "+2 rows=2 -0 rows=0" in output
    assert "foreign=1 rows=1 new-active=1 rows=1" in output
    assert "primary-break=1 rows=1" in output
    assert "tom/001.wav tom->kick" in output
    assert "snare/miss.wav snare->kick" in output
    assert "route tom->kick positives=2 rows=2 protected_correct=3 rows=3" in tsv_output
    assert "ignored merged expected-credit rows=1" in tsv_output
    assert "protected_by_expected=kick=1 snare=1 tom=1" in tsv_output
    assert "+2 rows=2 -0 rows=0" in tsv_output
    assert "foreign=1 rows=1 new-active=1 rows=1" in tsv_output
    assert "primary-break=1 rows=1" in tsv_output
    assert "tom/001.wav tom->kick" in tsv_output
    assert "snare/miss.wav snare->kick" in tsv_output
    assert "route tom->kick positives=3 rows=3 protected_correct=3 rows=3" in tsv_output_with_merged
    assert "route tom->kick positives=3 rows=3 protected_correct=4 rows=4" in multi_tsv_output
    assert "drum:tom/001.wav tom->kick" in multi_tsv_output
    assert "drum_second:tom/001.wav tom->kick" in multi_tsv_output
    print("test_find_drum_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
