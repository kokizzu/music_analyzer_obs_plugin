#!/usr/bin/env python3
"""Inspect a WAV file using analyzer_real_note_samples-compatible chunk rules."""

from __future__ import annotations

import argparse
from pathlib import Path


def inspect(path: Path) -> list[str]:
    size = path.stat().st_size
    lines = [f"wav_for_analyzer: path={path} bytes={size}"]
    with path.open("rb") as source:
        riff = source.read(4)
        source.read(4)
        wave = source.read(4)
        lines.append(f"header: riff={riff!r} wave={wave!r}")
        offset = 12
        while offset + 8 <= size:
            source.seek(offset)
            chunk_id = source.read(4)
            chunk_size_data = source.read(4)
            if len(chunk_size_data) != 4:
                lines.append(f"chunk: offset={offset} truncated-size")
                break
            chunk_size = int.from_bytes(chunk_size_data, "little")
            data_offset = offset + 8
            lines.append(
                f"chunk: offset={offset} id={chunk_id!r} size={chunk_size} data_offset={data_offset}"
            )
            if data_offset + chunk_size > size:
                lines.append("result: invalid chunk exceeds file length")
                break
            if chunk_id == b"fmt " and chunk_size >= 16:
                source.seek(data_offset)
                fields = source.read(16)
                lines.append(
                    "fmt: "
                    f"audio_format={int.from_bytes(fields[0:2], 'little')} "
                    f"channels={int.from_bytes(fields[2:4], 'little')} "
                    f"sample_rate={int.from_bytes(fields[4:8], 'little')} "
                    f"block_align={int.from_bytes(fields[12:14], 'little')} "
                    f"bits={int.from_bytes(fields[14:16], 'little')}"
                )
            offset = data_offset + chunk_size + (chunk_size & 1)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", required=True, type=Path)
    args = parser.parse_args()
    for line in inspect(args.wav):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
