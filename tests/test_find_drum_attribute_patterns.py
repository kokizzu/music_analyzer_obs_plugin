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


def row(sample: str, expected: str, detail_text: str) -> str:
    return f"analyzer_drum_samples: debug 100ms {sample} expected {expected} ({detail_text}) [{detail_text}]"


def main() -> int:
    rows = [
        row("tom/001.wav", "tom", details(kick_level=0.90, snare_level=0.10, tom_level=0.60)),
        row("tom/002.wav", "tom", details(kick_level=0.88, snare_level=0.10, tom_level=0.58)),
        row("tom/ok.wav", "tom", details(kick_level=0.50, snare_level=0.10, tom_level=0.95)),
        row("kick/ok.wav", "kick", details(kick_level=0.95, snare_level=0.10, tom_level=0.20)),
        row("snare/ok.wav", "snare", details(kick_level=0.10, snare_level=0.95, tom_level=0.20)),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "drum.err"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--route",
                "tom->kick",
                "--min-positive-samples",
                "2",
                "--max-negative-samples",
                "0",
                "--max-conditions",
                "3",
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
    assert "route tom->kick positives=2 rows=2 protected_correct=3 rows=3" in output
    assert "protected_by_expected=kick=1 snare=1 tom=1" in output
    assert "+2 rows=2 -0 rows=0" in output
    assert "tom/001.wav tom->kick" in output
    print("test_find_drum_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
