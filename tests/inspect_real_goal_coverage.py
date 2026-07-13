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
        bach10_fixture = read_text("tests/generate_bach10_fixture.py")
        direct_fit_small_fixture = read_text("tests/generate_direct_fit_small_fixture.py")
        musicnet_harness = read_text("tests/analyzer_musicnet.cpp")
        multtipop_harness = read_text("tests/analyzer_multtipop.cpp")
        maestro_harness = read_text("tests/analyzer_maestro.cpp")
        egmd_harness = read_text("tests/analyzer_egmd.cpp")
        goal_gate = read_text("tests/run_real_goal_gate.py")
        multtipop_inspector = read_text("tests/inspect_multtipop_dataset.py")
        spheres_inspector = read_text("tests/inspect_spheres_dataset.py")
        guitarset_inspector = read_text("tests/inspect_guitarset_dataset.py")
    except (OSError, json.JSONDecodeError) as exc:
        return fail(str(exc))

    target_minimum = int(catalog.get("criteria", {}).get("target_minimum_pieces", 20))
    urmp = dataset_by_id(catalog, "urmp")
    bach10 = dataset_by_id(catalog, "bach10")
    trios = dataset_by_id(catalog, "trios")
    wwq = dataset_by_id(catalog, "wwq")
    phenicx = dataset_by_id(catalog, "phenicx_anechoic")
    musicnet = dataset_by_id(catalog, "musicnet")
    multtipop = dataset_by_id(catalog, "multtipop")
    medleydb = dataset_by_id(catalog, "medleydb")
    spheres = dataset_by_id(catalog, "spheres")
    guitarset = dataset_by_id(catalog, "guitarset")
    maestro = dataset_by_id(catalog, "maestro")
    egmd = dataset_by_id(catalog, "e_gmd")
    if not urmp:
        return fail("catalog missing URMP")
    if not bach10:
        return fail("catalog missing Bach10")
    if not trios:
        return fail("catalog missing TRIOS")
    if not wwq:
        return fail("catalog missing MIREX Woodwind Quintet")
    if not phenicx:
        return fail("catalog missing PHENICX-Anechoic")
    if not musicnet:
        return fail("catalog missing MusicNet")
    if not multtipop:
        return fail("catalog missing MulTTiPop")
    if not medleydb:
        return fail("catalog missing MedleyDB")
    if not spheres:
        return fail("catalog missing Spheres")
    if not guitarset:
        return fail("catalog missing GuitarSet")
    if not maestro:
        return fail("catalog missing MAESTRO")
    if not egmd:
        return fail("catalog missing E-GMD")

    problems = []
    if urmp.get("piece_count", 0) < target_minimum:
        problems.append("URMP must provide at least the 20-piece target")
    if not (urmp.get("real_audio") and urmp.get("isolated_sources") and urmp.get("assembled_mix")):
        problems.append("URMP must remain the direct-fit real multitrack source")
    if not urmp.get("aligned_symbolic_truth"):
        problems.append("URMP must keep aligned note/MIDI truth")
    if urmp.get("automation_target") != "test-real-multitrack-20":
        problems.append("URMP automation target must remain test-real-multitrack-20")
    if bach10.get("fixture_target") != "test-bach10-fixture":
        problems.append("Bach10 generated fixture target must remain test-bach10-fixture")
    if bach10.get("suite_fixture_target") != "test-direct-fit-small-fixture":
        problems.append("Bach10 must remain represented in test-direct-fit-small-fixture")
    for dataset, name in ((trios, "TRIOS"), (wwq, "MIREX Woodwind Quintet"), (phenicx, "PHENICX-Anechoic")):
        if dataset.get("fixture_target") != "test-direct-fit-small-fixture":
            problems.append(f"{name} must remain represented in test-direct-fit-small-fixture")
    direct_fit_small_count = sum(
        dataset.get("piece_count", 0) for dataset in (bach10, trios, wwq, phenicx)
    )
    if direct_fit_small_count < target_minimum:
        problems.append("combined direct-fit-small catalog entries must provide at least 20 pieces")
    if musicnet.get("automation_target") != "test-real-musicnet-20":
        problems.append("MusicNet automation target must remain test-real-musicnet-20")
    if multtipop.get("automation_target") != "inspect-real-multtipop":
        problems.append("MulTTiPop automation target must remain inspect-real-multtipop")
    if medleydb.get("automation_target") != "inspect-real-medleydb":
        problems.append("MedleyDB automation target must remain inspect-real-medleydb")
    if spheres.get("automation_target") != "inspect-real-spheres":
        problems.append("Spheres automation target must remain inspect-real-spheres")
    if guitarset.get("automation_target") != "inspect-real-guitarset":
        problems.append("GuitarSet automation target must remain inspect-real-guitarset")
    if maestro.get("automation_target") != "test-real-maestro-20":
        problems.append("MAESTRO automation target must remain test-real-maestro-20")
    if egmd.get("automation_target") != "test-real-egmd-20":
        problems.append("E-GMD automation target must remain test-real-egmd-20")

    for text, needle, context in (
        (makefile, "test-real-goal-20", "Makefile combined real-data target"),
        (makefile, "inspect-real-goal-20", "Makefile combined real-data preflight"),
        (makefile, "test-real-goal-fixture", "Makefile combined fixture target"),
        (makefile, "tests/run_real_goal_gate.py inspect-20", "Makefile combined fixture preflight"),
        (makefile, "tests/inspect_urmp_dataset.py", "Makefile URMP preflight audit dependency"),
        (makefile, "tests/generate_musicnet_fixture.py", "Makefile MusicNet fixture"),
        (makefile, "tests/generate_bach10_fixture.py", "Makefile Bach10-style fixture"),
        (makefile, "tests/generate_direct_fit_small_fixture.py", "Makefile direct-fit-small fixture"),
        (makefile, "tests/generate_medleydb_fixture.py", "Makefile MedleyDB fixture"),
        (makefile, "tests/generate_multtipop_fixture.py", "Makefile MulTTiPop fixture"),
        (makefile, "tests/generate_spheres_fixture.py", "Makefile Spheres fixture"),
        (makefile, "tests/generate_guitarset_fixture.py", "Makefile GuitarSet fixture"),
        (makefile, "tests/generate_maestro_fixture.py", "Makefile MAESTRO fixture"),
        (makefile, "tests/generate_egmd_fixture.py", "Makefile E-GMD fixture"),
        (makefile, "test-bach10-fixture", "Makefile Bach10-style fixture target"),
        (makefile, "test-direct-fit-small-fixture", "Makefile direct-fit-small fixture target"),
        (makefile, "MUSIC_ANALYZER_URMP_REQUIRED_PIECES=20", "Makefile direct-fit-small 20-piece gate"),
        (makefile, "inspect-real-multtipop", "Makefile optional MulTTiPop preflight"),
        (makefile, "test-real-multtipop-20", "Makefile optional MulTTiPop analyzer gate"),
        (makefile, "$(BUILD_DIR)/analyzer_multtipop", "Makefile MulTTiPop analyzer binary"),
        (makefile, "$(BUILD_DIR)/analyzer_maestro", "Makefile MAESTRO analyzer binary"),
        (makefile, "$(BUILD_DIR)/analyzer_egmd", "Makefile E-GMD analyzer binary"),
        (makefile, "inspect-real-spheres", "Makefile optional Spheres preflight"),
        (makefile, "inspect-real-guitarset", "Makefile optional GuitarSet preflight"),
        (makefile, "test-real-maestro-20", "Makefile optional MAESTRO analyzer gate"),
        (makefile, "test-real-egmd-20", "Makefile optional E-GMD analyzer gate"),
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
        (goal_gate, "configured_guitarset", "combined gate optional GuitarSet root detection"),
        (goal_gate, "inspect-real-guitarset", "combined gate optional GuitarSet target"),
        (goal_gate, "configured_maestro", "combined gate optional MAESTRO root detection"),
        (goal_gate, "test-real-maestro-20", "combined gate optional MAESTRO target"),
        (goal_gate, "configured_egmd", "combined gate optional E-GMD root detection"),
        (goal_gate, "test-real-egmd-20", "combined gate optional E-GMD target"),
        (urmp_harness, "summed separated tracks", "URMP summed-stem playback check"),
        (urmp_harness, "provided mix", "URMP provided-mix check"),
        (urmp_harness, "stateful summed separated-track mix", "URMP stateful summed-mix check"),
        (urmp_harness, "range_summary(source_tracks, \"source tracks\")", "URMP source-track coverage report"),
        (urmp_harness, "source_track_stats.count == tested_pieces", "URMP source-track coverage assertion"),
        (urmp_harness, "active tracks min/avg/max", "URMP window-density report"),
        (urmp_harness, "chord hits", "URMP chord recall report"),
        (urmp_harness, "require_chord_recall", "URMP explicit chord coverage requirement"),
        (bach10_fixture, "Bach10-style", "Bach10 generated fixture report"),
        (bach10_fixture, "bs_as_cl_vn", "Bach10 generated fixture instrumentation"),
        (direct_fit_small_fixture, "Bach10", "direct-fit-small fixture Bach10 coverage"),
        (direct_fit_small_fixture, "TRIOS", "direct-fit-small fixture TRIOS coverage"),
        (direct_fit_small_fixture, "PHENICX", "direct-fit-small fixture PHENICX coverage"),
        (direct_fit_small_fixture, "WWQ", "direct-fit-small fixture WWQ coverage"),
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
        (maestro_harness, "read_maestro_midi", "MAESTRO aligned-MIDI parser"),
        (maestro_harness, "MAESTRO piano pitch-class recall", "MAESTRO real-audio recall gate"),
        (maestro_harness, "chord hits", "MAESTRO chord recall report"),
        (egmd_harness, "read_egmd_midi", "E-GMD aligned-MIDI parser"),
        (egmd_harness, "E-GMD drum-category recall", "E-GMD real-audio recall gate"),
        (egmd_harness, "drum hits", "E-GMD drum recall report"),
        (spheres_inspector, "range_summary(reconstructable_folder_counts, 'reconstructable folders')", "Spheres stem-layout coverage report"),
        (spheres_inspector, "MUSIC_ANALYZER_SPHERES_REQUIRED_PIECES", "Spheres preflight piece threshold"),
        (guitarset_inspector, "MUSIC_ANALYZER_GUITARSET_REQUIRE_HEX_AUDIO", "GuitarSet hex-audio requirement"),
        (guitarset_inspector, "note_midi", "GuitarSet note annotation check"),
        (guitarset_inspector, "hex audio files", "GuitarSet hex-audio coverage report"),
        (readme, "make test-real-goal-20", "README combined gate instructions"),
        (readme, "make inspect-real-goal-20", "README combined preflight instructions"),
        (readme, "make inspect-real-multtipop", "README MulTTiPop preflight instructions"),
        (readme, "make test-real-multtipop-20", "README MulTTiPop analyzer instructions"),
        (readme, "make inspect-real-spheres", "README Spheres preflight instructions"),
        (readme, "make inspect-real-guitarset", "README GuitarSet preflight instructions"),
        (readme, "make test-real-maestro-20", "README MAESTRO analyzer instructions"),
        (readme, "make test-real-egmd-20", "README E-GMD analyzer instructions"),
        (readme, "make test-bach10-fixture", "README Bach10 fixture instructions"),
        (readme, "make test-direct-fit-small-fixture", "README direct-fit-small fixture instructions"),
        (docs, "make test-real-goal-20", "dataset docs combined gate instructions"),
        (docs, "make inspect-real-goal-20", "dataset docs combined preflight instructions"),
        (docs, "make inspect-real-multtipop", "dataset docs MulTTiPop preflight instructions"),
        (docs, "make test-real-multtipop-20", "dataset docs MulTTiPop analyzer instructions"),
        (docs, "make inspect-real-spheres", "dataset docs Spheres preflight instructions"),
        (docs, "make inspect-real-guitarset", "dataset docs GuitarSet preflight instructions"),
        (docs, "make test-real-maestro-20", "dataset docs MAESTRO analyzer instructions"),
        (docs, "make test-real-egmd-20", "dataset docs E-GMD analyzer instructions"),
        (docs, "make test-bach10-fixture", "dataset docs Bach10 fixture instructions"),
        (docs, "make test-direct-fit-small-fixture", "dataset docs direct-fit-small fixture instructions"),
        (docs, "MulTTiPop", "dataset docs MulTTiPop candidate"),
        (docs, "The Spheres Dataset", "dataset docs Spheres candidate"),
        (docs, "GuitarSet", "dataset docs GuitarSet candidate"),
        (docs, "MAESTRO", "dataset docs MAESTRO candidate"),
        (docs, "E-GMD", "dataset docs E-GMD candidate"),
        (docs, "Bach10", "dataset docs Bach10 candidate"),
        (docs, "TRIOS", "dataset docs TRIOS candidate"),
        (docs, "PHENICX-Anechoic", "dataset docs PHENICX-Anechoic candidate"),
        (docs, "MIREX Woodwind Quintet", "dataset docs WWQ candidate"),
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
        "catalog=URMP+direct-fit-small+MusicNet+MedleyDB+MulTTiPop+Spheres+GuitarSet+MAESTRO+E-GMD, target=test-real-goal-20, "
        "fixture=URMP+Bach10-style+direct-fit-small+MusicNet+MedleyDB+MulTTiPop-audio+Spheres+GuitarSet+MAESTRO+E-GMD, "
        "summed_mix=yes, chord_checks=yes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
