#!/usr/bin/env python3

import io
import sys
import tempfile
import wave
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_maps_piano_samples as prep


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 4410)
    return buffer.getvalue()


def midi_bytes():
    return (
        b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0"
        b"MTrk\x00\x00\x00\x0c"
        b"\x00\x90\x3c\x40\x81\x70\x80\x3c\x00\x00\xff\x2f\x00"
    )


def add_pair(zf, kind, stem):
    base = f"ENSTDkCl/{kind}/MAPS_{kind}_{stem}_ENSTDkCl"
    zf.writestr(base + ".wav", wav_bytes())
    zf.writestr(base + ".mid", midi_bytes())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive = root / "maps.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            add_pair(zf, "UCHO", "C_M60-M64-M67")
            add_pair(zf, "RAND", "C_M60-M63-M67")
            add_pair(zf, "MUS", "chpn_op10")
            add_pair(zf, "ISOL", "NO_F_S0_M60")
            zf.writestr("ENSTDkCl/UCHO/MAPS_UCHO_missing_midi_ENSTDkCl.wav", wav_bytes())

        out = root / "out"
        args = type("Args", (), {
            "archive": str(archive),
            "output": str(out),
            "limit": 3,
            "min_recordings": 3,
            "kinds": "UCHO,RAND,MUS",
            "refresh": False,
        })()

        count = prep.prepare(args)
        assert count == 3
        metadata = (out / "maestro-v3.0.0.csv").read_text(encoding="utf-8")
        assert "audio_filename" in metadata
        assert "midi_filename" in metadata
        assert "isol" not in metadata.lower()
        assert len(list((out / "maps").rglob("*.wav"))) == 3
        assert len(list((out / "maps").rglob("*.mid"))) == 3

        reused = prep.prepare(args)
        assert reused == 3

    print("test_prepare_maps_piano_samples: ok")


if __name__ == "__main__":
    main()
