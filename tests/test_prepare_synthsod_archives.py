#!/usr/bin/env python3
import contextlib
import os
import tempfile
import zipfile
from pathlib import Path

import generate_synthsod_fixture
import inspect_synthsod_dataset
import prepare_synthsod_archives


@contextlib.contextmanager
def patched_env(values):
    previous = {}
    missing = object()
    for key, value in values.items():
        previous[key] = os.environ.get(key, missing)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def write_small_fixture(root, piece_count=2):
    for piece in range(1, piece_count + 1):
        piece_id = f"SYNTHSOD_{piece:03d}"
        close_mic = root / "SynthSOD-data" / piece_id / "Close Mic"
        for source_index, source_name in enumerate(generate_synthsod_fixture.SOURCE_NAMES):
            generate_synthsod_fixture.write_wav(
                str(close_mic / f"{source_name}.wav"),
                generate_synthsod_fixture.source_samples(piece - 1, source_index),
            )
        generate_synthsod_fixture.write_score(
            str(root / "SynthSOD-aligned-scores" / f"{piece_id}.txt"),
            piece - 1,
        )


def zip_tree(zip_path, source_root, archive_prefix):
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(source_root)
                archive.write(path, str(archive_prefix / relative))


def run_inspector(audio_root, scores_root, required_pieces):
    with patched_env(
        {
            "MUSIC_ANALYZER_SYNTHSOD_ROOT": str(audio_root),
            "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT": str(scores_root),
            "SYNTHSOD_PATH": None,
            "SYNTHSOD_SCORES_PATH": None,
            "MUSIC_ANALYZER_DATASET_ROOT": None,
            "MUSIC_ANALYZER_SYNTHSOD_REQUIRED_PIECES": str(required_pieces),
        }
    ):
        return inspect_synthsod_dataset.main()


def test_extracts_sample_and_scores_archives_for_existing_gate():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        fixture = base / "fixture"
        write_small_fixture(fixture)
        audio_zip = base / "SynthSOD-sample.zip"
        scores_zip = base / "SynthSOD_aligned_scores.zip"
        zip_tree(audio_zip, fixture / "SynthSOD-data", Path("download") / "SynthSOD-data")
        zip_tree(scores_zip, fixture / "SynthSOD-aligned-scores", Path("scores") / "SynthSOD-aligned-scores")

        out = base / "extracted"
        with patched_env(
            {
                "MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP": str(audio_zip),
                "MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP": str(scores_zip),
                "SYNTHSOD_AUDIO_ZIP": None,
                "SYNTHSOD_SCORES_ZIP": None,
            }
        ):
            if prepare_synthsod_archives.main(["prepare_synthsod_archives.py", str(out)]) != 0:
                raise AssertionError("archive extraction should accept SynthSOD sample and aligned-score zips")

        audio_root = prepare_synthsod_archives.find_audio_root(out)
        scores_root = prepare_synthsod_archives.find_scores_root(out)
        if audio_root.name != "SynthSOD-data":
            raise AssertionError("archive extraction should find the SynthSOD-data root")
        if scores_root.name != "SynthSOD-aligned-scores":
            raise AssertionError("archive extraction should find the aligned-score root")
        if run_inspector(audio_root, scores_root, required_pieces=2) != 0:
            raise AssertionError("extracted SynthSOD archive roots should pass the existing inspector")


def test_requires_archive_environment():
    with tempfile.TemporaryDirectory() as temp:
        with patched_env(
            {
                "MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP": None,
                "MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP": None,
                "SYNTHSOD_AUDIO_ZIP": None,
                "SYNTHSOD_SCORES_ZIP": None,
            }
        ):
            if prepare_synthsod_archives.main(["prepare_synthsod_archives.py", str(Path(temp) / "out")]) == 0:
                raise AssertionError("archive extraction should require explicit archive paths")


def test_rejects_unsafe_archive_members():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        audio_zip = base / "SynthSOD-sample.zip"
        scores_zip = base / "SynthSOD_aligned_scores.zip"
        with zipfile.ZipFile(audio_zip, "w") as archive:
            archive.writestr("../escape.txt", "bad")
        with zipfile.ZipFile(scores_zip, "w") as archive:
            archive.writestr("SynthSOD-aligned-scores/SYNTHSOD_001.txt", "start end pitch instrument\n")

        with patched_env(
            {
                "MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP": str(audio_zip),
                "MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP": str(scores_zip),
            }
        ):
            if prepare_synthsod_archives.main(["prepare_synthsod_archives.py", str(base / "out")]) == 0:
                raise AssertionError("archive extraction should reject unsafe archive members")


def main():
    test_extracts_sample_and_scores_archives_for_existing_gate()
    test_requires_archive_environment()
    test_rejects_unsafe_archive_members()
    print("test_prepare_synthsod_archives: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
