#!/usr/bin/env python3
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_text(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as input_file:
        return input_file.read()


def load_catalog():
    with open(os.path.join(ROOT, "tests", "real_dataset_catalog.json"), "r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def fail(message):
    print(f"inspect_real_goal_coverage: {message}", file=sys.stderr)
    return 1


def require(text, needle, context):
    if needle not in text:
        return f"{context}: missing `{needle}`"
    return ""


def dataset_by_id(catalog, dataset_id):
    for dataset in catalog.get("datasets", []):
        if dataset.get("id") == dataset_id:
            return dataset
    return None


def main():
    try:
        catalog = load_catalog()
        makefile = read_text("Makefile")
        readme = read_text("README.md")
        docs = read_text("docs/real_audio_dataset_candidates.md")
        urmp_harness = read_text("tests/analyzer_urmp.cpp")
        urmp_inspector = read_text("tests/inspect_urmp_dataset.py")
        musicnet_harness = read_text("tests/analyzer_musicnet.cpp")
        multtipop_harness = read_text("tests/analyzer_multtipop.cpp")
        goal_gate = read_text("tests/run_real_goal_gate.py")
        multtipop_inspector = read_text("tests/inspect_multtipop_dataset.py")
        spheres_inspector = read_text("tests/inspect_spheres_dataset.py")
    except (OSError, json.JSONDecodeError) as exc:
        return fail(str(exc))

    target_minimum = int(catalog.get("criteria", {}).get("target_minimum_pieces", 20))
    urmp = dataset_by_id(catalog, "urmp")
    musicnet = dataset_by_id(catalog, "musicnet")
    multtipop = dataset_by_id(catalog, "multtipop")
    medleydb = dataset_by_id(catalog, "medleydb")
    spheres = dataset_by_id(catalog, "spheres")
    if not urmp:
        return fail("catalog missing URMP")
    if not musicnet:
        return fail("catalog missing MusicNet")
    if not multtipop:
        return fail("catalog missing MulTTiPop")
    if not medleydb:
        return fail("catalog missing MedleyDB")
    if not spheres:
        return fail("catalog missing Spheres")

    problems = []
    if urmp.get("piece_count", 0) < target_minimum:
        problems.append("URMP must provide at least the 20-piece target")
    if not (urmp.get("real_audio") and urmp.get("isolated_sources") and urmp.get("assembled_mix")):
        problems.append("URMP must remain the direct-fit real multitrack source")
    if not urmp.get("aligned_symbolic_truth"):
        problems.append("URMP must keep aligned note/MIDI truth")
    if urmp.get("automation_target") != "test-real-multitrack-20":
        problems.append("URMP automation target must remain test-real-multitrack-20")
    if musicnet.get("automation_target") != "test-real-musicnet-20":
        problems.append("MusicNet automation target must remain test-real-musicnet-20")
    if multtipop.get("automation_target") != "inspect-real-multtipop":
        problems.append("MulTTiPop automation target must remain inspect-real-multtipop")
    if medleydb.get("automation_target") != "inspect-real-medleydb":
        problems.append("MedleyDB automation target must remain inspect-real-medleydb")
    if spheres.get("automation_target") != "inspect-real-spheres":
        problems.append("Spheres automation target must remain inspect-real-spheres")

    for text, needle, context in (
        (makefile, "test-real-goal-20", "Makefile combined real-data target"),
        (makefile, "inspect-real-goal-20", "Makefile combined real-data preflight"),
        (makefile, "test-real-goal-fixture", "Makefile combined fixture target"),
        (makefile, "tests/run_real_goal_gate.py inspect-20", "Makefile combined fixture preflight"),
        (makefile, "tests/inspect_urmp_dataset.py", "Makefile URMP preflight audit dependency"),
        (makefile, "tests/generate_musicnet_fixture.py", "Makefile MusicNet fixture"),
        (makefile, "tests/generate_medleydb_fixture.py", "Makefile MedleyDB fixture"),
        (makefile, "tests/generate_multtipop_fixture.py", "Makefile MulTTiPop fixture"),
        (makefile, "tests/generate_spheres_fixture.py", "Makefile Spheres fixture"),
        (makefile, "inspect-real-multtipop", "Makefile optional MulTTiPop preflight"),
        (makefile, "test-real-multtipop-20", "Makefile optional MulTTiPop analyzer gate"),
        (makefile, "$(BUILD_DIR)/analyzer_multtipop", "Makefile MulTTiPop analyzer binary"),
        (makefile, "inspect-real-spheres", "Makefile optional Spheres preflight"),
        (goal_gate, "test-real-multitrack-20", "combined gate required URMP target"),
        (goal_gate, "inspect-real-multitrack-20", "combined preflight required URMP target"),
        (goal_gate, "test-real-musicnet-20", "combined gate optional MusicNet target"),
        (goal_gate, "inspect-real-musicnet", "combined preflight optional MusicNet target"),
        (goal_gate, "inspect-real-medleydb", "combined gate optional MedleyDB target"),
        (goal_gate, "configured_multtipop", "combined gate optional MulTTiPop root detection"),
        (goal_gate, "inspect-real-multtipop", "combined gate optional MulTTiPop target"),
        (goal_gate, "multtipop_audio_configured", "combined gate optional MulTTiPop audio detection"),
        (goal_gate, "test-real-multtipop-20", "combined gate optional MulTTiPop analyzer target"),
        (goal_gate, "configured_spheres", "combined gate optional Spheres root detection"),
        (goal_gate, "inspect-real-spheres", "combined gate optional Spheres target"),
        (urmp_harness, "summed separated tracks", "URMP summed-stem playback check"),
        (urmp_harness, "provided mix", "URMP provided-mix check"),
        (urmp_harness, "stateful summed separated-track mix", "URMP stateful summed-mix check"),
        (urmp_harness, "range_summary(source_tracks, \"source tracks\")", "URMP source-track coverage report"),
        (urmp_harness, "source_track_stats.count == tested_pieces", "URMP source-track coverage assertion"),
        (urmp_harness, "active tracks min/avg/max", "URMP window-density report"),
        (urmp_harness, "chord hits", "URMP chord recall report"),
        (urmp_inspector, "matched_track_stats.summary", "URMP preflight track-density report"),
        (urmp_inspector, "candidate active tracks", "URMP preflight active-density report"),
        (urmp_inspector, "candidate pitch classes", "URMP preflight pitch-class density report"),
        (urmp_inspector, "MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW", "URMP preflight active-track threshold"),
        (urmp_inspector, "MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW", "URMP preflight pitch-class threshold"),
        (musicnet_harness, "active instruments min/avg/max", "MusicNet multi-instrument report"),
        (musicnet_harness, "chord hits", "MusicNet chord recall report"),
        (multtipop_inspector, "midi note parts", "MulTTiPop MIDI part-density report"),
        (multtipop_inspector, "MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO", "MulTTiPop optional audio threshold"),
        (multtipop_inspector, "valid_youtube_metadata", "MulTTiPop YouTube timing validation"),
        (multtipop_harness, "read_multtipop_midi", "MulTTiPop aligned-MIDI parser"),
        (multtipop_harness, "MulTTiPop real-pop pitch-class recall", "MulTTiPop real-audio recall gate"),
        (multtipop_harness, "chord hits", "MulTTiPop chord recall report"),
        (spheres_inspector, "range_summary(reconstructable_folder_counts, 'reconstructable folders')", "Spheres stem-layout coverage report"),
        (spheres_inspector, "MUSIC_ANALYZER_SPHERES_REQUIRED_PIECES", "Spheres preflight piece threshold"),
        (readme, "make test-real-goal-20", "README combined gate instructions"),
        (readme, "make inspect-real-goal-20", "README combined preflight instructions"),
        (readme, "make inspect-real-multtipop", "README MulTTiPop preflight instructions"),
        (readme, "make test-real-multtipop-20", "README MulTTiPop analyzer instructions"),
        (readme, "make inspect-real-spheres", "README Spheres preflight instructions"),
        (docs, "make test-real-goal-20", "dataset docs combined gate instructions"),
        (docs, "make inspect-real-goal-20", "dataset docs combined preflight instructions"),
        (docs, "make inspect-real-multtipop", "dataset docs MulTTiPop preflight instructions"),
        (docs, "make test-real-multtipop-20", "dataset docs MulTTiPop analyzer instructions"),
        (docs, "make inspect-real-spheres", "dataset docs Spheres preflight instructions"),
        (docs, "MulTTiPop", "dataset docs MulTTiPop candidate"),
        (docs, "The Spheres Dataset", "dataset docs Spheres candidate"),
        (docs, "URMP should be the first automated target", "dataset docs URMP priority"),
    ):
        problem = require(text, needle, context)
        if problem:
            problems.append(problem)

    if problems:
        for problem in problems:
            print(f"inspect_real_goal_coverage: {problem}", file=sys.stderr)
        return 1

    print(
        "inspect_real_goal_coverage: "
        "catalog=URMP+MusicNet+MedleyDB+MulTTiPop+Spheres, target=test-real-goal-20, "
        "fixture=URMP+MusicNet+MedleyDB+MulTTiPop-audio+Spheres, summed_mix=yes, chord_checks=yes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
