#!/usr/bin/env python3

import struct
import sys
import tempfile
import wave
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_star_drums_samples as prep


def wav_bytes():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.wav"
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(b"\x00\x00" * 44100)
        return path.read_bytes()


def read_midi_track(path):
    data = path.read_bytes()
    assert data[:4] == b"MThd"
    track_offset = data.index(b"MTrk")
    size = struct.unpack(">I", data[track_offset + 4:track_offset + 8])[0]
    return data[track_offset + 8:track_offset + 8 + size]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "star.zip"
        stem = "Song_mix_test_kit_full"
        annotation = (
            "0.000\tBD\t120\n"
            "0.125\tSD\t119\n"
            "0.250\tSS\t96\n"
            "0.375\tCHH\t90\n"
            "0.500\tPHH\t91\n"
            "0.625\tOHH\t92\n"
            "0.750\tCRC\t93\n"
            "0.875\tRD\t94\n"
            "1.000\tHT\t95\n"
            "1.125\tMT\t96\n"
            "1.250\tLT\t97\n"
            "1.375\tCL\t98\n"
            "1.500\tCB\t99\n"
            "1.625\tTB\t100\n"
        )
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr(f"star_drums_preview/data/test/annotation/{stem}.txt", annotation)
            zip_file.writestr(f"star_drums_preview/data/test/audio/mix/{stem}.wav", wav_bytes())

        out = Path(tmp) / "out"
        args = type("Args", (), {
            "archive": str(archive),
            "output": str(out),
            "audio_flavor": "mix",
            "limit": 0,
            "min_recordings": 1,
            "ffmpeg": "ffmpeg",
            "refresh": False,
        })()
        count = prep.prepare(args)
        assert count == 1
        metadata = (out / "e-gmd-v1.0.0.csv").read_text(encoding="utf-8")
        assert "test_Song_mix_test_kit_full_mix" in metadata
        assert (out / "audio/test_Song_mix_test_kit_full_mix.wav").is_file()
        track = read_midi_track(out / "midi/test_Song_mix_test_kit_full_mix.mid")
        for note in (36, 38, 37, 42, 44, 46, 49, 51, 50, 47, 43):
            assert bytes([0x99, note]) in track
        for unsupported in (39, 56, 54):
            assert bytes([0x99, unsupported]) not in track

        reused = prep.prepare(args)
        assert reused == 1

        linked_target = Path(tmp) / "external-star-output"
        linked_target.mkdir()
        (linked_target / "stale.txt").write_text("obsolete", encoding="utf-8")
        linked_out = Path(tmp) / "linked-out"
        linked_out.symlink_to(linked_target, target_is_directory=True)
        linked_args = type("Args", (), {
            "archive": str(archive),
            "output": str(linked_out),
            "audio_flavor": "mix",
            "limit": 0,
            "min_recordings": 1,
            "ffmpeg": "ffmpeg",
            "refresh": True,
        })()
        linked_count = prep.prepare(linked_args)
        assert linked_count == 1
        assert linked_out.is_symlink()
        assert not (linked_target / "stale.txt").exists()
        assert (linked_target / "e-gmd-v1.0.0.csv").is_file()

    print("test_prepare_star_drums_samples: ok")


if __name__ == "__main__":
    main()
