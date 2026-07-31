#!/usr/bin/env python3
import concurrent.futures
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
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


def test_cli_preserves_existing_output_until_manifest_replace():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"
        stale_file = output / "stale.txt"
        stale_file.parent.mkdir(parents=True, exist_ok=True)
        stale_file.write_text("keep", encoding="utf-8")

        examples = {
            "kick": "Kick 01.wav",
            "snare": "Snare 01.wav",
            "hihat": "Hat Closed 01.wav",
            "crash": "Crash 01.wav",
            "tom": "Tom 01.wav",
            "ride": "Ride 01.wav",
            "rim": "Rim Shot 01.wav",
        }
        for index, (category, filename) in enumerate(examples.items()):
            write_wav(source / category / filename, frequency=90.0 + index * 40.0)

        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "prepare_drum_samples.py"),
                "--source",
                str(source),
                "--output",
                str(output),
                "--limit-per-category",
                "1",
                "--no-archives",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if not stale_file.is_file():
            raise AssertionError("CLI preparation should not delete an existing output directory up front")
        if (output / "manifest.tsv.tmp").exists():
            raise AssertionError("temporary drum manifest should be atomically replaced")
        rows = rows_by_category(output / "manifest.tsv")
        for category in examples:
            if len(rows.get(category, [])) != 1:
                raise AssertionError(f"expected one prepared {category} row")


def test_concurrent_manifest_writes_use_distinct_temporary_files():
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp)
        manifest_a = [("kick", "kick/a.wav", "0.100000", "a")]
        manifest_b = [("snare", "snare/b.wav", "0.100000", "b")]
        barrier = threading.Barrier(2)
        original_replace = Path.replace

        def delayed_replace(path, target):
            if Path(target).name == "manifest.tsv":
                barrier.wait(timeout=5.0)
            return original_replace(path, target)

        Path.replace = delayed_replace
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(prepare_drum_samples.write_manifest, output, manifest_a),
                    pool.submit(prepare_drum_samples.write_manifest, output, manifest_b),
                ]
                for future in futures:
                    future.result(timeout=5.0)
        finally:
            Path.replace = original_replace

        if not (output / "manifest.tsv").is_file():
            raise AssertionError("concurrent writers should leave a completed manifest")
        leftovers = list(output.glob("*.tmp")) + list(output.glob(".*.tmp"))
        if leftovers:
            raise AssertionError(f"temporary manifest files should be replaced: {leftovers}")


def test_cli_reuses_complete_manifest_until_refresh():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        examples = {
            "kick": "Kick 01.wav",
            "snare": "Snare 01.wav",
            "hihat": "Hat Closed 01.wav",
            "crash": "Crash 01.wav",
            "tom": "Tom 01.wav",
            "ride": "Ride 01.wav",
            "rim": "Rim Shot 01.wav",
        }
        for index, (category, filename) in enumerate(examples.items()):
            write_wav(source / category / filename, frequency=90.0 + index * 40.0)

        command = [
            sys.executable,
            str(ROOT / "scripts" / "prepare_drum_samples.py"),
            "--source",
            str(source),
            "--output",
            str(output),
            "--limit-per-category",
            "1",
            "--no-archives",
        ]
        first = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        refreshed = subprocess.run(
            command + ["--refresh"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if "wrote" not in first.stdout:
            raise AssertionError(f"first run should prepare samples, got: {first.stdout}")
        if "reused" not in second.stdout:
            raise AssertionError(f"second run should reuse complete manifest, got: {second.stdout}")
        if "wrote" not in refreshed.stdout or "reused" in refreshed.stdout:
            raise AssertionError(f"refresh run should rebuild samples, got: {refreshed.stdout}")


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


def test_tom_label_requires_real_tom_token():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "CustomDMX" / "DMX808_Conga_001.wav", frequency=180.0)
        write_wav(source / "CustomDMX" / "DMX808_Clave1_A.wav", frequency=700.0)
        write_wav(source / "Sequential Circuits TOM" / "Clap.wav", frequency=900.0)
        write_wav(source / "kit" / "H_Tom_01.wav", frequency=160.0)
        write_wav(source / "kit" / "Tom Low.wav", frequency=130.0)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(source, output, 0, "first", unrar=None)
        rows = rows_by_category(manifest_path)
        tom_sources = "\n".join(row[2] for row in rows.get("tom", []))

        if counts["tom"] != 2:
            raise AssertionError(f"expected only real tom tokens to be labeled tom, got {counts['tom']}:\n{tom_sources}")
        for unexpected in ("CustomDMX", "Clap.wav", "Conga", "Clave"):
            if unexpected in tom_sources:
                raise AssertionError(f"unsupported percussion should not be labeled tom: {unexpected}")
        for expected in ("H_Tom_01.wav", "Tom Low.wav"):
            if expected not in tom_sources:
                raise AssertionError(f"expected {expected} to remain labeled tom")


def test_side_stick_aliases_win_over_snare_folder():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "kit" / "Snaredrums" / "Sideststick.wav", frequency=420.0)
        write_wav(source / "kit" / "Snaredrums" / "Side-Stick 01.wav", frequency=430.0)
        write_wav(source / "kit" / "Snaredrums" / "Snare 01.wav", frequency=260.0)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(source, output, 0, "first", unrar=None)
        rows = rows_by_category(manifest_path)
        rim_sources = "\n".join(row[2] for row in rows.get("rim", []))
        snare_sources = "\n".join(row[2] for row in rows.get("snare", []))

        if counts["rim"] != 2:
            raise AssertionError(f"expected side-stick aliases to be labeled rim, got {counts['rim']}:\n{rim_sources}")
        if counts["snare"] != 1:
            raise AssertionError(f"expected only plain snare to be labeled snare, got {counts['snare']}:\n{snare_sources}")
        for expected in ("Sideststick.wav", "Side-Stick 01.wav"):
            if expected not in rim_sources:
                raise AssertionError(f"expected {expected} to be labeled rim")
        if "Sideststick.wav" in snare_sources or "Side-Stick 01.wav" in snare_sources:
            raise AssertionError(f"side-stick aliases should not be labeled snare:\n{snare_sources}")


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


def test_source_filter_limits_candidate_selection():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "Roland TR-909 Drum Samples" / "BT0A0D0.WAV", frequency=80.0)
        write_wav(source / "Roland TR-909 Drum Samples" / "ST0T0S0.WAV", frequency=250.0)
        write_wav(source / "Other Kit" / "Kick 01.wav", frequency=90.0)
        write_wav(source / "Other Kit" / "Snare 01.wav", frequency=260.0)

        prepare_drum_samples.clean_output(output)
        counts, manifest_path = prepare_drum_samples.copy_samples(
            source,
            output,
            0,
            "spread",
            unrar=None,
            source_filter=re.compile("Roland TR-909", re.I),
        )
        rows = rows_by_category(manifest_path)
        sources = "\n".join(row[2] for category_rows in rows.values() for row in category_rows)

        if counts["kick"] != 1 or counts["snare"] != 1:
            raise AssertionError(f"expected filtered 909 kick/snare rows, got {counts}")
        if "Other Kit" in sources:
            raise AssertionError(f"source filter should exclude other kits:\n{sources}")
        if "Roland TR-909 Drum Samples" not in sources:
            raise AssertionError(f"source filter should keep Roland TR-909 rows:\n{sources}")


def test_cli_filter_rebuilds_mismatched_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"
        examples = {
            "kick": "Kick 01.wav",
            "snare": "Snare 01.wav",
            "hihat": "Hat Closed 01.wav",
            "crash": "Crash 01.wav",
            "tom": "Tom 01.wav",
            "ride": "Ride 01.wav",
            "rim": "Rim Shot 01.wav",
        }

        for index, filename in enumerate(examples.values()):
            write_wav(source / "Kit A" / filename, frequency=90.0 + index * 40.0)
            write_wav(source / "Kit B" / filename, frequency=95.0 + index * 40.0)

        command = [
            sys.executable,
            str(ROOT / "scripts" / "prepare_drum_samples.py"),
            "--source",
            str(source),
            "--output",
            str(output),
            "--limit-per-category",
            "1",
            "--selection",
            "spread",
            "--no-archives",
        ]
        first = subprocess.run(command + ["--source-filter", "Kit A"], check=True, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.run(command + ["--source-filter", "Kit B"], check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rows = rows_by_category(output / "manifest.tsv")
        sources = "\n".join(row[2] for category_rows in rows.values() for row in category_rows)

        if "wrote" not in first.stdout:
            raise AssertionError(f"first filtered run should write samples, got: {first.stdout}")
        if "wrote" not in second.stdout or "reused" in second.stdout:
            raise AssertionError(f"mismatched filter should rebuild manifest, got: {second.stdout}")
        if "Kit A" in sources or "Kit B" not in sources:
            raise AssertionError(f"rebuilt manifest should contain only Kit B rows:\n{sources}")


def test_cli_unlimited_cache_rebuilds_when_source_or_filter_expands():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"
        examples = {
            "kick": "Kick 01.wav",
            "snare": "Snare 01.wav",
            "hihat": "Hat Closed 01.wav",
            "crash": "Crash 01.wav",
            "tom": "Tom 01.wav",
            "ride": "Ride 01.wav",
            "rim": "Rim Shot 01.wav",
        }

        for index, filename in enumerate(examples.values()):
            write_wav(source / "Kit A" / filename, frequency=90.0 + index * 40.0)
            write_wav(source / "Kit B" / filename, frequency=95.0 + index * 40.0)

        command = [
            sys.executable,
            str(ROOT / "scripts" / "prepare_drum_samples.py"),
            "--source",
            str(source),
            "--output",
            str(output),
            "--limit-per-category",
            "0",
            "--selection",
            "spread",
            "--no-archives",
        ]

        first = subprocess.run(command + ["--source-filter", "Kit A"], check=True, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.run(command + ["--source-filter", "Kit A"], check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        broadened = subprocess.run(command + ["--source-filter", "Kit A|Kit B"], check=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        rows = rows_by_category(output / "manifest.tsv")
        if "wrote" not in first.stdout:
            raise AssertionError(f"first unlimited run should write samples, got: {first.stdout}")
        if "reused" not in second.stdout:
            raise AssertionError(f"unchanged unlimited run should reuse metadata, got: {second.stdout}")
        if "wrote" not in broadened.stdout or "reused" in broadened.stdout:
            raise AssertionError(f"broader unlimited filter should rebuild, got: {broadened.stdout}")
        if not (output / "manifest.meta.json").is_file():
            raise AssertionError("unlimited cache reuse should be guarded by manifest metadata")
        for category in examples:
            if len(rows.get(category, [])) != 2:
                raise AssertionError(f"broader filter should include both kits for {category}: {rows.get(category)}")

        write_wav(source / "Kit B" / "Kick Extra.wav", frequency=120.0)
        changed_source = subprocess.run(command + ["--source-filter", "Kit A|Kit B"], check=True, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rows = rows_by_category(output / "manifest.tsv")
        if "wrote" not in changed_source.stdout or "reused" in changed_source.stdout:
            raise AssertionError(f"changed unlimited source should rebuild, got: {changed_source.stdout}")
        if len(rows.get("kick", [])) != 3:
            raise AssertionError(f"changed unlimited source should include the new kick: {rows.get('kick')}")


def test_cli_audit_reports_candidate_and_selected_counts_without_writing():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        output = base / "out"

        write_wav(source / "kit-a" / "Kick 01.wav", frequency=80.0)
        write_wav(source / "kit-b" / "Kick 02.wav", frequency=90.0)
        write_wav(source / "kit-b" / "Clap 01.wav", frequency=900.0)

        zip_member = "pack/Snare 01.wav"
        zip_wav = base / "zip-snare.wav"
        write_wav(zip_wav, frequency=250.0)
        with zipfile.ZipFile(source / "snare-pack.zip", "w") as archive:
            archive.write(zip_wav, zip_member)

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "prepare_drum_samples.py"),
                "--source",
                str(source),
                "--output",
                str(output),
                "--limit-per-category",
                "1",
                "--selection",
                "spread",
                "--audit",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        expected_counts = "kick=2 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=0"
        expected_selected = "kick=1 snare=1 hihat=0 crash=0 tom=0 ride=0 rim=0"
        if "prepare_drum_samples audit: candidates=3 plain=2 zip=1 rar=0" not in completed.stdout:
            raise AssertionError(f"unexpected audit summary:\n{completed.stdout}")
        if f"candidate counts {expected_counts}" not in completed.stdout:
            raise AssertionError(f"unexpected candidate counts:\n{completed.stdout}")
        if f"selected counts limit=1 selection=spread {expected_selected}" not in completed.stdout:
            raise AssertionError(f"unexpected selected counts:\n{completed.stdout}")
        if output.exists():
            raise AssertionError("audit mode should not create or modify the output fixture directory")


def main():
    test_plain_zip_and_optional_rar_samples()
    test_missing_unrar_skips_rar_without_failing()
    test_no_archives_mode_skips_archives()
    test_cli_preserves_existing_output_until_manifest_replace()
    test_concurrent_manifest_writes_use_distinct_temporary_files()
    test_cli_reuses_complete_manifest_until_refresh()
    test_hihat_aliases_win_over_generic_cymbal_folder()
    test_tom_label_requires_real_tom_token()
    test_side_stick_aliases_win_over_snare_folder()
    test_spread_selection_uses_later_buckets()
    test_source_filter_limits_candidate_selection()
    test_cli_filter_rebuilds_mismatched_manifest()
    test_cli_unlimited_cache_rebuilds_when_source_or_filter_expands()
    test_cli_audit_reports_candidate_and_selected_counts_without_writing()
    print("test_prepare_drum_samples: 14 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
