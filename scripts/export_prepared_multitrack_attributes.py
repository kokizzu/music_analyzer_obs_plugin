#!/usr/bin/env python3
"""Export note/chord attributes for the external Prepared Multitrack fixture."""

import os
from pathlib import Path
import subprocess


EXTERNAL_ROOT = Path("build/InstrumentSamples/real-goal-fixture/prepared-multitrack-fixture")
PREPARED_ROOT = Path("build/prepared-multitrack-musicnet-fixture")
OUTPUT = Path("build/prepared_multitrack_attributes.tsv")
BINARY = Path("build/analyzer_musicnet")


def main() -> None:
    if not EXTERNAL_ROOT.is_dir():
        raise SystemExit(f"missing external Prepared Multitrack fixture: {EXTERNAL_ROOT}")
    environment = os.environ.copy()
    environment["MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT"] = str(EXTERNAL_ROOT)
    subprocess.run(["make", "test-prepared-multitrack-prepare"], check=True, env=environment)
    if not BINARY.is_file():
        raise SystemExit(f"missing MusicNet test binary: {BINARY}")
    OUTPUT.unlink(missing_ok=True)
    environment.update(
        {
            "MUSIC_ANALYZER_MUSICNET_ROOT": str(PREPARED_ROOT),
            "MUSIC_ANALYZER_MUSICNET_REQUIRED": "1",
            "MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV": str(OUTPUT),
        }
    )
    subprocess.run([str(BINARY)], check=True, env=environment)
    print(OUTPUT)


if __name__ == "__main__":
    main()
