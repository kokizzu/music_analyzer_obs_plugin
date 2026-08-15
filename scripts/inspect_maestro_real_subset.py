#!/usr/bin/env python3
"""Report whether a MAESTRO subset is complete without mutating corpus data."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: inspect_maestro_real_subset.py OUTPUT_DIR")
    output = Path(argv[1])
    resolved = output.resolve()
    metadata = resolved / "maestro-v3.0.0.csv"
    signature = resolved / ".maps_piano_signature"
    rows: list[dict[str, str]] = []
    if metadata.is_file():
        with metadata.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    complete = sum(
        (resolved / row.get("audio_filename", "")).is_file()
        and (resolved / row.get("midi_filename", "")).is_file()
        for row in rows
    )
    writers = []
    measurements = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if "scripts/prepare_maps_piano_samples.py" in command and "maestro_real_samples" in command:
            writers.append(proc.name)
        if "analyzer_maestro" in command and "MUSIC_ANALYZER_MAESTRO_ROOT" in command:
            measurements.append(proc.name)
    print(
        "maestro_real_subset: "
        f"path={resolved} metadata_rows={len(rows)} paired_files={complete}/{len(rows)} "
        f"signature={'present' if signature.is_file() else 'missing'} "
        f"active_writers={','.join(writers) or '0'} active_measurements={','.join(measurements) or '0'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
