#!/usr/bin/env python3
import csv
import json
import os
import shutil
import sys

import inspect_medleydb_dataset
from prepare_polyvocal_musicnet_fixture import read_csv_f0_points, points_to_notes
from prepare_slakh_musicnet_fixture import prepare_summed_stem_audio, write_labels


def prepare_track(track, annotation_path, output_root, output_id, ffmpeg):
    try:
        points = read_csv_f0_points(annotation_path)
    except (OSError, csv.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, f"{annotation_path}: {exc}"

    notes = points_to_notes(points, 96)
    if not notes:
        return False, "no usable melody-F0-derived note intervals"

    audio_out = os.path.join(output_root, "train_data", f"{output_id}.wav")
    label_out = os.path.join(output_root, "train_labels", f"{output_id}.csv")
    sample_rate = prepare_summed_stem_audio(track["stems"], audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_medleydb_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspect_medleydb_dataset.resolve_root()
    if not root:
        print(
            "prepare_medleydb_musicnet_fixture: set MUSIC_ANALYZER_MEDLEYDB_ROOT, "
            "MEDLEYDB_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_medleydb_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_tracks = inspect_medleydb_dataset.positive_int_env("MUSIC_ANALYZER_MEDLEYDB_REQUIRED_TRACKS", 20)
    required_melody_tracks = inspect_medleydb_dataset.positive_int_env(
        "MUSIC_ANALYZER_MEDLEYDB_REQUIRED_MELODY_TRACKS", required_tracks
    )
    prepare_tracks = inspect_medleydb_dataset.positive_int_env(
        "MUSIC_ANALYZER_MEDLEYDB_PREPARE_TRACKS", required_melody_tracks
    )
    min_stems = inspect_medleydb_dataset.positive_int_env("MUSIC_ANALYZER_MEDLEYDB_MIN_STEMS", 2)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_MEDLEYDB_FFMPEG") or "ffmpeg"

    tracks = inspect_medleydb_dataset.collect_track_dirs(root)
    annotations = inspect_medleydb_dataset.collect_melody_annotations(
        inspect_medleydb_dataset.candidate_annotation_roots(root)
    )
    complete = sorted(
        (
            track
            for track in tracks.values()
            if track["mix"] and len(track["stems"]) >= min_stems and annotations.get(track["track_id"])
        ),
        key=lambda track: track["track_id"],
    )

    if len(complete) < required_melody_tracks:
        print(
            f"prepare_medleydb_musicnet_fixture: expected at least {required_melody_tracks} "
            f"melody-annotated MedleyDB multitracks, got {len(complete)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    prepared = 0
    failures = []
    for track in complete:
        if prepared >= prepare_tracks:
            break
        annotation_path = sorted(annotations[track["track_id"]])[0]
        ok, error = prepare_track(track, annotation_path, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{track['track_id']}: {error}")

    if prepared < required_tracks:
        print(
            f"prepare_medleydb_musicnet_fixture: expected to prepare {required_tracks} "
            f"MedleyDB tracks, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_medleydb_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_medleydb_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"summed-stem MedleyDB melody recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
