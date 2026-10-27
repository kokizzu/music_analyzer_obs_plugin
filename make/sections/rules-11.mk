.PHONY: commit-real-drum-improvement
commit-real-drum-improvement:
	python3 scripts/manage_real_drum_improvement_commit.py apply

.PHONY: push-real-drum-improvement
push-real-drum-improvement:
	python3 scripts/manage_real_drum_improvement_commit.py push

.PHONY: test-real-drum-samples
test-real-drum-samples: build/analyzer_real_drum_samples
	sh ./scripts/test_real_drum_samples.sh

.PHONY: report-real-drum-samples-real-track
report-real-drum-samples-real-track: build/analyzer_real_drum_samples
	sh ./scripts/run_real_drum_source_report.sh "Real Drum Track"

.PHONY: test-real-drum-track-admission
test-real-drum-track-admission: build/analyzer_real_drum_samples
	sh ./scripts/test_real_drum_track_admission.sh

.PHONY: test-real-drum-one-shot-admission
test-real-drum-one-shot-admission: build/analyzer_real_drum_samples
	sh ./scripts/test_real_drum_one_shot_admission.sh

.PHONY: report-real-drum-samples-drum-track
report-real-drum-samples-drum-track: build/analyzer_real_drum_samples
	sh ./scripts/run_real_drum_source_report.sh "IDMT Drum Track"



.PHONY: report-urmp-mixture-ownership-attributes
report-urmp-mixture-ownership-attributes: scripts/report_urmp_mixture_ownership_attributes.py
	python3 scripts/report_urmp_mixture_ownership_attributes.py

.PHONY: report-urmp-other-recovery-profile
report-urmp-other-recovery-profile: build/analyzer_real_note_samples scripts/report_urmp_other_recovery_profile.py
	python3 scripts/report_urmp_other_recovery_profile.py

.PHONY: report-urmp-other-recovery-profile-reuse
report-urmp-other-recovery-profile-reuse: scripts/report_urmp_other_recovery_profile.py
	python3 scripts/report_urmp_other_recovery_profile.py --reuse

.PHONY: plan-detection-improvement-commit
plan-detection-improvement-commit: scripts/manage_detection_improvement_commit.py
	python3 scripts/manage_detection_improvement_commit.py plan

.PHONY: apply-detection-improvement-commit
apply-detection-improvement-commit: scripts/manage_detection_improvement_commit.py
	python3 scripts/manage_detection_improvement_commit.py apply

.PHONY: commit-detection-improvement
commit-detection-improvement: scripts/manage_detection_improvement_commit.py
	python3 scripts/manage_detection_improvement_commit.py commit

.PHONY: push-detection-improvement
push-detection-improvement: scripts/manage_detection_improvement_commit.py
	python3 scripts/manage_detection_improvement_commit.py push

.PHONY: debug-urmp-mixture-case
debug-urmp-mixture-case: build/analyzer_real_note_samples scripts/debug_urmp_mixture_case.py
	python3 scripts/debug_urmp_mixture_case.py

.PHONY: report-urmp-chord-opportunities
report-urmp-chord-opportunities: scripts/report_urmp_chord_opportunities.py
	python3 scripts/report_urmp_chord_opportunities.py

.PHONY: report-urmp-chord-cases
report-urmp-chord-cases: scripts/report_urmp_chord_cases.py
	python3 scripts/report_urmp_chord_cases.py

.PHONY: test-urmp-chord-cases-reuse
test-urmp-chord-cases-reuse: scripts/report_urmp_chord_cases.py
	python3 scripts/report_urmp_chord_cases.py --verify

.PHONY: test-urmp-chord-cases
test-urmp-chord-cases: build/analyzer_real_note_samples scripts/report_urmp_other_recovery_profile.py scripts/report_urmp_chord_cases.py
	python3 scripts/report_urmp_other_recovery_profile.py
	python3 scripts/report_urmp_chord_cases.py --verify

.PHONY: plan-nsynth-test-fixtures
plan-nsynth-test-fixtures: scripts/prepare_nsynth_test_fixtures.sh
	bash scripts/prepare_nsynth_test_fixtures.sh plan

.PHONY: setup-nsynth-test-fixtures
setup-nsynth-test-fixtures: scripts/prepare_nsynth_test_fixtures.sh
	bash scripts/prepare_nsynth_test_fixtures.sh apply

.PHONY: verify-nsynth-test-fixtures
verify-nsynth-test-fixtures: scripts/prepare_nsynth_test_fixtures.sh scripts/check_nsynth_test_fixtures.py
	bash scripts/prepare_nsynth_test_fixtures.sh verify
	python3 scripts/check_nsynth_test_fixtures.py

.PHONY: inspect-chord-detector-source
inspect-chord-detector-source: scripts/inspect_chord_detector_source.py
	python3 scripts/inspect_chord_detector_source.py

.PHONY: inspect-analysis-snapshot-source
inspect-analysis-snapshot-source: scripts/inspect_analysis_snapshot_source.py
	python3 scripts/inspect_analysis_snapshot_source.py

.PHONY: inspect-full-mix-debug-write-source
inspect-full-mix-debug-write-source: scripts/inspect_full_mix_debug_write_source.py
	python3 scripts/inspect_full_mix_debug_write_source.py

.PHONY: inspect-mixed-other-display-source
inspect-mixed-other-display-source: scripts/inspect_mixed_other_display_source.py
	python3 scripts/inspect_mixed_other_display_source.py

.PHONY: inspect-full-mix-other-predicates-source
inspect-full-mix-other-predicates-source: scripts/inspect_full_mix_other_predicates_source.py
	python3 scripts/inspect_full_mix_other_predicates_source.py

.PHONY: plan-urmp-mixture-cases
plan-urmp-mixture-cases: scripts/plan_urmp_mixture_cases.py
	python3 scripts/plan_urmp_mixture_cases.py

.PHONY: apply-urmp-mixture-cases
apply-urmp-mixture-cases: scripts/plan_urmp_mixture_cases.py
	python3 scripts/plan_urmp_mixture_cases.py apply

.PHONY: plan-real-instrument-expansion-fixtures
plan-real-instrument-expansion-fixtures: scripts/prepare_real_instrument_expansion.py
	python3 scripts/prepare_real_instrument_expansion.py plan

.PHONY: apply-real-instrument-expansion-fixtures
apply-real-instrument-expansion-fixtures: scripts/prepare_real_instrument_expansion.py
	python3 scripts/prepare_real_instrument_expansion.py apply

.PHONY: test-real-instrument-expansion
test-real-instrument-expansion: build/analyzer_real_note_samples scripts/test_real_instrument_expansion.py
	python3 scripts/test_real_instrument_expansion.py

.PHONY: report-full-mix-display-mirror-source
report-full-mix-display-mirror-source: scripts/report_full_mix_display_mirror_source.py
	python3 scripts/report_full_mix_display_mirror_source.py

.PHONY: report-full-mix-bass-attributes-script
report-full-mix-bass-attributes-script: scripts/report_full_mix_bass_attributes_script.py
	python3 scripts/report_full_mix_bass_attributes_script.py

.PHONY: report-full-mix-ownership-signatures
report-full-mix-ownership-signatures: scripts/report_full_mix_ownership_signatures.py
	python3 scripts/report_full_mix_ownership_signatures.py

.PHONY: report-real-instrument-expansion-bass-attributes
report-real-instrument-expansion-bass-attributes: build/analyzer_real_note_samples scripts/report_real_instrument_expansion_bass_attributes.py
	python3 scripts/report_real_instrument_expansion_bass_attributes.py

.PHONY: report-real-instrument-expansion-guitar-attributes
report-real-instrument-expansion-guitar-attributes: build/analyzer_real_note_samples scripts/report_real_instrument_expansion_bass_attributes.py
	python3 scripts/report_real_instrument_expansion_bass_attributes.py --family guitar

.PHONY: report-real-instrument-expansion-piano-attributes
report-real-instrument-expansion-piano-attributes: build/analyzer_real_note_samples scripts/report_real_instrument_expansion_bass_attributes.py
	python3 scripts/report_real_instrument_expansion_bass_attributes.py --family piano

.PHONY: report-real-instrument-expansion-other-attributes
report-real-instrument-expansion-other-attributes: build/analyzer_real_note_samples scripts/report_real_instrument_expansion_bass_attributes.py
	python3 scripts/report_real_instrument_expansion_bass_attributes.py --family other

.PHONY: report-real-instrument-expansion-flute-attributes
report-real-instrument-expansion-flute-attributes: build/analyzer_real_note_samples scripts/report_real_instrument_expansion_bass_attributes.py
	python3 scripts/report_real_instrument_expansion_bass_attributes.py --family other --source tinysol-flute

.PHONY: inspect-real-instrument-attribute-reporter
inspect-real-instrument-attribute-reporter: scripts/inspect_real_instrument_reporter_source.py
	python3 scripts/inspect_real_instrument_reporter_source.py

.PHONY: inspect-real-note-attribute-source
inspect-real-note-attribute-source: scripts/inspect_real_note_attribute_source.py
	python3 scripts/inspect_real_note_attribute_source.py

.PHONY: inspect-real-instrument-expansion-preparer
inspect-real-instrument-expansion-preparer: scripts/inspect_real_instrument_expansion_preparer_source.py
	python3 scripts/inspect_real_instrument_expansion_preparer_source.py

.PHONY: inspect-real-instrument-expansion-test
inspect-real-instrument-expansion-test: scripts/inspect_real_instrument_expansion_test_source.py
	python3 scripts/inspect_real_instrument_expansion_test_source.py

.PHONY: report-tinysol-fixture-categories
report-tinysol-fixture-categories: scripts/report_tinysol_fixture_categories.py
	python3 scripts/report_tinysol_fixture_categories.py

.PHONY: inspect-mixed-owner-source
inspect-mixed-owner-source: scripts/inspect_mixed_owner_source.py
	python3 scripts/inspect_mixed_owner_source.py

.PHONY: inspect-full-mix-display-flow-source
inspect-full-mix-display-flow-source: scripts/inspect_full_mix_display_flow_source.py
	python3 scripts/inspect_full_mix_display_flow_source.py

.PHONY: report-full-mix-vocal-guitar-collisions
report-full-mix-vocal-guitar-collisions: build/analyzer_real_note_samples scripts/report_full_mix_vocal_guitar_collisions.py
	python3 scripts/report_full_mix_vocal_guitar_collisions.py

.PHONY: snapshot-full-mix-vocal-guitar-collisions-baseline
snapshot-full-mix-vocal-guitar-collisions-baseline: build/analyzer_real_note_samples scripts/report_full_mix_vocal_guitar_collisions.py
	python3 scripts/report_full_mix_vocal_guitar_collisions.py --snapshot baseline

.PHONY: snapshot-full-mix-vocal-guitar-collisions-candidate
snapshot-full-mix-vocal-guitar-collisions-candidate: build/analyzer_real_note_samples scripts/report_full_mix_vocal_guitar_collisions.py
	python3 scripts/report_full_mix_vocal_guitar_collisions.py --snapshot candidate

.PHONY: compare-full-mix-vocal-guitar-collisions
compare-full-mix-vocal-guitar-collisions: scripts/report_full_mix_vocal_guitar_collisions.py
	python3 scripts/report_full_mix_vocal_guitar_collisions.py --compare baseline candidate

report-full-mix-other-attributes: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_other_attributes.py

.PHONY: report-full-mix-other-visual-patterns
report-full-mix-other-visual-patterns: report-full-mix-other-attributes
	python3 scripts/report_full_mix_other_visual_patterns.py

.PHONY: report-full-mix-piano-other-ownership
report-full-mix-piano-other-ownership: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_piano_other_ownership.py

.PHONY: report-full-mix-piano-guitar-ownership
report-full-mix-piano-guitar-ownership: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_piano_guitar_ownership.py

report-full-mix-vocal-attributes: build/analyzer_real_note_samples
	python3 scripts/report_full_mix_vocal_attributes.py

report-full-mix-vocal-feature-patterns:
	python3 scripts/report_full_mix_vocal_feature_patterns.py

test-full-mix-guitar-octave-alias: report-full-mix-guitar-attributes
	python3 scripts/test_full_mix_guitar_octave_alias.py

report-external-fixture-coverage:
	python3 scripts/report_external_fixture_coverage.py

report-fixture-storage:
	python3 scripts/report_fixture_storage.py

plan-external-audio-fixture-storage:
	python3 scripts/migrate_audio_fixture_storage.py plan

apply-external-audio-fixture-storage:
	python3 scripts/migrate_audio_fixture_storage.py apply

verify-external-audio-fixture-storage:
	python3 scripts/migrate_audio_fixture_storage.py verify

test-real-note-vocal-display-recall: audit-real-note-vocals
	python3 scripts/test_real_note_vocal_display_recall.py

inspect-external-vocal-manifests:
	python3 scripts/inspect_external_vocal_manifests.py

plan-real-note-vocal-fixture:
	python3 scripts/manage_real_note_vocal_fixture.py plan

apply-real-note-vocal-fixture:
	python3 scripts/manage_real_note_vocal_fixture.py apply

commit-instrument-route-inspection:
	python3 scripts/commit_staged_source_changes.py --message "test: inspect instrument route logic"

commit-full-mix-route-observability:
	python3 scripts/commit_staged_source_changes.py --message "test: expose full mix route examples"

test-instrument-synth-c5: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C5" build/analyzer_instrument_samples

analyze-instrument-synth-c5: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C5" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="build/synth_c5_attributes.tsv" build/analyzer_instrument_samples

report-instrument-synth-c5:
	python3 scripts/report_synth_c5_attributes.py

inspect-synth-c5-display-path:
	python3 scripts/inspect_analyzer_source_range.py 37890 37945

inspect-synth-c5-ranking-path:
	python3 scripts/inspect_synth_c5_ranking_symbols.py

inspect-synth-c5-low-octave-policy:
	python3 scripts/inspect_analyzer_source_range.py 15062 15375

inspect-synth-c5-pre-display-policy:
	python3 scripts/inspect_analyzer_source_range.py 37850 37895

inspect-synth-c5-visible-lower-policy:
	python3 scripts/inspect_analyzer_source_range.py 13664 13750
test-instrument-synth-saw-lead-c4: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="saw_lead" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C4" build/analyzer_instrument_samples

analyze-instrument-synth-saw-lead-c4: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="saw_lead" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C4" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$(BUILD_DIR)/saw_lead_c4_attributes.tsv" build/analyzer_instrument_samples

report-instrument-synth-saw-lead-c4:
	$(PYTHON) scripts/report_voice_oohs_g3_attributes.py --attributes "$(BUILD_DIR)/saw_lead_c4_attributes.tsv"
inspect-synth-harmonic-paths:
	python3 scripts/inspect_synth_harmonic_paths.py
export-real-note-vocal-attributes: build/analyzer_real_note_samples
	python3 scripts/export_real_note_vocal_attributes.py

report-real-note-vocal-attributes:
	python3 scripts/report_real_note_vocal_attributes.py
test-external-prepared-multitrack-20:
	sh scripts/run_external_prepared_multitrack_test.sh

export-external-prepared-multitrack-attributes: build/analyzer_musicnet
	python3 scripts/export_prepared_multitrack_attributes.py

report-external-prepared-multitrack-attributes:
	python3 scripts/report_prepared_multitrack_attributes.py
profile-real-note-vocal-misses:
	python3 scripts/profile_real_note_vocal_misses.py

report-code-baseline-diff:
	python3 scripts/report_code_baseline_diff.py

test-real-note-vocal-recall-regression: audit-real-note-vocals
	python3 scripts/check_real_note_vocal_recall.py build/real_note_vocal_audit.out --minimum-hits 167

.PHONY: inspect-real-drum-runner
inspect-real-drum-runner: scripts/inspect_real_drum_runner.py
	python3 scripts/inspect_real_drum_runner.py

.PHONY: report-external-drum-manifests
report-external-drum-manifests: scripts/report_external_drum_manifests.py
	python3 scripts/report_external_drum_manifests.py

.PHONY: report-real-drum-corpus
report-real-drum-corpus: build/analyzer_real_drum_samples scripts/report_real_drum_corpus.sh
	sh scripts/report_real_drum_corpus.sh

.PHONY: report-real-drum-corpus-debug
report-real-drum-corpus-debug: build/analyzer_real_drum_samples scripts/report_real_drum_corpus.sh
	sh scripts/report_real_drum_corpus.sh --verbose

.PHONY: commit-real-drum-corpus-coverage
commit-real-drum-corpus-coverage: scripts/manage_real_drum_corpus_coverage.py
	python3 scripts/manage_real_drum_corpus_coverage.py commit

.PHONY: push-real-drum-corpus-coverage
push-real-drum-corpus-coverage: scripts/manage_real_drum_corpus_coverage.py
	python3 scripts/manage_real_drum_corpus_coverage.py push

.PHONY: test-real-drum-corpus
test-real-drum-corpus: build/analyzer_real_drum_samples scripts/report_real_drum_corpus.sh
	sh scripts/report_real_drum_corpus.sh --verify

.PHONY: inspect-full-mix-attribute-report
inspect-full-mix-attribute-report: scripts/inspect_full_mix_attribute_report.py
	python3 scripts/inspect_full_mix_attribute_report.py

.PHONY: report-full-mix-piano-attributes
report-full-mix-piano-attributes: build/analyzer_real_note_samples scripts/report_full_mix_bass_attributes.py
	python3 scripts/report_full_mix_bass_attributes.py piano --all-shards

.PHONY: report-full-mix-piano-attributes-shard0
report-full-mix-piano-attributes-shard0: build/analyzer_real_note_samples scripts/report_full_mix_bass_attributes.py
	python3 scripts/report_full_mix_bass_attributes.py piano

.PHONY: report-full-mix-piano-attributes-sample
report-full-mix-piano-attributes-sample: build/analyzer_real_note_samples scripts/report_full_mix_bass_attributes.py
	python3 scripts/report_full_mix_bass_attributes.py piano --shard-count=16

.PHONY: inspect-full-mix-electric-piano-source
inspect-full-mix-electric-piano-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "measured_other_owned_electric_piano_supported"

.PHONY: inspect-full-mix-visual-boost-source
inspect-full-mix-visual-boost-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "boost_existing"

.PHONY: inspect-note-grid-source
inspect-note-grid-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "NoteGrid"

.PHONY: inspect-low-electronic-keyboard-source
inspect-low-electronic-keyboard-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "low_electronic"

.PHONY: inspect-full-mix-electric-piano-source
inspect-full-mix-electric-piano-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "measured_other_owned_electric_piano_supported"

.PHONY: inspect-full-mix-visual-boost-source
inspect-full-mix-visual-boost-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "boost_existing"

.PHONY: inspect-note-grid-source
inspect-note-grid-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "NoteGrid"

.PHONY: inspect-low-electronic-keyboard-source
inspect-low-electronic-keyboard-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "low_electronic"

.PHONY: inspect-low-keyboard-restore-source
inspect-low-keyboard-restore-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "restore_full_mix_low_keyboard"

.PHONY: inspect-full-mix-electric-piano-source
inspect-full-mix-electric-piano-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "measured_other_owned_electric_piano_supported"

.PHONY: inspect-full-mix-visual-boost-source
inspect-full-mix-visual-boost-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "boost_existing"

.PHONY: inspect-note-grid-source
inspect-note-grid-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "NoteGrid"

.PHONY: inspect-low-electronic-keyboard-source
inspect-low-electronic-keyboard-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "low_electronic"

.PHONY: inspect-low-keyboard-restore-source
inspect-low-keyboard-restore-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "restore_full_mix_low_keyboard"

.PHONY: inspect-diminished-chord-source
inspect-diminished-chord-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "diminished"

.PHONY: inspect-urmp-chord-report
inspect-urmp-chord-report: scripts/inspect_urmp_chord_report.py
	python3 scripts/inspect_urmp_chord_report.py

.PHONY: report-urmp-chord-attributes
report-urmp-chord-attributes: scripts/report_urmp_chord_attributes.py report-urmp-other-recovery-profile
	python3 scripts/report_urmp_chord_attributes.py

.PHONY: report-urmp-chord-attributes-cached
report-urmp-chord-attributes-cached: scripts/report_urmp_chord_attributes.py
	python3 scripts/report_urmp_chord_attributes.py

.PHONY: inspect-full-mix-electric-piano-source
inspect-full-mix-electric-piano-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "measured_other_owned_electric_piano_supported"

.PHONY: inspect-full-mix-visual-boost-source
inspect-full-mix-visual-boost-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "boost_existing"

.PHONY: inspect-note-grid-source
inspect-note-grid-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "NoteGrid"

.PHONY: inspect-low-electronic-keyboard-source
inspect-low-electronic-keyboard-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "low_electronic"

.PHONY: inspect-low-keyboard-restore-source
inspect-low-keyboard-restore-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "restore_full_mix_low_keyboard"

.PHONY: inspect-diminished-chord-source
inspect-diminished-chord-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "diminished"

.PHONY: inspect-urmp-chord-report
inspect-urmp-chord-report: scripts/inspect_urmp_chord_report.py
	python3 scripts/inspect_urmp_chord_report.py

.PHONY: report-urmp-chord-attributes
report-urmp-chord-attributes: scripts/report_urmp_chord_attributes.py report-urmp-other-recovery-profile
	python3 scripts/report_urmp_chord_attributes.py

.PHONY: report-urmp-chord-attributes-cached
report-urmp-chord-attributes-cached: scripts/report_urmp_chord_attributes.py
	python3 scripts/report_urmp_chord_attributes.py

.PHONY: inspect-global-chord-state-source
inspect-global-chord-state-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "snapshot.global_chord"

.PHONY: inspect-stabilize-chord-source
inspect-stabilize-chord-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "stabilize_chord"

.PHONY: inspect-stabilize-chord-body
inspect-stabilize-chord-body: scripts/inspect_stabilize_chord_source.py
	python3 scripts/inspect_stabilize_chord_source.py

.PHONY: inspect-chord-timing-source
inspect-chord-timing-source: scripts/inspect_analyzer_section.py
	python3 scripts/inspect_analyzer_section.py --source src/analyzer.cpp --topic "kChordHoldSeconds"

.PHONY: inspect-chord-temporal-tests
inspect-chord-temporal-tests: scripts/inspect_chord_temporal_tests.py
	python3 scripts/inspect_chord_temporal_tests.py

.PHONY: commit-chord-stability
commit-chord-stability: scripts/manage_real_drum_improvement_commit.py
	python3 scripts/manage_real_drum_improvement_commit.py apply

.PHONY: push-chord-stability
push-chord-stability: scripts/manage_real_drum_improvement_commit.py
	python3 scripts/manage_real_drum_improvement_commit.py push

.PHONY: report-urmp-chord-routes-cached start-analyzer-internal-test status-analyzer-internal-test start-urmp-profile-replay status-urmp-profile-replay
report-urmp-chord-routes-cached: scripts/report_urmp_chord_routes.py
	python3 scripts/report_urmp_chord_routes.py

start-analyzer-internal-test: scripts/manage_analyzer_internal_test.py
	python3 scripts/manage_analyzer_internal_test.py start

status-analyzer-internal-test: scripts/manage_analyzer_internal_test.py
	python3 scripts/manage_analyzer_internal_test.py status

start-urmp-profile-replay: scripts/manage_urmp_profile_replay.py
	python3 scripts/manage_urmp_profile_replay.py start

status-urmp-profile-replay: scripts/manage_urmp_profile_replay.py
	python3 scripts/manage_urmp_profile_replay.py status

.PHONY: inspect-vocadito-fixtures plan-vocadito-fixtures apply-vocadito-fixtures
inspect-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py inspect

plan-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py plan

apply-vocadito-fixtures: scripts/manage_vocadito_fixtures.py
	python3 scripts/manage_vocadito_fixtures.py apply

.PHONY: plan-vocadito-midrange-fixtures apply-vocadito-midrange-fixtures
plan-vocadito-midrange-fixtures: scripts/prepare_vocadito_midrange_fixtures.py
	python3 scripts/prepare_vocadito_midrange_fixtures.py plan

apply-vocadito-midrange-fixtures: scripts/prepare_vocadito_midrange_fixtures.py
	python3 scripts/prepare_vocadito_midrange_fixtures.py apply

.PHONY: report-vocadito-midrange-samples test-vocadito-midrange-samples
report-vocadito-midrange-samples: build/analyzer_real_note_samples apply-vocadito-midrange-fixtures scripts/test_vocadito_midrange.py
	python3 scripts/test_vocadito_midrange.py

test-vocadito-midrange-samples: build/analyzer_real_note_samples apply-vocadito-midrange-fixtures scripts/test_vocadito_midrange.py
	python3 scripts/test_vocadito_midrange.py --verify

.PHONY: plan-vocadito-fixture-commit commit-vocadito-fixture-commit push-vocadito-fixture-commit
plan-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py plan

commit-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py commit

push-vocadito-fixture-commit: scripts/manage_vocadito_fixture_commit.py
	python3 scripts/manage_vocadito_fixture_commit.py push

.PHONY: plan-iowa-piano-midrange-fixtures probe-iowa-piano-midrange-fixtures apply-iowa-piano-midrange-fixtures verify-iowa-piano-midrange-fixtures
plan-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py plan
probe-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py probe
apply-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py apply
verify-iowa-piano-midrange-fixtures: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py verify
.PHONY: start-iowa-piano-midrange-fixtures status-iowa-piano-midrange-fixtures stop-iowa-piano-midrange-fixtures
start-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py start
status-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py status
stop-iowa-piano-midrange-fixtures: scripts/manage_iowa_piano_fixture_download.py
	python3 scripts/manage_iowa_piano_fixture_download.py stop
.PHONY: test-iowa-piano-midrange-samples
test-iowa-piano-midrange-samples: build/analyzer_real_note_samples build/iowa_piano_midrange_samples scripts/test_iowa_piano_midrange.py
	python3 scripts/test_iowa_piano_midrange.py --verify
.PHONY: report-iowa-piano-midrange-samples
report-iowa-piano-midrange-samples: build/analyzer_real_note_samples build/iowa_piano_midrange_samples scripts/test_iowa_piano_midrange.py
	python3 scripts/test_iowa_piano_midrange.py --details --attributes
.PHONY: report-iowa-piano-attributes
report-iowa-piano-attributes: report-iowa-piano-midrange-samples scripts/report_iowa_piano_attributes.py
	python3 scripts/report_iowa_piano_attributes.py
.PHONY: publish-iowa-piano-midrange-partial
publish-iowa-piano-midrange-partial: scripts/prepare_iowa_piano_midrange_fixtures.py
	python3 scripts/prepare_iowa_piano_midrange_fixtures.py publish-partial
.PHONY: plan-iowa-piano-fixture-commit commit-iowa-piano-fixture push-iowa-piano-fixture
plan-iowa-piano-fixture-commit: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py plan
commit-iowa-piano-fixture: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py commit
push-iowa-piano-fixture: scripts/manage_iowa_piano_fixture_commit.py
	python3 scripts/manage_iowa_piano_fixture_commit.py push

.PHONY: report-guitar-profile-search-details
report-guitar-profile-search-details: scripts/report_guitar_profile_search.py
	python3 scripts/report_guitar_profile_search.py --details
.PHONY: report-vocal-profile-search-details
report-vocal-profile-search-details: scripts/report_guitar_profile_search.py
	python3 scripts/report_guitar_profile_search.py --family vocals --details
.PHONY: report-real-note-visible-recall
report-real-note-visible-recall: scripts/report_real_note_visible_recall.py
	python3 scripts/report_real_note_visible_recall.py
.PHONY: report-real-note-visible-recall-details
report-real-note-visible-recall-details: scripts/report_real_note_visible_recall.py
	python3 scripts/report_real_note_visible_recall.py --details
.PHONY: plan-visible-recall-reporting-commit commit-visible-recall-reporting push-visible-recall-reporting
plan-visible-recall-reporting-commit: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py plan
commit-visible-recall-reporting: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py commit
push-visible-recall-reporting: scripts/manage_visible_recall_reporting_commit.py
	python3 scripts/manage_visible_recall_reporting_commit.py push

.PHONY: probe-medleydb-sample
probe-medleydb-sample: scripts/probe_medleydb_sample.py
	python3 scripts/probe_medleydb_sample.py
.PHONY: start-medleydb-sample-download status-medleydb-sample-download stop-medleydb-sample-download
start-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py start
status-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py status
stop-medleydb-sample-download: scripts/manage_medleydb_sample_download.py
	python3 scripts/manage_medleydb_sample_download.py stop
.PHONY: inspect-medleydb-sample-archive
inspect-medleydb-sample-archive: scripts/inspect_medleydb_sample_archive.py
	python3 scripts/inspect_medleydb_sample_archive.py
.PHONY: inspect-medleydb-vocal-annotations
inspect-medleydb-vocal-annotations: scripts/inspect_medleydb_vocal_annotations.py
	python3 scripts/inspect_medleydb_vocal_annotations.py
.PHONY: plan-medleydb-vocal-mix-fixtures apply-medleydb-vocal-mix-fixtures verify-medleydb-vocal-mix-fixtures
plan-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py plan
apply-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py apply
verify-medleydb-vocal-mix-fixtures: scripts/prepare_medleydb_vocal_mix_fixtures.py
	python3 scripts/prepare_medleydb_vocal_mix_fixtures.py verify
.PHONY: report-medleydb-vocal-mix test-medleydb-vocal-mix
report-medleydb-vocal-mix: build/analyzer_real_note_samples build/medleydb_vocal_mix_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py
test-medleydb-vocal-mix: build/analyzer_real_note_samples build/medleydb_vocal_mix_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --verify
.PHONY: plan-medleydb-vocal-fixture-commit commit-medleydb-vocal-fixture push-medleydb-vocal-fixture
plan-medleydb-vocal-fixture-commit: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py plan
commit-medleydb-vocal-fixture: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py commit
push-medleydb-vocal-fixture: scripts/manage_medleydb_vocal_fixture_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_commit.py push

.PHONY: report-medleydb-vocal-mix-attributes
report-medleydb-vocal-mix-attributes: report-medleydb-vocal-mix scripts/report_medleydb_vocal_mix_attributes.py
	python3 scripts/report_medleydb_vocal_mix_attributes.py
.PHONY: report-medleydb-vocal-stem test-medleydb-vocal-stem
report-medleydb-vocal-stem: build/analyzer_real_note_samples build/medleydb_vocal_stem_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --stem
test-medleydb-vocal-stem: build/analyzer_real_note_samples build/medleydb_vocal_stem_samples scripts/test_medleydb_vocal_mix.py
	python3 scripts/test_medleydb_vocal_mix.py --stem --verify
.PHONY: report-medleydb-vocal-stem-attributes
report-medleydb-vocal-stem-attributes: report-medleydb-vocal-stem scripts/report_medleydb_vocal_mix_attributes.py
	python3 scripts/report_medleydb_vocal_mix_attributes.py --stem
.PHONY: report-basic-pitch-medleydb-mix-context report-basic-pitch-medleydb-stem-context test-basic-pitch-medleydb-context
$(BUILD_DIR)/basic_pitch_medleydb_context.o: tests/basic_pitch_medleydb_context.cpp src/analyzer.hpp src/basic_pitch_onnx_runtime.hpp src/basic_pitch_onnx_worker.hpp src/basic_pitch_pcm_history.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -I$(BTT_SOURCE_DIR) -c $< -o $@

$(BUILD_DIR)/basic_pitch_medleydb_context: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/basic_pitch_medleydb_context.o
	$(CXX) $(LDFLAGS) -o $@ $^ -ldl -lm -pthread

report-basic-pitch-medleydb-mix-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_medleydb_context "$(BUILD_DIR)/medleydb_vocal_mix_context_samples" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

report-basic-pitch-medleydb-stem-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_medleydb_context "$(BUILD_DIR)/medleydb_vocal_stem_context_samples" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

test-basic-pitch-medleydb-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/test_basic_pitch_medleydb_context.py
	$(PYTHON) scripts/test_basic_pitch_medleydb_context.py

.PHONY: plan-basic-pitch-medleydb-temporal-commit commit-basic-pitch-medleydb-temporal push-basic-pitch-medleydb-temporal
plan-basic-pitch-medleydb-temporal-commit: scripts/manage_basic_pitch_medleydb_temporal_commit.py
	$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py plan
commit-basic-pitch-medleydb-temporal: scripts/manage_basic_pitch_medleydb_temporal_commit.py
	$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py commit
push-basic-pitch-medleydb-temporal: scripts/manage_basic_pitch_medleydb_temporal_commit.py
	$(PYTHON) scripts/manage_basic_pitch_medleydb_temporal_commit.py push

.PHONY: plan-iowa-piano-temporal-control-commit commit-iowa-piano-temporal-control push-iowa-piano-temporal-control
plan-iowa-piano-temporal-control-commit: scripts/manage_iowa_piano_temporal_control_commit.py
	$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py plan
commit-iowa-piano-temporal-control: scripts/manage_iowa_piano_temporal_control_commit.py
	$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py commit
push-iowa-piano-temporal-control: scripts/manage_iowa_piano_temporal_control_commit.py
	$(PYTHON) scripts/manage_iowa_piano_temporal_control_commit.py push

.PHONY: inspect-iowa-piano-continuous-candidates
inspect-iowa-piano-continuous-candidates: scripts/inspect_iowa_piano_continuous_candidates.py
	$(PYTHON) scripts/inspect_iowa_piano_continuous_candidates.py

.PHONY: apply-iowa-piano-temporal-controls verify-iowa-piano-temporal-controls test-iowa-piano-temporal-controls
apply-iowa-piano-temporal-controls: scripts/prepare_iowa_piano_temporal_controls.py
	$(PYTHON) scripts/prepare_iowa_piano_temporal_controls.py apply
verify-iowa-piano-temporal-controls: scripts/prepare_iowa_piano_temporal_controls.py
	$(PYTHON) scripts/prepare_iowa_piano_temporal_controls.py verify
test-iowa-piano-temporal-controls: $(BUILD_DIR)/basic_pitch_medleydb_context apply-iowa-piano-temporal-controls $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/test_iowa_piano_temporal_controls.py
	$(PYTHON) scripts/test_iowa_piano_temporal_controls.py

.PHONY: plan-medleydb-vocal-fixture-update-commit commit-medleydb-vocal-fixture-update push-medleydb-vocal-fixture-update
plan-medleydb-vocal-fixture-update-commit: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py plan
commit-medleydb-vocal-fixture-update: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py commit
push-medleydb-vocal-fixture-update: scripts/manage_medleydb_vocal_fixture_update_commit.py
	python3 scripts/manage_medleydb_vocal_fixture_update_commit.py push

.PHONY: plan-low-bass-keyboard-routing-commit commit-low-bass-keyboard-routing push-low-bass-keyboard-routing
plan-low-bass-keyboard-routing-commit: scripts/manage_low_bass_keyboard_routing_commit.py
	$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py plan
commit-low-bass-keyboard-routing: scripts/manage_low_bass_keyboard_routing_commit.py
	$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py commit
push-low-bass-keyboard-routing: scripts/manage_low_bass_keyboard_routing_commit.py
	$(PYTHON) scripts/manage_low_bass_keyboard_routing_commit.py push

# Detection measurement checkpoint.
include accuracy_next.mk

.PHONY: plan-makefile-split apply-makefile-split verify-makefile-split publish-makefile-split test-makefile-source
plan-makefile-split: scripts/split_makefile.py
	$(PYTHON) scripts/split_makefile.py plan
apply-makefile-split: scripts/split_makefile.py
	$(PYTHON) scripts/split_makefile.py apply
verify-makefile-split: scripts/split_makefile.py
	$(PYTHON) scripts/split_makefile.py verify
publish-makefile-split: scripts/split_makefile.py
	$(PYTHON) scripts/split_makefile.py publish
test-makefile-source: tests/test_makefile_source.py scripts/makefile_source.py
	$(PYTHON) tests/test_makefile_source.py
