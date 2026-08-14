#!/usr/bin/env python3
"""Regression checks for stable SCMS mixed-vocal clip preparation."""

from __future__ import annotations

import sys
import tempfile
import wave
import stat
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_scms_vocal_mix_samples as prepare


def write_wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(44100)
        output.writeframes(b"\0\0" * 44100)


def write_fake_ffmpeg(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import shutil, sys\n"
        "args = sys.argv[1:]\n"
        "shutil.copyfile(args[args.index('-i') + 1], args[-1])\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def write_empty_ffmpeg(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "open(sys.argv[-1], 'wb').write(b'RIFF\\x46\\x00\\x00\\x00WAVEfmt \\x10\\x00\\x00\\x00\\x01\\x00\\x01\\x00\\x44\\xac\\x00\\x00\\x88\\x58\\x01\\x00\\x02\\x00\\x10\\x00LIST\\x1a\\x00\\x00\\x00INFOISFT\\x0e\\x00\\x00\\x00Lavf61.7.100\\x00data\\x00\\x00\\x00\\x00')\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "source" / "SCMS"
        write_wav(root / "audio" / "Artist_01.wav")
        pitch = root / "pitch" / "Artist_01.csv"
        pitch.parent.mkdir(parents=True)
        pitch.write_text("0.000,0\n" + "0.029,440\n" * 12, encoding="utf-8")
        points = prepare.pitch_points(pitch)
        assert prepare.longest_stable_run(points, 8) == (1, 13, 69)
        output = Path(temporary) / "prepared"
        ffmpeg = Path(temporary) / "fake-ffmpeg"
        write_fake_ffmpeg(ffmpeg)
        assert prepare.prepare(root.parent, output, 8, 0.5, 1, 1, str(ffmpeg)) == 1
        manifest = (output / "manifest.tsv").read_text(encoding="utf-8")
        assert "scms_Artist_01_A4" in manifest
        clip = output / "audio" / "scms_Artist_01_A4.wav"
        assert clip.is_file()
        clip.write_bytes(b"malformed")
        assert not prepare.valid_analyzer_wav(clip)
        assert prepare.prepare(root.parent, output, 8, 0.5, 1, 1, str(ffmpeg)) == 1
        assert prepare.valid_analyzer_wav(clip)
        clip.write_bytes(
            b"RIFF\x46\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00"
            b"\x88\x58\x01\x00\x02\x00\x10\x00LIST\x1a\x00\x00\x00INFOISFT\x0e\x00\x00\x00Lavf"
            b"61.7.100\x00data\x00\x00\x00\x00"
        )
        assert not prepare.valid_analyzer_wav(clip)
        empty_ffmpeg = Path(temporary) / "empty-ffmpeg"
        write_empty_ffmpeg(empty_ffmpeg)
        assert not prepare.clip_wav(root / "audio" / "Artist_01.wav", clip, 0, 0.5, str(empty_ffmpeg))
    print("test_prepare_scms_vocal_mix_samples: 9 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
