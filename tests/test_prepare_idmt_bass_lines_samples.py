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

import prepare_idmt_bass_lines_samples


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def sine_wav_bytes(midi=40, seconds=2.5, sample_rate=44100):
    data = io.BytesIO()
    freq = midi_frequency(midi)
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


def xml_text(track_id):
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<instrumentRecording>
  <globalParameter>
    <audioFileName>{track_id}.wav</audioFileName>
    <instrument>EBSS</instrument>
    <instrumentModel>Test Bass</instrumentModel>
    <pickUpSetting>Neck</pickUpSetting>
    <instrumentTuning>28,33,38,43</instrumentTuning>
  </globalParameter>
</instrumentRecording>
"""


def make_fixture(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("audio/001.wav", sine_wav_bytes(40))
        archive.writestr("audio/002.wav", sine_wav_bytes(43))
        archive.writestr("annotation/001.xml", xml_text("001"))
        archive.writestr("annotation/002.xml", xml_text("002"))
        archive.writestr(
            "misc/notes_csv/001_note_parameters.csv",
            "\n".join([
                "0.10,0.42,40,2,2,FS,NO,0,0",
                "0.50,0.82,41,2,3,PK,NO,0,0",
                "0.90,1.22,42,2,4,MU,VI,4,25",
                "1.30,1.39,43,3,0,ST,NO,0,0",
            ]) + "\n",
        )
        archive.writestr(
            "misc/notes_csv/002_note_parameters.csv",
            "\n".join([
                "0.10,0.55,43,3,0,SP,NO,0,0",
                "0.70,1.10,45,3,2,MU,NO,0,0",
            ]) + "\n",
        )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        expected = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]
        if header != expected:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def test_default_no_expression_manifest_and_clips():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "idmt.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_idmt_bass_lines_samples.prepare_samples(
            archive,
            output,
            min_samples=4,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        notes = [row[5] for row in rows]
        if notes != ["E2", "F2", "G2", "A2"]:
            raise AssertionError(f"unexpected notes: {notes}")
        if any(row[1] != "bass" for row in rows):
            raise AssertionError("all rows should map to bass")
        if any("expression=VI" in row[7] for row in rows):
            raise AssertionError("default expression filter should skip vibrato")
        for row in rows:
            clip_path = output / row[6]
            if not clip_path.is_file():
                raise AssertionError(f"missing clip {clip_path}")
            with wave.open(str(clip_path), "rb") as clip:
                if clip.getframerate() != 44100 or clip.getnchannels() != 1:
                    raise AssertionError("clip should preserve source WAV params")


def test_expression_filter_can_include_vibrato():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "idmt.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_idmt_bass_lines_samples.prepare_samples(
            archive,
            output,
            allowed_expressions="NO,VI",
            min_samples=5,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        if "F#2" not in [row[5] for row in rows]:
            raise AssertionError("VI expression row should be retained when enabled")


def test_limit_is_balanced_by_note():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "idmt.zip"
        output = root / "out"
        make_fixture(archive)
        prepare_idmt_bass_lines_samples.prepare_samples(
            archive,
            output,
            limit=2,
            min_samples=2,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 2 or len({row[5] for row in rows}) != 2:
            raise AssertionError(f"limit should retain two different notes, got {rows}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "idmt.zip"
        output = root / "out"
        make_fixture(archive)
        try:
            prepare_idmt_bass_lines_samples.prepare_samples(
                archive,
                output,
                min_samples=20,
                refresh=True,
            )
        except SystemExit:
            rows = manifest_rows(output / "manifest.tsv.partial")
            if len(rows) != 4:
                raise AssertionError("partial manifest should contain prepared NO rows")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_default_no_expression_manifest_and_clips()
    test_expression_filter_can_include_vibrato()
    test_limit_is_balanced_by_note()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_idmt_bass_lines_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
