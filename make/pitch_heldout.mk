# Source-disjoint held-out qualification tools.
.PHONY: build-pitch-heldout-tools
build-pitch-heldout-tools: scripts/build_pitch_heldout_tools.py tests/piano_context_pcm.cpp tests/pitch_primary_replay.cpp
	.separator-venv/bin/python scripts/build_pitch_heldout_tools.py

.PHONY: test-score-pitch-continuity-pair freeze-pitch-continuity-heldout run-pitch-continuity-heldout
test-score-pitch-continuity-pair: tests/test_score_pitch_continuity_pair.py scripts/score_pitch_continuity_pair.py
	.separator-venv/bin/python tests/test_score_pitch_continuity_pair.py
freeze-pitch-continuity-heldout:
	.separator-venv/bin/python scripts/validate_pitch_continuity_heldout.py freeze
run-pitch-continuity-heldout:
	.separator-venv/bin/python scripts/validate_pitch_continuity_heldout.py run

.PHONY: verify-pitch-heldout stage-pitch-heldout publish-pitch-heldout
verify-pitch-heldout:
	.separator-venv/bin/python scripts/checkpoint_pitch_heldout.py
stage-pitch-heldout:
	.separator-venv/bin/python scripts/checkpoint_pitch_heldout.py --stage
publish-pitch-heldout:
	.separator-venv/bin/python scripts/checkpoint_pitch_heldout.py --publish
