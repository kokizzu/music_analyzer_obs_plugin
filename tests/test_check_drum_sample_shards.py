#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_drum_sample_shards.py"


LOG_TEXT = """
analyzer_drum_samples: active matrix
  expected kick  kick=3 snare=1 hihat=0 crash=0 tom=1 ride=0 rim=0
  expected snare kick=1 snare=4 hihat=0 crash=0 tom=1 ride=0 rim=0
  expected hihat kick=0 snare=0 hihat=3 crash=1 tom=0 ride=1 rim=0
  expected crash kick=0 snare=0 hihat=1 crash=3 tom=0 ride=1 rim=0
  expected tom   kick=1 snare=2 hihat=0 crash=0 tom=4 ride=0 rim=0
  expected ride  kick=0 snare=0 hihat=1 crash=1 tom=0 ride=3 rim=0
  expected rim   kick=0 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=3
analyzer_drum_samples: primary matrix
  expected kick  kick=3 snare=0 hihat=0 crash=0 tom=0 ride=0 rim=0 ambiguous=0 none=0
  expected snare kick=0 snare=4 hihat=0 crash=0 tom=1 ride=0 rim=0 ambiguous=0 none=0
  expected hihat kick=0 snare=0 hihat=3 crash=0 tom=0 ride=0 rim=0 ambiguous=0 none=0
  expected crash kick=0 snare=0 hihat=0 crash=3 tom=0 ride=0 rim=0 ambiguous=0 none=0
  expected tom   kick=0 snare=1 hihat=0 crash=0 tom=4 ride=0 rim=0 ambiguous=0 none=0
  expected ride  kick=0 snare=0 hihat=0 crash=0 tom=0 ride=3 rim=0 ambiguous=0 none=0
  expected rim   kick=0 snare=0 hihat=0 crash=0 tom=0 ride=0 rim=3 ambiguous=0 none=0
analyzer_drum_samples: ok (usable 30, skipped 2)
""".strip()


def run_checker(*extra: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        log = pathlib.Path(tmpdir) / "shard.out"
        log.write_text(LOG_TEXT, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--min-recall-percent",
                "50",
                "--min-primary-recall-percent",
                "50",
                "--min-precision-percent",
                "20",
                "--max-false-percent",
                "80",
                *extra,
                str(log),
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
    require(completed.stdout, "check_drum_sample_shards: active matrix")
    require(completed.stdout, "expected snare kick=1 snare=4")
    require(completed.stdout, "check_drum_sample_shards: primary confusion snare->tom=1 tom->snare=1")
    require(completed.stdout, "check_drum_sample_shards: ok (usable 25, skipped 2")
    require(completed.stdout, "snare recall 4/5 primary 4/5 precision 4/8 false 4 50%")

    failed = run_checker("--snare-min-primary-recall-percent", "90")
    if failed.returncode == 0:
        raise AssertionError("expected shard checker to fail the snare primary threshold")
    require(failed.stderr, "expected 100ms snare primary recall >= 90%, got 80% (4/5)")

    subset = run_checker("--categories", "kick,snare,hihat")
    if subset.returncode != 0:
        raise AssertionError(subset.stderr)
    require(subset.stdout, "check_drum_sample_shards: ok (usable 25, skipped 2")
    require(subset.stdout, "hihat recall 3/3 primary 3/3")
    if "tom recall" in subset.stdout:
        raise AssertionError(f"subset checker should not summarize omitted categories:\n{subset.stdout}")

    unknown = run_checker("--categories", "kick,clap")
    if unknown.returncode == 0:
        raise AssertionError("expected shard checker to reject unknown categories")
    require(unknown.stderr, "unknown categories: clap")

    print("test_check_drum_sample_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
