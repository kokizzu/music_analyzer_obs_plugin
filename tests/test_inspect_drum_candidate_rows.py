#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_drum_candidate_rows.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    header = [
        "sample",
        "expected",
        "got",
        "crash_level",
        "hihat_level",
        "rim_band",
        "snare_band",
        "energy_high",
    ]
    rows = [
        ["hihat/a.wav", "hihat", "hihat", "0.90", "0.92", "4.00", "2.00", "0.70"],
        ["hihat/b.wav", "hihat", "hihat", "0.40", "0.88", "2.00", "1.00", "0.50"],
        ["crash/a.wav", "crash", "crash", "0.95", "0.10", "5.00", "1.50", "0.80"],
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / "rows.tsv"
        path.write_text(
            "\n".join(["\t".join(header)] + ["\t".join(row) for row in rows]) + "\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--condition",
                "crash_level>0.50",
                "--condition",
                "hihat_level>0.30",
                "--condition",
                "rim_band>=3.00",
                "--condition",
                "snare_band<=2.50",
                "--field",
                "crash_level",
                "--field",
                "energy_high",
                str(path),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "rows=3 selected=1")
    require(output, "expected={'hihat': 1}")
    require(output, "got={'hihat': 1}")
    require(output, "crash_level: min=0.900 med=0.900 max=0.900")
    require(output, "energy_high: min=0.700 med=0.700 max=0.700")
    require(output, "example hihat/a.wav expected=hihat got=hihat")
    print("test_inspect_drum_candidate_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
