test-measure-beat-this-live-sidecar: tests/test_measure_beat_this_live_sidecar.py scripts/measure_beat_this_live_sidecar.py scripts/beat_this_live_sidecar.py scripts/measure_beat_this_bpm.py
	$(PYTHON) tests/test_measure_beat_this_live_sidecar.py

test-beat-this-obs-sidecar: tests/test_beat_this_obs_sidecar.py src/plugin.cpp src/beat_this_sidecar_client.cpp
	$(PYTHON) tests/test_beat_this_obs_sidecar.py

test-summarize-beat-this-sidecar-replay: tests/test_summarize_beat_this_sidecar_replay.py scripts/summarize_beat_this_sidecar_replay.py
	$(PYTHON) tests/test_summarize_beat_this_sidecar_replay.py

test-summarize-beat-this-bpm: tests/test_summarize_beat_this_bpm.py scripts/summarize_beat_this_bpm.py
	$(PYTHON) tests/test_summarize_beat_this_bpm.py

measure-beat-this-gtzan-rhythm: install-beat-this-diagnostic prepare-gtzan-rhythm-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_DIAGNOSTIC_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-rolling-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_ROLLING_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-rolling-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_ROLLING_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-continuous-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --cadence-seconds 10 --minimum-stable-seconds 10

measure-beat-this-continuous-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --cadence-seconds 10 --minimum-stable-seconds 10

measure-beat-this-sidecar-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_live_sidecar.py
	+$(MAKE) measure-beat-this-sidecar-ballroom-prepared

measure-beat-this-sidecar-ballroom-prepared: scripts/measure_beat_this_live_sidecar.py
	$(PYTHON) scripts/measure_beat_this_live_sidecar.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_SIDECAR_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --start "$(BEAT_THIS_SIDECAR_REPLAY_START)" --limit "$(BEAT_THIS_SIDECAR_REPLAY_LIMIT)"

measure-beat-this-sidecar-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_live_sidecar.py
	+$(MAKE) measure-beat-this-sidecar-filobass-prepared

measure-beat-this-sidecar-filobass-prepared: scripts/measure_beat_this_live_sidecar.py
	$(PYTHON) scripts/measure_beat_this_live_sidecar.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_SIDECAR_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --start "$(BEAT_THIS_SIDECAR_REPLAY_START)" --limit "$(BEAT_THIS_SIDECAR_REPLAY_LIMIT)"

summarize-beat-this-sidecar-ballroom: scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_BALLROOM_LOG)
	$(PYTHON) scripts/summarize_beat_this_sidecar_replay.py "$(BEAT_THIS_SIDECAR_BALLROOM_LOG)" --output "$(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)"
	cat "$(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)"

summarize-beat-this-sidecar-filobass: scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_FILOBASS_SHARD_LOGS)
	$(PYTHON) scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_FILOBASS_SHARD_LOGS) --output "$(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)"
	cat "$(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)"

audit-beat-this-continuous-interval-gate: scripts/audit_beat_this_continuous_interval_gate.py $(BEAT_THIS_CONTINUOUS_BALLROOM_LOG) $(BEAT_THIS_CONTINUOUS_FILOBASS_LOG) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_beat_this_continuous_interval_gate.py "$(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)" "$(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)" --output "$(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)"
	cat "$(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)"

test-audit-beat-this-continuous-interval-gate: scripts/audit_beat_this_continuous_interval_gate.py tests/test_audit_beat_this_continuous_interval_gate.py
	$(PYTHON) tests/test_audit_beat_this_continuous_interval_gate.py

summarize-beat-this-gtzan-rhythm: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_DIAGNOSTIC_LOG)"

summarize-beat-this-real-tempo: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_BALLROOM_LOG) $(BEAT_THIS_FILOBASS_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_BALLROOM_LOG)"
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_FILOBASS_LOG)"

summarize-beat-this-rolling-tempo: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_ROLLING_BALLROOM_LOG) $(BEAT_THIS_ROLLING_FILOBASS_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --prefix "Beat This rolling tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_ROLLING_BALLROOM_LOG)"
	$(PYTHON) scripts/summarize_beat_this_bpm.py --prefix "Beat This rolling tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_ROLLING_FILOBASS_LOG)"

summarize-permissive-beat-tracker-gtzan-rhythm: scripts/inspect_tempo_confidence_calibration.py $(BTT_GTZAN_RHYTHM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_GTZAN_RHYTHM_LOG)"

.PHONY: inspect-tempo-tracker-consensus test-inspect-tempo-tracker-consensus inspect-three-tempo-tracker-consensus inspect-high-tempo-three-tracker-consensus test-inspect-three-tempo-tracker-consensus
inspect-tempo-tracker-consensus: scripts/inspect_tempo_tracker_consensus.py $(BALLROOM_BPM_LOG) $(BTT_BALLROOM_LOG) $(FILOBASS_BPM_LOG) $(BTT_FILOBASS_LOG) $(GTZAN_RHYTHM_BPM_LOG) $(BTT_GTZAN_RHYTHM_LOG)
	$(PYTHON) scripts/inspect_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --phase-gates "$(TEMPO_CONSENSUS_PHASE_GATES)" --btt-gates "$(TEMPO_CONSENSUS_BTT_GATES)" --agreement-gates "$(TEMPO_CONSENSUS_AGREEMENT_GATES)" --corpus Ballroom "$(BALLROOM_BPM_LOG)" "$(BTT_BALLROOM_LOG)" --corpus FiloBass "$(FILOBASS_BPM_LOG)" "$(BTT_FILOBASS_LOG)" --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_GTZAN_RHYTHM_LOG)"

test-inspect-tempo-tracker-consensus: tests/test_inspect_tempo_tracker_consensus.py scripts/inspect_tempo_tracker_consensus.py
	$(PYTHON) tests/test_inspect_tempo_tracker_consensus.py

inspect-three-tempo-tracker-consensus: scripts/inspect_three_tempo_tracker_consensus.py $(BALLROOM_BPM_LOG) $(BTT_BALLROOM_LOG) $(BEAT_THIS_BALLROOM_LOG) $(FILOBASS_BPM_LOG) $(BTT_FILOBASS_LOG) $(BEAT_THIS_FILOBASS_LOG) $(GTZAN_RHYTHM_BPM_LOG) $(BTT_GTZAN_RHYTHM_LOG) $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/inspect_three_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --corpus Ballroom "$(BALLROOM_BPM_LOG)" "$(BTT_BALLROOM_LOG)" "$(BEAT_THIS_BALLROOM_LOG)" --corpus FiloBass "$(FILOBASS_BPM_LOG)" "$(BTT_FILOBASS_LOG)" "$(BEAT_THIS_FILOBASS_LOG)" --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_GTZAN_RHYTHM_LOG)" "$(BEAT_THIS_DIAGNOSTIC_LOG)" --output "$(THREE_TEMPO_TRACKER_CONSENSUS_LOG)"
	cat "$(THREE_TEMPO_TRACKER_CONSENSUS_LOG)"

inspect-high-tempo-three-tracker-consensus: scripts/inspect_three_tempo_tracker_consensus.py $(GTZAN_RHYTHM_BPM_LOG) $(BTT_HIGH_TEMPO_GTZAN_LOG) $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/inspect_three_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --min-expected 150 --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_HIGH_TEMPO_GTZAN_LOG)" "$(BEAT_THIS_DIAGNOSTIC_LOG)" --output "$(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)"
	cat "$(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)"

test-inspect-three-tempo-tracker-consensus: tests/test_inspect_three_tempo_tracker_consensus.py scripts/inspect_three_tempo_tracker_consensus.py
	$(PYTHON) tests/test_inspect_three_tempo_tracker_consensus.py

measure-permissive-beat-tracker-high-tempo: measure-permissive-beat-tracker-high-tempo-ballroom measure-permissive-beat-tracker-high-tempo-filobass measure-permissive-beat-tracker-high-tempo-gtzan-rhythm

measure-permissive-beat-tracker-high-tempo-ballroom: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(BALLROOM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_BALLROOM_LOG)"

measure-permissive-beat-tracker-high-tempo-filobass: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(FILOBASS_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_FILOBASS_LOG)"

measure-permissive-beat-tracker-high-tempo-gtzan-rhythm: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_GTZAN_LOG)"

.PHONY: test-extract-btt-range-sweep measure-permissive-beat-tracker-tempo-chunk merge-permissive-beat-tracker-tempo-chunks extract-permissive-beat-tracker-high-tempo-gtzan-rhythm
test-extract-btt-range-sweep: tests/test_extract_btt_range_sweep.py scripts/extract_btt_range_sweep.py
	$(PYTHON) tests/test_extract_btt_range_sweep.py

measure-permissive-beat-tracker-tempo-chunk: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(BTT_TEMPO_CHUNK_ROOT)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" --start-index "$(BTT_TEMPO_CHUNK_START)" --limit "$(BTT_TEMPO_CHUNK_LIMIT)" > "$(BTT_TEMPO_CHUNK_OUTPUT)"

merge-permissive-beat-tracker-tempo-chunks:
	cat $(BTT_TEMPO_CHUNK_INPUTS) > "$(BTT_TEMPO_CHUNK_OUTPUT)"

extract-permissive-beat-tracker-high-tempo-gtzan-rhythm: scripts/extract_btt_range_sweep.py $(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)
	$(PYTHON) scripts/extract_btt_range_sweep.py --input "$(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)" --output "$(BTT_HIGH_TEMPO_GTZAN_LOG)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)"

summarize-permissive-beat-tracker-high-tempo: scripts/inspect_tempo_confidence_calibration.py $(BTT_HIGH_TEMPO_BALLROOM_LOG) $(BTT_HIGH_TEMPO_FILOBASS_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_HIGH_TEMPO_BALLROOM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_HIGH_TEMPO_FILOBASS_LOG)"

summarize-permissive-beat-tracker: scripts/inspect_tempo_confidence_calibration.py $(BTT_BALLROOM_LOG) $(BTT_FILOBASS_LOG) $(BTT_EGMD_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_BALLROOM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_FILOBASS_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_EGMD_LOG)"

inspect-live-permissive-tracker: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

.PHONY: inspect-live-permissive-tracker-borderline
inspect-live-permissive-tracker-borderline: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" --details-min-confidence "$(LIVE_BTT_DETAILS_MIN_CONFIDENCE)" --details-max-confidence "$(LIVE_BTT_DETAILS_MAX_CONFIDENCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" --details-min-confidence "$(LIVE_BTT_DETAILS_MIN_CONFIDENCE)" --details-max-confidence "$(LIVE_BTT_DETAILS_MAX_CONFIDENCE)" "$(FILOBASS_BPM_LOG)"

.PHONY: inspect-live-high-tempo-tracker
inspect-live-high-tempo-tracker: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field high_backend_raw --confidence-field high_backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field high_backend_raw --confidence-field high_backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

inspect-beat-tracker-backends: scripts/inspect_beat_tracker_backends.py
	$(PYTHON) scripts/inspect_beat_tracker_backends.py

analyze-bpm-diagnostics: analyze-egmd-bpm

test-core-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_core_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-visualizer-renderer test-analyzer-internal test-analyzer-smoke test-analyzer-cases test-analyzer-midi-ranges test-analyzer-urmp test-analyzer-musicnet test-analyzer-multtipop test-analyzer-guitarset test-analyzer-maestro test-analyzer-egmd

ANALYSIS_SCRIPT_TEST_TARGETS := inspect-real-dataset-catalog inspect-real-goal-coverage test-musicnet-remote test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-synthsod-remote test-synthsod-archive-extract test-synthsod-inspector test-synthsod-prepare test-polyvocal-inspector test-polyvocal-prepare test-prepared-multitrack-inspector test-prepared-multitrack-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-drum-sample-prepare test-hf-drum-kit-prepare test-idmt-drums-prepare test-mdb-drums-prepare test-star-drums-prepare test-medley-solos-prepare test-maps-piano-prepare test-bach10-mf0-synth-prepare test-instrument-sample-attribute-summary test-instrument-sample-owner-buckets test-filter-instrument-attribute-rows test-filter-drum-attribute-rows test-instrument-owner-patterns test-refresh-analyzer-detected-attribute-rows test-print-analyzer-detected-attributes test-analyzer-pattern-report test-measure-analyzer-patterns-target test-build-sharded-tsv test-drum-sample-shard-check test-egmd-shard-check test-maestro-shard-check test-instrument-family-shard-check test-musicnet-shard-check test-real-note-full-mix-shard-check test-real-note-sample-shard-check test-guitarset-shard-check test-philharmonia-prepare test-good-sounds-prepare test-iowa-piano-prepare test-iowa-zip-prepare test-idmt-bass-lines-prepare test-idmt-guitar-prepare test-tinysol-prepare test-vocadito-prepare test-vocalset-prepare test-guitar-fretboard-note-prepare test-guitar-techs-prepare test-guitar-techs-chord-prepare test-guitar-chord-mix-prepare test-gaps-guitar-prepare test-guitarset-miss-analysis test-guitarset-attribute-summary test-guitarset-attribute-buckets test-guitarset-attribute-patterns test-guitar-chord-recovery-analysis test-guitar-primary-order-analysis test-guitar-chord-extra-components-analysis test-real-note-miss-analysis test-real-note-attribute-summary test-real-note-attribute-buckets test-real-note-attribute-patterns test-real-note-attribute-rule test-real-note-display-shadow-eval test-egmd-miss-analysis test-egmd-drum-attribute-summary test-egmd-drum-recovery-eval test-drum-debug-row-analysis test-drum-primary-analysis test-drum-gate-matrix-summary test-drum-active-threshold-simulation test-drum-active-false-summary test-drum-active-false-patterns test-real-goal-script android-check
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-rule-flag-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-vocal-exact-note-cross-corpus
ANALYSIS_SCRIPT_TEST_TARGETS += test-maps-piano-attribute-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-compare-drum-gate-summaries
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-octave-display-aliases
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-vocal-display-fallback-eval
ANALYSIS_SCRIPT_TEST_TARGETS += test-detector-route-report-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-sample-skip-patterns
ANALYSIS_SCRIPT_TEST_TARGETS += test-sample-manifest-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-drum-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-real-note-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-detector-coverage-candidates test-compare-drum-primary-scores
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-good-sounds-archive-coverage
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-polyphonic-candidate-capacity test-inspect-harmonic-product-octave-evidence test-detection-accuracy-report test-summarize-isolated-guitar-visual
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-tempo-candidate-feasibility
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-urmp-bass-timing
ANALYSIS_SCRIPT_TEST_TARGETS += test-search-egmd-false-positive-caps
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-drum-false-positive-caps
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-drum-false-positive-contexts
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-chord-primary-components

test-drum-sample-shard-check: tests/test_check_drum_sample_shards.py scripts/check_drum_sample_shards.py
	$(PYTHON) tests/test_check_drum_sample_shards.py

test-maps-piano-attribute-summary: tests/test_analyze_maps_piano_attributes.py scripts/analyze_maps_piano_attributes.py
	$(PYTHON) tests/test_analyze_maps_piano_attributes.py

test-instrument-family-attribute-summary: tests/test_summarize_instrument_family_attributes.py scripts/summarize_instrument_family_attributes.py
	$(PYTHON) tests/test_summarize_instrument_family_attributes.py

test-inspect-drum-candidate-rows: tests/test_inspect_drum_candidate_rows.py scripts/inspect_drum_candidate_rows.py
	$(PYTHON) tests/test_inspect_drum_candidate_rows.py

test-inspect-real-note-candidate-rows: tests/test_inspect_real_note_candidate_rows.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_real_note_candidate_rows.py

test-inspect-detector-coverage-candidates: tests/test_inspect_detector_coverage_candidates.py scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_detector_coverage_candidates.py

test-inspect-good-sounds-archive-coverage: tests/test_inspect_good_sounds_archive_coverage.py scripts/inspect_good_sounds_archive_coverage.py scripts/prepare_good_sounds_samples.py
	$(PYTHON) tests/test_inspect_good_sounds_archive_coverage.py

test-egmd-shard-check: tests/test_check_egmd_shards.py scripts/check_egmd_shards.py
	$(PYTHON) tests/test_check_egmd_shards.py

test-maestro-shard-check: tests/test_check_maestro_shards.py scripts/check_maestro_shards.py
	$(PYTHON) tests/test_check_maestro_shards.py

test-instrument-family-shard-check: tests/test_check_instrument_family_shards.py scripts/check_instrument_family_shards.py
	$(PYTHON) tests/test_check_instrument_family_shards.py

test-musicnet-shard-check: tests/test_check_musicnet_shards.py scripts/check_musicnet_shards.py
	$(PYTHON) tests/test_check_musicnet_shards.py

test-real-note-full-mix-shard-check: tests/test_check_real_note_full_mix_shards.py scripts/check_real_note_full_mix_shards.py
	$(PYTHON) tests/test_check_real_note_full_mix_shards.py

test-real-note-sample-shard-check: tests/test_check_real_note_sample_shards.py scripts/check_real_note_sample_shards.py
	$(PYTHON) tests/test_check_real_note_sample_shards.py

test-guitarset-shard-check: tests/test_check_guitarset_shards.py scripts/check_guitarset_shards.py
	$(PYTHON) tests/test_check_guitarset_shards.py

DRUM_PRIMARY_ROUTE_EXPECTED ?= hihat
DRUM_PRIMARY_ROUTE_PRIMARY ?= none
DRUM_PRIMARY_ROUTE_LIMIT ?= 5

.PHONY: inspect-drum-primary-route
inspect-drum-primary-route: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/inspect_drum_primary_route.py
	$(PYTHON) scripts/inspect_drum_primary_route.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --expected "$(DRUM_PRIMARY_ROUTE_EXPECTED)" --primary "$(DRUM_PRIMARY_ROUTE_PRIMARY)" --limit "$(DRUM_PRIMARY_ROUTE_LIMIT)"

.PHONY: summarize-drum-primary-routes
summarize-drum-primary-routes: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/summarize_drum_primary_routes.py
	$(PYTHON) scripts/summarize_drum_primary_routes.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"

.PHONY: inspect-analyzer-ride-hihat
inspect-analyzer-ride-hihat: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "ride_hihat"

.PHONY: inspect-fret-zealot
inspect-fret-zealot: scripts/inspect_fret_zealot.py
	$(PYTHON) scripts/inspect_fret_zealot.py

.PHONY: inspect-fret-zealot-packet
inspect-fret-zealot-packet: scripts/inspect_source_range.py src/fret_control.cpp
	$(PYTHON) scripts/inspect_source_range.py src/fret_control.cpp 390 500

.PHONY: inspect-fret-zealot-integration
inspect-fret-zealot-integration: scripts/inspect_fret_zealot_integration.py
	$(PYTHON) scripts/inspect_fret_zealot_integration.py

.PHONY: inspect-fret-zealot-frames
inspect-fret-zealot-frames: scripts/inspect_fret_zealot_frames.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java
	$(PYTHON) scripts/inspect_fret_zealot_frames.py

.PHONY: inspect-fret-zealot-update-path
inspect-fret-zealot-update-path: scripts/inspect_source_range.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java
	$(PYTHON) scripts/inspect_source_range.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java 90 250

.PHONY: inspect-fret-zealot-android-tests
inspect-fret-zealot-android-tests: scripts/inspect_source_range.py tests/check_android_project.py
	$(PYTHON) scripts/inspect_source_range.py tests/check_android_project.py 1 90

.PHONY: test-fret-zealot-android-dispatch
test-fret-zealot-android-dispatch: tests/check_android_project.py
	$(PYTHON) tests/check_android_project.py

.PHONY: list-android-make-targets
list-android-make-targets: scripts/list_android_make_targets.py Makefile
	$(PYTHON) scripts/list_android_make_targets.py

.PHONY: inspect-android-native-cmake
inspect-android-native-cmake: scripts/inspect_source_range.py android/app/src/main/cpp/CMakeLists.txt
	$(PYTHON) scripts/inspect_source_range.py android/app/src/main/cpp/CMakeLists.txt 1 220

.PHONY: inspect-basic-pitch-android-guards
inspect-basic-pitch-android-guards: scripts/inspect_basic_pitch_android_guards.py
	$(PYTHON) scripts/inspect_basic_pitch_android_guards.py

.PHONY: inspect-basic-pitch-runtime
inspect-basic-pitch-runtime: scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.cpp
	$(PYTHON) scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.cpp 1 230

.PHONY: inspect-basic-pitch-runtime-header
inspect-basic-pitch-runtime-header: scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.hpp
	$(PYTHON) scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.hpp 1 180

.PHONY: repository-state
repository-state: scripts/report_repository_state.sh
	$(SHELL) scripts/report_repository_state.sh

.PHONY: report-analyzer-case-processes
report-analyzer-case-processes: scripts/report_analyzer_case_processes.sh
	$(SHELL) scripts/report_analyzer_case_processes.sh

.PHONY: report-drum-pattern-processes
report-drum-pattern-processes: scripts/report_drum_pattern_processes.sh
	$(SHELL) scripts/report_drum_pattern_processes.sh

.PHONY: report-egmd-processes
report-egmd-processes: scripts/report_egmd_processes.sh
	$(SHELL) scripts/report_egmd_processes.sh

.PHONY: wait-for-drum-pattern-processes
wait-for-drum-pattern-processes: scripts/wait_for_drum_pattern_processes.py
	$(PYTHON) scripts/wait_for_drum_pattern_processes.py

.PHONY: analyze-tom-snare-primary
analyze-tom-snare-primary: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/analyze_tom_snare_primary.py
	$(PYTHON) scripts/analyze_tom_snare_primary.py

.PHONY: inspect-analyzer-tom-snare
inspect-analyzer-tom-snare: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "tom_from_snare_primary_recovery"

.PHONY: analyze-hihat-none
analyze-hihat-none: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/analyze_hihat_none.py
	$(PYTHON) scripts/analyze_hihat_none.py

.PHONY: inspect-drum-debug-flags
inspect-drum-debug-flags: scripts/inspect_analyzer_section.py src/analyzer.hpp
	$(PYTHON) scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "DrumDebug"

.PHONY: inspect-analyzer-hihat-activation
inspect-analyzer-hihat-activation: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "drum_level_[HiHat] ="

.PHONY: inspect-analyzer-hihat-caps
inspect-analyzer-hihat-caps: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "cap_drum_level(HiHat"

.PHONY: inspect-analyzer-drum-activation-block
inspect-analyzer-drum-activation-block: scripts/inspect_source_range.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_source_range.py src/analyzer.cpp 31700 32200

.PHONY: inspect-analyzer-drum-transient
inspect-analyzer-drum-transient: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "drum_transient ="

.PHONY: inspect-analyzer-drum-transient-threshold
inspect-analyzer-drum-transient-threshold: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "kDrumTransientRatio"

.PHONY: evaluate-hihat-activation-candidate
evaluate-hihat-activation-candidate: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/evaluate_hihat_activation_candidate.py
	$(PYTHON) scripts/evaluate_hihat_activation_candidate.py

.PHONY: inspect-mdb-drum-shards
inspect-mdb-drum-shards: scripts/inspect_mdb_drum_shards.py
	$(PYTHON) scripts/inspect_mdb_drum_shards.py

.PHONY: inspect-egmd-test-options
inspect-egmd-test-options: scripts/inspect_egmd_test_options.py tests/analyzer_egmd.cpp
	$(PYTHON) scripts/inspect_egmd_test_options.py

.PHONY: inspect-mdb-hihat-misses
inspect-mdb-hihat-misses: scripts/inspect_mdb_hihat_misses.py
	$(PYTHON) scripts/inspect_mdb_hihat_misses.py

.PHONY: mine-mdb-hihat-selectors
mine-mdb-hihat-selectors: analyze-mdb-drum-windows scripts/mine_mdb_hihat_selectors.py
	$(PYTHON) scripts/mine_mdb_hihat_selectors.py

.PHONY: inspect-mdb-drum-target
inspect-mdb-drum-target: scripts/inspect_source_range.py Makefile
	$(PYTHON) scripts/inspect_source_range.py Makefile 3440 3520

.PHONY: inspect-egmd-recovery-evaluator
inspect-egmd-recovery-evaluator: scripts/inspect_source_range.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) scripts/inspect_source_range.py scripts/evaluate_egmd_drum_recovery.py 1 360

.PHONY: stop-analyzer-case-processes
stop-analyzer-case-processes: scripts/stop_analyzer_case_processes.py
	$(PYTHON) scripts/stop_analyzer_case_processes.py

.PHONY: inspect-fret-zealot-dispatch
inspect-fret-zealot-dispatch: scripts/inspect_fret_zealot_dispatch.py
	$(PYTHON) scripts/inspect_fret_zealot_dispatch.py

test-analysis-scripts-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_analysis_scripts_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(ANALYSIS_SCRIPT_TEST_TARGETS)

test-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-analysis-scripts-parallel test-core-parallel test-standalone

TEST_FAST_TARGETS := test-parallel test-detector-samples-parallel test-fret-control test-real-goal-fixture test-fixtures-parallel-isolated

test: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_fast $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(TEST_BINS) $(TEST_FAST_TARGETS)

inspect-real-dataset-catalog: tests/inspect_real_dataset_catalog.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md
	$(PYTHON) tests/inspect_real_dataset_catalog.py

inspect-real-goal-coverage: tests/inspect_real_goal_coverage.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md README.md Makefile src/analyzer.cpp tests/analyzer_urmp.cpp tests/inspect_urmp_dataset.py tests/generate_direct_fit_small_fixture.py tests/analyzer_musicnet.cpp tests/analyzer_multtipop.cpp tests/analyzer_guitarset.cpp tests/prepare_guitarset_manifest.py tests/analyzer_maestro.cpp tests/analyzer_egmd.cpp tests/run_real_goal_gate.py tests/print_real_dataset_sources.py tests/inspect_musicnet_remote.py tests/inspect_medleydb_dataset.py tests/prepare_medleydb_musicnet_fixture.py tests/inspect_musdb_dataset.py tests/inspect_slakh_dataset.py tests/prepare_slakh_musicnet_fixture.py tests/inspect_choralsynth_dataset.py tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_cocochorales_dataset.py tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_synthsod_remote.py tests/prepare_synthsod_archives.py tests/inspect_synthsod_dataset.py tests/prepare_synthsod_musicnet_fixture.py tests/generate_synthsod_fixture.py tests/inspect_polyvocal_dataset.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py tests/prepare_prepared_multitrack_musicnet_fixture.py tests/generate_prepared_multitrack_fixture.py tests/inspect_multtipop_dataset.py tests/inspect_spheres_dataset.py tests/inspect_guitarset_dataset.py
	$(PYTHON) tests/inspect_real_goal_coverage.py

real-dataset-sources: tests/print_real_dataset_sources.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md
	$(PYTHON) tests/print_real_dataset_sources.py

inspect-real-medleydb: tests/inspect_medleydb_dataset.py
	$(PYTHON) tests/inspect_medleydb_dataset.py

inspect-real-musdb: tests/inspect_musdb_dataset.py
	$(PYTHON) tests/inspect_musdb_dataset.py

inspect-real-slakh: tests/inspect_slakh_dataset.py
	$(PYTHON) tests/inspect_slakh_dataset.py

inspect-real-choralsynth: tests/inspect_choralsynth_dataset.py
	$(PYTHON) tests/inspect_choralsynth_dataset.py

inspect-real-cocochorales: tests/inspect_cocochorales_dataset.py
	$(PYTHON) tests/inspect_cocochorales_dataset.py

inspect-real-synthsod-remote: tests/inspect_synthsod_remote.py
	$(PYTHON) tests/inspect_synthsod_remote.py

inspect-real-synthsod: tests/inspect_synthsod_dataset.py
	$(PYTHON) tests/inspect_synthsod_dataset.py

extract-real-synthsod-archives: tests/prepare_synthsod_archives.py | $(BUILD_DIR)
	$(PYTHON) tests/prepare_synthsod_archives.py $(SYNTHSOD_ARCHIVE_EXTRACT_DIR)

inspect-real-polyvocal: tests/inspect_polyvocal_dataset.py
	$(PYTHON) tests/inspect_polyvocal_dataset.py

inspect-real-prepared-multitrack: tests/inspect_prepared_multitrack_dataset.py
	$(PYTHON) tests/inspect_prepared_multitrack_dataset.py

inspect-real-multtipop: tests/inspect_multtipop_dataset.py
	$(PYTHON) tests/inspect_multtipop_dataset.py

inspect-real-spheres: tests/inspect_spheres_dataset.py
	$(PYTHON) tests/inspect_spheres_dataset.py

inspect-real-guitarset: tests/inspect_guitarset_dataset.py
	$(PYTHON) tests/inspect_guitarset_dataset.py

inspect-real-maestro: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_maestro

inspect-real-egmd: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_egmd

inspect-real-musicnet: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

inspect-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=330 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1320 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

inspect-real-musicnet-remote: tests/inspect_musicnet_remote.py
	$(PYTHON) tests/inspect_musicnet_remote.py

test-musicnet-remote: tests/test_inspect_musicnet_remote.py tests/inspect_musicnet_remote.py
	$(PYTHON) tests/test_inspect_musicnet_remote.py

test-medleydb-inspector: tests/test_inspect_medleydb_dataset.py tests/inspect_medleydb_dataset.py
	$(PYTHON) tests/test_inspect_medleydb_dataset.py

test-medleydb-prepare: tests/test_prepare_medleydb_musicnet_fixture.py tests/prepare_medleydb_musicnet_fixture.py tests/inspect_medleydb_dataset.py tests/generate_medleydb_fixture.py
	$(PYTHON) tests/test_prepare_medleydb_musicnet_fixture.py

test-musdb-inspector: tests/test_inspect_musdb_dataset.py tests/inspect_musdb_dataset.py tests/generate_musdb_fixture.py
	$(PYTHON) tests/test_inspect_musdb_dataset.py

test-slakh-inspector: tests/test_inspect_slakh_dataset.py tests/inspect_slakh_dataset.py tests/generate_slakh_fixture.py
	$(PYTHON) tests/test_inspect_slakh_dataset.py

test-slakh-prepare: tests/test_prepare_slakh_musicnet_fixture.py tests/prepare_slakh_musicnet_fixture.py tests/inspect_slakh_dataset.py tests/generate_slakh_fixture.py
	$(PYTHON) tests/test_prepare_slakh_musicnet_fixture.py

test-choralsynth-inspector: tests/test_inspect_choralsynth_dataset.py tests/inspect_choralsynth_dataset.py tests/generate_choralsynth_fixture.py
	$(PYTHON) tests/test_inspect_choralsynth_dataset.py

test-choralsynth-prepare: tests/test_prepare_choralsynth_musicnet_fixture.py tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_choralsynth_dataset.py tests/generate_choralsynth_fixture.py
	$(PYTHON) tests/test_prepare_choralsynth_musicnet_fixture.py

test-cocochorales-inspector: tests/test_inspect_cocochorales_dataset.py tests/inspect_cocochorales_dataset.py tests/generate_cocochorales_fixture.py
	$(PYTHON) tests/test_inspect_cocochorales_dataset.py

test-cocochorales-prepare: tests/test_prepare_cocochorales_musicnet_fixture.py tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_cocochorales_dataset.py tests/generate_cocochorales_fixture.py
	$(PYTHON) tests/test_prepare_cocochorales_musicnet_fixture.py

test-synthsod-remote: tests/test_inspect_synthsod_remote.py tests/inspect_synthsod_remote.py
	$(PYTHON) tests/test_inspect_synthsod_remote.py

test-synthsod-archive-extract: tests/test_prepare_synthsod_archives.py tests/prepare_synthsod_archives.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_prepare_synthsod_archives.py

test-synthsod-inspector: tests/test_inspect_synthsod_dataset.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_inspect_synthsod_dataset.py

test-synthsod-prepare: tests/test_prepare_synthsod_musicnet_fixture.py tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_prepare_synthsod_musicnet_fixture.py

test-polyvocal-inspector: tests/test_inspect_polyvocal_dataset.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_inspect_polyvocal_dataset.py

test-polyvocal-prepare: tests/test_prepare_polyvocal_musicnet_fixture.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_prepare_polyvocal_musicnet_fixture.py

test-prepared-multitrack-inspector: tests/test_inspect_prepared_multitrack_dataset.py tests/inspect_prepared_multitrack_dataset.py tests/generate_prepared_multitrack_fixture.py
	$(PYTHON) tests/test_inspect_prepared_multitrack_dataset.py

test-prepared-multitrack-prepare: tests/test_prepare_prepared_multitrack_musicnet_fixture.py tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py tests/generate_prepared_multitrack_fixture.py
	$(PYTHON) tests/test_prepare_prepared_multitrack_musicnet_fixture.py

test-multtipop-inspector: tests/test_inspect_multtipop_dataset.py tests/inspect_multtipop_dataset.py tests/generate_multtipop_fixture.py
	$(PYTHON) tests/test_inspect_multtipop_dataset.py

test-spheres-inspector: tests/test_inspect_spheres_dataset.py tests/inspect_spheres_dataset.py
	$(PYTHON) tests/test_inspect_spheres_dataset.py

test-guitarset-inspector: tests/test_inspect_guitarset_dataset.py tests/inspect_guitarset_dataset.py tests/generate_guitarset_fixture.py
	$(PYTHON) tests/test_inspect_guitarset_dataset.py

test-urmp-inspector: tests/test_inspect_urmp_dataset.py tests/inspect_urmp_dataset.py
	$(PYTHON) tests/test_inspect_urmp_dataset.py

test-drum-sample-prepare: tests/test_prepare_drum_samples.py scripts/prepare_drum_samples.py
	$(PYTHON) tests/test_prepare_drum_samples.py








test-drum-sample-skip-patterns: tests/test_inspect_drum_sample_skip_patterns.py scripts/inspect_drum_sample_skip_patterns.py scripts/prepare_drum_samples.py
	$(PYTHON) tests/test_inspect_drum_sample_skip_patterns.py

test-hf-drum-kit-prepare: tests/test_prepare_hf_drum_kit_samples.py scripts/prepare_hf_drum_kit_samples.py
	$(PYTHON) tests/test_prepare_hf_drum_kit_samples.py

test-idmt-drums-prepare: tests/test_prepare_idmt_drums_samples.py scripts/prepare_idmt_drums_samples.py
	$(PYTHON) tests/test_prepare_idmt_drums_samples.py

test-mdb-drums-prepare: tests/test_prepare_mdb_drums_samples.py scripts/prepare_mdb_drums_samples.py
	$(PYTHON) tests/test_prepare_mdb_drums_samples.py

test-star-drums-prepare: tests/test_prepare_star_drums_samples.py scripts/prepare_star_drums_samples.py
	$(PYTHON) tests/test_prepare_star_drums_samples.py

test-medley-solos-prepare: tests/test_prepare_medley_solos_samples.py scripts/prepare_medley_solos_samples.py
	$(PYTHON) tests/test_prepare_medley_solos_samples.py

test-maps-piano-prepare: tests/test_prepare_maps_piano_samples.py scripts/prepare_maps_piano_samples.py
	$(PYTHON) tests/test_prepare_maps_piano_samples.py

test-bach10-mf0-synth-prepare: tests/test_prepare_bach10_mf0_synth_musicnet_fixture.py scripts/prepare_bach10_mf0_synth_musicnet_fixture.py
	$(PYTHON) tests/test_prepare_bach10_mf0_synth_musicnet_fixture.py

test-philharmonia-prepare: tests/test_prepare_philharmonia_samples.py scripts/prepare_philharmonia_samples.py
	$(PYTHON) tests/test_prepare_philharmonia_samples.py

test-pitch-shifted-violin-prepare: tests/test_prepare_pitch_shifted_violin_samples.py scripts/prepare_pitch_shifted_violin_samples.py
	$(PYTHON) tests/test_prepare_pitch_shifted_violin_samples.py

test-good-sounds-prepare: tests/test_prepare_good_sounds_samples.py scripts/prepare_good_sounds_samples.py
	$(PYTHON) tests/test_prepare_good_sounds_samples.py

test-iowa-piano-prepare: tests/test_prepare_iowa_piano_samples.py scripts/prepare_iowa_piano_samples.py
	$(PYTHON) tests/test_prepare_iowa_piano_samples.py

test-iowa-zip-prepare: tests/test_prepare_iowa_zip_samples.py scripts/prepare_iowa_zip_samples.py
	$(PYTHON) tests/test_prepare_iowa_zip_samples.py

test-idmt-bass-lines-prepare: tests/test_prepare_idmt_bass_lines_samples.py scripts/prepare_idmt_bass_lines_samples.py
	$(PYTHON) tests/test_prepare_idmt_bass_lines_samples.py

test-idmt-guitar-prepare: tests/test_prepare_idmt_guitar_samples.py scripts/prepare_idmt_guitar_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_idmt_guitar_samples.py

test-tinysol-prepare: tests/test_prepare_tinysol_samples.py scripts/prepare_tinysol_samples.py
	$(PYTHON) tests/test_prepare_tinysol_samples.py

test-vocadito-prepare: tests/test_prepare_vocadito_samples.py scripts/prepare_vocadito_samples.py
	$(PYTHON) tests/test_prepare_vocadito_samples.py

test-vocalset-prepare: tests/test_prepare_vocalset_samples.py scripts/prepare_vocalset_samples.py
	$(PYTHON) tests/test_prepare_vocalset_samples.py

test-guitar-fretboard-note-prepare: tests/test_prepare_guitar_fretboard_notes.py scripts/prepare_guitar_fretboard_notes.py
	$(PYTHON) tests/test_prepare_guitar_fretboard_notes.py

test-guitar-techs-prepare: tests/test_prepare_guitar_techs_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_guitar_techs_samples.py

test-guitar-techs-chord-prepare: tests/test_prepare_guitar_techs_chord_samples.py scripts/prepare_guitar_techs_chord_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_guitar_techs_chord_samples.py

test-guitar-chord-mix-prepare: tests/test_prepare_hf_guitar_chord_mix.py scripts/prepare_hf_guitar_chord_mix.py
	$(PYTHON) tests/test_prepare_hf_guitar_chord_mix.py

test-gaps-guitar-prepare: tests/test_prepare_gaps_guitar_samples.py scripts/prepare_gaps_guitar_samples.py
	$(PYTHON) tests/test_prepare_gaps_guitar_samples.py

test-guitarset-miss-analysis: tests/test_analyze_guitarset_misses.py scripts/analyze_guitarset_misses.py
	$(PYTHON) tests/test_analyze_guitarset_misses.py

test-guitarset-attribute-summary: tests/test_summarize_guitarset_attributes.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_summarize_guitarset_attributes.py

test-guitarset-attribute-buckets: tests/test_inspect_guitarset_attribute_buckets.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_inspect_guitarset_attribute_buckets.py

test-guitarset-attribute-patterns: tests/test_find_guitarset_attribute_patterns.py scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_find_guitarset_attribute_patterns.py

test-guitar-chord-recovery-analysis: tests/test_analyze_guitar_chord_recovery.py scripts/analyze_guitar_chord_recovery.py
	$(PYTHON) tests/test_analyze_guitar_chord_recovery.py

test-guitar-primary-order-analysis: tests/test_analyze_guitar_primary_order.py scripts/analyze_guitar_primary_order.py
	$(PYTHON) tests/test_analyze_guitar_primary_order.py

test-guitar-chord-extra-components-analysis: tests/test_analyze_guitar_chord_extra_components.py scripts/analyze_guitar_chord_extra_components.py
	$(PYTHON) tests/test_analyze_guitar_chord_extra_components.py

test-real-note-miss-analysis: tests/test_analyze_real_note_misses.py scripts/analyze_real_note_misses.py
	$(PYTHON) tests/test_analyze_real_note_misses.py

test-real-note-attribute-summary: tests/test_summarize_real_note_attributes.py scripts/summarize_real_note_attributes.py
	$(PYTHON) tests/test_summarize_real_note_attributes.py

test-good-sounds-bass-miss-inspector: tests/test_inspect_good_sounds_bass_misses.py scripts/inspect_good_sounds_bass_misses.py
	$(PYTHON) tests/test_inspect_good_sounds_bass_misses.py

test-real-note-attribute-buckets: tests/test_inspect_real_note_attribute_buckets.py scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) tests/test_inspect_real_note_attribute_buckets.py

test-real-note-attribute-patterns: tests/test_find_real_note_attribute_patterns.py scripts/find_real_note_attribute_patterns.py
	$(PYTHON) tests/test_find_real_note_attribute_patterns.py

test-real-note-attribute-rule: tests/test_measure_real_note_attribute_rule.py scripts/measure_real_note_attribute_rule.py
	$(PYTHON) tests/test_measure_real_note_attribute_rule.py

test-real-note-display-shadow-eval: tests/test_evaluate_real_note_display_shadow.py scripts/evaluate_real_note_display_shadow.py
	$(PYTHON) tests/test_evaluate_real_note_display_shadow.py

test-real-note-vocal-display-fallback-eval: tests/test_evaluate_real_note_vocal_display_fallback.py scripts/evaluate_real_note_vocal_display_fallback.py
	$(PYTHON) tests/test_evaluate_real_note_vocal_display_fallback.py

test-real-note-octave-display-aliases: tests/test_measure_real_note_octave_display_aliases.py scripts/measure_real_note_octave_display_aliases.py
	$(PYTHON) tests/test_measure_real_note_octave_display_aliases.py

test-sample-manifest-summary: tests/test_summarize_sample_manifests.py scripts/summarize_sample_manifests.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) test_sample_manifest_summary $(PYTHON) tests/test_summarize_sample_manifests.py

test-instrument-sample-attribute-summary: tests/test_summarize_instrument_sample_attributes.py scripts/summarize_instrument_sample_attributes.py
	$(PYTHON) tests/test_summarize_instrument_sample_attributes.py

test-instrument-sample-owner-buckets: tests/test_inspect_instrument_sample_owner_buckets.py scripts/inspect_instrument_sample_owner_buckets.py
	$(PYTHON) tests/test_inspect_instrument_sample_owner_buckets.py

test-filter-instrument-attribute-rows: tests/test_filter_instrument_attribute_rows.py scripts/filter_instrument_attribute_rows.py
	$(PYTHON) tests/test_filter_instrument_attribute_rows.py

test-filter-drum-attribute-rows: tests/test_filter_drum_attribute_rows.py scripts/filter_drum_attribute_rows.py
	$(PYTHON) tests/test_filter_drum_attribute_rows.py

test-instrument-owner-patterns: tests/test_find_instrument_owner_patterns.py scripts/find_instrument_owner_patterns.py
	$(PYTHON) tests/test_find_instrument_owner_patterns.py

test-refresh-analyzer-detected-attribute-rows: tests/test_refresh_analyzer_detected_attribute_rows.py scripts/refresh_analyzer_detected_attribute_rows.py
	$(PYTHON) tests/test_refresh_analyzer_detected_attribute_rows.py

test-print-analyzer-detected-attributes: tests/test_print_analyzer_detected_attributes.py scripts/print_analyzer_detected_attributes.py
	$(PYTHON) tests/test_print_analyzer_detected_attributes.py

test-analyzer-pattern-report: tests/test_report_analyzer_attribute_patterns.py scripts/report_analyzer_attribute_patterns.py
	$(PYTHON) tests/test_report_analyzer_attribute_patterns.py

test-detector-route-report-summary: tests/test_summarize_detector_route_report.py scripts/summarize_detector_route_report.py
	$(PYTHON) tests/test_summarize_detector_route_report.py

test-measure-analyzer-patterns-target: tests/test_measure_analyzer_patterns_makefile.py Makefile
	$(PYTHON) tests/test_measure_analyzer_patterns_makefile.py

test-build-sharded-tsv: tests/test_build_sharded_tsv.py scripts/build_sharded_tsv.sh
	$(PYTHON) tests/test_build_sharded_tsv.py

test-egmd-miss-analysis: tests/test_analyze_egmd_misses.py scripts/analyze_egmd_misses.py
	$(PYTHON) tests/test_analyze_egmd_misses.py

test-egmd-drum-attribute-summary: tests/test_summarize_egmd_drum_attributes.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) tests/test_summarize_egmd_drum_attributes.py

.PHONY: test-egmd-drum-recovery-eval evaluate-mdb-drum-recovery evaluate-star-drum-recovery
test-egmd-drum-recovery-eval: tests/test_evaluate_egmd_drum_recovery.py scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) tests/test_evaluate_egmd_drum_recovery.py

.PHONY: test-search-egmd-false-positive-caps
test-search-egmd-false-positive-caps: tests/test_search_egmd_false_positive_caps.py scripts/search_egmd_false_positive_caps.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) tests/test_search_egmd_false_positive_caps.py

evaluate-mdb-drum-recovery: analyze-mdb-drums-misses scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(MDB_DRUMS_MISS_LOG)" $(DRUM_RECOVERY_ARGS)

evaluate-star-drum-recovery: analyze-star-drums-misses scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(STAR_DRUMS_MISS_LOG)" $(DRUM_RECOVERY_ARGS)

test-drum-debug-row-analysis: tests/test_analyze_drum_debug_rows.py scripts/analyze_drum_debug_rows.py
	$(PYTHON) tests/test_analyze_drum_debug_rows.py

test-drum-primary-analysis: tests/test_analyze_drum_primary_debug.py tests/test_evaluate_drum_rule_grid.py tests/test_evaluate_drum_tom_bleed_caps.py tests/test_find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py scripts/evaluate_drum_rule_grid.py scripts/evaluate_drum_tom_bleed_caps.py scripts/find_drum_attribute_patterns.py
	$(PYTHON) tests/test_analyze_drum_primary_debug.py
	$(PYTHON) tests/test_evaluate_drum_rule_grid.py
	$(PYTHON) tests/test_evaluate_drum_tom_bleed_caps.py
	$(PYTHON) tests/test_find_drum_attribute_patterns.py

test-drum-gate-matrix-summary: tests/test_summarize_drum_gate_matrix.py scripts/summarize_drum_gate_matrix.py
	$(PYTHON) tests/test_summarize_drum_gate_matrix.py

test-compare-drum-primary-scores: tests/test_compare_drum_primary_scores.py scripts/compare_drum_primary_scores.py
	$(PYTHON) tests/test_compare_drum_primary_scores.py

test-compare-drum-gate-summaries: tests/test_compare_drum_gate_summaries.py scripts/compare_drum_gate_summaries.py
	$(PYTHON) tests/test_compare_drum_gate_summaries.py

test-drum-active-threshold-simulation: tests/test_simulate_drum_active_thresholds.py scripts/simulate_drum_active_thresholds.py
	$(PYTHON) tests/test_simulate_drum_active_thresholds.py

test-drum-active-false-summary: tests/test_summarize_drum_active_false_rows.py scripts/summarize_drum_active_false_rows.py
	$(PYTHON) tests/test_summarize_drum_active_false_rows.py

test-drum-rule-flag-summary: tests/test_summarize_drum_rule_flags.py scripts/summarize_drum_rule_flags.py
	$(PYTHON) tests/test_summarize_drum_rule_flags.py

test-drum-active-false-patterns: tests/test_find_drum_active_false_patterns.py scripts/find_drum_active_false_patterns.py
	$(PYTHON) tests/test_find_drum_active_false_patterns.py

test-real-goal-script: tests/test_run_real_goal_gate.py tests/run_real_goal_gate.py
	$(PYTHON) tests/test_run_real_goal_gate.py

prepare-real-goal-fixtures-parallel: $(URMP_FIXTURE_ARCHIVE) tests/generate_musicnet_fixture.py tests/generate_medleydb_fixture.py tests/generate_musdb_fixture.py tests/generate_slakh_fixture.py tests/generate_choralsynth_fixture.py tests/generate_cocochorales_fixture.py tests/generate_synthsod_fixture.py tests/generate_polyvocal_fixture.py tests/generate_prepared_multitrack_fixture.py tests/generate_multtipop_fixture.py tests/generate_spheres_fixture.py tests/generate_guitarset_fixture.py tests/generate_maestro_fixture.py tests/generate_egmd_fixture.py scripts/run_with_duration.sh | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_FIXTURE_DIR)
	mkdir -p $(REAL_GOAL_FIXTURE_DIR)
	+$(RUN_WITH_DURATION) real_goal_fixture_generation_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_GOAL_FIXTURE_PREP_TARGETS)

prepare-real-goal-urmp-fixture: $(URMP_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(REAL_GOAL_FIXTURE_DIR)
	+$(MAKE) decode-urmp-fixture URMP_FIXTURE_DIR=$(REAL_GOAL_URMP_FIXTURE_DIR)

prepare-real-goal-musicnet-fixture: tests/generate_musicnet_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(REAL_GOAL_MUSICNET_FIXTURE_DIR)

prepare-real-goal-medleydb-fixture: tests/generate_medleydb_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)

prepare-real-goal-musdb-fixture: tests/generate_musdb_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_musdb_fixture.py $(REAL_GOAL_MUSDB_FIXTURE_DIR)

prepare-real-goal-slakh-fixture: tests/generate_slakh_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)

prepare-real-goal-choralsynth-fixture: tests/generate_choralsynth_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)

prepare-real-goal-cocochorales-fixture: tests/generate_cocochorales_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)

prepare-real-goal-synthsod-fixture: tests/generate_synthsod_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)

prepare-real-goal-polyvocal-fixture: tests/generate_polyvocal_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)

prepare-real-goal-prepared-multitrack-fixture: tests/generate_prepared_multitrack_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)

prepare-real-goal-multtipop-fixture: tests/generate_multtipop_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio

prepare-real-goal-spheres-fixture: tests/generate_spheres_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_spheres_fixture.py $(REAL_GOAL_SPHERES_FIXTURE_DIR)

prepare-real-goal-guitarset-fixture: tests/generate_guitarset_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)

prepare-real-goal-maestro-fixture: tests/generate_maestro_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)

prepare-real-goal-egmd-fixture: tests/generate_egmd_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)

test-real-goal-fixture: $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd prepare-real-goal-fixtures-parallel tests/prepare_guitarset_manifest.py tests/run_real_goal_gate.py | $(BUILD_DIR)
	+MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)
	+MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-musicnet-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-medleydb-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_medleydb_fixture.py tests/prepare_medleydb_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	+MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) $(MAKE) test-real-medleydb-20

test-slakh-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_slakh_fixture.py tests/prepare_slakh_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	+MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) $(MAKE) test-real-slakh-20

test-choralsynth-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_choralsynth_fixture.py tests/prepare_choralsynth_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	+MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) $(MAKE) test-real-choralsynth-20

test-cocochorales-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_cocochorales_fixture.py tests/prepare_cocochorales_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	+MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) $(MAKE) test-real-cocochorales-20

test-synthsod-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_synthsod_fixture.py tests/prepare_synthsod_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	+MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores $(MAKE) test-real-synthsod-20

test-polyvocal-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_polyvocal_fixture.py tests/prepare_polyvocal_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	+MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 $(MAKE) test-real-polyvocal-20

test-prepared-multitrack-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_prepared_multitrack_fixture.py tests/prepare_prepared_multitrack_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	+MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) $(MAKE) test-real-prepared-multitrack-20

test-multtipop-audio-root-fixture: $(BUILD_DIR)/analyzer_multtipop tests/generate_multtipop_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT=$(REAL_GOAL_MULTTIPOP_AUDIO_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 $(BUILD_DIR)/analyzer_multtipop

test-guitarset-fixture: $(BUILD_DIR)/analyzer_guitarset tests/generate_guitarset_fixture.py tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT=100 $(BUILD_DIR)/analyzer_guitarset

test-maestro-fixture: $(BUILD_DIR)/analyzer_maestro tests/generate_maestro_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-egmd-fixture: $(BUILD_DIR)/analyzer_egmd tests/generate_egmd_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_EGMD_FIXTURE_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)
	MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=80 $(BUILD_DIR)/analyzer_egmd

test-bach10-fixture: $(BUILD_DIR)/analyzer_urmp tests/generate_bach10_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_bach10_fixture.py $(BACH10_FIXTURE_DIR)
	MUSIC_ANALYZER_URMP_ROOT=$(BACH10_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=10 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=40 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=4 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-direct-fit-small-fixture: $(BUILD_DIR)/analyzer_urmp $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(DIRECT_FIT_SMALL_FIXTURE_DIR)
	$(TAR) -xzf $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-direct-fit-small-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(DIRECT_FIT_SMALL_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=20 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=80 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=3 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-urmp-fixture: $(BUILD_DIR)/analyzer_urmp $(URMP_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-urmp-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp-full: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(BUILD_DIR)/analyzer_urmp

test-real-multitrack-20: test-real-urmp

test-real-multitrack-full: test-real-urmp-full

test-real-goal-20: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-real-goal-full: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py full "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

inspect-real-goal-20: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

inspect-real-goal-full: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py inspect-full "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-real-musicnet-20: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=330 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1320 $(BUILD_DIR)/analyzer_musicnet

.PHONY: download-real-urmp inspect-real-urmp-download prepare-real-urmp inspect-urmp-bass-timing test-inspect-urmp-bass-timing analyze-real-urmp-traits analyze-real-urmp-miss-traits summarize-real-urmp-miss-traits summarize-real-urmp-chord-miss-traits summarize-real-urmp-wrong-notes prepare-urmp-sax-exact-fixture measure-urmp-sax-exact measure-urmp-sax-full-mix find-urmp-sax-full-mix-row-confusion-patterns find-urmp-sax-full-mix-first-row-confusion-patterns find-urmp-good-sounds-sax-shared-routing-patterns analyze-urmp-sax-exact test-prepare-urmp-sax-exact-fixture test-urmp-download-scripts test-urmp-archive-extract download-real-musicnet inspect-real-musicnet-download prepare-real-musicnet inspect-downloaded-real-musicnet-20-traits analyze-downloaded-real-musicnet-recording analyze-downloaded-real-musicnet-chord-misses test-downloaded-real-musicnet-20 test-downloaded-real-musicnet-full test-musicnet-archive-extract test-run-musicnet-gate test-summarize-musicnet-attributes
download-real-urmp: $(URMP_ARCHIVE)

inspect-real-urmp-download: scripts/urmp_download_status.sh
	$(SHELL) scripts/urmp_download_status.sh "$(URMP_ARCHIVE)"

test-urmp-download-scripts: scripts/download_urmp_archive.sh scripts/urmp_download_status.sh tests/test_urmp_download_scripts.py
	$(PYTHON) -m pytest -q tests/test_urmp_download_scripts.py

prepare-real-urmp: $(URMP_ARCHIVE) scripts/extract_urmp_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/extract_urmp_archive.sh "$(URMP_ARCHIVE)" "$(URMP_EXTRACT_DIR)"

inspect-urmp-bass-timing: scripts/inspect_urmp_bass_timing.py | $(BUILD_DIR)
	@test -d "$(URMP_EXTRACT_DIR)/Dataset" || { printf '%s\n' "missing extracted URMP Dataset; run make prepare-real-urmp"; exit 2; }
	$(PYTHON) scripts/inspect_urmp_bass_timing.py --root "$(URMP_EXTRACT_DIR)" --output "$(URMP_BASS_TIMING_AUDIT)"

test-inspect-urmp-bass-timing: tests/test_inspect_urmp_bass_timing.py scripts/inspect_urmp_bass_timing.py
	$(PYTHON) tests/test_inspect_urmp_bass_timing.py

