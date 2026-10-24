#!/usr/bin/env python3
"""Fingerprint continuous real-audio replays and report timing/stability.

No short clips are looped. Unlabelled transitions are never scored as errors.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]


def source_reference(base, relative, destination):
    """Resolve a fixture symlink before normalizing its parent references."""
    return os.path.relpath((base / relative).resolve(strict=True), destination.resolve(strict=True))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows, rate):
    if not rows:
        raise ValueError("empty capture")
    hop = int(rate * .05 + .5)
    for index, row in enumerate(rows, 1):
        assert int(row["end_sample"]) == index * hop
        # Snapshot sequence is assigned by product hosts, not AnalysisEngine.
        assert int(row["hop_index"]) == index
    wall = sorted(float(row["wall_ms"]) for row in rows)
    def percentile(p):
        return wall[min(len(wall) - 1, int((len(wall) - 1) * p))]
    transitions = {key: sum(a[key] != b[key] for a, b in zip(rows, rows[1:]))
                   for key in ("chord", "guitar", "voice", "drums")}
    # A-B-A is only a stability signal: real repeated notes can be intentional.
    reversals = {key: sum(a[key] == c[key] != b[key] for a, b, c in zip(rows, rows[1:], rows[2:]))
                 for key in transitions}
    return dict(frames=len(rows), audio_seconds=len(rows) * hop / rate,
                wall_ms=dict(p50=percentile(.5), p95=percentile(.95), p99=percentile(.99), maximum=wall[-1]),
                deadline_misses=sum(value > hop / rate * 1000 for value in wall),
                cpu_ms=sum(float(row["cpu_ms"]) for row in rows),
                rss_growth_kb=int(rows[-1]["rss_kb"]) - int(rows[0]["rss_kb"]),
                transitions=transitions, one_hop_reversals=reversals,
                scope="Native engine only; transitions/reversals are not labelled accuracy or model freshness")


def prepare(wav, destination):
    with wave.open(str(wav), "rb") as audio:
        assert audio.getsampwidth() == 2 and audio.getcomptype() == "NONE", "PCM16 WAV required"
        rate, channels, count = audio.getframerate(), audio.getnchannels(), audio.getnframes()
        with destination.open("wb") as output:
            while raw := audio.readframes(8192):
                values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
                mono = [sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)]
                output.write(struct.pack("<" + "f" * len(mono), *mono))
    return rate, count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--paced", action="store_true")
    args = parser.parse_args()
    selected = []
    if args.input:
        selected = [("custom", args.input.resolve())]
    else:
        for corpus, relative in (("Ballroom", "build/ballroom-tempo-fixture"),
                                 ("FiloBass", "build/InstrumentSamples/filobass/tempo-fixture"),
                                 ("GTZAN", "build/gtzan-rhythm-tempo-fixture")):
            base = ROOT / relative
            with (base / "maestro-v3.0.0.csv").open() as stream:
                row = next(csv.DictReader(stream))
            selected.append((corpus, base / row["audio_filename"]))
    source_paths = [Path("src/analyzer.cpp"), Path("tests/analyzer_sustained.cpp"),
                    Path("build/analyzer_sustained"), Path(__file__).relative_to(ROOT)]
    source_paths += [p.relative_to(ROOT) for p in sorted((ROOT / "src").glob("*.hpp"))]
    signatures = {str(p): digest(ROOT / p) for p in source_paths}
    capabilities = subprocess.run([str(ROOT / "build/analyzer_sustained"), "--capabilities"],
                                  text=True, capture_output=True, check=True).stdout.strip()
    modes_to_run = ("native", "corrected") if capabilities == "pcm-correction" else ("native",)
    audio_hashes = {name: digest(path) for name, path in selected}
    key = hashlib.sha256(json.dumps([signatures, audio_hashes, args.paced], sort_keys=True).encode()).hexdigest()[:12]
    directory = ROOT / "build/sustained_analyzer" / key
    directory.mkdir(parents=True, exist_ok=True)
    report_path = directory / "report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else dict(
        signatures=signatures, audio_sha256=audio_hashes, paced=args.paced,
        capabilities=capabilities, recordings={}, complete=False)
    assert report["signatures"] == signatures and report["audio_sha256"] == audio_hashes
    def checkpoint():
        temporary = report_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(report_path)
    checkpoint()
    for name, path in selected:
        raw = directory / (name + ".f32")
        rate, count = prepare(path, raw)
        assert count / rate >= 20, "Sustained replay requires at least 20 seconds; never loop clips"
        modes = report["recordings"].setdefault(name, {})
        for mode in modes_to_run:
            output = directory / (name + "-" + mode + ".tsv")
            if mode in modes:
                assert digest(output) == modes[mode]["frames_sha256"], "Changed cached frames"
            else:
                subprocess.run([str(ROOT / "build/analyzer_sustained"), str(raw), str(rate), str(output),
                            "paced" if args.paced else "throughput", mode], check=True,
                           timeout=max(300, count / rate * 20))
            with output.open() as stream:
                rows = list(csv.DictReader(stream, delimiter="\t"))
            assert len(rows) == count // int(rate * .05 + .5)
            modes[mode] = dict(summary=summarize(rows, rate), frames_sha256=digest(output))
            assert all(digest(ROOT / p) == checksum for p, checksum in signatures.items())
            assert digest(path) == audio_hashes[name]
            checkpoint()
            print(name, mode, json.dumps(modes[mode]["summary"]), flush=True)
        report["recordings"][name] = modes
        assert digest(path) == audio_hashes[name]
    assert all(digest(ROOT / p) == checksum for p, checksum in signatures.items())
    report["complete"] = True
    checkpoint()
    print(directory.relative_to(ROOT) / "report.json", flush=True)


if __name__ == "__main__":
    main()
