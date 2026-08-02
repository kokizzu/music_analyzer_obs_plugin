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

import prepare_vocalset_samples


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


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        expected = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]
        if header != expected:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def make_all_files_fixture(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "VocalSet/FULL/female1/arpeggios/straight/f1_arpeggios_a_straight.wav",
            sine_wav_bytes(),
        )
        archive.writestr(
            "VocalSet/FULL/male1/scales/belt/m1_scales_e_belt.wav",
            sine_wav_bytes(freq=293.664768),
        )
        archive.writestr(
            "VocalSet/annotations/extended 4/all files.csv",
            "\n".join([
                "File Name,Gender,Singer name,Technique,Music Type,Vowel,BPM,File duration in milliseconds,Sequence,Start time,End time,Duration,Type,Average F0,Median F0,Min F0,Max F0,STD F0,Average F0 in range of STD,Estimated MIDI code,Ground truth Note name,Ground Truth Frequency,Ground Truth MIDI code,Lyric",
                "f1_arpeggios_a_straight,Female,f1,straight,arpeggios,a,120,2000,1,0.100,0.800,0.700,Sound,261.626,261.626,261,262,0.1,261.626,60,C4,261.626,60,la",
                "f1_arpeggios_a_straight,Female,f1,straight,arpeggios,a,120,2000,2,0.900,1.500,0.600,Sound,277.183,277.183,277,278,0.1,277.183,61,C#4,277.183,61,la",
                "f1_arpeggios_a_straight,Female,f1,straight,arpeggios,a,120,2000,3,1.600,1.800,0.200,Sound,329.628,329.628,329,330,0.1,329.628,64,E4,329.628,64,la",
                "f1_arpeggios_a_straight,Female,f1,straight,arpeggios,a,120,2000,4,1.000,1.700,0.700,Rest,391.995,391.995,391,392,0.1,391.995,67,G4,391.995,67,la",
                "m1_scales_e_belt,Male,m1,Belt_Harsh,scales,e,120,2000,1,0.200,1.000,0.800,Sound,293.665,293.665,293,294,0.1,293.665,62,D4,293.665,62,la",
                "m1_scales_e_belt,Male,m1,spoken,scales,e,120,2000,2,1.100,1.800,0.700,Sound,311.127,311.127,311,312,0.1,311.127,63,D#4,311.127,63,la",
            ]) + "\n",
        )


def make_without_header_fixture(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "VocalSet/FULL/female1/arpeggios/vibrato/f1_arpeggios_a_vibrato.wav",
            sine_wav_bytes(freq=329.627557),
        )
        archive.writestr(
            "VocalSet/annotations/extended 4/without file header/vibrato/f1_arpeggios_a_vibrato.csv",
            "1,0.100,0.900,0.800,Sound,329.628,329.628,329,330,0.1,329.628,64,E4,329.628,64,la\n",
        )


def test_all_files_manifest_and_clips():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "VocalSet.zip"
        output = root / "out"
        make_all_files_fixture(archive)
        prepare_vocalset_samples.prepare_samples(
            archive,
            output,
            allowed_techniques="straight,belt",
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


def test_without_file_header_fallback():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "VocalSet.zip"
        output = root / "out"
        make_without_header_fixture(archive)
        prepare_vocalset_samples.prepare_samples(
            archive,
            output,
            allowed_techniques="vibrato",
            min_samples=1,
            min_note_duration=0.20,
            max_cents=25,
            refresh=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        if [row[5] for row in rows] != ["E4"]:
            raise AssertionError(f"unexpected fallback rows: {rows}")


def test_limit_is_balanced_by_note():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "VocalSet.zip"
        output = root / "out"
        make_all_files_fixture(archive)
        prepare_vocalset_samples.prepare_samples(
            archive,
            output,
            allowed_techniques="straight,belt",
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
        archive = root / "VocalSet.zip"
        output = root / "out"
        make_all_files_fixture(archive)
        try:
            prepare_vocalset_samples.prepare_samples(
                archive,
                output,
                allowed_techniques="straight,belt",
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
    test_all_files_manifest_and_clips()
    test_without_file_header_fallback()
    test_limit_is_balanced_by_note()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_vocalset_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
