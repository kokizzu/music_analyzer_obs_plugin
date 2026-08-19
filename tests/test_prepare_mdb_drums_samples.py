#!/usr/bin/env python3

import struct
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_mdb_drums_samples as prep


def write_wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 44100)


def read_midi_events(path):
    data = path.read_bytes()
    assert data[:4] == b"MThd"
    track_offset = data.index(b"MTrk")
    size = struct.unpack(">I", data[track_offset + 4:track_offset + 8])[0]
    track = data[track_offset + 8:track_offset + 8 + size]
    return track


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "MDB Drums"
        write_wav(root / "audio/drum_only/MusicDelta_Test_Drum.wav")
        write_wav(root / "audio/full_mix/MusicDelta_Test_MIX.wav")
        annotation = root / "annotations/subclass/MusicDelta_Test_subclass.txt"
        annotation.parent.mkdir(parents=True, exist_ok=True)
        annotation.write_text(
            "0.000000 \t KD \n"
            "0.250000 \t SD \n"
            "0.500000 \t SST \n"
            "0.750000 \t CHH \n"
            "1.000000 \t OHH \n"
            "1.250000 \t CRC \n"
            "1.500000 \t RDC \n"
            "1.750000 \t LFT \n"
            "2.000000 \t TMB \n",
            encoding="utf-8",
        )

        entries = prep.tree_entries(str(root), {}, 1.0)
        assert [track["id"] for track in prep.discover_tracks(entries, "drum_only")] == [
            track["id"] for track in prep.discover_tracks(entries, "full_mix")
        ]

        out = Path(tmp) / "out"
        args = type("Args", (), {
            "output": str(out),
            "source_root": str(root),
            "tree_json": "",
            "audio_flavor": "full_mix",
            "limit": 0,
            "min_recordings": 1,
            "retries": 1,
            "timeout": 5.0,
            "refresh": False,
        })()
        count = prep.prepare(args)
        assert count == 1
        metadata = (out / "e-gmd-v1.0.0.csv").read_text(encoding="utf-8")
        assert "MusicDelta_Test,audio/MusicDelta_Test.wav,midi/MusicDelta_Test.mid" in metadata
        assert (out / "audio/MusicDelta_Test.wav").is_file()
        midi_track = read_midi_events(out / "midi/MusicDelta_Test.mid")
        for note in (36, 38, 37, 42, 46, 49, 51, 41):
            assert bytes([0x99, note, 96]) in midi_track
        assert bytes([0x99, 54, 96]) not in midi_track

        reused = prep.prepare(args)
        assert reused == 1
        args.refresh = True
        refreshed = prep.prepare(args)
        assert refreshed == 1

    print("test_prepare_mdb_drums_samples: ok")


if __name__ == "__main__":
    main()
