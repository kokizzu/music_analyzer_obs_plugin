#!/usr/bin/env python3
from pathlib import Path
import math
import struct
import sys
import tempfile
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_iowa_zip_samples


def write_executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_fake_curl(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
import shutil
import sys
import urllib.parse

args = sys.argv[1:]
out = args[args.index("-o") + 1]
url = args[-1]
parsed = urllib.parse.urlparse(url)
if parsed.scheme == "file":
    source = urllib.parse.unquote(parsed.path)
else:
    source = urllib.parse.unquote(url)
shutil.copyfile(source, out)
""",
    )


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
from pathlib import Path
import sys

out = Path(sys.argv[-1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(b"fake-wav")
""",
    )


def make_zip(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Bass.pizz.ff.sulE.E1.stereo.aif", b"aif-e1")
        archive.writestr("Bass.pizz.ff.sulE.F1.stereo.aif", b"aif-f1")
        archive.writestr("__MACOSX/._Bass.pizz.ff.sulE.F1.stereo.aif", b"ignored")
        archive.writestr("notes.txt", b"ignored")


def write_sine_wav(path, midi, seconds=0.5, sample_rate=48000):
    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    frames = []
    for index in range(int(seconds * sample_rate)):
        sample = int(math.sin(2.0 * math.pi * freq * index / sample_rate) * 14000)
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(b"".join(frames))


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["id", "family", "nsynth_family", "source", "midi", "note", "path", "signature"]:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def run_prepare(base, min_samples=2, limit=0):
    source_zip = base / "source.zip"
    make_zip(source_zip)
    cache = base / "cache"
    output = base / "out"
    curl = base / "fake-curl"
    ffmpeg = base / "fake-ffmpeg"
    write_fake_curl(curl)
    write_fake_ffmpeg(ffmpeg)
    prepare_iowa_zip_samples.main([
        "--spec",
        f"bass|bass|iowa-test-bass|{source_zip.resolve().as_uri()}",
        "--source-dir",
        str(cache),
        "--output",
        str(output),
        "--limit",
        str(limit),
        "--min-samples",
        str(min_samples),
        "--ffmpeg",
        str(ffmpeg),
        "--curl",
        str(curl),
        "--skip-pitch-check",
    ])
    return output


def test_zip_members_are_prepared_as_bass_notes():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp))
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 2:
            raise AssertionError(f"expected two rows, got {len(rows)}")
        families = [row[1] for row in rows]
        notes = [row[5] for row in rows]
        if families != ["bass", "bass"]:
            raise AssertionError(f"expected bass rows, got {families}")
        if notes != ["E1", "F1"]:
            raise AssertionError(f"expected E1/F1 notes, got {notes}")
        for row in rows:
            if not (output / row[6]).is_file():
                raise AssertionError(f"missing prepared WAV {row[6]}")


def test_limit_is_enforced_before_manifest_write():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), min_samples=1, limit=1)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 1:
            raise AssertionError(f"expected one limited row, got {len(rows)}")


def test_minimum_sample_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        try:
            run_prepare(Path(temp), min_samples=3)
        except SystemExit:
            partial = Path(temp) / "out" / "manifest.tsv.partial"
            rows = manifest_rows(partial)
            if len(rows) != 2:
                raise AssertionError("partial manifest should contain prepared rows")
        else:
            raise AssertionError("expected min-samples failure")


def test_pitch_reference_filter_rejects_neighbor_note():
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "e2.wav"
        write_sine_wav(path, 40)
        if not prepare_iowa_zip_samples.pitch_reference_ok(path, 40):
            raise AssertionError("exact E2 sine should pass pitch reference check")
        if prepare_iowa_zip_samples.pitch_reference_ok(path, 41):
            raise AssertionError("E2 sine should not pass as F2")


def main():
    test_zip_members_are_prepared_as_bass_notes()
    test_limit_is_enforced_before_manifest_write()
    test_minimum_sample_failure_writes_partial_manifest()
    test_pitch_reference_filter_rejects_neighbor_note()
    print("test_prepare_iowa_zip_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
