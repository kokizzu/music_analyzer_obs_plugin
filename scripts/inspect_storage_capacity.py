#!/usr/bin/env python3
"""Print available capacity for an external corpus-storage path."""

import argparse
from pathlib import Path
import shutil


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    path = args.path.resolve()
    if not path.is_dir():
        parser.error(f"not a directory: {path}")
    usage = shutil.disk_usage(path)
    gib = 1024 ** 3
    print(
        f"storage_capacity: path={path} total_gib={usage.total / gib:.1f} "
        f"used_gib={usage.used / gib:.1f} free_gib={usage.free / gib:.1f}"
    )


if __name__ == "__main__":
    main()
