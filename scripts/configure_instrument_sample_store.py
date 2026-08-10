#!/usr/bin/env python3
"""Safely configure the external store used for large instrument corpora."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


def describe(link: Path, target: Path) -> int:
    if link.is_symlink():
        actual = Path(os.readlink(link))
        if not actual.is_absolute():
            actual = (link.parent / actual).resolve()
        print(f"instrument_sample_store: link={link} target={actual}")
        print(f"instrument_sample_store: target_exists={actual.is_dir()}")
        return 0 if actual == target and actual.is_dir() else 1
    if link.exists():
        print(f"instrument_sample_store: {link} is an existing directory or file; refusing to replace it", file=sys.stderr)
        return 1
    print(f"instrument_sample_store: link_missing={link} expected_target={target}")
    return 1


def configure(link: Path, target: Path) -> int:
    if not target.is_dir():
        print(f"instrument_sample_store: target directory is unavailable: {target}", file=sys.stderr)
        return 1
    if link.is_symlink() or link.exists():
        return describe(link, target)
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target, target_is_directory=True)
    print(f"instrument_sample_store: created {link} -> {target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    link = args.link.absolute()
    target = args.target.absolute()
    return describe(link, target) if args.status else configure(link, target)


if __name__ == "__main__":
    raise SystemExit(main())
