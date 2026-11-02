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
