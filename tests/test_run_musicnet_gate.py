#!/usr/bin/env python3
"""Regression checks for retaining MusicNet gate output outside build/."""

import argparse
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="musicnet-gate-") as temporary:
        root = Path(temporary)
        binary = root / "analyzer"
        output = root / "external-store" / "measurement.out"
        binary.write_text("#!/bin/sh\nprintf 'recordings 20/330, windows 80, note hits 210/300, chord hits 40/80, simple chord hits 52/80\\n'\n", encoding="utf-8")
        binary.chmod(0o755)
        completed = subprocess.run(
            ["sh", str(args.script), str(binary), str(root / "musicnet"), str(output)],
            check=True,
            text=True,
            capture_output=True,
        )
        assert "recordings 20/330" in completed.stdout
        assert output.read_text(encoding="utf-8") == completed.stdout

    print("run_musicnet_gate: ok")


if __name__ == "__main__":
    main()
