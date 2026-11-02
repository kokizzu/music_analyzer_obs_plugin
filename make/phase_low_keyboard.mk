# Disabled phase-based low-note experiment and reproducible evidence.
.PHONY: test-phase-low-keyboard screen-phase-low-keyboard
test-phase-low-keyboard: tests/test_phase_low_keyboard.py scripts/phase_low_keyboard_reference.py
	.separator-venv/bin/python tests/test_phase_low_keyboard.py
screen-phase-low-keyboard: scripts/screen_phase_low_keyboard.py
	.separator-venv/bin/python scripts/screen_phase_low_keyboard.py

.PHONY: test-native-phase-low-keyboard build-phase-low-keyboard
$(BUILD_DIR)/phase_low_keyboard_test: tests/phase_low_keyboard.cpp src/phase_low_keyboard.hpp src/multiscale_low_keyboard.hpp src/low_keyboard_coherence.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-native-phase-low-keyboard: $(BUILD_DIR)/phase_low_keyboard_test
	$(BUILD_DIR)/phase_low_keyboard_test
build-phase-low-keyboard: scripts/build_phase_low_keyboard.py src/phase_low_keyboard.hpp
	.separator-venv/bin/python scripts/build_phase_low_keyboard.py

.PHONY: measure-phase-low-keyboard calibrate-phase-low-keyboard
measure-phase-low-keyboard: scripts/measure_phase_low_keyboard.py
	.separator-venv/bin/python scripts/measure_phase_low_keyboard.py
calibrate-phase-low-keyboard: scripts/measure_phase_low_keyboard.py
	.separator-venv/bin/python scripts/measure_phase_low_keyboard.py --calibration

.PHONY: validate-phase-piano-13 validate-phase-piano-15
validate-phase-piano-13: scripts/validate_phase_regressions.py
	.separator-venv/bin/python scripts/validate_phase_regressions.py --record 13
validate-phase-piano-15: scripts/validate_phase_regressions.py
	.separator-venv/bin/python scripts/validate_phase_regressions.py --record 15

.PHONY: verify-phase-low-keyboard stage-phase-low-keyboard publish-phase-low-keyboard
verify-phase-low-keyboard: scripts/checkpoint_phase_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_phase_low_keyboard.py
stage-phase-low-keyboard: scripts/checkpoint_phase_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_phase_low_keyboard.py --stage
publish-phase-low-keyboard: scripts/checkpoint_phase_low_keyboard.py
	.separator-venv/bin/python scripts/checkpoint_phase_low_keyboard.py --publish
