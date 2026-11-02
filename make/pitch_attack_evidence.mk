# Isolated Basic Pitch evidence; production decoder and request cadence unchanged.
.PHONY: build-pitch-attack-evidence capture-pitch-attack-evidence
build-pitch-attack-evidence: scripts/capture_pitch_attack_evidence.py tests/pitch_attack_evidence.cpp
	.separator-venv/bin/python scripts/capture_pitch_attack_evidence.py --build
capture-pitch-attack-evidence: scripts/capture_pitch_attack_evidence.py tests/pitch_attack_evidence.cpp
	.separator-venv/bin/python scripts/capture_pitch_attack_evidence.py

.PHONY: test-pitch-attack-queue
test-pitch-attack-queue: tests/test_pitch_attack_queue.py
	.separator-venv/bin/python tests/test_pitch_attack_queue.py

.PHONY: test-pitch-attack-history
test-pitch-attack-history: scripts/test_pitch_attack_history.py tests/pitch_attack_history_parity.cpp
	.separator-venv/bin/python scripts/test_pitch_attack_history.py

.PHONY: screen-pitch-attack-evidence
screen-pitch-attack-evidence: scripts/screen_pitch_attack_evidence.py scripts/pitch_attack_queue.py
	.separator-venv/bin/python scripts/screen_pitch_attack_evidence.py

.PHONY: screen-pitch-attack-ondemand
screen-pitch-attack-ondemand: scripts/screen_pitch_attack_ondemand.py
	.separator-venv/bin/python scripts/screen_pitch_attack_ondemand.py

.PHONY: screen-pitch-attack-prefetch
screen-pitch-attack-prefetch: scripts/screen_pitch_attack_prefetch.py scripts/pitch_attack_queue.py
	.separator-venv/bin/python scripts/screen_pitch_attack_prefetch.py

.PHONY: verify-pitch-attack-evidence stage-pitch-attack-evidence publish-pitch-attack-evidence
verify-pitch-attack-evidence:
	.separator-venv/bin/python scripts/checkpoint_pitch_attack.py
stage-pitch-attack-evidence:
	.separator-venv/bin/python scripts/checkpoint_pitch_attack.py --stage
publish-pitch-attack-evidence:
	.separator-venv/bin/python scripts/checkpoint_pitch_attack.py --publish
