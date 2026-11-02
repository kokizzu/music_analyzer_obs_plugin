.PHONY: test-routing-duration-score
$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_basic_pitch.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/piano_guitar_features.hpp src/piano_guitar_verifier.hpp src/piano_guitar_model_data.hpp src/native_timbre_features.hpp
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
