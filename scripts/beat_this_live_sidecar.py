#!/usr/bin/env python3
"""Run the optional Beat This! model behind a bounded binary sidecar protocol.

This program is deliberately *not* started by the OBS plugin.  It exists so a
future optional worker can use a persistent model process without placing
Python, model loading, allocation, or inference in OBS's audio callback.

stdin accepts fixed 20-second mono float32-le packets.  stdout contains one
machine-readable line per valid packet and nothing else.  A BPM is returned
only when the exact interval-count gate established by the causal replay is
satisfied.  Model assets are read from an external cache; this runner never
downloads them itself.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import struct
import sys
from array import array
from collections.abc import Callable, Iterable
from pathlib import Path

from measure_beat_this_bpm import tempo_from_beats


PROTOCOL = "mao-beat-this-v1"
MAGIC = b"MAOBT1\0\0"
HEADER = struct.Struct("<8sII")
SAMPLE_BYTES = 4
WINDOW_SECONDS = 20
MIN_INTERVALS = 44
MIN_SAMPLE_RATE = 8_000
MAX_SAMPLE_RATE = 192_000


def expected_samples(sample_rate: int) -> int:
    """Validate a supported rate and return the exact sidecar packet size."""
    if not MIN_SAMPLE_RATE <= sample_rate <= MAX_SAMPLE_RATE:
        raise ValueError(f"sample rate must be within {MIN_SAMPLE_RATE}..{MAX_SAMPLE_RATE}")
    return sample_rate * WINDOW_SECONDS


def validate_shape(sample_rate: int, sample_count: int) -> None:
    if sample_count != expected_samples(sample_rate):
        raise ValueError(f"packet must contain exactly {WINDOW_SECONDS} seconds of mono audio")


def read_exact(stream: io.BufferedReader | io.BytesIO, length: int) -> bytes:
    data = stream.read(length)
    if len(data) != length:
        raise ValueError("truncated sidecar packet")
    return data


def read_packet(stream: io.BufferedReader | io.BytesIO) -> tuple[int, bytes] | None:
    """Read one complete packet; EOF before a header is a clean shutdown."""
    raw_header = stream.read(HEADER.size)
    if not raw_header:
        return None
    if len(raw_header) != HEADER.size:
        raise ValueError("truncated sidecar header")
    magic, sample_rate, sample_count = HEADER.unpack(raw_header)
    if magic != MAGIC:
        raise ValueError("unrecognized sidecar packet magic")
    validate_shape(sample_rate, sample_count)
    return sample_rate, read_exact(stream, sample_count * SAMPLE_BYTES)


def samples_from_payload(payload: bytes, sample_count: int) -> array:
    if len(payload) != sample_count * SAMPLE_BYTES:
        raise ValueError("invalid float32 payload length")
    result = array("f")
    result.frombytes(payload)
    if sys.byteorder != "little":
        result.byteswap()
    if len(result) != sample_count or not all(math.isfinite(value) for value in result):
        raise ValueError("packet contains invalid samples")
    return result


def gated_response(beats: Iterable[float], sample_rate: int, sample_count: int) -> dict[str, int | float | str]:
    """Apply the exact 20-second/44-interval live-candidate gate."""
    validate_shape(sample_rate, sample_count)
    bpm, intervals = tempo_from_beats(list(beats), 0.0, float(WINDOW_SECONDS))
    ready = math.isfinite(bpm) and bpm > 0.0 and intervals >= MIN_INTERVALS
    return {
        "protocol": PROTOCOL,
        "status": "ready" if ready else "gated",
        "bpm": round(bpm, 6) if ready else 0.0,
        "intervals": intervals,
        "sample_rate": sample_rate,
        "samples": sample_count,
    }


def encode_response(response: dict[str, int | float | str]) -> bytes:
    return json.dumps(response, separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n"


BeatProvider = Callable[[array, int], Iterable[float]]


def cached_checkpoint(model_cache_root: Path, checkpoint: str) -> Path:
    """Resolve only the known local cache name; never let the library download."""
    if not checkpoint or Path(checkpoint).name != checkpoint or not checkpoint.replace("_", "").isalnum():
        raise ValueError("checkpoint must be a simple cached model name")
    resolved = model_cache_root / "cache" / "hub" / "checkpoints" / f"beat_this-{checkpoint}.ckpt"
    if not resolved.is_file():
        raise ValueError(f"Beat This checkpoint is missing from the external cache: {resolved}")
    return resolved


def serve(stream: io.BufferedReader | io.BytesIO, output: io.BufferedWriter | io.BytesIO, beat_provider: BeatProvider) -> int:
    """Handle packets synchronously; caller owns process scheduling and timeout."""
    while (packet := read_packet(stream)) is not None:
        sample_rate, payload = packet
        samples = samples_from_payload(payload, expected_samples(sample_rate))
        response = gated_response(beat_provider(samples, sample_rate), sample_rate, len(samples))
        output.write(encode_response(response))
        output.flush()
    return 0


def model_provider(runtime_root: Path, model_cache_root: Path, checkpoint: str, device: str) -> BeatProvider:
    """Load the model once, with caches restricted to the external sample store."""
    site_packages = runtime_root / "site-packages"
    if not site_packages.is_dir():
        raise ValueError(f"Beat This dependencies are missing: {site_packages}")
    checkpoint_file = cached_checkpoint(model_cache_root, checkpoint)
    sys.path.append(str(site_packages))
    os.environ["TORCH_HOME"] = str(model_cache_root / "cache")
    os.environ["XDG_CACHE_HOME"] = str(model_cache_root / "cache")
    from beat_this.inference import Audio2Beats  # pylint: disable=import-outside-toplevel

    tracker = Audio2Beats(checkpoint_path=str(checkpoint_file), device=device, dbn=False)

    def provide(samples: array, sample_rate: int) -> Iterable[float]:
        # Audio2Beats requires a one-dimensional ndarray.  The byte payload was
        # already fully validated before this copy into model-owned memory.
        import numpy as np  # pylint: disable=import-outside-toplevel

        beats, _ = tracker(np.asarray(samples, dtype=np.float32), sample_rate)
        return beats

    return provide


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--model-cache-root", type=Path, required=True)
    parser.add_argument("--checkpoint", default="final0")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    try:
        provider = model_provider(args.runtime_root, args.model_cache_root, args.checkpoint, args.device)
        return serve(sys.stdin.buffer, sys.stdout.buffer, provider)
    except (BrokenPipeError, ValueError) as error:
        print(f"Beat This sidecar: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
