#!/usr/bin/env python3
"""Summarize recorded IDMT drum-shard outputs after a parallel test run."""

from pathlib import Path


BUILD = Path("build")


def print_tail(path: Path, limit: int = 20) -> None:
    print(f"== {path} ==")
    if not path.exists():
        print("missing")
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-limit:]:
        print(line)


def main() -> None:
    for category in ("kick", "snare", "hihat"):
        print_tail(BUILD / f"idmt_drums_samples_shard_{category}.out")
        print_tail(BUILD / f"idmt_drums_samples_shard_{category}.err")
    duration_logs = sorted(BUILD.glob("*idmt_drums*duration*"))
    for path in duration_logs:
        print_tail(path, 5)


if __name__ == "__main__":
    main()
