# Frozen continuous instrument-control qualification.
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
