#!/usr/bin/env python3

from pathlib import Path
import math
import struct
import sys
import tempfile
import wave
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_idmt_drums_samples


def fixture_svl(frames, sample_rate=44100):
    points = "\n".join(f'      <point frame="{frame}" label="New Point" />' for frame in frames)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE sonic-visualiser>
<sv>
  <data>
    <model id="2" sampleRate="{sample_rate}" start="0" end="44100" type="sparse" dimensions="1" resolution="1" dataset="1" />
    <dataset id="1" dimensions="1">
{points}
    </dataset>
  </data>
</sv>
"""


def write_hit_wav(path, frames, sample_rate=44100, duration_seconds=1.0):
    frame_count = int(sample_rate * duration_seconds)
    samples = [0] * frame_count
    for hit_frame in frames:
        if hit_frame < 0 or hit_frame >= frame_count:
            continue
        for offset in range(256):
            index = hit_frame + offset
            if index >= frame_count:
                break
            envelope = max(0.0, 1.0 - offset / 256.0)
            value = int(math.sin(offset * 0.9) * envelope * 18000)
            samples[index] = max(-32768, min(32767, samples[index] + value))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def write_fixture_zip(path):
    codes = ("KD", "SD", "HH")
    frames = (-3, 2000, 12000, 24000)
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        with zipfile.ZipFile(path, "w") as archive:
            for code in codes:
                wav_path = temp_path / f"Fixture01#{code}#train.wav"
                write_hit_wav(wav_path, frames)
                archive.write(wav_path, f"audio/Fixture01#{code}#train.wav")
                archive.writestr(f"annotation_svl/Fixture01#{code}.svl", fixture_svl(frames))


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != prepare_idmt_drums_samples.MANIFEST_HEADER:
            raise AssertionError(f"unexpected manifest header {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def run_prepare(base, limit_per_category=0, min_per_category=1):
    archive = base / "IDMT-SMT-DRUMS-V2.zip"
    output = base / "out"
    write_fixture_zip(archive)
    prepare_idmt_drums_samples.main([
        "--archive",
        str(archive),
        "--output",
        str(output),
        "--limit-per-category",
        str(limit_per_category),
        "--min-per-category",
        str(min_per_category),
        "--clip-seconds",
        "0.05",
        "--pre-roll-seconds",
        "0.002",
    ])
    return output


def test_svl_parser_skips_negative_frames():
    sample_rate, points = prepare_idmt_drums_samples.parse_svl_points(
        fixture_svl([-3, 10, 20]).encode("utf-8")
    )
    if sample_rate != 44100:
        raise AssertionError(f"unexpected sample rate {sample_rate}")
    if points != [10, 20]:
        raise AssertionError(f"unexpected points {points}")


def test_idmt_drums_train_hits_are_prepared_by_category():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), min_per_category=3)
        rows = manifest_rows(output / "manifest.tsv")
        categories = [row[0] for row in rows]
        if categories.count("kick") != 3 or categories.count("snare") != 3 or categories.count("hihat") != 3:
            raise AssertionError(f"unexpected categories {categories}")
        if any("-3" in row[1] for row in rows):
            raise AssertionError(f"negative SVL frame should not be prepared: {rows}")
        for row in rows:
            wav_path = output / row[1]
            if not wav_path.is_file():
                raise AssertionError(f"missing prepared WAV {wav_path}")


def test_limit_per_category_is_enforced():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), limit_per_category=2, min_per_category=2)
        rows = manifest_rows(output / "manifest.tsv")
        categories = [row[0] for row in rows]
        if categories.count("kick") != 2 or categories.count("snare") != 2 or categories.count("hihat") != 2:
            raise AssertionError(f"unexpected limited categories {categories}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        try:
            run_prepare(base, limit_per_category=2, min_per_category=3)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            rows = manifest_rows(partial)
            if len(rows) != 6:
                raise AssertionError(f"partial manifest should contain the limited rows, got {len(rows)}")
        else:
            raise AssertionError("expected min-per-category failure")


def main():
    test_svl_parser_skips_negative_frames()
    test_idmt_drums_train_hits_are_prepared_by_category()
    test_limit_per_category_is_enforced()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_idmt_drums_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
