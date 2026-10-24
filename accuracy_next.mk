# Repeatable measurements for the next five detection improvements.
.PHONY: inspect-primary-branch
inspect-primary-branch: scripts/inspect_primary_branch.py
	$(PYTHON) scripts/inspect_primary_branch.py

$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/tempo_candidate_gate.hpp
$(BUILD_DIR)/analyzer_sustained: tests/analyzer_sustained.cpp src/analyzer.hpp $(ANALYZER_TEST_OBJ)
	$(CXX) $(CXXFLAGS) -Isrc $< $(ANALYZER_TEST_OBJ) -lm -pthread -o $@

.PHONY: test-sustained-analyzer measure-sustained-analyzer measure-sustained-analyzer-paced
test-sustained-analyzer: tests/test_sustained_analyzer.py scripts/measure_sustained_analyzer.py
	$(PYTHON) tests/test_sustained_analyzer.py

measure-sustained-analyzer: $(BUILD_DIR)/analyzer_sustained scripts/measure_sustained_analyzer.py
	$(PYTHON) scripts/measure_sustained_analyzer.py

measure-sustained-analyzer-paced: $(BUILD_DIR)/analyzer_sustained scripts/measure_sustained_analyzer.py
	$(PYTHON) scripts/measure_sustained_analyzer.py --paced

.PHONY: test-sustained-piano measure-sustained-piano
test-sustained-piano: tests/test_sustained_piano.py scripts/measure_sustained_piano.py
	$(PYTHON) tests/test_sustained_piano.py
measure-sustained-piano: $(BUILD_DIR)/analyzer_sustained scripts/measure_sustained_piano.py
	$(PYTHON) scripts/measure_sustained_piano.py

.PHONY: screen-next-bpm screen-next-chord screen-next-timbre screen-next-drums
.PHONY: test-next-detection
test-next-detection: tests/test_next_detection.py scripts/evaluate_next_detection.py
	$(PYTHON) tests/test_next_detection.py
screen-next-bpm: scripts/evaluate_next_detection.py
	$(PYTHON) scripts/evaluate_next_detection.py bpm
screen-next-chord: scripts/evaluate_next_detection.py
	$(PYTHON) scripts/evaluate_next_detection.py chord
screen-next-timbre: scripts/evaluate_next_detection.py
	.separator-venv/bin/python scripts/evaluate_next_detection.py timbre
screen-next-drums: scripts/evaluate_next_detection.py
	.separator-venv/bin/python scripts/evaluate_next_detection.py drum

.PHONY: screen-next-timbre-forest screen-next-drums-forest
screen-next-timbre-forest: scripts/evaluate_next_detection.py
	.separator-venv/bin/python scripts/evaluate_next_detection.py timbre --forest
screen-next-drums-forest: scripts/evaluate_next_detection.py
	.separator-venv/bin/python scripts/evaluate_next_detection.py drum --forest

$(BUILD_DIR)/tempo_candidate_gate: tests/tempo_candidate_gate.cpp src/tempo_candidate_gate.hpp src/pcm_tempo_selection.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
.PHONY: test-tempo-candidate-gate
test-tempo-candidate-gate: $(BUILD_DIR)/tempo_candidate_gate
	$(BUILD_DIR)/tempo_candidate_gate

.PHONY: plan-next-detection-publication stage-next-detection-publication commit-next-detection-publication push-next-detection-publication
plan-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py plan
stage-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py stage
commit-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py commit
push-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py push
