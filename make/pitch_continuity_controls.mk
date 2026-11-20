# Frozen continuous instrument-control qualification.
.PHONY: test-regression-recordings register-detection-regressions replay-detection-regressions
test-regression-recordings:
	$(PYTHON) tests/test_regression_recordings.py
register-detection-regressions:
	$(PYTHON) scripts/regression_recordings.py register
replay-detection-regressions:
	$(PYTHON) scripts/regression_recordings.py replay
.PHONY: test-pipeline-diagnostics check-primary-standalone-build
test-pipeline-diagnostics:
	$(PYTHON) tests/test_pipeline_diagnostics.py
check-primary-standalone-build:
	$(PYTHON) scripts/pipeline_diagnostics.py
.PHONY: measure-workspace-pipeline
measure-workspace-pipeline: standalone-basic-pitch
	$(PYTHON) scripts/pipeline_diagnostics.py --workspace
.PHONY: test-native-note-candidates screen-native-note-candidates
test-native-note-candidates:
	$(PYTHON) tests/test_native_note_candidates.py
screen-native-note-candidates:
	.separator-venv/bin/python scripts/screen_native_note_candidates.py
.PHONY: test-primary-source-recovery test-source-recovery
test-primary-source-recovery:
	$(PYTHON) scripts/validate_source_recovery.py
test-source-recovery:
	$(PYTHON) scripts/validate_source_recovery.py --candidate
.PHONY: inspect-detection-lifecycle
inspect-detection-lifecycle:
	$(PYTHON) scripts/checkpoint_detection_diagnostics.py inspect
.PHONY: test-note-onset-score
test-note-onset-score:
	$(PYTHON) tests/test_note_onset_score.py
.PHONY: test-detection-validation-store screen-routing-onset-proposals
test-detection-validation-store:
	$(PYTHON) tests/test_detection_validation_store.py
screen-routing-onset-proposals:
	.separator-venv/bin/python scripts/screen_routing_onset_proposals.py
.PHONY: test-analyzer-diagnostic capture-analyzer-diagnostic replay-analyzer-diagnostic test-primary-diagnostic-replay
DIAGNOSTIC_SECONDS ?= 15
DIAGNOSTIC_RECORDING ?= latest
test-analyzer-diagnostic:
	$(PYTHON) tests/test_analyzer_diagnostic.py
capture-analyzer-diagnostic:
	$(PYTHON) scripts/analyzer_diagnostic.py capture --seconds $(DIAGNOSTIC_SECONDS)
replay-analyzer-diagnostic:
	$(PYTHON) scripts/analyzer_diagnostic.py replay --recording $(DIAGNOSTIC_RECORDING)
test-primary-diagnostic-replay:
	$(PYTHON) scripts/analyzer_diagnostic.py self-test
.PHONY: benchmark-detection-worker
benchmark-detection-worker:
	$(PYTHON) scripts/benchmark_detection_worker.py
.PHONY: verify-detection-diagnostics stage-detection-diagnostics publish-detection-diagnostics
verify-detection-diagnostics:
	$(PYTHON) scripts/checkpoint_detection_diagnostics.py verify
stage-detection-diagnostics:
	$(PYTHON) scripts/checkpoint_detection_diagnostics.py stage
publish-detection-diagnostics:
	$(PYTHON) scripts/checkpoint_detection_diagnostics.py publish
.PHONY: test-pitch-control-tail
test-pitch-control-tail:
	.separator-venv/bin/python tests/test_pitch_control_tail.py
.PHONY: build-selected-pitch-evidence test-selected-pitch-evidence
build-selected-pitch-evidence:
	.separator-venv/bin/python scripts/build_selected_pitch_evidence.py --build
test-selected-pitch-evidence:
	.separator-venv/bin/python scripts/build_selected_pitch_evidence.py

.PHONY: test-pitch-control-gates freeze-pitch-continuity-controls run-pitch-continuity-controls
test-pitch-control-gates:
	.separator-venv/bin/python scripts/validate_pitch_continuity_controls.py parity
freeze-pitch-continuity-controls:
	.separator-venv/bin/python scripts/validate_pitch_continuity_controls.py freeze
run-pitch-continuity-controls:
	.separator-venv/bin/python scripts/validate_pitch_continuity_controls.py run

.PHONY: verify-pitch-controls stage-pitch-controls publish-pitch-controls
verify-pitch-controls:
	.separator-venv/bin/python scripts/checkpoint_pitch_controls.py
stage-pitch-controls:
	.separator-venv/bin/python scripts/checkpoint_pitch_controls.py --stage
publish-pitch-controls:
	.separator-venv/bin/python scripts/checkpoint_pitch_controls.py --publish
