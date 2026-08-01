#!/usr/bin/env python3

import math
from pathlib import Path
import struct
import sys
import tempfile
import wave
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_guitar_techs_samples


NOTE_PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def write_executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_var_len(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(bytes_out)


def midi_event(delta, payload):
    return write_var_len(delta) + payload


def write_midi(path):
    ticks_per_quarter = 480
    events = [
        midi_event(0, b"\xff\x51\x03\x07\xa1\x20"),
        midi_event(120, bytes((0x90, 40, 90))),
        midi_event(480, bytes((0x80, 40, 0))),
        midi_event(120, bytes((0x90, 60, 85))),
        midi_event(480, bytes((0x80, 60, 0))),
        midi_event(0, b"\xff\x2f\x00"),
    ]
    track = b"".join(events)
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 1, ticks_per_quarter)
    path.write_bytes(header + b"MTrk" + struct.pack(">I", len(track)) + track)


def write_placeholder_wav(path):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(b"\x00\x00" * 4800)


def write_fixture_zip(path):
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        midi_path = temp_path / "midi_allsinglenotes.mid"
        direct_path = temp_path / "directinput_allsinglenotes.wav"
        mic_path = temp_path / "micamp_allsinglenotes.wav"
        write_midi(midi_path)
        write_placeholder_wav(direct_path)
        write_placeholder_wav(mic_path)
        with zipfile.ZipFile(path, "w") as archive:
            archive.write(midi_path, "P1_singlenotes/midi/midi_allsinglenotes.mid")
            archive.write(direct_path, "P1_singlenotes/audio/directinput/directinput_allsinglenotes.wav")
            archive.write(mic_path, "P1_singlenotes/audio/micamp/micamp_allsinglenotes.wav")


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
import math
from pathlib import Path
import re
import struct
import sys
import wave

PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

out = Path(sys.argv[-1])
match = re.search(r"_([A-G](?:#)?)([0-8])\\.wav", out.name)
if not match:
    raise SystemExit(f"cannot infer note from {out}")
name, octave = match.groups()
midi = (int(octave) + 1) * 12 + PITCH_CLASS[name]
freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
sample_rate = 48000
frames = []
for index in range(int(sample_rate * 0.8)):
    sample = int(math.sin(2.0 * math.pi * freq * index / sample_rate) * 16000)
    frames.append(struct.pack("<h", sample))
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    wav.writeframes(b"".join(frames))
""",
    )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["id", "family", "nsynth_family", "source", "midi", "note", "path", "signature"]:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def run_prepare(base, limit=0, min_samples=1):
    archive = base / "P1_singlenotes.zip"
    output = base / "out"
    ffmpeg = base / "fake-ffmpeg"
    write_fixture_zip(archive)
    write_fake_ffmpeg(ffmpeg)
    prepare_guitar_techs_samples.main([
        "--archive",
        str(archive),
        "--output",
        str(output),
        "--cache-dir",
        str(base / "cache"),
        "--limit",
        str(limit),
        "--min-samples",
        str(min_samples),
        "--ffmpeg",
        str(ffmpeg),
    ])
    return output


def test_guitar_techs_zip_is_prepared_as_guitar_notes():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), min_samples=4)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 4:
            raise AssertionError(f"expected 4 rows, got {len(rows)}")
        families = [row[1] for row in rows]
        nsynth_families = [row[2] for row in rows]
        notes = [row[5] for row in rows]
        sources = [row[3] for row in rows]
        if families != ["guitar"] * 4:
            raise AssertionError(f"expected guitar family rows, got {families}")
        if notes != ["E2", "C4", "E2", "C4"]:
            raise AssertionError(f"expected E2/C4/E2/C4, got {notes}")
        if sources != ["electronic"] * 4:
            raise AssertionError(f"expected coarse electronic source rows, got {sources}")
        if not any(family == "guitar_techs:directinput" for family in nsynth_families):
            raise AssertionError(f"missing directinput detail: {nsynth_families}")
        if not any(family == "guitar_techs:micamp" for family in nsynth_families):
            raise AssertionError(f"missing micamp detail: {nsynth_families}")
        for row in rows:
            if not (output / row[6]).is_file():
                raise AssertionError(f"missing prepared WAV {row[6]}")


def test_limit_is_enforced_before_manifest_write():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), limit=2, min_samples=2)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 2:
            raise AssertionError(f"expected two limited rows, got {len(rows)}")


def test_minimum_sample_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        try:
            run_prepare(base, limit=1, min_samples=3)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            rows = manifest_rows(partial)
            if len(rows) != 1:
                raise AssertionError("partial manifest should contain the limited prepared row")
        else:
            raise AssertionError("expected min-samples failure")


def test_midi_parser_reads_tempos_and_notes():
    with tempfile.TemporaryDirectory() as temp:
        midi = Path(temp) / "notes.mid"
        write_midi(midi)
        notes = prepare_guitar_techs_samples.parse_midi_notes(midi)
        if [note["midi"] for note in notes] != [40, 60]:
            raise AssertionError(f"unexpected MIDI notes: {notes}")
        if not math.isclose(notes[0]["start"], 0.125, abs_tol=0.001):
            raise AssertionError(f"unexpected first note start: {notes[0]['start']}")


def main():
    test_guitar_techs_zip_is_prepared_as_guitar_notes()
    test_limit_is_enforced_before_manifest_write()
    test_minimum_sample_failure_writes_partial_manifest()
    test_midi_parser_reads_tempos_and_notes()
    print("test_prepare_guitar_techs_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
