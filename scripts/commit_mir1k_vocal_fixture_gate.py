#!/usr/bin/env python3
"""Commit and push only the staged MIR-1K vocal regression fixture gate."""

from __future__ import annotations

import subprocess


PREFIX = "tests/fixtures/mir1k_clean_vocals/"


def main() -> int:
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True,
                            text=True, stdout=subprocess.PIPE).stdout.splitlines()
    if not staged or staged[0] != "Makefile" or len(staged) not in (1, 223) or any(
            not path.startswith(PREFIX) for path in staged[1:]):
        raise RuntimeError(f"refusing mixed commit: {staged[:4]} ... ({len(staged)} paths)")
    subprocess.run(["git", "commit", "-m", "Add MIR-1K vocal full-mix regression fixtures"], check=True)
    subprocess.run(["git", "push"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
