# Native note release evidence and experiments.
.PHONY: audit-keyboard-release-tails
audit-keyboard-release-tails: scripts/audit_keyboard_release_tails.py
	.separator-venv/bin/python scripts/audit_keyboard_release_tails.py

.PHONY: test-keyboard-release-tails
test-keyboard-release-tails: tests/test_keyboard_release_tails.py scripts/audit_keyboard_release_tails.py
	.separator-venv/bin/python tests/test_keyboard_release_tails.py

.PHONY: verify-keyboard-release stage-keyboard-release publish-keyboard-release
verify-keyboard-release: scripts/checkpoint_keyboard_release.py
	.separator-venv/bin/python scripts/checkpoint_keyboard_release.py
stage-keyboard-release: scripts/checkpoint_keyboard_release.py
	.separator-venv/bin/python scripts/checkpoint_keyboard_release.py --stage
publish-keyboard-release: scripts/checkpoint_keyboard_release.py
	.separator-venv/bin/python scripts/checkpoint_keyboard_release.py --publish
