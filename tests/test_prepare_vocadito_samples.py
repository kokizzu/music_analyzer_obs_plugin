#!/usr/bin/env python3

from pathlib import Path
import io
import math
import struct
import sys
import tempfile
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_vocadito_samples


def sine_wav_bytes(freq=261.625565, seconds=2.0, sample_rate=44100):
    data = io.BytesIO()
    frame_count = int(seconds * sample_rate)
    with wave.open(data, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = 0.25 * math.sin(2.0 * math.pi * freq * index / sample_rate)
            frames.extend(struct.pack("<h", int(sample * 32767.0)))
        file.writeframes(bytes(frames))
    return data.getvalue()


def make_fixture(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "vocadito_metadata.csv",
            "\n".join([
                "track_id,singer_id,average_pitch,language",
                "1,S1,60,English",
                "2,S2,62,Tagalog",
            ]) + "\n",
        )
        archive.writestr("Audio/vocadito_1.wav", sine_wav_bytes())
        archive.writestr("Audio/vocadito_2.wav", sine_wav_bytes(freq=293.664768))
        archive.writestr(
            "Annotations/Notes/vocadito_1_notesA1.csv",
            "\n".join([
                "0.100,261.626,0.600",
                "0.900,277.183,0.500",
                "1.500,270.000,0.500",
                "1.700,391.995,0.100",
            ]) + "\n",
        )
        archive.writestr(
            "Annotations/Notes/vocadito_1_notesA2.csv",
            "\n".join([
                "0.100,293.665,0.600",
            ]) + "\n",
        )
        archive.writestr(
            "Annotations/Notes/vocadito_2_notesA1.csv",
            "\n".join([
                "0.200,293.665,0.800",
            ]) + "\n",
        )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        expected = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]
        if header != expected:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def test_default_a1_manifest_and_clips():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "vocadito.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_vocadito_samples.prepare_samples(
            archive,
            output,
            min_samples=3,
            min_note_duration=0.20,
            max_cents=25,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        notes = [row[5] for row in rows]
        if notes != ["C4", "C#4", "D4"]:
            raise AssertionError(f"unexpected note labels: {notes}")
        if any(row[1] != "vocals" for row in rows):
            raise AssertionError("all rows should map to vocals")
        for row in rows:
            clip_path = output / row[6]
            if not clip_path.is_file():
                raise AssertionError(f"missing clip {clip_path}")
            with wave.open(str(clip_path), "rb") as clip:
                if clip.getframerate() != 44100 or clip.getnchannels() != 1:
                    raise AssertionError("clip should preserve source WAV params")


def test_both_annotator_mode_is_available():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "vocadito.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_vocadito_samples.prepare_samples(
            archive,
            output,
            annotator="both",
            min_samples=4,
            min_note_duration=0.20,
            max_cents=25,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        annotators = [row[7] for row in rows]
        if not any("A2" in quality for quality in annotators):
            raise AssertionError("both annotator mode should include A2 rows")


def test_limit_is_balanced_by_note():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "vocadito.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_vocadito_samples.prepare_samples(
            archive,
            output,
            limit=2,
            min_samples=2,
            min_note_duration=0.20,
            max_cents=25,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 2 or len({row[5] for row in rows}) != 2:
            raise AssertionError(f"limit should retain two different notes, got {rows}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "vocadito.zip"
        output = root / "out"
        make_fixture(archive)
        try:
            prepare_vocadito_samples.prepare_samples(
                archive,
                output,
                min_samples=10,
                min_note_duration=0.20,
                max_cents=25,
                refresh=True,
            )
        except SystemExit:
            rows = manifest_rows(output / "manifest.tsv.partial")
            if len(rows) != 3:
                raise AssertionError("partial manifest should contain prepared rows")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_default_a1_manifest_and_clips()
    test_both_annotator_mode_is_available()
    test_limit_is_balanced_by_note()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_vocadito_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
