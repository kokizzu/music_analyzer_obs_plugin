#!/usr/bin/env python3
"""Inspect suspicious top-level worktree artifacts without modifying them."""

from pathlib import Path


root = Path(__file__).resolve().parents[1]
names = (":memory:.ses", "=0.04", "=0.163", "=0.713", "=1.137", "absent@4", "guitar", "ride", "tom")
for name in names:
    path = root / name
    if not path.exists() and not path.is_symlink():
        print(f"missing={name}")
        continue
    stat = path.stat()
    print(f"path={name} kind={'dir' if path.is_dir() else 'file'} bytes={stat.st_size} mtime={stat.st_mtime}")
    if path.is_file():
        data = path.read_bytes()[:256]
        print(f"prefix={data!r}")
