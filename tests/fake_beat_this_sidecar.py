#!/usr/bin/env python3
"""Model-free protocol fixture for the C++ sidecar-client test."""

import json
import struct
import sys


HEADER = struct.Struct("<8sII")
MAGIC = b"MAOBT1\0\0"


def read_exact(length: int) -> bytes:
    data = sys.stdin.buffer.read(length)
    if len(data) != length:
        raise SystemExit(2)
    return data


while True:
    header = sys.stdin.buffer.read(HEADER.size)
    if not header:
        break
    magic, sample_rate, samples = HEADER.unpack(header)
    if magic != MAGIC:
        raise SystemExit(3)
    read_exact(samples * 4)
    sys.stdout.write(json.dumps({
        "bpm": 128.0,
        "intervals": 44,
        "protocol": "mao-beat-this-v1",
        "sample_rate": sample_rate,
        "samples": samples,
        "status": "ready",
    }, separators=(",", ":")) + "\n")
    sys.stdout.flush()
