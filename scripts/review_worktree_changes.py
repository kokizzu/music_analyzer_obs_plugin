#!/usr/bin/env python3
"""Print a compact, reviewable inventory of the current Git worktree."""

from __future__ import annotations

import collections
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout


def section(title: str, value: str) -> None:
    print(f"\n== {title} ==")
    print(value.rstrip() or "(none)")


def status_entries() -> list[str]:
    return git("status", "--short", "--untracked-files=all").splitlines()


def print_summary(entries: list[str]) -> None:
    counts: collections.Counter[str] = collections.Counter()
    for entry in entries:
        path = entry[3:] if len(entry) >= 4 else entry
        top = path.split("/", 1)[0]
        counts[top] += 1

    print("\n== summary ==")
    print(f"worktree entries: {len(entries)}")
    for top, count in sorted(counts.items()):
        print(f"{top}: {count}")

    print("\ntracked changes with line counts:")
    print(git("diff", "--numstat").rstrip() or "(none)")

    untracked = [
        entry[3:]
        for entry in entries
        if entry.startswith("?? ")
    ]
    print(f"\nuntracked files: {len(untracked)}")
    generated_candidates = [
        path
        for path in untracked
        if any(token in path.lower() for token in ("generate", "fixture", "cache", "sample"))
    ]
    print("generated/fixture/cache/sample candidates:")
    print("\n".join(generated_candidates) or "(none)")
    for path in untracked:
        file_path = ROOT / path
        if file_path.is_file():
            try:
                lines = sum(1 for _ in file_path.open("rb"))
                size = file_path.stat().st_size
                print(f"{path}\t{size} bytes\t{lines} lines")
            except OSError as exc:
                print(f"{path}\tstat failed: {exc}")
        else:
            print(f"{path}\t(non-regular or missing)")


def main() -> int:
    entries = status_entries()
    print_summary(entries)
    section("status", "\n".join(entries))
    section("unstaged name-status", git("diff", "--name-status"))
    section("staged name-status", git("diff", "--cached", "--name-status"))
    section("unstaged stat", git("diff", "--stat"))
    section("staged stat", git("diff", "--cached", "--stat"))
    section("diff check", git("diff", "--check"))
    section("staged diff check", git("diff", "--cached", "--check"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
