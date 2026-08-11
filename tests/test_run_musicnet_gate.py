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
        attributes = root / "external-store" / "attributes.tsv"
        binary.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"recording cap $MUSIC_ANALYZER_MUSICNET_MAX_RECORDINGS, required recordings $MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS, windows $MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS, max windows $MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING, attributes $MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV\"\n",
            encoding="utf-8",
        )
        binary.chmod(0o755)
        completed = subprocess.run(
            ["sh", str(args.script), str(binary), str(root / "musicnet"), str(output), "20", "80", str(attributes)],
            check=True,
            text=True,
            capture_output=True,
        )
        assert "recording cap 20, required recordings 20, windows 80, max windows 4" in completed.stdout
        assert f"attributes {attributes}" in completed.stdout
        assert output.read_text(encoding="utf-8") == completed.stdout

    print("run_musicnet_gate: ok")


if __name__ == "__main__":
    main()
