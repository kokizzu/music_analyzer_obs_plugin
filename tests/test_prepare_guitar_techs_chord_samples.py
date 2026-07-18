#!/usr/bin/env python3

from pathlib import Path
import struct
import sys
import tempfile
import wave
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_guitar_techs_chord_samples


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


def write_chord_midi(path):
    ticks_per_quarter = 480
    events = [
        midi_event(0, b"\xff\x51\x03\x07\xa1\x20"),
        midi_event(120, bytes((0x90, 48, 92))),
        midi_event(0, bytes((0x90, 52, 90))),
        midi_event(0, bytes((0x90, 55, 88))),
        midi_event(480, bytes((0x80, 48, 0))),
        midi_event(0, bytes((0x80, 52, 0))),
        midi_event(0, bytes((0x80, 55, 0))),
        midi_event(120, bytes((0x90, 50, 91))),
        midi_event(0, bytes((0x90, 54, 89))),
        midi_event(0, bytes((0x90, 57, 87))),
        midi_event(480, bytes((0x80, 50, 0))),
        midi_event(0, bytes((0x80, 54, 0))),
        midi_event(0, bytes((0x80, 57, 0))),
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
        wav.writeframes(b"\x00\x00" * 48000 * 3)


def write_fixture_zip(path):
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        midi_path = temp_path / "midi_chords.mid"
        direct_path = temp_path / "directinput_chords.wav"
        mic_path = temp_path / "micamp_chords.wav"
        write_chord_midi(midi_path)
        write_placeholder_wav(direct_path)
        write_placeholder_wav(mic_path)
        with zipfile.ZipFile(path, "w") as archive:
            archive.write(midi_path, "P1_chords/midi/midi_chords.mid")
            archive.write(direct_path, "P1_chords/audio/directinput/directinput_chords.wav")
            archive.write(mic_path, "P1_chords/audio/micamp/micamp_chords.wav")


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
from pathlib import Path
import sys
import wave

out = Path(sys.argv[-1])
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(48000)
    wav.writeframes(b"\\x00\\x00" * 48000)
""",
    )


def read_manifest(path):
    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                rows.append(line.split("\t"))
    return rows


def run_prepare(base, limit=0, min_samples=1):
    archive = base / "P1_chords.zip"
    output = base / "out"
    ffmpeg = base / "fake-ffmpeg"
    write_fixture_zip(archive)
    write_fake_ffmpeg(ffmpeg)
    prepare_guitar_techs_chord_samples.main([
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


def test_guitar_techs_chords_are_prepared_as_guitarset_manifest():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), min_samples=4)
        rows = read_manifest(output / "manifest.tsv")
        audio_rows = [row for row in rows if row[0] == "AUDIO"]
        note_rows = [row for row in rows if row[0] == "NOTE"]
        if len(audio_rows) != 4:
            raise AssertionError(f"expected four chord clips, got {len(audio_rows)}")
        if len(note_rows) != 12:
            raise AssertionError(f"expected twelve note rows, got {len(note_rows)}")
        for row in audio_rows:
            if not Path(row[2]).is_file():
                raise AssertionError(f"missing prepared WAV {row[2]}")
        first_clip_notes = [int(row[4]) for row in note_rows if row[1] == audio_rows[0][1]]
        if first_clip_notes != [48, 52, 55]:
            raise AssertionError(f"expected C major note rows, got {first_clip_notes}")


def test_limit_is_enforced_after_candidate_spread():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), limit=2, min_samples=2)
        rows = read_manifest(output / "manifest.tsv")
        audio_rows = [row for row in rows if row[0] == "AUDIO"]
        if len(audio_rows) != 2:
            raise AssertionError(f"expected two limited clips, got {len(audio_rows)}")


def test_minimum_sample_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        try:
            run_prepare(base, limit=1, min_samples=3)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            rows = read_manifest(partial)
            audio_rows = [row for row in rows if row[0] == "AUDIO"]
            if len(audio_rows) != 1:
                raise AssertionError("partial manifest should contain the limited prepared clip")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_guitar_techs_chords_are_prepared_as_guitarset_manifest()
    test_limit_is_enforced_after_candidate_spread()
    test_minimum_sample_failure_writes_partial_manifest()
    print("test_prepare_guitar_techs_chord_samples: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
