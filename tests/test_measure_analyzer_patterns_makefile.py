#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def target_recipe(makefile: str, target: str) -> str:
    match = re.search(rf"^{re.escape(target)}:.*(?:\n\t.*)+", makefile, re.MULTILINE)
    assert match is not None, f"missing {target} target"
    return match.group(0)


def assert_atomic_build_recipe(makefile: str, target: str) -> None:
    recipe = target_recipe(makefile, target)
    assert 'tmp="$@.$$$$.tmp"' in recipe, f"{target} must build through a per-process temp file"
    assert '-o "$$tmp"' in recipe, f"{target} must write compiler/linker output to the temp file"
    assert '&& mv "$$tmp" "$@"' in recipe, f"{target} must publish the temp file atomically"


def main() -> int:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    for target in [
        "$(BUILD_DIR)/fret_control_tests.o",
        "$(BUILD_DIR)/analyzer_test.o",
        "$(BUILD_DIR)/analyzer_smoke.o",
        "$(BUILD_DIR)/analyzer_cases.o",
        "$(BUILD_DIR)/analyzer_midi_ranges.o",
        "$(BUILD_DIR)/analyzer_urmp.o",
        "$(BUILD_DIR)/analyzer_musicnet.o",
        "$(BUILD_DIR)/analyzer_multtipop.o",
        "$(BUILD_DIR)/analyzer_guitarset.o",
        "$(BUILD_DIR)/analyzer_maestro.o",
        "$(BUILD_DIR)/analyzer_egmd.o",
        "$(BUILD_DIR)/analyzer_drum_samples.o",
        "$(BUILD_DIR)/analyzer_instrument_samples.o",
        "$(BUILD_DIR)/analyzer_real_note_samples.o",
        "$(BUILD_DIR)/analyzer_instrument_family_samples.o",
        "$(BUILD_DIR)/standalone.o",
        "$(BUILD_DIR)/standalone_bass_guitar.o",
        "$(BUILD_DIR)/fret_control_tests",
        "$(BUILD_DIR)/analyzer_smoke",
        "$(BUILD_DIR)/analyzer_cases",
        "$(BUILD_DIR)/analyzer_midi_ranges",
        "$(BUILD_DIR)/analyzer_urmp",
        "$(BUILD_DIR)/analyzer_musicnet",
        "$(BUILD_DIR)/analyzer_multtipop",
        "$(BUILD_DIR)/analyzer_guitarset",
        "$(BUILD_DIR)/analyzer_maestro",
        "$(BUILD_DIR)/analyzer_egmd",
        "$(BUILD_DIR)/analyzer_drum_samples",
        "$(BUILD_DIR)/analyzer_instrument_samples",
        "$(BUILD_DIR)/analyzer_real_note_samples",
        "$(BUILD_DIR)/analyzer_instrument_family_samples",
        "$(STANDALONE_BIN)",
        "$(BASS_GUITAR_STANDALONE_BIN)",
    ]:
        assert_atomic_build_recipe(makefile, target)

    recipe = target_recipe(makefile, "report-analyzer-patterns-from-rows")
    for text in [
        "$(RUN_WITH_DURATION) analyzer_pattern_report_sections",
        "$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) measure-analyzer-pattern-report-sections",
        "cat $(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)",
    ]:
        assert text in recipe, f"report-analyzer-patterns-from-rows does not include {text}"

    sections_recipe = target_recipe(makefile, "measure-analyzer-pattern-report-sections")
    assert "$(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)" in sections_recipe, (
        "pattern report section fanout must build all default section outputs"
    )
    section_recipes = "\n".join(
        target_recipe(makefile, target)
        for target in [
            "$(MEASURE_ANALYZER_PATTERN_DETECTED_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_GUITAR_PRIMARY_ORDER_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_RECOVERY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_DRUM_PRIMARY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_FULL_SKIP_REPORT)",
        ]
    )
    expected = [
        "$(MAKE) print-analyzer-detected-attributes",
        "scripts/report_analyzer_attribute_patterns.py",
        "$(MAKE) find-instrument-owner-patterns",
        "$(MAKE) find-instrument-status-patterns",
        "$(MAKE) find-real-note-attribute-patterns",
        "$(MAKE) find-real-note-row-confusion-patterns",
        "$(MAKE) find-real-note-visual-row-confusion-patterns",
        "$(MAKE) find-guitar-chord-mix-attribute-patterns",
        "$(MAKE) analyze-guitar-chord-primary-order",
        "$(MAKE) analyze-guitar-chord-mix-recovery",
        "$(MAKE) analyze-guitar-chord-mix-extra-components",
        "$(MAKE) find-drum-primary-attribute-patterns",
        "$(MAKE) find-protected-drum-primary-attribute-patterns",
        "$(MAKE) analyze-drum-spread-gate-matrix",
        "$(MAKE) find-drum-spread-exact-attribute-patterns",
        "$(MEASURE_INSTRUMENT_PATTERN_ARGS)",
        "$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)",
        "$(MEASURE_GUITAR_PATTERN_ARGS)",
        "$(PRIMARY_ORDER_ARGS)",
        "$(RECOVERY_ARGS)",
        "$(EXTRA_COMPONENT_ARGS)",
        "$(MEASURE_DRUM_PATTERN_ARGS)",
        "$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS)",
        "$(PATTERN_REPORT_ARGS)",
        "measure-analyzer-patterns-full",
    ]
    for text in expected:
        assert text in section_recipes, f"pattern report section recipes do not include {text}"
    assert "$(MAKE) find-drum-full-attribute-patterns" not in recipe, (
        "default pattern report must not mine exhaustive full-drum rows"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT)"
    ).splitlines()[0], (
        "protected drum primary report must wait for spread rows to avoid parallel TSV regeneration"
    )
    protected_inputs = re.search(
        r"^DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS \?= (?P<value>.*)$",
        makefile,
        re.MULTILINE,
    )
    assert protected_inputs is not None, "missing protected drum primary input list"
    assert "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" in protected_inputs.group("value"), (
        "protected drum primary mining must include cached full-exact rows when available"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT)"
    ).splitlines()[0], (
        "drum active false report must wait for spread rows to avoid parallel TSV regeneration"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT)"
    ).splitlines()[0], (
        "drum spread exact pattern report must wait for spread rows to avoid parallel TSV regeneration"
    )

    pattern_recipe = target_recipe(makefile, "measure-analyzer-patterns")
    assert "measure-analyzer-attribute-rows" in pattern_recipe, "pattern target must refresh bounded rows"
    assert "$(MAKE) report-analyzer-patterns-from-rows" in pattern_recipe, (
        "pattern target must reuse the print/report helper"
    )

    report_recipe = target_recipe(makefile, "measure-analyzer-pattern-report")
    assert "$(MAKE) -s measure-analyzer-patterns" in report_recipe, (
        "saved report target must reuse the measurement target without make recipe echo"
    )
    assert "$(MEASURE_ANALYZER_REPORT)" in report_recipe, "report target must write the configured report path"

    spread_recipe = target_recipe(makefile, "test-drum-samples-spread")
    spread_manifest_recipe = target_recipe(makefile, "$(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv")
    spread_matrix_recipe = target_recipe(makefile, "analyze-drum-spread-gate-matrix")
    assert "$(MAKE) prepare-drum-samples-spread" in spread_manifest_recipe, (
        "spread sample manifest target must delegate to the spread prepare target"
    )
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in spread_matrix_recipe, (
        "spread matrix row dump must include primary miss labels, not only debug rows"
    )
    for recipe_text, target in (
        (spread_recipe, "test-drum-samples-spread"),
        (spread_matrix_recipe, "analyze-drum-spread-gate-matrix"),
    ):
        for category in ["KICK", "SNARE", "HIHAT", "CRASH", "TOM", "RIDE", "RIM"]:
            env_name = f"MUSIC_ANALYZER_DRUM_SAMPLE_MIN_{category}_PRIMARY_RECALL_PERCENT"
            var_name = f"$(DRUM_SAMPLE_SPREAD_MIN_{category}_PRIMARY_PERCENT)"
            assert env_name in recipe_text, f"{target} must enforce {env_name}"
            assert var_name in recipe_text, f"{target} must use {var_name}"

    assert "ONLINE_CPU_COUNT := $(or $(shell nproc 2>/dev/null)" in makefile, (
        "parallel test defaults must derive the online CPU count"
    )
    assert "PARALLEL_TEST_JOBS ?= $(ONLINE_CPU_COUNT)" in makefile, (
        "parallel test job count must remain overrideable while defaulting to online CPUs"
    )
    assert "PARALLEL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(PARALLEL_TEST_JOBS))" in makefile, (
        "parallel aggregate targets must reuse an inherited GNU make jobserver"
    )
    analysis_script_targets = re.search(r"^ANALYSIS_SCRIPT_TEST_TARGETS := (.+)$", makefile, re.MULTILINE)
    assert analysis_script_targets is not None, "missing analysis script parallel target list"
    analysis_script_target_list = analysis_script_targets.group(1)
    for target in [
        "inspect-real-dataset-catalog",
        "test-analyzer-pattern-report",
        "test-real-note-attribute-patterns",
        "test-drum-gate-matrix-summary",
        "test-drum-sample-shard-check",
        "test-real-note-full-mix-shard-check",
        "test-real-note-sample-shard-check",
        "android-check",
    ]:
        assert target in analysis_script_target_list, (
            f"analysis script parallel target list must include {target}"
        )
    analysis_scripts_recipe = target_recipe(makefile, "test-analysis-scripts-parallel")
    assert "$(RUN_WITH_DURATION) test_analysis_scripts_parallel" in analysis_scripts_recipe, (
        "analysis script parallel target must report aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) test_analysis_scripts_parallel" in analysis_scripts_recipe, (
        "analysis script parallel target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(ANALYSIS_SCRIPT_TEST_TARGETS)" in analysis_scripts_recipe, (
        "analysis script parallel target must fan out through jobserver-aware make"
    )
    detector_improvement_recipe = target_recipe(makefile, "analyze-detector-improvements")
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvement_samples" in detector_improvement_recipe, (
        "detector improvement workflow must report the bounded sample-regression duration"
    )
    assert "$(MAKE) test-detector-samples-parallel" in detector_improvement_recipe, (
        "detector improvement workflow must reuse the bounded parallel detector sample gate"
    )
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvement_patterns" in detector_improvement_recipe, (
        "detector improvement workflow must report the bounded pattern-analysis duration"
    )
    assert "$(MAKE) -s measure-analyzer-patterns" in detector_improvement_recipe, (
        "detector improvement workflow must generate clean measured attribute and pattern reports"
    )
    detector_improvement_full_recipe = target_recipe(makefile, "analyze-detector-improvements-full")
    assert "$(MAKE) test-real-world-samples-max-parallel" in detector_improvement_full_recipe, (
        "full detector improvement workflow must reuse the max real-world parallel gate"
    )
    assert "$(MAKE) -s measure-analyzer-patterns-full" in detector_improvement_full_recipe, (
        "full detector improvement workflow must generate clean exhaustive pattern reports"
    )
    default_test_recipe = target_recipe(makefile, "test")
    assert "$(RUN_WITH_DURATION) test_fast" in default_test_recipe, (
        "default test target must report the fast parallel aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) test_fast" in default_test_recipe, (
        "default test target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-parallel test-detector-samples-parallel test-fret-control test-real-goal-fixture test-fixtures-parallel-isolated" in default_test_recipe, (
        "default test target must fan out independent test groups and isolated fixtures together"
    )
    isolated_fixture_recipe = target_recipe(makefile, "test-fixtures-parallel-isolated")
    assert "$(RUN_WITH_DURATION) test_fixtures_parallel_isolated" in isolated_fixture_recipe, (
        "isolated fixture target must report aggregate duration"
    )
    assert 'REAL_GOAL_FIXTURE_DIR="$(REAL_GOAL_PARALLEL_FIXTURE_DIR)" test-fixtures-parallel' in isolated_fixture_recipe, (
        "isolated fixture target must run fixtures under a separate real-goal root"
    )
    assert "$(MAKE) test-instrument-samples\n" not in default_test_recipe, (
        "default test target must not run generated instrument samples serially"
    )
    max_samples_parallel_recipe = target_recipe(makefile, "test-real-world-samples-max-parallel")
    assert "\n\t+$(RUN_WITH_DURATION) real_world_samples_max" in max_samples_parallel_recipe, (
        "max real-world sample tests must preserve the make jobserver through the duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_WORLD_SAMPLE_MAX_TARGETS)" in max_samples_parallel_recipe, (
        "max real-world sample tests must fan out through jobserver-aware make"
    )
    for wrapper, aggregate in {
        "test-drum-real-world-samples": "test-drum-real-world-samples-parallel",
        "test-drum-real-world-samples-full": "test-drum-real-world-samples-full-parallel",
        "test-real-world-samples": "test-real-world-samples-parallel",
        "test-real-world-samples-full": "test-real-world-samples-full-parallel",
        "test-real-world-samples-max": "test-real-world-samples-max-parallel",
    }.items():
        wrapper_recipe = target_recipe(makefile, wrapper)
        assert f"$(MAKE) {aggregate}" in wrapper_recipe, (
            f"{wrapper} must delegate to {aggregate}"
        )
        assert f"\n\t+$(MAKE) {aggregate}" in wrapper_recipe, (
            f"{wrapper} must preserve the make jobserver while delegating"
        )
        assert "$(PARALLEL_TEST_MAKE_JOBS)" not in wrapper_recipe, (
            f"{wrapper} must let {aggregate} own its job fanout"
        )
    real_world_targets = re.search(r"^REAL_WORLD_SAMPLE_TARGETS := (.+)$", makefile, re.MULTILINE)
    assert real_world_targets is not None, "missing real-world sample target list"
    real_world_target_list = real_world_targets.group(1)
    assert "test-real-note-samples-full-mix-parallel" in real_world_target_list, (
        "parallel real-world sample tests must use the sharded real-note full-mix gate"
    )
    assert "test-real-note-samples-full-mix " not in real_world_target_list + " ", (
        "parallel real-world sample tests must not use the serial real-note full-mix gate"
    )
    real_note_sharded_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-parallel")
    assert "REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))" in makefile, (
        "real-note shard tests must not force nested jobserver mode"
    )
    assert "REAL_NOTE_FULL_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/real_note_full_mix_shard_,$(addsuffix .out,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))" in makefile, (
        "real-note full-mix aggregate checker must consume deterministic shard outputs"
    )
    for text in [
        "REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT ?= 30",
        "REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT ?= 43",
        "REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT ?= 15",
    ]:
        assert text in makefile, f"real-note aggregate gate must include {text}"
    assert "$(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) $(REAL_NOTE_FULL_MIX_SHARD_TARGETS)" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_parallel" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must report aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_parallel" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must preserve the make jobserver through the duration wrapper"
    )
    assert "scripts/prepare_nsynth_samples.py\" -nt \"$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv\"" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must skip sample regeneration when the manifest is fresh"
    )
    assert "$(PYTHON) scripts/check_real_note_full_mix_shards.py" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must validate aggregated shard ownership metrics"
    )
    for text in [
        "--min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT)\"",
        "--guitar-min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT)\"",
        "--other-min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT)\"",
        "$(REAL_NOTE_FULL_MIX_SHARD_OUTS)",
    ]:
        assert text in real_note_sharded_recipe, (
            f"real-note aggregate checker recipe must include {text}"
        )
    real_note_shard_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-shard-%")
    for text in [
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_FULL_MIX_SHARDS)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0",
        "$(REAL_NOTE_FULL_MIX_SHARD_GATE_ENV)",
    ]:
        assert text in real_note_shard_recipe, f"real-note shard target must include {text}"
    assert "$(REAL_NOTE_FULL_MIX_GATE_ENV)" not in real_note_shard_recipe, (
        "individual real-note shards must not enforce whole-corpus ownership thresholds"
    )
    for text in [
        "> \"$(BUILD_DIR)/real_note_full_mix_shard_$*.out\"",
        "2> \"$(BUILD_DIR)/real_note_full_mix_shard_$*.err\"",
    ]:
        assert text in real_note_shard_recipe, f"real-note shard target must write {text}"
    for text in [
        "REAL_NOTE_FULL_MIX_GATE_ENV = \\",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=\"$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=\"$(REAL_NOTE_FULL_MIX_MIN_FIRST_ROW_PERCENT)\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=\"$(REAL_NOTE_FULL_MIX_MIN_GUITAR_FIRST_ROW_PERCENT)\"",
    ]:
        assert text in makefile, f"real-note full-mix gate env must include {text}"
    for text in [
        "REAL_NOTE_FULL_MIX_SHARD_GATE_ENV = \\",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999",
    ]:
        assert text in makefile, f"real-note shard gate env must include {text}"
    isolated_sample_sharded_recipe = target_recipe(makefile, "test-real-note-sample-shards")
    assert "REAL_NOTE_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_SAMPLE_SHARDS))" in makefile, (
        "isolated real-note shard tests must not force nested jobserver mode"
    )
    assert "REAL_NOTE_SAMPLE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_,$(addsuffix .out,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))" in makefile, (
        "isolated real-note aggregate checker must consume deterministic shard outputs"
    )
    assert "$(MAKE) $(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS) $(REAL_NOTE_SAMPLE_SHARD_TARGETS)" in isolated_sample_sharded_recipe, (
        "isolated real-note parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(PYTHON) scripts/check_real_note_sample_shards.py" in isolated_sample_sharded_recipe, (
        "isolated real-note parallel target must validate aggregated shard sample metrics"
    )
    assert "$(REAL_NOTE_SAMPLE_HIT_PERCENT_ARGS)" in isolated_sample_sharded_recipe, (
        "isolated real-note aggregate checker must validate per-family recall gates"
    )
    for text in [
        "--min-bass-hit-percent \"$(REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT)\"",
        "--min-guitar-hit-percent \"$(REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT)\"",
        "--min-piano-hit-percent \"$(REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT)\"",
        "--min-vocals-hit-percent \"$(REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT)\"",
        "--min-other-hit-percent \"$(REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT)\"",
    ]:
        assert text in makefile, f"isolated real-note recall gate args must include {text}"
    isolated_sample_shard_recipe = target_recipe(makefile, "test-real-note-sample-shard-%")
    for text in [
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0",
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=\"$(REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES)\"",
        "> \"$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.out\"",
        "2> \"$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.err\"",
    ]:
        assert text in isolated_sample_shard_recipe, (
            f"isolated real-note shard target must include {text}"
        )
    for target, tag in {
        "test-real-note-samples": "nsynth",
        "test-guitar-fretboard-note-samples": "guitar_fretboard",
        "test-guitar-techs-samples": "guitar_techs",
        "test-philharmonia-samples": "philharmonia",
        "test-philharmonia-samples-full": "philharmonia_full",
        "test-good-sounds-samples": "good_sounds",
        "test-iowa-piano-samples": "iowa_piano",
        "test-iowa-bass-samples": "iowa_bass",
        "test-iowa-strings-samples": "iowa_strings",
        "test-iowa-orchestra-samples": "iowa_orchestra",
        "test-iowa-orchestra-full-samples": "iowa_orchestra_full",
        "test-idmt-bass-lines-samples": "idmt_bass_lines",
        "test-idmt-guitar-samples": "idmt_guitar",
        "test-tinysol-samples": "tinysol",
        "test-vocadito-samples": "vocadito",
        "test-vocalset-samples": "vocalset",
    }.items():
        assert f"{target}: REAL_NOTE_SAMPLE_TAG := {tag}" in makefile, (
            f"{target} must configure a deterministic isolated real-note shard tag"
        )
        recipe_text = target_recipe(makefile, target)
        assert "$(RUN_REAL_NOTE_SAMPLE_SHARDS)" in recipe_text, (
            f"{target} must delegate to the isolated real-note shard runner"
        )
        assert "\n\t+$(RUN_REAL_NOTE_SAMPLE_SHARDS)" in recipe_text, (
            f"{target} must preserve the make jobserver through the isolated real-note shard runner"
        )
    for family in ["BASS", "GUITAR", "PIANO", "VOCALS", "OTHER"]:
        assert f"REAL_NOTE_MIN_{family}_HIT_PERCENT ?= 100" in makefile, (
            f"NSynth isolated target must default to strict {family.lower()} recall"
        )
        assert (
            f"test-real-note-samples: REAL_NOTE_SAMPLE_MIN_{family}_HIT_PERCENT := "
            f"$(REAL_NOTE_MIN_{family}_HIT_PERCENT)"
        ) in makefile, (
            f"NSynth isolated target must pass through strict {family.lower()} recall"
        )
    instrument_sharded_recipe = target_recipe(makefile, "test-instrument-samples-parallel")
    assert "INSTRUMENT_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))" in makefile, (
        "generated instrument sample shards must not force nested jobserver mode"
    )
    assert "$(MAKE) $(INSTRUMENT_SAMPLE_TEST_MAKE_JOBS) $(INSTRUMENT_SAMPLE_SHARD_TARGETS)" in instrument_sharded_recipe, (
        "generated instrument sample parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_instrument_samples_parallel" in instrument_sharded_recipe, (
        "generated instrument sample parallel target must report aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) analyzer_instrument_samples_parallel" in instrument_sharded_recipe, (
        "generated instrument sample parallel target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(INSTRUMENT_SAMPLE_MANIFEST_STAMP)" in instrument_sharded_recipe.splitlines()[0], (
        "generated instrument sample parallel target must share a prepared manifest stamp"
    )
    instrument_shard_recipe = target_recipe(makefile, "test-instrument-samples-shard-%")
    assert "$(INSTRUMENT_SAMPLE_MANIFEST_STAMP)" in instrument_shard_recipe.splitlines()[0], (
        "generated instrument shard target must depend on the shared manifest stamp"
    )
    for text in [
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1",
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT=\"$(INSTRUMENT_SAMPLE_SHARDS)\"",
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX=\"$*\"",
    ]:
        assert text in instrument_shard_recipe, f"generated instrument shard target must include {text}"
    detector_regression_targets = re.search(
        r"^DETECTOR_SAMPLE_REGRESSION_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert detector_regression_targets is not None, "missing detector sample regression target list"
    detector_regression_target_list = detector_regression_targets.group(1)
    assert "test-real-note-samples-full-mix-parallel" in detector_regression_target_list, (
        "detector sample regression loop must use the sharded real-note full-mix gate"
    )
    assert "test-real-note-samples-full-mix " not in detector_regression_target_list + " ", (
        "detector sample regression loop must not use the serial real-note full-mix gate"
    )
    assert "test-analyzer-cases" in detector_regression_target_list, (
        "detector sample regression loop must include synthetic temporal/chord/analyzer cases"
    )
    assert "test-guitar-chord-mix-samples" in detector_regression_target_list, (
        "detector sample regression loop must include the real guitar chord mix gate"
    )
    assert "$(DRUM_REAL_WORLD_SAMPLE_TARGETS)" in detector_regression_target_list, (
        "detector sample regression loop must include real-world drum sample gates"
    )
    assert "test-drum-samples-full-parallel-optional" not in detector_regression_target_list, (
        "detector sample regression loop must keep the expensive local full-drum gate out of the parallel fanout"
    )
    assert "test-vocadito-samples" in detector_regression_target_list, (
        "detector sample regression loop must include the real vocal note gate"
    )
    assert "test-instrument-samples-parallel" in detector_regression_target_list, (
        "detector sample regression loop must use the sharded generated instrument sample gate"
    )
    assert "test-instrument-samples " not in detector_regression_target_list + " ", (
        "detector sample regression loop must not use the serial generated instrument sample gate"
    )
    detector_regression_serial_targets = re.search(
        r"^DETECTOR_SAMPLE_REGRESSION_SERIAL_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert detector_regression_serial_targets is not None, (
        "missing detector sample serial regression target list"
    )
    detector_regression_serial_target_list = detector_regression_serial_targets.group(1)
    assert "test-drum-samples-full-parallel-optional" in detector_regression_serial_target_list, (
        "detector sample serial regression loop must include the sharded full-drum gate when local samples exist"
    )
    detector_regression_recipe = target_recipe(makefile, "test-detector-samples-parallel")
    assert "\n\t+$(RUN_WITH_DURATION) detector_samples_parallel" in detector_regression_recipe, (
        "detector sample regression target must preserve the make jobserver through the parallel duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_REGRESSION_TARGETS)" in detector_regression_recipe, (
        "detector sample regression target must fan out core gates through jobserver-aware make"
    )
    assert "\n\t+$(RUN_WITH_DURATION) detector_samples_serial" in detector_regression_recipe, (
        "detector sample regression target must preserve the make jobserver through the serial duration wrapper"
    )
    assert "$(MAKE) $(DETECTOR_SAMPLE_REGRESSION_SERIAL_TARGETS)" in detector_regression_recipe, (
        "detector sample regression target must run expensive local full-drum coverage after the core fanout"
    )
    real_world_full_targets = re.search(
        r"^REAL_WORLD_SAMPLE_FULL_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert real_world_full_targets is not None, "missing full real-world sample target list"
    real_world_full_target_list = real_world_full_targets.group(1)
    assert "test-guitar-chord-mix-samples-parallel" in real_world_full_target_list, (
        "full real-world sample tests must use the sharded guitar chord mix gate"
    )
    assert "test-guitar-chord-mix-samples " not in real_world_full_target_list + " ", (
        "full real-world sample tests must not use the serial guitar chord mix gate"
    )
    assert "test-drum-samples-full-parallel-optional" in real_world_full_target_list, (
        "full real-world sample tests must use the sharded full-drum sample gate"
    )
    assert "test-drum-samples-full-optional " not in real_world_full_target_list + " ", (
        "full real-world sample tests must not use the serial full-drum sample gate"
    )
    drum_real_world_full_targets = re.search(
        r"^DRUM_REAL_WORLD_SAMPLE_FULL_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert drum_real_world_full_targets is not None, "missing full drum real-world sample target list"
    drum_real_world_full_target_list = drum_real_world_full_targets.group(1)
    assert "test-drum-samples-full-parallel-optional" in drum_real_world_full_target_list, (
        "full drum real-world sample tests must use the sharded full-drum sample gate"
    )
    assert "test-drum-samples-full-optional " not in drum_real_world_full_target_list + " ", (
        "full drum real-world sample tests must not use the serial full-drum sample gate"
    )
    real_world_full_recipe = target_recipe(makefile, "test-real-world-samples-full")
    assert "$(MAKE) test-real-world-samples-full-parallel" in real_world_full_recipe, (
        "full real-world wrapper must delegate to the parallel aggregate"
    )
    real_world_max_targets = re.search(
        r"^REAL_WORLD_SAMPLE_MAX_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert real_world_max_targets is not None, "missing max real-world sample target list"
    real_world_max_target_list = real_world_max_targets.group(1)
    assert "test-guitar-chord-mix-samples-parallel" in real_world_max_target_list, (
        "max real-world sample tests must use the sharded guitar chord mix gate"
    )
    assert "test-guitar-chord-mix-samples " not in real_world_max_target_list + " ", (
        "max real-world sample tests must not use the serial guitar chord mix gate"
    )
    assert "test-drum-samples-full-parallel-optional" in real_world_max_target_list, (
        "max real-world sample tests must use the sharded full-drum sample gate"
    )
    assert "test-drum-samples-full-optional " not in real_world_max_target_list + " ", (
        "max real-world sample tests must not use the serial full-drum sample gate"
    )
    drum_full_manifest_recipe = target_recipe(makefile, "$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv")
    assert "$(MAKE) prepare-drum-samples-full" in drum_full_manifest_recipe, (
        "full drum sample manifest target must delegate to the full prepare target"
    )
    drum_full_parallel_recipe = target_recipe(makefile, "test-drum-samples-full-parallel")
    assert "DRUM_SAMPLE_FULL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_SAMPLE_FULL_SHARD_CATEGORIES)))" in makefile, (
        "full drum shard tests must not force nested jobserver mode"
    )
    assert "$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv" in drum_full_parallel_recipe.splitlines()[0], (
        "full drum parallel target must share a prepared manifest stamp"
    )
    assert "$(MAKE) $(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS) $(DRUM_SAMPLE_FULL_SHARD_TARGETS)" in drum_full_parallel_recipe, (
        "full drum parallel target must fan out category shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full_parallel" in drum_full_parallel_recipe, (
        "full drum parallel target must report aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) analyzer_drum_samples_full_parallel" in drum_full_parallel_recipe, (
        "full drum parallel target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(PYTHON) scripts/check_drum_sample_shards.py" in drum_full_parallel_recipe, (
        "full drum parallel target must validate aggregated shard matrices"
    )
    assert "--tom-max-false-percent \"$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)\"" in drum_full_parallel_recipe, (
        "full drum parallel target must preserve the serial tom false-positive gate"
    )
    assert "DRUM_FULL_EXACT_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_full_exact_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_FULL_SHARD_CATEGORIES)))" in makefile, (
        "full drum exact attribute rows must have deterministic per-category shard parts"
    )
    drum_full_attribute_parallel_recipe = target_recipe(makefile, "analyze-drum-full-gate-matrix-parallel")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full_attribute_rows_parallel" in drum_full_attribute_parallel_recipe, (
        "full drum exact attribute rows must report aggregate parallel duration"
    )
    assert "scripts/build_sharded_tsv.sh \"$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)\" \"$(MAKE)\" \"$(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS)\" $(DRUM_FULL_EXACT_ATTRIBUTE_PARTS)" in drum_full_attribute_parallel_recipe, (
        "full drum exact attribute rows must be built by the sharded TSV combiner"
    )
    drum_full_attribute_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_full_exact_attribute_rows_%.tsv")
    assert "FORCE" in drum_full_attribute_shard_recipe.splitlines()[0], (
        "full drum exact attribute shard target must use FORCE so each category executes"
    )
    for text in [
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1",
        "$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows",
    ]:
        assert text in drum_full_attribute_shard_recipe, (
            f"full drum exact attribute shard target must include {text}"
        )
    full_exact_pattern_recipe = target_recipe(makefile, "find-drum-full-exact-attribute-patterns")
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in full_exact_pattern_recipe, (
        "stale full drum pattern rows must refresh through the parallel attribute builder"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix;" not in full_exact_pattern_recipe, (
        "stale full drum pattern rows must not use the serial full analyzer path"
    )
    drum_full_shard_recipe = target_recipe(makefile, "test-drum-samples-full-shard-%")
    assert "FORCE" in drum_full_shard_recipe.splitlines()[0], (
        "full drum shard pattern must use FORCE so each category executes"
    )
    assert "$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv" in drum_full_shard_recipe.splitlines()[0], (
        "full drum shard target must depend on the shared manifest stamp"
    )
    for text in [
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0",
    ]:
        assert text in drum_full_shard_recipe, f"full drum shard target must include {text}"
    phony_lines = "\n".join(re.findall(r"^\.PHONY:.*$", makefile, re.MULTILINE))
    drum_full_cached_recipe = target_recipe(makefile, "find-drum-full-exact-attribute-patterns-cached")
    assert "find-drum-full-exact-attribute-patterns-cached" in phony_lines, (
        "cached full drum pattern target must be phony"
    )
    assert "using cached drum full exact attribute TSV" in drum_full_cached_recipe, (
        "cached full drum pattern target must announce when it reuses existing rows"
    )
    assert "$(BUILD_DIR)/analyzer_drum_samples\" -nt" not in drum_full_cached_recipe, (
        "cached full drum pattern target must not force analyzer freshness regeneration"
    )
    assert "$(PYTHON) scripts/find_drum_attribute_patterns.py \"$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)\"" in drum_full_cached_recipe, (
        "cached full drum pattern target must mine the full drum exact TSV"
    )
    guitar_chord_sharded_recipe = target_recipe(makefile, "test-guitar-chord-mix-samples-parallel")
    assert "GUITAR_CHORD_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/guitar_chord_mix_samples_shard_,$(addsuffix .out,$(GUITAR_CHORD_MIX_SHARD_INDEXES)))" in makefile, (
        "guitar chord mix parallel target must define deterministic shard output logs"
    )
    assert "$(MAKE) $(GUITAR_CHORD_MIX_TEST_MAKE_JOBS) $(GUITAR_CHORD_MIX_SHARD_TARGETS)" in guitar_chord_sharded_recipe, (
        "guitar chord mix parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples_parallel" in guitar_chord_sharded_recipe, (
        "guitar chord mix parallel target must report aggregate duration"
    )
    assert "scripts/check_guitarset_shards.py $(GUITAR_CHORD_MIX_SHARD_OUTS)" in guitar_chord_sharded_recipe, (
        "guitar chord mix parallel target must validate aggregate shard metrics"
    )
    for text in [
        "--required-excerpts \"$(GUITAR_CHORD_MIX_MIN_EXCERPTS)\"",
        "--required-windows \"$(GUITAR_CHORD_MIX_MIN_WINDOWS)\"",
        "--min-chord-hits \"$(GUITAR_CHORD_MIX_MIN_CHORD_HITS)\"",
    ]:
        assert text in guitar_chord_sharded_recipe, (
            f"guitar chord mix aggregate checker must include {text}"
        )
    for target_var in [
        "$(GUITAR_CHORD_MIX_SHARD_TARGETS)",
        "$(GUITAR_TECHS_CHORD_SHARD_TARGETS)",
        "$(EGFXSET_GUITAR_SHARD_TARGETS)",
        "$(GAPS_GUITAR_SHARD_TARGETS)",
        "$(GAPS_GUITAR_FULL_SHARD_TARGETS)",
        "$(GUITARSET_SHARD_TARGETS)",
    ]:
        assert target_var not in phony_lines, (
            f"{target_var} must not expand into concrete .PHONY targets because that masks pattern recipes"
        )
    guitar_chord_shard_recipe = target_recipe(makefile, "test-guitar-chord-mix-samples-shard-%")
    assert "FORCE" in guitar_chord_shard_recipe.splitlines()[0], (
        "guitar chord mix shard pattern must use FORCE so each shard executes"
    )
    for text in [
        "guitar_chord_mix_samples_shard_$*.out",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0",
    ]:
        assert text in guitar_chord_shard_recipe, (
            f"guitar chord mix shard target must include {text}"
        )
    for aggregate, shard, jobs_var, shards_var, targets_var, duration in [
        (
            "test-guitar-techs-chord-samples",
            "test-guitar-techs-chord-samples-shard-%",
            "GUITAR_TECHS_CHORD_TEST_MAKE_JOBS",
            "GUITAR_TECHS_CHORD_SHARDS",
            "GUITAR_TECHS_CHORD_SHARD_TARGETS",
            "analyzer_guitar_techs_chord_samples_parallel",
        ),
        (
            "test-egfxset-guitar-samples",
            "test-egfxset-guitar-samples-shard-%",
            "EGFXSET_GUITAR_TEST_MAKE_JOBS",
            "EGFXSET_GUITAR_SHARDS",
            "EGFXSET_GUITAR_SHARD_TARGETS",
            "analyzer_egfxset_guitar_samples_parallel",
        ),
        (
            "test-gaps-guitar-samples",
            "test-gaps-guitar-samples-shard-%",
            "GAPS_GUITAR_TEST_MAKE_JOBS",
            "GAPS_GUITAR_SHARDS",
            "GAPS_GUITAR_SHARD_TARGETS",
            "analyzer_gaps_guitar_samples_parallel",
        ),
        (
            "test-gaps-guitar-samples-full",
            "test-gaps-guitar-samples-full-shard-%",
            "GAPS_GUITAR_FULL_TEST_MAKE_JOBS",
            "GAPS_GUITAR_FULL_SHARDS",
            "GAPS_GUITAR_FULL_SHARD_TARGETS",
            "analyzer_gaps_guitar_samples_full_parallel",
        ),
        (
            "test-downloaded-guitarset",
            "test-downloaded-guitarset-shard-%",
            "GUITARSET_TEST_MAKE_JOBS",
            "GUITARSET_SHARDS",
            "GUITARSET_SHARD_TARGETS",
            "analyzer_guitarset_downloaded_parallel",
        ),
    ]:
        assert f"{jobs_var} = $(if $(filter -j%,$(MAKEFLAGS)),,-j$({shards_var}))" in makefile, (
            f"{aggregate} shard fanout must reuse an inherited GNU make jobserver"
        )
        aggregate_recipe = target_recipe(makefile, aggregate)
        assert f"$(MAKE) $({jobs_var}) $({targets_var})" in aggregate_recipe, (
            f"{aggregate} must fan out deterministic shards through jobserver-aware make"
        )
        assert f"$(RUN_WITH_DURATION) {duration}" in aggregate_recipe, (
            f"{aggregate} must report aggregate duration"
        )
        shard_recipe = target_recipe(makefile, shard)
        assert "FORCE" in shard_recipe.splitlines()[0], f"{shard} must use FORCE so each shard executes"
        for text in [
            f'MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$({shards_var})"',
            'MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*"',
            "$(BUILD_DIR)/analyzer_guitarset",
        ]:
            assert text in shard_recipe, f"{shard} must include {text}"
    guitarset_shard_recipe = target_recipe(makefile, "test-downloaded-guitarset-shard-%")
    assert "$(GUITARSET_SHARD_GATE_ENV)" in guitarset_shard_recipe, (
        "downloaded GuitarSet shards must use a permissive per-shard coverage gate"
    )
    for text in [
        "GUITARSET_SHARD_GATE_ENV ?=",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0",
    ]:
        assert text in makefile, f"GuitarSet shard gate must include {text}"
    detector_regression_recipe = target_recipe(makefile, "test-detector-samples-parallel")
    assert "\n\t+$(RUN_WITH_DURATION) detector_samples_parallel" in detector_regression_recipe, (
        "detector sample regression target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_REGRESSION_TARGETS)" in detector_regression_recipe, (
        "detector sample regression target must fan out through jobserver-aware make"
    )
    assert "REAL_WORLD_SAMPLE_MAX_TARGETS :=" in makefile, "missing max real-world sample target list"
    assert "REAL_WORLD_SAMPLE_MAX_BASE_TARGETS :=" in makefile, (
        "max real-world sample target list must avoid duplicated default/max targets"
    )
    max_samples_parallel_recipe = target_recipe(makefile, "test-real-world-samples-max-parallel")
    assert "$(RUN_WITH_DURATION) real_world_samples_max" in max_samples_parallel_recipe, (
        "max real-world sample parallel target must report aggregate duration"
    )
    for target, override in {
        "test-iowa-piano-samples-max": "IOWA_PIANO_SAMPLE_LIMIT=0",
        "test-iowa-orchestra-full-samples-max": (
            "IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT=0 IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE=0"
        ),
        "test-good-sounds-samples-max": "GOOD_SOUNDS_SAMPLE_LIMIT=0",
        "test-medley-solos-samples-max": "MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=0",
        "test-maps-piano-samples-max": "MAPS_PIANO_RECORDING_LIMIT=0",
        "test-maps-piano-note-samples-max": "MAPS_PIANO_NOTE_RECORDING_LIMIT=0",
    }.items():
        max_helper_recipe = target_recipe(makefile, target)
        assert override in max_helper_recipe, f"{target} must preserve its max override"

    for category in ["kick", "snare", "tom", "rim"]:
        debug_target = target_recipe(makefile, f"$(BUILD_DIR)/full_{category}_debug.err")
        assert "$(BUILD_DIR)/analyzer_drum_samples" in debug_target, (
            f"full {category} debug rows must rebuild when the analyzer binary changes"
        )
        assert "scripts/run_with_duration.sh" in debug_target, (
            f"full {category} debug rows must report duration"
        )
        assert "| prepare-drum-samples-full" in debug_target, (
            f"full {category} debug rows must prepare the full sample manifest without forcing rebuilds"
        )
        assert f"MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY={category}" in debug_target, (
            f"full {category} debug rows must use the matching category filter"
        )
        assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in debug_target, (
            f"full {category} debug rows must include primary miss diagnostics"
        )
        assert f'full_{category}_debug.out' in debug_target, (
            f"full {category} debug rows must keep stdout in its paired log"
        )
        assert '2> "$@"' in debug_target, (
            f"full {category} debug rows must write stderr to the file target"
        )

    for category in ["kick", "tom", "snare", "hihat", "crash", "ride", "rim"]:
        debug_target = target_recipe(makefile, f"$(BUILD_DIR)/{category}_primary_debug.err")
        assert "$(BUILD_DIR)/analyzer_drum_samples" in debug_target, (
            f"primary {category} debug rows must rebuild when the analyzer binary changes"
        )
        assert "scripts/run_with_duration.sh" in debug_target, (
            f"primary {category} debug rows must report duration"
        )
        assert "| $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv" in debug_target, (
            f"primary {category} debug rows must depend on the concrete spread sample manifest"
        )
        assert f"MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY={category}" in debug_target, (
            f"primary {category} debug rows must use the matching category filter"
        )
        assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in debug_target, (
            f"primary {category} debug rows must include primary miss diagnostics"
        )
        assert f'{category}_primary_debug.out' in debug_target, (
            f"primary {category} debug rows must keep stdout in its paired log"
        )
        assert '2> "$@"' in debug_target, (
            f"primary {category} debug rows must write stderr to the file target"
        )

    drum_recipe = target_recipe(makefile, "find-drum-attribute-patterns")
    assert "full_rim_debug.err" in drum_recipe, "drum pattern search must protect full rim rows"
    assert "$(FULL_DRUM_DEBUG_ERRS)" in drum_recipe, (
        "full debug pattern search must depend on stale-aware full debug file targets"
    )

    drum_primary_recipe = target_recipe(makefile, "find-drum-primary-attribute-patterns")
    assert "drum_primary_miss_attribute_rows.tsv" in drum_primary_recipe, (
        "default drum search must use bounded measured primary rows"
    )
    assert "scripts/find_drum_attribute_patterns.py" in drum_primary_recipe, (
        "primary drum search must use the pattern miner"
    )
    assert "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" in drum_primary_recipe, (
        "primary drum search must depend on the stale-aware primary TSV target"
    )
    assert "full_kick_debug.err" not in drum_primary_recipe, (
        "default primary drum search must not mine exhaustive full logs"
    )

    drum_primary_misses_recipe = target_recipe(makefile, "analyze-drum-primary-misses")
    assert "$(PRIMARY_DRUM_DEBUG_ERRS)" in drum_primary_misses_recipe, (
        "primary drum miss summary must depend on stale-aware primary debug logs"
    )

    drum_primary_rows_recipe = target_recipe(makefile, "analyze-drum-primary-attribute-rows")
    assert "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" in drum_primary_rows_recipe, (
        "primary drum phony target must depend on the file-backed TSV target"
    )

    drum_primary_rows_file_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv")
    assert "$(PRIMARY_DRUM_DEBUG_ERRS)" in drum_primary_rows_file_recipe, (
        "primary drum TSV rows must come from stale-aware bounded primary debug logs"
    )
    assert "--dump-rows" in drum_primary_rows_file_recipe, "primary drum TSV rows must be dumped as TSV"
    assert "--include-debug-rows" in drum_primary_rows_file_recipe, (
        "primary drum TSV rows must include correct primary rows for protected pattern search"
    )

    drum_full_recipe = target_recipe(makefile, "find-drum-full-attribute-patterns")
    assert "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" in drum_full_recipe, (
        "legacy full drum search must use the parallel exact full-manifest TSV"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in drum_full_recipe, (
        "legacy full drum search must refresh stale rows through the parallel attribute builder"
    )
    assert "scripts/find_drum_attribute_patterns.py" in drum_full_recipe, "full drum search must use the pattern miner"
    assert "drum_full_attribute_rows.tsv" not in drum_full_recipe, (
        "legacy full drum search must not depend on the serial full-row dump"
    )

    drum_spread_exact_recipe = target_recipe(makefile, "find-drum-spread-exact-attribute-patterns")
    assert "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" in drum_spread_exact_recipe, (
        "exact spread drum search must use the exact full-manifest TSV"
    )
    assert "analyze-drum-spread-gate-matrix" in drum_spread_exact_recipe, (
        "exact spread drum search must regenerate the exact gate rows when missing or stale"
    )
    assert '$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in drum_spread_exact_recipe, (
        "exact spread drum search must not mine stale exact TSV rows"
    )
    assert 'scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in drum_spread_exact_recipe, (
        "exact spread drum search must regenerate when the row parser changes"
    )

    drum_full_exact_recipe = target_recipe(makefile, "find-drum-full-exact-attribute-patterns")
    assert "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" in drum_full_exact_recipe, (
        "exact full drum search must use the exact full-manifest TSV"
    )
    assert "analyze-drum-full-gate-matrix" in drum_full_exact_recipe, (
        "exact full drum search must regenerate the exact full gate rows when missing or stale"
    )
    assert '$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"' in drum_full_exact_recipe, (
        "exact full drum search must not mine stale exact full TSV rows"
    )
    assert 'scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"' in drum_full_exact_recipe, (
        "exact full drum search must regenerate when the row parser changes"
    )
    for target in [
        "find-drum-attribute-patterns",
        "find-drum-primary-attribute-patterns",
        "find-drum-full-attribute-patterns",
        "find-drum-spread-exact-attribute-patterns",
        "find-drum-full-exact-attribute-patterns",
        "find-drum-full-exact-attribute-patterns-cached",
        "find-drum-active-false-patterns",
        "find-hf-drum-primary-attribute-patterns",
        "find-idmt-drum-primary-attribute-patterns",
        "find-protected-drum-primary-attribute-patterns",
    ]:
        assert '--jobs "$(DRUM_PATTERN_JOBS)"' in target_recipe(makefile, target), (
            f"{target} should mine independent drum routes in parallel by default"
        )
    for target in [
        "find-real-note-attribute-patterns",
        "find-real-note-row-confusion-patterns",
        "find-real-note-practical-row-confusion-patterns",
        "find-real-note-focused-row-confusion-patterns",
        "find-real-note-visual-row-confusion-patterns",
        "find-real-note-focused-visual-row-confusion-patterns",
    ]:
        assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in target_recipe(makefile, target), (
            f"{target} should mine independent real-note buckets in parallel by default"
        )

    drum_full_gate_recipe = target_recipe(makefile, "analyze-drum-full-gate-matrix")
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in drum_full_gate_recipe, (
        "full matrix row dump must include primary miss labels, not only debug rows"
    )

    drum_full_rows_recipe = target_recipe(makefile, "analyze-drum-full-attribute-rows")
    assert "$(BUILD_DIR)/drum_full_attribute_rows.tsv" in drum_full_rows_recipe, (
        "full drum phony target must depend on the file-backed TSV target"
    )

    drum_full_rows_file_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_full_attribute_rows.tsv")
    assert "$(FULL_DRUM_DEBUG_ERRS)" in drum_full_rows_file_recipe, (
        "full drum TSV rows must come from stale-aware full debug logs"
    )
    assert "--include-debug-rows" in drum_full_rows_file_recipe, "full drum TSV rows must include correct primary rows"

    for target in ["analyze-hf-drum-primary-attribute-rows", "analyze-idmt-drum-primary-attribute-rows"]:
        recipe_text = target_recipe(makefile, target)
        assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in recipe_text, (
            f"{target} must include primary miss diagnostics in its row dump"
        )
        assert "--dump-rows --include-debug-rows" in recipe_text, (
            f"{target} must dump miss rows together with protected correct rows"
        )

    row_dump_targets = {
        "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)": (
            "instrument_sample_attributes.tsv",
            "inspect_instrument_sample_owner_buckets.py",
            "--dump-rows",
        ),
        "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)": (
            "real_note_full_mix_attributes.tsv",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(REAL_NOTE_MISS_ATTRIBUTE_ROWS)": (
            "real_note_full_mix_attributes.tsv",
            "inspect_real_note_attribute_buckets.py",
            "--misses-only",
        ),
        "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)": (
            "guitar_chord_mix_attributes.tsv",
            "inspect_guitarset_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS)": (
            "guitar_chord_mix_attributes.tsv",
            "inspect_guitarset_attribute_buckets.py",
            "--misses-only",
        ),
    }
    for target, required_parts in row_dump_targets.items():
        row_dump_recipe = target_recipe(makefile, target)
        for text in required_parts:
            assert text in row_dump_recipe, f"{target} must include {text}"
        assert '> "$@"' in row_dump_recipe, f"{target} must write to its file target"

    source_attribute_targets = {
        "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "scripts/build_sharded_tsv.sh",
            "$(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)",
        ),
    }
    for target, required_parts in source_attribute_targets.items():
        source_recipe = target_recipe(makefile, target)
        for text in required_parts:
            assert text in source_recipe, f"{target} must include {text}"
        assert "| $(BUILD_DIR)" in source_recipe, f"{target} must create output under the build dir"

    real_note_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/real_note_full_mix_attributes.tsv")
    assert "REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))" in makefile, (
        "real-note attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "$(BUILD_DIR)/analyzer_real_note_samples" in real_note_attribute_recipe.splitlines()[0], (
        "real-note attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in real_note_attribute_recipe.splitlines()[0], (
        "real-note attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS)' in real_note_attribute_recipe, (
        "real-note attribute TSV must use the locked helper to build and combine shards"
    )
    real_note_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/real_note_full_mix_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_real_note_samples",
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1",
        "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_FULL_MIX_SHARDS)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
        "real_note_full_mix_attributes.shard-$*.out",
    ]:
        assert text in real_note_attribute_shard_recipe, (
            f"real-note attribute shard target must include {text}"
        )

    instrument_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/instrument_sample_attributes.tsv")
    assert "INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))" in makefile, (
        "instrument attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "$(BUILD_DIR)/analyzer_instrument_samples" in instrument_attribute_recipe.splitlines()[0], (
        "instrument attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "$(INSTRUMENT_SAMPLE_MANIFEST_STAMP)" in instrument_attribute_recipe.splitlines()[0], (
        "instrument attribute TSV must share the prepared manifest stamp"
    )
    assert "scripts/build_sharded_tsv.sh" in instrument_attribute_recipe.splitlines()[0], (
        "instrument attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS)" $(INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS)' in instrument_attribute_recipe, (
        "instrument attribute TSV must use the locked helper to build and combine shards"
    )
    instrument_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/instrument_sample_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_instrument_samples",
        "$(INSTRUMENT_SAMPLE_MANIFEST_STAMP)",
        "MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT=\"$(INSTRUMENT_SAMPLE_SHARDS)\"",
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX=\"$*\"",
        "instrument_sample_attributes.shard-$*.out",
    ]:
        assert text in instrument_attribute_shard_recipe, (
            f"instrument attribute shard target must include {text}"
        )

    guitar_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv")
    assert "GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_CHORD_MIX_SHARDS))" in makefile, (
        "guitar chord attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in guitar_attribute_recipe.splitlines()[0], (
        "guitar chord attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in guitar_attribute_recipe.splitlines()[0], (
        "guitar chord attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)' in guitar_attribute_recipe, (
        "guitar chord attribute TSV must use the locked helper to build and combine shards"
    )
    guitar_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/guitar_chord_mix_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_guitarset",
        "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        "MUSIC_ANALYZER_GUITARSET_SHARD_COUNT=\"$(GUITAR_CHORD_MIX_SHARDS)\"",
        "MUSIC_ANALYZER_GUITARSET_SHARD_INDEX=\"$*\"",
        "guitar_chord_mix_attributes.shard-$*.out",
    ]:
        assert text in guitar_attribute_shard_recipe, (
            f"guitar chord attribute shard target must include {text}"
        )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=\"$(GUITAR_CHORD_MIX_MIN_EXCERPTS)\"" not in guitar_attribute_shard_recipe, (
        "guitar chord attribute shards must not fail uneven shards with the global excerpt floor"
    )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=\"$(GUITAR_CHORD_MIX_MIN_WINDOWS)\"" not in guitar_attribute_shard_recipe, (
        "guitar chord attribute shards must not fail uneven shards with the global window floor"
    )

    downloaded_guitarset_attribute_recipe = target_recipe(makefile, "$(GUITARSET_ATTRIBUTE_TSV)")
    assert "GUITARSET_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITARSET_SHARDS))" in makefile, (
        "downloaded GuitarSet attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in downloaded_guitarset_attribute_recipe.splitlines()[0], (
        "downloaded GuitarSet attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in downloaded_guitarset_attribute_recipe.splitlines()[0], (
        "downloaded GuitarSet attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITARSET_ATTRIBUTE_MAKE_JOBS)" $(GUITARSET_ATTRIBUTE_PARTS)' in downloaded_guitarset_attribute_recipe, (
        "downloaded GuitarSet attribute TSV must use the locked helper to build and combine shards"
    )
    downloaded_guitarset_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/guitarset_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_guitarset",
        "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_GUITARSET_SHARD_COUNT=\"$(GUITARSET_SHARDS)\"",
        "MUSIC_ANALYZER_GUITARSET_SHARD_INDEX=\"$*\"",
        "$(GUITARSET_SHARD_GATE_ENV)",
        "guitarset_attributes.shard-$*.out",
    ]:
        assert text in downloaded_guitarset_attribute_shard_recipe, (
            f"downloaded GuitarSet attribute shard target must include {text}"
        )

    stale_aware_attribute_shortcuts = {
        "inspect-instrument-sample-owner-buckets": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "find-instrument-owner-patterns": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "find-instrument-status-patterns": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "filter-instrument-attribute-rows": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "inspect-real-note-attribute-buckets": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-attribute-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-row-confusion-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-practical-row-confusion-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-focused-row-confusion-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-focused-visual-row-confusion-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "evaluate-real-note-display-shadow": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "analyze-guitar-chord-mix-recovery": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "analyze-guitar-chord-mix-extra-components": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "inspect-guitar-chord-mix-attribute-buckets": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "find-guitar-chord-mix-attribute-patterns": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "analyze-guitarset-attributes": "$(GUITARSET_ATTRIBUTE_TSV)",
        "inspect-guitarset-attribute-buckets": "$(GUITARSET_ATTRIBUTE_TSV)",
        "find-guitarset-attribute-patterns": "$(GUITARSET_ATTRIBUTE_TSV)",
    }
    for target, tsv in stale_aware_attribute_shortcuts.items():
        shortcut_recipe = target_recipe(makefile, target)
        assert tsv in shortcut_recipe.splitlines()[0], f"{target} must depend on {tsv}"
        assert "if [ ! -f" not in shortcut_recipe, (
            f"{target} must use Make timestamp checks, not existence-only TSV refresh"
        )
    real_note_inspect_recipe = target_recipe(makefile, "inspect-real-note-attribute-buckets")
    assert '$(if $(INSPECT_BUCKET),--bucket "$(INSPECT_BUCKET)")' in real_note_inspect_recipe, (
        "real-note bucket inspection must accept bucket names through INSPECT_BUCKET"
    )

    rows_recipe = target_recipe(makefile, "measure-analyzer-attribute-rows")
    assert rows_recipe.splitlines()[0] == "measure-analyzer-attribute-rows:", (
        "default row measurement must own the parallel analyzer fanout"
    )
    assert "MEASURE_ANALYZER_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(MEASURE_ANALYZER_JOBS))" in makefile, (
        "attribute row measurement must reuse an inherited GNU make jobserver"
    )
    assert "$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS)" in rows_recipe, (
        "default row measurement must run independent analyzer producers through jobserver-aware make"
    )
    for text in [
        "analyze-instrument-sample-attributes",
        "analyze-real-note-attributes",
        "analyze-guitar-chord-mix-attributes",
        "analyze-drum-primary-attribute-rows",
    ]:
        assert text in rows_recipe, f"default row measurement must run {text}"
    assert "analyze-drum-primary-attribute-rows" in rows_recipe, (
        "default row measurement must reuse bounded primary drum rows"
    )
    assert "$(MEASURE_ANALYZER_ROW_DUMPS)" in rows_recipe, (
        "default row measurement must build row dump file targets in parallel"
    )
    assert "measure-analyzer-attribute-rows-full" in rows_recipe, "default row target must point to the full target"

    for target in [
        "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
    ]:
        attribute_recipe = target_recipe(makefile, target)
        assert "scripts/build_sharded_tsv.sh" in attribute_recipe, (
            f"{target} must use the locked sharded TSV helper"
        )
    guitar_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv")
    assert "scripts/build_sharded_tsv.sh" in guitar_attribute_recipe, (
        "guitar chord attribute exporter must publish through the locked sharded TSV helper"
    )

    full_rows_recipe = target_recipe(makefile, "measure-analyzer-attribute-rows-full")
    assert "analyze-drum-rule-grid" in full_rows_recipe, "full row target must own full debug drum logs"
    assert "drum_full_attribute_rows.tsv" in full_rows_recipe, "missing full drum attribute row dump"

    detected_recipe = target_recipe(makefile, "measure-analyzer-detected-attributes")
    assert "measure-analyzer-attribute-rows" in detected_recipe, "detected target must refresh bounded rows"
    assert "$(MAKE) print-analyzer-detected-attributes" in detected_recipe, (
        "detected target must reuse the print-only target"
    )

    print_recipe = target_recipe(makefile, "print-analyzer-detected-attributes")
    assert "$(MEASURE_ANALYZER_ROW_DUMPS)" in print_recipe, (
        "print target must depend on stale-aware row dumps"
    )
    assert "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" in print_recipe, (
        "print target must depend on stale-aware drum primary rows"
    )
    assert "refresh-analyzer-detected-attribute-rows" not in print_recipe, (
        "print target must not use the refresh-only helper because it can report stale detector rows"
    )
    assert "scripts/print_analyzer_detected_attributes.py" in print_recipe, "missing measured row printer"
    assert "$(ATTRIBUTE_ROW_REPORT_ARGS)" in print_recipe, "print target needs overridable args"
    assert "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs instrument rows"
    assert "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs real-note rows"
    assert "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs guitar rows"
    assert "drum_primary_miss_attribute_rows.tsv" in print_recipe, "print target needs drum primary rows"
    assert "drum_full_attribute_rows.tsv" in print_recipe, "print target can include protected drum rows"
    assert "analyze-instrument-sample-attributes" not in print_recipe, (
        "print-only target must not regenerate analyzer TSVs"
    )

    refresh_recipe = target_recipe(makefile, "refresh-analyzer-detected-attribute-rows")
    assert "scripts/refresh_analyzer_detected_attribute_rows.py" in refresh_recipe, (
        "refresh target must use the refresh helper"
    )
    assert "--build-dir \"$(BUILD_DIR)\"" in refresh_recipe, "refresh helper needs the configured build dir"
    assert "--python \"$(PYTHON)\"" in refresh_recipe, "refresh helper needs the configured Python"
    for text in [
        "instrument_sample_attributes.tsv",
        "real_note_full_mix_attributes.tsv",
        "guitar_chord_mix_attributes.tsv",
        "kick_primary_debug.err",
        "drum_full_attribute_rows.tsv",
        "inspect_instrument_sample_owner_buckets.py",
        "inspect_real_note_attribute_buckets.py",
        "inspect_guitarset_attribute_buckets.py",
        "analyze_drum_primary_debug.py",
    ]:
        assert text in makefile, f"refresh workflow missing {text}"
    for forbidden in [
        "$(BUILD_DIR)/analyzer_instrument_samples",
        "$(BUILD_DIR)/analyzer_real_note_samples",
        "$(BUILD_DIR)/analyzer_guitarset",
        "$(BUILD_DIR)/analyzer_drum_samples",
    ]:
        assert forbidden not in refresh_recipe, "refresh target must not run analyzer binaries"

    detected_full_recipe = target_recipe(makefile, "measure-analyzer-detected-attributes-full")
    assert "measure-analyzer-attribute-rows-full" in detected_full_recipe, "full detected target must regenerate full rows"
    assert "$(MAKE) print-analyzer-detected-attributes" in detected_full_recipe, (
        "full detected target must reuse the print-only target"
    )

    patterns_full_recipe = target_recipe(makefile, "measure-analyzer-patterns-full")
    assert "measure-analyzer-attribute-rows-full" in patterns_full_recipe, "full pattern target must measure full rows first"
    assert "analyze-drum-tom-bleed-caps" in patterns_full_recipe, "full pattern target must run full drum diagnostics"
    assert "$(MAKE) report-analyzer-patterns-from-rows-full" in patterns_full_recipe, (
        "full pattern target must use measured rows without rerunning the bounded target"
    )

    full_report_recipe = target_recipe(makefile, "report-analyzer-patterns-from-rows-full")
    assert "$(MAKE) report-analyzer-patterns-from-rows REPORT_FULL_DRUM_SKIP=0" in full_report_recipe, (
        "full report helper must suppress the bounded skip message"
    )
    assert "$(RUN_WITH_DURATION) analyzer_pattern_full_report_sections" in full_report_recipe, (
        "full report helper must fan out full pattern sections"
    )
    assert "cat $(MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS)" in full_report_recipe, (
        "full report helper must print full pattern sections in deterministic order"
    )
    full_section_recipes = "\n".join(
        target_recipe(makefile, target)
        for target in [
            "$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_EXACT_REPORT)",
        ]
    )
    full_drum_report_recipe = target_recipe(makefile, "$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT)")
    assert "$(BUILD_DIR)/drum_full_attribute_rows.tsv" not in full_drum_report_recipe.splitlines()[0], (
        "full drum pattern report must not prebuild serial full-row dumps"
    )
    assert "$(MAKE) find-drum-full-attribute-patterns" in full_section_recipes, (
        "full report helper must mine protected full-drum rows through the parallel exact TSV"
    )
    assert "$(MAKE) find-drum-full-exact-attribute-patterns" in full_section_recipes, (
        "full report helper must mine exact full gate rows"
    )
    assert "$(MEASURE_DRUM_FULL_PATTERN_ARGS)" in full_section_recipes, (
        "full drum pattern target needs bounded default args"
    )

    shadow_recipe = target_recipe(makefile, "evaluate-real-note-display-shadow")
    assert "scripts/evaluate_real_note_display_shadow.py" in shadow_recipe, (
        "display shadow target must use the dedicated evaluator"
    )
    assert "$(or $(DISPLAY_SHADOW_ARGS),--summary-only)" in shadow_recipe, (
        "display shadow target should default to concise output"
    )

    row_confusion_recipe = target_recipe(makefile, "find-real-note-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in row_confusion_recipe, (
        "row-confusion mining should default to runtime-observable fields"
    )
    assert "--include-row-context" not in row_confusion_recipe, (
        "row-confusion auto-search must not use display-row fields as candidate rules"
    )
    practical_row_confusion_recipe = target_recipe(makefile, "find-real-note-practical-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in practical_row_confusion_recipe, (
        "practical row-confusion mining should keep runtime-observable fields"
    )
    assert "$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS)" in practical_row_confusion_recipe, (
        "practical row-confusion mining should use the bounded low-false defaults"
    )
    assert "--include-row-context" not in practical_row_confusion_recipe, (
        "practical row-confusion auto-search must not mine circular display-row fields"
    )
    focused_row_confusion_recipe = target_recipe(makefile, "find-real-note-focused-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in focused_row_confusion_recipe, (
        "focused row-confusion mining should keep runtime-observable field exclusions"
    )
    assert "$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS)" in focused_row_confusion_recipe, (
        "focused row-confusion mining should use the protected detector-rule defaults"
    )
    assert "--include-row-context" not in focused_row_confusion_recipe, (
        "focused detector-side row-confusion mining must not use circular display-row fields"
    )
    for text in [
        "--exclude-field buffer_strongest_row",
        "--exclude-field buffer_visual_strongest_row",
    ]:
        assert text in makefile, f"runtime row-confusion excludes must include {text}"
    for text in [
        "MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8",
        "--min-positive-samples 20",
        "--max-negative-samples 20",
        "--max-conditions 2",
    ]:
        assert text in makefile, f"practical row-confusion defaults must include {text}"
    for text in [
        "MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8",
        "--max-conditions 3",
        "--protected-scope same-source-correct-row",
    ]:
        assert text in makefile, f"focused row-confusion defaults must include {text}"
    visual_row_confusion_recipe = target_recipe(makefile, "find-real-note-visual-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in visual_row_confusion_recipe, (
        "visual row-confusion mining should default to runtime-observable fields"
    )
    assert "$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS)" in visual_row_confusion_recipe, (
        "visual row-confusion mining should use bounded practical defaults"
    )
    assert "--include-row-context" not in visual_row_confusion_recipe, (
        "visual row-confusion auto-search must not mine circular display-row fields"
    )
    focused_visual_row_confusion_recipe = target_recipe(makefile, "find-real-note-focused-visual-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in focused_visual_row_confusion_recipe, (
        "focused visual row-confusion mining should keep runtime field exclusions"
    )
    assert "$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)" in focused_visual_row_confusion_recipe, (
        "focused visual row-confusion mining should use the protected diagnostic defaults"
    )
    assert "--include-row-context" not in focused_visual_row_confusion_recipe, (
        "focused row-context diagnostics should be controlled by the default args variable"
    )
    for text in [
        "MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8",
        "--protected-scope same-source-correct-row",
        "--include-row-context",
    ]:
        assert text in makefile, f"focused visual row-confusion defaults must include {text}"
    assert ".PHONY: find-real-note-row-confusion-patterns find-real-note-practical-row-confusion-patterns find-real-note-focused-row-confusion-patterns find-real-note-visual-row-confusion-patterns find-real-note-focused-visual-row-confusion-patterns" in makefile, (
        "all real-note row-confusion shortcuts should be phony"
    )
    for field in [
        "expected_midi",
        "raw_local_best_note",
        "raw_octave_down_ratio",
        "raw_third_octave_up_ratio",
        "expected_row_pitch_delta",
        "debug_delta",
        "debug_abs_delta",
    ]:
        assert f"--exclude-field {field}" in makefile, (
            f"runtime row-confusion excludes must include ground-truth field {field}"
        )

    status_recipe = target_recipe(makefile, "find-instrument-status-patterns")
    assert "scripts/find_instrument_owner_patterns.py" in status_recipe, "status search must use the pattern miner"
    assert "$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)" in status_recipe, "status search needs direct defaults"
    assert "--status-top-buckets 0 $(PATTERN_ARGS)" in status_recipe, (
        "custom status search args must stay in final-status mode"
    )

    for variable in [
        "MEASURE_ANALYZER_REPORT",
        "PATTERN_REPORT_ARGS",
        "ATTRIBUTE_ROW_REPORT_ARGS",
        "REPORT_FULL_DRUM_SKIP",
        "INSTRUMENT_DETECTED_ATTRIBUTE_ROWS",
        "REAL_NOTE_DETECTED_ATTRIBUTE_ROWS",
        "REAL_NOTE_MISS_ATTRIBUTE_ROWS",
        "GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS",
        "GUITAR_CHORD_MISS_ATTRIBUTE_ROWS",
        "MEASURE_ANALYZER_ROW_DUMPS",
        "MEASURE_INSTRUMENT_PATTERN_ARGS",
        "MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS",
        "REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES",
        "MEASURE_GUITAR_PATTERN_ARGS",
        "MEASURE_DRUM_PATTERN_ARGS",
        "MEASURE_DRUM_FULL_PATTERN_ARGS",
        "MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS",
        "DRUM_PATTERN_JOBS",
        "REAL_NOTE_PATTERN_JOBS",
        "DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS",
        "DRUM_FULL_EXACT_ATTRIBUTE_ROWS",
        "PRIMARY_DRUM_DEBUG_ERRS",
        "FULL_DRUM_DEBUG_ERRS",
        "MEASURE_ANALYZER_JOBS",
        "DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT",
        "DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT",
    ]:
        assert f"{variable} ?=" in makefile, f"missing overridable {variable}"

    print("test_measure_analyzer_patterns_makefile: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
