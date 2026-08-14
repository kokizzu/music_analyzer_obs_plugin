#!/usr/bin/env python3
"""Regression checks for the non-mutating MIR-1K download status script."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_mir1k_download.py"
SPEC = importlib.util.spec_from_file_location("inspect_mir1k_download", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "mir1k.tar.gz"
        assert INSPECT.describe(archive, "archive") == "archive=missing"
        archive.write_bytes(b"fixture")
        assert INSPECT.describe(archive, "archive") == "archive=present bytes=7"
    print("test_inspect_mir1k_download: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
