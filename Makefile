CXX ?= g++
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
TAR ?= tar
FFMPEG ?= ffmpeg
CURL ?= curl
ARIA2C ?= aria2c
BUILD_DIR ?= build
INSTRUMENT_SAMPLE_STORE ?= /media/kyz/sshflashtor/InstrumentSamples
INSTRUMENT_SAMPLE_STORE_LINK ?= $(BUILD_DIR)/InstrumentSamples
REAL_DATASET_ROOT ?= $(INSTRUMENT_SAMPLE_STORE_LINK)
MUSICNET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/musicnet
MUSICNET_ARCHIVE ?= $(MUSICNET_SOURCE_DIR)/musicnet.tar.gz
MUSICNET_METADATA ?= $(MUSICNET_SOURCE_DIR)/musicnet_metadata.csv
MUSICNET_MIDI_ARCHIVE ?= $(MUSICNET_SOURCE_DIR)/musicnet_midis.tar.gz
MUSICNET_EXTRACT_DIR ?= $(MUSICNET_SOURCE_DIR)/extracted
MUSICNET_20_MEASUREMENT_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_20_measurement.out
MUSICNET_FULL_MEASUREMENT_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_full_measurement.out
MUSICNET_20_ATTRIBUTE_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_20_attributes.tsv
MUSICNET_FULL_ATTRIBUTE_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_full_attributes.tsv
MUSICNET_RECORDING_MEASUREMENT_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_recording_measurement.out
MUSICNET_RECORDING_ATTRIBUTE_OUTPUT ?= $(MUSICNET_SOURCE_DIR)/musicnet_recording_attributes.tsv
MUSICNET_ANALYSIS_RECORDING_IDS ?=
MUSICNET_ANALYSIS_MAX_RECORDINGS ?= 1
MUSICNET_DOWNLOAD_CONNECTIONS ?= 8
MUSICNET_ARCHIVE_URL ?= https://zenodo.org/api/records/5120004/files/musicnet.tar.gz/content
MUSICNET_METADATA_URL ?= https://zenodo.org/api/records/5120004/files/musicnet_metadata.csv/content
MUSICNET_MIDI_ARCHIVE_URL ?= https://zenodo.org/api/records/5120004/files/musicnet_midis.tar.gz/content
URMP_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/urmp
URMP_ARCHIVE ?= $(URMP_SOURCE_DIR)/urmp-kaggle.zip
URMP_EXTRACT_DIR ?= $(URMP_SOURCE_DIR)/extracted
URMP_MEASUREMENT_OUTPUT ?= $(URMP_SOURCE_DIR)/urmp_measurement.out
URMP_TRAIT_SAMPLE_OUTPUT ?= $(URMP_SOURCE_DIR)/urmp_trait_sample.out
URMP_DOWNLOAD_CONNECTIONS ?= 8
URMP_ARCHIVE_URL ?= https://www.kaggle.com/api/v1/datasets/download/alonhaviv/multi-modal-music-performance-urmp
DETECTION_ACCURACY_REPORT ?= docs/detection_accuracy_report.md
DETECTION_ACCURACY_CHORD_TSVS ?= $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(GUITARSET_ATTRIBUTE_TSV)
DETECTION_ACCURACY_CHORD_ARGS = $(foreach path,$(wildcard $(DETECTION_ACCURACY_CHORD_TSVS)),--chord-input "$(path)")
DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV ?= $(BUILD_DIR)/vocadito_full_mix_attributes.tsv
DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG = $(if $(wildcard $(DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV)),--vocal-full-mix-input "$(DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV)")
DETECTION_ACCURACY_BACH10_GATE_ARGS = $(foreach path,$(wildcard $(BACH10_MF0_SYNTH_SHARD_OUTS)),--bach10-gate-output "$(path)")
DETECTION_ACCURACY_MUSICNET_GATE_ARG = $(if $(wildcard $(MUSICNET_FULL_MEASUREMENT_OUTPUT)),--musicnet-gate-output "$(MUSICNET_FULL_MEASUREMENT_OUTPUT)",$(if $(wildcard $(MUSICNET_20_MEASUREMENT_OUTPUT)),--musicnet-gate-output "$(MUSICNET_20_MEASUREMENT_OUTPUT)"))
DETECTION_ACCURACY_URMP_GATE_ARG = $(if $(wildcard $(URMP_MEASUREMENT_OUTPUT)),--urmp-gate-output "$(URMP_MEASUREMENT_OUTPUT)")
DETECTION_ACCURACY_DRUM_GATE_ARG = $(if $(wildcard $(DRUM_FULL_GATE_OUT)),--drum-gate-output "$(DRUM_FULL_GATE_OUT)")
ANDROID_SDK_ROOT ?= $(CURDIR)/$(BUILD_DIR)/android-sdk
ANDROID_GRADLE_VERSION ?= 8.10.2
ANDROID_EMULATOR_API ?= 35
ANDROID_EMULATOR_ABI ?= x86_64
ANDROID_EMULATOR_IMAGE ?= google_apis
ANDROID_AVD_NAME ?= music_analyzer_api$(ANDROID_EMULATOR_API)_$(ANDROID_EMULATOR_ABI)
ANDROID_AVD_HOME ?= $(CURDIR)/$(BUILD_DIR)/android-avd
ANDROID_ROUTE_INTERVAL ?= 1
ROOT ?= G
ANDROID_DEBUG_ROOT ?= $(ROOT)
ANDROID_ADB := $(ANDROID_SDK_ROOT)/platform-tools/adb
ANDROID_PROFILE_PACKAGE ?= dev.benalu.musicanalyzer.bassguitar
BASS_GUITAR_APK := android/app/build/outputs/apk/bassGuitar/debug/app-bassGuitar-debug.apk
COMPLETE_APK := android/app/build/outputs/apk/complete/debug/app-complete-debug.apk
ICON_SOURCE ?= assets/music-analyzer-icon.png
BASS_GUITAR_ICON_SOURCE ?= assets/music-analyzer-bass-guitar-icon.png
APP_ICON_HEADER := src/app_icon_rgba.hpp
BASS_GUITAR_APP_ICON_HEADER := src/app_icon_bass_guitar_rgba.hpp
ANDROID_GRADLE_BIN := $(BUILD_DIR)/gradle/gradle-$(ANDROID_GRADLE_VERSION)/bin/gradle
GRADLE ?= $(if $(wildcard $(ANDROID_GRADLE_BIN)),$(ANDROID_GRADLE_BIN),gradle)
DEPS_DIR ?= $(BUILD_DIR)/deps
BUILD_TIME := $(shell date +%Y.%m%d.%H%M)
BUILD_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
STANDALONE_VERSION := $(BUILD_TIME).$(BUILD_COMMIT)
RUN_WITH_DURATION := $(SHELL) scripts/run_with_duration.sh
REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS ?=
MEASURE_REAL_NOTE_SUMMARY_ARGS ?= --detail-limit 8 --sample-limit 5
MEASURE_ANALYZER_REPORT ?= $(BUILD_DIR)/analyzer_measurement_report.txt
PATTERN_REPORT_ARGS ?= --row-examples 6
ATTRIBUTE_ROW_REPORT_ARGS ?= --rows 16
PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS ?=
REPORT_FULL_DRUM_SKIP ?= 1
MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS ?= $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)
MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS ?= $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)
DRUM_ACTIVE_EXTRA_PROTECTED_ROWS ?= $(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)
DRUM_ACTIVE_REFRESH_FULL_ROWS = $(if $(filter $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS),$(DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)),1,0)
INSTRUMENT_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/instrument_detected_attribute_rows.tsv
REAL_NOTE_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/real_note_detected_attribute_rows.tsv
REAL_NOTE_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/real_note_miss_attribute_rows.tsv
REAL_NOTE_CANDIDATE_ROW_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv
REAL_NOTE_CANDIDATE_RULE ?=
REAL_NOTE_CANDIDATE_ARGS ?=
GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_chord_detected_attribute_rows.tsv
GUITAR_CHORD_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_chord_miss_attribute_rows.tsv
GUITAR_CANDIDATE_ROW_PATHS ?= $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GUITARSET_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS) $(EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)
DRUM_CANDIDATE_ROW_PATHS ?= $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv
DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS ?= $(wildcard $(REAL_NOTE_CANDIDATE_ROW_PATHS) $(GUITAR_CANDIDATE_ROW_PATHS) $(DRUM_CANDIDATE_ROW_PATHS) $(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS))
DETECTOR_COVERAGE_CANDIDATE_ARGS ?=
DETECTOR_COVERAGE_SUMMARY_ARGS ?= --summary-only --top 12
MEASURE_ANALYZER_ROW_DUMPS ?= $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS) $(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS) $(REAL_NOTE_MISS_ATTRIBUTE_ROWS) $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS)
CACHED_ANALYZER_ATTRIBUTE_ROW_PATHS ?= $(MEASURE_ANALYZER_ROW_DUMPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv
CACHED_ANALYZER_PATTERN_INPUT_PATHS ?= $(CACHED_ANALYZER_ATTRIBUTE_ROW_PATHS) $(BUILD_DIR)/instrument_sample_attributes.tsv $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(BUILD_DIR)/guitar_chord_mix_attributes.tsv
MEASURE_ANALYZER_PATTERN_DETECTED_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_detected.txt
MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_summary.txt
MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_instrument_owner.txt
MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_instrument_status.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_summary.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_OWNERSHIP_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_ownership.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_octave_displacement.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_row_confusion.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_visual_row_confusion.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_weak_expected.txt
MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_real_note_weak_visual_expected.txt
MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_guitar_chord.txt
MEASURE_ANALYZER_PATTERN_GUITAR_PRIMARY_ORDER_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_guitar_primary_order.txt
MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_RECOVERY_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_guitar_chord_recovery.txt
MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_guitar_chord_extra.txt
MEASURE_ANALYZER_PATTERN_DRUM_PRIMARY_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_drum_primary.txt
MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_protected_drum_primary.txt
MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_drum_spread_matrix.txt
MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_drum_active_false.txt
MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_drum_spread_exact.txt
MEASURE_ANALYZER_PATTERN_FULL_SKIP_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_full_skip.txt
MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_full_drum.txt
MEASURE_ANALYZER_PATTERN_FULL_DRUM_EXACT_REPORT := $(BUILD_DIR)/measure_analyzer_pattern_full_drum_exact.txt
MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP := $(BUILD_DIR)/measure_analyzer_pattern_drum_protected_rows.stamp
DETECTOR_IMPROVEMENT_ROUTE_REPORT ?= $(BUILD_DIR)/detector_improvement_route_scan.txt
DETECTOR_IMPROVEMENT_ROUTE_SUMMARY ?= $(BUILD_DIR)/detector_improvement_route_summary.txt
DETECTOR_IMPROVEMENT_AUDIT_REPORT ?= $(BUILD_DIR)/detector_improvement_audit.txt
DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES ?= 60
DETECTOR_IMPROVEMENT_AUDIT_TARGETS ?= detector-improvement-route-summary-refresh find-protected-drum-primary-attribute-patterns find-protected-drum-full-exact-attribute-patterns find-drum-active-false-patterns-full
MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS := \
	$(MEASURE_ANALYZER_PATTERN_DETECTED_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OWNERSHIP_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_GUITAR_PRIMARY_ORDER_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_RECOVERY_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_DRUM_PRIMARY_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_FULL_SKIP_REPORT)
MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS := \
	$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT) \
	$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_EXACT_REPORT)
MEASURE_ANALYZER_CACHED_PATTERN_DETECTED_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_detected.txt
MEASURE_ANALYZER_CACHED_PATTERN_SUMMARY_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_summary.txt
MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_OWNER_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_instrument_owner.txt
MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_STATUS_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_instrument_status.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_SUMMARY_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_summary.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OWNERSHIP_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_ownership.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_octave_displacement.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_row_confusion.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_visual_row_confusion.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_weak_expected.txt
MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_real_note_weak_visual_expected.txt
MEASURE_ANALYZER_CACHED_PATTERN_GUITAR_CHORD_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_guitar_chord.txt
MEASURE_ANALYZER_CACHED_PATTERN_DRUM_PRIMARY_REPORT := $(BUILD_DIR)/measure_analyzer_cached_pattern_drum_primary.txt
MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY := $(BUILD_DIR)/measure_analyzer_cached_pattern_candidate_summary.txt
MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY := $(BUILD_DIR)/measure_analyzer_cached_pattern_coverage_summary.txt
MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS := \
	$(MEASURE_ANALYZER_CACHED_PATTERN_DETECTED_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_SUMMARY_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_OWNER_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_STATUS_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_SUMMARY_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OWNERSHIP_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_GUITAR_CHORD_REPORT) \
	$(MEASURE_ANALYZER_CACHED_PATTERN_DRUM_PRIMARY_REPORT)
MEASURE_INSTRUMENT_PATTERN_ARGS ?= --limit 4 --min-positive-samples 20 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 1 --profile-fields 5
MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS ?= --status-bucket miss:strings --status-bucket miss:synth --limit 4 --min-positive-samples 2 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 2 --profile-fields 5 --exclude-field program_name --exclude-field note --exclude-field raw_local_best_note
MEASURE_REAL_NOTE_PATTERN_ARGS ?= --limit 4 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 1
MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 2 --beam-width 240 --show-examples 1 --show-near-misses 4 --profile-fields 5
MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 3 --beam-width 240 --show-examples 1 --show-near-misses 4 --protected-scope all --profile-fields 5
MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 2 --beam-width 240 --show-examples 1 --show-near-misses 4 --protected-scope all --include-row-context --profile-fields 5
MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 2 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 4 --protected-scope all --profile-fields 5
MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 2 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 4 --protected-scope all --include-row-context --profile-fields 5
MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS ?= $(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS)
MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS ?= --top-buckets 8 --limit 4 --min-positive-samples 1 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 4 --protected-scope all --profile-fields 5
MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS ?= --limit 8 --min-positive-samples 20 --max-negative-samples 25 --max-conditions 3 --beam-width 120 --show-examples 1 --show-near-misses 4 --protected-scope all --profile-fields 5
MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 3 --beam-width 240 --show-examples 1 --show-near-misses 4 --protected-scope all --include-row-context
MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 2 --beam-width 240 --show-examples 1 --show-near-misses 4 --protected-scope all --include-row-context --profile-fields 5
MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS ?= --top-buckets 8 --limit 8 --min-positive-samples 20 --max-negative-samples 20 --max-conditions 2 --beam-width 240 --show-examples 1 --show-near-misses 4 --protected-scope all --include-row-context --profile-fields 5
REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS ?=
REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS = $(foreach path,$(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS),--extra-candidate-path "$(path)")
REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS ?=
REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")
VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv
VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")
VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)
VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")
REAL_NOTE_RULE_CONDITIONS ?=
REAL_NOTE_RULE_GROUP_BY ?=
REAL_NOTE_RULE_CONDITION_ARGS = $(foreach condition,$(REAL_NOTE_RULE_CONDITIONS),--condition "$(condition)")
REAL_NOTE_RULE_GROUP_BY_ARGS = $(foreach field,$(REAL_NOTE_RULE_GROUP_BY),--group-by "$(field)")
REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES ?= \
	--exclude-field buffer_strongest_row \
	--exclude-field buffer_visual_strongest_row \
	--exclude-field expected_midi \
	--exclude-field expected_row_score \
	--exclude-field first_row_score \
	--exclude-field visual_first_row_score \
	--exclude-field strongest_row_score \
	--exclude-field visual_strongest_row_score \
	--exclude-field expected_first_score_ratio \
	--exclude-field expected_strongest_score_ratio \
	--exclude-field expected_visual_first_score_ratio \
	--exclude-field expected_visual_strongest_score_ratio \
	--exclude-field first_expected_score_margin \
	--exclude-field strongest_expected_score_margin \
	--exclude-field visual_first_expected_score_margin \
	--exclude-field visual_strongest_expected_score_margin \
	--exclude-field expected_strongest_pitch_level_ratio \
	--exclude-field strongest_expected_pitch_level_margin \
	--exclude-field expected_visual_strongest_pitch_level_ratio \
	--exclude-field visual_strongest_expected_pitch_level_margin \
	--exclude-field raw_expected_peak \
	--exclude-field raw_expected_ratio \
	--exclude-field raw_tuned_peak \
	--exclude-field raw_tuned_ratio \
	--exclude-field raw_tuned_cent_offset \
	--exclude-field raw_tuned_abs_cent_offset \
	--exclude-field raw_local_best_note \
	--exclude-field raw_local_best_midi \
	--exclude-field raw_local_best_peak \
	--exclude-field raw_expected_rank \
	--exclude-field raw_prev_ratio \
	--exclude-field raw_next_ratio \
	--exclude-field raw_octave_down_ratio \
	--exclude-field raw_octave_up_ratio \
	--exclude-field raw_fifth_up_ratio \
	--exclude-field raw_second_octave_up_ratio \
	--exclude-field raw_upper_major_third_ratio \
	--exclude-field raw_upper_fifth_ratio \
	--exclude-field raw_third_octave_up_ratio \
	--exclude-field raw_best_debug_delta \
	--exclude-field raw_best_debug_abs_delta \
	--exclude-field expected_row_exact_level \
	--exclude-field expected_row_pitch_level \
	--exclude-field expected_row_pitch_delta \
	--exclude-field expected_exact_row_count \
	--exclude-field expected_pitch_row_count \
	--exclude-field expected_row_visual_exact_level \
	--exclude-field expected_row_visual_pitch_level \
	--exclude-field expected_row_visual_pitch_delta \
	--exclude-field expected_visual_exact_row_count \
	--exclude-field expected_visual_pitch_row_count \
	--exclude-field strongest_row_exact_level \
	--exclude-field strongest_row_pitch_level \
	--exclude-field strongest_row_pitch_delta \
	--exclude-field visual_strongest_row_exact_level \
	--exclude-field visual_strongest_row_pitch_level \
	--exclude-field visual_strongest_row_pitch_delta \
	--exclude-field bass_level \
	--exclude-field guitar_level \
	--exclude-field piano_level \
	--exclude-field vocal_level \
	--exclude-field other_level \
	--exclude-field amb_level \
	--exclude-field bass_visual_level \
	--exclude-field guitar_visual_level \
	--exclude-field piano_visual_level \
	--exclude-field vocal_visual_level \
	--exclude-field other_visual_level \
	--exclude-field amb_visual_level \
	--exclude-field debug_delta \
	--exclude-field debug_abs_delta
MEASURE_GUITAR_PATTERN_ARGS ?= --top-buckets 4 --limit 4 --min-positive-recordings 3 --max-negative-recordings 0 --max-conditions 3 --beam-width 180 --show-examples 1
MEASURE_GUITAR_ROUTE_PATTERN_ARGS ?= $(MEASURE_GUITAR_PATTERN_ARGS) --runtime-only
EXTRA_COMPONENT_ARGS ?= --simulate-prune primary-equivalent --simulate-prune primary-equivalent-plain --simulate-prune primary-equivalent-plain-observed-playable --simulate-prune common-observed-playable --simulate-prune primary-same-root-equivalent --simulate-prune observed-playable --simulate-prune primary-equivalent-observed-playable
MEASURE_DRUM_PATTERN_ARGS ?= --top-routes 4 --limit 4 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 3 --beam-width 220 --show-examples 1
MEASURE_PROTECTED_DRUM_PATTERN_ARGS ?= --top-routes 4 --limit 4 --min-positive-samples 20 --min-route-positive-samples 20 --max-negative-samples 0 --max-new-active-samples 0 --max-primary-break-samples 0 --max-conditions 1 --beam-width 40 --show-examples 1 --show-near-misses 2
MEASURE_DRUM_FULL_PATTERN_ARGS ?= --top-routes 4 --limit 4 --min-positive-samples 20 --min-route-positive-samples 20 --max-negative-samples 0 --max-new-active-samples 0 --max-primary-break-samples 0 --max-conditions 3 --beam-width 64 --show-examples 1 --show-near-misses 2 --profile-fields 5
MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS ?= --top-routes 6 --limit 6 --min-positive-samples 8 --max-protected-samples 0 --max-conditions 2 --beam-width 160 --show-examples 1 --show-near-misses 2 --protected-margin 0.002 --protected-relative-margin 0.001 --min-near-protected-score 0.10 --exclude-fields kick_level
DRUM_PATTERN_JOBS ?= $(PARALLEL_TEST_JOBS)
REAL_NOTE_PATTERN_JOBS ?= $(PARALLEL_TEST_JOBS)
INSTRUMENT_PATTERN_JOBS ?= $(PARALLEL_TEST_JOBS)
DISPLAY_SHADOW_JOBS ?= $(REAL_NOTE_PATTERN_JOBS)
OBS_USER_PLUGIN_DIR ?= $(HOME)/.config/obs-studio/plugins/music-analyzer-obs/bin/64bit
URMP_FIXTURE_ARCHIVE := tests/fixtures/urmp-mini.tar.gz
DIRECT_FIT_SMALL_FIXTURE_ARCHIVE := tests/fixtures/direct-fit-small.tar.gz
URMP_FIXTURE_DIR := $(BUILD_DIR)/urmp-fixture
BACH10_FIXTURE_DIR := $(BUILD_DIR)/bach10-fixture
BACH10_MF0_SYNTH_URL ?= https://zenodo.org/api/records/1481156/files/Bach10-mf0-syth.tar.gz/content
BACH10_MF0_SYNTH_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/bach10_mf0_synth
BACH10_MF0_SYNTH_ARCHIVE ?= $(BACH10_MF0_SYNTH_SOURCE_DIR)/Bach10-mf0-syth.tar.gz
BACH10_MF0_SYNTH_SOURCE_ROOT ?=
BACH10_MF0_SYNTH_SAMPLE_DIR ?= $(BUILD_DIR)/bach10_mf0_synth_musicnet
BACH10_MF0_SYNTH_RECORDING_LIMIT ?= 0
BACH10_MF0_SYNTH_MIN_RECORDINGS ?= 10
BACH10_MF0_SYNTH_REQUIRED_WINDOWS ?= 40
BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING ?= 4
BACH10_MF0_SYNTH_MIN_RECALL_PERCENT ?= 40
BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT ?= 60
BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT ?= 0
BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT ?= 0
BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT ?= 50
BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT ?= 55
BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT ?= 50
BACH10_MF0_SYNTH_SHARDS ?= 4
BACH10_MF0_SYNTH_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(BACH10_MF0_SYNTH_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
BACH10_MF0_SYNTH_SHARD_TARGETS := $(addprefix test-bach10-mf0-synth-samples-shard-,$(BACH10_MF0_SYNTH_SHARD_INDEXES))
BACH10_MF0_SYNTH_SHARD_OUTS := $(addprefix $(BUILD_DIR)/bach10_mf0_synth_samples_shard_,$(addsuffix .out,$(BACH10_MF0_SYNTH_SHARD_INDEXES)))
BACH10_MF0_SYNTH_LOCK_DIR ?= $(BUILD_DIR)/bach10_mf0_synth_samples.lock
BACH10_MF0_SYNTH_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(BACH10_MF0_SYNTH_SHARD_INDEXES)))
DIRECT_FIT_SMALL_FIXTURE_DIR := $(BUILD_DIR)/direct-fit-small-fixture
MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/musicnet-fixture
MEDLEYDB_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/medleydb-musicnet-fixture
SLAKH_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/slakh-musicnet-fixture
CHORALSYNTH_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/choralsynth-musicnet-fixture
COCOCHORALES_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/cocochorales-musicnet-fixture
SYNTHSOD_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/synthsod-musicnet-fixture
SYNTHSOD_ARCHIVE_EXTRACT_DIR := $(BUILD_DIR)/synthsod-archives
POLYVOCAL_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/polyvocal-musicnet-fixture
PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/prepared-multitrack-musicnet-fixture
REAL_GOAL_FIXTURE_DIR := $(BUILD_DIR)/real-goal-fixture
REAL_GOAL_PARALLEL_FIXTURE_DIR ?= $(BUILD_DIR)/real-goal-fixture-parallel
REAL_GOAL_URMP_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/urmp-fixture
REAL_GOAL_MUSICNET_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/musicnet-fixture
REAL_GOAL_MEDLEYDB_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/medleydb-fixture
REAL_GOAL_MUSDB_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/musdb-fixture
REAL_GOAL_SLAKH_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/slakh-fixture
REAL_GOAL_CHORALSYNTH_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/choralsynth-fixture
REAL_GOAL_COCOCHORALES_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/cocochorales-fixture
REAL_GOAL_SYNTHSOD_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/synthsod-fixture
REAL_GOAL_POLYVOCAL_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/polyvocal-fixture
REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/prepared-multitrack-fixture
REAL_GOAL_SPHERES_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/spheres-fixture
REAL_GOAL_MULTTIPOP_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/multtipop-fixture
REAL_GOAL_MULTTIPOP_AUDIO_DIR := $(REAL_GOAL_FIXTURE_DIR)/multtipop-audio
REAL_GOAL_GUITARSET_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/guitarset-fixture
GUITARSET_MANIFEST := $(BUILD_DIR)/guitarset-manifest.tsv
REAL_GOAL_MAESTRO_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/maestro-fixture
REAL_GOAL_EGMD_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/egmd-fixture
REAL_GOAL_MEDLEYDB_AUDIO_DIR := $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)/MedleyDB
REAL_GOAL_MEDLEYDB_ANNOTATION_DIR := $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)/Annotations
REAL_GOAL_FIXTURE_PREP_TARGETS := \
	prepare-real-goal-urmp-fixture \
	prepare-real-goal-musicnet-fixture \
	prepare-real-goal-medleydb-fixture \
	prepare-real-goal-musdb-fixture \
	prepare-real-goal-slakh-fixture \
	prepare-real-goal-choralsynth-fixture \
	prepare-real-goal-cocochorales-fixture \
	prepare-real-goal-synthsod-fixture \
	prepare-real-goal-polyvocal-fixture \
	prepare-real-goal-prepared-multitrack-fixture \
	prepare-real-goal-multtipop-fixture \
	prepare-real-goal-spheres-fixture \
	prepare-real-goal-guitarset-fixture \
	prepare-real-goal-maestro-fixture \
	prepare-real-goal-egmd-fixture
DRUM_SAMPLE_SOURCE_DIR ?= /media/kyz/sshflashtor/DrumSamples
DRUM_SAMPLE_BUILD_DIR ?= $(BUILD_DIR)/drum_samples
DRUM_SAMPLE_LIMIT ?= 160
DRUM_SAMPLE_SELECTION ?= spread
DRUM_SAMPLE_SOURCE_FILTER ?=
DRUM_SAMPLE_MIN_PRECISION_PERCENT ?= 20
DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT ?= 62
DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT ?= 80
DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT ?= 88
DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT ?= 95
DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT ?= 80
DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT ?= 88
DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT ?= 85
DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT ?= 22
DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT ?= 38
DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT ?= 20
UNRAR ?= unrar
DRUM_SAMPLE_SPREAD_BUILD_DIR ?= $(BUILD_DIR)/drum_samples_spread
DRUM_SAMPLE_SPREAD_LIMIT ?= 240
DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT ?= 40
DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT ?= 15
DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT ?= 55
DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT ?= 80
DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT ?= 90
DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT ?= 95
DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT ?= 78
DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT ?= 88
DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT ?= 86
DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT ?= 90
DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT ?= 78
DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT ?= 88
DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT ?= 68
DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT ?= 70
DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT ?= 64
DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT ?= 78
DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT ?= 24
DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT ?= 45
DRUM_SAMPLE_FULL_BUILD_DIR ?= $(BUILD_DIR)/drum_samples_full
DRUM_SAMPLE_FULL_LIMIT ?= 0
DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT ?= 35
DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT ?= 3
DRUM_SAMPLE_FULL_MIN_KICK_RECALL_PERCENT ?= 48
DRUM_SAMPLE_FULL_MIN_SNARE_RECALL_PERCENT ?= 85
DRUM_SAMPLE_FULL_MIN_HIHAT_RECALL_PERCENT ?= 94
DRUM_SAMPLE_FULL_MIN_CRASH_RECALL_PERCENT ?= 95
DRUM_SAMPLE_FULL_MIN_TOM_RECALL_PERCENT ?= 65
DRUM_SAMPLE_FULL_MIN_RIDE_RECALL_PERCENT ?= 90
DRUM_SAMPLE_FULL_MIN_RIM_RECALL_PERCENT ?= 88
DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT ?= 91
DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT ?= 72
DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT ?= 80
DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT ?= 60
DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT ?= 60
DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT ?= 58
DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT ?= 64
DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT ?= 45
DRUM_SPREAD_GATE_OUT ?= $(BUILD_DIR)/drum_samples_spread_gate.out
DRUM_SPREAD_GATE_ERR ?= $(BUILD_DIR)/drum_samples_spread_gate.err
DRUM_SPREAD_GATE_SUMMARY ?= $(BUILD_DIR)/drum_samples_spread_gate_matrix.txt
DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/drum_spread_exact_attribute_rows.tsv
DRUM_ACTIVE_SIM_ARGS ?=
PRIMARY_DRUM_DEBUG_ERRS ?= $(BUILD_DIR)/kick_primary_debug.err $(BUILD_DIR)/tom_primary_debug.err $(BUILD_DIR)/snare_primary_debug.err $(BUILD_DIR)/hihat_primary_debug.err $(BUILD_DIR)/crash_primary_debug.err $(BUILD_DIR)/ride_primary_debug.err $(BUILD_DIR)/rim_primary_debug.err
DRUM_FULL_GATE_OUT ?= $(BUILD_DIR)/drum_samples_full_gate.out
DRUM_FULL_GATE_ERR ?= $(BUILD_DIR)/drum_samples_full_gate.err
DRUM_FULL_GATE_SUMMARY ?= $(BUILD_DIR)/drum_samples_full_gate_matrix.txt
DRUM_FULL_EXACT_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/drum_full_exact_attribute_rows.tsv
DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/drum_full_merged_expected_attribute_rows.tsv
DRUM_SPREAD_EXACT_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_spread_exact_attribute_rows.lock
DRUM_SAMPLE_SHARD_CATEGORIES := kick snare hihat crash tom ride rim
DRUM_SAMPLE_SHARD_TARGETS := $(addprefix test-drum-samples-shard-,$(DRUM_SAMPLE_SHARD_CATEGORIES))
DRUM_SAMPLE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/drum_samples_test_shard_,$(addsuffix .out,$(DRUM_SAMPLE_SHARD_CATEGORIES)))
DRUM_SAMPLE_LOCK_DIR ?= $(BUILD_DIR)/drum_samples.lock
DRUM_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_SAMPLE_SHARD_CATEGORIES)))
DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES := kick snare hihat crash tom ride rim
DRUM_SAMPLE_SPREAD_SHARD_TARGETS := $(addprefix test-drum-samples-spread-shard-,$(DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES))
DRUM_SAMPLE_SPREAD_TEST_SHARD_OUTS := $(addprefix $(BUILD_DIR)/drum_samples_spread_test_shard_,$(addsuffix .out,$(DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES)))
DRUM_SAMPLE_SPREAD_SHARD_OUTS := $(addprefix $(BUILD_DIR)/drum_samples_spread_shard_,$(addsuffix .out,$(DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES)))
DRUM_SPREAD_EXACT_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_spread_exact_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES)))
DRUM_SAMPLE_SPREAD_LOCK_DIR ?= $(BUILD_DIR)/drum_samples_spread.lock
DRUM_SAMPLE_SPREAD_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_SAMPLE_SPREAD_SHARD_CATEGORIES)))
DRUM_SAMPLE_FULL_SHARD_CATEGORIES := kick snare hihat crash tom ride rim
DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY ?= 4
DRUM_SAMPLE_FULL_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
DRUM_SAMPLE_FULL_SHARD_IDS := $(foreach category,$(DRUM_SAMPLE_FULL_SHARD_CATEGORIES),$(addprefix $(category)-,$(DRUM_SAMPLE_FULL_SHARD_INDEXES)))
DRUM_SAMPLE_FULL_SHARD_TARGETS := $(addprefix test-drum-samples-full-shard-,$(DRUM_SAMPLE_FULL_SHARD_IDS))
DRUM_SAMPLE_FULL_SHARD_OUTS := $(addprefix $(BUILD_DIR)/drum_samples_full_shard_,$(addsuffix .out,$(DRUM_SAMPLE_FULL_SHARD_IDS)))
DRUM_SAMPLE_FULL_LOCK_DIR ?= $(BUILD_DIR)/drum_samples_full.lock
DRUM_FULL_EXACT_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_full_exact_attribute_rows.lock
DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/drum_full_merged_expected_attribute_rows.lock
DRUM_FULL_EXACT_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_full_exact_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_FULL_SHARD_IDS)))
DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/drum_full_merged_expected_attribute_rows_,$(addsuffix .tsv,$(DRUM_SAMPLE_FULL_SHARD_IDS)))
DRUM_SAMPLE_FULL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_SAMPLE_FULL_SHARD_IDS)))
FULL_DRUM_DEBUG_ERRS ?= $(BUILD_DIR)/full_kick_debug.err $(BUILD_DIR)/full_snare_debug.err $(BUILD_DIR)/full_tom_debug.err $(BUILD_DIR)/full_rim_debug.err
DRUM_MACHINE_SAMPLE_BUILD_DIR ?= $(BUILD_DIR)/drum_machine_samples
DRUM_MACHINE_SAMPLE_LIMIT ?= 0
DRUM_MACHINE_SAMPLE_FILTER ?= Roland TR-909 Drum Samples|dr202_samples.zip|JazzFunkKit.rar
DRUM_MACHINE_MIN_RECALL_PERCENT ?= 35
DRUM_MACHINE_MIN_PRECISION_PERCENT ?= 5
DRUM_MACHINE_MIN_KICK_RECALL_PERCENT ?= 50
DRUM_MACHINE_MIN_SNARE_RECALL_PERCENT ?= 80
DRUM_MACHINE_MIN_HIHAT_RECALL_PERCENT ?= 90
DRUM_MACHINE_MIN_CRASH_RECALL_PERCENT ?= 80
DRUM_MACHINE_MIN_TOM_RECALL_PERCENT ?= 65
DRUM_MACHINE_MIN_RIDE_RECALL_PERCENT ?= 85
DRUM_MACHINE_MIN_RIM_RECALL_PERCENT ?= 60
DRUM_MACHINE_MAX_KICK_FALSE_PERCENT ?= 24
DRUM_MACHINE_MAX_TOM_FALSE_PERCENT ?= 64
DRUM_MACHINE_SHARD_CATEGORIES := kick snare hihat crash tom ride rim
DRUM_MACHINE_SHARD_TARGETS := $(addprefix test-drum-machine-samples-shard-,$(DRUM_MACHINE_SHARD_CATEGORIES))
DRUM_MACHINE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/drum_machine_samples_shard_,$(addsuffix .out,$(DRUM_MACHINE_SHARD_CATEGORIES)))
DRUM_MACHINE_SAMPLE_LOCK_DIR ?= $(BUILD_DIR)/drum_machine_samples.lock
DRUM_MACHINE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(DRUM_MACHINE_SHARD_CATEGORIES)))
HF_DRUM_KIT_SAMPLE_DIR ?= $(BUILD_DIR)/hf_drum_kit_samples
HF_DRUM_KIT_LIMIT_PER_CATEGORY ?= 300
HF_DRUM_KIT_MIN_RECALL_PERCENT ?= 20
HF_DRUM_KIT_MIN_PRECISION_PERCENT ?= 18
HF_DRUM_KIT_MIN_KICK_PRIMARY_PERCENT ?= 90
HF_DRUM_KIT_MIN_SNARE_PRIMARY_PERCENT ?= 96
HF_DRUM_KIT_MIN_HIHAT_PRIMARY_PERCENT ?= 96
HF_DRUM_KIT_MIN_CRASH_PRIMARY_PERCENT ?= 90
HF_DRUM_KIT_MIN_TOM_PRIMARY_PERCENT ?= 92
HF_DRUM_KIT_MIN_RIDE_PRIMARY_PERCENT ?= 96
HF_DRUM_KIT_MIN_RIM_PRIMARY_PERCENT ?= 92
HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT ?= 12
HF_DRUM_KIT_PRIMARY_DEBUG_OUT ?= $(BUILD_DIR)/hf_drum_kit_primary_debug.out
HF_DRUM_KIT_PRIMARY_DEBUG_ERR ?= $(BUILD_DIR)/hf_drum_kit_primary_debug.err
HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/hf_drum_kit_primary_attribute_rows.tsv
HF_DRUM_KIT_PRIMARY_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_primary_attribute_rows.lock
HF_DRUM_KIT_SHARD_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_samples.lock
HF_DRUM_KIT_PREP_LOCK_DIR ?= $(BUILD_DIR)/hf_drum_kit_prepare.lock
HF_DRUM_KIT_SHARD_CATEGORIES := kick snare hihat crash tom ride rim
HF_DRUM_KIT_SHARD_TARGETS := $(addprefix test-hf-drum-kit-samples-shard-,$(HF_DRUM_KIT_SHARD_CATEGORIES))
HF_DRUM_KIT_SHARD_OUTS := $(addprefix $(BUILD_DIR)/hf_drum_kit_samples_shard_,$(addsuffix .out,$(HF_DRUM_KIT_SHARD_CATEGORIES)))
HF_DRUM_KIT_PRIMARY_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_,$(addsuffix .tsv,$(HF_DRUM_KIT_SHARD_CATEGORIES)))
HF_DRUM_KIT_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(HF_DRUM_KIT_SHARD_CATEGORIES)))
IDMT_DRUMS_URL ?= https://zenodo.org/api/records/7544164/files/IDMT-SMT-DRUMS-V2.zip/content
IDMT_DRUMS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/idmt_drums
IDMT_DRUMS_ARCHIVE ?= $(IDMT_DRUMS_SOURCE_DIR)/IDMT-SMT-DRUMS-V2.zip
IDMT_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/idmt_drums_samples
IDMT_DRUMS_LIMIT_PER_CATEGORY ?= 0
IDMT_DRUMS_MIN_PER_CATEGORY ?= 300
IDMT_DRUMS_MIN_RECALL_PERCENT ?= 70
IDMT_DRUMS_MIN_SNARE_RECALL_PERCENT ?= 90
IDMT_DRUMS_MIN_SNARE_PRIMARY_RECALL_PERCENT ?= 80
IDMT_DRUMS_MIN_PRECISION_PERCENT ?= 50
IDMT_DRUMS_MAX_KICK_FALSE_PERCENT ?= 12
IDMT_DRUMS_DOWNLOAD_CONNECTIONS ?= 8
IDMT_DRUMS_PRIMARY_DEBUG_OUT ?= $(BUILD_DIR)/idmt_drums_primary_debug.out
IDMT_DRUMS_PRIMARY_DEBUG_ERR ?= $(BUILD_DIR)/idmt_drums_primary_debug.err
IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_drums_primary_attribute_rows.tsv
IDMT_DRUMS_PRIMARY_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_primary_attribute_rows.lock
IDMT_DRUMS_SHARD_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_samples.lock
IDMT_DRUMS_ARCHIVE_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_archive.lock
IDMT_DRUMS_PREP_LOCK_DIR ?= $(BUILD_DIR)/idmt_drums_prepare.lock
IDMT_DRUMS_SHARD_CATEGORIES := kick snare hihat
IDMT_DRUMS_SHARD_TARGETS := $(addprefix test-idmt-drums-samples-shard-,$(IDMT_DRUMS_SHARD_CATEGORIES))
IDMT_DRUMS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/idmt_drums_samples_shard_,$(addsuffix .out,$(IDMT_DRUMS_SHARD_CATEGORIES)))
IDMT_DRUMS_PRIMARY_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/idmt_drums_primary_attribute_rows_,$(addsuffix .tsv,$(IDMT_DRUMS_SHARD_CATEGORIES)))
IDMT_DRUMS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(IDMT_DRUMS_SHARD_CATEGORIES)))
DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS ?= $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)
MDB_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/mdb_drums_samples
MDB_DRUMS_SOURCE_ROOT ?=
MDB_DRUMS_RECORDING_LIMIT ?= 0
MDB_DRUMS_MIN_RECORDINGS ?= 20
MDB_DRUMS_REQUIRED_WINDOWS ?= 80
MDB_DRUMS_MIN_RECALL_PERCENT ?= 70
MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT ?= 0
MDB_DRUMS_MIN_PRECISION_PERCENT ?= 55
MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT ?= 70
MDB_DRUMS_MISS_LOG ?= $(BUILD_DIR)/mdb_drums_misses.log
MDB_DRUMS_WINDOW_LOG ?= $(BUILD_DIR)/mdb_drums_windows.log
MDB_DRUMS_SHARDS ?= 4
MDB_DRUMS_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MDB_DRUMS_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MDB_DRUMS_SHARD_TARGETS := $(addprefix test-mdb-drums-samples-shard-,$(MDB_DRUMS_SHARD_INDEXES))
MDB_DRUMS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/mdb_drums_samples_shard_,$(addsuffix .out,$(MDB_DRUMS_SHARD_INDEXES)))
MDB_DRUMS_LOCK_DIR ?= $(BUILD_DIR)/mdb_drums_samples.lock
MDB_DRUMS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MDB_DRUMS_SHARD_INDEXES)))
BPM_DIAG_TOLERANCE ?= 8
EGMD_BPM_MAX_SECONDS ?= 20
MDB_BPM_MAX_SECONDS ?= 20
EGMD_BPM_LOG ?= $(BUILD_DIR)/egmd_bpm_diagnostics.log
REAL_EGMD_BPM_LOG ?= $(BUILD_DIR)/real_egmd_bpm_diagnostics.log
MDB_BPM_LOG ?= $(BUILD_DIR)/mdb_bpm_diagnostics.log
STAR_DRUMS_URL ?= https://zenodo.org/records/15690078/files/STAR_Drums_preview.zip?download=1
STAR_DRUMS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/star_drums
STAR_DRUMS_ARCHIVE ?= $(STAR_DRUMS_SOURCE_DIR)/STAR_Drums_preview.zip
STAR_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/star_drums_preview_samples
STAR_DRUMS_AUDIO_FLAVOR ?= mix
STAR_DRUMS_RECORDING_LIMIT ?= 0
STAR_DRUMS_MIN_RECORDINGS ?= 4
STAR_DRUMS_REQUIRED_WINDOWS ?= 12
STAR_DRUMS_MIN_RECALL_PERCENT ?= 60
STAR_DRUMS_MIN_WINDOW_RECALL_PERCENT ?= 0
STAR_DRUMS_MIN_PRECISION_PERCENT ?= 65
STAR_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT ?= 75
STAR_DRUMS_MISS_LOG ?= $(BUILD_DIR)/star_drums_misses.log
STAR_DRUMS_SHARDS ?= 4
STAR_DRUMS_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(STAR_DRUMS_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
STAR_DRUMS_SHARD_TARGETS := $(addprefix test-star-drums-samples-shard-,$(STAR_DRUMS_SHARD_INDEXES))
STAR_DRUMS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/star_drums_samples_shard_,$(addsuffix .out,$(STAR_DRUMS_SHARD_INDEXES)))
STAR_DRUMS_LOCK_DIR ?= $(BUILD_DIR)/star_drums_samples.lock
STAR_DRUMS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(STAR_DRUMS_SHARD_INDEXES)))
MEDLEY_SOLOS_URL ?= https://zenodo.org/api/records/3464194/files/Medley-solos-DB.tar.gz/content
MEDLEY_SOLOS_METADATA_URL ?= https://zenodo.org/api/records/3464194/files/Medley-solos-DB_metadata.csv/content
MEDLEY_SOLOS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/medley_solos
MEDLEY_SOLOS_ARCHIVE ?= $(MEDLEY_SOLOS_SOURCE_DIR)/Medley-solos-DB.tar.gz
MEDLEY_SOLOS_METADATA ?= $(MEDLEY_SOLOS_SOURCE_DIR)/Medley-solos-DB_metadata.csv
MEDLEY_SOLOS_SAMPLE_DIR ?= $(BUILD_DIR)/medley_solos_samples
MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT ?= 120
MEDLEY_SOLOS_MIN_SAMPLES ?= 600
MEDLEY_SOLOS_MIN_COUNTS ?= guitar=100,piano=100,vocals=100,other=300
MEDLEY_SOLOS_MIN_RECALL_PERCENT ?= 20
MEDLEY_SOLOS_SHARDS ?= 4
MEDLEY_SOLOS_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MEDLEY_SOLOS_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MEDLEY_SOLOS_SHARD_TARGETS := $(addprefix test-medley-solos-samples-shard-,$(MEDLEY_SOLOS_SHARD_INDEXES))
MEDLEY_SOLOS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/medley_solos_samples_shard_,$(addsuffix .out,$(MEDLEY_SOLOS_SHARD_INDEXES)))
MEDLEY_SOLOS_LOCK_DIR ?= $(BUILD_DIR)/medley_solos_samples.lock
MEDLEY_SOLOS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MEDLEY_SOLOS_SHARD_INDEXES)))
MAPS_PIANO_URL ?= https://zenodo.org/api/records/18160555/files/ENSTDkCl.zip/content
MAPS_PIANO_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/maps_piano
MAPS_PIANO_ARCHIVE ?= $(MAPS_PIANO_SOURCE_DIR)/ENSTDkCl.zip
MAPS_PIANO_SAMPLE_DIR ?= $(BUILD_DIR)/maps_piano_samples
MAPS_PIANO_NOTE_SAMPLE_DIR ?= $(BUILD_DIR)/maps_piano_note_samples
MAPS_PIANO_RECORDING_LIMIT ?= 80
MAPS_PIANO_MIN_RECORDINGS ?= 40
MAPS_PIANO_REQUIRED_WINDOWS ?= 80
MAPS_PIANO_MAX_WINDOWS_PER_RECORDING ?= 4
MAPS_PIANO_MIN_RECALL_PERCENT ?= 40
MAPS_PIANO_MIN_PRECISION_PERCENT ?= 75
MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT ?= 60
MAPS_PIANO_MAX_CONTAMINATION_PERCENT ?= 5
MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT ?= 5
MAPS_PIANO_MIN_CHORD_RECALL_PERCENT ?= 20
MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT ?= 70
MAPS_PIANO_MIN_CHORD_CHECKS ?= 20
MAPS_PIANO_KINDS ?= UCHO,RAND,MUS
MAPS_PIANO_SHARDS ?= 4
MAPS_PIANO_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MAPS_PIANO_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MAPS_PIANO_SHARD_TARGETS := $(addprefix test-maps-piano-samples-shard-,$(MAPS_PIANO_SHARD_INDEXES))
MAPS_PIANO_SHARD_OUTS := $(addprefix $(BUILD_DIR)/maps_piano_samples_shard_,$(addsuffix .out,$(MAPS_PIANO_SHARD_INDEXES)))
MAPS_PIANO_LOCK_DIR ?= $(BUILD_DIR)/maps_piano_samples.lock
MAPS_PIANO_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MAPS_PIANO_SHARD_INDEXES)))
MAPS_PIANO_NOTE_RECORDING_LIMIT ?= 240
MAPS_PIANO_NOTE_MIN_RECORDINGS ?= 160
MAPS_PIANO_NOTE_REQUIRED_WINDOWS ?= 160
MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING ?= 2
MAPS_PIANO_NOTE_MIN_RECALL_PERCENT ?= 70
MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT ?= 80
MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT ?= 90
MAPS_PIANO_NOTE_MAX_CONTAMINATION_PERCENT ?= 5
MAPS_PIANO_NOTE_MAX_FALSE_NON_KEYBOARD_PERCENT ?= 5
MAPS_PIANO_NOTE_SHARDS ?= 4
MAPS_PIANO_NOTE_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MAPS_PIANO_NOTE_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MAPS_PIANO_NOTE_SHARD_TARGETS := $(addprefix test-maps-piano-note-samples-shard-,$(MAPS_PIANO_NOTE_SHARD_INDEXES))
MAPS_PIANO_NOTE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/maps_piano_note_samples_shard_,$(addsuffix .out,$(MAPS_PIANO_NOTE_SHARD_INDEXES)))
MAPS_PIANO_NOTE_LOCK_DIR ?= $(BUILD_DIR)/maps_piano_note_samples.lock
MAPS_PIANO_NOTE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MAPS_PIANO_NOTE_SHARD_INDEXES)))
INSTRUMENT_SAMPLE_BUILD_ROOT ?= $(BUILD_DIR)
INSTRUMENT_SAMPLE_SOURCE_DIR ?= $(BUILD_DIR)/instrument_sample_sources
INSTRUMENT_SAMPLE_SOUNDFONT ?=
INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE ?= fluid-soundfont-gm
INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY ?= 0
INSTRUMENT_SAMPLE_DRUM_KITS ?= 8
INSTRUMENT_SAMPLE_TARGET_PER_FAMILY ?= 1000
INSTRUMENT_SAMPLE_JOBS ?= 4
INSTRUMENT_ATTRIBUTE_ARGS ?= --top 12 --examples 5
MEASURE_REAL_NOTE_ARGS ?= --detail-limit 12 --sample-limit 24
MEASURE_GUITAR_BUCKET_ARGS ?= --top-misses 8
REAL_SAMPLE_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)
NSYNTH_SAMPLE_URL ?= http://download.magenta.tensorflow.org/datasets/nsynth/nsynth-test.jsonwav.tar.gz
NSYNTH_SAMPLE_ARCHIVE ?= $(REAL_SAMPLE_SOURCE_DIR)/nsynth-test.jsonwav.tar.gz
NSYNTH_SAMPLE_ROOT ?= $(REAL_SAMPLE_SOURCE_DIR)/nsynth-test
REAL_NOTE_SAMPLE_DIR ?= $(BUILD_DIR)/real_note_samples
REAL_NOTE_SAMPLE_LIMIT ?= 0
GUITAR_FRETBOARD_NOTES_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_fretboard_notes_samples
GUITAR_FRETBOARD_NOTES_LIMIT ?= 0
GUITAR_FRETBOARD_NOTES_OFFLINE ?= 1
GUITAR_FRETBOARD_NOTES_MIN_GUITAR ?= 390
GUITAR_FRETBOARD_NOTES_MAX_FAILURES ?= 1
GUITAR_TECHS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/guitar_techs
GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE ?= $(GUITAR_TECHS_SOURCE_DIR)/P1_singlenotes.zip
GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE ?= $(GUITAR_TECHS_SOURCE_DIR)/P2_singlenotes.zip
GUITAR_TECHS_P1_CHORDS_ARCHIVE ?= $(GUITAR_TECHS_SOURCE_DIR)/P1_chords.zip
GUITAR_TECHS_P2_CHORDS_ARCHIVE ?= $(GUITAR_TECHS_SOURCE_DIR)/P2_chords.zip
GUITAR_TECHS_P1_SINGLENOTES_URL ?= https://zenodo.org/api/records/14963133/files/P1_singlenotes.zip/content
GUITAR_TECHS_P2_SINGLENOTES_URL ?= https://zenodo.org/api/records/14963133/files/P2_singlenotes.zip/content
GUITAR_TECHS_P1_CHORDS_URL ?= https://zenodo.org/api/records/14963133/files/P1_chords.zip/content
GUITAR_TECHS_P2_CHORDS_URL ?= https://zenodo.org/api/records/14963133/files/P2_chords.zip/content
GUITAR_TECHS_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_techs_samples
GUITAR_TECHS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitar_techs_attributes.tsv
GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_detected_attribute_rows.tsv
GUITAR_TECHS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_miss_attribute_rows.tsv
GUITAR_TECHS_SAMPLE_LIMIT ?= 0
GUITAR_TECHS_MIN_GUITAR ?= 200
GUITAR_TECHS_MAX_FAILURES ?= 0
GUITAR_TECHS_CHORD_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_techs_chord_samples
GUITAR_TECHS_CHORD_MANIFEST ?= $(GUITAR_TECHS_CHORD_SAMPLE_DIR)/manifest.tsv
GUITAR_TECHS_CHORD_ATTRIBUTE_STEM ?= $(BUILD_DIR)/guitar_techs_chord_attributes
GUITAR_TECHS_CHORD_ATTRIBUTE_TSV ?= $(GUITAR_TECHS_CHORD_ATTRIBUTE_STEM).tsv
GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_chord_detected_attribute_rows.tsv
GUITAR_TECHS_CHORD_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_chord_miss_attribute_rows.tsv
GUITAR_TECHS_CHORD_CASE_ID ?= guitar_techs_chords_P2_chords_micamp_set2_m7b5_0063_6149
GUITAR_TECHS_CHORD_CASE_MANIFEST ?= $(BUILD_DIR)/guitar_techs_chord_case_manifest.tsv
GUITAR_TECHS_CHORD_CASE_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitar_techs_chord_case_attributes.tsv
GUITAR_TECHS_CHORD_CASE_OUT ?= $(BUILD_DIR)/guitar_techs_chord_case.out
GUITAR_TECHS_CHORD_SAMPLE_LIMIT ?= 0
# The current public P1/P2 archives provide 7,016 usable labelled chord excerpts.
GUITAR_TECHS_CHORD_MIN_EXCERPTS ?= 3000
GUITAR_TECHS_CHORD_MIN_WINDOWS ?= 3000
GUITAR_TECHS_CHORD_MIN_RECALL_PERCENT ?= 80
GUITAR_TECHS_CHORD_MIN_PRECISION_PERCENT ?= 80
GUITAR_TECHS_CHORD_MIN_GUITAR_RECALL_PERCENT ?= 80
# Full P1/P2 coverage has 7,484 labelled windows. Probe-supported rootless
# maj7 and dominant-seventh recovery reaches 7,207 / 7,484 (96.30%).
GUITAR_TECHS_CHORD_MIN_CHORD_RECALL_PERCENT ?= 96.25
GUITAR_TECHS_CHORD_MIN_CHORD_PRECISION_PERCENT ?= 87
GUITAR_TECHS_CHORD_MAX_CONTAMINATION_PERCENT ?= 5
GUITAR_TECHS_CHORD_MAX_FALSE_VOCAL_PERCENT ?= 5
GUITAR_TECHS_DOWNLOAD_CONNECTIONS ?= 8
GUITAR_CHORD_MIX_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_chord_mix_samples
GUITAR_CHORD_MIX_MANIFEST ?= $(GUITAR_CHORD_MIX_SAMPLE_DIR)/manifest.tsv
GUITAR_CHORD_MIX_LIMIT ?= 0
GUITAR_CHORD_MIX_MIN_EXCERPTS ?= 500
GUITAR_CHORD_MIX_MIN_WINDOWS ?= 500
GUITAR_CHORD_MIX_MIN_RECALL_PERCENT ?= 75
GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT ?= 65
GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT ?= 75
GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT ?= 93
GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT ?= 95
GUITAR_CHORD_MIX_MIN_CHORD_HITS ?= 480
GUITAR_CHORD_MIX_MIN_PRIMARY_CHORD_HITS ?= 400
GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT ?= 20
GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT ?= 5
GUITAR_CHORD_MIX_MISS_LOG ?= $(BUILD_DIR)/guitar_chord_mix_misses.log
EGFXSET_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/egfxset_guitar_samples
EGFXSET_GUITAR_MANIFEST ?= $(EGFXSET_GUITAR_SAMPLE_DIR)/manifest.tsv
EGFXSET_GUITAR_ATTRIBUTE_TSV ?= $(BUILD_DIR)/egfxset_guitar_attributes.tsv
EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/egfxset_guitar_detected_attribute_rows.tsv
EGFXSET_GUITAR_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/egfxset_guitar_miss_attribute_rows.tsv
EGFXSET_GUITAR_PATTERN_BUCKET ?= single_note_false_chord:any:any
EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET ?= no_chord:any:any
EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKETS ?= $(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET) chord_hit:any:any
EGFXSET_GUITAR_PATTERN_PROTECTED_PATHS ?= $(EGFXSET_GUITAR_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv
EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET_ARGS = $(foreach bucket,$(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKETS),--protected-bucket "$(bucket)")
EGFXSET_GUITAR_PATTERN_PROTECTED_PATH_ARGS = $(foreach path,$(EGFXSET_GUITAR_PATTERN_PROTECTED_PATHS),--protected-path "$(path)")
EGFXSET_GUITAR_SAMPLE_LIMIT ?= 0
EGFXSET_GUITAR_DOWNLOAD_JOBS ?= 8
EGFXSET_GUITAR_MIN_EXCERPTS ?= 490
EGFXSET_GUITAR_MIN_WINDOWS ?= 490
EGFXSET_GUITAR_MIN_RECALL_PERCENT ?= 75
EGFXSET_GUITAR_MIN_PRECISION_PERCENT ?= 65
EGFXSET_GUITAR_MIN_GUITAR_RECALL_PERCENT ?= 75
EGFXSET_GUITAR_MAX_CONTAMINATION_PERCENT ?= 35
EGFXSET_GUITAR_MAX_FALSE_VOCAL_PERCENT ?= 10
EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT ?= 1
EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_COUNT ?= 2
GAPS_GUITAR_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/gaps
GAPS_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/gaps_guitar_samples
GAPS_GUITAR_MANIFEST ?= $(GAPS_GUITAR_SAMPLE_DIR)/manifest.tsv
GAPS_GUITAR_ATTRIBUTE_TSV ?= $(BUILD_DIR)/gaps_guitar_attributes.tsv
GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/gaps_guitar_detected_attribute_rows.tsv
GAPS_GUITAR_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/gaps_guitar_miss_attribute_rows.tsv
GAPS_GUITAR_METADATA_URL ?= https://huggingface.co/datasets/xavriley/GAPS/raw/main/gaps_metadata_with_splits.csv
GAPS_GUITAR_BASE_URL ?= https://huggingface.co/datasets/xavriley/GAPS/resolve/main
GAPS_GUITAR_OFFLINE ?= 0
GAPS_GUITAR_SAMPLE_LIMIT ?= 42
GAPS_GUITAR_MIN_EXCERPTS ?= 40
GAPS_GUITAR_MIN_NOTES ?= 12
GAPS_GUITAR_MIN_WINDOWS ?= 120
GAPS_GUITAR_MIN_RECALL_PERCENT ?= 65
GAPS_GUITAR_MIN_PRECISION_PERCENT ?= 60
GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT ?= 65
GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT ?= 51
GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT ?= 56
GAPS_GUITAR_MAX_CONTAMINATION_PERCENT ?= 35
GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT ?= 10
GAPS_GUITAR_MISS_LOG ?= $(BUILD_DIR)/gaps_guitar_misses.log
GAPS_GUITAR_FULL_SAMPLE_DIR ?= $(BUILD_DIR)/gaps_guitar_samples_full
GAPS_GUITAR_FULL_MANIFEST ?= $(GAPS_GUITAR_FULL_SAMPLE_DIR)/manifest.tsv
GAPS_GUITAR_FULL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/gaps_guitar_full_attributes.tsv
GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/gaps_guitar_full_detected_attribute_rows.tsv
GAPS_GUITAR_FULL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/gaps_guitar_full_miss_attribute_rows.tsv
GAPS_GUITAR_FULL_SAMPLE_LIMIT ?= 0
GAPS_GUITAR_FULL_MIN_EXCERPTS ?= 90
GAPS_GUITAR_FULL_MIN_WINDOWS ?= 500
GAPS_GUITAR_FULL_MISS_LOG ?= $(BUILD_DIR)/gaps_guitar_full_misses.log
GUITAR_ANALYSIS_NOTE_PATH ?= $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)
GUITARSET_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/guitarset
# Keep the downloaded archives and the extracted multi-gigabyte GuitarSet audio
# in the external sample store.  build/InstrumentSamples is its stable project
# symlink, so analyzer targets remain self-contained without filling the repo disk.
GUITARSET_ROOT ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/guitarset
GUITARSET_MISS_LOG ?= $(BUILD_DIR)/guitarset_verbose.log
GUITARSET_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitarset_attributes.tsv
GUITARSET_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitarset_detected_attribute_rows.tsv
GUITARSET_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitarset_miss_attribute_rows.tsv
GUITARSET_ANNOTATION_ARCHIVE ?= $(GUITARSET_SOURCE_DIR)/annotation.zip
GUITARSET_AUDIO_ARCHIVE ?= $(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip
GUITARSET_DOWNLOAD_LOCK_DIR ?= $(BUILD_DIR)/guitarset_download.lock
GUITARSET_ANNOTATION_URL ?= https://zenodo.org/api/records/3371780/files/annotation.zip/content
GUITARSET_AUDIO_URL ?= https://zenodo.org/api/records/3371780/files/audio_mono-mic.zip/content
GUITARSET_MIN_RECALL_PERCENT ?= 75
GUITARSET_MIN_PRECISION_PERCENT ?= 65
GUITARSET_MIN_GUITAR_RECALL_PERCENT ?= 75
GUITARSET_MIN_CHORD_RECALL_PERCENT ?= 69
GUITARSET_MIN_CHORD_PRECISION_PERCENT ?= 71
GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT ?= 84
GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT ?= 52
GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT ?= 75
GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT ?= 84
GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT ?= 65
PHILHARMONIA_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/philharmonia
PHILHARMONIA_SAMPLE_DIR ?= $(BUILD_DIR)/philharmonia_samples
PHILHARMONIA_ATTRIBUTE_TSV ?= $(BUILD_DIR)/philharmonia_attributes.tsv
PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_detected_attribute_rows.tsv
PHILHARMONIA_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_miss_attribute_rows.tsv
PHILHARMONIA_SAMPLE_LIMIT ?= 5000
PHILHARMONIA_BASE_URL ?= https://philharmonia-assets.s3-eu-west-1.amazonaws.com/uploads/2020/02/12112005
PHILHARMONIA_MIN_SAMPLES ?= 1000
PHILHARMONIA_FULL_SAMPLE_DIR ?= $(BUILD_DIR)/philharmonia_samples_full
PHILHARMONIA_FULL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/philharmonia_full_attributes.tsv
PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_full_detected_attribute_rows.tsv
PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/philharmonia_full_miss_attribute_rows.tsv
PHILHARMONIA_FULL_SAMPLE_LIMIT ?= 0
PHILHARMONIA_FULL_MIN_SAMPLES ?= 2500
PHILHARMONIA_FULL_MIN_BASS ?= 80
PHILHARMONIA_FULL_MIN_GUITAR ?= 140
PHILHARMONIA_FULL_MIN_OTHER ?= 2200
PHILHARMONIA_FULL_MAX_FAILURES ?= 25
PHILHARMONIA_FULL_PROGRESS_EVERY ?= 250
GOOD_SOUNDS_URL ?= https://zenodo.org/api/records/820937/files/good-sounds.zip/content
GOOD_SOUNDS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/good_sounds
GOOD_SOUNDS_ARCHIVE ?= $(GOOD_SOUNDS_SOURCE_DIR)/good-sounds.zip
GOOD_SOUNDS_SAMPLE_DIR ?= $(BUILD_DIR)/good_sounds_samples
GOOD_SOUNDS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/good_sounds_attributes.tsv
GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_detected_attribute_rows.tsv
GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_miss_attribute_rows.tsv
GOOD_SOUNDS_SAMPLE_LIMIT ?= 1000
GOOD_SOUNDS_MIN_SAMPLES ?= 500
GOOD_SOUNDS_MIN_BASS ?= 50
GOOD_SOUNDS_MIN_OTHER ?= 450
GOOD_SOUNDS_MAX_FAILURES ?= 20
GOOD_SOUNDS_DOWNLOAD_CONNECTIONS ?= 8
IOWA_PIANO_PAGE_URL ?= https://theremin.music.uiowa.edu/MISpiano.html
IOWA_PIANO_FILE_BASE_URL ?= https://theremin.music.uiowa.edu/sound files/MIS/Piano_Other/piano/
IOWA_PIANO_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_piano
IOWA_PIANO_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_piano_samples
IOWA_PIANO_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_piano_attributes.tsv
IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_piano_detected_attribute_rows.tsv
IOWA_PIANO_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_piano_miss_attribute_rows.tsv
IOWA_PIANO_SAMPLE_LIMIT ?= 85
IOWA_PIANO_MIN_PIANO ?= 85
IOWA_PIANO_DOWNLOAD_RETRIES ?= 4
IOWA_BASS_ZIP_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Double Bass/Bass.pizz.ff.sulE.stereo.zip
IOWA_BASS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_bass
IOWA_BASS_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_bass_samples
IOWA_BASS_SAMPLE_LIMIT ?= 24
IOWA_BASS_MIN_BASS ?= 20
IOWA_ZIP_DOWNLOAD_RETRIES ?= 4
IOWA_STRINGS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_orchestra
IOWA_STRINGS_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_strings_samples
IOWA_STRINGS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_strings_attributes.tsv
IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_strings_detected_attribute_rows.tsv
IOWA_STRINGS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_strings_miss_attribute_rows.tsv
IOWA_STRINGS_SAMPLE_LIMIT ?= 80
IOWA_STRINGS_MIN_SAMPLES ?= 60
IOWA_STRINGS_MIN_BASS ?= 0
IOWA_STRINGS_MIN_OTHER ?= 60
IOWA_STRINGS_MAX_FAILURES ?= 8
IOWA_STRINGS_VIOLIN_ARCO_SULG_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Violin/Violin.arco.ff.sulG.stereo.zip
IOWA_STRINGS_VIOLA_ARCO_SULC_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Viola/Viola.arco.ff.sulC.stereo.zip
IOWA_STRINGS_CELLO_ARCO_SULC_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Cello/Cello.arco.ff.sulC.stereo.zip
IOWA_STRINGS_SPEC_ARGS = \
	--spec "other|strings|iowa-violin-arco-2012|$(IOWA_STRINGS_VIOLIN_ARCO_SULG_URL)" \
	--spec "other|strings|iowa-viola-arco-2012|$(IOWA_STRINGS_VIOLA_ARCO_SULC_URL)" \
	--spec "other|strings|iowa-cello-arco-2012|$(IOWA_STRINGS_CELLO_ARCO_SULC_URL)"
IOWA_ORCHESTRA_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_orchestra
IOWA_ORCHESTRA_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_orchestra_samples
IOWA_ORCHESTRA_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_orchestra_attributes.tsv
IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_detected_attribute_rows.tsv
IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_miss_attribute_rows.tsv
IOWA_ORCHESTRA_SAMPLE_LIMIT ?= 480
IOWA_ORCHESTRA_MIN_SAMPLES ?= 240
IOWA_ORCHESTRA_MIN_BASS ?= 20
IOWA_ORCHESTRA_MIN_OTHER ?= 220
IOWA_ORCHESTRA_MAX_FAILURES ?= 16
IOWA_ORCHESTRA_SPEC_ARGS = \
	--spec "other|woodwind|iowa-flute-vib-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Woodwinds/Flute/Flute.vib.ff.stereo.zip" \
	--spec "other|woodwind|iowa-oboe-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Woodwinds/Oboe/Oboe.ff.stereo.zip" \
	--spec "other|woodwind|iowa-bb-clarinet-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Woodwinds/Bb Clarinet/BbClarinet.ff.stereo.zip" \
	--spec "other|brass|iowa-horn-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Brass/Horn/Horn.ff.stereo.zip" \
	--spec "other|brass|iowa-bb-trumpet-vib-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Brass/BbTrumpet/Trumpet.vib.ff.stereo.zip" \
	--spec "other|strings|iowa-violin-arco-ff-sulg|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Violin/Violin.arco.ff.sulG.stereo.zip" \
	--spec "bass|bass|iowa-double-bass-pizz-ff-sule|$(IOWA_BASS_ZIP_URL)" \
	--spec "other|pitched-percussion|iowa-marimba-yarn-ff|https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Percussion/Marimba/Marimba.yarn.ff.stereo.zip"
IOWA_ORCHESTRA_FULL_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_orchestra
IOWA_ORCHESTRA_FULL_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_orchestra_full_samples
IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_orchestra_full_attributes.tsv
IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_full_detected_attribute_rows.tsv
IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/iowa_orchestra_full_miss_attribute_rows.tsv
IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT ?= 720
IOWA_ORCHESTRA_FULL_MIN_SAMPLES ?= 520
IOWA_ORCHESTRA_FULL_MIN_BASS ?= 20
IOWA_ORCHESTRA_FULL_MIN_OTHER ?= 480
IOWA_ORCHESTRA_FULL_MAX_FAILURES ?= 20
IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE ?= 1
IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT ?= 180
IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES ?= 1
IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES ?= 6
IOWA_ORCHESTRA_FULL_SPEC_ARGS = \
	--spec "bass|bass|iowa-double-bass-pizz-ff-sule|$(IOWA_BASS_ZIP_URL)"
IOWA_ORCHESTRA_FULL_PAGE_ARGS = \
	--page-spec "other|woodwind|iowa-flute-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISFlute2012.html" \
	--page-spec "other|woodwind|iowa-alto-flute-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISaltoflute2012.html" \
	--page-spec "other|woodwind|iowa-bass-flute-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBassFlute2012.html" \
	--page-spec "other|woodwind|iowa-oboe-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISOboe2012.html" \
	--page-spec "other|woodwind|iowa-eb-clarinet-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISEbClarinet2012.html" \
	--page-spec "other|woodwind|iowa-bb-clarinet-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBbClarinet2012.html" \
	--page-spec "other|woodwind|iowa-bass-clarinet-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBbBassClarinet2012.html" \
	--page-spec "other|woodwind|iowa-bassoon-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBassoon2012.html" \
	--page-spec "other|woodwind|iowa-soprano-sax-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBbSopranoSaxophone2012.html" \
	--page-spec "other|woodwind|iowa-alto-sax-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISEbAltoSaxophone2012.html" \
	--page-spec "other|brass|iowa-horn-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISHorn2012.html" \
	--page-spec "other|brass|iowa-bb-trumpet-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBbTrumpet2012.html" \
	--page-spec "other|brass|iowa-tenor-trombone-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISTenorTrombone2012.html" \
	--page-spec "other|brass|iowa-bass-trombone-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBassTrombone2012.html" \
	--page-spec "other|brass|iowa-tuba-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISTuba2012.html" \
	--page-spec "other|strings|iowa-violin-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISViolin2012.html" \
	--page-spec "other|strings|iowa-viola-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISViola2012.html" \
	--page-spec "other|strings|iowa-cello-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISCello2012.html" \
	--page-spec "bass|bass|iowa-double-bass-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISDoubleBass2012.html" \
	--page-spec "other|pitched-percussion|iowa-marimba-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISMarimba2012.html" \
	--page-spec "other|pitched-percussion|iowa-xylophone-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISxylophone2012.html" \
	--page-spec "other|pitched-percussion|iowa-vibraphone-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISVibraphone2012.html" \
	--page-spec "other|pitched-percussion|iowa-bells-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISBells2012.html" \
	--page-spec "other|pitched-percussion|iowa-crotales-page|https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISCrotales2012.html"
IDMT_BASS_LINES_URL ?= https://zenodo.org/api/records/7544099/files/IDMT-SMT-BASS-SINGLE-TRACKS.zip/content
IDMT_BASS_LINES_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/idmt_bass_lines
IDMT_BASS_LINES_ARCHIVE ?= $(IDMT_BASS_LINES_SOURCE_DIR)/IDMT-SMT-BASS-SINGLE-TRACKS.zip
IDMT_BASS_LINES_SAMPLE_DIR ?= $(BUILD_DIR)/idmt_bass_lines_samples
IDMT_BASS_LINES_ATTRIBUTE_TSV ?= $(BUILD_DIR)/idmt_bass_lines_attributes.tsv
IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_bass_lines_detected_attribute_rows.tsv
IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_bass_lines_miss_attribute_rows.tsv
IDMT_BASS_LINES_SAMPLE_LIMIT ?= 0
IDMT_BASS_LINES_MIN_BASS ?= 600
IDMT_BASS_LINES_MAX_FAILURES ?= 0
IDMT_BASS_LINES_EXPRESSIONS ?= NO
IDMT_BASS_LINES_MIN_NOTE_DURATION ?= 0.18
IDMT_GUITAR_URL ?= https://zenodo.org/api/records/7544110/files/IDMT-SMT-GUITAR_V2.zip/content
IDMT_GUITAR_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/idmt_guitar
IDMT_GUITAR_ARCHIVE ?= $(IDMT_GUITAR_SOURCE_DIR)/IDMT-SMT-GUITAR_V2.zip
IDMT_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/idmt_guitar_samples
IDMT_GUITAR_ATTRIBUTE_TSV ?= $(BUILD_DIR)/idmt_guitar_attributes.tsv
IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_guitar_detected_attribute_rows.tsv
IDMT_GUITAR_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/idmt_guitar_miss_attribute_rows.tsv
IDMT_GUITAR_SAMPLE_LIMIT ?= 0
IDMT_GUITAR_MIN_GUITAR ?= 200
IDMT_GUITAR_MAX_FAILURES ?= 8
IDMT_GUITAR_EXPRESSIONS ?=
IDMT_GUITAR_DOWNLOAD_CONNECTIONS ?= 8
TINYSOL_METADATA_URL ?= https://zenodo.org/api/records/3632193/files/TinySOL_metadata.csv/content
TINYSOL_ARCHIVE_URL ?= https://zenodo.org/api/records/3632193/files/TinySOL.zip/content
TINYSOL_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/tinysol
TINYSOL_ARCHIVE ?= $(TINYSOL_SOURCE_DIR)/TinySOL.zip
TINYSOL_METADATA_PATH ?= $(TINYSOL_SOURCE_DIR)/TinySOL_metadata.csv
TINYSOL_SAMPLE_DIR ?= $(BUILD_DIR)/tinysol_samples
TINYSOL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/tinysol_attributes.tsv
TINYSOL_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/tinysol_detected_attribute_rows.tsv
TINYSOL_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/tinysol_miss_attribute_rows.tsv
TINYSOL_SAMPLE_LIMIT ?= 0
TINYSOL_MIN_SAMPLES ?= 1000
TINYSOL_MIN_BASS ?= 100
TINYSOL_MIN_PIANO ?= 50
TINYSOL_MIN_OTHER ?= 800
TINYSOL_DOWNLOAD_CONNECTIONS ?= 8
VOCADITO_URL ?= https://zenodo.org/api/records/5578807/files/vocadito.zip/content
VOCADITO_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/vocadito
VOCADITO_ARCHIVE ?= $(VOCADITO_SOURCE_DIR)/vocadito.zip
VOCADITO_SAMPLE_DIR ?= $(BUILD_DIR)/vocadito_samples
VOCADITO_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocadito_attributes.tsv
VOCADITO_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocadito_detected_attribute_rows.tsv
VOCADITO_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocadito_miss_attribute_rows.tsv
VOCADITO_SAMPLE_LIMIT ?= 0
VOCADITO_MIN_VOCALS ?= 300
VOCADITO_MAX_FAILURES ?= 0
VOCADITO_ANNOTATOR ?= A1
VOCADITO_MAX_CENTS ?= 25
VOCADITO_MIN_NOTE_DURATION ?= 0.22
VOCADITO_DOWNLOAD_CONNECTIONS ?= 8
VOCADITO_FULL_MIX_MIN_ANY_HIT_PERCENT ?= 100
VOCADITO_FULL_MIX_MIN_EXPECTED_ROW_PERCENT ?= 25
VOCADITO_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT ?= 80
VOCADITO_FULL_MIX_MIN_FIRST_ROW_PERCENT ?= 5
VOCADITO_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT ?= 5
VOCADITO_FULL_MIX_MIN_VISUAL_ROW_PERCENT ?= 4
VOCADITO_FULL_MIX_MIN_VOCALS_VISUAL_ROW_PERCENT ?= 4
VOCADITO_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT ?= 25
VOCALSET_URL ?= https://zenodo.org/api/records/10200775/files/VocalSet.zip/content
VOCALSET_ARCHIVE_BYTES ?= 2488206010
VOCALSET_ARCHIVE_MD5 ?= 8d39344bbc775aa040840783ae73cfa4
VOCALSET_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/vocalset
VOCALSET_ARCHIVE ?= $(VOCALSET_SOURCE_DIR)/VocalSet.zip
VOCALSET_SAMPLE_DIR ?= $(BUILD_DIR)/vocalset_samples
VOCALSET_DOWNLOAD_LOCK_DIR ?= $(BUILD_DIR)/vocalset_download.lock
VOCALSET_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocalset_attributes.tsv
VOCALSET_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocalset_detected_attribute_rows.tsv
VOCALSET_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/vocalset_miss_attribute_rows.tsv
VOCALSET_SAMPLE_LIMIT ?= 2400
VOCALSET_MIN_VOCALS ?= 2000
VOCALSET_MAX_FAILURES ?= 35
VOCALSET_MIN_VOCALS_HIT_PERCENT ?= 98
VOCALSET_MAX_CENTS ?= 25
VOCALSET_MIN_NOTE_DURATION ?= 0.22
VOCALSET_ALLOWED_TECHNIQUES ?= belt,breathy,fast_forte,fast_piano,forte,lip_trill,messa,slow_forte,slow_piano,straight,trill,trillo,vibrato
# The Zenodo content endpoint does not advertise byte-range support.  Parallel
# aria2 segments therefore produce a same-sized but corrupt archive.
VOCALSET_DOWNLOAD_CONNECTIONS ?= 1
VOCALSET_FULL_MIX_MIN_ANY_HIT_PERCENT ?= 99
VOCALSET_FULL_MIX_MIN_EXPECTED_ROW_PERCENT ?= 52
VOCALSET_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT ?= 50
VOCALSET_FULL_MIX_MIN_FIRST_ROW_PERCENT ?= 5
VOCALSET_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT ?= 5
VOCALSET_FULL_MIX_MIN_VISUAL_ROW_PERCENT ?= 6
VOCALSET_FULL_MIX_MIN_VOCALS_VISUAL_ROW_PERCENT ?= 6
VOCALSET_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT ?= 25
REAL_NOTE_MIN_BASS ?= 100
REAL_NOTE_MIN_GUITAR ?= 300
REAL_NOTE_MIN_PIANO ?= 1000
REAL_NOTE_MIN_VOCALS ?= 20
REAL_NOTE_MIN_OTHER ?= 500
REAL_NOTE_MIN_BASS_HIT_PERCENT ?= 100
REAL_NOTE_MIN_GUITAR_HIT_PERCENT ?= 100
REAL_NOTE_MIN_PIANO_HIT_PERCENT ?= 100
REAL_NOTE_MIN_VOCALS_HIT_PERCENT ?= 100
REAL_NOTE_MIN_OTHER_HIT_PERCENT ?= 100
REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT ?= 99
REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT ?= 80
REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT ?= 65
REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT ?= 70
REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT ?= 85
REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT ?= 90
REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT ?= 75
REAL_NOTE_FULL_MIX_MIN_FIRST_ROW_PERCENT ?= 25
REAL_NOTE_FULL_MIX_MIN_BASS_FIRST_ROW_PERCENT ?= 20
REAL_NOTE_FULL_MIX_MIN_GUITAR_FIRST_ROW_PERCENT ?= 40
REAL_NOTE_FULL_MIX_MIN_PIANO_FIRST_ROW_PERCENT ?= 30
REAL_NOTE_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT ?= 0
REAL_NOTE_FULL_MIX_MIN_OTHER_FIRST_ROW_PERCENT ?= 12
REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT ?= 30
REAL_NOTE_FULL_MIX_AGG_MIN_BASS_FIRST_ROW_PERCENT ?= 30
REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT ?= 43
REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_FIRST_ROW_PERCENT ?= 35
REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_FIRST_ROW_PERCENT ?= 20
REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT ?= 15
REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT ?= 38
REAL_NOTE_FULL_MIX_AGG_MIN_BASS_VISUAL_ROW_PERCENT ?= 30
REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT ?= 15
REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_VISUAL_ROW_PERCENT ?= 45
REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_VISUAL_ROW_PERCENT ?= 15
REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT ?= 30
REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT ?= 25
REAL_NOTE_FULL_MIX_MAX_FAILURES ?= 0
REAL_NOTE_FULL_MIX_GATE_ENV = \
	MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_BASS_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_GUITAR_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_PIANO_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_OTHER_FIRST_ROW_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT="$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" \
	MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_FULL_MIX_MAX_FAILURES)"
REAL_NOTE_FULL_MIX_SHARD_GATE_ENV = \
	MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 \
	MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 \
	MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999
PHILHARMONIA_MIN_BASS ?= 50
PHILHARMONIA_MIN_GUITAR ?= 140
PHILHARMONIA_MIN_OTHER ?= 1000

OBS_CFLAGS_RAW := $(shell $(PKG_CONFIG) --cflags libobs)
OBS_CFLAGS := $(filter-out -std=gnu17 -Werror,$(OBS_CFLAGS_RAW))
OBS_INCLUDEDIR := $(shell $(PKG_CONFIG) --variable=includedir libobs)
SDL2_SYSTEM_HEADER := $(firstword $(wildcard /usr/include/SDL2/SDL.h /usr/local/include/SDL2/SDL.h))
SDL2_LOCAL_HEADER := $(DEPS_DIR)/usr/include/SDL2/SDL.h
SDL2_DEP := $(if $(SDL2_SYSTEM_HEADER),,$(SDL2_LOCAL_HEADER))
SDL2_CFLAGS := $(if $(SDL2_SYSTEM_HEADER),$(shell $(PKG_CONFIG) --cflags sdl2 2>/dev/null),-I$(DEPS_DIR)/usr/include/SDL2 -I$(DEPS_DIR)/usr/include/x86_64-linux-gnu -D_REENTRANT)
SDL2_LIBS := $(if $(SDL2_SYSTEM_HEADER),$(shell $(PKG_CONFIG) --libs sdl2 2>/dev/null),/lib/x86_64-linux-gnu/libSDL2-2.0.so.0)
SIMDE_SYSTEM_HEADER := $(firstword $(wildcard /usr/include/simde/x86/sse2.h /usr/local/include/simde/x86/sse2.h))
SIMDE_LOCAL_HEADER := $(DEPS_DIR)/usr/include/simde/x86/sse2.h
SIMDE_DEP := $(if $(SIMDE_SYSTEM_HEADER),,$(SIMDE_LOCAL_HEADER))
LOCAL_SIMDE_CFLAGS := $(if $(SIMDE_SYSTEM_HEADER),,-I$(DEPS_DIR)/usr/include)
OBS_LIBS := $(shell $(PKG_CONFIG) --libs libobs)

CXXFLAGS ?= -O2 -g
CXXFLAGS += -std=c++17 -fPIC -Wall -Wextra

RENDERER_OBJ := $(BUILD_DIR)/visualizer_renderer.o
PLUGIN_OBJS := $(BUILD_DIR)/analyzer.o $(RENDERER_OBJ) $(BUILD_DIR)/plugin.o
ANALYZER_TEST_OBJ := $(BUILD_DIR)/analyzer_test.o
TEST_BINS := $(BUILD_DIR)/fret_control_tests $(BUILD_DIR)/visualizer_renderer_tests $(BUILD_DIR)/analyzer_internal $(BUILD_DIR)/analyzer_smoke $(BUILD_DIR)/analyzer_cases $(BUILD_DIR)/analyzer_midi_ranges $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd $(BUILD_DIR)/analyzer_drum_samples $(BUILD_DIR)/analyzer_instrument_samples $(BUILD_DIR)/analyzer_real_note_samples $(BUILD_DIR)/analyzer_instrument_family_samples
STANDALONE_BIN := $(BUILD_DIR)/music-analyzer-standalone
BASS_GUITAR_STANDALONE_BIN := $(BUILD_DIR)/music-analyzer-bass-guitar
ONLINE_CPU_COUNT := $(or $(shell nproc 2>/dev/null),$(shell getconf _NPROCESSORS_ONLN 2>/dev/null),4)
PARALLEL_TEST_JOBS ?= $(ONLINE_CPU_COUNT)
PARALLEL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(PARALLEL_TEST_JOBS))
REAL_GOAL_MAKE_JOBS ?= $(PARALLEL_TEST_MAKE_JOBS)
MEASURE_ANALYZER_JOBS ?= $(PARALLEL_TEST_JOBS)
MEASURE_ANALYZER_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(MEASURE_ANALYZER_JOBS))
REFRESH_ANALYZER_ATTRIBUTE_JOBS ?= $(MEASURE_ANALYZER_JOBS)
REAL_NOTE_FULL_MIX_SHARDS ?= $(PARALLEL_TEST_JOBS)
REAL_NOTE_FULL_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(REAL_NOTE_FULL_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
REAL_NOTE_FULL_MIX_SHARD_TARGETS := $(addprefix test-real-note-samples-full-mix-shard-,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES))
REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX ?= real_note_full_mix_shard
REAL_NOTE_FULL_MIX_LOCK_DIR ?= $(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX).lock
REAL_NOTE_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/real_note_full_mix_attributes.lock
REAL_NOTE_FULL_MIX_SHARD_OUTS = $(addprefix $(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_,$(addsuffix .out,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))
REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/real_note_full_mix_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))
REAL_NOTE_FULL_MIX_VERBOSE_SHARD_TARGETS := $(addprefix analyze-real-note-misses-shard-,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES))
REAL_NOTE_FULL_MIX_VERBOSE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/real_note_full_mix_verbose_shard_,$(addsuffix .out,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))
REAL_NOTE_FULL_MIX_VERBOSE_SHARD_ERRS := $(addprefix $(BUILD_DIR)/real_note_full_mix_verbose_shard_,$(addsuffix .err,$(REAL_NOTE_FULL_MIX_SHARD_INDEXES)))
REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))
REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_FULL_MIX_SHARDS))
VOCADITO_FULL_MIX_SHARDS ?= $(PARALLEL_TEST_JOBS)
VOCADITO_FULL_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(VOCADITO_FULL_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
VOCADITO_FULL_MIX_SHARD_TARGETS := $(addprefix test-vocadito-samples-full-mix-shard-,$(VOCADITO_FULL_MIX_SHARD_INDEXES))
VOCADITO_FULL_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/vocadito_full_mix_shard_,$(addsuffix .out,$(VOCADITO_FULL_MIX_SHARD_INDEXES)))
VOCADITO_FULL_MIX_LOCK_DIR ?= $(BUILD_DIR)/vocadito_full_mix_shard.lock
VOCADITO_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocadito_full_mix_attributes.tsv
VOCADITO_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/vocadito_full_mix_attributes.lock
VOCADITO_FULL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/vocadito_full_mix_attributes.shard-,$(addsuffix .tsv,$(VOCADITO_FULL_MIX_SHARD_INDEXES)))
VOCADITO_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(VOCADITO_FULL_MIX_SHARDS))
VOCADITO_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(VOCADITO_FULL_MIX_SHARDS))
REAL_NOTE_FULL_MIX_MAX_VISUAL_PIANO_ELECTRONIC_GUITAR ?= 160
REAL_NOTE_FULL_MIX_MIN_VISIBLE_LIT_EXACT_SAMPLE_PERCENT ?= 73
REAL_NOTE_FULL_MIX_MIN_VISIBLE_LIT_EXACT_FAMILY_SAMPLE_PERCENT ?= bass=90 guitar=74 piano=67 vocals=90 other=77
REAL_NOTE_FULL_MIX_MAX_ROW_SOURCE_ROUTES ?= \
	piano/electronic->guitar=320 \
	other/acoustic->guitar=195 \
	other/acoustic->piano=180 \
	piano/electronic->bass=100 \
	piano/electronic->other=95 \
	other/acoustic->bass=75 \
	guitar/acoustic->piano=75
REAL_NOTE_FULL_MIX_MAX_VISUAL_SOURCE_ROUTES ?= \
	other/acoustic->piano=190 \
	piano/electronic->bass=180 \
	piano/electronic->other=160 \
	piano/electronic->guitar=$(REAL_NOTE_FULL_MIX_MAX_VISUAL_PIANO_ELECTRONIC_GUITAR) \
	other/acoustic->bass=140 \
	guitar/acoustic->piano=135
REAL_NOTE_FULL_MIX_SOURCE_ROUTE_LIMIT_ARGS = \
	$(foreach route,$(REAL_NOTE_FULL_MIX_MAX_ROW_SOURCE_ROUTES),--max-row-source-route "$(route)") \
	$(foreach route,$(REAL_NOTE_FULL_MIX_MAX_VISUAL_SOURCE_ROUTES),--max-visual-source-route "$(route)")
REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_ARGS = \
	--check-only \
	--min-visible-lit-exact-sample-percent "$(REAL_NOTE_FULL_MIX_MIN_VISIBLE_LIT_EXACT_SAMPLE_PERCENT)" \
	$(foreach threshold,$(REAL_NOTE_FULL_MIX_MIN_VISIBLE_LIT_EXACT_FAMILY_SAMPLE_PERCENT),--min-visible-lit-exact-family-sample-percent "$(threshold)")
REAL_NOTE_SAMPLE_SHARDS ?= $(PARALLEL_TEST_JOBS)
REAL_NOTE_SAMPLE_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(REAL_NOTE_SAMPLE_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
VOCALSET_FULL_MIX_SHARDS ?= $(REAL_NOTE_SAMPLE_SHARDS)
VOCALSET_FULL_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(VOCALSET_FULL_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
VOCALSET_FULL_MIX_SHARD_TARGETS := $(addprefix test-vocalset-samples-full-mix-shard-,$(VOCALSET_FULL_MIX_SHARD_INDEXES))
VOCALSET_FULL_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/vocalset_full_mix_shard_,$(addsuffix .out,$(VOCALSET_FULL_MIX_SHARD_INDEXES)))
VOCALSET_FULL_MIX_LOCK_DIR ?= $(BUILD_DIR)/vocalset_full_mix_shard.lock
VOCALSET_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocalset_full_mix_attributes.tsv
VOCALSET_EXPANDED_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocalset_expanded_full_mix_attributes.tsv
VOCALSET_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/vocalset_full_mix_attributes.lock
VOCALSET_FULL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/vocalset_full_mix_attributes.shard-,$(addsuffix .tsv,$(VOCALSET_FULL_MIX_SHARD_INDEXES)))
VOCALSET_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(VOCALSET_FULL_MIX_SHARDS))
VOCALSET_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(VOCALSET_FULL_MIX_SHARDS))
REAL_NOTE_SAMPLE_TAG ?= isolated
REAL_NOTE_SAMPLE_ROOT ?= $(REAL_NOTE_SAMPLE_DIR)
REAL_NOTE_SAMPLE_REQUIRED_SAMPLES ?= 1000
REAL_NOTE_SAMPLE_MIN_BASS ?= 0
REAL_NOTE_SAMPLE_MIN_GUITAR ?= 0
REAL_NOTE_SAMPLE_MIN_PIANO ?= 0
REAL_NOTE_SAMPLE_MIN_VOCALS ?= 0
REAL_NOTE_SAMPLE_MIN_OTHER ?= 0
REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT ?= 0
REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT ?= 0
REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT ?= 0
REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT ?= 0
REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT ?= 0
REAL_NOTE_SAMPLE_MAX_FAILURES ?= 0
REAL_NOTE_SAMPLE_MAX_FAILURE_LINES ?= 80
REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES ?= 999999
REAL_NOTE_SAMPLE_SHARD_TARGETS := $(addprefix test-real-note-sample-shard-,$(REAL_NOTE_SAMPLE_SHARD_INDEXES))
REAL_NOTE_SAMPLE_PARALLEL_TARGETS := test-real-note-samples-parallel test-guitar-fretboard-note-samples-parallel test-guitar-techs-samples-parallel test-philharmonia-samples-parallel test-philharmonia-samples-full-parallel test-good-sounds-samples-parallel test-iowa-piano-samples-parallel test-iowa-bass-samples-parallel test-iowa-strings-samples-parallel test-iowa-orchestra-samples-parallel test-iowa-orchestra-full-samples-parallel test-idmt-bass-lines-samples-parallel test-idmt-guitar-samples-parallel test-tinysol-samples-parallel test-vocadito-samples-parallel test-vocalset-samples-parallel
REAL_NOTE_SAMPLE_SHARD_OUTS := $(addprefix $(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_,$(addsuffix .out,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
REAL_NOTE_SAMPLE_LOCK_DIR ?= $(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG).lock
IDMT_BASS_LINES_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_bass_lines_attributes.lock
IDMT_GUITAR_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/idmt_guitar_attributes.lock
GUITAR_TECHS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_techs_attributes.lock
GOOD_SOUNDS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/good_sounds_attributes.lock
TINYSOL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/tinysol_attributes.lock
VOCADITO_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/vocadito_attributes.lock
VOCALSET_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/vocalset_attributes.lock
IOWA_PIANO_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_piano_attributes.lock
IOWA_STRINGS_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_strings_attributes.lock
PHILHARMONIA_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/philharmonia_attributes.lock
PHILHARMONIA_FULL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/philharmonia_full_attributes.lock
IOWA_ORCHESTRA_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_orchestra_attributes.lock
IOWA_ORCHESTRA_FULL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_orchestra_full_attributes.lock
IDMT_BASS_LINES_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/idmt_bass_lines_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
IDMT_GUITAR_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/idmt_guitar_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
GUITAR_TECHS_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/guitar_techs_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
GOOD_SOUNDS_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/good_sounds_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
TINYSOL_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/tinysol_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
VOCADITO_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/vocadito_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
VOCALSET_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/vocalset_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
IOWA_PIANO_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/iowa_piano_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
IOWA_STRINGS_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/iowa_strings_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
PHILHARMONIA_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/philharmonia_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
PHILHARMONIA_FULL_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/philharmonia_full_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
IOWA_ORCHESTRA_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/iowa_orchestra_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
IOWA_ORCHESTRA_FULL_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/iowa_orchestra_full_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
REAL_NOTE_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(REAL_NOTE_SAMPLE_SHARDS))
REAL_NOTE_SAMPLE_HIT_PERCENT_ARGS = --min-bass-hit-percent "$(REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT)" --min-guitar-hit-percent "$(REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT)" --min-piano-hit-percent "$(REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT)" --min-vocals-hit-percent "$(REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT)" --min-other-hit-percent "$(REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT)"
RUN_REAL_NOTE_SAMPLE_SHARDS = $(MAKE) REAL_NOTE_SAMPLE_SHARDS="$(REAL_NOTE_SAMPLE_SHARDS)" REAL_NOTE_SAMPLE_TAG="$(REAL_NOTE_SAMPLE_TAG)" REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_ROOT)" REAL_NOTE_SAMPLE_REQUIRED_SAMPLES="$(REAL_NOTE_SAMPLE_REQUIRED_SAMPLES)" REAL_NOTE_SAMPLE_MIN_BASS="$(REAL_NOTE_SAMPLE_MIN_BASS)" REAL_NOTE_SAMPLE_MIN_GUITAR="$(REAL_NOTE_SAMPLE_MIN_GUITAR)" REAL_NOTE_SAMPLE_MIN_PIANO="$(REAL_NOTE_SAMPLE_MIN_PIANO)" REAL_NOTE_SAMPLE_MIN_VOCALS="$(REAL_NOTE_SAMPLE_MIN_VOCALS)" REAL_NOTE_SAMPLE_MIN_OTHER="$(REAL_NOTE_SAMPLE_MIN_OTHER)" REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT)" REAL_NOTE_SAMPLE_MAX_FAILURES="$(REAL_NOTE_SAMPLE_MAX_FAILURES)" REAL_NOTE_SAMPLE_MAX_FAILURE_LINES="$(REAL_NOTE_SAMPLE_MAX_FAILURE_LINES)" REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES="$(REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES)" test-real-note-sample-shards
RUN_REAL_NOTE_SAMPLE_SHARDS_UNLOCKED = $(MAKE) REAL_NOTE_SAMPLE_SHARDS="$(REAL_NOTE_SAMPLE_SHARDS)" REAL_NOTE_SAMPLE_TAG="$(REAL_NOTE_SAMPLE_TAG)" REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_ROOT)" REAL_NOTE_SAMPLE_REQUIRED_SAMPLES="$(REAL_NOTE_SAMPLE_REQUIRED_SAMPLES)" REAL_NOTE_SAMPLE_MIN_BASS="$(REAL_NOTE_SAMPLE_MIN_BASS)" REAL_NOTE_SAMPLE_MIN_GUITAR="$(REAL_NOTE_SAMPLE_MIN_GUITAR)" REAL_NOTE_SAMPLE_MIN_PIANO="$(REAL_NOTE_SAMPLE_MIN_PIANO)" REAL_NOTE_SAMPLE_MIN_VOCALS="$(REAL_NOTE_SAMPLE_MIN_VOCALS)" REAL_NOTE_SAMPLE_MIN_OTHER="$(REAL_NOTE_SAMPLE_MIN_OTHER)" REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT)" REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT="$(REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT)" REAL_NOTE_SAMPLE_MAX_FAILURES="$(REAL_NOTE_SAMPLE_MAX_FAILURES)" REAL_NOTE_SAMPLE_MAX_FAILURE_LINES="$(REAL_NOTE_SAMPLE_MAX_FAILURE_LINES)" REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES="$(REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES)" test-real-note-sample-shards-unlocked
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS :=
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS :=
ifneq ($(wildcard $(IDMT_BASS_LINES_ARCHIVE)),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "IDMT bass lines=$(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(IDMT_GUITAR_ARCHIVE)),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "IDMT guitar=$(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(and $(wildcard $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)),$(wildcard $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE))),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "GuitarTechs=$(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(GOOD_SOUNDS_ARCHIVE)),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Good Sounds=$(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(and $(wildcard $(TINYSOL_METADATA_PATH)),$(wildcard $(TINYSOL_ARCHIVE))),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(TINYSOL_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "TinySOL=$(TINYSOL_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(VOCADITO_ARCHIVE)),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(VOCADITO_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Vocadito=$(VOCADITO_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(VOCALSET_ARCHIVE)),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "VocalSet=$(VOCALSET_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa piano=$(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa strings=$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Philharmonia=$(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Philharmonia full=$(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa orchestra=$(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)"
endif
ifneq ($(wildcard $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv),)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS += $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)
REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS += --extra-real-note "Iowa orchestra full=$(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)"
endif
INSTRUMENT_SAMPLE_SHARDS ?= $(PARALLEL_TEST_JOBS)
INSTRUMENT_SAMPLE_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(INSTRUMENT_SAMPLE_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
INSTRUMENT_SAMPLE_SHARD_TARGETS := $(addprefix test-instrument-samples-shard-,$(INSTRUMENT_SAMPLE_SHARD_INDEXES))
INSTRUMENT_SAMPLE_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/instrument_sample_attributes.lock
INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/instrument_sample_attributes.shard-,$(addsuffix .tsv,$(INSTRUMENT_SAMPLE_SHARD_INDEXES)))
INSTRUMENT_SAMPLE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))
INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(INSTRUMENT_SAMPLE_SHARDS))
INSTRUMENT_SAMPLE_MANIFEST_STAMP := $(BUILD_DIR)/instrument_sample_manifests.stamp
GUITAR_CHORD_MIX_SHARDS ?= $(PARALLEL_TEST_JOBS)
GUITAR_CHORD_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GUITAR_CHORD_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GUITAR_CHORD_MIX_SHARD_TARGETS := $(addprefix test-guitar-chord-mix-samples-shard-,$(GUITAR_CHORD_MIX_SHARD_INDEXES))
GUITAR_CHORD_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/guitar_chord_mix_samples_shard_,$(addsuffix .out,$(GUITAR_CHORD_MIX_SHARD_INDEXES)))
GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_chord_mix_attributes.lock
GUITAR_CHORD_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/guitar_chord_mix_attributes.shard-,$(addsuffix .tsv,$(GUITAR_CHORD_MIX_SHARD_INDEXES)))
GUITAR_CHORD_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_CHORD_MIX_SHARDS))
GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_CHORD_MIX_SHARDS))
GUITAR_TECHS_CHORD_SHARDS ?= $(PARALLEL_TEST_JOBS)
GUITAR_TECHS_CHORD_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GUITAR_TECHS_CHORD_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GUITAR_TECHS_CHORD_SHARD_TARGETS := $(addprefix test-guitar-techs-chord-samples-shard-,$(GUITAR_TECHS_CHORD_SHARD_INDEXES))
GUITAR_TECHS_CHORD_SHARD_OUTS := $(addprefix $(BUILD_DIR)/guitar_techs_chord_samples_shard_,$(addsuffix .out,$(GUITAR_TECHS_CHORD_SHARD_INDEXES)))
GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitar_techs_chord_attributes.lock
GUITAR_TECHS_CHORD_ATTRIBUTE_PARTS := $(addprefix $(GUITAR_TECHS_CHORD_ATTRIBUTE_STEM).shard-,$(addsuffix .tsv,$(GUITAR_TECHS_CHORD_SHARD_INDEXES)))
GUITAR_TECHS_CHORD_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_TECHS_CHORD_SHARDS))
GUITAR_TECHS_CHORD_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITAR_TECHS_CHORD_SHARDS))
EGFXSET_GUITAR_SHARDS ?= $(PARALLEL_TEST_JOBS)
EGFXSET_GUITAR_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(EGFXSET_GUITAR_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
EGFXSET_GUITAR_SHARD_TARGETS := $(addprefix test-egfxset-guitar-samples-shard-,$(EGFXSET_GUITAR_SHARD_INDEXES))
EGFXSET_GUITAR_SHARD_OUTS := $(addprefix $(BUILD_DIR)/egfxset_guitar_samples_shard_,$(addsuffix .out,$(EGFXSET_GUITAR_SHARD_INDEXES)))
EGFXSET_GUITAR_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/egfxset_guitar_attributes.lock
EGFXSET_GUITAR_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/egfxset_guitar_attributes.shard-,$(addsuffix .tsv,$(EGFXSET_GUITAR_SHARD_INDEXES)))
EGFXSET_GUITAR_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(EGFXSET_GUITAR_SHARDS))
EGFXSET_GUITAR_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(EGFXSET_GUITAR_SHARDS))
GAPS_GUITAR_SHARDS ?= $(PARALLEL_TEST_JOBS)
GAPS_GUITAR_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GAPS_GUITAR_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GAPS_GUITAR_SHARD_TARGETS := $(addprefix test-gaps-guitar-samples-shard-,$(GAPS_GUITAR_SHARD_INDEXES))
GAPS_GUITAR_SHARD_OUTS := $(addprefix $(BUILD_DIR)/gaps_guitar_samples_shard_,$(addsuffix .out,$(GAPS_GUITAR_SHARD_INDEXES)))
GAPS_GUITAR_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/gaps_guitar_attributes.lock
GAPS_GUITAR_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/gaps_guitar_attributes.shard-,$(addsuffix .tsv,$(GAPS_GUITAR_SHARD_INDEXES)))
GAPS_GUITAR_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_SHARDS))
GAPS_GUITAR_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_SHARDS))
GAPS_GUITAR_FULL_SHARDS ?= $(PARALLEL_TEST_JOBS)
GAPS_GUITAR_FULL_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GAPS_GUITAR_FULL_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GAPS_GUITAR_FULL_SHARD_TARGETS := $(addprefix test-gaps-guitar-samples-full-shard-,$(GAPS_GUITAR_FULL_SHARD_INDEXES))
GAPS_GUITAR_FULL_SHARD_OUTS := $(addprefix $(BUILD_DIR)/gaps_guitar_samples_full_shard_,$(addsuffix .out,$(GAPS_GUITAR_FULL_SHARD_INDEXES)))
GAPS_GUITAR_FULL_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/gaps_guitar_full_attributes.lock
GAPS_GUITAR_FULL_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/gaps_guitar_full_attributes.shard-,$(addsuffix .tsv,$(GAPS_GUITAR_FULL_SHARD_INDEXES)))
GAPS_GUITAR_FULL_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_FULL_SHARDS))
GAPS_GUITAR_FULL_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GAPS_GUITAR_FULL_SHARDS))
GUITARSET_SHARDS ?= $(PARALLEL_TEST_JOBS)
GUITARSET_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GUITARSET_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GUITARSET_SHARD_TARGETS := $(addprefix test-downloaded-guitarset-shard-,$(GUITARSET_SHARD_INDEXES))
GUITARSET_SHARD_OUTS := $(addprefix $(BUILD_DIR)/guitarset_shard_,$(addsuffix .out,$(GUITARSET_SHARD_INDEXES)))
GUITARSET_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/guitarset_attributes.lock
GUITARSET_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/guitarset_attributes.shard-,$(addsuffix .tsv,$(GUITARSET_SHARD_INDEXES)))
GUITARSET_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITARSET_SHARDS))
GUITARSET_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GUITARSET_SHARDS))
GUITARSET_SHARD_GATE_ENV ?= MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0
GUITARSET_ATTRIBUTE_GATE_ENV ?= MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_ONLY=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=0 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0

.PHONY: FORCE all standalone standalone-bass-guitar setup-android setup-android-emulator android-emulator android-emulator-stop android-stop-apps android-uninstall-old-packages android-profile android-profile-bass-guitar android-profile-complete android-audio-status android-route-desktop-audio android-route-desktop-audio-watch android-grant-permissions android-install-bass-guitar android-install-complete android-run android-run-bass-guitar android-run-complete android android-complete android-bass-guitar android-check check-standalone-deps install-standalone-deps test-standalone profile-standalone prepare-drum-samples test-drum-samples prepare-drum-samples-spread test-drum-samples-spread analyze-drum-primary-misses analyze-drum-rule-grid analyze-drum-full-attribute-rows find-drum-attribute-patterns find-drum-full-attribute-patterns prepare-drum-samples-full test-drum-samples-full prepare-drum-machine-samples test-drum-machine-samples prepare-hf-drum-kit-samples test-hf-drum-kit-samples download-idmt-drums-samples prepare-idmt-drums-samples test-idmt-drums-samples prepare-mdb-drums-samples test-mdb-drums-samples analyze-mdb-drums-misses analyze-mdb-drum-attributes download-star-drums-samples prepare-star-drums-samples test-star-drums-samples analyze-star-drums-misses analyze-star-drum-attributes test-drum-real-world-samples test-drum-real-world-samples-full download-medley-solos-samples prepare-medley-solos-samples test-medley-solos-samples download-maps-piano-samples prepare-maps-piano-samples test-maps-piano-samples prepare-maps-piano-note-samples test-maps-piano-note-samples download-bach10-mf0-synth-samples prepare-bach10-mf0-synth-samples test-bach10-mf0-synth-samples prepare-instrument-samples test-instrument-samples analyze-instrument-sample-attributes download-real-note-samples prepare-real-note-samples test-real-note-samples test-real-note-samples-full-mix analyze-real-note-misses analyze-real-note-attributes inspect-real-note-attribute-buckets find-real-note-attribute-patterns prepare-guitar-fretboard-note-samples test-guitar-fretboard-note-samples download-guitar-techs-samples prepare-guitar-techs-samples test-guitar-techs-samples download-guitar-techs-chord-samples prepare-guitar-techs-chord-samples test-guitar-techs-chord-samples analyze-guitar-techs-chord-attributes analyze-guitar-techs-chord-extra-components prepare-guitar-chord-mix-samples test-guitar-chord-mix-samples analyze-guitar-chord-mix-misses analyze-guitar-chord-mix-attributes analyze-guitar-chord-mix-recovery inspect-guitar-chord-mix-attribute-buckets find-guitar-chord-mix-attribute-patterns prepare-egfxset-guitar-samples test-egfxset-guitar-samples prepare-gaps-guitar-samples test-gaps-guitar-samples analyze-gaps-guitar-misses download-guitarset-samples prepare-downloaded-guitarset test-downloaded-guitarset analyze-guitarset-misses download-philharmonia-samples prepare-philharmonia-samples test-philharmonia-samples prepare-philharmonia-samples-full test-philharmonia-samples-full download-good-sounds-samples prepare-good-sounds-samples test-good-sounds-samples prepare-iowa-piano-samples test-iowa-piano-samples prepare-iowa-bass-samples test-iowa-bass-samples prepare-iowa-strings-samples test-iowa-strings-samples prepare-iowa-orchestra-samples test-iowa-orchestra-samples prepare-iowa-orchestra-full-samples test-iowa-orchestra-full-samples download-idmt-bass-lines-samples prepare-idmt-bass-lines-samples test-idmt-bass-lines-samples download-idmt-guitar-samples prepare-idmt-guitar-samples test-idmt-guitar-samples download-tinysol-samples prepare-tinysol-samples test-tinysol-samples download-vocadito-samples prepare-vocadito-samples test-vocadito-samples test-vocadito-samples-full-mix test-vocadito-samples-full-mix-parallel test-vocadito-samples-full-mix-shard-% download-vocalset-samples prepare-vocalset-samples test-vocalset-samples test-configured-real-world-samples test-real-world-samples test-real-world-samples-full test-real-world-samples-max test-midi-ranges clean clean-pycache deps install-user test real-dataset-sources inspect-real-dataset-catalog inspect-real-goal-coverage inspect-real-goal-20 inspect-real-goal-full inspect-real-medleydb inspect-real-musdb inspect-real-slakh inspect-real-choralsynth inspect-real-cocochorales inspect-real-synthsod-remote inspect-real-synthsod extract-real-synthsod-archives inspect-real-polyvocal inspect-real-prepared-multitrack inspect-real-multtipop inspect-real-musicnet-remote inspect-real-musicnet inspect-real-musicnet-full inspect-real-spheres inspect-real-guitarset inspect-real-maestro inspect-real-egmd test-musicnet-remote test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-synthsod-remote test-synthsod-archive-extract test-synthsod-inspector test-synthsod-prepare test-polyvocal-inspector test-polyvocal-prepare test-prepared-multitrack-inspector test-prepared-multitrack-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-drum-sample-prepare test-hf-drum-kit-prepare test-idmt-drums-prepare test-mdb-drums-prepare test-star-drums-prepare test-medley-solos-prepare test-maps-piano-prepare test-bach10-mf0-synth-prepare test-instrument-sample-attribute-summary test-philharmonia-prepare test-good-sounds-prepare test-iowa-piano-prepare test-iowa-zip-prepare test-idmt-bass-lines-prepare test-idmt-guitar-prepare test-tinysol-prepare test-vocadito-prepare test-vocalset-prepare test-guitar-fretboard-note-prepare test-guitar-techs-prepare test-guitar-techs-chord-prepare test-guitar-chord-mix-prepare test-gaps-guitar-prepare test-guitarset-miss-analysis test-guitarset-attribute-summary test-guitarset-attribute-buckets test-guitarset-attribute-patterns test-real-note-miss-analysis test-real-note-attribute-summary test-real-note-attribute-buckets test-real-note-attribute-patterns test-egmd-miss-analysis test-egmd-drum-attribute-summary test-drum-primary-analysis test-real-goal-script test-real-goal-fixture test-musicnet-fixture test-medleydb-fixture test-slakh-fixture test-choralsynth-fixture test-cocochorales-fixture test-synthsod-fixture test-polyvocal-fixture test-prepared-multitrack-fixture test-multtipop-audio-root-fixture test-guitarset-fixture test-maestro-fixture test-egmd-fixture test-bach10-fixture test-direct-fit-small-fixture test-urmp-fixture test-real-goal-20 test-real-goal-full test-real-multitrack-20 test-real-multitrack-full test-real-urmp test-real-urmp-full test-real-musicnet-20 test-real-musicnet-full test-real-medleydb-20 test-real-slakh-20 test-real-slakh-full test-real-choralsynth-20 test-real-cocochorales-20 test-real-synthsod-20 test-real-synthsod-full test-real-polyvocal-20 test-real-prepared-multitrack-20 test-real-prepared-multitrack-full test-real-multtipop-20 test-real-multtipop-full test-real-guitarset-20 test-real-guitarset-full test-real-maestro-20 test-real-maestro-full test-real-egmd-20 test-real-egmd-full inspect-real-multitrack-20 inspect-real-multitrack-full inspect-real-urmp inspect-real-urmp-full inspect-urmp-fixture decode-urmp-fixture decode-direct-fit-small-fixture update-urmp-fixture update-direct-fit-small-fixture
.PHONY: find-real-note-row-confusion-patterns find-real-note-practical-row-confusion-patterns find-real-note-focused-row-confusion-patterns find-real-note-coverage-row-confusion-patterns find-real-note-visual-row-confusion-patterns find-real-note-focused-visual-row-confusion-patterns find-real-note-coverage-visual-row-confusion-patterns find-real-note-ownership-patterns find-real-note-octave-displacement-patterns find-real-note-octave-displacement-runtime-patterns find-real-note-weak-expected-patterns find-real-note-weak-visual-expected-patterns inspect-real-note-candidate-rows inspect-detector-coverage-candidates measure-real-note-octave-display-aliases evaluate-real-note-display-shadow evaluate-real-note-vocal-shadow-safety evaluate-real-note-vocal-shadow-safety-nsynth evaluate-real-note-vocal-shadow-safety-vocadito evaluate-real-note-vocal-display-fallback measure-real-note-attribute-rule analyze-vocadito-attributes analyze-vocadito-full-mix-attributes find-vocadito-full-mix-row-confusion-patterns find-vocadito-full-mix-visual-row-confusion-patterns find-vocadito-full-mix-ownership-patterns find-vocadito-full-mix-broad-vocal-ownership-patterns analyze-idmt-bass-lines-attributes analyze-idmt-guitar-attributes analyze-guitar-techs-attributes analyze-tinysol-attributes analyze-vocalset-attributes analyze-iowa-piano-attributes analyze-iowa-strings-attributes analyze-philharmonia-attributes analyze-philharmonia-full-attributes analyze-iowa-orchestra-attributes analyze-iowa-orchestra-full-attributes
.PHONY: filter-drum-primary-attribute-rows filter-drum-full-attribute-rows filter-drum-full-exact-attribute-rows test-filter-drum-attribute-rows
.PHONY: test-build-sharded-tsv test-guitarset-shard-check test-instrument-family-shard-check test-musicnet-shard-check
.PHONY: prepare-guitar-techs-chord-case inspect-guitar-techs-chord-case refresh-guitar-techs-chord-attributes
.PHONY: prepare-gaps-guitar-samples-full test-gaps-guitar-samples-full analyze-gaps-guitar-misses-full analyze-gaps-guitar-attributes inspect-gaps-guitar-attribute-buckets find-gaps-guitar-attribute-patterns analyze-gaps-guitar-full-attributes inspect-gaps-guitar-full-attribute-buckets find-gaps-guitar-full-attribute-patterns
.PHONY: analyze-guitarset-attributes inspect-guitarset-attribute-buckets find-guitarset-attribute-patterns analyze-egfxset-guitar-attributes inspect-egfxset-guitar-attribute-buckets find-egfxset-guitar-attribute-patterns
.PHONY: inspect-guitarset-download restore-guitarset-audio-partial test-guitarset-download-inspector
.PHONY: test-fret-control android-lint icon-assets
.PHONY: measure-analyzer-attributes measure-analyzer-attribute-rows measure-analyzer-attribute-rows-full require-cached-analyzer-attribute-rows refresh-analyzer-detected-attribute-rows print-analyzer-detected-attributes print-analyzer-detected-attributes-cached measure-analyzer-detected-attributes measure-analyzer-detected-attributes-full measure-analyzer-pattern-report-sections report-analyzer-patterns-from-rows report-analyzer-patterns-from-cached-rows report-analyzer-patterns-from-rows-full measure-analyzer-patterns measure-analyzer-patterns-cached measure-analyzer-patterns-cached-summary measure-analyzer-patterns-cached-coverage measure-analyzer-patterns-full measure-analyzer-pattern-report inspect-instrument-sample-owner-buckets find-instrument-owner-patterns find-instrument-status-patterns test-instrument-sample-owner-buckets test-filter-instrument-attribute-rows test-instrument-owner-patterns test-refresh-analyzer-detected-attribute-rows test-print-analyzer-detected-attributes test-analyzer-pattern-report test-detector-route-report-summary test-measure-analyzer-patterns-target analyze-drum-primary-attribute-rows find-drum-primary-attribute-patterns analyze-drum-spread-gate-matrix-serial analyze-drum-spread-gate-matrix-parallel analyze-drum-spread-gate-matrix-parallel-unlocked analyze-drum-tom-bleed-caps analyze-drum-tom-bleed-caps-cached
.PHONY: analyze-drum-spread-gate-matrix analyze-drum-full-gate-matrix analyze-drum-full-gate-matrix-parallel analyze-drum-full-merged-expected-attribute-rows analyze-drum-active-false-rows analyze-drum-rule-flags compare-drum-gate-matrix compare-drum-primary-scores find-drum-active-false-patterns find-drum-active-false-patterns-full find-drum-spread-exact-attribute-patterns find-drum-full-exact-attribute-patterns find-drum-full-exact-attribute-patterns-cached find-protected-drum-full-exact-attribute-patterns test-drum-gate-matrix-summary test-compare-drum-gate-summaries test-drum-active-threshold-simulation test-drum-active-false-summary test-drum-rule-flag-summary test-drum-active-false-patterns test-inspect-drum-candidate-rows test-inspect-real-note-candidate-rows test-inspect-detector-coverage-candidates
.PHONY: analyze-hf-drum-primary-attribute-rows analyze-hf-drum-primary-attribute-rows-serial analyze-hf-drum-primary-attribute-rows-parallel find-hf-drum-primary-attribute-patterns analyze-idmt-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows-serial analyze-idmt-drum-primary-attribute-rows-parallel find-idmt-drum-primary-attribute-patterns analyze-protected-drum-primary-attribute-rows find-protected-drum-primary-attribute-patterns
.PHONY: analyze-guitar-chord-mix-recovery analyze-guitar-chord-primary-order analyze-gaps-guitar-full-primary-order analyze-guitar-chord-mix-extra-components analyze-guitar-minor-third-candidates analyze-guitar-major-third-candidates analyze-guitar-minor-fifth-candidates analyze-guitar-major-fifth-candidates inspect-guitar-techs-chord-attribute-buckets find-guitar-techs-chord-attribute-patterns find-guitar-techs-chord-route-patterns find-guitar-chord-mix-route-patterns find-egfxset-guitar-route-patterns find-gaps-guitar-route-patterns find-gaps-guitar-full-route-patterns find-guitarset-route-patterns test-guitar-chord-recovery-analysis test-guitar-primary-order-analysis test-guitar-chord-extra-components-analysis test-guitar-techs-chord-samples-parallel test-guitar-chord-mix-samples-serial test-guitar-chord-mix-samples-parallel test-egfxset-guitar-samples-parallel test-gaps-guitar-samples-parallel test-gaps-guitar-samples-full-parallel test-downloaded-guitarset-parallel
.PHONY: audition-sample
.PHONY: find-real-note-first-row-confusion-patterns find-real-note-first-visual-row-confusion-patterns
.PHONY: analyze-real-note-misses-serial analyze-real-note-misses-parallel analyze-real-note-misses-shard-%
.PHONY: test-vocadito-samples-full-mix-parallel-unlocked
.PHONY: test-parallel test-core-parallel test-analysis-scripts-parallel test-fixtures-parallel test-fixtures-parallel-isolated test-real-note-sample-shards test-real-note-sample-shards-unlocked test-real-note-sample-shard-% $(REAL_NOTE_SAMPLE_PARALLEL_TARGETS) test-real-note-samples-full-mix-serial test-real-note-samples-full-mix-parallel test-real-note-samples-full-mix-parallel-unlocked test-real-note-samples-full-mix-detector-parallel test-real-note-visual-strength test-real-note-full-mix-shard-check test-real-note-sample-shard-check test-instrument-samples-serial test-instrument-samples-parallel test-visualizer-renderer test-analyzer-internal test-analyzer-smoke test-analyzer-cases test-analyzer-midi-ranges test-analyzer-urmp test-analyzer-musicnet test-analyzer-multtipop test-analyzer-guitarset test-analyzer-maestro test-analyzer-egmd
.PHONY: prepare-real-goal-fixtures-parallel $(REAL_GOAL_FIXTURE_PREP_TARGETS)
.PHONY: test-drum-real-world-samples-parallel test-drum-real-world-samples-full-parallel test-real-world-samples-parallel test-real-world-samples-full-parallel test-real-world-samples-max-parallel test-drum-samples-optional test-drum-samples-spread-optional test-drum-machine-samples-optional test-drum-samples-full-optional test-idmt-bass-lines-samples-optional test-idmt-guitar-samples-optional test-good-sounds-samples-optional test-medley-solos-samples-optional test-medley-solos-samples-serial test-medley-solos-samples-parallel test-medley-solos-samples-parallel-unlocked test-medley-solos-samples-shard-% test-maps-piano-samples-optional test-maps-piano-note-samples-optional test-bach10-mf0-synth-samples-optional test-bach10-mf0-synth-samples-serial test-bach10-mf0-synth-samples-parallel test-bach10-mf0-synth-samples-parallel-unlocked test-bach10-mf0-synth-samples-shard-% analyze-bach10-mf0-synth-chord-misses analyze-bach10-mf0-synth-pitch-misses test-vocalset-samples-optional test-vocalset-samples-full-mix-optional
.PHONY: test-drum-samples-full-serial test-drum-samples-full-parallel test-drum-samples-full-parallel-unlocked test-drum-samples-full-shard-% test-drum-machine-samples-serial test-drum-machine-samples-parallel test-drum-machine-samples-parallel-unlocked test-drum-machine-samples-shard-% test-hf-drum-kit-samples-serial test-hf-drum-kit-samples-parallel test-hf-drum-kit-samples-parallel-unlocked test-hf-drum-kit-samples-shard-% test-idmt-drums-samples-serial test-idmt-drums-samples-parallel test-idmt-drums-samples-parallel-unlocked test-idmt-drums-samples-shard-% test-drum-samples-full-parallel-optional test-drum-sample-shard-check
.PHONY: test-iowa-piano-samples-max test-iowa-orchestra-full-samples-max test-good-sounds-samples-max test-medley-solos-samples-max test-maps-piano-samples-max test-maps-piano-note-samples-max
.PHONY: detector-improvement-samples detector-improvement-patterns detector-improvement-patterns-cached detector-improvement-patterns-cached-summary detector-improvement-routes detector-improvement-route-report detector-improvement-route-report-refresh detector-improvement-route-summary detector-improvement-route-summary-cached detector-improvement-route-summary-refresh detector-improvement-coverage-cached detector-improvement-status-cached detector-improvement-samples-full detector-improvement-patterns-full detector-improvement-audit detector-improvement-audit-cached detector-improvement-audit-report detector-improvement-audit-report-cached analyze-detector-improvements analyze-detector-improvement-routes analyze-detector-improvements-full

.PRECIOUS: $(NSYNTH_SAMPLE_ARCHIVE) $(TINYSOL_ARCHIVE) $(GOOD_SOUNDS_ARCHIVE) $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P1_CHORDS_ARCHIVE) $(GUITAR_TECHS_P2_CHORDS_ARCHIVE) $(GUITARSET_ANNOTATION_ARCHIVE) $(GUITARSET_AUDIO_ARCHIVE) $(IDMT_DRUMS_ARCHIVE) $(IDMT_GUITAR_ARCHIVE) $(STAR_DRUMS_ARCHIVE) $(MEDLEY_SOLOS_ARCHIVE) $(MAPS_PIANO_ARCHIVE) $(BACH10_MF0_SYNTH_ARCHIVE) $(VOCALSET_ARCHIVE)

FORCE:

icon-assets: scripts/generate_icon_assets.sh
	$(SHELL) scripts/generate_icon_assets.sh "$(ICON_SOURCE)" "$(BASS_GUITAR_ICON_SOURCE)"

all: $(SIMDE_DEP) $(BUILD_DIR)/music-analyzer-obs.so

standalone: $(STANDALONE_BIN) $(BASS_GUITAR_STANDALONE_BIN)

standalone-bass-guitar: $(BASS_GUITAR_STANDALONE_BIN)

setup-android: scripts/setup_android.sh
	BUILD_DIR="$(CURDIR)/$(BUILD_DIR)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" ANDROID_GRADLE_VERSION="$(ANDROID_GRADLE_VERSION)" $(SHELL) scripts/setup_android.sh

setup-android-emulator: setup-android scripts/setup_android_emulator.sh
	BUILD_DIR="$(CURDIR)/$(BUILD_DIR)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" ANDROID_AVD_HOME="$(ANDROID_AVD_HOME)" ANDROID_EMULATOR_API="$(ANDROID_EMULATOR_API)" ANDROID_EMULATOR_ABI="$(ANDROID_EMULATOR_ABI)" ANDROID_EMULATOR_IMAGE="$(ANDROID_EMULATOR_IMAGE)" ANDROID_AVD_NAME="$(ANDROID_AVD_NAME)" $(SHELL) scripts/setup_android_emulator.sh

android-emulator:
	ANDROID_HOME="$(ANDROID_SDK_ROOT)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" ANDROID_AVD_HOME="$(ANDROID_AVD_HOME)" "$(ANDROID_SDK_ROOT)/emulator/emulator" -avd "$(ANDROID_AVD_NAME)" -gpu host

android-emulator-stop:
	-"$(ANDROID_ADB)" emu kill

android-stop-apps:
	"$(ANDROID_ADB)" wait-for-device
	-"$(ANDROID_ADB)" shell am force-stop dev.benalu.musicanalyzer.bassguitar
	-"$(ANDROID_ADB)" shell am force-stop dev.benalu.musicanalyzer.complete
	-"$(ANDROID_ADB)" shell am force-stop dev.kyz.musicanalyzer.bassguitar
	-"$(ANDROID_ADB)" shell am force-stop dev.kyz.musicanalyzer.complete

android-uninstall-old-packages:
	@if "$(ANDROID_ADB)" get-state >/dev/null 2>&1; then \
		"$(ANDROID_ADB)" uninstall dev.kyz.musicanalyzer.bassguitar || true; \
		"$(ANDROID_ADB)" uninstall dev.kyz.musicanalyzer.complete || true; \
	else \
		printf '%s\n' "android-uninstall-old-packages: no Android device/emulator connected"; \
	fi

android-profile: android-profile-bass-guitar

android-profile-bass-guitar: scripts/profile_android_app.sh
	ANDROID_ADB="$(ANDROID_ADB)" ANDROID_PROFILE_PACKAGE="$(ANDROID_PROFILE_PACKAGE)" $(SHELL) scripts/profile_android_app.sh

android-profile-complete: scripts/profile_android_app.sh
	ANDROID_ADB="$(ANDROID_ADB)" ANDROID_PROFILE_PACKAGE="dev.benalu.musicanalyzer.complete" $(SHELL) scripts/profile_android_app.sh

android-audio-status: scripts/android_audio_status.sh
	ANDROID_ADB="$(ANDROID_ADB)" $(SHELL) scripts/android_audio_status.sh

android-route-desktop-audio: scripts/route_android_emulator_audio.sh
	ANDROID_MIC_SOURCE="$(ANDROID_MIC_SOURCE)" ANDROID_ROUTE_INTERVAL="$(ANDROID_ROUTE_INTERVAL)" $(SHELL) scripts/route_android_emulator_audio.sh

android-route-desktop-audio-watch: scripts/route_android_emulator_audio.sh
	ANDROID_MIC_SOURCE="$(ANDROID_MIC_SOURCE)" ANDROID_ROUTE_INTERVAL="$(ANDROID_ROUTE_INTERVAL)" $(SHELL) scripts/route_android_emulator_audio.sh --watch

android-set-root: scripts/set_android_debug_root.sh
	ANDROID_ADB="$(ANDROID_ADB)" ANDROID_DEBUG_ROOT="$(ANDROID_DEBUG_ROOT)" $(SHELL) scripts/set_android_debug_root.sh

.PHONY: android-set-root android-measure-fret-zealot-update android-verify-fret-zealot-update

android-measure-fret-zealot-update: scripts/measure_fret_zealot_update.sh
	ANDROID_ADB="$(ANDROID_ADB)" $(SHELL) scripts/measure_fret_zealot_update.sh

android-verify-fret-zealot-update: android-check android-install-complete android-measure-fret-zealot-update

android-grant-permissions:
	"$(ANDROID_ADB)" wait-for-device
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.RECORD_AUDIO
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.BLUETOOTH_SCAN
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.BLUETOOTH_CONNECT
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.RECORD_AUDIO
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.BLUETOOTH_SCAN
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.BLUETOOTH_CONNECT

android-install-bass-guitar: android-bass-guitar
	"$(ANDROID_ADB)" wait-for-device
	"$(ANDROID_ADB)" install -r "$(BASS_GUITAR_APK)"
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.RECORD_AUDIO
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.BLUETOOTH_SCAN
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.BLUETOOTH_CONNECT

android-install-complete: android-complete
	"$(ANDROID_ADB)" wait-for-device
	"$(ANDROID_ADB)" install -r "$(COMPLETE_APK)"
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.RECORD_AUDIO
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.BLUETOOTH_SCAN
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.BLUETOOTH_CONNECT

android-run: android-run-bass-guitar

android-run-bass-guitar: android-install-bass-guitar android-stop-apps
	"$(ANDROID_ADB)" shell monkey -p dev.benalu.musicanalyzer.bassguitar -c android.intent.category.LAUNCHER 1

android-run-complete: android-install-complete android-stop-apps
	"$(ANDROID_ADB)" shell monkey -p dev.benalu.musicanalyzer.complete -c android.intent.category.LAUNCHER 1

android: android-complete android-bass-guitar

android-complete:
	ANDROID_HOME="$(ANDROID_SDK_ROOT)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" $(GRADLE) -p android :app:assembleCompleteDebug

android-bass-guitar:
	ANDROID_HOME="$(ANDROID_SDK_ROOT)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" $(GRADLE) -p android :app:assembleBassGuitarDebug

android-lint:
	ANDROID_HOME="$(ANDROID_SDK_ROOT)" ANDROID_SDK_ROOT="$(ANDROID_SDK_ROOT)" $(GRADLE) -p android :app:lintCompleteDebug :app:lintBassGuitarDebug

android-check: tests/check_android_project.py
	$(PYTHON) tests/check_android_project.py

deps: $(SIMDE_LOCAL_HEADER)

check-standalone-deps:
	@test -f "$(if $(SDL2_SYSTEM_HEADER),$(SDL2_SYSTEM_HEADER),$(SDL2_LOCAL_HEADER))"

install-standalone-deps: $(SDL2_DEP)

$(SIMDE_LOCAL_HEADER): | $(DEPS_DIR)
	cd $(DEPS_DIR) && apt-get download libsimde-dev
	dpkg-deb -x $(DEPS_DIR)/libsimde-dev_*.deb $(DEPS_DIR)

$(SDL2_LOCAL_HEADER): | $(DEPS_DIR)
	cd $(DEPS_DIR) && apt-get download libsdl2-dev
	dpkg-deb -x $(DEPS_DIR)/libsdl2-dev_*.deb $(DEPS_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(DEPS_DIR): | $(BUILD_DIR)
	mkdir -p $(DEPS_DIR)

$(BUILD_DIR)/music-analyzer-obs.so: $(PLUGIN_OBJS)
	$(CXX) -shared -o $@ $^ $(OBS_LIBS) -pthread

$(BUILD_DIR)/plugin.o: src/plugin.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(SIMDE_DEP) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(BUILD_DIR)/analyzer.o: src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/visualizer_renderer.o: src/visualizer_renderer.cpp src/visualizer_renderer.hpp src/analyzer.hpp src/fret_control.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/fret_control.o: src/fret_control.cpp src/fret_control.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/fret_control_tests.o: tests/fret_control.cpp src/fret_control.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/fret_control_tests: $(BUILD_DIR)/fret_control.o $(BUILD_DIR)/fret_control_tests.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ && mv "$$tmp" "$@"

$(BUILD_DIR)/visualizer_renderer_tests.o: tests/visualizer_renderer.cpp src/visualizer_renderer.cpp src/visualizer_renderer.hpp src/analyzer.hpp src/fret_control.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/visualizer_renderer_tests: $(BUILD_DIR)/visualizer_renderer_tests.o $(BUILD_DIR)/analyzer_test.o $(BUILD_DIR)/fret_control.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm && mv "$$tmp" "$@"

$(BUILD_DIR)/standalone.o: src/standalone.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(APP_ICON_HEADER) $(SDL2_DEP) FORCE | $(BUILD_DIR)
	+$(MAKE) check-standalone-deps
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) $(SDL2_CFLAGS) -DMAO_STANDALONE_WITH_SDL=1 -DMAO_STANDALONE_VERSION=\"$(STANDALONE_VERSION)\" -Isrc -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/standalone_bass_guitar.o: src/standalone.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(BASS_GUITAR_APP_ICON_HEADER) $(SDL2_DEP) FORCE | $(BUILD_DIR)
	+$(MAKE) check-standalone-deps
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) $(SDL2_CFLAGS) -DMAO_STANDALONE_WITH_SDL=1 -DMAO_STANDALONE_BASS_GUITAR=1 -DMAO_STANDALONE_VERSION=\"$(STANDALONE_VERSION)\" -Isrc -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(STANDALONE_BIN): $(ANALYZER_TEST_OBJ) $(RENDERER_OBJ) $(BUILD_DIR)/standalone.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ $(SDL2_LIBS) -lm -pthread && mv "$$tmp" "$@"

$(BASS_GUITAR_STANDALONE_BIN): $(ANALYZER_TEST_OBJ) $(RENDERER_OBJ) $(BUILD_DIR)/standalone_bass_guitar.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ $(SDL2_LIBS) -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_test.o: src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_smoke.o: tests/analyzer_smoke.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_internal.o: tests/analyzer_internal.cpp src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_cases.o: tests/analyzer_cases.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_midi_ranges.o: tests/analyzer_midi_ranges.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_urmp.o: tests/analyzer_urmp.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_musicnet.o: tests/analyzer_musicnet.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_multtipop.o: tests/analyzer_multtipop.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_guitarset.o: tests/analyzer_guitarset.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_maestro.o: tests/analyzer_maestro.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_egmd.o: tests/analyzer_egmd.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_drum_samples.o: tests/analyzer_drum_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_instrument_samples.o: tests/analyzer_instrument_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_real_note_samples.o: tests/analyzer_real_note_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_instrument_family_samples.o: tests/analyzer_instrument_family_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_smoke: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_smoke.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_internal: $(BUILD_DIR)/analyzer_internal.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_cases: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_cases.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_midi_ranges: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_midi_ranges.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_urmp: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_urmp.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_musicnet: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_musicnet.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_multtipop: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_multtipop.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_guitarset: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_guitarset.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_maestro: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_maestro.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_egmd: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_egmd.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_drum_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_drum_samples.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_instrument_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_instrument_samples.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_real_note_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_real_note_samples.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_instrument_family_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_instrument_family_samples.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ -lm -pthread && mv "$$tmp" "$@"

STANDALONE_TEST_TARGETS := test-standalone-isolation test-standalone-version-complete test-standalone-version-bass-guitar test-standalone-self-test-complete test-standalone-self-test-bass-guitar
.PHONY: $(STANDALONE_TEST_TARGETS)

test-standalone: android-check scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_standalone_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(STANDALONE_TEST_TARGETS)

test-standalone-isolation: tests/check_standalone_isolation.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) check_standalone_isolation $(PYTHON) tests/check_standalone_isolation.py

test-standalone-version-complete: $(STANDALONE_BIN) tests/check_standalone_version.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) check_standalone_version_complete $(PYTHON) tests/check_standalone_version.py $(STANDALONE_BIN)

test-standalone-version-bass-guitar: $(BASS_GUITAR_STANDALONE_BIN) tests/check_standalone_version.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) check_standalone_version_bass_guitar $(PYTHON) tests/check_standalone_version.py $(BASS_GUITAR_STANDALONE_BIN)

test-standalone-self-test-complete: $(STANDALONE_BIN) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) standalone_self_test env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(STANDALONE_BIN) --self-test

test-standalone-self-test-bass-guitar: $(BASS_GUITAR_STANDALONE_BIN) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) standalone_bass_guitar_self_test env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(BASS_GUITAR_STANDALONE_BIN) --self-test

profile-standalone: standalone scripts/profile_standalone.sh
	BUILD_DIR="$(BUILD_DIR)" $(SHELL) scripts/profile_standalone.sh

prepare-drum-samples: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_LIMIT)" DRUM_SAMPLE_SELECTION="$(DRUM_SAMPLE_SELECTION)" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_LIMIT)" --selection "$(DRUM_SAMPLE_SELECTION)" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --unrar "$(UNRAR)"

$(DRUM_SAMPLE_BUILD_DIR)/manifest.tsv: FORCE scripts/prepare_drum_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-drum-samples

.PHONY: inspect-drum-sample-coverage inspect-drum-sample-skip-patterns
inspect-drum-sample-coverage: scripts/prepare_drum_samples.py
	+@if [ ! -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then printf '%s\n' "drum sample coverage: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; exit 0; fi
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_FULL_LIMIT)" DRUM_SAMPLE_SELECTION="spread" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_FULL_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_FULL_LIMIT)" --selection "spread" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --unrar "$(UNRAR)" --audit

inspect-drum-sample-skip-patterns: scripts/inspect_drum_sample_skip_patterns.py scripts/prepare_drum_samples.py
	+@if [ ! -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then printf '%s\n' "inspect_drum_sample_skip_patterns: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; exit 0; fi
	$(PYTHON) scripts/inspect_drum_sample_skip_patterns.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --unrar "$(UNRAR)" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)"

test-drum-samples: test-drum-samples-parallel

test-drum-samples-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples

test-drum-samples-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_SAMPLE_LOCK_DIR)" -- "$(MAKE)" test-drum-samples-parallel-unlocked

test-drum-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(DRUM_SAMPLE_TEST_MAKE_JOBS) $(DRUM_SAMPLE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_drum_sample_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-precision-percent "$(DRUM_SAMPLE_MIN_PRECISION_PERCENT)" --kick-min-recall-percent "$(DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT)" --snare-min-recall-percent "$(DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT)" --hihat-min-recall-percent "$(DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT)" --crash-min-recall-percent "$(DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT)" --tom-min-recall-percent "$(DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT)" --ride-min-recall-percent "$(DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT)" --rim-min-recall-percent "$(DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT)" --kick-max-false-percent "$(DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT)" --tom-max-false-percent "$(DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT)" --rim-max-false-percent "$(DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT)" $(DRUM_SAMPLE_SHARD_OUTS)

test-drum-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_BUILD_DIR)/manifest.tsv scripts/run_with_duration.sh
	@category="$*"; $(RUN_WITH_DURATION) analyzer_drum_samples_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_samples_test_shard_$*.out" 2> "$(BUILD_DIR)/drum_samples_test_shard_$*.err"

prepare-drum-samples-spread: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_SPREAD_LIMIT)" DRUM_SAMPLE_SELECTION="spread" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_SPREAD_LIMIT)" --selection "spread" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --no-archives

$(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv: FORCE scripts/prepare_drum_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-drum-samples-spread

test-drum-samples-spread: test-drum-samples-spread-parallel

test-drum-samples-spread-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-spread scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_spread env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples

test-drum-samples-spread-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_spread_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_SAMPLE_SPREAD_LOCK_DIR)" -- "$(MAKE)" test-drum-samples-spread-parallel-unlocked

test-drum-samples-spread-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(DRUM_SAMPLE_SPREAD_TEST_MAKE_JOBS) $(DRUM_SAMPLE_SPREAD_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_drum_sample_spread_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT)" --min-precision-percent "$(DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT)" --kick-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT)" --snare-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT)" --hihat-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT)" --crash-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT)" --tom-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT)" --ride-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT)" --rim-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT)" --kick-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT)" --snare-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT)" --hihat-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT)" --crash-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT)" --tom-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT)" --ride-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT)" --rim-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT)" --kick-max-false-percent "$(DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT)" --tom-max-false-percent "$(DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT)" $(DRUM_SAMPLE_SPREAD_TEST_SHARD_OUTS)

test-drum-samples-spread-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/run_with_duration.sh
	@category="$*"; $(RUN_WITH_DURATION) analyzer_drum_samples_spread_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_samples_spread_test_shard_$*.out" 2> "$(BUILD_DIR)/drum_samples_spread_test_shard_$*.err"

analyze-drum-spread-gate-matrix: analyze-drum-spread-gate-matrix-parallel

analyze-drum-spread-gate-matrix-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-spread scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_spread_matrix env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=2000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(DRUM_SPREAD_GATE_OUT)" 2> "$(DRUM_SPREAD_GATE_ERR)"
	$(PYTHON) scripts/summarize_drum_gate_matrix.py "$(DRUM_SPREAD_GATE_OUT)" > "$(DRUM_SPREAD_GATE_SUMMARY)"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(DRUM_SPREAD_GATE_ERR)" > "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"
	@cat "$(DRUM_SPREAD_GATE_SUMMARY)"
	@printf '%s\n' "drum spread exact attribute TSV: $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"

analyze-drum-spread-gate-matrix-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_spread_matrix_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_SPREAD_EXACT_ATTRIBUTE_LOCK_DIR)" -- "$(MAKE)" analyze-drum-spread-gate-matrix-parallel-unlocked

analyze-drum-spread-gate-matrix-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_spread_attribute_rows_parallel $(SHELL) scripts/build_sharded_tsv.sh "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" "$(MAKE)" "$(DRUM_SAMPLE_SPREAD_TEST_MAKE_JOBS)" $(DRUM_SPREAD_EXACT_ATTRIBUTE_PARTS)
	$(RUN_WITH_DURATION) check_drum_sample_spread_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT)" --min-precision-percent "$(DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT)" --kick-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT)" --snare-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT)" --hihat-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT)" --crash-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT)" --tom-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT)" --ride-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT)" --rim-min-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT)" --kick-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_KICK_PRIMARY_PERCENT)" --snare-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_SNARE_PRIMARY_PERCENT)" --hihat-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_PRIMARY_PERCENT)" --crash-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_CRASH_PRIMARY_PERCENT)" --tom-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_TOM_PRIMARY_PERCENT)" --ride-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIDE_PRIMARY_PERCENT)" --rim-min-primary-recall-percent "$(DRUM_SAMPLE_SPREAD_MIN_RIM_PRIMARY_PERCENT)" --kick-max-false-percent "$(DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT)" --tom-max-false-percent "$(DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT)" $(DRUM_SAMPLE_SPREAD_SHARD_OUTS)
	$(PYTHON) scripts/summarize_drum_gate_matrix.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" > "$(DRUM_SPREAD_GATE_SUMMARY)"
	@cat "$(DRUM_SPREAD_GATE_SUMMARY)"
	@printf '%s\n' "drum spread exact attribute TSV: $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"

$(BUILD_DIR)/drum_spread_exact_attribute_rows_%.tsv: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_spread_attribute_rows_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=2000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_samples_spread_shard_$*.out" 2> "$(BUILD_DIR)/drum_spread_exact_attribute_rows_$*.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/drum_spread_exact_attribute_rows_$*.err" > "$@"

analyze-drum-active-false-rows: $(BUILD_DIR)/analyzer_drum_samples scripts/summarize_drum_active_false_rows.py scripts/analyze_drum_primary_debug.py
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then if [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; fi; elif [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "drum active false-row summary: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR) and $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; exit 0; fi
	$(PYTHON) scripts/summarize_drum_active_false_rows.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" $(DRUM_ACTIVE_FALSE_ARGS)

analyze-drum-rule-flags: $(BUILD_DIR)/analyzer_drum_samples scripts/summarize_drum_rule_flags.py scripts/analyze_drum_primary_debug.py
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then if [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; fi; elif [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "drum rule flag summary: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR) and $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; exit 0; fi
	$(PYTHON) scripts/summarize_drum_rule_flags.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" $(DRUM_RULE_FLAG_ARGS)

compare-drum-gate-matrix: scripts/compare_drum_gate_summaries.py
	@if [ -z "$(DRUM_GATE_BEFORE)" ] || [ -z "$(DRUM_GATE_AFTER)" ]; then printf '%s\n' "compare-drum-gate-matrix: set DRUM_GATE_BEFORE=/path/before and DRUM_GATE_AFTER=/path/after"; exit 2; fi
	$(PYTHON) scripts/compare_drum_gate_summaries.py "$(DRUM_GATE_BEFORE)" "$(DRUM_GATE_AFTER)"

compare-drum-primary-scores: scripts/compare_drum_primary_scores.py
	@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix; fi
	$(PYTHON) scripts/compare_drum_primary_scores.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"
	@if [ -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(PYTHON) scripts/compare_drum_primary_scores.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; fi

find-drum-active-false-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_active_false_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then if [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; fi; elif [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "drum active false pattern candidates: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR) and $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; exit 0; fi
	+@missing=0; for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS); do if [ ! -f "$$path" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$$path" ]; then missing=1; fi; done; if [ "$$missing" = "1" ]; then $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) analyze-hf-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows; fi
	+@if [ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] && { [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; }; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	+@if [ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ] && { [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ]; }; then $(MAKE) analyze-drum-full-merged-expected-attribute-rows; fi
	@set --; for rows in $(DRUM_ACTIVE_EXTRA_PROTECTED_ROWS); do if [ -f "$$rows" ]; then set -- "$$@" --extra-protected-rows "$$rows"; fi; done; $(PYTHON) scripts/find_drum_active_false_patterns.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" "$$@" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS))

find-drum-active-false-patterns-full: DRUM_ACTIVE_EXTRA_PROTECTED_ROWS := $(MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS)
find-drum-active-false-patterns-full: find-drum-active-false-patterns

$(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP): $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) $(BUILD_DIR)/analyzer_drum_samples scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@missing=0; for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS); do if [ ! -f "$$path" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$$path" ]; then missing=1; fi; done; if [ "$$missing" = "1" ]; then $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) analyze-hf-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows; fi
	+@if [ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] && { [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; }; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	+@if [ "$(DRUM_ACTIVE_REFRESH_FULL_ROWS)" = "1" ] && [ -f "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ] && { [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" ]; }; then $(MAKE) analyze-drum-full-merged-expected-attribute-rows; fi
	@touch "$@"

analyze-drum-active-thresholds: $(BUILD_DIR)/analyzer_drum_samples scripts/simulate_drum_active_thresholds.py scripts/analyze_drum_primary_debug.py
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then if [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; fi; elif [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "drum active threshold simulation: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR) and $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; exit 0; fi
	$(PYTHON) scripts/simulate_drum_active_thresholds.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" $(DRUM_ACTIVE_SIM_ARGS)

$(BUILD_DIR)/kick_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_kick_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=kick MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=kick MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/kick_primary_debug.out" 2> "$@"

$(BUILD_DIR)/tom_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_tom_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=tom MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=tom MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/tom_primary_debug.out" 2> "$@"

$(BUILD_DIR)/snare_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_snare_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=snare MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=snare MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/snare_primary_debug.out" 2> "$@"

$(BUILD_DIR)/hihat_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_hihat_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=hihat MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=hihat MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/hihat_primary_debug.out" 2> "$@"

$(BUILD_DIR)/crash_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_crash_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=crash MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=crash MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/crash_primary_debug.out" 2> "$@"

$(BUILD_DIR)/ride_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_ride_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=ride MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=ride MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/ride_primary_debug.out" 2> "$@"

$(BUILD_DIR)/rim_primary_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | $(DRUM_SAMPLE_SPREAD_BUILD_DIR)/manifest.tsv
	$(RUN_WITH_DURATION) analyzer_drum_samples_primary_rim_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/rim_primary_debug.out" 2> "$@"

analyze-drum-primary-misses: $(PRIMARY_DRUM_DEBUG_ERRS) scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/analyze_drum_primary_debug.py "$(BUILD_DIR)/kick_primary_debug.err" "$(BUILD_DIR)/tom_primary_debug.err" "$(BUILD_DIR)/snare_primary_debug.err" "$(BUILD_DIR)/hihat_primary_debug.err" "$(BUILD_DIR)/crash_primary_debug.err" "$(BUILD_DIR)/ride_primary_debug.err" "$(BUILD_DIR)/rim_primary_debug.err"

$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv: $(PRIMARY_DRUM_DEBUG_ERRS) scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/kick_primary_debug.err" "$(BUILD_DIR)/tom_primary_debug.err" "$(BUILD_DIR)/snare_primary_debug.err" "$(BUILD_DIR)/hihat_primary_debug.err" "$(BUILD_DIR)/crash_primary_debug.err" "$(BUILD_DIR)/ride_primary_debug.err" "$(BUILD_DIR)/rim_primary_debug.err" > "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"

analyze-drum-primary-attribute-rows: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv
	@printf '%s\n' "drum primary attribute TSV: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"

$(BUILD_DIR)/full_kick_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | prepare-drum-samples-full
	$(RUN_WITH_DURATION) analyzer_drum_samples_full_kick_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=kick MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=kick MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=6000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_kick_debug.out" 2> "$@"

$(BUILD_DIR)/full_snare_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | prepare-drum-samples-full
	$(RUN_WITH_DURATION) analyzer_drum_samples_full_snare_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=snare MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=snare MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=5200 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_snare_debug.out" 2> "$@"

$(BUILD_DIR)/full_tom_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | prepare-drum-samples-full
	$(RUN_WITH_DURATION) analyzer_drum_samples_full_tom_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=tom MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=tom MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=2500 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_tom_debug.out" 2> "$@"

$(BUILD_DIR)/full_rim_debug.err: $(BUILD_DIR)/analyzer_drum_samples scripts/run_with_duration.sh | prepare-drum-samples-full
	$(RUN_WITH_DURATION) analyzer_drum_samples_full_rim_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=900 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_rim_debug.out" 2> "$@"

analyze-drum-rule-grid: $(FULL_DRUM_DEBUG_ERRS) scripts/analyze_drum_debug_rows.py scripts/evaluate_drum_rule_grid.py
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected tom --focus tom --against snare --examples 8 "$(BUILD_DIR)/full_tom_debug.err"
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected snare --focus tom --against snare --examples 8 "$(BUILD_DIR)/full_snare_debug.err"
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected kick --focus tom --against kick --examples 8 "$(BUILD_DIR)/full_kick_debug.err"
	$(PYTHON) scripts/evaluate_drum_rule_grid.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" --top 80

analyze-drum-tom-bleed-caps: $(FULL_DRUM_DEBUG_ERRS) scripts/evaluate_drum_tom_bleed_caps.py
	$(PYTHON) scripts/evaluate_drum_tom_bleed_caps.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" $(DRUM_TOM_BLEED_ARGS)

analyze-drum-tom-bleed-caps-cached: scripts/evaluate_drum_tom_bleed_caps.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix-parallel; else printf '%s\n' "using cached drum full exact attribute TSV: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"; fi
	$(PYTHON) scripts/evaluate_drum_tom_bleed_caps.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(DRUM_TOM_BLEED_ARGS)

$(BUILD_DIR)/drum_full_attribute_rows.tsv: $(FULL_DRUM_DEBUG_ERRS) scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" "$(BUILD_DIR)/full_rim_debug.err" > "$(BUILD_DIR)/drum_full_attribute_rows.tsv"

analyze-drum-full-attribute-rows: $(BUILD_DIR)/drum_full_attribute_rows.tsv
	@printf '%s\n' "full drum attribute TSV: $(BUILD_DIR)/drum_full_attribute_rows.tsv"

find-drum-attribute-patterns: $(FULL_DRUM_DEBUG_ERRS) scripts/find_drum_attribute_patterns.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" "$(BUILD_DIR)/full_rim_debug.err" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

find-drum-primary-attribute-patterns: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

find-drum-full-attribute-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_DRUM_FULL_PATTERN_ARGS))

find-drum-spread-exact-attribute-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then if [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; fi; elif [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "drum spread exact pattern candidates: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR) and $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; exit 0; fi
	@if [ -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then $(PYTHON) scripts/find_drum_attribute_patterns.py "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS); fi

prepare-drum-samples-full: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_FULL_LIMIT)" DRUM_SAMPLE_SELECTION="$(DRUM_SAMPLE_SELECTION)" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_FULL_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_FULL_LIMIT)" --selection "$(DRUM_SAMPLE_SELECTION)" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --unrar "$(UNRAR)"

$(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv: FORCE scripts/prepare_drum_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-drum-samples-full

test-drum-samples-full: test-drum-samples-full-parallel

test-drum-samples-full-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-full scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_full env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

test-drum-samples-full-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh scripts/run_with_lock.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_full_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_SAMPLE_FULL_LOCK_DIR)" -- "$(MAKE)" test-drum-samples-full-parallel-unlocked

test-drum-samples-full-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS) $(DRUM_SAMPLE_FULL_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_drum_sample_full_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT)" --min-precision-percent "$(DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT)" --kick-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_KICK_RECALL_PERCENT)" --snare-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_SNARE_RECALL_PERCENT)" --hihat-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_HIHAT_RECALL_PERCENT)" --crash-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_CRASH_RECALL_PERCENT)" --tom-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_TOM_RECALL_PERCENT)" --ride-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_RIDE_RECALL_PERCENT)" --rim-min-recall-percent "$(DRUM_SAMPLE_FULL_MIN_RIM_RECALL_PERCENT)" --kick-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT)" --snare-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT)" --hihat-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT)" --crash-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT)" --tom-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT)" --ride-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT)" --rim-min-primary-recall-percent "$(DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT)" --tom-max-false-percent "$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)" $(DRUM_SAMPLE_FULL_SHARD_OUTS)

test-drum-samples-full-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/run_with_duration.sh
	@stem="$*"; category="$${stem%-*}"; shard="$${stem##*-}"; $(RUN_WITH_DURATION) analyzer_drum_samples_full_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT="$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX="$$shard" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_samples_full_shard_$*.out" 2> "$(BUILD_DIR)/drum_samples_full_shard_$*.err"

analyze-drum-full-gate-matrix: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-full scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_full_matrix env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=20000 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples > "$(DRUM_FULL_GATE_OUT)" 2> "$(DRUM_FULL_GATE_ERR)"
	$(PYTHON) scripts/summarize_drum_gate_matrix.py "$(DRUM_FULL_GATE_OUT)" > "$(DRUM_FULL_GATE_SUMMARY)"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(DRUM_FULL_GATE_ERR)" > "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"
	@cat "$(DRUM_FULL_GATE_SUMMARY)"
	@printf '%s\n' "drum full exact attribute TSV: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"

analyze-drum-full-gate-matrix-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_full_attribute_rows_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_FULL_EXACT_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" "$(MAKE)" "$(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS)" $(DRUM_FULL_EXACT_ATTRIBUTE_PARTS)
	$(PYTHON) scripts/summarize_drum_gate_matrix.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" > "$(DRUM_FULL_GATE_SUMMARY)"
	@cat "$(DRUM_FULL_GATE_SUMMARY)"
	@printf '%s\n' "drum full exact attribute TSV: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"

$(BUILD_DIR)/drum_full_exact_attribute_rows_%.tsv: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	@stem="$*"; category="$${stem%-*}"; shard="$${stem##*-}"; $(RUN_WITH_DURATION) analyzer_drum_samples_full_attribute_rows_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT="$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX="$$shard" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=20000 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_full_exact_attribute_rows_$*.out" 2> "$(BUILD_DIR)/drum_full_exact_attribute_rows_$*.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/drum_full_exact_attribute_rows_$*.err" > "$@"

analyze-drum-full-merged-expected-attribute-rows: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_drum_samples_full_merged_expected_rows_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)" "$(MAKE)" "$(DRUM_SAMPLE_FULL_TEST_MAKE_JOBS)" $(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_PARTS)
	@printf '%s\n' "drum full merged expected attribute TSV: $(DRUM_FULL_MERGED_EXPECTED_ATTRIBUTE_ROWS)"

$(BUILD_DIR)/drum_full_merged_expected_attribute_rows_%.tsv: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_SAMPLE_FULL_BUILD_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	@stem="$*"; category="$${stem%-*}"; shard="$${stem##*-}"; $(RUN_WITH_DURATION) analyzer_drum_samples_full_merged_expected_rows_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_COUNT="$(DRUM_SAMPLE_FULL_SHARDS_PER_CATEGORY)" MUSIC_ANALYZER_DRUM_SAMPLE_SHARD_INDEX="$$shard" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=20000 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_MERGED_EXPECTED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_full_merged_expected_attribute_rows_$*.out" 2> "$(BUILD_DIR)/drum_full_merged_expected_attribute_rows_$*.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows --include-merged-debug-rows "$(BUILD_DIR)/drum_full_merged_expected_attribute_rows_$*.err" > "$@"

find-drum-full-exact-attribute-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_DRUM_FULL_PATTERN_ARGS))

find-drum-full-exact-attribute-patterns-cached: scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix-parallel; else printf '%s\n' "using cached drum full exact attribute TSV: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)"; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_DRUM_FULL_PATTERN_ARGS))

find-protected-drum-full-exact-attribute-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	+@missing=0; for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS); do if [ ! -f "$$path" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$$path" ]; then missing=1; fi; done; if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ] && { [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; }; then missing=1; fi; if [ "$$missing" = "1" ]; then $(MAKE) analyze-protected-drum-primary-attribute-rows; fi
	@set --; for path in $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS); do if [ -f "$$path" ]; then set -- "$$@" "$$path"; fi; done; $(PYTHON) scripts/find_drum_attribute_patterns.py "$$@" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_DRUM_FULL_PATTERN_ARGS))

prepare-drum-machine-samples: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_MACHINE_SAMPLE_LIMIT)" DRUM_SAMPLE_SELECTION="spread" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_MACHINE_SAMPLE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" --limit-per-category "$(DRUM_MACHINE_SAMPLE_LIMIT)" --selection "spread" --source-filter "$(DRUM_MACHINE_SAMPLE_FILTER)" --unrar "$(UNRAR)"

$(DRUM_MACHINE_SAMPLE_BUILD_DIR)/manifest.tsv: FORCE scripts/prepare_drum_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-drum-machine-samples

test-drum-machine-samples: test-drum-machine-samples-parallel

test-drum-machine-samples-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-machine-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_machine_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_MACHINE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_MACHINE_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_MACHINE_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_MACHINE_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_MACHINE_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_MACHINE_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_MACHINE_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_MACHINE_MAX_TOM_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

test-drum-machine-samples-parallel: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_MACHINE_SAMPLE_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh scripts/run_with_lock.sh
	+$(RUN_WITH_DURATION) analyzer_drum_machine_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(DRUM_MACHINE_SAMPLE_LOCK_DIR)" -- "$(MAKE)" test-drum-machine-samples-parallel-unlocked

test-drum-machine-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(DRUM_MACHINE_SAMPLE_BUILD_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(DRUM_MACHINE_TEST_MAKE_JOBS) $(DRUM_MACHINE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_drum_machine_sample_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-recall-percent "$(DRUM_MACHINE_MIN_RECALL_PERCENT)" --min-precision-percent "$(DRUM_MACHINE_MIN_PRECISION_PERCENT)" --kick-min-recall-percent "$(DRUM_MACHINE_MIN_KICK_RECALL_PERCENT)" --snare-min-recall-percent "$(DRUM_MACHINE_MIN_SNARE_RECALL_PERCENT)" --hihat-min-recall-percent "$(DRUM_MACHINE_MIN_HIHAT_RECALL_PERCENT)" --crash-min-recall-percent "$(DRUM_MACHINE_MIN_CRASH_RECALL_PERCENT)" --tom-min-recall-percent "$(DRUM_MACHINE_MIN_TOM_RECALL_PERCENT)" --ride-min-recall-percent "$(DRUM_MACHINE_MIN_RIDE_RECALL_PERCENT)" --rim-min-recall-percent "$(DRUM_MACHINE_MIN_RIM_RECALL_PERCENT)" --kick-max-false-percent "$(DRUM_MACHINE_MAX_KICK_FALSE_PERCENT)" --tom-max-false-percent "$(DRUM_MACHINE_MAX_TOM_FALSE_PERCENT)" $(DRUM_MACHINE_SHARD_OUTS)

test-drum-machine-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(DRUM_MACHINE_SAMPLE_BUILD_DIR)/manifest.tsv scripts/run_with_duration.sh
	@category="$*"; $(RUN_WITH_DURATION) analyzer_drum_machine_samples_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$$category" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$$category" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/drum_machine_samples_shard_$*.out" 2> "$(BUILD_DIR)/drum_machine_samples_shard_$*.err"

prepare-hf-drum-kit-samples: scripts/prepare_hf_drum_kit_samples.py scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(HF_DRUM_KIT_PREP_LOCK_DIR)" -- env HF_DRUM_KIT_SAMPLE_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" HF_DRUM_KIT_LIMIT_PER_CATEGORY="$(HF_DRUM_KIT_LIMIT_PER_CATEGORY)" $(PYTHON) scripts/prepare_hf_drum_kit_samples.py --output "$(HF_DRUM_KIT_SAMPLE_DIR)"

$(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv: scripts/prepare_hf_drum_kit_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-hf-drum-kit-samples

test-hf-drum-kit-samples: test-hf-drum-kit-samples-parallel

test-hf-drum-kit-samples-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-hf-drum-kit-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(HF_DRUM_KIT_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

test-hf-drum-kit-samples-parallel: $(BUILD_DIR)/analyzer_drum_samples $(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples_locked $(SHELL) scripts/run_with_lock.sh "$(HF_DRUM_KIT_SHARD_LOCK_DIR)" -- "$(MAKE)" test-hf-drum-kit-samples-parallel-unlocked

test-hf-drum-kit-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples_parallel $(MAKE) $(HF_DRUM_KIT_TEST_MAKE_JOBS) $(HF_DRUM_KIT_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_hf_drum_kit_shards $(PYTHON) scripts/check_drum_sample_shards.py --min-recall-percent "$(HF_DRUM_KIT_MIN_RECALL_PERCENT)" --min-precision-percent "$(HF_DRUM_KIT_MIN_PRECISION_PERCENT)" --kick-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_KICK_PRIMARY_PERCENT)" --snare-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_SNARE_PRIMARY_PERCENT)" --hihat-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_HIHAT_PRIMARY_PERCENT)" --crash-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_CRASH_PRIMARY_PERCENT)" --tom-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_TOM_PRIMARY_PERCENT)" --ride-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_RIDE_PRIMARY_PERCENT)" --rim-min-primary-recall-percent "$(HF_DRUM_KIT_MIN_RIM_PRIMARY_PERCENT)" --kick-max-false-percent "$(HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT)" $(HF_DRUM_KIT_SHARD_OUTS)

test-hf-drum-kit-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/hf_drum_kit_samples_shard_$*.out" 2> "$(BUILD_DIR)/hf_drum_kit_samples_shard_$*.err"

analyze-hf-drum-primary-attribute-rows: analyze-hf-drum-primary-attribute-rows-parallel

analyze-hf-drum-primary-attribute-rows-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-hf-drum-kit-samples scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_hf_drum_kit_primary_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=5000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(HF_DRUM_KIT_PRIMARY_DEBUG_OUT)" 2> "$(HF_DRUM_KIT_PRIMARY_DEBUG_ERR)"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(HF_DRUM_KIT_PRIMARY_DEBUG_ERR)" > "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)"
	@printf '%s\n' "HF drum-kit primary attribute TSV: $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)"

analyze-hf-drum-primary-attribute-rows-parallel: $(BUILD_DIR)/analyzer_drum_samples $(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_hf_drum_kit_primary_debug_parallel $(SHELL) scripts/run_with_lock.sh "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" "$(MAKE)" "$(HF_DRUM_KIT_TEST_MAKE_JOBS)" $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_PARTS)
	@printf '%s\n' "HF drum-kit primary attribute TSV: $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)"

$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_%.tsv: FORCE $(BUILD_DIR)/analyzer_drum_samples $(HF_DRUM_KIT_SAMPLE_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_hf_drum_kit_primary_debug_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=5000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_$*.out" 2> "$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_$*.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/hf_drum_kit_primary_attribute_rows_$*.err" > "$@"

find-hf-drum-primary-attribute-patterns: scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-hf-drum-primary-attribute-rows; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

download-idmt-drums-samples: $(IDMT_DRUMS_ARCHIVE)

$(IDMT_DRUMS_ARCHIVE): FORCE scripts/download_idmt_drums_archive.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(IDMT_DRUMS_ARCHIVE_LOCK_DIR)" -- $(SHELL) scripts/download_idmt_drums_archive.sh "$(IDMT_DRUMS_ARCHIVE)" "$(IDMT_DRUMS_URL)" "$(IDMT_DRUMS_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)" "$(PYTHON)"

prepare-idmt-drums-samples: scripts/prepare_idmt_drums_samples.py download-idmt-drums-samples scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(IDMT_DRUMS_PREP_LOCK_DIR)" -- env IDMT_DRUMS_ARCHIVE="$(IDMT_DRUMS_ARCHIVE)" IDMT_DRUMS_SAMPLE_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" IDMT_DRUMS_LIMIT_PER_CATEGORY="$(IDMT_DRUMS_LIMIT_PER_CATEGORY)" IDMT_DRUMS_MIN_PER_CATEGORY="$(IDMT_DRUMS_MIN_PER_CATEGORY)" $(PYTHON) scripts/prepare_idmt_drums_samples.py --archive "$(IDMT_DRUMS_ARCHIVE)" --output "$(IDMT_DRUMS_SAMPLE_DIR)" --limit-per-category "$(IDMT_DRUMS_LIMIT_PER_CATEGORY)" --min-per-category "$(IDMT_DRUMS_MIN_PER_CATEGORY)"

$(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv: scripts/prepare_idmt_drums_samples.py download-idmt-drums-samples | $(BUILD_DIR)
	+$(MAKE) prepare-idmt-drums-samples

test-idmt-drums-samples: test-idmt-drums-samples-parallel

test-idmt-drums-samples-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-idmt-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_drums_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="kick,snare,hihat" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(IDMT_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(IDMT_DRUMS_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(IDMT_DRUMS_MIN_SNARE_PRIMARY_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(IDMT_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(IDMT_DRUMS_MAX_KICK_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

test-idmt-drums-samples-parallel: $(BUILD_DIR)/analyzer_drum_samples $(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_idmt_drums_samples_locked $(SHELL) scripts/run_with_lock.sh "$(IDMT_DRUMS_SHARD_LOCK_DIR)" -- "$(MAKE)" test-idmt-drums-samples-parallel-unlocked

test-idmt-drums-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_drum_samples $(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv scripts/check_drum_sample_shards.py scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_idmt_drums_samples_parallel $(MAKE) $(IDMT_DRUMS_TEST_MAKE_JOBS) $(IDMT_DRUMS_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_idmt_drums_shards $(PYTHON) scripts/check_drum_sample_shards.py --categories "kick,snare,hihat" --min-recall-percent "$(IDMT_DRUMS_MIN_RECALL_PERCENT)" --snare-min-recall-percent "$(IDMT_DRUMS_MIN_SNARE_RECALL_PERCENT)" --snare-min-primary-recall-percent "$(IDMT_DRUMS_MIN_SNARE_PRIMARY_RECALL_PERCENT)" --min-precision-percent "$(IDMT_DRUMS_MIN_PRECISION_PERCENT)" --kick-max-false-percent "$(IDMT_DRUMS_MAX_KICK_FALSE_PERCENT)" $(IDMT_DRUMS_SHARD_OUTS)

test-idmt-drums-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_drum_samples $(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_drums_samples_shard_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/idmt_drums_samples_shard_$*.out" 2> "$(BUILD_DIR)/idmt_drums_samples_shard_$*.err"

analyze-idmt-drum-primary-attribute-rows: analyze-idmt-drum-primary-attribute-rows-parallel

analyze-idmt-drum-primary-attribute-rows-serial: $(BUILD_DIR)/analyzer_drum_samples prepare-idmt-drums-samples scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_drums_primary_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="kick,snare,hihat" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=4000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(IDMT_DRUMS_PRIMARY_DEBUG_OUT)" 2> "$(IDMT_DRUMS_PRIMARY_DEBUG_ERR)"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(IDMT_DRUMS_PRIMARY_DEBUG_ERR)" > "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"
	@printf '%s\n' "IDMT drum primary attribute TSV: $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

analyze-idmt-drum-primary-attribute-rows-parallel: $(BUILD_DIR)/analyzer_drum_samples $(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_idmt_drums_primary_debug_parallel $(SHELL) scripts/run_with_lock.sh "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" "$(MAKE)" "$(IDMT_DRUMS_TEST_MAKE_JOBS)" $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_PARTS)
	@printf '%s\n' "IDMT drum primary attribute TSV: $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

$(BUILD_DIR)/idmt_drums_primary_attribute_rows_%.tsv: FORCE $(BUILD_DIR)/analyzer_drum_samples $(IDMT_DRUMS_SAMPLE_DIR)/manifest.tsv scripts/analyze_drum_primary_debug.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_drums_primary_debug_$* env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="$*" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="$*" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=4000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/idmt_drums_primary_attribute_rows_$*.out" 2> "$(BUILD_DIR)/idmt_drums_primary_attribute_rows_$*.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(BUILD_DIR)/idmt_drums_primary_attribute_rows_$*.err" > "$@"

find-idmt-drum-primary-attribute-patterns: scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@if [ ! -f "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" ]; then $(MAKE) analyze-idmt-drum-primary-attribute-rows; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

analyze-protected-drum-primary-attribute-rows:
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) analyze-drum-spread-gate-matrix analyze-hf-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows; else printf '%s\n' "analyze-drum-spread-gate-matrix: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) analyze-hf-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows; fi
	@printf '%s\n' "protected drum primary attribute TSVs:"
	@printf '%s\n' "  $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

find-protected-drum-primary-attribute-patterns: $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py
	+@missing=0; for path in $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS); do if [ ! -f "$$path" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$$path" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$$path" ]; then missing=1; fi; done; if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ] && { [ ! -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; }; then missing=1; fi; if [ "$$missing" = "1" ]; then $(MAKE) analyze-protected-drum-primary-attribute-rows; fi
	+@if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ] && { [ ! -f "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "$(BUILD_DIR)/analyzer_drum_samples" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ] || [ "scripts/analyze_drum_primary_debug.py" -nt "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" ]; }; then $(MAKE) analyze-drum-full-gate-matrix-parallel; fi
	@set --; for path in $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS); do if [ -f "$$path" ]; then set -- "$$@" "$$path"; fi; done; if [ "$$#" -eq 0 ]; then printf '%s\n' "protected drum primary pattern candidates: skipped; no attribute rows"; else $(PYTHON) scripts/find_drum_attribute_patterns.py "$$@" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS)); fi

prepare-mdb-drums-samples: scripts/prepare_mdb_drums_samples.py | $(BUILD_DIR)
	MDB_DRUMS_SAMPLE_DIR="$(MDB_DRUMS_SAMPLE_DIR)" MDB_DRUMS_SOURCE_ROOT="$(MDB_DRUMS_SOURCE_ROOT)" MDB_DRUMS_RECORDING_LIMIT="$(MDB_DRUMS_RECORDING_LIMIT)" MDB_DRUMS_MIN_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_mdb_drums_samples.py --output "$(MDB_DRUMS_SAMPLE_DIR)" --source-root "$(MDB_DRUMS_SOURCE_ROOT)" --limit "$(MDB_DRUMS_RECORDING_LIMIT)" --min-recordings "$(MDB_DRUMS_MIN_RECORDINGS)"

test-mdb-drums-samples: test-mdb-drums-samples-parallel

test-mdb-drums-samples-serial: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mdb_drums_samples env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT="$(MDB_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT="$(MDB_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT="$(MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(BUILD_DIR)/analyzer_egmd

test-mdb-drums-samples-parallel: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/check_egmd_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_mdb_drums_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MDB_DRUMS_LOCK_DIR)" -- "$(MAKE)" test-mdb-drums-samples-parallel-unlocked

test-mdb-drums-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/check_egmd_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MDB_DRUMS_TEST_MAKE_JOBS) $(MDB_DRUMS_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_mdb_drums_shards $(PYTHON) scripts/check_egmd_shards.py --min-recordings "$(MDB_DRUMS_MIN_RECORDINGS)" --min-windows "$(MDB_DRUMS_REQUIRED_WINDOWS)" --min-recall-percent "$(MDB_DRUMS_MIN_RECALL_PERCENT)" --min-precision-percent "$(MDB_DRUMS_MIN_PRECISION_PERCENT)" --max-false-positive-windows-percent "$(MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(MDB_DRUMS_SHARD_OUTS)

test-mdb-drums-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_mdb_drums_samples_shard_$* env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_EGMD_MAX_WINDOWS_PER_RECORDING=4 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_SHARD_COUNT="$(MDB_DRUMS_SHARDS)" MUSIC_ANALYZER_EGMD_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_egmd > "$(BUILD_DIR)/mdb_drums_samples_shard_$*.out" 2> "$(BUILD_DIR)/mdb_drums_samples_shard_$*.err"

analyze-mdb-drums-misses: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/analyze_egmd_misses.py
	env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_MISSES=1 MUSIC_ANALYZER_EGMD_VERBOSE_MISS_LIMIT=240 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVES=1 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVE_LIMIT=240 $(BUILD_DIR)/analyzer_egmd > "$(MDB_DRUMS_MISS_LOG).summary" 2> "$(MDB_DRUMS_MISS_LOG)"
	$(PYTHON) scripts/analyze_egmd_misses.py "$(MDB_DRUMS_MISS_LOG)"

.PHONY: analyze-mdb-drum-windows
analyze-mdb-drum-windows: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples
	env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOWS=1 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOW_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(MDB_DRUMS_WINDOW_LOG).summary" 2> "$(MDB_DRUMS_WINDOW_LOG)"
	@printf '%s\n' "MDB drum all-window log: $(MDB_DRUMS_WINDOW_LOG)"

.PHONY: evaluate-mdb-drum-windows
evaluate-mdb-drum-windows: analyze-mdb-drum-windows scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(MDB_DRUMS_WINDOW_LOG)" $(DRUM_RECOVERY_ARGS)

analyze-mdb-drum-attributes: analyze-mdb-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(MDB_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-star-drums-samples: $(STAR_DRUMS_ARCHIVE)

$(STAR_DRUMS_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(STAR_DRUMS_SOURCE_DIR)"
	curl -fL -C - -o "$(STAR_DRUMS_ARCHIVE)" "$(STAR_DRUMS_URL)"
	$(PYTHON) -m zipfile -t "$(STAR_DRUMS_ARCHIVE)" >/dev/null

prepare-star-drums-samples: scripts/prepare_star_drums_samples.py download-star-drums-samples | $(BUILD_DIR)
	STAR_DRUMS_ARCHIVE="$(STAR_DRUMS_ARCHIVE)" STAR_DRUMS_SAMPLE_DIR="$(STAR_DRUMS_SAMPLE_DIR)" STAR_DRUMS_AUDIO_FLAVOR="$(STAR_DRUMS_AUDIO_FLAVOR)" STAR_DRUMS_RECORDING_LIMIT="$(STAR_DRUMS_RECORDING_LIMIT)" STAR_DRUMS_MIN_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_star_drums_samples.py --archive "$(STAR_DRUMS_ARCHIVE)" --output "$(STAR_DRUMS_SAMPLE_DIR)" --audio-flavor "$(STAR_DRUMS_AUDIO_FLAVOR)" --limit "$(STAR_DRUMS_RECORDING_LIMIT)" --min-recordings "$(STAR_DRUMS_MIN_RECORDINGS)" --ffmpeg "$(FFMPEG)"

test-star-drums-samples: test-star-drums-samples-parallel

test-star-drums-samples-serial: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_star_drums_samples env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(STAR_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT="$(STAR_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(STAR_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT="$(STAR_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT="$(STAR_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(BUILD_DIR)/analyzer_egmd

test-star-drums-samples-parallel: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/check_egmd_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_star_drums_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(STAR_DRUMS_LOCK_DIR)" -- "$(MAKE)" test-star-drums-samples-parallel-unlocked

test-star-drums-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/check_egmd_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(STAR_DRUMS_TEST_MAKE_JOBS) $(STAR_DRUMS_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_star_drums_shards $(PYTHON) scripts/check_egmd_shards.py --min-recordings "$(STAR_DRUMS_MIN_RECORDINGS)" --min-windows "$(STAR_DRUMS_REQUIRED_WINDOWS)" --min-recall-percent "$(STAR_DRUMS_MIN_RECALL_PERCENT)" --min-precision-percent "$(STAR_DRUMS_MIN_PRECISION_PERCENT)" --max-false-positive-windows-percent "$(STAR_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(STAR_DRUMS_SHARD_OUTS)

test-star-drums-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_star_drums_samples_shard_$* env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_EGMD_MAX_WINDOWS_PER_RECORDING=4 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(STAR_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_SHARD_COUNT="$(STAR_DRUMS_SHARDS)" MUSIC_ANALYZER_EGMD_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_egmd > "$(BUILD_DIR)/star_drums_samples_shard_$*.out" 2> "$(BUILD_DIR)/star_drums_samples_shard_$*.err"

analyze-star-drums-misses: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/analyze_egmd_misses.py
	env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(STAR_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_MISSES=1 MUSIC_ANALYZER_EGMD_VERBOSE_MISS_LIMIT=120 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVES=1 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVE_LIMIT=120 $(BUILD_DIR)/analyzer_egmd > "$(STAR_DRUMS_MISS_LOG).summary" 2> "$(STAR_DRUMS_MISS_LOG)"
	$(PYTHON) scripts/analyze_egmd_misses.py "$(STAR_DRUMS_MISS_LOG)"

analyze-star-drum-attributes: analyze-star-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(STAR_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-medley-solos-samples: $(MEDLEY_SOLOS_METADATA) $(MEDLEY_SOLOS_ARCHIVE)

$(MEDLEY_SOLOS_METADATA): | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	curl -fL -C - -o "$(MEDLEY_SOLOS_METADATA)" "$(MEDLEY_SOLOS_METADATA_URL)"

$(MEDLEY_SOLOS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && ! $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(MEDLEY_SOLOS_ARCHIVE)" "$(MEDLEY_SOLOS_ARCHIVE).part"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ] && $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ]; then curl -fL -C - -o "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_URL)"; fi
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ]; then $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null; mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	$(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null

prepare-medley-solos-samples: scripts/prepare_medley_solos_samples.py download-medley-solos-samples | $(BUILD_DIR)
	MEDLEY_SOLOS_METADATA="$(MEDLEY_SOLOS_METADATA)" MEDLEY_SOLOS_ARCHIVE="$(MEDLEY_SOLOS_ARCHIVE)" MEDLEY_SOLOS_SAMPLE_DIR="$(MEDLEY_SOLOS_SAMPLE_DIR)" MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT="$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" MEDLEY_SOLOS_MIN_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MEDLEY_SOLOS_MIN_COUNTS="$(MEDLEY_SOLOS_MIN_COUNTS)" $(PYTHON) scripts/prepare_medley_solos_samples.py --metadata "$(MEDLEY_SOLOS_METADATA)" --archive "$(MEDLEY_SOLOS_ARCHIVE)" --output "$(MEDLEY_SOLOS_SAMPLE_DIR)" --limit-per-instrument "$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-counts "$(MEDLEY_SOLOS_MIN_COUNTS)"

test-medley-solos-samples: test-medley-solos-samples-parallel

test-medley-solos-samples-serial: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_medley_solos_samples env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT="$(MEDLEY_SOLOS_MIN_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_instrument_family_samples

test-medley-solos-samples-parallel: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/check_instrument_family_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_medley_solos_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MEDLEY_SOLOS_LOCK_DIR)" -- "$(MAKE)" test-medley-solos-samples-parallel-unlocked

test-medley-solos-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/check_instrument_family_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MEDLEY_SOLOS_TEST_MAKE_JOBS) $(MEDLEY_SOLOS_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_medley_solos_shards $(PYTHON) scripts/check_instrument_family_shards.py --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-recall-percent "$(MEDLEY_SOLOS_MIN_RECALL_PERCENT)" $(MEDLEY_SOLOS_SHARD_OUTS)

test-medley-solos-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_medley_solos_samples_shard_$* env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_COUNT="$(MEDLEY_SOLOS_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_instrument_family_samples > "$(BUILD_DIR)/medley_solos_samples_shard_$*.out" 2> "$(BUILD_DIR)/medley_solos_samples_shard_$*.err"

download-maps-piano-samples: $(MAPS_PIANO_ARCHIVE)

$(MAPS_PIANO_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(MAPS_PIANO_SOURCE_DIR)"
	if [ -s "$(MAPS_PIANO_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(MAPS_PIANO_ARCHIVE)" "$(MAPS_PIANO_ARCHIVE).part"; fi
	if [ ! -s "$(MAPS_PIANO_ARCHIVE)" ] && [ -s "$(MAPS_PIANO_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE).part" >/dev/null 2>&1; then mv "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_ARCHIVE)"; fi
	if [ ! -s "$(MAPS_PIANO_ARCHIVE)" ]; then curl -fL -C - -o "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_URL)"; fi
	if [ -s "$(MAPS_PIANO_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE).part" >/dev/null; mv "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null

prepare-maps-piano-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MAPS_PIANO_KINDS="$(MAPS_PIANO_KINDS)" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_SAMPLE_DIR)" --limit "$(MAPS_PIANO_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --kinds "$(MAPS_PIANO_KINDS)"

test-maps-piano-samples: test-maps-piano-samples-parallel

test-maps-piano-samples-serial: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT="$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT="$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT="$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT="$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(BUILD_DIR)/analyzer_maestro

test-maps-piano-samples-parallel: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_maps_piano_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MAPS_PIANO_LOCK_DIR)" -- "$(MAKE)" test-maps-piano-samples-parallel-unlocked

test-maps-piano-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MAPS_PIANO_TEST_MAKE_JOBS) $(MAPS_PIANO_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_maps_piano_shards $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_REQUIRED_WINDOWS)" --min-recall-percent "$(MAPS_PIANO_MIN_RECALL_PERCENT)" --min-precision-percent "$(MAPS_PIANO_MIN_PRECISION_PERCENT)" --min-keyboard-recall-percent "$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" --max-contamination-percent "$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" --max-false-non-keyboard-percent "$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" --min-chord-recall-percent "$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" --min-chord-checks "$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(MAPS_PIANO_SHARD_OUTS)

test-maps-piano-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_samples_shard_$*.err"

prepare-maps-piano-note-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MAPS_PIANO_KINDS="ISOL" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_NOTE_SAMPLE_DIR)" --limit "$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --kinds "ISOL"

test-maps-piano-note-samples: test-maps-piano-note-samples-parallel

test-maps-piano-note-samples-serial: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_note_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT="$(MAPS_PIANO_NOTE_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT="$(MAPS_PIANO_NOTE_MAX_FALSE_NON_KEYBOARD_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 $(BUILD_DIR)/analyzer_maestro

test-maps-piano-note-samples-parallel: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/check_maestro_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_maps_piano_note_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MAPS_PIANO_NOTE_LOCK_DIR)" -- "$(MAKE)" test-maps-piano-note-samples-parallel-unlocked

test-maps-piano-note-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/check_maestro_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(MAPS_PIANO_NOTE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_maps_piano_note_shards $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" --min-recall-percent "$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" --min-precision-percent "$(MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT)" --min-keyboard-recall-percent "$(MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT)" --max-contamination-percent "$(MAPS_PIANO_NOTE_MAX_CONTAMINATION_PERCENT)" --max-false-non-keyboard-percent "$(MAPS_PIANO_NOTE_MAX_FALSE_NON_KEYBOARD_PERCENT)" --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_NOTE_SHARD_OUTS)

test-maps-piano-note-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_note_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.err"

download-bach10-mf0-synth-samples: $(BACH10_MF0_SYNTH_ARCHIVE)

$(BACH10_MF0_SYNTH_ARCHIVE): scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	mkdir -p "$(BACH10_MF0_SYNTH_SOURCE_DIR)"
	$(SHELL) scripts/download_musicnet_archive.sh "$(BACH10_MF0_SYNTH_ARCHIVE)" "$(BACH10_MF0_SYNTH_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

prepare-bach10-mf0-synth-samples: scripts/prepare_bach10_mf0_synth_musicnet_fixture.py | $(BUILD_DIR)
	+if [ -z "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" ]; then $(MAKE) download-bach10-mf0-synth-samples; fi
	BACH10_MF0_SYNTH_ARCHIVE="$(BACH10_MF0_SYNTH_ARCHIVE)" BACH10_MF0_SYNTH_SOURCE_ROOT="$(BACH10_MF0_SYNTH_SOURCE_ROOT)" BACH10_MF0_SYNTH_SAMPLE_DIR="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" BACH10_MF0_SYNTH_RECORDING_LIMIT="$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" BACH10_MF0_SYNTH_MIN_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_bach10_mf0_synth_musicnet_fixture.py --archive "$(BACH10_MF0_SYNTH_ARCHIVE)" --source-root "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" --output "$(BACH10_MF0_SYNTH_SAMPLE_DIR)" --limit "$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" --min-recordings "$(BACH10_MF0_SYNTH_MIN_RECORDINGS)"

test-bach10-mf0-synth-samples: test-bach10-mf0-synth-samples-parallel

test-bach10-mf0-synth-samples-serial: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_musicnet

test-bach10-mf0-synth-samples-parallel: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/check_musicnet_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(BACH10_MF0_SYNTH_LOCK_DIR)" -- "$(MAKE)" test-bach10-mf0-synth-samples-parallel-unlocked

test-bach10-mf0-synth-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/check_musicnet_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(BACH10_MF0_SYNTH_TEST_MAKE_JOBS) $(BACH10_MF0_SYNTH_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_bach10_mf0_synth_shards $(PYTHON) scripts/check_musicnet_shards.py --min-recordings "$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" --min-windows "$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" --min-recall-percent "$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" --min-precision-percent "$(BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT)" --min-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT)" --min-simple-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT)" --min-global-chord-precision-percent "$(BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT)" --min-global-simple-chord-precision-percent "$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT)" --min-global-simple-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT)" --min-chord-checks 5 $(BACH10_MF0_SYNTH_SHARD_OUTS)

test-bach10-mf0-synth-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples_shard_$* env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_SHARD_COUNT="$(BACH10_MF0_SYNTH_SHARDS)" MUSIC_ANALYZER_MUSICNET_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_musicnet > "$(BUILD_DIR)/bach10_mf0_synth_samples_shard_$*.out" 2> "$(BUILD_DIR)/bach10_mf0_synth_samples_shard_$*.err"

analyze-bach10-mf0-synth-chord-misses: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyze_bach10_mf0_synth_chord_misses env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 MUSIC_ANALYZER_MUSICNET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_musicnet

analyze-bach10-mf0-synth-pitch-misses: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyze_bach10_mf0_synth_pitch_misses env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 MUSIC_ANALYZER_MUSICNET_VERBOSE_PITCH_MISSES=1 $(BUILD_DIR)/analyzer_musicnet

prepare-instrument-samples: scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	INSTRUMENT_SAMPLE_BUILD_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" INSTRUMENT_SAMPLE_SOURCE_DIR="$(INSTRUMENT_SAMPLE_SOURCE_DIR)" INSTRUMENT_SAMPLE_SOUNDFONT="$(INSTRUMENT_SAMPLE_SOUNDFONT)" INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE="$(INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE)" INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY="$(INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY)" INSTRUMENT_SAMPLE_DRUM_KITS="$(INSTRUMENT_SAMPLE_DRUM_KITS)" INSTRUMENT_SAMPLE_TARGET_PER_FAMILY="$(INSTRUMENT_SAMPLE_TARGET_PER_FAMILY)" INSTRUMENT_SAMPLE_JOBS="$(INSTRUMENT_SAMPLE_JOBS)" $(PYTHON) scripts/prepare_instrument_samples.py --output-root "$(INSTRUMENT_SAMPLE_BUILD_ROOT)" --download-dir "$(INSTRUMENT_SAMPLE_SOURCE_DIR)"

$(INSTRUMENT_SAMPLE_MANIFEST_STAMP): scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-instrument-samples
	@touch "$@"

test-instrument-samples: test-instrument-samples-parallel

test-instrument-samples-serial: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" $(BUILD_DIR)/analyzer_instrument_samples

test-instrument-samples-parallel: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_instrument_samples_parallel $(MAKE) $(INSTRUMENT_SAMPLE_TEST_MAKE_JOBS) $(INSTRUMENT_SAMPLE_SHARD_TARGETS)

test-instrument-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples_shard_$* env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT="$(INSTRUMENT_SAMPLE_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_instrument_samples

$(BUILD_DIR)/instrument_sample_attributes.tsv: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/prepare_instrument_samples.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(INSTRUMENT_SAMPLE_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS)" $(INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS)

$(BUILD_DIR)/instrument_sample_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	-env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT="$(INSTRUMENT_SAMPLE_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX="$*" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_instrument_samples > "$(BUILD_DIR)/instrument_sample_attributes.shard-$*.out"

analyze-instrument-sample-attributes: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/summarize_instrument_sample_attributes.py
	$(PYTHON) scripts/summarize_instrument_sample_attributes.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSTRUMENT_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/instrument_sample_attributes.tsv"

inspect-instrument-sample-owner-buckets: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/inspect_instrument_sample_owner_buckets.py
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSPECT_INSTRUMENT_OWNER_ARGS)

find-instrument-owner-patterns: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py
	$(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(PATTERN_ARGS)

find-instrument-status-patterns: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py
	$(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(if $(PATTERN_ARGS),--status-top-buckets 0 $(PATTERN_ARGS),$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS))

filter-instrument-attribute-rows: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/filter_instrument_attribute_rows.py
	$(PYTHON) scripts/filter_instrument_attribute_rows.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(FILTER_ATTRIBUTE_ARGS)

filter-drum-primary-attribute-rows: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(FILTER_DRUM_ATTRIBUTE_ARGS)

filter-drum-full-attribute-rows: $(BUILD_DIR)/drum_full_attribute_rows.tsv scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(FILTER_DRUM_ATTRIBUTE_ARGS)

filter-drum-full-exact-attribute-rows: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(FILTER_DRUM_ATTRIBUTE_ARGS)

measure-analyzer-attributes: analyze-instrument-sample-attributes analyze-real-note-attributes analyze-guitar-chord-mix-attributes analyze-drum-primary-misses analyze-mdb-drum-attributes
	@printf '%s\n' ""
	@printf '%s\n' "measurement report files:"
	@printf '%s\n' "  instrument TSV: $(BUILD_DIR)/instrument_sample_attributes.tsv"
	@printf '%s\n' "  real-note TSV: $(BUILD_DIR)/real_note_full_mix_attributes.tsv"
	@printf '%s\n' "  guitar chord TSV: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv"
	@printf '%s\n' "  drum primary logs: $(BUILD_DIR)/*_primary_debug.err"
	@printf '%s\n' "  MDB drum log: $(MDB_DRUMS_MISS_LOG)"
	@printf '%s\n' ""
	@printf '%s\n' "real-note detailed non-hit attributes:"
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(MEASURE_REAL_NOTE_ARGS)
	@printf '%s\n' ""
	@printf '%s\n' "generated sample owner attribute buckets:"
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(MEASURE_INSTRUMENT_OWNER_ARGS)
	@printf '%s\n' ""
	@printf '%s\n' "guitar chord miss attribute buckets:"
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(MEASURE_GUITAR_BUCKET_ARGS)

$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/inspect_instrument_sample_owner_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --dump-rows > "$@"

$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows > "$@"

$(REAL_NOTE_MISS_ATTRIBUTE_ROWS): $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows --misses-only > "$@"

$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows > "$@"

$(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS): $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows --misses-only > "$@"

measure-analyzer-attribute-rows:
	+$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) analyze-instrument-sample-attributes analyze-real-note-attributes analyze-guitar-chord-mix-attributes analyze-drum-primary-attribute-rows
	+$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_ROW_DUMPS)
	@printf '%s\n' "attribute row dumps:"
	@printf '%s\n' "  $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(REAL_NOTE_MISS_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"
	@if [ -f "$(BUILD_DIR)/drum_full_attribute_rows.tsv" ]; then printf '%s\n' "  $(BUILD_DIR)/drum_full_attribute_rows.tsv"; else printf '%s\n' "  full drum rows skipped; run make measure-analyzer-attribute-rows-full for exhaustive drum rows"; fi

measure-analyzer-attribute-rows-full: measure-analyzer-attribute-rows analyze-drum-rule-grid $(BUILD_DIR)/drum_full_attribute_rows.tsv
	@printf '%s\n' "full drum attribute row dump:"
	@printf '%s\n' "  $(BUILD_DIR)/drum_full_attribute_rows.tsv"

require-cached-analyzer-attribute-rows:
	@missing=0; for rows in $(CACHED_ANALYZER_PATTERN_INPUT_PATHS); do if [ ! -f "$$rows" ]; then printf '%s\n' "missing cached analyzer pattern input: $$rows"; missing=1; fi; done; if [ "$$missing" -ne 0 ]; then printf '%s\n' "run make measure-analyzer-attribute-rows to regenerate cached analyzer rows"; exit 2; fi

refresh-analyzer-detected-attribute-rows: scripts/refresh_analyzer_detected_attribute_rows.py
	$(PYTHON) scripts/refresh_analyzer_detected_attribute_rows.py --build-dir "$(BUILD_DIR)" --python "$(PYTHON)" --jobs "$(REFRESH_ANALYZER_ATTRIBUTE_JOBS)"

print-analyzer-detected-attributes: $(MEASURE_ANALYZER_ROW_DUMPS) $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_detected_attributes $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) $(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)

print-analyzer-detected-attributes-cached: scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_detected_attributes_cached $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) $(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)

measure-analyzer-detected-attributes: measure-analyzer-attribute-rows
	+$(MAKE) print-analyzer-detected-attributes

measure-analyzer-detected-attributes-full: measure-analyzer-attribute-rows-full
	+$(MAKE) print-analyzer-detected-attributes

$(MEASURE_ANALYZER_PATTERN_DETECTED_REPORT): FORCE $(MEASURE_ANALYZER_ROW_DUMPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/print_analyzer_detected_attributes.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; $(MAKE) print-analyzer-detected-attributes > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT): FORCE $(MEASURE_ANALYZER_ROW_DUMPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/report_analyzer_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/report_analyzer_attribute_patterns.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(PATTERN_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT): FORCE $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument owner pattern candidates:"; $(MAKE) find-instrument-owner-patterns PATTERN_ARGS="$(MEASURE_INSTRUMENT_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT): FORCE $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument final-status pattern candidates:"; $(MAKE) find-instrument-status-patterns PATTERN_ARGS="$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix coverage summary:"; $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(MEASURE_REAL_NOTE_SUMMARY_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix pattern candidates:"; $(MAKE) find-real-note-attribute-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OWNERSHIP_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note ownership-miss pattern candidates:"; $(MAKE) find-real-note-ownership-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note octave-displacement pattern candidates:"; $(MAKE) find-real-note-octave-displacement-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note strongest-row confusion pattern candidates:"; $(MAKE) find-real-note-row-confusion-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note visual-row confusion pattern candidates:"; $(MAKE) find-real-note-visual-row-confusion-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak expected-row pattern candidates:"; $(MAKE) find-real-note-weak-expected-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak visual expected-row pattern candidates:"; $(MAKE) find-real-note-weak-visual-expected-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord pattern candidates:"; $(MAKE) find-guitar-chord-mix-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_PRIMARY_ORDER_REPORT): FORCE $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord primary-order analysis:"; $(MAKE) analyze-guitar-chord-primary-order PRIMARY_ORDER_ARGS="$(PRIMARY_ORDER_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_RECOVERY_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_recovery.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord recovery threshold simulation:"; $(MAKE) analyze-guitar-chord-mix-recovery RECOVERY_ARGS="$(RECOVERY_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_extra_components.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord extra component analysis:"; $(MAKE) analyze-guitar-chord-mix-extra-components EXTRA_COMPONENT_ARGS="$(EXTRA_COMPONENT_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_PRIMARY_REPORT): FORCE $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum primary pattern candidates:"; $(MAKE) find-drum-primary-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum spread exact gate matrix:"; if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; elif [ -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "skipped regeneration; using existing $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; else printf '%s\n' "skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) $(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP) scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "protected drum primary pattern candidates:"; $(MAKE) find-protected-drum-primary-attribute-patterns PATTERN_ARGS="$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) $(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP) scripts/summarize_drum_active_false_rows.py scripts/find_drum_active_false_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum active false-row summary:"; $(MAKE) analyze-drum-active-false-rows; printf '%s\n' ""; printf '%s\n' "drum active false pattern candidates:"; $(MAKE) find-drum-active-false-patterns $(if $(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS),DRUM_ACTIVE_EXTRA_PROTECTED_ROWS="$(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)") PATTERN_ARGS="$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum spread exact pattern candidates:"; $(MAKE) find-drum-spread-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_SKIP_REPORT): FORCE | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { if [ "$(REPORT_FULL_DRUM_SKIP)" = "1" ]; then printf '%s\n' ""; printf '%s\n' "protected drum full-row pattern candidates:"; printf '%s\n' "skipped; run make measure-analyzer-patterns-full for exhaustive protected full-drum rows"; fi; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "protected drum full-row pattern candidates:"; $(MAKE) find-protected-drum-full-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_FULL_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_EXACT_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum full exact pattern candidates:"; $(MAKE) find-drum-full-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_FULL_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

measure-analyzer-pattern-report-sections: $(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)
	@true

report-analyzer-patterns-from-rows: scripts/run_with_duration.sh scripts/report_analyzer_attribute_patterns.py scripts/print_analyzer_detected_attributes.py
	+$(RUN_WITH_DURATION) analyzer_pattern_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) measure-analyzer-pattern-report-sections
	@cat $(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)

$(MEASURE_ANALYZER_CACHED_PATTERN_DETECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(RUN_WITH_DURATION) analyzer_detected_attributes_cached $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_SUMMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/report_analyzer_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/report_analyzer_attribute_patterns.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(PATTERN_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_OWNER_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument owner pattern candidates:"; $(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(MEASURE_INSTRUMENT_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_STATUS_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument final-status pattern candidates:"; $(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_SUMMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/summarize_real_note_attributes.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix coverage summary:"; $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(MEASURE_REAL_NOTE_SUMMARY_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OWNERSHIP_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note ownership-miss pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note octave-displacement pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status octave_displacement --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note strongest-row confusion pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note visual-row confusion pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak expected-row pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status weak_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak visual expected-row pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status weak_visual_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_GUITAR_CHORD_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord pattern candidates:"; $(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(MEASURE_GUITAR_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_DRUM_PRIMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum primary pattern candidates:"; $(PYTHON) scripts/find_drum_attribute_patterns.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --jobs "$(DRUM_PATTERN_JOBS)" $(MEASURE_DRUM_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

report-analyzer-patterns-from-cached-rows: require-cached-analyzer-attribute-rows scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_cached_pattern_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS)
	@cat $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS)

$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY): $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS) scripts/summarize_detector_route_report.py | $(BUILD_DIR)
	@tmp_report="$@.$$$$.report"; tmp="$@.$$$$.tmp"; cat $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS) > "$$tmp_report" && $(PYTHON) scripts/summarize_detector_route_report.py "$$tmp_report" > "$$tmp"; status="$$?"; rm -f "$$tmp_report"; if [ "$$status" -eq 0 ]; then mv "$$tmp" "$@"; else rm -f "$$tmp"; exit "$$status"; fi

measure-analyzer-patterns-cached-summary: $(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY) scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	@cat "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"
	+@$(MAKE) measure-analyzer-patterns-cached-coverage

measure-analyzer-patterns-cached-coverage: scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py | $(BUILD_DIR)
	+@if [ ! -f "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" ]; then $(MAKE) "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"; fi
	@tmp="$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY).$$$$.tmp"; $(PYTHON) scripts/inspect_detector_coverage_candidates.py "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" $(DETECTOR_COVERAGE_SUMMARY_ARGS) $(DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS) > "$$tmp" && mv "$$tmp" "$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY)"
	@cat "$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY)"

report-analyzer-patterns-from-rows-full:
	+$(MAKE) report-analyzer-patterns-from-rows REPORT_FULL_DRUM_SKIP=0 MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS="$(MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS)"
	+$(RUN_WITH_DURATION) analyzer_pattern_full_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS)
	@cat $(MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS)

measure-analyzer-patterns: measure-analyzer-attribute-rows
	+$(MAKE) report-analyzer-patterns-from-rows

measure-analyzer-patterns-cached: require-cached-analyzer-attribute-rows
	+$(MAKE) report-analyzer-patterns-from-cached-rows

measure-analyzer-patterns-full: measure-analyzer-attribute-rows analyze-drum-full-gate-matrix-parallel analyze-drum-full-merged-expected-attribute-rows analyze-drum-tom-bleed-caps-cached
	+$(MAKE) report-analyzer-patterns-from-rows-full

measure-analyzer-pattern-report: | $(BUILD_DIR)
	+$(MAKE) -s measure-analyzer-patterns | tee "$(MEASURE_ANALYZER_REPORT)"
	@printf '%s\n' "measurement report: $(MEASURE_ANALYZER_REPORT)"

download-real-note-samples: FORCE | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if [ -s "$(NSYNTH_SAMPLE_ARCHIVE)" ] && ! $(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_ARCHIVE).corrupt"; fi
	@if [ ! -s "$(NSYNTH_SAMPLE_ARCHIVE)" ]; then curl -fL -C - -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	@$(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null

$(NSYNTH_SAMPLE_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if [ ! -s "$(NSYNTH_SAMPLE_ARCHIVE)" ]; then curl -fL -C - -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	@$(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null

$(NSYNTH_SAMPLE_ROOT)/examples.json: $(NSYNTH_SAMPLE_ARCHIVE) | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if ! $(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_ARCHIVE).corrupt"; curl -fL -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	$(TAR) -xzf "$(NSYNTH_SAMPLE_ARCHIVE)" -C "$(REAL_SAMPLE_SOURCE_DIR)"
	touch "$@"

prepare-real-note-samples: scripts/prepare_nsynth_samples.py $(NSYNTH_SAMPLE_ROOT)/examples.json | $(BUILD_DIR)
	NSYNTH_SAMPLE_ROOT="$(NSYNTH_SAMPLE_ROOT)" REAL_NOTE_SAMPLE_DIR="$(REAL_NOTE_SAMPLE_DIR)" REAL_NOTE_SAMPLE_LIMIT="$(REAL_NOTE_SAMPLE_LIMIT)" $(PYTHON) scripts/prepare_nsynth_samples.py --nsynth-root "$(NSYNTH_SAMPLE_ROOT)" --output "$(REAL_NOTE_SAMPLE_DIR)" --limit "$(REAL_NOTE_SAMPLE_LIMIT)"

test-real-note-sample-shards: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_sample_shards.py
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_locked $(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_SAMPLE_LOCK_DIR)" -- $(RUN_REAL_NOTE_SAMPLE_SHARDS_UNLOCKED)

test-real-note-sample-shards-unlocked: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_parallel $(MAKE) $(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS) $(REAL_NOTE_SAMPLE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_shards $(PYTHON) scripts/check_real_note_sample_shards.py --min-bass "$(REAL_NOTE_SAMPLE_MIN_BASS)" --min-guitar "$(REAL_NOTE_SAMPLE_MIN_GUITAR)" --min-piano "$(REAL_NOTE_SAMPLE_MIN_PIANO)" --min-vocals "$(REAL_NOTE_SAMPLE_MIN_VOCALS)" --min-other "$(REAL_NOTE_SAMPLE_MIN_OTHER)" $(REAL_NOTE_SAMPLE_HIT_PERCENT_ARGS) --max-failures "$(REAL_NOTE_SAMPLE_MAX_FAILURES)" $(REAL_NOTE_SAMPLE_SHARD_OUTS)

test-real-note-sample-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(REAL_NOTE_SAMPLE_REQUIRED_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_ROOT)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES="$(REAL_NOTE_SAMPLE_MAX_FAILURE_LINES)" MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.out" 2> "$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.err"

test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_TAG := nsynth
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(REAL_NOTE_SAMPLE_DIR)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(REAL_NOTE_MIN_BASS)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(REAL_NOTE_MIN_GUITAR)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO := $(REAL_NOTE_MIN_PIANO)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS := $(REAL_NOTE_MIN_VOCALS)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(REAL_NOTE_MIN_OTHER)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT := $(REAL_NOTE_MIN_BASS_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT := $(REAL_NOTE_MIN_GUITAR_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT := $(REAL_NOTE_MIN_PIANO_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT := $(REAL_NOTE_MIN_VOCALS_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT := $(REAL_NOTE_MIN_OTHER_HIT_PERCENT)
test-real-note-samples: test-real-note-samples-parallel

test-real-note-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

test-real-note-samples-full-mix: test-real-note-samples-full-mix-parallel

test-real-note-samples-full-mix-serial: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" $(REAL_NOTE_FULL_MIX_GATE_ENV) $(BUILD_DIR)/analyzer_real_note_samples

test-real-note-samples-full-mix-parallel: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_full_mix_shards.py
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_parallel $(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_FULL_MIX_LOCK_DIR)" -- "$(MAKE)" REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX="$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)" test-real-note-samples-full-mix-parallel-unlocked

test-real-note-samples-full-mix-parallel-unlocked: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/check_real_note_full_mix_shards.py
	+$(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX="$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)" $(REAL_NOTE_FULL_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_real_note_full_mix_shards $(PYTHON) scripts/check_real_note_full_mix_shards.py --min-any-hit-percent "$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" --min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" --min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT)" --min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT)" --bass-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" --guitar-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" --piano-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" --vocals-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" --other-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" --bass-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_BASS_FIRST_ROW_PERCENT)" --guitar-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT)" --piano-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_FIRST_ROW_PERCENT)" --vocals-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_FIRST_ROW_PERCENT)" --other-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT)" --bass-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_BASS_VISUAL_ROW_PERCENT)" --guitar-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT)" --piano-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_VISUAL_ROW_PERCENT)" --vocals-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_VISUAL_ROW_PERCENT)" --other-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT)" --max-drum-active-percent "$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" $(REAL_NOTE_FULL_MIX_SOURCE_ROUTE_LIMIT_ARGS) $(REAL_NOTE_FULL_MIX_SHARD_OUTS)

test-real-note-samples-full-mix-detector-parallel: REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX := detector_real_note_full_mix_shard
test-real-note-samples-full-mix-detector-parallel: test-real-note-samples-full-mix-parallel

test-real-note-samples-full-mix-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 $(REAL_NOTE_FULL_MIX_SHARD_GATE_ENV) $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.out" 2> "$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.err"

analyze-real-note-misses: analyze-real-note-misses-parallel

analyze-real-note-misses-serial: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/analyze_real_note_misses.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" $(REAL_NOTE_FULL_MIX_GATE_ENV) MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_verbose.out" 2> "$(BUILD_DIR)/real_note_full_mix_verbose.err"
	$(PYTHON) scripts/analyze_real_note_misses.py "$(BUILD_DIR)/real_note_full_mix_verbose.err"

analyze-real-note-misses-parallel: $(BUILD_DIR)/analyzer_real_note_samples scripts/analyze_real_note_misses.py scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose_parallel $(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) $(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_TARGETS)
	$(PYTHON) scripts/analyze_real_note_misses.py $(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_ERRS)

analyze-real-note-misses-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_verbose_shard_$*.out" 2> "$(BUILD_DIR)/real_note_full_mix_verbose_shard_$*.err"

$(BUILD_DIR)/real_note_full_mix_attributes.tsv: $(BUILD_DIR)/analyzer_real_note_samples scripts/prepare_nsynth_samples.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/real_note_full_mix_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_real_note_samples scripts/prepare_nsynth_samples.py | $(BUILD_DIR)
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_attributes.shard-$*.out"

test-real-note-visual-strength: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_visual_strength $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_ARGS)

analyze-real-note-attributes: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/real_note_full_mix_attributes.tsv"

update-detection-accuracy-report: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/write_detection_accuracy_report.py
	$(PYTHON) scripts/write_detection_accuracy_report.py --input "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(DETECTION_ACCURACY_CHORD_ARGS) $(DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG) $(DETECTION_ACCURACY_URMP_GATE_ARG) $(DETECTION_ACCURACY_BACH10_GATE_ARGS) $(DETECTION_ACCURACY_MUSICNET_GATE_ARG) $(DETECTION_ACCURACY_DRUM_GATE_ARG) --output "$(DETECTION_ACCURACY_REPORT)"

test-detection-accuracy-report: tests/test_write_detection_accuracy_report.py scripts/write_detection_accuracy_report.py
	$(PYTHON) tests/test_write_detection_accuracy_report.py

inspect-real-note-attribute-buckets: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(INSPECT_BUCKET),--bucket "$(INSPECT_BUCKET)") $(INSPECT_ARGS)

find-real-note-attribute-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(PATTERN_ARGS)

find-real-note-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),--top-buckets 8 --limit 10 --max-negative-samples 0 --max-conditions 3 --beam-width 120 --show-near-misses 4 --show-examples 1)

find-real-note-practical-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-focused-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-coverage-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-first-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-focused-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-coverage-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-first-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-ownership-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS))

find-real-note-octave-displacement-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

find-real-note-octave-displacement-runtime-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

find-real-note-weak-expected-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status weak_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS))

find-real-note-weak-visual-expected-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status weak_visual_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS))

measure-real-note-octave-display-aliases: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/measure_real_note_octave_display_aliases.py
	$(PYTHON) scripts/measure_real_note_octave_display_aliases.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(OCTAVE_ALIAS_ARGS)

evaluate-real-note-display-shadow: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_display_shadow $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(DISPLAY_SHADOW_ARGS),--summary-only --jobs "$(DISPLAY_SHADOW_JOBS)")

.PHONY: evaluate-real-note-display-shadow-all
evaluate-real-note-display-shadow-all: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_display_shadow_all $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(DISPLAY_SHADOW_ARGS),--shadow-row all --target-row all --compact-routes --threshold-search --max-protected 0 --min-threshold-extra-hits 20 --threshold-limit 8 --jobs "$(DISPLAY_SHADOW_JOBS)")

evaluate-real-note-vocal-shadow-safety: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) real_note_vocal_shadow_safety_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) evaluate-real-note-vocal-shadow-safety-nsynth evaluate-real-note-vocal-shadow-safety-vocadito

evaluate-real-note-vocal-shadow-safety-nsynth: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_shadow_nsynth $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --shadow-row other --target-row vocals --compact-routes --threshold-search --max-protected 0 --threshold-limit 4

evaluate-real-note-vocal-shadow-safety-vocadito: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_shadow_vocadito $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --shadow-row other --target-row vocals --compact-routes --threshold-search --max-protected 0 --threshold-limit 4

evaluate-real-note-vocal-display-fallback: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_vocal_display_fallback.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_display_fallback $(PYTHON) scripts/evaluate_real_note_vocal_display_fallback.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(VOCAL_DISPLAY_FALLBACK_ARGS),--summary-only --top 12)

measure-real-note-attribute-rule: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/measure_real_note_attribute_rule.py
	$(PYTHON) scripts/measure_real_note_attribute_rule.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_RULE_CONDITION_ARGS) $(REAL_NOTE_RULE_GROUP_BY_ARGS) $(RULE_ARGS)

inspect-real-note-candidate-rows: $(REAL_NOTE_CANDIDATE_ROW_PATHS) scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) scripts/inspect_real_note_candidate_rows.py $(if $(REAL_NOTE_CANDIDATE_RULE),--rule "$(REAL_NOTE_CANDIDATE_RULE)") $(REAL_NOTE_CANDIDATE_ARGS) $(REAL_NOTE_CANDIDATE_ROW_PATHS)

inspect-detector-coverage-candidates: scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	@test -f "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" || { printf '%s\n' "missing $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY); run make detector-improvement-route-summary first"; exit 2; }
	$(PYTHON) scripts/inspect_detector_coverage_candidates.py "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" $(DETECTOR_COVERAGE_CANDIDATE_ARGS) $(DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS)

detector-improvement-coverage-cached:
	+$(MAKE) inspect-detector-coverage-candidates DETECTOR_COVERAGE_CANDIDATE_ARGS="$(DETECTOR_COVERAGE_SUMMARY_ARGS)"

$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(VOCADITO_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(VOCADITO_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/vocadito_full_mix_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(VOCADITO_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCADITO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCADITO_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=20 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocadito_full_mix_attributes.shard-$*.out"

analyze-vocadito-full-mix-attributes: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)"

find-vocadito-full-mix-row-confusion-patterns: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" $(VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-vocadito-full-mix-visual-row-confusion-patterns: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" $(VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-vocadito-full-mix-ownership-patterns: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" $(VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-vocadito-full-mix-broad-vocal-ownership-patterns: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCADITO_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" $(VOCADITO_PATTERN_EXTRA_PROTECTED_ARGS) --bucket "ownership_miss:vocals/*->*" --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS))

prepare-guitar-fretboard-note-samples: scripts/prepare_guitar_fretboard_notes.py | $(BUILD_DIR)
	GUITAR_FRETBOARD_NOTES_SAMPLE_DIR="$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)" GUITAR_FRETBOARD_NOTES_LIMIT="$(GUITAR_FRETBOARD_NOTES_LIMIT)" GUITAR_FRETBOARD_NOTES_OFFLINE="$(GUITAR_FRETBOARD_NOTES_OFFLINE)" $(PYTHON) scripts/prepare_guitar_fretboard_notes.py --output "$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)"

test-guitar-fretboard-note-samples test-guitar-fretboard-note-samples-parallel: REAL_NOTE_SAMPLE_TAG := guitar_fretboard
test-guitar-fretboard-note-samples test-guitar-fretboard-note-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)
test-guitar-fretboard-note-samples test-guitar-fretboard-note-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(GUITAR_FRETBOARD_NOTES_MIN_GUITAR)
test-guitar-fretboard-note-samples test-guitar-fretboard-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(GUITAR_FRETBOARD_NOTES_MIN_GUITAR)
test-guitar-fretboard-note-samples test-guitar-fretboard-note-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(GUITAR_FRETBOARD_NOTES_MAX_FAILURES)
test-guitar-fretboard-note-samples: test-guitar-fretboard-note-samples-parallel

test-guitar-fretboard-note-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-guitar-fretboard-note-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

download-guitar-techs-samples: $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)

$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P1_singlenotes.zip.part" "$(GUITAR_TECHS_P1_SINGLENOTES_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P1_SINGLENOTES_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" >/dev/null

$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P2_singlenotes.zip.part" "$(GUITAR_TECHS_P2_SINGLENOTES_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P2_SINGLENOTES_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" >/dev/null

prepare-guitar-techs-samples: scripts/prepare_guitar_techs_samples.py download-guitar-techs-samples | $(BUILD_DIR)
	GUITAR_TECHS_SAMPLE_DIR="$(GUITAR_TECHS_SAMPLE_DIR)" GUITAR_TECHS_SAMPLE_LIMIT="$(GUITAR_TECHS_SAMPLE_LIMIT)" GUITAR_TECHS_MIN_SAMPLES="$(GUITAR_TECHS_MIN_GUITAR)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_samples.py --archive "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" --output "$(GUITAR_TECHS_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_MIN_GUITAR)" --ffmpeg "$(FFMPEG)"

$(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv: scripts/prepare_guitar_techs_samples.py $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-guitar-techs-samples
	@touch "$(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv"

test-guitar-techs-samples test-guitar-techs-samples-parallel: REAL_NOTE_SAMPLE_TAG := guitar_techs
test-guitar-techs-samples test-guitar-techs-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(GUITAR_TECHS_SAMPLE_DIR)
test-guitar-techs-samples test-guitar-techs-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(GUITAR_TECHS_MIN_GUITAR)
test-guitar-techs-samples test-guitar-techs-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(GUITAR_TECHS_MIN_GUITAR)
test-guitar-techs-samples test-guitar-techs-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(GUITAR_TECHS_MAX_FAILURES)
test-guitar-techs-samples: test-guitar-techs-samples-parallel

test-guitar-techs-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-guitar-techs-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(GUITAR_TECHS_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GUITAR_TECHS_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(GUITAR_TECHS_ATTRIBUTE_PARTS)

$(BUILD_DIR)/guitar_techs_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_guitar_techs_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GUITAR_TECHS_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GUITAR_TECHS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/guitar_techs_attributes.shard-$*.out" 2> "$(BUILD_DIR)/guitar_techs_attributes.shard-$*.err"

$(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS): $(GUITAR_TECHS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(GUITAR_TECHS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS): $(GUITAR_TECHS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(GUITAR_TECHS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-guitar-techs-attributes: $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "GuitarTechs attribute rows:"
	@printf '%s\n' "  $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS)"

download-guitar-techs-chord-samples: $(GUITAR_TECHS_P1_CHORDS_ARCHIVE) $(GUITAR_TECHS_P2_CHORDS_ARCHIVE)

$(GUITAR_TECHS_P1_CHORDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P1_chords.zip.part" "$(GUITAR_TECHS_P1_CHORDS_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P1_CHORDS_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" >/dev/null

$(GUITAR_TECHS_P2_CHORDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P2_chords.zip.part" "$(GUITAR_TECHS_P2_CHORDS_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P2_CHORDS_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" >/dev/null

prepare-guitar-techs-chord-samples: scripts/prepare_guitar_techs_chord_samples.py download-guitar-techs-chord-samples | $(BUILD_DIR)
	GUITAR_TECHS_CHORD_SAMPLE_DIR="$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" GUITAR_TECHS_CHORD_SAMPLE_LIMIT="$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" GUITAR_TECHS_CHORD_MIN_EXCERPTS="$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_chord_samples.py --archive "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" --output "$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" --ffmpeg "$(FFMPEG)"

$(GUITAR_TECHS_CHORD_MANIFEST): scripts/prepare_guitar_techs_chord_samples.py | $(BUILD_DIR)
	+$(MAKE) download-guitar-techs-chord-samples
	GUITAR_TECHS_CHORD_SAMPLE_DIR="$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" GUITAR_TECHS_CHORD_SAMPLE_LIMIT="$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" GUITAR_TECHS_CHORD_MIN_EXCERPTS="$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_chord_samples.py --archive "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" --output "$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" --ffmpeg "$(FFMPEG)"

test-guitar-techs-chord-samples: test-guitar-techs-chord-samples-parallel

test-guitar-techs-chord-samples-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-techs-chord-samples scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_guitar_techs_chord_samples_parallel $(MAKE) $(GUITAR_TECHS_CHORD_TEST_MAKE_JOBS) $(GUITAR_TECHS_CHORD_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_guitar_techs_chord_shards $(PYTHON) scripts/check_guitarset_shards.py $(GUITAR_TECHS_CHORD_SHARD_OUTS) --required-excerpts "$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" --required-windows "$(GUITAR_TECHS_CHORD_MIN_WINDOWS)" --min-recall-percent "$(GUITAR_TECHS_CHORD_MIN_RECALL_PERCENT)" --min-precision-percent "$(GUITAR_TECHS_CHORD_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(GUITAR_TECHS_CHORD_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent "$(GUITAR_TECHS_CHORD_MAX_CONTAMINATION_PERCENT)" --max-false-vocal-percent "$(GUITAR_TECHS_CHORD_MAX_FALSE_VOCAL_PERCENT)" --min-chord-checks "$(GUITAR_TECHS_CHORD_MIN_WINDOWS)" --min-chord-recall-percent "$(GUITAR_TECHS_CHORD_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(GUITAR_TECHS_CHORD_MIN_CHORD_PRECISION_PERCENT)"

test-guitar-techs-chord-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_CHORD_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/guitar_techs_chord_samples_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_guitar_techs_chord_samples_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_CHORD_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITAR_TECHS_CHORD_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_CHORD_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_TECHS_CHORD_ATTRIBUTE_PARTS)

refresh-guitar-techs-chord-attributes: $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_CHORD_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GUITAR_TECHS_CHORD_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" "$(MAKE)" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_TECHS_CHORD_ATTRIBUTE_PARTS)

$(BUILD_DIR)/guitar_techs_chord_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_CHORD_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/guitar_techs_chord_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_CHORD_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITAR_TECHS_CHORD_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS): $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(GUITAR_TECHS_CHORD_MISS_ATTRIBUTE_ROWS): $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" --dump-rows --misses-only > "$@"

analyze-guitar-techs-chord-attributes: $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"
	@printf '%s\n' "attribute TSV: $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"

analyze-guitar-techs-chord-extra-components: $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_chord_extra_components.py
	$(PYTHON) scripts/analyze_guitar_chord_extra_components.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" $(EXTRA_COMPONENT_ARGS)

inspect-guitar-techs-chord-attribute-buckets: $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" $(BUCKET_ARGS)

find-guitar-techs-chord-attribute-patterns: $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" $(PATTERN_ARGS)

find-guitar-techs-chord-route-patterns:
	+$(MAKE) find-guitar-techs-chord-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

$(GUITAR_CHORD_MIX_MANIFEST): | $(BUILD_DIR) scripts/prepare_hf_guitar_chord_mix.py
	GUITAR_CHORD_MIX_SAMPLE_DIR="$(GUITAR_CHORD_MIX_SAMPLE_DIR)" GUITAR_CHORD_MIX_LIMIT="$(GUITAR_CHORD_MIX_LIMIT)" GUITAR_CHORD_MIX_MIN_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(GUITAR_CHORD_MIX_SAMPLE_DIR)" --limit "$(GUITAR_CHORD_MIX_LIMIT)" --min-samples "$(GUITAR_CHORD_MIX_MIN_EXCERPTS)"

prepare-guitar-chord-mix-samples: scripts/prepare_hf_guitar_chord_mix.py | $(BUILD_DIR)
	GUITAR_CHORD_MIX_SAMPLE_DIR="$(GUITAR_CHORD_MIX_SAMPLE_DIR)" GUITAR_CHORD_MIX_LIMIT="$(GUITAR_CHORD_MIX_LIMIT)" GUITAR_CHORD_MIX_MIN_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(GUITAR_CHORD_MIX_SAMPLE_DIR)" --limit "$(GUITAR_CHORD_MIX_LIMIT)" --min-samples "$(GUITAR_CHORD_MIX_MIN_EXCERPTS)"

test-guitar-chord-mix-samples: test-guitar-chord-mix-samples-parallel

test-guitar-chord-mix-samples-serial: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS="$(GUITAR_CHORD_MIX_MIN_CHORD_HITS)" MUSIC_ANALYZER_GUITARSET_MIN_PRIMARY_CHORD_HITS="$(GUITAR_CHORD_MIX_MIN_PRIMARY_CHORD_HITS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

test-guitar-chord-mix-samples-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples_parallel $(MAKE) $(GUITAR_CHORD_MIX_TEST_MAKE_JOBS) $(GUITAR_CHORD_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_guitar_chord_mix_shards $(PYTHON) scripts/check_guitarset_shards.py $(GUITAR_CHORD_MIX_SHARD_OUTS) --required-excerpts "$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" --required-windows "$(GUITAR_CHORD_MIX_MIN_WINDOWS)" --min-recall-percent "$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" --min-precision-percent "$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent "$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" --max-false-vocal-percent "$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" --min-chord-checks "$(GUITAR_CHORD_MIX_MIN_WINDOWS)" --min-chord-recall-percent "$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" --min-chord-hits "$(GUITAR_CHORD_MIX_MIN_CHORD_HITS)" --min-primary-chord-hits "$(GUITAR_CHORD_MIX_MIN_PRIMARY_CHORD_HITS)"

test-guitar-chord-mix-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITAR_CHORD_MIX_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/guitar_chord_mix_samples_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0 MUSIC_ANALYZER_GUITARSET_MIN_PRIMARY_CHORD_HITS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITAR_CHORD_MIX_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

analyze-guitar-chord-mix-misses: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GUITAR_CHORD_MIX_MISS_LOG).summary" 2> "$(GUITAR_CHORD_MIX_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GUITAR_CHORD_MIX_MISS_LOG)"

$(BUILD_DIR)/guitar_chord_mix_attributes.tsv: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/guitar_chord_mix_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITAR_CHORD_MIX_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/guitar_chord_mix_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITAR_CHORD_MIX_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

analyze-guitar-chord-mix-attributes: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv"
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv"

analyze-guitar-chord-mix-recovery: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_recovery.py
	$(PYTHON) scripts/analyze_guitar_chord_recovery.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(RECOVERY_ARGS)

analyze-guitar-chord-primary-order: $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py
	$(PYTHON) scripts/analyze_guitar_primary_order.py "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" $(PRIMARY_ORDER_ARGS)

analyze-gaps-guitar-full-primary-order: $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py
	$(PYTHON) scripts/analyze_guitar_primary_order.py "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)" $(PRIMARY_ORDER_ARGS)

analyze-guitar-minor-third-candidates: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_minor_third_candidates.py
	$(PYTHON) scripts/analyze_guitar_minor_third_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"

prepare-guitar-techs-chord-case: $(GUITAR_TECHS_CHORD_MANIFEST) scripts/extract_guitarset_manifest_recording.py | $(BUILD_DIR)
	$(PYTHON) scripts/extract_guitarset_manifest_recording.py "$(GUITAR_TECHS_CHORD_MANIFEST)" "$(GUITAR_TECHS_CHORD_CASE_MANIFEST)" --recording-id "$(GUITAR_TECHS_CHORD_CASE_ID)"

inspect-guitar-techs-chord-case: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-techs-chord-case scripts/inspect_guitarset_attribute_buckets.py
	rm -f "$(GUITAR_TECHS_CHORD_CASE_ATTRIBUTE_TSV)" "$(GUITAR_TECHS_CHORD_CASE_OUT)"
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_CHORD_CASE_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$(GUITAR_TECHS_CHORD_CASE_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_guitarset > "$(GUITAR_TECHS_CHORD_CASE_OUT)"
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_CHORD_CASE_ATTRIBUTE_TSV)" --dump-rows

analyze-guitar-major-third-candidates: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_minor_third_candidates.py
	$(PYTHON) scripts/analyze_guitar_minor_third_candidates.py --quality major "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"

analyze-guitar-minor-fifth-candidates: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_minor_third_candidates.py
	$(PYTHON) scripts/analyze_guitar_minor_third_candidates.py --tone fifth "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"

analyze-guitar-major-fifth-candidates: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_minor_third_candidates.py
	$(PYTHON) scripts/analyze_guitar_minor_third_candidates.py --quality major --tone fifth "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"

audition-sample: scripts/audition_sample.sh
	bash scripts/audition_sample.sh "$(AUDIO)" "$(START)" "$(DURATION)"

analyze-guitar-chord-mix-extra-components: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_extra_components.py
	$(PYTHON) scripts/analyze_guitar_chord_extra_components.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(EXTRA_COMPONENT_ARGS)

inspect-guitar-chord-mix-attribute-buckets: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/inspect_guitarset_attribute_buckets.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(if $(INSPECT_ARGS),$(INSPECT_ARGS),$(BUCKET_ARGS))

find-guitar-chord-mix-attribute-patterns: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") $(PATTERN_ARGS)

find-guitar-chord-mix-route-patterns:
	+$(MAKE) find-guitar-chord-mix-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

prepare-egfxset-guitar-samples: scripts/prepare_hf_guitar_chord_mix.py | $(BUILD_DIR)
	EGFXSET_GUITAR_SAMPLE_DIR="$(EGFXSET_GUITAR_SAMPLE_DIR)" EGFXSET_GUITAR_SAMPLE_LIMIT="$(EGFXSET_GUITAR_SAMPLE_LIMIT)" EGFXSET_GUITAR_MIN_EXCERPTS="$(EGFXSET_GUITAR_MIN_EXCERPTS)" EGFXSET_GUITAR_DOWNLOAD_JOBS="$(EGFXSET_GUITAR_DOWNLOAD_JOBS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(EGFXSET_GUITAR_SAMPLE_DIR)" --sources "egfxset" --limit "$(EGFXSET_GUITAR_SAMPLE_LIMIT)" --min-samples "$(EGFXSET_GUITAR_MIN_EXCERPTS)" --min-notes 1 --min-pitch-classes 1 --jobs "$(EGFXSET_GUITAR_DOWNLOAD_JOBS)"

$(EGFXSET_GUITAR_MANIFEST): scripts/prepare_hf_guitar_chord_mix.py | $(BUILD_DIR)
	EGFXSET_GUITAR_SAMPLE_DIR="$(EGFXSET_GUITAR_SAMPLE_DIR)" EGFXSET_GUITAR_SAMPLE_LIMIT="$(EGFXSET_GUITAR_SAMPLE_LIMIT)" EGFXSET_GUITAR_MIN_EXCERPTS="$(EGFXSET_GUITAR_MIN_EXCERPTS)" EGFXSET_GUITAR_DOWNLOAD_JOBS="$(EGFXSET_GUITAR_DOWNLOAD_JOBS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(EGFXSET_GUITAR_SAMPLE_DIR)" --sources "egfxset" --limit "$(EGFXSET_GUITAR_SAMPLE_LIMIT)" --min-samples "$(EGFXSET_GUITAR_MIN_EXCERPTS)" --min-notes 1 --min-pitch-classes 1 --jobs "$(EGFXSET_GUITAR_DOWNLOAD_JOBS)"

test-egfxset-guitar-samples: test-egfxset-guitar-samples-parallel

test-egfxset-guitar-samples-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-egfxset-guitar-samples scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_egfxset_guitar_samples_parallel $(MAKE) $(EGFXSET_GUITAR_TEST_MAKE_JOBS) $(EGFXSET_GUITAR_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_egfxset_guitar_shards $(PYTHON) scripts/check_guitarset_shards.py $(EGFXSET_GUITAR_SHARD_OUTS) --required-excerpts "$(EGFXSET_GUITAR_MIN_EXCERPTS)" --required-windows "$(EGFXSET_GUITAR_MIN_WINDOWS)" --min-recall-percent "$(EGFXSET_GUITAR_MIN_RECALL_PERCENT)" --min-precision-percent "$(EGFXSET_GUITAR_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(EGFXSET_GUITAR_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent "$(EGFXSET_GUITAR_MAX_CONTAMINATION_PERCENT)" --max-false-vocal-percent "$(EGFXSET_GUITAR_MAX_FALSE_VOCAL_PERCENT)" --min-chord-checks 0 --max-single-note-chord-false-percent "$(EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT)" --max-single-note-chord-false-count "$(EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_COUNT)"

test-egfxset-guitar-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(EGFXSET_GUITAR_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/egfxset_guitar_samples_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_egfxset_guitar_samples_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(EGFXSET_GUITAR_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=1 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=1 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=1 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(EGFXSET_GUITAR_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(EGFXSET_GUITAR_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(EGFXSET_GUITAR_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(EGFXSET_GUITAR_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(EGFXSET_GUITAR_ATTRIBUTE_MAKE_JOBS)" $(EGFXSET_GUITAR_ATTRIBUTE_PARTS)

$(BUILD_DIR)/egfxset_guitar_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(EGFXSET_GUITAR_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/egfxset_guitar_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(EGFXSET_GUITAR_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=1 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=1 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=1 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(EGFXSET_GUITAR_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS): $(EGFXSET_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(EGFXSET_GUITAR_MISS_ATTRIBUTE_ROWS): $(EGFXSET_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)" --misses-only > "$@"

analyze-egfxset-guitar-attributes: $(EGFXSET_GUITAR_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)" $(GUITARSET_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(EGFXSET_GUITAR_ATTRIBUTE_TSV)"

inspect-egfxset-guitar-attribute-buckets: $(EGFXSET_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)" $(BUCKET_ARGS)

find-egfxset-guitar-attribute-patterns: $(EGFXSET_GUITAR_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(EGFXSET_GUITAR_ATTRIBUTE_TSV)" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)",--bucket "$(EGFXSET_GUITAR_PATTERN_BUCKET)") $(if $(PATTERN_PROTECTED_PATHS),$(foreach path,$(PATTERN_PROTECTED_PATHS),--protected-path "$(path)"),$(EGFXSET_GUITAR_PATTERN_PROTECTED_PATH_ARGS)) $(if $(PATTERN_PROTECTED_BUCKET),--protected-bucket "$(PATTERN_PROTECTED_BUCKET)",$(EGFXSET_GUITAR_PATTERN_PROTECTED_BUCKET_ARGS)) $(PATTERN_ARGS)

find-egfxset-guitar-route-patterns:
	+$(MAKE) find-egfxset-guitar-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

prepare-gaps-guitar-samples: scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_OFFLINE="$(GAPS_GUITAR_OFFLINE)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

$(GAPS_GUITAR_MANIFEST): scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_OFFLINE="$(GAPS_GUITAR_OFFLINE)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

test-gaps-guitar-samples: test-gaps-guitar-samples-parallel

test-gaps-guitar-samples-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_gaps_guitar_samples_parallel $(MAKE) $(GAPS_GUITAR_TEST_MAKE_JOBS) $(GAPS_GUITAR_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_gaps_guitar_shards $(PYTHON) scripts/check_guitarset_shards.py $(GAPS_GUITAR_SHARD_OUTS) --required-excerpts "$(GAPS_GUITAR_MIN_EXCERPTS)" --required-windows "$(GAPS_GUITAR_MIN_WINDOWS)" --min-recall-percent "$(GAPS_GUITAR_MIN_RECALL_PERCENT)" --min-precision-percent "$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent "$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" --max-false-vocal-percent "$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" --min-chord-checks "$(GAPS_GUITAR_MIN_WINDOWS)" --min-chord-recall-percent "$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)"

test-gaps-guitar-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/gaps_guitar_samples_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_gaps_guitar_samples_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GAPS_GUITAR_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GAPS_GUITAR_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GAPS_GUITAR_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GAPS_GUITAR_ATTRIBUTE_MAKE_JOBS)" $(GAPS_GUITAR_ATTRIBUTE_PARTS)

$(BUILD_DIR)/gaps_guitar_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/gaps_guitar_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 $(GUITARSET_ATTRIBUTE_GATE_ENV) MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GAPS_GUITAR_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS): $(GAPS_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(GAPS_GUITAR_MISS_ATTRIBUTE_ROWS): $(GAPS_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_ATTRIBUTE_TSV)" --misses-only > "$@"

analyze-gaps-guitar-attributes: $(GAPS_GUITAR_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(GAPS_GUITAR_ATTRIBUTE_TSV)" $(GUITARSET_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(GAPS_GUITAR_ATTRIBUTE_TSV)"

inspect-gaps-guitar-attribute-buckets: $(GAPS_GUITAR_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_ATTRIBUTE_TSV)" $(BUCKET_ARGS)

find-gaps-guitar-attribute-patterns: $(GAPS_GUITAR_ATTRIBUTE_TSV) scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(GAPS_GUITAR_ATTRIBUTE_TSV)" $(PATTERN_ARGS)

find-gaps-guitar-route-patterns:
	+$(MAKE) find-gaps-guitar-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

analyze-gaps-guitar-misses: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GAPS_GUITAR_MISS_LOG).summary" 2> "$(GAPS_GUITAR_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GAPS_GUITAR_MISS_LOG)"

prepare-gaps-guitar-samples-full: scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_FULL_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_OFFLINE="$(GAPS_GUITAR_OFFLINE)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_FULL_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

$(GAPS_GUITAR_FULL_MANIFEST): scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_FULL_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_OFFLINE="$(GAPS_GUITAR_OFFLINE)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_FULL_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

test-gaps-guitar-samples-full: test-gaps-guitar-samples-full-parallel

test-gaps-guitar-samples-full-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples-full scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_gaps_guitar_samples_full_parallel $(MAKE) $(GAPS_GUITAR_FULL_TEST_MAKE_JOBS) $(GAPS_GUITAR_FULL_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_gaps_guitar_full_shards $(PYTHON) scripts/check_guitarset_shards.py $(GAPS_GUITAR_FULL_SHARD_OUTS) --required-excerpts "$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" --required-windows "$(GAPS_GUITAR_FULL_MIN_WINDOWS)" --min-recall-percent "$(GAPS_GUITAR_MIN_RECALL_PERCENT)" --min-precision-percent "$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent "$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" --max-false-vocal-percent "$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" --min-chord-checks "$(GAPS_GUITAR_FULL_MIN_WINDOWS)" --min-chord-recall-percent "$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)"

test-gaps-guitar-samples-full-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_FULL_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/gaps_guitar_samples_full_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_gaps_guitar_samples_full_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_FULL_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GAPS_GUITAR_FULL_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_FULL_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GAPS_GUITAR_FULL_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_MAKE_JOBS)" $(GAPS_GUITAR_FULL_ATTRIBUTE_PARTS)

$(BUILD_DIR)/gaps_guitar_full_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(GAPS_GUITAR_FULL_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/gaps_guitar_full_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_FULL_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 $(GUITARSET_ATTRIBUTE_GATE_ENV) MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GAPS_GUITAR_FULL_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS): $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(GAPS_GUITAR_FULL_MISS_ATTRIBUTE_ROWS): $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" --misses-only > "$@"

analyze-gaps-guitar-full-attributes: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(GUITARSET_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)"

inspect-gaps-guitar-full-attribute-buckets: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(BUCKET_ARGS)

find-gaps-guitar-full-attribute-patterns: $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(PATTERN_ARGS)

find-gaps-guitar-full-route-patterns:
	+$(MAKE) find-gaps-guitar-full-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

analyze-gaps-guitar-misses-full: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples-full scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_FULL_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GAPS_GUITAR_FULL_MISS_LOG).summary" 2> "$(GAPS_GUITAR_FULL_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GAPS_GUITAR_FULL_MISS_LOG)"

.PHONY: guitarset-download-samples-unlocked

.PHONY: inspect-guitarset-download

inspect-guitarset-download: scripts/inspect_guitarset_download.py
	$(PYTHON) scripts/inspect_guitarset_download.py --annotation "$(GUITARSET_ANNOTATION_ARCHIVE)" --audio "$(GUITARSET_AUDIO_ARCHIVE)"

restore-guitarset-audio-partial: scripts/restore_largest_download_partial.py
	$(PYTHON) scripts/restore_largest_download_partial.py "$(GUITARSET_AUDIO_ARCHIVE)"

test-guitarset-download-inspector: tests/test_inspect_guitarset_download.py scripts/inspect_guitarset_download.py
	$(PYTHON) tests/test_inspect_guitarset_download.py

download-guitarset-samples: scripts/run_with_lock.sh
	+$(SHELL) scripts/run_with_lock.sh "$(GUITARSET_DOWNLOAD_LOCK_DIR)" -- "$(MAKE)" guitarset-download-samples-unlocked

guitarset-download-samples-unlocked: $(GUITARSET_ANNOTATION_ARCHIVE) $(GUITARSET_AUDIO_ARCHIVE)

$(GUITARSET_ANNOTATION_ARCHIVE): FORCE scripts/check_zip_archive.py | $(BUILD_DIR)
	mkdir -p "$(GUITARSET_SOURCE_DIR)"
	if [ -s "$(GUITARSET_ANNOTATION_ARCHIVE)" ] && ! $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_ANNOTATION_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITARSET_ANNOTATION_ARCHIVE)" "$(GUITARSET_ANNOTATION_ARCHIVE).part"; fi
	if [ ! -s "$(GUITARSET_ANNOTATION_ARCHIVE)" ] && [ -s "$(GUITARSET_ANNOTATION_ARCHIVE).part" ] && $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_ANNOTATION_ARCHIVE).part" >/dev/null 2>&1; then mv "$(GUITARSET_ANNOTATION_ARCHIVE).part" "$(GUITARSET_ANNOTATION_ARCHIVE)"; fi
	if [ ! -s "$(GUITARSET_ANNOTATION_ARCHIVE)" ]; then curl -fL -C - -o "$(GUITARSET_ANNOTATION_ARCHIVE).part" "$(GUITARSET_ANNOTATION_URL)"; fi
	if [ -s "$(GUITARSET_ANNOTATION_ARCHIVE).part" ]; then $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_ANNOTATION_ARCHIVE).part"; mv "$(GUITARSET_ANNOTATION_ARCHIVE).part" "$(GUITARSET_ANNOTATION_ARCHIVE)"; fi
	$(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_ANNOTATION_ARCHIVE)"

$(GUITARSET_AUDIO_ARCHIVE): FORCE scripts/check_zip_archive.py | $(BUILD_DIR)
	mkdir -p "$(GUITARSET_SOURCE_DIR)"
	if [ -s "$(GUITARSET_AUDIO_ARCHIVE)" ] && ! $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_AUDIO_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITARSET_AUDIO_ARCHIVE)" "$(GUITARSET_AUDIO_ARCHIVE).part"; fi
	if [ ! -s "$(GUITARSET_AUDIO_ARCHIVE)" ] && [ -s "$(GUITARSET_AUDIO_ARCHIVE).part" ] && $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_AUDIO_ARCHIVE).part" >/dev/null 2>&1; then mv "$(GUITARSET_AUDIO_ARCHIVE).part" "$(GUITARSET_AUDIO_ARCHIVE)"; fi
	if [ ! -s "$(GUITARSET_AUDIO_ARCHIVE)" ]; then curl -fL -C - -o "$(GUITARSET_AUDIO_ARCHIVE).part" "$(GUITARSET_AUDIO_URL)"; fi
	if [ -s "$(GUITARSET_AUDIO_ARCHIVE).part" ]; then $(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_AUDIO_ARCHIVE).part"; mv "$(GUITARSET_AUDIO_ARCHIVE).part" "$(GUITARSET_AUDIO_ARCHIVE)"; fi
	$(PYTHON) scripts/check_zip_archive.py "$(GUITARSET_AUDIO_ARCHIVE)"

prepare-downloaded-guitarset: download-guitarset-samples
	mkdir -p "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_ANNOTATION_ARCHIVE)" "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_AUDIO_ARCHIVE)" "$(GUITARSET_ROOT)"
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py "$(GUITARSET_MANIFEST)"

$(GUITARSET_MANIFEST): tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	+$(MAKE) download-guitarset-samples
	mkdir -p "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_ANNOTATION_ARCHIVE)" "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_AUDIO_ARCHIVE)" "$(GUITARSET_ROOT)"
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py "$(GUITARSET_MANIFEST)"

test-downloaded-guitarset: test-downloaded-guitarset-parallel

test-downloaded-guitarset-parallel: $(BUILD_DIR)/analyzer_guitarset prepare-downloaded-guitarset scripts/run_with_duration.sh scripts/check_guitarset_shards.py
	+$(RUN_WITH_DURATION) analyzer_guitarset_downloaded_parallel $(MAKE) $(GUITARSET_TEST_MAKE_JOBS) $(GUITARSET_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_guitarset_downloaded_shards $(PYTHON) scripts/check_guitarset_shards.py $(GUITARSET_SHARD_OUTS) --required-excerpts 200 --required-windows 1000 --min-recall-percent "$(GUITARSET_MIN_RECALL_PERCENT)" --min-precision-percent "$(GUITARSET_MIN_PRECISION_PERCENT)" --min-guitar-recall-percent "$(GUITARSET_MIN_GUITAR_RECALL_PERCENT)" --max-contamination-percent 100 --max-false-vocal-percent 100 --min-chord-checks 1000 --min-chord-recall-percent "$(GUITARSET_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(GUITARSET_MIN_CHORD_PRECISION_PERCENT)" --min-major-minor-chord-recall-percent "$(GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT)" --min-other-chord-recall-percent "$(GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT)" --min-simple-chord-recall-percent "$(GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT)" --min-simple-major-minor-chord-recall-percent "$(GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT)" --min-simple-other-chord-recall-percent "$(GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT)"

test-downloaded-guitarset-shard-%: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITARSET_MANIFEST) scripts/run_with_duration.sh
	@out="$(BUILD_DIR)/guitarset_shard_$*.out"; $(RUN_WITH_DURATION) analyzer_guitarset_downloaded_shard_$* env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 $(GUITARSET_SHARD_GATE_ENV) MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITARSET_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_guitarset > "$$out"

analyze-guitarset-misses: $(BUILD_DIR)/analyzer_guitarset prepare-downloaded-guitarset scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=200 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1000 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITARSET_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITARSET_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITARSET_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=1000 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITARSET_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GUITARSET_MISS_LOG).summary" 2> "$(GUITARSET_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GUITARSET_MISS_LOG)"

$(GUITARSET_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(GUITARSET_MANIFEST) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GUITARSET_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GUITARSET_ATTRIBUTE_MAKE_JOBS)" $(GUITARSET_ATTRIBUTE_PARTS)

$(BUILD_DIR)/guitarset_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_guitarset $(GUITARSET_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/guitarset_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 $(GUITARSET_ATTRIBUTE_GATE_ENV) MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITARSET_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

analyze-guitarset-attributes: $(GUITARSET_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(GUITARSET_ATTRIBUTE_TSV)" $(GUITARSET_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(GUITARSET_ATTRIBUTE_TSV)"

$(GUITARSET_DETECTED_ATTRIBUTE_ROWS): $(GUITARSET_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITARSET_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(GUITARSET_MISS_ATTRIBUTE_ROWS): $(GUITARSET_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITARSET_ATTRIBUTE_TSV)" --dump-rows --misses-only > "$@"

inspect-guitarset-attribute-buckets: $(GUITARSET_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITARSET_ATTRIBUTE_TSV)" $(BUCKET_ARGS)

find-guitarset-attribute-patterns: $(GUITARSET_ATTRIBUTE_TSV) scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(GUITARSET_ATTRIBUTE_TSV)" $(PATTERN_ARGS)

find-guitarset-route-patterns:
	+$(MAKE) find-guitarset-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS)"

download-philharmonia-samples: | $(BUILD_DIR)
	mkdir -p "$(PHILHARMONIA_SOURCE_DIR)"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" "$(PHILHARMONIA_BASE_URL)/Woodwind.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" "$(PHILHARMONIA_BASE_URL)/Brass.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" "$(PHILHARMONIA_BASE_URL)/Strings.zip"

prepare-philharmonia-samples: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	PHILHARMONIA_SOURCE_DIR="$(PHILHARMONIA_SOURCE_DIR)" PHILHARMONIA_SAMPLE_DIR="$(PHILHARMONIA_SAMPLE_DIR)" PHILHARMONIA_SAMPLE_LIMIT="$(PHILHARMONIA_SAMPLE_LIMIT)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_philharmonia_samples.py --source "$(PHILHARMONIA_SOURCE_DIR)" --output "$(PHILHARMONIA_SAMPLE_DIR)" --limit "$(PHILHARMONIA_SAMPLE_LIMIT)" --min-samples "$(PHILHARMONIA_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	+$(MAKE) prepare-philharmonia-samples
	@touch "$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv"

test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_TAG := philharmonia
test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(PHILHARMONIA_SAMPLE_DIR)
test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(PHILHARMONIA_MIN_SAMPLES)
test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(PHILHARMONIA_MIN_BASS)
test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(PHILHARMONIA_MIN_GUITAR)
test-philharmonia-samples test-philharmonia-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(PHILHARMONIA_MIN_OTHER)
test-philharmonia-samples: test-philharmonia-samples-parallel

test-philharmonia-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-philharmonia-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(PHILHARMONIA_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(PHILHARMONIA_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(PHILHARMONIA_ATTRIBUTE_PARTS)

$(BUILD_DIR)/philharmonia_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_philharmonia_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(PHILHARMONIA_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PHILHARMONIA_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/philharmonia_attributes.shard-$*.out" 2> "$(BUILD_DIR)/philharmonia_attributes.shard-$*.err"

$(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS): $(PHILHARMONIA_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(PHILHARMONIA_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(PHILHARMONIA_MISS_ATTRIBUTE_ROWS): $(PHILHARMONIA_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(PHILHARMONIA_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-philharmonia-attributes: $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS) $(PHILHARMONIA_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Philharmonia attribute rows:"
	@printf '%s\n' "  $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(PHILHARMONIA_MISS_ATTRIBUTE_ROWS)"

prepare-philharmonia-samples-full: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	PHILHARMONIA_SOURCE_DIR="$(PHILHARMONIA_SOURCE_DIR)" PHILHARMONIA_SAMPLE_DIR="$(PHILHARMONIA_FULL_SAMPLE_DIR)" PHILHARMONIA_SAMPLE_LIMIT="$(PHILHARMONIA_FULL_SAMPLE_LIMIT)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_philharmonia_samples.py --source "$(PHILHARMONIA_SOURCE_DIR)" --output "$(PHILHARMONIA_FULL_SAMPLE_DIR)" --limit "$(PHILHARMONIA_FULL_SAMPLE_LIMIT)" --min-samples "$(PHILHARMONIA_FULL_MIN_SAMPLES)" --progress-every "$(PHILHARMONIA_FULL_PROGRESS_EVERY)" --ffmpeg "$(FFMPEG)"

$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	+$(MAKE) prepare-philharmonia-samples-full
	@touch "$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv"

test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_TAG := philharmonia_full
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_ROOT := $(PHILHARMONIA_FULL_SAMPLE_DIR)
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(PHILHARMONIA_FULL_MIN_SAMPLES)
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(PHILHARMONIA_FULL_MIN_BASS)
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(PHILHARMONIA_FULL_MIN_GUITAR)
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(PHILHARMONIA_FULL_MIN_OTHER)
test-philharmonia-samples-full test-philharmonia-samples-full-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(PHILHARMONIA_FULL_MAX_FAILURES)
test-philharmonia-samples-full: test-philharmonia-samples-full-parallel

test-philharmonia-samples-full-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-philharmonia-samples-full scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(PHILHARMONIA_FULL_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(PHILHARMONIA_FULL_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(PHILHARMONIA_FULL_ATTRIBUTE_PARTS)

$(BUILD_DIR)/philharmonia_full_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_philharmonia_full_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(PHILHARMONIA_FULL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PHILHARMONIA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/philharmonia_full_attributes.shard-$*.out" 2> "$(BUILD_DIR)/philharmonia_full_attributes.shard-$*.err"

$(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS): $(PHILHARMONIA_FULL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS): $(PHILHARMONIA_FULL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-philharmonia-full-attributes: $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS) $(PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Philharmonia full attribute rows:"
	@printf '%s\n' "  $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(PHILHARMONIA_FULL_MISS_ATTRIBUTE_ROWS)"

download-good-sounds-samples: $(GOOD_SOUNDS_ARCHIVE)

$(GOOD_SOUNDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GOOD_SOUNDS_SOURCE_DIR)"
	if [ -s "$(GOOD_SOUNDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GOOD_SOUNDS_ARCHIVE)" "$(GOOD_SOUNDS_ARCHIVE).part"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ] && [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)" -s "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GOOD_SOUNDS_SOURCE_DIR)" --out "good-sounds.zip.part" "$(GOOD_SOUNDS_URL)"; else curl -fL -C - -o "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_URL)"; fi; fi
	if [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null; mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null

prepare-good-sounds-samples: scripts/prepare_good_sounds_samples.py download-good-sounds-samples | $(BUILD_DIR)
	GOOD_SOUNDS_ARCHIVE="$(GOOD_SOUNDS_ARCHIVE)" GOOD_SOUNDS_SAMPLE_DIR="$(GOOD_SOUNDS_SAMPLE_DIR)" GOOD_SOUNDS_SAMPLE_LIMIT="$(GOOD_SOUNDS_SAMPLE_LIMIT)" GOOD_SOUNDS_MIN_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_good_sounds_samples.py --archive "$(GOOD_SOUNDS_ARCHIVE)" --output "$(GOOD_SOUNDS_SAMPLE_DIR)" --limit "$(GOOD_SOUNDS_SAMPLE_LIMIT)" --min-samples "$(GOOD_SOUNDS_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_TAG := good_sounds
test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(GOOD_SOUNDS_SAMPLE_DIR)
test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(GOOD_SOUNDS_MIN_SAMPLES)
test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(GOOD_SOUNDS_MIN_BASS)
test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(GOOD_SOUNDS_MIN_OTHER)
test-good-sounds-samples test-good-sounds-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(GOOD_SOUNDS_MAX_FAILURES)
test-good-sounds-samples: test-good-sounds-samples-parallel

test-good-sounds-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-good-sounds-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv: scripts/prepare_good_sounds_samples.py $(GOOD_SOUNDS_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-good-sounds-samples

$(GOOD_SOUNDS_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GOOD_SOUNDS_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(GOOD_SOUNDS_ATTRIBUTE_PARTS)

$(BUILD_DIR)/good_sounds_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_good_sounds_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GOOD_SOUNDS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/good_sounds_attributes.shard-$*.out" 2> "$(BUILD_DIR)/good_sounds_attributes.shard-$*.err"

$(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS): $(GOOD_SOUNDS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(GOOD_SOUNDS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS): $(GOOD_SOUNDS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(GOOD_SOUNDS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

.PHONY: analyze-good-sounds-attributes
analyze-good-sounds-attributes: $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS) $(GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Good Sounds attribute rows:"
	@printf '%s\n' "  $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS)"

prepare-iowa-piano-samples: scripts/prepare_iowa_piano_samples.py | $(BUILD_DIR)
	IOWA_PIANO_PAGE_URL="$(IOWA_PIANO_PAGE_URL)" IOWA_PIANO_FILE_BASE_URL="$(IOWA_PIANO_FILE_BASE_URL)" IOWA_PIANO_SOURCE_DIR="$(IOWA_PIANO_SOURCE_DIR)" IOWA_PIANO_SAMPLE_DIR="$(IOWA_PIANO_SAMPLE_DIR)" IOWA_PIANO_SAMPLE_LIMIT="$(IOWA_PIANO_SAMPLE_LIMIT)" IOWA_PIANO_MIN_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" IOWA_PIANO_DOWNLOAD_RETRIES="$(IOWA_PIANO_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_piano_samples.py --page-url "$(IOWA_PIANO_PAGE_URL)" --file-base-url "$(IOWA_PIANO_FILE_BASE_URL)" --source-dir "$(IOWA_PIANO_SOURCE_DIR)" --output "$(IOWA_PIANO_SAMPLE_DIR)" --limit "$(IOWA_PIANO_SAMPLE_LIMIT)" --min-samples "$(IOWA_PIANO_MIN_PIANO)" --download-retries "$(IOWA_PIANO_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv: scripts/prepare_iowa_piano_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-iowa-piano-samples
	@touch "$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv"

test-iowa-piano-samples test-iowa-piano-samples-parallel: REAL_NOTE_SAMPLE_TAG := iowa_piano
test-iowa-piano-samples test-iowa-piano-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IOWA_PIANO_SAMPLE_DIR)
test-iowa-piano-samples test-iowa-piano-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IOWA_PIANO_MIN_PIANO)
test-iowa-piano-samples test-iowa-piano-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO := $(IOWA_PIANO_MIN_PIANO)
test-iowa-piano-samples: test-iowa-piano-samples-parallel

test-iowa-piano-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-piano-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IOWA_PIANO_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IOWA_PIANO_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IOWA_PIANO_ATTRIBUTE_PARTS)

$(BUILD_DIR)/iowa_piano_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_piano_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/iowa_piano_attributes.shard-$*.out" 2> "$(BUILD_DIR)/iowa_piano_attributes.shard-$*.err"

$(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS): $(IOWA_PIANO_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_PIANO_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IOWA_PIANO_MISS_ATTRIBUTE_ROWS): $(IOWA_PIANO_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_PIANO_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-iowa-piano-attributes: $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS) $(IOWA_PIANO_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Iowa piano attribute rows:"
	@printf '%s\n' "  $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IOWA_PIANO_MISS_ATTRIBUTE_ROWS)"

prepare-iowa-bass-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_BASS_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_BASS_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_BASS_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_BASS_MIN_BASS)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py --spec "bass|bass|iowa-double-bass-pizz-sulE|$(IOWA_BASS_ZIP_URL)" --source-dir "$(IOWA_BASS_SOURCE_DIR)" --output "$(IOWA_BASS_SAMPLE_DIR)" --limit "$(IOWA_BASS_SAMPLE_LIMIT)" --min-samples "$(IOWA_BASS_MIN_BASS)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-bass-samples test-iowa-bass-samples-parallel: REAL_NOTE_SAMPLE_TAG := iowa_bass
test-iowa-bass-samples test-iowa-bass-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IOWA_BASS_SAMPLE_DIR)
test-iowa-bass-samples test-iowa-bass-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IOWA_BASS_MIN_BASS)
test-iowa-bass-samples test-iowa-bass-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(IOWA_BASS_MIN_BASS)
test-iowa-bass-samples: test-iowa-bass-samples-parallel

test-iowa-bass-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-bass-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

prepare-iowa-strings-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_STRINGS_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_STRINGS_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_STRINGS_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_STRINGS_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py $(IOWA_STRINGS_SPEC_ARGS) --source-dir "$(IOWA_STRINGS_SOURCE_DIR)" --output "$(IOWA_STRINGS_SAMPLE_DIR)" --limit "$(IOWA_STRINGS_SAMPLE_LIMIT)" --min-samples "$(IOWA_STRINGS_MIN_SAMPLES)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_TAG := iowa_strings
test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IOWA_STRINGS_SAMPLE_DIR)
test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IOWA_STRINGS_MIN_SAMPLES)
test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(IOWA_STRINGS_MIN_BASS)
test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(IOWA_STRINGS_MIN_OTHER)
test-iowa-strings-samples test-iowa-strings-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(IOWA_STRINGS_MAX_FAILURES)
test-iowa-strings-samples: test-iowa-strings-samples-parallel

test-iowa-strings-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-strings-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-iowa-strings-samples
	@touch "$(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv"

$(IOWA_STRINGS_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IOWA_STRINGS_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IOWA_STRINGS_ATTRIBUTE_PARTS)

$(BUILD_DIR)/iowa_strings_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_strings_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_STRINGS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_STRINGS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/iowa_strings_attributes.shard-$*.out" 2> "$(BUILD_DIR)/iowa_strings_attributes.shard-$*.err"

$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS): $(IOWA_STRINGS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_STRINGS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IOWA_STRINGS_MISS_ATTRIBUTE_ROWS): $(IOWA_STRINGS_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_STRINGS_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-iowa-strings-attributes: $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS) $(IOWA_STRINGS_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Iowa strings attribute rows:"
	@printf '%s\n' "  $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IOWA_STRINGS_MISS_ATTRIBUTE_ROWS)"

prepare-iowa-orchestra-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_ORCHESTRA_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_ORCHESTRA_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_ORCHESTRA_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_ORCHESTRA_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py $(IOWA_ORCHESTRA_SPEC_ARGS) --source-dir "$(IOWA_ORCHESTRA_SOURCE_DIR)" --output "$(IOWA_ORCHESTRA_SAMPLE_DIR)" --limit "$(IOWA_ORCHESTRA_SAMPLE_LIMIT)" --min-samples "$(IOWA_ORCHESTRA_MIN_SAMPLES)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

$(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-iowa-orchestra-samples
	@touch "$(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv"

test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_TAG := iowa_orchestra
test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IOWA_ORCHESTRA_SAMPLE_DIR)
test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IOWA_ORCHESTRA_MIN_SAMPLES)
test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(IOWA_ORCHESTRA_MIN_BASS)
test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(IOWA_ORCHESTRA_MIN_OTHER)
test-iowa-orchestra-samples test-iowa-orchestra-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(IOWA_ORCHESTRA_MAX_FAILURES)
test-iowa-orchestra-samples: test-iowa-orchestra-samples-parallel

test-iowa-orchestra-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-orchestra-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IOWA_ORCHESTRA_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IOWA_ORCHESTRA_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IOWA_ORCHESTRA_ATTRIBUTE_PARTS)

$(BUILD_DIR)/iowa_orchestra_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_orchestra_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_ORCHESTRA_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_ORCHESTRA_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/iowa_orchestra_attributes.shard-$*.out" 2> "$(BUILD_DIR)/iowa_orchestra_attributes.shard-$*.err"

$(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS): $(IOWA_ORCHESTRA_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_ORCHESTRA_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS): $(IOWA_ORCHESTRA_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_ORCHESTRA_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-iowa-orchestra-attributes: $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS) $(IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Iowa orchestra attribute rows:"
	@printf '%s\n' "  $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IOWA_ORCHESTRA_MISS_ATTRIBUTE_ROWS)"

prepare-iowa-orchestra-full-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_ORCHESTRA_FULL_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_TIMEOUT="$(IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES)" IOWA_ZIP_MAX_DOWNLOAD_FAILURES="$(IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES)" IOWA_ZIP_MAX_ZIPS_PER_PAGE="$(IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py $(IOWA_ORCHESTRA_FULL_SPEC_ARGS) $(IOWA_ORCHESTRA_FULL_PAGE_ARGS) --source-dir "$(IOWA_ORCHESTRA_FULL_SOURCE_DIR)" --output "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" --limit "$(IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT)" --min-samples "$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" --max-zips-per-page "$(IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE)" --download-timeout "$(IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT)" --download-retries "$(IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES)" --max-download-failures "$(IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-iowa-orchestra-full-samples
	@touch "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv"

test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_TAG := iowa_orchestra_full
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(IOWA_ORCHESTRA_FULL_MIN_BASS)
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(IOWA_ORCHESTRA_FULL_MIN_OTHER)
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(IOWA_ORCHESTRA_FULL_MAX_FAILURES)
test-iowa-orchestra-full-samples test-iowa-orchestra-full-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURE_LINES := 120
test-iowa-orchestra-full-samples: test-iowa-orchestra-full-samples-parallel

test-iowa-orchestra-full-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-orchestra-full-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_PARTS)

$(BUILD_DIR)/iowa_orchestra_full_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_orchestra_full_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/iowa_orchestra_full_attributes.shard-$*.out" 2> "$(BUILD_DIR)/iowa_orchestra_full_attributes.shard-$*.err"

$(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS): $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS): $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-iowa-orchestra-full-attributes: $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS) $(IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Iowa orchestra full attribute rows:"
	@printf '%s\n' "  $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IOWA_ORCHESTRA_FULL_MISS_ATTRIBUTE_ROWS)"

download-idmt-bass-lines-samples: $(IDMT_BASS_LINES_ARCHIVE)

$(IDMT_BASS_LINES_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(IDMT_BASS_LINES_SOURCE_DIR)"
	if [ ! -s "$(IDMT_BASS_LINES_ARCHIVE)" ] || ! $(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null 2>&1; then curl -fL -C - -o "$(IDMT_BASS_LINES_ARCHIVE)" "$(IDMT_BASS_LINES_URL)"; fi
	$(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null

prepare-idmt-bass-lines-samples: scripts/prepare_idmt_bass_lines_samples.py download-idmt-bass-lines-samples | $(BUILD_DIR)
	IDMT_BASS_LINES_ARCHIVE="$(IDMT_BASS_LINES_ARCHIVE)" IDMT_BASS_LINES_SAMPLE_DIR="$(IDMT_BASS_LINES_SAMPLE_DIR)" IDMT_BASS_LINES_SAMPLE_LIMIT="$(IDMT_BASS_LINES_SAMPLE_LIMIT)" IDMT_BASS_LINES_MIN_BASS="$(IDMT_BASS_LINES_MIN_BASS)" IDMT_BASS_LINES_EXPRESSIONS="$(IDMT_BASS_LINES_EXPRESSIONS)" IDMT_BASS_LINES_MIN_NOTE_DURATION="$(IDMT_BASS_LINES_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_idmt_bass_lines_samples.py --archive "$(IDMT_BASS_LINES_ARCHIVE)" --output "$(IDMT_BASS_LINES_SAMPLE_DIR)" --limit "$(IDMT_BASS_LINES_SAMPLE_LIMIT)" --min-samples "$(IDMT_BASS_LINES_MIN_BASS)" --expressions "$(IDMT_BASS_LINES_EXPRESSIONS)" --min-note-duration "$(IDMT_BASS_LINES_MIN_NOTE_DURATION)"

$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv: scripts/prepare_idmt_bass_lines_samples.py $(IDMT_BASS_LINES_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-idmt-bass-lines-samples
	@touch "$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv"

test-idmt-bass-lines-samples test-idmt-bass-lines-samples-parallel: REAL_NOTE_SAMPLE_TAG := idmt_bass_lines
test-idmt-bass-lines-samples test-idmt-bass-lines-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IDMT_BASS_LINES_SAMPLE_DIR)
test-idmt-bass-lines-samples test-idmt-bass-lines-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IDMT_BASS_LINES_MIN_BASS)
test-idmt-bass-lines-samples test-idmt-bass-lines-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(IDMT_BASS_LINES_MIN_BASS)
test-idmt-bass-lines-samples test-idmt-bass-lines-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(IDMT_BASS_LINES_MAX_FAILURES)
test-idmt-bass-lines-samples: test-idmt-bass-lines-samples-parallel

test-idmt-bass-lines-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-idmt-bass-lines-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IDMT_BASS_LINES_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IDMT_BASS_LINES_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IDMT_BASS_LINES_ATTRIBUTE_PARTS)

$(BUILD_DIR)/idmt_bass_lines_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_idmt_bass_lines_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IDMT_BASS_LINES_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IDMT_BASS_LINES_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/idmt_bass_lines_attributes.shard-$*.out" 2> "$(BUILD_DIR)/idmt_bass_lines_attributes.shard-$*.err"

$(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS): $(IDMT_BASS_LINES_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IDMT_BASS_LINES_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS): $(IDMT_BASS_LINES_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IDMT_BASS_LINES_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-idmt-bass-lines-attributes: $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS) $(IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "IDMT bass lines attribute rows:"
	@printf '%s\n' "  $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IDMT_BASS_LINES_MISS_ATTRIBUTE_ROWS)"

download-idmt-guitar-samples: $(IDMT_GUITAR_ARCHIVE)

$(IDMT_GUITAR_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(IDMT_GUITAR_SOURCE_DIR)"
	if [ -s "$(IDMT_GUITAR_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(IDMT_GUITAR_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(IDMT_GUITAR_ARCHIVE)" "$(IDMT_GUITAR_ARCHIVE).part"; fi
	if [ ! -s "$(IDMT_GUITAR_ARCHIVE)" ] && [ -s "$(IDMT_GUITAR_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(IDMT_GUITAR_ARCHIVE).part" >/dev/null 2>&1; then mv "$(IDMT_GUITAR_ARCHIVE).part" "$(IDMT_GUITAR_ARCHIVE)"; fi
	if [ ! -s "$(IDMT_GUITAR_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(IDMT_GUITAR_DOWNLOAD_CONNECTIONS)" -s "$(IDMT_GUITAR_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(IDMT_GUITAR_SOURCE_DIR)" --out "IDMT-SMT-GUITAR_V2.zip.part" "$(IDMT_GUITAR_URL)"; else curl -fL -C - -o "$(IDMT_GUITAR_ARCHIVE).part" "$(IDMT_GUITAR_URL)"; fi; fi
	if [ -s "$(IDMT_GUITAR_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(IDMT_GUITAR_ARCHIVE).part" >/dev/null; mv "$(IDMT_GUITAR_ARCHIVE).part" "$(IDMT_GUITAR_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(IDMT_GUITAR_ARCHIVE)" >/dev/null

prepare-idmt-guitar-samples: scripts/prepare_idmt_guitar_samples.py download-idmt-guitar-samples | $(BUILD_DIR)
	IDMT_GUITAR_ARCHIVE="$(IDMT_GUITAR_ARCHIVE)" IDMT_GUITAR_SAMPLE_DIR="$(IDMT_GUITAR_SAMPLE_DIR)" IDMT_GUITAR_SAMPLE_LIMIT="$(IDMT_GUITAR_SAMPLE_LIMIT)" IDMT_GUITAR_MIN_GUITAR="$(IDMT_GUITAR_MIN_GUITAR)" IDMT_GUITAR_EXPRESSIONS="$(IDMT_GUITAR_EXPRESSIONS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_idmt_guitar_samples.py --archive "$(IDMT_GUITAR_ARCHIVE)" --output "$(IDMT_GUITAR_SAMPLE_DIR)" --limit "$(IDMT_GUITAR_SAMPLE_LIMIT)" --min-samples "$(IDMT_GUITAR_MIN_GUITAR)" --expressions "$(IDMT_GUITAR_EXPRESSIONS)" --ffmpeg "$(FFMPEG)"

$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv: scripts/prepare_idmt_guitar_samples.py $(IDMT_GUITAR_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-idmt-guitar-samples
	@touch "$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv"

test-idmt-guitar-samples test-idmt-guitar-samples-parallel: REAL_NOTE_SAMPLE_TAG := idmt_guitar
test-idmt-guitar-samples test-idmt-guitar-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(IDMT_GUITAR_SAMPLE_DIR)
test-idmt-guitar-samples test-idmt-guitar-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(IDMT_GUITAR_MIN_GUITAR)
test-idmt-guitar-samples test-idmt-guitar-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(IDMT_GUITAR_MIN_GUITAR)
test-idmt-guitar-samples test-idmt-guitar-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(IDMT_GUITAR_MAX_FAILURES)
test-idmt-guitar-samples: test-idmt-guitar-samples-parallel

test-idmt-guitar-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-idmt-guitar-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(IDMT_GUITAR_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IDMT_GUITAR_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IDMT_GUITAR_ATTRIBUTE_PARTS)

$(BUILD_DIR)/idmt_guitar_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_idmt_guitar_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IDMT_GUITAR_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IDMT_GUITAR_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/idmt_guitar_attributes.shard-$*.out" 2> "$(BUILD_DIR)/idmt_guitar_attributes.shard-$*.err"

$(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS): $(IDMT_GUITAR_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IDMT_GUITAR_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(IDMT_GUITAR_MISS_ATTRIBUTE_ROWS): $(IDMT_GUITAR_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IDMT_GUITAR_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-idmt-guitar-attributes: $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(IDMT_GUITAR_MISS_ATTRIBUTE_ROWS) scripts/summarize_real_note_attributes.py
	@printf '%s\n' "IDMT guitar attribute rows:"
	@printf '%s\n' "  $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(IDMT_GUITAR_MISS_ATTRIBUTE_ROWS)"
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(IDMT_GUITAR_ATTRIBUTE_TSV)"

download-tinysol-samples: $(TINYSOL_METADATA_PATH) $(TINYSOL_ARCHIVE)

$(TINYSOL_METADATA_PATH): FORCE | $(BUILD_DIR)
	mkdir -p "$(TINYSOL_SOURCE_DIR)"
	if [ ! -s "$(TINYSOL_METADATA_PATH)" ] || ! head -n 1 "$(TINYSOL_METADATA_PATH)" | grep -q "Pitch ID"; then rm -f "$(TINYSOL_METADATA_PATH)"; curl -fL -C - -o "$(TINYSOL_METADATA_PATH)" "$(TINYSOL_METADATA_URL)"; fi
	head -n 1 "$(TINYSOL_METADATA_PATH)" | grep -q "Pitch ID"

$(TINYSOL_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(TINYSOL_SOURCE_DIR)"
	if [ -s "$(TINYSOL_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(TINYSOL_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(TINYSOL_ARCHIVE)" "$(TINYSOL_ARCHIVE).part"; fi
	if [ ! -s "$(TINYSOL_ARCHIVE)" ] && [ -s "$(TINYSOL_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(TINYSOL_ARCHIVE).part" >/dev/null 2>&1; then mv "$(TINYSOL_ARCHIVE).part" "$(TINYSOL_ARCHIVE)"; fi
	if [ ! -s "$(TINYSOL_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(TINYSOL_DOWNLOAD_CONNECTIONS)" -s "$(TINYSOL_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(TINYSOL_SOURCE_DIR)" --out "TinySOL.zip.part" "$(TINYSOL_ARCHIVE_URL)"; else curl -fL -C - -o "$(TINYSOL_ARCHIVE).part" "$(TINYSOL_ARCHIVE_URL)"; fi; fi
	if [ ! -s "$(TINYSOL_ARCHIVE)" ]; then $(PYTHON) -m zipfile -t "$(TINYSOL_ARCHIVE).part" >/dev/null && mv "$(TINYSOL_ARCHIVE).part" "$(TINYSOL_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(TINYSOL_ARCHIVE)" >/dev/null

prepare-tinysol-samples: scripts/prepare_tinysol_samples.py download-tinysol-samples | $(BUILD_DIR)
	TINYSOL_METADATA_PATH="$(TINYSOL_METADATA_PATH)" TINYSOL_ARCHIVE="$(TINYSOL_ARCHIVE)" TINYSOL_SAMPLE_DIR="$(TINYSOL_SAMPLE_DIR)" TINYSOL_SAMPLE_LIMIT="$(TINYSOL_SAMPLE_LIMIT)" TINYSOL_MIN_SAMPLES="$(TINYSOL_MIN_SAMPLES)" $(PYTHON) scripts/prepare_tinysol_samples.py --metadata "$(TINYSOL_METADATA_PATH)" --archive "$(TINYSOL_ARCHIVE)" --output "$(TINYSOL_SAMPLE_DIR)" --limit "$(TINYSOL_SAMPLE_LIMIT)" --min-samples "$(TINYSOL_MIN_SAMPLES)"

$(TINYSOL_SAMPLE_DIR)/manifest.tsv: scripts/prepare_tinysol_samples.py $(TINYSOL_METADATA_PATH) $(TINYSOL_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-tinysol-samples
	@touch "$(TINYSOL_SAMPLE_DIR)/manifest.tsv"

test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_TAG := tinysol
test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(TINYSOL_SAMPLE_DIR)
test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(TINYSOL_MIN_SAMPLES)
test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(TINYSOL_MIN_BASS)
test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO := $(TINYSOL_MIN_PIANO)
test-tinysol-samples test-tinysol-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(TINYSOL_MIN_OTHER)
test-tinysol-samples: test-tinysol-samples-parallel

test-tinysol-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-tinysol-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(TINYSOL_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(TINYSOL_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(TINYSOL_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(TINYSOL_ATTRIBUTE_PARTS)

$(BUILD_DIR)/tinysol_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(TINYSOL_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_tinysol_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(TINYSOL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(TINYSOL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/tinysol_attributes.shard-$*.out" 2> "$(BUILD_DIR)/tinysol_attributes.shard-$*.err"

$(TINYSOL_DETECTED_ATTRIBUTE_ROWS): $(TINYSOL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(TINYSOL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(TINYSOL_MISS_ATTRIBUTE_ROWS): $(TINYSOL_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(TINYSOL_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-tinysol-attributes: $(TINYSOL_DETECTED_ATTRIBUTE_ROWS) $(TINYSOL_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "TinySOL attribute rows:"
	@printf '%s\n' "  $(TINYSOL_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(TINYSOL_MISS_ATTRIBUTE_ROWS)"

download-vocadito-samples: $(VOCADITO_ARCHIVE)

$(VOCADITO_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(VOCADITO_SOURCE_DIR)"
	if [ -s "$(VOCADITO_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(VOCADITO_ARCHIVE)" "$(VOCADITO_ARCHIVE).part"; fi
	if [ ! -s "$(VOCADITO_ARCHIVE)" ] && [ -s "$(VOCADITO_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE).part" >/dev/null 2>&1; then mv "$(VOCADITO_ARCHIVE).part" "$(VOCADITO_ARCHIVE)"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(VOCADITO_ARCHIVE)" ]; then if command -v aria2c >/dev/null 2>&1; then aria2c --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(VOCADITO_DOWNLOAD_CONNECTIONS)" --split="$(VOCADITO_DOWNLOAD_CONNECTIONS)" --min-split-size=1M --dir "$(VOCADITO_SOURCE_DIR)" --out "vocadito.zip.part" "$(VOCADITO_URL)"; else curl -fL -C - -o "$(VOCADITO_ARCHIVE).part" "$(VOCADITO_URL)"; fi; fi
	if [ -s "$(VOCADITO_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE).part" >/dev/null; mv -f "$(VOCADITO_ARCHIVE).part" "$(VOCADITO_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE)" >/dev/null

prepare-vocadito-samples: scripts/prepare_vocadito_samples.py download-vocadito-samples | $(BUILD_DIR)
	VOCADITO_ARCHIVE="$(VOCADITO_ARCHIVE)" VOCADITO_SAMPLE_DIR="$(VOCADITO_SAMPLE_DIR)" VOCADITO_SAMPLE_LIMIT="$(VOCADITO_SAMPLE_LIMIT)" VOCADITO_MIN_VOCALS="$(VOCADITO_MIN_VOCALS)" VOCADITO_ANNOTATOR="$(VOCADITO_ANNOTATOR)" VOCADITO_MAX_CENTS="$(VOCADITO_MAX_CENTS)" VOCADITO_MIN_NOTE_DURATION="$(VOCADITO_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_vocadito_samples.py --archive "$(VOCADITO_ARCHIVE)" --output "$(VOCADITO_SAMPLE_DIR)" --limit "$(VOCADITO_SAMPLE_LIMIT)" --min-samples "$(VOCADITO_MIN_VOCALS)" --annotator "$(VOCADITO_ANNOTATOR)" --max-cents "$(VOCADITO_MAX_CENTS)" --min-note-duration "$(VOCADITO_MIN_NOTE_DURATION)"

$(VOCADITO_SAMPLE_DIR)/manifest.tsv: scripts/prepare_vocadito_samples.py $(VOCADITO_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-vocadito-samples
	@touch "$(VOCADITO_SAMPLE_DIR)/manifest.tsv"

test-vocadito-samples test-vocadito-samples-parallel: REAL_NOTE_SAMPLE_TAG := vocadito
test-vocadito-samples test-vocadito-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(VOCADITO_SAMPLE_DIR)
test-vocadito-samples test-vocadito-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(VOCADITO_MIN_VOCALS)
test-vocadito-samples test-vocadito-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS := $(VOCADITO_MIN_VOCALS)
test-vocadito-samples test-vocadito-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(VOCADITO_MAX_FAILURES)
test-vocadito-samples: test-vocadito-samples-parallel

test-vocadito-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(VOCADITO_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(VOCADITO_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(VOCADITO_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(VOCADITO_ATTRIBUTE_PARTS)

$(BUILD_DIR)/vocadito_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(VOCADITO_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_vocadito_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCADITO_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCADITO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocadito_attributes.shard-$*.out" 2> "$(BUILD_DIR)/vocadito_attributes.shard-$*.err"

$(VOCADITO_DETECTED_ATTRIBUTE_ROWS): $(VOCADITO_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(VOCADITO_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(VOCADITO_MISS_ATTRIBUTE_ROWS): $(VOCADITO_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(VOCADITO_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-vocadito-attributes: $(VOCADITO_DETECTED_ATTRIBUTE_ROWS) $(VOCADITO_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "Vocadito attribute rows:"
	@printf '%s\n' "  $(VOCADITO_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(VOCADITO_MISS_ATTRIBUTE_ROWS)"

test-vocadito-samples-full-mix:
	+$(MAKE) test-vocadito-samples-full-mix-parallel

test-vocadito-samples-full-mix-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_full_mix_shards.py
	+$(RUN_WITH_DURATION) analyzer_vocadito_samples_full_mix_parallel $(SHELL) scripts/run_with_lock.sh "$(VOCADITO_FULL_MIX_LOCK_DIR)" -- "$(MAKE)" test-vocadito-samples-full-mix-parallel-unlocked

test-vocadito-samples-full-mix-parallel-unlocked: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/run_with_duration.sh scripts/check_real_note_full_mix_shards.py
	+$(MAKE) $(VOCADITO_FULL_MIX_TEST_MAKE_JOBS) $(VOCADITO_FULL_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_vocadito_full_mix_shards $(PYTHON) scripts/check_real_note_full_mix_shards.py --min-any-hit-percent "$(VOCADITO_FULL_MIX_MIN_ANY_HIT_PERCENT)" --min-expected-row-percent "$(VOCADITO_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" --min-first-row-percent "$(VOCADITO_FULL_MIX_MIN_FIRST_ROW_PERCENT)" --min-visual-row-percent "$(VOCADITO_FULL_MIX_MIN_VISUAL_ROW_PERCENT)" --bass-min-expected-row-percent 0 --guitar-min-expected-row-percent 0 --piano-min-expected-row-percent 0 --vocals-min-expected-row-percent "$(VOCADITO_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" --other-min-expected-row-percent 0 --bass-min-first-row-percent 0 --guitar-min-first-row-percent 0 --piano-min-first-row-percent 0 --vocals-min-first-row-percent "$(VOCADITO_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT)" --other-min-first-row-percent 0 --bass-min-visual-row-percent 0 --guitar-min-visual-row-percent 0 --piano-min-visual-row-percent 0 --vocals-min-visual-row-percent "$(VOCADITO_FULL_MIX_MIN_VOCALS_VISUAL_ROW_PERCENT)" --other-min-visual-row-percent 0 --max-drum-active-percent "$(VOCADITO_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" $(VOCADITO_FULL_MIX_SHARD_OUTS)

test-vocadito-samples-full-mix-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_vocadito_samples_full_mix_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(VOCADITO_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCADITO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCADITO_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=20 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocadito_full_mix_shard_$*.out" 2> "$(BUILD_DIR)/vocadito_full_mix_shard_$*.err"

.PHONY: vocalset-download-samples-unlocked

download-vocalset-samples: scripts/run_with_lock.sh
	+$(SHELL) scripts/run_with_lock.sh "$(VOCALSET_DOWNLOAD_LOCK_DIR)" -- "$(MAKE)" vocalset-download-samples-unlocked

vocalset-download-samples-unlocked: $(VOCALSET_ARCHIVE)

$(VOCALSET_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(VOCALSET_SOURCE_DIR)"
	if [ -s "$(VOCALSET_ARCHIVE)" ] && { ! $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE)" >/dev/null 2>&1 || ! printf '%s  %s\n' "$(VOCALSET_ARCHIVE_MD5)" "$(VOCALSET_ARCHIVE)" | md5sum -c - >/dev/null 2>&1; }; then mv -f "$(VOCALSET_ARCHIVE)" "$(VOCALSET_ARCHIVE).part"; fi
	if [ -s "$(VOCALSET_ARCHIVE).part" ] && [ "$$(wc -c < "$(VOCALSET_ARCHIVE).part")" = "$(VOCALSET_ARCHIVE_BYTES)" ] && ! printf '%s  %s\n' "$(VOCALSET_ARCHIVE_MD5)" "$(VOCALSET_ARCHIVE).part" | md5sum -c - >/dev/null 2>&1; then rm -f "$(VOCALSET_ARCHIVE).part"; fi
	if [ ! -s "$(VOCALSET_ARCHIVE)" ] && [ -s "$(VOCALSET_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE).part" >/dev/null 2>&1; then mv "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_ARCHIVE)"; fi
	if [ ! -s "$(VOCALSET_ARCHIVE)" ]; then if command -v aria2c >/dev/null 2>&1; then aria2c --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(VOCALSET_DOWNLOAD_CONNECTIONS)" --split="$(VOCALSET_DOWNLOAD_CONNECTIONS)" --min-split-size=1M --dir "$(VOCALSET_SOURCE_DIR)" --out "VocalSet.zip.part" "$(VOCALSET_URL)"; else curl -fL -C - -o "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_URL)"; fi; fi
	if [ -s "$(VOCALSET_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE).part" >/dev/null && printf '%s  %s\n' "$(VOCALSET_ARCHIVE_MD5)" "$(VOCALSET_ARCHIVE).part" | md5sum -c - >/dev/null && mv "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE)" >/dev/null

prepare-vocalset-samples: scripts/prepare_vocalset_samples.py download-vocalset-samples | $(BUILD_DIR)
	VOCALSET_ARCHIVE="$(VOCALSET_ARCHIVE)" VOCALSET_SAMPLE_DIR="$(VOCALSET_SAMPLE_DIR)" VOCALSET_SAMPLE_LIMIT="$(VOCALSET_SAMPLE_LIMIT)" VOCALSET_MIN_VOCALS="$(VOCALSET_MIN_VOCALS)" VOCALSET_ALLOWED_TECHNIQUES="$(VOCALSET_ALLOWED_TECHNIQUES)" VOCALSET_MAX_CENTS="$(VOCALSET_MAX_CENTS)" VOCALSET_MIN_NOTE_DURATION="$(VOCALSET_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_vocalset_samples.py --archive "$(VOCALSET_ARCHIVE)" --output "$(VOCALSET_SAMPLE_DIR)" --limit "$(VOCALSET_SAMPLE_LIMIT)" --min-samples "$(VOCALSET_MIN_VOCALS)" --allowed-techniques "$(VOCALSET_ALLOWED_TECHNIQUES)" --max-cents "$(VOCALSET_MAX_CENTS)" --min-note-duration "$(VOCALSET_MIN_NOTE_DURATION)"

$(VOCALSET_SAMPLE_DIR)/manifest.tsv: scripts/prepare_vocalset_samples.py $(VOCALSET_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-vocalset-samples
	@touch "$(VOCALSET_SAMPLE_DIR)/manifest.tsv"

test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_TAG := vocalset
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(VOCALSET_SAMPLE_DIR)
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(VOCALSET_MIN_VOCALS)
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS := $(VOCALSET_MIN_VOCALS)
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT := $(VOCALSET_MIN_VOCALS_HIT_PERCENT)
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(VOCALSET_MAX_FAILURES)
test-vocalset-samples test-vocalset-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURE_LINES := 120
test-vocalset-samples: test-vocalset-samples-parallel

test-vocalset-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocalset-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

test-vocalset-samples-full-mix:
	+$(MAKE) test-vocalset-samples-full-mix-parallel

test-vocalset-samples-full-mix-parallel: $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_full_mix_shards.py
	+$(RUN_WITH_DURATION) analyzer_vocalset_samples_full_mix_parallel $(SHELL) scripts/run_with_lock.sh "$(VOCALSET_FULL_MIX_LOCK_DIR)" -- "$(MAKE)" test-vocalset-samples-full-mix-parallel-unlocked

test-vocalset-samples-full-mix-parallel-unlocked: $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh scripts/check_real_note_full_mix_shards.py
	+$(MAKE) $(VOCALSET_FULL_MIX_TEST_MAKE_JOBS) $(VOCALSET_FULL_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_vocalset_full_mix_shards $(PYTHON) scripts/check_real_note_full_mix_shards.py --min-any-hit-percent "$(VOCALSET_FULL_MIX_MIN_ANY_HIT_PERCENT)" --min-expected-row-percent "$(VOCALSET_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" --min-first-row-percent "$(VOCALSET_FULL_MIX_MIN_FIRST_ROW_PERCENT)" --min-visual-row-percent "$(VOCALSET_FULL_MIX_MIN_VISUAL_ROW_PERCENT)" --bass-min-expected-row-percent 0 --guitar-min-expected-row-percent 0 --piano-min-expected-row-percent 0 --vocals-min-expected-row-percent "$(VOCALSET_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" --other-min-expected-row-percent 0 --bass-min-first-row-percent 0 --guitar-min-first-row-percent 0 --piano-min-first-row-percent 0 --vocals-min-first-row-percent "$(VOCALSET_FULL_MIX_MIN_VOCALS_FIRST_ROW_PERCENT)" --other-min-first-row-percent 0 --bass-min-visual-row-percent 0 --guitar-min-visual-row-percent 0 --piano-min-visual-row-percent 0 --vocals-min-visual-row-percent "$(VOCALSET_FULL_MIX_MIN_VOCALS_VISUAL_ROW_PERCENT)" --other-min-visual-row-percent 0 --max-drum-active-percent "$(VOCALSET_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" $(VOCALSET_FULL_MIX_SHARD_OUTS)

test-vocalset-samples-full-mix-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_vocalset_samples_full_mix_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(VOCALSET_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=20 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocalset_full_mix_shard_$*.out" 2> "$(BUILD_DIR)/vocalset_full_mix_shard_$*.err"

$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(VOCALSET_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(VOCALSET_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/vocalset_full_mix_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocalset-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(VOCALSET_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=20 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocalset_full_mix_attributes.shard-$*.out"

.PHONY: analyze-vocalset-full-mix-attributes analyze-vocalset-expanded-full-mix-attributes find-vocalset-full-mix-row-confusion-patterns find-vocalset-full-mix-visual-row-confusion-patterns find-vocalset-full-mix-ownership-patterns find-vocalset-full-mix-broad-vocal-ownership-patterns

analyze-vocalset-full-mix-attributes: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)"

analyze-vocalset-expanded-full-mix-attributes: scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(VOCALSET_EXPANDED_FULL_MIX_ATTRIBUTE_TSV)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(VOCALSET_EXPANDED_FULL_MIX_ATTRIBUTE_TSV)"

find-vocalset-full-mix-row-confusion-patterns: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-vocalset-full-mix-visual-row-confusion-patterns: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-vocalset-full-mix-ownership-patterns: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-vocalset-full-mix-broad-vocal-ownership-patterns: $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS) --bucket "ownership_miss:vocals/*->*" --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS))

$(VOCALSET_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(VOCALSET_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(VOCALSET_ATTRIBUTE_PARTS)

$(BUILD_DIR)/vocalset_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(VOCALSET_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_vocalset_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/vocalset_attributes.shard-$*.out" 2> "$(BUILD_DIR)/vocalset_attributes.shard-$*.err"

$(VOCALSET_DETECTED_ATTRIBUTE_ROWS): $(VOCALSET_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(VOCALSET_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug > "$@"

$(VOCALSET_MISS_ATTRIBUTE_ROWS): $(VOCALSET_ATTRIBUTE_TSV) scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(VOCALSET_ATTRIBUTE_TSV)" --dump-rows --include-empty-debug --status miss > "$@"

analyze-vocalset-attributes: $(VOCALSET_DETECTED_ATTRIBUTE_ROWS) $(VOCALSET_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "VocalSet attribute rows:"
	@printf '%s\n' "  $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(VOCALSET_MISS_ATTRIBUTE_ROWS)"
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(VOCALSET_DETECTED_ATTRIBUTE_ROWS)"

DRUM_REAL_WORLD_SAMPLE_TARGETS := test-hf-drum-kit-samples-parallel test-idmt-drums-samples-parallel test-mdb-drums-samples-parallel test-star-drums-samples-parallel test-drum-samples-optional test-drum-samples-spread-optional
DRUM_REAL_WORLD_SAMPLE_FULL_TARGETS := $(DRUM_REAL_WORLD_SAMPLE_TARGETS) test-drum-machine-samples-optional test-drum-samples-full-parallel-optional
REAL_WORLD_SAMPLE_TARGETS := test-real-note-samples-parallel test-real-note-samples-full-mix-parallel test-guitar-fretboard-note-samples-parallel test-hf-drum-kit-samples-parallel test-idmt-drums-samples-parallel test-mdb-drums-samples-parallel test-star-drums-samples-parallel test-downloaded-guitarset-parallel test-philharmonia-samples-parallel test-iowa-piano-samples-parallel test-iowa-bass-samples-parallel test-idmt-bass-lines-samples-parallel test-vocadito-samples-parallel test-vocadito-samples-full-mix-parallel
REAL_WORLD_SAMPLE_FULL_TARGETS := $(REAL_WORLD_SAMPLE_TARGETS) test-guitar-techs-samples-parallel test-guitar-techs-chord-samples-parallel test-guitar-chord-mix-samples-parallel test-egfxset-guitar-samples-parallel test-gaps-guitar-samples-parallel test-idmt-guitar-samples-parallel test-iowa-strings-samples-parallel test-iowa-orchestra-samples-parallel test-iowa-orchestra-full-samples-parallel test-philharmonia-samples-full-parallel test-tinysol-samples-parallel test-drum-machine-samples-optional test-drum-samples-full-parallel-optional test-good-sounds-samples-optional test-medley-solos-samples-optional test-maps-piano-samples-optional test-maps-piano-note-samples-optional test-bach10-mf0-synth-samples-optional test-vocalset-samples-optional test-vocalset-samples-full-mix-optional test-configured-real-world-samples
REAL_WORLD_SAMPLE_MAX_BASE_TARGETS := $(filter-out test-iowa-piano-samples-parallel,$(REAL_WORLD_SAMPLE_TARGETS))
REAL_WORLD_SAMPLE_MAX_TARGETS := $(REAL_WORLD_SAMPLE_MAX_BASE_TARGETS) test-guitar-techs-samples-parallel test-guitar-techs-chord-samples-parallel test-guitar-chord-mix-samples-parallel test-egfxset-guitar-samples-parallel test-gaps-guitar-samples-full-parallel test-idmt-guitar-samples-parallel test-iowa-piano-samples-max test-iowa-strings-samples-parallel test-iowa-orchestra-samples-parallel test-iowa-orchestra-full-samples-max test-philharmonia-samples-full-parallel test-tinysol-samples-parallel test-good-sounds-samples-max test-medley-solos-samples-max test-maps-piano-samples-max test-maps-piano-note-samples-max test-bach10-mf0-synth-samples-parallel test-vocalset-samples-parallel test-drum-machine-samples-optional test-drum-samples-full-parallel-optional test-configured-real-world-samples
DETECTOR_SAMPLE_REGRESSION_TARGETS := test-analyzer-cases test-real-note-samples-parallel test-real-note-samples-full-mix-detector-parallel test-real-note-visual-strength test-guitar-fretboard-note-samples-parallel test-guitar-techs-samples-parallel test-guitar-techs-chord-samples-parallel test-guitar-chord-mix-samples-parallel test-egfxset-guitar-samples-parallel test-gaps-guitar-samples-parallel test-downloaded-guitarset-parallel $(DRUM_REAL_WORLD_SAMPLE_TARGETS) test-drum-machine-samples-optional test-idmt-bass-lines-samples-optional test-idmt-guitar-samples-optional test-philharmonia-samples-parallel test-philharmonia-samples-full-parallel test-iowa-piano-samples-parallel test-iowa-bass-samples-parallel test-iowa-strings-samples-parallel test-iowa-orchestra-samples-parallel test-maps-piano-samples-optional test-maps-piano-note-samples-optional test-bach10-mf0-synth-samples-optional test-tinysol-samples-parallel test-vocadito-samples-parallel test-vocadito-samples-full-mix-parallel test-vocalset-samples-optional test-vocalset-samples-full-mix-optional test-instrument-samples-parallel test-drum-samples-full-parallel-optional
DETECTOR_SAMPLE_FULL_REGRESSION_TARGETS := test-analyzer-cases test-instrument-samples-parallel test-real-world-samples-max-parallel
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS :=
ifneq ($(wildcard $(IDMT_BASS_LINES_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IDMT_BASS_LINES_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(IDMT_GUITAR_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IDMT_GUITAR_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(and $(wildcard $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)),$(wildcard $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE))),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(GOOD_SOUNDS_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(and $(wildcard $(TINYSOL_METADATA_PATH)),$(wildcard $(TINYSOL_ARCHIVE))),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(TINYSOL_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(VOCADITO_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(VOCADITO_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(VOCALSET_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_PIANO_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(PHILHARMONIA_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(PHILHARMONIA_FULL_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_ORCHESTRA_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_ORCHESTRA_FULL_DETECTED_ATTRIBUTE_ROWS)
endif
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS := $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)
ifneq ($(wildcard $(VOCALSET_ARCHIVE)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(VOCALSET_DETECTED_ATTRIBUTE_ROWS)
endif
ifneq ($(wildcard $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)
endif
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS :=
ifneq ($(wildcard $(GUITAR_CHORD_MIX_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitar-chord-mix-route-patterns
endif
ifneq ($(wildcard $(GUITAR_TECHS_CHORD_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitar-techs-chord-route-patterns
endif
ifneq ($(wildcard $(EGFXSET_GUITAR_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-egfxset-guitar-route-patterns
endif
ifneq ($(wildcard $(GAPS_GUITAR_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-gaps-guitar-route-patterns
endif
ifneq ($(wildcard $(GAPS_GUITAR_FULL_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-gaps-guitar-full-route-patterns
endif
ifneq ($(wildcard $(GUITARSET_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitarset-route-patterns
endif
DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS ?= $(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS)
DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS ?= $(DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS)
DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS := find-real-note-focused-row-confusion-patterns find-real-note-coverage-row-confusion-patterns find-real-note-focused-visual-row-confusion-patterns find-real-note-coverage-visual-row-confusion-patterns find-real-note-ownership-patterns evaluate-real-note-display-shadow-all evaluate-real-note-vocal-shadow-safety evaluate-real-note-vocal-display-fallback find-vocadito-full-mix-ownership-patterns find-vocadito-full-mix-broad-vocal-ownership-patterns find-vocadito-full-mix-visual-row-confusion-patterns $(DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS) find-instrument-owner-patterns find-instrument-status-patterns find-drum-full-exact-attribute-patterns-cached
TEST_FIXTURE_PARALLEL_TARGETS := test-real-note-samples test-direct-fit-small-fixture test-synthsod-fixture test-prepared-multitrack-fixture test-multtipop-audio-root-fixture
SAMPLE_MANIFEST_SUMMARY_PATHS ?= $(sort $(wildcard $(BUILD_DIR)/*samples*/manifest.tsv $(BUILD_DIR)/*_samples/manifest.tsv $(BUILD_DIR)/*-manifest.tsv $(BUILD_DIR)/guitarset-manifest.tsv))
.PHONY: test-detector-samples test-detector-samples-full test-detector-samples-parallel test-detector-samples-full-parallel
.PHONY: summarize-sample-manifests test-sample-manifest-summary

ifneq ($(wildcard $(DRUM_SAMPLE_SOURCE_DIR)),)
test-drum-samples-optional: test-drum-samples-parallel
test-drum-samples-spread-optional: test-drum-samples-spread-parallel
test-drum-machine-samples-optional: test-drum-machine-samples-parallel
test-drum-samples-full-optional: test-drum-samples-full
test-drum-samples-full-parallel-optional: test-drum-samples-full-parallel
else
test-drum-samples-optional:
	printf '%s\n' "test-drum-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"
test-drum-samples-spread-optional:
	printf '%s\n' "test-drum-samples-spread: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"
test-drum-machine-samples-optional:
	printf '%s\n' "test-drum-machine-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"
test-drum-samples-full-optional:
	printf '%s\n' "test-drum-samples-full: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"
test-drum-samples-full-parallel-optional:
	printf '%s\n' "test-drum-samples-full-parallel: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"
endif

ifneq ($(wildcard $(GOOD_SOUNDS_ARCHIVE)),)
test-good-sounds-samples-optional: test-good-sounds-samples-parallel
else
test-good-sounds-samples-optional:
	printf '%s\n' "test-good-sounds-samples: skipped; missing $(GOOD_SOUNDS_ARCHIVE)"
endif

ifneq ($(wildcard $(IDMT_BASS_LINES_ARCHIVE)),)
test-idmt-bass-lines-samples-optional: test-idmt-bass-lines-samples-parallel
else
test-idmt-bass-lines-samples-optional:
	printf '%s\n' "test-idmt-bass-lines-samples: skipped; missing $(IDMT_BASS_LINES_ARCHIVE)"
endif

ifneq ($(wildcard $(IDMT_GUITAR_ARCHIVE)),)
test-idmt-guitar-samples-optional: test-idmt-guitar-samples-parallel
else
test-idmt-guitar-samples-optional:
	printf '%s\n' "test-idmt-guitar-samples: skipped; missing $(IDMT_GUITAR_ARCHIVE)"
endif

ifneq ($(wildcard $(MEDLEY_SOLOS_ARCHIVE)),)
test-medley-solos-samples-optional: test-medley-solos-samples-parallel
else
test-medley-solos-samples-optional:
	printf '%s\n' "test-medley-solos-samples: skipped; missing $(MEDLEY_SOLOS_ARCHIVE)"
endif

ifneq ($(wildcard $(MAPS_PIANO_ARCHIVE)),)
test-maps-piano-samples-optional: test-maps-piano-samples-parallel
test-maps-piano-note-samples-optional: test-maps-piano-note-samples-parallel
else
test-maps-piano-samples-optional:
	printf '%s\n' "test-maps-piano-samples: skipped; missing $(MAPS_PIANO_ARCHIVE)"
test-maps-piano-note-samples-optional:
	printf '%s\n' "test-maps-piano-note-samples: skipped; missing $(MAPS_PIANO_ARCHIVE)"
endif

ifneq ($(or $(BACH10_MF0_SYNTH_SOURCE_ROOT),$(wildcard $(BACH10_MF0_SYNTH_ARCHIVE))),)
test-bach10-mf0-synth-samples-optional: test-bach10-mf0-synth-samples-parallel
else
test-bach10-mf0-synth-samples-optional:
	printf '%s\n' "test-bach10-mf0-synth-samples: skipped; missing $(BACH10_MF0_SYNTH_ARCHIVE)"
endif

ifneq ($(wildcard $(VOCALSET_ARCHIVE)),)
test-vocalset-samples-optional: test-vocalset-samples-parallel
test-vocalset-samples-full-mix-optional: test-vocalset-samples-full-mix-parallel
else
test-vocalset-samples-optional:
	printf '%s\n' "test-vocalset-samples: skipped; missing $(VOCALSET_ARCHIVE)"
test-vocalset-samples-full-mix-optional:
	printf '%s\n' "test-vocalset-samples-full-mix: skipped; missing $(VOCALSET_ARCHIVE)"
endif

test-drum-real-world-samples-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) drum_real_world_samples_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DRUM_REAL_WORLD_SAMPLE_TARGETS)

test-drum-real-world-samples-full-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) drum_real_world_samples_full_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DRUM_REAL_WORLD_SAMPLE_FULL_TARGETS)

test-real-world-samples-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) real_world_samples_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_WORLD_SAMPLE_TARGETS)

test-real-world-samples-full-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) real_world_samples_full_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_WORLD_SAMPLE_FULL_TARGETS)

test-detector-samples-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_samples_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_REGRESSION_TARGETS)

test-detector-samples: test-detector-samples-parallel

test-detector-samples-full-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_samples_full_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_SAMPLE_FULL_REGRESSION_TARGETS)

test-detector-samples-full: test-detector-samples-full-parallel

test-fixtures-parallel: $(BUILD_DIR)/analyzer_real_note_samples $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_fixtures_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(TEST_FIXTURE_PARALLEL_TARGETS)

test-fixtures-parallel-isolated: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_fixtures_parallel_isolated $(MAKE) REAL_GOAL_FIXTURE_DIR="$(REAL_GOAL_PARALLEL_FIXTURE_DIR)" test-fixtures-parallel

test-drum-real-world-samples: scripts/run_with_duration.sh
	+$(MAKE) test-drum-real-world-samples-parallel

test-drum-real-world-samples-full: scripts/run_with_duration.sh
	+$(MAKE) test-drum-real-world-samples-full-parallel

test-real-world-samples: scripts/run_with_duration.sh
	+$(MAKE) test-real-world-samples-parallel

test-configured-real-world-samples: tests/run_real_goal_gate.py
	+$(PYTHON) tests/run_real_goal_gate.py optional-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-real-world-samples-full: scripts/run_with_duration.sh
	+$(MAKE) test-real-world-samples-full-parallel

test-iowa-piano-samples-max:
	+$(MAKE) IOWA_PIANO_SAMPLE_LIMIT=0 test-iowa-piano-samples-parallel

test-iowa-orchestra-full-samples-max:
	+$(MAKE) IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT=0 IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE=0 test-iowa-orchestra-full-samples-parallel

test-good-sounds-samples-max:
	+$(MAKE) GOOD_SOUNDS_SAMPLE_LIMIT=0 test-good-sounds-samples-parallel

test-medley-solos-samples-max:
	+$(MAKE) MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=0 test-medley-solos-samples-parallel

test-maps-piano-samples-max:
	+$(MAKE) MAPS_PIANO_RECORDING_LIMIT=0 test-maps-piano-samples-parallel

test-maps-piano-note-samples-max:
	+$(MAKE) MAPS_PIANO_NOTE_RECORDING_LIMIT=0 test-maps-piano-note-samples-parallel

test-real-world-samples-max-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) real_world_samples_max $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_WORLD_SAMPLE_MAX_TARGETS)

.PHONY: audit-build-sample-storage relocate-build-sample-storage

# Keep downloaded and generated audio sample corpora off the workspace disk.
# The apply target refuses collisions so an existing external corpus is never
# overwritten or merged implicitly.
audit-build-sample-storage: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --dry-run

relocate-build-sample-storage: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --apply

test-real-world-samples-max: scripts/run_with_duration.sh
	+$(MAKE) test-real-world-samples-max-parallel

summarize-sample-manifests: scripts/summarize_sample_manifests.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) sample_manifest_summary $(PYTHON) scripts/summarize_sample_manifests.py $(SAMPLE_MANIFEST_SUMMARY_PATHS)

detector-improvement-samples: test-detector-samples-parallel

detector-improvement-patterns: measure-analyzer-patterns

detector-improvement-patterns-cached: measure-analyzer-patterns-cached

detector-improvement-patterns-cached-summary: measure-analyzer-patterns-cached-summary

detector-improvement-routes: analyze-detector-improvement-routes

detector-improvement-samples-full: test-detector-samples-full-parallel

detector-improvement-patterns-full: measure-analyzer-patterns-full

analyze-detector-improvements: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_improvements_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) detector-improvement-samples detector-improvement-patterns

analyze-detector-improvement-routes: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_improvement_routes_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS)" REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS)" $(DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS)

detector-improvement-route-report: $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)
	@printf '%s\n' "detector improvement route report: $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)"

detector-improvement-route-report-refresh: FORCE
	+$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)
	@printf '%s\n' "detector improvement route report: $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)"

$(DETECTOR_IMPROVEMENT_ROUTE_REPORT): Makefile src/analyzer.cpp src/analyzer.hpp tests/analyzer_guitarset.cpp tests/analyzer_real_note_samples.cpp tests/analyzer_instrument_samples.cpp tests/analyzer_drum_samples.cpp scripts/run_with_duration.sh scripts/find_real_note_attribute_patterns.py scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/evaluate_real_note_display_shadow.py scripts/evaluate_real_note_vocal_display_fallback.py scripts/find_instrument_owner_patterns.py scripts/find_drum_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; $(RUN_WITH_DURATION) detector_improvement_routes_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS)" REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS)" $(DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS) > "$$tmp" 2>&1; status="$$?"; if [ "$$status" -eq 0 ]; then mv "$$tmp" "$@"; tail -n 1 "$@"; else cat "$$tmp"; exit "$$status"; fi

detector-improvement-route-summary: $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)
	@printf '%s\n' "detector improvement route summary: $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"

detector-improvement-route-summary-cached:
	@test -f "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" || { printf '%s\n' "missing $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY); run make detector-improvement-route-summary-refresh"; exit 2; }
	@cat "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"

detector-improvement-route-summary-refresh: FORCE
	+$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)
	@printf '%s\n' "detector improvement route summary: $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"

$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY): $(DETECTOR_IMPROVEMENT_ROUTE_REPORT) scripts/summarize_detector_route_report.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/summarize_detector_route_report.py "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" > "$$tmp" && mv "$$tmp" "$@" && cat "$@"

analyze-detector-improvements-full: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_improvements_full_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) detector-improvement-samples-full detector-improvement-patterns-full

detector-improvement-audit: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_improvement_audit_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_IMPROVEMENT_AUDIT_TARGETS)

detector-improvement-audit-cached: detector-improvement-route-summary-cached detector-improvement-audit-report-cached
	@true

detector-improvement-status-cached: detector-improvement-coverage-cached detector-improvement-audit-cached
	@true

detector-improvement-audit-report: $(DETECTOR_IMPROVEMENT_AUDIT_REPORT)
	@printf '%s\n' "detector improvement audit report: $(DETECTOR_IMPROVEMENT_AUDIT_REPORT)"

detector-improvement-audit-report-cached:
	@test -f "$(DETECTOR_IMPROVEMENT_AUDIT_REPORT)" || { printf '%s\n' "missing $(DETECTOR_IMPROVEMENT_AUDIT_REPORT); run make detector-improvement-audit-report"; exit 2; }
	@tail -n "$(DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES)" "$(DETECTOR_IMPROVEMENT_AUDIT_REPORT)"
	@printf '%s\n' "detector improvement audit report: $(DETECTOR_IMPROVEMENT_AUDIT_REPORT)"

$(DETECTOR_IMPROVEMENT_AUDIT_REPORT): FORCE Makefile scripts/run_with_duration.sh scripts/summarize_detector_route_report.py scripts/find_real_note_attribute_patterns.py scripts/evaluate_real_note_display_shadow.py scripts/find_drum_attribute_patterns.py scripts/find_drum_active_false_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; $(RUN_WITH_DURATION) detector_improvement_audit_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(DETECTOR_IMPROVEMENT_AUDIT_TARGETS) > "$$tmp" 2>&1; status="$$?"; if [ "$$status" -eq 0 ]; then mv "$$tmp" "$@"; tail -n "$(DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES)" "$@"; else cat "$$tmp"; exit "$$status"; fi

test-midi-ranges: $(BUILD_DIR)/analyzer_midi_ranges scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_midi_ranges $(BUILD_DIR)/analyzer_midi_ranges

test-fret-control: $(BUILD_DIR)/fret_control_tests scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) fret_control_tests $(BUILD_DIR)/fret_control_tests

test-visualizer-renderer: $(BUILD_DIR)/visualizer_renderer_tests scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) visualizer_renderer_tests $(BUILD_DIR)/visualizer_renderer_tests

test-analyzer-smoke: $(BUILD_DIR)/analyzer_smoke scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_smoke $(BUILD_DIR)/analyzer_smoke

test-analyzer-internal: $(BUILD_DIR)/analyzer_internal scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_internal $(BUILD_DIR)/analyzer_internal

test-analyzer-cases: $(BUILD_DIR)/analyzer_cases scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_cases $(BUILD_DIR)/analyzer_cases

test-analyzer-midi-ranges: $(BUILD_DIR)/analyzer_midi_ranges scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_midi_ranges $(BUILD_DIR)/analyzer_midi_ranges

test-analyzer-urmp: $(BUILD_DIR)/analyzer_urmp scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_urmp $(BUILD_DIR)/analyzer_urmp

test-analyzer-musicnet: $(BUILD_DIR)/analyzer_musicnet scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_musicnet $(BUILD_DIR)/analyzer_musicnet

test-analyzer-multtipop: $(BUILD_DIR)/analyzer_multtipop scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_multtipop $(BUILD_DIR)/analyzer_multtipop

test-analyzer-guitarset: $(BUILD_DIR)/analyzer_guitarset scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitarset $(BUILD_DIR)/analyzer_guitarset

test-analyzer-maestro: $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maestro $(BUILD_DIR)/analyzer_maestro

test-analyzer-egmd: $(BUILD_DIR)/analyzer_egmd scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_egmd $(BUILD_DIR)/analyzer_egmd

.PHONY: test-bpm-regression
test-bpm-regression: test-analyzer-cases test-egmd-fixture

.PHONY: analyze-egmd-bpm analyze-real-egmd-bpm analyze-mdb-bpm analyze-bpm-diagnostics
analyze-egmd-bpm: $(BUILD_DIR)/analyzer_egmd tests/generate_egmd_fixture.py scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	rm -rf "$(REAL_GOAL_EGMD_FIXTURE_DIR)"
	$(PYTHON) tests/generate_egmd_fixture.py "$(REAL_GOAL_EGMD_FIXTURE_DIR)"
	$(RUN_WITH_DURATION) analyzer_egmd_bpm_fixture env MUSIC_ANALYZER_EGMD_ROOT="$(REAL_GOAL_EGMD_FIXTURE_DIR)" MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(EGMD_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(EGMD_BPM_LOG).summary" 2> "$(EGMD_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(EGMD_BPM_LOG)"

analyze-real-egmd-bpm: $(BUILD_DIR)/analyzer_egmd scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_real_egmd_bpm env MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=20 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=80 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS=20 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(EGMD_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(REAL_EGMD_BPM_LOG).summary" 2> "$(REAL_EGMD_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(REAL_EGMD_BPM_LOG)"

analyze-mdb-bpm: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_mdb_bpm env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(MDB_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(MDB_BPM_LOG).summary" 2> "$(MDB_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(MDB_BPM_LOG)"

analyze-bpm-diagnostics: analyze-egmd-bpm

test-core-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_core_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-visualizer-renderer test-analyzer-internal test-analyzer-smoke test-analyzer-cases test-analyzer-midi-ranges test-analyzer-urmp test-analyzer-musicnet test-analyzer-multtipop test-analyzer-guitarset test-analyzer-maestro test-analyzer-egmd

ANALYSIS_SCRIPT_TEST_TARGETS := inspect-real-dataset-catalog inspect-real-goal-coverage test-musicnet-remote test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-synthsod-remote test-synthsod-archive-extract test-synthsod-inspector test-synthsod-prepare test-polyvocal-inspector test-polyvocal-prepare test-prepared-multitrack-inspector test-prepared-multitrack-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-drum-sample-prepare test-hf-drum-kit-prepare test-idmt-drums-prepare test-mdb-drums-prepare test-star-drums-prepare test-medley-solos-prepare test-maps-piano-prepare test-bach10-mf0-synth-prepare test-instrument-sample-attribute-summary test-instrument-sample-owner-buckets test-filter-instrument-attribute-rows test-filter-drum-attribute-rows test-instrument-owner-patterns test-refresh-analyzer-detected-attribute-rows test-print-analyzer-detected-attributes test-analyzer-pattern-report test-measure-analyzer-patterns-target test-build-sharded-tsv test-drum-sample-shard-check test-egmd-shard-check test-maestro-shard-check test-instrument-family-shard-check test-musicnet-shard-check test-real-note-full-mix-shard-check test-real-note-sample-shard-check test-guitarset-shard-check test-philharmonia-prepare test-good-sounds-prepare test-iowa-piano-prepare test-iowa-zip-prepare test-idmt-bass-lines-prepare test-idmt-guitar-prepare test-tinysol-prepare test-vocadito-prepare test-vocalset-prepare test-guitar-fretboard-note-prepare test-guitar-techs-prepare test-guitar-techs-chord-prepare test-guitar-chord-mix-prepare test-gaps-guitar-prepare test-guitarset-miss-analysis test-guitarset-attribute-summary test-guitarset-attribute-buckets test-guitarset-attribute-patterns test-guitar-chord-recovery-analysis test-guitar-primary-order-analysis test-guitar-chord-extra-components-analysis test-real-note-miss-analysis test-real-note-attribute-summary test-real-note-attribute-buckets test-real-note-attribute-patterns test-real-note-attribute-rule test-real-note-display-shadow-eval test-egmd-miss-analysis test-egmd-drum-attribute-summary test-egmd-drum-recovery-eval test-drum-debug-row-analysis test-drum-primary-analysis test-drum-gate-matrix-summary test-drum-active-threshold-simulation test-drum-active-false-summary test-drum-active-false-patterns test-real-goal-script android-check
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-rule-flag-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-compare-drum-gate-summaries
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-octave-display-aliases
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-vocal-display-fallback-eval
ANALYSIS_SCRIPT_TEST_TARGETS += test-detector-route-report-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-sample-skip-patterns
ANALYSIS_SCRIPT_TEST_TARGETS += test-sample-manifest-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-drum-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-real-note-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-detector-coverage-candidates test-compare-drum-primary-scores

test-drum-sample-shard-check: tests/test_check_drum_sample_shards.py scripts/check_drum_sample_shards.py
	$(PYTHON) tests/test_check_drum_sample_shards.py

test-inspect-drum-candidate-rows: tests/test_inspect_drum_candidate_rows.py scripts/inspect_drum_candidate_rows.py
	$(PYTHON) tests/test_inspect_drum_candidate_rows.py

test-inspect-real-note-candidate-rows: tests/test_inspect_real_note_candidate_rows.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_real_note_candidate_rows.py

test-inspect-detector-coverage-candidates: tests/test_inspect_detector_coverage_candidates.py scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_detector_coverage_candidates.py

test-egmd-shard-check: tests/test_check_egmd_shards.py scripts/check_egmd_shards.py
	$(PYTHON) tests/test_check_egmd_shards.py

test-maestro-shard-check: tests/test_check_maestro_shards.py scripts/check_maestro_shards.py
	$(PYTHON) tests/test_check_maestro_shards.py

test-instrument-family-shard-check: tests/test_check_instrument_family_shards.py scripts/check_instrument_family_shards.py
	$(PYTHON) tests/test_check_instrument_family_shards.py

test-musicnet-shard-check: tests/test_check_musicnet_shards.py scripts/check_musicnet_shards.py
	$(PYTHON) tests/test_check_musicnet_shards.py

test-real-note-full-mix-shard-check: tests/test_check_real_note_full_mix_shards.py scripts/check_real_note_full_mix_shards.py
	$(PYTHON) tests/test_check_real_note_full_mix_shards.py

test-real-note-sample-shard-check: tests/test_check_real_note_sample_shards.py scripts/check_real_note_sample_shards.py
	$(PYTHON) tests/test_check_real_note_sample_shards.py

test-guitarset-shard-check: tests/test_check_guitarset_shards.py scripts/check_guitarset_shards.py
	$(PYTHON) tests/test_check_guitarset_shards.py

test-analysis-scripts-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_analysis_scripts_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(ANALYSIS_SCRIPT_TEST_TARGETS)

test-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-analysis-scripts-parallel test-core-parallel test-standalone

TEST_FAST_TARGETS := test-parallel test-detector-samples-parallel test-fret-control test-real-goal-fixture test-fixtures-parallel-isolated

test: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_fast $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(TEST_BINS) $(TEST_FAST_TARGETS)

inspect-real-dataset-catalog: tests/inspect_real_dataset_catalog.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md
	$(PYTHON) tests/inspect_real_dataset_catalog.py

inspect-real-goal-coverage: tests/inspect_real_goal_coverage.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md README.md Makefile src/analyzer.cpp tests/analyzer_urmp.cpp tests/inspect_urmp_dataset.py tests/generate_direct_fit_small_fixture.py tests/analyzer_musicnet.cpp tests/analyzer_multtipop.cpp tests/analyzer_guitarset.cpp tests/prepare_guitarset_manifest.py tests/analyzer_maestro.cpp tests/analyzer_egmd.cpp tests/run_real_goal_gate.py tests/print_real_dataset_sources.py tests/inspect_musicnet_remote.py tests/inspect_medleydb_dataset.py tests/prepare_medleydb_musicnet_fixture.py tests/inspect_musdb_dataset.py tests/inspect_slakh_dataset.py tests/prepare_slakh_musicnet_fixture.py tests/inspect_choralsynth_dataset.py tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_cocochorales_dataset.py tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_synthsod_remote.py tests/prepare_synthsod_archives.py tests/inspect_synthsod_dataset.py tests/prepare_synthsod_musicnet_fixture.py tests/generate_synthsod_fixture.py tests/inspect_polyvocal_dataset.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py tests/prepare_prepared_multitrack_musicnet_fixture.py tests/generate_prepared_multitrack_fixture.py tests/inspect_multtipop_dataset.py tests/inspect_spheres_dataset.py tests/inspect_guitarset_dataset.py
	$(PYTHON) tests/inspect_real_goal_coverage.py

real-dataset-sources: tests/print_real_dataset_sources.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md
	$(PYTHON) tests/print_real_dataset_sources.py

inspect-real-medleydb: tests/inspect_medleydb_dataset.py
	$(PYTHON) tests/inspect_medleydb_dataset.py

inspect-real-musdb: tests/inspect_musdb_dataset.py
	$(PYTHON) tests/inspect_musdb_dataset.py

inspect-real-slakh: tests/inspect_slakh_dataset.py
	$(PYTHON) tests/inspect_slakh_dataset.py

inspect-real-choralsynth: tests/inspect_choralsynth_dataset.py
	$(PYTHON) tests/inspect_choralsynth_dataset.py

inspect-real-cocochorales: tests/inspect_cocochorales_dataset.py
	$(PYTHON) tests/inspect_cocochorales_dataset.py

inspect-real-synthsod-remote: tests/inspect_synthsod_remote.py
	$(PYTHON) tests/inspect_synthsod_remote.py

inspect-real-synthsod: tests/inspect_synthsod_dataset.py
	$(PYTHON) tests/inspect_synthsod_dataset.py

extract-real-synthsod-archives: tests/prepare_synthsod_archives.py | $(BUILD_DIR)
	$(PYTHON) tests/prepare_synthsod_archives.py $(SYNTHSOD_ARCHIVE_EXTRACT_DIR)

inspect-real-polyvocal: tests/inspect_polyvocal_dataset.py
	$(PYTHON) tests/inspect_polyvocal_dataset.py

inspect-real-prepared-multitrack: tests/inspect_prepared_multitrack_dataset.py
	$(PYTHON) tests/inspect_prepared_multitrack_dataset.py

inspect-real-multtipop: tests/inspect_multtipop_dataset.py
	$(PYTHON) tests/inspect_multtipop_dataset.py

inspect-real-spheres: tests/inspect_spheres_dataset.py
	$(PYTHON) tests/inspect_spheres_dataset.py

inspect-real-guitarset: tests/inspect_guitarset_dataset.py
	$(PYTHON) tests/inspect_guitarset_dataset.py

inspect-real-maestro: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_maestro

inspect-real-egmd: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_egmd

inspect-real-musicnet: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

inspect-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=330 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1320 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

inspect-real-musicnet-remote: tests/inspect_musicnet_remote.py
	$(PYTHON) tests/inspect_musicnet_remote.py

test-musicnet-remote: tests/test_inspect_musicnet_remote.py tests/inspect_musicnet_remote.py
	$(PYTHON) tests/test_inspect_musicnet_remote.py

test-medleydb-inspector: tests/test_inspect_medleydb_dataset.py tests/inspect_medleydb_dataset.py
	$(PYTHON) tests/test_inspect_medleydb_dataset.py

test-medleydb-prepare: tests/test_prepare_medleydb_musicnet_fixture.py tests/prepare_medleydb_musicnet_fixture.py tests/inspect_medleydb_dataset.py tests/generate_medleydb_fixture.py
	$(PYTHON) tests/test_prepare_medleydb_musicnet_fixture.py

test-musdb-inspector: tests/test_inspect_musdb_dataset.py tests/inspect_musdb_dataset.py tests/generate_musdb_fixture.py
	$(PYTHON) tests/test_inspect_musdb_dataset.py

test-slakh-inspector: tests/test_inspect_slakh_dataset.py tests/inspect_slakh_dataset.py tests/generate_slakh_fixture.py
	$(PYTHON) tests/test_inspect_slakh_dataset.py

test-slakh-prepare: tests/test_prepare_slakh_musicnet_fixture.py tests/prepare_slakh_musicnet_fixture.py tests/inspect_slakh_dataset.py tests/generate_slakh_fixture.py
	$(PYTHON) tests/test_prepare_slakh_musicnet_fixture.py

test-choralsynth-inspector: tests/test_inspect_choralsynth_dataset.py tests/inspect_choralsynth_dataset.py tests/generate_choralsynth_fixture.py
	$(PYTHON) tests/test_inspect_choralsynth_dataset.py

test-choralsynth-prepare: tests/test_prepare_choralsynth_musicnet_fixture.py tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_choralsynth_dataset.py tests/generate_choralsynth_fixture.py
	$(PYTHON) tests/test_prepare_choralsynth_musicnet_fixture.py

test-cocochorales-inspector: tests/test_inspect_cocochorales_dataset.py tests/inspect_cocochorales_dataset.py tests/generate_cocochorales_fixture.py
	$(PYTHON) tests/test_inspect_cocochorales_dataset.py

test-cocochorales-prepare: tests/test_prepare_cocochorales_musicnet_fixture.py tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_cocochorales_dataset.py tests/generate_cocochorales_fixture.py
	$(PYTHON) tests/test_prepare_cocochorales_musicnet_fixture.py

test-synthsod-remote: tests/test_inspect_synthsod_remote.py tests/inspect_synthsod_remote.py
	$(PYTHON) tests/test_inspect_synthsod_remote.py

test-synthsod-archive-extract: tests/test_prepare_synthsod_archives.py tests/prepare_synthsod_archives.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_prepare_synthsod_archives.py

test-synthsod-inspector: tests/test_inspect_synthsod_dataset.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_inspect_synthsod_dataset.py

test-synthsod-prepare: tests/test_prepare_synthsod_musicnet_fixture.py tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py tests/generate_synthsod_fixture.py
	$(PYTHON) tests/test_prepare_synthsod_musicnet_fixture.py

test-polyvocal-inspector: tests/test_inspect_polyvocal_dataset.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_inspect_polyvocal_dataset.py

test-polyvocal-prepare: tests/test_prepare_polyvocal_musicnet_fixture.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_prepare_polyvocal_musicnet_fixture.py

test-prepared-multitrack-inspector: tests/test_inspect_prepared_multitrack_dataset.py tests/inspect_prepared_multitrack_dataset.py tests/generate_prepared_multitrack_fixture.py
	$(PYTHON) tests/test_inspect_prepared_multitrack_dataset.py

test-prepared-multitrack-prepare: tests/test_prepare_prepared_multitrack_musicnet_fixture.py tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py tests/generate_prepared_multitrack_fixture.py
	$(PYTHON) tests/test_prepare_prepared_multitrack_musicnet_fixture.py

test-multtipop-inspector: tests/test_inspect_multtipop_dataset.py tests/inspect_multtipop_dataset.py tests/generate_multtipop_fixture.py
	$(PYTHON) tests/test_inspect_multtipop_dataset.py

test-spheres-inspector: tests/test_inspect_spheres_dataset.py tests/inspect_spheres_dataset.py
	$(PYTHON) tests/test_inspect_spheres_dataset.py

test-guitarset-inspector: tests/test_inspect_guitarset_dataset.py tests/inspect_guitarset_dataset.py tests/generate_guitarset_fixture.py
	$(PYTHON) tests/test_inspect_guitarset_dataset.py

test-urmp-inspector: tests/test_inspect_urmp_dataset.py tests/inspect_urmp_dataset.py
	$(PYTHON) tests/test_inspect_urmp_dataset.py

test-drum-sample-prepare: tests/test_prepare_drum_samples.py scripts/prepare_drum_samples.py
	$(PYTHON) tests/test_prepare_drum_samples.py

test-drum-sample-skip-patterns: tests/test_inspect_drum_sample_skip_patterns.py scripts/inspect_drum_sample_skip_patterns.py scripts/prepare_drum_samples.py
	$(PYTHON) tests/test_inspect_drum_sample_skip_patterns.py

test-hf-drum-kit-prepare: tests/test_prepare_hf_drum_kit_samples.py scripts/prepare_hf_drum_kit_samples.py
	$(PYTHON) tests/test_prepare_hf_drum_kit_samples.py

test-idmt-drums-prepare: tests/test_prepare_idmt_drums_samples.py scripts/prepare_idmt_drums_samples.py
	$(PYTHON) tests/test_prepare_idmt_drums_samples.py

test-mdb-drums-prepare: tests/test_prepare_mdb_drums_samples.py scripts/prepare_mdb_drums_samples.py
	$(PYTHON) tests/test_prepare_mdb_drums_samples.py

test-star-drums-prepare: tests/test_prepare_star_drums_samples.py scripts/prepare_star_drums_samples.py
	$(PYTHON) tests/test_prepare_star_drums_samples.py

test-medley-solos-prepare: tests/test_prepare_medley_solos_samples.py scripts/prepare_medley_solos_samples.py
	$(PYTHON) tests/test_prepare_medley_solos_samples.py

test-maps-piano-prepare: tests/test_prepare_maps_piano_samples.py scripts/prepare_maps_piano_samples.py
	$(PYTHON) tests/test_prepare_maps_piano_samples.py

test-bach10-mf0-synth-prepare: tests/test_prepare_bach10_mf0_synth_musicnet_fixture.py scripts/prepare_bach10_mf0_synth_musicnet_fixture.py
	$(PYTHON) tests/test_prepare_bach10_mf0_synth_musicnet_fixture.py

test-philharmonia-prepare: tests/test_prepare_philharmonia_samples.py scripts/prepare_philharmonia_samples.py
	$(PYTHON) tests/test_prepare_philharmonia_samples.py

test-good-sounds-prepare: tests/test_prepare_good_sounds_samples.py scripts/prepare_good_sounds_samples.py
	$(PYTHON) tests/test_prepare_good_sounds_samples.py

test-iowa-piano-prepare: tests/test_prepare_iowa_piano_samples.py scripts/prepare_iowa_piano_samples.py
	$(PYTHON) tests/test_prepare_iowa_piano_samples.py

test-iowa-zip-prepare: tests/test_prepare_iowa_zip_samples.py scripts/prepare_iowa_zip_samples.py
	$(PYTHON) tests/test_prepare_iowa_zip_samples.py

test-idmt-bass-lines-prepare: tests/test_prepare_idmt_bass_lines_samples.py scripts/prepare_idmt_bass_lines_samples.py
	$(PYTHON) tests/test_prepare_idmt_bass_lines_samples.py

test-idmt-guitar-prepare: tests/test_prepare_idmt_guitar_samples.py scripts/prepare_idmt_guitar_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_idmt_guitar_samples.py

test-tinysol-prepare: tests/test_prepare_tinysol_samples.py scripts/prepare_tinysol_samples.py
	$(PYTHON) tests/test_prepare_tinysol_samples.py

test-vocadito-prepare: tests/test_prepare_vocadito_samples.py scripts/prepare_vocadito_samples.py
	$(PYTHON) tests/test_prepare_vocadito_samples.py

test-vocalset-prepare: tests/test_prepare_vocalset_samples.py scripts/prepare_vocalset_samples.py
	$(PYTHON) tests/test_prepare_vocalset_samples.py

test-guitar-fretboard-note-prepare: tests/test_prepare_guitar_fretboard_notes.py scripts/prepare_guitar_fretboard_notes.py
	$(PYTHON) tests/test_prepare_guitar_fretboard_notes.py

test-guitar-techs-prepare: tests/test_prepare_guitar_techs_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_guitar_techs_samples.py

test-guitar-techs-chord-prepare: tests/test_prepare_guitar_techs_chord_samples.py scripts/prepare_guitar_techs_chord_samples.py scripts/prepare_guitar_techs_samples.py
	$(PYTHON) tests/test_prepare_guitar_techs_chord_samples.py

test-guitar-chord-mix-prepare: tests/test_prepare_hf_guitar_chord_mix.py scripts/prepare_hf_guitar_chord_mix.py
	$(PYTHON) tests/test_prepare_hf_guitar_chord_mix.py

test-gaps-guitar-prepare: tests/test_prepare_gaps_guitar_samples.py scripts/prepare_gaps_guitar_samples.py
	$(PYTHON) tests/test_prepare_gaps_guitar_samples.py

test-guitarset-miss-analysis: tests/test_analyze_guitarset_misses.py scripts/analyze_guitarset_misses.py
	$(PYTHON) tests/test_analyze_guitarset_misses.py

test-guitarset-attribute-summary: tests/test_summarize_guitarset_attributes.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_summarize_guitarset_attributes.py

test-guitarset-attribute-buckets: tests/test_inspect_guitarset_attribute_buckets.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_inspect_guitarset_attribute_buckets.py

test-guitarset-attribute-patterns: tests/test_find_guitarset_attribute_patterns.py scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) tests/test_find_guitarset_attribute_patterns.py

test-guitar-chord-recovery-analysis: tests/test_analyze_guitar_chord_recovery.py scripts/analyze_guitar_chord_recovery.py
	$(PYTHON) tests/test_analyze_guitar_chord_recovery.py

test-guitar-primary-order-analysis: tests/test_analyze_guitar_primary_order.py scripts/analyze_guitar_primary_order.py
	$(PYTHON) tests/test_analyze_guitar_primary_order.py

test-guitar-chord-extra-components-analysis: tests/test_analyze_guitar_chord_extra_components.py scripts/analyze_guitar_chord_extra_components.py
	$(PYTHON) tests/test_analyze_guitar_chord_extra_components.py

test-real-note-miss-analysis: tests/test_analyze_real_note_misses.py scripts/analyze_real_note_misses.py
	$(PYTHON) tests/test_analyze_real_note_misses.py

test-real-note-attribute-summary: tests/test_summarize_real_note_attributes.py scripts/summarize_real_note_attributes.py
	$(PYTHON) tests/test_summarize_real_note_attributes.py

test-real-note-attribute-buckets: tests/test_inspect_real_note_attribute_buckets.py scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) tests/test_inspect_real_note_attribute_buckets.py

test-real-note-attribute-patterns: tests/test_find_real_note_attribute_patterns.py scripts/find_real_note_attribute_patterns.py
	$(PYTHON) tests/test_find_real_note_attribute_patterns.py

test-real-note-attribute-rule: tests/test_measure_real_note_attribute_rule.py scripts/measure_real_note_attribute_rule.py
	$(PYTHON) tests/test_measure_real_note_attribute_rule.py

test-real-note-display-shadow-eval: tests/test_evaluate_real_note_display_shadow.py scripts/evaluate_real_note_display_shadow.py
	$(PYTHON) tests/test_evaluate_real_note_display_shadow.py

test-real-note-vocal-display-fallback-eval: tests/test_evaluate_real_note_vocal_display_fallback.py scripts/evaluate_real_note_vocal_display_fallback.py
	$(PYTHON) tests/test_evaluate_real_note_vocal_display_fallback.py

test-real-note-octave-display-aliases: tests/test_measure_real_note_octave_display_aliases.py scripts/measure_real_note_octave_display_aliases.py
	$(PYTHON) tests/test_measure_real_note_octave_display_aliases.py

test-sample-manifest-summary: tests/test_summarize_sample_manifests.py scripts/summarize_sample_manifests.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) test_sample_manifest_summary $(PYTHON) tests/test_summarize_sample_manifests.py

test-instrument-sample-attribute-summary: tests/test_summarize_instrument_sample_attributes.py scripts/summarize_instrument_sample_attributes.py
	$(PYTHON) tests/test_summarize_instrument_sample_attributes.py

test-instrument-sample-owner-buckets: tests/test_inspect_instrument_sample_owner_buckets.py scripts/inspect_instrument_sample_owner_buckets.py
	$(PYTHON) tests/test_inspect_instrument_sample_owner_buckets.py

test-filter-instrument-attribute-rows: tests/test_filter_instrument_attribute_rows.py scripts/filter_instrument_attribute_rows.py
	$(PYTHON) tests/test_filter_instrument_attribute_rows.py

test-filter-drum-attribute-rows: tests/test_filter_drum_attribute_rows.py scripts/filter_drum_attribute_rows.py
	$(PYTHON) tests/test_filter_drum_attribute_rows.py

test-instrument-owner-patterns: tests/test_find_instrument_owner_patterns.py scripts/find_instrument_owner_patterns.py
	$(PYTHON) tests/test_find_instrument_owner_patterns.py

test-refresh-analyzer-detected-attribute-rows: tests/test_refresh_analyzer_detected_attribute_rows.py scripts/refresh_analyzer_detected_attribute_rows.py
	$(PYTHON) tests/test_refresh_analyzer_detected_attribute_rows.py

test-print-analyzer-detected-attributes: tests/test_print_analyzer_detected_attributes.py scripts/print_analyzer_detected_attributes.py
	$(PYTHON) tests/test_print_analyzer_detected_attributes.py

test-analyzer-pattern-report: tests/test_report_analyzer_attribute_patterns.py scripts/report_analyzer_attribute_patterns.py
	$(PYTHON) tests/test_report_analyzer_attribute_patterns.py

test-detector-route-report-summary: tests/test_summarize_detector_route_report.py scripts/summarize_detector_route_report.py
	$(PYTHON) tests/test_summarize_detector_route_report.py

test-measure-analyzer-patterns-target: tests/test_measure_analyzer_patterns_makefile.py Makefile
	$(PYTHON) tests/test_measure_analyzer_patterns_makefile.py

test-build-sharded-tsv: tests/test_build_sharded_tsv.py scripts/build_sharded_tsv.sh
	$(PYTHON) tests/test_build_sharded_tsv.py

test-egmd-miss-analysis: tests/test_analyze_egmd_misses.py scripts/analyze_egmd_misses.py
	$(PYTHON) tests/test_analyze_egmd_misses.py

test-egmd-drum-attribute-summary: tests/test_summarize_egmd_drum_attributes.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) tests/test_summarize_egmd_drum_attributes.py

.PHONY: test-egmd-drum-recovery-eval evaluate-mdb-drum-recovery evaluate-star-drum-recovery
test-egmd-drum-recovery-eval: tests/test_evaluate_egmd_drum_recovery.py scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) tests/test_evaluate_egmd_drum_recovery.py

evaluate-mdb-drum-recovery: analyze-mdb-drums-misses scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(MDB_DRUMS_MISS_LOG)" $(DRUM_RECOVERY_ARGS)

evaluate-star-drum-recovery: analyze-star-drums-misses scripts/evaluate_egmd_drum_recovery.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(STAR_DRUMS_MISS_LOG)" $(DRUM_RECOVERY_ARGS)

test-drum-debug-row-analysis: tests/test_analyze_drum_debug_rows.py scripts/analyze_drum_debug_rows.py
	$(PYTHON) tests/test_analyze_drum_debug_rows.py

test-drum-primary-analysis: tests/test_analyze_drum_primary_debug.py tests/test_evaluate_drum_rule_grid.py tests/test_evaluate_drum_tom_bleed_caps.py tests/test_find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py scripts/evaluate_drum_rule_grid.py scripts/evaluate_drum_tom_bleed_caps.py scripts/find_drum_attribute_patterns.py
	$(PYTHON) tests/test_analyze_drum_primary_debug.py
	$(PYTHON) tests/test_evaluate_drum_rule_grid.py
	$(PYTHON) tests/test_evaluate_drum_tom_bleed_caps.py
	$(PYTHON) tests/test_find_drum_attribute_patterns.py

test-drum-gate-matrix-summary: tests/test_summarize_drum_gate_matrix.py scripts/summarize_drum_gate_matrix.py
	$(PYTHON) tests/test_summarize_drum_gate_matrix.py

test-compare-drum-primary-scores: tests/test_compare_drum_primary_scores.py scripts/compare_drum_primary_scores.py
	$(PYTHON) tests/test_compare_drum_primary_scores.py

test-compare-drum-gate-summaries: tests/test_compare_drum_gate_summaries.py scripts/compare_drum_gate_summaries.py
	$(PYTHON) tests/test_compare_drum_gate_summaries.py

test-drum-active-threshold-simulation: tests/test_simulate_drum_active_thresholds.py scripts/simulate_drum_active_thresholds.py
	$(PYTHON) tests/test_simulate_drum_active_thresholds.py

test-drum-active-false-summary: tests/test_summarize_drum_active_false_rows.py scripts/summarize_drum_active_false_rows.py
	$(PYTHON) tests/test_summarize_drum_active_false_rows.py

test-drum-rule-flag-summary: tests/test_summarize_drum_rule_flags.py scripts/summarize_drum_rule_flags.py
	$(PYTHON) tests/test_summarize_drum_rule_flags.py

test-drum-active-false-patterns: tests/test_find_drum_active_false_patterns.py scripts/find_drum_active_false_patterns.py
	$(PYTHON) tests/test_find_drum_active_false_patterns.py

test-real-goal-script: tests/test_run_real_goal_gate.py tests/run_real_goal_gate.py
	$(PYTHON) tests/test_run_real_goal_gate.py

prepare-real-goal-fixtures-parallel: $(URMP_FIXTURE_ARCHIVE) tests/generate_musicnet_fixture.py tests/generate_medleydb_fixture.py tests/generate_musdb_fixture.py tests/generate_slakh_fixture.py tests/generate_choralsynth_fixture.py tests/generate_cocochorales_fixture.py tests/generate_synthsod_fixture.py tests/generate_polyvocal_fixture.py tests/generate_prepared_multitrack_fixture.py tests/generate_multtipop_fixture.py tests/generate_spheres_fixture.py tests/generate_guitarset_fixture.py tests/generate_maestro_fixture.py tests/generate_egmd_fixture.py scripts/run_with_duration.sh | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_FIXTURE_DIR)
	mkdir -p $(REAL_GOAL_FIXTURE_DIR)
	+$(RUN_WITH_DURATION) real_goal_fixture_generation_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) $(REAL_GOAL_FIXTURE_PREP_TARGETS)

prepare-real-goal-urmp-fixture: $(URMP_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(REAL_GOAL_FIXTURE_DIR)
	+$(MAKE) decode-urmp-fixture URMP_FIXTURE_DIR=$(REAL_GOAL_URMP_FIXTURE_DIR)

prepare-real-goal-musicnet-fixture: tests/generate_musicnet_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(REAL_GOAL_MUSICNET_FIXTURE_DIR)

prepare-real-goal-medleydb-fixture: tests/generate_medleydb_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)

prepare-real-goal-musdb-fixture: tests/generate_musdb_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_musdb_fixture.py $(REAL_GOAL_MUSDB_FIXTURE_DIR)

prepare-real-goal-slakh-fixture: tests/generate_slakh_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)

prepare-real-goal-choralsynth-fixture: tests/generate_choralsynth_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)

prepare-real-goal-cocochorales-fixture: tests/generate_cocochorales_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)

prepare-real-goal-synthsod-fixture: tests/generate_synthsod_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)

prepare-real-goal-polyvocal-fixture: tests/generate_polyvocal_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)

prepare-real-goal-prepared-multitrack-fixture: tests/generate_prepared_multitrack_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)

prepare-real-goal-multtipop-fixture: tests/generate_multtipop_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio

prepare-real-goal-spheres-fixture: tests/generate_spheres_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_spheres_fixture.py $(REAL_GOAL_SPHERES_FIXTURE_DIR)

prepare-real-goal-guitarset-fixture: tests/generate_guitarset_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)

prepare-real-goal-maestro-fixture: tests/generate_maestro_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)

prepare-real-goal-egmd-fixture: tests/generate_egmd_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)

test-real-goal-fixture: $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd prepare-real-goal-fixtures-parallel tests/prepare_guitarset_manifest.py tests/run_real_goal_gate.py | $(BUILD_DIR)
	+MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)
	+MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-musicnet-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-medleydb-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_medleydb_fixture.py tests/prepare_medleydb_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	+MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) $(MAKE) test-real-medleydb-20

test-slakh-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_slakh_fixture.py tests/prepare_slakh_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	+MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) $(MAKE) test-real-slakh-20

test-choralsynth-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_choralsynth_fixture.py tests/prepare_choralsynth_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	+MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) $(MAKE) test-real-choralsynth-20

test-cocochorales-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_cocochorales_fixture.py tests/prepare_cocochorales_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	+MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) $(MAKE) test-real-cocochorales-20

test-synthsod-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_synthsod_fixture.py tests/prepare_synthsod_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	+MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores $(MAKE) test-real-synthsod-20

test-polyvocal-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_polyvocal_fixture.py tests/prepare_polyvocal_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	+MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 $(MAKE) test-real-polyvocal-20

test-prepared-multitrack-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_prepared_multitrack_fixture.py tests/prepare_prepared_multitrack_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	+MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) $(MAKE) test-real-prepared-multitrack-20

test-multtipop-audio-root-fixture: $(BUILD_DIR)/analyzer_multtipop tests/generate_multtipop_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT=$(REAL_GOAL_MULTTIPOP_AUDIO_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 $(BUILD_DIR)/analyzer_multtipop

test-guitarset-fixture: $(BUILD_DIR)/analyzer_guitarset tests/generate_guitarset_fixture.py tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT=100 $(BUILD_DIR)/analyzer_guitarset

test-maestro-fixture: $(BUILD_DIR)/analyzer_maestro tests/generate_maestro_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-egmd-fixture: $(BUILD_DIR)/analyzer_egmd tests/generate_egmd_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_EGMD_FIXTURE_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)
	MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=80 $(BUILD_DIR)/analyzer_egmd

test-bach10-fixture: $(BUILD_DIR)/analyzer_urmp tests/generate_bach10_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_bach10_fixture.py $(BACH10_FIXTURE_DIR)
	MUSIC_ANALYZER_URMP_ROOT=$(BACH10_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=10 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=40 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=4 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-direct-fit-small-fixture: $(BUILD_DIR)/analyzer_urmp $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(DIRECT_FIT_SMALL_FIXTURE_DIR)
	$(TAR) -xzf $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-direct-fit-small-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(DIRECT_FIT_SMALL_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=20 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=80 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=3 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-urmp-fixture: $(BUILD_DIR)/analyzer_urmp $(URMP_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-urmp-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp-full: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(BUILD_DIR)/analyzer_urmp

test-real-multitrack-20: test-real-urmp

test-real-multitrack-full: test-real-urmp-full

test-real-goal-20: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-real-goal-full: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py full "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

inspect-real-goal-20: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

inspect-real-goal-full: tests/run_real_goal_gate.py
	+MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/run_real_goal_gate.py inspect-full "$(MAKE)" $(REAL_GOAL_MAKE_JOBS)

test-real-musicnet-20: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=330 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1320 $(BUILD_DIR)/analyzer_musicnet

.PHONY: download-real-urmp inspect-real-urmp-download prepare-real-urmp analyze-real-urmp-traits analyze-real-urmp-miss-traits summarize-real-urmp-miss-traits test-urmp-download-scripts test-urmp-archive-extract download-real-musicnet inspect-real-musicnet-download prepare-real-musicnet inspect-downloaded-real-musicnet-20-traits analyze-downloaded-real-musicnet-recording test-downloaded-real-musicnet-20 test-downloaded-real-musicnet-full test-musicnet-archive-extract test-run-musicnet-gate test-summarize-musicnet-attributes
download-real-urmp: $(URMP_ARCHIVE)

inspect-real-urmp-download: scripts/urmp_download_status.sh
	$(SHELL) scripts/urmp_download_status.sh "$(URMP_ARCHIVE)"

test-urmp-download-scripts: scripts/download_urmp_archive.sh scripts/urmp_download_status.sh tests/test_urmp_download_scripts.py
	$(PYTHON) -m pytest -q tests/test_urmp_download_scripts.py

prepare-real-urmp: $(URMP_ARCHIVE) scripts/extract_urmp_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/extract_urmp_archive.sh "$(URMP_ARCHIVE)" "$(URMP_EXTRACT_DIR)"

analyze-real-urmp-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_measurement.sh
	$(SHELL) scripts/capture_urmp_measurement.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_MEASUREMENT_OUTPUT)"

analyze-real-urmp-miss-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_trait_sample.sh
	$(SHELL) scripts/capture_urmp_trait_sample.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_MEASUREMENT_OUTPUT)"

summarize-real-urmp-miss-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

test-urmp-archive-extract: scripts/extract_urmp_archive.sh tests/test_extract_urmp_archive.py
	$(PYTHON) tests/test_extract_urmp_archive.py scripts/extract_urmp_archive.sh

$(URMP_ARCHIVE): FORCE scripts/download_urmp_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_urmp_archive.sh "$@" "$(URMP_ARCHIVE_URL)" "$(URMP_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

download-real-musicnet: $(MUSICNET_ARCHIVE) $(MUSICNET_METADATA) $(MUSICNET_MIDI_ARCHIVE)

inspect-real-musicnet-download: scripts/musicnet_download_status.sh
	$(SHELL) scripts/musicnet_download_status.sh "$(MUSICNET_ARCHIVE)"

$(MUSICNET_ARCHIVE): FORCE scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_musicnet_archive.sh "$@" "$(MUSICNET_ARCHIVE_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

$(MUSICNET_METADATA): FORCE | $(BUILD_DIR)
	mkdir -p "$(MUSICNET_SOURCE_DIR)"
	$(CURL) -fL -C - -o "$@.part" "$(MUSICNET_METADATA_URL)"
	mv -f "$@.part" "$@"

$(MUSICNET_MIDI_ARCHIVE): FORCE scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_musicnet_archive.sh "$@" "$(MUSICNET_MIDI_ARCHIVE_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

prepare-real-musicnet: $(MUSICNET_ARCHIVE) scripts/extract_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/extract_musicnet_archive.sh "$(MUSICNET_ARCHIVE)" "$(MUSICNET_EXTRACT_DIR)"

test-musicnet-archive-extract: scripts/extract_musicnet_archive.sh tests/test_extract_musicnet_archive.py
	$(PYTHON) tests/test_extract_musicnet_archive.py scripts/extract_musicnet_archive.sh

test-run-musicnet-gate: scripts/run_musicnet_gate.sh tests/test_run_musicnet_gate.py
	$(PYTHON) tests/test_run_musicnet_gate.py scripts/run_musicnet_gate.sh

test-summarize-musicnet-attributes: scripts/summarize_musicnet_attributes.py tests/test_summarize_musicnet_attributes.py
	$(PYTHON) tests/test_summarize_musicnet_attributes.py

inspect-downloaded-real-musicnet: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet
	MUSIC_ANALYZER_MUSICNET_ROOT="$(MUSICNET_EXTRACT_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

analyze-downloaded-real-musicnet-20-traits: scripts/summarize_musicnet_attributes.py
	$(PYTHON) scripts/summarize_musicnet_attributes.py "$(MUSICNET_20_ATTRIBUTE_OUTPUT)"

analyze-downloaded-real-musicnet-recording: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	@test -n "$(MUSICNET_ANALYSIS_RECORDING_IDS)" || { printf '%s\n' "set MUSICNET_ANALYSIS_RECORDING_IDS=<MusicNet id>" >&2; exit 2; }
	MUSIC_ANALYZER_MUSICNET_RECORDING_IDS="$(MUSICNET_ANALYSIS_RECORDING_IDS)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MUSICNET_MAX_RECORDINGS="$(MUSICNET_ANALYSIS_MAX_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING=12 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 $(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_RECORDING_MEASUREMENT_OUTPUT)" "" "" "$(MUSICNET_RECORDING_ATTRIBUTE_OUTPUT)"

test-downloaded-real-musicnet-20: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	$(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_20_MEASUREMENT_OUTPUT)" 20 80 "$(MUSICNET_20_ATTRIBUTE_OUTPUT)"

test-downloaded-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	$(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_FULL_MEASUREMENT_OUTPUT)" "" "" "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

test-real-medleydb-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_medleydb_musicnet_fixture.py tests/inspect_medleydb_dataset.py | $(BUILD_DIR)
	rm -rf $(MEDLEYDB_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_medleydb_musicnet_fixture.py $(MEDLEYDB_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(MEDLEYDB_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=1 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=1 $(BUILD_DIR)/analyzer_musicnet

test-real-slakh-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_slakh_musicnet_fixture.py tests/inspect_slakh_dataset.py | $(BUILD_DIR)
	rm -rf $(SLAKH_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_slakh_musicnet_fixture.py $(SLAKH_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SLAKH_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-slakh-full: $(BUILD_DIR)/analyzer_musicnet tests/prepare_slakh_musicnet_fixture.py tests/inspect_slakh_dataset.py | $(BUILD_DIR)
	rm -rf $(SLAKH_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS=225 MUSIC_ANALYZER_SLAKH_PREPARE_TRACKS=225 $(PYTHON) tests/prepare_slakh_musicnet_fixture.py $(SLAKH_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SLAKH_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=225 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=900 $(BUILD_DIR)/analyzer_musicnet

test-real-choralsynth-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_choralsynth_dataset.py | $(BUILD_DIR)
	rm -rf $(CHORALSYNTH_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_choralsynth_musicnet_fixture.py $(CHORALSYNTH_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(CHORALSYNTH_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-cocochorales-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_cocochorales_dataset.py | $(BUILD_DIR)
	rm -rf $(COCOCHORALES_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_cocochorales_musicnet_fixture.py $(COCOCHORALES_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(COCOCHORALES_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-synthsod-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py | $(BUILD_DIR)
	rm -rf $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_synthsod_musicnet_fixture.py $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SYNTHSOD_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-synthsod-full: $(BUILD_DIR)/analyzer_musicnet tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py | $(BUILD_DIR)
	rm -rf $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_SYNTHSOD_PREPARE_PIECES=1000000 $(PYTHON) tests/prepare_synthsod_musicnet_fixture.py $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SYNTHSOD_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-polyvocal-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py | $(BUILD_DIR)
	rm -rf $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_polyvocal_musicnet_fixture.py $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(POLYVOCAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-prepared-multitrack-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py | $(BUILD_DIR)
	rm -rf $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-prepared-multitrack-full: $(BUILD_DIR)/analyzer_musicnet tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py | $(BUILD_DIR)
	rm -rf $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES=1000000 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-multtipop-20: $(BUILD_DIR)/analyzer_multtipop
	MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 $(BUILD_DIR)/analyzer_multtipop

test-real-multtipop-full: $(BUILD_DIR)/analyzer_multtipop
	MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 MUSIC_ANALYZER_MULTTIPOP_REQUIRED_SEGMENTS=572 MUSIC_ANALYZER_MULTTIPOP_REQUIRED_WINDOWS=2288 $(BUILD_DIR)/analyzer_multtipop

test-real-guitarset-20: $(BUILD_DIR)/analyzer_guitarset tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	$(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 $(BUILD_DIR)/analyzer_guitarset

test-real-guitarset-full: $(BUILD_DIR)/analyzer_guitarset tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	$(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=360 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1440 $(BUILD_DIR)/analyzer_guitarset

test-real-maestro-20: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-real-maestro-full: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1276 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=5104 $(BUILD_DIR)/analyzer_maestro

test-real-egmd-20: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 $(BUILD_DIR)/analyzer_egmd

test-real-egmd-full: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=45537 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=182148 $(BUILD_DIR)/analyzer_egmd

.PHONY: inspect-instrument-sample-store configure-instrument-sample-store test-instrument-sample-store inspect-sample-build-migration migrate-sample-build-directories test-sample-build-migration

inspect-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --status --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

configure-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

inspect-sample-build-migration: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --status --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

migrate-sample-build-directories: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

test-instrument-sample-store: tests/test_configure_instrument_sample_store.py scripts/configure_instrument_sample_store.py
	$(PYTHON) tests/test_configure_instrument_sample_store.py

test-sample-build-migration: tests/test_migrate_sample_build_directories.py scripts/migrate_sample_build_directories.py
	$(PYTHON) tests/test_migrate_sample_build_directories.py

inspect-real-urmp: tests/inspect_urmp_dataset.py
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-urmp-full: tests/inspect_urmp_dataset.py
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-multitrack-20: inspect-real-urmp

inspect-real-multitrack-full: inspect-real-urmp-full

inspect-urmp-fixture: $(URMP_FIXTURE_ARCHIVE) tests/inspect_urmp_dataset.py | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-urmp-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 $(PYTHON) tests/inspect_urmp_dataset.py

decode-urmp-fixture:
	$(FFMPEG) -version >/dev/null
	find $(URMP_FIXTURE_DIR) -type f -name '*.flac' -print | while IFS= read -r flac; do \
		wav=$${flac%.flac}.wav; \
		$(FFMPEG) -nostdin -hide_banner -loglevel error -y -i "$$flac" "$$wav"; \
	done

decode-direct-fit-small-fixture:
	$(FFMPEG) -version >/dev/null
	find $(DIRECT_FIT_SMALL_FIXTURE_DIR) -type f -name '*.flac' -print | while IFS= read -r flac; do \
		wav=$${flac%.flac}.wav; \
		$(FFMPEG) -nostdin -hide_banner -loglevel error -y -i "$$flac" "$$wav"; \
	done

update-urmp-fixture: tests/generate_urmp_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_urmp_fixture.py $(URMP_FIXTURE_DIR)
	mkdir -p tests/fixtures
	$(TAR) --sort=name --mtime='UTC 2026-01-01' --owner=0 --group=0 --numeric-owner -czf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR) urmp-fixture

update-direct-fit-small-fixture: tests/generate_direct_fit_small_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_direct_fit_small_fixture.py $(DIRECT_FIT_SMALL_FIXTURE_DIR)
	$(FFMPEG) -version >/dev/null
	find $(DIRECT_FIT_SMALL_FIXTURE_DIR) -type f -name '*.wav' -print | while IFS= read -r wav; do \
		flac=$${wav%.wav}.flac; \
		$(FFMPEG) -nostdin -hide_banner -loglevel error -y -i "$$wav" "$$flac"; \
		rm -f "$$wav"; \
	done
	mkdir -p tests/fixtures
	$(TAR) --sort=name --mtime='UTC 2026-01-01' --owner=0 --group=0 --numeric-owner -czf $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) -C $(BUILD_DIR) direct-fit-small-fixture

install-user: all
	@if pgrep -x obs >/dev/null 2>&1 || pgrep -x obs-studio >/dev/null 2>&1; then \
		echo "OBS is running; refusing to copy $(BUILD_DIR)/music-analyzer-obs.so. Close OBS first."; \
		exit 1; \
	fi
	mkdir -p $(OBS_USER_PLUGIN_DIR)
	cp $(BUILD_DIR)/music-analyzer-obs.so $(OBS_USER_PLUGIN_DIR)/

clean:
	rm -rf $(BUILD_DIR)

clean-pycache:
	find tests -type d -name '__pycache__' -prune -exec rm -rf {} +
.PHONY: check-worktree
check-worktree: scripts/check_worktree.sh
	bash scripts/check_worktree.sh

.PHONY: commit-verified
commit-verified: scripts/commit_verified.sh
	@test -n "$(COMMIT_MESSAGE)"
	@test -n "$(COMMIT_PATHS)"
	bash scripts/commit_verified.sh "$(COMMIT_MESSAGE)" $(COMMIT_PATHS)

.PHONY: push-current-branch
push-current-branch: scripts/push_current_branch.sh
	bash scripts/push_current_branch.sh

.PHONY: locate-gaps-guitar-sample
locate-gaps-guitar-sample: scripts/locate_gaps_guitar_sample.sh
	@test -n "$(SAMPLE_ID)"
	bash scripts/locate_gaps_guitar_sample.sh "$(SAMPLE_ID)"

.PHONY: inspect-gaps-guitar-full-rows
inspect-gaps-guitar-full-rows: build/gaps_guitar_full_attributes.tsv scripts/inspect_gaps_guitar_full_rows.sh
	@test -n "$(SAMPLE_ID)"
	bash scripts/inspect_gaps_guitar_full_rows.sh "$(SAMPLE_ID)"

.PHONY: analyze-gaps-guitar-power-alias-candidates
analyze-gaps-guitar-power-alias-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_power_alias_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_power_alias_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(POWER_ALIAS_ARGS)

.PHONY: inspect-analyzer-symbol
inspect-analyzer-symbol: scripts/inspect_analyzer_symbol.sh
	@test -n "$(SYMBOL)"
	bash scripts/inspect_analyzer_symbol.sh "$(SYMBOL)"

.PHONY: rebuild-analyzer-guitarset
rebuild-analyzer-guitarset:
	+$(MAKE) -B build/analyzer_guitarset

.PHONY: analyze-gaps-guitar-display-restore-candidates
analyze-gaps-guitar-display-restore-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_display_restore_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_display_restore_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(DISPLAY_RESTORE_ARGS)

.PHONY: analyze-gaps-guitar-major-seventh-candidates
analyze-gaps-guitar-major-seventh-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_major_seventh_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_major_seventh_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(MAJOR_SEVENTH_ARGS)
.PHONY: analyze-gaps-guitar-analysis-fifth-power-candidates
analyze-gaps-guitar-analysis-fifth-power-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_fifth_power_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_FIFTH_POWER_ARGS)
.PHONY: analyze-gaps-guitar-low-root-power-candidates
analyze-gaps-guitar-low-root-power-candidates:
	@python3 scripts/analyze_gaps_guitar_low_root_power_candidates.py
.PHONY: find-gaps-guitar-rows
find-gaps-guitar-rows:
	@test -n "$(EXPECTED)"
	@python3 scripts/find_gaps_guitar_rows.py --expected "$(EXPECTED)" $(if $(MISSING),--missing "$(MISSING)") $(FIND_GAPS_GUITAR_ROWS_ARGS)
.PHONY: analyze-gaps-guitar-analysis-note-candidates
analyze-gaps-guitar-analysis-note-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_note_candidates.py $(ANALYSIS_NOTE_ARGS) "$(GUITAR_ANALYSIS_NOTE_PATH)"
.PHONY: analyze-gaps-guitar-analysis-minor-alias-candidates
analyze-gaps-guitar-analysis-minor-alias-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_minor_alias_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_MINOR_ALIAS_ARGS)
.PHONY: analyze-gaps-guitar-analysis-add9-alias-candidates
analyze-gaps-guitar-analysis-add9-alias-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_add9_alias_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_ADD9_ALIAS_ARGS)
.PHONY: analyze-guitar-rootless-dim-candidates
analyze-guitar-rootless-dim-candidates:
	@python3 scripts/analyze_guitar_rootless_dim_candidates.py $(ROOTLESS_DIM_ARGS) build/gaps_guitar_full_attributes.tsv build/guitar_techs_chord_attributes.tsv build/guitar_chord_mix_attributes.tsv
.PHONY: test-gaps-guitar-regressions
test-gaps-guitar-regressions: build/gaps_guitar_full_attributes.tsv
	@python3 scripts/check_gaps_guitar_regressions.py build/gaps_guitar_full_attributes.tsv
.PHONY: search-repo
search-repo:
	@sh scripts/search_repo.sh "$(QUERY)"

.PHONY: show-repo-lines
show-repo-lines:
	@sh scripts/show_repo_lines.sh "$(FILE)" "$(START)" "$(END)"
