#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_real_note_sample_shards.py"


SHARD_0 = """
analyzer_real_note_samples: 143 checks passed (usable 6, bass 2/2, guitar 1/1, piano 1/1, vocals 1/1, other 1/1)
""".strip()

SHARD_1 = """
analyzer_real_note_samples: 2 tolerated failures within limit 999999 (usable 5, bass 1/2, guitar 2/2, piano 0/0, vocals 1/1, other 0/0)
""".strip()


def run_checker(*extra: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []
        for index, text in enumerate([SHARD_0, SHARD_1]):
            path = pathlib.Path(tmpdir) / f"shard-{index}.out"
            path.write_text(text, encoding="utf-8")
            paths.append(path)
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--min-bass",
                "4",
                "--min-guitar",
                "3",
                "--min-piano",
                "1",
                "--min-vocals",
                "2",
                "--min-other",
                "1",
                "--max-failures",
                "2",
                *extra,
                *[str(path) for path in paths],
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    completed = run_checker()
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    require(
        completed.stdout,
        "check_real_note_sample_shards: ok (usable 11, failures 2/2, "
        "bass 3/4, guitar 3/3, piano 1/1, vocals 2/2, other 1/1)",
    )

    failed_family = run_checker("--min-guitar", "4")
    if failed_family.returncode == 0:
        raise AssertionError("expected checker to fail the guitar sample minimum")
    require(failed_family.stderr, "expected at least 4 guitar real note samples, got 3")

    failed_budget = run_checker("--max-failures", "1")
    if failed_budget.returncode == 0:
        raise AssertionError("expected checker to fail the aggregate failure budget")
    require(failed_budget.stderr, "expected isolated real-note failures <= 1, got 2")

    print("test_check_real_note_sample_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
