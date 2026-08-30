#!/usr/bin/env python3
"""Probe the official MedleyDB sample archive without downloading it."""

from __future__ import annotations

import urllib.request


URL = "https://zenodo.org/record/1438309/files/MedleyDB_Sample.tar.gz?download=1"


def main() -> int:
    request = urllib.request.Request(URL, method="HEAD", headers={"User-Agent": "music-analyzer-fixture-fetch/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"url={response.url}")
        print(f"content-length={response.headers.get('Content-Length', 'unknown')}")
        print(f"content-type={response.headers.get('Content-Type', 'unknown')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
