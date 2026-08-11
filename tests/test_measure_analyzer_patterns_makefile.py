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


def assert_alias_target(makefile: str, target: str, dependency: str) -> None:
    assert re.search(
        rf"^{re.escape(target)}: {re.escape(dependency)}$", makefile, re.MULTILINE
    ), f"{target} must delegate directly to {dependency}"


def assert_atomic_build_recipe(makefile: str, target: str) -> None:
    recipe = target_recipe(makefile, target)
    assert 'tmp="$@.$$$$.tmp"' in recipe, f"{target} must build through a per-process temp file"
    assert '-o "$$tmp"' in recipe, f"{target} must write compiler/linker output to the temp file"
    assert '&& mv "$$tmp" "$@"' in recipe, f"{target} must publish the temp file atomically"


def continuation_variable_refs(makefile: str, variable: str) -> list[str]:
    lines = makefile.splitlines()
    prefix = f"{variable} := "
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue

        body = [line[len(prefix) :]]
        while body[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            index += 1
            body.append(lines[index])
        return re.findall(r"\$\([^)]+\)", "\n".join(body))

    raise AssertionError(f"missing {variable}")


def continuation_variable_body(makefile: str, variable: str) -> str:
    lines = makefile.splitlines()
    prefix_re = re.compile(rf"^{re.escape(variable)}\s*[?:+]?=\s*")
    for index, line in enumerate(lines):
        match = prefix_re.match(line)
        if not match:
            continue

        body = [line[match.end() :]]
        while body[-1].rstrip().endswith("\\") and index + 1 < len(lines):
            index += 1
            body.append(lines[index])
        return "\n".join(body)

    raise AssertionError(f"missing {variable}")


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

    standalone_recipe = target_recipe(makefile, "test-standalone")
    assert "$(RUN_WITH_DURATION) test_standalone_parallel" in standalone_recipe, (
        "standalone checks must be fanned out through the duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(STANDALONE_TEST_TARGETS)" in standalone_recipe, (
        "standalone checks must use the configured parallel test jobs"
    )
    assert "android-check" in standalone_recipe.splitlines()[0], (
        "test-standalone must keep the Android build isolation check"
    )
    assert (
        "STANDALONE_TEST_TARGETS := test-standalone-isolation "
        "test-standalone-version-complete test-standalone-version-bass-guitar "
        "test-standalone-self-test-complete test-standalone-self-test-bass-guitar"
    ) in makefile, "standalone parallel target list must include every standalone check"
    standalone_subtarget_commands = {
        "test-standalone-isolation": "check_standalone_isolation",
        "test-standalone-version-complete": "check_standalone_version_complete",
        "test-standalone-version-bass-guitar": "check_standalone_version_bass_guitar",
        "test-standalone-self-test-complete": "standalone_self_test",
        "test-standalone-self-test-bass-guitar": "standalone_bass_guitar_self_test",
    }
    for target, duration_label in standalone_subtarget_commands.items():
        assert duration_label in target_recipe(makefile, target), (
            f"{target} must preserve the {duration_label} check"
        )

    assert_alias_target(makefile, "test-drum-samples", "test-drum-samples-parallel")
    drum_parallel_recipe = target_recipe(makefile, "test-drum-samples-parallel")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_parallel" in drum_parallel_recipe, (
        "default drum sample gate must be fanned out through the duration wrapper"
    )
    assert "scripts/run_with_lock.sh" in drum_parallel_recipe, (
        "default drum sample gate must serialize writes to shared shard outputs"
    )
    drum_unlocked_recipe = target_recipe(makefile, "test-drum-samples-parallel-unlocked")
    for text in [
        "$(MAKE) $(DRUM_SAMPLE_TEST_MAKE_JOBS) $(DRUM_SAMPLE_SHARD_TARGETS)",
        "scripts/check_drum_sample_shards.py",
        "$(DRUM_SAMPLE_SHARD_OUTS)",
        '--rim-max-false-percent "$(DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT)"',
    ]:
        assert text in drum_unlocked_recipe, (
            f"default drum sample parallel gate must include {text}"
        )
    drum_serial_recipe = target_recipe(makefile, "test-drum-samples-serial")
    assert "analyzer_drum_samples env" in drum_serial_recipe, (
        "default drum serial fallback must keep the original single-process gate"
    )
    assert 'MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT)"' in drum_serial_recipe, (
        "default drum serial fallback must keep the configurable rim false-positive gate"
    )
    assert "DRUM_SAMPLE_LOCK_DIR ?= $(BUILD_DIR)/drum_samples.lock" in makefile, (
        "default drum shard aggregation must have a stable lock path"
    )

    assert_alias_target(makefile, "test-drum-samples-spread", "test-drum-samples-spread-parallel")
    spread_parallel_recipe = target_recipe(makefile, "test-drum-samples-spread-parallel")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_spread_parallel" in spread_parallel_recipe, (
        "spread drum sample gate must be fanned out through the duration wrapper"
    )
    assert "scripts/run_with_lock.sh" in spread_parallel_recipe, (
        "spread drum sample gate must serialize writes to shared shard outputs"
    )
    spread_unlocked_recipe = target_recipe(makefile, "test-drum-samples-spread-parallel-unlocked")
    for text in [
        "$(MAKE) $(DRUM_SAMPLE_SPREAD_TEST_MAKE_JOBS) $(DRUM_SAMPLE_SPREAD_SHARD_TARGETS)",
        "scripts/check_drum_sample_shards.py",
        "$(DRUM_SAMPLE_SPREAD_TEST_SHARD_OUTS)",
    ]:
        assert text in spread_unlocked_recipe, (
            f"spread drum sample parallel gate must include {text}"
        )
    spread_serial_recipe = target_recipe(makefile, "test-drum-samples-spread-serial")
    assert "analyzer_drum_samples_spread env" in spread_serial_recipe, (
        "spread drum sample serial fallback must keep the original single-process gate"
    )

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
    for variable in [
        "MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS",
        "MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS",
    ]:
        refs = continuation_variable_refs(makefile, variable)
        duplicates = sorted({ref for ref in refs if refs.count(ref) > 1})
        assert not duplicates, f"{variable} must not list duplicate outputs: {duplicates}"
    section_recipes = "\n".join(
        target_recipe(makefile, target)
        for target in [
            "$(MEASURE_ANALYZER_PATTERN_DETECTED_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT)",
            "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT)",
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
        "scripts/summarize_real_note_attributes.py",
        "$(MEASURE_REAL_NOTE_SUMMARY_ARGS)",
        "$(MAKE) find-real-note-attribute-patterns",
        "$(MAKE) find-real-note-row-confusion-patterns",
        "$(MAKE) find-real-note-visual-row-confusion-patterns",
        "$(MAKE) find-real-note-weak-expected-patterns",
        "$(MAKE) find-real-note-weak-visual-expected-patterns",
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
        "$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS)",
        "$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS)",
        "$(MEASURE_GUITAR_PATTERN_ARGS)",
        "$(PRIMARY_ORDER_ARGS)",
        "$(RECOVERY_ARGS)",
        "$(EXTRA_COMPONENT_ARGS)",
        "$(MEASURE_DRUM_PATTERN_ARGS)",
        "$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS)",
        "$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS)",
        "$(PATTERN_REPORT_ARGS)",
        "measure-analyzer-patterns-full",
    ]
    for text in expected:
        assert text in section_recipes, f"pattern report section recipes do not include {text}"
    assert (
        "MEASURE_REAL_NOTE_SUMMARY_ARGS ?= --detail-limit 8 --sample-limit 5"
    ) in makefile, (
        "standard analyzer pattern reports must include bounded real-note weak bucket diagnostics"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT)" in continuation_variable_body(
        makefile, "MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS"
    ), (
        "standard pattern report fanout must include the real-note coverage summary"
    )
    real_note_summary_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT)"
    )
    assert "real-note full-mix coverage summary:" in real_note_summary_recipe, (
        "real-note coverage section must be labeled in the measurement report"
    )
    assert "$(PYTHON) scripts/summarize_real_note_attributes.py" in real_note_summary_recipe, (
        "real-note coverage section must run the real-note attribute summarizer"
    )
    assert "$(MEASURE_REAL_NOTE_SUMMARY_ARGS)" in real_note_summary_recipe, (
        "real-note coverage section must use bounded detailed summary defaults"
    )
    assert "$(MAKE) find-drum-full-attribute-patterns" not in recipe, (
        "default pattern report must not mine exhaustive full-drum rows"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT)"
    ).splitlines()[0], (
        "protected drum primary report must wait for spread rows to avoid parallel TSV regeneration"
    )
    assert "MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP := $(BUILD_DIR)/measure_analyzer_pattern_drum_protected_rows.stamp" in makefile, (
        "pattern reports must use a shared protected drum row refresh stamp"
    )
    visual_report_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT)"
    )
    runtime_row_excludes = re.search(
        r"^REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES \?= (?P<value>(?:.*\\\n)+.*)$",
        makefile,
        re.MULTILINE,
    )
    assert runtime_row_excludes is not None, "missing real-note runtime row-confusion excludes"
    for text in [
        "--exclude-field expected_row_visual_exact_level",
        "--exclude-field expected_row_visual_pitch_level",
        "--exclude-field expected_row_visual_pitch_delta",
        "--exclude-field expected_visual_exact_row_count",
        "--exclude-field expected_visual_pitch_row_count",
        "--exclude-field strongest_row_exact_level",
        "--exclude-field strongest_row_pitch_level",
        "--exclude-field strongest_row_pitch_delta",
        "--exclude-field visual_strongest_row_exact_level",
        "--exclude-field visual_strongest_row_pitch_level",
        "--exclude-field visual_strongest_row_pitch_delta",
        "--exclude-field bass_level",
        "--exclude-field guitar_level",
        "--exclude-field piano_level",
        "--exclude-field vocal_level",
        "--exclude-field other_level",
        "--exclude-field amb_level",
        "--exclude-field bass_visual_level",
        "--exclude-field guitar_visual_level",
        "--exclude-field piano_visual_level",
        "--exclude-field vocal_visual_level",
        "--exclude-field other_visual_level",
        "--exclude-field amb_visual_level",
    ]:
        assert text in runtime_row_excludes.group("value"), (
            "runtime visual row-confusion mining must not use row-output fields"
        )
    assert "$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)" in visual_report_recipe, (
        "visual row-confusion report should use protected row-context diagnostics"
    )
    assert "$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)" not in visual_report_recipe, (
        "visual row-confusion report must not reuse strongest-row defaults"
    )
    octave_report_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT)"
    )
    assert "$(MAKE) find-real-note-octave-displacement-patterns" in octave_report_recipe, (
        "octave displacement report must use the dedicated real-note octave miner"
    )
    assert "$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS)" in octave_report_recipe, (
        "octave displacement report must use bounded octave-displacement defaults"
    )
    octave_target_recipe = target_recipe(makefile, "find-real-note-octave-displacement-patterns")
    assert "--bucket-status octave_displacement" in octave_target_recipe, (
        "octave displacement target must mine octave-displacement buckets"
    )
    assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in octave_target_recipe, (
        "octave displacement target must run pattern search with configured parallel jobs"
    )
    weak_report_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT)"
    )
    assert "$(MAKE) find-real-note-weak-expected-patterns" in weak_report_recipe, (
        "weak expected-row report must use the dedicated real-note weak-row miner"
    )
    assert "$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS)" in weak_report_recipe, (
        "weak expected-row report must use bounded weak-row defaults"
    )
    weak_target_recipe = target_recipe(makefile, "find-real-note-weak-expected-patterns")
    assert "--bucket-status weak_expected_row" in weak_target_recipe, (
        "weak expected-row target must mine weak expected-row buckets"
    )
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in weak_target_recipe, (
        "weak expected-row mining must not report ground-truth fields as detector-rule candidates"
    )
    assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in weak_target_recipe, (
        "weak expected-row target must run pattern search with configured parallel jobs"
    )
    weak_visual_report_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT)"
    )
    assert "$(MAKE) find-real-note-weak-visual-expected-patterns" in weak_visual_report_recipe, (
        "weak visual expected-row report must use the dedicated real-note weak-row miner"
    )
    assert "$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS)" in weak_visual_report_recipe, (
        "weak visual expected-row report must use bounded weak-row defaults"
    )
    weak_visual_target_recipe = target_recipe(makefile, "find-real-note-weak-visual-expected-patterns")
    assert "--bucket-status weak_visual_expected_row" in weak_visual_target_recipe, (
        "weak visual expected-row target must mine weak visual expected-row buckets"
    )
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in weak_visual_target_recipe, (
        "weak visual expected-row mining must not report ground-truth fields as detector-rule candidates"
    )
    assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in weak_visual_target_recipe, (
        "weak visual expected-row target must run pattern search with configured parallel jobs"
    )
    protected_stamp_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP)"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT)" in protected_stamp_recipe.splitlines()[0], (
        "shared protected row refresh must wait for the spread matrix report"
    )
    assert "for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" in protected_stamp_recipe, (
        "shared protected row refresh must refresh HF and IDMT rows when missing or stale"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) analyze-hf-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows" in protected_stamp_recipe, (
        "shared protected row refresh must rebuild HF and IDMT rows in parallel"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in protected_stamp_recipe, (
        "shared protected row refresh must refresh stale optional full exact rows"
    )
    assert "$(MAKE) analyze-drum-full-merged-expected-attribute-rows" in protected_stamp_recipe, (
        "shared protected row refresh must refresh stale optional merged full rows"
    )
    assert 'touch "$@"' in protected_stamp_recipe, (
        "shared protected row refresh must publish a real stamp for parallel make synchronization"
    )
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT)"
    ).splitlines()[0], (
        "protected drum primary report must wait for the shared protected row refresh"
    )
    protected_drum_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT)"
    )
    assert "$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS)" in protected_drum_recipe, (
        "protected drum primary report must use bounded protected-pattern defaults"
    )
    assert 'PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"' not in protected_drum_recipe, (
        "protected drum primary report must not reuse the expensive generic drum pattern defaults"
    )
    protected_drum_target_recipe = target_recipe(
        makefile, "find-protected-drum-primary-attribute-patterns"
    )
    assert "$(or $(PATTERN_ARGS),$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS))" in protected_drum_target_recipe, (
        "direct protected drum primary mining must use bounded defaults when audit calls it without PATTERN_ARGS"
    )
    protected_drum_args = re.search(
        r"^MEASURE_PROTECTED_DRUM_PATTERN_ARGS \?= (?P<value>.*)$",
        makefile,
        re.MULTILINE,
    )
    assert protected_drum_args is not None, "missing protected drum pattern defaults"
    for text in [
        "--min-positive-samples 20",
        "--min-route-positive-samples 20",
        "--max-conditions 1",
        "--beam-width 40",
    ]:
        assert text in protected_drum_args.group("value"), (
            "protected drum pattern defaults should stay bounded for the standard report"
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
    assert "$(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP)" in target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT)"
    ).splitlines()[0], (
        "drum active false report must wait for the shared protected row refresh"
    )
    active_false_args = re.search(
        r"^MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS \?= (?P<value>.*)$",
        makefile,
        re.MULTILINE,
    )
    assert active_false_args is not None, "missing drum active false pattern defaults"
    assert "--exclude-fields kick_level" in active_false_args.group("value"), (
        "drum active false pattern defaults must avoid merged expected-level fields"
    )
    assert "--min-near-protected-score 0.10" in active_false_args.group("value"), (
        "drum active false pattern defaults must reject fragile near-protected candidates"
    )
    active_false_target_recipe = target_recipe(makefile, "find-drum-active-false-patterns")
    assert "$(or $(PATTERN_ARGS),$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS))" in active_false_target_recipe, (
        "direct drum active-false mining must use bounded defaults when audit calls it without PATTERN_ARGS"
    )
    active_false_protected = re.search(
        r"^MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS \?= (?P<value>.*)$",
        makefile,
        re.MULTILINE,
    )
    assert active_false_protected is not None, "missing active false extra protected row defaults"
    assert "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" not in active_false_protected.group("value"), (
        "bounded drum active false mining must not force exhaustive full-drum rows"
    )
    assert "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" not in active_false_protected.group("value"), (
        "bounded drum active false mining must not force merged expected full-drum rows"
    )
    assert "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" in active_false_protected.group("value"), (
        "drum active false mining must protect HF drum-kit primary true-hit rows"
    )
    assert "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" in active_false_protected.group("value"), (
        "drum active false mining must protect IDMT drum primary true-hit rows"
    )
    active_false_full_protected = re.search(
        r"^MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS \?= (?P<value>.*)$",
        makefile,
        re.MULTILINE,
    )
    assert active_false_full_protected is not None, "missing full active false extra protected row defaults"
    assert "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" in active_false_full_protected.group("value"), (
        "full drum active false mining must protect exact full-drum true-hit rows"
    )
    assert "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" in active_false_full_protected.group("value"), (
        "full drum active false mining must protect merged expected-hit rows"
    )
    assert "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" in active_false_full_protected.group("value"), (
        "full drum active false mining must still protect HF drum-kit primary true-hit rows"
    )
    assert "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" in active_false_full_protected.group("value"), (
        "full drum active false mining must still protect IDMT drum primary true-hit rows"
    )
    assert "DRUM_ACTIVE_EXTRA_PROTECTED_ROWS ?= $(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)" in makefile, (
        "direct drum active false mining must inherit the measured protected row defaults"
    )
    assert (
        "DRUM_ACTIVE_REFRESH_FULL_ROWS = $(if $(filter $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) "
        "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS),$(DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)),1,0)"
    ) in makefile, (
        "drum active false mining must refresh full rows only when full TSVs are protected inputs"
    )
    active_false_recipe = target_recipe(makefile, "find-drum-active-false-patterns")
    assert '$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in active_false_recipe, (
        "direct drum active false mining must refresh stale spread rows"
    )
    assert 'scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in active_false_recipe, (
        "direct drum active false mining must refresh spread rows when the parser changes"
    )
    assert "for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" in active_false_recipe, (
        "direct drum active false mining must refresh HF and IDMT protected rows when missing"
    )
    assert '[ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ]' in active_false_recipe, (
        "direct drum active false mining must refresh stale HF and IDMT protected rows"
    )
    assert '[ "scripts/analyze_drum_primary_debug.py" -nt "$$path" ]' in active_false_recipe, (
        "direct drum active false mining must refresh HF and IDMT rows when the parser changes"
    )
    assert '[ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]' in active_false_recipe, (
        "direct drum active false mining must not refresh optional full exact rows unless enabled"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in active_false_recipe, (
        "direct drum active false mining must refresh stale full exact rows through the parallel builder"
    )
    assert '[ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ]' in active_false_recipe, (
        "direct drum active false mining must not refresh optional merged expected rows unless enabled"
    )
    assert "$(MAKE) analyze-drum-full-merged-expected-attribute-rows" in active_false_recipe, (
        "direct drum active false mining must refresh stale merged expected full rows"
    )
    assert "for rows in $(DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)" in active_false_recipe, (
        "drum active false mining must iterate over protected TSV inputs at execution time"
    )
    assert '--extra-protected-rows "$$rows"' in active_false_recipe, (
        "drum active false mining must pass each existing protected TSV as a separate parser argument"
    )
    for target in [
        "analyze-drum-active-false-rows",
        "analyze-drum-rule-flags",
        "analyze-drum-active-thresholds",
    ]:
        stale_summary_recipe = target_recipe(makefile, target)
        assert '$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in stale_summary_recipe, (
            f"{target} must refresh stale spread rows after detector changes"
        )
        assert 'scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in stale_summary_recipe, (
            f"{target} must refresh stale spread rows after parser changes"
        )
        assert "$(MAKE) analyze-drum-spread-gate-matrix" in stale_summary_recipe, (
            f"{target} must rebuild spread rows through the matrix target"
        )
    assert (
        "find-drum-active-false-patterns-full: DRUM_ACTIVE_EXTRA_PROTECTED_ROWS := "
        "$(MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS)"
    ) in makefile, (
        "full drum active false mining wrapper must opt into full protected row inputs"
    )
    assert "find-drum-active-false-patterns-full: find-drum-active-false-patterns" in makefile, (
        "full drum active false mining wrapper must reuse the direct pattern miner"
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
    require_cached_rows_recipe = target_recipe(makefile, "require-cached-analyzer-attribute-rows")
    assert "$(CACHED_ANALYZER_PATTERN_INPUT_PATHS)" in require_cached_rows_recipe, (
        "cached row guard must check the full cached pattern input list"
    )
    assert "missing cached analyzer pattern input:" in require_cached_rows_recipe, (
        "cached row guard must print every missing input path"
    )
    assert "run make measure-analyzer-attribute-rows" in require_cached_rows_recipe, (
        "cached row guard must tell users how to regenerate analyzer rows"
    )
    cached_report_recipe = target_recipe(makefile, "report-analyzer-patterns-from-cached-rows")
    assert "require-cached-analyzer-attribute-rows" in cached_report_recipe, (
        "cached report helper must validate row files before mining patterns"
    )
    assert "analyzer_cached_pattern_report_sections" in cached_report_recipe, (
        "cached report helper must report a distinct aggregate duration"
    )
    assert "$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS)" in cached_report_recipe, (
        "cached report helper must mine cached report sections in parallel"
    )
    assert "measure-analyzer-pattern-report-sections" not in cached_report_recipe, (
        "cached report helper must not call normal report sections that can rebuild analyzer TSVs"
    )
    cached_section_refs = continuation_variable_refs(
        makefile, "MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS"
    )
    for report_var in [
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OWNERSHIP_REPORT)",
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT)",
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT)",
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT)",
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT)",
        "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT)",
    ]:
        assert report_var in cached_section_refs, (
            f"cached analyzer report sections must include {report_var}"
        )
    cached_detected_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_CACHED_PATTERN_DETECTED_REPORT)"
    )
    assert "print_analyzer_detected_attributes.py" in cached_detected_recipe, (
        "cached detected report must call the print script directly"
    )
    for forbidden in [
        "$(BUILD_DIR)/analyzer_real_note_samples",
        "$(BUILD_DIR)/analyzer_instrument_samples",
        "prepare-real-note-samples",
        "analyze-drum-spread-gate-matrix",
    ]:
        assert forbidden not in cached_detected_recipe, (
            f"cached detected report must not depend on {forbidden}"
        )
    cached_real_note_row_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT)"
    )
    for required in [
        "scripts/find_real_note_attribute_patterns.py",
        "--bucket-status row_confusion",
        "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)",
        "$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)",
    ]:
        assert required in cached_real_note_row_recipe, (
            f"cached real-note row-confusion report must include {required}"
        )
    cached_real_note_visual_row_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT)"
    )
    for required in [
        "--bucket-status visual_row_confusion",
        "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)",
        "$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)",
    ]:
        assert required in cached_real_note_visual_row_recipe, (
            f"cached real-note visual-row report must include {required}"
        )
    for recipe_name, cached_recipe in [
        ("row-confusion", cached_real_note_row_recipe),
        ("visual-row-confusion", cached_real_note_visual_row_recipe),
    ]:
        for forbidden in [
            "$(MAKE) find-real-note",
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "prepare-real-note-samples",
        ]:
            assert forbidden not in cached_recipe, (
                f"cached real-note {recipe_name} report must not call rebuild path {forbidden}"
            )
    cached_pattern_recipe = target_recipe(makefile, "measure-analyzer-patterns-cached")
    assert "require-cached-analyzer-attribute-rows" in cached_pattern_recipe, (
        "cached pattern target must fail fast when row files are missing"
    )
    assert "$(MAKE) report-analyzer-patterns-from-cached-rows" in cached_pattern_recipe, (
        "cached pattern target must reuse the cached report helper"
    )
    assert "measure-analyzer-attribute-rows" not in cached_pattern_recipe.splitlines()[0], (
        "cached pattern target must not regenerate bounded analyzer rows"
    )
    assert (
        "MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY := "
        "$(BUILD_DIR)/measure_analyzer_cached_pattern_candidate_summary.txt"
    ) in makefile, (
        "cached pattern candidate summary must have a stable file-backed output path"
    )
    assert re.search(
        r"^\$\(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY\): "
        r"\$\(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS\) "
        r"scripts/summarize_detector_route_report\.py \| \$\(BUILD_DIR\)",
        makefile,
        re.MULTILINE,
    ), "cached candidate summary must derive from saved cached pattern sections"
    cached_summary_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"
    )
    for required in [
        'tmp_report="$@.$$$$.report"',
        'tmp="$@.$$$$.tmp"',
        'cat $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS) > "$$tmp_report"',
        '$(PYTHON) scripts/summarize_detector_route_report.py "$$tmp_report" > "$$tmp"',
        'rm -f "$$tmp_report"',
        'mv "$$tmp" "$@"',
    ]:
        assert required in cached_summary_recipe, (
            f"cached candidate summary recipe must include {required}"
        )
    cached_summary_alias = target_recipe(makefile, "measure-analyzer-patterns-cached-summary")
    assert "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" in cached_summary_alias.splitlines()[0], (
        "cached summary helper must depend on the file-backed summary"
    )
    assert 'cat "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"' in cached_summary_alias, (
        "cached summary helper must print the compact candidate report"
    )
    assert_alias_target(makefile, "analyze-real-note-misses", "analyze-real-note-misses-parallel")
    real_note_misses_serial_recipe = target_recipe(makefile, "analyze-real-note-misses-serial")
    assert "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999" in real_note_misses_serial_recipe, (
        "serial real-note miss diagnostics must tolerate misses long enough to print the summary"
    )
    real_note_misses_parallel_recipe = target_recipe(makefile, "analyze-real-note-misses-parallel")
    assert "$(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_TARGETS)" in real_note_misses_parallel_recipe, (
        "parallel real-note miss diagnostics must run every verbose shard target"
    )
    assert "$(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_ERRS)" in real_note_misses_parallel_recipe, (
        "parallel real-note miss diagnostics must aggregate every shard stderr file"
    )
    real_note_misses_shard_recipe = target_recipe(makefile, "analyze-real-note-misses-shard-%")
    for text in [
        "MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1",
        'MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)"',
        'MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*"',
        "MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999",
        '2> "$(BUILD_DIR)/real_note_full_mix_verbose_shard_$*.err"',
    ]:
        assert text in real_note_misses_shard_recipe, (
            f"real-note verbose shard recipe must include {text}"
        )
    report_recipe = target_recipe(makefile, "measure-analyzer-pattern-report")
    assert "$(MAKE) -s measure-analyzer-patterns" in report_recipe, (
        "saved report target must reuse the measurement target without make recipe echo"
    )
    assert "$(MEASURE_ANALYZER_REPORT)" in report_recipe, "report target must write the configured report path"

    drum_manifest_recipe = target_recipe(makefile, "$(DRUM_SAMPLE_BUILD_DIR)/manifest.tsv")
    assert "FORCE" in drum_manifest_recipe.splitlines()[0], (
        "default drum sample manifest target must rerun the metadata-aware preparer"
    )
    assert "$(MAKE) prepare-drum-samples" in drum_manifest_recipe, (
        "default drum sample manifest target must delegate to the default prepare target"
    )
    spread_recipe = target_recipe(makefile, "test-drum-samples-spread-serial")
    spread_manifest_recipe = target_recipe(makefile, "$(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv")
    assert "FORCE" in spread_manifest_recipe.splitlines()[0], (
        "spread drum sample manifest target must rerun the metadata-aware preparer"
    )
    assert "analyze-drum-spread-gate-matrix: analyze-drum-spread-gate-matrix-parallel" in makefile, (
        "default spread matrix target must use the parallel spread row builder"
    )
    spread_matrix_recipe = target_recipe(makefile, "analyze-drum-spread-gate-matrix-parallel")
    spread_matrix_unlocked_recipe = target_recipe(
        makefile, "analyze-drum-spread-gate-matrix-parallel-unlocked"
    )
    spread_matrix_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_spread_exact_attribute_rows_%.tsv")
    assert "scripts/run_with_lock.sh \"$(DRUM_SPREAD_EXACT_ATTRIBUTE_LOCK_DIR)\"" in spread_matrix_recipe, (
        "parallel spread matrix target must lock the whole generate/check/report sequence"
    )
    assert '"$(MAKE)" analyze-drum-spread-gate-matrix-parallel-unlocked' in spread_matrix_recipe, (
        "parallel spread matrix target must run the checked implementation under the lock"
    )
    assert not re.search(r"\n\t.*scripts/check_drum_sample_shards\.py", spread_matrix_recipe), (
        "spread matrix checker must not run outside the shared row lock"
    )
    assert "$(MAKE) prepare-drum-samples-spread" in spread_manifest_recipe, (
        "spread sample manifest target must delegate to the spread prepare target"
    )
    audit_recipe = target_recipe(makefile, "inspect-drum-sample-coverage")
    assert "--audit" in audit_recipe, "drum sample coverage target must use read-only audit mode"
    assert "DRUM_SAMPLE_FULL_BUILD_DIR" in audit_recipe, (
        "drum sample coverage audit should match the full-library spread configuration"
    )
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in spread_matrix_shard_recipe, (
        "spread matrix row dump must include primary miss labels, not only debug rows"
    )
    for category in ["KICK", "SNARE", "HIHAT", "CRASH", "TOM", "RIDE", "RIM"]:
        env_name = f"MUSIC_ANALYZER_DRUM_SAMPLE_MIN_{category}_PRIMARY_RECALL_PERCENT"
        var_name = f"$(DRUM_SAMPLE_SPREAD_MIN_{category}_PRIMARY_PERCENT)"
        assert env_name in spread_recipe, (
            f"test-drum-samples-spread-serial must enforce {env_name}"
        )
        assert var_name in spread_recipe, (
            f"test-drum-samples-spread-serial must use {var_name}"
        )
        assert var_name in spread_matrix_unlocked_recipe, (
            "parallel spread matrix checker must enforce the configured primary thresholds"
        )

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
        "test-egmd-shard-check",
        "test-maestro-shard-check",
        "test-instrument-family-shard-check",
        "test-musicnet-shard-check",
        "test-real-note-full-mix-shard-check",
        "test-real-note-sample-shard-check",
        "android-check",
    ]:
        assert target in analysis_script_target_list, (
            f"analysis script parallel target list must include {target}"
        )
    assert re.search(
        r"^ANALYSIS_SCRIPT_TEST_TARGETS \+= test-detector-route-report-summary$",
        makefile,
        re.MULTILINE,
    ), "analysis script parallel target list must include the detector route summary test"
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
    for dataset, var_prefix, label in [
        ("mdb", "MDB_DRUMS", "MDB Drums"),
        ("star", "STAR_DRUMS", "STAR Drums"),
    ]:
        target = f"test-{dataset}-drums-samples"
        assert_alias_target(makefile, target, f"{target}-parallel")
        parallel_recipe = target_recipe(makefile, f"{target}-parallel")
        unlocked_recipe = target_recipe(makefile, f"{target}-parallel-unlocked")
        shard_recipe = target_recipe(makefile, f"{target}-shard-%")
        serial_recipe = target_recipe(makefile, f"{target}-serial")
        assert "scripts/check_egmd_shards.py" in parallel_recipe, (
            f"{label} parallel target must depend on the E-GMD shard checker"
        )
        assert "scripts/run_with_lock.sh" in parallel_recipe, (
            f"{label} parallel target must lock shared shard outputs"
        )
        assert f"$(MAKE) $({var_prefix}_TEST_MAKE_JOBS) $({var_prefix}_SHARD_TARGETS)" in unlocked_recipe, (
            f"{label} parallel target must fan out deterministic recording shards"
        )
        assert f"$({var_prefix}_SHARD_OUTS)" in unlocked_recipe, (
            f"{label} parallel checker must aggregate every shard output"
        )
        assert f'MUSIC_ANALYZER_EGMD_SHARD_COUNT="$({var_prefix}_SHARDS)"' in shard_recipe, (
            f"{label} shard target must pass the configured shard count"
        )
        assert 'MUSIC_ANALYZER_EGMD_SHARD_INDEX="$$shard"' in shard_recipe, (
            f"{label} shard target must pass its concrete shard index"
        )
        assert "MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT" in shard_recipe, (
            f"{label} shard target must preserve the per-window recall gate"
        )
        assert "MUSIC_ANALYZER_EGMD_SHARD_COUNT" not in serial_recipe, (
            f"{label} serial fallback must keep the original unsharded harness"
        )
    assert_alias_target(makefile, "test-medley-solos-samples", "test-medley-solos-samples-parallel")
    medley_parallel_recipe = target_recipe(makefile, "test-medley-solos-samples-parallel")
    medley_unlocked_recipe = target_recipe(makefile, "test-medley-solos-samples-parallel-unlocked")
    medley_shard_recipe = target_recipe(makefile, "test-medley-solos-samples-shard-%")
    medley_serial_recipe = target_recipe(makefile, "test-medley-solos-samples-serial")
    assert "scripts/check_instrument_family_shards.py" in medley_parallel_recipe, (
        "Medley-solos parallel target must depend on the instrument-family shard checker"
    )
    assert "scripts/run_with_lock.sh" in medley_parallel_recipe, (
        "Medley-solos parallel target must lock shared shard outputs"
    )
    assert "$(MAKE) $(MEDLEY_SOLOS_TEST_MAKE_JOBS) $(MEDLEY_SOLOS_SHARD_TARGETS)" in medley_unlocked_recipe, (
        "Medley-solos parallel target must fan out deterministic sample shards"
    )
    assert "$(MEDLEY_SOLOS_SHARD_OUTS)" in medley_unlocked_recipe, (
        "Medley-solos parallel checker must aggregate every shard output"
    )
    assert 'MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_COUNT="$(MEDLEY_SOLOS_SHARDS)"' in medley_shard_recipe, (
        "Medley-solos shard target must pass the configured shard count"
    )
    assert 'MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_INDEX="$$shard"' in medley_shard_recipe, (
        "Medley-solos shard target must pass its concrete shard index"
    )
    assert "MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_COUNT" not in medley_serial_recipe, (
        "Medley-solos serial fallback must keep the original unsharded harness"
    )
    for target, var_prefix, label in [
        ("test-maps-piano-samples", "MAPS_PIANO", "MAPS piano chord/music"),
        ("test-maps-piano-note-samples", "MAPS_PIANO_NOTE", "MAPS piano note"),
    ]:
        assert_alias_target(makefile, target, f"{target}-parallel")
        parallel_recipe = target_recipe(makefile, f"{target}-parallel")
        unlocked_recipe = target_recipe(makefile, f"{target}-parallel-unlocked")
        shard_recipe = target_recipe(makefile, f"{target}-shard-%")
        serial_recipe = target_recipe(makefile, f"{target}-serial")
        assert "scripts/check_maestro_shards.py" in parallel_recipe, (
            f"{label} parallel target must depend on the MAESTRO shard checker"
        )
        assert "scripts/run_with_lock.sh" in parallel_recipe, (
            f"{label} parallel target must lock shared shard outputs"
        )
        assert f"$(MAKE) $({var_prefix}_TEST_MAKE_JOBS) $({var_prefix}_SHARD_TARGETS)" in unlocked_recipe, (
            f"{label} parallel target must fan out deterministic recording shards"
        )
        assert f"$({var_prefix}_SHARD_OUTS)" in unlocked_recipe, (
            f"{label} parallel checker must aggregate every shard output"
        )
        assert f'MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$({var_prefix}_SHARDS)"' in shard_recipe, (
            f"{label} shard target must pass the configured shard count"
        )
        assert 'MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard"' in shard_recipe, (
            f"{label} shard target must pass its concrete shard index"
        )
        assert "MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT" in shard_recipe, (
            f"{label} shard target must preserve the pitch-class recall gate"
        )
        assert "MUSIC_ANALYZER_MAESTRO_SHARD_COUNT" not in serial_recipe, (
            f"{label} serial fallback must keep the original unsharded harness"
        )
    assert_alias_target(
        makefile,
        "test-bach10-mf0-synth-samples",
        "test-bach10-mf0-synth-samples-parallel",
    )
    bach_parallel_recipe = target_recipe(makefile, "test-bach10-mf0-synth-samples-parallel")
    bach_unlocked_recipe = target_recipe(makefile, "test-bach10-mf0-synth-samples-parallel-unlocked")
    bach_shard_recipe = target_recipe(makefile, "test-bach10-mf0-synth-samples-shard-%")
    bach_serial_recipe = target_recipe(makefile, "test-bach10-mf0-synth-samples-serial")
    assert "scripts/check_musicnet_shards.py" in bach_parallel_recipe, (
        "Bach10 parallel target must depend on the MusicNet shard checker"
    )
    assert "scripts/run_with_lock.sh" in bach_parallel_recipe, (
        "Bach10 parallel target must lock shared shard outputs"
    )
    assert "$(MAKE) $(BACH10_MF0_SYNTH_TEST_MAKE_JOBS) $(BACH10_MF0_SYNTH_SHARD_TARGETS)" in bach_unlocked_recipe, (
        "Bach10 parallel target must fan out deterministic recording shards"
    )
    assert "$(BACH10_MF0_SYNTH_SHARD_OUTS)" in bach_unlocked_recipe, (
        "Bach10 parallel checker must aggregate every shard output"
    )
    assert 'MUSIC_ANALYZER_MUSICNET_SHARD_COUNT="$(BACH10_MF0_SYNTH_SHARDS)"' in bach_shard_recipe, (
        "Bach10 shard target must pass the configured shard count"
    )
    assert 'MUSIC_ANALYZER_MUSICNET_SHARD_INDEX="$$shard"' in bach_shard_recipe, (
        "Bach10 shard target must pass its concrete shard index"
    )
    assert "MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT" in bach_shard_recipe, (
        "Bach10 shard target must preserve the per-window pitch recall gate"
    )
    assert "MUSIC_ANALYZER_MUSICNET_SHARD_COUNT" not in bach_serial_recipe, (
        "Bach10 serial fallback must keep the original unsharded harness"
    )
    bach_chord_miss_recipe = target_recipe(makefile, "analyze-bach10-mf0-synth-chord-misses")
    assert "$(RUN_WITH_DURATION) analyze_bach10_mf0_synth_chord_misses" in bach_chord_miss_recipe, (
        "Bach10 chord-miss diagnostics must report their duration"
    )
    assert "prepare-bach10-mf0-synth-samples" in bach_chord_miss_recipe, (
        "Bach10 chord-miss diagnostics must prepare the real synth fixture"
    )
    for text in [
        "MUSIC_ANALYZER_MUSICNET_VERBOSE_CHORD_MISSES=1",
        "MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0",
        "MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0",
        "MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1",
    ]:
        assert text in bach_chord_miss_recipe, f"Bach10 chord-miss diagnostics must include {text}"
    detector_improvement_recipe = target_recipe(makefile, "analyze-detector-improvements")
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvements_parallel" in detector_improvement_recipe, (
        "detector improvement workflow must report the aggregate parallel duration"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) detector-improvement-samples detector-improvement-patterns" in detector_improvement_recipe, (
        "detector improvement workflow must fan out sample gates and pattern reports together"
    )
    assert re.search(
        r"^detector-improvement-samples: test-detector-samples-parallel$",
        makefile,
        re.MULTILINE,
    ), "detector improvement samples helper must reuse the bounded parallel detector sample gate"
    assert re.search(
        r"^detector-improvement-patterns: measure-analyzer-patterns$",
        makefile,
        re.MULTILINE,
    ), "detector improvement pattern helper must generate measured attribute and pattern reports"
    assert re.search(
        r"^detector-improvement-patterns-cached: measure-analyzer-patterns-cached$",
        makefile,
        re.MULTILINE,
    ), "detector improvement cached pattern helper must reuse cached measured rows"
    assert re.search(
        r"^detector-improvement-patterns-cached-summary: "
        r"measure-analyzer-patterns-cached-summary$",
        makefile,
        re.MULTILINE,
    ), "detector improvement cached summary helper must reuse the cached candidate summary"
    route_scan_targets = re.search(
        r"^DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert route_scan_targets is not None, "missing detector improvement route-scan target list"
    assert "DETECTOR_IMPROVEMENT_ROUTE_REPORT ?= $(BUILD_DIR)/detector_improvement_route_scan.txt" in makefile, (
        "detector improvement route scan must have a stable file-backed report path"
    )
    assert "DETECTOR_IMPROVEMENT_ROUTE_SUMMARY ?= $(BUILD_DIR)/detector_improvement_route_summary.txt" in makefile, (
        "detector improvement route summary must have a stable file-backed report path"
    )
    assert "DETECTOR_IMPROVEMENT_AUDIT_REPORT ?= $(BUILD_DIR)/detector_improvement_audit.txt" in makefile, (
        "detector improvement audit must have a stable file-backed report path"
    )
    for variable in [
        "MEASURE_INSTRUMENT_PATTERN_ARGS",
        "MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS",
    ]:
        match = re.search(rf"^{variable} \?= (.+)$", makefile, re.MULTILINE)
        assert match is not None, f"missing {variable}"
        assert "--profile-fields" in match.group(1), (
            f"{variable} must include attribute-profile output for detector route reports"
        )
    route_scan_target_list = route_scan_targets.group(1)
    for target in [
        "find-real-note-focused-row-confusion-patterns",
        "find-real-note-coverage-row-confusion-patterns",
        "find-real-note-focused-visual-row-confusion-patterns",
        "find-real-note-coverage-visual-row-confusion-patterns",
        "find-real-note-ownership-patterns",
        "evaluate-real-note-display-shadow-all",
        "evaluate-real-note-vocal-shadow-safety",
        "find-vocadito-full-mix-ownership-patterns",
        "find-vocadito-full-mix-broad-vocal-ownership-patterns",
        "find-vocadito-full-mix-visual-row-confusion-patterns",
        "$(DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS)",
        "find-instrument-owner-patterns",
        "find-instrument-status-patterns",
        "find-drum-full-exact-attribute-patterns-cached",
    ]:
        assert target in route_scan_target_list, (
            f"detector improvement route scan must include {target}"
        )
    broad_vocal_recipe = target_recipe(makefile, "find-vocadito-full-mix-broad-vocal-ownership-patterns")
    assert '--bucket "ownership_miss:vocals/*->*"' in broad_vocal_recipe, (
        "broad vocal ownership route must mine the cross-source wildcard bucket"
    )
    assert '$(MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS)' in broad_vocal_recipe, (
        "broad vocal ownership route must use bounded route-report defaults"
    )
    assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in broad_vocal_recipe, (
        "broad vocal ownership route must run pattern search with configured parallel jobs"
    )
    for text in [
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS :=",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitar-chord-mix-route-patterns",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitar-techs-chord-route-patterns",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-egfxset-guitar-route-patterns",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-gaps-guitar-route-patterns",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-gaps-guitar-full-route-patterns",
        "DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitarset-route-patterns",
    ]:
        assert text in makefile, (
            f"detector route scans must optionally include guitar evidence target {text}"
        )
    for target, delegated in {
        "find-guitar-chord-mix-route-patterns": "find-guitar-chord-mix-attribute-patterns",
        "find-guitar-techs-chord-route-patterns": "find-guitar-techs-chord-attribute-patterns",
        "find-egfxset-guitar-route-patterns": "find-egfxset-guitar-attribute-patterns",
        "find-gaps-guitar-route-patterns": "find-gaps-guitar-attribute-patterns",
        "find-gaps-guitar-full-route-patterns": "find-gaps-guitar-full-attribute-patterns",
        "find-guitarset-route-patterns": "find-guitarset-attribute-patterns",
    }.items():
        recipe = target_recipe(makefile, target)
        assert f"$(MAKE) {delegated}" in recipe, (
            f"{target} must delegate to {delegated}"
        )
        assert 'PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"' in recipe, (
            f"{target} must use bounded route-report guitar pattern args"
        )
    assert "MEASURE_GUITAR_ROUTE_PATTERN_ARGS ?= $(MEASURE_GUITAR_PATTERN_ARGS) --runtime-only" in makefile, (
        "route guitar pattern mining must only emit runtime-observable candidate fields"
    )
    assert "VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv" in makefile, (
        "Vocadito route mining must protect candidate vocal rules against the broad NSynth full-mix TSV"
    )
    assert 'VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")' in makefile, (
        "Vocadito protected TSV inputs must be converted into repeatable pattern-miner arguments"
    )
    for target in [
        "find-vocadito-full-mix-row-confusion-patterns",
        "find-vocadito-full-mix-visual-row-confusion-patterns",
        "find-vocadito-full-mix-ownership-patterns",
        "find-vocadito-full-mix-broad-vocal-ownership-patterns",
    ]:
        vocadito_pattern_recipe = target_recipe(makefile, target)
        assert "$(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS)" in vocadito_pattern_recipe.splitlines()[0], (
            f"{target} must wait for protected real-note TSV inputs"
        )
        assert "$(VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS)" in vocadito_pattern_recipe, (
            f"{target} must pass protected real-note TSV inputs to the pattern miner"
        )
    route_scan_recipe = target_recipe(makefile, "analyze-detector-improvement-routes")
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvement_routes_parallel" in route_scan_recipe, (
        "detector improvement route scan must preserve the make jobserver through the duration wrapper"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS :=" in makefile, (
        "detector route scans must define optional candidate real-note rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available IDMT bass rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available IDMT guitar rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available GuitarTechs electric-guitar rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Good Sounds real-instrument rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(TINYSOL_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available TinySOL acoustic instrument rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Iowa piano rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Iowa strings rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Philharmonia rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Philharmonia full rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Iowa orchestra rows"
    )
    assert "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)" in makefile, (
        "detector route scans should mine candidates from available Iowa orchestra full rows"
    )
    assert "--show-examples 4 --protected-scope all" in continuation_variable_body(
        makefile, "MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS"
    ), (
        "coverage row-confusion scans should retain enough examples for sample-family grouping"
    )
    assert "--show-examples 4 --protected-scope all --include-row-context" in continuation_variable_body(
        makefile, "MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS"
    ), (
        "coverage visual-row scans should retain enough examples for sample-family grouping"
    )
    assert "--show-examples 4 --protected-scope all" in continuation_variable_body(
        makefile, "MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS"
    ), (
        "ownership scans should retain enough examples for sample-family grouping"
    )
    assert (
        "DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS ?= "
        "$(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS)"
    ) in makefile, (
        "detector route scans must pass optional IDMT rows as candidate evidence"
    )
    assert (
        "DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS ?= "
        "$(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS)"
    ) in makefile, (
        "detector route scans must keep protected vocal evidence behind an optional path set"
    )
    route_scan_submake = (
        '$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) '
        'REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS)" '
        'REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS)" '
        "$(DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS)"
    )
    assert route_scan_submake in route_scan_recipe, (
        "detector improvement route scan must fan out independent miners with protected vocal rows"
    )
    assert re.search(
        r"^detector-improvement-routes: analyze-detector-improvement-routes$",
        makefile,
        re.MULTILINE,
    ), "detector improvement route helper must delegate to the parallel route scan"
    route_report_recipe = target_recipe(makefile, "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)")
    assert re.search(
        r"^\$\(DETECTOR_IMPROVEMENT_ROUTE_REPORT\): Makefile src/analyzer\.cpp src/analyzer\.hpp "
        r"tests/analyzer_guitarset\.cpp tests/analyzer_real_note_samples\.cpp "
        r"tests/analyzer_instrument_samples\.cpp tests/analyzer_drum_samples\.cpp "
        r"scripts/run_with_duration\.sh "
        r"scripts/find_real_note_attribute_patterns\.py "
        r"scripts/find_guitarset_attribute_patterns\.py "
        r"scripts/inspect_guitarset_attribute_buckets\.py "
        r"scripts/evaluate_real_note_display_shadow\.py "
        r"scripts/evaluate_real_note_vocal_display_fallback\.py "
        r"scripts/find_instrument_owner_patterns\.py "
        r"scripts/find_drum_attribute_patterns\.py",
        makefile,
        re.MULTILINE,
    ), "detector improvement route report must cache output until detector or mining inputs change"
    assert 'tmp="$@.$$$$.tmp"' in route_report_recipe, (
        "detector improvement route report must write through a per-process temp file"
    )
    assert "$(RUN_WITH_DURATION) detector_improvement_routes_parallel" in route_report_recipe, (
        "detector improvement route report must capture the timed route scan"
    )
    assert route_scan_submake in route_report_recipe, (
        "detector improvement route report must capture the cross-protected route scan"
    )
    assert "> \"$$tmp\" 2>&1" in route_report_recipe, (
        "detector improvement route report must capture stdout and stderr into the report"
    )
    assert 'mv "$$tmp" "$@"' in route_report_recipe, (
        "detector improvement route report must publish atomically"
    )
    assert 'tail -n 1 "$@"' in route_report_recipe, (
        "detector improvement route report must echo the saved duration line"
    )
    route_report_alias = target_recipe(makefile, "detector-improvement-route-report")
    assert "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" in route_report_alias, (
        "detector improvement route report helper must depend on the file-backed report"
    )
    route_report_refresh_recipe = target_recipe(makefile, "detector-improvement-route-report-refresh")
    assert "$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" in route_report_refresh_recipe, (
        "detector improvement route report refresh helper must force the expensive miner run"
    )
    route_summary_recipe = target_recipe(makefile, "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)")
    assert re.search(
        r"^\$\(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY\): \$\(DETECTOR_IMPROVEMENT_ROUTE_REPORT\) "
        r"scripts/summarize_detector_route_report\.py \| \$\(BUILD_DIR\)",
        makefile,
        re.MULTILINE,
    ), "detector improvement route summary must derive from the saved route report"
    assert 'tmp="$@.$$$$.tmp"' in route_summary_recipe, (
        "detector improvement route summary must write through a per-process temp file"
    )
    assert 'scripts/summarize_detector_route_report.py "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)"' in route_summary_recipe, (
        "detector improvement route summary must run the summary parser against the saved route report"
    )
    assert 'mv "$$tmp" "$@"' in route_summary_recipe, (
        "detector improvement route summary must publish atomically"
    )
    assert 'cat "$@"' in route_summary_recipe, (
        "detector improvement route summary helper must print the compact report"
    )
    route_summary_alias = target_recipe(makefile, "detector-improvement-route-summary")
    assert "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" in route_summary_alias, (
        "detector improvement route summary helper must depend on the file-backed summary"
    )
    route_summary_refresh_recipe = target_recipe(makefile, "detector-improvement-route-summary-refresh")
    assert "$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" in route_summary_refresh_recipe, (
        "detector improvement route summary refresh helper must force a fresh route report and summary"
    )
    route_summary_cached_recipe = target_recipe(makefile, "detector-improvement-route-summary-cached")
    assert "run make detector-improvement-route-summary-refresh" in route_summary_cached_recipe, (
        "cached route summary helper must tell users how to refresh missing evidence"
    )
    assert 'cat "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"' in route_summary_cached_recipe, (
        "cached route summary helper must print the existing summary directly"
    )
    assert "$(MAKE)" not in route_summary_cached_recipe, (
        "cached route summary helper must not trigger Make prerequisites"
    )
    detector_improvement_full_recipe = target_recipe(makefile, "analyze-detector-improvements-full")
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvements_full_parallel" in detector_improvement_full_recipe, (
        "full detector improvement workflow must report the aggregate parallel duration"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) detector-improvement-samples-full detector-improvement-patterns-full" in detector_improvement_full_recipe, (
        "full detector improvement workflow must fan out full sample gates and full pattern reports together"
    )
    assert re.search(
        r"^detector-improvement-samples-full: test-detector-samples-full-parallel$",
        makefile,
        re.MULTILINE,
    ), "full detector improvement samples helper must reuse the full parallel detector sample gate"
    assert re.search(
        r"^detector-improvement-patterns-full: measure-analyzer-patterns-full$",
        makefile,
        re.MULTILINE,
    ), "full detector improvement pattern helper must generate exhaustive pattern reports"
    audit_targets = re.search(
        r"^DETECTOR_IMPROVEMENT_AUDIT_TARGETS \?= (.+)$", makefile, re.MULTILINE
    )
    assert audit_targets is not None, "missing detector improvement audit target list"
    audit_target_list = audit_targets.group(1)
    for target in [
        "detector-improvement-route-summary-refresh",
        "find-protected-drum-primary-attribute-patterns",
        "find-protected-drum-full-exact-attribute-patterns",
        "find-drum-active-false-patterns-full",
    ]:
        assert target in audit_target_list, (
            f"detector improvement audit must include {target}"
        )
    assert audit_target_list.count("find-drum-full-exact-attribute-patterns-cached") == 0, (
        "detector improvement audit must not duplicate the cached full-drum scan already included "
        "by the route summary"
    )
    audit_recipe = target_recipe(makefile, "detector-improvement-audit")
    assert "\n\t+$(RUN_WITH_DURATION) detector_improvement_audit_parallel" in audit_recipe, (
        "detector improvement audit must report aggregate duration"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_IMPROVEMENT_AUDIT_TARGETS)" in audit_recipe, (
        "detector improvement audit must fan out route and drum scans through parallel make"
    )
    audit_report_recipe = target_recipe(makefile, "$(DETECTOR_IMPROVEMENT_AUDIT_REPORT)")
    assert re.search(
        r"^\$\(DETECTOR_IMPROVEMENT_AUDIT_REPORT\): FORCE Makefile scripts/run_with_duration\.sh "
        r"scripts/summarize_detector_route_report\.py scripts/find_real_note_attribute_patterns\.py "
        r"scripts/evaluate_real_note_display_shadow\.py scripts/find_drum_attribute_patterns\.py "
        r"scripts/find_drum_active_false_patterns\.py",
        makefile,
        re.MULTILINE,
    ), "detector improvement audit report must refresh instead of serving stale miner output"
    assert 'tmp="$@.$$$$.tmp"' in audit_report_recipe, (
        "detector improvement audit report must write through a per-process temp file"
    )
    assert "$(RUN_WITH_DURATION) detector_improvement_audit_parallel" in audit_report_recipe, (
        "detector improvement audit report must capture the timed parallel audit"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_IMPROVEMENT_AUDIT_TARGETS)" in audit_report_recipe, (
        "detector improvement audit report must fan out the configured audit targets"
    )
    assert "> \"$$tmp\" 2>&1" in audit_report_recipe, (
        "detector improvement audit report must capture stdout and stderr into the report"
    )
    assert 'mv "$$tmp" "$@"' in audit_report_recipe, (
        "detector improvement audit report must publish atomically"
    )
    assert 'tail -n "$(DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES)" "$@"' in audit_report_recipe, (
        "detector improvement audit report must print the final decision context"
    )
    audit_report_alias = target_recipe(makefile, "detector-improvement-audit-report")
    assert "$(DETECTOR_IMPROVEMENT_AUDIT_REPORT)" in audit_report_alias, (
        "detector improvement audit report helper must depend on the file-backed report"
    )
    cached_audit_report_recipe = target_recipe(makefile, "detector-improvement-audit-report-cached")
    assert "run make detector-improvement-audit-report" in cached_audit_report_recipe, (
        "cached audit report helper must tell users how to generate missing evidence"
    )
    assert 'tail -n "$(DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES)" "$(DETECTOR_IMPROVEMENT_AUDIT_REPORT)"' in cached_audit_report_recipe, (
        "cached audit report helper must print the existing final decision context"
    )
    assert "$(MAKE)" not in cached_audit_report_recipe, (
        "cached audit report helper must not trigger the expensive audit refresh"
    )
    cached_audit_recipe = target_recipe(makefile, "detector-improvement-audit-cached")
    assert "detector-improvement-route-summary-cached detector-improvement-audit-report-cached" in cached_audit_recipe, (
        "cached audit helper must combine cached route and audit evidence"
    )
    cached_status_recipe = target_recipe(makefile, "detector-improvement-status-cached")
    assert "detector-improvement-coverage-cached detector-improvement-audit-cached" in cached_status_recipe, (
        "cached detector status helper must combine cached coverage and audit evidence"
    )
    assert "$(MAKE)" not in cached_status_recipe, (
        "cached detector status helper must not trigger an expensive refresh itself"
    )
    assert "DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES ?= 60" in makefile, (
        "audit tail length must remain overrideable for cached and refresh reports"
    )
    default_test_recipe = target_recipe(makefile, "test")
    assert "$(RUN_WITH_DURATION) test_fast" in default_test_recipe, (
        "default test target must report the fast parallel aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) test_fast" in default_test_recipe, (
        "default test target must preserve the make jobserver through the duration wrapper"
    )
    test_fast_targets = re.search(r"^TEST_FAST_TARGETS := (.+)$", makefile, re.MULTILINE)
    assert test_fast_targets is not None, "default test target must declare the fast target fanout list"
    test_fast_target_list = test_fast_targets.group(1)
    for target in [
        "test-parallel",
        "test-detector-samples-parallel",
        "test-fret-control",
        "test-real-goal-fixture",
        "test-fixtures-parallel-isolated",
    ]:
        assert target in test_fast_target_list, (
            f"default test target fanout list must include {target}"
        )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(TEST_BINS) $(TEST_FAST_TARGETS)" in default_test_recipe, (
        "default test target must fan out test binaries, independent test groups, and isolated fixtures together"
    )
    isolated_fixture_recipe = target_recipe(makefile, "test-fixtures-parallel-isolated")
    assert "$(RUN_WITH_DURATION) test_fixtures_parallel_isolated" in isolated_fixture_recipe, (
        "isolated fixture target must report aggregate duration"
    )
    assert 'REAL_GOAL_FIXTURE_DIR="$(REAL_GOAL_PARALLEL_FIXTURE_DIR)" test-fixtures-parallel' in isolated_fixture_recipe, (
        "isolated fixture target must run fixtures under a separate real-goal root"
    )
    assert re.search(r"^REAL_GOAL_MAKE_JOBS \?=", makefile, re.MULTILINE), (
        "real-goal coordinator must have a make parallelism handoff for no-jobserver invocations"
    )
    configured_real_world_recipe = target_recipe(makefile, "test-configured-real-world-samples")
    assert 'run_real_goal_gate.py optional-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)' in configured_real_world_recipe, (
        "configured real-world sample gate must pass explicit parallel make args into the Python coordinator"
    )
    real_goal_fixture_recipe = target_recipe(makefile, "test-real-goal-fixture")
    assert "prepare-real-goal-fixtures-parallel" in real_goal_fixture_recipe.splitlines()[0], (
        "real-goal fixture gate must build its generated fixtures through the parallel prep target"
    )
    assert 'run_real_goal_gate.py inspect-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)' in real_goal_fixture_recipe, (
        "real-goal fixture preflight must pass explicit parallel make args into the Python coordinator"
    )
    assert 'run_real_goal_gate.py 20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)' in real_goal_fixture_recipe, (
        "real-goal fixture analyzer gate must pass explicit parallel make args into the Python coordinator"
    )
    real_goal_fixture_prep_targets = continuation_variable_body(makefile, "REAL_GOAL_FIXTURE_PREP_TARGETS")
    for target in [
        "prepare-real-goal-urmp-fixture",
        "prepare-real-goal-musicnet-fixture",
        "prepare-real-goal-medleydb-fixture",
        "prepare-real-goal-musdb-fixture",
        "prepare-real-goal-slakh-fixture",
        "prepare-real-goal-choralsynth-fixture",
        "prepare-real-goal-cocochorales-fixture",
        "prepare-real-goal-synthsod-fixture",
        "prepare-real-goal-polyvocal-fixture",
        "prepare-real-goal-prepared-multitrack-fixture",
        "prepare-real-goal-multtipop-fixture",
        "prepare-real-goal-spheres-fixture",
        "prepare-real-goal-guitarset-fixture",
        "prepare-real-goal-maestro-fixture",
        "prepare-real-goal-egmd-fixture",
    ]:
        assert target in real_goal_fixture_prep_targets, (
            f"real-goal fixture prep fanout must include {target}"
        )
    real_goal_fixture_prep_recipe = target_recipe(makefile, "prepare-real-goal-fixtures-parallel")
    assert "$(RUN_WITH_DURATION) real_goal_fixture_generation_parallel" in real_goal_fixture_prep_recipe, (
        "real-goal fixture prep must report aggregate parallel generation duration"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_GOAL_FIXTURE_PREP_TARGETS)" in real_goal_fixture_prep_recipe, (
        "real-goal fixture prep must fan out dataset generators through jobserver-aware make"
    )
    assert "rm -rf $(REAL_GOAL_FIXTURE_DIR)" in real_goal_fixture_prep_recipe, (
        "real-goal fixture prep must still reset the shared generated fixture root once before fanout"
    )
    for wrapper in [
        "test-real-goal-20",
        "test-real-goal-full",
        "inspect-real-goal-20",
        "inspect-real-goal-full",
    ]:
        wrapper_recipe = target_recipe(makefile, wrapper)
        assert '"$(MAKE)" $(REAL_GOAL_MAKE_JOBS)' in wrapper_recipe, (
            f"{wrapper} must pass explicit parallel make args into the Python coordinator"
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
    real_world_target_names = real_world_target_list.split()
    for target in [
        "test-real-note-samples-parallel",
        "test-guitar-fretboard-note-samples-parallel",
        "test-downloaded-guitarset-parallel",
        "test-philharmonia-samples-parallel",
        "test-iowa-piano-samples-parallel",
        "test-iowa-bass-samples-parallel",
        "test-idmt-bass-lines-samples-parallel",
        "test-vocadito-samples-parallel",
    ]:
        assert target in real_world_target_names, (
            f"parallel real-world sample tests must call {target} directly"
        )
    for target in [
        "test-real-note-samples",
        "test-guitar-fretboard-note-samples",
        "test-downloaded-guitarset",
        "test-philharmonia-samples",
        "test-iowa-piano-samples",
        "test-iowa-bass-samples",
        "test-idmt-bass-lines-samples",
        "test-vocadito-samples",
    ]:
        assert target not in real_world_target_names, (
            f"parallel real-world sample tests must not route through {target}"
        )
    assert "test-real-note-samples-full-mix-parallel" in real_world_target_list, (
        "parallel real-world sample tests must use the sharded real-note full-mix gate"
    )
    assert "test-vocadito-samples-full-mix-parallel" in real_world_target_list, (
        "parallel real-world sample tests must include the real vocal full-mix gate"
    )
    assert "test-real-note-samples-full-mix " not in real_world_target_list + " ", (
        "parallel real-world sample tests must not use the serial real-note full-mix gate"
    )
    assert_alias_target(
        makefile, "test-real-note-samples-full-mix", "test-real-note-samples-full-mix-parallel"
    )
    real_note_serial_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-serial")
    assert "$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix" in real_note_serial_recipe, (
        "real-note full-mix serial target must preserve the single-process analyzer harness"
    )
    assert "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT" not in real_note_serial_recipe, (
        "real-note full-mix serial target must not set shard variables"
    )
    real_note_sharded_recipe = target_recipe(makefile, "test-real-note-samples-full-mix-parallel")
    assert "REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))" in makefile, (
        "real-note shard tests must not force nested jobserver mode"
    )
    assert "REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX ?= real_note_full_mix_shard" in makefile, (
        "real-note full-mix shards must have a configurable output prefix for nested parallel runs"
    )
    assert "REAL_NOTE_FULL_MIX_LOCK_DIR ?= $(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX).lock" in makefile, (
        "real-note full-mix shards must lock by output prefix for concurrent top-level runs"
    )
    assert "REAL_NOTE_FULL_MIX_SHARD_OUTS = $(addprefix $(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_,$(addsuffix .out,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))" in makefile, (
        "real-note full-mix aggregate checker must consume deterministic shard outputs"
    )
    for text in [
        "REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT ?= 30",
        "REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT ?= 43",
        "REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT ?= 15",
        "REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT ?= 38",
        "REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT ?= 15",
        "REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT ?= 30",
    ]:
        assert text in makefile, f"real-note aggregate gate must include {text}"
    assert "scripts/run_with_lock.sh \"$(REAL_NOTE_FULL_MIX_LOCK_DIR)\"" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must lock shared shard outputs"
    )
    assert "\"$(MAKE)\" REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX=\"$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)\" test-real-note-samples-full-mix-parallel-unlocked" in real_note_sharded_recipe, (
        "real-note full-mix parallel target must delegate locked work to an internal target"
    )
    real_note_sharded_unlocked_recipe = target_recipe(
        makefile, "test-real-note-samples-full-mix-parallel-unlocked"
    )
    assert "$(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX=\"$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)\" $(REAL_NOTE_FULL_MIX_SHARD_TARGETS)" in real_note_sharded_unlocked_recipe, (
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
    assert "$(PYTHON) scripts/check_real_note_full_mix_shards.py" in real_note_sharded_unlocked_recipe, (
        "real-note full-mix parallel target must validate aggregated shard ownership metrics"
    )
    for text in [
        "--min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT)\"",
        "--min-visual-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT)\"",
        "--guitar-min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT)\"",
        "--other-min-first-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT)\"",
        "--guitar-min-visual-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT)\"",
        "--other-min-visual-row-percent \"$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT)\"",
        "$(REAL_NOTE_FULL_MIX_SHARD_OUTS)",
    ]:
        assert text in real_note_sharded_unlocked_recipe, (
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
        "> \"$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.out\"",
        "2> \"$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.err\"",
    ]:
        assert text in real_note_shard_recipe, f"real-note shard target must write {text}"
    vocadito_full_mix_recipe = target_recipe(makefile, "test-vocadito-samples-full-mix-parallel")
    assert "VOCADITO_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(VOCADITO_FULL_MIX_SHARDS))" in makefile, (
        "Vocadito full-mix shards must not force nested jobserver mode"
    )
    assert "VOCADITO_FULL_MIX_LOCK_DIR ?= $(BUILD_DIR)/vocadito_full_mix_shard.lock" in makefile, (
        "Vocadito full-mix shards must have a stable lock path"
    )
    assert "scripts/run_with_lock.sh \"$(VOCADITO_FULL_MIX_LOCK_DIR)\"" in vocadito_full_mix_recipe, (
        "Vocadito full-mix target must lock shared shard outputs"
    )
    assert "\"$(MAKE)\" test-vocadito-samples-full-mix-parallel-unlocked" in vocadito_full_mix_recipe, (
        "Vocadito full-mix target must delegate locked work to an internal target"
    )
    vocadito_full_mix_unlocked_recipe = target_recipe(
        makefile, "test-vocadito-samples-full-mix-parallel-unlocked"
    )
    assert "$(MAKE) $(VOCADITO_FULL_MIX_TEST_MAKE_JOBS) $(VOCADITO_FULL_MIX_SHARD_TARGETS)" in vocadito_full_mix_unlocked_recipe, (
        "Vocadito full-mix target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_vocadito_samples_full_mix_parallel" in vocadito_full_mix_recipe, (
        "Vocadito full-mix target must report aggregate duration"
    )
    for text in [
        "--min-any-hit-percent \"$(VOCADITO_FULL_MIX_MIN_ANY_HIT_PERCENT)\"",
        "--vocals-min-expected-row-percent \"$(VOCADITO_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)\"",
        "--vocals-min-first-row-percent \"$(VOCADITO_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT)\"",
        "--min-visual-row-percent \"$(VOCADITO_FULL_MIX_MIN_VISUAL_ROW_PERCENT)\"",
        "--vocals-min-visual-row-percent \"$(VOCADITO_FULL_MIX_MIN_VOCALS_VISUAL_ROW_PERCENT)\"",
        "--max-drum-active-percent \"$(VOCADITO_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)\"",
        "$(VOCADITO_FULL_MIX_SHARD_OUTS)",
    ]:
        assert text in vocadito_full_mix_unlocked_recipe, (
            f"Vocadito full-mix aggregate checker recipe must include {text}"
        )
    vocadito_full_mix_shard_recipe = target_recipe(makefile, "test-vocadito-samples-full-mix-shard-%")
    for text in [
        "MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1",
        "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(VOCADITO_SAMPLE_DIR)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(VOCADITO_FULL_MIX_SHARDS)\"",
        "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
        "> \"$(BUILD_DIR)/vocadito_full_mix_shard_$*.out\"",
    ]:
        assert text in vocadito_full_mix_shard_recipe, (
            f"Vocadito full-mix shard target must include {text}"
        )
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
    isolated_sample_unlocked_recipe = target_recipe(makefile, "test-real-note-sample-shards-unlocked")
    assert "REAL_NOTE_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_SAMPLE_SHARDS))" in makefile, (
        "isolated real-note shard tests must not force nested jobserver mode"
    )
    assert "REAL_NOTE_SAMPLE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_,$(addsuffix .out,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))" in makefile, (
        "isolated real-note aggregate checker must consume deterministic shard outputs"
    )
    assert "REAL_NOTE_SAMPLE_LOCK_DIR ?= $(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG).lock" in makefile, (
        "isolated real-note shard tests must lock per sample tag"
    )
    assert "scripts/run_with_lock.sh" in isolated_sample_sharded_recipe, (
        "isolated real-note shard wrapper must lock the shard outputs before aggregation"
    )
    assert 'scripts/run_with_lock.sh "$(REAL_NOTE_SAMPLE_LOCK_DIR)" -- $(RUN_REAL_NOTE_SAMPLE_SHARDS_UNLOCKED)' in isolated_sample_sharded_recipe, (
        "isolated real-note shard wrapper must run the unlocked shard target under the tag lock"
    )
    assert "$(MAKE) $(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS) $(REAL_NOTE_SAMPLE_SHARD_TARGETS)" in isolated_sample_unlocked_recipe, (
        "isolated real-note parallel target must fan out deterministic shards through jobserver-aware make"
    )
    assert "$(PYTHON) scripts/check_real_note_sample_shards.py" in isolated_sample_unlocked_recipe, (
        "isolated real-note parallel target must validate aggregated shard sample metrics"
    )
    assert "$(REAL_NOTE_SAMPLE_HIT_PERCENT_ARGS)" in isolated_sample_unlocked_recipe, (
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
        parallel_target = f"{target}-parallel"
        assert_alias_target(makefile, target, parallel_target)
        assert f"{target} {parallel_target}: REAL_NOTE_SAMPLE_TAG := {tag}" in makefile, (
            f"{target} and {parallel_target} must configure the same deterministic isolated real-note shard tag"
        )
        recipe_text = target_recipe(makefile, parallel_target)
        assert "$(RUN_REAL_NOTE_SAMPLE_SHARDS)" in recipe_text, (
            f"{parallel_target} must delegate to the isolated real-note shard runner"
        )
        assert "\n\t+$(RUN_REAL_NOTE_SAMPLE_SHARDS)" in recipe_text, (
            f"{parallel_target} must preserve the make jobserver through the isolated real-note shard runner"
        )
    iowa_strings_recipe = target_recipe(makefile, "prepare-iowa-strings-samples")
    for text in [
        "IOWA_STRINGS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_orchestra",
        "IOWA_STRINGS_SAMPLE_LIMIT ?= 80",
        "IOWA_STRINGS_MIN_SAMPLES ?= 60",
        "IOWA_STRINGS_MIN_OTHER ?= 60",
        "IOWA_STRINGS_MAX_FAILURES ?= 8",
        "IOWA_STRINGS_SPEC_ARGS =",
        "IOWA_STRINGS_VIOLIN_ARCO_SULG_URL",
        "IOWA_STRINGS_VIOLA_ARCO_SULC_URL",
        "IOWA_STRINGS_CELLO_ARCO_SULC_URL",
    ]:
        assert text in makefile, f"Iowa strings coverage must keep {text}"
    assert "$(IOWA_STRINGS_SPEC_ARGS)" in iowa_strings_recipe, (
        "Iowa strings preparation must use the multi-source spec list"
    )
    for family in ["BASS", "GUITAR", "PIANO", "VOCALS", "OTHER"]:
        assert f"REAL_NOTE_MIN_{family}_HIT_PERCENT ?= 100" in makefile, (
            f"NSynth isolated target must default to strict {family.lower()} recall"
        )
        assert (
            f"test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_{family}_HIT_PERCENT := "
            f"$(REAL_NOTE_MIN_{family}_HIT_PERCENT)"
        ) in makefile, (
            f"NSynth isolated target must pass through strict {family.lower()} recall"
        )
    assert_alias_target(makefile, "test-instrument-samples", "test-instrument-samples-parallel")
    instrument_serial_recipe = target_recipe(makefile, "test-instrument-samples-serial")
    assert "$(RUN_WITH_DURATION) analyzer_instrument_samples env" in instrument_serial_recipe, (
        "generated instrument serial target must preserve the single-process analyzer harness"
    )
    assert "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT" not in instrument_serial_recipe, (
        "generated instrument serial target must not set shard variables"
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
    detector_regression_target_names = detector_regression_target_list.split()
    assert "test-real-note-samples-full-mix-detector-parallel" in detector_regression_target_names, (
        "detector sample regression loop must use the isolated sharded real-note full-mix gate"
    )
    assert "test-real-note-visual-strength" in detector_regression_target_list, (
        "detector sample regression loop must guard visible real-note highlight strength"
    )
    assert "test-real-note-samples-full-mix-parallel" not in detector_regression_target_list, (
        "detector sample regression loop must not race the public real-note full-mix shard outputs"
    )
    assert re.search(
        r"^test-real-note-samples-full-mix-detector-parallel: REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX := detector_real_note_full_mix_shard$",
        makefile,
        re.MULTILINE,
    ), "detector real-note full-mix wrapper must isolate shard output names"
    assert re.search(
        r"^test-real-note-samples-full-mix-detector-parallel: test-real-note-samples-full-mix-parallel$",
        makefile,
        re.MULTILINE,
    ), "detector real-note full-mix wrapper must delegate to the same sharded gate"
    visual_strength_recipe = target_recipe(makefile, "test-real-note-visual-strength")
    assert "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" in visual_strength_recipe.splitlines()[0], (
        "real-note visual strength gate must reuse the sharded attribute TSV"
    )
    assert "$(RUN_WITH_DURATION) real_note_visual_strength" in visual_strength_recipe, (
        "real-note visual strength gate must report duration"
    )
    assert "scripts/summarize_real_note_attributes.py" in visual_strength_recipe, (
        "real-note visual strength gate must use the attribute summarizer validation path"
    )
    assert "$(REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_ARGS)" in visual_strength_recipe, (
        "real-note visual strength gate must use the configured visible-lit thresholds"
    )
    assert "--min-visible-lit-exact-sample-percent" in makefile, (
        "real-note visible strength thresholds must check overall bright exact-note coverage"
    )
    assert "--min-visible-lit-exact-family-sample-percent" in makefile, (
        "real-note visible strength thresholds must check per-family bright exact-note coverage"
    )
    assert "test-vocadito-samples-full-mix-parallel" in detector_regression_target_names, (
        "detector sample regression loop must include real vocal full-mix ownership coverage"
    )
    assert "test-real-note-samples-full-mix " not in detector_regression_target_list + " ", (
        "detector sample regression loop must not use the serial real-note full-mix gate"
    )
    assert "test-analyzer-cases" in detector_regression_target_list, (
        "detector sample regression loop must include synthetic temporal/chord/analyzer cases"
    )
    assert re.search(
        r"^test-bpm-regression: test-analyzer-cases test-egmd-fixture$",
        makefile,
        re.MULTILINE,
    ), "BPM regression target must cover synthetic tempo cases and generated E-GMD tempo fixtures"
    for target in [
        "test-real-note-samples-parallel",
        "test-guitar-fretboard-note-samples-parallel",
        "test-guitar-techs-samples-parallel",
        "test-guitar-techs-chord-samples-parallel",
        "test-guitar-chord-mix-samples-parallel",
        "test-egfxset-guitar-samples-parallel",
        "test-gaps-guitar-samples-parallel",
        "test-downloaded-guitarset-parallel",
        "test-philharmonia-samples-parallel",
        "test-philharmonia-samples-full-parallel",
        "test-iowa-piano-samples-parallel",
        "test-iowa-bass-samples-parallel",
        "test-iowa-strings-samples-parallel",
        "test-iowa-orchestra-samples-parallel",
        "test-tinysol-samples-parallel",
        "test-vocadito-samples-parallel",
    ]:
        assert target in detector_regression_target_names, (
            f"detector sample regression loop must call {target} directly"
        )
    for target in [
        "test-real-note-samples",
        "test-guitar-fretboard-note-samples",
        "test-guitar-techs-samples",
        "test-guitar-techs-chord-samples",
        "test-guitar-chord-mix-samples",
        "test-egfxset-guitar-samples",
        "test-gaps-guitar-samples",
        "test-downloaded-guitarset",
        "test-philharmonia-samples",
        "test-philharmonia-samples-full",
        "test-iowa-piano-samples",
        "test-iowa-bass-samples",
        "test-iowa-strings-samples",
        "test-iowa-orchestra-samples",
        "test-tinysol-samples",
        "test-vocadito-samples",
    ]:
        assert target not in detector_regression_target_names, (
            f"detector sample regression loop must not route through {target}"
        )
    assert "test-guitar-chord-mix-samples-parallel" in detector_regression_target_names, (
        "detector sample regression loop must include the real guitar chord mix gate"
    )
    assert "$(DRUM_REAL_WORLD_SAMPLE_TARGETS)" in detector_regression_target_list, (
        "detector sample regression loop must include real-world drum sample gates"
    )
    assert "test-drum-machine-samples-optional" in detector_regression_target_list, (
        "detector sample regression loop must include local drum-machine kit coverage"
    )
    assert "test-idmt-bass-lines-samples-optional" in detector_regression_target_list, (
        "detector sample regression loop must include optional real electric bass-line coverage"
    )
    assert "test-idmt-guitar-samples-optional" in detector_regression_target_list, (
        "detector sample regression loop must include optional real guitar note coverage"
    )
    assert "test-drum-samples-full-parallel-optional" in detector_regression_target_list, (
        "detector sample regression loop must include the optional local full-drum gate in the jobserver fanout"
    )
    assert "test-vocadito-samples-parallel" in detector_regression_target_names, (
        "detector sample regression loop must include the real vocal note gate"
    )
    assert "test-instrument-samples-parallel" in detector_regression_target_names, (
        "detector sample regression loop must use the sharded generated instrument sample gate"
    )
    assert "test-instrument-samples " not in detector_regression_target_list + " ", (
        "detector sample regression loop must not use the serial generated instrument sample gate"
    )
    assert re.search(
        r"^test-idmt-bass-lines-samples-optional: test-idmt-bass-lines-samples-parallel$",
        makefile,
        re.MULTILINE,
    ), "optional IDMT bass-line wrapper must run the real sample gate when the archive exists"
    assert re.search(
        r"^test-idmt-guitar-samples-optional: test-idmt-guitar-samples-parallel$",
        makefile,
        re.MULTILINE,
    ), "optional IDMT guitar wrapper must run the real sample gate when the archive exists"
    for optional_target, parallel_target in {
        "test-drum-samples-optional": "test-drum-samples-parallel",
        "test-drum-samples-spread-optional": "test-drum-samples-spread-parallel",
        "test-drum-machine-samples-optional": "test-drum-machine-samples-parallel",
        "test-good-sounds-samples-optional": "test-good-sounds-samples-parallel",
        "test-medley-solos-samples-optional": "test-medley-solos-samples-parallel",
        "test-maps-piano-samples-optional": "test-maps-piano-samples-parallel",
        "test-maps-piano-note-samples-optional": "test-maps-piano-note-samples-parallel",
        "test-bach10-mf0-synth-samples-optional": "test-bach10-mf0-synth-samples-parallel",
        "test-vocalset-samples-optional": "test-vocalset-samples-parallel",
    }.items():
        assert re.search(
            rf"^{re.escape(optional_target)}: {re.escape(parallel_target)}$",
            makefile,
            re.MULTILINE,
        ), f"{optional_target} must use {parallel_target} when its data is present"
    assert 'test-idmt-bass-lines-samples: skipped; missing $(IDMT_BASS_LINES_ARCHIVE)' in target_recipe(
        makefile, "test-idmt-bass-lines-samples-optional"
    ), "optional IDMT bass-line wrapper must skip cleanly when the archive is missing"
    assert 'test-idmt-guitar-samples: skipped; missing $(IDMT_GUITAR_ARCHIVE)' in target_recipe(
        makefile, "test-idmt-guitar-samples-optional"
    ), "optional IDMT guitar wrapper must skip cleanly when the archive is missing"
    drum_machine_manifest_recipe = target_recipe(makefile, "$(DRUM_MACHINE_SAMPLE_BUILD_DIR)/manifest.tsv")
    assert "FORCE" in drum_machine_manifest_recipe.splitlines()[0], (
        "drum-machine sample manifest target must rerun the metadata-aware preparer"
    )
    assert "$(MAKE) prepare-drum-machine-samples" in drum_machine_manifest_recipe, (
        "drum-machine sample manifest target must delegate to the drum-machine prepare target"
    )
    for target, prepare_target in {
        "$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv": "prepare-idmt-bass-lines-samples",
        "$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv": "prepare-idmt-guitar-samples",
    }.items():
        manifest_recipe = target_recipe(makefile, target)
        assert f"$(MAKE) {prepare_target}" in manifest_recipe, (
            f"{target} must refresh through {prepare_target}"
        )
        assert f'@touch "{target.removesuffix("/manifest.tsv")}/manifest.tsv"' in manifest_recipe, (
            f"{target} must update its timestamp after an idempotent prepare"
        )
    detector_regression_recipe = target_recipe(makefile, "test-detector-samples-parallel")
    assert "\n\t+$(RUN_WITH_DURATION) detector_samples_parallel" in detector_regression_recipe, (
        "detector sample regression target must preserve the make jobserver through the parallel duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_REGRESSION_TARGETS)" in detector_regression_recipe, (
        "detector sample regression target must fan out core gates through jobserver-aware make"
    )
    assert "detector_samples_serial" not in detector_regression_recipe, (
        "detector sample regression target must keep detector gates in one jobserver-aware fanout"
    )
    assert re.search(
        r"^test-detector-samples: test-detector-samples-parallel$", makefile, re.MULTILINE
    ), "default detector sample gate must delegate to the parallel target"
    detector_regression_full_recipe = target_recipe(makefile, "test-detector-samples-full-parallel")
    assert "\n\t+$(RUN_WITH_DURATION) detector_samples_full_parallel" in detector_regression_full_recipe, (
        "full detector sample regression target must preserve the make jobserver through the parallel duration wrapper"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_FULL_REGRESSION_TARGETS)" in detector_regression_full_recipe, (
        "full detector sample regression target must fan out core gates through jobserver-aware make"
    )
    assert re.search(
        r"^test-detector-samples-full: test-detector-samples-full-parallel$", makefile, re.MULTILINE
    ), "default full detector sample gate must delegate to the parallel target"
    real_world_full_targets = re.search(
        r"^REAL_WORLD_SAMPLE_FULL_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert real_world_full_targets is not None, "missing full real-world sample target list"
    real_world_full_target_list = real_world_full_targets.group(1)
    real_world_full_target_names = real_world_full_target_list.split()
    for target in [
        "test-guitar-techs-samples-parallel",
        "test-guitar-techs-chord-samples-parallel",
        "test-guitar-chord-mix-samples-parallel",
        "test-egfxset-guitar-samples-parallel",
        "test-gaps-guitar-samples-parallel",
        "test-idmt-guitar-samples-parallel",
        "test-iowa-strings-samples-parallel",
        "test-iowa-orchestra-samples-parallel",
        "test-iowa-orchestra-full-samples-parallel",
        "test-philharmonia-samples-full-parallel",
        "test-tinysol-samples-parallel",
    ]:
        assert target in real_world_full_target_names, (
            f"full real-world sample tests must call {target} directly"
        )
    for target in [
        "test-guitar-techs-samples",
        "test-guitar-techs-chord-samples",
        "test-guitar-chord-mix-samples",
        "test-egfxset-guitar-samples",
        "test-gaps-guitar-samples",
        "test-idmt-guitar-samples",
        "test-iowa-strings-samples",
        "test-iowa-orchestra-samples",
        "test-iowa-orchestra-full-samples",
        "test-philharmonia-samples-full",
        "test-tinysol-samples",
    ]:
        assert target not in real_world_full_target_names, (
            f"full real-world sample tests must not route through {target}"
        )
    assert "test-guitar-chord-mix-samples-parallel" in real_world_full_target_names, (
        "full real-world sample tests must use the sharded guitar chord mix gate"
    )
    assert "test-drum-samples-full-parallel-optional" in real_world_full_target_names, (
        "full real-world sample tests must use the sharded full-drum sample gate"
    )
    assert "test-drum-samples-full-optional" not in real_world_full_target_names, (
        "full real-world sample tests must not use the serial full-drum sample gate"
    )
    drum_real_world_full_targets = re.search(
        r"^DRUM_REAL_WORLD_SAMPLE_FULL_TARGETS := (.+)$", makefile, re.MULTILINE
    )
    assert drum_real_world_full_targets is not None, "missing full drum real-world sample target list"
    drum_real_world_full_target_list = drum_real_world_full_targets.group(1)
    drum_real_world_full_target_names = drum_real_world_full_target_list.split()
    assert "test-drum-samples-full-parallel-optional" in drum_real_world_full_target_names, (
        "full drum real-world sample tests must use the sharded full-drum sample gate"
    )
    assert "test-drum-samples-full-optional" not in drum_real_world_full_target_names, (
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
    assert "FORCE" in drum_full_manifest_recipe.splitlines()[0], (
        "full drum sample manifest target must rerun the metadata-aware preparer"
    )
    assert "$(MAKE) prepare-drum-samples-full" in drum_full_manifest_recipe, (
        "full drum sample manifest target must delegate to the full prepare target"
    )
    assert_alias_target(makefile, "test-drum-samples-full", "test-drum-samples-full-parallel")
    drum_full_serial_recipe = target_recipe(makefile, "test-drum-samples-full-serial")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full env" in drum_full_serial_recipe, (
        "full drum serial target must preserve the single-process analyzer harness"
    )
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY" not in drum_full_serial_recipe, (
        "full drum serial target must not set per-category shard filters"
    )
    drum_full_parallel_recipe = target_recipe(makefile, "test-drum-samples-full-parallel")
    assert "DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY ?= 4" in makefile, (
        "full drum category shards must be chunked by a configurable per-category shard count"
    )
    assert "DRUM_SAMPLE_FULL_SHARD_IDS := $(foreach category,$(DRUM_SAMPLE_FULL_SHARD_CATEGORIES),$(addprefix $(category)-,$(DRUM_SAMPLE_FULL_SHARD_INDEXES)))" in makefile, (
        "full drum shards must combine category and chunk index deterministically"
    )
    assert "DRUM_SAMPLE_FULL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_SAMPLE_FULL_SHARD_IDS)))" in makefile, (
        "full drum shard tests must not force nested jobserver mode"
    )
    assert "DRUM_SAMPLE_FULL_LOCK_DIR ?= $(BUILD_DIR)/drum_samples_full.lock" in makefile, (
        "full drum shard aggregation must have a stable lock path"
    )
    assert "$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv" in drum_full_parallel_recipe.splitlines()[0], (
        "full drum parallel target must share a prepared manifest stamp"
    )
    assert "scripts/run_with_lock.sh \"$(DRUM_SAMPLE_FULL_LOCK_DIR)\"" in drum_full_parallel_recipe, (
        "full drum parallel target must lock shared shard outputs"
    )
    assert "\"$(MAKE)\" test-drum-samples-full-parallel-unlocked" in drum_full_parallel_recipe, (
        "full drum parallel target must delegate the locked work to an internal target"
    )
    drum_full_parallel_unlocked_recipe = target_recipe(makefile, "test-drum-samples-full-parallel-unlocked")
    assert "$(MAKE) $(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS) $(DRUM_SAMPLE_FULL_SHARD_TARGETS)" in drum_full_parallel_unlocked_recipe, (
        "full drum parallel target must fan out category shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full_parallel" in drum_full_parallel_recipe, (
        "full drum parallel target must report aggregate duration"
    )
    assert "\n\t+$(RUN_WITH_DURATION) analyzer_drum_samples_full_parallel" in drum_full_parallel_recipe, (
        "full drum parallel target must preserve the make jobserver through the duration wrapper"
    )
    assert "$(PYTHON) scripts/check_drum_sample_shards.py" in drum_full_parallel_unlocked_recipe, (
        "full drum parallel target must validate aggregated shard matrices"
    )
    assert "--tom-max-false-percent \"$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)\"" in drum_full_parallel_unlocked_recipe, (
        "full drum parallel target must preserve the serial tom false-positive gate"
    )
    assert "DRUM_FULL_EXACT_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_full_exact_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_FULL_SHARD_IDS)))" in makefile, (
        "full drum exact attribute rows must have deterministic category-chunk shard parts"
    )
    assert "DRUM_FULL_EXACT_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_full_exact_attribute_rows.lock" in makefile, (
        "full drum exact attribute rows must have a stable lock path"
    )
    assert "DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/drum_full_merged_expected_attribute_rows.tsv" in makefile, (
        "full drum merged expected rows must have a stable aggregate TSV path"
    )
    assert "DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_full_merged_expected_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_FULL_SHARD_IDS)))" in makefile, (
        "full drum merged expected rows must have deterministic category-chunk shard parts"
    )
    assert "DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_full_merged_expected_attribute_rows.lock" in makefile, (
        "full drum merged expected rows must have a stable lock path"
    )
    drum_full_attribute_parallel_recipe = target_recipe(makefile, "analyze-drum-full-gate-matrix-parallel")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full_attribute_rows_parallel" in drum_full_attribute_parallel_recipe, (
        "full drum exact attribute rows must report aggregate parallel duration"
    )
    assert "scripts/build_sharded_tsv.sh \"$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)\" \"$(MAKE)\" \"$(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS)\" $(DRUM_FULL_EXACT_ATTRIBUTE_PARTS)" in drum_full_attribute_parallel_recipe, (
        "full drum exact attribute rows must be built by the sharded TSV combiner"
    )
    assert "scripts/run_with_lock.sh \"$(DRUM_FULL_EXACT_ATTRIBUTE_LOCK_DIR)\"" in drum_full_attribute_parallel_recipe, (
        "full drum exact attribute rows must lock shared output files"
    )
    assert "$(PYTHON) scripts/summarize_drum_gate_matrix.py \"$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)\" > \"$(DRUM_FULL_GATE_SUMMARY)\"" in drum_full_attribute_parallel_recipe, (
        "full drum exact parallel target must refresh the gate matrix summary from the TSV"
    )
    assert "@cat \"$(DRUM_FULL_GATE_SUMMARY)\"" in drum_full_attribute_parallel_recipe, (
        "full drum exact parallel target must print the refreshed matrix summary"
    )
    drum_full_attribute_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_full_exact_attribute_rows_%.tsv")
    assert "FORCE" in drum_full_attribute_shard_recipe.splitlines()[0], (
        "full drum exact attribute shard target must use FORCE so each category executes"
    )
    for text in [
        "stem=\"$*\"",
        "category=\"$${stem%-*}\"",
        "shard=\"$${stem##*-}\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT=\"$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX=\"$$shard\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1",
        "$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows",
    ]:
        assert text in drum_full_attribute_shard_recipe, (
            f"full drum exact attribute shard target must include {text}"
        )
    drum_full_merged_parallel_recipe = target_recipe(makefile, "analyze-drum-full-merged-expected-attribute-rows")
    assert "$(RUN_WITH_DURATION) analyzer_drum_samples_full_merged_expected_rows_parallel" in drum_full_merged_parallel_recipe, (
        "full drum merged expected rows must report aggregate parallel duration"
    )
    assert "scripts/build_sharded_tsv.sh \"$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)\" \"$(MAKE)\" \"$(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS)\" $(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_PARTS)" in drum_full_merged_parallel_recipe, (
        "full drum merged expected rows must be built by the sharded TSV combiner"
    )
    assert "scripts/run_with_lock.sh \"$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_LOCK_DIR)\"" in drum_full_merged_parallel_recipe, (
        "full drum merged expected rows must lock shared output files"
    )
    drum_full_merged_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/drum_full_merged_expected_attribute_rows_%.tsv"
    )
    assert "FORCE" in drum_full_merged_shard_recipe.splitlines()[0], (
        "full drum merged expected shard target must use FORCE so each category executes"
    )
    for text in [
        "stem=\"$*\"",
        "category=\"$${stem%-*}\"",
        "shard=\"$${stem##*-}\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT=\"$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX=\"$$shard\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_MERGED_EXPECTED=1",
        "$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows --include-merged-debug-rows",
    ]:
        assert text in drum_full_merged_shard_recipe, (
            f"full drum merged expected shard target must include {text}"
        )
    full_exact_pattern_recipe = target_recipe(makefile, "find-drum-full-exact-attribute-patterns")
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in full_exact_pattern_recipe, (
        "stale full drum pattern rows must refresh through the parallel attribute builder"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix;" not in full_exact_pattern_recipe, (
        "stale full drum pattern rows must not use the serial full analyzer path"
    )
    protected_full_exact_recipe = target_recipe(
        makefile, "find-protected-drum-full-exact-attribute-patterns"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in protected_full_exact_recipe, (
        "protected full drum mining must refresh required full exact rows through the sharded builder"
    )
    assert "$(MAKE) analyze-protected-drum-primary-attribute-rows" in protected_full_exact_recipe, (
        "protected full drum mining must refresh spread, HF, and IDMT guard rows when stale"
    )
    assert "$(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS)" in protected_full_exact_recipe, (
        "protected full drum mining must mine full rows with spread, HF, and IDMT guard rows"
    )
    assert "$(or $(PATTERN_ARGS),$(MEASURE_DRUM_FULL_PATTERN_ARGS))" in protected_full_exact_recipe, (
        "protected full drum mining must use exhaustive full-drum pattern defaults"
    )
    drum_full_shard_recipe = target_recipe(makefile, "test-drum-samples-full-shard-%")
    assert "FORCE" in drum_full_shard_recipe.splitlines()[0], (
        "full drum shard pattern must use FORCE so each category executes"
    )
    assert "$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv" in drum_full_shard_recipe.splitlines()[0], (
        "full drum shard target must depend on the shared manifest stamp"
    )
    for text in [
        "stem=\"$*\"",
        "category=\"$${stem%-*}\"",
        "shard=\"$${stem##*-}\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$$category\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT=\"$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX=\"$$shard\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0",
    ]:
        assert text in drum_full_shard_recipe, f"full drum shard target must include {text}"

    assert_alias_target(makefile, "test-hf-drum-kit-samples", "test-hf-drum-kit-samples-parallel")
    assert "HF_DRUM_KIT_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(HF_DRUM_KIT_SHARD_CATEGORIES)))" in makefile, (
        "HF drum-kit shard tests must not force nested jobserver mode"
    )
    hf_parallel_recipe = target_recipe(makefile, "test-hf-drum-kit-samples-parallel")
    hf_unlocked_recipe = target_recipe(makefile, "test-hf-drum-kit-samples-parallel-unlocked")
    assert "$(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv" in hf_parallel_recipe.splitlines()[0], (
        "HF drum-kit parallel target must share a prepared manifest stamp"
    )
    assert "HF_DRUM_KIT_SHARD_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_samples.lock" in makefile, (
        "HF drum-kit sample shards must have a stable lock path"
    )
    assert "HF_DRUM_KIT_PREP_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_prepare.lock" in makefile, (
        "HF drum-kit fixture preparation must have a stable lock path"
    )
    assert "HF_DRUM_KIT_LIMIT_PER_CATEGORY ?= 300" in makefile, (
        "HF drum-kit fixture preparation must default to a bounded balanced corpus"
    )
    hf_prepare_recipe = target_recipe(makefile, "prepare-hf-drum-kit-samples")
    assert 'scripts/run_with_lock.sh "$(HF_DRUM_KIT_PREP_LOCK_DIR)" -- env' in hf_prepare_recipe, (
        "HF drum-kit fixture preparation must lock its shared output directory"
    )
    assert 'scripts/run_with_lock.sh "$(HF_DRUM_KIT_SHARD_LOCK_DIR)" -- "$(MAKE)" test-hf-drum-kit-samples-parallel-unlocked' in hf_parallel_recipe, (
        "HF drum-kit parallel target must lock shared shard outputs"
    )
    assert "$(MAKE) $(HF_DRUM_KIT_TEST_MAKE_JOBS) $(HF_DRUM_KIT_SHARD_TARGETS)" in hf_unlocked_recipe, (
        "HF drum-kit parallel target must fan out category shards through jobserver-aware make"
    )
    assert "$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples_parallel" in hf_unlocked_recipe, (
        "HF drum-kit parallel target must report aggregate duration"
    )
    assert "$(PYTHON) scripts/check_drum_sample_shards.py" in hf_unlocked_recipe, (
        "HF drum-kit parallel target must validate aggregated shard matrices"
    )
    hf_shard_recipe = target_recipe(makefile, "test-hf-drum-kit-samples-shard-%")
    for text in [
        "$(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0",
    ]:
        assert text in hf_shard_recipe, f"HF drum-kit shard target must include {text}"
    assert_alias_target(
        makefile,
        "analyze-hf-drum-primary-attribute-rows",
        "analyze-hf-drum-primary-attribute-rows-parallel",
    )
    hf_attribute_parallel_recipe = target_recipe(makefile, "analyze-hf-drum-primary-attribute-rows-parallel")
    assert "HF_DRUM_KIT_PRIMARY_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_primary_attribute_rows.lock" in makefile, (
        "HF drum-kit attribute rows must have a stable lock path"
    )
    assert "scripts/build_sharded_tsv.sh \"$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)\" \"$(MAKE)\" \"$(HF_DRUM_KIT_TEST_MAKE_JOBS)\" $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_PARTS)" in hf_attribute_parallel_recipe, (
        "HF drum-kit attribute rows must be built by the sharded TSV combiner"
    )
    assert "scripts/run_with_lock.sh \"$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_LOCK_DIR)\"" in hf_attribute_parallel_recipe, (
        "HF drum-kit attribute rows must lock shared output files"
    )
    hf_attribute_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_%.tsv")
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in hf_attribute_shard_recipe, (
        "HF drum-kit attribute shard must include primary debug rows"
    )

    assert_alias_target(makefile, "test-idmt-drums-samples", "test-idmt-drums-samples-parallel")
    assert "IDMT_DRUMS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(IDMT_DRUMS_SHARD_CATEGORIES)))" in makefile, (
        "IDMT drum shard tests must not force nested jobserver mode"
    )
    idmt_parallel_recipe = target_recipe(makefile, "test-idmt-drums-samples-parallel")
    idmt_unlocked_recipe = target_recipe(makefile, "test-idmt-drums-samples-parallel-unlocked")
    assert "$(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv" in idmt_parallel_recipe.splitlines()[0], (
        "IDMT drum parallel target must share a prepared manifest stamp"
    )
    assert "IDMT_DRUMS_SHARD_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_samples.lock" in makefile, (
        "IDMT drum sample shards must have a stable lock path"
    )
    assert "IDMT_DRUMS_ARCHIVE_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_archive.lock" in makefile, (
        "IDMT drum archive download must have a stable lock path"
    )
    assert "IDMT_DRUMS_PREP_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_prepare.lock" in makefile, (
        "IDMT drum fixture preparation must have a stable lock path"
    )
    idmt_archive_recipe = target_recipe(makefile, "$(IDMT_DRUMS_ARCHIVE)")
    assert 'scripts/run_with_lock.sh "$(IDMT_DRUMS_ARCHIVE_LOCK_DIR)"' in idmt_archive_recipe, (
        "IDMT drum archive download must lock its partial archive"
    )
    assert "scripts/download_idmt_drums_archive.sh" in idmt_archive_recipe, (
        "IDMT drum archive download must use the atomic archive helper"
    )
    idmt_prepare_recipe = target_recipe(makefile, "prepare-idmt-drums-samples")
    assert 'scripts/run_with_lock.sh "$(IDMT_DRUMS_PREP_LOCK_DIR)" -- env' in idmt_prepare_recipe, (
        "IDMT drum fixture preparation must lock its shared output directory"
    )
    assert 'scripts/run_with_lock.sh "$(IDMT_DRUMS_SHARD_LOCK_DIR)" -- "$(MAKE)" test-idmt-drums-samples-parallel-unlocked' in idmt_parallel_recipe, (
        "IDMT drum parallel target must lock shared shard outputs"
    )
    assert "$(MAKE) $(IDMT_DRUMS_TEST_MAKE_JOBS) $(IDMT_DRUMS_SHARD_TARGETS)" in idmt_unlocked_recipe, (
        "IDMT drum parallel target must fan out category shards through jobserver-aware make"
    )
    assert "--categories \"kick,snare,hihat\"" in idmt_unlocked_recipe, (
        "IDMT drum parallel checker must validate only dataset categories"
    )
    idmt_shard_recipe = target_recipe(makefile, "test-idmt-drums-samples-shard-%")
    for text in [
        "$(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv",
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=\"$*\"",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0",
    ]:
        assert text in idmt_shard_recipe, f"IDMT drum shard target must include {text}"
    assert_alias_target(
        makefile,
        "analyze-idmt-drum-primary-attribute-rows",
        "analyze-idmt-drum-primary-attribute-rows-parallel",
    )
    idmt_attribute_parallel_recipe = target_recipe(makefile, "analyze-idmt-drum-primary-attribute-rows-parallel")
    assert "IDMT_DRUMS_PRIMARY_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_primary_attribute_rows.lock" in makefile, (
        "IDMT drum attribute rows must have a stable lock path"
    )
    assert "scripts/build_sharded_tsv.sh \"$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)\" \"$(MAKE)\" \"$(IDMT_DRUMS_TEST_MAKE_JOBS)\" $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_PARTS)" in idmt_attribute_parallel_recipe, (
        "IDMT drum attribute rows must be built by the sharded TSV combiner"
    )
    assert "scripts/run_with_lock.sh \"$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_LOCK_DIR)\"" in idmt_attribute_parallel_recipe, (
        "IDMT drum attribute rows must lock shared output files"
    )
    idmt_attribute_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/idmt_drums_primary_attribute_rows_%.tsv")
    assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in idmt_attribute_shard_recipe, (
        "IDMT drum attribute shard must include primary debug rows"
    )

    phony_lines = "\n".join(re.findall(r"^\.PHONY:.*$", makefile, re.MULTILINE))
    drum_full_cached_recipe = target_recipe(makefile, "find-drum-full-exact-attribute-patterns-cached")
    assert "find-drum-full-exact-attribute-patterns-cached" in phony_lines, (
        "cached full drum pattern target must be phony"
    )
    assert "find-protected-drum-full-exact-attribute-patterns" in phony_lines, (
        "protected full drum pattern target must be phony"
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
    assert_alias_target(
        makefile, "test-guitar-chord-mix-samples", "test-guitar-chord-mix-samples-parallel"
    )
    guitar_chord_serial_recipe = target_recipe(makefile, "test-guitar-chord-mix-samples-serial")
    assert "$(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples env" in guitar_chord_serial_recipe, (
        "guitar chord mix serial target must preserve the single-process analyzer harness"
    )
    assert "MUSIC_ANALYZER_GUITARSET_SHARD_COUNT" not in guitar_chord_serial_recipe, (
        "guitar chord mix serial target must not set shard variables"
    )
    assert "MUSIC_ANALYZER_GUITARSET_MIN_PRIMARY_CHORD_HITS=\"$(GUITAR_CHORD_MIX_MIN_PRIMARY_CHORD_HITS)\"" in guitar_chord_serial_recipe, (
        "guitar chord mix serial target must enforce primary chord hits"
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
        "--min-primary-chord-hits \"$(GUITAR_CHORD_MIX_MIN_PRIMARY_CHORD_HITS)\"",
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
        "MUSIC_ANALYZER_GUITARSET_MIN_PRIMARY_CHORD_HITS=0",
    ]:
        assert text in guitar_chord_shard_recipe, (
            f"guitar chord mix shard target must include {text}"
        )
    for public_target, aggregate, shard, jobs_var, shards_var, targets_var, duration in [
        (
            "test-guitar-techs-chord-samples",
            "test-guitar-techs-chord-samples-parallel",
            "test-guitar-techs-chord-samples-shard-%",
            "GUITAR_TECHS_CHORD_TEST_MAKE_JOBS",
            "GUITAR_TECHS_CHORD_SHARDS",
            "GUITAR_TECHS_CHORD_SHARD_TARGETS",
            "analyzer_guitar_techs_chord_samples_parallel",
        ),
        (
            "test-egfxset-guitar-samples",
            "test-egfxset-guitar-samples-parallel",
            "test-egfxset-guitar-samples-shard-%",
            "EGFXSET_GUITAR_TEST_MAKE_JOBS",
            "EGFXSET_GUITAR_SHARDS",
            "EGFXSET_GUITAR_SHARD_TARGETS",
            "analyzer_egfxset_guitar_samples_parallel",
        ),
        (
            "test-gaps-guitar-samples",
            "test-gaps-guitar-samples-parallel",
            "test-gaps-guitar-samples-shard-%",
            "GAPS_GUITAR_TEST_MAKE_JOBS",
            "GAPS_GUITAR_SHARDS",
            "GAPS_GUITAR_SHARD_TARGETS",
            "analyzer_gaps_guitar_samples_parallel",
        ),
        (
            "test-gaps-guitar-samples-full",
            "test-gaps-guitar-samples-full-parallel",
            "test-gaps-guitar-samples-full-shard-%",
            "GAPS_GUITAR_FULL_TEST_MAKE_JOBS",
            "GAPS_GUITAR_FULL_SHARDS",
            "GAPS_GUITAR_FULL_SHARD_TARGETS",
            "analyzer_gaps_guitar_samples_full_parallel",
        ),
        (
            "test-downloaded-guitarset",
            "test-downloaded-guitarset-parallel",
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
        assert_alias_target(makefile, public_target, aggregate)
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
    egfxset_shard_recipe = target_recipe(makefile, "test-egfxset-guitar-samples-shard-%")
    for text in [
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
    ]:
        assert text in egfxset_shard_recipe, (
            f"EGFXSET shard target must keep per-shard coverage gate permissive: {text}"
        )
    for text in [
        'MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(EGFXSET_GUITAR_MIN_EXCERPTS)"',
        'MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(EGFXSET_GUITAR_MIN_WINDOWS)"',
    ]:
        assert text not in egfxset_shard_recipe, (
            f"EGFXSET shard target must leave aggregate coverage gate to the parent checker: {text}"
        )
    for target, aggregate_vars in {
        "test-guitar-techs-chord-samples-shard-%": "GUITAR_TECHS_CHORD",
        "test-gaps-guitar-samples-shard-%": "GAPS_GUITAR",
        "test-gaps-guitar-samples-full-shard-%": "GAPS_GUITAR_FULL",
    }.items():
        shard_recipe = target_recipe(makefile, target)
        for text in [
            "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
            "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
            "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        ]:
            assert text in shard_recipe, (
                f"{target} must keep per-shard coverage/chord gates permissive: {text}"
            )
        for text in [
            f'MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$({aggregate_vars}_MIN_EXCERPTS)"',
            f'MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$({aggregate_vars}_MIN_WINDOWS)"',
            f'MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$({aggregate_vars}_MIN_WINDOWS)"',
        ]:
            assert text not in shard_recipe, (
                f"{target} must leave aggregate coverage/chord gates to the parent checker: {text}"
            )
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
    for target, override, parallel_target in [
        ("test-iowa-piano-samples-max", "IOWA_PIANO_SAMPLE_LIMIT=0", "test-iowa-piano-samples-parallel"),
        (
            "test-iowa-orchestra-full-samples-max",
            "IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT=0 IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE=0",
            "test-iowa-orchestra-full-samples-parallel",
        ),
        ("test-good-sounds-samples-max", "GOOD_SOUNDS_SAMPLE_LIMIT=0", "test-good-sounds-samples-parallel"),
        (
            "test-medley-solos-samples-max",
            "MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=0",
            "test-medley-solos-samples-parallel",
        ),
        ("test-maps-piano-samples-max", "MAPS_PIANO_RECORDING_LIMIT=0", "test-maps-piano-samples-parallel"),
        (
            "test-maps-piano-note-samples-max",
            "MAPS_PIANO_NOTE_RECORDING_LIMIT=0",
            "test-maps-piano-note-samples-parallel",
        ),
    ]:
        max_helper_recipe = target_recipe(makefile, target)
        assert override in max_helper_recipe, f"{target} must preserve its max override"
        assert parallel_target in max_helper_recipe, f"{target} must delegate to {parallel_target}"

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
    assert "analyze-drum-spread-gate-matrix: analyze-drum-spread-gate-matrix-parallel" in makefile, (
        "default spread matrix target must use the parallel spread row builder"
    )
    spread_parallel_recipe = target_recipe(makefile, "analyze-drum-spread-gate-matrix-parallel")
    spread_unlocked_recipe = target_recipe(
        makefile, "analyze-drum-spread-gate-matrix-parallel-unlocked"
    )
    assert "DRUM_SPREAD_EXACT_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_spread_exact_attribute_rows.lock" in makefile, (
        "spread drum exact attribute rows must have a stable lock path"
    )
    assert '"$(MAKE)" analyze-drum-spread-gate-matrix-parallel-unlocked' in spread_parallel_recipe, (
        "parallel spread matrix target must run the full implementation under the lock"
    )
    assert "scripts/build_sharded_tsv.sh" in spread_unlocked_recipe, (
        "parallel spread matrix target must concatenate sharded exact TSV rows"
    )
    assert "scripts/run_with_lock.sh \"$(DRUM_SPREAD_EXACT_ATTRIBUTE_LOCK_DIR)\"" in spread_parallel_recipe, (
        "parallel spread matrix target must lock shared exact TSV rows"
    )
    assert "$(DRUM_SPREAD_EXACT_ATTRIBUTE_PARTS)" in spread_unlocked_recipe, (
        "parallel spread matrix target must build the category exact row parts"
    )
    assert "scripts/check_drum_sample_shards.py" in spread_unlocked_recipe, (
        "parallel spread matrix target must validate the same drum gate thresholds"
    )
    assert not re.search(r"\n\t.*scripts/check_drum_sample_shards\.py", spread_parallel_recipe), (
        "parallel spread matrix checker must stay inside the lock"
    )
    assert "$(DRUM_SAMPLE_SPREAD_SHARD_OUTS)" in spread_unlocked_recipe, (
        "parallel spread matrix target must validate category shard outputs"
    )
    assert 'scripts/summarize_drum_gate_matrix.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in spread_unlocked_recipe, (
        "parallel spread matrix target must summarize the concatenated TSV"
    )
    spread_shard_recipe = target_recipe(makefile, "$(BUILD_DIR)/drum_spread_exact_attribute_rows_%.tsv")
    assert 'MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*"' in spread_shard_recipe, (
        "spread exact TSV shard must run one expected category at a time"
    )
    assert 'MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*"' in spread_shard_recipe, (
        "spread exact TSV shard must filter the manifest category"
    )
    assert "--dump-rows --include-debug-rows" in spread_shard_recipe, (
        "spread exact TSV shard must include protected correct rows"
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
        "find-protected-drum-full-exact-attribute-patterns",
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
        "find-real-note-coverage-row-confusion-patterns",
        "find-real-note-visual-row-confusion-patterns",
        "find-real-note-focused-visual-row-confusion-patterns",
        "find-real-note-coverage-visual-row-confusion-patterns",
        "find-real-note-ownership-patterns",
        "find-real-note-octave-displacement-patterns",
        "find-real-note-weak-expected-patterns",
        "find-real-note-weak-visual-expected-patterns",
    ]:
        assert '--jobs "$(REAL_NOTE_PATTERN_JOBS)"' in target_recipe(makefile, target), (
            f"{target} should mine independent real-note buckets in parallel by default"
        )
    assert "INSTRUMENT_PATTERN_JOBS ?= $(PARALLEL_TEST_JOBS)" in makefile, (
        "instrument pattern mining should default to the shared parallel job count"
    )
    for target in ["find-instrument-owner-patterns", "find-instrument-status-patterns"]:
        assert '--jobs "$(INSTRUMENT_PATTERN_JOBS)"' in target_recipe(makefile, target), (
            f"{target} should mine independent instrument buckets in parallel by default"
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

    for target in ["analyze-hf-drum-primary-attribute-rows-serial", "analyze-idmt-drum-primary-attribute-rows-serial"]:
        recipe_text = target_recipe(makefile, target)
        assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in recipe_text, (
            f"{target} must include primary miss diagnostics in its row dump"
        )
        assert "--dump-rows --include-debug-rows" in recipe_text, (
            f"{target} must dump miss rows together with protected correct rows"
        )
    for target in [
        "$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_%.tsv",
        "$(BUILD_DIR)/idmt_drums_primary_attribute_rows_%.tsv",
    ]:
        recipe_text = target_recipe(makefile, target)
        assert "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1" in recipe_text, (
            f"{target} must include primary miss diagnostics in its row dump"
        )
        assert "--dump-rows --include-debug-rows" in recipe_text, (
            f"{target} must dump miss rows together with protected correct rows"
        )
    for target, rows in [
        ("find-hf-drum-primary-attribute-patterns", "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)"),
        ("find-idmt-drum-primary-attribute-patterns", "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"),
    ]:
        recipe_text = target_recipe(makefile, target)
        assert f'$(BUILD_DIR)/analyzer_drum_samples" -nt "{rows}"' in recipe_text, (
            f"{target} must not mine stale protected rows"
        )
        assert f'scripts/analyze_drum_primary_debug.py" -nt "{rows}"' in recipe_text, (
            f"{target} must refresh rows when the parser changes"
        )
    protected_recipe = target_recipe(makefile, "find-protected-drum-primary-attribute-patterns")
    assert '[ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ]' in protected_recipe, (
        "protected drum primary mining must refresh stale HF and IDMT rows"
    )
    assert '$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"' in protected_recipe, (
        "protected drum primary mining must refresh stale spread rows"
    )
    assert '[ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]' in protected_recipe, (
        "protected drum primary mining must refresh optional full exact rows"
    )
    assert "$(MAKE) analyze-drum-full-gate-matrix-parallel" in protected_recipe, (
        "protected drum primary mining must rebuild stale optional full exact rows when the sample source is available"
    )
    assert 'for path in $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS)' in protected_recipe, (
        "protected drum primary mining must include the configured protected row set after refresh"
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
        "$(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IDMT_BASS_LINES_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS)": (
            "$(IDMT_BASS_LINES_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IDMT_GUITAR_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IDMT_GUITAR_MISS_ATTRIBUTE_ROWS)": (
            "$(IDMT_GUITAR_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)": (
            "$(GUITAR_TECHS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS)": (
            "$(GUITAR_TECHS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)": (
            "$(GOOD_SOUNDS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS)": (
            "$(GOOD_SOUNDS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(TINYSOL_DETECTED_ATTRIBUTE_ROWS)": (
            "$(TINYSOL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(TINYSOL_MISS_ATTRIBUTE_ROWS)": (
            "$(TINYSOL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IOWA_PIANO_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IOWA_PIANO_MISS_ATTRIBUTE_ROWS)": (
            "$(IOWA_PIANO_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IOWA_STRINGS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IOWA_STRINGS_MISS_ATTRIBUTE_ROWS)": (
            "$(IOWA_STRINGS_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)": (
            "$(PHILHARMONIA_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(PHILHARMONIA_MISS_ATTRIBUTE_ROWS)": (
            "$(PHILHARMONIA_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)": (
            "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS)": (
            "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IOWA_ORCHESTRA_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS)": (
            "$(IOWA_ORCHESTRA_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
        ),
        "$(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)": (
            "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--dump-rows",
            "--include-empty-debug",
        ),
        "$(IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS)": (
            "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)",
            "inspect_real_note_attribute_buckets.py",
            "--include-empty-debug",
            "--status miss",
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
        "$(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS)": (
            "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(GUITAR_TECHS_CHORD_MISS_ATTRIBUTE_ROWS)": (
            "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--misses-only",
        ),
        "$(EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS)": (
            "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(EGFXSET_GUITAR_MISS_ATTRIBUTE_ROWS)": (
            "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--misses-only",
        ),
        "$(GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS)": (
            "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(GAPS_GUITAR_MISS_ATTRIBUTE_ROWS)": (
            "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--misses-only",
        ),
        "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)": (
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
            "inspect_guitarset_attribute_buckets.py",
            "--dump-rows",
        ),
        "$(GAPS_GUITAR_FULL_MISS_ATTRIBUTE_ROWS)": (
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
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
        "$(IDMT_BASS_LINES_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IDMT_BASS_LINES_ATTRIBUTE_LOCK_DIR)",
            "$(IDMT_BASS_LINES_ATTRIBUTE_PARTS)",
        ),
        "$(IDMT_GUITAR_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IDMT_GUITAR_ATTRIBUTE_LOCK_DIR)",
            "$(IDMT_GUITAR_ATTRIBUTE_PARTS)",
        ),
        "$(GUITAR_TECHS_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GUITAR_TECHS_ATTRIBUTE_LOCK_DIR)",
            "$(GUITAR_TECHS_ATTRIBUTE_PARTS)",
        ),
        "$(GOOD_SOUNDS_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GOOD_SOUNDS_ATTRIBUTE_LOCK_DIR)",
            "$(GOOD_SOUNDS_ATTRIBUTE_PARTS)",
        ),
        "$(TINYSOL_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(TINYSOL_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(TINYSOL_ATTRIBUTE_LOCK_DIR)",
            "$(TINYSOL_ATTRIBUTE_PARTS)",
        ),
        "$(IOWA_PIANO_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IOWA_PIANO_ATTRIBUTE_LOCK_DIR)",
            "$(IOWA_PIANO_ATTRIBUTE_PARTS)",
        ),
        "$(IOWA_STRINGS_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IOWA_STRINGS_ATTRIBUTE_LOCK_DIR)",
            "$(IOWA_STRINGS_ATTRIBUTE_PARTS)",
        ),
        "$(PHILHARMONIA_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(PHILHARMONIA_ATTRIBUTE_LOCK_DIR)",
            "$(PHILHARMONIA_ATTRIBUTE_PARTS)",
        ),
        "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(PHILHARMONIA_FULL_ATTRIBUTE_LOCK_DIR)",
            "$(PHILHARMONIA_FULL_ATTRIBUTE_PARTS)",
        ),
        "$(IOWA_ORCHESTRA_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IOWA_ORCHESTRA_ATTRIBUTE_LOCK_DIR)",
            "$(IOWA_ORCHESTRA_ATTRIBUTE_PARTS)",
        ),
        "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_real_note_samples",
            "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_LOCK_DIR)",
            "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_PARTS)",
        ),
        "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR)",
            "$(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)",
        ),
        "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "$(GUITAR_TECHS_CHORD_MANIFEST)",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR)",
            "$(GUITAR_TECHS_CHORD_ATTRIBUTE_PARTS)",
        ),
        "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "$(EGFXSET_GUITAR_MANIFEST)",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(EGFXSET_GUITAR_ATTRIBUTE_LOCK_DIR)",
            "$(EGFXSET_GUITAR_ATTRIBUTE_PARTS)",
        ),
        "$(GAPS_GUITAR_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "$(GAPS_GUITAR_MANIFEST)",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GAPS_GUITAR_ATTRIBUTE_LOCK_DIR)",
            "$(GAPS_GUITAR_ATTRIBUTE_PARTS)",
        ),
        "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)": (
            "$(BUILD_DIR)/analyzer_guitarset",
            "$(GAPS_GUITAR_FULL_MANIFEST)",
            "scripts/build_sharded_tsv.sh",
            "scripts/run_with_lock.sh",
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_LOCK_DIR)",
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_PARTS)",
        ),
    }
    for target, required_parts in source_attribute_targets.items():
        source_recipe = target_recipe(makefile, target)
        for text in required_parts:
            assert text in source_recipe, f"{target} must include {text}"
        assert "| $(BUILD_DIR)" in source_recipe, f"{target} must create output under the build dir"
    assert "IDMT_BASS_LINES_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_bass_lines_attributes.lock" in makefile, (
        "IDMT bass-line attribute TSV must have a stable lock path"
    )
    assert "IDMT_GUITAR_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_guitar_attributes.lock" in makefile, (
        "IDMT guitar attribute TSV must have a stable lock path"
    )
    assert "GUITAR_TECHS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_techs_attributes.lock" in makefile, (
        "GuitarTechs attribute TSV must have a stable lock path"
    )
    assert "GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_techs_chord_attributes.lock" in makefile, (
        "GuitarTechs chord attribute TSV must have a stable lock path"
    )
    assert "GOOD_SOUNDS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/good_sounds_attributes.lock" in makefile, (
        "Good Sounds attribute TSV must have a stable lock path"
    )
    assert "TINYSOL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/tinysol_attributes.lock" in makefile, (
        "TinySOL attribute TSV must have a stable lock path"
    )
    assert "IOWA_PIANO_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_piano_attributes.lock" in makefile, (
        "Iowa piano attribute TSV must have a stable lock path"
    )
    assert "IOWA_STRINGS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_strings_attributes.lock" in makefile, (
        "Iowa strings attribute TSV must have a stable lock path"
    )
    assert "PHILHARMONIA_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/philharmonia_attributes.lock" in makefile, (
        "Philharmonia attribute TSV must have a stable lock path"
    )
    assert "PHILHARMONIA_FULL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/philharmonia_full_attributes.lock" in makefile, (
        "Philharmonia full attribute TSV must have a stable lock path"
    )
    assert "IOWA_ORCHESTRA_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_orchestra_attributes.lock" in makefile, (
        "Iowa orchestra attribute TSV must have a stable lock path"
    )
    assert "IOWA_ORCHESTRA_FULL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_orchestra_full_attributes.lock" in makefile, (
        "Iowa orchestra full attribute TSV must have a stable lock path"
    )

    real_note_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/real_note_full_mix_attributes.tsv")
    assert "REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))" in makefile, (
        "real-note attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "REAL_NOTE_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/real_note_full_mix_attributes.lock" in makefile, (
        "real-note attribute TSV must have a stable lock path"
    )
    assert "$(BUILD_DIR)/analyzer_real_note_samples" in real_note_attribute_recipe.splitlines()[0], (
        "real-note attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in real_note_attribute_recipe.splitlines()[0], (
        "real-note attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS)' in real_note_attribute_recipe, (
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

    vocadito_attribute_recipe = target_recipe(makefile, "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)")
    assert "VOCADITO_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/vocadito_full_mix_attributes.lock" in makefile, (
        "Vocadito attribute TSV must have a stable lock path"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(VOCADITO_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(VOCADITO_FULL_MIX_ATTRIBUTE_PARTS)' in vocadito_attribute_recipe, (
        "Vocadito attribute TSV must use the locked helper to build and combine shards"
    )
    for target, required_parts in {
        "$(BUILD_DIR)/idmt_bass_lines_attributes.shard-%.tsv": (
            "$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IDMT_BASS_LINES_MIN_BASS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IDMT_BASS_LINES_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "idmt_bass_lines_attributes.shard-$*.out",
            "idmt_bass_lines_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/idmt_guitar_attributes.shard-%.tsv": (
            "$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IDMT_GUITAR_MIN_GUITAR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IDMT_GUITAR_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "idmt_guitar_attributes.shard-$*.out",
            "idmt_guitar_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/guitar_techs_attributes.shard-%.tsv": (
            "$(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(GUITAR_TECHS_MIN_GUITAR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(GUITAR_TECHS_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "guitar_techs_attributes.shard-$*.out",
            "guitar_techs_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/good_sounds_attributes.shard-%.tsv": (
            "$(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(GOOD_SOUNDS_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(GOOD_SOUNDS_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "good_sounds_attributes.shard-$*.out",
            "good_sounds_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/tinysol_attributes.shard-%.tsv": (
            "$(TINYSOL_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(TINYSOL_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(TINYSOL_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "tinysol_attributes.shard-$*.out",
            "tinysol_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/iowa_piano_attributes.shard-%.tsv": (
            "$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IOWA_PIANO_MIN_PIANO)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IOWA_PIANO_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "iowa_piano_attributes.shard-$*.out",
            "iowa_piano_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/philharmonia_attributes.shard-%.tsv": (
            "$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(PHILHARMONIA_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(PHILHARMONIA_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "philharmonia_attributes.shard-$*.out",
            "philharmonia_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/philharmonia_full_attributes.shard-%.tsv": (
            "$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(PHILHARMONIA_FULL_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(PHILHARMONIA_FULL_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "philharmonia_full_attributes.shard-$*.out",
            "philharmonia_full_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/iowa_orchestra_attributes.shard-%.tsv": (
            "$(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IOWA_ORCHESTRA_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IOWA_ORCHESTRA_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "iowa_orchestra_attributes.shard-$*.out",
            "iowa_orchestra_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/iowa_strings_attributes.shard-%.tsv": (
            "$(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IOWA_STRINGS_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IOWA_STRINGS_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "iowa_strings_attributes.shard-$*.out",
            "iowa_strings_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/iowa_orchestra_full_attributes.shard-%.tsv": (
            "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "iowa_orchestra_full_attributes.shard-$*.out",
            "iowa_orchestra_full_attributes.shard-$*.err",
        ),
        "$(BUILD_DIR)/vocalset_attributes.shard-%.tsv": (
            "$(VOCALSET_SAMPLE_DIR)/manifest.tsv",
            "MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=\"$(VOCALSET_MIN_VOCALS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=\"$(VOCALSET_SAMPLE_DIR)\"",
            "MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV=\"$@\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT=\"$(REAL_NOTE_SAMPLE_SHARDS)\"",
            "MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=\"$*\"",
            "vocalset_attributes.shard-$*.out",
            "vocalset_attributes.shard-$*.err",
        ),
    }.items():
        idmt_attribute_shard_recipe = target_recipe(makefile, target)
        for text in required_parts:
            assert text in idmt_attribute_shard_recipe, (
                f"{target} must include {text}"
            )

    instrument_attribute_recipe = target_recipe(makefile, "$(BUILD_DIR)/instrument_sample_attributes.tsv")
    assert "INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))" in makefile, (
        "instrument attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "INSTRUMENT_SAMPLE_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/instrument_sample_attributes.lock" in makefile, (
        "instrument attribute TSV must have a stable lock path"
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
    assert '$(SHELL) scripts/run_with_lock.sh "$(INSTRUMENT_SAMPLE_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS)" $(INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS)' in instrument_attribute_recipe, (
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
    assert "GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_chord_mix_attributes.lock" in makefile, (
        "guitar chord attribute TSV must have a stable lock path"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in guitar_attribute_recipe.splitlines()[0], (
        "guitar chord attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in guitar_attribute_recipe.splitlines()[0], (
        "guitar chord attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)' in guitar_attribute_recipe, (
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

    guitar_techs_chord_attribute_recipe = target_recipe(makefile, "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)")
    assert "GUITAR_TECHS_CHORD_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_TECHS_CHORD_SHARDS))" in makefile, (
        "GuitarTechs chord attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in guitar_techs_chord_attribute_recipe.splitlines()[0], (
        "GuitarTechs chord attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "$(GUITAR_TECHS_CHORD_MANIFEST)" in guitar_techs_chord_attribute_recipe.splitlines()[0], (
        "GuitarTechs chord attribute TSV must rebuild when the prepared manifest changes"
    )
    assert "scripts/build_sharded_tsv.sh" in guitar_techs_chord_attribute_recipe.splitlines()[0], (
        "GuitarTechs chord attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_TECHS_CHORD_ATTRIBUTE_PARTS)' in guitar_techs_chord_attribute_recipe, (
        "GuitarTechs chord attribute TSV must use the locked helper to build and combine shards"
    )
    guitar_techs_chord_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/guitar_techs_chord_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_guitarset",
        "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0",
        "MUSIC_ANALYZER_GUITARSET_SHARD_COUNT=\"$(GUITAR_TECHS_CHORD_SHARDS)\"",
        "MUSIC_ANALYZER_GUITARSET_SHARD_INDEX=\"$*\"",
        "guitar_techs_chord_attributes.shard-$*.out",
    ]:
        assert text in guitar_techs_chord_attribute_shard_recipe, (
            f"GuitarTechs chord attribute shard target must include {text}"
        )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=\"$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)\"" not in guitar_techs_chord_attribute_shard_recipe, (
        "GuitarTechs chord attribute shards must not fail uneven shards with the global excerpt floor"
    )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=\"$(GUITAR_TECHS_CHORD_MIN_WINDOWS)\"" not in guitar_techs_chord_attribute_shard_recipe, (
        "GuitarTechs chord attribute shards must not fail uneven shards with the global window floor"
    )

    egfxset_guitar_attribute_recipe = target_recipe(makefile, "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)")
    assert "EGFXSET_GUITAR_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(EGFXSET_GUITAR_SHARDS))" in makefile, (
        "EGFXSET guitar attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "EGFXSET_GUITAR_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/egfxset_guitar_attributes.lock" in makefile, (
        "EGFXSET guitar attribute TSV must have a stable lock path"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in egfxset_guitar_attribute_recipe.splitlines()[0], (
        "EGFXSET guitar attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "$(EGFXSET_GUITAR_MANIFEST)" in egfxset_guitar_attribute_recipe.splitlines()[0], (
        "EGFXSET guitar attribute TSV must rebuild when the prepared manifest changes"
    )
    assert "scripts/build_sharded_tsv.sh" in egfxset_guitar_attribute_recipe.splitlines()[0], (
        "EGFXSET guitar attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(EGFXSET_GUITAR_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(EGFXSET_GUITAR_ATTRIBUTE_MAKE_JOBS)" $(EGFXSET_GUITAR_ATTRIBUTE_PARTS)' in egfxset_guitar_attribute_recipe, (
        "EGFXSET guitar attribute TSV must use the locked helper to build and combine shards"
    )
    egfxset_guitar_attribute_shard_recipe = target_recipe(
        makefile, "$(BUILD_DIR)/egfxset_guitar_attributes.shard-%.tsv"
    )
    for text in [
        "$(BUILD_DIR)/analyzer_guitarset",
        "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@\"",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=1",
        "MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0",
        "MUSIC_ANALYZER_GUITARSET_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT=100",
        "MUSIC_ANALYZER_GUITARSET_SHARD_COUNT=\"$(EGFXSET_GUITAR_SHARDS)\"",
        "MUSIC_ANALYZER_GUITARSET_SHARD_INDEX=\"$*\"",
        "egfxset_guitar_attributes.shard-$*.out",
    ]:
        assert text in egfxset_guitar_attribute_shard_recipe, (
            f"EGFXSET guitar attribute shard target must include {text}"
        )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=\"$(EGFXSET_GUITAR_MIN_EXCERPTS)\"" not in egfxset_guitar_attribute_shard_recipe, (
        "EGFXSET guitar attribute shards must not fail uneven shards with the global excerpt floor"
    )
    assert "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=\"$(EGFXSET_GUITAR_MIN_WINDOWS)\"" not in egfxset_guitar_attribute_shard_recipe, (
        "EGFXSET guitar attribute shards must not fail uneven shards with the global window floor"
    )
    egfxset_guitar_pattern_recipe = target_recipe(makefile, "find-egfxset-guitar-attribute-patterns")
    assert "EGFXSET_GUITAR_PATTERN_BUCKET ?= single_note_false_chord:any:any" in makefile, (
        "EGFXSET guitar pattern mining should default to the single-note false-chord bucket"
    )
    assert "EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET ?= no_chord:any:any" in makefile, (
        "EGFXSET guitar pattern mining should protect clean no-chord single-note rows by default"
    )
    assert "EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKETS ?= $(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET) chord_hit:any:any" in makefile, (
        "EGFXSET guitar pattern mining should also protect known guitar chord hits by default"
    )
    assert "EGFXSET_GUITAR_PATTERN_PROTECTED_PATHS ?= $(EGFXSET_GUITAR_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv" in makefile, (
        "EGFXSET guitar pattern mining should compare against both single-note and chord-hit rows"
    )
    assert 'EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET_ARGS = $(foreach bucket,$(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKETS),--protected-bucket "$(bucket)")' in makefile, (
        "EGFXSET guitar pattern mining must expand all default protected buckets"
    )
    assert 'EGFXSET_GUITAR_PATTERN_PROTECTED_PATH_ARGS = $(foreach path,$(EGFXSET_GUITAR_PATTERN_PROTECTED_PATHS),--protected-path "$(path)")' in makefile, (
        "EGFXSET guitar pattern mining must expand all default protected paths"
    )
    assert "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" in egfxset_guitar_pattern_recipe.splitlines()[0], (
        "EGFXSET guitar pattern mining must refresh real guitar chord-hit protected rows by default"
    )
    assert '$(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)",--bucket "$(EGFXSET_GUITAR_PATTERN_BUCKET)")' in egfxset_guitar_pattern_recipe, (
        "EGFXSET guitar pattern mining must use a useful default bucket while allowing PATTERN_BUCKET overrides"
    )
    assert '$(if $(PATTERN_PROTECTED_PATHS),$(foreach path,$(PATTERN_PROTECTED_PATHS),--protected-path "$(path)"),$(EGFXSET_GUITAR_PATTERN_PROTECTED_PATH_ARGS))' in egfxset_guitar_pattern_recipe, (
        "EGFXSET guitar pattern mining must allow protected-path overrides"
    )
    assert '$(if $(PATTERN_PROTECTED_BUCKET),--protected-bucket "$(PATTERN_PROTECTED_BUCKET)",$(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET_ARGS))' in egfxset_guitar_pattern_recipe, (
        "EGFXSET guitar pattern mining must compare against protected rows while allowing protected-bucket overrides"
    )

    for label, target, manifest, shards, lock_dir, parts, shard_target, out_name in [
        (
            "GAPS guitar",
            "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
            "$(GAPS_GUITAR_MANIFEST)",
            "$(GAPS_GUITAR_SHARDS)",
            "$(GAPS_GUITAR_ATTRIBUTE_LOCK_DIR)",
            "$(GAPS_GUITAR_ATTRIBUTE_PARTS)",
            "$(BUILD_DIR)/gaps_guitar_attributes.shard-%.tsv",
            "gaps_guitar_attributes.shard-$*.out",
        ),
        (
            "full GAPS guitar",
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
            "$(GAPS_GUITAR_FULL_MANIFEST)",
            "$(GAPS_GUITAR_FULL_SHARDS)",
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_LOCK_DIR)",
            "$(GAPS_GUITAR_FULL_ATTRIBUTE_PARTS)",
            "$(BUILD_DIR)/gaps_guitar_full_attributes.shard-%.tsv",
            "gaps_guitar_full_attributes.shard-$*.out",
        ),
    ]:
        attribute_recipe = target_recipe(makefile, target)
        assert "$(BUILD_DIR)/analyzer_guitarset" in attribute_recipe.splitlines()[0], (
            f"{label} attribute TSV must rebuild when the analyzer binary changes"
        )
        assert manifest in attribute_recipe.splitlines()[0], (
            f"{label} attribute TSV must rebuild when the prepared manifest changes"
        )
        assert "scripts/build_sharded_tsv.sh" in attribute_recipe.splitlines()[0], (
            f"{label} attribute TSV must rebuild when the sharded TSV helper changes"
        )
        assert f'$(SHELL) scripts/run_with_lock.sh "{lock_dir}" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "' in attribute_recipe, (
            f"{label} attribute TSV must use the locked helper to build and combine shards"
        )
        assert parts in attribute_recipe, f"{label} attribute TSV must combine all shard parts"

        shard_recipe = target_recipe(makefile, shard_target)
        for text in [
            "$(BUILD_DIR)/analyzer_guitarset",
            f'MUSIC_ANALYZER_GUITARSET_MANIFEST="{manifest}"',
            "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV=\"$@\"",
            "$(GUITARSET_ATTRIBUTE_GATE_ENV)",
            "MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2",
            "MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2",
            f"MUSIC_ANALYZER_GUITARSET_SHARD_COUNT=\"{shards}\"",
            "MUSIC_ANALYZER_GUITARSET_SHARD_INDEX=\"$*\"",
            out_name,
        ]:
            assert text in shard_recipe, f"{label} attribute shard target must include {text}"
        assert "$(GUITARSET_SHARD_GATE_ENV)" not in shard_recipe, (
            f"{label} attribute shards must allow empty shards while gathering cached rows"
        )

    assert "GAPS_GUITAR_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_SHARDS))" in makefile, (
        "GAPS guitar attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "GAPS_GUITAR_FULL_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_FULL_SHARDS))" in makefile, (
        "full GAPS guitar attribute shards must force -j only when the parent make has no jobserver"
    )

    downloaded_guitarset_attribute_recipe = target_recipe(makefile, "$(GUITARSET_ATTRIBUTE_TSV)")
    assert "GUITARSET_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITARSET_SHARDS))" in makefile, (
        "downloaded GuitarSet attribute shards must force -j only when the parent make has no jobserver"
    )
    assert "GUITARSET_ATTRIBUTE_GATE_ENV ?=" in makefile, (
        "downloaded GuitarSet attribute shards must have a separate permissive coverage gate"
    )
    for text in [
        "MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_ONLY=1",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=0",
        "MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=0",
    ]:
        assert text in makefile, f"downloaded GuitarSet attribute gate must include {text}"
    assert "GUITARSET_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitarset_attributes.lock" in makefile, (
        "downloaded GuitarSet attribute TSV must have a stable lock path"
    )
    assert "$(BUILD_DIR)/analyzer_guitarset" in downloaded_guitarset_attribute_recipe.splitlines()[0], (
        "downloaded GuitarSet attribute TSV must rebuild when the analyzer binary changes"
    )
    assert "scripts/build_sharded_tsv.sh" in downloaded_guitarset_attribute_recipe.splitlines()[0], (
        "downloaded GuitarSet attribute TSV must rebuild when the sharded TSV helper changes"
    )
    assert '$(SHELL) scripts/run_with_lock.sh "$(GUITARSET_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITARSET_ATTRIBUTE_MAKE_JOBS)" $(GUITARSET_ATTRIBUTE_PARTS)' in downloaded_guitarset_attribute_recipe, (
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
        "$(GUITARSET_ATTRIBUTE_GATE_ENV)",
        "guitarset_attributes.shard-$*.out",
    ]:
        assert text in downloaded_guitarset_attribute_shard_recipe, (
            f"downloaded GuitarSet attribute shard target must include {text}"
        )
    assert "$(GUITARSET_SHARD_GATE_ENV)" not in downloaded_guitarset_attribute_shard_recipe, (
        "downloaded GuitarSet attribute shards must not fail just because a shard has no usable excerpts"
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
        "analyze-idmt-bass-lines-attributes": "$(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-idmt-guitar-attributes": "$(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-guitar-techs-attributes": "$(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-good-sounds-attributes": "$(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-tinysol-attributes": "$(TINYSOL_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-iowa-piano-attributes": "$(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-iowa-strings-attributes": "$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-philharmonia-attributes": "$(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-philharmonia-full-attributes": "$(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-iowa-orchestra-attributes": "$(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-iowa-orchestra-full-attributes": "$(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)",
        "analyze-guitar-chord-mix-recovery": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "analyze-guitar-chord-mix-extra-components": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "inspect-guitar-chord-mix-attribute-buckets": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "find-guitar-chord-mix-attribute-patterns": "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv",
        "analyze-egfxset-guitar-attributes": "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)",
        "inspect-egfxset-guitar-attribute-buckets": "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)",
        "find-egfxset-guitar-attribute-patterns": "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)",
        "analyze-gaps-guitar-attributes": "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
        "inspect-gaps-guitar-attribute-buckets": "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
        "find-gaps-guitar-attribute-patterns": "$(GAPS_GUITAR_ATTRIBUTE_TSV)",
        "analyze-gaps-guitar-full-attributes": "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
        "inspect-gaps-guitar-full-attribute-buckets": "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
        "find-gaps-guitar-full-attribute-patterns": "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)",
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
    real_note_rule_recipe = target_recipe(makefile, "measure-real-note-attribute-rule")
    assert "$(REAL_NOTE_RULE_CONDITION_ARGS)" in real_note_rule_recipe, (
        "real-note rule measurement must accept quoted conditions through REAL_NOTE_RULE_CONDITIONS"
    )
    assert "$(REAL_NOTE_RULE_GROUP_BY_ARGS)" in real_note_rule_recipe, (
        "real-note rule measurement must accept quoted grouping fields through REAL_NOTE_RULE_GROUP_BY"
    )
    assert "$(RULE_ARGS)" in real_note_rule_recipe, (
        "real-note rule measurement must keep the low-level RULE_ARGS escape hatch"
    )
    for text in [
        'REAL_NOTE_RULE_CONDITION_ARGS = $(foreach condition,$(REAL_NOTE_RULE_CONDITIONS),--condition "$(condition)")',
        'REAL_NOTE_RULE_GROUP_BY_ARGS = $(foreach field,$(REAL_NOTE_RULE_GROUP_BY),--group-by "$(field)")',
    ]:
        assert text in makefile, f"real-note rule Makefile plumbing must include {text}"
    real_note_candidate_recipe = target_recipe(makefile, "inspect-real-note-candidate-rows")
    assert "$(REAL_NOTE_CANDIDATE_ROW_PATHS)" in real_note_candidate_recipe, (
        "real-note candidate inspection must accept TSV paths through REAL_NOTE_CANDIDATE_ROW_PATHS"
    )
    assert '--rule "$(REAL_NOTE_CANDIDATE_RULE)"' in real_note_candidate_recipe, (
        "real-note candidate inspection must pass route-summary rules as one quoted --rule"
    )
    assert "$(REAL_NOTE_CANDIDATE_ARGS)" in real_note_candidate_recipe, (
        "real-note candidate inspection must keep an argument escape hatch"
    )
    detector_coverage_recipe = target_recipe(makefile, "inspect-detector-coverage-candidates")
    assert "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" not in detector_coverage_recipe.splitlines()[0], (
        "detector coverage inspection must not force-refresh the route summary"
    )
    assert 'test -f "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"' in detector_coverage_recipe, (
        "detector coverage inspection must require an existing saved route summary"
    )
    assert '"$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"' in detector_coverage_recipe, (
        "detector coverage inspection must pass the saved route summary to the helper"
    )
    assert "scripts/inspect_detector_coverage_candidates.py" in detector_coverage_recipe, (
        "detector coverage inspection must use the dedicated coverage helper"
    )
    assert "$(DETECTOR_COVERAGE_CANDIDATE_ARGS)" in detector_coverage_recipe, (
        "detector coverage inspection must keep an argument escape hatch"
    )
    assert "$(DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS)" in detector_coverage_recipe, (
        "detector coverage inspection must accept cached TSV paths through Make"
    )
    detector_coverage_cached_recipe = target_recipe(makefile, "detector-improvement-coverage-cached")
    assert "inspect-detector-coverage-candidates" in detector_coverage_cached_recipe, (
        "cached detector coverage helper must reuse the inspector target"
    )
    assert 'DETECTOR_COVERAGE_CANDIDATE_ARGS="$(DETECTOR_COVERAGE_SUMMARY_ARGS)"' in detector_coverage_cached_recipe, (
        "cached detector coverage helper must use the compact summary args"
    )
    cached_pattern_coverage_recipe = target_recipe(makefile, "measure-analyzer-patterns-cached-coverage")
    assert "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" in cached_pattern_coverage_recipe, (
        "cached pattern coverage must inspect the existing cached candidate summary"
    )
    assert "scripts/inspect_detector_coverage_candidates.py" in cached_pattern_coverage_recipe, (
        "cached pattern coverage must reuse the detector coverage inspector"
    )
    assert "$(DETECTOR_COVERAGE_SUMMARY_ARGS)" in cached_pattern_coverage_recipe, (
        "cached pattern coverage must use compact coverage output by default"
    )
    assert "$(DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS)" in cached_pattern_coverage_recipe, (
        "cached pattern coverage must inspect configured cached candidate row paths"
    )
    assert 'if [ ! -f "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" ]' in cached_pattern_coverage_recipe, (
        "cached pattern coverage should rebuild the candidate summary only when it is missing"
    )
    cached_pattern_summary_recipe = target_recipe(makefile, "measure-analyzer-patterns-cached-summary")
    assert "measure-analyzer-patterns-cached-coverage" in cached_pattern_summary_recipe, (
        "cached pattern summary should print expanded coverage status beside candidate blockers"
    )
    for text in [
        "REAL_NOTE_CANDIDATE_ROW_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv",
        "REAL_NOTE_CANDIDATE_RULE ?=",
        "REAL_NOTE_CANDIDATE_ARGS ?=",
        "GUITAR_CANDIDATE_ROW_PATHS ?= $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GUITARSET_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS) $(EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)",
        "DRUM_CANDIDATE_ROW_PATHS ?= $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv",
        "DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS ?= $(wildcard $(REAL_NOTE_CANDIDATE_ROW_PATHS) $(GUITAR_CANDIDATE_ROW_PATHS) $(DRUM_CANDIDATE_ROW_PATHS) $(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS))",
        "MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY := $(BUILD_DIR)/measure_analyzer_cached_pattern_coverage_summary.txt",
        "DETECTOR_COVERAGE_CANDIDATE_ARGS ?=",
        "DETECTOR_COVERAGE_SUMMARY_ARGS ?= --summary-only --top 12",
        "detector-improvement-status-cached",
        "ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-detector-coverage-candidates",
    ]:
        assert text in makefile, f"real-note candidate Makefile plumbing must include {text}"
    assert "GUITARSET_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitarset_detected_attribute_rows.tsv" in makefile, (
        "GuitarSet coverage inspection must have a cached derived-row target"
    )
    guitarset_detected_recipe = target_recipe(makefile, "$(GUITARSET_DETECTED_ATTRIBUTE_ROWS)")
    assert "--dump-rows" in guitarset_detected_recipe, (
        "GuitarSet coverage rows must expose derived chord evidence columns"
    )
    runtime_excludes = continuation_variable_body(makefile, "REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES")
    for field in [
        "expected_row_score",
        "first_row_score",
        "visual_first_row_score",
        "strongest_row_score",
        "visual_strongest_row_score",
        "expected_first_score_ratio",
        "expected_strongest_score_ratio",
        "expected_visual_first_score_ratio",
        "expected_visual_strongest_score_ratio",
        "first_expected_score_margin",
        "strongest_expected_score_margin",
        "visual_first_expected_score_margin",
        "visual_strongest_expected_score_margin",
        "expected_strongest_pitch_level_ratio",
        "strongest_expected_pitch_level_margin",
        "expected_visual_strongest_pitch_level_ratio",
        "visual_strongest_expected_pitch_level_margin",
    ]:
        assert f"--exclude-field {field}" in runtime_excludes, (
            f"runtime route scans must exclude ground-truth-derived field {field}"
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
    assert "EXTRA_COMPONENT_ARGS ?= --simulate-prune primary-equivalent" in makefile, (
        "default guitar extra-component report must simulate candidate label-pruning policies"
    )
    assert "--simulate-prune primary-equivalent-observed-playable" in makefile, (
        "guitar extra-component report must include observed-playable equivalent pruning"
    )
    assert "--simulate-prune primary-equivalent-plain-observed-playable" in makefile, (
        "guitar extra-component report must measure plain-safe pruning that preserves observed extensions"
    )
    guitar_extra_recipe = target_recipe(makefile, "$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT)")
    assert 'EXTRA_COMPONENT_ARGS="$(EXTRA_COMPONENT_ARGS)"' in guitar_extra_recipe, (
        "guitar extra-component report must pass the default pruning simulation arguments"
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
    assert "$(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS)" in print_recipe, (
        "print target must depend on optional real-note dataset row dumps when those archives exist"
    )
    assert "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" in print_recipe, (
        "print target must depend on stale-aware drum primary rows"
    )
    assert "refresh-analyzer-detected-attribute-rows" not in print_recipe, (
        "print target must not use the refresh-only helper because it can report stale detector rows"
    )
    assert "scripts/print_analyzer_detected_attributes.py" in print_recipe, "missing measured row printer"
    assert "$(RUN_WITH_DURATION) analyzer_detected_attributes" in print_recipe, (
        "print target should report duration for comparing detector iterations"
    )
    assert "scripts/run_with_duration.sh" in print_recipe, (
        "print target needs the duration helper dependency"
    )
    assert "$(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS)" in print_recipe, (
        "print target must pass optional real-note dataset sections to the report"
    )
    assert "$(ATTRIBUTE_ROW_REPORT_ARGS)" in print_recipe, "print target needs overridable args"
    assert "$(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)" in print_recipe, (
        "print target needs a dedicated escape hatch for summary/filtered report args"
    )
    assert "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs instrument rows"
    assert "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs real-note rows"
    assert "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" in print_recipe, "print target needs guitar rows"
    assert "drum_primary_miss_attribute_rows.tsv" in print_recipe, "print target needs drum primary rows"
    assert "drum_full_attribute_rows.tsv" in print_recipe, "print target can include protected drum rows"
    assert "analyze-instrument-sample-attributes" not in print_recipe, (
        "print-only target must not regenerate analyzer TSVs"
    )

    cached_print_recipe = target_recipe(makefile, "print-analyzer-detected-attributes-cached")
    assert "$(MEASURE_ANALYZER_ROW_DUMPS)" not in cached_print_recipe, (
        "cached print target must not refresh stale-aware row dumps"
    )
    assert "$(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS)" not in cached_print_recipe, (
        "cached print target must not trigger optional dataset refreshes"
    )
    assert "scripts/print_analyzer_detected_attributes.py" in cached_print_recipe, (
        "cached print target must use the same measured row printer"
    )
    assert "$(RUN_WITH_DURATION) analyzer_detected_attributes_cached" in cached_print_recipe, (
        "cached print target should report its own duration label"
    )
    assert "$(ATTRIBUTE_ROW_REPORT_ARGS)" in cached_print_recipe, (
        "cached print target needs the same overridable args"
    )
    assert "$(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)" in cached_print_recipe, (
        "cached print target needs the same dedicated report args"
    )
    assert "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" in cached_print_recipe, (
        "cached print target needs instrument rows"
    )
    assert "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" in cached_print_recipe, (
        "cached print target needs real-note rows"
    )
    assert "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" in cached_print_recipe, (
        "cached print target needs guitar rows"
    )
    assert "drum_primary_miss_attribute_rows.tsv" in cached_print_recipe, (
        "cached print target needs drum primary rows"
    )
    for text in [
        "IDMT_BASS_LINES_ATTRIBUTE_TSV ?= $(BUILD_DIR)/idmt_bass_lines_attributes.tsv",
        "IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_bass_lines_detected_attribute_rows.tsv",
        "IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_bass_lines_miss_attribute_rows.tsv",
        "IDMT_GUITAR_ATTRIBUTE_TSV ?= $(BUILD_DIR)/idmt_guitar_attributes.tsv",
        "IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_guitar_detected_attribute_rows.tsv",
        "IDMT_GUITAR_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_guitar_miss_attribute_rows.tsv",
        "GUITAR_TECHS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitar_techs_attributes.tsv",
        "GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_detected_attribute_rows.tsv",
        "GUITAR_TECHS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_miss_attribute_rows.tsv",
        "GOOD_SOUNDS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/good_sounds_attributes.tsv",
        "GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_detected_attribute_rows.tsv",
        "GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_miss_attribute_rows.tsv",
        "TINYSOL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/tinysol_attributes.tsv",
        "TINYSOL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/tinysol_detected_attribute_rows.tsv",
        "TINYSOL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/tinysol_miss_attribute_rows.tsv",
        "IOWA_PIANO_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_piano_attributes.tsv",
        "IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_piano_detected_attribute_rows.tsv",
        "IOWA_PIANO_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_piano_miss_attribute_rows.tsv",
        "IOWA_STRINGS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_strings_attributes.tsv",
        "IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_strings_detected_attribute_rows.tsv",
        "IOWA_STRINGS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_strings_miss_attribute_rows.tsv",
        "PHILHARMONIA_ATTRIBUTE_TSV ?= $(BUILD_DIR)/philharmonia_attributes.tsv",
        "PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_detected_attribute_rows.tsv",
        "PHILHARMONIA_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_miss_attribute_rows.tsv",
        "PHILHARMONIA_MIN_SAMPLES ?= 1000",
        "PHILHARMONIA_FULL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/philharmonia_full_attributes.tsv",
        "PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_full_detected_attribute_rows.tsv",
        "PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_full_miss_attribute_rows.tsv",
        "IOWA_ORCHESTRA_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_orchestra_attributes.tsv",
        "IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_detected_attribute_rows.tsv",
        "IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_miss_attribute_rows.tsv",
        "IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_orchestra_full_attributes.tsv",
        "IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_full_detected_attribute_rows.tsv",
        "IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_full_miss_attribute_rows.tsv",
        "VOCALSET_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocalset_attributes.tsv",
        "VOCALSET_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocalset_detected_attribute_rows.tsv",
        "VOCALSET_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocalset_miss_attribute_rows.tsv",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS :=",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS :=",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(TINYSOL_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)",
        "REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)",
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "IDMT bass lines=$(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "IDMT guitar=$(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "GuitarTechs=$(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Good Sounds=$(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "TinySOL=$(TINYSOL_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "VocalSet=$(VOCALSET_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa piano=$(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa strings=$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Philharmonia=$(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Philharmonia full=$(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa orchestra=$(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)"',
        'REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa orchestra full=$(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)"',
    ]:
        assert text in makefile, f"optional real-note attribute plumbing must include {text}"

    vocalset_analyze_recipe = target_recipe(makefile, "analyze-vocalset-attributes")
    assert '$(PYTHON) scripts/summarize_real_note_attributes.py "$(VOCALSET_DETECTED_ATTRIBUTE_ROWS)"' in vocalset_analyze_recipe, (
        "VocalSet attribute analysis should print the same sample-level summary as other real-note diagnostics"
    )

    refresh_recipe = target_recipe(makefile, "refresh-analyzer-detected-attribute-rows")
    assert "scripts/refresh_analyzer_detected_attribute_rows.py" in refresh_recipe, (
        "refresh target must use the refresh helper"
    )
    assert "--build-dir \"$(BUILD_DIR)\"" in refresh_recipe, "refresh helper needs the configured build dir"
    assert "--python \"$(PYTHON)\"" in refresh_recipe, "refresh helper needs the configured Python"
    assert "--jobs \"$(REFRESH_ANALYZER_ATTRIBUTE_JOBS)\"" in refresh_recipe, (
        "refresh helper must derive independent detected-attribute row dumps in parallel"
    )
    assert "REFRESH_ANALYZER_ATTRIBUTE_JOBS ?= $(MEASURE_ANALYZER_JOBS)" in makefile, (
        "refresh helper needs an overridable job count tied to the measurement workflow"
    )
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

    maps_archive_recipe = target_recipe(makefile, "$(MAPS_PIANO_ARCHIVE)")
    assert "$(MAPS_PIANO_ARCHIVE): FORCE" in maps_archive_recipe.splitlines()[0], (
        "MAPS piano archive target must revalidate existing downloads"
    )
    assert 'mv -f "$(MAPS_PIANO_ARCHIVE)" "$(MAPS_PIANO_ARCHIVE).part"' in maps_archive_recipe, (
        "MAPS piano archive target must quarantine corrupt completed zips"
    )
    assert 'zipfile -t "$(MAPS_PIANO_ARCHIVE).part"' in maps_archive_recipe, (
        "MAPS piano archive target must validate partial zips before promotion"
    )
    assert 'curl -fL -C - -o "$(MAPS_PIANO_ARCHIVE).part"' in maps_archive_recipe, (
        "MAPS piano archive target must resume downloads into a partial file"
    )

    medley_archive_recipe = target_recipe(makefile, "$(MEDLEY_SOLOS_ARCHIVE)")
    assert "$(MEDLEY_SOLOS_ARCHIVE): FORCE" in medley_archive_recipe.splitlines()[0], (
        "Medley Solos archive target must revalidate existing downloads"
    )
    assert 'mv -f "$(MEDLEY_SOLOS_ARCHIVE)" "$(MEDLEY_SOLOS_ARCHIVE).part"' in medley_archive_recipe, (
        "Medley Solos archive target must quarantine corrupt completed tarballs"
    )
    assert '$(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part"' in medley_archive_recipe, (
        "Medley Solos archive target must validate partial tarballs before promotion"
    )
    assert 'curl -fL -C - -o "$(MEDLEY_SOLOS_ARCHIVE).part"' in medley_archive_recipe, (
        "Medley Solos archive target must resume downloads into a partial file"
    )

    good_sounds_archive_recipe = target_recipe(makefile, "$(GOOD_SOUNDS_ARCHIVE)")
    assert "GOOD_SOUNDS_DOWNLOAD_CONNECTIONS ?= 8" in makefile, (
        "Good Sounds download parallelism must be configurable"
    )
    assert "$(GOOD_SOUNDS_ARCHIVE): FORCE" in good_sounds_archive_recipe.splitlines()[0], (
        "Good Sounds archive target must revalidate existing downloads"
    )
    assert 'mv -f "$(GOOD_SOUNDS_ARCHIVE)" "$(GOOD_SOUNDS_ARCHIVE).part"' in good_sounds_archive_recipe, (
        "Good Sounds archive target must quarantine corrupt completed zips"
    )
    assert 'zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part"' in good_sounds_archive_recipe, (
        "Good Sounds archive target must validate partial zips before promotion"
    )
    assert 'command -v "$(ARIA2C)"' in good_sounds_archive_recipe, (
        "Good Sounds archive target must use aria2c when available"
    )
    assert '-x "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)"' in good_sounds_archive_recipe, (
        "Good Sounds aria2c download must use the configured connection count"
    )
    assert '-s "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)"' in good_sounds_archive_recipe, (
        "Good Sounds aria2c download must split the transfer across configured connections"
    )
    assert 'curl -fL -C - -o "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_URL)"' in good_sounds_archive_recipe, (
        "Good Sounds archive target must keep a resumable curl fallback"
    )

    vocalset_archive_recipe = target_recipe(makefile, "$(VOCALSET_ARCHIVE)")
    assert "VOCALSET_DOWNLOAD_CONNECTIONS ?= 1" in makefile, (
        "VocalSet download concurrency must remain configurable and range-safe"
    )
    assert 'mv -f "$(VOCALSET_ARCHIVE)" "$(VOCALSET_ARCHIVE).part"' in vocalset_archive_recipe, (
        "VocalSet archive target must quarantine corrupt completed zips"
    )
    assert 'zipfile -t "$(VOCALSET_ARCHIVE).part"' in vocalset_archive_recipe, (
        "VocalSet archive target must validate partial zips before promotion"
    )
    assert "command -v aria2c" in vocalset_archive_recipe, (
        "VocalSet archive target must use aria2c when available"
    )
    assert '--max-connection-per-server="$(VOCALSET_DOWNLOAD_CONNECTIONS)"' in vocalset_archive_recipe, (
        "VocalSet aria2c download must use the configured connection count"
    )
    assert '--split="$(VOCALSET_DOWNLOAD_CONNECTIONS)"' in vocalset_archive_recipe, (
        "VocalSet aria2c download must split the transfer across configured connections"
    )
    assert 'curl -fL -C - -o "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_URL)"' in vocalset_archive_recipe, (
        "VocalSet archive target must keep a resumable curl fallback"
    )

    assert "GUITARSET_ANNOTATION_ARCHIVE ?= $(GUITARSET_SOURCE_DIR)/annotation.zip" in makefile, (
        "downloaded GuitarSet annotation archive must have a named cache path"
    )
    assert "GUITARSET_AUDIO_ARCHIVE ?= $(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip" in makefile, (
        "downloaded GuitarSet audio archive must have a named cache path"
    )
    assert "$(GUITARSET_ANNOTATION_ARCHIVE)" in makefile and "$(GUITARSET_AUDIO_ARCHIVE)" in makefile, (
        "downloaded GuitarSet archives must be referenced through named variables"
    )
    guitarset_download_recipe = target_recipe(makefile, "download-guitarset-samples")
    assert "scripts/run_with_lock.sh" in guitarset_download_recipe.splitlines()[0], (
        "downloaded GuitarSet target must use the shared download lock"
    )
    assert '"$(MAKE)" guitarset-download-samples-unlocked' in guitarset_download_recipe, (
        "downloaded GuitarSet target must delegate archive work through the lock"
    )
    assert re.search(
        r"^guitarset-download-samples-unlocked: .*\$\(GUITARSET_ANNOTATION_ARCHIVE\) \$\(GUITARSET_AUDIO_ARCHIVE\)",
        makefile,
        re.MULTILINE,
    ), (
        "unlocked GuitarSet target must depend on validated archive targets"
    )
    assert 'curl -L -C - -o "$(GUITARSET_SOURCE_DIR)/annotation.zip"' not in makefile, (
        "downloaded GuitarSet target must not write directly to the final annotation archive"
    )
    assert 'curl -L -C - -o "$(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip"' not in makefile, (
        "downloaded GuitarSet target must not write directly to the final audio archive"
    )
    for target, var, url in [
        ("$(GUITARSET_ANNOTATION_ARCHIVE)", "GUITARSET_ANNOTATION_ARCHIVE", "GUITARSET_ANNOTATION_URL"),
        ("$(GUITARSET_AUDIO_ARCHIVE)", "GUITARSET_AUDIO_ARCHIVE", "GUITARSET_AUDIO_URL"),
    ]:
        archive_recipe = target_recipe(makefile, target)
        assert f"{target}: FORCE" in archive_recipe.splitlines()[0], (
            f"{target} must revalidate existing downloads"
        )
        assert f'mv -f "$({var})" "$({var}).part"' in archive_recipe, (
            f"{target} must quarantine corrupt completed zips"
        )
        assert f'scripts/check_zip_archive.py "$({var}).part"' in archive_recipe, (
            f"{target} must validate a complete partial zip before promotion"
        )
        assert f'mv -f "$({var}).part" "$({var}).corrupt"' not in archive_recipe, (
            f"{target} must keep incomplete partial zips so curl can resume them"
        )
        assert f'curl -fL -C - -o "$({var}).part" "$({url})"' in archive_recipe, (
            f"{target} must resume downloads into a partial file"
        )
        assert f'scripts/check_zip_archive.py "$({var})"' in archive_recipe, (
            f"{target} must validate the final zip"
        )
    for target in ["prepare-downloaded-guitarset", "$(GUITARSET_MANIFEST)"]:
        recipe = target_recipe(makefile, target)
        assert 'zipfile -e "$(GUITARSET_ANNOTATION_ARCHIVE)"' in recipe, (
            f"{target} must extract the validated annotation archive"
        )
        assert 'zipfile -e "$(GUITARSET_AUDIO_ARCHIVE)"' in recipe, (
            f"{target} must extract the validated audio archive"
        )

    patterns_full_recipe = target_recipe(makefile, "measure-analyzer-patterns-full")
    assert "measure-analyzer-attribute-rows-full" not in patterns_full_recipe, (
        "full pattern target must not regenerate legacy serial full-drum debug rows"
    )
    assert "analyze-drum-full-gate-matrix-parallel" in patterns_full_recipe, (
        "full pattern target must measure full exact drum rows through the sharded builder"
    )
    assert "analyze-drum-full-merged-expected-attribute-rows" in patterns_full_recipe, (
        "full pattern target must measure merged full drum rows through the sharded builder"
    )
    assert "analyze-drum-tom-bleed-caps-cached" in patterns_full_recipe, (
        "full pattern target must run full drum diagnostics from cached sharded rows"
    )
    assert "$(MAKE) report-analyzer-patterns-from-rows-full" in patterns_full_recipe, (
        "full pattern target must use measured rows without rerunning the bounded target"
    )

    full_report_recipe = target_recipe(makefile, "report-analyzer-patterns-from-rows-full")
    assert '$(MAKE) report-analyzer-patterns-from-rows REPORT_FULL_DRUM_SKIP=0 MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS="$(MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS)"' in full_report_recipe, (
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
    assert "$(MAKE) find-protected-drum-full-exact-attribute-patterns" in full_section_recipes, (
        "full report helper must mine protected full-drum rows with spread, HF, and IDMT guard rows"
    )
    assert "$(MAKE) find-drum-full-exact-attribute-patterns" in full_section_recipes, (
        "full report helper must mine exact full gate rows"
    )
    assert "$(MEASURE_DRUM_FULL_PATTERN_ARGS)" in full_section_recipes, (
        "full drum pattern target needs bounded default args"
    )
    drum_full_args = re.search(
        r"^MEASURE_DRUM_FULL_PATTERN_ARGS \?= (.+)$", makefile, re.MULTILINE
    )
    assert drum_full_args is not None, "missing full drum pattern defaults"
    assert "--profile-fields" in drum_full_args.group(1), (
        "full drum pattern defaults must include route attribute profiles"
    )
    assert "--max-new-active-samples 0" in drum_full_args.group(1), (
        "full drum pattern defaults must reject rules that newly activate protected non-target drums"
    )
    assert "--max-primary-break-samples 0" in drum_full_args.group(1), (
        "full drum pattern defaults must reject rules that break protected primary labels"
    )
    protected_drum_args = re.search(
        r"^MEASURE_PROTECTED_DRUM_PATTERN_ARGS \?= (.+)$", makefile, re.MULTILINE
    )
    assert protected_drum_args is not None, "missing protected drum pattern defaults"
    assert "--max-new-active-samples 0" in protected_drum_args.group(1), (
        "protected drum pattern defaults must reject rules that newly activate protected non-target drums"
    )
    assert "--max-primary-break-samples 0" in protected_drum_args.group(1), (
        "protected drum pattern defaults must reject rules that break protected primary labels"
    )

    shadow_recipe = target_recipe(makefile, "evaluate-real-note-display-shadow")
    assert "scripts/evaluate_real_note_display_shadow.py" in shadow_recipe, (
        "display shadow target must use the dedicated evaluator"
    )
    assert "$(RUN_WITH_DURATION) real_note_display_shadow" in shadow_recipe, (
        "display shadow target should print duration"
    )
    assert '$(or $(DISPLAY_SHADOW_ARGS),--summary-only --jobs "$(DISPLAY_SHADOW_JOBS)")' in shadow_recipe, (
        "display shadow target should default to concise output"
    )
    assert '--jobs "$(DISPLAY_SHADOW_JOBS)"' in shadow_recipe, (
        "display shadow target should pass the configured worker count"
    )
    all_shadow_recipe = target_recipe(makefile, "evaluate-real-note-display-shadow-all")
    assert "$(RUN_WITH_DURATION) real_note_display_shadow_all" in all_shadow_recipe, (
        "all-route display shadow target should print duration"
    )
    assert "--shadow-row all --target-row all --compact-routes --threshold-search" in all_shadow_recipe, (
        "all-route display shadow mining should default to compact threshold summaries"
    )
    assert '--jobs "$(DISPLAY_SHADOW_JOBS)"' in all_shadow_recipe, (
        "all-route display shadow mining should run compact route summaries in parallel"
    )
    vocal_shadow_recipe = target_recipe(makefile, "evaluate-real-note-vocal-shadow-safety")
    assert "$(RUN_WITH_DURATION) real_note_vocal_shadow_safety_parallel" in vocal_shadow_recipe, (
        "vocal shadow safety scan should print duration for the parallel aggregate"
    )
    assert "$(MAKE) $(PARALLEL_TEST_MAKE_JOBS)" in vocal_shadow_recipe, (
        "vocal shadow safety scan should run dataset checks through parallel make jobs"
    )
    assert "evaluate-real-note-vocal-shadow-safety-nsynth" in vocal_shadow_recipe, (
        "vocal shadow safety scan should include the NSynth subtarget"
    )
    assert "evaluate-real-note-vocal-shadow-safety-vocadito" in vocal_shadow_recipe, (
        "vocal shadow safety scan should include the Vocadito subtarget"
    )
    nsynth_vocal_shadow_recipe = target_recipe(makefile, "evaluate-real-note-vocal-shadow-safety-nsynth")
    assert "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" in nsynth_vocal_shadow_recipe, (
        "vocal shadow safety scan should include NSynth full-mix attributes"
    )
    vocadito_vocal_shadow_recipe = target_recipe(makefile, "evaluate-real-note-vocal-shadow-safety-vocadito")
    assert "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" in vocadito_vocal_shadow_recipe, (
        "vocal shadow safety scan should include Vocadito full-mix attributes"
    )
    assert "--shadow-row other --target-row vocals --compact-routes --threshold-search" in nsynth_vocal_shadow_recipe, (
        "NSynth vocal shadow safety scan should focus the risky other-to-vocal route"
    )
    assert "--shadow-row other --target-row vocals --compact-routes --threshold-search" in vocadito_vocal_shadow_recipe, (
        "vocal shadow safety scan should focus the risky other-to-vocal route"
    )
    assert "--max-protected 0 --threshold-limit 4" in nsynth_vocal_shadow_recipe, (
        "NSynth vocal shadow safety scan should report only zero-protected candidate thresholds"
    )
    assert "--max-protected 0 --threshold-limit 4" in vocadito_vocal_shadow_recipe, (
        "vocal shadow safety scan should report only zero-protected candidate thresholds"
    )

    row_confusion_recipe = target_recipe(makefile, "find-real-note-row-confusion-patterns")
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in row_confusion_recipe, (
        "row-confusion mining should default to runtime-observable fields"
    )
    assert "--include-row-context" not in row_confusion_recipe, (
        "row-confusion auto-search must not use display-row fields as candidate rules"
    )
    runtime_octave_recipe = target_recipe(
        makefile, "find-real-note-octave-displacement-runtime-patterns"
    )
    assert "--bucket-status octave_displacement" in runtime_octave_recipe, (
        "runtime octave mining must select the octave-displacement bucket"
    )
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in runtime_octave_recipe, (
        "runtime octave mining must exclude expected-label-derived attributes"
    )
    assert "--include-row-context" not in runtime_octave_recipe, (
        "runtime octave mining must not reintroduce label-derived row context"
    )
    ownership_recipe = target_recipe(makefile, "find-real-note-ownership-patterns")
    assert "--bucket-status ownership_miss" in ownership_recipe, (
        "real-note ownership mining must select the ownership miss bucket"
    )
    assert "$(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES)" in ownership_recipe, (
        "real-note ownership mining should default to runtime-observable fields"
    )
    assert "$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS)" in ownership_recipe, (
        "real-note ownership mining needs ownership-sized default thresholds"
    )
    ownership_report_recipe = target_recipe(
        makefile, "$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OWNERSHIP_REPORT)"
    )
    assert "$(MAKE) find-real-note-ownership-patterns" in ownership_report_recipe, (
        "pattern report sections must include real-note ownership mining"
    )
    assert "$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS)" in ownership_report_recipe, (
        "real-note ownership report should use ownership-sized default thresholds"
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
        "--protected-scope all",
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
    assert "REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS ?=" in makefile, (
        "real-note pattern mining must keep optional protected TSV inputs default-empty for ad hoc reports"
    )
    assert 'REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")' in makefile, (
        "real-note protected TSV inputs must be converted into repeatable pattern-miner arguments"
    )
    assert "REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS ?=" in makefile, (
        "real-note pattern mining must keep optional candidate TSV inputs default-empty for ad hoc reports"
    )
    assert 'REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS = $(foreach path,$(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS),--extra-candidate-path "$(path)")' in makefile, (
        "real-note candidate TSV inputs must be converted into repeatable pattern-miner arguments"
    )
    for text in [
        "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)",
        "DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS ?= $(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS)",
    ]:
        assert text in makefile, f"detector route candidate-set defaults must include {text}"
    for text in [
        "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS := $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)",
        "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)",
        "DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)",
        "DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS ?= $(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS)",
    ]:
        assert text in makefile, f"detector route protected-set defaults must include {text}"
    for target in [
        "find-real-note-attribute-patterns",
        "find-real-note-row-confusion-patterns",
        "find-real-note-practical-row-confusion-patterns",
        "find-real-note-focused-row-confusion-patterns",
        "find-real-note-visual-row-confusion-patterns",
        "find-real-note-focused-visual-row-confusion-patterns",
        "find-real-note-ownership-patterns",
        "find-real-note-octave-displacement-patterns",
        "find-real-note-weak-expected-patterns",
        "find-real-note-weak-visual-expected-patterns",
    ]:
        real_note_pattern_recipe = target_recipe(makefile, target)
        assert "$(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS)" in real_note_pattern_recipe.splitlines()[0], (
            f"{target} must wait for optional candidate TSV inputs"
        )
        assert "$(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS)" in real_note_pattern_recipe.splitlines()[0], (
            f"{target} must wait for optional protected TSV inputs"
        )
        assert "$(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS)" in real_note_pattern_recipe, (
            f"{target} must pass optional candidate TSV inputs to the pattern miner"
        )
        assert "$(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS)" in real_note_pattern_recipe, (
            f"{target} must pass optional protected TSV inputs to the pattern miner"
        )
    for text in [
        "MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8",
        "--protected-scope all",
        "--include-row-context",
    ]:
        assert text in makefile, f"focused visual row-confusion defaults must include {text}"
    assert ".PHONY: find-real-note-row-confusion-patterns find-real-note-practical-row-confusion-patterns find-real-note-focused-row-confusion-patterns find-real-note-coverage-row-confusion-patterns find-real-note-visual-row-confusion-patterns find-real-note-focused-visual-row-confusion-patterns find-real-note-coverage-visual-row-confusion-patterns find-real-note-ownership-patterns find-real-note-octave-displacement-patterns" in makefile, (
        "all real-note pattern shortcuts should be phony"
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
        "INSTRUMENT_PATTERN_JOBS",
        "MEASURE_REAL_NOTE_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS",
        "MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS",
        "REAL_NOTE_RULE_CONDITIONS",
        "REAL_NOTE_RULE_GROUP_BY",
        "REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES",
        "DISPLAY_SHADOW_JOBS",
        "MEASURE_GUITAR_PATTERN_ARGS",
        "MEASURE_GUITAR_ROUTE_PATTERN_ARGS",
        "MEASURE_DRUM_PATTERN_ARGS",
        "MEASURE_DRUM_FULL_PATTERN_ARGS",
        "MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS",
        "MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS",
        "DRUM_PATTERN_JOBS",
        "REAL_NOTE_PATTERN_JOBS",
        "DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS",
        "DRUM_FULL_EXACT_ATTRIBUTE_ROWS",
        "DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS",
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
