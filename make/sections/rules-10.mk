.PHONY: locate-urmp-fixture
locate-urmp-fixture:
	python3 scripts/locate_urmp_fixture.py

.PHONY: inspect-quiet-monophonic-visual-test
inspect-quiet-monophonic-visual-test:
	python3 scripts/inspect_quiet_monophonic_visual_test.py

.PHONY: inspect-detector-improvement-routes-target
inspect-detector-improvement-routes-target:
	python3 scripts/inspect_detector_improvement_routes_target.py
.PHONY: inspect-makefile-text
inspect-makefile-text: scripts/inspect_makefile_text.py
	@$(PYTHON) scripts/inspect_makefile_text.py

.PHONY: inspect-hihat-suppression-path
inspect-hihat-suppression-path: scripts/inspect_hihat_suppression_path.py
	@$(PYTHON) scripts/inspect_hihat_suppression_path.py

.PHONY: inspect-hihat-caps
inspect-hihat-caps: scripts/inspect_hihat_caps.py
	@$(PYTHON) scripts/inspect_hihat_caps.py

.PHONY: inspect-hihat-initial-classification
inspect-hihat-initial-classification: scripts/inspect_hihat_initial_classification.py
	@$(PYTHON) scripts/inspect_hihat_initial_classification.py

.PHONY: inspect-makefile-drum-targets
inspect-makefile-drum-targets: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source Makefile --topic "analyzer_drum_samples"

.PHONY: inspect-makefile-test-drum-targets
inspect-makefile-test-drum-targets: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source Makefile --topic "test-drum-samples"

.PHONY: report-real-drum-test-status
report-real-drum-test-status: scripts/report_real_drum_test_status.py
	@$(PYTHON) scripts/report_real_drum_test_status.py

.PHONY: inspect-egmd-drum-debug-output
inspect-egmd-drum-debug-output: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source tests/analyzer_egmd.cpp --topic "drum_debug_rule_flags"

.PHONY: report-dense-hihat-recovery
report-dense-hihat-recovery: scripts/report_dense_hihat_recovery.py
	@$(PYTHON) scripts/report_dense_hihat_recovery.py

.PHONY: measure-mdb-dense-hihat-recovery
measure-mdb-dense-hihat-recovery: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/run_with_duration.sh scripts/report_dense_hihat_recovery.py
	$(RUN_WITH_DURATION) analyzer_mdb_dense_hihat_recovery env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="80" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_ALL=1 $(BUILD_DIR)/analyzer_egmd > "$(BUILD_DIR)/mdb_dense_hihat_recovery.out" 2> "$(BUILD_DIR)/mdb_dense_hihat_recovery.log"
	@$(PYTHON) scripts/report_dense_hihat_recovery.py

.PHONY: inspect-hihat-test-diagnostics
inspect-hihat-test-diagnostics: scripts/inspect_hihat_test_diagnostics.py
	@$(PYTHON) scripts/inspect_hihat_test_diagnostics.py
.PHONY: inspect-real-note-harness
inspect-real-note-harness:
	python3 scripts/inspect_real_note_harness.py
.PHONY: analyze-real-note-ownership
analyze-real-note-ownership: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_ownership.py

.PHONY: report-real-note-ownership
report-real-note-ownership:
	python3 scripts/analyze_real_note_ownership.py --report

.PHONY: report-real-note-shard-errors
report-real-note-shard-errors:
	python3 scripts/analyze_real_note_ownership.py --shard-errors
.PHONY: debug-real-note-sample
debug-real-note-sample: build/analyzer_real_note_samples
	python3 scripts/debug_real_note_sample.py

.PHONY: debug-real-note-guitar-reference
debug-real-note-guitar-reference: build/analyzer_real_note_samples
	python3 scripts/debug_real_note_sample.py guitar_acoustic_010-046-025
.PHONY: inspect-full-mix-arbitration
inspect-full-mix-arbitration:
	python3 scripts/inspect_full_mix_arbitration.py
.PHONY: analyze-real-note-guitar-ownership
analyze-real-note-guitar-ownership: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_guitar_ownership.py
.PHONY: analyze-real-note-guitar-misses
analyze-real-note-guitar-misses: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_guitar_misses.py
.PHONY: test-real-note-guitar-full-mix-recall
test-real-note-guitar-full-mix-recall: analyze-real-note-guitar-misses
	python3 scripts/check_real_note_guitar_full_mix_recall.py
.PHONY: report-real-note-guitar-misses
report-real-note-guitar-misses:
	python3 scripts/analyze_real_note_guitar_misses.py --report
.PHONY: analyze-real-note-piano-guitar-routes
analyze-real-note-piano-guitar-routes: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_piano_guitar_routes.py
.PHONY: inspect-full-mix-guitar-row
inspect-full-mix-guitar-row:
	python3 scripts/inspect_full_mix_guitar_row.py
analyze-real-note-low-guitar-shapes:
	python3 scripts/analyze_real_note_low_guitar_shapes.py
report-low-guitar-shape-separation:
	python3 scripts/report_low_guitar_shape_separation.py
test-real-note-low-electronic-piano-guitar-shadow: build/analyzer_real_note_samples
	python3 scripts/check_real_note_low_electronic_piano_guitar_shadow.py
inspect-full-mix-ownership-classifier:
	python3 scripts/inspect_full_mix_ownership_classifier.py
report-piano-guitar-owner-aliases:
	python3 scripts/report_piano_guitar_owner_aliases.py
report-same-pitch-guitar-owner-separation:
	python3 scripts/report_same_pitch_guitar_owner_separation.py
list-fixture-import-tools:
	python3 scripts/list_fixture_import_tools.py
report-real-audio-fixture-coverage:
	python3 scripts/summarize_real_audio_fixture_coverage.py
report-guitarset-miss-process:
	python3 scripts/report_guitarset_miss_process.py
inspect-guitarset-chord-selection:
	python3 scripts/inspect_guitarset_chord_selection.py
guitarset-debug-windows: build/analyzer_guitarset
	python3 scripts/run_guitarset_debug_windows.py
report-guitarset-major-minor-debug:
	python3 scripts/report_guitarset_major_minor_debug.py

.PHONY: check-fret-zealot-auto-recovery
check-fret-zealot-auto-recovery:
	python3 scripts/check_fret_zealot_auto_recovery.py
.PHONY: stop-low-electronic-piano-guitar-shadow
stop-low-electronic-piano-guitar-shadow:
	python3 scripts/stop_low_electronic_piano_guitar_shadow.py
.PHONY: inspect-real-note-vocal-routes
inspect-real-note-vocal-routes:
	python3 scripts/inspect_real_note_vocal_routes.py
.PHONY: inspect-full-mix-vocal-scoring
inspect-full-mix-vocal-scoring:
	python3 scripts/inspect_full_mix_vocal_scoring.py
.PHONY: inspect-vocal-display-weight
inspect-vocal-display-weight:
	python3 scripts/inspect_vocal_display_weight.py
.PHONY: inspect-full-mix-debug-candidate
inspect-full-mix-debug-candidate:
	python3 scripts/inspect_full_mix_debug_candidate.py
.PHONY: inspect-real-note-debug-output
inspect-real-note-debug-output:
	python3 scripts/inspect_real_note_debug_output.py
.PHONY: collect-real-note-vocal-attributes
collect-real-note-vocal-attributes: build/analyzer_real_note_samples
	python3 scripts/collect_real_note_vocal_attributes.py
.PHONY: inspect-full-mix-vocal-profile
inspect-full-mix-vocal-profile:
	python3 scripts/inspect_full_mix_vocal_profile.py
.PHONY: inspect-vocal-row-population
inspect-vocal-row-population:
	python3 scripts/inspect_vocal_row_population.py
.PHONY: status-guitar-chord-primary-collection
status-guitar-chord-primary-collection:
	python3 scripts/status_guitar_chord_primary_collection.py
.PHONY: find-high-soprano-vocal-mirror-flag
find-high-soprano-vocal-mirror-flag:
	python3 scripts/find_high_soprano_vocal_mirror_flag.py
.PHONY: status-real-note-full-mix
status-real-note-full-mix:
	python3 scripts/status_real_note_full_mix.py
.PHONY: plan-mir1k-vocal-fixtures
plan-mir1k-vocal-fixtures:
	python3 scripts/plan_mir1k_vocal_fixtures.py
.PHONY: import-mir1k-vocal-archive
import-mir1k-vocal-archive:
	python3 scripts/import_mir1k_vocal_archive.py
.PHONY: status-mir1k-vocal-import
status-mir1k-vocal-import:
	python3 scripts/status_mir1k_vocal_import.py
.PHONY: inspect-mir1k-vocal-layout
inspect-mir1k-vocal-layout:
	python3 scripts/inspect_mir1k_vocal_layout.py

.PHONY: inspect-mir1k-vocal-pitch-labels
inspect-mir1k-vocal-pitch-labels:
	python3 scripts/inspect_mir1k_vocal_pitch_labels.py

.PHONY: inspect-real-note-sample-test-contract
inspect-real-note-sample-test-contract:
	python3 scripts/inspect_real_note_sample_test_contract.py

.PHONY: prepare-mir1k-vocal-fixtures
prepare-mir1k-vocal-fixtures:
	python3 scripts/prepare_mir1k_vocal_fixtures.py

.PHONY: test-mir1k-clean-vocal-fixtures
test-mir1k-clean-vocal-fixtures:
	python3 scripts/run_mir1k_vocal_fixture_test.py

.PHONY: test-mir1k-clean-vocal-fixtures-full-mix
test-mir1k-clean-vocal-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix

.PHONY: test-mir1k-vocal-mix-fixtures-full-mix
test-mir1k-vocal-mix-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --mixed-fixtures

.PHONY: measure-mir1k-vocal-mix-fixtures-full-mix
measure-mir1k-vocal-mix-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --mixed-fixtures --measure-only

.PHONY: probe-mir1k-vocal-linear-separation
probe-mir1k-vocal-linear-separation:
	python3 scripts/probe_mir1k_vocal_linear_separation.py

.PHONY: inspect-full-mix-ownership-application
inspect-full-mix-ownership-application:
	python3 scripts/inspect_full_mix_ownership_application.py

.PHONY: probe-mir1k-vocal-tree-separation
probe-mir1k-vocal-tree-separation:
	python3 scripts/probe_mir1k_vocal_tree_separation.py

.PHONY: stage-mir1k-vocal-fixture-commit
stage-mir1k-vocal-fixture-commit:
	python3 scripts/stage_mir1k_vocal_fixture_commit.py

.PHONY: commit-push-mir1k-vocal-fixture
commit-push-mir1k-vocal-fixture:
	python3 scripts/commit_push_mir1k_vocal_fixture.py

.PHONY: inspect-runtime-model-assets
inspect-runtime-model-assets:
	python3 scripts/inspect_runtime_model_assets.py

.PHONY: inspect-basic-pitch-vocal-fusion-contract
inspect-basic-pitch-vocal-fusion-contract:
	python3 scripts/inspect_basic_pitch_vocal_fusion_contract.py

.PHONY: status-guitarset-miss-analysis
status-guitarset-miss-analysis:
	python3 scripts/status_guitarset_miss_analysis.py

.PHONY: summarize-latest-guitarset-miss-run
summarize-latest-guitarset-miss-run:
	python3 scripts/summarize_latest_guitarset_miss_run.py

.PHONY: inspect-guitarset-basic-pitch-usage
inspect-guitarset-basic-pitch-usage:
	python3 scripts/inspect_guitarset_basic_pitch_usage.py

.PHONY: summarize-current-real-audio-fixture-coverage
summarize-current-real-audio-fixture-coverage:
	python3 scripts/summarize_current_real_audio_fixture_coverage.py

.PHONY: plan-idmt-bass-import
plan-idmt-bass-import:
	python3 scripts/plan_idmt_bass_import.py

.PHONY: import-idmt-bass-archive
import-idmt-bass-archive:
	python3 scripts/import_idmt_bass_archive.py

.PHONY: inspect-idmt-bass-layout
inspect-idmt-bass-layout:
	python3 scripts/inspect_idmt_bass_layout.py

.PHONY: status-idmt-bass-import
status-idmt-bass-import:
	python3 scripts/status_idmt_bass_import.py

.PHONY: stop-idmt-bass-import
stop-idmt-bass-import:
	python3 scripts/stop_idmt_bass_import.py

.PHONY: import-idmt-bass-single-track-archive
import-idmt-bass-single-track-archive:
	python3 scripts/import_idmt_bass_single_track_archive.py

.PHONY: inspect-idmt-bass-single-track-layout
inspect-idmt-bass-single-track-layout:
	python3 scripts/inspect_idmt_bass_single_track_layout.py

.PHONY: collect-mir1k-clean-vocal-attributes
collect-mir1k-clean-vocal-attributes:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --attributes

.PHONY: summarize-mir1k-clean-vocal-attributes
summarize-mir1k-clean-vocal-attributes:
	python3 scripts/summarize_mir1k_vocal_attributes.py

.PHONY: inspect-full-mix-owner-scoring
inspect-full-mix-owner-scoring:
	python3 scripts/inspect_full_mix_owner_scoring.py

.PHONY: collect-real-note-full-mix-attributes
collect-real-note-full-mix-attributes:
	python3 scripts/collect_real_note_full_mix_attributes.py

.PHONY: summarize-real-note-full-mix-attributes
summarize-real-note-full-mix-attributes:
	python3 scripts/summarize_real_note_full_mix_attributes.py

.PHONY: status-real-note-full-mix-attribute-collection
status-real-note-full-mix-attribute-collection:
	python3 scripts/status_real_note_full_mix_attribute_collection.py

.PHONY: compare-mir1k-vocal-feature-distributions
compare-mir1k-vocal-feature-distributions:
	python3 scripts/compare_mir1k_vocal_feature_distributions.py

.PHONY: evaluate-mir1k-vocal-recovery-rules
evaluate-mir1k-vocal-recovery-rules:
	python3 scripts/evaluate_mir1k_vocal_recovery_rules.py

.PHONY: plan-mir1k-vocal-test-fixtures
inspect-mir1k-vocal-fixture-pipeline:
	python3 scripts/inspect_mir1k_vocal_fixture_pipeline.py

.PHONY: inspect-mir1k-vocal-fixture-pipeline
plan-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py plan

.PHONY: apply-mir1k-vocal-test-fixtures
apply-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py apply

.PHONY: test-mir1k-vocal-full-mix
test-mir1k-vocal-full-mix: $(BUILD_DIR)/analyzer_real_note_samples tests/fixtures/mir1k_clean_vocals/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mir1k_vocal_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=221 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="tests/fixtures/mir1k_clean_vocals" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=221 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=70 $(BUILD_DIR)/analyzer_real_note_samples
.PHONY: stage-mir1k-vocal-fixture-gate
stage-mir1k-vocal-fixture-gate: scripts/stage_mir1k_vocal_fixture_gate.py
	python3 scripts/stage_mir1k_vocal_fixture_gate.py
.PHONY: commit-mir1k-vocal-fixture-gate
commit-mir1k-vocal-fixture-gate: scripts/commit_mir1k_vocal_fixture_gate.py
	python3 scripts/commit_mir1k_vocal_fixture_gate.py

MIR1K_VOCAL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/mir1k_vocal_full_mix_attributes.tsv
.PHONY: collect-mir1k-vocal-full-mix-attributes
collect-mir1k-vocal-full-mix-attributes: $(BUILD_DIR)/analyzer_real_note_samples tests/fixtures/mir1k_clean_vocals/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mir1k_vocal_full_mix_attributes env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=221 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="tests/fixtures/mir1k_clean_vocals" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=221 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(MIR1K_VOCAL_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	@printf '%s\n' "attribute TSV: $(MIR1K_VOCAL_ATTRIBUTE_TSV)"

.PHONY: summarize-mir1k-vocal-ownership
summarize-mir1k-vocal-ownership: $(MIR1K_VOCAL_ATTRIBUTE_TSV) build/real_note_full_mix_attributes.tsv scripts/summarize_mir1k_vocal_ownership.py
	python3 scripts/summarize_mir1k_vocal_ownership.py

.PHONY: plan-clean-mir1k-vocal-test-fixture-stale
plan-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py plan

.PHONY: apply-clean-mir1k-vocal-test-fixture-stale
apply-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py apply

.PHONY: status-detection-data-worktree
status-detection-data-worktree:
	python3 scripts/status_detection_data_worktree.py

.PHONY: show-mir1k-makefile-blocks
show-mir1k-makefile-blocks:
	python3 scripts/show_mir1k_makefile_blocks.py
.PHONY: inspect-fret-zealot-scale-path
inspect-fret-zealot-scale-path:
	@python3 scripts/inspect_fret_zealot_scale_path.py

.PHONY: inspect-fret-zealot-controller
inspect-fret-zealot-controller:
	@python3 scripts/inspect_fret_zealot_controller.py

.PHONY: inspect-fret-zealot-callers
inspect-fret-zealot-callers:
	@python3 scripts/inspect_fret_zealot_callers.py

.PHONY: test-fret-zealot-frame-settle
test-fret-zealot-frame-settle:
	@python3 tests/check_fret_zealot_frame_settle.py

.PHONY: show-fret-zealot-worktree-diff
show-fret-zealot-worktree-diff:
	@python3 scripts/show_fret_zealot_worktree_diff.py

.PHONY: check-idmt-bass-single-track-setup
check-idmt-bass-single-track-setup:
	@python3 scripts/check_idmt_bass_single_track_setup.py

.PHONY: inspect-idmt-bass-single-track-importer
inspect-idmt-bass-single-track-importer:
	@python3 scripts/inspect_idmt_bass_single_track_importer.py

.PHONY: diagnose-idmt-bass-single-track-archive
diagnose-idmt-bass-single-track-archive:
	@python3 scripts/diagnose_idmt_bass_single_track_archive.py

.PHONY: status-idmt-bass-single-track-import
status-idmt-bass-single-track-import:
	@python3 scripts/status_idmt_bass_single_track_import.py

.PHONY: summarize-idmt-bass-single-track-annotations
summarize-idmt-bass-single-track-annotations:
	@python3 scripts/summarize_idmt_bass_single_track_annotations.py

.PHONY: inspect-real-note-fixture-pipeline
inspect-real-note-fixture-pipeline:
	@python3 scripts/inspect_real_note_fixture_pipeline.py

.PHONY: prepare-idmt-bass-single-track-fixture test-prepare-idmt-bass-single-track-fixture measure-idmt-bass-single-track test-idmt-bass-single-track
prepare-idmt-bass-single-track-fixture: import-idmt-bass-single-track-archive
	@python3 scripts/prepare_idmt_bass_single_track_fixture.py

test-prepare-idmt-bass-single-track-fixture: prepare-idmt-bass-single-track-fixture
	@python3 tests/test_prepare_idmt_bass_single_track_fixture.py

measure-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py

test-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --min-recall 95

.PHONY: status-idmt-bass-single-track-measurement
status-idmt-bass-single-track-measurement:
	@python3 scripts/status_idmt_bass_single_track_measurement.py

.PHONY: summarize-idmt-bass-single-track-measurement
summarize-idmt-bass-single-track-measurement:
	@python3 scripts/summarize_idmt_bass_single_track_measurement.py

.PHONY: inspect-bass-tuning-detector
inspect-bass-tuning-detector:
	@python3 scripts/inspect_bass_tuning_detector.py

IDMT_BASS_SAMPLE_ID ?= idmt_bass_005_056
.PHONY: inspect-idmt-bass-sample-attributes
inspect-idmt-bass-sample-attributes:
	@python3 scripts/inspect_idmt_bass_sample_attributes.py --sample-id "$(IDMT_BASS_SAMPLE_ID)"

.PHONY: inspect-idmt-bass-high-register-attributes
inspect-idmt-bass-high-register-attributes:
	@python3 scripts/inspect_idmt_bass_sample_attributes.py --sample-id idmt_bass_017_004

.PHONY: debug-idmt-bass-single-track-sample
debug-idmt-bass-single-track-sample: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --debug-sample "$(IDMT_BASS_SAMPLE_ID)"

.PHONY: debug-idmt-bass-high-register-sample
debug-idmt-bass-high-register-sample: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --debug-sample idmt_bass_017_004

.PHONY: inspect-idmt-bass-recording-017
inspect-idmt-bass-recording-017:
	@python3 scripts/inspect_idmt_bass_recording_017.py

.PHONY: stage-idmt-bass-single-track-fixture show-staged-idmt-bass-single-track-fixture commit-and-push-idmt-bass-single-track-fixture
stage-idmt-bass-single-track-fixture:
	@python3 scripts/stage_idmt_bass_single_track_fixture.py

show-staged-idmt-bass-single-track-fixture:
	@python3 scripts/show_staged_idmt_bass_single_track_fixture.py

commit-and-push-idmt-bass-single-track-fixture:
	@python3 scripts/commit_and_push_idmt_bass_single_track_fixture.py

.PHONY: inspect-bass-note-path
inspect-bass-note-path:
	@python3 scripts/inspect_bass_note_path.py
.PHONY: status-real-note-sample-test
status-real-note-sample-test:
	@python3 scripts/status_real_note_sample_test.py

.PHONY: inspect-real-note-sample-test
inspect-real-note-sample-test:
	@python3 scripts/inspect_real_note_sample_test.py

.PHONY: summarize-real-note-sample-shards
summarize-real-note-sample-shards:
	@python3 scripts/summarize_real_note_sample_shards.py

.PHONY: inspect-real-note-shard-output
inspect-real-note-shard-output:
	@python3 scripts/inspect_real_note_shard_output.py

.PHONY: inspect-bass-natural-harmonic-path
inspect-bass-natural-harmonic-path:
	@python3 scripts/inspect_bass_natural_harmonic_path.py

.PHONY: inspect-idmt-bass-debug-target
inspect-idmt-bass-debug-target:
	@python3 scripts/inspect_idmt_bass_debug_target.py

.PHONY: status-idmt-bass-debug
status-idmt-bass-debug:
	@python3 scripts/status_idmt_bass_debug.py

.PHONY: plan-clean-idmt-bass-single-track-fixture-tmp clean-idmt-bass-single-track-fixture-tmp
plan-clean-idmt-bass-single-track-fixture-tmp:
	@python3 scripts/clean_idmt_bass_single_track_fixture_tmp.py plan

clean-idmt-bass-single-track-fixture-tmp:
	@python3 scripts/clean_idmt_bass_single_track_fixture_tmp.py apply

.PHONY: inspect-fret-zealot-settle-change
inspect-fret-zealot-settle-change:
	@python3 scripts/inspect_fret_zealot_settle_change.py

.PHONY: inspect-fret-zealot-auto-scheduler
inspect-fret-zealot-auto-scheduler:
	@python3 scripts/inspect_fret_zealot_auto_scheduler.py

.PHONY: test-fret-zealot-initial-auto-scale
test-fret-zealot-initial-auto-scale: tests/test_fret_zealot_initial_auto_scale.py
	@python3 tests/test_fret_zealot_initial_auto_scale.py

.PHONY: evaluate-guitarset-extension-promotion
evaluate-guitarset-extension-promotion: scripts/evaluate_guitarset_extension_promotion.py
	@python3 scripts/evaluate_guitarset_extension_promotion.py

.PHONY: inspect-chord-label-parsers
inspect-chord-label-parsers: scripts/inspect_chord_label_parsers.py
	@python3 scripts/inspect_chord_label_parsers.py

.PHONY: inspect-guitar-same-root-alias-guard
inspect-guitar-same-root-alias-guard: scripts/inspect_guitar_same_root_alias_guard.py
	@python3 scripts/inspect_guitar_same_root_alias_guard.py

NSYNTH_SPLIT ?= test
.PHONY: plan-nsynth-acoustic-bass-fixture prepare-nsynth-acoustic-bass-fixture quarantine-nsynth-acoustic-bass-fixture plan-nsynth-acoustic-bass-valid-fixture prepare-nsynth-acoustic-bass-valid-fixture quarantine-nsynth-acoustic-bass-valid-fixture plan-nsynth-acoustic-bass-train-fixture prepare-nsynth-acoustic-bass-train-fixture
plan-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

quarantine-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py quarantine

plan-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

quarantine-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py quarantine

plan-nsynth-acoustic-bass-train-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="train" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-train-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="train" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

.PHONY: inspect-nsynth-acoustic-bass-importer
inspect-nsynth-acoustic-bass-importer: scripts/inspect_nsynth_fixture_importer.py
	@python3 scripts/inspect_nsynth_fixture_importer.py

.PHONY: probe-nsynth-acoustic-bass-valid-range
probe-nsynth-acoustic-bass-valid-range: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py probe

.PHONY: plan-stage-fret-zealot-frame-settle stage-fret-zealot-frame-settle
plan-stage-fret-zealot-frame-settle:
	@python3 scripts/stage_fret_zealot_frame_settle.py plan

stage-fret-zealot-frame-settle:
	@python3 scripts/stage_fret_zealot_frame_settle.py apply

.PHONY: commit-fret-zealot-frame-settle
commit-fret-zealot-frame-settle:
	@python3 scripts/commit_fret_zealot_frame_settle.py

.PHONY: evaluate-ambiguous-display-recovery
evaluate-ambiguous-display-recovery:
	@python3 scripts/evaluate_ambiguous_display_recovery.py

.PHONY: inspect-full-mix-display-mirror-support
inspect-full-mix-display-mirror-support:
	@python3 scripts/inspect_full_mix_display_mirror_support.py

.PHONY: inspect-shared-note-cases
inspect-shared-note-cases:
	@python3 scripts/inspect_shared_note_cases.py

.PHONY: check-real-note-guitar-full-mix-recall
check-real-note-guitar-full-mix-recall:
	@python3 scripts/check_real_note_guitar_full_mix_recall.py

.PHONY: test-ambiguous-display-recovery
test-ambiguous-display-recovery: analyze-real-note-attributes tests/test_ambiguous_display_recovery.py
	@python3 tests/test_ambiguous_display_recovery.py

.PHONY: test-high-soprano-vocal-mirror
test-high-soprano-vocal-mirror: tests/test_high_soprano_vocal_mirror.py
	$(PYTHON) tests/test_high_soprano_vocal_mirror.py

.PHONY: inspect-high-soprano-vocal-mirror-change
inspect-high-soprano-vocal-mirror-change: scripts/inspect_high_soprano_vocal_mirror_change.py
	$(PYTHON) scripts/inspect_high_soprano_vocal_mirror_change.py

.PHONY: summarize-high-soprano-vocal-mirror-result
summarize-high-soprano-vocal-mirror-result: scripts/summarize_high_soprano_mirror_result.py
	$(PYTHON) scripts/summarize_high_soprano_mirror_result.py
.PHONY: stage-high-soprano-vocal-mirror
stage-high-soprano-vocal-mirror: scripts/stage_high_soprano_vocal_mirror.py
	$(PYTHON) scripts/stage_high_soprano_vocal_mirror.py
.PHONY: commit-high-soprano-vocal-mirror
commit-high-soprano-vocal-mirror: scripts/commit_high_soprano_vocal_mirror.py
	$(PYTHON) scripts/commit_high_soprano_vocal_mirror.py

.PHONY: plan-stage-ambiguous-display-recovery stage-ambiguous-display-recovery commit-ambiguous-display-recovery
plan-stage-ambiguous-display-recovery:
	@python3 scripts/stage_ambiguous_display_recovery.py plan

stage-ambiguous-display-recovery:
	@python3 scripts/stage_ambiguous_display_recovery.py apply

commit-ambiguous-display-recovery:
	@python3 scripts/commit_ambiguous_display_recovery.py
plan-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py plan

stage-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py stage

unstage-code-baseline-commit:
	python3 scripts/unstage_code_baseline_commit.py

commit-code-baseline:
	python3 scripts/manage_code_baseline_commit.py commit

verify-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py verify

push-code-baseline:
	python3 scripts/manage_code_baseline_commit.py push

report-instrument-sample-storage:
	python3 scripts/report_instrument_sample_storage.py

plan-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py plan --store "$(INSTRUMENT_SAMPLE_STORE)"

prepare-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py apply --store "$(INSTRUMENT_SAMPLE_STORE)"

verify-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py verify --store "$(INSTRUMENT_SAMPLE_STORE)"

analyze-sneakybass-fixture: build/analyzer_instrument_samples verify-sneakybass-fixture
	$(PYTHON) scripts/run_sneakybass_fixture_audit.py --binary "$(BUILD_DIR)/analyzer_instrument_samples" --fixture-root "$(INSTRUMENT_SAMPLE_STORE)/real-fixtures/sneakybass" --log "$(BUILD_DIR)/sneakybass_fixture_audit.log" --attributes "$(BUILD_DIR)/sneakybass_fixture_attributes.tsv" --jobs "$(PARALLEL_TEST_JOBS)" --source-name "$(SNEAKYBASS_SOURCE_NAME)"

analyze-sneakybass-fixture-regular-bass: build/analyzer_instrument_samples verify-sneakybass-fixture
	$(PYTHON) scripts/run_sneakybass_fixture_audit.py --binary "$(BUILD_DIR)/analyzer_instrument_samples" --fixture-root "$(INSTRUMENT_SAMPLE_STORE)/real-fixtures/sneakybass" --log "$(BUILD_DIR)/sneakybass_fixture_regular_bass_audit.log" --attributes "$(BUILD_DIR)/sneakybass_fixture_regular_bass_attributes.tsv" --jobs "$(PARALLEL_TEST_JOBS)" --source-name "bass"

report-sneakybass-fixture-audit:
	$(PYTHON) scripts/report_sneakybass_fixture_audit.py --log "$(BUILD_DIR)/sneakybass_fixture_audit.log"

report-sneakybass-fixture-attributes:
	$(PYTHON) scripts/report_sneakybass_fixture_attributes.py --attributes "$(BUILD_DIR)/sneakybass_fixture_attributes.tsv"
commit-real-bass-fixture-audit:
	python3 scripts/commit_staged_source_changes.py --message "test: add external real bass fixture audit"
SNEAKYBASS_SOURCE_NAME ?= double bass
test-instrument-vocal-voice-oohs-g3: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="vocals" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="voice_oohs" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="G3" build/analyzer_instrument_samples

analyze-instrument-vocal-voice-oohs-g3: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="vocals" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="voice_oohs" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="G3" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$(BUILD_DIR)/voice_oohs_g3_attributes.tsv" build/analyzer_instrument_samples

report-instrument-vocal-voice-oohs-g3:
	$(PYTHON) scripts/report_voice_oohs_g3_attributes.py --attributes "$(BUILD_DIR)/voice_oohs_g3_attributes.tsv"
commit-vocal-source-hint-recovery:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover low vocals from keyboard ownership"

commit-synthetic-overtone-pruning:
	python3 scripts/commit_staged_source_changes.py --message "fix: prefer synthetic note fundamentals over overtones"

commit-synthetic-c5-fundamentals:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover high synthetic fundamentals from subharmonics"

commit-generated-gm-hihat-recovery:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover generated GM hi-hat tails"

commit-real-bass-tracking-diagnostics:
	python3 scripts/commit_staged_source_changes.py --message "test: add external bass tracking diagnostics"

commit-fixture-source-inventory:
	python3 scripts/commit_staged_source_changes.py --message "test: inventory external fixture sources"

inspect-drum-fixture-harness:
	python3 scripts/inspect_drum_fixture_harness.py

test-drum-kit-hihat: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="hihat" build/analyzer_instrument_samples

analyze-drum-kit-hihat: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="hihat" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="build/drum_hihat_attributes.tsv" build/analyzer_instrument_samples

inspect-hihat-suppression:
	python3 scripts/inspect_hihat_suppression.py

inspect-hihat-drum-policy:
	python3 scripts/inspect_analyzer_source_range.py 31480 31740

inspect-bass-detector-paths:
	python3 scripts/inspect_bass_detector_paths.py

inspect-bass-alias-policy:
	python3 scripts/inspect_analyzer_source_range.py 1000 1245

report-sneakybass-octave-aliases:
	python3 scripts/report_sneakybass_octave_aliases.py

report-sneakybass-tracking-alignment:
	python3 scripts/report_sneakybass_tracking_alignment.py

inventory-external-fixture-sources:
	python3 scripts/inventory_external_fixture_sources.py

inspect-instrument-route-logic:
	python3 scripts/inspect_instrument_route_logic.py

report-full-mix-route-examples:
	python3 scripts/report_full_mix_route_examples.py

test-real-note-samples-full-mix-route-examples:
	MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLE_LIMIT=48 $(MAKE) test-real-note-samples-full-mix

debug-real-note-piano-guitar-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh keyboard_electronic_001-071-025

debug-real-note-piano-guitar-visual-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh keyboard_electronic_002-033-050

debug-real-note-vocal-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocadito_35_A1_004_A2

debug-real-note-vocal-vibrato-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocalset_f7_scales_vibrato_i_19_C_4

debug-real-note-vocal-piano-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocalset_f7_scales_belt_u_3_D_4

report-real-note-debug-sample:
	python3 scripts/report_real_note_debug_sample.py

report-real-note-fixture-coverage:
	python3 scripts/report_real_note_fixture_coverage.py

report-external-fixture-inventory:
	python3 scripts/report_external_fixture_inventory.py

audit-real-note-vocals: build/analyzer_real_note_samples
	sh scripts/run_real_note_vocal_audit.sh

report-real-note-vocal-audit:
	python3 scripts/report_real_note_vocal_audit.py

report-real-note-full-mix-shards:
	python3 scripts/report_real_note_full_mix_shards.py

report-full-mix-guitar-attributes: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_guitar_attributes.py

.PHONY: report-full-mix-guitar-visual-patterns
report-full-mix-guitar-visual-patterns: report-full-mix-guitar-attributes
	python3 scripts/report_full_mix_guitar_visual_patterns.py

.PHONY: report-full-mix-guitar-attack-attributes
report-full-mix-guitar-attack-attributes: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_guitar_attributes.py --attack

.PHONY: report-full-mix-guitar-attack-patterns
report-full-mix-guitar-attack-patterns: report-full-mix-guitar-attack-attributes
	python3 scripts/report_full_mix_guitar_visual_patterns.py --buffer first --input-phase attack

.PHONY: report-full-mix-piano-guitar-onset-ownership
report-full-mix-piano-guitar-onset-ownership: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_piano_guitar_attack_ownership.py

.PHONY: report-full-mix-bass-attributes
report-full-mix-bass-attributes: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_bass_attributes.py

.PHONY: inspect-timbre-classifier-source
inspect-timbre-classifier-source: scripts/inspect_timbre_classifier_source.py
	python3 scripts/inspect_timbre_classifier_source.py

.PHONY: report-full-mix-visual-failures
report-full-mix-visual-failures: scripts/report_full_mix_visual_failures.py
	python3 scripts/report_full_mix_visual_failures.py

.PHONY: report-full-mix-vocal-failures
report-full-mix-vocal-failures: scripts/report_full_mix_vocal_failures.py
	python3 scripts/report_full_mix_vocal_failures.py

.PHONY: inspect-vocal-display-source
inspect-vocal-display-source: scripts/inspect_vocal_display_source.py
	python3 scripts/inspect_vocal_display_source.py

.PHONY: report-real-note-fixture-inventory
report-real-note-fixture-inventory: scripts/report_real_note_fixture_inventory.py
	python3 scripts/report_real_note_fixture_inventory.py

.PHONY: report-real-note-full-mix-attributes
report-real-note-full-mix-attributes: build/analyzer_real_note_samples scripts/report_real_note_full_mix_attributes.py
	python3 scripts/report_real_note_full_mix_attributes.py

.PHONY: report-real-note-full-mix-attributes-reuse
report-real-note-full-mix-attributes-reuse: scripts/report_real_note_full_mix_attributes.py
	python3 scripts/report_real_note_full_mix_attributes.py --reuse

.PHONY: report-guitar-profile-search
report-guitar-profile-search: scripts/report_guitar_profile_search.py
	python3 scripts/report_guitar_profile_search.py

.PHONY: report-timbre-classifier
report-timbre-classifier: scripts/report_timbre_classifier.py
	python3 scripts/report_timbre_classifier.py

.PHONY: plan-urmp-multitrack-fixtures
plan-urmp-multitrack-fixtures: scripts/prepare_urmp_multitrack_fixtures.py
	python3 scripts/prepare_urmp_multitrack_fixtures.py plan

.PHONY: apply-urmp-multitrack-fixtures
apply-urmp-multitrack-fixtures: scripts/prepare_urmp_multitrack_fixtures.py
	python3 scripts/prepare_urmp_multitrack_fixtures.py apply

.PHONY: report-urmp-multitrack-inventory
report-urmp-multitrack-inventory: scripts/report_urmp_multitrack_inventory.py
	python3 scripts/report_urmp_multitrack_inventory.py

.PHONY: inspect-real-note-test-source
inspect-real-note-test-source: scripts/inspect_real_note_test_source.py
	python3 scripts/inspect_real_note_test_source.py

.PHONY: plan-urmp-analyzer-cases
plan-urmp-analyzer-cases: scripts/prepare_urmp_analyzer_cases.py
	python3 scripts/prepare_urmp_analyzer_cases.py plan

.PHONY: apply-urmp-analyzer-cases
apply-urmp-analyzer-cases: scripts/prepare_urmp_analyzer_cases.py
	python3 scripts/prepare_urmp_analyzer_cases.py apply

.PHONY: report-urmp-analyzer-cases
report-urmp-analyzer-cases: build/analyzer_real_note_samples scripts/report_urmp_analyzer_cases.py
	python3 scripts/report_urmp_analyzer_cases.py

.PHONY: test-urmp-analyzer-cases
test-urmp-analyzer-cases: build/analyzer_real_note_samples scripts/report_urmp_analyzer_cases.py
	python3 scripts/report_urmp_analyzer_cases.py --verify

.PHONY: report-urmp-mixture-cases
report-urmp-mixture-cases: build/analyzer_real_note_samples scripts/report_urmp_analyzer_cases.py
	python3 scripts/report_urmp_analyzer_cases.py --mixtures

.PHONY: test-urmp-mixture-cases
test-urmp-mixture-cases: build/analyzer_real_note_samples scripts/report_urmp_analyzer_cases.py
	python3 scripts/report_urmp_analyzer_cases.py --mixtures --verify

.PHONY: inspect-full-mix-owner-source
inspect-full-mix-owner-source: scripts/inspect_full_mix_owner_source.py
	python3 scripts/inspect_full_mix_owner_source.py
.PHONY: report-drum-fixture-candidates
report-drum-fixture-candidates: scripts/report_drum_fixture_candidates.py
	python3 scripts/report_drum_fixture_candidates.py

.PHONY: inspect-real-note-drum-test-source
inspect-real-note-drum-test-source: scripts/inspect_real_note_drum_test_source.py
	python3 scripts/inspect_real_note_drum_test_source.py

.PHONY: inspect-analyzer-test-utils-source
inspect-analyzer-test-utils-source: scripts/inspect_analyzer_test_utils_source.py
	python3 scripts/inspect_analyzer_test_utils_source.py

.PHONY: inspect-drum-detector-source
inspect-drum-detector-source: scripts/inspect_drum_detector_source.py
	python3 scripts/inspect_drum_detector_source.py

.PHONY: report-idmt-drum-fixture-manifest
report-idmt-drum-fixture-manifest: scripts/report_idmt_drum_fixture_manifest.py
	python3 scripts/report_idmt_drum_fixture_manifest.py

.PHONY: report-real-drum-samples-debug
report-real-drum-samples-debug: build/analyzer_real_drum_samples
	MUSIC_ANALYZER_REAL_DRUM_VERBOSE=1 build/analyzer_real_drum_samples

.PHONY: report-real-drum-samples-one-shot
report-real-drum-samples-one-shot: build/analyzer_real_drum_samples
	MUSIC_ANALYZER_REAL_DRUM_SOURCE="IDMT Drum One Shot" build/analyzer_real_drum_samples

.PHONY: report-real-drum-samples-one-shot-debug
report-real-drum-samples-one-shot-debug: build/analyzer_real_drum_samples
	MUSIC_ANALYZER_REAL_DRUM_SOURCE="IDMT Drum One Shot" MUSIC_ANALYZER_REAL_DRUM_VERBOSE=1 build/analyzer_real_drum_samples

build/analyzer_real_drum_samples.o: tests/analyzer_real_drum_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp
	tmp="$@.$$$$.tmp"; g++ -O2 -g -std=c++17 -fPIC -Wall -Wextra -Isrc -Ithird_party/beat_and_tempo_tracking -c $< -o "$$tmp" && mv "$$tmp" "$@"

build/analyzer_real_drum_samples: build/analyzer_test.o build/btt_BTT.o build/btt_DFT.o build/btt_Filter.o build/btt_STFT.o build/btt_Statistics.o build/btt_fastsin.o build/basic_pitch_onnx_runtime.o build/basic_pitch_onnx_decoder.o build/basic_pitch_onnx_worker.o build/basic_pitch_pcm_history.o build/analyzer_real_drum_samples.o
	tmp="$@.$$$$.tmp"; g++ -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

.PHONY: report-real-drum-samples
report-real-drum-samples: build/analyzer_real_drum_samples
	build/analyzer_real_drum_samples

.PHONY: report-real-drum-samples-matrix
report-real-drum-samples-matrix: build/analyzer_real_drum_samples
	sh ./scripts/run_real_drum_source_matrix.sh

.PHONY: plan-real-drum-improvement-commit
plan-real-drum-improvement-commit:
	python3 scripts/manage_real_drum_improvement_commit.py plan

