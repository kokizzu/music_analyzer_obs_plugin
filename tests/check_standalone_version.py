#!/usr/bin/env python3

import re
import subprocess
import sys


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_standalone_version.py /path/to/music-analyzer-standalone")

    result = subprocess.run([sys.argv[1], "--version"], check=True, text=True, capture_output=True)
    version = result.stdout.strip()
    if not re.fullmatch(r"\d{4}\.\d{4}\.\d{4}\.[0-9a-fA-F]+|unknown", version):
        raise SystemExit(f"check_standalone_version: invalid version '{version}'")
    print(f"check_standalone_version: {version}")


if __name__ == "__main__":
    main()
