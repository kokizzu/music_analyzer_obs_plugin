# Frozen continuous instrument-control qualification.
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
