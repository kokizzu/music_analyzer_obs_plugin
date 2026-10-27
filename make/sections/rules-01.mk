.PHONY: plan-basic-pitch-other-vocal-recovery-commit commit-basic-pitch-other-vocal-recovery push-basic-pitch-other-vocal-recovery
plan-basic-pitch-other-vocal-recovery-commit: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
	$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py plan

commit-basic-pitch-other-vocal-recovery: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
	$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py commit

push-basic-pitch-other-vocal-recovery: scripts/manage_basic_pitch_other_vocal_recovery_commit.py
	$(PYTHON) scripts/manage_basic_pitch_other_vocal_recovery_commit.py push

CXX ?= g++
PYTHON ?= python3

ACTIVE_GOAL_FILE ?= /home/kyz/.codex/attachments/46ea0f9b-3fe5-461f-90f6-07da1a97dc8d/pasted-text-1.txt

.PHONY: show-active-goal
show-active-goal: scripts/show_active_goal.sh
	$(SHELL) scripts/show_active_goal.sh "$(ACTIVE_GOAL_FILE)"

.PHONY: list-make-targets test-list-make-targets find-repo-text test-find-repo-text
list-make-targets: scripts/list_make_targets.py
	$(PYTHON) scripts/list_make_targets.py Makefile "$(TERM)"

test-drum-hihat-tail-regression: build/analyzer_drum_samples prepare-drum-samples-spread
	MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="hihat" MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY="hihat" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT=94 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT=89 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="build/drum_samples_spread" build/analyzer_drum_samples

test-list-make-targets: scripts/list_make_targets.py
	$(PYTHON) scripts/list_make_targets.py Makefile detection >/dev/null

find-repo-text: scripts/find_repo_text.py
	$(PYTHON) scripts/find_repo_text.py "$(or $(SCOPE),.)" "$(TEXT)" "$(or $(MAX_RESULTS),100)"

test-find-repo-text: scripts/find_repo_text.py
	$(PYTHON) scripts/find_repo_text.py scripts find_repo_text 1 >/dev/null

# Explicitly approved, resumable external corpus acquisitions. This registry
# is task-scoped: a target belongs here only while it is an active accuracy
# coverage gap, rather than merely being supported by the project.
APPROVED_CORPUS_DOWNLOAD_TARGETS ?= measure-maestro-real-samples measure-kraisler measure-ballroom-bpm download-filobass download-gtzan-rhythm download-candombe
CORPUS_DOWNLOAD_LOG_TARGET ?= $(word 1,$(APPROVED_CORPUS_DOWNLOAD_TARGETS))
PKG_CONFIG ?= pkg-config
TAR ?= tar
FFMPEG ?= ffmpeg
CURL ?= curl
ARIA2C ?= aria2c
BUILD_DIR ?= build
INSTRUMENT_SAMPLE_STORE ?= /media/kyz/sshflashtor/InstrumentSamples
INSTRUMENT_SAMPLE_STORE_LINK ?= $(BUILD_DIR)/InstrumentSamples
ONNXRUNTIME_VERSION ?= 1.29.0
ONNXRUNTIME_ROOT ?= $(BUILD_DIR)/onnxruntime-linux-x64-$(ONNXRUNTIME_VERSION)
ONNXRUNTIME_HEADER ?= $(ONNXRUNTIME_ROOT)/include/onnxruntime_c_api.h
ONNXRUNTIME_LIBRARY ?= $(ONNXRUNTIME_ROOT)/lib/libonnxruntime.so
BASIC_PITCH_ONNX_MODEL ?= $(BUILD_DIR)/basic_pitch/nmp.onnx
ZEROX808_CC0_REPOSITORY ?= https://github.com/averagenative/0x808.git
ZEROX808_CC0_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/0x808_cc0
ZEROX808_RIM_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/0x808_rim_samples
ZEROX808_RIM_MEASUREMENT ?= $(BUILD_DIR)/0x808_rim_measurement.log
ZEROX808_RIM_PRIMARY_DEBUG_OUT ?= $(BUILD_DIR)/0x808_rim_primary_debug.out
ZEROX808_RIM_PRIMARY_DEBUG_ERR ?= $(BUILD_DIR)/0x808_rim_primary_debug.err
ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/0x808_rim_primary_attribute_rows.tsv
ZEROX808_VIRTUOSITY_RIM_CANDIDATE_AUDIT ?= $(BUILD_DIR)/0x808_virtuosity_rim_candidate_audit.txt
UNRULY_CROSS_SOURCE_RIM_CANDIDATE_AUDIT ?= $(BUILD_DIR)/unruly_cross_source_rim_candidate_audit.txt
UNRULY_RIM_PRIMARY_CANDIDATE_AUDIT ?= $(BUILD_DIR)/unruly_rim_primary_candidate_audit.txt
RIM_PRIMARY_CANDIDATE_AUDIT ?= $(BUILD_DIR)/rim_primary_candidate_audit.txt
UNRULY_DRUMS_ARCHIVE_URL ?= https://github.com/sfzinstruments/karoryfer.unruly-drums/releases/download/v1.100/Unruly_Drums_1100.zip
UNRULY_DRUMS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/unruly_drums_cc0
UNRULY_DRUMS_ARCHIVE ?= $(UNRULY_DRUMS_SOURCE_DIR)/Unruly_Drums_1100.zip
UNRULY_DRUMS_RIM_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/unruly_drums_rim_samples
UNRULY_DRUMS_RIM_MEASUREMENT ?= $(BUILD_DIR)/unruly_drums_rim_measurement.log
UNRULY_DRUMS_RIM_PRIMARY_DEBUG_OUT ?= $(BUILD_DIR)/unruly_drums_rim_primary_debug.out
UNRULY_DRUMS_RIM_PRIMARY_DEBUG_ERR ?= $(BUILD_DIR)/unruly_drums_rim_primary_debug.err
UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/unruly_drums_rim_primary_attribute_rows.tsv
UNRULY_DRUMS_DOWNLOAD_CHUNKS ?= 4
AGPT_GUITAR_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/agpt_guitar
AGPT_GUITAR_ARCHIVE ?= $(AGPT_GUITAR_SOURCE_DIR)/aGPTset_z.zip
AGPT_GUITAR_ARCHIVE_URL ?= https://zenodo.org/records/10159492/files/aGPTset_z.zip?download=1
AGPT_GUITAR_ARCHIVE_MD5 ?= 1dff8103f9ad6e1a86cee2e5e39cbe87
AGPT_GUITAR_EXTRACTED_DIR ?= $(AGPT_GUITAR_SOURCE_DIR)/extracted
AGPT_GUITAR_SAMPLE_DIR ?= $(AGPT_GUITAR_SOURCE_DIR)/prepared_notes
AGPT_GUITAR_SAMPLE_LIMIT ?= 2000
AGPT_GUITAR_MIN_GUITAR ?= 1000
AGPT_GUITAR_MAX_FAILURES ?= 999999
AGPT_GUITAR_MEASUREMENT ?= $(BUILD_DIR)/agpt_guitar_measurement.tsv
AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/agpt_guitar_full_mix_attributes.tsv
AGPT_GUITAR_FULL_MIX_MEASUREMENT ?= $(BUILD_DIR)/agpt_guitar_full_mix_measurement.out
AGPT_GUITAR_VISUAL_PRIMARY_MEASUREMENT ?= $(BUILD_DIR)/agpt_guitar_visual_primary.tsv
AGPT_GUITAR_VISUAL_PATTERN_REPORT ?= $(BUILD_DIR)/agpt_guitar_visual_pattern_report.txt
AGPT_GUITAR_VISUAL_PATTERN_MAX_CONDITIONS ?= 3
AGPT_GUITAR_VISUAL_PATTERN_BEAM_WIDTH ?= 240
DREANSS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/dreanss
DREANSS_ANNOTATION_ARCHIVE ?= $(DREANSS_SOURCE_DIR)/dreanss_v1.zip
DREANSS_ANNOTATION_ARCHIVE_URL ?= https://zenodo.org/records/1290739/files/dreanss_v1.zip?download=1
DREANSS_ANNOTATION_ARCHIVE_MD5 ?= 17b7554ac68cabd84b513f23bb9e967c

.PHONY: start-approved-corpus-downloads stop-approved-corpus-downloads report-approved-corpus-downloads show-approved-corpus-download-log test-approved-corpus-download-manager queue-filobass-bpm-after-download queue-candombe-bpm-after-download test-validate-maestro-subset-archive
start-approved-corpus-downloads: scripts/start_approved_corpus_downloads.sh scripts/run_approved_corpus_download.sh
	$(SHELL) scripts/start_approved_corpus_downloads.sh "$(MAKE)" "$(BUILD_DIR)" $(APPROVED_CORPUS_DOWNLOAD_TARGETS)

stop-approved-corpus-downloads: scripts/stop_approved_corpus_downloads.sh
	$(SHELL) scripts/stop_approved_corpus_downloads.sh "$(BUILD_DIR)" $(APPROVED_CORPUS_DOWNLOAD_TARGETS)

report-approved-corpus-downloads: scripts/report_approved_corpus_downloads.sh
	$(SHELL) scripts/report_approved_corpus_downloads.sh "$(BUILD_DIR)" $(APPROVED_CORPUS_DOWNLOAD_TARGETS)

show-approved-corpus-download-log: scripts/show_approved_corpus_download_log.sh
	$(SHELL) scripts/show_approved_corpus_download_log.sh "$(BUILD_DIR)" "$(CORPUS_DOWNLOAD_LOG_TARGET)"

test-approved-corpus-download-manager: tests/test_approved_corpus_download_manager.py scripts/start_approved_corpus_downloads.sh scripts/run_approved_corpus_download.sh scripts/stop_approved_corpus_downloads.sh scripts/report_approved_corpus_downloads.sh scripts/show_approved_corpus_download_log.sh scripts/measure_filobass_after_download.sh scripts/measure_candombe_after_download.sh scripts/download_ballroom_annotations.sh scripts/download_gtzan_rhythm_dataset.sh scripts/download_candombe_dataset.sh
	$(SHELL) -n scripts/start_approved_corpus_downloads.sh
	$(SHELL) -n scripts/run_approved_corpus_download.sh
	$(SHELL) -n scripts/stop_approved_corpus_downloads.sh
	$(SHELL) -n scripts/report_approved_corpus_downloads.sh
	$(SHELL) -n scripts/show_approved_corpus_download_log.sh
	$(SHELL) -n scripts/measure_filobass_after_download.sh
	$(SHELL) -n scripts/measure_candombe_after_download.sh
	$(SHELL) -n scripts/download_ballroom_annotations.sh
	bash -n scripts/download_gtzan_rhythm_dataset.sh
	bash -n scripts/download_candombe_dataset.sh
	$(PYTHON) tests/test_approved_corpus_download_manager.py

# This is deliberately separate from the download registry: it is a queued
# measurement, not a second acquisition.  The detached manager preserves it
# if the interactive session ends while FiloBass is still transferring.
queue-filobass-bpm-after-download: scripts/measure_filobass_after_download.sh
	$(SHELL) scripts/start_approved_corpus_downloads.sh "$(MAKE)" "$(BUILD_DIR)" measure-filobass-bpm-after-download

queue-candombe-bpm-after-download: scripts/measure_candombe_after_download.sh
	$(SHELL) scripts/start_approved_corpus_downloads.sh "$(MAKE)" "$(BUILD_DIR)" measure-candombe-bpm-after-download

.PHONY: measure-filobass-bpm-after-download
measure-filobass-bpm-after-download: scripts/measure_filobass_after_download.sh
	$(SHELL) scripts/measure_filobass_after_download.sh "$(MAKE)" "$(BUILD_DIR)"

.PHONY: measure-candombe-bpm-after-download
measure-candombe-bpm-after-download: scripts/measure_candombe_after_download.sh
	$(SHELL) scripts/measure_candombe_after_download.sh "$(MAKE)" "$(BUILD_DIR)"

test-validate-maestro-subset-archive: tests/test_validate_maestro_subset_archive.py scripts/validate_maestro_subset_archive.py scripts/prepare_maps_piano_samples.py
	$(PYTHON) tests/test_validate_maestro_subset_archive.py

.PHONY: inspect-maestro-audit-capacity
inspect-maestro-audit-capacity: scripts/inspect_storage_capacity.py
	$(PYTHON) scripts/inspect_storage_capacity.py "$(INSTRUMENT_SAMPLE_STORE)"

.PHONY: download-agpt-guitar-samples test-download-agpt-guitar-samples
download-agpt-guitar-samples: scripts/download_agpt_guitar_samples.sh | $(INSTRUMENT_SAMPLE_STORE_LINK)
	$(SHELL) scripts/download_agpt_guitar_samples.sh "$(AGPT_GUITAR_ARCHIVE)" "$(AGPT_GUITAR_ARCHIVE_URL)" "$(AGPT_GUITAR_ARCHIVE_MD5)"

test-download-agpt-guitar-samples: scripts/download_agpt_guitar_samples.sh
	$(SHELL) -n scripts/download_agpt_guitar_samples.sh

.PHONY: extract-agpt-guitar-samples test-extract-agpt-guitar-samples
extract-agpt-guitar-samples: scripts/extract_agpt_guitar_samples.sh download-agpt-guitar-samples | $(INSTRUMENT_SAMPLE_STORE_LINK)
	$(SHELL) scripts/extract_agpt_guitar_samples.sh "$(AGPT_GUITAR_ARCHIVE)" "$(AGPT_GUITAR_EXTRACTED_DIR)"

test-extract-agpt-guitar-samples: scripts/extract_agpt_guitar_samples.sh
	$(SHELL) -n scripts/extract_agpt_guitar_samples.sh

.PHONY: start-agpt-guitar-extraction test-start-agpt-guitar-extraction
start-agpt-guitar-extraction: scripts/start_agpt_guitar_extraction.sh scripts/extract_agpt_guitar_samples.sh $(AGPT_GUITAR_ARCHIVE) | $(INSTRUMENT_SAMPLE_STORE_LINK)
	$(SHELL) scripts/start_agpt_guitar_extraction.sh "$(CURDIR)/scripts/extract_agpt_guitar_samples.sh" "$(AGPT_GUITAR_ARCHIVE)" "$(AGPT_GUITAR_EXTRACTED_DIR)"

test-start-agpt-guitar-extraction: scripts/start_agpt_guitar_extraction.sh
	$(SHELL) -n scripts/start_agpt_guitar_extraction.sh

.PHONY: prepare-agpt-guitar-samples test-prepare-agpt-guitar-samples
prepare-agpt-guitar-samples: scripts/prepare_agpt_guitar_samples.py extract-agpt-guitar-samples | $(INSTRUMENT_SAMPLE_STORE_LINK)
	$(PYTHON) scripts/prepare_agpt_guitar_samples.py --source "$(AGPT_GUITAR_EXTRACTED_DIR)" --output "$(AGPT_GUITAR_SAMPLE_DIR)" --limit "$(AGPT_GUITAR_SAMPLE_LIMIT)" --min-samples "$(AGPT_GUITAR_MIN_GUITAR)" --ffmpeg "$(FFMPEG)"

test-prepare-agpt-guitar-samples: tests/test_prepare_agpt_guitar_samples.py scripts/prepare_agpt_guitar_samples.py
	$(PYTHON) tests/test_prepare_agpt_guitar_samples.py

.PHONY: test-agpt-guitar-samples test-agpt-guitar-samples-parallel
test-agpt-guitar-samples test-agpt-guitar-samples-parallel: REAL_NOTE_SAMPLE_TAG := agpt_guitar
test-agpt-guitar-samples test-agpt-guitar-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(AGPT_GUITAR_SAMPLE_DIR)
test-agpt-guitar-samples test-agpt-guitar-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(AGPT_GUITAR_MIN_GUITAR)
test-agpt-guitar-samples test-agpt-guitar-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(AGPT_GUITAR_MIN_GUITAR)
test-agpt-guitar-samples test-agpt-guitar-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(AGPT_GUITAR_MAX_FAILURES)
test-agpt-guitar-samples: test-agpt-guitar-samples-parallel
test-agpt-guitar-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-agpt-guitar-samples scripts/run_with_duration.sh
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

.PHONY: download-dreanss-annotations test-download-dreanss-annotations
download-dreanss-annotations: scripts/download_dreanss_annotations.sh | $(INSTRUMENT_SAMPLE_STORE_LINK)
	$(SHELL) scripts/download_dreanss_annotations.sh "$(DREANSS_ANNOTATION_ARCHIVE)" "$(DREANSS_ANNOTATION_ARCHIVE_URL)" "$(DREANSS_ANNOTATION_ARCHIVE_MD5)"

test-download-dreanss-annotations: scripts/download_dreanss_annotations.sh
	$(SHELL) -n scripts/download_dreanss_annotations.sh

.PHONY: discover-dreanss-audio-sources test-discover-dreanss-audio-sources
discover-dreanss-audio-sources: scripts/discover_dreanss_audio_sources.sh
	$(SHELL) scripts/discover_dreanss_audio_sources.sh

test-discover-dreanss-audio-sources: scripts/discover_dreanss_audio_sources.sh
	$(SHELL) -n scripts/discover_dreanss_audio_sources.sh

.PHONY: inspect-agpt-guitar-download test-inspect-agpt-guitar-download
inspect-agpt-guitar-download: scripts/inspect_agpt_guitar_download.sh
	$(SHELL) scripts/inspect_agpt_guitar_download.sh "$(AGPT_GUITAR_ARCHIVE)"

test-inspect-agpt-guitar-download: scripts/inspect_agpt_guitar_download.sh
	$(SHELL) -n scripts/inspect_agpt_guitar_download.sh

.PHONY: wait-agpt-guitar-download
wait-agpt-guitar-download: scripts/inspect_agpt_guitar_download.sh
	$(SHELL) scripts/inspect_agpt_guitar_download.sh "$(AGPT_GUITAR_ARCHIVE)" "25"

.PHONY: inspect-zip-archive inspect-agpt-guitar-archive test-inspect-agpt-guitar-archive test-inspect-zip-archive
inspect-zip-archive: scripts/inspect_zip_archive.py
	@test -n "$(ZIP_ARCHIVE)" || { printf '%s\n' 'set ZIP_ARCHIVE=path/to/archive.zip'; exit 2; }
	$(PYTHON) scripts/inspect_zip_archive.py "$(ZIP_ARCHIVE)"

inspect-agpt-guitar-archive: scripts/inspect_agpt_guitar_archive.py $(AGPT_GUITAR_ARCHIVE)
	python3 scripts/inspect_agpt_guitar_archive.py "$(AGPT_GUITAR_ARCHIVE)"

test-inspect-agpt-guitar-archive: tests/test_inspect_agpt_guitar_archive.py scripts/inspect_agpt_guitar_archive.py
	python3 tests/test_inspect_agpt_guitar_archive.py

test-inspect-zip-archive: tests/test_inspect_zip_archive.py scripts/inspect_zip_archive.py
	python3 tests/test_inspect_zip_archive.py

.PHONY: inspect-dreanss-annotations
inspect-dreanss-annotations: scripts/inspect_zip_archive.py $(DREANSS_ANNOTATION_ARCHIVE)
	python3 scripts/inspect_zip_archive.py "$(DREANSS_ANNOTATION_ARCHIVE)"

.PHONY: inspect-maestro-real-subset
inspect-maestro-real-subset: scripts/inspect_maestro_real_subset.py
	$(PYTHON) scripts/inspect_maestro_real_subset.py "$(MAESTRO_REAL_SAMPLE_DIR)"

.PHONY: test-inspect-maestro-real-subset
test-inspect-maestro-real-subset: tests/test_inspect_maestro_real_subset.py scripts/inspect_maestro_real_subset.py
	$(PYTHON) tests/test_inspect_maestro_real_subset.py

.PHONY: stop-maestro-real-subset-writers
stop-maestro-real-subset-writers: scripts/stop_maestro_real_subset_writers.py
	$(PYTHON) scripts/stop_maestro_real_subset_writers.py

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
MUSICNET_ROUTING_OUTPUT ?= $(BUILD_DIR)/musicnet_routing.tsv
MUSICNET_ANALYSIS_RECORDING_IDS ?=
MUSICNET_ANALYSIS_MAX_RECORDINGS ?= 1
MUSICNET_DOWNLOAD_CONNECTIONS ?= 8
MUSICNET_ARCHIVE_URL ?= https://zenodo.org/api/records/5120004/files/musicnet.tar.gz/content
MUSICNET_METADATA_URL ?= https://zenodo.org/api/records/5120004/files/musicnet_metadata.csv/content
MUSICNET_MIDI_ARCHIVE_URL ?= https://zenodo.org/api/records/5120004/files/musicnet_midis.tar.gz/content
DAGSTUHL_CHOIRSET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/dagstuhl_choirset
DAGSTUHL_CHOIRSET_ARCHIVE ?= $(DAGSTUHL_CHOIRSET_SOURCE_DIR)/DagstuhlChoirSet.zip
DAGSTUHL_CHOIRSET_EXTRACT_DIR ?= $(DAGSTUHL_CHOIRSET_SOURCE_DIR)/extracted
DAGSTUHL_CHOIRSET_PREPARED_DIR ?= $(DAGSTUHL_CHOIRSET_SOURCE_DIR)/prepared-multitrack
DAGSTUHL_CHOIRSET_PREPARE_LOCK_DIR ?= $(BUILD_DIR)/locks/dagstuhl_choirset_prepare.lock
DAGSTUHL_CHOIRSET_MUSICNET_DIR ?= $(DAGSTUHL_CHOIRSET_SOURCE_DIR)/musicnet-fixture
DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_attributes.tsv
DAGSTUHL_CHOIRSET_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_measurement.tsv
DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_validation.txt
DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_inventory.txt
DAGSTUHL_CHOIRSET_PATTERN_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_pattern_rows.tsv
DAGSTUHL_CHOIRSET_OWNERSHIP_PATTERN_REPORT ?= $(BUILD_DIR)/dagstuhl_choirset_ownership_pattern_report.txt
DAGSTUHL_CHOIRSET_CROSS_CORPUS_OWNERSHIP_OUTPUT ?= $(BUILD_DIR)/dagstuhl_choirset_cross_corpus_ownership.tsv
DAGSTUHL_CHOIRSET_SHARED_OWNERSHIP_PATTERN_REPORT ?= $(BUILD_DIR)/dagstuhl_choirset_shared_ownership_pattern_report.txt
DAGSTUHL_CHOIRSET_ARCHIVE_URL ?= https://zenodo.org/api/records/3897182/files/DagstuhlChoirSet.zip/content
DAGSTUHL_CHOIRSET_ARCHIVE_MD5 ?= 6d7ccdd5e3f43e54981b0f12d19987f9
DAGSTUHL_CHOIRSET_DOWNLOAD_CONNECTIONS ?= 8
CHORAL_SINGING_DATASET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/choral_singing_dataset
CHORAL_SINGING_DATASET_ARCHIVE ?= $(CHORAL_SINGING_DATASET_SOURCE_DIR)/ChoralSingingDataset.zip
CHORAL_SINGING_DATASET_EXTRACT_DIR ?= $(CHORAL_SINGING_DATASET_SOURCE_DIR)/extracted
CHORAL_SINGING_DATASET_PREPARED_DIR ?= $(CHORAL_SINGING_DATASET_SOURCE_DIR)/prepared-multitrack
CHORAL_SINGING_DATASET_MUSICNET_DIR ?= $(CHORAL_SINGING_DATASET_SOURCE_DIR)/musicnet-fixture
CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/choral_singing_dataset_attributes.tsv
CHORAL_SINGING_DATASET_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/choral_singing_dataset_measurement.tsv
CHORAL_SINGING_DATASET_PATTERN_OUTPUT ?= $(BUILD_DIR)/choral_singing_dataset_pattern_rows.tsv
CHORAL_SINGING_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT ?= $(BUILD_DIR)/choral_singing_dataset_cross_corpus_ownership.tsv
CHORAL_SINGING_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT ?= $(BUILD_DIR)/choral_singing_dataset_shared_ownership_pattern_report.txt
CHORAL_SINGING_DATASET_INSPECTION_OUTPUT ?= $(BUILD_DIR)/choral_singing_dataset_inventory.txt
CHORAL_SINGING_DATASET_ARCHIVE_URL ?= https://zenodo.org/records/2649950/files/ChoralSingingDataset.zip?download=1
CHORAL_SINGING_DATASET_ARCHIVE_MD5 ?= 7a9643609a1c3902b5255d78dbba3303
CHORAL_SINGING_DATASET_DOWNLOAD_CONNECTIONS ?= 8
CHORAL_SINGING_DATASET_DOWNLOAD_LOCK_DIR ?= $(BUILD_DIR)/locks/choral_singing_dataset_download.lock
CHORAL_SINGING_DATASET_INSPECT_ARGS ?=
ESMUC_CHOIR_DATASET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/esmuc_choir_dataset
ESMUC_CHOIR_DATASET_ARCHIVE ?= $(ESMUC_CHOIR_DATASET_SOURCE_DIR)/EsmucChoirDataset_v1.0.0.zip
ESMUC_CHOIR_DATASET_EXTRACT_DIR ?= $(ESMUC_CHOIR_DATASET_SOURCE_DIR)/extracted
ESMUC_CHOIR_DATASET_PREPARED_DIR ?= $(ESMUC_CHOIR_DATASET_SOURCE_DIR)/prepared-multitrack
ESMUC_CHOIR_DATASET_MUSICNET_DIR ?= $(ESMUC_CHOIR_DATASET_SOURCE_DIR)/musicnet-fixture
ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/esmuc_choir_dataset_attributes.tsv
ESMUC_CHOIR_DATASET_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/esmuc_choir_dataset_measurement.tsv
ESMUC_CHOIR_DATASET_PATTERN_OUTPUT ?= $(BUILD_DIR)/esmuc_choir_dataset_pattern_rows.tsv
ESMUC_CHOIR_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT ?= $(BUILD_DIR)/esmuc_choir_dataset_cross_corpus_ownership.tsv
ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT ?= $(BUILD_DIR)/esmuc_choir_dataset_shared_ownership_pattern_report.txt
ESMUC_SHARED_VOCAL_MAX_CONDITIONS ?= 2
ESMUC_SHARED_VOCAL_FILTER_ARGS ?=
ESMUC_CHOIR_DATASET_ARCHIVE_URL ?= https://zenodo.org/records/5848990/files/EsmucChoirDataset_v1.0.0.zip?download=1
ESMUC_CHOIR_DATASET_ARCHIVE_MD5 ?= ba2b4b5c4326dbe0a6d391167fa30574
ESMUC_CHOIR_DATASET_DOWNLOAD_CONNECTIONS ?= 8
ESMUC_CHOIR_DATASET_DOWNLOAD_LOCK_DIR ?= $(BUILD_DIR)/locks/esmuc_choir_dataset_download.lock
ESMUC_CHOIR_DATASET_INSPECT_ARGS ?=
MIR1K_DATASET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/mir1k_dataset
MIR1K_DATASET_ARCHIVE ?= $(MIR1K_DATASET_SOURCE_DIR)/mir1k_yourmt3_16k.tar.gz
MIR1K_DATASET_EXTRACT_DIR ?= $(MIR1K_DATASET_SOURCE_DIR)/extracted
MIR1K_DATASET_SAMPLE_DIR ?= $(MIR1K_DATASET_SOURCE_DIR)/prepared-vocal-mix
MIR1K_DATASET_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/mir1k_vocal_mix_attributes.tsv
MIR1K_DATASET_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/mir1k_vocal_mix_measurement.out
VOCAL_EXACT_NOTE_CROSS_CORPUS_OUTPUT ?= $(BUILD_DIR)/vocal_exact_note_cross_corpus.tsv
SCMS_VOCAL_CROSS_CORPUS_ARG = $(if $(wildcard $(SCMS_DATASET_ATTRIBUTE_OUTPUT)),--input "SCMS=$(SCMS_DATASET_ATTRIBUTE_OUTPUT)")
MIR1K_DATASET_ARCHIVE_URL ?= https://zenodo.org/record/7955481/files/mir1k_yourmt3_16k.tar.gz?download=1
MIR1K_DATASET_ARCHIVE_MD5 ?= 4cbac56a4e971432ca807efd5cb76d67
MIR1K_DATASET_DOWNLOAD_CONNECTIONS ?= 8
MIR1K_DATASET_DOWNLOAD_LOCK_DIR ?= $(BUILD_DIR)/locks/mir1k_dataset_download.lock
MIR1K_DATASET_INSPECT_ARGS ?=
MIR1K_DATASET_SAMPLE_LIMIT ?= 300
MIR1K_DATASET_MIN_SAMPLES ?= 250
SCMS_DATASET_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/saraga_carnatic_melody_synth
SCMS_DATASET_ARCHIVE ?= $(SCMS_DATASET_SOURCE_DIR)/Saraga-Carnatic-Melody-Synth.zip
SCMS_DATASET_EXTRACT_DIR ?= $(SCMS_DATASET_SOURCE_DIR)/extracted
SCMS_DATASET_SAMPLE_DIR ?= $(SCMS_DATASET_SOURCE_DIR)/prepared-vocal-mix
SCMS_DATASET_ARCHIVE_URL ?= https://zenodo.org/records/5553925/files/Saraga-Carnatic-Melody-Synth.zip?download=1
SCMS_DATASET_ARCHIVE_MD5 ?= 08322351d024f206e21abca962e495ab
SCMS_DATASET_DOWNLOAD_CONNECTIONS ?= 8
SCMS_DATASET_SAMPLE_LIMIT ?= 300
SCMS_DATASET_MIN_SAMPLES ?= 250
SCMS_DATASET_INSPECTION_OUTPUT ?= $(BUILD_DIR)/scms_dataset_inventory.txt
SCMS_DATASET_VALIDATION_OUTPUT ?= $(BUILD_DIR)/scms_dataset_validation.txt
SCMS_DATASET_DOWNLOAD_LOG ?= $(BUILD_DIR)/scms_dataset_download.log
SCMS_DATASET_DOWNLOAD_PID ?= $(BUILD_DIR)/scms_dataset_download.pid
SCMS_VOCAL_MEASUREMENT_LOG ?= $(BUILD_DIR)/scms_vocal_measurement.log
SCMS_VOCAL_MEASUREMENT_PID ?= $(BUILD_DIR)/scms_vocal_measurement.pid
SCMS_DATASET_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/scms_vocal_mix_attributes.tsv
SCMS_VOCAL_OTHER_ROUTE_AUDIT ?= $(BUILD_DIR)/scms_vocal_other_route_audit.txt
SCMS_DATASET_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/scms_vocal_mix_measurement.out
SCMS_DATASET_DEBUG_WAV ?= $(SCMS_DATASET_SAMPLE_DIR)/audio/scms_Athirum_Kazhal_3_F3.wav
SCMS_VOCAL_MIX_SHARDS ?= 8
SCMS_VOCAL_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(SCMS_VOCAL_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
SCMS_VOCAL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/scms_vocal_mix_attributes.shard-,$(addsuffix .tsv,$(SCMS_VOCAL_MIX_SHARD_INDEXES)))
SCMS_VOCAL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(SCMS_VOCAL_MIX_SHARDS))
URMP_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/urmp
URMP_ARCHIVE ?= $(URMP_SOURCE_DIR)/urmp-kaggle.zip
URMP_EXTRACT_DIR ?= $(URMP_SOURCE_DIR)/extracted
# The dataset itself belongs in the external sample store.  Analyzer reports
# are regenerable build artifacts and must remain writable in the workspace.
URMP_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/urmp_measurement.out
URMP_TRAIT_SAMPLE_OUTPUT ?= $(BUILD_DIR)/urmp_trait_sample.out
URMP_DOWNLOAD_CONNECTIONS ?= 8
URMP_ARCHIVE_URL ?= https://www.kaggle.com/api/v1/datasets/download/alonhaviv/multi-modal-music-performance-urmp
URMP_SAX_EXACT_FIXTURE_DIR ?= $(BUILD_DIR)/urmp_sax_exact_fixture
URMP_SAX_EXACT_FIXTURE_MANIFEST ?= $(URMP_SAX_EXACT_FIXTURE_DIR)/manifest.tsv
URMP_SAX_EXACT_ATTRIBUTE_TSV ?= $(BUILD_DIR)/urmp_sax_exact_attributes.tsv
URMP_SAX_EXACT_OUTPUT ?= $(BUILD_DIR)/urmp_sax_exact.out
URMP_SAX_EXACT_MIN_SAMPLES ?= 250
URMP_SAX_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/urmp_sax_full_mix_attributes.tsv
URMP_SAX_FULL_MIX_OUTPUT ?= $(BUILD_DIR)/urmp_sax_full_mix.out
URMP_SAX_FULL_MIX_MIN_SAMPLES ?= $(URMP_SAX_EXACT_MIN_SAMPLES)
URMP_BASS_TIMING_AUDIT ?= $(BUILD_DIR)/urmp_bass_timing_audit.tsv
URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT ?= $(BUILD_DIR)/urmp_good_sounds_sax_shared_patterns.txt
DETECTION_ACCURACY_URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_ARG = --urmp-good-sounds-sax-shared-pattern-audit "$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)" --urmp-bass-timing-audit "$(URMP_BASS_TIMING_AUDIT)" $(DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG) $(DETECTION_ACCURACY_DOMINANT_SEVENTH_EXTENSION_AUDIT_ARG)
OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT ?= $(BUILD_DIR)/octave_correction_cross_corpus_audit.txt
DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG = --octave-correction-cross-corpus-audit "$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)"
DOMINANT_SEVENTH_EXTENSION_AUDIT ?= $(BUILD_DIR)/dominant_seventh_extension_audit.txt
DETECTION_ACCURACY_DOMINANT_SEVENTH_EXTENSION_AUDIT_ARG = --dominant-seventh-extension-audit "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)"
GLOBAL_CHORD_CONFIDENCE_AUDIT ?= $(BUILD_DIR)/global_chord_confidence_audit.txt
DETECTION_ACCURACY_GLOBAL_CHORD_CONFIDENCE_AUDIT_ARG = --global-chord-confidence-audit "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)"
SAME_ROOT_GUITAR_QUALITY_AUDIT ?= $(BUILD_DIR)/same_root_guitar_quality_audit.txt
OWNER_CLASSIFIER_LOCO_AUDIT ?= $(BUILD_DIR)/owner_classifier_loco_audit.txt
OWNER_CLASSIFIER_FEATURE_PROFILE ?= scores
OWNER_CLASSIFIER_QUALITY_LOCO_AUDIT ?= $(BUILD_DIR)/owner_classifier_quality_loco_audit.txt
OWNER_SCORE_CALIBRATION_LOCO_AUDIT ?= $(BUILD_DIR)/owner_score_calibration_loco_audit.txt
DRUM_PRIMARY_LOCO_AUDIT ?= $(BUILD_DIR)/drum_primary_loco_audit.txt
DRUM_FALSE_POSITIVE_CAP_AUDIT ?= $(BUILD_DIR)/drum_false_positive_cap_audit.txt
MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT ?= $(BUILD_DIR)/mdb_full_mix_false_positive_cap_audit.txt
MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT ?= $(BUILD_DIR)/mdb_full_mix_competing_active_context_audit.txt
MDB_COMPETING_ACTIVE_CONTEXT_RUNTIME_REPLAYED ?= kick when snare/kick>=1.18987
MDB_COMPETING_ACTIVE_CONTEXT_RUNTIME_GAINED ?=
MDB_SOURCE_SCOPED_CONTEXT_AUDIT ?= $(BUILD_DIR)/mdb_source_scoped_context_audit.txt
MDB_SOURCE_SCOPED_CONTEXT_ARGS ?=
DRUM_RECOVERY_CANDIDATE_AUDIT ?= $(BUILD_DIR)/drum_recovery_candidate_audit.txt
DRUM_FALSE_POSITIVE_CONTEXT_AUDIT ?= $(BUILD_DIR)/drum_false_positive_context_audit.txt
CHORD_PRIMARY_COMPONENT_AUDIT ?= $(BUILD_DIR)/chord_primary_component_audit.txt
CHORD_PRIMARY_COMPONENT_ARGS ?=
POLYPHONIC_CANDIDATE_CAPACITY_AUDIT ?= $(BUILD_DIR)/polyphonic_candidate_capacity_audit.txt
HARMONIC_PRODUCT_OCTAVE_AUDIT ?= $(BUILD_DIR)/harmonic_product_octave_audit.txt
SATB_RELATIVE_CHROMA_SELECTOR_AUDIT ?= $(BUILD_DIR)/satb_relative_chroma_selector_audit.txt
DETECTION_ACCURACY_OWNER_CLASSIFIER_LOCO_AUDIT_ARG = --owner-classifier-loco-audit "$(OWNER_CLASSIFIER_LOCO_AUDIT)" --owner-classifier-quality-loco-audit "$(OWNER_CLASSIFIER_QUALITY_LOCO_AUDIT)"
DETECTION_ACCURACY_OWNER_SCORE_CALIBRATION_LOCO_AUDIT_ARG = --owner-score-calibration-loco-audit "$(OWNER_SCORE_CALIBRATION_LOCO_AUDIT)"
DETECTION_ACCURACY_DRUM_FALSE_POSITIVE_CAP_AUDIT_ARG = --drum-false-positive-cap-audit "$(DRUM_FALSE_POSITIVE_CAP_AUDIT)"
DETECTION_ACCURACY_MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT_ARG = --mdb-full-mix-false-positive-cap-audit "$(MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT)"
DETECTION_ACCURACY_MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT_ARG = --mdb-full-mix-competing-active-context-audit "$(MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT)"
DETECTION_ACCURACY_DRUM_FALSE_POSITIVE_CONTEXT_AUDIT_ARG = --drum-false-positive-context-audit "$(DRUM_FALSE_POSITIVE_CONTEXT_AUDIT)"
DETECTION_ACCURACY_DRUM_RECOVERY_CANDIDATE_AUDIT_ARG = $(if $(wildcard $(DRUM_RECOVERY_CANDIDATE_AUDIT)),--drum-recovery-candidate-audit "$(DRUM_RECOVERY_CANDIDATE_AUDIT)")
DETECTION_ACCURACY_CHORD_PRIMARY_COMPONENT_AUDIT_ARG = --chord-primary-component-audit "$(CHORD_PRIMARY_COMPONENT_AUDIT)"
DETECTION_ACCURACY_POLYPHONIC_CANDIDATE_CAPACITY_AUDIT_ARG = --polyphonic-candidate-capacity-audit "$(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT)"
DETECTION_ACCURACY_HARMONIC_PRODUCT_OCTAVE_AUDIT_ARG = --harmonic-product-octave-audit "$(HARMONIC_PRODUCT_OCTAVE_AUDIT)"
DETECTION_ACCURACY_SATB_RELATIVE_CHROMA_SELECTOR_AUDIT_ARG = --satb-relative-chroma-selector-audit "$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)"
DETECTION_ACCURACY_SAME_ROOT_GUITAR_QUALITY_AUDIT_ARG = --same-root-guitar-quality-audit "$(SAME_ROOT_GUITAR_QUALITY_AUDIT)" $(DETECTION_ACCURACY_OWNER_CLASSIFIER_LOCO_AUDIT_ARG) $(DETECTION_ACCURACY_OWNER_SCORE_CALIBRATION_LOCO_AUDIT_ARG) --drum-primary-loco-audit "$(DRUM_PRIMARY_LOCO_AUDIT)" $(DETECTION_ACCURACY_DRUM_FALSE_POSITIVE_CAP_AUDIT_ARG) $(DETECTION_ACCURACY_MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT_ARG) $(DETECTION_ACCURACY_MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT_ARG) $(DETECTION_ACCURACY_DRUM_FALSE_POSITIVE_CONTEXT_AUDIT_ARG) $(DETECTION_ACCURACY_DRUM_RECOVERY_CANDIDATE_AUDIT_ARG) $(DETECTION_ACCURACY_CHORD_PRIMARY_COMPONENT_AUDIT_ARG) $(DETECTION_ACCURACY_POLYPHONIC_CANDIDATE_CAPACITY_AUDIT_ARG) $(DETECTION_ACCURACY_HARMONIC_PRODUCT_OCTAVE_AUDIT_ARG) $(DETECTION_ACCURACY_SATB_RELATIVE_CHROMA_SELECTOR_AUDIT_ARG) $(DETECTION_ACCURACY_29K_DRUMS_INSPECTION_ARG) $(DETECTION_ACCURACY_29K_DRUMS_MEASUREMENT_ARG) $(DETECTION_ACCURACY_29K_DRUMS_PRIMARY_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_VIRTUOSITY_DRUMS_MEASUREMENT_ARG)
DETECTION_ACCURACY_GUITARSET_ATTRIBUTE_ARG = $(if $(wildcard $(GUITARSET_ATTRIBUTE_TSV)),--guitarset-attribute-input "$(GUITARSET_ATTRIBUTE_TSV)") $(if $(wildcard $(GUITAR_TECHS_ISOLATED_VISUAL_AUDIT)),--guitar-techs-isolated-visual-audit "$(GUITAR_TECHS_ISOLATED_VISUAL_AUDIT)") $(if $(wildcard $(IDMT_GUITAR_ISOLATED_VISUAL_AUDIT)),--idmt-guitar-isolated-visual-audit "$(IDMT_GUITAR_ISOLATED_VISUAL_AUDIT)") $(if $(wildcard $(AGPT_GUITAR_MEASUREMENT)),--agpt-guitar-measurement "$(AGPT_GUITAR_MEASUREMENT)") $(if $(wildcard $(AGPT_GUITAR_VISUAL_PRIMARY_MEASUREMENT)),--agpt-guitar-visual-primary "$(AGPT_GUITAR_VISUAL_PRIMARY_MEASUREMENT)") $(if $(wildcard $(AGPT_GUITAR_VISUAL_PATTERN_REPORT)),--agpt-guitar-visual-mining "$(AGPT_GUITAR_VISUAL_PATTERN_REPORT)") $(if $(wildcard $(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT)),--cross-corpus-guitar-primary-order-audit "$(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT)") $(DETECTION_ACCURACY_FSD50K_RIM_METADATA_ARG)
DETECTION_ACCURACY_REPORT ?= docs/detection_accuracy_report.md
DETECTION_ACCURACY_29K_DRUMS_INSPECTION_ARG = $(if $(wildcard $(SAMPLES29K_DRUMS_INSPECTION)),--29k-drums-inspection "$(SAMPLES29K_DRUMS_INSPECTION)")
DETECTION_ACCURACY_29K_DRUMS_MEASUREMENT_ARG = $(if $(wildcard $(SAMPLES29K_DRUMS_MEASUREMENT)),--29k-drums-measurement "$(SAMPLES29K_DRUMS_MEASUREMENT)")
DETECTION_ACCURACY_29K_DRUMS_PRIMARY_ATTRIBUTE_ARG = $(if $(wildcard $(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)),--29k-drums-primary-attributes "$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)")
DETECTION_ACCURACY_VIRTUOSITY_DRUMS_MEASUREMENT_ARG = $(if $(wildcard $(VIRTUOSITY_DRUMS_MEASUREMENT)),--virtuosity-drums-measurement "$(VIRTUOSITY_DRUMS_MEASUREMENT)")
DETECTION_ACCURACY_FSD50K_RIM_METADATA_ARG = $(if $(wildcard $(FSD50K_RIM_METADATA_AUDIT)),--fsd50k-rim-metadata-audit "$(FSD50K_RIM_METADATA_AUDIT)") $(DETECTION_ACCURACY_COMMONS_RIMSHOT_CANDIDATE_ARG)
DETECTION_ACCURACY_COMMONS_RIMSHOT_CANDIDATE_ARG = $(if $(wildcard $(COMMONS_RIMSHOT_CANDIDATE_AUDIT)),--commons-rimshot-candidate-audit "$(COMMONS_RIMSHOT_CANDIDATE_AUDIT)")
DETECTION_ACCURACY_PIXABAY_RIMSHOT_MEASUREMENT_ARG = $(if $(wildcard $(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)),--pixabay-rimshot-measurement-audit "$(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)")
DETECTION_ACCURACY_PIXABAY_RIMSHOT_F_MEASUREMENT_ARG = $(if $(wildcard $(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)),--pixabay-rimshot-f-measurement-audit "$(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)")
DETECTION_ACCURACY_PIXABAY_RIM_SHOT_MEASUREMENT_ARG = $(if $(wildcard $(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)),--pixabay-rim-shot-measurement-audit "$(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)")
DETECTION_ACCURACY_FSD50K_RIM_METADATA_ARG += $(DETECTION_ACCURACY_PIXABAY_RIMSHOT_MEASUREMENT_ARG)
DETECTION_ACCURACY_FSD50K_RIM_METADATA_ARG += $(DETECTION_ACCURACY_PIXABAY_RIMSHOT_F_MEASUREMENT_ARG)
DETECTION_ACCURACY_FSD50K_RIM_METADATA_ARG += $(DETECTION_ACCURACY_PIXABAY_RIM_SHOT_MEASUREMENT_ARG)
HIGH_VOCAL_OCTAVE_AUDIT ?= $(BUILD_DIR)/high_vocal_octave_evidence.txt
HIGH_SOPRANO_VOCAL_MIRROR_AUDIT ?= $(BUILD_DIR)/high_soprano_vocal_mirror_audit.txt
DETECTION_ACCURACY_HIGH_VOCAL_OCTAVE_AUDIT_ARG = $(if $(wildcard $(HIGH_VOCAL_OCTAVE_AUDIT)),--high-vocal-octave-audit "$(HIGH_VOCAL_OCTAVE_AUDIT)")
DETECTION_ACCURACY_HIGH_SOPRANO_VOCAL_MIRROR_AUDIT_ARG = $(if $(wildcard $(HIGH_SOPRANO_VOCAL_MIRROR_AUDIT)),--high-soprano-vocal-mirror-audit "$(HIGH_SOPRANO_VOCAL_MIRROR_AUDIT)")
GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT ?= $(BUILD_DIR)/guitar_chord_primary_display_audit.txt
DETECTION_ACCURACY_GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT_ARG = $(if $(wildcard $(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)),--guitar-chord-primary-display-audit "$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)")
GUITAR_CHORD_TONE_RECOVERY_AUDIT ?= $(BUILD_DIR)/guitar_chord_tone_recovery_audit.txt
DETECTION_ACCURACY_GUITAR_CHORD_TONE_RECOVERY_AUDIT_ARG = $(if $(wildcard $(GUITAR_CHORD_TONE_RECOVERY_AUDIT)),--guitar-chord-tone-recovery-audit "$(GUITAR_CHORD_TONE_RECOVERY_AUDIT)")
DETECTION_ACCURACY_IRMAS_LABELLED_ARG = $(if $(wildcard $(IRMAS_ATTRIBUTE_OUTPUT)),--irmas-labelled-input "$(IRMAS_ATTRIBUTE_OUTPUT)")
DETECTION_ACCURACY_MUSICNET_ROUTING_ARG = $(if $(wildcard $(MUSICNET_ROUTING_OUTPUT)),--musicnet-routing-input "$(MUSICNET_ROUTING_OUTPUT)")
DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_ARG = $(if $(wildcard $(DAGSTUHL_CHOIRSET_MEASUREMENT_OUTPUT)),--dagstuhl-choirset-input "$(DAGSTUHL_CHOIRSET_MEASUREMENT_OUTPUT)")
DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_VALIDATION_ARG = $(if $(wildcard $(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT)),--dagstuhl-choirset-validation "$(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT)")
DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_INSPECTION_ARG = $(if $(wildcard $(DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT)),--dagstuhl-choirset-inspection "$(DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT)")
DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_EXTRACT_ARG = $(if $(wildcard $(DAGSTUHL_CHOIRSET_EXTRACT_DIR)/DagstuhlChoirSet/README.md),--dagstuhl-choirset-extraction "$(DAGSTUHL_CHOIRSET_EXTRACT_DIR)/DagstuhlChoirSet/README.md")
DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_MANIFEST_ARG = $(if $(wildcard $(DAGSTUHL_CHOIRSET_PREPARED_DIR)/manifest.json),--dagstuhl-choirset-manifest "$(DAGSTUHL_CHOIRSET_PREPARED_DIR)/manifest.json")
# The full MAESTRO replay is a verbose diagnostic stream, whereas the dashboard
# requires a completed shard-summary contract.  Its attribute TSV and manifest
# remain eligible evidence; do not misparse a partial/verbose log as a summary.
DETECTION_ACCURACY_MAESTRO_REAL_MEASUREMENT_ARG =
DETECTION_ACCURACY_MAESTRO_REAL_ATTRIBUTE_ARG = $(if $(wildcard $(MAESTRO_REAL_ATTRIBUTE_TSV)),--maestro-real-attribute-input "$(MAESTRO_REAL_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_INDEPENDENT_PIANO_STATE_ARG = $(if $(wildcard $(MAESTRO_REAL_CHORD_STATE_OUTPUT)),--independent-piano-chord-state-evidence "$(MAESTRO_REAL_CHORD_STATE_OUTPUT)")
DETECTION_ACCURACY_INDEPENDENT_PIANO_STABILITY_ARG = $(if $(wildcard $(INDEPENDENT_PIANO_CHORD_STABILITY_OUTPUT)),--independent-piano-chord-stability-evidence "$(INDEPENDENT_PIANO_CHORD_STABILITY_OUTPUT)")
INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT ?= $(BUILD_DIR)/independent_piano_exact_chord_fallback.txt
DETECTION_ACCURACY_INDEPENDENT_PIANO_EXACT_FALLBACK_ARG = $(if $(wildcard $(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)),--independent-piano-exact-chord-fallback-audit "$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_CONFIRMATION_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_CONFIRMATION_AUDIT)),--piano-chord-confirmation-audit "$(PIANO_CHORD_CONFIRMATION_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_CONFIRM3_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_CONFIRM3_AUDIT)),--piano-chord-confirm3-audit "$(PIANO_CHORD_CONFIRM3_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_TONE018_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_TONE018_AUDIT)),--piano-chord-tone018-audit "$(PIANO_CHORD_TONE018_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_MARGIN060_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_MARGIN060_AUDIT)),--piano-chord-margin060-audit "$(PIANO_CHORD_MARGIN060_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_BASSBONUS000_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_BASSBONUS000_AUDIT)),--piano-chord-bassbonus000-audit "$(PIANO_CHORD_BASSBONUS000_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT)),--piano-chord-display-confidence-audit "$(PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT)")
DETECTION_ACCURACY_PIANO_CHORD_DISPLAY_GATE_AUDIT_ARG = $(if $(wildcard $(PIANO_CHORD_DISPLAY_GATE_AUDIT)),--piano-chord-display-gate-audit "$(PIANO_CHORD_DISPLAY_GATE_AUDIT)")
DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG = $(if $(wildcard $(MAESTRO_REAL_SAMPLE_DIR)/maestro-v3.0.0.csv),--maestro-real-manifest "$(MAESTRO_REAL_SAMPLE_DIR)/maestro-v3.0.0.csv") $(DETECTION_ACCURACY_MAESTRO_REAL_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_INDEPENDENT_PIANO_STATE_ARG) $(DETECTION_ACCURACY_INDEPENDENT_PIANO_STABILITY_ARG) $(DETECTION_ACCURACY_INDEPENDENT_PIANO_EXACT_FALLBACK_ARG) $(DETECTION_ACCURACY_PIANO_CHORD_CONFIRMATION_AUDIT_ARG) $(DETECTION_ACCURACY_PIANO_CHORD_CONFIRM3_AUDIT_ARG) $(DETECTION_ACCURACY_PIANO_CHORD_TONE018_AUDIT_ARG) $(DETECTION_ACCURACY_PIANO_CHORD_MARGIN060_AUDIT_ARG) $(DETECTION_ACCURACY_PIANO_CHORD_BASSBONUS000_AUDIT_ARG)
DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG += $(DETECTION_ACCURACY_PIANO_CHORD_DISPLAY_GATE_AUDIT_ARG)
DETECTION_ACCURACY_KRAISLER_ARCHIVE_ARG = $(if $(wildcard $(KRAISLER_ARCHIVE)),--kraisler-archive "$(KRAISLER_ARCHIVE)")
DETECTION_ACCURACY_KRAISLER_EXTRACT_ARG = $(if $(wildcard $(KRAISLER_EXTRACT_DIR)),--kraisler-extraction "$(KRAISLER_EXTRACT_DIR)")
DETECTION_ACCURACY_KRAISLER_MANIFEST_ARG = $(if $(wildcard $(KRAISLER_PREPARED_DIR)/manifest.json),--kraisler-manifest "$(KRAISLER_PREPARED_DIR)/manifest.json")
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG = $(if $(wildcard $(KRAISLER_MEASUREMENT_OUTPUT)),--kraisler-measurement "$(KRAISLER_MEASUREMENT_OUTPUT)") $(DETECTION_ACCURACY_KRAISLER_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_ANNOTATIONS_ARG) $(DETECTION_ACCURACY_GTZAN_RHYTHM_BPM_ARG) $(DETECTION_ACCURACY_BEAT_THIS_GTZAN_ARG) $(DETECTION_ACCURACY_BEAT_THIS_BALLROOM_ARG) $(DETECTION_ACCURACY_BEAT_THIS_FILOBASS_ARG) $(DETECTION_ACCURACY_FILOBASS_BPM_ARG) $(DETECTION_ACCURACY_FILOBASS_ONSET_DIAGNOSTIC_ARG) $(DETECTION_ACCURACY_EGMD_BPM_ARG) $(DETECTION_ACCURACY_IDMT_BASS_TEMPO_METADATA_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_CANDOMBE_BPM_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_IMMEDIATE_SOURCE_BPM_3S_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_CANDOMBE_INSPECTION_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_THREE_TEMPO_TRACKER_CONSENSUS_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_BEAT_THIS_ROLLING_BALLROOM_ARG) $(DETECTION_ACCURACY_BEAT_THIS_ROLLING_FILOBASS_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_BALLROOM_ARG) $(DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_FILOBASS_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_INTERVAL_GATE_ARG)
DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG += $(DETECTION_ACCURACY_BEAT_THIS_SIDECAR_BALLROOM_ARG) $(DETECTION_ACCURACY_BEAT_THIS_SIDECAR_FILOBASS_ARG)
DETECTION_ACCURACY_KRAISLER_BPM_ARG = $(if $(wildcard $(KRAISLER_BPM_LOG)),--kraisler-bpm-input "$(KRAISLER_BPM_LOG)")
DETECTION_ACCURACY_BALLROOM_BPM_ARG = $(if $(wildcard $(BALLROOM_BPM_LOG)),--ballroom-bpm-input "$(BALLROOM_BPM_LOG)")
DETECTION_ACCURACY_BALLROOM_ANNOTATIONS_ARG = $(if $(wildcard $(BALLROOM_ANNOTATIONS_DIR)/.git),--ballroom-annotations "$(BALLROOM_ANNOTATIONS_DIR)")
DETECTION_ACCURACY_GTZAN_RHYTHM_BPM_ARG = $(if $(wildcard $(GTZAN_RHYTHM_BPM_LOG)),--gtzan-rhythm-bpm-input "$(GTZAN_RHYTHM_BPM_LOG)")
DETECTION_ACCURACY_BEAT_THIS_GTZAN_ARG = $(if $(wildcard $(BEAT_THIS_DIAGNOSTIC_LOG)),--beat-this-gtzan-bpm-input "$(BEAT_THIS_DIAGNOSTIC_LOG)")
DETECTION_ACCURACY_BEAT_THIS_BALLROOM_ARG = $(if $(wildcard $(BEAT_THIS_BALLROOM_LOG)),--beat-this-ballroom-bpm-input "$(BEAT_THIS_BALLROOM_LOG)")
DETECTION_ACCURACY_BEAT_THIS_FILOBASS_ARG = $(if $(wildcard $(BEAT_THIS_FILOBASS_LOG)),--beat-this-filobass-bpm-input "$(BEAT_THIS_FILOBASS_LOG)")
DETECTION_ACCURACY_BEAT_THIS_ROLLING_BALLROOM_ARG = $(if $(wildcard $(BEAT_THIS_ROLLING_BALLROOM_LOG)),--beat-this-rolling-ballroom-bpm-input "$(BEAT_THIS_ROLLING_BALLROOM_LOG)")
DETECTION_ACCURACY_BEAT_THIS_ROLLING_FILOBASS_ARG = $(if $(wildcard $(BEAT_THIS_ROLLING_FILOBASS_LOG)),--beat-this-rolling-filobass-bpm-input "$(BEAT_THIS_ROLLING_FILOBASS_LOG)")
DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_BALLROOM_ARG = $(if $(wildcard $(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)),--beat-this-continuous-ballroom-bpm-input "$(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)")
DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_FILOBASS_ARG = $(if $(wildcard $(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)),--beat-this-continuous-filobass-bpm-input "$(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)")
DETECTION_ACCURACY_BEAT_THIS_CONTINUOUS_INTERVAL_GATE_ARG = $(if $(wildcard $(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)),--beat-this-continuous-interval-gate-audit "$(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)")
DETECTION_ACCURACY_BEAT_THIS_SIDECAR_BALLROOM_ARG = $(if $(wildcard $(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)),--beat-this-sidecar-ballroom-audit "$(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)")
DETECTION_ACCURACY_BEAT_THIS_SIDECAR_FILOBASS_ARG = $(if $(wildcard $(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)),--beat-this-sidecar-filobass-audit "$(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)")
DETECTION_ACCURACY_THREE_TEMPO_TRACKER_CONSENSUS_ARG = $(if $(wildcard $(THREE_TEMPO_TRACKER_CONSENSUS_LOG)),--three-tempo-tracker-consensus-input "$(THREE_TEMPO_TRACKER_CONSENSUS_LOG)")
DETECTION_ACCURACY_HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_ARG = $(if $(wildcard $(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)),--high-tempo-three-tracker-consensus-input "$(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)")
DETECTION_ACCURACY_CANDOMBE_BPM_ARG = $(if $(wildcard $(CANDOMBE_BPM_LOG)),--candombe-bpm-input "$(CANDOMBE_BPM_LOG)")
DETECTION_ACCURACY_CANDOMBE_INSPECTION_ARG = $(if $(wildcard $(CANDOMBE_INSPECTION_OUTPUT)),--candombe-inspection "$(CANDOMBE_INSPECTION_OUTPUT)")
DETECTION_ACCURACY_FILOBASS_BPM_ARG = $(if $(wildcard $(FILOBASS_BPM_LOG)),--filobass-bpm-input "$(FILOBASS_BPM_LOG)")
DETECTION_ACCURACY_FILOBASS_ONSET_DIAGNOSTIC_ARG = $(if $(wildcard $(FILOBASS_ONSET_DIAGNOSTICS)),--filobass-onset-diagnostic-input "$(FILOBASS_ONSET_DIAGNOSTICS)")
DETECTION_ACCURACY_IMMEDIATE_SOURCE_BPM_3S_ARG = $(if $(wildcard $(IMMEDIATE_SOURCE_BPM_3S_AUDIT)),--immediate-source-bpm-3s-audit "$(IMMEDIATE_SOURCE_BPM_3S_AUDIT)")
DETECTION_ACCURACY_BTT_BALLROOM_ARG = $(if $(wildcard $(BTT_BALLROOM_LOG)),--btt-ballroom-bpm-input "$(BTT_BALLROOM_LOG)")
DETECTION_ACCURACY_BTT_FILOBASS_ARG = $(if $(wildcard $(BTT_FILOBASS_LOG)),--btt-filobass-bpm-input "$(BTT_FILOBASS_LOG)")
DETECTION_ACCURACY_BTT_EGMD_ARG = $(if $(wildcard $(BTT_EGMD_LOG)),--btt-egmd-bpm-input "$(BTT_EGMD_LOG)")
DETECTION_ACCURACY_BTT_HIGH_TEMPO_BALLROOM_ARG = $(if $(wildcard $(BTT_HIGH_TEMPO_BALLROOM_LOG)),--btt-high-tempo-ballroom-bpm-input "$(BTT_HIGH_TEMPO_BALLROOM_LOG)")
DETECTION_ACCURACY_BTT_HIGH_TEMPO_FILOBASS_ARG = $(if $(wildcard $(BTT_HIGH_TEMPO_FILOBASS_LOG)),--btt-high-tempo-filobass-bpm-input "$(BTT_HIGH_TEMPO_FILOBASS_LOG)")
DETECTION_ACCURACY_BTT_ARGS = $(DETECTION_ACCURACY_BTT_BALLROOM_ARG) $(DETECTION_ACCURACY_BTT_FILOBASS_ARG) $(DETECTION_ACCURACY_BTT_EGMD_ARG) $(DETECTION_ACCURACY_BTT_HIGH_TEMPO_BALLROOM_ARG) $(DETECTION_ACCURACY_BTT_HIGH_TEMPO_FILOBASS_ARG)
DETECTION_ACCURACY_EGMD_BPM_ARG = $(if $(wildcard $(EGMD_BPM_LOG)),--egmd-bpm-input "$(EGMD_BPM_LOG)")
DETECTION_ACCURACY_IDMT_BASS_TEMPO_METADATA_ARG = $(if $(wildcard $(IDMT_BASS_LINES_TEMPO_METADATA)),--idmt-bass-tempo-metadata-input "$(IDMT_BASS_LINES_TEMPO_METADATA)")
DETECTION_ACCURACY_CHORAL_SINGING_DATASET_ARG = $(if $(wildcard $(CHORAL_SINGING_DATASET_ARCHIVE)),--choral-singing-dataset-archive "$(CHORAL_SINGING_DATASET_ARCHIVE)")
DETECTION_ACCURACY_CHORAL_SINGING_DATASET_EXTRACT_ARG = $(if $(wildcard $(CHORAL_SINGING_DATASET_EXTRACT_DIR)/ChoralSingingDataset/README.txt),--choral-singing-dataset-extraction "$(CHORAL_SINGING_DATASET_EXTRACT_DIR)/ChoralSingingDataset/README.txt")
DETECTION_ACCURACY_CHORAL_SINGING_DATASET_INSPECTION_ARG = $(if $(wildcard $(CHORAL_SINGING_DATASET_INSPECTION_OUTPUT)),--choral-singing-dataset-inspection "$(CHORAL_SINGING_DATASET_INSPECTION_OUTPUT)")
DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MANIFEST_ARG = $(if $(wildcard $(CHORAL_SINGING_DATASET_PREPARED_DIR)/manifest.json),--choral-singing-dataset-manifest "$(CHORAL_SINGING_DATASET_PREPARED_DIR)/manifest.json")
DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MEASUREMENT_ARG = $(if $(wildcard $(CHORAL_SINGING_DATASET_MEASUREMENT_OUTPUT)),--choral-singing-dataset-measurement "$(CHORAL_SINGING_DATASET_MEASUREMENT_OUTPUT)")
DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG = $(if $(wildcard $(ESMUC_CHOIR_DATASET_ARCHIVE)),--esmuc-choir-dataset-archive "$(ESMUC_CHOIR_DATASET_ARCHIVE)")
DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG = $(if $(wildcard $(ESMUC_CHOIR_DATASET_EXTRACT_DIR)/README.md),--esmuc-choir-dataset-extraction "$(ESMUC_CHOIR_DATASET_EXTRACT_DIR)/README.md")
DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MANIFEST_ARG = $(if $(wildcard $(ESMUC_CHOIR_DATASET_PREPARED_DIR)/manifest.json),--esmuc-choir-dataset-manifest "$(ESMUC_CHOIR_DATASET_PREPARED_DIR)/manifest.json")
DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MEASUREMENT_ARG = $(if $(wildcard $(ESMUC_CHOIR_DATASET_MEASUREMENT_OUTPUT)),--esmuc-choir-dataset-measurement "$(ESMUC_CHOIR_DATASET_MEASUREMENT_OUTPUT)")
DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_PATTERN_REPORT_ARG = $(if $(wildcard $(ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)),--esmuc-choir-dataset-pattern-report "$(ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)")
DETECTION_ACCURACY_MIR1K_DATASET_ARCHIVE_ARG = $(if $(wildcard $(MIR1K_DATASET_ARCHIVE)),--mir1k-dataset-archive "$(MIR1K_DATASET_ARCHIVE)")
DETECTION_ACCURACY_MIR1K_DATASET_EXTRACT_ARG = $(if $(wildcard $(MIR1K_DATASET_EXTRACT_DIR)/.mir1k-extraction-complete),--mir1k-dataset-extraction "$(MIR1K_DATASET_EXTRACT_DIR)/.mir1k-extraction-complete")
DETECTION_ACCURACY_OTHER_DETECTION_ARG := --other-detection-disabled
DETECTION_ACCURACY_BASIC_PITCH_ONNX_ARGS = --basic-pitch-onnx-true-miss-replay "$(BASIC_PITCH_ONNX_CHOIR_REPLAY)" --basic-pitch-onnx-full-replay "$(BASIC_PITCH_ONNX_CHOIR_FULL_REPLAY)" --basic-pitch-onnx-safe-replay "$(BASIC_PITCH_ONNX_CHOIR_SAFE_REPLAY)" --basic-pitch-onnx-choir-strict-replay "$(BASIC_PITCH_ONNX_CHOIR_STRICT_REPLAY)" --basic-pitch-onnx-musicnet-strict-replay "$(BASIC_PITCH_ONNX_MUSICNET_STRICT_REPLAY)" --basic-pitch-onnx-cross-domain-safe-replay "$(BASIC_PITCH_ONNX_CROSS_DOMAIN_SAFE_REPLAY)" --basic-pitch-onnx-cross-domain-worker-safe-replay "$(BASIC_PITCH_ONNX_CROSS_DOMAIN_WORKER_SAFE_REPLAY)"
DETECTION_ACCURACY_MIR1K_FULL_MIX_ARG = $(if $(wildcard $(MIR1K_DATASET_ATTRIBUTE_OUTPUT)),--mir1k-full-mix-input "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)")
DETECTION_ACCURACY_SCMS_ARCHIVE_ARG = $(if $(wildcard $(SCMS_DATASET_VALIDATION_OUTPUT)),--scms-dataset-archive "$(SCMS_DATASET_ARCHIVE)")
DETECTION_ACCURACY_SCMS_INSPECTION_ARG = $(if $(wildcard $(SCMS_DATASET_INSPECTION_OUTPUT)),--scms-dataset-inspection "$(SCMS_DATASET_INSPECTION_OUTPUT)")
DETECTION_ACCURACY_SCMS_FULL_MIX_ARG = $(if $(wildcard $(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete),--scms-dataset-extraction "$(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete") $(if $(wildcard $(SCMS_DATASET_SAMPLE_DIR)/manifest.tsv),--scms-dataset-manifest "$(SCMS_DATASET_SAMPLE_DIR)/manifest.tsv") $(if $(wildcard $(SCMS_DATASET_MEASUREMENT_OUTPUT)),--scms-dataset-measurement "$(SCMS_DATASET_MEASUREMENT_OUTPUT)") $(if $(wildcard $(SCMS_DATASET_ATTRIBUTE_OUTPUT)),--scms-full-mix-input "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)") $(if $(wildcard $(SCMS_VOCAL_OTHER_ROUTE_AUDIT)),--scms-vocal-other-route-audit "$(SCMS_VOCAL_OTHER_ROUTE_AUDIT)")
DETECTION_ACCURACY_VOCAL_EXACT_NOTE_CROSS_CORPUS_ARG = $(if $(wildcard $(VOCAL_EXACT_NOTE_CROSS_CORPUS_OUTPUT)),--vocal-exact-note-cross-corpus-input "$(VOCAL_EXACT_NOTE_CROSS_CORPUS_OUTPUT)")
DETECTION_ACCURACY_PHILHARMONIA_FULL_ARG = $(if $(wildcard $(PHILHARMONIA_FULL_ATTRIBUTE_TSV)),--philharmonia-full-input "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_IOWA_ORCHESTRA_FULL_ARG = $(if $(wildcard $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)),--iowa-orchestra-full-input "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_TINYSOL_WIND_EXACT_ARG = $(if $(wildcard $(TINYSOL_WIND_EXACT_ATTRIBUTE_TSV)),--tinysol-wind-exact-input "$(TINYSOL_WIND_EXACT_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_IOWA_SAX_FULL_MIX_ARG = $(if $(wildcard $(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)),--iowa-sax-full-mix-input "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_IOWA_PIANO_FULL_MIX_ARG = $(if $(wildcard $(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)),--iowa-piano-full-mix-input "$(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_TINYSOL_SAX_FULL_MIX_ARG = $(if $(wildcard $(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)),--tinysol-sax-full-mix-input "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_MIX_ARG = $(if $(wildcard $(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)),--tinysol-flute-full-mix-input "$(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_ARG = $(DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_MIX_ARG)
DETECTION_ACCURACY_REAL_A2S_TENOR_SCALE_ARG = $(if $(wildcard $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)),--real-a2s-tenor-scale-input "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_URMP_SAX_EXACT_ARG = $(if $(wildcard $(URMP_SAX_EXACT_ATTRIBUTE_TSV)),--urmp-sax-exact-input "$(URMP_SAX_EXACT_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_URMP_SAX_FULL_MIX_ARG = $(if $(wildcard $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)),--urmp-sax-full-mix-input "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_CHORD_TSVS ?= $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV) $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(GUITARSET_ATTRIBUTE_TSV)
DETECTION_ACCURACY_CHORD_ARGS = $(foreach path,$(wildcard $(DETECTION_ACCURACY_CHORD_TSVS)),--chord-input "$(path)")
# Chord-route candidates must be safe against every cached labelled guitar
# corpus, not merely against the source corpus that happened to expose them.
# IDMT-SMT-Guitar contributes independent, real electric-guitar ownership
# evidence even though its monophonic clips do not supply a chord target.
# The explicit source path added by each route target below also covers the
# smaller GAPS subset, which is intentionally not part of the accuracy rollup.
GUITAR_CHORD_ROUTE_PROTECTED_TSVS ?= $(DETECTION_ACCURACY_CHORD_TSVS) $(EGFXSET_GUITAR_ATTRIBUTE_TSV) $(IDMT_GUITAR_ATTRIBUTE_TSV)
GUITAR_CHORD_ROUTE_PROTECTED_ARGS = $(foreach path,$(wildcard $(GUITAR_CHORD_ROUTE_PROTECTED_TSVS)),--protected-path "$(path)")
DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV ?= $(BUILD_DIR)/vocadito_full_mix_attributes.tsv
DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG = $(if $(wildcard $(DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV)),--vocal-full-mix-input "$(DETECTION_ACCURACY_VOCAL_FULL_MIX_TSV)")
DETECTION_ACCURACY_VOCALSET_FULL_MIX_TSV ?= $(BUILD_DIR)/vocalset_full_mix_attributes.tsv
DETECTION_ACCURACY_VOCALSET_FULL_MIX_ARG = $(if $(wildcard $(DETECTION_ACCURACY_VOCALSET_FULL_MIX_TSV)),--vocalset-full-mix-input "$(DETECTION_ACCURACY_VOCALSET_FULL_MIX_TSV)")
DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_TSV ?= $(BUILD_DIR)/vocalset_clean_vowel_attributes.tsv
DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_ARG = $(if $(wildcard $(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_TSV)),--focused-vocalset-clean-vowel-input "$(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_TSV)")
DETECTION_ACCURACY_STAR_DRUMS_GATE_OUTPUT ?= $(STAR_DRUMS_MISS_LOG).windows.summary
DETECTION_ACCURACY_STAR_DRUMS_GATE_ARG = $(if $(wildcard $(DETECTION_ACCURACY_STAR_DRUMS_GATE_OUTPUT)),--star-drums-gate-output "$(DETECTION_ACCURACY_STAR_DRUMS_GATE_OUTPUT)")
DETECTION_ACCURACY_MDB_DRUMS_GATE_OUTPUT ?= $(MDB_DRUMS_WINDOW_LOG).summary
DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG = $(if $(wildcard $(DETECTION_ACCURACY_MDB_DRUMS_GATE_OUTPUT)),--mdb-drums-gate-output "$(DETECTION_ACCURACY_MDB_DRUMS_GATE_OUTPUT)")
DETECTION_ACCURACY_MDB_RIM_COVERAGE_ARG = $(if $(wildcard $(MDB_RIM_COVERAGE_AUDIT)),--mdb-rim-coverage-input "$(MDB_RIM_COVERAGE_AUDIT)")
DETECTION_ACCURACY_BABYSLAKH_DRUMS_GATE_OUTPUT ?= $(BABYSLAKH_DRUMS_LOG)
DETECTION_ACCURACY_BABYSLAKH_DRUMS_GATE_ARG = $(if $(wildcard $(DETECTION_ACCURACY_BABYSLAKH_DRUMS_GATE_OUTPUT)),--babyslakh-drums-gate-output "$(DETECTION_ACCURACY_BABYSLAKH_DRUMS_GATE_OUTPUT)")
DETECTION_ACCURACY_BABYSLAKH_CALIBRATION_AUDIT_ARG = $(if $(wildcard $(BABYSLAKH_DRUM_CALIBRATION_AUDIT)),--babyslakh-calibration-audit "$(BABYSLAKH_DRUM_CALIBRATION_AUDIT)")
DETECTION_ACCURACY_BABYSLAKH_STATUS_ARGS = $(if $(wildcard $(BABYSLAKH_ARCHIVE)),--babyslakh-archive "$(BABYSLAKH_ARCHIVE)") $(if $(wildcard $(BABYSLAKH_EXTRACTED_DIR)),--babyslakh-extraction "$(BABYSLAKH_EXTRACTED_DIR)") $(if $(wildcard $(BABYSLAKH_DRUMS_SAMPLE_DIR)/e-gmd-v1.0.0.csv),--babyslakh-manifest "$(BABYSLAKH_DRUMS_SAMPLE_DIR)/e-gmd-v1.0.0.csv")
DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG += $(DETECTION_ACCURACY_MDB_RIM_COVERAGE_ARG) $(DETECTION_ACCURACY_BABYSLAKH_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_BABYSLAKH_CALIBRATION_AUDIT_ARG) $(DETECTION_ACCURACY_BABYSLAKH_STATUS_ARGS)
DETECTION_ACCURACY_BACH10_GATE_ARGS = $(foreach path,$(wildcard $(BACH10_MF0_SYNTH_SHARD_OUTS)),--bach10-gate-output "$(path)")
DETECTION_ACCURACY_MUSICNET_GATE_ARG = $(if $(wildcard $(MUSICNET_FULL_MEASUREMENT_OUTPUT)),--musicnet-gate-output "$(MUSICNET_FULL_MEASUREMENT_OUTPUT)",$(if $(wildcard $(MUSICNET_20_MEASUREMENT_OUTPUT)),--musicnet-gate-output "$(MUSICNET_20_MEASUREMENT_OUTPUT)"))
DETECTION_ACCURACY_MUSICNET_GATE_ARG += $(DETECTION_ACCURACY_MUSICNET_ROUTING_ARG)
DETECTION_ACCURACY_MAPS_GATE_ARGS = $(foreach path,$(wildcard $(MAPS_PIANO_SHARD_OUTS)),--maps-gate-output "$(path)")
DETECTION_ACCURACY_MAPS_NOTE_GATE_ARGS = $(foreach path,$(wildcard $(MAPS_PIANO_NOTE_SHARD_OUTS)),--maps-note-gate-output "$(path)")
DETECTION_ACCURACY_MAPS_ATTRIBUTE_ARG = $(if $(wildcard $(MAPS_PIANO_ATTRIBUTE_TSV)),--maps-attribute-input "$(MAPS_PIANO_ATTRIBUTE_TSV)") $(if $(wildcard $(ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT)),--electronic-piano-guitar-route-audit "$(ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT)")
DETECTION_ACCURACY_CROSS_CORPUS_CHORD_ARGS =
DETECTION_ACCURACY_URMP_GATE_ARG = $(if $(wildcard $(URMP_MEASUREMENT_OUTPUT)),--urmp-gate-output "$(URMP_MEASUREMENT_OUTPUT)")
DETECTION_ACCURACY_DRUM_GATE_ARG = $(if $(wildcard $(DRUM_FULL_GATE_OUT)),--drum-gate-output "$(DRUM_FULL_GATE_OUT)")
DETECTION_ACCURACY_HF_DRUM_GATE_ARGS = $(foreach path,$(wildcard $(HF_DRUM_KIT_SHARD_OUTS)),--hf-drum-gate-output "$(path)")
DETECTION_ACCURACY_ROUTE_SUMMARY_ARG = $(if $(wildcard $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)),--route-summary "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)")
DETECTION_ACCURACY_GOOD_SOUNDS_FULL_MIX_ARG = $(if $(wildcard $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)),--good-sounds-full-mix-input "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)") $(if $(wildcard $(TENOR_SAX_PIANO_ROUTE_AUDIT)),--tenor-sax-piano-route-audit "$(TENOR_SAX_PIANO_ROUTE_AUDIT)") $(if $(wildcard $(VIOLIN_GUITAR_ROUTE_AUDIT)),--violin-guitar-route-audit "$(VIOLIN_GUITAR_ROUTE_AUDIT)")
DETECTION_ACCURACY_PITCH_SHIFTED_VIOLIN_ARG = $(if $(wildcard $(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV)),--pitch-shifted-violin-input "$(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV)")
DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/medley_solos_attributes.tsv
DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_ARG = $(if $(wildcard $(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_TSV)),--medley-solos-attribute-input "$(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_TSV)")
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
GUITAR_CANDIDATE_ROW_PATHS ?= $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GUITARSET_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_MUSIC_DETECTED_ATTRIBUTE_ROWS) $(EGFXSET_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)
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
DETECTOR_IMPROVEMENT_ROUTE_SUMMARY_ARGS ?= --min-actionable-corpora 2
DETECTOR_IMPROVEMENT_AUDIT_REPORT ?= $(BUILD_DIR)/detector_improvement_audit.txt
DETECTOR_IMPROVEMENT_AUDIT_TAIL_LINES ?= 60
DETECTOR_IMPROVEMENT_AUDIT_TARGETS ?= detector-improvement-route-summary-refresh find-protected-drum-primary-attribute-patterns find-protected-drum-full-exact-attribute-patterns find-drum-active-false-patterns-full
# Each route miner can use REAL_NOTE_PATTERN_JOBS workers itself.  Keep the
# outer fan-out bounded so several large Python process pools cannot exhaust
# memory before any protected candidate is reported.
DETECTOR_IMPROVEMENT_ROUTE_MAKE_JOBS ?= -j2
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
DAGSTUHL_CHOIRSET_PATTERN_EXTRA_PROTECTED_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)
DAGSTUHL_CHOIRSET_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(DAGSTUHL_CHOIRSET_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")
GOOD_SOUNDS_FULL_MIX_PATTERN_EXTRA_PROTECTED_PATHS ?= $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)
GOOD_SOUNDS_FULL_MIX_PATTERN_EXTRA_PROTECTED_ARGS = $(foreach path,$(GOOD_SOUNDS_FULL_MIX_PATTERN_EXTRA_PROTECTED_PATHS),--extra-protected-path "$(path)")
GOOD_SOUNDS_FULL_MIX_OWNERSHIP_PATTERN_ARGS ?= --top-buckets 16 --limit 12 --min-positive-samples 2 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --show-near-misses 4 --protected-scope all --include-row-context --profile-fields 5
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
OBS_USER_PLUGIN_ROOT ?= $(abspath $(OBS_USER_PLUGIN_DIR)/../..)
OBS_USER_PLUGIN_DATA_DIR ?= $(OBS_USER_PLUGIN_ROOT)/data/basic_pitch
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
DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS ?= $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS) $(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)
MDB_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/mdb_drums_full_mix_samples
MDB_DRUMS_SOURCE_ROOT ?=
MDB_DRUMS_AUDIO_FLAVOR ?= full_mix
MDB_DRUMS_RECORDING_LIMIT ?= 0
MDB_DRUMS_MIN_RECORDINGS ?= 20
MDB_DRUMS_REQUIRED_WINDOWS ?= 80
MDB_DRUMS_MIN_RECALL_PERCENT ?= 70
MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT ?= 0
MDB_DRUMS_MIN_PRECISION_PERCENT ?= 55
MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT ?= 70
MDB_DRUMS_MISS_LOG ?= $(BUILD_DIR)/mdb_drums_misses.log
MDB_DRUMS_WINDOW_LOG ?= $(BUILD_DIR)/mdb_drums_windows.log
MDB_RIM_COVERAGE_AUDIT ?= $(BUILD_DIR)/mdb_rim_coverage.txt
MDB_DRUMS_SHARDS ?= 4
MDB_DRUMS_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MDB_DRUMS_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MDB_DRUMS_SHARD_TARGETS := $(addprefix test-mdb-drums-samples-shard-,$(MDB_DRUMS_SHARD_INDEXES))
MDB_DRUMS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/mdb_drums_samples_shard_,$(addsuffix .out,$(MDB_DRUMS_SHARD_INDEXES)))
MDB_DRUMS_LOCK_DIR ?= $(BUILD_DIR)/mdb_drums_samples.lock
MDB_DRUMS_PREP_LOCK_DIR ?= $(BUILD_DIR)/mdb_drums_prepare.lock
MDB_DRUMS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MDB_DRUMS_SHARD_INDEXES)))
BABYSLAKH_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/baby_slakh
BABYSLAKH_ARCHIVE ?= $(BABYSLAKH_SOURCE_DIR)/babyslakh_16k.tar.gz
BABYSLAKH_ARCHIVE_URL ?= https://zenodo.org/api/records/4603870/files/babyslakh_16k.tar.gz/content
BABYSLAKH_ARCHIVE_MD5 ?= 311096dc2bde7d61c97e930edbfc7f78
BABYSLAKH_DOWNLOAD_CONNECTIONS ?= 1
BABYSLAKH_EXTRACTED_DIR ?= $(BABYSLAKH_SOURCE_DIR)/extracted
BABYSLAKH_REQUIRED_TRACKS ?= 20
BABYSLAKH_DRUMS_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/babyslakh_drums_samples
BABYSLAKH_DRUMS_MIN_RECORDINGS ?= $(BABYSLAKH_REQUIRED_TRACKS)
BABYSLAKH_DRUMS_LOG ?= $(BUILD_DIR)/babyslakh_drums_diagnostics.log
BABYSLAKH_DRUM_CALIBRATION_AUDIT ?= $(BUILD_DIR)/babyslakh_drum_calibration_audit.txt
ENST_DRUMS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/enst_drums
ENST_DRUMS_ARCHIVE ?= $(ENST_DRUMS_SOURCE_DIR)/enstdrums_yourmt3_16k.tar.gz
ENST_DRUMS_ARCHIVE_URL ?= https://zenodo.org/record/7831843/files/enstdrums_yourmt3_16k.tar.gz?download=1
ENST_DRUMS_ARCHIVE_MD5 ?= 7e28c2a923e4f4162b3d83877cedb5eb
ENST_DRUMS_LICENSE_ACCEPTED ?= 0
ENST_DRUMS_INSPECTION ?= $(BUILD_DIR)/enst_drums_inspection.txt
ENST_DRUMS_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/enst_drums_samples
ENST_DRUMS_LIMIT_PER_CATEGORY ?= 32
ENST_DRUMS_MIN_PER_CATEGORY ?= 1
ENST_DRUMS_MEASUREMENT ?= $(BUILD_DIR)/enst_drums_measurement.log
EGMD_ARCHIVE_URL ?= https://storage.googleapis.com/magentadata/datasets/e-gmd/v1.0.0/e-gmd-v1.0.0.zip
EGMD_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/egmd
EGMD_ARCHIVE_BYTES ?= 96422999145
EGMD_ARCHIVE ?= $(EGMD_SOURCE_DIR)/e-gmd-v1.0.0.zip
EGMD_ARCHIVE_MD5 ?= 514af23329b0472a8349d1aaf8fb98dd
EGMD_DOWNLOAD_LOG ?= $(BUILD_DIR)/egmd_download.log
EGMD_DOWNLOAD_PID ?= $(BUILD_DIR)/egmd_download.pid
VIRTUOSITY_DRUMS_REPOSITORY ?= https://github.com/sfzinstruments/virtuosity_drums.git
VIRTUOSITY_DRUMS_BRANCH ?= master
VIRTUOSITY_DRUMS_SOURCE_PROBE ?= $(BUILD_DIR)/virtuosity_drums_source.txt
VIRTUOSITY_DRUMS_COMMIT ?= 9f04cf9a734527edfbb0a4eee1f674e45bbf71bc
VIRTUOSITY_DRUMS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/virtuosity_drums
VIRTUOSITY_DRUMS_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/virtuosity_drums_samples
VIRTUOSITY_DRUMS_LIMIT_PER_CATEGORY ?= 48
VIRTUOSITY_DRUMS_MIN_PER_CATEGORY ?= 20
VIRTUOSITY_DRUMS_MEASUREMENT ?= $(BUILD_DIR)/virtuosity_drums_measurement.log
VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/virtuosity_drums_primary_attribute_rows.tsv
SAMPLES29K_DRUMS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/29k_samples_drums
SAMPLES29K_DRUMS_ARCHIVE ?= $(SAMPLES29K_DRUMS_SOURCE_DIR)/29kSamplesDrumsDataset.zip
SAMPLES29K_DRUMS_ARCHIVE_URL ?= https://zenodo.org/records/4958592/files/29kSamplesDrumsDataset.zip?download=1
SAMPLES29K_DRUMS_ARCHIVE_MD5 ?= 75784e5bdbd069af66bee91d25b3e984
SAMPLES29K_DRUMS_INSPECTION ?= $(BUILD_DIR)/29k_samples_drums_inspection.txt
SAMPLES29K_DRUMS_SAMPLE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/29k_samples_drums_samples
SAMPLES29K_DRUMS_LIMIT_PER_CATEGORY ?= 500
SAMPLES29K_DRUMS_MIN_PER_CATEGORY ?= 500
SAMPLES29K_DRUMS_MEASUREMENT ?= $(BUILD_DIR)/29k_samples_drums_measurement.log
SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/29k_samples_drums_primary_attribute_rows.tsv
CACHED_PROTECTED_DRUM_PRIMARY_PATTERN_REPORT ?= $(BUILD_DIR)/cached_protected_drum_primary_patterns.txt
SAMPLES29K_DRUMS_JOB_LOG ?= $(BUILD_DIR)/corpus-download-jobs/measure-29k-drums.log
FSD50K_RIM_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/fsd50k_rim
FSD50K_RIM_GROUND_TRUTH_ARCHIVE ?= $(FSD50K_RIM_SOURCE_DIR)/FSD50K.ground_truth.zip
FSD50K_RIM_METADATA_ARCHIVE ?= $(FSD50K_RIM_SOURCE_DIR)/FSD50K.metadata.zip
FSD50K_RIM_METADATA_AUDIT ?= $(BUILD_DIR)/fsd50k_rim_metadata.txt
COMMONS_RIMSHOT_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/commons_rimshot
COMMONS_RIMSHOT_AUDIO ?= $(COMMONS_RIMSHOT_SOURCE_DIR)/Kevin_MacLeod_assorted_rimshots_-_13-second_roll.wav
COMMONS_RIMSHOT_URL ?= https://upload.wikimedia.org/wikipedia/commons/c/cb/Kevin_MacLeod_assorted_rimshots_-_13-second_roll.wav
COMMONS_RIMSHOT_SHA1 ?= 11b1e0f8e317aed2a75a7a1b0750c2d13e9221fd
COMMONS_RIMSHOT_CANDIDATE_AUDIT ?= $(BUILD_DIR)/commons_rimshot_candidate.txt
PIXABAY_RIMSHOT_CANDIDATE_AUDIT ?= $(BUILD_DIR)/pixabay_rimshot_candidate.txt
PIXABAY_RIMSHOT_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/pixabay_rimshot
PIXABAY_RIMSHOT_MP3 ?= $(PIXABAY_RIMSHOT_SOURCE_DIR)/freesound_community-rimshot-sweet-107111.mp3
PIXABAY_RIMSHOT_WAV ?= $(PIXABAY_RIMSHOT_SOURCE_DIR)/rim/rimshot_sweet.wav
PIXABAY_RIMSHOT_URL ?= https://cdn.pixabay.com/download/audio/2022/03/26/audio_98d9528d9c.mp3?filename=freesound_community-rimshot-sweet-107111.mp3
PIXABAY_RIMSHOT_SHA256 ?= ad6d74f1afc7d46e16da50ec11fc68a82618b831e8cd10dd9f7050bed612e79f
PIXABAY_RIMSHOT_MEASUREMENT ?= $(BUILD_DIR)/pixabay_rimshot_measurement.log
PIXABAY_RIMSHOT_MEASUREMENT_AUDIT ?= $(BUILD_DIR)/pixabay_rimshot_measurement.txt
PIXABAY_RIMSHOT_F_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/pixabay_rimshot_f
PIXABAY_RIMSHOT_F_MP3 ?= $(PIXABAY_RIMSHOT_F_SOURCE_DIR)/freesound_community-rimshot-f-56918.mp3
PIXABAY_RIMSHOT_F_URL ?= https://cdn.pixabay.com/download/audio/2022/03/13/audio_c9677d181e.mp3?filename=freesound_community-rimshot-f-56918.mp3
PIXABAY_RIMSHOT_F_SHA256 ?= da503da40bb589ae325f3cbbded5a01e1f72d07ca3e2340176b74ccd53b12c36
PIXABAY_RIMSHOT_F_WAV ?= $(PIXABAY_RIMSHOT_F_SOURCE_DIR)/rim/rimshot_f.wav
PIXABAY_RIMSHOT_F_MEASUREMENT ?= $(BUILD_DIR)/pixabay_rimshot_f_measurement.log
PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT ?= $(BUILD_DIR)/pixabay_rimshot_f_measurement.txt
PIXABAY_RIM_SHOT_CANDIDATE_AUDIT ?= $(BUILD_DIR)/pixabay_rim_shot_candidate.txt
PIXABAY_RIM_SHOT_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/pixabay_rim_shot
PIXABAY_RIM_SHOT_MP3 ?= $(PIXABAY_RIM_SHOT_SOURCE_DIR)/freesound_community-rim-shot-90328.mp3
PIXABAY_RIM_SHOT_URL ?= https://cdn.pixabay.com/download/audio/2022/03/15/audio_05b41c4543.mp3?filename=freesound_community-rim-shot-90328.mp3
PIXABAY_RIM_SHOT_SHA256 ?= 8d8012b487f635e4d3c806a5f8cc1d4817d10142f17c7cd0ce7a6f8935cf9d12
PIXABAY_RIM_SHOT_WAV ?= $(PIXABAY_RIM_SHOT_SOURCE_DIR)/rim/rim_shot.wav
PIXABAY_RIM_SHOT_MEASUREMENT ?= $(BUILD_DIR)/pixabay_rim_shot_measurement.log
PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT ?= $(BUILD_DIR)/pixabay_rim_shot_measurement.txt
BPM_DIAG_TOLERANCE ?= 8
IMMEDIATE_SOURCE_BPM_3S_AUDIT ?= $(BUILD_DIR)/immediate_source_bpm_3s_audit.txt
FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG ?= $(BUILD_DIR)/filobass_bpm_3s_source_diagnostics.log
GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG ?= $(BUILD_DIR)/gtzan_rhythm_bpm_3s_source_diagnostics.log
EGMD_BPM_MAX_SECONDS ?= 20
MDB_BPM_MAX_SECONDS ?= 20
MAESTRO_BPM_MAX_SECONDS ?= 20
EGMD_BPM_LOG ?= $(BUILD_DIR)/egmd_bpm_diagnostics.log
REAL_EGMD_BPM_LOG ?= $(BUILD_DIR)/real_egmd_bpm_diagnostics.log
MDB_BPM_LOG ?= $(BUILD_DIR)/mdb_bpm_diagnostics.log
MAESTRO_BPM_LOG ?= $(BUILD_DIR)/maestro_bpm_diagnostics.log
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
MEDLEY_SOLOS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/medley_solos_attributes.tsv
MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT ?= 300
MEDLEY_SOLOS_MIN_SAMPLES ?= 600
MEDLEY_SOLOS_MIN_COUNTS ?= guitar=100,piano=100,vocals=100,other=300
MEDLEY_SOLOS_MIN_RECALL_PERCENT ?= 20
MEDLEY_SOLOS_DEBUG_SAMPLE_ID ?=
MEDLEY_SOLOS_SHARDS ?= 4
MEDLEY_SOLOS_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(MEDLEY_SOLOS_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
MEDLEY_SOLOS_SHARD_TARGETS := $(addprefix test-medley-solos-samples-shard-,$(MEDLEY_SOLOS_SHARD_INDEXES))
MEDLEY_SOLOS_SHARD_OUTS := $(addprefix $(BUILD_DIR)/medley_solos_samples_shard_,$(addsuffix .out,$(MEDLEY_SOLOS_SHARD_INDEXES)))
MEDLEY_SOLOS_LOCK_DIR ?= $(BUILD_DIR)/medley_solos_samples.lock
MEDLEY_SOLOS_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MEDLEY_SOLOS_SHARD_INDEXES)))
MAPS_PIANO_URL ?= https://zenodo.org/api/records/18160555/files/ENSTDkCl.zip/content
MAPS_PIANO_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/maps_piano
MAPS_PIANO_ARCHIVE ?= $(MAPS_PIANO_SOURCE_DIR)/ENSTDkCl.zip
MAPS_PIANO_DOWNLOAD_CONNECTIONS ?= 8
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
MAPS_PIANO_ATTRIBUTE_TSV ?= $(BUILD_DIR)/maps_piano_attributes.tsv
MAPS_PIANO_CHORD_STATE_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_audit.tsv
MAPS_PIANO_CHORD_STATE_CONFIRM1_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_audit_confirm1.tsv
MAPS_PIANO_CHORD_STATE_CONFIRM3_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_confirm3_audit.tsv
MAPS_PIANO_CHORD_STATE_TONE018_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_tone018_audit.tsv
MAPS_PIANO_CHORD_STATE_MARGIN060_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_margin060_audit.tsv
MAPS_PIANO_CHORD_STATE_BASSBONUS000_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_bassbonus000_audit.tsv
ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT ?= $(BUILD_DIR)/electronic_piano_guitar_route_audit.txt
MAPS_PIANO_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/maps_piano_attributes.shard-,$(addsuffix .tsv,$(MAPS_PIANO_SHARD_INDEXES)))
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
MAPS_PIANO_NOTE_ATTRIBUTE_TSV ?= $(BUILD_DIR)/maps_piano_note_attributes.tsv
MAPS_PIANO_NOTE_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/maps_piano_note_attributes.shard-,$(addsuffix .tsv,$(MAPS_PIANO_NOTE_SHARD_INDEXES)))
MAPS_PIANO_NOTE_LOCK_DIR ?= $(BUILD_DIR)/maps_piano_note_samples.lock
MAPS_PIANO_NOTE_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(words $(MAPS_PIANO_NOTE_SHARD_INDEXES)))
MAESTRO_REAL_URL ?= https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0.zip
MAESTRO_REAL_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/maestro_real
MAESTRO_REAL_ARCHIVE ?= $(MAESTRO_REAL_SOURCE_DIR)/maestro-v3.0.0.zip
MAESTRO_REAL_SAMPLE_DIR ?= $(BUILD_DIR)/maestro_real_samples
# Keep the configured audit size aligned with the extracted external subset.  A
# smaller default makes the dashboard incorrectly report that a valid larger
# subset is unprepared on the next refresh.
MAESTRO_REAL_SAMPLE_LIMIT ?= 320
MAESTRO_REAL_MIN_RECORDINGS ?= 160
MAESTRO_REAL_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/maestro_real_measurement.out
MAESTRO_REAL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/maestro_real_attributes.tsv
MAESTRO_REAL_CHORD_EVIDENCE_OUTPUT ?= $(BUILD_DIR)/independent_piano_chord_evidence.txt
MAESTRO_REAL_CHORD_STATE_OUTPUT ?= $(BUILD_DIR)/independent_piano_chord_states.txt
MAESTRO_REAL_CHORD_STATE_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_audit.tsv
MAESTRO_REAL_CHORD_STATE_CONFIRM1_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_audit_confirm1.tsv
MAESTRO_REAL_CHORD_STATE_CONFIRM3_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_confirm3_audit.tsv
MAESTRO_REAL_CHORD_STATE_TONE018_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_tone018_audit.tsv
MAESTRO_REAL_CHORD_STATE_MARGIN060_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_margin060_audit.tsv
MAESTRO_REAL_CHORD_STATE_BASSBONUS000_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_bassbonus000_audit.tsv
MAESTRO_REAL_CHORD_STATE_CONFIDENCE070_AUDIT ?= $(BUILD_DIR)/maestro_real_chord_state_confidence070.tsv
INDEPENDENT_PIANO_CHORD_STABILITY_OUTPUT ?= $(BUILD_DIR)/independent_piano_chord_stability.txt
PIANO_CHORD_CONFIRMATION_AUDIT ?= $(BUILD_DIR)/piano_chord_confirmation_audit.txt
PIANO_CHORD_CONFIRM3_AUDIT ?= $(BUILD_DIR)/piano_chord_confirm3_audit.txt
PIANO_CHORD_TONE018_AUDIT ?= $(BUILD_DIR)/piano_chord_tone018_audit.txt
PIANO_CHORD_MARGIN060_AUDIT ?= $(BUILD_DIR)/piano_chord_margin060_audit.txt
PIANO_CHORD_BASSBONUS000_AUDIT ?= $(BUILD_DIR)/piano_chord_bassbonus000_audit.txt
PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT ?= $(BUILD_DIR)/piano_chord_display_confidence_audit.txt
PIANO_CHORD_DISPLAY_GATE_AUDIT ?= $(BUILD_DIR)/piano_chord_display_gate_audit.txt
MAPS_PIANO_CHORD_STATE_CONFIDENCE070_AUDIT ?= $(BUILD_DIR)/maps_piano_chord_state_confidence070.tsv
PIANO_CHORD_STATE_AUDIT_MAX_SEQUENCES ?= 64
KRAISLER_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/kraisler
KRAISLER_ARCHIVE ?= $(KRAISLER_SOURCE_DIR)/KRAISLER.zip
KRAISLER_EXTRACT_DIR ?= $(KRAISLER_SOURCE_DIR)/extracted
KRAISLER_PREPARED_DIR ?= $(KRAISLER_SOURCE_DIR)/prepared-multitrack
KRAISLER_MUSICNET_DIR ?= $(KRAISLER_SOURCE_DIR)/musicnet-fixture
KRAISLER_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/kraisler_attributes.tsv
KRAISLER_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/kraisler_measurement.tsv
KRAISLER_TEMPO_FIXTURE_DIR ?= $(BUILD_DIR)/kraisler-tempo-fixture
KRAISLER_BPM_LOG ?= $(BUILD_DIR)/kraisler_bpm_diagnostics.log
KRAISLER_ARCHIVE_URL ?= https://zenodo.org/api/records/21082251/files/KRAISLER.zip/content
KRAISLER_ARCHIVE_MD5 ?= 22f6f51e9c356c1ea8f591d85603fd73
KRAISLER_MIN_TRACKS ?= 20
BALLROOM_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/ballroom_tempo
BALLROOM_AUDIO_DIR ?= $(BALLROOM_SOURCE_DIR)/audio
BALLROOM_ANNOTATIONS_DIR ?= $(BALLROOM_SOURCE_DIR)/annotations
BALLROOM_TEMPO_FIXTURE_DIR ?= $(BUILD_DIR)/ballroom-tempo-fixture
BALLROOM_BPM_LOG ?= $(BUILD_DIR)/ballroom_bpm_diagnostics.log
BALLROOM_BPM_LIMIT ?= 64
LIVE_BTT_DETAILS_MIN_CONFIDENCE ?= 0.70
LIVE_BTT_DETAILS_MAX_CONFIDENCE ?= 0.80
FILOBASS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/filobass
FILOBASS_ARCHIVE ?= $(FILOBASS_SOURCE_DIR)/FiloBass_v1.0.0.zip
FILOBASS_EXTRACT_DIR ?= $(FILOBASS_SOURCE_DIR)/extracted
FILOBASS_INSPECTION_OUTPUT ?= $(BUILD_DIR)/filobass_inspection.tsv
FILOBASS_TEMPO_FIXTURE_DIR ?= $(FILOBASS_SOURCE_DIR)/tempo-fixture
FILOBASS_BPM_LOG ?= $(BUILD_DIR)/filobass_bpm_diagnostics.log
GTZAN_RHYTHM_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/gtzan_rhythm
GTZAN_RHYTHM_AUDIO_ARCHIVE ?= $(GTZAN_RHYTHM_SOURCE_DIR)/gtzan-dataset-music-genre-classification.zip
GTZAN_RHYTHM_ANNOTATIONS_ARCHIVE ?= $(GTZAN_RHYTHM_SOURCE_DIR)/GTZAN-Rhythm_v2_ismir2015_lbd_2015-10-28.tar_.gz
GTZAN_RHYTHM_AUDIO_URL ?= https://huggingface.co/datasets/m-a-p/GTZAN/resolve/main/gtzan-dataset-music-genre-classification.zip?download=true
GTZAN_RHYTHM_ANNOTATIONS_URL ?= https://huggingface.co/datasets/m-a-p/GTZAN/resolve/main/GTZAN-Rhythm_v2_ismir2015_lbd_2015-10-28.tar_.gz?download=true
GTZAN_RHYTHM_DOWNLOAD_CONNECTIONS ?= 8
GTZAN_RHYTHM_INSPECTION_OUTPUT ?= $(BUILD_DIR)/gtzan_rhythm_inspection.txt
GTZAN_RHYTHM_TEMPO_FIXTURE_DIR ?= $(BUILD_DIR)/gtzan-rhythm-tempo-fixture
GTZAN_RHYTHM_BPM_LOG ?= $(BUILD_DIR)/gtzan_rhythm_bpm_diagnostics.log
GTZAN_RHYTHM_BPM_LIMIT ?= 100
CANDOMBE_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/candombe
CANDOMBE_AUDIO_ARCHIVE ?= $(CANDOMBE_SOURCE_DIR)/candombe_audio.zip
CANDOMBE_ANNOTATIONS_ARCHIVE ?= $(CANDOMBE_SOURCE_DIR)/candombe_annotations.zip
CANDOMBE_AUDIO_URL ?= https://zenodo.org/records/6533068/files/candombe_audio.zip?download=1
CANDOMBE_ANNOTATIONS_URL ?= https://zenodo.org/records/6533068/files/candombe_annotations.zip?download=1
CANDOMBE_INSPECTION_OUTPUT ?= $(BUILD_DIR)/candombe_inspection.txt
CANDOMBE_TEMPO_FIXTURE_DIR ?= $(CANDOMBE_SOURCE_DIR)/tempo-fixture
CANDOMBE_BPM_LOG ?= $(BUILD_DIR)/candombe_bpm_diagnostics.log
CANDOMBE_BPM_LIMIT ?= 35
BTT_BALLROOM_LOG ?= $(BUILD_DIR)/btt_ballroom_bpm_diagnostics.log
BTT_FILOBASS_LOG ?= $(BUILD_DIR)/btt_filobass_bpm_diagnostics.log
BTT_GTZAN_RHYTHM_LOG ?= $(BUILD_DIR)/btt_gtzan_rhythm_bpm_diagnostics.log
BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG ?= $(BUILD_DIR)/btt_gtzan_rhythm_range_sweep.log
BTT_GTZAN_RHYTHM_RANGE_SWEEP_MINS ?= 40,100,120,140,160
TEMPO_CONSENSUS_PHASE_GATES ?= 0.00,0.20,0.30,0.40,0.50,0.60
TEMPO_CONSENSUS_BTT_GATES ?= 0.00,0.15,0.25,0.35,0.45,0.55,0.60,0.70,0.80
TEMPO_CONSENSUS_AGREEMENT_GATES ?= 2,4,8,12
BEAT_THIS_DIAGNOSTIC_ROOT ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/beat_this_diagnostic
BEAT_THIS_RUNTIME_ROOT ?= $(BUILD_DIR)/beat_this_runtime
BEAT_THIS_DIAGNOSTIC_LOG ?= $(BUILD_DIR)/beat_this_final0_gtzan_rhythm_bpm_diagnostics.log
BEAT_THIS_BALLROOM_LOG ?= $(BUILD_DIR)/beat_this_final0_ballroom_bpm_diagnostics.log
BEAT_THIS_FILOBASS_LOG ?= $(BUILD_DIR)/beat_this_final0_filobass_bpm_diagnostics.log
BEAT_THIS_ROLLING_BALLROOM_LOG ?= $(BUILD_DIR)/beat_this_final0_rolling_ballroom_bpm_diagnostics.log
BEAT_THIS_ROLLING_FILOBASS_LOG ?= $(BUILD_DIR)/beat_this_final0_rolling_filobass_bpm_diagnostics.log
BEAT_THIS_CONTINUOUS_BALLROOM_LOG ?= $(BUILD_DIR)/beat_this_final0_continuous_ballroom_bpm_diagnostics.log
BEAT_THIS_CONTINUOUS_FILOBASS_LOG ?= $(BUILD_DIR)/beat_this_final0_continuous_filobass_bpm_diagnostics.log
BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT ?= $(BUILD_DIR)/beat_this_continuous_interval_gate_audit.txt
BEAT_THIS_SIDECAR_BALLROOM_LOG ?= $(BUILD_DIR)/beat_this_final0_sidecar_ballroom_replay.log
BEAT_THIS_SIDECAR_FILOBASS_LOG ?= $(BUILD_DIR)/beat_this_final0_sidecar_filobass_replay.log
BEAT_THIS_SIDECAR_FILOBASS_SHARD_LOGS ?= $(BUILD_DIR)/beat_this_final0_sidecar_filobass_replay_0.log $(BUILD_DIR)/beat_this_final0_sidecar_filobass_replay_12.log $(BUILD_DIR)/beat_this_final0_sidecar_filobass_replay_24.log $(BUILD_DIR)/beat_this_final0_sidecar_filobass_replay_36.log
BEAT_THIS_SIDECAR_BALLROOM_AUDIT ?= $(BUILD_DIR)/beat_this_sidecar_ballroom_replay.txt
BEAT_THIS_SIDECAR_FILOBASS_AUDIT ?= $(BUILD_DIR)/beat_this_sidecar_filobass_replay.txt
BEAT_THIS_SIDECAR_REPLAY_START ?= 0
BEAT_THIS_SIDECAR_REPLAY_LIMIT ?= 0
THREE_TEMPO_TRACKER_CONSENSUS_LOG ?= $(BUILD_DIR)/three_tempo_tracker_consensus.log
HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG ?= $(BUILD_DIR)/high_tempo_three_tempo_tracker_consensus.log
BEAT_THIS_DIAGNOSTIC_MODEL ?= final0
BTT_EGMD_LOG ?= $(BUILD_DIR)/btt_egmd_bpm_diagnostics.log
BTT_HIGH_TEMPO_MIN ?= 120
BTT_HIGH_TEMPO_BALLROOM_LOG ?= $(BUILD_DIR)/btt_high_tempo_ballroom_bpm_diagnostics.log
BTT_HIGH_TEMPO_FILOBASS_LOG ?= $(BUILD_DIR)/btt_high_tempo_filobass_bpm_diagnostics.log
BTT_HIGH_TEMPO_GTZAN_LOG ?= $(BUILD_DIR)/btt_high_tempo_gtzan_rhythm_bpm_diagnostics.log
BTT_TEMPO_CHUNK_ROOT ?=
BTT_TEMPO_CHUNK_OUTPUT ?=
BTT_TEMPO_CHUNK_START ?= 0
BTT_TEMPO_CHUNK_LIMIT ?= 10
BTT_TEMPO_CHUNK_INPUTS ?=
# Keep the complete annotated FiloBass corpus in the default diagnostic.  A
# smaller prefix can overstate a BPM route that does not generalize to all 48
# real bass stems.
FILOBASS_BPM_LIMIT ?= 48
FILOBASS_ONSET_DIAGNOSTICS ?= $(BUILD_DIR)/filobass_bass_onset_diagnostics.tsv
IRMAS_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/irmas
IRMAS_TEST_PART1_ARCHIVE ?= $(IRMAS_SOURCE_DIR)/IRMAS-TestingData-Part1.zip
IRMAS_TEST_PART2_ARCHIVE ?= $(IRMAS_SOURCE_DIR)/IRMAS-TestingData-Part2.zip
IRMAS_TEST_PART3_ARCHIVE ?= $(IRMAS_SOURCE_DIR)/IRMAS-TestingData-Part3.zip
IRMAS_TEST_PART1_URL ?= https://zenodo.org/records/1290750/files/IRMAS-TestingData-Part1.zip?download=1
IRMAS_TEST_PART2_URL ?= https://zenodo.org/records/1290750/files/IRMAS-TestingData-Part2.zip?download=1
IRMAS_TEST_PART3_URL ?= https://zenodo.org/records/1290750/files/IRMAS-TestingData-Part3.zip?download=1
IRMAS_TEST_PART1_MD5 ?= 5a2e65520dcedada565dff2050bb2a56
IRMAS_TEST_PART2_MD5 ?= afb0c8ea92f34ee653693106be95c895
IRMAS_TEST_PART3_MD5 ?= 9b3fb2d0c89cdc98037121c25bd5b556
IRMAS_ARCHIVES := $(IRMAS_TEST_PART1_ARCHIVE) $(IRMAS_TEST_PART2_ARCHIVE) $(IRMAS_TEST_PART3_ARCHIVE)
IRMAS_EXTRACT_DIR ?= $(IRMAS_SOURCE_DIR)/extracted
IRMAS_PREPARED_DIR ?= $(BUILD_DIR)/irmas_labelled_samples
IRMAS_ATTRIBUTE_OUTPUT ?= $(BUILD_DIR)/irmas_labelled_attributes.tsv
IRMAS_MEASUREMENT_OUTPUT ?= $(BUILD_DIR)/irmas_labelled_measurement.out
IRMAS_INVENTORY_OUTPUT ?= $(BUILD_DIR)/irmas_inventory.txt
IRMAS_MAX_SAMPLES_PER_LABEL ?= 192
IRMAS_MIN_SAMPLES ?= 240
KRAISLER_MIN_PIECES ?= 60
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
REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID ?=
REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV ?= $(BUILD_DIR)/real_note_full_mix_debug_attributes.tsv
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
GUITAR_TECHS_P3_MUSIC_ARCHIVE ?= $(GUITAR_TECHS_SOURCE_DIR)/P3_music.zip
GUITAR_TECHS_P1_SINGLENOTES_URL ?= https://zenodo.org/api/records/14963133/files/P1_singlenotes.zip/content
GUITAR_TECHS_P2_SINGLENOTES_URL ?= https://zenodo.org/api/records/14963133/files/P2_singlenotes.zip/content
GUITAR_TECHS_P1_CHORDS_URL ?= https://zenodo.org/api/records/14963133/files/P1_chords.zip/content
GUITAR_TECHS_P2_CHORDS_URL ?= https://zenodo.org/api/records/14963133/files/P2_chords.zip/content
GUITAR_TECHS_P3_MUSIC_URL ?= https://zenodo.org/api/records/14963133/files/P3_music.zip/content
GUITAR_TECHS_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_techs_samples
GUITAR_TECHS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitar_techs_attributes.tsv
GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_detected_attribute_rows.tsv
GUITAR_TECHS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_miss_attribute_rows.tsv
GUITAR_TECHS_ISOLATED_VISUAL_AUDIT ?= $(BUILD_DIR)/guitar_techs_isolated_visual_audit.txt
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
GUITAR_TECHS_MUSIC_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_techs_music_samples
GUITAR_TECHS_MUSIC_MANIFEST ?= $(GUITAR_TECHS_MUSIC_SAMPLE_DIR)/manifest.tsv
GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV ?= $(BUILD_DIR)/guitar_techs_music_attributes.tsv
GUITAR_TECHS_MUSIC_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_music_detected_attribute_rows.tsv
GUITAR_TECHS_MUSIC_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/guitar_techs_music_miss_attribute_rows.tsv
GUITAR_TECHS_MUSIC_DEBUG_OUT ?= $(BUILD_DIR)/guitar_techs_music_debug.out
GUITAR_TECHS_MUSIC_DEBUG_PATTERN ?=
GUITAR_TECHS_MUSIC_SAMPLE_LIMIT ?= 650
GUITAR_TECHS_MUSIC_MIN_EXCERPTS ?= 100
GUITAR_TECHS_MUSIC_MIN_WINDOWS ?= 100
GUITAR_TECHS_MUSIC_MIN_RECALL_PERCENT ?= 0
GUITAR_TECHS_MUSIC_MIN_PRECISION_PERCENT ?= 0
GUITAR_TECHS_MUSIC_MIN_GUITAR_RECALL_PERCENT ?= 0
GUITAR_TECHS_MUSIC_MAX_CONTAMINATION_PERCENT ?= 100
GUITAR_TECHS_MUSIC_MAX_FALSE_VOCAL_PERCENT ?= 100
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
PHILHARMONIA_FULL_DEBUG_SAMPLE_ID ?=
PHILHARMONIA_FULL_DEBUG_ATTRIBUTE_TSV ?= $(BUILD_DIR)/philharmonia_full_debug_attributes.tsv
PHILHARMONIA_FULL_SAMPLE_LIMIT ?= 0
PHILHARMONIA_FULL_MIN_SAMPLES ?= 2500
PHILHARMONIA_FULL_MIN_BASS ?= 80
PHILHARMONIA_FULL_MIN_GUITAR ?= 140
PHILHARMONIA_FULL_MIN_OTHER ?= 2200
PHILHARMONIA_FULL_MAX_FAILURES ?= 25
PHILHARMONIA_FULL_PROGRESS_EVERY ?= 250
PITCH_SHIFTED_VIOLIN_SAMPLE_DIR ?= $(BUILD_DIR)/pitch_shifted_violin_samples
PITCH_SHIFTED_VIOLIN_SOURCE_MANIFEST ?= $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv
PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV ?= $(BUILD_DIR)/pitch_shifted_violin_attributes.tsv
PITCH_SHIFTED_VIOLIN_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/pitch_shifted_violin_attributes.lock
PITCH_SHIFTED_VIOLIN_PER_MIDI ?= 4
PITCH_SHIFTED_VIOLIN_MIN_SAMPLES ?= 20
PITCH_SHIFTED_VIOLIN_MAX_FAILURES ?= 20
GOOD_SOUNDS_URL ?= https://zenodo.org/api/records/820937/files/good-sounds.zip/content
GOOD_SOUNDS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/good_sounds
GOOD_SOUNDS_ARCHIVE ?= $(GOOD_SOUNDS_SOURCE_DIR)/good-sounds.zip
GOOD_SOUNDS_SAMPLE_DIR ?= $(BUILD_DIR)/good_sounds_samples
GOOD_SOUNDS_ATTRIBUTE_TSV ?= $(BUILD_DIR)/good_sounds_attributes.tsv
GOOD_SOUNDS_DETECTED_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_detected_attribute_rows.tsv
GOOD_SOUNDS_MISS_ATTRIBUTE_ROWS ?= $(BUILD_DIR)/good_sounds_miss_attribute_rows.tsv
GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/good_sounds_full_mix_attributes.tsv
TENOR_SAX_PIANO_ROUTE_AUDIT ?= $(BUILD_DIR)/tenor_sax_piano_route_audit.txt
VIOLIN_GUITAR_ROUTE_AUDIT ?= $(BUILD_DIR)/violin_guitar_route_audit.txt
GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/good_sounds_full_mix_attributes.lock
GOOD_SOUNDS_DEBUG_SAMPLE_ID ?=
GOOD_SOUNDS_DEBUG_ATTRIBUTE_TSV ?= $(BUILD_DIR)/good_sounds_debug_attributes.tsv
GOOD_SOUNDS_DEBUG_INSPECT_ARGS ?= --dump-rows --include-empty-debug
GOOD_SOUNDS_SAMPLE_LIMIT ?= 1500
GOOD_SOUNDS_MIN_SAMPLES ?= 500
GOOD_SOUNDS_REFRESH ?= 0
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
IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_piano_full_mix_attributes.tsv
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
IOWA_ORCHESTRA_FULL_DEBUG_SAMPLE_ID ?=
IOWA_ORCHESTRA_FULL_DEBUG_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_orchestra_full_debug_attributes.tsv
IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT ?= 720
IOWA_ORCHESTRA_FULL_MIN_SAMPLES ?= 520
IOWA_ORCHESTRA_FULL_MIN_BASS ?= 20
IOWA_ORCHESTRA_FULL_MIN_OTHER ?= 480
IOWA_ORCHESTRA_FULL_MAX_FAILURES ?= 20
IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE ?= 1
IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT ?= 180
IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES ?= 1
IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES ?= 6
IOWA_SAX_FULL_MIX_FIXTURE_DIR ?= $(BUILD_DIR)/iowa_sax_full_mix_fixture
IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/iowa_sax_full_mix_attributes.tsv
IOWA_SAX_FULL_MIX_OUTPUT ?= $(BUILD_DIR)/iowa_sax_full_mix.out
IOWA_SAX_FULL_MIX_MIN_SAMPLES ?= 60
TINYSOL_SAX_FULL_MIX_FIXTURE_DIR ?= $(BUILD_DIR)/tinysol_sax_full_mix_fixture
TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/tinysol_sax_full_mix_attributes.tsv
TINYSOL_SAX_FULL_MIX_OUTPUT ?= $(BUILD_DIR)/tinysol_sax_full_mix.out
TINYSOL_SAX_FULL_MIX_MIN_SAMPLES ?= 98
TINYSOL_FLUTE_FULL_MIX_FIXTURE_DIR ?= $(BUILD_DIR)/tinysol_flute_full_mix_fixture
TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV ?= $(BUILD_DIR)/tinysol_flute_full_mix_attributes.tsv
TINYSOL_FLUTE_FULL_MIX_OUTPUT ?= $(BUILD_DIR)/tinysol_flute_full_mix.out
TINYSOL_FLUTE_FULL_MIX_MIN_SAMPLES ?= 118
TINYSOL_WIND_EXACT_FIXTURE_DIR ?= $(BUILD_DIR)/tinysol_wind_exact_fixture
TINYSOL_WIND_EXACT_ATTRIBUTE_TSV ?= $(BUILD_DIR)/tinysol_wind_exact_attributes.tsv
TINYSOL_WIND_EXACT_OUTPUT ?= $(BUILD_DIR)/tinysol_wind_exact.out
TINYSOL_WIND_EXACT_MIN_SAMPLES ?= 219
REAL_A2S_SAX_SOURCE_DIR ?= $(INSTRUMENT_SAMPLE_STORE_LINK)/real_a2s_sax
REAL_A2S_SAX_ARCHIVE ?= $(REAL_A2S_SAX_SOURCE_DIR)/real_a2s_sax_dataset.tgz
REAL_A2S_SAX_ARCHIVE_URL ?= https://grfia.dlsi.ua.es/audio-to-score/real_a2s_sax_dataset.tgz
REAL_A2S_SAX_METADATA_DIR ?= $(REAL_A2S_SAX_SOURCE_DIR)/metadata
REAL_A2S_SAX_PROBE_DIR ?= $(REAL_A2S_SAX_SOURCE_DIR)/probe
REAL_A2S_SAX_SCALE_FIXTURE_DIR ?= $(BUILD_DIR)/real_a2s_tenor_scale_fixture
REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV ?= $(BUILD_DIR)/real_a2s_tenor_scale_attributes.tsv
REAL_A2S_SAX_SCALE_MIDI_OFFSET ?= -12
REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES ?= BbMajScale BMajScale CMajScale C\#MajScale DMajScale EbMajScale EMajScale FMajScale F\#MajScale GMajScale AbMajScale AMajScale
REAL_A2S_SAX_TENOR_SCALE_INPUTS = $(foreach recording,$(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES),--input "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/$(recording).wav" "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/$(recording).krn" 80 0.50)
REAL_A2S_SAX_TENOR_EXERCISE_INPUTS = --input "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex1.krn" 80 0.34 --input "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex2.wav" "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex2.krn" 80 0.50 --input "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex3.wav" "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex3.krn" 80 0.40
REAL_A2S_SAX_SCALE_MIN_SAMPLES ?= 360
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
IDMT_BASS_LINES_TEMPO_METADATA ?= $(BUILD_DIR)/idmt_bass_lines_tempo_metadata.tsv
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
IDMT_GUITAR_ISOLATED_VISUAL_AUDIT ?= $(BUILD_DIR)/idmt_guitar_isolated_visual_audit.txt
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
VOCALSET_CLEAN_VOWEL_SAMPLE_ID ?= vocalset_f1_scales_straight_i_9_C5
VOCALSET_CLEAN_VOWEL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/vocalset_clean_vowel_attributes.tsv
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

