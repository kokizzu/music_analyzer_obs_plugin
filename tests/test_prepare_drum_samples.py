#!/usr/bin/env python3
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_drum_samples


def write_wav(path, frequency=120.0, seconds=0.08, sample_rate=48000):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for index in range(int(seconds * sample_rate)):
        sample = int(math.sin(2.0 * math.pi * frequency * index / sample_rate) * 12000)
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(b"".join(frames))


def rows_by_category(manifest_path):
    rows = {}
    with manifest_path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["category", "path", "duration_seconds", "source"]:
            raise AssertionError("unexpected drum manifest header")
        for line in file:
            category, path, duration, source = line.rstrip("\n").split("\t")
            rows.setdefault(category, []).append((path, duration, source))
    return rows


def make_rar_archive(source_dir, archive_path, member_path):
    rar = shutil.which("rar")
    unrar = shutil.which("unrar")
    if not rar or not unrar:
        return None
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [rar, "a", "-idq", str(archive_path), str(member_path.relative_to(source_dir))],
        cwd=str(source_dir),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return unrar


def test_plain_zip_and_optional_rar_samples():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "plain" / "Kick 01.wav", frequency=80.0)

        zip_member = "pack/Hat Closed 01.wav"
        zip_wav = base / "zip-hat.wav"
        write_wav(zip_wav, frequency=520.0)
        with zipfile.ZipFile(source / "hihat-pack.zip", "w") as archive:
            archive.write(zip_wav, zip_member)
        retained_zip = list(prepare_drum_samples.collect_zip_wavs(source, retain_data=True))
        if not retained_zip or retained_zip[0].data is None:
            raise AssertionError("retain_data ZIP candidates should keep already-read archive bytes")
        lazy_zip = list(prepare_drum_samples.collect_zip_wavs(source, retain_data=False))
        if not lazy_zip or lazy_zip[0].data is not None:
            raise AssertionError("non-retained ZIP candidates should not keep archive bytes")

        rar_source = base / "rar-src"
        rar_member = rar_source / "Snares" / "Snare 01.wav"
        write_wav(rar_member, frequency=250.0)
        unrar = make_rar_archive(rar_source, source / "snare-pack.rar", rar_member)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(source, output, 0, "first", unrar=unrar)
        rows = rows_by_category(manifest_path)

        if counts["kick"] != 1:
            raise AssertionError("plain kick WAV should be copied")
        if counts["hihat"] != 1:
            raise AssertionError("zipped hihat WAV should be copied")
        if rows["hihat"][0][2].count("!") != 1:
            raise AssertionError("ZIP manifest source should identify archive member")

        if unrar:
            if counts["snare"] != 1:
                raise AssertionError("RAR snare WAV should be copied when unrar is available")
            if rows["snare"][0][2].count("!") != 1:
                raise AssertionError("RAR manifest source should identify archive member")


def test_missing_unrar_skips_rar_without_failing():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"
        rar_source = base / "rar-src"
        rar_member = rar_source / "Snares" / "Snare 01.wav"
        write_wav(rar_member, frequency=250.0)
        if not make_rar_archive(rar_source, source / "snare-pack.rar", rar_member):
            return

        prepare_drum_samples.clean_output(output)
        counts, _manifest_path = prepare_drum_samples.copy_samples(source, output, 0, "first", unrar=None)
        if counts["snare"] != 0:
            raise AssertionError("RAR samples should be skipped when no unrar command is configured")


def test_no_archives_mode_skips_archives():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "plain" / "Kick 01.wav", frequency=80.0)

        zip_member = "pack/Snare 01.wav"
        zip_wav = base / "zip-snare.wav"
        write_wav(zip_wav, frequency=250.0)
        with zipfile.ZipFile(source / "snare-pack.zip", "w") as archive:
            archive.write(zip_wav, zip_member)

        prepare_drum_samples.clean_output(output)
        counts, _manifest_path = prepare_drum_samples.copy_samples(
            source, output, 0, "first", unrar=None, include_archives=False
        )

        if counts["kick"] != 1:
            raise AssertionError("plain WAVs should still be copied in no-archives mode")
        if counts["snare"] != 0:
            raise AssertionError("ZIP samples should be skipped in no-archives mode")


def test_hihat_aliases_win_over_generic_cymbal_folder():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "machine" / "Cymbals" / "707oh.wav", frequency=520.0)
        write_wav(source / "machine" / "Cymbals" / "Realch1.wav", frequency=530.0)
        write_wav(source / "machine" / "Cymbals" / "Hat Pedal.wav", frequency=540.0)
        write_wav(source / "machine" / "Cymbals" / "CYMBAL_001.wav", frequency=650.0)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(source, output, 0, "first", unrar=None)
        rows = rows_by_category(manifest_path)
        hihat_sources = "\n".join(row[2] for row in rows.get("hihat", []))
        crash_sources = "\n".join(row[2] for row in rows.get("crash", []))

        if counts["hihat"] != 3:
            raise AssertionError(f"expected three hi-hat aliases, got {counts['hihat']}:\n{hihat_sources}")
        if counts["crash"] != 1:
            raise AssertionError(f"expected generic cymbal to remain crash, got {counts['crash']}:\n{crash_sources}")
        for expected in ("707oh.wav", "Realch1.wav", "Hat Pedal.wav"):
            if expected not in hihat_sources:
                raise AssertionError(f"expected {expected} to be labeled hihat")
        if "CYMBAL_001.wav" not in crash_sources:
            raise AssertionError("expected generic CYMBAL_001.wav to be labeled crash")


def test_spread_selection_uses_later_buckets():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        for index in range(6):
            write_wav(source / "aaa-first" / f"Kick {index:02d}.wav", frequency=80.0 + index)
        write_wav(source / "bbb-second" / "Kick Later.wav", frequency=95.0)
        write_wav(source / "ccc-third" / "Kick Later.wav", frequency=105.0)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(source, output, 3, "spread", unrar=None)
        rows = rows_by_category(manifest_path)
        sources = [row[2] for row in rows["kick"]]

        if counts["kick"] != 3:
            raise AssertionError("spread fixture should honor per-category limit")
        if not any("bbb-second" in source for source in sources):
            raise AssertionError("spread fixture should include later source buckets")
        if not any("ccc-third" in source for source in sources):
            raise AssertionError("spread fixture should include third source bucket")


def main():
    test_plain_zip_and_optional_rar_samples()
    test_missing_unrar_skips_rar_without_failing()
    test_no_archives_mode_skips_archives()
    test_hihat_aliases_win_over_generic_cymbal_folder()
    test_spread_selection_uses_later_buckets()
    print("test_prepare_drum_samples: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
