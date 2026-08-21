#!/usr/bin/env python3
"""Replay labelled audio through the persistent, disabled Beat This! sidecar.

This is an offline verification harness, not an OBS backend.  It sends one
causal 20-second packet at a time to one persistent child process, records
only the sidecar's gated replies, and never opens an audio output device.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import select
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

from beat_this_live_sidecar import HEADER, MAGIC, PROTOCOL, WINDOW_SECONDS
from measure_beat_this_bpm import bpm_from_midi


def trailing_window_bounds(sample_count: int, sample_rate: int, stable_start: float) -> tuple[int, int]:
    """Return the exact causal 20-second window ending after the stable span starts."""
    if sample_count <= 0 or sample_rate <= 0 or stable_start < 0.0:
        raise ValueError("audio length, sample rate, and stable offset must be valid")
    last = int(round((stable_start + WINDOW_SECONDS) * sample_rate))
    first = last - WINDOW_SECONDS * sample_rate
    if first < 0 or last > sample_count:
        raise ValueError("audio does not contain a complete causal 20-second sidecar window")
    return first, last


def packet(signal: np.ndarray, sample_rate: int) -> bytes:
    """Encode exactly one validated mono float32 packet for the child."""
    samples = np.asarray(signal, dtype="<f4")
    if samples.ndim != 1 or len(samples) != sample_rate * WINDOW_SECONDS:
        raise ValueError("sidecar packet must be exactly 20 seconds of mono audio")
    if not np.isfinite(samples).all():
        raise ValueError("sidecar packet contains non-finite samples")
    return HEADER.pack(MAGIC, sample_rate, len(samples)) + samples.tobytes()


def parse_reply(text: str, sample_rate: int) -> dict[str, Any]:
    """Accept only the fixed, complete reply shape defined by the protocol."""
    child: subprocess.Popen[bytes] | None = None
    try:
        reply = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("sidecar emitted malformed JSON") from error
    expected_samples = sample_rate * WINDOW_SECONDS
    if not isinstance(reply, dict) or reply.get("protocol") != PROTOCOL:
        raise ValueError("sidecar emitted an unknown protocol reply")
    if reply.get("sample_rate") != sample_rate or reply.get("samples") != expected_samples:
        raise ValueError("sidecar reply does not match its submitted packet")
    if reply.get("status") not in {"ready", "gated"}:
        raise ValueError("sidecar reply has an invalid status")
    intervals = reply.get("intervals")
    bpm = reply.get("bpm")
    if not isinstance(intervals, int) or intervals < 0 or not isinstance(bpm, (int, float)):
        raise ValueError("sidecar reply has invalid BPM fields")
    if reply["status"] == "gated" and bpm != 0.0:
        raise ValueError("gated sidecar reply must withhold its BPM")
    return reply


def load_audio_loader(runtime_root: Path, model_cache_root: Path):
    """Import the optional loader without allowing it to use a repository cache."""
    site_packages = runtime_root / "site-packages"
    if not site_packages.is_dir():
        raise ValueError(f"Beat This dependencies are missing: {site_packages}")
    sys.path.append(str(site_packages))
    os.environ["TORCH_HOME"] = str(model_cache_root / "cache")
    os.environ["XDG_CACHE_HOME"] = str(model_cache_root / "cache")
    from beat_this.preprocessing import load_audio  # pylint: disable=import-outside-toplevel

    return load_audio


def expected_bpm(row: dict[str, str], root: Path) -> float:
    return float(row["bpm"]) if row.get("bpm") else bpm_from_midi(root / row["midi_filename"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--model-cache-root", type=Path, required=True)
    parser.add_argument("--metadata", default="maestro-v3.0.0.csv")
    parser.add_argument("--checkpoint", default="final0")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--start", type=int, default=0, help="zero-based metadata row to start from")
    parser.add_argument("--limit", type=int, default=0, help="0 replays every available row")
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--response-timeout", type=float, default=120.0)
    args = parser.parse_args()
    if args.start < 0 or args.limit < 0 or args.tolerance < 0.0 or args.response_timeout <= 0.0:
        parser.error("--start, --limit, and --tolerance must be non-negative; --response-timeout must be positive")
    try:
        load_audio = load_audio_loader(args.runtime_root, args.model_cache_root)
        with (args.root / args.metadata).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows = rows[args.start:args.start + args.limit if args.limit else None]
        if not rows:
            raise ValueError("metadata contains no sidecar replay rows")
        command = [
            sys.executable,
            str(Path(__file__).with_name("beat_this_live_sidecar.py")),
            "--runtime-root", str(args.runtime_root),
            "--model-cache-root", str(args.model_cache_root),
            "--checkpoint", args.checkpoint,
            "--device", args.device,
        ]
        child = subprocess.Popen(  # nosec B603: fixed local Python sidecar command
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        assert child.stdin is not None and child.stdout is not None
        results: list[str] = []
        try:
            for index, row in enumerate(rows, args.start + 1):
                signal, sample_rate = load_audio(args.root / row["audio_filename"])
                signal = np.asarray(signal)
                if signal.ndim == 2:
                    signal = signal.mean(axis=1)
                if signal.ndim != 1:
                    raise ValueError(f"audio must decode to mono or time-by-channel samples, got {signal.shape}")
                rate = int(sample_rate)
                expected = expected_bpm(row, args.root)
                try:
                    first, last = trailing_window_bounds(
                        len(signal), rate, float(row.get("tempo_audio_offset_seconds", "0") or 0.0)
                    )
                except ValueError as error:
                    if str(error) != "audio does not contain a complete causal 20-second sidecar window":
                        raise
                    results.append(
                        "Beat This sidecar replay"
                        f"\tid={index}\texpected={expected:.2f}\traw=0.00\tintervals=0"
                        f"\tpacket_seconds={WINDOW_SECONDS}\twall_seconds=0.000\tmodel={args.checkpoint}"
                        "\terror=0.00\tstatus=unavailable"
                    )
                    continue
                started = time.monotonic()
                child.stdin.write(packet(signal[first:last], rate))
                child.stdin.flush()
                ready, _, _ = select.select([child.stdout], [], [], args.response_timeout)
                if not ready:
                    raise ValueError(f"sidecar response {index} exceeded {args.response_timeout:.1f}s")
                response_line = child.stdout.readline()
                elapsed = time.monotonic() - started
                if not response_line:
                    raise ValueError(f"sidecar exited before reply {index}")
                reply = parse_reply(response_line.decode("ascii", errors="strict"), rate)
                raw = float(reply["bpm"])
                error = abs(raw - expected) if reply["status"] == "ready" else 0.0
                status = "withheld" if reply["status"] == "gated" else ("hit" if error <= args.tolerance else "miss")
                results.append(
                    "Beat This sidecar replay"
                    f"\tid={index}\texpected={expected:.2f}\traw={raw:.2f}\tintervals={reply['intervals']}"
                    f"\tpacket_seconds={WINDOW_SECONDS}\twall_seconds={elapsed:.3f}\tmodel={args.checkpoint}"
                    f"\terror={error:.2f}\tstatus={status}"
                )
        finally:
            child.stdin.close()
        stderr = child.stderr.read().decode("utf-8", errors="replace") if child.stderr is not None else ""
        if child.wait(timeout=10.0) != 0:
            raise ValueError(f"sidecar exited with {child.returncode}: {stderr.strip()}")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=10.0)
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as handle:
        handle.write("\n".join(results) + "\n")
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(f"Beat This sidecar replay: wrote {len(results)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
