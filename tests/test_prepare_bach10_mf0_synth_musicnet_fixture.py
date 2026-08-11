#!/usr/bin/env python3

import io
import math
import struct
import sys
import tarfile
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_bach10_mf0_synth_musicnet_fixture as prep


SAMPLE_RATE = 44100


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def wav_bytes(notes):
    samples = [0.0 for _ in range(SAMPLE_RATE)]
    for midi in notes:
        freq = midi_frequency(midi)
        for index in range(len(samples)):
            samples[index] += 0.12 * math.sin(2.0 * math.pi * freq * index / SAMPLE_RATE)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            frames.extend(struct.pack("<h", int(max(-0.95, min(0.95, sample)) * 32767.0)))
        wav.writeframes(bytes(frames))
    return buffer.getvalue()


def f0_csv(midi):
    freq = midi_frequency(midi)
    rows = ["time,frequency"]
    for index in range(10):
        rows.append(f"{index * 0.05:.3f},{freq:.6f}")
    return ("\n".join(rows) + "\n").encode("utf-8")


def add_tar_bytes(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def write_fake_archive(path, pieces=2):
    with tarfile.open(path, "w:gz") as tar:
        for piece in range(1, pieces + 1):
            base = f"{piece:02d}_chorale"
            notes = [60 + piece, 64 + piece, 67 + piece, 72 + piece]
            add_tar_bytes(tar, f"Bach10-mf0-syth/audio_mix/{base}.wav", wav_bytes(notes))
            for suffix, midi in zip(("bassoon", "sax", "clarinet", "violin"), notes):
                add_tar_bytes(
                    tar,
                    f"Bach10-mf0-syth/annotation_stems/{base}_{suffix}.csv",
                    f0_csv(midi),
                )


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive = root / "bach10.tar.gz"
        write_fake_archive(archive, pieces=2)
        out = root / "out"
        args = type("Args", (), {
            "archive": str(archive),
            "source_root": "",
            "output": str(out),
            "limit": 0,
            "min_recordings": 2,
            "refresh": False,
        })()

        count = prep.prepare(args)
        assert count == 2
        assert (out / "train_data" / "1.wav").is_file()
        assert (out / "train_labels" / "1.csv").is_file()
        assert not (out / "train_data" / "01.wav").exists()
        assert not (out / "train_labels" / "01.csv").exists()
        assert len(list((out / "train_data").glob("*.wav"))) == 2
        labels = sorted((out / "train_labels").glob("*.csv"))
        assert len(labels) == 2
        first_label = (out / "train_labels" / "1.csv").read_text(encoding="utf-8")
        assert "start_time,end_time,instrument,note" in first_label
        for midi in (61, 65, 68, 73):
            assert f",{midi}," in first_label

        reused = prep.prepare(args)
        assert reused == 2

        linked_target = root / "external-output"
        linked_output = root / "linked-output"
        linked_output.symlink_to(linked_target, target_is_directory=True)
        linked_args = type("Args", (), {
            "archive": str(archive),
            "source_root": "",
            "output": str(linked_output),
            "limit": 0,
            "min_recordings": 2,
            "refresh": True,
        })()
        linked = prep.prepare(linked_args)
        assert linked == 2
        assert linked_output.is_symlink()
        assert (linked_output / "train_data" / "1.wav").is_file()
        assert (linked_target / "train_labels" / "1.csv").is_file()

        too_many = type("Args", (), {
            "archive": str(archive),
            "source_root": "",
            "output": str(root / "too_many"),
            "limit": 0,
            "min_recordings": 3,
            "refresh": False,
        })()
        try:
            prep.prepare(too_many)
            raise AssertionError("expected insufficient-piece failure")
        except SystemExit as exc:
            assert exc.code

    print("test_prepare_bach10_mf0_synth_musicnet_fixture: ok")


if __name__ == "__main__":
    main()
