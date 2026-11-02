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

.PHONY: replay-pitch-attack-envelope
replay-pitch-attack-envelope: scripts/replay_pitch_attack_envelope.py tests/pitch_attack_replay_support.hpp
	.separator-venv/bin/python scripts/replay_pitch_attack_envelope.py

.PHONY: score-pitch-attack-envelope
score-pitch-attack-envelope: scripts/score_pitch_attack_envelope.py
	.separator-venv/bin/python scripts/score_pitch_attack_envelope.py

.PHONY: build-pitch-attack-display replay-pitch-attack-display
build-pitch-attack-display: scripts/replay_pitch_attack_display.py src/piano_attack_display.hpp tests/piano_attack_display.cpp
	.separator-venv/bin/python scripts/replay_pitch_attack_display.py --build
replay-pitch-attack-display: scripts/replay_pitch_attack_display.py src/piano_attack_display.hpp tests/piano_attack_display.cpp
	.separator-venv/bin/python scripts/replay_pitch_attack_display.py

.PHONY: score-pitch-attack-display
score-pitch-attack-display: scripts/score_pitch_attack_envelope.py
	.separator-venv/bin/python scripts/score_pitch_attack_envelope.py --display

.PHONY: test-piano-attack-display
test-piano-attack-display: scripts/test_piano_attack_display.py tests/piano_attack_display.cpp src/piano_attack_display.hpp
	.separator-venv/bin/python scripts/test_piano_attack_display.py

.PHONY: test-pitch-attack-continuity screen-pitch-attack-continuity
test-pitch-attack-continuity: tests/test_pitch_attack_continuity.py scripts/pitch_attack_continuity.py
	.separator-venv/bin/python tests/test_pitch_attack_continuity.py
screen-pitch-attack-continuity: scripts/screen_pitch_attack_continuity.py scripts/pitch_attack_continuity.py
	.separator-venv/bin/python scripts/screen_pitch_attack_continuity.py

.PHONY: test-native-piano-attack-continuity
test-native-piano-attack-continuity: scripts/test_piano_attack_display.py tests/piano_attack_continuity.cpp src/piano_attack_continuity.hpp
	.separator-venv/bin/python scripts/test_piano_attack_display.py --continuity

.PHONY: replay-pitch-attack-continuity score-pitch-attack-continuity
replay-pitch-attack-continuity: scripts/replay_pitch_attack_continuity.py src/piano_attack_continuity.hpp tests/piano_attack_continuity.cpp
	.separator-venv/bin/python scripts/replay_pitch_attack_continuity.py
score-pitch-attack-continuity: scripts/score_pitch_attack_envelope.py
	.separator-venv/bin/python scripts/score_pitch_attack_envelope.py --continuity

.PHONY: verify-pitch-continuity stage-pitch-continuity publish-pitch-continuity
verify-pitch-continuity:
	.separator-venv/bin/python scripts/checkpoint_pitch_continuity.py
stage-pitch-continuity:
	.separator-venv/bin/python scripts/checkpoint_pitch_continuity.py --stage
publish-pitch-continuity:
	.separator-venv/bin/python scripts/checkpoint_pitch_continuity.py --publish
