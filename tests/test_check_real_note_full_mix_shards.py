#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_real_note_full_mix_shards.py"


LOG_TEXT = """
analyzer_real_note_samples full-mix: 572 checks passed (usable 10, bass 2/2, guitar 2/2, piano 2/2, vocals 2/2, other 2/2; any-row 10/10, expected-row 9/10, first-row 5/10, drum-active-windows 1/40, expected-row-by-family bass=2/2 guitar=2/2 piano=2/2 vocals=2/2 other=1/2, first-row-by-family bass=1/2 guitar=1/2 piano=1/2 vocals=1/2 other=1/2, drums kick=0 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=0)
analyzer_real_note_samples full-mix row-confusion: bass[bass=1,guitar=1,piano=0,vocals=0,other=0,amb=0,none=0] guitar[bass=0,guitar=1,piano=1,vocals=0,other=0,amb=0,none=0] piano[bass=0,guitar=0,piano=1,vocals=1,other=0,amb=0,none=0] vocals[bass=0,guitar=0,piano=0,vocals=1,other=1,amb=0,none=0] other[bass=0,guitar=0,piano=0,vocals=0,other=1,amb=1,none=0]
analyzer_real_note_samples full-mix visual-row-confusion: bass[bass=2,guitar=0,piano=0,vocals=0,other=0,amb=0,none=0] guitar[bass=0,guitar=1,piano=0,vocals=0,other=0,amb=1,none=0] piano[bass=0,guitar=1,piano=1,vocals=0,other=0,amb=0,none=0] vocals[bass=0,guitar=0,piano=0,vocals=1,other=0,amb=1,none=0] other[bass=0,guitar=0,piano=1,vocals=0,other=1,amb=0,none=0]
analyzer_real_note_samples full-mix row-confusion-source-routes: bass/electronic->guitar=1 guitar/acoustic->piano=1 piano/electronic->vocals=1 vocals/acoustic->other=1 other/acoustic->amb=1
analyzer_real_note_samples full-mix visual-row-confusion-source-routes: guitar/acoustic->amb=1 piano/electronic->guitar=1 vocals/acoustic->amb=1 other/acoustic->piano=1
""".strip()


def run_checker(*extra: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        log = pathlib.Path(tmpdir) / "shard.out"
        log.write_text(LOG_TEXT, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--min-any-hit-percent",
                "90",
                "--min-expected-row-percent",
                "90",
                "--min-first-row-percent",
                "50",
                "--max-drum-active-percent",
                "5",
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
    completed = run_checker("--other-min-expected-row-percent", "50")
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    require(
        completed.stdout,
        "check_real_note_full_mix_shards: ok (usable 10, any-row 10/10, "
        "expected-row 9/10, first-row 5/10, drum-active-windows 1/40)",
    )
    require(
        completed.stdout,
        "first-row-by-family bass=1/2 guitar=1/2 piano=1/2 vocals=1/2 other=1/2",
    )
    require(completed.stdout, "bass[bass=1,guitar=1,piano=0,vocals=0,other=0,amb=0,none=0]")
    require(
        completed.stdout,
        "check_real_note_full_mix_shards: row-confusion routes "
        "bass->guitar=1 guitar->piano=1 piano->vocals=1 vocals->other=1 other->amb=1",
    )
    require(
        completed.stdout,
        "check_real_note_full_mix_shards: visual-row-confusion routes "
        "guitar->amb=1 piano->guitar=1 vocals->amb=1 other->piano=1",
    )
    require(
        completed.stdout,
        "check_real_note_full_mix_shards: row-confusion source routes "
        "bass/electronic->guitar=1 guitar/acoustic->piano=1 piano/electronic->vocals=1 "
        "vocals/acoustic->other=1 other/acoustic->amb=1",
    )
    require(
        completed.stdout,
        "check_real_note_full_mix_shards: visual-row-confusion source routes "
        "guitar/acoustic->amb=1 piano/electronic->guitar=1 vocals/acoustic->amb=1 "
        "other/acoustic->piano=1",
    )

    failed = run_checker("--other-min-expected-row-percent", "100")
    if failed.returncode == 0:
        raise AssertionError("expected shard checker to fail the other expected-row threshold")
    require(failed.stderr, "expected full-mix other expected-row >= 100%, got 50% (1/2)")

    print("test_check_real_note_full_mix_shards: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
