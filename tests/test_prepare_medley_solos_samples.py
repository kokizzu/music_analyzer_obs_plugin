#!/usr/bin/env python3

import csv
import io
import shutil
import sys
import tarfile
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_medley_solos_samples as prep


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 4410)
    return buffer.getvalue()


def float_wav_bytes():
    frames = b"\x00\x00\x00\x00" * 441
    fmt = (3).to_bytes(2, "little") + (1).to_bytes(2, "little") + (44100).to_bytes(4, "little") + \
        (176400).to_bytes(4, "little") + (4).to_bytes(2, "little") + (32).to_bytes(2, "little")
    return b"RIFF" + (36 + len(frames)).to_bytes(4, "little") + b"WAVEfmt " + \
        (16).to_bytes(4, "little") + fmt + b"data" + len(frames).to_bytes(4, "little") + frames


def add_tar_file(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        metadata = root / "metadata.csv"
        archive = root / "medley.tar.gz"
        rows = [
            ("test", "distorted electric guitar", "1", "001", "11111111-1111-1111-1111-111111111111"),
            ("test", "piano", "4", "002", "22222222-2222-2222-2222-222222222222"),
            ("test", "female singer", "2", "003", "33333333-3333-3333-3333-333333333333"),
            ("test", "violin", "7", "004", "44444444-4444-4444-4444-444444444444"),
            ("test", "unknown", "9", "005", "55555555-5555-5555-5555-555555555555"),
        ]
        with metadata.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(("subset", "instrument", "instrument_id", "song_id", "uuid4"))
            writer.writerows(rows)

        with tarfile.open(archive, "w:gz") as tar:
            for subset, instrument, instrument_id, _song_id, uuid4 in rows[:4]:
                basename = f"Medley-solos-DB_{subset}-{instrument_id}_{uuid4}.wav"
                data = float_wav_bytes() if instrument == "piano" else wav_bytes()
                add_tar_file(tar, f"Medley-solos-DB/audio/{basename}", data)

        out = root / "out"
        args = type("Args", (), {
            "metadata": str(metadata),
            "archive": str(archive),
            "output": str(out),
            "limit_per_instrument": 1,
            "min_samples": 4,
            "min_counts": "guitar=1,piano=1,vocals=1,other=1",
            "subsets": "test",
            "refresh": False,
            "ffmpeg": shutil.which("ffmpeg") or "ffmpeg",
        })()

        count = prep.prepare(args)
        assert count == 4
        manifest = (out / "manifest.tsv").read_text(encoding="utf-8")
        assert "distorted electric guitar" in manifest
        assert "\tguitar\t" in manifest
        assert "\tpiano\t" in manifest
        assert "\tvocals\t" in manifest
        assert "\tother\t" in manifest
        assert "unknown" not in manifest
        assert len(list((out / "audio").rglob("*.wav"))) == 4
        piano = next((out / "audio" / "piano").glob("*.wav"))
        assert prep.wav_format_tag(piano) == 1

        reused = prep.prepare(args)
        assert reused == 4

        external_output = root / "external-out"
        external_output.mkdir()
        linked_output = root / "linked-out"
        linked_output.symlink_to(external_output, target_is_directory=True)
        args.output = str(linked_output)
        args.refresh = True
        linked_count = prep.prepare(args)
        assert linked_count == 4
        assert linked_output.is_symlink()
        assert (external_output / "manifest.tsv").is_file()
        assert len(list((external_output / "audio").rglob("*.wav"))) == 4

    print("test_prepare_medley_solos_samples: ok")


if __name__ == "__main__":
    main()
