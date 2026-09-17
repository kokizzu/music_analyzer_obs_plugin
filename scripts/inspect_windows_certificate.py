#!/usr/bin/env python3
"""Inspect a discovered Windows certificate's public metadata only."""

from __future__ import annotations

import subprocess
from pathlib import Path


CERTIFICATE = Path("/media/kyz/aigenshared/music-analyzer-local-dev.crt")


def main() -> None:
    if not CERTIFICATE.is_file():
        raise SystemExit(f"certificate not found: {CERTIFICATE}")
    result = subprocess.run(
        [
            "openssl",
            "x509",
            "-in",
            str(CERTIFICATE),
            "-noout",
            "-subject",
            "-issuer",
            "-dates",
            "-ext",
            "keyUsage",
            "-ext",
            "extendedKeyUsage",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    print(f"certificate={CERTIFICATE}")
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
