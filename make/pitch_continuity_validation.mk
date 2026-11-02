# Frozen recording-disjoint calibration; no production promotion.
.PHONY: freeze-pitch-continuity-calibration capture-pitch-continuity-calibration prepare-pitch-continuity-calibration replay-pitch-continuity-calibration score-pitch-continuity-calibration
freeze-pitch-continuity-calibration:
	.separator-venv/bin/python scripts/validate_pitch_continuity_calibration.py freeze
capture-pitch-continuity-calibration:
	.separator-venv/bin/python scripts/validate_pitch_continuity_calibration.py capture
prepare-pitch-continuity-calibration:
	.separator-venv/bin/python scripts/validate_pitch_continuity_calibration.py prepare
replay-pitch-continuity-calibration:
	.separator-venv/bin/python scripts/validate_pitch_continuity_calibration.py replay
score-pitch-continuity-calibration:
	.separator-venv/bin/python scripts/validate_pitch_continuity_calibration.py score

.PHONY: verify-pitch-calibration stage-pitch-calibration publish-pitch-calibration
verify-pitch-calibration:
	.separator-venv/bin/python scripts/checkpoint_pitch_calibration.py
stage-pitch-calibration:
	.separator-venv/bin/python scripts/checkpoint_pitch_calibration.py --stage
publish-pitch-calibration:
	.separator-venv/bin/python scripts/checkpoint_pitch_calibration.py --publish
