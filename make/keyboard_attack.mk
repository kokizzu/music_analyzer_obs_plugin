# First-hit attack evidence; runtime changes require independent replay gates.
.PHONY: screen-piano-context-attacks
screen-piano-context-attacks: scripts/screen_piano_context_attacks.py
	.separator-venv/bin/python scripts/screen_piano_context_attacks.py

.PHONY: screen-piano-context-joint-attacks
screen-piano-context-joint-attacks: scripts/screen_piano_context_attacks.py
	.separator-venv/bin/python scripts/screen_piano_context_attacks.py --joint

.PHONY: screen-piano-context-empirical-joint-attacks
screen-piano-context-empirical-joint-attacks: scripts/screen_piano_context_attacks.py
	.separator-venv/bin/python scripts/screen_piano_context_attacks.py --joint --empirical-cutoff

.PHONY: test-supervised-piano-dictionary
test-supervised-piano-dictionary: tests/test_supervised_piano_dictionary.py
	.separator-venv/bin/python tests/test_supervised_piano_dictionary.py

.PHONY: screen-supervised-piano-attacks
screen-supervised-piano-attacks: scripts/screen_supervised_piano_attacks.py scripts/supervised_piano_dictionary.py
	.separator-venv/bin/python scripts/screen_supervised_piano_attacks.py

.PHONY: transfer-real-piano-dictionary
transfer-real-piano-dictionary: scripts/transfer_real_piano_dictionary.py scripts/supervised_piano_dictionary.py
	.separator-venv/bin/python scripts/transfer_real_piano_dictionary.py

.PHONY: test-real-piano-dictionary
test-real-piano-dictionary: tests/test_real_piano_dictionary.py scripts/transfer_real_piano_dictionary.py
	.separator-venv/bin/python tests/test_real_piano_dictionary.py

.PHONY: screen-piano-attack-rises test-piano-attack-rises
screen-piano-attack-rises: scripts/screen_piano_attack_rises.py
	.separator-venv/bin/python scripts/screen_piano_attack_rises.py
test-piano-attack-rises: tests/test_piano_attack_rises.py scripts/screen_piano_attack_rises.py
	.separator-venv/bin/python tests/test_piano_attack_rises.py

.PHONY: verify-attack-dictionary stage-attack-dictionary publish-attack-dictionary
verify-attack-dictionary: scripts/checkpoint_attack_dictionary.py
	.separator-venv/bin/python scripts/checkpoint_attack_dictionary.py
stage-attack-dictionary: scripts/checkpoint_attack_dictionary.py
	.separator-venv/bin/python scripts/checkpoint_attack_dictionary.py --stage
publish-attack-dictionary: scripts/checkpoint_attack_dictionary.py
	.separator-venv/bin/python scripts/checkpoint_attack_dictionary.py --publish
