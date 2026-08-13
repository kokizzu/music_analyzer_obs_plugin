#!/usr/bin/env python3
"""Print non-summary diagnostics from isolated real-note analyzer shard logs."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", default="build")
    parser.add_argument("--tag")
    parser.add_argument("--path", action="append", type=Path)
    parser.add_argument("--limit", type=int, default=32)
    args = parser.parse_args()

    paths = list(args.path or [])
    if not paths:
        if not args.tag:
            parser.error("provide --tag or at least one --path")
        paths = sorted(Path(args.build_dir).glob(f"real_note_{args.tag}_shard_*.err"))
    if not paths:
        parser.error(f"no shard error logs for tag `{args.tag}` under {args.build_dir}")

    printed = 0
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip() or line.startswith("analyzer_real_note_samples:"):
                continue
            print(f"{path.name}: {line}")
            printed += 1
            if args.limit > 0 and printed >= args.limit:
                break
        if args.limit > 0 and printed >= args.limit:
            break
    print(f"real_note_shard_error_lines={printed} shards={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
