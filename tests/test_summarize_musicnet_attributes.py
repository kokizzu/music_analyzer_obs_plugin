#!/usr/bin/env python3
"""Regression test for MusicNet trait aggregation."""

import subprocess
import tempfile
from pathlib import Path


HEADER = "expected_pcs\tmissing_pcs\textra_pcs\texpected_chords\tchord_hit\tsimple_chord_hit\tdetected_by_row\n"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="musicnet-traits-") as temporary:
        path = Path(temporary) / "traits.tsv"
        path.write_text(
            HEADER
            + "C E G\t--\t--\tC\t1\t1\tkeys=C E G\n"
            + "C E G\tE\tD\tC\t0\t1\tkeys=C D G\n"
            + "D F# A\tF#\tC#\tD\t0\t0\tother=C# D A\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["python3", "scripts/summarize_musicnet_attributes.py", str(path)],
            check=True,
            text=True,
            capture_output=True,
        )
    assert "exact pitch sets 1/3, exact chords 1/3, simplified chords 2/3" in result.stdout
    assert "missing pitch classes: E=1 F#=1" in result.stdout
    assert "extra pitch classes: D=1 C#=1" in result.stdout
    assert "extra pitch classes by row: keys:D=1 other:C#=1" in result.stdout
    assert "C: exact=1/2 simple=2/2" in result.stdout
    print("summarize_musicnet_attributes: ok")


if __name__ == "__main__":
    main()
