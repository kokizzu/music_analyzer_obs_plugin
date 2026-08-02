#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_egmd_shards.py"


def write_log(directory: pathlib.Path, name: str, body: str) -> pathlib.Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        shard_a = write_log(
            root,
            "a.out",
            "analyzer_egmd: 6 checks passed (recordings 2/4, windows 8, read failures 0, "
            "no-candidate recordings 0, unusable 0, drum hits 12/16, drum precision 75.00%, "
            "drum recall 75.00%, F1 75.00%, false-positive windows 25.00% (2/8), "
            "recall by category kick:4/4-0/snare:2/4-2, fp by category kick:1/snare:3, "
            "tp/fp/fn 12/4/4, hits min/avg/max 1/2.00/3, categories min/avg/max 1/2.00/3)\n",
        )
        shard_b = write_log(
            root,
            "b.out",
            "analyzer_egmd: 6 checks passed (recordings 2/4, windows 8, read failures 0, "
            "no-candidate recordings 0, unusable 0, drum hits 13/16, drum precision 81.25%, "
            "drum recall 81.25%, F1 81.25%, false-positive windows 12.50% (1/8), "
            "recall by category kick:5/5-0/snare:3/4-1, fp by category kick:2/snare:1, "
            "tp/fp/fn 13/3/3, hits min/avg/max 1/2.00/3, categories min/avg/max 1/2.00/3)\n",
        )

        result = run_checker(
            "--min-recordings",
            "4",
            "--min-windows",
            "16",
            "--min-recall-percent",
            "75",
            "--min-precision-percent",
            "75",
            "--max-false-positive-windows-percent",
            "20",
            str(shard_a),
            str(shard_b),
        )
        assert result.returncode == 0, result.stderr
        assert "check_egmd_shards: ok" in result.stdout
        assert "recordings 4/4" in result.stdout
        assert "drum hits 25/32" in result.stdout

        fail_result = run_checker(
            "--min-recordings",
            "4",
            "--min-windows",
            "16",
            "--min-recall-percent",
            "80",
            "--min-precision-percent",
            "75",
            "--max-false-positive-windows-percent",
            "20",
            str(shard_a),
            str(shard_b),
        )
        assert fail_result.returncode == 1
        assert "expected drum-category recall >= 80%" in fail_result.stderr

        bad = write_log(root, "bad.out", "analyzer_egmd: 1 checks passed (recordings 1/1)\n")
        bad_result = run_checker(
            "--min-recordings",
            "1",
            "--min-windows",
            "1",
            "--min-recall-percent",
            "1",
            "--min-precision-percent",
            "1",
            "--max-false-positive-windows-percent",
            "100",
            str(bad),
        )
        assert bad_result.returncode == 1
        assert "missing analyzer_egmd summary line" in bad_result.stderr

    print("test_check_egmd_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
