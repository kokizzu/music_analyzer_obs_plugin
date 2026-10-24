# Repeatable measurements for the next five detection improvements.
.PHONY: inspect-primary-branch
inspect-primary-branch: scripts/inspect_primary_branch.py
	$(PYTHON) scripts/inspect_primary_branch.py

.PHONY: prepare-native-voice-primary
prepare-native-voice-primary: scripts/prepare_native_voice_primary.py
	$(PYTHON) scripts/prepare_native_voice_primary.py

.PHONY: freeze-native-voice-hook
freeze-native-voice-hook: scripts/prepare_native_voice_primary.py
	$(PYTHON) scripts/prepare_native_voice_primary.py --freeze-hook

.PHONY: measure-native-voice-primary
measure-native-voice-primary: scripts/measure_keyboard_voice_pair.py scripts/prepare_native_voice_primary.py
	$(PYTHON) scripts/measure_keyboard_voice_pair.py --primary --spectral

$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/tempo_candidate_gate.hpp
$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/keyboard_voice_classifier.hpp src/keyboard_voice_model_data.hpp
$(BUILD_DIR)/analyzer.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/analyzer_test_basic_pitch.o $(BUILD_DIR)/analyzer_internal.o: src/native_mfcc_voice.hpp src/native_mfcc_voice_model_data.hpp src/native_timbre_features.hpp
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

.PHONY: evaluate-keyboard-voice-classifier
evaluate-keyboard-voice-classifier: scripts/evaluate_keyboard_voice_classifier.py
	.separator-venv/bin/python scripts/evaluate_keyboard_voice_classifier.py

.PHONY: evaluate-native-mfcc-voice
evaluate-native-mfcc-voice: scripts/evaluate_native_mfcc_voice.py
	.separator-venv/bin/python scripts/evaluate_native_mfcc_voice.py

.PHONY: freeze-native-mfcc-voice generate-native-mfcc-voice
freeze-native-mfcc-voice: scripts/export_native_mfcc_voice.py
	$(PYTHON) scripts/export_native_mfcc_voice.py --freeze
generate-native-mfcc-voice: scripts/export_native_mfcc_voice.py
	$(PYTHON) scripts/export_native_mfcc_voice.py

.PHONY: freeze-native-mfcc-goldens test-native-mfcc-voice check-native-mfcc-voice-parity
freeze-native-mfcc-goldens: scripts/export_native_mfcc_voice.py
	$(PYTHON) scripts/export_native_mfcc_voice.py --goldens
$(BUILD_DIR)/native_mfcc_voice: tests/native_mfcc_voice.cpp src/native_mfcc_voice.hpp src/native_mfcc_voice_model_data.hpp src/keyboard_voice_classifier.hpp src/keyboard_voice_model_data.hpp src/native_timbre_features.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-native-mfcc-voice: $(BUILD_DIR)/native_mfcc_voice tests/test_native_mfcc_voice.py
	$(PYTHON) tests/test_native_mfcc_voice.py
check-native-mfcc-voice-parity: $(BUILD_DIR)/native_mfcc_voice tests/test_native_mfcc_voice.py
	$(PYTHON) tests/test_native_mfcc_voice.py --full

.PHONY: test-drum-attack-shapes evaluate-drum-attack-shapes
test-drum-attack-shapes: tests/test_drum_attack_shapes.py scripts/evaluate_drum_attack_shapes.py
	.separator-venv/bin/python tests/test_drum_attack_shapes.py
evaluate-drum-attack-shapes: scripts/evaluate_drum_attack_shapes.py
	.separator-venv/bin/python scripts/evaluate_drum_attack_shapes.py

.PHONY: evaluate-drum-spectral-shapes
evaluate-drum-spectral-shapes: scripts/evaluate_drum_attack_shapes.py scripts/native_timbre_reference.py
	.separator-venv/bin/python scripts/evaluate_drum_attack_shapes.py --spectral

.PHONY: freeze-keyboard-voice-model generate-keyboard-voice-model test-keyboard-voice-classifier check-keyboard-voice-model-parity
freeze-keyboard-voice-model: scripts/export_keyboard_voice_model.py
	$(PYTHON) scripts/export_keyboard_voice_model.py --freeze
generate-keyboard-voice-model: scripts/export_keyboard_voice_model.py
	$(PYTHON) scripts/export_keyboard_voice_model.py
$(BUILD_DIR)/keyboard_voice_classifier: tests/keyboard_voice_classifier.cpp src/keyboard_voice_classifier.hpp src/keyboard_voice_model_data.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@

$(BUILD_DIR)/native_timbre_features: tests/native_timbre_features.cpp src/native_timbre_features.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
.PHONY: test-native-timbre-features test-native-timbre-reference
test-native-timbre-features: $(BUILD_DIR)/native_timbre_features
	$(BUILD_DIR)/native_timbre_features
test-native-timbre-reference: $(BUILD_DIR)/native_timbre_features tests/test_native_timbre_reference.py scripts/native_timbre_reference.py
	.separator-venv/bin/python tests/test_native_timbre_reference.py
test-keyboard-voice-classifier: $(BUILD_DIR)/keyboard_voice_classifier tests/test_keyboard_voice_classifier.py
	$(PYTHON) tests/test_keyboard_voice_classifier.py
check-keyboard-voice-model-parity: $(BUILD_DIR)/keyboard_voice_classifier tests/test_keyboard_voice_classifier.py
	$(PYTHON) tests/test_keyboard_voice_classifier.py --full

.PHONY: screen-next-bpm screen-next-chord screen-next-timbre screen-next-drums
.PHONY: test-next-detection
test-next-detection: tests/test_next_detection.py scripts/evaluate_next_detection.py
	$(PYTHON) tests/test_next_detection.py
screen-next-bpm: scripts/evaluate_next_detection.py
	$(PYTHON) scripts/evaluate_next_detection.py bpm
.PHONY: test-backbeat-tempo screen-backbeat-tempo
test-backbeat-tempo: tests/test_backbeat_tempo.py scripts/evaluate_backbeat_tempo.py
	$(PYTHON) tests/test_backbeat_tempo.py
screen-backbeat-tempo: scripts/evaluate_backbeat_tempo.py
	$(PYTHON) scripts/evaluate_backbeat_tempo.py
screen-next-chord: scripts/evaluate_next_detection.py
	$(PYTHON) scripts/evaluate_next_detection.py chord
.PHONY: screen-chord-source-agreement
screen-chord-source-agreement: scripts/evaluate_chord_source_agreement.py
	$(PYTHON) scripts/evaluate_chord_source_agreement.py
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

$(BUILD_DIR)/pcm_tempo_score_cache: tests/pcm_tempo_score_cache.cpp src/pcm_tempo_evidence.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
.PHONY: test-pcm-tempo-score-cache
test-pcm-tempo-score-cache: $(BUILD_DIR)/pcm_tempo_score_cache
	$(BUILD_DIR)/pcm_tempo_score_cache

.PHONY: plan-next-detection-publication stage-next-detection-publication commit-next-detection-publication push-next-detection-publication
plan-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py plan
stage-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py stage
commit-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py commit
push-next-detection-publication: scripts/publish_next_detection.py
	$(PYTHON) scripts/publish_next_detection.py push
