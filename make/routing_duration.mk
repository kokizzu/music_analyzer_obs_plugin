.PHONY: test-routing-duration-score
$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_basic_pitch.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/piano_guitar_features.hpp src/piano_guitar_verifier.hpp src/piano_guitar_model_data.hpp src/native_timbre_features.hpp src/routing_duplicate_consensus.hpp src/native_piano_consensus_cached_hook.inc
test-routing-duration-score: tests/test_routing_duration_score.py
	$(PYTHON) tests/test_routing_duration_score.py

.PHONY: build-routing-duration-primary measure-routing-duration-baseline
build-routing-duration-primary: scripts/routing_duration_baseline.py
	$(PYTHON) scripts/routing_duration_baseline.py
measure-routing-duration-baseline: scripts/routing_duration_baseline.py scripts/routing_duration_score.py
	$(PYTHON) scripts/routing_duration_baseline.py --measure

.PHONY: capture-routing-candidates
capture-routing-candidates: scripts/capture_routing_candidates.py tests/routing_candidate_replay.cpp
	$(PYTHON) scripts/capture_routing_candidates.py

.PHONY: publish-routing-duration-checkpoint
publish-routing-duration-checkpoint: scripts/manage_routing_duration_goal.py
	$(PYTHON) scripts/manage_routing_duration_goal.py

.PHONY: capture-routing-controls
capture-routing-controls: scripts/capture_routing_controls.py
	$(PYTHON) scripts/capture_routing_controls.py

.PHONY: test-routing-alignment audit-routing-alignment
test-routing-alignment: tests/test_routing_alignment.py scripts/routing_alignment.py
	.separator-venv/bin/python tests/test_routing_alignment.py
audit-routing-alignment: scripts/audit_routing_alignment.py scripts/routing_alignment.py
	.separator-venv/bin/python scripts/audit_routing_alignment.py

.PHONY: evaluate-guitar-duplicate-model
evaluate-guitar-duplicate-model: scripts/evaluate_guitar_duplicate_model.py
	.separator-venv/bin/python scripts/evaluate_guitar_duplicate_model.py

.PHONY: capture-routing-polycontrols
capture-routing-polycontrols: scripts/capture_routing_polycontrols.py
	$(PYTHON) scripts/capture_routing_polycontrols.py

.PHONY: evaluate-guitar-context-veto
evaluate-guitar-context-veto: scripts/evaluate_guitar_context_veto.py
	$(PYTHON) scripts/evaluate_guitar_context_veto.py

.PHONY: evaluate-guitar-keyboard-context
evaluate-guitar-keyboard-context: scripts/evaluate_guitar_context_veto.py
	$(PYTHON) scripts/evaluate_guitar_context_veto.py --keyboard-context

.PHONY: capture-routing-guitarset
capture-routing-guitarset: scripts/capture_routing_guitarset.py
	$(PYTHON) scripts/capture_routing_guitarset.py

.PHONY: evaluate-guitar-music-model
evaluate-guitar-music-model: scripts/evaluate_guitar_music_model.py
	.separator-venv/bin/python scripts/evaluate_guitar_music_model.py

.PHONY: freeze-piano-guitar-model generate-piano-guitar-model test-piano-guitar-verifier check-piano-guitar-verifier-parity
freeze-piano-guitar-model: scripts/export_piano_guitar_model.py
	$(PYTHON) scripts/export_piano_guitar_model.py --freeze
generate-piano-guitar-model: scripts/export_piano_guitar_model.py
	$(PYTHON) scripts/export_piano_guitar_model.py
$(BUILD_DIR)/piano_guitar_verifier: tests/piano_guitar_verifier.cpp src/piano_guitar_verifier.hpp src/piano_guitar_model_data.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-piano-guitar-verifier: $(BUILD_DIR)/piano_guitar_verifier tests/test_piano_guitar_verifier.py
	$(PYTHON) tests/test_piano_guitar_verifier.py
check-piano-guitar-verifier-parity: $(BUILD_DIR)/piano_guitar_verifier tests/test_piano_guitar_verifier.py
	$(PYTHON) tests/test_piano_guitar_verifier.py --full

.PHONY: build-piano-guitar-trial
build-piano-guitar-trial: scripts/build_piano_guitar_trial.py tests/piano_guitar_pair.cpp
	$(PYTHON) scripts/build_piano_guitar_trial.py

.PHONY: measure-piano-guitar-trial measure-piano-guitar-controls
measure-piano-guitar-trial: scripts/measure_piano_guitar_trial.py
	$(PYTHON) scripts/measure_piano_guitar_trial.py
measure-piano-guitar-controls: scripts/measure_piano_guitar_trial.py
	$(PYTHON) scripts/measure_piano_guitar_trial.py --controls

.PHONY: test-guitar-music-context
test-guitar-music-context: tests/test_guitar_music_context.py scripts/evaluate_guitar_music_model.py
	$(PYTHON) tests/test_guitar_music_context.py

.PHONY: validate-piano-guitar-all validate-piano-guitar-rate48-a validate-piano-guitar-rate48-b validate-piano-guitar-reserved
validate-piano-guitar-all: scripts/validate_piano_guitar_extensions.py
	$(PYTHON) scripts/run_routing_extensions.py --mode original
validate-piano-guitar-rate48-a: scripts/validate_piano_guitar_extensions.py
	$(PYTHON) scripts/run_routing_extensions.py --mode rate48 --shards 2 --shard 0
validate-piano-guitar-rate48-b: scripts/validate_piano_guitar_extensions.py
	$(PYTHON) scripts/run_routing_extensions.py --mode rate48 --shards 2 --shard 1
validate-piano-guitar-reserved: scripts/validate_piano_guitar_extensions.py
	$(PYTHON) scripts/run_routing_extensions.py --mode reserved

.PHONY: audit-voice-duration-candidates
audit-voice-duration-candidates: scripts/audit_voice_duration_candidates.py
	$(PYTHON) scripts/audit_voice_duration_candidates.py

.PHONY: inspect-routing-replays
inspect-routing-replays: scripts/inspect_routing_replays.py
	$(PYTHON) scripts/inspect_routing_replays.py

.PHONY: test-voice-duration-candidates
test-voice-duration-candidates: tests/test_voice_duration_candidates.py scripts/audit_voice_duration_candidates.py
	$(PYTHON) tests/test_voice_duration_candidates.py

.PHONY: verify-routing-extensions publish-routing-extensions
verify-routing-extensions: scripts/checkpoint_routing_extensions.py
	$(PYTHON) scripts/checkpoint_routing_extensions.py
publish-routing-extensions: scripts/checkpoint_routing_extensions.py
	$(PYTHON) scripts/checkpoint_routing_extensions.py --publish

.PHONY: plan-routing-replay-repair apply-routing-replay-repair
plan-routing-replay-repair: scripts/repair_routing_replay_checkpoints.py
	$(PYTHON) scripts/repair_routing_replay_checkpoints.py
apply-routing-replay-repair: scripts/repair_routing_replay_checkpoints.py
	$(PYTHON) scripts/repair_routing_replay_checkpoints.py --apply

.PHONY: evaluate-voice-duplicate
evaluate-voice-duplicate: scripts/evaluate_voice_duplicate.py
	$(PYTHON) scripts/evaluate_voice_duplicate.py

.PHONY: build-piano-voice-trial
build-piano-voice-trial: scripts/build_piano_voice_trial.py src/experimental_piano_voice_hook.inc tests/piano_voice_pair.cpp
	$(PYTHON) scripts/build_piano_voice_trial.py

.PHONY: measure-piano-voice-trial measure-piano-voice-controls
measure-piano-voice-trial: scripts/measure_piano_voice_trial.py
	$(PYTHON) scripts/measure_piano_voice_trial.py
measure-piano-voice-controls: scripts/measure_piano_voice_trial.py
	$(PYTHON) scripts/measure_piano_voice_trial.py --controls

.PHONY: audit-keyboard-recovery
audit-keyboard-recovery: scripts/audit_keyboard_recovery.py
	$(PYTHON) scripts/audit_keyboard_recovery.py

.PHONY: validate-piano-voice-extensions
validate-piano-voice-extensions: scripts/validate_piano_voice_extensions.py
	$(PYTHON) scripts/validate_piano_voice_extensions.py

.PHONY: evaluate-keyboard-recovery
evaluate-keyboard-recovery: scripts/evaluate_keyboard_recovery.py
	.separator-venv/bin/python scripts/evaluate_keyboard_recovery.py

.PHONY: trace-primary-duration
trace-primary-duration: scripts/trace_primary_duration.py tests/primary_duration_trace.cpp tests/primary_duration_trace.hpp
	$(PYTHON) scripts/trace_primary_duration.py

.PHONY: test-keyboard-recovery
test-keyboard-recovery: tests/test_keyboard_recovery.py scripts/evaluate_keyboard_recovery.py scripts/audit_keyboard_recovery.py
	$(PYTHON) tests/test_keyboard_recovery.py

.PHONY: audit-keyboard-tracking-recovery
audit-keyboard-tracking-recovery: scripts/audit_keyboard_tracking_recovery.py
	$(PYTHON) scripts/audit_keyboard_tracking_recovery.py

.PHONY: capture-routing-regression-evidence
capture-routing-regression-evidence: scripts/capture_routing_regression_evidence.py
	$(PYTHON) scripts/capture_routing_regression_evidence.py

.PHONY: evaluate-routing-consensus
evaluate-routing-consensus: scripts/evaluate_routing_consensus.py
	$(PYTHON) scripts/evaluate_routing_consensus.py

.PHONY: test-routing-consensus
test-routing-consensus: tests/test_routing_consensus.py scripts/evaluate_routing_consensus.py
	$(PYTHON) tests/test_routing_consensus.py

.PHONY: verify-voice-duration-evidence publish-voice-duration-evidence
verify-voice-duration-evidence: scripts/checkpoint_voice_duration_evidence.py
	$(PYTHON) scripts/checkpoint_voice_duration_evidence.py
publish-voice-duration-evidence: scripts/checkpoint_voice_duration_evidence.py
	$(PYTHON) scripts/checkpoint_voice_duration_evidence.py --publish

.PHONY: test-native-routing-consensus
$(BUILD_DIR)/routing_duplicate_consensus: tests/routing_duplicate_consensus.cpp src/routing_duplicate_consensus.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-native-routing-consensus: $(BUILD_DIR)/routing_duplicate_consensus
	$(BUILD_DIR)/routing_duplicate_consensus

.PHONY: build-routing-consensus-trial
build-routing-consensus-trial: scripts/build_routing_consensus_trial.py src/native_piano_consensus_cached_hook.inc tests/routing_consensus_pair.cpp
	$(PYTHON) scripts/build_routing_consensus_trial.py

.PHONY: measure-routing-consensus-piano measure-routing-consensus-controls
measure-routing-consensus-piano: scripts/measure_routing_consensus.py
	$(PYTHON) scripts/measure_routing_consensus.py
measure-routing-consensus-controls: scripts/measure_routing_consensus.py
	$(PYTHON) scripts/measure_routing_consensus.py --controls

.PHONY: plan-routing-consensus-validation validate-routing-consensus-a validate-routing-consensus-b
plan-routing-consensus-validation: scripts/validate_routing_consensus.py
	$(PYTHON) scripts/validate_routing_consensus.py --plan
validate-routing-consensus-a: scripts/validate_routing_consensus.py
	$(PYTHON) scripts/validate_routing_consensus.py --shard 0
validate-routing-consensus-b: scripts/validate_routing_consensus.py
	$(PYTHON) scripts/validate_routing_consensus.py --shard 1

.PHONY: benchmark-routing-consensus
benchmark-routing-consensus: scripts/benchmark_routing_consensus.py tests/routing_consensus_latency.cpp
	$(PYTHON) scripts/benchmark_routing_consensus.py

.PHONY: test-keyboard-alias-visibility-baseline
test-keyboard-alias-visibility-baseline: scripts/test_keyboard_alias_visibility.py tests/keyboard_alias_visibility.cpp
	$(PYTHON) scripts/test_keyboard_alias_visibility.py

.PHONY: test-routing-cepstral-cache
$(BUILD_DIR)/routing_cepstral_cache: tests/routing_cepstral_cache.cpp src/native_timbre_features.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-routing-cepstral-cache: $(BUILD_DIR)/routing_cepstral_cache
	$(BUILD_DIR)/routing_cepstral_cache

.PHONY: build-keyboard-alias-trial
build-keyboard-alias-trial: scripts/build_keyboard_alias_trial.py src/keyboard_alias_visibility_guard.inc tests/keyboard_alias_visibility.cpp tests/keyboard_alias_visibility_pair.cpp
	$(PYTHON) scripts/build_keyboard_alias_trial.py

.PHONY: measure-keyboard-alias-trial
measure-keyboard-alias-trial: scripts/measure_keyboard_alias_trial.py
	$(PYTHON) scripts/measure_keyboard_alias_trial.py

.PHONY: prepare-routing-consensus-rollout
prepare-routing-consensus-rollout: scripts/prepare_routing_consensus_rollout.py tests/routing_consensus_default.cpp
	$(PYTHON) scripts/prepare_routing_consensus_rollout.py

.PHONY: verify-native-routing-consensus publish-native-routing-consensus
verify-native-routing-consensus: scripts/publish_native_routing_consensus.py
	$(PYTHON) scripts/publish_native_routing_consensus.py
publish-native-routing-consensus: scripts/publish_native_routing_consensus.py
	$(PYTHON) scripts/publish_native_routing_consensus.py --publish

.PHONY: trace-keyboard-stages test-keyboard-stage-trace
trace-keyboard-stages: scripts/trace_keyboard_stages.py tests/keyboard_stage_trace.cpp tests/keyboard_stage_trace.hpp
	$(PYTHON) scripts/trace_keyboard_stages.py
$(BUILD_DIR)/keyboard_stage_trace_test: tests/keyboard_stage_trace_test.cpp tests/keyboard_stage_trace.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests $< -o $@
test-keyboard-stage-trace: $(BUILD_DIR)/keyboard_stage_trace_test tests/test_keyboard_stage_trace.py
	$(BUILD_DIR)/keyboard_stage_trace_test
	$(PYTHON) tests/test_keyboard_stage_trace.py

.PHONY: test-low-keyboard-fundamental-baseline
test-low-keyboard-fundamental-baseline: scripts/test_keyboard_alias_visibility.py tests/low_keyboard_fundamental.cpp
	$(PYTHON) scripts/test_keyboard_alias_visibility.py --low-fundamental

.PHONY: build-low-keyboard-trial
build-low-keyboard-trial: scripts/build_keyboard_alias_trial.py src/low_keyboard_fundamental_guard.inc tests/low_keyboard_fundamental.cpp tests/low_keyboard_pair.cpp
	$(PYTHON) scripts/build_keyboard_alias_trial.py --low-fundamental

.PHONY: measure-low-keyboard-trial
measure-low-keyboard-trial: scripts/measure_low_keyboard_trial.py
	$(PYTHON) scripts/measure_low_keyboard_trial.py

.PHONY: test-note-grid-comparison
$(BUILD_DIR)/note_grid_comparison: tests/note_grid_comparison.cpp tests/note_grid_comparison.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests $< -o $@
test-note-grid-comparison: $(BUILD_DIR)/note_grid_comparison
	$(BUILD_DIR)/note_grid_comparison

.PHONY: audit-keyboard-grace
audit-keyboard-grace: scripts/audit_keyboard_grace.py
	$(PYTHON) scripts/audit_keyboard_grace.py

.PHONY: calibrate-low-keyboard-trial freeze-low-keyboard-parameters measure-low-keyboard-heldout
calibrate-low-keyboard-trial: scripts/measure_low_keyboard_trial.py
	$(PYTHON) scripts/measure_low_keyboard_trial.py --calibration
freeze-low-keyboard-parameters: scripts/freeze_low_keyboard_parameters.py
	$(PYTHON) scripts/freeze_low_keyboard_parameters.py
measure-low-keyboard-heldout: scripts/measure_low_keyboard_trial.py
	$(PYTHON) scripts/measure_low_keyboard_trial.py --heldout

.PHONY: plan-low-keyboard-controls validate-low-keyboard-controls-a validate-low-keyboard-controls-b validate-low-keyboard-controls-c validate-low-keyboard-controls-d
plan-low-keyboard-controls: scripts/validate_low_keyboard_controls.py
	$(PYTHON) scripts/validate_low_keyboard_controls.py --plan
validate-low-keyboard-controls-a: scripts/validate_low_keyboard_controls.py
	$(PYTHON) scripts/validate_low_keyboard_controls.py --shard 0
validate-low-keyboard-controls-b: scripts/validate_low_keyboard_controls.py
	$(PYTHON) scripts/validate_low_keyboard_controls.py --shard 1
validate-low-keyboard-controls-c: scripts/validate_low_keyboard_controls.py
	$(PYTHON) scripts/validate_low_keyboard_controls.py --shard 2
validate-low-keyboard-controls-d: scripts/validate_low_keyboard_controls.py
	$(PYTHON) scripts/validate_low_keyboard_controls.py --shard 3

.PHONY: evaluate-low-keyboard-coherence
evaluate-low-keyboard-coherence: scripts/evaluate_low_keyboard_coherence.py
	.separator-venv/bin/python scripts/evaluate_low_keyboard_coherence.py

.PHONY: verify-low-keyboard-evidence stage-low-keyboard-evidence publish-low-keyboard-evidence
verify-low-keyboard-evidence: scripts/checkpoint_low_keyboard_evidence.py
	$(PYTHON) scripts/checkpoint_low_keyboard_evidence.py
stage-low-keyboard-evidence: scripts/checkpoint_low_keyboard_evidence.py
	$(PYTHON) scripts/checkpoint_low_keyboard_evidence.py --stage
publish-low-keyboard-evidence: scripts/checkpoint_low_keyboard_evidence.py
	$(PYTHON) scripts/checkpoint_low_keyboard_evidence.py --publish

.PHONY: test-low-keyboard-coherence
$(BUILD_DIR)/low_keyboard_coherence_test: tests/low_keyboard_coherence.cpp src/low_keyboard_coherence.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-low-keyboard-coherence: $(BUILD_DIR)/low_keyboard_coherence_test
	$(BUILD_DIR)/low_keyboard_coherence_test

$(BUILD_DIR)/low_keyboard_coherence_history: tests/low_keyboard_coherence_history.cpp src/low_keyboard_coherence.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
.PHONY: test-low-keyboard-coherence-history
test-low-keyboard-coherence-history: $(BUILD_DIR)/low_keyboard_coherence_history
	$(BUILD_DIR)/low_keyboard_coherence_history

.PHONY: build-low-keyboard-coherence-trial
build-low-keyboard-coherence-trial: scripts/build_keyboard_alias_trial.py scripts/low_keyboard_coherence_trial.py src/low_keyboard_coherence.hpp tests/low_keyboard_coherence_pair.cpp
	$(PYTHON) scripts/build_keyboard_alias_trial.py --coherence

.PHONY: measure-low-keyboard-coherence
measure-low-keyboard-coherence: scripts/measure_low_keyboard_coherence.py
	$(PYTHON) scripts/measure_low_keyboard_coherence.py

.PHONY: calibrate-low-keyboard-coherence freeze-low-keyboard-coherence measure-low-keyboard-coherence-heldout
calibrate-low-keyboard-coherence: scripts/validate_low_keyboard_coherence.py
	$(PYTHON) scripts/validate_low_keyboard_coherence.py --calibration
freeze-low-keyboard-coherence: scripts/validate_low_keyboard_coherence.py
	$(PYTHON) scripts/validate_low_keyboard_coherence.py --freeze
measure-low-keyboard-coherence-heldout: scripts/validate_low_keyboard_coherence.py
	$(PYTHON) scripts/validate_low_keyboard_coherence.py --heldout

.PHONY: plan-coherence-controls validate-coherence-controls-a validate-coherence-controls-b validate-coherence-controls-c validate-coherence-controls-d
plan-coherence-controls: scripts/validate_low_keyboard_coherence_controls.py
	$(PYTHON) scripts/validate_low_keyboard_coherence_controls.py --plan
validate-coherence-controls-a: scripts/validate_low_keyboard_coherence_controls.py
	$(PYTHON) scripts/validate_low_keyboard_coherence_controls.py --shard 0
validate-coherence-controls-b: scripts/validate_low_keyboard_coherence_controls.py
	$(PYTHON) scripts/validate_low_keyboard_coherence_controls.py --shard 1
validate-coherence-controls-c: scripts/validate_low_keyboard_coherence_controls.py
	$(PYTHON) scripts/validate_low_keyboard_coherence_controls.py --shard 2
validate-coherence-controls-d: scripts/validate_low_keyboard_coherence_controls.py
	$(PYTHON) scripts/validate_low_keyboard_coherence_controls.py --shard 3

.PHONY: benchmark-low-keyboard-coherence
benchmark-low-keyboard-coherence: scripts/benchmark_low_keyboard_coherence.py tests/low_keyboard_coherence_latency.cpp
	$(PYTHON) scripts/benchmark_low_keyboard_coherence.py

.PHONY: verify-keyboard-coherence stage-keyboard-coherence publish-keyboard-coherence
verify-keyboard-coherence: scripts/checkpoint_keyboard_coherence.py
	$(PYTHON) scripts/checkpoint_keyboard_coherence.py
stage-keyboard-coherence: scripts/checkpoint_keyboard_coherence.py
	$(PYTHON) scripts/checkpoint_keyboard_coherence.py --stage
publish-keyboard-coherence: scripts/checkpoint_keyboard_coherence.py
	$(PYTHON) scripts/checkpoint_keyboard_coherence.py --publish

.PHONY: audit-keyboard-confirmation
audit-keyboard-confirmation: scripts/audit_keyboard_confirmation.py
	$(PYTHON) scripts/audit_keyboard_confirmation.py

.PHONY: evaluate-keyboard-confirmation test-keyboard-confirmation
evaluate-keyboard-confirmation: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py
test-keyboard-confirmation: tests/test_keyboard_confirmation.py scripts/evaluate_keyboard_confirmation.py
	$(PYTHON) tests/test_keyboard_confirmation.py

.PHONY: capture-joint-pitch test-joint-pitch
capture-joint-pitch: scripts/capture_joint_pitch.py scripts/joint_pitch_reference.py
	.separator-venv/bin/python scripts/capture_joint_pitch.py
test-joint-pitch: tests/test_joint_pitch_reference.py scripts/joint_pitch_reference.py
	.separator-venv/bin/python tests/test_joint_pitch_reference.py

.PHONY: evaluate-joint-confirmation
evaluate-joint-confirmation: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --joint

.PHONY: evaluate-confirmation-empirical evaluate-joint-confirmation-empirical
evaluate-confirmation-empirical: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --empirical-cutoff
evaluate-joint-confirmation-empirical: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --joint --empirical-cutoff

.PHONY: evaluate-confirmation-pedal evaluate-joint-confirmation-pedal
evaluate-confirmation-pedal: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --empirical-cutoff --pedal-support
evaluate-joint-confirmation-pedal: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --joint --empirical-cutoff --pedal-support

.PHONY: evaluate-confirmation-pedal-strict evaluate-joint-confirmation-pedal-strict
evaluate-confirmation-pedal-strict: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --pedal-support
evaluate-joint-confirmation-pedal-strict: scripts/evaluate_keyboard_confirmation.py
	.separator-venv/bin/python scripts/evaluate_keyboard_confirmation.py --joint --pedal-support

.PHONY: verify-confirmation-research stage-confirmation-research publish-confirmation-research
verify-confirmation-research: scripts/checkpoint_confirmation_research.py
	$(PYTHON) scripts/checkpoint_confirmation_research.py
stage-confirmation-research: scripts/checkpoint_confirmation_research.py
	$(PYTHON) scripts/checkpoint_confirmation_research.py --stage
publish-confirmation-research: scripts/checkpoint_confirmation_research.py
	$(PYTHON) scripts/checkpoint_confirmation_research.py --publish

.PHONY: capture-joint-note-coverage test-joint-note-coverage
capture-joint-note-coverage: scripts/capture_joint_note_coverage.py
	.separator-venv/bin/python scripts/capture_joint_note_coverage.py
test-joint-note-coverage: tests/test_joint_note_coverage.py
	.separator-venv/bin/python tests/test_joint_note_coverage.py

.PHONY: screen-joint-note-coverage
screen-joint-note-coverage: scripts/screen_joint_note_coverage.py
	.separator-venv/bin/python scripts/screen_joint_note_coverage.py

.PHONY: test-joint-grace-rules calibrate-joint-grace
test-joint-grace-rules: tests/test_joint_grace_rules.py scripts/joint_grace_rules.py
	$(PYTHON) tests/test_joint_grace_rules.py
calibrate-joint-grace: scripts/calibrate_joint_grace.py
	.separator-venv/bin/python scripts/calibrate_joint_grace.py

.PHONY: verify-joint-grace stage-joint-grace publish-joint-grace
verify-joint-grace: scripts/checkpoint_joint_grace.py
	.separator-venv/bin/python scripts/checkpoint_joint_grace.py
stage-joint-grace: scripts/checkpoint_joint_grace.py
	.separator-venv/bin/python scripts/checkpoint_joint_grace.py --stage
publish-joint-grace: scripts/checkpoint_joint_grace.py
	.separator-venv/bin/python scripts/checkpoint_joint_grace.py --publish

.PHONY: test-native-joint-pitch
test-native-joint-pitch: scripts/test_native_joint_pitch.py src/joint_piano_fit.hpp tests/joint_piano_fit_replay.cpp
	.separator-venv/bin/python scripts/test_native_joint_pitch.py

.PHONY: test-joint-piano-fit-safety
$(BUILD_DIR)/joint_piano_fit_safety: tests/joint_piano_fit_safety.cpp src/joint_piano_fit.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-joint-piano-fit-safety: $(BUILD_DIR)/joint_piano_fit_safety
	$(BUILD_DIR)/joint_piano_fit_safety

.PHONY: stage-native-joint-pitch publish-native-joint-pitch
stage-native-joint-pitch: scripts/checkpoint_native_joint_pitch.py
	.separator-venv/bin/python scripts/checkpoint_native_joint_pitch.py --stage
publish-native-joint-pitch: scripts/checkpoint_native_joint_pitch.py
	.separator-venv/bin/python scripts/checkpoint_native_joint_pitch.py --publish
