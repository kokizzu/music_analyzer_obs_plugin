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


def main() -> int:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    recipe = target_recipe(makefile, "report-analyzer-patterns-from-rows")
    expected = [
        "$(MAKE) print-analyzer-detected-attributes",
        "scripts/report_analyzer_attribute_patterns.py",
        "$(MAKE) find-instrument-owner-patterns",
        "$(MAKE) find-instrument-status-patterns",
        "$(MAKE) find-real-note-attribute-patterns",
        "$(MAKE) find-real-note-row-confusion-patterns",
        "$(MAKE) find-guitar-chord-mix-attribute-patterns",
        "$(MAKE) analyze-guitar-chord-mix-recovery",
        "$(MAKE) analyze-guitar-chord-mix-extra-components",
        "$(MAKE) find-drum-primary-attribute-patterns",
        "$(MAKE) analyze-drum-spread-gate-matrix",
        "$(MAKE) find-drum-spread-exact-attribute-patterns",
        "$(MEASURE_INSTRUMENT_PATTERN_ARGS)",
        "$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)",
        "$(MEASURE_GUITAR_PATTERN_ARGS)",
        "$(RECOVERY_ARGS)",
        "$(EXTRA_COMPONENT_ARGS)",
        "$(MEASURE_DRUM_PATTERN_ARGS)",
        "$(PATTERN_REPORT_ARGS)",
        "measure-analyzer-patterns-full",
    ]
    for text in expected:
        assert text in recipe, f"report-analyzer-patterns-from-rows does not include {text}"
    assert "$(MAKE) find-drum-full-attribute-patterns" not in recipe, (
        "default pattern report must not mine exhaustive full-drum rows"
    )

    pattern_recipe = target_recipe(makefile, "measure-analyzer-patterns")
    assert "measure-analyzer-attribute-rows" in pattern_recipe, "pattern target must refresh bounded rows"
    assert "$(MAKE) report-analyzer-patterns-from-rows" in pattern_recipe, (
        "pattern target must reuse the print/report helper"
    )

    report_recipe = target_recipe(makefile, "measure-analyzer-pattern-report")
    assert "$(MAKE) measure-analyzer-patterns" in report_recipe, "report target must reuse the measurement target"
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

    assert "PARALLEL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(PARALLEL_TEST_JOBS))" in makefile, (
        "parallel aggregate targets must reuse an inherited GNU make jobserver"
    )
    max_samples_recipe = target_recipe(makefile, "test-real-world-samples-max")
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_WORLD_SAMPLE_MAX_TARGETS)" in max_samples_recipe, (
        "max real-world sample tests must fan out through jobserver-aware make"
    )
    real_note_sharded_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-parallel")
    assert "REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))" in makefile, (
        "real-note shard tests must not force nested jobserver mode"
    )
    assert "$(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) $(REAL_NOTE_FULL_MIX_SHARD_TARGETS)" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "scripts/prepare_nsynth_samples.py\" -nt \"$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv\"" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must skip sample regeneration when the manifest is fresh"
    )
    real_note_shard_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-shard-%")
    for text in [
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_FULL_MIX_SHARDS)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=\"$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)\"",
        "MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0",
    ]:
        assert text in real_note_shard_recipe, f"real-note shard target must include {text}"
    instrument_sharded_recipe = target_recipe(makefile, "test-instrument-samples-parallel")
    assert "INSTRUMENT_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))" in makefile, (
        "generated instrument sample shards must not force nested jobserver mode"
    )
    assert "$(MAKE) $(INSTRUMENT_SAMPLE_TEST_MAKE_JOBS) $(INSTRUMENT_SAMPLE_SHARD_TARGETS)" in instrument_sharded_recipe, (
        "generated instrument sample parallel target must fan out deterministic shards through jobserver-aware make"
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
    assert "test-instrument-samples-parallel" in detector_regression_target_list, (
        "detector sample regression loop must use the sharded generated instrument sample gate"
    )
    assert "test-instrument-samples " not in detector_regression_target_list + " ", (
        "detector sample regression loop must not use the serial generated instrument sample gate"
    )
    assert "REAL_WORLD_SAMPLE_MAX_TARGETS :=" in makefile, "missing max real-world sample target list"
    assert "REAL_WORLD_SAMPLE_MAX_BASE_TARGETS :=" in makefile, (
        "max real-world sample target list must avoid duplicated default/max targets"
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
    assert "drum_full_attribute_rows.tsv" in drum_full_recipe, "full drum search must use measured TSV rows"
    assert "scripts/find_drum_attribute_patterns.py" in drum_full_recipe, "full drum search must use the pattern miner"
    assert "$(BUILD_DIR)/drum_full_attribute_rows.tsv" in drum_full_recipe, (
        "full drum search must depend on the stale-aware full TSV target"
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
            "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@.tmp\"",
            "guitar_chord_mix_attributes.out",
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
    assert "$(MAKE) $(REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS) $(REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS)" in real_note_attribute_recipe, (
        "real-note attribute TSV must build shard parts in parallel even when top-level make is serial"
    )
    assert "awk 'FNR == 1 && NR != 1 { next } { print }'" in real_note_attribute_recipe, (
        "real-note attribute TSV must concatenate shard rows while dropping duplicate headers"
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
    assert "$(MAKE) $(INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS) $(INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS)" in instrument_attribute_recipe, (
        "instrument attribute TSV must build shard parts in parallel even when top-level make is serial"
    )
    assert "awk 'FNR == 1 && NR != 1 { next } { print }'" in instrument_attribute_recipe, (
        "instrument attribute TSV must concatenate shard rows while dropping duplicate headers"
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

    stale_aware_attribute_shortcuts = {
        "inspect-instrument-sample-owner-buckets": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "find-instrument-owner-patterns": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "find-instrument-status-patterns": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "filter-instrument-attribute-rows": "$(BUILD_DIR)/instrument_sample_attributes.tsv",
        "inspect-real-note-attribute-buckets": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-attribute-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "find-real-note-row-confusion-patterns": "$(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "analyze-guitar-chord-mix-recovery": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "analyze-guitar-chord-mix-extra-components": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "inspect-guitar-chord-mix-attribute-buckets": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "find-guitar-chord-mix-attribute-patterns": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
    }
    for target, tsv in stale_aware_attribute_shortcuts.items():
        shortcut_recipe = target_recipe(makefile, target)
        assert tsv in shortcut_recipe.splitlines()[0], f"{target} must depend on {tsv}"
        assert "if [ ! -f" not in shortcut_recipe, (
            f"{target} must use Make timestamp checks, not existence-only TSV refresh"
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
        "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
    ]:
        attribute_recipe = target_recipe(makefile, target)
        assert "$@.tmp" in attribute_recipe, f"{target} must write through a temporary TSV"
        assert 'mv "$@.tmp" "$@"' in attribute_recipe, f"{target} must publish TSV atomically"
    guitar_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv")
    assert 'MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@.tmp"' in guitar_attribute_recipe, (
        "guitar chord attribute exporter must not stream directly to the final TSV"
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
    assert "$(MAKE) find-drum-full-attribute-patterns" in full_report_recipe, (
        "full report helper must mine exhaustive full-drum rows"
    )
    assert "$(MAKE) find-drum-full-exact-attribute-patterns" in full_report_recipe, (
        "full report helper must mine exact full gate rows"
    )
    assert "$(MEASURE_DRUM_FULL_PATTERN_ARGS)" in full_report_recipe, (
        "full drum pattern target needs bounded default args"
    )

    status_recipe = target_recipe(makefile, "find-instrument-status-patterns")
    assert "scripts/find_instrument_owner_patterns.py" in status_recipe, "status search must use the pattern miner"
    assert "$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)" in status_recipe, "status search needs direct defaults"

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
        "MEASURE_GUITAR_PATTERN_ARGS",
        "MEASURE_DRUM_PATTERN_ARGS",
        "MEASURE_DRUM_FULL_PATTERN_ARGS",
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
