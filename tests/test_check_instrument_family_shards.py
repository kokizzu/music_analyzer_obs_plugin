#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_instrument_family_shards.py"


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


def summary(
    *,
    usable: int,
    guitar: tuple[int, int],
    piano: tuple[int, int],
    vocals: tuple[int, int],
    other: tuple[int, int],
) -> str:
    return (
        "analyzer_instrument_family_samples: 9 checks passed "
        f"(usable {usable}, guitar {guitar[0]}/{guitar[1]}, piano {piano[0]}/{piano[1]}, "
        f"vocals {vocals[0]}/{vocals[1]}, other {other[0]}/{other[1]}; "
        "cross rows guitar/piano/vocals/other guitar piano=0 vocals=0 other=1; "
        "piano guitar=0 vocals=0 other=0; vocals guitar=0 piano=0 other=0; "
        "other guitar=1 piano=0 vocals=0)\n"
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        shard_a = write_log(
            root,
            "a.out",
            summary(
                usable=4,
                guitar=(2, 2),
                piano=(1, 2),
                vocals=(0, 0),
                other=(1, 1),
            ),
        )
        shard_b = write_log(
            root,
            "b.out",
            summary(
                usable=4,
                guitar=(1, 2),
                piano=(2, 2),
                vocals=(1, 1),
                other=(1, 1),
            ),
        )
        result = run_checker(
            "--min-samples",
            "8",
            "--min-recall-percent",
            "50",
            str(shard_a),
            str(shard_b),
        )
        assert result.returncode == 0, result.stderr
        assert "check_instrument_family_shards: ok" in result.stdout
        assert "usable 8" in result.stdout
        assert "guitar 3/4" in result.stdout
        assert "piano 3/4" in result.stdout

        recall_result = run_checker(
            "--min-samples",
            "8",
            "--min-recall-percent",
            "80",
            str(shard_a),
            str(shard_b),
        )
        assert recall_result.returncode == 1
        assert "expected guitar recall >= 80%" in recall_result.stderr

        sample_result = run_checker(
            "--min-samples",
            "9",
            "--min-recall-percent",
            "50",
            str(shard_a),
            str(shard_b),
        )
        assert sample_result.returncode == 1
        assert "expected at least 9 usable samples" in sample_result.stderr

        malformed = write_log(root, "bad.out", "analyzer_instrument_family_samples: nope\n")
        malformed_result = run_checker(
            "--min-samples",
            "1",
            "--min-recall-percent",
            "1",
            str(malformed),
        )
        assert malformed_result.returncode == 1
        assert "missing analyzer_instrument_family_samples pass summary line" in malformed_result.stderr

    print("test_check_instrument_family_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
