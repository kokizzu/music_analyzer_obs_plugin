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

.PHONY: screen-multiscale-low-keyboard test-multiscale-low-keyboard
screen-multiscale-low-keyboard: scripts/screen_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/screen_multiscale_low_keyboard.py
test-multiscale-low-keyboard: tests/test_multiscale_low_keyboard.py scripts/screen_multiscale_low_keyboard.py
	.separator-venv/bin/python tests/test_multiscale_low_keyboard.py

.PHONY: build-multiscale-low-keyboard
build-multiscale-low-keyboard: scripts/build_multiscale_low_keyboard.py src/multiscale_low_keyboard.hpp
	.separator-venv/bin/python scripts/build_multiscale_low_keyboard.py

.PHONY: measure-multiscale-low-keyboard calibrate-multiscale-low-keyboard
measure-multiscale-low-keyboard: scripts/measure_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/measure_multiscale_low_keyboard.py
calibrate-multiscale-low-keyboard: scripts/measure_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/measure_multiscale_low_keyboard.py --calibration

.PHONY: test-native-multiscale-low-keyboard
$(BUILD_DIR)/multiscale_low_keyboard_test: tests/multiscale_low_keyboard.cpp src/multiscale_low_keyboard.hpp src/low_keyboard_coherence.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-native-multiscale-low-keyboard: $(BUILD_DIR)/multiscale_low_keyboard_test
	$(BUILD_DIR)/multiscale_low_keyboard_test

.PHONY: freeze-multiscale-fresh measure-multiscale-fresh-21 measure-multiscale-fresh-22 measure-multiscale-fresh-23 measure-multiscale-fresh-24
freeze-multiscale-fresh: scripts/run_multiscale_fresh.py
	.separator-venv/bin/python scripts/run_multiscale_fresh.py --freeze
measure-multiscale-fresh-21: scripts/run_multiscale_fresh.py
	.separator-venv/bin/python scripts/run_multiscale_fresh.py --record 21
measure-multiscale-fresh-22: scripts/run_multiscale_fresh.py
	.separator-venv/bin/python scripts/run_multiscale_fresh.py --record 22
measure-multiscale-fresh-23: scripts/run_multiscale_fresh.py
	.separator-venv/bin/python scripts/run_multiscale_fresh.py --record 23
measure-multiscale-fresh-24: scripts/run_multiscale_fresh.py
	.separator-venv/bin/python scripts/run_multiscale_fresh.py --record 24

.PHONY: plan-multiscale-controls validate-multiscale-controls-a validate-multiscale-controls-b validate-multiscale-controls-c validate-multiscale-controls-d
plan-multiscale-controls: scripts/validate_multiscale_controls.py
	.separator-venv/bin/python scripts/validate_multiscale_controls.py --plan
validate-multiscale-controls-a: scripts/validate_multiscale_controls.py
	.separator-venv/bin/python scripts/validate_multiscale_controls.py --shard 0
validate-multiscale-controls-b: scripts/validate_multiscale_controls.py
	.separator-venv/bin/python scripts/validate_multiscale_controls.py --shard 1
validate-multiscale-controls-c: scripts/validate_multiscale_controls.py
	.separator-venv/bin/python scripts/validate_multiscale_controls.py --shard 2
validate-multiscale-controls-d: scripts/validate_multiscale_controls.py
	.separator-venv/bin/python scripts/validate_multiscale_controls.py --shard 3

.PHONY: benchmark-multiscale-low-keyboard
benchmark-multiscale-low-keyboard: scripts/benchmark_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/benchmark_multiscale_low_keyboard.py

.PHONY: qualify-multiscale-low-keyboard
qualify-multiscale-low-keyboard: scripts/qualify_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/qualify_multiscale_low_keyboard.py

.PHONY: verify-multiscale-low-keyboard stage-multiscale-low-keyboard publish-multiscale-low-keyboard
verify-multiscale-low-keyboard: scripts/checkpoint_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_multiscale_low_keyboard.py
stage-multiscale-low-keyboard: scripts/checkpoint_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_multiscale_low_keyboard.py --stage
publish-multiscale-low-keyboard: scripts/checkpoint_multiscale_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_multiscale_low_keyboard.py --publish
