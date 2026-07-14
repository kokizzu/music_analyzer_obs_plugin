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
        guitarset_harness = read_text("tests/analyzer_guitarset.cpp")
        guitarset_manifest = read_text("tests/prepare_guitarset_manifest.py")
        maestro_harness = read_text("tests/analyzer_maestro.cpp")
        egmd_harness = read_text("tests/analyzer_egmd.cpp")
        goal_gate = read_text("tests/run_real_goal_gate.py")
        source_printer = read_text("tests/print_real_dataset_sources.py")
        medleydb_inspector = read_text("tests/inspect_medleydb_dataset.py")
        medleydb_prepare = read_text("tests/prepare_medleydb_musicnet_fixture.py")
        musdb_inspector = read_text("tests/inspect_musdb_dataset.py")
        slakh_inspector = read_text("tests/inspect_slakh_dataset.py")
        slakh_prepare = read_text("tests/prepare_slakh_musicnet_fixture.py")
        choralsynth_inspector = read_text("tests/inspect_choralsynth_dataset.py")
        choralsynth_prepare = read_text("tests/prepare_choralsynth_musicnet_fixture.py")
        cocochorales_inspector = read_text("tests/inspect_cocochorales_dataset.py")
        cocochorales_prepare = read_text("tests/prepare_cocochorales_musicnet_fixture.py")
        synthsod_inspector = read_text("tests/inspect_synthsod_dataset.py")
        synthsod_prepare = read_text("tests/prepare_synthsod_musicnet_fixture.py")
        synthsod_fixture = read_text("tests/generate_synthsod_fixture.py")
        polyvocal_inspector = read_text("tests/inspect_polyvocal_dataset.py")
        polyvocal_prepare = read_text("tests/prepare_polyvocal_musicnet_fixture.py")
        polyvocal_fixture = read_text("tests/generate_polyvocal_fixture.py")
        prepared_multitrack_inspector = read_text("tests/inspect_prepared_multitrack_dataset.py")
        prepared_multitrack_prepare = read_text("tests/prepare_prepared_multitrack_musicnet_fixture.py")
        prepared_multitrack_fixture = read_text("tests/generate_prepared_multitrack_fixture.py")
        multtipop_inspector = read_text("tests/inspect_multtipop_dataset.py")
        multtipop_fixture = read_text("tests/generate_multtipop_fixture.py")
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
    eep = dataset_by_id(catalog, "eep")
    musicnet = dataset_by_id(catalog, "musicnet")
    multtipop = dataset_by_id(catalog, "multtipop")
    medleydb = dataset_by_id(catalog, "medleydb")
    musdb = dataset_by_id(catalog, "musdb18")
    slakh = dataset_by_id(catalog, "slakh2100")
    choralsynth = dataset_by_id(catalog, "choralsynth")
    cocochorales = dataset_by_id(catalog, "cocochorales")
    synthsod = dataset_by_id(catalog, "synthsod")
    polyvocal = dataset_by_id(catalog, "polyvocal_f0")
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
    if not eep:
        return fail("catalog missing EEP")
    if not musicnet:
        return fail("catalog missing MusicNet")
    if not multtipop:
        return fail("catalog missing MulTTiPop")
    if not medleydb:
        return fail("catalog missing MedleyDB")
    if not musdb:
        return fail("catalog missing MUSDB18")
    if not slakh:
        return fail("catalog missing Slakh2100")
    if not choralsynth:
        return fail("catalog missing ChoralSynth")
    if not cocochorales:
        return fail("catalog missing CocoChorales")
    if not synthsod:
        return fail("catalog missing SynthSOD")
    if not polyvocal:
        return fail("catalog missing Vocal Ensemble F0 Aggregate")
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
    if medleydb.get("automation_target") != "test-real-medleydb-20":
        problems.append("MedleyDB automation target must remain test-real-medleydb-20")
    if musdb.get("automation_target") != "inspect-real-musdb":
        problems.append("MUSDB18 automation target must remain inspect-real-musdb")
    if slakh.get("automation_target") != "test-real-slakh-20":
        problems.append("Slakh2100 automation target must remain test-real-slakh-20")
    if choralsynth.get("automation_target") != "test-real-choralsynth-20":
        problems.append("ChoralSynth automation target must remain test-real-choralsynth-20")
    if cocochorales.get("automation_target") != "test-real-cocochorales-20":
        problems.append("CocoChorales automation target must remain test-real-cocochorales-20")
    if cocochorales.get("piece_count", 0) < target_minimum:
        problems.append("CocoChorales must provide at least 20 generated pieces")
    if not (
        (not cocochorales.get("real_audio"))
        and cocochorales.get("isolated_sources")
        and cocochorales.get("assembled_mix")
        and cocochorales.get("aligned_symbolic_truth")
    ):
        problems.append("CocoChorales must remain synthetic multitrack stem/MIDI truth")
    if synthsod.get("automation_target") != "test-real-synthsod-20":
        problems.append("SynthSOD automation target must remain test-real-synthsod-20")
    if synthsod.get("piece_count", 0) < target_minimum:
        problems.append("SynthSOD must provide at least 20 generated pieces")
    if not (
        (not synthsod.get("real_audio"))
        and synthsod.get("isolated_sources")
        and synthsod.get("assembled_mix")
        and synthsod.get("aligned_symbolic_truth")
    ):
        problems.append("SynthSOD must remain synthetic multitrack stem/score truth")
    if polyvocal.get("automation_target") != "test-real-polyvocal-20":
        problems.append("Vocal Ensemble F0 Aggregate automation target must remain test-real-polyvocal-20")
    if polyvocal.get("piece_count", 0) < target_minimum:
        problems.append("Vocal Ensemble F0 Aggregate must provide at least 20 vocal pieces")
    if not (
        polyvocal.get("real_audio")
        and polyvocal.get("isolated_sources")
        and polyvocal.get("assembled_mix")
        and polyvocal.get("aligned_symbolic_truth")
    ):
        problems.append("Vocal Ensemble F0 Aggregate must remain real multitrack F0 truth")
    if spheres.get("automation_target") != "inspect-real-spheres":
        problems.append("Spheres automation target must remain inspect-real-spheres")
    if guitarset.get("automation_target") != "test-real-guitarset-20":
        problems.append("GuitarSet automation target must remain test-real-guitarset-20")
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
        (makefile, "DIRECT_FIT_SMALL_FIXTURE_ARCHIVE", "Makefile direct-fit-small fixture archive"),
        (makefile, "tests/generate_medleydb_fixture.py", "Makefile MedleyDB fixture"),
        (makefile, "tests/prepare_medleydb_musicnet_fixture.py", "Makefile MedleyDB analyzer preparation"),
        (makefile, "tests/generate_musdb_fixture.py", "Makefile MUSDB18 fixture"),
        (makefile, "tests/generate_slakh_fixture.py", "Makefile Slakh2100 fixture"),
        (makefile, "tests/prepare_slakh_musicnet_fixture.py", "Makefile Slakh2100 analyzer preparation"),
        (makefile, "tests/generate_choralsynth_fixture.py", "Makefile ChoralSynth fixture"),
        (makefile, "tests/prepare_choralsynth_musicnet_fixture.py", "Makefile ChoralSynth analyzer preparation"),
        (makefile, "tests/generate_cocochorales_fixture.py", "Makefile CocoChorales fixture"),
        (makefile, "tests/prepare_cocochorales_musicnet_fixture.py", "Makefile CocoChorales analyzer preparation"),
        (makefile, "tests/generate_synthsod_fixture.py", "Makefile SynthSOD fixture"),
        (makefile, "tests/prepare_synthsod_musicnet_fixture.py", "Makefile SynthSOD analyzer preparation"),
        (makefile, "tests/generate_polyvocal_fixture.py", "Makefile Vocal Ensemble F0 fixture"),
        (makefile, "tests/prepare_polyvocal_musicnet_fixture.py", "Makefile Vocal Ensemble F0 analyzer preparation"),
        (makefile, "tests/generate_prepared_multitrack_fixture.py", "Makefile prepared multitrack fixture"),
        (makefile, "tests/prepare_prepared_multitrack_musicnet_fixture.py", "Makefile prepared multitrack analyzer preparation"),
        (makefile, "tests/generate_multtipop_fixture.py", "Makefile MulTTiPop fixture"),
        (makefile, "tests/generate_spheres_fixture.py", "Makefile Spheres fixture"),
        (makefile, "tests/generate_guitarset_fixture.py", "Makefile GuitarSet fixture"),
        (makefile, "tests/generate_maestro_fixture.py", "Makefile MAESTRO fixture"),
        (makefile, "tests/generate_egmd_fixture.py", "Makefile E-GMD fixture"),
        (makefile, "test-bach10-fixture", "Makefile Bach10-style fixture target"),
        (makefile, "test-direct-fit-small-fixture", "Makefile direct-fit-small fixture target"),
        (makefile, "update-direct-fit-small-fixture", "Makefile direct-fit-small fixture update target"),
        (makefile, "MUSIC_ANALYZER_URMP_REQUIRED_PIECES=20", "Makefile direct-fit-small 20-piece gate"),
        (makefile, "inspect-real-multtipop", "Makefile optional MulTTiPop preflight"),
        (makefile, "inspect-real-musdb", "Makefile optional MUSDB18 preflight"),
        (makefile, "inspect-real-slakh", "Makefile optional Slakh2100 preflight"),
        (makefile, "test-real-slakh-20", "Makefile optional Slakh2100 analyzer gate"),
        (makefile, "inspect-real-choralsynth", "Makefile optional ChoralSynth preflight"),
        (makefile, "test-real-choralsynth-20", "Makefile optional ChoralSynth analyzer gate"),
        (makefile, "inspect-real-cocochorales", "Makefile optional CocoChorales preflight"),
        (makefile, "test-real-cocochorales-20", "Makefile optional CocoChorales analyzer gate"),
        (makefile, "inspect-real-synthsod", "Makefile optional SynthSOD preflight"),
        (makefile, "test-real-synthsod-20", "Makefile optional SynthSOD analyzer gate"),
        (makefile, "test-synthsod-fixture", "Makefile SynthSOD fixture gate"),
        (makefile, "inspect-real-polyvocal", "Makefile optional Vocal Ensemble F0 preflight"),
        (makefile, "test-real-polyvocal-20", "Makefile optional Vocal Ensemble F0 analyzer gate"),
        (makefile, "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1", "Makefile generated Vocal Ensemble F0 source-audio requirement"),
        (makefile, "inspect-real-prepared-multitrack", "Makefile optional prepared multitrack preflight"),
        (makefile, "test-real-prepared-multitrack-20", "Makefile optional prepared multitrack analyzer gate"),
        (makefile, "test-prepared-multitrack-fixture", "Makefile prepared multitrack fixture gate"),
        (source_printer, "real_vocal_multitrack_truth", "source printer Vocal Ensemble F0 category"),
        (makefile, "test-real-multtipop-20", "Makefile optional MulTTiPop analyzer gate"),
        (makefile, "test-multtipop-audio-root-fixture", "Makefile MulTTiPop external audio-root fixture target"),
        (makefile, "MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT=$(REAL_GOAL_MULTTIPOP_AUDIO_DIR)", "Makefile MulTTiPop external audio-root analyzer gate"),
        (makefile, "$(BUILD_DIR)/analyzer_multtipop", "Makefile MulTTiPop analyzer binary"),
        (makefile, "$(BUILD_DIR)/analyzer_guitarset", "Makefile GuitarSet analyzer binary"),
        (makefile, "$(BUILD_DIR)/analyzer_maestro", "Makefile MAESTRO analyzer binary"),
        (makefile, "$(BUILD_DIR)/analyzer_egmd", "Makefile E-GMD analyzer binary"),
        (makefile, "inspect-real-spheres", "Makefile optional Spheres preflight"),
        (makefile, "inspect-real-guitarset", "Makefile optional GuitarSet preflight"),
        (makefile, "test-real-guitarset-20", "Makefile optional GuitarSet analyzer gate"),
        (makefile, "test-real-maestro-20", "Makefile optional MAESTRO analyzer gate"),
        (makefile, "test-real-egmd-20", "Makefile optional E-GMD analyzer gate"),
        (goal_gate, "test-real-multitrack-20", "combined gate required URMP target"),
        (goal_gate, "inspect-real-multitrack-20", "combined preflight required URMP target"),
        (goal_gate, "test-real-musicnet-20", "combined gate optional MusicNet target"),
        (goal_gate, "inspect-real-musicnet", "combined preflight optional MusicNet target"),
        (goal_gate, "test-real-medleydb-20", "combined gate optional MedleyDB analyzer target"),
        (goal_gate, "configured_multtipop", "combined gate optional MulTTiPop root detection"),
        (goal_gate, "configured_musdb", "combined gate optional MUSDB18 root detection"),
        (goal_gate, "inspect-real-musdb", "combined gate optional MUSDB18 preflight target"),
        (goal_gate, "configured_slakh", "combined gate optional Slakh2100 root detection"),
        (goal_gate, "inspect-real-slakh", "combined gate optional Slakh2100 preflight target"),
        (goal_gate, "test-real-slakh-20", "combined gate optional Slakh2100 analyzer target"),
        (goal_gate, "configured_choralsynth", "combined gate optional ChoralSynth root detection"),
        (goal_gate, "inspect-real-choralsynth", "combined gate optional ChoralSynth preflight target"),
        (goal_gate, "test-real-choralsynth-20", "combined gate optional ChoralSynth analyzer target"),
        (goal_gate, "configured_cocochorales", "combined gate optional CocoChorales root detection"),
        (goal_gate, "inspect-real-cocochorales", "combined gate optional CocoChorales preflight target"),
        (goal_gate, "test-real-cocochorales-20", "combined gate optional CocoChorales analyzer target"),
        (goal_gate, "configured_synthsod", "combined gate optional SynthSOD root detection"),
        (goal_gate, "inspect-real-synthsod", "combined gate optional SynthSOD preflight target"),
        (goal_gate, "test-real-synthsod-20", "combined gate optional SynthSOD analyzer target"),
        (goal_gate, "configured_polyvocal", "combined gate optional Vocal Ensemble F0 root detection"),
        (goal_gate, "inspect-real-polyvocal", "combined gate optional Vocal Ensemble F0 preflight target"),
        (goal_gate, "test-real-polyvocal-20", "combined gate optional Vocal Ensemble F0 analyzer target"),
        (goal_gate, "configured_prepared_multitrack", "combined gate optional prepared multitrack root detection"),
        (goal_gate, "inspect-real-prepared-multitrack", "combined gate optional prepared multitrack preflight target"),
        (goal_gate, "test-real-prepared-multitrack-20", "combined gate optional prepared multitrack analyzer target"),
        (goal_gate, "inspect-real-multtipop", "combined gate optional MulTTiPop target"),
        (goal_gate, "multtipop_audio_configured", "combined gate optional MulTTiPop audio detection"),
        (goal_gate, "test-real-multtipop-20", "combined gate optional MulTTiPop analyzer target"),
        (goal_gate, "configured_spheres", "combined gate optional Spheres root detection"),
        (goal_gate, "inspect-real-spheres", "combined gate optional Spheres target"),
        (goal_gate, "configured_guitarset", "combined gate optional GuitarSet root detection"),
        (goal_gate, "test-real-guitarset-20", "combined gate optional GuitarSet analyzer target"),
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
        (medleydb_inspector, "melody_annotated_multitracks", "MedleyDB melody coverage report"),
        (medleydb_prepare, "prepare_medleydb_musicnet_fixture", "MedleyDB MusicNet-shaped analyzer preparation"),
        (medleydb_prepare, "prepare_summed_stem_audio", "MedleyDB summed-stem playback preparation"),
        (medleydb_prepare, "summed-stem MedleyDB melody recordings", "MedleyDB generated MusicNet labels"),
        (multtipop_inspector, "midi note parts", "MulTTiPop MIDI part-density report"),
        (multtipop_inspector, "MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO", "MulTTiPop optional audio threshold"),
        (multtipop_inspector, "MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT", "MulTTiPop external audio-root preflight"),
        (multtipop_inspector, "valid_youtube_metadata", "MulTTiPop YouTube timing validation"),
        (multtipop_fixture, "audio_root", "MulTTiPop fixture external audio-root mode"),
        (multtipop_harness, "read_multtipop_midi", "MulTTiPop aligned-MIDI parser"),
        (multtipop_harness, "MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT", "MulTTiPop analyzer external audio-root lookup"),
        (multtipop_harness, "MulTTiPop real-pop pitch-class recall", "MulTTiPop real-audio recall gate"),
        (multtipop_harness, "chord hits", "MulTTiPop chord recall report"),
        (musdb_inspector, "EXPECTED_STEMS", "MUSDB18 expected stem list"),
        (musdb_inspector, "MUSIC_ANALYZER_MUSDB_REQUIRED_TRACKS", "MUSDB18 preflight track threshold"),
        (musdb_inspector, "audio seconds per stem", "MUSDB18 audio-duration coverage report"),
        (slakh_inspector, "DEFAULT_REQUIRED_CLASSES", "Slakh2100 required instrument class list"),
        (slakh_inspector, "MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS", "Slakh2100 preflight track threshold"),
        (slakh_inspector, "readable MIDI files per track", "Slakh2100 MIDI coverage report"),
        (slakh_prepare, "prepare_slakh_musicnet_fixture", "Slakh2100 MusicNet-shaped analyzer preparation"),
        (slakh_prepare, "parse_midi_notes", "Slakh2100 MIDI note parser"),
        (slakh_prepare, "prepare_summed_stem_audio", "Slakh2100 summed-stem playback preparation"),
        (slakh_prepare, "train_labels", "Slakh2100 generated MusicNet labels"),
        (choralsynth_inspector, "MUSIC_ANALYZER_CHORALSYNTH_REQUIRED_PIECES", "ChoralSynth preflight piece threshold"),
        (choralsynth_inspector, "voices per piece", "ChoralSynth voice coverage report"),
        (choralsynth_inspector, "score.musicxml", "ChoralSynth score file check"),
        (choralsynth_prepare, "prepare_choralsynth_musicnet_fixture", "ChoralSynth MusicNet-shaped analyzer preparation"),
        (choralsynth_prepare, "parse_midi_notes", "ChoralSynth MIDI note parser"),
        (choralsynth_prepare, "train_labels", "ChoralSynth generated MusicNet labels"),
        (cocochorales_inspector, "MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES", "CocoChorales preflight piece threshold"),
        (cocochorales_inspector, "stems per piece", "CocoChorales stem coverage report"),
        (cocochorales_inspector, "mix audio", "CocoChorales mix file check"),
        (cocochorales_prepare, "prepare_cocochorales_musicnet_fixture", "CocoChorales MusicNet-shaped analyzer preparation"),
        (cocochorales_prepare, "prepare_summed_stem_audio", "CocoChorales summed-stem playback preparation"),
        (cocochorales_prepare, "parse_midi_notes", "CocoChorales MIDI note parser"),
        (cocochorales_prepare, "train_labels", "CocoChorales generated MusicNet labels"),
        (synthsod_inspector, "SynthSOD-data", "SynthSOD documented audio root check"),
        (synthsod_inspector, "Close Mic", "SynthSOD close-mic source folder check"),
        (synthsod_inspector, "score note rows per piece", "SynthSOD aligned-score note coverage report"),
        (synthsod_inspector, "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT", "SynthSOD aligned-score root environment"),
        (synthsod_fixture, "SynthSOD-aligned-scores", "SynthSOD generated aligned-score fixture"),
        (synthsod_prepare, "prepare_summed_stem_audio", "SynthSOD summed-stem playback preparation"),
        (synthsod_prepare, "summed-stem SynthSOD recordings", "SynthSOD MusicNet-shaped preparation"),
        (polyvocal_inspector, "mtracks_info.json", "Vocal Ensemble F0 prepared metadata check"),
        (polyvocal_inspector, "usable F0 annotations per mix", "Vocal Ensemble F0 annotation coverage report"),
        (polyvocal_inspector, "source audio tracks per mix", "Vocal Ensemble F0 source-audio coverage report"),
        (polyvocal_inspector, "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO", "Vocal Ensemble F0 source-audio requirement"),
        (polyvocal_fixture, "source_audio_files", "Vocal Ensemble F0 generated source-audio metadata"),
        (polyvocal_prepare, "points_to_notes", "Vocal Ensemble F0 contour-to-note conversion"),
        (polyvocal_prepare, "prepare_summed_source_audio", "Vocal Ensemble F0 summed source-audio preparation"),
        (polyvocal_prepare, "real vocal-F0 recordings", "Vocal Ensemble F0 MusicNet-shaped preparation"),
        (prepared_multitrack_inspector, "manifest.json", "prepared multitrack manifest check"),
        (prepared_multitrack_inspector, "source audio tracks per piece", "prepared multitrack source-audio coverage report"),
        (prepared_multitrack_inspector, "note-bearing sources per piece", "prepared multitrack per-source note coverage report"),
        (prepared_multitrack_inspector, "pitch classes per piece", "prepared multitrack pitch-class coverage report"),
        (prepared_multitrack_fixture, "SOURCE_NAMES", "prepared multitrack generated source metadata"),
        (prepared_multitrack_prepare, "prepare_summed_stem_audio", "prepared multitrack summed-source playback preparation"),
        (prepared_multitrack_prepare, "summed-source prepared multitrack recordings", "prepared multitrack MusicNet-shaped preparation"),
        (maestro_harness, "read_maestro_midi", "MAESTRO aligned-MIDI parser"),
        (maestro_harness, "MAESTRO piano pitch-class recall", "MAESTRO real-audio recall gate"),
        (maestro_harness, "chord hits", "MAESTRO chord recall report"),
        (egmd_harness, "read_egmd_midi", "E-GMD aligned-MIDI parser"),
        (egmd_harness, "E-GMD drum-category recall", "E-GMD real-audio recall gate"),
        (egmd_harness, "drum hits", "E-GMD drum recall report"),
        (spheres_inspector, "range_summary(reconstructable_folder_counts, 'reconstructable folders')", "Spheres stem-layout coverage report"),
        (spheres_inspector, "MUSIC_ANALYZER_SPHERES_REQUIRED_PIECES", "Spheres preflight piece threshold"),
        (spheres_inspector, "MUSIC_ANALYZER_SPHERES_REQUIRED_SOURCE_FOLDERS", "Spheres source-folder threshold"),
        (spheres_inspector, "MUSIC_ANALYZER_SPHERES_MIN_AUDIO_SECONDS", "Spheres audio-duration threshold"),
        (guitarset_inspector, "MUSIC_ANALYZER_GUITARSET_REQUIRE_HEX_AUDIO", "GuitarSet hex-audio requirement"),
        (guitarset_inspector, "note_midi", "GuitarSet note annotation check"),
        (guitarset_inspector, "hex audio files", "GuitarSet hex-audio coverage report"),
        (guitarset_manifest, "note_midi", "GuitarSet manifest note parser"),
        (guitarset_manifest, "midi_note", "GuitarSet manifest MIDI-note parser"),
        (guitarset_harness, "GuitarSet guitar pitch-class recall", "GuitarSet analyzer recall gate"),
        (guitarset_harness, "chord hits", "GuitarSet analyzer chord recall report"),
        (readme, "make test-real-goal-20", "README combined gate instructions"),
        (readme, "make inspect-real-goal-20", "README combined preflight instructions"),
        (readme, "make inspect-real-medleydb", "README MedleyDB preflight instructions"),
        (readme, "make test-real-medleydb-20", "README MedleyDB analyzer instructions"),
        (readme, "make inspect-real-multtipop", "README MulTTiPop preflight instructions"),
        (readme, "make inspect-real-musdb", "README MUSDB18 preflight instructions"),
        (readme, "make inspect-real-slakh", "README Slakh2100 preflight instructions"),
        (readme, "make test-real-slakh-20", "README Slakh2100 analyzer instructions"),
        (readme, "summing the per-source stem audio", "README Slakh2100 summed-stem playback instructions"),
        (readme, "make inspect-real-choralsynth", "README ChoralSynth preflight instructions"),
        (readme, "make test-real-choralsynth-20", "README ChoralSynth analyzer instructions"),
        (readme, "make inspect-real-cocochorales", "README CocoChorales preflight instructions"),
        (readme, "make test-real-cocochorales-20", "README CocoChorales analyzer instructions"),
        (readme, "make inspect-real-synthsod", "README SynthSOD preflight instructions"),
        (readme, "make test-real-synthsod-20", "README SynthSOD analyzer instructions"),
        (readme, "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT", "README SynthSOD aligned-score instructions"),
        (readme, "make inspect-real-polyvocal", "README Vocal Ensemble F0 preflight instructions"),
        (readme, "make test-real-polyvocal-20", "README Vocal Ensemble F0 analyzer instructions"),
        (readme, "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1", "README Vocal Ensemble F0 source-audio instructions"),
        (readme, "make test-real-prepared-multitrack-20", "README prepared multitrack analyzer instructions"),
        (readme, "make test-real-multtipop-20", "README MulTTiPop analyzer instructions"),
        (readme, "make test-multtipop-audio-root-fixture", "README MulTTiPop external audio-root fixture instructions"),
        (readme, "make inspect-real-spheres", "README Spheres preflight instructions"),
        (readme, "make inspect-real-guitarset", "README GuitarSet preflight instructions"),
        (readme, "make test-real-guitarset-20", "README GuitarSet analyzer instructions"),
        (readme, "make test-real-maestro-20", "README MAESTRO analyzer instructions"),
        (readme, "make test-real-egmd-20", "README E-GMD analyzer instructions"),
        (readme, "make test-bach10-fixture", "README Bach10 fixture instructions"),
        (readme, "make test-direct-fit-small-fixture", "README direct-fit-small fixture instructions"),
        (docs, "make test-real-goal-20", "dataset docs combined gate instructions"),
        (docs, "make inspect-real-goal-20", "dataset docs combined preflight instructions"),
        (docs, "make inspect-real-medleydb", "dataset docs MedleyDB preflight instructions"),
        (docs, "make test-real-medleydb-20", "dataset docs MedleyDB analyzer instructions"),
        (docs, "make inspect-real-multtipop", "dataset docs MulTTiPop preflight instructions"),
        (docs, "make inspect-real-musdb", "dataset docs MUSDB18 preflight instructions"),
        (docs, "make inspect-real-slakh", "dataset docs Slakh2100 preflight instructions"),
        (docs, "make test-real-slakh-20", "dataset docs Slakh2100 analyzer instructions"),
        (docs, "summing the per-source stem audio", "dataset docs Slakh2100 summed-stem playback instructions"),
        (docs, "make inspect-real-choralsynth", "dataset docs ChoralSynth preflight instructions"),
        (docs, "make test-real-choralsynth-20", "dataset docs ChoralSynth analyzer instructions"),
        (docs, "make inspect-real-cocochorales", "dataset docs CocoChorales preflight instructions"),
        (docs, "make test-real-cocochorales-20", "dataset docs CocoChorales analyzer instructions"),
        (docs, "make inspect-real-synthsod", "dataset docs SynthSOD preflight instructions"),
        (docs, "make test-real-synthsod-20", "dataset docs SynthSOD analyzer instructions"),
        (docs, "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT", "dataset docs SynthSOD aligned-score instructions"),
        (docs, "make inspect-real-polyvocal", "dataset docs Vocal Ensemble F0 preflight instructions"),
        (docs, "make test-real-polyvocal-20", "dataset docs Vocal Ensemble F0 analyzer instructions"),
        (docs, "MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1", "dataset docs Vocal Ensemble F0 source-audio instructions"),
        (docs, "make test-real-prepared-multitrack-20", "dataset docs prepared multitrack analyzer instructions"),
        (docs, "make test-real-multtipop-20", "dataset docs MulTTiPop analyzer instructions"),
        (docs, "make test-multtipop-audio-root-fixture", "dataset docs MulTTiPop external audio-root fixture instructions"),
        (docs, "make inspect-real-spheres", "dataset docs Spheres preflight instructions"),
        (docs, "make inspect-real-guitarset", "dataset docs GuitarSet preflight instructions"),
        (docs, "make test-real-guitarset-20", "dataset docs GuitarSet analyzer instructions"),
        (docs, "make test-real-maestro-20", "dataset docs MAESTRO analyzer instructions"),
        (docs, "make test-real-egmd-20", "dataset docs E-GMD analyzer instructions"),
        (docs, "make test-bach10-fixture", "dataset docs Bach10 fixture instructions"),
        (docs, "make test-direct-fit-small-fixture", "dataset docs direct-fit-small fixture instructions"),
        (docs, "MulTTiPop", "dataset docs MulTTiPop candidate"),
        (docs, "The Spheres Dataset", "dataset docs Spheres candidate"),
        (docs, "MUSDB18", "dataset docs MUSDB18 candidate"),
        (docs, "Slakh2100", "dataset docs Slakh2100 candidate"),
        (docs, "ChoralSynth", "dataset docs ChoralSynth candidate"),
        (docs, "CocoChorales", "dataset docs CocoChorales candidate"),
        (docs, "SynthSOD", "dataset docs SynthSOD candidate"),
        (docs, "Vocal Ensemble F0 Aggregate", "dataset docs Vocal Ensemble F0 candidate"),
        (docs, "GuitarSet", "dataset docs GuitarSet candidate"),
        (docs, "MAESTRO", "dataset docs MAESTRO candidate"),
        (docs, "E-GMD", "dataset docs E-GMD candidate"),
        (docs, "Bach10", "dataset docs Bach10 candidate"),
        (docs, "TRIOS", "dataset docs TRIOS candidate"),
        (docs, "PHENICX-Anechoic", "dataset docs PHENICX-Anechoic candidate"),
        (docs, "MIREX Woodwind Quintet", "dataset docs WWQ candidate"),
        (docs, "Ensemble Expressive Performance", "dataset docs EEP candidate"),
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
        "catalog=URMP+EEP+direct-fit-small+MusicNet+MedleyDB+MUSDB18+Slakh2100+ChoralSynth+CocoChorales+SynthSOD+PolyVocal+PreparedMultitrack+MulTTiPop+Spheres+GuitarSet+MAESTRO+E-GMD, target=test-real-goal-20, "
        "fixture=URMP+Bach10-style+direct-fit-small+MusicNet+MedleyDB+MUSDB18+Slakh2100+ChoralSynth+CocoChorales+SynthSOD+PolyVocal-source+PreparedMultitrack+MulTTiPop-audio+Spheres+GuitarSet+MAESTRO+E-GMD, "
        "summed_mix=yes, chord_checks=yes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
