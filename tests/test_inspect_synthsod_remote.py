#!/usr/bin/env python3
import contextlib
import json
import os
import tempfile
from pathlib import Path

import inspect_synthsod_remote


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


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)


def audio_record(files=None, license_id="cc-by-sa-4.0"):
    return {
        "title": "SynthSOD: Developing an Heterogeneous Dataset for Orchestra Music Source Separation",
        "doi_url": "https://doi.org/10.5281/zenodo.13759492",
        "metadata": {"license": {"id": license_id}, "description": "SynthSOD audio"},
        "files": files
        if files is not None
        else [
            {
                "key": "SynthSOD.zip",
                "size": 45_027_927_968,
                "links": {"self": "https://zenodo.org/api/records/13759492/files/SynthSOD.zip/content"},
            },
            {
                "key": "SynthSOD-sample.zip",
                "size": 2_009_641_471,
                "links": {"self": "https://zenodo.org/api/records/13759492/files/SynthSOD-sample.zip/content"},
            },
        ],
    }


def scores_record(description=None, files=None, license_id="cc-by-4.0"):
    return {
        "title": "SynthSOD aligned scores",
        "doi_url": "https://doi.org/10.5281/zenodo.14971533",
        "metadata": {
            "license": {"id": license_id},
            "description": description
            if description is not None
            else "Text files include the start and end time of every note, the MIDI pitch, and the MIDI instrument.",
        },
        "files": files
        if files is not None
        else [
            {
                "key": "SynthSOD_aligned_scores.zip",
                "size": 16_438_323,
                "links": {
                    "self": "https://zenodo.org/api/records/14971533/files/SynthSOD_aligned_scores.zip/content"
                },
            }
        ],
    }


def run_remote(audio, scores):
    with tempfile.TemporaryDirectory() as temp:
        audio_path = Path(temp) / "audio.json"
        scores_path = Path(temp) / "scores.json"
        write_json(audio_path, audio)
        write_json(scores_path, scores)
        with patched_env(
            {
                "MUSIC_ANALYZER_SYNTHSOD_AUDIO_RECORD_JSON": str(audio_path),
                "MUSIC_ANALYZER_SYNTHSOD_SCORES_RECORD_JSON": str(scores_path),
            }
        ):
            return inspect_synthsod_remote.main()


def test_accepts_current_synthsod_record_shape():
    if run_remote(audio_record(), scores_record()) != 0:
        raise AssertionError("SynthSOD remote metadata should accept current archive shape")


def test_requires_sample_archive():
    files = [file_info for file_info in audio_record()["files"] if file_info["key"] != "SynthSOD-sample.zip"]
    if run_remote(audio_record(files=files), scores_record()) == 0:
        raise AssertionError("SynthSOD remote metadata should require the sample archive")


def test_requires_score_note_semantics():
    if run_remote(audio_record(), scores_record(description="Text files include score notes.")) == 0:
        raise AssertionError("SynthSOD remote metadata should require note timing, pitch, and instrument semantics")


def main():
    test_accepts_current_synthsod_record_shape()
    test_requires_sample_archive()
    test_requires_score_note_semantics()
    print("test_inspect_synthsod_remote: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
