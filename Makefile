CXX ?= g++
PYTHON ?= python3

ACTIVE_GOAL_FILE ?= /home/kyz/.codex/attachments/46ea0f9b-3fe5-461f-90f6-07da1a97dc8d/pasted-text-1.txt

.PHONY: show-active-goal
show-active-goal: scripts/show_active_goal.sh
	$(SHELL) scripts/show_active_goal.sh "$(ACTIVE_GOAL_FILE)"

.PHONY: list-make-targets test-list-make-targets find-repo-text test-find-repo-text
list-make-targets: scripts/list_make_targets.py
	$(PYTHON) scripts/list_make_targets.py Makefile "$(TERM)"

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
BTT_SOURCE_DIR := third_party/beat_and_tempo_tracking
BTT_C_SOURCES := $(wildcard $(BTT_SOURCE_DIR)/src/*.c)
BTT_OBJS := $(patsubst $(BTT_SOURCE_DIR)/src/%.c,$(BUILD_DIR)/btt_%.o,$(BTT_C_SOURCES))
BASIC_PITCH_RUNTIME_OBJS := $(BUILD_DIR)/basic_pitch_onnx_runtime.o $(BUILD_DIR)/basic_pitch_onnx_decoder.o $(BUILD_DIR)/basic_pitch_onnx_worker.o $(BUILD_DIR)/basic_pitch_pcm_history.o
PLUGIN_OBJS := $(BUILD_DIR)/analyzer.o $(RENDERER_OBJ) $(BUILD_DIR)/beat_this_sidecar_client.o $(BUILD_DIR)/plugin.o $(BTT_OBJS) $(BASIC_PITCH_RUNTIME_OBJS)
ANALYZER_TEST_OBJ := $(BUILD_DIR)/analyzer_test.o $(BTT_OBJS) $(BASIC_PITCH_RUNTIME_OBJS)
TEST_BINS := $(BUILD_DIR)/fret_control_tests $(BUILD_DIR)/visualizer_renderer_tests $(BUILD_DIR)/analyzer_internal $(BUILD_DIR)/analyzer_smoke $(BUILD_DIR)/analyzer_cases $(BUILD_DIR)/analyzer_midi_ranges $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd $(BUILD_DIR)/analyzer_drum_samples $(BUILD_DIR)/analyzer_instrument_samples $(BUILD_DIR)/analyzer_real_note_samples $(BUILD_DIR)/analyzer_instrument_family_samples
BTT_PROBE := $(BUILD_DIR)/btt_tempo_probe
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
GOOD_SOUNDS_FULL_MIX_SHARDS ?= $(REAL_NOTE_FULL_MIX_SHARDS)
GOOD_SOUNDS_FULL_MIX_SHARD_INDEXES := $(shell i=0; while [ $$i -lt $(GOOD_SOUNDS_FULL_MIX_SHARDS) ]; do printf '%s ' $$i; i=$$((i + 1)); done)
GOOD_SOUNDS_FULL_MIX_SHARD_TARGETS := $(addprefix test-good-sounds-full-mix-shard-,$(GOOD_SOUNDS_FULL_MIX_SHARD_INDEXES))
GOOD_SOUNDS_FULL_MIX_SHARD_OUTS := $(addprefix $(BUILD_DIR)/good_sounds_full_mix_shard_,$(addsuffix .out,$(GOOD_SOUNDS_FULL_MIX_SHARD_INDEXES)))
GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/good_sounds_full_mix_attributes.shard-,$(addsuffix .tsv,$(GOOD_SOUNDS_FULL_MIX_SHARD_INDEXES)))
GOOD_SOUNDS_FULL_MIX_TEST_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GOOD_SOUNDS_FULL_MIX_SHARDS))
GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_MAKE_JOBS = $(if $(filter -j%,$(MAKEFLAGS)),,-j$(GOOD_SOUNDS_FULL_MIX_SHARDS))
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
REAL_NOTE_FULL_MIX_MIN_VISIBLE_LIT_EXACT_FAMILY_SAMPLE_PERCENT ?= bass=90 guitar=74 piano=67 vocals=90
REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_EXCLUDED_FAMILIES ?= other
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
	$(foreach family,$(REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_EXCLUDED_FAMILIES),--exclude-family "$(family)") \
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
IOWA_PIANO_FULL_MIX_ATTRIBUTE_LOCK_DIR ?= $(BUILD_DIR)/iowa_piano_full_mix_attributes.lock
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
IOWA_PIANO_FULL_MIX_ATTRIBUTE_PARTS := $(addprefix $(BUILD_DIR)/iowa_piano_full_mix_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))
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
.PHONY: find-real-note-row-confusion-patterns find-real-note-practical-row-confusion-patterns find-real-note-focused-row-confusion-patterns find-real-note-coverage-row-confusion-patterns find-real-note-visual-row-confusion-patterns find-real-note-focused-visual-row-confusion-patterns find-real-note-coverage-visual-row-confusion-patterns find-real-note-ownership-patterns find-real-note-octave-displacement-patterns find-real-note-octave-displacement-runtime-patterns find-real-note-weak-expected-patterns find-real-note-weak-visual-expected-patterns inspect-real-note-candidate-rows inspect-real-note-candidate-rows-cached inspect-real-note-full-mix-debug-cached inspect-detector-coverage-candidates measure-real-note-octave-display-aliases evaluate-real-note-display-shadow evaluate-real-note-vocal-shadow-safety evaluate-real-note-vocal-shadow-safety-nsynth evaluate-real-note-vocal-shadow-safety-vocadito evaluate-real-note-vocal-display-fallback measure-real-note-attribute-rule measure-electronic-piano-guitar-route-cached measure-scms-vocal-other-route-cached measure-tenor-sax-piano-route-cached analyze-vocadito-attributes analyze-vocadito-full-mix-attributes find-vocadito-full-mix-row-confusion-patterns find-vocadito-full-mix-visual-row-confusion-patterns find-vocadito-full-mix-ownership-patterns find-vocadito-full-mix-broad-vocal-ownership-patterns analyze-idmt-bass-lines-attributes analyze-idmt-guitar-attributes analyze-guitar-techs-attributes analyze-tinysol-attributes analyze-vocalset-attributes analyze-iowa-piano-attributes analyze-iowa-strings-attributes analyze-philharmonia-attributes analyze-philharmonia-full-attributes analyze-philharmonia-full-exact-midi-misses analyze-iowa-orchestra-attributes analyze-iowa-orchestra-full-attributes analyze-iowa-orchestra-full-exact-midi-misses summarize-iowa-orchestra-full-attributes inspect-iowa-orchestra-full-debug-cached
.PHONY: filter-drum-primary-attribute-rows filter-drum-full-attribute-rows filter-drum-full-exact-attribute-rows test-filter-drum-attribute-rows
.PHONY: test-build-sharded-tsv test-guitarset-shard-check test-instrument-family-shard-check test-musicnet-shard-check test-analyze-exact-midi-misses
.PHONY: prepare-guitar-techs-chord-case inspect-guitar-techs-chord-case refresh-guitar-techs-chord-attributes
.PHONY: prepare-gaps-guitar-samples-full test-gaps-guitar-samples-full analyze-gaps-guitar-misses-full analyze-gaps-guitar-attributes inspect-gaps-guitar-attribute-buckets find-gaps-guitar-attribute-patterns analyze-gaps-guitar-full-attributes inspect-gaps-guitar-full-attribute-buckets find-gaps-guitar-full-attribute-patterns test-good-sounds-full-mix test-good-sounds-full-mix-parallel analyze-good-sounds-full-mix-attributes refresh-good-sounds-full-mix-attributes-cached prepare-iowa-sax-full-mix-fixture measure-iowa-sax-full-mix find-iowa-sax-full-mix-row-confusion-patterns find-iowa-sax-full-mix-first-row-confusion-patterns prepare-tinysol-sax-full-mix-fixture measure-tinysol-sax-full-mix find-tinysol-sax-full-mix-first-row-confusion-patterns prepare-tinysol-flute-full-mix-fixture measure-tinysol-flute-full-mix find-tinysol-flute-full-mix-row-confusion-patterns prepare-tinysol-wind-exact-fixture measure-tinysol-wind-exact
.PHONY: analyze-guitarset-attributes inspect-guitarset-attribute-buckets find-guitarset-attribute-patterns analyze-egfxset-guitar-attributes inspect-egfxset-guitar-attribute-buckets find-egfxset-guitar-attribute-patterns
.PHONY: inspect-guitarset-download restore-guitarset-audio-partial test-guitarset-download-inspector
.PHONY: test-fret-control android-lint icon-assets
.PHONY: measure-analyzer-attributes measure-analyzer-attribute-rows measure-analyzer-attribute-rows-full require-cached-analyzer-attribute-rows refresh-analyzer-detected-attribute-rows print-analyzer-detected-attributes print-analyzer-detected-attributes-cached measure-analyzer-detected-attributes measure-analyzer-detected-attributes-full measure-analyzer-pattern-report-sections report-analyzer-patterns-from-rows report-analyzer-patterns-from-cached-rows report-analyzer-patterns-from-rows-full measure-analyzer-patterns measure-analyzer-patterns-cached measure-analyzer-patterns-cached-summary measure-analyzer-patterns-cached-coverage measure-analyzer-patterns-full measure-analyzer-pattern-report inspect-instrument-sample-owner-buckets find-instrument-owner-patterns find-instrument-status-patterns test-instrument-sample-owner-buckets test-filter-instrument-attribute-rows test-instrument-owner-patterns test-refresh-analyzer-detected-attribute-rows test-print-analyzer-detected-attributes test-analyzer-pattern-report test-detector-route-report-summary test-measure-analyzer-patterns-target analyze-drum-primary-attribute-rows find-drum-primary-attribute-patterns analyze-drum-spread-gate-matrix-serial analyze-drum-spread-gate-matrix-parallel analyze-drum-spread-gate-matrix-parallel-unlocked analyze-drum-tom-bleed-caps analyze-drum-tom-bleed-caps-cached
.PHONY: analyze-drum-spread-gate-matrix analyze-drum-full-gate-matrix analyze-drum-full-gate-matrix-parallel analyze-drum-full-merged-expected-attribute-rows analyze-drum-active-false-rows analyze-drum-rule-flags compare-drum-gate-matrix compare-drum-primary-scores find-drum-active-false-patterns find-drum-active-false-patterns-full find-drum-spread-exact-attribute-patterns find-drum-full-exact-attribute-patterns find-drum-full-exact-attribute-patterns-cached find-protected-drum-full-exact-attribute-patterns test-drum-gate-matrix-summary test-compare-drum-gate-summaries test-drum-active-threshold-simulation test-drum-active-false-summary test-drum-rule-flag-summary test-drum-active-false-patterns test-inspect-drum-candidate-rows test-inspect-real-note-candidate-rows test-inspect-detector-coverage-candidates
.PHONY: analyze-hf-drum-primary-attribute-rows analyze-hf-drum-primary-attribute-rows-serial analyze-hf-drum-primary-attribute-rows-parallel find-hf-drum-primary-attribute-patterns analyze-idmt-drum-primary-attribute-rows analyze-idmt-drum-primary-attribute-rows-serial analyze-idmt-drum-primary-attribute-rows-parallel find-idmt-drum-primary-attribute-patterns analyze-protected-drum-primary-attribute-rows find-protected-drum-primary-attribute-patterns
.PHONY: analyze-guitar-chord-mix-recovery analyze-guitar-chord-primary-order analyze-gaps-guitar-full-primary-order measure-guitar-chord-primary-display-audit-cached analyze-guitar-chord-mix-extra-components analyze-guitar-minor-third-candidates analyze-guitar-major-third-candidates analyze-guitar-minor-fifth-candidates analyze-guitar-major-fifth-candidates inspect-guitar-techs-chord-attribute-buckets find-guitar-techs-chord-attribute-patterns find-guitar-techs-chord-route-patterns find-guitar-chord-mix-route-patterns find-egfxset-guitar-route-patterns find-gaps-guitar-route-patterns find-gaps-guitar-full-route-patterns find-guitarset-route-patterns analyze-medley-solos-attributes analyze-medley-solos-attributes-cached inspect-medley-solos-misses inspect-medley-solos-misses-cached inspect-medley-solos-debug-cached refresh-medley-solos-attributes-cached test-guitar-chord-recovery-analysis test-guitar-primary-order-analysis test-guitar-chord-extra-components-analysis test-guitar-techs-chord-samples-parallel test-guitar-chord-mix-samples-serial test-guitar-chord-mix-samples-parallel test-egfxset-guitar-samples-parallel test-gaps-guitar-samples-parallel test-gaps-guitar-samples-full-parallel test-downloaded-guitarset-parallel
.PHONY: audition-sample
.PHONY: find-real-note-first-row-confusion-patterns find-real-note-first-visual-row-confusion-patterns
.PHONY: find-real-note-octave-displacement-cached
.PHONY: analyze-real-note-misses-serial analyze-real-note-misses-parallel analyze-real-note-misses-shard-%
.PHONY: test-vocadito-samples-full-mix-parallel-unlocked
.PHONY: test-parallel test-core-parallel test-analysis-scripts-parallel test-fixtures-parallel test-fixtures-parallel-isolated test-real-note-sample-shards test-real-note-sample-shards-unlocked test-real-note-sample-shard-% $(REAL_NOTE_SAMPLE_PARALLEL_TARGETS) test-real-note-samples-full-mix-serial test-real-note-samples-full-mix-parallel test-real-note-samples-full-mix-parallel-unlocked test-real-note-samples-full-mix-detector-parallel test-real-note-visual-strength test-real-note-full-mix-shard-check test-real-note-sample-shard-check test-instrument-samples-serial test-instrument-samples-parallel test-visualizer-renderer test-analyzer-internal test-analyzer-smoke test-analyzer-cases test-analyzer-midi-ranges test-analyzer-urmp test-analyzer-musicnet test-analyzer-multtipop test-analyzer-guitarset test-analyzer-maestro test-analyzer-egmd test-beat-this-sidecar-client
.PHONY: run-repo-script

# Run a repository-maintained helper through Make.  Keep one-off inspection and
# maintenance commands in scripts/ so invocation follows the same audit trail
# as build and test targets: make -s run-repo-script SCRIPT=scripts/name.sh.
run-repo-script:
	@test -n "$(SCRIPT)" || { printf '%s\n' 'set SCRIPT=scripts/<name>.sh'; exit 2; }
	@/bin/sh scripts/run_repo_script.sh "$(SCRIPT)" $(ARGS)
.PHONY: prepare-real-goal-fixtures-parallel $(REAL_GOAL_FIXTURE_PREP_TARGETS)
.PHONY: test-drum-real-world-samples-parallel test-drum-real-world-samples-full-parallel test-real-world-samples-parallel test-real-world-samples-full-parallel test-real-world-samples-max-parallel test-drum-samples-optional test-drum-samples-spread-optional test-drum-machine-samples-optional test-drum-samples-full-optional test-idmt-bass-lines-samples-optional test-idmt-guitar-samples-optional test-good-sounds-samples-optional test-medley-solos-samples-optional test-medley-solos-samples-serial test-medley-solos-samples-parallel test-medley-solos-samples-parallel-unlocked test-medley-solos-samples-shard-% test-maps-piano-samples-optional test-maps-piano-note-samples-optional test-bach10-mf0-synth-samples-optional test-bach10-mf0-synth-samples-serial test-bach10-mf0-synth-samples-parallel test-bach10-mf0-synth-samples-parallel-unlocked test-bach10-mf0-synth-samples-shard-% analyze-bach10-mf0-synth-chord-misses analyze-bach10-mf0-synth-pitch-misses test-vocalset-samples-optional test-vocalset-samples-full-mix-optional
.PHONY: test-drum-samples-full-serial test-drum-samples-full-parallel test-drum-samples-full-parallel-unlocked test-drum-samples-full-shard-% test-drum-machine-samples-serial test-drum-machine-samples-parallel test-drum-machine-samples-parallel-unlocked test-drum-machine-samples-shard-% test-hf-drum-kit-samples-serial test-hf-drum-kit-samples-parallel test-hf-drum-kit-samples-parallel-unlocked test-hf-drum-kit-samples-shard-% test-idmt-drums-samples-serial test-idmt-drums-samples-parallel test-idmt-drums-samples-parallel-unlocked test-idmt-drums-samples-shard-% test-drum-samples-full-parallel-optional test-drum-sample-shard-check
.PHONY: test-iowa-piano-samples-max test-iowa-orchestra-full-samples-max test-good-sounds-samples-max test-medley-solos-samples-max test-maps-piano-samples-max test-maps-piano-note-samples-max measure-maps-piano-cached measure-maps-piano-cached-shard-% measure-maps-piano-note-cached measure-maps-piano-note-cached-shard-% refresh-maps-piano-note-attributes-cached refresh-maps-piano-note-attributes-cached-shard-% analyze-maps-piano-attributes-cached analyze-maps-piano-note-attributes-cached
.PHONY: capture-analyzer-cases
.PHONY: detector-improvement-samples detector-improvement-patterns detector-improvement-patterns-cached detector-improvement-patterns-cached-summary detector-improvement-routes detector-improvement-route-report detector-improvement-route-report-refresh detector-improvement-route-summary detector-improvement-route-summary-cached detector-improvement-route-summary-from-cached-report detector-improvement-route-summary-refresh detector-improvement-coverage-cached detector-improvement-status-cached detector-improvement-samples-full detector-improvement-patterns-full detector-improvement-audit detector-improvement-audit-cached detector-improvement-audit-report detector-improvement-audit-report-cached analyze-detector-improvements analyze-detector-improvement-routes analyze-detector-improvements-full

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

# Optional research-only ONNX probe.  It is deliberately not a prerequisite of
# `all` or `install-user`: the live fusion path must first pass protected-corpus
# gates and run off the OBS audio thread.
$(ONNXRUNTIME_HEADER) $(BASIC_PITCH_ONNX_MODEL): scripts/download_basic_pitch_onnx_probe.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_basic_pitch_onnx_probe.sh "$(ONNXRUNTIME_VERSION)" "$(ONNXRUNTIME_ROOT)" "$(BASIC_PITCH_ONNX_MODEL)"

$(BUILD_DIR)/basic_pitch_onnx_probe.o: tests/basic_pitch_onnx_probe.cpp $(ONNXRUNTIME_HEADER) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -I"$(ONNXRUNTIME_ROOT)/include" -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_probe: $(BUILD_DIR)/basic_pitch_onnx_probe.o
	$(CXX) -o $@ $^ -ldl

.PHONY: test-basic-pitch-onnx-probe
test-basic-pitch-onnx-probe: $(BUILD_DIR)/basic_pitch_onnx_probe $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_onnx_probe "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

$(BUILD_DIR)/basic_pitch_onnx_runtime.o: src/basic_pitch_onnx_runtime.cpp src/basic_pitch_onnx_runtime.hpp $(ONNXRUNTIME_HEADER) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -I"$(ONNXRUNTIME_ROOT)/include" -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_runtime_tests.o: tests/basic_pitch_onnx_runtime.cpp src/basic_pitch_onnx_runtime.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_runtime_tests: $(BUILD_DIR)/basic_pitch_onnx_runtime.o $(BUILD_DIR)/basic_pitch_onnx_runtime_tests.o
	$(CXX) -o $@ $^ -ldl

.PHONY: test-basic-pitch-onnx-runtime
test-basic-pitch-onnx-runtime: $(BUILD_DIR)/basic_pitch_onnx_runtime_tests $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_onnx_runtime_tests "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

$(BUILD_DIR)/basic_pitch_onnx_signal_tests.o: tests/basic_pitch_onnx_signal.cpp src/basic_pitch_onnx_runtime.hpp src/basic_pitch_onnx_decoder.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_signal_tests: $(BUILD_DIR)/basic_pitch_onnx_runtime.o $(BUILD_DIR)/basic_pitch_onnx_decoder.o $(BUILD_DIR)/basic_pitch_onnx_signal_tests.o
	$(CXX) -o $@ $^ -ldl

.PHONY: test-basic-pitch-onnx-signal
test-basic-pitch-onnx-signal: $(BUILD_DIR)/basic_pitch_onnx_signal_tests $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_onnx_signal_tests "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

$(BUILD_DIR)/basic_pitch_onnx_decoder.o: src/basic_pitch_onnx_decoder.cpp src/basic_pitch_onnx_decoder.hpp src/basic_pitch_onnx_runtime.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_decoder_tests.o: tests/basic_pitch_onnx_decoder.cpp src/basic_pitch_onnx_decoder.hpp src/basic_pitch_onnx_runtime.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_decoder_tests: $(BUILD_DIR)/basic_pitch_onnx_decoder.o $(BUILD_DIR)/basic_pitch_onnx_decoder_tests.o
	$(CXX) -o $@ $^

.PHONY: test-basic-pitch-onnx-decoder
test-basic-pitch-onnx-decoder: $(BUILD_DIR)/basic_pitch_onnx_decoder_tests
	$(BUILD_DIR)/basic_pitch_onnx_decoder_tests

$(BUILD_DIR)/basic_pitch_onnx_worker.o: src/basic_pitch_onnx_worker.cpp src/basic_pitch_onnx_worker.hpp src/basic_pitch_onnx_runtime.hpp src/basic_pitch_onnx_decoder.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_worker_tests.o: tests/basic_pitch_onnx_worker.cpp src/basic_pitch_onnx_worker.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_worker_tests: $(BUILD_DIR)/basic_pitch_onnx_runtime.o $(BUILD_DIR)/basic_pitch_onnx_decoder.o $(BUILD_DIR)/basic_pitch_onnx_worker.o $(BUILD_DIR)/basic_pitch_onnx_worker_tests.o
	$(CXX) -o $@ $^ -ldl -pthread

.PHONY: test-basic-pitch-onnx-worker
test-basic-pitch-onnx-worker: $(BUILD_DIR)/basic_pitch_onnx_worker_tests $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	$(BUILD_DIR)/basic_pitch_onnx_worker_tests "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

$(BUILD_DIR)/basic_pitch_pcm_history.o: src/basic_pitch_pcm_history.cpp src/basic_pitch_pcm_history.hpp src/basic_pitch_onnx_runtime.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_pcm_history_tests.o: tests/basic_pitch_pcm_history.cpp src/basic_pitch_pcm_history.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_pcm_history_tests: $(BUILD_DIR)/basic_pitch_pcm_history.o $(BUILD_DIR)/basic_pitch_pcm_history_tests.o
	$(CXX) -o $@ $^

.PHONY: test-basic-pitch-pcm-history
test-basic-pitch-pcm-history: $(BUILD_DIR)/basic_pitch_pcm_history_tests
	$(BUILD_DIR)/basic_pitch_pcm_history_tests

$(BUILD_DIR)/basic_pitch_vocal_fusion_tests.o: tests/basic_pitch_vocal_fusion.cpp src/basic_pitch_vocal_fusion.hpp src/analyzer.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/basic_pitch_vocal_fusion_tests: $(BUILD_DIR)/basic_pitch_vocal_fusion_tests.o
	$(CXX) -o $@ $^

.PHONY: test-basic-pitch-vocal-fusion
test-basic-pitch-vocal-fusion: $(BUILD_DIR)/basic_pitch_vocal_fusion_tests
	$(BUILD_DIR)/basic_pitch_vocal_fusion_tests

.PHONY: test-basic-pitch-onnx inspect-basic-pitch-owner-evidence-core diagnose-basic-pitch-owner-evidence-asan
test-basic-pitch-onnx: test-basic-pitch-onnx-probe test-basic-pitch-onnx-runtime test-basic-pitch-onnx-signal test-basic-pitch-onnx-decoder test-basic-pitch-onnx-worker test-basic-pitch-pcm-history test-basic-pitch-vocal-fusion


inspect-basic-pitch-owner-evidence-core: $(BUILD_DIR)/basic_pitch_onnx_musicnet scripts/inspect_basic_pitch_core.sh
	$(SHELL) scripts/inspect_basic_pitch_core.sh "$(BUILD_DIR)/basic_pitch_onnx_musicnet" core

BASIC_PITCH_OWNER_EVIDENCE_ASAN_LOG ?= $(BUILD_DIR)/basic_pitch_owner_evidence_asan.log

diagnose-basic-pitch-owner-evidence-asan: $(BUILD_DIR)/basic_pitch_onnx_musicnet scripts/run_basic_pitch_owner_evidence_asan.sh
	$(SHELL) scripts/run_basic_pitch_owner_evidence_asan.sh "$(MAKE)" "$(BUILD_DIR)/basic_pitch_onnx_musicnet" "$(CXXFLAGS)" "$(LDFLAGS)" "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" "$(BASIC_PITCH_OWNER_EVIDENCE_ASAN_LOG)"

BASIC_PITCH_ONNX_CHOIR_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_choir_replay.tsv
BASIC_PITCH_ONNX_FUSION_THRESHOLD ?= 0.30

$(BUILD_DIR)/basic_pitch_onnx_musicnet.o: tests/basic_pitch_onnx_musicnet.cpp src/basic_pitch_onnx_runtime.hpp src/basic_pitch_onnx_decoder.hpp src/basic_pitch_pcm_history.hpp src/basic_pitch_vocal_fusion.hpp tests/analyzer_musicnet.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -I$(BTT_SOURCE_DIR) -c $< -o $@

$(BUILD_DIR)/basic_pitch_onnx_musicnet: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/basic_pitch_onnx_musicnet.o
	$(CXX) $(LDFLAGS) -o $@ $^ -ldl -lm -pthread

$(BASIC_PITCH_ONNX_CHOIR_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" true-miss "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" true-miss "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" true-miss "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-choir
measure-basic-pitch-onnx-choir: $(BASIC_PITCH_ONNX_CHOIR_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CHOIR_REPLAY)"

BASIC_PITCH_ONNX_CHOIR_FULL_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_choir_full_replay.tsv
BASIC_PITCH_ONNX_CHOIR_SAFE_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_choir_safe_replay.tsv
BASIC_PITCH_ONNX_CHOIR_STRICT_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_choir_strict_replay.tsv
BASIC_PITCH_ONNX_MUSICNET_SAFE_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_musicnet_safe_replay.tsv
BASIC_PITCH_ONNX_MUSICNET_STRICT_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_musicnet_strict_replay.tsv
BASIC_PITCH_ONNX_CROSS_DOMAIN_SAFE_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_cross_domain_safe_replay.tsv
BASIC_PITCH_ONNX_CROSS_DOMAIN_WORKER_SAFE_REPLAY ?= $(BUILD_DIR)/basic_pitch_onnx_cross_domain_worker_safe_replay.tsv
BASIC_PITCH_ONNX_OWNER_EVIDENCE ?= $(BUILD_DIR)/basic_pitch_onnx_owner_evidence.tsv
BASIC_PITCH_ONNX_OWNER_EVIDENCE_AUDIT ?= $(BUILD_DIR)/basic_pitch_onnx_owner_evidence_audit.txt

$(BASIC_PITCH_ONNX_CHOIR_FULL_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-choir-full
measure-basic-pitch-onnx-choir-full: $(BASIC_PITCH_ONNX_CHOIR_FULL_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CHOIR_FULL_REPLAY)"

$(BASIC_PITCH_ONNX_CHOIR_SAFE_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.70; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.70; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.70; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-choir-safe
measure-basic-pitch-onnx-choir-safe: $(BASIC_PITCH_ONNX_CHOIR_SAFE_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CHOIR_SAFE_REPLAY)"

$(BASIC_PITCH_ONNX_CHOIR_STRICT_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.80; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.80; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.80; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-choir-strict
measure-basic-pitch-onnx-choir-strict: $(BASIC_PITCH_ONNX_CHOIR_STRICT_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CHOIR_STRICT_REPLAY)"

$(BASIC_PITCH_ONNX_MUSICNET_SAFE_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet MusicNet "$(MUSICNET_EXTRACT_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.70; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-musicnet-safe
measure-basic-pitch-onnx-musicnet-safe: $(BASIC_PITCH_ONNX_MUSICNET_SAFE_REPLAY)
	cat "$(BASIC_PITCH_ONNX_MUSICNET_SAFE_REPLAY)"

$(BASIC_PITCH_ONNX_MUSICNET_STRICT_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet MusicNet "$(MUSICNET_EXTRACT_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.80; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-musicnet-strict
measure-basic-pitch-onnx-musicnet-strict: $(BASIC_PITCH_ONNX_MUSICNET_STRICT_REPLAY)
	cat "$(BASIC_PITCH_ONNX_MUSICNET_STRICT_REPLAY)"

$(BASIC_PITCH_ONNX_CROSS_DOMAIN_SAFE_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet MusicNet "$(MUSICNET_EXTRACT_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all 0.85; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-cross-domain-safe
measure-basic-pitch-onnx-cross-domain-safe: $(BASIC_PITCH_ONNX_CROSS_DOMAIN_SAFE_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CROSS_DOMAIN_SAFE_REPLAY)"

$(BASIC_PITCH_ONNX_CROSS_DOMAIN_WORKER_SAFE_REPLAY): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { \
		printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" worker 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" worker 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" worker 0.85; \
		$(BUILD_DIR)/basic_pitch_onnx_musicnet MusicNet "$(MUSICNET_EXTRACT_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" worker 0.85; \
	} > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-cross-domain-worker-safe
measure-basic-pitch-onnx-cross-domain-worker-safe: $(BASIC_PITCH_ONNX_CROSS_DOMAIN_WORKER_SAFE_REPLAY)
	cat "$(BASIC_PITCH_ONNX_CROSS_DOMAIN_WORKER_SAFE_REPLAY)"

$(BASIC_PITCH_ONNX_OWNER_EVIDENCE): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/measure_basic_pitch_onnx_owner_evidence.sh | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(SHELL) scripts/measure_basic_pitch_onnx_owner_evidence.sh "$(BUILD_DIR)/basic_pitch_onnx_musicnet" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(MUSICNET_EXTRACT_DIR)" > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-owner-evidence
measure-basic-pitch-onnx-owner-evidence: $(BASIC_PITCH_ONNX_OWNER_EVIDENCE)
	cat "$(BASIC_PITCH_ONNX_OWNER_EVIDENCE)"

$(BASIC_PITCH_ONNX_OWNER_EVIDENCE_AUDIT): $(BASIC_PITCH_ONNX_OWNER_EVIDENCE) scripts/summarize_basic_pitch_owner_evidence.py | $(BUILD_DIR)
	$(PYTHON) scripts/summarize_basic_pitch_owner_evidence.py "$(BASIC_PITCH_ONNX_OWNER_EVIDENCE)" --output "$@"

.PHONY: summarize-basic-pitch-onnx-owner-evidence
summarize-basic-pitch-onnx-owner-evidence: $(BASIC_PITCH_ONNX_OWNER_EVIDENCE_AUDIT)
	cat "$(BASIC_PITCH_ONNX_OWNER_EVIDENCE_AUDIT)"

.PHONY: measure-basic-pitch-onnx-musicnet-at-threshold
measure-basic-pitch-onnx-musicnet-at-threshold: $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet MusicNet "$(MUSICNET_EXTRACT_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"

.PHONY: measure-basic-pitch-onnx-choir-full-at-threshold
measure-basic-pitch-onnx-choir-full-at-threshold: $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" all "$(BASIC_PITCH_ONNX_FUSION_THRESHOLD)"

.PHONY: measure-basic-pitch-sequential-choir
measure-basic-pitch-sequential-choir: $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
	@printf 'corpus\tthreshold\twindows\texpected\tnative_hits\tonnx_hits\tfused_hits\tnovel_correct\tnovel_false\n'; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet DCS "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" sequential 0.80; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet CSD "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" sequential 0.80; \
	$(BUILD_DIR)/basic_pitch_onnx_musicnet ESMUC "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" sequential 0.80

BASIC_PITCH_ONNX_STRICT_SWEEP ?= $(BUILD_DIR)/basic_pitch_onnx_strict_sweep.tsv

$(BASIC_PITCH_ONNX_STRICT_SWEEP): $(BUILD_DIR)/basic_pitch_onnx_musicnet $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/measure_basic_pitch_onnx_strict_sweep.sh | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(SHELL) scripts/measure_basic_pitch_onnx_strict_sweep.sh "$(BUILD_DIR)/basic_pitch_onnx_musicnet" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)" "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" "$(MUSICNET_EXTRACT_DIR)" > "$$tmp" && mv "$$tmp" "$@"

.PHONY: measure-basic-pitch-onnx-strict-sweep
measure-basic-pitch-onnx-strict-sweep: $(BASIC_PITCH_ONNX_STRICT_SWEEP)
	cat "$(BASIC_PITCH_ONNX_STRICT_SWEEP)"

$(BUILD_DIR)/music-analyzer-obs.so: $(PLUGIN_OBJS)
	$(CXX) -shared -o $@ $^ $(OBS_LIBS) -pthread

$(BUILD_DIR)/plugin.o: src/plugin.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(SIMDE_DEP) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(BUILD_DIR)/beat_this_sidecar_client.o: src/beat_this_sidecar_client.cpp src/beat_this_sidecar_client.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/beat_this_sidecar_client_tests.o: tests/beat_this_sidecar_client.cpp src/beat_this_sidecar_client.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/beat_this_sidecar_client_tests: $(BUILD_DIR)/beat_this_sidecar_client.o $(BUILD_DIR)/beat_this_sidecar_client_tests.o
	tmp="$@.$$$$.tmp"; $(CXX) -o "$$tmp" $^ && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer.o: src/analyzer.cpp src/analyzer.hpp src/basic_pitch_vocal_fusion.hpp src/basic_pitch_onnx_worker.hpp src/basic_pitch_pcm_history.hpp $(BTT_SOURCE_DIR)/BTT.h | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) -Isrc -I$(BTT_SOURCE_DIR) -c $< -o $@

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

$(BUILD_DIR)/visualizer_renderer_tests: $(BUILD_DIR)/visualizer_renderer_tests.o $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/fret_control.o
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

$(BUILD_DIR)/analyzer_test.o: src/analyzer.cpp src/analyzer.hpp src/basic_pitch_vocal_fusion.hpp src/basic_pitch_onnx_worker.hpp src/basic_pitch_pcm_history.hpp $(BTT_SOURCE_DIR)/BTT.h | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -I$(BTT_SOURCE_DIR) -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/btt_%.o: $(BTT_SOURCE_DIR)/src/%.c $(BTT_SOURCE_DIR)/BTT.h | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CC) $(CFLAGS) -fPIC -I$(BTT_SOURCE_DIR) -I$(BTT_SOURCE_DIR)/src -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_smoke.o: tests/analyzer_smoke.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o "$$tmp" && mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_internal.o: tests/analyzer_internal.cpp src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -Itests -I$(BTT_SOURCE_DIR) -c $< -o "$$tmp" && mv "$$tmp" "$@"

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


$(BUILD_DIR)/analyzer_internal: $(BUILD_DIR)/analyzer_internal.o $(BTT_OBJS) $(BASIC_PITCH_RUNTIME_OBJS)
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

$(BTT_PROBE): tests/btt_tempo_probe.c $(BTT_SOURCE_DIR)/BTT.h $(BTT_SOURCE_DIR)/demos/offline/MKAiff.c $(wildcard $(BTT_SOURCE_DIR)/src/*.c) | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CC) $(CFLAGS) -I$(BTT_SOURCE_DIR) -I$(BTT_SOURCE_DIR)/demos/offline $^ -lm -o "$$tmp" && mv "$$tmp" "$@"

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

# Independent CC0 TR-505 one-shots.  Keep both the source and the generated
# manifest in InstrumentSamples; build/ must not accumulate copied samples.
.PHONY: download-0x808-cc0-drum-samples prepare-0x808-rim-samples measure-0x808-rim-samples
download-0x808-cc0-drum-samples: scripts/download_0x808_cc0_drum_samples.sh
	$(SHELL) scripts/download_0x808_cc0_drum_samples.sh "$(ZEROX808_CC0_SOURCE_DIR)" "$(ZEROX808_CC0_REPOSITORY)"

prepare-0x808-rim-samples: download-0x808-cc0-drum-samples scripts/prepare_drum_samples.py
	+$(MAKE) prepare-drum-samples DRUM_SAMPLE_SOURCE_DIR="$(ZEROX808_CC0_SOURCE_DIR)/samples" DRUM_SAMPLE_BUILD_DIR="$(ZEROX808_RIM_SAMPLE_DIR)" DRUM_SAMPLE_LIMIT=32 DRUM_SAMPLE_SELECTION=spread

measure-0x808-rim-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-0x808-rim-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_0x808_rim_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(ZEROX808_RIM_SAMPLE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(ZEROX808_RIM_MEASUREMENT)" 2>&1

$(ZEROX808_RIM_PRIMARY_DEBUG_ERR): $(BUILD_DIR)/analyzer_drum_samples prepare-0x808-rim-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_0x808_rim_primary_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=32 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(ZEROX808_RIM_SAMPLE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(ZEROX808_RIM_PRIMARY_DEBUG_OUT)" 2> "$@"

$(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS): $(ZEROX808_RIM_PRIMARY_DEBUG_ERR) scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(ZEROX808_RIM_PRIMARY_DEBUG_ERR)" > "$@"

.PHONY: analyze-0x808-rim-primary-attributes
analyze-0x808-rim-primary-attributes: $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)
	@printf '%s\n' "0x808 Rim primary attribute TSV: $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)"

.PHONY: find-0x808-virtuosity-rim-primary-patterns
find-0x808-virtuosity-rim-primary-patterns: $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS) $(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS) scripts/find_drum_attribute_patterns.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)" "$(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --route "rim->snare" --route "rim->crash" --min-positive-samples 2 --max-negative-samples 0 --max-new-active-samples 0 --max-primary-break-samples 0 --max-conditions 2 --beam-width 96 --require-positive-source 0x808_rim_primary_attribute_rows --require-positive-source virtuosity_drums_primary_attribute_rows --profile-fields 10 --show-near-misses 6 --jobs 1 > "$(ZEROX808_VIRTUOSITY_RIM_CANDIDATE_AUDIT)"
	@printf '%s\n' "0x808/Virtuosity Rim candidate audit: $(ZEROX808_VIRTUOSITY_RIM_CANDIDATE_AUDIT)"

.PHONY: evaluate-rim-primary-candidate
evaluate-rim-primary-candidate: $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS) $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS) scripts/evaluate_rim_primary_candidate.py
	$(PYTHON) scripts/evaluate_rim_primary_candidate.py "$(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)" $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS) > "$(RIM_PRIMARY_CANDIDATE_AUDIT)"
	@cat "$(RIM_PRIMARY_CANDIDATE_AUDIT)"

# Independently recorded CC0 acoustic rimshot/rim-click material. The archive
# and generated manifest remain in InstrumentSamples, so build/ only holds
# transient analysis logs.
.PHONY: download-unruly-drums-samples inspect-unruly-drums-rim-paths prepare-unruly-drums-rim-samples measure-unruly-drums-rim-samples analyze-unruly-drums-rim-primary find-unruly-cross-source-rim-primary-patterns evaluate-unruly-rim-primary-candidate
download-unruly-drums-samples: scripts/download_unruly_drums_samples.sh
	$(SHELL) scripts/download_unruly_drums_samples.sh "$(UNRULY_DRUMS_ARCHIVE)" "$(UNRULY_DRUMS_ARCHIVE_URL)" "$(UNRULY_DRUMS_DOWNLOAD_CHUNKS)"

inspect-unruly-drums-rim-paths: download-unruly-drums-samples scripts/inspect_unruly_drums_rim_paths.sh
	$(SHELL) scripts/inspect_unruly_drums_rim_paths.sh "$(UNRULY_DRUMS_ARCHIVE)"

prepare-unruly-drums-rim-samples: download-unruly-drums-samples scripts/prepare_unruly_drums_rim_samples.py
	$(PYTHON) scripts/prepare_unruly_drums_rim_samples.py --archive "$(UNRULY_DRUMS_ARCHIVE)" --output "$(UNRULY_DRUMS_RIM_SAMPLE_DIR)" --limit 96

measure-unruly-drums-rim-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-unruly-drums-rim-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_unruly_drums_rim_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(UNRULY_DRUMS_RIM_SAMPLE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(UNRULY_DRUMS_RIM_MEASUREMENT)" 2>&1

$(UNRULY_DRUMS_RIM_PRIMARY_DEBUG_ERR): $(BUILD_DIR)/analyzer_drum_samples prepare-unruly-drums-rim-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_unruly_drums_rim_primary_debug env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=128 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(UNRULY_DRUMS_RIM_SAMPLE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(UNRULY_DRUMS_RIM_PRIMARY_DEBUG_OUT)" 2> "$@"

$(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS): $(UNRULY_DRUMS_RIM_PRIMARY_DEBUG_ERR) scripts/analyze_drum_primary_debug.py
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(UNRULY_DRUMS_RIM_PRIMARY_DEBUG_ERR)" > "$@"

analyze-unruly-drums-rim-primary: $(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS)
	@printf '%s\n' "unruly drums rim primary TSV: $(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS)"

find-unruly-cross-source-rim-primary-patterns: $(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS) $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS) $(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS) scripts/find_drum_attribute_patterns.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS)" "$(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)" "$(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --route "rim->snare" --route "rim->crash" --min-positive-samples 2 --max-negative-samples 0 --max-new-active-samples 0 --max-primary-break-samples 0 --max-conditions 2 --beam-width 96 --require-positive-source unruly_drums_rim_primary_attribute_rows --require-positive-source 0x808_rim_primary_attribute_rows --require-positive-source virtuosity_drums_primary_attribute_rows --profile-fields 10 --show-near-misses 8 --jobs 1 > "$(UNRULY_CROSS_SOURCE_RIM_CANDIDATE_AUDIT)"
	@printf '%s\n' "Unruly cross-source Rim candidate audit: $(UNRULY_CROSS_SOURCE_RIM_CANDIDATE_AUDIT)"

evaluate-unruly-rim-primary-candidate: $(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS) $(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS) $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS) scripts/evaluate_rim_primary_candidate.py
	$(PYTHON) scripts/evaluate_rim_primary_candidate.py --candidate-name unruly_cross_source_rim_v1 --condition 'crash_band>=1.033' --condition 'snare_kick_body_ratio<=1.674' "$(UNRULY_DRUMS_RIM_PRIMARY_ATTRIBUTE_ROWS)" "$(ZEROX808_RIM_PRIMARY_ATTRIBUTE_ROWS)" $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS) > "$(UNRULY_RIM_PRIMARY_CANDIDATE_AUDIT)"
	@cat "$(UNRULY_RIM_PRIMARY_CANDIDATE_AUDIT)"

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

prepare-mdb-drums-samples: scripts/prepare_mdb_drums_samples.py scripts/run_with_lock.sh | $(BUILD_DIR)
	+@if [ -L "$(MDB_DRUMS_SAMPLE_DIR)" ]; then :; else $(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR="$(notdir $(MDB_DRUMS_SAMPLE_DIR))"; fi
	$(SHELL) scripts/run_with_lock.sh "$(MDB_DRUMS_PREP_LOCK_DIR)" -- env MDB_DRUMS_SAMPLE_DIR="$(MDB_DRUMS_SAMPLE_DIR)" MDB_DRUMS_SOURCE_ROOT="$(MDB_DRUMS_SOURCE_ROOT)" MDB_DRUMS_AUDIO_FLAVOR="$(MDB_DRUMS_AUDIO_FLAVOR)" MDB_DRUMS_RECORDING_LIMIT="$(MDB_DRUMS_RECORDING_LIMIT)" MDB_DRUMS_MIN_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_mdb_drums_samples.py --output "$(MDB_DRUMS_SAMPLE_DIR)" --source-root "$(MDB_DRUMS_SOURCE_ROOT)" --audio-flavor "$(MDB_DRUMS_AUDIO_FLAVOR)" --limit "$(MDB_DRUMS_RECORDING_LIMIT)" --min-recordings "$(MDB_DRUMS_MIN_RECORDINGS)"

.PHONY: download-babyslakh probe-babyslakh-download test-download-babyslakh-script download-babyslakh-background stop-babyslakh-background reset-babyslakh-download-control finalize-babyslakh-download discard-babyslakh-corrupt-partial inspect-babyslakh-download inspect-babyslakh-downloader test-download-babyslakh-background-scripts test-babyslakh-background-extraction-scripts inspect-babyslakh-extraction extract-babyslakh-background test-inspect-babyslakh-archive test-extract-babyslakh-archive test-prepare-babyslakh-drums inspect-babyslakh-archive inspect-babyslakh-archive-existing extract-babyslakh inspect-babyslakh prepare-babyslakh-drums measure-babyslakh-drums
.PHONY: probe-egmd-download check-egmd-storage download-egmd-background inspect-egmd-download test-probe-egmd-download-script test-check-egmd-storage-script test-download-egmd-script test-start-egmd-download-script test-inspect-egmd-download-script download-enst-drums inspect-enst-drums prepare-enst-drums-samples measure-enst-drums test-download-enst-drums-script test-prepare-enst-drums-samples probe-virtuosity-drums-source test-probe-virtuosity-drums-source download-virtuosity-drums test-download-virtuosity-drums-script prepare-virtuosity-drums-samples measure-virtuosity-drums analyze-virtuosity-drums-primary-attribute-rows find-virtuosity-drum-primary-attribute-patterns test-prepare-virtuosity-drums-samples download-29k-drums inspect-29k-drums-download inspect-29k-drums-archive prepare-29k-drums-samples measure-29k-drums analyze-29k-drums-primary-attribute-rows find-29k-drum-primary-attribute-patterns find-cached-protected-drum-primary-attribute-patterns test-download-29k-drums-script test-inspect-29k-drums-download test-inspect-29k-drums-archive test-prepare-29k-drums-samples test-measure-29k-drums-makefile download-fsd50k-rim-metadata inspect-fsd50k-rim-metadata test-download-fsd50k-rim-metadata-script test-inspect-fsd50k-rim-metadata
probe-egmd-download: scripts/probe_egmd_download.sh
	$(SHELL) scripts/probe_egmd_download.sh "$(EGMD_ARCHIVE_URL)"

test-probe-egmd-download-script: scripts/probe_egmd_download.sh
	sh -n scripts/probe_egmd_download.sh

check-egmd-storage: scripts/check_egmd_storage.sh
	$(SHELL) scripts/check_egmd_storage.sh "$(EGMD_SOURCE_DIR)" "$(EGMD_ARCHIVE_BYTES)"

test-check-egmd-storage-script: scripts/check_egmd_storage.sh
	sh -n scripts/check_egmd_storage.sh

download-egmd-background: check-egmd-storage scripts/download_egmd.sh scripts/start_egmd_download.sh | $(BUILD_DIR)
	$(SHELL) scripts/start_egmd_download.sh "$(CURDIR)/scripts/download_egmd.sh" "$(EGMD_ARCHIVE)" "$(EGMD_ARCHIVE_URL)" "$(EGMD_ARCHIVE_MD5)" "$(EGMD_DOWNLOAD_LOG)" "$(EGMD_DOWNLOAD_PID)"

inspect-egmd-download: scripts/inspect_egmd_download.sh
	$(SHELL) scripts/inspect_egmd_download.sh "$(EGMD_ARCHIVE)" "$(EGMD_DOWNLOAD_LOG)" "$(EGMD_DOWNLOAD_PID)"

test-download-egmd-script: scripts/download_egmd.sh
	sh -n scripts/download_egmd.sh

test-start-egmd-download-script: scripts/start_egmd_download.sh
	sh -n scripts/start_egmd_download.sh

test-inspect-egmd-download-script: scripts/inspect_egmd_download.sh
	sh -n scripts/inspect_egmd_download.sh

download-enst-drums: scripts/download_enst_drums.sh
	$(SHELL) scripts/download_enst_drums.sh "$(ENST_DRUMS_ARCHIVE)" "$(ENST_DRUMS_ARCHIVE_URL)" "$(ENST_DRUMS_ARCHIVE_MD5)" "$(ENST_DRUMS_LICENSE_ACCEPTED)"

inspect-enst-drums: download-enst-drums scripts/inspect_enst_drums_archive.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_enst_drums_archive.py "$(ENST_DRUMS_ARCHIVE)" > "$(ENST_DRUMS_INSPECTION)"
	cat "$(ENST_DRUMS_INSPECTION)"

prepare-enst-drums-samples: inspect-enst-drums scripts/prepare_enst_drums_samples.py
	+@if [ -L "$(ENST_DRUMS_SAMPLE_DIR)" ]; then :; else $(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR="$(notdir $(ENST_DRUMS_SAMPLE_DIR))"; fi
	$(PYTHON) scripts/prepare_enst_drums_samples.py --archive "$(ENST_DRUMS_ARCHIVE)" --output "$(ENST_DRUMS_SAMPLE_DIR)" --limit-per-category "$(ENST_DRUMS_LIMIT_PER_CATEGORY)" --min-per-category "$(ENST_DRUMS_MIN_PER_CATEGORY)" --reset-generated

measure-enst-drums: $(BUILD_DIR)/analyzer_drum_samples prepare-enst-drums-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="tom,ride,rim" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SAMPLES_PER_CATEGORY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=4000 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(ENST_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(ENST_DRUMS_MEASUREMENT)" 2>&1
	cat "$(ENST_DRUMS_MEASUREMENT)"

test-prepare-enst-drums-samples: tests/test_prepare_enst_drums_samples.py scripts/prepare_enst_drums_samples.py
	$(PYTHON) tests/test_prepare_enst_drums_samples.py

probe-virtuosity-drums-source: scripts/probe_virtuosity_drums_source.sh | $(BUILD_DIR)
	$(SHELL) scripts/probe_virtuosity_drums_source.sh "$(VIRTUOSITY_DRUMS_REPOSITORY)" "$(VIRTUOSITY_DRUMS_BRANCH)" > "$(VIRTUOSITY_DRUMS_SOURCE_PROBE)"
	cat "$(VIRTUOSITY_DRUMS_SOURCE_PROBE)"

test-probe-virtuosity-drums-source: scripts/probe_virtuosity_drums_source.sh
	sh -n scripts/probe_virtuosity_drums_source.sh

download-virtuosity-drums: configure-instrument-sample-store scripts/download_virtuosity_drums.sh
	$(SHELL) scripts/download_virtuosity_drums.sh "$(VIRTUOSITY_DRUMS_SOURCE_DIR)" "$(VIRTUOSITY_DRUMS_REPOSITORY)" "$(VIRTUOSITY_DRUMS_COMMIT)"

test-download-virtuosity-drums-script: scripts/download_virtuosity_drums.sh
	sh -n scripts/download_virtuosity_drums.sh

prepare-virtuosity-drums-samples: download-virtuosity-drums scripts/prepare_virtuosity_drums_samples.py
	$(PYTHON) scripts/prepare_virtuosity_drums_samples.py --source "$(VIRTUOSITY_DRUMS_SOURCE_DIR)" --output "$(VIRTUOSITY_DRUMS_SAMPLE_DIR)" --limit-per-category "$(VIRTUOSITY_DRUMS_LIMIT_PER_CATEGORY)" --min-per-category "$(VIRTUOSITY_DRUMS_MIN_PER_CATEGORY)"

measure-virtuosity-drums: $(BUILD_DIR)/analyzer_drum_samples prepare-virtuosity-drums-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="tom,ride,rim" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=4000 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(VIRTUOSITY_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(VIRTUOSITY_DRUMS_MEASUREMENT)" 2>&1
	cat "$(VIRTUOSITY_DRUMS_MEASUREMENT)"
	+$(MAKE) update-detection-accuracy-report-cached

$(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS): $(VIRTUOSITY_DRUMS_MEASUREMENT) scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(VIRTUOSITY_DRUMS_MEASUREMENT)" > "$@"

analyze-virtuosity-drums-primary-attribute-rows: measure-virtuosity-drums
	+$(MAKE) "$(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"
	@printf '%s\n' "Virtuosity Drums primary attribute TSV: $(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

find-virtuosity-drum-primary-attribute-patterns: $(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS) scripts/find_drum_attribute_patterns.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(VIRTUOSITY_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

test-prepare-virtuosity-drums-samples: tests/test_prepare_virtuosity_drums_samples.py scripts/prepare_virtuosity_drums_samples.py
	$(PYTHON) tests/test_prepare_virtuosity_drums_samples.py

test-download-enst-drums-script: scripts/download_enst_drums.sh tests/test_download_enst_drums_script.py
	sh -n scripts/download_enst_drums.sh
	$(PYTHON) tests/test_download_enst_drums_script.py

download-fsd50k-rim-metadata: configure-instrument-sample-store scripts/download_fsd50k_rim_metadata.sh
	$(SHELL) scripts/download_fsd50k_rim_metadata.sh "$(FSD50K_RIM_SOURCE_DIR)" "$(PYTHON)"

inspect-fsd50k-rim-metadata: download-fsd50k-rim-metadata scripts/inspect_fsd50k_rim_metadata.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_fsd50k_rim_metadata.py "$(FSD50K_RIM_GROUND_TRUTH_ARCHIVE)" "$(FSD50K_RIM_METADATA_ARCHIVE)" --output "$(FSD50K_RIM_METADATA_AUDIT)"
	cat "$(FSD50K_RIM_METADATA_AUDIT)"

test-download-fsd50k-rim-metadata-script: scripts/download_fsd50k_rim_metadata.sh
	sh -n scripts/download_fsd50k_rim_metadata.sh

test-inspect-fsd50k-rim-metadata: tests/test_inspect_fsd50k_rim_metadata.py scripts/inspect_fsd50k_rim_metadata.py
	$(PYTHON) tests/test_inspect_fsd50k_rim_metadata.py

.PHONY: download-commons-rimshot-candidate inspect-commons-rimshot-candidate test-commons-rimshot-candidate
download-commons-rimshot-candidate: configure-instrument-sample-store scripts/download_commons_rimshot_candidate.sh
	$(SHELL) scripts/download_commons_rimshot_candidate.sh "$(COMMONS_RIMSHOT_AUDIO)" "$(COMMONS_RIMSHOT_URL)" "$(COMMONS_RIMSHOT_SHA1)"

inspect-commons-rimshot-candidate: download-commons-rimshot-candidate scripts/inspect_commons_rimshot_candidate.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_commons_rimshot_candidate.py "$(COMMONS_RIMSHOT_AUDIO)" --output "$(COMMONS_RIMSHOT_CANDIDATE_AUDIT)"
	cat "$(COMMONS_RIMSHOT_CANDIDATE_AUDIT)"

test-commons-rimshot-candidate: scripts/download_commons_rimshot_candidate.sh scripts/inspect_commons_rimshot_candidate.py tests/test_inspect_commons_rimshot_candidate.py
	sh -n scripts/download_commons_rimshot_candidate.sh
	$(PYTHON) tests/test_inspect_commons_rimshot_candidate.py

.PHONY: resolve-pixabay-rimshot-candidate resolve-pixabay-rimshot-f-candidate resolve-pixabay-rim-shot-candidate test-resolve-pixabay-rimshot-candidate
resolve-pixabay-rimshot-candidate: scripts/resolve_pixabay_rimshot_candidate.py | $(BUILD_DIR)
	$(PYTHON) scripts/resolve_pixabay_rimshot_candidate.py --output "$(PIXABAY_RIMSHOT_CANDIDATE_AUDIT)"
	cat "$(PIXABAY_RIMSHOT_CANDIDATE_AUDIT)"

resolve-pixabay-rimshot-f-candidate: scripts/resolve_pixabay_rimshot_candidate.py | $(BUILD_DIR)
	$(PYTHON) scripts/resolve_pixabay_rimshot_candidate.py --page "https://pixabay.com/sound-effects/rimshot-f-56918/" --require "RimShot-f" --require "gnuoctathorpe" --require "Free for use" --candidate-name "pixabay_rimshot_f_candidate" --duration-seconds "unverified" --origin-license "unverified"

resolve-pixabay-rim-shot-candidate: scripts/resolve_pixabay_rimshot_candidate.py | $(BUILD_DIR)
	$(PYTHON) scripts/resolve_pixabay_rimshot_candidate.py --output "$(PIXABAY_RIM_SHOT_CANDIDATE_AUDIT)" --page "https://pixabay.com/sound-effects/musical-rim-shot-90328/" --require "Rim Shot" --require "theundecided" --require "Free for use" --candidate-name "pixabay_rim_shot_candidate" --duration-seconds "4" --origin-license "Pixabay-Content-License"
	cat "$(PIXABAY_RIM_SHOT_CANDIDATE_AUDIT)"

.PHONY: discover-pixabay-rimshot-f-checksum
discover-pixabay-rimshot-f-checksum: configure-instrument-sample-store scripts/discover_pixabay_rimshot_checksum.sh
	$(SHELL) scripts/discover_pixabay_rimshot_checksum.sh "$(PIXABAY_RIMSHOT_F_MP3)" "$(PIXABAY_RIMSHOT_F_URL)"

.PHONY: discover-pixabay-rim-shot-checksum
discover-pixabay-rim-shot-checksum: configure-instrument-sample-store scripts/discover_pixabay_rimshot_checksum.sh
	$(SHELL) scripts/discover_pixabay_rimshot_checksum.sh "$(PIXABAY_RIM_SHOT_MP3)" "$(PIXABAY_RIM_SHOT_URL)"

test-resolve-pixabay-rimshot-candidate: scripts/resolve_pixabay_rimshot_candidate.py tests/test_resolve_pixabay_rimshot_candidate.py
	$(PYTHON) tests/test_resolve_pixabay_rimshot_candidate.py

.PHONY: download-pixabay-rimshot-candidate measure-pixabay-rimshot-candidate
download-pixabay-rimshot-candidate: configure-instrument-sample-store scripts/download_pixabay_rimshot_candidate.sh
	$(SHELL) scripts/download_pixabay_rimshot_candidate.sh "$(PIXABAY_RIMSHOT_MP3)" "$(PIXABAY_RIMSHOT_WAV)" "$(PIXABAY_RIMSHOT_URL)" "$(PIXABAY_RIMSHOT_SHA256)" "Pixabay/Sajmund-Freesound-Rimshot-sweet"

measure-pixabay-rimshot-candidate: $(BUILD_DIR)/analyzer_drum_samples download-pixabay-rimshot-candidate scripts/inspect_pixabay_rimshot_measurement.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) pixabay_rimshot_candidate env MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SAMPLES_PER_CATEGORY=1 MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(PIXABAY_RIMSHOT_SOURCE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(PIXABAY_RIMSHOT_MEASUREMENT)" 2>&1
	$(PYTHON) scripts/inspect_pixabay_rimshot_measurement.py "$(PIXABAY_RIMSHOT_MEASUREMENT)" --output "$(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)"
	cat "$(PIXABAY_RIMSHOT_MEASUREMENT)"
	cat "$(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)"

.PHONY: test-inspect-pixabay-rimshot-measurement
test-inspect-pixabay-rimshot-measurement: scripts/inspect_pixabay_rimshot_measurement.py tests/test_inspect_pixabay_rimshot_measurement.py
	$(PYTHON) tests/test_inspect_pixabay_rimshot_measurement.py

.PHONY: download-pixabay-rimshot-f-candidate measure-pixabay-rimshot-f-candidate
download-pixabay-rimshot-f-candidate: configure-instrument-sample-store scripts/download_pixabay_rimshot_candidate.sh
	$(SHELL) scripts/download_pixabay_rimshot_candidate.sh "$(PIXABAY_RIMSHOT_F_MP3)" "$(PIXABAY_RIMSHOT_F_WAV)" "$(PIXABAY_RIMSHOT_F_URL)" "$(PIXABAY_RIMSHOT_F_SHA256)" "Pixabay/gnuoctathorpe-Freesound-RimShot-f"

measure-pixabay-rimshot-f-candidate: $(BUILD_DIR)/analyzer_drum_samples download-pixabay-rimshot-f-candidate scripts/inspect_pixabay_rimshot_measurement.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) pixabay_rimshot_f_candidate env MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SAMPLES_PER_CATEGORY=1 MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(PIXABAY_RIMSHOT_F_SOURCE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(PIXABAY_RIMSHOT_F_MEASUREMENT)" 2>&1
	$(PYTHON) scripts/inspect_pixabay_rimshot_measurement.py "$(PIXABAY_RIMSHOT_F_MEASUREMENT)" --output "$(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)"
	cat "$(PIXABAY_RIMSHOT_F_MEASUREMENT)"
	cat "$(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)"

.PHONY: download-pixabay-rim-shot-candidate measure-pixabay-rim-shot-candidate
download-pixabay-rim-shot-candidate: configure-instrument-sample-store scripts/download_pixabay_rimshot_candidate.sh
	$(SHELL) scripts/download_pixabay_rimshot_candidate.sh "$(PIXABAY_RIM_SHOT_MP3)" "$(PIXABAY_RIM_SHOT_WAV)" "$(PIXABAY_RIM_SHOT_URL)" "$(PIXABAY_RIM_SHOT_SHA256)" "Pixabay/theundecided-Freesound-Rim-Shot"

measure-pixabay-rim-shot-candidate: $(BUILD_DIR)/analyzer_drum_samples download-pixabay-rim-shot-candidate scripts/inspect_pixabay_rimshot_measurement.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) pixabay_rim_shot_candidate env MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SAMPLES_PER_CATEGORY=1 MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(PIXABAY_RIM_SHOT_SOURCE_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(PIXABAY_RIM_SHOT_MEASUREMENT)" 2>&1
	$(PYTHON) scripts/inspect_pixabay_rimshot_measurement.py "$(PIXABAY_RIM_SHOT_MEASUREMENT)" --output "$(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)"
	cat "$(PIXABAY_RIM_SHOT_MEASUREMENT)"
	cat "$(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)"

download-29k-drums: scripts/download_29k_samples_drums.sh
	$(SHELL) scripts/download_29k_samples_drums.sh "$(SAMPLES29K_DRUMS_ARCHIVE)" "$(SAMPLES29K_DRUMS_ARCHIVE_URL)" "$(SAMPLES29K_DRUMS_ARCHIVE_MD5)" "$(PYTHON)"

inspect-29k-drums-download: scripts/inspect_29k_samples_drums_download.py
	$(PYTHON) scripts/inspect_29k_samples_drums_download.py "$(SAMPLES29K_DRUMS_ARCHIVE)" "$(SAMPLES29K_DRUMS_JOB_LOG)"

inspect-29k-drums-archive: download-29k-drums scripts/inspect_29k_samples_drums.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_29k_samples_drums.py "$(SAMPLES29K_DRUMS_ARCHIVE)" > "$(SAMPLES29K_DRUMS_INSPECTION)"
	cat "$(SAMPLES29K_DRUMS_INSPECTION)"

prepare-29k-drums-samples: inspect-29k-drums-archive scripts/prepare_29k_samples_drums.py
	$(PYTHON) scripts/prepare_29k_samples_drums.py --archive "$(SAMPLES29K_DRUMS_ARCHIVE)" --output "$(SAMPLES29K_DRUMS_SAMPLE_DIR)" --limit-per-category "$(SAMPLES29K_DRUMS_LIMIT_PER_CATEGORY)" --min-per-category "$(SAMPLES29K_DRUMS_MIN_PER_CATEGORY)"

measure-29k-drums: $(BUILD_DIR)/analyzer_drum_samples prepare-29k-drums-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="tom,ride" MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=4000 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(SAMPLES29K_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=100 $(BUILD_DIR)/analyzer_drum_samples > "$(SAMPLES29K_DRUMS_MEASUREMENT)" 2>&1
	cat "$(SAMPLES29K_DRUMS_MEASUREMENT)"
	+$(MAKE) update-detection-accuracy-report-cached

$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS): $(SAMPLES29K_DRUMS_MEASUREMENT) scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows --include-debug-rows "$(SAMPLES29K_DRUMS_MEASUREMENT)" > "$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

analyze-29k-drums-primary-attribute-rows: measure-29k-drums
	+$(MAKE) "$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"
	+$(MAKE) update-detection-accuracy-report-cached
	@printf '%s\n' "29k drum primary attribute TSV: $(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"

find-29k-drum-primary-attribute-patterns: $(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS) scripts/find_drum_attribute_patterns.py
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(SAMPLES29K_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS)

find-cached-protected-drum-primary-attribute-patterns: scripts/find_drum_attribute_patterns.py
	@set --; for path in $(DRUM_PROTECTED_PRIMARY_ATTRIBUTE_INPUTS); do if [ -f "$$path" ]; then set -- "$$@" "$$path"; fi; done; if [ "$$#" -eq 0 ]; then printf '%s\n' "cached protected drum primary pattern candidates: skipped; no attribute rows"; else $(PYTHON) scripts/find_drum_attribute_patterns.py "$$@" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") --jobs "$(DRUM_PATTERN_JOBS)" $(PATTERN_ARGS) > "$(CACHED_PROTECTED_DRUM_PRIMARY_PATTERN_REPORT)"; printf '%s\n' "cached protected drum primary patterns: $(CACHED_PROTECTED_DRUM_PRIMARY_PATTERN_REPORT)"; fi

test-download-29k-drums-script: scripts/download_29k_samples_drums.sh
	sh -n scripts/download_29k_samples_drums.sh

test-inspect-29k-drums-download: tests/test_inspect_29k_samples_drums_download.py scripts/inspect_29k_samples_drums_download.py
	$(PYTHON) tests/test_inspect_29k_samples_drums_download.py

test-prepare-29k-drums-samples: tests/test_prepare_29k_samples_drums.py scripts/prepare_29k_samples_drums.py
	$(PYTHON) tests/test_prepare_29k_samples_drums.py

test-measure-29k-drums-makefile: tests/test_measure_29k_drums_makefile.py Makefile
	$(PYTHON) tests/test_measure_29k_drums_makefile.py

test-inspect-29k-drums-archive: tests/test_inspect_29k_samples_drums.py scripts/inspect_29k_samples_drums.py
	$(PYTHON) tests/test_inspect_29k_samples_drums.py

download-babyslakh: scripts/download_babyslakh.sh
	$(SHELL) scripts/download_babyslakh.sh "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_ARCHIVE_URL)" "$(BABYSLAKH_ARCHIVE_MD5)" "$(BABYSLAKH_DOWNLOAD_CONNECTIONS)"

probe-babyslakh-download: scripts/probe_babyslakh_download.sh
	$(SHELL) scripts/probe_babyslakh_download.sh "$(BABYSLAKH_ARCHIVE_URL)"

test-download-babyslakh-script: scripts/download_babyslakh.sh
	sh -n scripts/download_babyslakh.sh

download-babyslakh-background: scripts/start_babyslakh_background_download.sh scripts/download_babyslakh_background_worker.sh
	$(SHELL) scripts/start_babyslakh_background_download.sh "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_ARCHIVE_URL)" "$(BABYSLAKH_ARCHIVE_MD5)" "$(CURDIR)/scripts/download_babyslakh_background_worker.sh" "$(BABYSLAKH_DOWNLOAD_CONNECTIONS)"

stop-babyslakh-background: scripts/stop_babyslakh_background_download.sh
	$(SHELL) scripts/stop_babyslakh_background_download.sh

reset-babyslakh-download-control: scripts/reset_babyslakh_download_control.sh
	$(SHELL) scripts/reset_babyslakh_download_control.sh "$(BABYSLAKH_ARCHIVE)"

finalize-babyslakh-download: scripts/finalize_babyslakh_partial.sh
	$(SHELL) scripts/finalize_babyslakh_partial.sh "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_ARCHIVE_MD5)"

discard-babyslakh-corrupt-partial: scripts/discard_babyslakh_corrupt_partial.sh
	$(SHELL) scripts/discard_babyslakh_corrupt_partial.sh "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_ARCHIVE_MD5)"

inspect-babyslakh-download: scripts/inspect_babyslakh_download.py
	$(PYTHON) scripts/inspect_babyslakh_download.py "$(BABYSLAKH_ARCHIVE)"

inspect-babyslakh-downloader: scripts/inspect_download_accelerator.py
	$(PYTHON) scripts/inspect_download_accelerator.py

test-download-babyslakh-background-scripts: scripts/start_babyslakh_background_download.sh scripts/stop_babyslakh_background_download.sh scripts/reset_babyslakh_download_control.sh scripts/finalize_babyslakh_partial.sh scripts/discard_babyslakh_corrupt_partial.sh scripts/download_babyslakh_background_worker.sh scripts/inspect_babyslakh_download.py
	sh -n scripts/start_babyslakh_background_download.sh
	sh -n scripts/stop_babyslakh_background_download.sh
	sh -n scripts/reset_babyslakh_download_control.sh
	sh -n scripts/finalize_babyslakh_partial.sh
	sh -n scripts/discard_babyslakh_corrupt_partial.sh
	sh -n scripts/download_babyslakh_background_worker.sh
	$(PYTHON) -m py_compile scripts/inspect_babyslakh_download.py

test-babyslakh-background-extraction-scripts: scripts/start_babyslakh_background_extraction.sh scripts/extract_babyslakh_background_worker.sh scripts/inspect_babyslakh_extraction.py
	sh -n scripts/start_babyslakh_background_extraction.sh
	sh -n scripts/extract_babyslakh_background_worker.sh
	$(PYTHON) -m py_compile scripts/inspect_babyslakh_extraction.py

test-inspect-babyslakh-archive: tests/test_inspect_babyslakh_archive.py scripts/inspect_babyslakh_archive.py
	$(PYTHON) tests/test_inspect_babyslakh_archive.py

test-extract-babyslakh-archive: tests/test_extract_babyslakh_archive.py scripts/extract_babyslakh_archive.py
	$(PYTHON) tests/test_extract_babyslakh_archive.py

test-prepare-babyslakh-drums: tests/test_prepare_babyslakh_drums.py scripts/prepare_babyslakh_drums.py tests/inspect_slakh_dataset.py
	$(PYTHON) tests/test_prepare_babyslakh_drums.py

inspect-babyslakh-archive: download-babyslakh scripts/inspect_babyslakh_archive.py
	$(PYTHON) scripts/inspect_babyslakh_archive.py "$(BABYSLAKH_ARCHIVE)"

inspect-babyslakh-archive-existing: scripts/inspect_babyslakh_archive.py
	$(PYTHON) scripts/inspect_babyslakh_archive.py "$(BABYSLAKH_ARCHIVE)"

extract-babyslakh: inspect-babyslakh-archive scripts/extract_babyslakh_archive.py
	$(PYTHON) scripts/extract_babyslakh_archive.py "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_EXTRACTED_DIR)"

extract-babyslakh-background: inspect-babyslakh-archive-existing scripts/start_babyslakh_background_extraction.sh scripts/extract_babyslakh_background_worker.sh scripts/extract_babyslakh_archive.py
	$(SHELL) scripts/start_babyslakh_background_extraction.sh "$(BABYSLAKH_ARCHIVE)" "$(BABYSLAKH_EXTRACTED_DIR)" "$(PYTHON)" "$(CURDIR)/scripts/extract_babyslakh_archive.py" "$(CURDIR)/scripts/extract_babyslakh_background_worker.sh"

inspect-babyslakh-extraction: scripts/inspect_babyslakh_extraction.py
	$(PYTHON) scripts/inspect_babyslakh_extraction.py "$(BABYSLAKH_EXTRACTED_DIR)"

inspect-babyslakh: extract-babyslakh tests/inspect_slakh_dataset.py
	MUSIC_ANALYZER_SLAKH_ROOT="$(BABYSLAKH_EXTRACTED_DIR)" MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS="$(BABYSLAKH_REQUIRED_TRACKS)" $(PYTHON) tests/inspect_slakh_dataset.py

prepare-babyslakh-drums: inspect-babyslakh-archive-existing scripts/prepare_babyslakh_drums.py tests/inspect_slakh_dataset.py
	$(PYTHON) scripts/prepare_babyslakh_drums.py --root "$(BABYSLAKH_EXTRACTED_DIR)" --output "$(BABYSLAKH_DRUMS_SAMPLE_DIR)" --min-recordings "$(BABYSLAKH_DRUMS_MIN_RECORDINGS)"

measure-babyslakh-drums: $(BUILD_DIR)/analyzer_egmd prepare-babyslakh-drums | $(BUILD_DIR)
	env MUSIC_ANALYZER_EGMD_ROOT="$(BABYSLAKH_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_SOURCE_NAME="BabySlakh drums" MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(BABYSLAKH_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 $(BUILD_DIR)/analyzer_egmd > "$(BABYSLAKH_DRUMS_LOG)" 2>&1
	cat "$(BABYSLAKH_DRUMS_LOG)"

.PHONY: test-audit-babyslakh-drum-calibration audit-babyslakh-drum-calibration
test-audit-babyslakh-drum-calibration: tests/test_audit_babyslakh_drum_calibration.py scripts/audit_babyslakh_drum_calibration.py
	$(PYTHON) tests/test_audit_babyslakh_drum_calibration.py

audit-babyslakh-drum-calibration: measure-babyslakh-drums scripts/audit_babyslakh_drum_calibration.py | $(BUILD_DIR)
	$(PYTHON) scripts/audit_babyslakh_drum_calibration.py --mdb "$(MDB_DRUMS_WINDOW_LOG).summary" --star "$(STAR_DRUMS_MISS_LOG).windows.summary" --babyslakh "$(BABYSLAKH_DRUMS_LOG)" --output "$(BABYSLAKH_DRUM_CALIBRATION_AUDIT)"

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

.PHONY: analyze-mdb-drum-windows inspect-mdb-rim-coverage test-inspect-mdb-rim-coverage
analyze-mdb-drum-windows: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples
	env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOWS=1 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOW_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(MDB_DRUMS_WINDOW_LOG).summary" 2> "$(MDB_DRUMS_WINDOW_LOG)"
	@printf '%s\n' "MDB drum all-window log: $(MDB_DRUMS_WINDOW_LOG)"

inspect-mdb-rim-coverage: analyze-mdb-drum-windows scripts/inspect_mdb_rim_coverage.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_mdb_rim_coverage.py "$(MDB_DRUMS_WINDOW_LOG)" --output "$(MDB_RIM_COVERAGE_AUDIT)"
	cat "$(MDB_RIM_COVERAGE_AUDIT)"

test-inspect-mdb-rim-coverage: tests/test_inspect_mdb_rim_coverage.py scripts/inspect_mdb_rim_coverage.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) tests/test_inspect_mdb_rim_coverage.py

.PHONY: evaluate-mdb-drum-windows
evaluate-mdb-drum-windows: analyze-mdb-drum-windows scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(MDB_DRUMS_WINDOW_LOG)" $(DRUM_RECOVERY_ARGS)

analyze-mdb-drum-attributes: analyze-mdb-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(MDB_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-star-drums-samples: $(STAR_DRUMS_ARCHIVE)

$(STAR_DRUMS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(STAR_DRUMS_SOURCE_DIR)"
	@if [ -s "$(STAR_DRUMS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(STAR_DRUMS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(STAR_DRUMS_ARCHIVE)" "$(STAR_DRUMS_ARCHIVE).corrupt"; fi
	@if [ ! -s "$(STAR_DRUMS_ARCHIVE)" ]; then curl -fL -C - -o "$(STAR_DRUMS_ARCHIVE)" "$(STAR_DRUMS_URL)"; fi
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

.PHONY: analyze-star-drum-windows evaluate-star-drum-windows
analyze-star-drum-windows: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples
	env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(STAR_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOWS=1 MUSIC_ANALYZER_EGMD_VERBOSE_WINDOW_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(STAR_DRUMS_MISS_LOG).windows.summary" 2> "$(STAR_DRUMS_MISS_LOG).windows"
	@printf '%s\n' "STAR drum all-window log: $(STAR_DRUMS_MISS_LOG).windows"

evaluate-star-drum-windows: analyze-star-drum-windows scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) scripts/evaluate_egmd_drum_recovery.py "$(STAR_DRUMS_MISS_LOG).windows" $(DRUM_RECOVERY_ARGS)

.PHONY: search-drum-false-positive-caps
search-drum-false-positive-caps: analyze-mdb-drum-windows analyze-star-drum-windows scripts/search_egmd_false_positive_caps.py
	$(PYTHON) scripts/search_egmd_false_positive_caps.py --input "MDB=$(MDB_DRUMS_WINDOW_LOG)" --input "STAR=$(STAR_DRUMS_MISS_LOG).windows"

.PHONY: audit-drum-false-positive-caps test-audit-drum-false-positive-caps
audit-drum-false-positive-caps: analyze-mdb-drum-windows analyze-star-drum-windows scripts/audit_drum_false_positive_caps.py scripts/search_egmd_false_positive_caps.py $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_drum_false_positive_caps.py --real-input "MDB=$(MDB_DRUMS_WINDOW_LOG)" --real-input "STAR=$(STAR_DRUMS_MISS_LOG).windows" --protected "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" --protected "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" --protected "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --output "$(DRUM_FALSE_POSITIVE_CAP_AUDIT)"

test-audit-drum-false-positive-caps: tests/test_audit_drum_false_positive_caps.py scripts/audit_drum_false_positive_caps.py
	$(PYTHON) tests/test_audit_drum_false_positive_caps.py

.PHONY: audit-mdb-full-mix-false-positive-caps audit-mdb-full-mix-competing-active-contexts test-audit-drum-competing-active-contexts audit-mdb-source-scoped-contexts test-audit-drum-source-scoped-contexts
audit-mdb-full-mix-false-positive-caps: analyze-mdb-drum-windows scripts/audit_drum_false_positive_caps.py scripts/search_egmd_false_positive_caps.py $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_drum_false_positive_caps.py --real-input "MDB=$(MDB_DRUMS_WINDOW_LOG)" --protected "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" --protected "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" --protected "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --output "$(MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT)"

audit-mdb-full-mix-competing-active-contexts: analyze-mdb-drum-windows analyze-star-drum-windows scripts/audit_drum_competing_active_contexts.py scripts/evaluate_egmd_drum_recovery.py $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_drum_competing_active_contexts.py --real-input "$(MDB_DRUMS_WINDOW_LOG)" --real-input "$(STAR_DRUMS_MISS_LOG).windows" --protected "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" --protected "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" --protected "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --output "$(MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT)" --runtime-replayed-context "$(MDB_COMPETING_ACTIVE_CONTEXT_RUNTIME_REPLAYED)" $(if $(MDB_COMPETING_ACTIVE_CONTEXT_RUNTIME_GAINED),--runtime-gain-context "$(MDB_COMPETING_ACTIVE_CONTEXT_RUNTIME_GAINED)")

test-audit-drum-competing-active-contexts: tests/test_audit_drum_competing_active_contexts.py scripts/audit_drum_competing_active_contexts.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) tests/test_audit_drum_competing_active_contexts.py

audit-mdb-source-scoped-contexts: analyze-mdb-drum-windows analyze-star-drum-windows scripts/audit_drum_source_scoped_contexts.py scripts/evaluate_egmd_drum_recovery.py | $(BUILD_DIR)
	$(PYTHON) scripts/audit_drum_source_scoped_contexts.py --real-input "$(MDB_DRUMS_WINDOW_LOG)" --real-input "$(STAR_DRUMS_MISS_LOG).windows" --output "$(MDB_SOURCE_SCOPED_CONTEXT_AUDIT)" $(MDB_SOURCE_SCOPED_CONTEXT_ARGS)

test-audit-drum-source-scoped-contexts: tests/test_audit_drum_source_scoped_contexts.py scripts/audit_drum_source_scoped_contexts.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) tests/test_audit_drum_source_scoped_contexts.py

.PHONY: audit-drum-false-positive-contexts test-audit-drum-false-positive-contexts
audit-drum-false-positive-contexts: analyze-mdb-drum-windows analyze-star-drum-windows scripts/audit_drum_false_positive_contexts.py scripts/search_egmd_false_positive_caps.py $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) $(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_drum_false_positive_contexts.py --real-input "MDB=$(MDB_DRUMS_WINDOW_LOG)" --real-input "STAR=$(STAR_DRUMS_MISS_LOG).windows" --protected "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" --protected "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" --protected "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" --output "$(DRUM_FALSE_POSITIVE_CONTEXT_AUDIT)"

test-audit-drum-false-positive-contexts: tests/test_audit_drum_false_positive_contexts.py scripts/audit_drum_false_positive_contexts.py
	$(PYTHON) tests/test_audit_drum_false_positive_contexts.py

.PHONY: audit-drum-recovery-candidates test-audit-drum-recovery-candidates
audit-drum-recovery-candidates: analyze-mdb-drum-windows analyze-star-drum-windows scripts/find_egmd_drum_recovery_candidates.py | $(BUILD_DIR)
	$(PYTHON) scripts/find_egmd_drum_recovery_candidates.py --real-input "MDB=$(MDB_DRUMS_WINDOW_LOG)" --real-input "STAR=$(STAR_DRUMS_MISS_LOG).windows" --output "$(DRUM_RECOVERY_CANDIDATE_AUDIT)"

test-audit-drum-recovery-candidates: tests/test_find_egmd_drum_recovery_candidates.py scripts/find_egmd_drum_recovery_candidates.py
	$(PYTHON) tests/test_find_egmd_drum_recovery_candidates.py

analyze-star-drum-attributes: analyze-star-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(STAR_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-medley-solos-samples: $(MEDLEY_SOLOS_METADATA) $(MEDLEY_SOLOS_ARCHIVE)

.PHONY: download-real-a2s-sax-samples
download-real-a2s-sax-samples: $(REAL_A2S_SAX_ARCHIVE)

.PHONY: inspect-real-a2s-sax-archive
inspect-real-a2s-sax-archive: download-real-a2s-sax-samples
	$(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)"

.PHONY: extract-real-a2s-sax-metadata
extract-real-a2s-sax-metadata: download-real-a2s-sax-samples
	mkdir -p "$(REAL_A2S_SAX_METADATA_DIR)"
	$(TAR) -xzf "$(REAL_A2S_SAX_ARCHIVE)" -C "$(REAL_A2S_SAX_METADATA_DIR)" --wildcards '*/Tenor_Sax_Index.csv' '*/Dataset_Index.xlsx' '*/krn/tenor/*'

.PHONY: print-real-a2s-tenor-index inspect-real-a2s-tenor-index-cached inspect-real-a2s-sax-score-members list-detection-make-targets inspect-detection-make-target inspect-detector-source

list-detection-make-targets: scripts/list_detection_make_targets.py
	$(PYTHON) scripts/list_detection_make_targets.py

inspect-basic-pitch-display-fusion: scripts/inspect_basic_pitch_display_fusion.py
	$(PYTHON) scripts/inspect_basic_pitch_display_fusion.py

inspect-basic-pitch-replay-contract: scripts/inspect_basic_pitch_replay_contract.py
	$(PYTHON) scripts/inspect_basic_pitch_replay_contract.py

report-basic-pitch-owner-evidence: scripts/report_basic_pitch_owner_evidence.py
	$(PYTHON) scripts/report_basic_pitch_owner_evidence.py

inspect-full-mix-candidate-builder: scripts/inspect_full_mix_candidate_builder.py
	$(PYTHON) scripts/inspect_full_mix_candidate_builder.py

inspect-gaps-guitar-miss-evaluator: scripts/inspect_gaps_guitar_miss_evaluator.py
	$(PYTHON) scripts/inspect_gaps_guitar_miss_evaluator.py

inspect-gaps-guitar-attributes-schema: scripts/inspect_gaps_guitar_attributes_schema.py
	$(PYTHON) scripts/inspect_gaps_guitar_attributes_schema.py

sweep-gaps-guitar-pitch-sources: scripts/sweep_gaps_guitar_pitch_sources.py
	$(PYTHON) scripts/sweep_gaps_guitar_pitch_sources.py

measure-gaps-guitar-pipeline-loss: scripts/measure_gaps_guitar_pipeline_loss.py
	$(PYTHON) scripts/measure_gaps_guitar_pipeline_loss.py

measure-gaps-guitar-triad-restore: scripts/measure_gaps_guitar_triad_restore.py
	$(PYTHON) scripts/measure_gaps_guitar_triad_restore.py

locate-gaps-guitar-replay: scripts/locate_gaps_guitar_replay.py
	$(PYTHON) scripts/locate_gaps_guitar_replay.py

report-drum-primary-analysis: scripts/report_drum_primary_analysis.py
	$(PYTHON) scripts/report_drum_primary_analysis.py

wait-drum-primary-analysis: scripts/wait_drum_primary_analysis.py
	$(PYTHON) scripts/wait_drum_primary_analysis.py

report-drum-tom-snare-primary: scripts/analyze_tom_snare_primary.py
	$(PYTHON) scripts/analyze_tom_snare_primary.py

inspect-tom-snare-arbitration: scripts/inspect_tom_snare_arbitration.py
	$(PYTHON) scripts/inspect_tom_snare_arbitration.py

mine-drum-tom-snare-selectors: scripts/mine_drum_tom_snare_selectors.py
	$(PYTHON) scripts/mine_drum_tom_snare_selectors.py

inspect-urmp-pre-envelope-path: scripts/inspect_urmp_pre_envelope_path.py
	$(PYTHON) scripts/inspect_urmp_pre_envelope_path.py

inspect-chord-result-contract: scripts/inspect_chord_result_contract.py
	$(PYTHON) scripts/inspect_chord_result_contract.py


report-real-urmp-process: scripts/report_real_urmp_process.py
	$(PYTHON) scripts/report_real_urmp_process.py

test-real-urmp-logged: scripts/run_real_urmp_logged.py
	$(PYTHON) scripts/run_real_urmp_logged.py

summarize-real-urmp-log: scripts/summarize_real_urmp_log.py
	$(PYTHON) scripts/summarize_real_urmp_log.py

summarize-detection-accuracy-report: scripts/summarize_detection_accuracy_report.py
	$(PYTHON) scripts/summarize_detection_accuracy_report.py

inspect-shared-ownership-ranking: scripts/inspect_shared_ownership_ranking.py
	$(PYTHON) scripts/inspect_shared_ownership_ranking.py

inspect-detector-samples-parallel-target: scripts/inspect_detector_samples_parallel_target.py
	$(PYTHON) scripts/inspect_detector_samples_parallel_target.py

plan-commit-fret-zealot-auto-stabilization: scripts/commit_verified_fret_zealot_auto_stabilization.py
	$(PYTHON) scripts/commit_verified_fret_zealot_auto_stabilization.py

commit-fret-zealot-auto-stabilization: scripts/commit_verified_fret_zealot_auto_stabilization.py
	$(PYTHON) scripts/commit_verified_fret_zealot_auto_stabilization.py apply

.PHONY: inspect-fret-zealot-scale-update
inspect-fret-zealot-scale-update: scripts/inspect_fret_zealot_scale_update.py
	$(PYTHON) scripts/inspect_fret_zealot_scale_update.py

.PHONY: test-fret-zealot-auto-root-stability
test-fret-zealot-auto-root-stability: tests/check_fret_zealot_auto_root_stability.py
	$(PYTHON) tests/check_fret_zealot_auto_root_stability.py

inspect-detection-make-target: scripts/list_detection_make_targets.py
	$(PYTHON) scripts/list_detection_make_targets.py "$(MAKE_TARGET_NAME)"

inspect-detector-source: scripts/inspect_detector_source.py
	$(PYTHON) scripts/inspect_detector_source.py "$(DETECTOR_SOURCE_TERM)" --context "$(or $(DETECTOR_SOURCE_CONTEXT),3)"

.PHONY: inspect-project-source
inspect-project-source: scripts/inspect_project_source.py
	$(PYTHON) scripts/inspect_project_source.py "$(PROJECT_SOURCE_TERM)" --context "$(or $(PROJECT_SOURCE_CONTEXT),3)"

print-real-a2s-tenor-index: download-real-a2s-sax-samples
	$(TAR) -xOzf "$(REAL_A2S_SAX_ARCHIVE)" real_a2s_sax_dataset/Tenor_Sax_Index.csv

inspect-real-a2s-tenor-index-cached: scripts/inspect_real_a2s_tenor_index.py
	$(PYTHON) scripts/inspect_real_a2s_tenor_index.py --index "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/Tenor_Sax_Index.csv"

inspect-real-a2s-sax-score-members: download-real-a2s-sax-samples
	$(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" --wildcards '*.krn'

.PHONY: extract-real-a2s-sax-scale-probes
extract-real-a2s-sax-scale-probes: download-real-a2s-sax-samples
	mkdir -p "$(REAL_A2S_SAX_PROBE_DIR)"
	$(TAR) -xzf "$(REAL_A2S_SAX_ARCHIVE)" -C "$(REAL_A2S_SAX_PROBE_DIR)" $(foreach recording,$(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES),real_a2s_sax_dataset/real/tenor/$(recording).wav)

.PHONY: extract-real-a2s-sax-exercise-probes
extract-real-a2s-sax-exercise-probes: download-real-a2s-sax-samples
	mkdir -p "$(REAL_A2S_SAX_PROBE_DIR)"
	$(TAR) -xzf "$(REAL_A2S_SAX_ARCHIVE)" -C "$(REAL_A2S_SAX_PROBE_DIR)" real_a2s_sax_dataset/real/tenor/Ex1.wav real_a2s_sax_dataset/real/tenor/Ex2.wav real_a2s_sax_dataset/real/tenor/Ex3.wav

.PHONY: inspect-real-a2s-sax-scale-probes
inspect-real-a2s-sax-scale-probes: extract-real-a2s-sax-scale-probes scripts/inspect_real_a2s_sax_scale.py
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn"


.PHONY: inspect-real-a2s-sax-scale-probes-cached
inspect-real-a2s-sax-scale-probes-cached: scripts/inspect_real_a2s_sax_scale.py
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" || { printf '%s\n' "missing scale probe; run make extract-real-a2s-sax-scale-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn" || { printf '%s\n' "missing tenor score; run make extract-real-a2s-sax-metadata first"; exit 2; }
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn"

.PHONY: inspect-real-a2s-sax-exercise-probes-cached
inspect-real-a2s-sax-exercise-probes-cached: scripts/inspect_real_a2s_sax_scale.py
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex1.krn"
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex2.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex2.krn"
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex3.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex3.krn"

.PHONY: test-inspect-real-a2s-sax-scale
test-inspect-real-a2s-sax-scale: tests/test_inspect_real_a2s_sax_scale.py scripts/inspect_real_a2s_sax_scale.py
	$(PYTHON) tests/test_inspect_real_a2s_sax_scale.py

.PHONY: prepare-real-a2s-tenor-scale-probes prepare-real-a2s-tenor-scale-probes-cached test-prepare-real-a2s-tenor-scale-probes measure-real-a2s-tenor-scale-probes analyze-real-a2s-tenor-scale-probes find-real-a2s-tenor-scale-routing-patterns
prepare-real-a2s-tenor-scale-probes: extract-real-a2s-sax-scale-probes extract-real-a2s-sax-metadata scripts/prepare_real_a2s_sax_scale_fixture.py
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=real_a2s_tenor_scale_fixture
	$(PYTHON) scripts/prepare_real_a2s_sax_scale_fixture.py $(REAL_A2S_SAX_TENOR_SCALE_INPUTS) $(REAL_A2S_SAX_TENOR_EXERCISE_INPUTS) --output "$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --midi-offset "$(REAL_A2S_SAX_SCALE_MIDI_OFFSET)"

prepare-real-a2s-tenor-scale-probes-cached: scripts/prepare_real_a2s_sax_scale_fixture.py
	@for recording in $(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES); do test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/$$recording.wav" || { printf '%s\n' "missing scale probe; run make extract-real-a2s-sax-scale-probes first"; exit 2; }; done
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex2.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex3.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@for recording in $(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES); do test -s "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/$$recording.krn" || { printf '%s\n' "missing tenor score; run make extract-real-a2s-sax-metadata first"; exit 2; }; done
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=real_a2s_tenor_scale_fixture
	$(PYTHON) scripts/prepare_real_a2s_sax_scale_fixture.py $(REAL_A2S_SAX_TENOR_SCALE_INPUTS) $(REAL_A2S_SAX_TENOR_EXERCISE_INPUTS) --output "$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --midi-offset "$(REAL_A2S_SAX_SCALE_MIDI_OFFSET)"

test-prepare-real-a2s-tenor-scale-probes: tests/test_prepare_real_a2s_sax_scale_fixture.py scripts/prepare_real_a2s_sax_scale_fixture.py
	$(PYTHON) tests/test_prepare_real_a2s_sax_scale_fixture.py

measure-real-a2s-tenor-scale-probes: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-a2s-tenor-scale-probes-cached | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(REAL_A2S_SAX_SCALE_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples

analyze-real-a2s-tenor-scale-probes: $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) scripts/analyze_exact_midi_misses.py
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

find-real-a2s-tenor-scale-routing-patterns: $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" --bucket-status first_row_confusion --top-buckets 6 --min-positive-samples 3 --max-negative-samples 0 --include-row-context --profile-fields 10 --show-examples 2

$(REAL_A2S_SAX_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(REAL_A2S_SAX_SOURCE_DIR)"
	if [ -s "$(REAL_A2S_SAX_ARCHIVE)" ] && ! $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(REAL_A2S_SAX_ARCHIVE)" "$(REAL_A2S_SAX_ARCHIVE).part"; fi
	if [ ! -s "$(REAL_A2S_SAX_ARCHIVE)" ] && [ -s "$(REAL_A2S_SAX_ARCHIVE).part" ] && $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE).part" >/dev/null 2>&1; then mv "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE)"; fi
	if [ ! -s "$(REAL_A2S_SAX_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 8 -s 8 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(REAL_A2S_SAX_SOURCE_DIR)" --out "real_a2s_sax_dataset.tgz.part" "$(REAL_A2S_SAX_ARCHIVE_URL)"; else curl -fL -C - -o "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE_URL)"; fi; fi
	if [ -s "$(REAL_A2S_SAX_ARCHIVE).part" ]; then $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE).part" >/dev/null; mv "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE)"; fi
	$(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" >/dev/null

$(MEDLEY_SOLOS_METADATA): | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	curl -fL -C - -o "$(MEDLEY_SOLOS_METADATA)" "$(MEDLEY_SOLOS_METADATA_URL)"

$(MEDLEY_SOLOS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && ! $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(MEDLEY_SOLOS_ARCHIVE)" "$(MEDLEY_SOLOS_ARCHIVE).part"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ] && $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 8 -s 8 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(MEDLEY_SOLOS_SOURCE_DIR)" --out "Medley-solos-DB.tar.gz.part" "$(MEDLEY_SOLOS_URL)"; else curl -fL -C - -o "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_URL)"; fi; fi
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ]; then $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null; mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	$(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null

prepare-medley-solos-samples: scripts/prepare_medley_solos_samples.py download-medley-solos-samples | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=medley_solos_samples
	MEDLEY_SOLOS_METADATA="$(MEDLEY_SOLOS_METADATA)" MEDLEY_SOLOS_ARCHIVE="$(MEDLEY_SOLOS_ARCHIVE)" MEDLEY_SOLOS_SAMPLE_DIR="$(MEDLEY_SOLOS_SAMPLE_DIR)" MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT="$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" MEDLEY_SOLOS_MIN_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MEDLEY_SOLOS_MIN_COUNTS="$(MEDLEY_SOLOS_MIN_COUNTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_medley_solos_samples.py --metadata "$(MEDLEY_SOLOS_METADATA)" --archive "$(MEDLEY_SOLOS_ARCHIVE)" --output "$(MEDLEY_SOLOS_SAMPLE_DIR)" --limit-per-instrument "$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-counts "$(MEDLEY_SOLOS_MIN_COUNTS)" --ffmpeg "$(FFMPEG)"

test-medley-solos-samples: test-medley-solos-samples-parallel

$(MEDLEY_SOLOS_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_instrument_family_samples > "$@.out"

# Recompute metrics from the prepared corpus without forcing its download/prepare
# prerequisite.  This is safe for routine detector iterations and keeps the
# persisted report synchronized with the analyzer currently under test.
refresh-medley-solos-attributes-cached: $(BUILD_DIR)/analyzer_instrument_family_samples scripts/run_with_lock.sh | $(BUILD_DIR)
	@test -s "$(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv; run make prepare-medley-solos-samples first"; exit 2; }
	@rm -f "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	+$(SHELL) scripts/run_with_lock.sh "$(MEDLEY_SOLOS_LOCK_DIR)" -- env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_ATTRIBUTE_TSV="$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_instrument_family_samples

analyze-medley-solos-attributes: $(MEDLEY_SOLOS_ATTRIBUTE_TSV) scripts/summarize_instrument_family_attributes.py
	$(PYTHON) scripts/summarize_instrument_family_attributes.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	@printf '%s\n' "Medley Solos attribute TSV: $(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

analyze-medley-solos-attributes-cached: scripts/summarize_instrument_family_attributes.py
	@test -s "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MEDLEY_SOLOS_ATTRIBUTE_TSV); run make refresh-medley-solos-attributes-cached first"; exit 2; }
	$(PYTHON) scripts/summarize_instrument_family_attributes.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	@printf '%s\n' "Medley Solos cached attribute TSV: $(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-misses: $(MEDLEY_SOLOS_ATTRIBUTE_TSV) scripts/inspect_instrument_family_misses.py
	$(PYTHON) scripts/inspect_instrument_family_misses.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-misses-cached: scripts/inspect_instrument_family_misses.py
	@test -s "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MEDLEY_SOLOS_ATTRIBUTE_TSV); run make inspect-medley-solos-misses first"; exit 2; }
	$(PYTHON) scripts/inspect_instrument_family_misses.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-debug-cached: $(BUILD_DIR)/analyzer_instrument_family_samples
	@test -n "$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set MEDLEY_SOLOS_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv; run make prepare-medley-solos-samples first"; exit 2; }
	env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ID="$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_DEBUG_SAMPLE_ID="$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" $(BUILD_DIR)/analyzer_instrument_family_samples

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
	if [ ! -s "$(MAPS_PIANO_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(MAPS_PIANO_DOWNLOAD_CONNECTIONS)" -s "$(MAPS_PIANO_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(MAPS_PIANO_SOURCE_DIR)" --out "ENSTDkCl.zip.part" "$(MAPS_PIANO_URL)"; else curl -fL -C - -o "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_URL)"; fi; fi
	if [ -s "$(MAPS_PIANO_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE).part" >/dev/null; mv "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null

prepare-maps-piano-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MAPS_PIANO_KINDS="$(MAPS_PIANO_KINDS)" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_SAMPLE_DIR)" --limit "$(MAPS_PIANO_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --kinds "$(MAPS_PIANO_KINDS)"

# MAESTRO is a second independently recorded Disklavier corpus.  Its archive
# and the selected WAV/MIDI fixture remain under InstrumentSamples; build only
# retains the stable symlink used by analyzer targets.
download-maestro-real-samples: scripts/validate_maestro_subset_archive.py scripts/prepare_maps_piano_samples.py | $(BUILD_DIR)
	mkdir -p "$(MAESTRO_REAL_SOURCE_DIR)"
	test -s "$(MAESTRO_REAL_ARCHIVE)" || curl -fL -C - -o "$(MAESTRO_REAL_ARCHIVE).part" "$(MAESTRO_REAL_URL)"
	@test ! -s "$(MAESTRO_REAL_ARCHIVE).part" || mv "$(MAESTRO_REAL_ARCHIVE).part" "$(MAESTRO_REAL_ARCHIVE)"
	$(PYTHON) scripts/validate_maestro_subset_archive.py --archive "$(MAESTRO_REAL_ARCHIVE)" --kinds OTHER --min-pairs "$(MAESTRO_REAL_MIN_RECORDINGS)"

.PHONY: download-kraisler validate-kraisler-archive extract-kraisler prepare-kraisler measure-kraisler summarize-kraisler test-validate-kraisler-archive test-extract-kraisler test-prepare-kraisler test-summarize-kraisler
download-kraisler: configure-instrument-sample-store $(KRAISLER_ARCHIVE) validate-kraisler-archive

$(KRAISLER_ARCHIVE): scripts/validate_kraisler_archive.py
	mkdir -p "$(KRAISLER_SOURCE_DIR)"
	if test -s "$@"; then $(PYTHON) scripts/validate_kraisler_archive.py --archive "$@" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"; elif command -v aria2c >/dev/null 2>&1; then aria2c --continue=true --allow-overwrite=true --auto-file-renaming=false --file-allocation=none --max-tries=5 --retry-wait=5 --max-connection-per-server=8 --split=8 --min-split-size=1M --dir "$(KRAISLER_SOURCE_DIR)" --out "KRAISLER.zip.part" "$(KRAISLER_ARCHIVE_URL)" && mv "$@.part" "$@"; else curl -fL -C - -o "$@.part" "$(KRAISLER_ARCHIVE_URL)" && mv "$@.part" "$@"; fi

validate-kraisler-archive: $(KRAISLER_ARCHIVE) scripts/validate_kraisler_archive.py
	$(PYTHON) scripts/validate_kraisler_archive.py --archive "$(KRAISLER_ARCHIVE)" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

extract-kraisler: validate-kraisler-archive scripts/extract_kraisler.py
	$(PYTHON) scripts/extract_kraisler.py --archive "$(KRAISLER_ARCHIVE)" --output "$(KRAISLER_EXTRACT_DIR)" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

prepare-kraisler: extract-kraisler scripts/prepare_kraisler_manifest.py
	$(PYTHON) scripts/prepare_kraisler_manifest.py --root "$(KRAISLER_EXTRACT_DIR)" --output "$(KRAISLER_PREPARED_DIR)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

measure-kraisler: $(BUILD_DIR)/analyzer_musicnet prepare-kraisler tests/prepare_prepared_multitrack_musicnet_fixture.py scripts/summarize_kraisler_measurement.py | $(BUILD_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(KRAISLER_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_SOURCES=2 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py "$(KRAISLER_MUSICNET_DIR)"
	MUSIC_ANALYZER_MUSICNET_ROOT="$(KRAISLER_MUSICNET_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$(KRAISLER_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) summarize-kraisler

summarize-kraisler: $(KRAISLER_ATTRIBUTE_OUTPUT) prepare-kraisler scripts/summarize_kraisler_measurement.py
	$(PYTHON) scripts/summarize_kraisler_measurement.py --attributes "$(KRAISLER_ATTRIBUTE_OUTPUT)" --manifest "$(KRAISLER_PREPARED_DIR)/manifest.json" --output "$(KRAISLER_MEASUREMENT_OUTPUT)"

.PHONY: download-irmas validate-irmas extract-irmas inspect-irmas prepare-irmas measure-irmas test-irmas-scripts
download-irmas: $(IRMAS_ARCHIVES)

validate-irmas: $(IRMAS_ARCHIVES)

define IRMAS_ARCHIVE_RULE
$(1): FORCE scripts/validate_irmas_archive.py | $(BUILD_DIR)
	mkdir -p "$(IRMAS_SOURCE_DIR)"
	if [ -s "$$@" ] && ! $(PYTHON) scripts/validate_irmas_archive.py --archive "$$@" --md5 "$(2)" >/dev/null 2>&1; then mv -f "$$@" "$$@.corrupt"; fi
	if [ ! -s "$$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 4 -s 4 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(IRMAS_SOURCE_DIR)" --out "$(notdir $(1)).part" "$(3)"; else curl -fL -C - -o "$$@.part" "$(3)"; fi; fi
	if [ -s "$$@.part" ]; then $(PYTHON) scripts/validate_irmas_archive.py --archive "$$@.part" --md5 "$(2)"; mv -f "$$@.part" "$$@"; fi
	$(PYTHON) scripts/validate_irmas_archive.py --archive "$$@" --md5 "$(2)"
endef
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART1_ARCHIVE),$(IRMAS_TEST_PART1_MD5),$(IRMAS_TEST_PART1_URL)))
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART2_ARCHIVE),$(IRMAS_TEST_PART2_MD5),$(IRMAS_TEST_PART2_URL)))
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART3_ARCHIVE),$(IRMAS_TEST_PART3_MD5),$(IRMAS_TEST_PART3_URL)))

extract-irmas: download-irmas scripts/extract_irmas.py
	$(PYTHON) scripts/extract_irmas.py $(foreach archive,$(IRMAS_ARCHIVES),--archive "$(archive)") --output "$(IRMAS_EXTRACT_DIR)"

inspect-irmas: extract-irmas scripts/inspect_irmas.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_irmas.py --root "$(IRMAS_EXTRACT_DIR)" > "$(IRMAS_INVENTORY_OUTPUT)"
	cat "$(IRMAS_INVENTORY_OUTPUT)"

prepare-irmas: extract-irmas scripts/prepare_irmas_manifest.py
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=irmas_labelled_samples
	$(PYTHON) scripts/prepare_irmas_manifest.py --root "$(IRMAS_EXTRACT_DIR)" --output "$(IRMAS_PREPARED_DIR)" --max-per-label "$(IRMAS_MAX_SAMPLES_PER_LABEL)" --minimum-samples "$(IRMAS_MIN_SAMPLES)"

measure-irmas: $(BUILD_DIR)/analyzer_real_note_samples prepare-irmas | $(BUILD_DIR)
	MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IRMAS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IRMAS_PREPARED_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_LABEL_ONLY=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(IRMAS_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_real_note_samples > "$(IRMAS_MEASUREMENT_OUTPUT)"

test-irmas-scripts: tests/test_irmas_scripts.py scripts/validate_irmas_archive.py scripts/extract_irmas.py scripts/prepare_irmas_manifest.py scripts/inspect_irmas.py
	$(PYTHON) tests/test_irmas_scripts.py

test-validate-kraisler-archive: tests/test_validate_kraisler_archive.py scripts/validate_kraisler_archive.py
	$(PYTHON) tests/test_validate_kraisler_archive.py

test-extract-kraisler: tests/test_extract_kraisler.py scripts/extract_kraisler.py scripts/validate_kraisler_archive.py
	$(PYTHON) tests/test_extract_kraisler.py

test-prepare-kraisler: tests/test_prepare_kraisler_manifest.py scripts/prepare_kraisler_manifest.py
	$(PYTHON) tests/test_prepare_kraisler_manifest.py

test-summarize-kraisler: tests/test_summarize_kraisler_measurement.py scripts/summarize_kraisler_measurement.py
	$(PYTHON) tests/test_summarize_kraisler_measurement.py

prepare-maestro-real-samples: scripts/prepare_maps_piano_samples.py download-maestro-real-samples | $(BUILD_DIR)
	+$(MAKE) BUILD_SAMPLE_STORAGE_DIR=maestro_real_samples ensure-build-sample-storage-link
	MAPS_PIANO_ARCHIVE="$(MAESTRO_REAL_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAESTRO_REAL_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAESTRO_REAL_SAMPLE_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAESTRO_REAL_MIN_RECORDINGS)" MAPS_PIANO_KINDS=OTHER $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAESTRO_REAL_ARCHIVE)" --output "$(MAESTRO_REAL_SAMPLE_DIR)" --limit "$(MAESTRO_REAL_SAMPLE_LIMIT)" --min-recordings "$(MAESTRO_REAL_MIN_RECORDINGS)" --kinds OTHER

measure-maestro-real-samples: $(BUILD_DIR)/analyzer_maestro prepare-maestro-real-samples scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) maestro_real_measurement env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAESTRO_REAL_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAESTRO_REAL_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$(MAESTRO_REAL_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_maestro > "$(MAESTRO_REAL_MEASUREMENT_OUTPUT)"
	@# Keep the committed accuracy dashboard synchronized with a new real result.
	@if test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)"; then $(MAKE) analyze-independent-piano-chord-evidence analyze-independent-piano-chord-states; else printf '%s\n' "independent piano comparison skipped: missing $(MAPS_PIANO_ATTRIBUTE_TSV)"; fi
	@if test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv"; then $(MAKE) update-detection-accuracy-report-cached; else printf '%s\n' "accuracy dashboard refresh skipped: missing $(BUILD_DIR)/real_note_full_mix_attributes.tsv"; fi

test-maps-piano-samples: test-maps-piano-samples-parallel

test-maps-piano-samples-serial: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT="$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT="$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT="$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT="$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(BUILD_DIR)/analyzer_maestro

test-maps-piano-samples-parallel: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_maps_piano_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MAPS_PIANO_LOCK_DIR)" -- "$(MAKE)" test-maps-piano-samples-parallel-unlocked

test-maps-piano-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MAPS_PIANO_TEST_MAKE_JOBS) $(MAPS_PIANO_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_maps_piano_shards $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_REQUIRED_WINDOWS)" --min-recall-percent "$(MAPS_PIANO_MIN_RECALL_PERCENT)" --min-precision-percent "$(MAPS_PIANO_MIN_PRECISION_PERCENT)" --min-keyboard-recall-percent "$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" --max-contamination-percent "$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" --max-false-non-keyboard-percent "$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" --min-chord-recall-percent "$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" --min-chord-checks "$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(MAPS_PIANO_SHARD_OUTS)

test-maps-piano-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_samples_shard_$*.err"

capture-analyzer-cases: $(BUILD_DIR)/analyzer_cases scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_cases_capture $(BUILD_DIR)/analyzer_cases > "$(BUILD_DIR)/analyzer_cases_capture.out" 2>&1

# Measure the prepared MAPS chord fixture without archive checks, preparation,
# or downloading.  The regular test target remains the policy gate.
measure-maps-piano-cached: $(BUILD_DIR)/analyzer_maestro scripts/check_maestro_shards.py scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_SAMPLE_DIR)/maps" || { printf '%s\n' "missing prepared MAPS piano CSV or audio under $(MAPS_PIANO_SAMPLE_DIR); run make prepare-maps-piano-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) analyzer_maps_piano_cached $(MAKE) $(MAPS_PIANO_TEST_MAKE_JOBS) $(addprefix measure-maps-piano-cached-shard-,$(MAPS_PIANO_SHARD_INDEXES))
	$(RUN_WITH_DURATION) check_maps_piano_cached $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_REQUIRED_WINDOWS)" --min-recall-percent 0 --min-precision-percent 0 --min-keyboard-recall-percent 0 --max-contamination-percent 100 --max-false-non-keyboard-percent 100 --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_SHARD_OUTS)

measure-maps-piano-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_samples_shard_$*.err"

$(MAPS_PIANO_ATTRIBUTE_TSV): $(MAPS_PIANO_ATTRIBUTE_PARTS) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(BUILD_DIR)/maps_piano_attributes.lock" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(MAPS_PIANO_TEST_MAKE_JOBS)" $(MAPS_PIANO_ATTRIBUTE_PARTS)

$(BUILD_DIR)/maps_piano_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$*" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_attributes.shard-$*.out"

analyze-maps-piano-attributes: $(MAPS_PIANO_ATTRIBUTE_TSV)
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

# Inspect already generated MAPS traits without entering the preparation graph.
analyze-maps-piano-attributes-cached: scripts/analyze_maps_piano_attributes.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing cached $(MAPS_PIANO_ATTRIBUTE_TSV)"; exit 2; }
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

summarize-maps-piano-attributes: scripts/analyze_maps_piano_attributes.py
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

summarize-maps-piano-note-attributes: scripts/analyze_maps_piano_attributes.py
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

.PHONY: inspect-maps-piano-low-miss-rows
inspect-maps-piano-low-miss-rows: scripts/inspect_maps_piano_low_miss_rows.py
	$(PYTHON) scripts/inspect_maps_piano_low_miss_rows.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

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
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_note_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.err"

# Measure the prepared MAPS isolated-piano fixture without preparing or
# downloading it.  This is intentionally non-gating: the current benchmark
# records its low precision as evidence in the dashboard.
measure-maps-piano-note-cached: $(BUILD_DIR)/analyzer_maestro scripts/check_maestro_shards.py scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maps/isol" || { printf '%s\n' "missing prepared MAPS isolated-piano CSV or audio under $(MAPS_PIANO_NOTE_SAMPLE_DIR); run make prepare-maps-piano-note-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) analyzer_maps_piano_note_cached $(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(addprefix measure-maps-piano-note-cached-shard-,$(MAPS_PIANO_NOTE_SHARD_INDEXES))
	$(RUN_WITH_DURATION) check_maps_piano_note_cached $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" --min-recall-percent 0 --min-precision-percent 0 --min-keyboard-recall-percent 0 --max-contamination-percent 100 --max-false-non-keyboard-percent 100 --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_NOTE_SHARD_OUTS)

measure-maps-piano-note-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_note_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.err"

# Regenerate diagnostic traits from the already-prepared external MAPS cache.
# This must not prepare or download samples, and remains non-gating.
refresh-maps-piano-note-attributes-cached: $(BUILD_DIR)/analyzer_maestro scripts/merge_tsv_parts.sh scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maps/isol" || { printf '%s\n' "missing prepared MAPS isolated-piano CSV or audio under $(MAPS_PIANO_NOTE_SAMPLE_DIR); run make prepare-maps-piano-note-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) refresh_maps_piano_note_attributes_cached $(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(addprefix refresh-maps-piano-note-attributes-cached-shard-,$(MAPS_PIANO_NOTE_SHARD_INDEXES))
	$(RUN_WITH_DURATION) merge_maps_piano_note_attributes_cached $(SHELL) scripts/merge_tsv_parts.sh "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)" $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS)

refresh-maps-piano-note-attributes-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh | $(BUILD_DIR)
	@shard="$*"; $(RUN_WITH_DURATION) refresh_maps_piano_note_attributes_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.tsv" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.out" 2> "$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.err"

$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV): $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(BUILD_DIR)/maps_piano_note_attributes.lock" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(MAPS_PIANO_NOTE_TEST_MAKE_JOBS)" $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS)

$(BUILD_DIR)/maps_piano_note_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$*" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_attributes.shard-$*.out"

analyze-maps-piano-note-attributes: $(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

# Inspect already generated isolated-piano traits without preparing or downloading.
analyze-maps-piano-note-attributes-cached: scripts/analyze_maps_piano_attributes.py
	@test -s "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)" || { printf '%s\n' "missing cached $(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"; exit 2; }
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

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

.PHONY: test-instrument-samples-hihat
test-instrument-samples-hihat: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples_hihat env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="hihat" $(BUILD_DIR)/analyzer_instrument_samples

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

filter-hf-drum-primary-attribute-rows: $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" $(FILTER_DRUM_ATTRIBUTE_ARGS)

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

update-detection-accuracy-report: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT) $(GUITAR_CHORD_TONE_RECOVERY_AUDIT) $(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT) $(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT) $(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT) $(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT) inspect-urmp-bass-timing inspect-harmonic-product-octave-evidence-cached audit-dominant-seventh-extension audit-global-chord-confidence audit-same-root-guitar-quality evaluate-owner-classifier-loco evaluate-owner-classifier-quality-loco evaluate-drum-primary-loco audit-drum-false-positive-caps audit-mdb-full-mix-false-positive-caps audit-mdb-full-mix-competing-active-contexts audit-drum-false-positive-contexts audit-chord-primary-components audit-independent-piano-exact-chord-fallback audit-piano-chord-confirmation audit-piano-chord-confirm3 audit-piano-chord-tone018 audit-piano-chord-margin060 audit-piano-chord-bassbonus000 inspect-mdb-rim-coverage inspect-fsd50k-rim-metadata inspect-commons-rimshot-candidate measure-pixabay-rimshot-candidate measure-pixabay-rimshot-f-candidate measure-pixabay-rim-shot-candidate audit-beat-this-continuous-interval-gate inspect-high-vocal-octave-evidence-cached scripts/write_detection_accuracy_report.py
	$(PYTHON) scripts/write_detection_accuracy_report.py --input "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(DETECTION_ACCURACY_CHORD_ARGS) $(DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_ARG) $(DETECTION_ACCURACY_URMP_GATE_ARG) $(DETECTION_ACCURACY_BACH10_GATE_ARGS) $(DETECTION_ACCURACY_MUSICNET_GATE_ARG) $(DETECTION_ACCURACY_MAPS_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_NOTE_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_CROSS_CORPUS_CHORD_ARGS) $(DETECTION_ACCURACY_DRUM_GATE_ARG) $(DETECTION_ACCURACY_HF_DRUM_GATE_ARGS) $(DETECTION_ACCURACY_STAR_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_ROUTE_SUMMARY_ARG) $(DETECTION_ACCURACY_GOOD_SOUNDS_FULL_MIX_ARG) $(DETECTION_ACCURACY_IRMAS_LABELLED_ARG) $(DETECTION_ACCURACY_PITCH_SHIFTED_VIOLIN_ARG) $(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_PHILHARMONIA_FULL_ARG) $(DETECTION_ACCURACY_IOWA_ORCHESTRA_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_WIND_EXACT_ARG) $(DETECTION_ACCURACY_IOWA_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_IOWA_PIANO_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_SAX_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_ARG) $(DETECTION_ACCURACY_REAL_A2S_TENOR_SCALE_ARG) $(DETECTION_ACCURACY_URMP_SAX_EXACT_ARG) $(DETECTION_ACCURACY_URMP_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_VALIDATION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_INSPECTION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_EXTRACT_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_MANIFEST_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MEASUREMENT_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_ARCHIVE_ARG) $(DETECTION_ACCURACY_KRAISLER_EXTRACT_ARG) $(DETECTION_ACCURACY_KRAISLER_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG) $(DETECTION_ACCURACY_KRAISLER_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_ANNOTATIONS_ARG) $(DETECTION_ACCURACY_EGMD_BPM_ARG) $(DETECTION_ACCURACY_BTT_ARGS) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_INSPECTION_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_PATTERN_REPORT_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_ARCHIVE_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_MIR1K_FULL_MIX_ARG) $(DETECTION_ACCURACY_SCMS_ARCHIVE_ARG) $(DETECTION_ACCURACY_SCMS_INSPECTION_ARG) $(DETECTION_ACCURACY_SCMS_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCAL_EXACT_NOTE_CROSS_CORPUS_ARG) $(DETECTION_ACCURACY_HIGH_VOCAL_OCTAVE_AUDIT_ARG) $(DETECTION_ACCURACY_HIGH_SOPRANO_VOCAL_MIRROR_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_TONE_RECOVERY_AUDIT_ARG) $(DETECTION_ACCURACY_URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_ARG) $(DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG) $(DETECTION_ACCURACY_GLOBAL_CHORD_CONFIDENCE_AUDIT_ARG) $(DETECTION_ACCURACY_SAME_ROOT_GUITAR_QUALITY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITARSET_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_OTHER_DETECTION_ARG) $(DETECTION_ACCURACY_BASIC_PITCH_ONNX_ARGS) --output "$(DETECTION_ACCURACY_REPORT)"

# Choir corpus preparation rewrites shared manifests, so keep this refresh
# serialized even when a caller runs make with -j.
.PHONY: refresh-choir-chord-accuracy
refresh-choir-chord-accuracy:
	+$(MAKE) -B $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) measure-dagstuhl-choirset
	+$(MAKE) measure-choral-singing-dataset
	+$(MAKE) measure-esmuc-choir-dataset
	+$(MAKE) update-detection-accuracy-report-cached

.PHONY: inspect-satb-missing-pitch-evidence test-inspect-satb-missing-pitch-evidence
inspect-satb-missing-pitch-evidence: scripts/inspect_satb_missing_pitch_evidence.py
	$(PYTHON) scripts/inspect_satb_missing_pitch_evidence.py --input "DCS=$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"

.PHONY: audit-satb-relative-chroma-selector test-audit-satb-relative-chroma-selector
audit-satb-relative-chroma-selector: $(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)
	@cat "$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)"

$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT): scripts/audit_satb_relative_chroma_selector.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached SATB selector input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/audit_satb_relative_chroma_selector.py --input "DCS=$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$@"

test-audit-satb-relative-chroma-selector: tests/test_audit_satb_relative_chroma_selector.py scripts/audit_satb_relative_chroma_selector.py
	$(PYTHON) tests/test_audit_satb_relative_chroma_selector.py

test-inspect-satb-missing-pitch-evidence: tests/test_inspect_satb_missing_pitch_evidence.py scripts/inspect_satb_missing_pitch_evidence.py
	$(PYTHON) tests/test_inspect_satb_missing_pitch_evidence.py

.PHONY: update-detection-accuracy-report-cached
update-detection-accuracy-report-cached: DETECTION_ACCURACY_OTHER_DETECTION_ARG += $(DETECTION_ACCURACY_BASIC_PITCH_ONNX_ARGS)
update-detection-accuracy-report-cached: scripts/write_detection_accuracy_report.py
	@test -f "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing build/real_note_full_mix_attributes.tsv; run make update-detection-accuracy-report first"; exit 2; }
	@for path in "$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)" "$(GUITAR_CHORD_TONE_RECOVERY_AUDIT)" "$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)" "$(URMP_BASS_TIMING_AUDIT)" "$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)" "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)" "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)" "$(SAME_ROOT_GUITAR_QUALITY_AUDIT)" "$(OWNER_CLASSIFIER_LOCO_AUDIT)" "$(OWNER_CLASSIFIER_QUALITY_LOCO_AUDIT)" "$(DRUM_PRIMARY_LOCO_AUDIT)" "$(DRUM_FALSE_POSITIVE_CAP_AUDIT)" "$(MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT)" "$(MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT)" "$(DRUM_FALSE_POSITIVE_CONTEXT_AUDIT)" "$(CHORD_PRIMARY_COMPONENT_AUDIT)" "$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)" "$(PIANO_CHORD_CONFIRMATION_AUDIT)" "$(PIANO_CHORD_CONFIRM3_AUDIT)" "$(PIANO_CHORD_TONE018_AUDIT)" "$(PIANO_CHORD_MARGIN060_AUDIT)" "$(PIANO_CHORD_BASSBONUS000_AUDIT)" "$(MDB_RIM_COVERAGE_AUDIT)" "$(FSD50K_RIM_METADATA_AUDIT)" "$(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)" "$(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)" "$(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)" "$(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT)" "$(HARMONIC_PRODUCT_OCTAVE_AUDIT)" "$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)"; do test -s "$$path" || { printf '%s\n' "missing cached accuracy audit: $$path"; exit 2; }; done
	$(PYTHON) scripts/write_detection_accuracy_report.py --input "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(DETECTION_ACCURACY_CHORD_ARGS) $(DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_ARG) $(DETECTION_ACCURACY_URMP_GATE_ARG) $(DETECTION_ACCURACY_BACH10_GATE_ARGS) $(DETECTION_ACCURACY_MUSICNET_GATE_ARG) $(DETECTION_ACCURACY_MAPS_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_NOTE_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_DRUM_GATE_ARG) $(DETECTION_ACCURACY_HF_DRUM_GATE_ARGS) $(DETECTION_ACCURACY_STAR_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_ROUTE_SUMMARY_ARG) $(DETECTION_ACCURACY_GOOD_SOUNDS_FULL_MIX_ARG) $(DETECTION_ACCURACY_IRMAS_LABELLED_ARG) $(DETECTION_ACCURACY_PITCH_SHIFTED_VIOLIN_ARG) $(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_PHILHARMONIA_FULL_ARG) $(DETECTION_ACCURACY_IOWA_ORCHESTRA_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_WIND_EXACT_ARG) $(DETECTION_ACCURACY_IOWA_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_IOWA_PIANO_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_MIX_ARG) $(DETECTION_ACCURACY_REAL_A2S_TENOR_SCALE_ARG) $(DETECTION_ACCURACY_URMP_SAX_EXACT_ARG) $(DETECTION_ACCURACY_URMP_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_VALIDATION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_INSPECTION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_EXTRACT_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_MANIFEST_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MEASUREMENT_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_ARCHIVE_ARG) $(DETECTION_ACCURACY_KRAISLER_EXTRACT_ARG) $(DETECTION_ACCURACY_KRAISLER_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG) $(DETECTION_ACCURACY_BTT_ARGS) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_INSPECTION_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_PATTERN_REPORT_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_ARCHIVE_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_MIR1K_FULL_MIX_ARG) $(DETECTION_ACCURACY_SCMS_ARCHIVE_ARG) $(DETECTION_ACCURACY_SCMS_INSPECTION_ARG) $(DETECTION_ACCURACY_SCMS_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCAL_EXACT_NOTE_CROSS_CORPUS_ARG) $(DETECTION_ACCURACY_HIGH_VOCAL_OCTAVE_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_TONE_RECOVERY_AUDIT_ARG) $(DETECTION_ACCURACY_URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_ARG) $(DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG) $(DETECTION_ACCURACY_DOMINANT_SEVENTH_EXTENSION_AUDIT_ARG) $(DETECTION_ACCURACY_GLOBAL_CHORD_CONFIDENCE_AUDIT_ARG) $(DETECTION_ACCURACY_SAME_ROOT_GUITAR_QUALITY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITARSET_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_OTHER_DETECTION_ARG) --output "$(DETECTION_ACCURACY_REPORT)"

test-detection-accuracy-report: tests/test_write_detection_accuracy_report.py scripts/write_detection_accuracy_report.py
	$(PYTHON) tests/test_write_detection_accuracy_report.py

test-summarize-isolated-guitar-visual: tests/test_summarize_isolated_guitar_visual.py scripts/summarize_isolated_guitar_visual.py
	$(PYTHON) tests/test_summarize_isolated_guitar_visual.py

.PHONY: test-analyzer-real-note-label-only
test-analyzer-real-note-label-only: $(BUILD_DIR)/analyzer_real_note_samples tests/test_analyzer_real_note_label_only.py
	$(PYTHON) tests/test_analyzer_real_note_label_only.py

inspect-real-note-attribute-buckets: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(INSPECT_BUCKET),--bucket "$(INSPECT_BUCKET)") $(INSPECT_ARGS)

inspect-real-note-full-mix-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(REAL_NOTE_SAMPLE_DIR)/manifest.tsv; prepare samples separately before inspecting"; exit 2; }
	@rm -f "$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)"
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)" --sample-id "$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)

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

# Mine an existing real-note export without rebuilding or preparing NSynth.
find-real-note-octave-displacement-cached: scripts/find_real_note_attribute_patterns.py
	@test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing build/real_note_full_mix_attributes.tsv; run make analyze-real-note-attributes first"; exit 2; }
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

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

# Audit the leading electronic-piano-to-Guitar display candidate without replaying
# audio.  The profile must recur on independent MAPS and MAESTRO piano rows before
# it can be considered for a runtime routing change.
measure-electronic-piano-guitar-route-cached: scripts/measure_real_note_attribute_rule.py
	@test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing $(BUILD_DIR)/real_note_full_mix_attributes.tsv; run make test-real-note-samples-full-mix first"; exit 2; }
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV); run make analyze-maps-piano-attributes first"; exit 2; }
	@test -s "$(MAESTRO_REAL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAESTRO_REAL_ATTRIBUTE_TSV); run make measure-maestro-real-samples first"; exit 2; }
	@tmp="$(ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT).tmp"; $(PYTHON) scripts/measure_real_note_attribute_rule.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --condition "status=hit" --condition "family=piano" --condition "buffer_strongest_row=guitar" --condition "guitar_keyboard_score_ratio>=2.147" --condition "noise<=0.001" --condition "slope>=0.086" --compare-path "$(MAPS_PIANO_ATTRIBUTE_TSV)" --compare-path "$(MAESTRO_REAL_ATTRIBUTE_TSV)" --group-by source --group-by buffer_strongest_row --examples 12 > "$$tmp" && mv "$$tmp" "$(ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT)"
	@cat "$(ELECTRONIC_PIANO_GUITAR_ROUTE_AUDIT)"

# Audit the largest SCMS vocal-to-Other visual-route profile without replaying
# audio.  At least two independent vocal corpora must reproduce it before a
# display-rerouting change can be considered.
measure-scms-vocal-other-route-cached: scripts/measure_real_note_attribute_rule.py
	@for path in "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached vocal route input: $$path"; exit 2; }; done
	@tmp="$(SCMS_VOCAL_OTHER_ROUTE_AUDIT).tmp"; $(PYTHON) scripts/measure_real_note_attribute_rule.py "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)" --condition "status=hit" --condition "family=vocals" --condition "buffer_visual_strongest_row=other" --condition "other_vocal_score_ratio>=2.75" --condition "partial5>=0.002" --condition "third_octave_ratio>=0.035" --compare-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" --group-by source --group-by buffer_visual_strongest_row --examples 12 > "$$tmp" && mv "$$tmp" "$(SCMS_VOCAL_OTHER_ROUTE_AUDIT)"
	@cat "$(SCMS_VOCAL_OTHER_ROUTE_AUDIT)"

# Measure the leading Good Sounds tenor-saxophone-to-Piano route on three
# independently prepared saxophone fixtures before considering any reroute.
measure-tenor-sax-piano-route-cached: scripts/measure_real_note_attribute_rule.py
	@for path in "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached tenor-sax route input: $$path"; exit 2; }; done
	@tmp="$(TENOR_SAX_PIANO_ROUTE_AUDIT).tmp"; $(PYTHON) scripts/measure_real_note_attribute_rule.py "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --condition "status=hit" --condition "family=other" --condition "buffer_strongest_row=piano" --condition "adjacent_upper_ratio<=0.007" --condition "debug_midi<=66" --condition "keyboard_guitar_score_ratio>=5.238" --primary-condition "source=sax-tenor" --compare-path "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" --compare-path "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --group-by source --group-by buffer_strongest_row --examples 12 > "$$tmp" && mv "$$tmp" "$(TENOR_SAX_PIANO_ROUTE_AUDIT)"
	@cat "$(TENOR_SAX_PIANO_ROUTE_AUDIT)"

.PHONY: measure-violin-guitar-route-cached
# Audit the leading Good Sounds violin-to-Guitar route on independent Iowa
# strings and KRAISLER piano--violin mixture evidence.
measure-violin-guitar-route-cached: scripts/measure_real_note_attribute_rule.py
	@for path in "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)" "$(KRAISLER_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached violin route input: $$path"; exit 2; }; done
	@tmp="$(VIOLIN_GUITAR_ROUTE_AUDIT).tmp"; $(PYTHON) scripts/measure_real_note_attribute_rule.py "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --condition "status=hit" --condition "family=other" --condition "buffer_strongest_row=guitar" --condition "adjacent_lower_ratio<=0.002" --condition "keyboard_other_score_ratio>=1.325" --condition "pitch_confidence>=0.956" --primary-condition "source=violin" --compare-path "$(IOWA_STRINGS_DETECTED_ATTRIBUTE_ROWS)" --compare-path "$(KRAISLER_ATTRIBUTE_OUTPUT)" --group-by source --group-by buffer_strongest_row --examples 12 > "$$tmp" && mv "$$tmp" "$(VIOLIN_GUITAR_ROUTE_AUDIT)"
	@cat "$(VIOLIN_GUITAR_ROUTE_AUDIT)"

inspect-real-note-candidate-rows: $(REAL_NOTE_CANDIDATE_ROW_PATHS) scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) scripts/inspect_real_note_candidate_rows.py $(if $(REAL_NOTE_CANDIDATE_RULE),--rule "$(REAL_NOTE_CANDIDATE_RULE)") $(REAL_NOTE_CANDIDATE_ARGS) $(REAL_NOTE_CANDIDATE_ROW_PATHS)

inspect-real-note-shard-errors: scripts/inspect_real_note_shard_errors.py
	@test -n "$(REAL_NOTE_SHARD_ERROR_TAG)" || { printf '%s\n' "set REAL_NOTE_SHARD_ERROR_TAG"; exit 2; }
	$(PYTHON) scripts/inspect_real_note_shard_errors.py --tag "$(REAL_NOTE_SHARD_ERROR_TAG)" $(REAL_NOTE_SHARD_ERROR_ARGS)

inspect-guitar-fretboard-note-failure: $(BUILD_DIR)/analyzer_real_note_samples prepare-guitar-fretboard-note-samples scripts/analyze_real_note_misses.py scripts/inspect_real_note_shard_errors.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) guitar_fretboard_verbose_shard env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GUITAR_FRETBOARD_NOTES_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX=9 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_guitar_fretboard_verbose.out" 2> "$(BUILD_DIR)/real_note_guitar_fretboard_verbose.err"
	$(PYTHON) scripts/inspect_real_note_shard_errors.py --path "$(BUILD_DIR)/real_note_guitar_fretboard_verbose.err"
	$(PYTHON) scripts/analyze_real_note_misses.py "$(BUILD_DIR)/real_note_guitar_fretboard_verbose.err"

inspect-vocalset-note-failures: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocalset-samples scripts/analyze_real_note_misses.py scripts/inspect_real_note_shard_errors.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) vocalset_verbose_misses env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=128 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_vocalset_verbose.out" 2> "$(BUILD_DIR)/real_note_vocalset_verbose.err"
	$(PYTHON) scripts/inspect_real_note_shard_errors.py --path "$(BUILD_DIR)/real_note_vocalset_verbose.err" --limit 0
	$(PYTHON) scripts/analyze_real_note_misses.py "$(BUILD_DIR)/real_note_vocalset_verbose.err"

# Read only existing exports.  This is suitable for trait investigation when
# a corpus archive is absent or intentionally must not be revalidated.
inspect-real-note-candidate-rows-cached: scripts/inspect_real_note_candidate_rows.py
	@test -n "$(REAL_NOTE_CANDIDATE_ROW_PATHS)" || { printf '%s\n' "set REAL_NOTE_CANDIDATE_ROW_PATHS"; exit 2; }
	@for path in $(REAL_NOTE_CANDIDATE_ROW_PATHS); do test -s "$$path" || { printf '%s\n' "missing cached candidate rows: $$path"; exit 2; }; done
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

.PHONY: find-good-sounds-full-mix-ownership-patterns inspect-good-sounds-full-mix-debug-cached validate-good-sounds-archive
find-good-sounds-full-mix-ownership-patterns: scripts/find_real_note_attribute_patterns.py
	@test -f "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV); run make analyze-good-sounds-full-mix-attributes first"; exit 2; }
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" $(GOOD_SOUNDS_FULL_MIX_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(GOOD_SOUNDS_FULL_MIX_OWNERSHIP_PATTERN_ARGS))

.PHONY: inspect-good-sounds-full-mix-debug-cached
inspect-good-sounds-full-mix-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(GOOD_SOUNDS_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set GOOD_SOUNDS_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv; prepare samples separately before inspecting"; exit 2; }
	@rm -f "$(GOOD_SOUNDS_DEBUG_ATTRIBUTE_TSV)"
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GOOD_SOUNDS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(GOOD_SOUNDS_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(GOOD_SOUNDS_DEBUG_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(GOOD_SOUNDS_DEBUG_ATTRIBUTE_TSV)" --sample-id "$(GOOD_SOUNDS_DEBUG_SAMPLE_ID)" $(GOOD_SOUNDS_DEBUG_INSPECT_ARGS)

.PHONY: inspect-good-sounds-full-mix-bass-misses
inspect-good-sounds-full-mix-bass-misses: scripts/inspect_good_sounds_bass_misses.py
	@test -f "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV); run make analyze-good-sounds-full-mix-attributes first"; exit 2; }
	$(PYTHON) scripts/inspect_good_sounds_bass_misses.py "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)"

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
	@test -f "$(GUITAR_TECHS_SAMPLE_DIR)/manifest.tsv"

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

$(GUITAR_TECHS_ISOLATED_VISUAL_AUDIT): $(GUITAR_TECHS_ATTRIBUTE_TSV) scripts/summarize_isolated_guitar_visual.py | $(BUILD_DIR)
	$(PYTHON) scripts/summarize_isolated_guitar_visual.py "$(GUITAR_TECHS_ATTRIBUTE_TSV)" --label "Guitar-TECHS" --output "$@"

analyze-guitar-techs-attributes: $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS)
	@printf '%s\n' "GuitarTechs attribute rows:"
	@printf '%s\n' "  $(GUITAR_TECHS_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_TECHS_MISS_ATTRIBUTE_ROWS)"

download-guitar-techs-chord-samples: $(GUITAR_TECHS_P1_CHORDS_ARCHIVE) $(GUITAR_TECHS_P2_CHORDS_ARCHIVE)

.PHONY: download-guitar-techs-music-samples
download-guitar-techs-music-samples: $(GUITAR_TECHS_P3_MUSIC_ARCHIVE)

.PHONY: inspect-guitar-techs-music-archive
inspect-guitar-techs-music-archive: $(GUITAR_TECHS_P3_MUSIC_ARCHIVE) scripts/check_zip_archive.py
	$(PYTHON) scripts/check_zip_archive.py --list "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)"

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

$(GUITAR_TECHS_P3_MUSIC_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE).part"; fi
	# Keep an incomplete archive: aria2/curl can resume it on the next invocation.
	# Only a complete ZIP is promoted to the final filename below.
	if [ ! -s "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P3_music.zip.part" "$(GUITAR_TECHS_P3_MUSIC_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE).part" "$(GUITAR_TECHS_P3_MUSIC_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE).part" "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" >/dev/null

prepare-guitar-techs-chord-samples: scripts/prepare_guitar_techs_chord_samples.py download-guitar-techs-chord-samples | $(BUILD_DIR)
	GUITAR_TECHS_CHORD_SAMPLE_DIR="$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" GUITAR_TECHS_CHORD_SAMPLE_LIMIT="$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" GUITAR_TECHS_CHORD_MIN_EXCERPTS="$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_chord_samples.py --archive "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" --output "$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" --ffmpeg "$(FFMPEG)"

.PHONY: prepare-guitar-techs-music-samples test-guitar-techs-music-samples
prepare-guitar-techs-music-samples: scripts/prepare_guitar_techs_chord_samples.py $(GUITAR_TECHS_P3_MUSIC_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=guitar_techs_music_samples
	GUITAR_TECHS_CHORD_SAMPLE_DIR="$(GUITAR_TECHS_MUSIC_SAMPLE_DIR)" GUITAR_TECHS_CHORD_SAMPLE_LIMIT="$(GUITAR_TECHS_MUSIC_SAMPLE_LIMIT)" GUITAR_TECHS_CHORD_MIN_EXCERPTS="$(GUITAR_TECHS_MUSIC_MIN_EXCERPTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_chord_samples.py --archive "$(GUITAR_TECHS_P3_MUSIC_ARCHIVE)" --output "$(GUITAR_TECHS_MUSIC_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_MUSIC_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_MUSIC_MIN_EXCERPTS)" --ffmpeg "$(FFMPEG)"

$(GUITAR_TECHS_MUSIC_MANIFEST): scripts/prepare_guitar_techs_chord_samples.py $(GUITAR_TECHS_P3_MUSIC_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-guitar-techs-music-samples

test-guitar-techs-music-samples: $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_MUSIC_MANIFEST) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_techs_music_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_MUSIC_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_TECHS_MUSIC_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_TECHS_MUSIC_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_TECHS_MUSIC_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_TECHS_MUSIC_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_TECHS_MUSIC_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_TECHS_MUSIC_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_TECHS_MUSIC_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(GUITAR_TECHS_MUSIC_EXTRA_ENV) $(BUILD_DIR)/analyzer_guitarset

.PHONY: debug-guitar-techs-music-windows inspect-guitar-techs-music-debug
debug-guitar-techs-music-windows:
	@$(MAKE) --no-print-directory test-guitar-techs-music-samples GUITAR_TECHS_MUSIC_EXTRA_ENV="MUSIC_ANALYZER_GUITARSET_DEBUG_WINDOWS=1" > "$(GUITAR_TECHS_MUSIC_DEBUG_OUT)" 2>&1
	@printf '%s\n' "guitar debug windows: $(GUITAR_TECHS_MUSIC_DEBUG_OUT)"

inspect-guitar-techs-music-debug: $(GUITAR_TECHS_MUSIC_DEBUG_OUT)
	@test -n "$(GUITAR_TECHS_MUSIC_DEBUG_PATTERN)" || { printf '%s\n' "set GUITAR_TECHS_MUSIC_DEBUG_PATTERN to a recording id or trait"; exit 2; }
	rg -n -- "$(GUITAR_TECHS_MUSIC_DEBUG_PATTERN)" "$(GUITAR_TECHS_MUSIC_DEBUG_OUT)"

$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_guitarset $(GUITAR_TECHS_MUSIC_MANIFEST) | $(BUILD_DIR)
	@out="$(BUILD_DIR)/guitar_techs_music_attributes.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_MUSIC_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT=100 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_HITS=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

$(GUITAR_TECHS_MUSIC_DETECTED_ATTRIBUTE_ROWS): $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)" --dump-rows > "$@"

$(GUITAR_TECHS_MUSIC_MISS_ATTRIBUTE_ROWS): $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV) scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)" --dump-rows --misses-only > "$@"

.PHONY: analyze-guitar-techs-music-attributes
analyze-guitar-techs-music-attributes: $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV) scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)"
	@printf '%s\n' "attribute TSV: $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)"

.PHONY: find-guitar-techs-music-attribute-patterns find-guitar-techs-music-route-patterns
find-guitar-techs-music-attribute-patterns: $(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV) scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py scripts/summarize_guitarset_attributes.py
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)" $(PATTERN_ARGS)

find-guitar-techs-music-route-patterns:
	+$(MAKE) find-guitar-techs-music-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(GUITAR_TECHS_MUSIC_ATTRIBUTE_TSV)\""

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
	+$(MAKE) find-guitar-techs-chord-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)\""

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

.PHONY: analyze-downloaded-guitarset-chord-recovery
analyze-downloaded-guitarset-chord-recovery: $(GUITARSET_ATTRIBUTE_TSV) scripts/analyze_guitar_chord_recovery.py
	$(PYTHON) scripts/analyze_guitar_chord_recovery.py "$(GUITARSET_ATTRIBUTE_TSV)" $(RECOVERY_ARGS)

.PHONY: audit-same-root-guitar-quality test-audit-same-root-guitar-quality
audit-same-root-guitar-quality: scripts/audit_same_root_guitar_quality.py $(GUITARSET_ATTRIBUTE_TSV)
	@for path in "$(GUITARSET_ATTRIBUTE_TSV)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached same-root guitar quality input: $$path"; exit 2; }; done
	@tmp="$(SAME_ROOT_GUITAR_QUALITY_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_same_root_guitar_quality.py "$(GUITARSET_ATTRIBUTE_TSV)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" > "$$tmp" && mv "$$tmp" "$(SAME_ROOT_GUITAR_QUALITY_AUDIT)" && cat "$(SAME_ROOT_GUITAR_QUALITY_AUDIT)"

test-audit-same-root-guitar-quality: tests/test_audit_same_root_guitar_quality.py scripts/audit_same_root_guitar_quality.py
	$(PYTHON) tests/test_audit_same_root_guitar_quality.py

.PHONY: evaluate-owner-classifier-loco evaluate-owner-classifier-quality-loco test-evaluate-owner-classifier-loco evaluate-drum-primary-loco test-evaluate-drum-primary-loco
evaluate-owner-classifier-loco: scripts/evaluate_owner_classifier_loco.py
	@for path in "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached owner-classifier input: $$path"; exit 2; }; done
	@tmp="$(OWNER_CLASSIFIER_LOCO_AUDIT).$$$$.tmp"; $(PYTHON) scripts/evaluate_owner_classifier_loco.py --feature-profile "$(OWNER_CLASSIFIER_FEATURE_PROFILE)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$(OWNER_CLASSIFIER_LOCO_AUDIT)" && cat "$(OWNER_CLASSIFIER_LOCO_AUDIT)"

evaluate-owner-classifier-quality-loco: scripts/evaluate_owner_classifier_loco.py
	+$(MAKE) -s evaluate-owner-classifier-loco OWNER_CLASSIFIER_FEATURE_PROFILE=quality OWNER_CLASSIFIER_LOCO_AUDIT="$(OWNER_CLASSIFIER_QUALITY_LOCO_AUDIT)"

.PHONY: audit-owner-classifier-quality-margin
audit-owner-classifier-quality-margin: scripts/audit_owner_classifier_quality_margin.py scripts/evaluate_owner_classifier_loco.py
	@$(PYTHON) scripts/audit_owner_classifier_quality_margin.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)"

test-evaluate-owner-classifier-loco: tests/test_evaluate_owner_classifier_loco.py scripts/evaluate_owner_classifier_loco.py
	$(PYTHON) tests/test_evaluate_owner_classifier_loco.py

evaluate-drum-primary-loco: scripts/evaluate_drum_primary_loco.py | $(BUILD_DIR)
	@for path in "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)"; do test -s "$$path" || { printf '%s\n' "missing cached drum-primary LOCO input: $$path"; exit 2; }; done
	@tmp="$(DRUM_PRIMARY_LOCO_AUDIT).$$$$.tmp"; $(PYTHON) scripts/evaluate_drum_primary_loco.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" "$(IDMT_DRUMS_PRIMARY_ATTRIBUTE_ROWS)" > "$$tmp" && mv "$$tmp" "$(DRUM_PRIMARY_LOCO_AUDIT)" && cat "$(DRUM_PRIMARY_LOCO_AUDIT)"

test-evaluate-drum-primary-loco: tests/test_evaluate_drum_primary_loco.py scripts/evaluate_drum_primary_loco.py
	$(PYTHON) tests/test_evaluate_drum_primary_loco.py

.PHONY: evaluate-owner-score-calibration-loco test-evaluate-owner-score-calibration-loco
evaluate-owner-score-calibration-loco: scripts/evaluate_owner_score_calibration_loco.py
	@for path in "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached owner-score-calibration input: $$path"; exit 2; }; done
	@tmp="$(OWNER_SCORE_CALIBRATION_LOCO_AUDIT).$$$$.tmp"; $(PYTHON) scripts/evaluate_owner_score_calibration_loco.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$(OWNER_SCORE_CALIBRATION_LOCO_AUDIT)" && cat "$(OWNER_SCORE_CALIBRATION_LOCO_AUDIT)"

test-evaluate-owner-score-calibration-loco: tests/test_evaluate_owner_score_calibration_loco.py scripts/evaluate_owner_score_calibration_loco.py
	$(PYTHON) tests/test_evaluate_owner_score_calibration_loco.py

# Inspect an existing real-audio chord export without re-preparing its corpus.
analyze-guitar-chord-mix-recovery-cached: scripts/analyze_guitar_chord_recovery.py
	@test -s "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" || { printf '%s\n' "missing build/guitar_chord_mix_attributes.tsv; run make analyze-guitar-chord-mix-attributes first"; exit 2; }
	$(PYTHON) scripts/analyze_guitar_chord_recovery.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(RECOVERY_ARGS)

# Recompute controlled real-audio chord metrics from an existing manifest only.
refresh-guitar-chord-mix-attributes-cached: $(BUILD_DIR)/analyzer_guitarset scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	@test -s "$(GUITAR_CHORD_MIX_MANIFEST)" || { printf '%s\n' "missing $(GUITAR_CHORD_MIX_MANIFEST); run make prepare-guitar-chord-mix-samples first"; exit 2; }
	@rm -f "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv"
	+$(SHELL) scripts/run_with_lock.sh "$(GUITAR_CHORD_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(MAKE)" "$(GUITAR_CHORD_MIX_ATTRIBUTE_MAKE_JOBS)" $(GUITAR_CHORD_MIX_ATTRIBUTE_PARTS)

analyze-guitar-chord-primary-order: $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py
	$(PYTHON) scripts/analyze_guitar_primary_order.py "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" $(PRIMARY_ORDER_ARGS)

analyze-gaps-guitar-full-primary-order: $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py
	$(PYTHON) scripts/analyze_guitar_primary_order.py "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)" $(PRIMARY_ORDER_ARGS)

CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT ?= $(BUILD_DIR)/cross_corpus_guitar_primary_order_audit.txt

$(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT): FORCE $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS) $(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS) scripts/audit_cross_corpus_guitar_primary_order.sh | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(SHELL) scripts/audit_cross_corpus_guitar_primary_order.sh "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)" "$(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS)" > "$$tmp" && mv "$$tmp" "$@"
	@printf '%s\n' "cross-corpus guitar primary-order audit: $@"

.PHONY: audit-cross-corpus-guitar-primary-order audit-cross-corpus-guitar-primary-order-cached test-audit-cross-corpus-guitar-primary-order
audit-cross-corpus-guitar-primary-order: $(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT)

audit-cross-corpus-guitar-primary-order-cached: scripts/audit_cross_corpus_guitar_primary_order.sh | $(BUILD_DIR)
	@test -s "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" && test -s "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)" && test -s "$(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS)" || { printf '%s\n' 'missing cached Guitar Chord Mix, GAPS, or Guitar-TECHS attribute rows'; exit 2; }
	@tmp="$(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT).$$$$.tmp"; $(SHELL) scripts/audit_cross_corpus_guitar_primary_order.sh "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" "$(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS)" "$(GUITAR_TECHS_CHORD_DETECTED_ATTRIBUTE_ROWS)" > "$$tmp" && mv "$$tmp" "$(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT)"
	@printf '%s\n' "cached cross-corpus guitar primary-order audit: $(CROSS_CORPUS_GUITAR_PRIMARY_ORDER_AUDIT)"

test-audit-cross-corpus-guitar-primary-order: scripts/audit_cross_corpus_guitar_primary_order.sh
	$(SHELL) -n scripts/audit_cross_corpus_guitar_primary_order.sh

$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT): FORCE $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) $(GAPS_GUITAR_FULL_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py | $(BUILD_DIR)
	@tmp="$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT).$$$$.tmp"; { printf '%s\n' "source=Guitar_Chord_Mix"; $(MAKE) -s analyze-guitar-chord-primary-order; printf '%s\n' "comparison=GAPS_full"; $(MAKE) -s analyze-gaps-guitar-full-primary-order; } > "$$tmp" && mv "$$tmp" "$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)"
	@printf '%s\n' "guitar chord primary display audit: $(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)"

measure-guitar-chord-primary-display-audit-cached: $(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)

$(GUITAR_CHORD_TONE_RECOVERY_AUDIT): FORCE $(GAPS_GUITAR_FULL_ATTRIBUTE_TSV) $(BUILD_DIR)/guitar_chord_mix_attributes.tsv $(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV) scripts/analyze_guitar_minor_third_candidates.py | $(BUILD_DIR)
	@tmp="$(GUITAR_CHORD_TONE_RECOVERY_AUDIT).$$$$.tmp"; { printf '%s\n' "tone=minor-third"; $(MAKE) -s analyze-guitar-minor-third-candidates; printf '%s\n' "tone=major-third"; $(MAKE) -s analyze-guitar-major-third-candidates; printf '%s\n' "tone=minor-fifth"; $(MAKE) -s analyze-guitar-minor-fifth-candidates; printf '%s\n' "tone=major-fifth"; $(MAKE) -s analyze-guitar-major-fifth-candidates; } > "$$tmp" && mv "$$tmp" "$(GUITAR_CHORD_TONE_RECOVERY_AUDIT)"
	@printf '%s\n' "guitar chord tone recovery audit: $(GUITAR_CHORD_TONE_RECOVERY_AUDIT)"

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
	+$(MAKE) find-guitar-chord-mix-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(BUILD_DIR)/guitar_chord_mix_attributes.tsv\""

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
	+$(MAKE) find-egfxset-guitar-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(EGFXSET_GUITAR_ATTRIBUTE_TSV)\""

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
	+$(MAKE) find-gaps-guitar-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(GAPS_GUITAR_ATTRIBUTE_TSV)\""

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
	+$(MAKE) find-gaps-guitar-full-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)\""

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
	@out="$(BUILD_DIR)/guitarset_attributes.shard-$*.out"; env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 $(GUITARSET_ATTRIBUTE_GATE_ENV) MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_SHARD_COUNT="$(GUITARSET_SHARDS)" MUSIC_ANALYZER_GUITARSET_SHARD_INDEX="$*" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_guitarset > "$$out"

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
	+$(MAKE) find-guitarset-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_ROUTE_PATTERN_ARGS) $(GUITAR_CHORD_ROUTE_PROTECTED_ARGS) --protected-path \"$(GUITARSET_ATTRIBUTE_TSV)\""

download-philharmonia-samples: | $(BUILD_DIR)
	mkdir -p "$(PHILHARMONIA_SOURCE_DIR)"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" "$(PHILHARMONIA_BASE_URL)/Woodwind.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" "$(PHILHARMONIA_BASE_URL)/Brass.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" "$(PHILHARMONIA_BASE_URL)/Strings.zip"

prepare-philharmonia-samples: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	PHILHARMONIA_SOURCE_DIR="$(PHILHARMONIA_SOURCE_DIR)" PHILHARMONIA_SAMPLE_DIR="$(PHILHARMONIA_SAMPLE_DIR)" PHILHARMONIA_SAMPLE_LIMIT="$(PHILHARMONIA_SAMPLE_LIMIT)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_philharmonia_samples.py --source "$(PHILHARMONIA_SOURCE_DIR)" --output "$(PHILHARMONIA_SAMPLE_DIR)" --limit "$(PHILHARMONIA_SAMPLE_LIMIT)" --min-samples "$(PHILHARMONIA_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	+$(MAKE) prepare-philharmonia-samples
	@test -f "$(PHILHARMONIA_SAMPLE_DIR)/manifest.tsv"

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
	@test -f "$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv"

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

$(PHILHARMONIA_FULL_ATTRIBUTE_TSV): FORCE $(BUILD_DIR)/analyzer_real_note_samples $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	# The sample drive can retain objects with future timestamps; force the
	# analyzer link before measuring so this report always reflects source.
	+$(MAKE) -B $(BUILD_DIR)/analyzer_real_note_samples
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

analyze-philharmonia-full-exact-midi-misses: scripts/analyze_exact_midi_misses.py
	@test -f "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(PHILHARMONIA_FULL_ATTRIBUTE_TSV); run make test-philharmonia-samples-full first"; exit 2; }
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

# Silent one-sample runtime trace for measured Philharmonia octave/error clusters.
inspect-philharmonia-full-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(PHILHARMONIA_FULL_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set PHILHARMONIA_FULL_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(PHILHARMONIA_FULL_SAMPLE_DIR)/manifest.tsv; prepare samples separately before inspecting"; exit 2; }
	@rm -f "$(PHILHARMONIA_FULL_DEBUG_ATTRIBUTE_TSV)"
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PHILHARMONIA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(PHILHARMONIA_FULL_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(PHILHARMONIA_FULL_DEBUG_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(PHILHARMONIA_FULL_DEBUG_ATTRIBUTE_TSV)" --sample-id "$(PHILHARMONIA_FULL_DEBUG_SAMPLE_ID)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)

test-analyze-exact-midi-misses: tests/test_analyze_exact_midi_misses.py scripts/analyze_exact_midi_misses.py
	$(PYTHON) tests/test_analyze_exact_midi_misses.py

# These are explicitly derived samples: real Philharmonia violin recordings
# shifted down one octave for coverage of sample-playback/pitch-shifted timbres.
# They are intentionally kept out of aggregate real-world accuracy dashboards.
prepare-pitch-shifted-violin-samples: scripts/prepare_pitch_shifted_violin_samples.py $(PITCH_SHIFTED_VIOLIN_SOURCE_MANIFEST) | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR="$(notdir $(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR))"
	$(PYTHON) scripts/prepare_pitch_shifted_violin_samples.py --source-manifest "$(PITCH_SHIFTED_VIOLIN_SOURCE_MANIFEST)" --output "$(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)" --per-midi "$(PITCH_SHIFTED_VIOLIN_PER_MIDI)" --ffmpeg "$(FFMPEG)"

$(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)/manifest.tsv: scripts/prepare_pitch_shifted_violin_samples.py $(PITCH_SHIFTED_VIOLIN_SOURCE_MANIFEST) | $(BUILD_DIR)
	+$(MAKE) prepare-pitch-shifted-violin-samples

test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel: REAL_NOTE_SAMPLE_TAG := pitchshifted_violin
test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)
test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel: REAL_NOTE_SAMPLE_REQUIRED_SAMPLES := $(PITCH_SHIFTED_VIOLIN_MIN_SAMPLES)
test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(PITCH_SHIFTED_VIOLIN_MIN_SAMPLES)
test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel: REAL_NOTE_SAMPLE_MAX_FAILURES := $(PITCH_SHIFTED_VIOLIN_MAX_FAILURES)
test-pitch-shifted-violin-samples: test-pitch-shifted-violin-samples-parallel

test-pitch-shifted-violin-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-pitch-shifted-violin-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

$(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(addprefix $(BUILD_DIR)/pitch_shifted_violin_attributes.shard-,$(addsuffix .tsv,$(REAL_NOTE_SAMPLE_SHARD_INDEXES)))

$(BUILD_DIR)/pitch_shifted_violin_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_pitch_shifted_violin_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(PITCH_SHIFTED_VIOLIN_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PITCH_SHIFTED_VIOLIN_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/pitch_shifted_violin_attributes.shard-$*.out" 2> "$(BUILD_DIR)/pitch_shifted_violin_attributes.shard-$*.err"

analyze-pitch-shifted-violin-attributes: $(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV)
	@printf '%s\n' "Pitch-shifted violin attribute TSV: $(PITCH_SHIFTED_VIOLIN_ATTRIBUTE_TSV)"

download-good-sounds-samples: validate-good-sounds-archive

.PHONY: inspect-good-sounds-archive-coverage
inspect-good-sounds-archive-coverage: scripts/inspect_good_sounds_archive_coverage.py scripts/prepare_good_sounds_samples.py
	@test -s "$(GOOD_SOUNDS_ARCHIVE)" || { printf '%s\n' "missing $(GOOD_SOUNDS_ARCHIVE)"; exit 2; }
	$(PYTHON) scripts/inspect_good_sounds_archive_coverage.py "$(GOOD_SOUNDS_ARCHIVE)" $(GOOD_SOUNDS_ARCHIVE_COVERAGE_ARGS)

$(GOOD_SOUNDS_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(GOOD_SOUNDS_SOURCE_DIR)"
	if [ -s "$(GOOD_SOUNDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GOOD_SOUNDS_ARCHIVE)" "$(GOOD_SOUNDS_ARCHIVE).part"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ] && [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)" -s "$(GOOD_SOUNDS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GOOD_SOUNDS_SOURCE_DIR)" --out "good-sounds.zip.part" "$(GOOD_SOUNDS_URL)"; else curl -fL -C - -o "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_URL)"; fi; fi
	if [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null; mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi

validate-good-sounds-archive: FORCE $(GOOD_SOUNDS_ARCHIVE)
	if ! $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null 2>&1; then if [ -s "$(GOOD_SOUNDS_ARCHIVE)" ]; then mv -f "$(GOOD_SOUNDS_ARCHIVE)" "$(GOOD_SOUNDS_ARCHIVE).part"; fi; $(MAKE) "$(GOOD_SOUNDS_ARCHIVE)"; fi

prepare-good-sounds-samples: scripts/prepare_good_sounds_samples.py download-good-sounds-samples | $(BUILD_DIR)
	GOOD_SOUNDS_ARCHIVE="$(GOOD_SOUNDS_ARCHIVE)" GOOD_SOUNDS_SAMPLE_DIR="$(GOOD_SOUNDS_SAMPLE_DIR)" GOOD_SOUNDS_SAMPLE_LIMIT="$(GOOD_SOUNDS_SAMPLE_LIMIT)" GOOD_SOUNDS_MIN_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_good_sounds_samples.py --archive "$(GOOD_SOUNDS_ARCHIVE)" --output "$(GOOD_SOUNDS_SAMPLE_DIR)" --limit "$(GOOD_SOUNDS_SAMPLE_LIMIT)" --min-samples "$(GOOD_SOUNDS_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)" $(if $(filter 1 true yes,$(GOOD_SOUNDS_REFRESH)),--refresh)

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

# Good Sounds uses the same labeled manifest schema as the canonical real-note
# fixture.  Keep its full-mix output separate so this independent acoustic
# corpus can add route coverage without changing the baseline NSynth ledger.
test-good-sounds-full-mix: test-good-sounds-full-mix-parallel

test-good-sounds-full-mix-parallel: $(BUILD_DIR)/analyzer_real_note_samples validate-good-sounds-archive $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh scripts/check_real_note_full_mix_shards.py
	+$(RUN_WITH_DURATION) analyzer_good_sounds_full_mix_parallel $(MAKE) $(GOOD_SOUNDS_FULL_MIX_TEST_MAKE_JOBS) $(GOOD_SOUNDS_FULL_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_good_sounds_full_mix_shards $(PYTHON) scripts/check_real_note_full_mix_shards.py --min-any-hit-percent 0 --min-expected-row-percent 0 --min-first-row-percent 0 --min-visual-row-percent 0 --bass-min-expected-row-percent 0 --guitar-min-expected-row-percent 0 --piano-min-expected-row-percent 0 --vocals-min-expected-row-percent 0 --other-min-expected-row-percent 0 --bass-min-first-row-percent 0 --guitar-min-first-row-percent 0 --piano-min-first-row-percent 0 --vocals-min-first-row-percent 0 --other-min-first-row-percent 0 --bass-min-visual-row-percent 0 --guitar-min-visual-row-percent 0 --piano-min-visual-row-percent 0 --vocals-min-visual-row-percent 0 --other-min-visual-row-percent 0 --max-drum-active-percent 100 $(GOOD_SOUNDS_FULL_MIX_SHARD_OUTS)

test-good-sounds-full-mix-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_good_sounds_full_mix_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(GOOD_SOUNDS_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GOOD_SOUNDS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/good_sounds_full_mix_shard_$*.out" 2> "$(BUILD_DIR)/good_sounds_full_mix_shard_$*.err"

$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples validate-good-sounds-archive $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/good_sounds_full_mix_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(GOOD_SOUNDS_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GOOD_SOUNDS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/good_sounds_full_mix_attributes.shard-$*.out"

analyze-good-sounds-full-mix-attributes: $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV) scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)"

# Rebuild attributes from the already prepared external corpus; never invokes
# the sample preparation/download target during normal detector iteration.
refresh-good-sounds-full-mix-attributes-cached: $(BUILD_DIR)/analyzer_real_note_samples scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	@test -s "$(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(GOOD_SOUNDS_SAMPLE_DIR)/manifest.tsv; prepare samples separately before measuring"; exit 2; }
	@rm -f "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)"
	+$(SHELL) scripts/run_with_lock.sh "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(MAKE)" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_PARTS)

prepare-iowa-piano-samples: scripts/prepare_iowa_piano_samples.py | $(BUILD_DIR)
	IOWA_PIANO_PAGE_URL="$(IOWA_PIANO_PAGE_URL)" IOWA_PIANO_FILE_BASE_URL="$(IOWA_PIANO_FILE_BASE_URL)" IOWA_PIANO_SOURCE_DIR="$(IOWA_PIANO_SOURCE_DIR)" IOWA_PIANO_SAMPLE_DIR="$(IOWA_PIANO_SAMPLE_DIR)" IOWA_PIANO_SAMPLE_LIMIT="$(IOWA_PIANO_SAMPLE_LIMIT)" IOWA_PIANO_MIN_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" IOWA_PIANO_DOWNLOAD_RETRIES="$(IOWA_PIANO_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_piano_samples.py --page-url "$(IOWA_PIANO_PAGE_URL)" --file-base-url "$(IOWA_PIANO_FILE_BASE_URL)" --source-dir "$(IOWA_PIANO_SOURCE_DIR)" --output "$(IOWA_PIANO_SAMPLE_DIR)" --limit "$(IOWA_PIANO_SAMPLE_LIMIT)" --min-samples "$(IOWA_PIANO_MIN_PIANO)" --download-retries "$(IOWA_PIANO_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv: scripts/prepare_iowa_piano_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-iowa-piano-samples
	@test -f "$(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv"

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

# Re-measure the already prepared external piano corpus in full-mix mode. This
# supplies routing features to the cross-corpus rule audit; it does not fetch
# data or play audio.
.PHONY: measure-iowa-piano-full-mix
measure-iowa-piano-full-mix: $(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)"

$(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(IOWA_PIANO_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS)" $(IOWA_PIANO_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/iowa_piano_full_mix_attributes.shard-%.tsv: FORCE $(BUILD_DIR)/analyzer_real_note_samples $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_piano_full_mix_attributes_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/iowa_piano_full_mix_attributes.shard-$*.out" 2> "$(BUILD_DIR)/iowa_piano_full_mix_attributes.shard-$*.err"

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
	@test -f "$(IOWA_STRINGS_SAMPLE_DIR)/manifest.tsv"

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
	@test -f "$(IOWA_ORCHESTRA_SAMPLE_DIR)/manifest.tsv"

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
	@test -f "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv"

prepare-iowa-sax-full-mix-fixture: $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv scripts/prepare_real_note_subset_fixture.py | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=iowa_sax_full_mix_fixture
	$(PYTHON) scripts/prepare_real_note_subset_fixture.py --source-manifest "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv" --output "$(IOWA_SAX_FULL_MIX_FIXTURE_DIR)" --source-token sax

measure-iowa-sax-full-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-sax-full-mix-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_iowa_sax_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_SAX_FULL_MIX_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_SAX_FULL_MIX_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=40 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(IOWA_SAX_FULL_MIX_OUTPUT)"
	@cat "$(IOWA_SAX_FULL_MIX_OUTPUT)"

find-iowa-sax-full-mix-row-confusion-patterns: $(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status row_confusion --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

find-iowa-sax-full-mix-first-row-confusion-patterns: $(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status first_row_confusion --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

prepare-tinysol-sax-full-mix-fixture: $(TINYSOL_SAMPLE_DIR)/manifest.tsv scripts/prepare_real_note_subset_fixture.py | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=tinysol_sax_full_mix_fixture
	$(PYTHON) scripts/prepare_real_note_subset_fixture.py --source-manifest "$(TINYSOL_SAMPLE_DIR)/manifest.tsv" --output "$(TINYSOL_SAX_FULL_MIX_FIXTURE_DIR)" --source-token alto-saxophone

prepare-tinysol-flute-full-mix-fixture: $(TINYSOL_SAMPLE_DIR)/manifest.tsv scripts/prepare_real_note_subset_fixture.py | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=tinysol_flute_full_mix_fixture
	$(PYTHON) scripts/prepare_real_note_subset_fixture.py --source-manifest "$(TINYSOL_SAMPLE_DIR)/manifest.tsv" --output "$(TINYSOL_FLUTE_FULL_MIX_FIXTURE_DIR)" --source-token flute

# A fresh, symlink-only independent check for the two Philharmonia wind/brass
# clusters. It is deliberately isolated-note mode: exact octave evidence must
# precede any display-routing recovery rule.
prepare-tinysol-wind-exact-fixture: $(TINYSOL_SAMPLE_DIR)/manifest.tsv scripts/prepare_real_note_subset_fixture.py | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=tinysol_wind_exact_fixture
	$(PYTHON) scripts/prepare_real_note_subset_fixture.py --source-manifest "$(TINYSOL_SAMPLE_DIR)/manifest.tsv" --output "$(TINYSOL_WIND_EXACT_FIXTURE_DIR)" --source-token oboe --source-token trombone

measure-tinysol-wind-exact: $(BUILD_DIR)/analyzer_real_note_samples prepare-tinysol-wind-exact-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_tinysol_wind_exact env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(TINYSOL_WIND_EXACT_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(TINYSOL_WIND_EXACT_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=40 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(TINYSOL_WIND_EXACT_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(TINYSOL_WIND_EXACT_OUTPUT)"
	@cat "$(TINYSOL_WIND_EXACT_OUTPUT)"

measure-tinysol-sax-full-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-tinysol-sax-full-mix-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_tinysol_sax_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(TINYSOL_SAX_FULL_MIX_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(TINYSOL_SAX_FULL_MIX_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=40 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(TINYSOL_SAX_FULL_MIX_OUTPUT)"
	@cat "$(TINYSOL_SAX_FULL_MIX_OUTPUT)"

measure-tinysol-flute-full-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-tinysol-flute-full-mix-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_tinysol_flute_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(TINYSOL_FLUTE_FULL_MIX_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(TINYSOL_FLUTE_FULL_MIX_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=40 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(TINYSOL_FLUTE_FULL_MIX_OUTPUT)"
	@cat "$(TINYSOL_FLUTE_FULL_MIX_OUTPUT)"

find-tinysol-flute-full-mix-row-confusion-patterns: $(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status row_confusion --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

find-tinysol-sax-full-mix-first-row-confusion-patterns: $(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status first_row_confusion --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

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

analyze-iowa-orchestra-full-exact-midi-misses: scripts/analyze_exact_midi_misses.py
	@test -f "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV); run make analyze-iowa-orchestra-full-attributes first"; exit 2; }
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

summarize-iowa-orchestra-full-attributes: $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV) scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)"

# Silent one-sample runtime trace for measured Iowa octave/error clusters.
inspect-iowa-orchestra-full-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(IOWA_ORCHESTRA_FULL_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set IOWA_ORCHESTRA_FULL_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)/manifest.tsv; prepare samples separately before inspecting"; exit 2; }
	@rm -f "$(IOWA_ORCHESTRA_FULL_DEBUG_ATTRIBUTE_TSV)"
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(IOWA_ORCHESTRA_FULL_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(IOWA_ORCHESTRA_FULL_DEBUG_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(IOWA_ORCHESTRA_FULL_DEBUG_ATTRIBUTE_TSV)" --sample-id "$(IOWA_ORCHESTRA_FULL_DEBUG_SAMPLE_ID)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)

download-idmt-bass-lines-samples: $(IDMT_BASS_LINES_ARCHIVE)

.PHONY: inspect-idmt-bass-tempo-metadata test-inspect-idmt-bass-tempo-metadata
inspect-idmt-bass-tempo-metadata: $(IDMT_BASS_LINES_ARCHIVE) scripts/inspect_idmt_bass_tempo_metadata.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_idmt_bass_tempo_metadata.py --archive "$(IDMT_BASS_LINES_ARCHIVE)" --output "$(IDMT_BASS_LINES_TEMPO_METADATA)"

test-inspect-idmt-bass-tempo-metadata: tests/test_inspect_idmt_bass_tempo_metadata.py scripts/inspect_idmt_bass_tempo_metadata.py
	$(PYTHON) tests/test_inspect_idmt_bass_tempo_metadata.py

$(IDMT_BASS_LINES_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(IDMT_BASS_LINES_SOURCE_DIR)"
	if [ ! -s "$(IDMT_BASS_LINES_ARCHIVE)" ] || ! $(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null 2>&1; then curl -fL -C - -o "$(IDMT_BASS_LINES_ARCHIVE)" "$(IDMT_BASS_LINES_URL)"; fi
	$(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null

prepare-idmt-bass-lines-samples: scripts/prepare_idmt_bass_lines_samples.py download-idmt-bass-lines-samples | $(BUILD_DIR)
	IDMT_BASS_LINES_ARCHIVE="$(IDMT_BASS_LINES_ARCHIVE)" IDMT_BASS_LINES_SAMPLE_DIR="$(IDMT_BASS_LINES_SAMPLE_DIR)" IDMT_BASS_LINES_SAMPLE_LIMIT="$(IDMT_BASS_LINES_SAMPLE_LIMIT)" IDMT_BASS_LINES_MIN_BASS="$(IDMT_BASS_LINES_MIN_BASS)" IDMT_BASS_LINES_EXPRESSIONS="$(IDMT_BASS_LINES_EXPRESSIONS)" IDMT_BASS_LINES_MIN_NOTE_DURATION="$(IDMT_BASS_LINES_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_idmt_bass_lines_samples.py --archive "$(IDMT_BASS_LINES_ARCHIVE)" --output "$(IDMT_BASS_LINES_SAMPLE_DIR)" --limit "$(IDMT_BASS_LINES_SAMPLE_LIMIT)" --min-samples "$(IDMT_BASS_LINES_MIN_BASS)" --expressions "$(IDMT_BASS_LINES_EXPRESSIONS)" --min-note-duration "$(IDMT_BASS_LINES_MIN_NOTE_DURATION)"

$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv: scripts/prepare_idmt_bass_lines_samples.py $(IDMT_BASS_LINES_ARCHIVE) | $(BUILD_DIR)
	+$(MAKE) prepare-idmt-bass-lines-samples
	@test -f "$(IDMT_BASS_LINES_SAMPLE_DIR)/manifest.tsv"
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
	@test -f "$(IDMT_GUITAR_SAMPLE_DIR)/manifest.tsv"
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

$(IDMT_GUITAR_ISOLATED_VISUAL_AUDIT): $(IDMT_GUITAR_ATTRIBUTE_TSV) scripts/summarize_isolated_guitar_visual.py | $(BUILD_DIR)
	$(PYTHON) scripts/summarize_isolated_guitar_visual.py "$(IDMT_GUITAR_ATTRIBUTE_TSV)" --label "IDMT Guitar" --output "$@"

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
	@test -f "$(TINYSOL_SAMPLE_DIR)/manifest.tsv"

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
	@test -f "$(VOCADITO_SAMPLE_DIR)/manifest.tsv"

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

.PHONY: download-dagstuhl-choirset validate-dagstuhl-choirset-archive extract-dagstuhl-choirset prepare-dagstuhl-choirset inspect-dagstuhl-choirset measure-dagstuhl-choirset export-dagstuhl-choirset-pattern-rows inspect-dagstuhl-cross-corpus-ownership find-dagstuhl-shared-vocal-ownership-patterns find-dagstuhl-choirset-ownership-patterns inspect-dagstuhl-vocal-evidence test-dagstuhl-choirset-20 inspect-dagstuhl-choirset-archive test-dagstuhl-choirset-archive test-extract-dagstuhl-choirset test-prepare-dagstuhl-choirset test-summarize-dagstuhl-choirset test-export-dagstuhl-choirset-pattern-rows test-inspect-vocal-ownership-cross-corpus test-inspect-dagstuhl-vocal-evidence download-choral-singing-dataset download-choral-singing-dataset-unlocked validate-choral-singing-dataset-archive extract-choral-singing-dataset prepare-choral-singing-dataset inspect-choral-singing-dataset measure-choral-singing-dataset summarize-choral-singing-dataset export-choral-singing-dataset-pattern-rows inspect-choral-singing-dataset-cross-corpus-ownership find-choral-singing-dataset-shared-vocal-ownership-patterns inspect-choral-singing-dataset-archive test-validate-choral-singing-dataset test-extract-choral-singing-dataset test-prepare-choral-singing-dataset test-inspect-choral-singing-dataset-archive download-esmuc-choir-dataset download-esmuc-choir-dataset-unlocked validate-esmuc-choir-dataset-archive extract-esmuc-choir-dataset clean-esmuc-choir-dataset-staging prepare-esmuc-choir-dataset inspect-esmuc-choir-dataset measure-esmuc-choir-dataset summarize-esmuc-choir-dataset export-esmuc-choir-dataset-pattern-rows inspect-esmuc-choir-dataset-cross-corpus-ownership find-esmuc-choir-dataset-shared-vocal-ownership-patterns inspect-esmuc-choir-dataset-archive test-validate-esmuc-choir-dataset test-extract-esmuc-choir-dataset test-prepare-esmuc-choir-dataset test-inspect-esmuc-choir-dataset-archive download-mir1k-dataset download-mir1k-dataset-unlocked validate-mir1k-dataset-archive extract-mir1k-dataset clean-mir1k-dataset-staging prepare-mir1k-vocal-mix-samples measure-mir1k-vocal-mix inspect-mir1k-vocal-mix-measurement inspect-mir1k-dataset-archive inspect-mir1k-dataset-download test-validate-mir1k-dataset test-extract-mir1k-dataset test-prepare-mir1k-vocal-mix-samples test-inspect-mir1k-dataset-archive test-inspect-mir1k-download

download-dagstuhl-choirset: configure-instrument-sample-store $(DAGSTUHL_CHOIRSET_ARCHIVE) validate-dagstuhl-choirset-archive

download-choral-singing-dataset: scripts/run_with_lock.sh
	+$(SHELL) scripts/run_with_lock.sh "$(CHORAL_SINGING_DATASET_DOWNLOAD_LOCK_DIR)" -- "$(MAKE)" download-choral-singing-dataset-unlocked

download-choral-singing-dataset-unlocked: configure-instrument-sample-store $(CHORAL_SINGING_DATASET_ARCHIVE) validate-choral-singing-dataset-archive

download-esmuc-choir-dataset: scripts/run_with_lock.sh
	+$(SHELL) scripts/run_with_lock.sh "$(ESMUC_CHOIR_DATASET_DOWNLOAD_LOCK_DIR)" -- "$(MAKE)" download-esmuc-choir-dataset-unlocked

download-esmuc-choir-dataset-unlocked: configure-instrument-sample-store $(ESMUC_CHOIR_DATASET_ARCHIVE) validate-esmuc-choir-dataset-archive

download-mir1k-dataset: scripts/run_with_lock.sh
	+$(SHELL) scripts/run_with_lock.sh "$(MIR1K_DATASET_DOWNLOAD_LOCK_DIR)" -- "$(MAKE)" download-mir1k-dataset-unlocked

download-mir1k-dataset-unlocked: configure-instrument-sample-store $(MIR1K_DATASET_ARCHIVE) validate-mir1k-dataset-archive

validate-mir1k-dataset-archive: $(MIR1K_DATASET_ARCHIVE) scripts/validate_mir1k_dataset.py
	$(PYTHON) scripts/validate_mir1k_dataset.py --archive "$(MIR1K_DATASET_ARCHIVE)" --expected-md5 "$(MIR1K_DATASET_ARCHIVE_MD5)"

extract-mir1k-dataset: validate-mir1k-dataset-archive scripts/extract_mir1k_dataset.py
	$(PYTHON) scripts/extract_mir1k_dataset.py --archive "$(MIR1K_DATASET_ARCHIVE)" --output "$(MIR1K_DATASET_EXTRACT_DIR)"

clean-mir1k-dataset-staging: scripts/extract_mir1k_dataset.py
	$(PYTHON) scripts/extract_mir1k_dataset.py --archive "$(MIR1K_DATASET_ARCHIVE)" --output "$(MIR1K_DATASET_EXTRACT_DIR)" --discard-stale-staging

prepare-mir1k-vocal-mix-samples: extract-mir1k-dataset scripts/prepare_mir1k_vocal_mix_samples.py
	$(PYTHON) scripts/prepare_mir1k_vocal_mix_samples.py --root "$(MIR1K_DATASET_EXTRACT_DIR)" --output "$(MIR1K_DATASET_SAMPLE_DIR)" --limit "$(MIR1K_DATASET_SAMPLE_LIMIT)" --minimum-samples "$(MIR1K_DATASET_MIN_SAMPLES)"

measure-mir1k-vocal-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-mir1k-vocal-mix-samples scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_mir1k_vocal_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(MIR1K_DATASET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(MIR1K_DATASET_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_real_note_samples > "$(MIR1K_DATASET_MEASUREMENT_OUTPUT)"

inspect-mir1k-vocal-mix-measurement: scripts/inspect_mir1k_measurement.py
	$(PYTHON) scripts/inspect_mir1k_measurement.py --measurement "$(MIR1K_DATASET_MEASUREMENT_OUTPUT)" --attributes "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"

inspect-mir1k-dataset-archive: validate-mir1k-dataset-archive scripts/inspect_mir1k_dataset_archive.py
	$(PYTHON) scripts/inspect_mir1k_dataset_archive.py --archive "$(MIR1K_DATASET_ARCHIVE)" $(MIR1K_DATASET_INSPECT_ARGS)

inspect-mir1k-dataset-download: scripts/inspect_mir1k_download.py
	$(PYTHON) scripts/inspect_mir1k_download.py --archive "$(MIR1K_DATASET_ARCHIVE)" --lock-dir "$(MIR1K_DATASET_DOWNLOAD_LOCK_DIR)"

validate-esmuc-choir-dataset-archive: $(ESMUC_CHOIR_DATASET_ARCHIVE) scripts/validate_esmuc_choir_dataset.py
	$(PYTHON) scripts/validate_esmuc_choir_dataset.py --archive "$(ESMUC_CHOIR_DATASET_ARCHIVE)" --expected-md5 "$(ESMUC_CHOIR_DATASET_ARCHIVE_MD5)"

extract-esmuc-choir-dataset: validate-esmuc-choir-dataset-archive scripts/extract_esmuc_choir_dataset.py
	$(PYTHON) scripts/extract_esmuc_choir_dataset.py --archive "$(ESMUC_CHOIR_DATASET_ARCHIVE)" --output "$(ESMUC_CHOIR_DATASET_EXTRACT_DIR)"

clean-esmuc-choir-dataset-staging: scripts/extract_esmuc_choir_dataset.py
	$(PYTHON) scripts/extract_esmuc_choir_dataset.py --archive "$(ESMUC_CHOIR_DATASET_ARCHIVE)" --output "$(ESMUC_CHOIR_DATASET_EXTRACT_DIR)" --discard-stale-staging

prepare-esmuc-choir-dataset: extract-esmuc-choir-dataset scripts/prepare_esmuc_choir_dataset_manifest.py
	$(PYTHON) scripts/prepare_esmuc_choir_dataset_manifest.py --root "$(ESMUC_CHOIR_DATASET_EXTRACT_DIR)" --output "$(ESMUC_CHOIR_DATASET_PREPARED_DIR)" --minimum-pieces 19

inspect-esmuc-choir-dataset: prepare-esmuc-choir-dataset
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(ESMUC_CHOIR_DATASET_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES=19 $(MAKE) -s inspect-real-prepared-multitrack

measure-esmuc-choir-dataset: $(BUILD_DIR)/analyzer_musicnet prepare-esmuc-choir-dataset tests/prepare_prepared_multitrack_musicnet_fixture.py scripts/summarize_dagstuhl_choirset_measurement.py | $(BUILD_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(ESMUC_CHOIR_DATASET_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES=19 MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES=19 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py "$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)"
	MUSIC_ANALYZER_MUSICNET_ROOT="$(ESMUC_CHOIR_DATASET_MUSICNET_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=19 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) summarize-esmuc-choir-dataset

summarize-esmuc-choir-dataset: $(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT) prepare-esmuc-choir-dataset scripts/summarize_dagstuhl_choirset_measurement.py
	$(PYTHON) scripts/summarize_dagstuhl_choirset_measurement.py --corpus-label ESMUC --attributes "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" --manifest "$(ESMUC_CHOIR_DATASET_PREPARED_DIR)/manifest.json" --output "$(ESMUC_CHOIR_DATASET_MEASUREMENT_OUTPUT)"

export-esmuc-choir-dataset-pattern-rows: $(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT) prepare-esmuc-choir-dataset scripts/export_dagstuhl_choirset_pattern_rows.py | $(BUILD_DIR)
	$(PYTHON) scripts/export_dagstuhl_choirset_pattern_rows.py --attributes "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" --manifest "$(ESMUC_CHOIR_DATASET_PREPARED_DIR)/manifest.json" --output "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)"

.PHONY: inspect-high-vocal-octave-evidence-cached test-inspect-high-vocal-octave-evidence inspect-polyphonic-candidate-capacity test-inspect-polyphonic-candidate-capacity inspect-harmonic-product-octave-evidence-cached test-inspect-harmonic-product-octave-evidence

inspect-polyphonic-candidate-capacity: $(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT)
	@cat "$(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT)"

$(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT): scripts/inspect_polyphonic_candidate_capacity.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached polyphonic capacity input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/inspect_polyphonic_candidate_capacity.py "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$@"

inspect-harmonic-product-octave-evidence-cached: scripts/inspect_harmonic_product_octave_evidence.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached harmonic-product audit input: $$path"; exit 2; }; done
	@$(PYTHON) scripts/inspect_harmonic_product_octave_evidence.py --input "DCS=$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" --output "$(HARMONIC_PRODUCT_OCTAVE_AUDIT)"

test-inspect-harmonic-product-octave-evidence: tests/test_inspect_harmonic_product_octave_evidence.py scripts/inspect_harmonic_product_octave_evidence.py
	$(PYTHON) tests/test_inspect_harmonic_product_octave_evidence.py

test-inspect-polyphonic-candidate-capacity: tests/test_inspect_polyphonic_candidate_capacity.py scripts/inspect_polyphonic_candidate_capacity.py
	$(PYTHON) tests/test_inspect_polyphonic_candidate_capacity.py

inspect-high-vocal-octave-evidence-cached: scripts/inspect_high_vocal_octave_evidence.py
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv"; do test -s "$$path" || { printf '%s\n' "missing cached high-vocal audit input: $$path"; exit 2; }; done
	$(PYTHON) scripts/inspect_high_vocal_octave_evidence.py --candidate "DCS=$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --candidate "CSD=$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --candidate "ESMUC=$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --protected "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --output "$(HIGH_VOCAL_OCTAVE_AUDIT)"
	@cat "$(HIGH_VOCAL_OCTAVE_AUDIT)"

test-inspect-high-vocal-octave-evidence: tests/test_inspect_high_vocal_octave_evidence.py scripts/inspect_high_vocal_octave_evidence.py
	$(PYTHON) tests/test_inspect_high_vocal_octave_evidence.py

.PHONY: find-high-vocal-ownership-patterns-cached

find-high-vocal-ownership-patterns-cached: scripts/find_real_note_attribute_patterns.py
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv"; do test -s "$$path" || { printf '%s\n' "missing cached high-vocal pattern input: $$path"; exit 2; }; done
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --extra-candidate-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --bucket "ownership_miss:vocals/*->*" --filter-condition "debug_midi>=77" --filter-condition "debug_midi<=78" --filter-condition "debug_owner=piano" --exclude-field expected_row_score --exclude-field first_row_score --exclude-field visual_first_row_score --exclude-field strongest_row_score --exclude-field visual_strongest_row_score --exclude-field expected_first_score_ratio --exclude-field expected_strongest_score_ratio --exclude-field expected_visual_first_score_ratio --exclude-field expected_visual_strongest_score_ratio --exclude-field first_expected_score_margin --exclude-field strongest_expected_score_margin --exclude-field visual_first_expected_score_margin --exclude-field visual_strongest_expected_score_margin --exclude-field debug_delta --exclude-field debug_abs_delta --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 1 --show-near-misses 8 --protected-scope all --profile-fields 8

.PHONY: audit-high-soprano-vocal-mirror-cached

# Compare the current broad F5/F#5 Keyboard-to-Vocal display mirror against the
# narrower cross-choir candidate before changing the live classification rule.
audit-high-soprano-vocal-mirror-cached: scripts/measure_real_note_attribute_rule.py
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached high-soprano mirror input: $$path"; exit 2; }; done
	@tmp="$(HIGH_SOPRANO_VOCAL_MIRROR_AUDIT).tmp"; { \
		printf '%s\n' 'current broad mirror'; \
		$(PYTHON) scripts/measure_real_note_attribute_rule.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --condition "debug_owner=piano" --condition "debug_midi>=77" --condition "debug_midi<=78" --condition "noise>=0.024" --condition "partial2>=0.114" --compare-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --compare-path "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --compare-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --compare-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" --group-by family --group-by status --group-by first_row --examples 4; \
		printf '%s\n' 'narrow cross-choir candidate'; \
		$(PYTHON) scripts/measure_real_note_attribute_rule.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --condition "debug_owner=piano" --condition "debug_midi>=77" --condition "debug_midi<=78" --condition "adjacent_upper_ratio>=0.032" --condition "noise>=0.122" --condition "pitch_confidence<=0.814" --compare-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --compare-path "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --compare-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --compare-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" --group-by family --group-by status --group-by first_row --examples 4; \
	} > "$$tmp" && mv "$$tmp" "$(HIGH_SOPRANO_VOCAL_MIRROR_AUDIT)"
	@cat "$(HIGH_SOPRANO_VOCAL_MIRROR_AUDIT)"

inspect-esmuc-choir-dataset-cross-corpus-ownership: export-esmuc-choir-dataset-pattern-rows scripts/inspect_vocal_ownership_cross_corpus.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached cross-corpus vocal input: $$path"; exit 2; }; done
	$(PYTHON) scripts/inspect_vocal_ownership_cross_corpus.py --input "DCS=$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --input "Vocadito=$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --input "VocalSet=$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --input "MIR1K=$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" $(SCMS_VOCAL_CROSS_CORPUS_ARG) --output "$(ESMUC_CHOIR_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"
	@cat "$(ESMUC_CHOIR_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"

inspect-vocal-exact-note-cross-corpus: export-esmuc-choir-dataset-pattern-rows scripts/inspect_vocal_exact_note_cross_corpus.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached cross-corpus vocal input: $$path"; exit 2; }; done
	$(PYTHON) scripts/inspect_vocal_exact_note_cross_corpus.py --input "DCS=$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --input "Vocadito=$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --input "VocalSet=$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --input "MIR1K=$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" $(SCMS_VOCAL_CROSS_CORPUS_ARG) --output "$(VOCAL_EXACT_NOTE_CROSS_CORPUS_OUTPUT)"
	@cat "$(VOCAL_EXACT_NOTE_CROSS_CORPUS_OUTPUT)"

find-esmuc-choir-dataset-shared-vocal-ownership-patterns: $(ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)
	@cat "$(ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)"

.PHONY: find-esmuc-choir-dataset-shared-vocal-ownership-patterns-cached

find-esmuc-choir-dataset-shared-vocal-ownership-patterns-cached: scripts/find_real_note_attribute_patterns.py
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached shared-vocal pattern input: $$path"; exit 2; }; done
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --extra-candidate-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --bucket "ownership_miss:vocals/*->*" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) $(ESMUC_SHARED_VOCAL_FILTER_ARGS) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 3 --max-negative-samples 0 --max-conditions "$(ESMUC_SHARED_VOCAL_MAX_CONDITIONS)" --show-examples 1 --show-near-misses 8 --protected-scope all --profile-fields 6

$(ESMUC_CHOIR_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT): Makefile export-esmuc-choir-dataset-pattern-rows $(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT) $(CHORAL_SINGING_DATASET_PATTERN_OUTPUT) $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) $(MIR1K_DATASET_ATTRIBUTE_OUTPUT) scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached shared-vocal pattern input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --extra-candidate-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(ESMUC_CHOIR_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(MIR1K_DATASET_ATTRIBUTE_OUTPUT)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --bucket "ownership_miss:vocals/*->*" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) $(ESMUC_SHARED_VOCAL_FILTER_ARGS) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 3 --max-negative-samples 0 --max-conditions "$(ESMUC_SHARED_VOCAL_MAX_CONDITIONS)" --show-examples 1 --show-near-misses 8 --protected-scope all --profile-fields 6 > "$$tmp" 2>&1; status="$$?"; mv "$$tmp" "$@"; exit "$$status"

inspect-esmuc-choir-dataset-archive: validate-esmuc-choir-dataset-archive scripts/inspect_esmuc_choir_dataset_archive.py
	$(PYTHON) scripts/inspect_esmuc_choir_dataset_archive.py --archive "$(ESMUC_CHOIR_DATASET_ARCHIVE)" $(ESMUC_CHOIR_DATASET_INSPECT_ARGS)

validate-choral-singing-dataset-archive: $(CHORAL_SINGING_DATASET_ARCHIVE) scripts/validate_choral_singing_dataset.py
	$(PYTHON) scripts/validate_choral_singing_dataset.py --archive "$(CHORAL_SINGING_DATASET_ARCHIVE)" --expected-md5 "$(CHORAL_SINGING_DATASET_ARCHIVE_MD5)"

extract-choral-singing-dataset: validate-choral-singing-dataset-archive scripts/extract_choral_singing_dataset.py
	$(PYTHON) scripts/extract_choral_singing_dataset.py --archive "$(CHORAL_SINGING_DATASET_ARCHIVE)" --output "$(CHORAL_SINGING_DATASET_EXTRACT_DIR)"

prepare-choral-singing-dataset: extract-choral-singing-dataset scripts/prepare_choral_singing_dataset_manifest.py
	$(PYTHON) scripts/prepare_choral_singing_dataset_manifest.py --root "$(CHORAL_SINGING_DATASET_EXTRACT_DIR)/ChoralSingingDataset" --output "$(CHORAL_SINGING_DATASET_PREPARED_DIR)" --minimum-pieces 12

inspect-choral-singing-dataset: prepare-choral-singing-dataset
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(CHORAL_SINGING_DATASET_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES=12 $(MAKE) -s inspect-real-prepared-multitrack

measure-choral-singing-dataset: $(BUILD_DIR)/analyzer_musicnet prepare-choral-singing-dataset tests/prepare_prepared_multitrack_musicnet_fixture.py scripts/summarize_dagstuhl_choirset_measurement.py | $(BUILD_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(CHORAL_SINGING_DATASET_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES=12 MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES=12 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py "$(CHORAL_SINGING_DATASET_MUSICNET_DIR)"
	MUSIC_ANALYZER_MUSICNET_ROOT="$(CHORAL_SINGING_DATASET_MUSICNET_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=12 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) summarize-choral-singing-dataset

summarize-choral-singing-dataset: $(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT) prepare-choral-singing-dataset scripts/summarize_dagstuhl_choirset_measurement.py
	$(PYTHON) scripts/summarize_dagstuhl_choirset_measurement.py --corpus-label CSD --attributes "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --manifest "$(CHORAL_SINGING_DATASET_PREPARED_DIR)/manifest.json" --output "$(CHORAL_SINGING_DATASET_MEASUREMENT_OUTPUT)"

export-choral-singing-dataset-pattern-rows: $(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT) prepare-choral-singing-dataset scripts/export_dagstuhl_choirset_pattern_rows.py | $(BUILD_DIR)
	$(PYTHON) scripts/export_dagstuhl_choirset_pattern_rows.py --attributes "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --manifest "$(CHORAL_SINGING_DATASET_PREPARED_DIR)/manifest.json" --output "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)"

inspect-choral-singing-dataset-cross-corpus-ownership: export-choral-singing-dataset-pattern-rows scripts/inspect_vocal_ownership_cross_corpus.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached cross-corpus vocal input: $$path"; exit 2; }; done
	$(PYTHON) scripts/inspect_vocal_ownership_cross_corpus.py --input "DCS=$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --input "Vocadito=$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --input "VocalSet=$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --output "$(CHORAL_SINGING_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"
	@cat "$(CHORAL_SINGING_DATASET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"

find-choral-singing-dataset-shared-vocal-ownership-patterns: $(CHORAL_SINGING_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)
	@cat "$(CHORAL_SINGING_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT)"

$(CHORAL_SINGING_DATASET_SHARED_OWNERSHIP_PATTERN_REPORT): Makefile export-choral-singing-dataset-pattern-rows $(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT) $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached shared-vocal pattern input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --extra-candidate-path "$(CHORAL_SINGING_DATASET_PATTERN_OUTPUT)" --extra-candidate-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --bucket "ownership_miss:vocals/*->*" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 2 --show-examples 1 --show-near-misses 8 --protected-scope all --profile-fields 6 > "$$tmp" 2>&1; status="$$?"; mv "$$tmp" "$@"; exit "$$status"

inspect-choral-singing-dataset-archive: $(CHORAL_SINGING_DATASET_INSPECTION_OUTPUT)
	@cat "$(CHORAL_SINGING_DATASET_INSPECTION_OUTPUT)"

$(CHORAL_SINGING_DATASET_INSPECTION_OUTPUT): validate-choral-singing-dataset-archive scripts/inspect_choral_singing_dataset_archive.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_choral_singing_dataset_archive.py --archive "$(CHORAL_SINGING_DATASET_ARCHIVE)" $(CHORAL_SINGING_DATASET_INSPECT_ARGS) > "$@"

validate-dagstuhl-choirset-archive: $(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT)
	@cat "$(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT)"

$(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT): $(DAGSTUHL_CHOIRSET_ARCHIVE) scripts/validate_dagstuhl_choirset.py | $(BUILD_DIR)
	$(PYTHON) scripts/validate_dagstuhl_choirset.py --archive "$(DAGSTUHL_CHOIRSET_ARCHIVE)" --expected-md5 "$(DAGSTUHL_CHOIRSET_ARCHIVE_MD5)" > "$@"

extract-dagstuhl-choirset: validate-dagstuhl-choirset-archive scripts/extract_dagstuhl_choirset.py
	$(PYTHON) scripts/extract_dagstuhl_choirset.py --archive "$(DAGSTUHL_CHOIRSET_ARCHIVE)" --output "$(DAGSTUHL_CHOIRSET_EXTRACT_DIR)"

prepare-dagstuhl-choirset: extract-dagstuhl-choirset scripts/prepare_dagstuhl_choirset_manifest.py scripts/run_with_lock.sh
	$(SHELL) scripts/run_with_lock.sh "$(DAGSTUHL_CHOIRSET_PREPARE_LOCK_DIR)" -- $(PYTHON) scripts/prepare_dagstuhl_choirset_manifest.py --root "$(DAGSTUHL_CHOIRSET_EXTRACT_DIR)/DagstuhlChoirSet" --output "$(DAGSTUHL_CHOIRSET_PREPARED_DIR)"

inspect-dagstuhl-choirset: prepare-dagstuhl-choirset
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(DAGSTUHL_CHOIRSET_PREPARED_DIR)" $(MAKE) -s inspect-real-prepared-multitrack

measure-dagstuhl-choirset: $(BUILD_DIR)/analyzer_musicnet prepare-dagstuhl-choirset tests/prepare_prepared_multitrack_musicnet_fixture.py scripts/summarize_dagstuhl_choirset_measurement.py | $(BUILD_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(DAGSTUHL_CHOIRSET_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES=20 MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES=20 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py "$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)"
	MUSIC_ANALYZER_MUSICNET_ROOT="$(DAGSTUHL_CHOIRSET_MUSICNET_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_musicnet
	$(PYTHON) scripts/summarize_dagstuhl_choirset_measurement.py --attributes "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --manifest "$(DAGSTUHL_CHOIRSET_PREPARED_DIR)/manifest.json" --output "$(DAGSTUHL_CHOIRSET_MEASUREMENT_OUTPUT)"

test-dagstuhl-choirset-20: measure-dagstuhl-choirset

export-dagstuhl-choirset-pattern-rows: measure-dagstuhl-choirset scripts/export_dagstuhl_choirset_pattern_rows.py | $(BUILD_DIR)
	$(PYTHON) scripts/export_dagstuhl_choirset_pattern_rows.py --attributes "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --manifest "$(DAGSTUHL_CHOIRSET_PREPARED_DIR)/manifest.json" --output "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)"

inspect-dagstuhl-cross-corpus-ownership: export-dagstuhl-choirset-pattern-rows scripts/inspect_vocal_ownership_cross_corpus.py | $(BUILD_DIR)
	@for path in "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached cross-corpus vocal input: $$path"; exit 2; }; done
	$(PYTHON) scripts/inspect_vocal_ownership_cross_corpus.py --input "DCS=$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --input "Vocadito=$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --input "VocalSet=$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --output "$(DAGSTUHL_CHOIRSET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"
	@cat "$(DAGSTUHL_CHOIRSET_CROSS_CORPUS_OWNERSHIP_OUTPUT)"

find-dagstuhl-shared-vocal-ownership-patterns: $(DAGSTUHL_CHOIRSET_SHARED_OWNERSHIP_PATTERN_REPORT)
	@cat "$(DAGSTUHL_CHOIRSET_SHARED_OWNERSHIP_PATTERN_REPORT)"

$(DAGSTUHL_CHOIRSET_SHARED_OWNERSHIP_PATTERN_REPORT): Makefile export-dagstuhl-choirset-pattern-rows $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(VOCALSET_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached shared-vocal pattern input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" --extra-candidate-path "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --bucket "ownership_miss:vocals/*->*" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 2 --show-examples 1 --show-near-misses 8 --protected-scope all --profile-fields 6 > "$$tmp" 2>&1; status="$$?"; mv "$$tmp" "$@"; exit "$$status"

find-dagstuhl-choirset-ownership-patterns: $(DAGSTUHL_CHOIRSET_OWNERSHIP_PATTERN_REPORT)
	@cat "$(DAGSTUHL_CHOIRSET_OWNERSHIP_PATTERN_REPORT)"

$(DAGSTUHL_CHOIRSET_OWNERSHIP_PATTERN_REPORT): export-dagstuhl-choirset-pattern-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in $(DAGSTUHL_CHOIRSET_PATTERN_EXTRA_PROTECTED_PATHS); do test -s "$$path" || { printf '%s\n' "missing cached protected DCS pattern input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(DAGSTUHL_CHOIRSET_PATTERN_OUTPUT)" $(DAGSTUHL_CHOIRSET_PATTERN_EXTRA_PROTECTED_ARGS) --bucket "ownership_miss:vocals/*->*" --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_BROAD_VOCAL_PATTERN_ARGS)) > "$$tmp" 2>&1; status="$$?"; mv "$$tmp" "$@"; exit "$$status"

inspect-dagstuhl-vocal-evidence: measure-dagstuhl-choirset scripts/inspect_dagstuhl_vocal_evidence.py
	$(PYTHON) scripts/inspect_dagstuhl_vocal_evidence.py --attributes "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)"

inspect-dagstuhl-choirset-archive: $(DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT)
	@cat "$(DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT)"

$(DAGSTUHL_CHOIRSET_INSPECTION_OUTPUT): $(DAGSTUHL_CHOIRSET_VALIDATION_OUTPUT) scripts/inspect_dagstuhl_choirset_archive.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_dagstuhl_choirset_archive.py --archive "$(DAGSTUHL_CHOIRSET_ARCHIVE)" > "$@"

test-dagstuhl-choirset-archive: tests/test_validate_dagstuhl_choirset.py scripts/validate_dagstuhl_choirset.py
	$(PYTHON) tests/test_validate_dagstuhl_choirset.py

test-validate-choral-singing-dataset: tests/test_validate_choral_singing_dataset.py scripts/validate_choral_singing_dataset.py
	$(PYTHON) tests/test_validate_choral_singing_dataset.py

test-validate-esmuc-choir-dataset: tests/test_validate_esmuc_choir_dataset.py scripts/validate_esmuc_choir_dataset.py
	$(PYTHON) tests/test_validate_esmuc_choir_dataset.py

test-extract-esmuc-choir-dataset: tests/test_extract_esmuc_choir_dataset.py scripts/extract_esmuc_choir_dataset.py scripts/validate_esmuc_choir_dataset.py
	$(PYTHON) tests/test_extract_esmuc_choir_dataset.py

test-prepare-esmuc-choir-dataset: tests/test_prepare_esmuc_choir_dataset_manifest.py scripts/prepare_esmuc_choir_dataset_manifest.py
	$(PYTHON) tests/test_prepare_esmuc_choir_dataset_manifest.py

test-inspect-esmuc-choir-dataset-archive: tests/test_inspect_esmuc_choir_dataset_archive.py scripts/inspect_esmuc_choir_dataset_archive.py
	$(PYTHON) tests/test_inspect_esmuc_choir_dataset_archive.py

test-validate-mir1k-dataset: tests/test_validate_mir1k_dataset.py scripts/validate_mir1k_dataset.py
	$(PYTHON) tests/test_validate_mir1k_dataset.py

test-validate-scms-dataset: tests/test_validate_scms_dataset.py scripts/validate_scms_dataset.py
	$(PYTHON) tests/test_validate_scms_dataset.py

test-inspect-scms-dataset: tests/test_inspect_scms_dataset_archive.py scripts/inspect_scms_dataset_archive.py
	$(PYTHON) tests/test_inspect_scms_dataset_archive.py

test-extract-scms-dataset: tests/test_extract_scms_dataset.py scripts/extract_scms_dataset.py
	$(PYTHON) tests/test_extract_scms_dataset.py

test-prepare-scms-vocal-mix-samples: tests/test_prepare_scms_vocal_mix_samples.py scripts/prepare_scms_vocal_mix_samples.py
	$(PYTHON) tests/test_prepare_scms_vocal_mix_samples.py

test-start-scms-dataset-download: tests/test_start_scms_dataset_download.py scripts/start_scms_dataset_download.sh
	$(PYTHON) tests/test_start_scms_dataset_download.py

test-start-scms-vocal-measurement: tests/test_start_scms_vocal_measurement.py scripts/start_scms_vocal_measurement.sh
	$(PYTHON) tests/test_start_scms_vocal_measurement.py

test-extract-mir1k-dataset: tests/test_extract_mir1k_dataset.py scripts/extract_mir1k_dataset.py scripts/validate_mir1k_dataset.py
	$(PYTHON) tests/test_extract_mir1k_dataset.py

test-prepare-mir1k-vocal-mix-samples: tests/test_prepare_mir1k_vocal_mix_samples.py scripts/prepare_mir1k_vocal_mix_samples.py
	$(PYTHON) tests/test_prepare_mir1k_vocal_mix_samples.py

test-inspect-mir1k-dataset-archive: tests/test_inspect_mir1k_dataset_archive.py scripts/inspect_mir1k_dataset_archive.py
	$(PYTHON) tests/test_inspect_mir1k_dataset_archive.py

test-inspect-mir1k-download: tests/test_inspect_mir1k_download.py scripts/inspect_mir1k_download.py
	$(PYTHON) tests/test_inspect_mir1k_download.py

test-extract-choral-singing-dataset: tests/test_extract_choral_singing_dataset.py scripts/extract_choral_singing_dataset.py scripts/validate_choral_singing_dataset.py
	$(PYTHON) tests/test_extract_choral_singing_dataset.py

test-prepare-choral-singing-dataset: tests/test_prepare_choral_singing_dataset_manifest.py scripts/prepare_choral_singing_dataset_manifest.py
	$(PYTHON) tests/test_prepare_choral_singing_dataset_manifest.py

test-inspect-choral-singing-dataset-archive: tests/test_inspect_choral_singing_dataset_archive.py scripts/inspect_choral_singing_dataset_archive.py
	$(PYTHON) tests/test_inspect_choral_singing_dataset_archive.py

test-extract-dagstuhl-choirset: tests/test_extract_dagstuhl_choirset.py scripts/extract_dagstuhl_choirset.py scripts/validate_dagstuhl_choirset.py
	$(PYTHON) tests/test_extract_dagstuhl_choirset.py

test-prepare-dagstuhl-choirset: tests/test_prepare_dagstuhl_choirset_manifest.py scripts/prepare_dagstuhl_choirset_manifest.py
	$(PYTHON) tests/test_prepare_dagstuhl_choirset_manifest.py

test-summarize-dagstuhl-choirset: tests/test_summarize_dagstuhl_choirset_measurement.py scripts/summarize_dagstuhl_choirset_measurement.py
	$(PYTHON) tests/test_summarize_dagstuhl_choirset_measurement.py

test-export-dagstuhl-choirset-pattern-rows: tests/test_export_dagstuhl_choirset_pattern_rows.py scripts/export_dagstuhl_choirset_pattern_rows.py
	$(PYTHON) tests/test_export_dagstuhl_choirset_pattern_rows.py

test-inspect-vocal-ownership-cross-corpus: tests/test_inspect_vocal_ownership_cross_corpus.py scripts/inspect_vocal_ownership_cross_corpus.py
	$(PYTHON) tests/test_inspect_vocal_ownership_cross_corpus.py

test-inspect-vocal-exact-note-cross-corpus: tests/test_inspect_vocal_exact_note_cross_corpus.py scripts/inspect_vocal_exact_note_cross_corpus.py
	$(PYTHON) tests/test_inspect_vocal_exact_note_cross_corpus.py

.PHONY: inspect-vocal-exact-note-cross-corpus test-inspect-vocal-exact-note-cross-corpus

test-inspect-dagstuhl-vocal-evidence: tests/test_inspect_dagstuhl_vocal_evidence.py scripts/inspect_dagstuhl_vocal_evidence.py
	$(PYTHON) tests/test_inspect_dagstuhl_vocal_evidence.py

$(DAGSTUHL_CHOIRSET_ARCHIVE): scripts/validate_dagstuhl_choirset.py
	mkdir -p "$(DAGSTUHL_CHOIRSET_SOURCE_DIR)"
	if [ -s "$@" ] && ! $(PYTHON) scripts/validate_dagstuhl_choirset.py --archive "$@" --expected-md5 "$(DAGSTUHL_CHOIRSET_ARCHIVE_MD5)" >/dev/null 2>&1; then mv -f "$@" "$@.part"; fi
	if [ ! -s "$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(DAGSTUHL_CHOIRSET_DOWNLOAD_CONNECTIONS)" --split="$(DAGSTUHL_CHOIRSET_DOWNLOAD_CONNECTIONS)" --min-split-size=8M --file-allocation=none --dir "$(DAGSTUHL_CHOIRSET_SOURCE_DIR)" --out "DagstuhlChoirSet.zip.part" "$(DAGSTUHL_CHOIRSET_ARCHIVE_URL)"; else $(CURL) -fL --continue-at - --output "$@.part" "$(DAGSTUHL_CHOIRSET_ARCHIVE_URL)"; fi; fi
	$(PYTHON) scripts/validate_dagstuhl_choirset.py --archive "$@.part" --expected-md5 "$(DAGSTUHL_CHOIRSET_ARCHIVE_MD5)"
	mv -f "$@.part" "$@"

$(CHORAL_SINGING_DATASET_ARCHIVE): scripts/validate_choral_singing_dataset.py
	mkdir -p "$(CHORAL_SINGING_DATASET_SOURCE_DIR)"
	if [ -s "$@" ] && ! $(PYTHON) scripts/validate_choral_singing_dataset.py --archive "$@" --expected-md5 "$(CHORAL_SINGING_DATASET_ARCHIVE_MD5)" >/dev/null 2>&1; then mv -f "$@" "$@.part"; fi
	if [ ! -s "$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(CHORAL_SINGING_DATASET_DOWNLOAD_CONNECTIONS)" --split="$(CHORAL_SINGING_DATASET_DOWNLOAD_CONNECTIONS)" --min-split-size=8M --file-allocation=none --dir "$(CHORAL_SINGING_DATASET_SOURCE_DIR)" --out "ChoralSingingDataset.zip.part" "$(CHORAL_SINGING_DATASET_ARCHIVE_URL)"; else $(CURL) -fL --continue-at - --output "$@.part" "$(CHORAL_SINGING_DATASET_ARCHIVE_URL)"; fi; fi
	if [ -s "$@.part" ]; then $(PYTHON) scripts/validate_choral_singing_dataset.py --archive "$@.part" --expected-md5 "$(CHORAL_SINGING_DATASET_ARCHIVE_MD5)"; mv -f "$@.part" "$@"; fi
	test -s "$@"

$(ESMUC_CHOIR_DATASET_ARCHIVE): scripts/validate_esmuc_choir_dataset.py
	mkdir -p "$(ESMUC_CHOIR_DATASET_SOURCE_DIR)"
	if [ -s "$@" ] && ! $(PYTHON) scripts/validate_esmuc_choir_dataset.py --archive "$@" --expected-md5 "$(ESMUC_CHOIR_DATASET_ARCHIVE_MD5)" >/dev/null 2>&1; then mv -f "$@" "$@.part"; fi
	if [ ! -s "$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(ESMUC_CHOIR_DATASET_DOWNLOAD_CONNECTIONS)" --split="$(ESMUC_CHOIR_DATASET_DOWNLOAD_CONNECTIONS)" --min-split-size=8M --file-allocation=none --dir "$(ESMUC_CHOIR_DATASET_SOURCE_DIR)" --out "EsmucChoirDataset_v1.0.0.zip.part" "$(ESMUC_CHOIR_DATASET_ARCHIVE_URL)"; else $(CURL) -fL --continue-at - --output "$@.part" "$(ESMUC_CHOIR_DATASET_ARCHIVE_URL)"; fi; fi
	if [ -s "$@.part" ]; then $(PYTHON) scripts/validate_esmuc_choir_dataset.py --archive "$@.part" --expected-md5 "$(ESMUC_CHOIR_DATASET_ARCHIVE_MD5)"; mv -f "$@.part" "$@"; fi
	test -s "$@"

$(MIR1K_DATASET_ARCHIVE): scripts/validate_mir1k_dataset.py
	mkdir -p "$(MIR1K_DATASET_SOURCE_DIR)"
	if [ -s "$@" ] && ! $(PYTHON) scripts/validate_mir1k_dataset.py --archive "$@" --expected-md5 "$(MIR1K_DATASET_ARCHIVE_MD5)" >/dev/null 2>&1; then mv -f "$@" "$@.part"; fi
	if [ ! -s "$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(MIR1K_DATASET_DOWNLOAD_CONNECTIONS)" --split="$(MIR1K_DATASET_DOWNLOAD_CONNECTIONS)" --min-split-size=8M --file-allocation=none --dir "$(MIR1K_DATASET_SOURCE_DIR)" --out "mir1k_yourmt3_16k.tar.gz.part" "$(MIR1K_DATASET_ARCHIVE_URL)"; else $(CURL) -fL --continue-at - --output "$@.part" "$(MIR1K_DATASET_ARCHIVE_URL)"; fi; fi
	if [ -s "$@.part" ]; then $(PYTHON) scripts/validate_mir1k_dataset.py --archive "$@.part" --expected-md5 "$(MIR1K_DATASET_ARCHIVE_MD5)"; mv -f "$@.part" "$@"; fi
	test -s "$@"

.PHONY: download-scms-dataset start-scms-dataset-download scms-dataset-download-status start-scms-vocal-measurement start-scms-vocal-measurement-refresh scms-vocal-measurement-status validate-scms-dataset-archive inspect-scms-dataset extract-scms-dataset prepare-scms-vocal-mix-samples refresh-scms-vocal-mix-samples measure-scms-vocal-mix measure-scms-vocal-mix-refresh measure-scms-vocal-mix-sharded measure-scms-vocal-mix-shard-% inspect-scms-prepared-wav clean-scms-dataset-staging test-validate-scms-dataset test-inspect-scms-dataset test-start-scms-dataset-download test-start-scms-vocal-measurement test-extract-scms-dataset test-prepare-scms-vocal-mix-samples

download-scms-dataset: configure-instrument-sample-store $(SCMS_DATASET_ARCHIVE) validate-scms-dataset-archive

# A foreground terminal is intentionally not required for multi-hour public
# corpus transfers. The actual transfer remains this Make target, with aria2's
# own resume metadata and the checksum gate above; this launcher only records
# its detached PID and log in regenerable build state.
start-scms-dataset-download: configure-instrument-sample-store scripts/start_scms_dataset_download.sh | $(BUILD_DIR)
	$(SHELL) scripts/start_scms_dataset_download.sh --pid-file "$(SCMS_DATASET_DOWNLOAD_PID)" --log-file "$(SCMS_DATASET_DOWNLOAD_LOG)" --archive "$(SCMS_DATASET_ARCHIVE)" --archive-part "$(SCMS_DATASET_ARCHIVE).part" --workdir "$(CURDIR)"

scms-dataset-download-status:
	$(SHELL) scripts/start_scms_dataset_download.sh --status --pid-file "$(SCMS_DATASET_DOWNLOAD_PID)" --log-file "$(SCMS_DATASET_DOWNLOAD_LOG)" --archive "$(SCMS_DATASET_ARCHIVE)" --archive-part "$(SCMS_DATASET_ARCHIVE).part"

start-scms-vocal-measurement: scripts/start_scms_vocal_measurement.sh | $(BUILD_DIR)
	$(SHELL) scripts/start_scms_vocal_measurement.sh --pid-file "$(SCMS_VOCAL_MEASUREMENT_PID)" --log-file "$(SCMS_VOCAL_MEASUREMENT_LOG)" --workdir "$(CURDIR)" --limit "$(SCMS_DATASET_SAMPLE_LIMIT)" --minimum-samples "$(SCMS_DATASET_MIN_SAMPLES)"

start-scms-vocal-measurement-refresh: scripts/start_scms_vocal_measurement.sh | $(BUILD_DIR)
	$(SHELL) scripts/start_scms_vocal_measurement.sh --pid-file "$(SCMS_VOCAL_MEASUREMENT_PID)" --log-file "$(SCMS_VOCAL_MEASUREMENT_LOG)" --workdir "$(CURDIR)" --limit "$(SCMS_DATASET_SAMPLE_LIMIT)" --minimum-samples "$(SCMS_DATASET_MIN_SAMPLES)" --target measure-scms-vocal-mix-refresh

scms-vocal-measurement-status:
	$(SHELL) scripts/start_scms_vocal_measurement.sh --status --pid-file "$(SCMS_VOCAL_MEASUREMENT_PID)" --log-file "$(SCMS_VOCAL_MEASUREMENT_LOG)"

validate-scms-dataset-archive: $(SCMS_DATASET_VALIDATION_OUTPUT)
	@cat "$(SCMS_DATASET_VALIDATION_OUTPUT)"

$(SCMS_DATASET_VALIDATION_OUTPUT): $(SCMS_DATASET_ARCHIVE) scripts/validate_scms_dataset.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/validate_scms_dataset.py --archive "$(SCMS_DATASET_ARCHIVE)" --expected-md5 "$(SCMS_DATASET_ARCHIVE_MD5)" > "$$tmp" && mv "$$tmp" "$@"

inspect-scms-dataset: $(SCMS_DATASET_INSPECTION_OUTPUT)
	@cat "$(SCMS_DATASET_INSPECTION_OUTPUT)"

$(SCMS_DATASET_INSPECTION_OUTPUT): $(SCMS_DATASET_VALIDATION_OUTPUT) scripts/inspect_scms_dataset_archive.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_scms_dataset_archive.py --archive "$(SCMS_DATASET_ARCHIVE)" > "$@"

# Inspect before extraction: the archive inventory records the published
# audio/annotation layout used by the importer below.
extract-scms-dataset: $(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete

$(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete: $(SCMS_DATASET_INSPECTION_OUTPUT) scripts/extract_scms_dataset.py
	$(PYTHON) scripts/extract_scms_dataset.py --archive "$(SCMS_DATASET_ARCHIVE)" --output "$(SCMS_DATASET_EXTRACT_DIR)"

clean-scms-dataset-staging: scripts/extract_scms_dataset.py
	$(PYTHON) scripts/extract_scms_dataset.py --archive "$(SCMS_DATASET_ARCHIVE)" --output "$(SCMS_DATASET_EXTRACT_DIR)" --discard-stale-staging

prepare-scms-vocal-mix-samples: $(SCMS_DATASET_SAMPLE_DIR)/manifest.tsv

$(SCMS_DATASET_SAMPLE_DIR)/manifest.tsv: $(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete scripts/prepare_scms_vocal_mix_samples.py
	$(PYTHON) scripts/prepare_scms_vocal_mix_samples.py --root "$(SCMS_DATASET_EXTRACT_DIR)" --output "$(SCMS_DATASET_SAMPLE_DIR)" --limit "$(SCMS_DATASET_SAMPLE_LIMIT)" --minimum-samples "$(SCMS_DATASET_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

# Explicitly rebuild the manifest when the requested sample limits change.
# The normal target is cached for routine measurements; this refresh variant
# makes an evidence-expansion run visible and reproducible.
refresh-scms-vocal-mix-samples: $(SCMS_DATASET_EXTRACT_DIR)/.scms-extraction-complete scripts/prepare_scms_vocal_mix_samples.py
	$(PYTHON) scripts/prepare_scms_vocal_mix_samples.py --root "$(SCMS_DATASET_EXTRACT_DIR)" --output "$(SCMS_DATASET_SAMPLE_DIR)" --limit "$(SCMS_DATASET_SAMPLE_LIMIT)" --minimum-samples "$(SCMS_DATASET_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

measure-scms-vocal-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-scms-vocal-mix-samples scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_scms_vocal_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(SCMS_DATASET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(SCMS_DATASET_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(SCMS_DATASET_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_real_note_samples > "$(SCMS_DATASET_MEASUREMENT_OUTPUT)"

measure-scms-vocal-mix-refresh: refresh-scms-vocal-mix-samples
	+$(MAKE) measure-scms-vocal-mix

# Shards keep the 999-clip full-mix evidence pass inside short command windows.
# Each worker owns a part TSV; the merge is atomic and cannot interleave rows.
measure-scms-vocal-mix-sharded: $(SCMS_VOCAL_MIX_ATTRIBUTE_PARTS) | $(BUILD_DIR)
	@tmp="$(SCMS_DATASET_ATTRIBUTE_OUTPUT).$$$$.tmp"; awk 'FNR == 1 && NR != 1 { next } { print }' $(SCMS_VOCAL_MIX_ATTRIBUTE_PARTS) > "$$tmp" && mv "$$tmp" "$(SCMS_DATASET_ATTRIBUTE_OUTPUT)"

$(BUILD_DIR)/scms_vocal_mix_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_real_note_samples prepare-scms-vocal-mix-samples | $(BUILD_DIR)
	@shard="$*"; env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(SCMS_VOCAL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$$shard" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(SCMS_DATASET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/scms_vocal_mix_shard_$$shard.out"

inspect-scms-prepared-wav:
	$(PYTHON) scripts/inspect_wav_for_analyzer.py --wav "$(SCMS_DATASET_DEBUG_WAV)"

$(SCMS_DATASET_ARCHIVE): scripts/validate_scms_dataset.py
	mkdir -p "$(SCMS_DATASET_SOURCE_DIR)"
	if [ -s "$@" ] && ! $(PYTHON) scripts/validate_scms_dataset.py --archive "$@" --expected-md5 "$(SCMS_DATASET_ARCHIVE_MD5)" >/dev/null 2>&1; then mv -f "$@" "$@.part"; fi
	if [ ! -s "$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" --continue=true --allow-overwrite=true --auto-file-renaming=false --max-tries=5 --retry-wait=5 --max-connection-per-server="$(SCMS_DATASET_DOWNLOAD_CONNECTIONS)" --split="$(SCMS_DATASET_DOWNLOAD_CONNECTIONS)" --min-split-size=8M --file-allocation=none --dir "$(SCMS_DATASET_SOURCE_DIR)" --out "Saraga-Carnatic-Melody-Synth.zip.part" "$(SCMS_DATASET_ARCHIVE_URL)"; else $(CURL) -fL --continue-at - --output "$@.part" "$(SCMS_DATASET_ARCHIVE_URL)"; fi; fi
	if [ -s "$@.part" ]; then $(PYTHON) scripts/validate_scms_dataset.py --archive "$@.part" --expected-md5 "$(SCMS_DATASET_ARCHIVE_MD5)"; mv -f "$@.part" "$@"; fi
	test -s "$@"

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
	@test -f "$(VOCALSET_SAMPLE_DIR)/manifest.tsv"

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

.PHONY: analyze-vocalset-full-mix-attributes analyze-vocalset-expanded-full-mix-attributes find-vocalset-full-mix-row-confusion-patterns find-vocalset-full-mix-visual-row-confusion-patterns find-vocalset-full-mix-ownership-patterns find-vocalset-full-mix-broad-vocal-ownership-patterns find-vocalset-full-mix-cached-ownership-patterns inspect-vocalset-full-mix-debug-cached test-vocalset-clean-vowel-cached refresh-vocalset-clean-vowel-attributes-cached

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

# Mine an existing full-mix export without rebuilding or validating the large VocalSet archive.
find-vocalset-full-mix-cached-ownership-patterns: scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(VOCALSET_FULL_MIX_ATTRIBUTE_TSV)" $(VOCALSET_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

# Analyze one existing VocalSet fixture in memory and print its per-buffer
# candidate traits.  This deliberately has no audio-output step.
inspect-vocalset-full-mix-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(VOCALSET_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set VOCALSET_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(VOCALSET_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(VOCALSET_SAMPLE_DIR)/manifest.tsv; run make prepare-vocalset-samples first"; exit 2; }
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(VOCALSET_DEBUG_SAMPLE_ID)" $(BUILD_DIR)/analyzer_real_note_samples

# Regression gate for the measured C5 clean-vowel recovery. It reads the
# existing fixture only, so it neither prepares nor downloads VocalSet.
test-vocalset-clean-vowel-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -s "$(VOCALSET_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(VOCALSET_SAMPLE_DIR)/manifest.tsv; run make prepare-vocalset-samples first"; exit 2; }
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=0 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(VOCALSET_CLEAN_VOWEL_SAMPLE_ID)" $(BUILD_DIR)/analyzer_real_note_samples

# Persist the one-fixture C5 clean-vowel result without preparing or downloading
# VocalSet, so the accuracy dashboard is regenerated from current evidence.
refresh-vocalset-clean-vowel-attributes-cached: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_lock.sh | $(BUILD_DIR)
	@test -s "$(VOCALSET_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(VOCALSET_SAMPLE_DIR)/manifest.tsv; run make prepare-vocalset-samples first"; exit 2; }
	@rm -f "$(VOCALSET_CLEAN_VOWEL_ATTRIBUTE_TSV)"
	+$(SHELL) scripts/run_with_lock.sh "$(VOCALSET_ATTRIBUTE_LOCK_DIR)" -- env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=0 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(VOCALSET_CLEAN_VOWEL_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(VOCALSET_CLEAN_VOWEL_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples

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
ifneq ($(wildcard $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)
endif
ifneq ($(wildcard $(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(TINYSOL_FLUTE_FULL_MIX_ATTRIBUTE_TSV)
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
ifneq ($(wildcard $(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IOWA_PIANO_FULL_MIX_ATTRIBUTE_TSV)
else ifneq ($(wildcard $(IOWA_PIANO_SAMPLE_DIR)/manifest.tsv),)
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
ifneq ($(wildcard $(REAL_A2S_SAX_SCALE_FIXTURE_DIR)/manifest.tsv),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)
endif
ifneq ($(wildcard $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)
endif
ifneq ($(wildcard $(MIR1K_DATASET_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(MIR1K_DATASET_ATTRIBUTE_OUTPUT)
endif
ifneq ($(wildcard $(SCMS_DATASET_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(SCMS_DATASET_ATTRIBUTE_OUTPUT)
endif
ifneq ($(wildcard $(KRAISLER_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(KRAISLER_ATTRIBUTE_OUTPUT)
endif
ifneq ($(wildcard $(IRMAS_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_CANDIDATE_PATHS += $(IRMAS_ATTRIBUTE_OUTPUT)
endif
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS := $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)
ifneq ($(wildcard $(KRAISLER_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(KRAISLER_ATTRIBUTE_OUTPUT)
endif
ifneq ($(wildcard $(IRMAS_ATTRIBUTE_OUTPUT)),)
DETECTOR_REAL_NOTE_PATTERN_OPTIONAL_PROTECTED_PATHS += $(IRMAS_ATTRIBUTE_OUTPUT)
endif
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
ifneq ($(wildcard $(GUITAR_TECHS_MUSIC_MANIFEST)),)
DETECTOR_GUITAR_PATTERN_ROUTE_TARGETS += find-guitar-techs-music-route-patterns
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

.PHONY: audit-build-sample-storage relocate-build-sample-storage deduplicate-build-sample-storage compare-build-sample-storage-conflicts merge-build-sample-storage-nonconflicting ensure-build-sample-storage-link
.PHONY: prepare-pitch-shifted-violin-samples test-pitch-shifted-violin-samples test-pitch-shifted-violin-samples-parallel analyze-pitch-shifted-violin-attributes test-pitch-shifted-violin-prepare

# Keep downloaded and generated audio sample corpora off the workspace disk.
# The apply target refuses collisions so an existing external corpus is never
# overwritten or merged implicitly.
audit-build-sample-storage: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --dry-run

relocate-build-sample-storage: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --apply

deduplicate-build-sample-storage: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --deduplicate-identical

# Inspect or safely merge a pre-existing external destination without
# overwriting it.  These keep collision handling inside the Makefile workflow.
compare-build-sample-storage-conflicts: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --compare-conflicts

merge-build-sample-storage-nonconflicting: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --merge-nonconflicting

# Usage: make ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=good_sounds_samples
ensure-build-sample-storage-link: scripts/relocate_build_sample_directories.sh
	@test -n "$(BUILD_SAMPLE_STORAGE_DIR)"
	bash scripts/relocate_build_sample_directories.sh --ensure-link "$(BUILD_SAMPLE_STORAGE_DIR)"

test-real-world-samples-max: scripts/run_with_duration.sh
	+$(MAKE) test-real-world-samples-max-parallel

summarize-sample-manifests: scripts/summarize_sample_manifests.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) sample_manifest_summary $(PYTHON) scripts/summarize_sample_manifests.py $(SAMPLE_MANIFEST_SUMMARY_PATHS)

detector-improvement-samples: test-detector-samples-parallel

detector-improvement-patterns: measure-analyzer-patterns

detector-improvement-patterns-cached: measure-analyzer-patterns-cached

detector-improvement-patterns-cached-summary: measure-analyzer-patterns-cached-summary

# Compare cached labelled chord outcomes without rebuilding or playing corpus audio.
analyze-cross-corpus-chord-evidence-cached: scripts/summarize_cross_corpus_chord_evidence.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV); run make analyze-maps-piano-attributes first"; exit 2; }
	@test -s "$(GUITARSET_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(GUITARSET_ATTRIBUTE_TSV); run make analyze-guitarset-attributes first"; exit 2; }
	$(PYTHON) scripts/summarize_cross_corpus_chord_evidence.py "$(MAPS_PIANO_ATTRIBUTE_TSV)" "$(GUITARSET_ATTRIBUTE_TSV)"

.PHONY: analyze-independent-piano-chord-evidence
analyze-independent-piano-chord-evidence: scripts/summarize_cross_corpus_chord_evidence.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV); run make analyze-maps-piano-attributes first"; exit 2; }
	@test -s "$(MAESTRO_REAL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAESTRO_REAL_ATTRIBUTE_TSV); run make measure-maestro-real-samples first"; exit 2; }
	$(PYTHON) scripts/summarize_cross_corpus_chord_evidence.py "$(MAPS_PIANO_ATTRIBUTE_TSV)" "$(MAESTRO_REAL_ATTRIBUTE_TSV)" > "$(MAESTRO_REAL_CHORD_EVIDENCE_OUTPUT)"
	@cat "$(MAESTRO_REAL_CHORD_EVIDENCE_OUTPUT)"

.PHONY: analyze-independent-piano-chord-states test-independent-piano-chord-states audit-independent-piano-exact-chord-fallback test-audit-independent-piano-exact-chord-fallback
analyze-independent-piano-chord-states: scripts/summarize_independent_piano_chord_states.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV); run make analyze-maps-piano-attributes first"; exit 2; }
	@test -s "$(MAESTRO_REAL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAESTRO_REAL_ATTRIBUTE_TSV); run make measure-maestro-real-samples first"; exit 2; }
	$(PYTHON) scripts/summarize_independent_piano_chord_states.py "$(MAPS_PIANO_ATTRIBUTE_TSV)" "$(MAESTRO_REAL_ATTRIBUTE_TSV)" > "$(MAESTRO_REAL_CHORD_STATE_OUTPUT)"
	@cat "$(MAESTRO_REAL_CHORD_STATE_OUTPUT)"

test-independent-piano-chord-states: tests/test_summarize_independent_piano_chord_states.py scripts/summarize_independent_piano_chord_states.py
	$(PYTHON) tests/test_summarize_independent_piano_chord_states.py

# Replays contiguous annotated stable-chord windows through one AnalysisEngine.
# This specifically tests the runtime switch-confirm/no-label hold behavior,
# whereas the normal attributes intentionally analyze each window independently.
.PHONY: measure-maps-piano-chord-state-cached measure-maestro-real-chord-state-cached measure-maps-piano-chord-display-gate070 measure-maestro-real-chord-display-gate070 analyze-independent-piano-chord-stability-cached test-summarize-piano-chord-state-audit audit-piano-chord-confirmation audit-piano-chord-confirm3 audit-piano-chord-tone018 audit-piano-chord-margin060 audit-piano-chord-bassbonus000 audit-piano-chord-display-confidence test-audit-piano-chord-confirmation test-audit-piano-chord-display-confidence
measure-maps-piano-chord-state-cached: $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh | $(BUILD_DIR)
	@test -s "$(MAPS_PIANO_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_SAMPLE_DIR)/maps" || { printf '%s\n' "missing prepared MAPS piano CSV or audio under $(MAPS_PIANO_SAMPLE_DIR); run make prepare-maps-piano-samples first"; exit 2; }
	$(RUN_WITH_DURATION) maps_piano_chord_state_audit env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_CHORD_STATE_AUDIT_TSV="$(MAPS_PIANO_CHORD_STATE_AUDIT)" MUSIC_ANALYZER_MAESTRO_CHORD_STATE_AUDIT_MAX_SEQUENCES="$(PIANO_CHORD_STATE_AUDIT_MAX_SEQUENCES)" $(BUILD_DIR)/analyzer_maestro

measure-maestro-real-chord-state-cached: $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh | $(BUILD_DIR)
	@test -s "$(MAESTRO_REAL_SAMPLE_DIR)/maestro-v3.0.0.csv" || { printf '%s\n' "missing prepared MAESTRO CSV under $(MAESTRO_REAL_SAMPLE_DIR); run make prepare-maestro-real-samples first"; exit 2; }
	$(RUN_WITH_DURATION) maestro_real_chord_state_audit env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAESTRO_REAL_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_CHORD_STATE_AUDIT_TSV="$(MAESTRO_REAL_CHORD_STATE_AUDIT)" MUSIC_ANALYZER_MAESTRO_CHORD_STATE_AUDIT_MAX_SEQUENCES="$(PIANO_CHORD_STATE_AUDIT_MAX_SEQUENCES)" $(BUILD_DIR)/analyzer_maestro

measure-maps-piano-chord-display-gate070:
	+$(MAKE) measure-maps-piano-chord-state-cached MAPS_PIANO_CHORD_STATE_AUDIT="$(MAPS_PIANO_CHORD_STATE_CONFIDENCE070_AUDIT)"

measure-maestro-real-chord-display-gate070:
	+$(MAKE) measure-maestro-real-chord-state-cached MAESTRO_REAL_CHORD_STATE_AUDIT="$(MAESTRO_REAL_CHORD_STATE_CONFIDENCE070_AUDIT)"

analyze-independent-piano-chord-stability-cached: scripts/summarize_piano_chord_state_audit.py | $(BUILD_DIR)
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing cached $(MAPS_PIANO_CHORD_STATE_AUDIT); run make measure-maps-piano-chord-state-cached first"; exit 2; }
	@test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing cached $(MAESTRO_REAL_CHORD_STATE_AUDIT); run make measure-maestro-real-chord-state-cached first"; exit 2; }
	$(PYTHON) scripts/summarize_piano_chord_state_audit.py "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" > "$(INDEPENDENT_PIANO_CHORD_STABILITY_OUTPUT)"
	@cat "$(INDEPENDENT_PIANO_CHORD_STABILITY_OUTPUT)"

test-summarize-piano-chord-state-audit: tests/test_summarize_piano_chord_state_audit.py scripts/summarize_piano_chord_state_audit.py
	$(PYTHON) tests/test_summarize_piano_chord_state_audit.py

audit-piano-chord-confirmation: scripts/audit_piano_chord_confirmation.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing baseline piano chord-state audits"; exit 2; }
	@test -s "$(MAPS_PIANO_CHORD_STATE_CONFIRM1_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_CONFIRM1_AUDIT)" || { printf '%s\n' "missing cached one-frame piano chord-state trial audits"; exit 2; }
	@tmp="$(PIANO_CHORD_CONFIRMATION_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_confirmation.py --baseline "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" --trial "$(MAPS_PIANO_CHORD_STATE_CONFIRM1_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_CONFIRM1_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_CONFIRMATION_AUDIT)" && cat "$(PIANO_CHORD_CONFIRMATION_AUDIT)"

audit-piano-chord-confirm3: scripts/audit_piano_chord_confirmation.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing baseline piano chord-state audits"; exit 2; }
	@test -s "$(MAPS_PIANO_CHORD_STATE_CONFIRM3_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_CONFIRM3_AUDIT)" || { printf '%s\n' "missing cached three-frame piano chord-state trial audits"; exit 2; }
	@tmp="$(PIANO_CHORD_CONFIRM3_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_confirmation.py --baseline "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" --trial "$(MAPS_PIANO_CHORD_STATE_CONFIRM3_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_CONFIRM3_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_CONFIRM3_AUDIT)" && cat "$(PIANO_CHORD_CONFIRM3_AUDIT)"

audit-piano-chord-tone018: scripts/audit_piano_chord_confirmation.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing baseline piano chord-state audits"; exit 2; }
	@test -s "$(MAPS_PIANO_CHORD_STATE_TONE018_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_TONE018_AUDIT)" || { printf '%s\n' "missing cached 0.18 chord-tone trial audits"; exit 2; }
	@tmp="$(PIANO_CHORD_TONE018_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_confirmation.py --baseline "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" --trial "$(MAPS_PIANO_CHORD_STATE_TONE018_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_TONE018_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_TONE018_AUDIT)" && cat "$(PIANO_CHORD_TONE018_AUDIT)"

audit-piano-chord-margin060: scripts/audit_piano_chord_confirmation.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing baseline piano chord-state audits"; exit 2; }
	@test -s "$(MAPS_PIANO_CHORD_STATE_MARGIN060_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_MARGIN060_AUDIT)" || { printf '%s\n' "missing cached 0.05/0.60 chord-margin trial audits"; exit 2; }
	@tmp="$(PIANO_CHORD_MARGIN060_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_confirmation.py --baseline "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" --trial "$(MAPS_PIANO_CHORD_STATE_MARGIN060_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_MARGIN060_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_MARGIN060_AUDIT)" && cat "$(PIANO_CHORD_MARGIN060_AUDIT)"

audit-piano-chord-bassbonus000: scripts/audit_piano_chord_confirmation.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing baseline piano chord-state audits"; exit 2; }
	@test -s "$(MAPS_PIANO_CHORD_STATE_BASSBONUS000_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_BASSBONUS000_AUDIT)" || { printf '%s\n' "missing cached zero bass-root-bonus chord trial audits"; exit 2; }
	@tmp="$(PIANO_CHORD_BASSBONUS000_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_confirmation.py --baseline "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" --trial "$(MAPS_PIANO_CHORD_STATE_BASSBONUS000_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_BASSBONUS000_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_BASSBONUS000_AUDIT)" && cat "$(PIANO_CHORD_BASSBONUS000_AUDIT)"

audit-piano-chord-display-confidence: scripts/audit_piano_chord_display_confidence.py
	@test -s "$(MAPS_PIANO_CHORD_STATE_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" || { printf '%s\n' "missing cached baseline piano chord-state audits"; exit 2; }
	@tmp="$(PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_display_confidence.py "$(MAPS_PIANO_CHORD_STATE_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_AUDIT)" > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT)" && cat "$(PIANO_CHORD_DISPLAY_CONFIDENCE_AUDIT)"

test-audit-piano-chord-display-confidence: tests/test_audit_piano_chord_display_confidence.py scripts/audit_piano_chord_display_confidence.py
	$(PYTHON) tests/test_audit_piano_chord_display_confidence.py

audit-piano-chord-display-gate: scripts/audit_piano_chord_display_gate.py
	@test -s "$(BUILD_DIR)/maps_piano_chord_state_confidence060.tsv" && test -s "$(BUILD_DIR)/maestro_real_chord_state_confidence060.tsv" && test -s "$(MAPS_PIANO_CHORD_STATE_CONFIDENCE070_AUDIT)" && test -s "$(MAESTRO_REAL_CHORD_STATE_CONFIDENCE070_AUDIT)" || { printf '%s\n' "missing cached 0.60 or 0.70 display-gate piano replays"; exit 2; }
	@tmp="$(PIANO_CHORD_DISPLAY_GATE_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_piano_chord_display_gate.py --baseline "$(BUILD_DIR)/maps_piano_chord_state_confidence060.tsv" "$(BUILD_DIR)/maestro_real_chord_state_confidence060.tsv" --trial "$(MAPS_PIANO_CHORD_STATE_CONFIDENCE070_AUDIT)" "$(MAESTRO_REAL_CHORD_STATE_CONFIDENCE070_AUDIT)" --floor 0.70 > "$$tmp" && mv "$$tmp" "$(PIANO_CHORD_DISPLAY_GATE_AUDIT)" && cat "$(PIANO_CHORD_DISPLAY_GATE_AUDIT)"

test-audit-piano-chord-display-gate: tests/test_audit_piano_chord_display_gate.py scripts/audit_piano_chord_display_gate.py
	$(PYTHON) tests/test_audit_piano_chord_display_gate.py

test-audit-piano-chord-confirmation: tests/test_audit_piano_chord_confirmation.py scripts/audit_piano_chord_confirmation.py scripts/summarize_piano_chord_state_audit.py
	$(PYTHON) tests/test_audit_piano_chord_confirmation.py

audit-independent-piano-exact-chord-fallback: scripts/audit_independent_piano_exact_chord_fallback.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV)"; exit 2; }
	@test -s "$(MAESTRO_REAL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAESTRO_REAL_ATTRIBUTE_TSV)"; exit 2; }
	@tmp="$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_independent_piano_exact_chord_fallback.py "$(MAPS_PIANO_ATTRIBUTE_TSV)" "$(MAESTRO_REAL_ATTRIBUTE_TSV)" > "$$tmp" && mv "$$tmp" "$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)" && cat "$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)"

test-audit-independent-piano-exact-chord-fallback: tests/test_audit_independent_piano_exact_chord_fallback.py scripts/audit_independent_piano_exact_chord_fallback.py
	$(PYTHON) tests/test_audit_independent_piano_exact_chord_fallback.py

.PHONY: audit-chord-primary-components test-audit-chord-primary-components
audit-chord-primary-components: scripts/audit_chord_primary_components.py | $(BUILD_DIR)
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAPS_PIANO_ATTRIBUTE_TSV)"; exit 2; }
	@test -s "$(MAESTRO_REAL_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MAESTRO_REAL_ATTRIBUTE_TSV)"; exit 2; }
	@tmp="$(CHORD_PRIMARY_COMPONENT_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_chord_primary_components.py "$(MAPS_PIANO_ATTRIBUTE_TSV)" "$(MAESTRO_REAL_ATTRIBUTE_TSV)" $(CHORD_PRIMARY_COMPONENT_ARGS) > "$$tmp" && mv "$$tmp" "$(CHORD_PRIMARY_COMPONENT_AUDIT)" && cat "$(CHORD_PRIMARY_COMPONENT_AUDIT)"

test-audit-chord-primary-components: tests/test_audit_chord_primary_components.py scripts/audit_chord_primary_components.py
	$(PYTHON) tests/test_audit_chord_primary_components.py

test-cross-corpus-chord-evidence: tests/test_summarize_cross_corpus_chord_evidence.py scripts/summarize_cross_corpus_chord_evidence.py
	$(PYTHON) tests/test_summarize_cross_corpus_chord_evidence.py

detector-improvement-routes: analyze-detector-improvement-routes

.PHONY: detector-improvement-routes-bounded
detector-improvement-routes-bounded: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) detector_improvement_routes_bounded $(MAKE) -j4 PARALLEL_TEST_JOBS=4 REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS)" REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS="$(DETECTOR_REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS)" $(DETECTOR_IMPROVEMENT_ROUTE_SCAN_TARGETS)

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

# Reformat an already measured scan without rebuilding its expensive audio-analysis prerequisites.
detector-improvement-route-summary-from-cached-report: scripts/summarize_detector_route_report.py
	@test -s "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" || { printf '%s\n' "missing $(DETECTOR_IMPROVEMENT_ROUTE_REPORT); run make detector-improvement-route-report first"; exit 2; }
	@tmp="$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY).$$$$.tmp"; $(PYTHON) scripts/summarize_detector_route_report.py "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY_ARGS) > "$$tmp" && mv "$$tmp" "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)" && cat "$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"

detector-improvement-route-summary-refresh: FORCE
	+$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_REPORT)
	+$(MAKE) --always-make $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)
	@printf '%s\n' "detector improvement route summary: $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY)"

$(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY): $(DETECTOR_IMPROVEMENT_ROUTE_REPORT) scripts/summarize_detector_route_report.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/summarize_detector_route_report.py "$(DETECTOR_IMPROVEMENT_ROUTE_REPORT)" $(DETECTOR_IMPROVEMENT_ROUTE_SUMMARY_ARGS) > "$$tmp" && mv "$$tmp" "$@" && cat "$@"

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

test-beat-this-sidecar-client: $(BUILD_DIR)/beat_this_sidecar_client_tests tests/fake_beat_this_sidecar.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) beat_this_sidecar_client_tests $(BUILD_DIR)/beat_this_sidecar_client_tests "$(CURDIR)/tests/fake_beat_this_sidecar.py"

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

.PHONY: test-bpm-moving-window-contract test-bpm-regression
test-bpm-moving-window-contract:
	$(PYTHON) tests/test_bpm_moving_window_contract.py

test-bpm-regression: test-analyzer-cases test-egmd-fixture test-bpm-moving-window-contract

.PHONY: start-agpt-guitar-preparation
start-agpt-guitar-preparation: scripts/start_agpt_guitar_prepare.sh scripts/prepare_agpt_guitar_samples.py
	$(SHELL) scripts/start_agpt_guitar_prepare.sh "$(CURDIR)/scripts/prepare_agpt_guitar_samples.py" "$(AGPT_GUITAR_EXTRACTED_DIR)" "$(AGPT_GUITAR_SAMPLE_DIR)" "$(AGPT_GUITAR_SAMPLE_LIMIT)" "$(AGPT_GUITAR_MIN_GUITAR)" "ffmpeg"

.PHONY: inspect-agpt-guitar-preparation
inspect-agpt-guitar-preparation: scripts/inspect_agpt_guitar_preparation.sh
	$(SHELL) scripts/inspect_agpt_guitar_preparation.sh "$(AGPT_GUITAR_SAMPLE_DIR)" "$(AGPT_GUITAR_MIN_GUITAR)"

.PHONY: start-agpt-guitar-evaluation
start-agpt-guitar-evaluation: scripts/start_agpt_guitar_evaluation.sh
	$(SHELL) scripts/start_agpt_guitar_evaluation.sh "$(MAKE)" "$(AGPT_GUITAR_SAMPLE_DIR)" "$(AGPT_GUITAR_MIN_GUITAR)"

.PHONY: stop-agpt-guitar-evaluation
stop-agpt-guitar-evaluation: scripts/stop_agpt_guitar_evaluation.sh
	$(SHELL) scripts/stop_agpt_guitar_evaluation.sh "$(AGPT_GUITAR_SAMPLE_DIR)"

.PHONY: summarize-agpt-guitar-evaluation
summarize-agpt-guitar-evaluation: scripts/summarize_agpt_guitar_evaluation.py
	@set -- $(wildcard $(BUILD_DIR)/real_note_agpt_guitar_shard_*.out); test "$$1" != "" || { printf '%s\n' "missing AG-PT shard outputs; run test-agpt-guitar-samples first"; exit 2; }; $(PYTHON) scripts/summarize_agpt_guitar_evaluation.py --output "$(AGPT_GUITAR_MEASUREMENT)" --minimum-samples "$(AGPT_GUITAR_MIN_GUITAR)" "$$@"
	@cat "$(AGPT_GUITAR_MEASUREMENT)"

.PHONY: measure-agpt-guitar-full-mix
measure-agpt-guitar-full-mix: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_agpt_guitar_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(AGPT_GUITAR_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(AGPT_GUITAR_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(AGPT_GUITAR_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(AGPT_GUITAR_FULL_MIX_MEASUREMENT)"

.PHONY: start-agpt-guitar-full-mix-measurement
start-agpt-guitar-full-mix-measurement: $(BUILD_DIR)/analyzer_real_note_samples scripts/start_agpt_guitar_full_mix_measurement.sh
	$(SHELL) scripts/start_agpt_guitar_full_mix_measurement.sh "$(CURDIR)/$(BUILD_DIR)/analyzer_real_note_samples" "$(AGPT_GUITAR_SAMPLE_DIR)" "$(AGPT_GUITAR_MIN_GUITAR)" "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" "$(AGPT_GUITAR_FULL_MIX_MEASUREMENT)"

.PHONY: inspect-agpt-guitar-full-mix
inspect-agpt-guitar-full-mix: scripts/summarize_real_note_attributes.py
	@test -s "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing AG-PT full-mix attributes; run make measure-agpt-guitar-full-mix first"; exit 2; }
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)"

.PHONY: summarize-agpt-guitar-visual-primary
summarize-agpt-guitar-visual-primary: scripts/summarize_agpt_guitar_visual_primary.py
	@test -s "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing completed AG-PT full-mix attributes"; exit 2; }
	$(PYTHON) scripts/summarize_agpt_guitar_visual_primary.py --input "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" --output "$(AGPT_GUITAR_VISUAL_PRIMARY_MEASUREMENT)"
	@cat "$(AGPT_GUITAR_VISUAL_PRIMARY_MEASUREMENT)"

.PHONY: inspect-agpt-guitar-visual-examples
inspect-agpt-guitar-visual-examples: scripts/inspect_agpt_guitar_visual_examples.py
	$(PYTHON) scripts/inspect_agpt_guitar_visual_examples.py

.PHONY: analyze-agpt-guitar-visual-candidates
analyze-agpt-guitar-visual-candidates: scripts/find_real_note_attribute_patterns.py
	@test -s "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing completed AG-PT full-mix attributes"; exit 2; }
	@test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing protected real-note attributes"; exit 2; }
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" --top-buckets 8 --bucket-status visual_row_confusion --limit 8 --min-positive-samples 20 --max-negative-samples 0 --max-conditions "$(AGPT_GUITAR_VISUAL_PATTERN_MAX_CONDITIONS)" --beam-width "$(AGPT_GUITAR_VISUAL_PATTERN_BEAM_WIDTH)" --include-row-context --protected-scope all --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --show-examples 3 --show-near-misses 8 --profile-fields 8 > "$(AGPT_GUITAR_VISUAL_PATTERN_REPORT)"
	@cat "$(AGPT_GUITAR_VISUAL_PATTERN_REPORT)"

.PHONY: start-agpt-guitar-visual-mining
start-agpt-guitar-visual-mining: scripts/start_agpt_guitar_visual_mining.sh
	@test -s "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" || { printf '%s\n' "missing completed AG-PT full-mix attributes"; exit 2; }
	@test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing protected real-note attributes"; exit 2; }
	$(SHELL) scripts/start_agpt_guitar_visual_mining.sh "$(AGPT_GUITAR_FULL_MIX_ATTRIBUTE_TSV)" "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(AGPT_GUITAR_VISUAL_PATTERN_REPORT)"

.PHONY: inspect-agpt-guitar-visual-mining
inspect-agpt-guitar-visual-mining: scripts/inspect_agpt_guitar_visual_miner.sh
	$(SHELL) scripts/inspect_agpt_guitar_visual_miner.sh

.PHONY: test-agpt-guitar-preparation-scripts
test-agpt-guitar-preparation-scripts:
	$(SHELL) -n scripts/start_agpt_guitar_prepare.sh scripts/start_agpt_guitar_evaluation.sh scripts/stop_agpt_guitar_evaluation.sh scripts/start_agpt_guitar_full_mix_measurement.sh scripts/start_agpt_guitar_visual_mining.sh scripts/inspect_agpt_guitar_preparation.sh scripts/inspect_agpt_guitar_visual_miner.sh

.PHONY: test-summarize-agpt-guitar-evaluation
test-summarize-agpt-guitar-evaluation: tests/test_summarize_agpt_guitar_evaluation.py scripts/summarize_agpt_guitar_evaluation.py
	$(PYTHON) tests/test_summarize_agpt_guitar_evaluation.py

.PHONY: test-summarize-agpt-guitar-visual-primary
test-summarize-agpt-guitar-visual-primary: tests/test_summarize_agpt_guitar_visual_primary.py scripts/summarize_agpt_guitar_visual_primary.py
	$(PYTHON) tests/test_summarize_agpt_guitar_visual_primary.py

.PHONY: analyze-egmd-bpm measure-egmd-bpm-cached summarize-egmd-bpm analyze-real-egmd-bpm analyze-mdb-bpm analyze-maestro-bpm analyze-kraisler-bpm measure-kraisler-bpm-cached summarize-kraisler-bpm download-ballroom-tempo download-ballroom-annotations download-permissive-beat-tracker test-download-ballroom-tempo-script test-prepare-ballroom-tempo-fixture prepare-ballroom-tempo-fixture measure-ballroom-bpm summarize-ballroom-bpm download-filobass inspect-filobass prepare-filobass-tempo-fixture measure-filobass-bpm summarize-filobass-bpm inspect-filobass-tempo-onsets inspect-tempo-candidate-feasibility inspect-tempo-confidence-calibration inspect-beat-tracker-backends analyze-bpm-diagnostics test-analyze-egmd-tempo test-inspect-tempo-candidate-feasibility measure-permissive-beat-tracker-high-tempo measure-permissive-beat-tracker-high-tempo-ballroom measure-permissive-beat-tracker-high-tempo-filobass measure-permissive-beat-tracker-high-tempo-gtzan-rhythm summarize-permissive-beat-tracker-high-tempo

test-analyze-egmd-tempo: tests/test_analyze_egmd_tempo.py scripts/analyze_egmd_tempo.py
	$(PYTHON) tests/test_analyze_egmd_tempo.py

test-inspect-tempo-candidate-feasibility: tests/test_inspect_tempo_candidate_feasibility.py scripts/inspect_tempo_candidate_feasibility.py
	$(PYTHON) tests/test_inspect_tempo_candidate_feasibility.py

.PHONY: summarize-immediate-source-bpm-3s test-summarize-immediate-source-bpm
summarize-immediate-source-bpm-3s: scripts/summarize_immediate_source_bpm.py | $(BUILD_DIR)
	@test -s "$(BUILD_DIR)/ballroom_bpm_3s_source_diagnostics.log" || { printf '%s\n' "missing Ballroom 3 s source diagnostics; run the 3 s replay first"; exit 2; }
	@inputs="--input Ballroom=$(BUILD_DIR)/ballroom_bpm_3s_source_diagnostics.log"; if test -s "$(FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG)"; then inputs="$$inputs --input FiloBass=$(FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG)"; fi; if test -s "$(GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG)"; then inputs="$$inputs --input GTZAN-Rhythm=$(GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG)"; fi; $(PYTHON) scripts/summarize_immediate_source_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" $$inputs --output "$(IMMEDIATE_SOURCE_BPM_3S_AUDIT)"
	cat "$(IMMEDIATE_SOURCE_BPM_3S_AUDIT)"

test-summarize-immediate-source-bpm: tests/test_summarize_immediate_source_bpm.py scripts/summarize_immediate_source_bpm.py
	$(PYTHON) tests/test_summarize_immediate_source_bpm.py

.PHONY: measure-ballroom-immediate-source-bpm-3s measure-filobass-immediate-source-bpm-3s

measure-ballroom-immediate-source-bpm-3s: $(BUILD_DIR)/analyzer_maestro prepare-ballroom-tempo-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_ballroom_bpm_3s_source env MUSIC_ANALYZER_MAESTRO_ROOT="$(BALLROOM_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS=3 $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/ballroom_bpm_3s_source_diagnostics.log.summary" 2> "$(BUILD_DIR)/ballroom_bpm_3s_source_diagnostics.log"
	$(PYTHON) scripts/summarize_immediate_source_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" --input "Ballroom=$(BUILD_DIR)/ballroom_bpm_3s_source_diagnostics.log"

measure-filobass-immediate-source-bpm-3s: $(BUILD_DIR)/analyzer_maestro prepare-filobass-tempo-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_filobass_bpm_3s_source env MUSIC_ANALYZER_MAESTRO_ROOT="$(FILOBASS_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS=3 $(BUILD_DIR)/analyzer_maestro > "$(FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG).summary" 2> "$(FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG)"
	$(PYTHON) scripts/summarize_immediate_source_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" --input "FiloBass=$(FILOBASS_IMMEDIATE_SOURCE_BPM_3S_LOG)"

.PHONY: measure-gtzan-immediate-source-bpm-3s
measure-gtzan-immediate-source-bpm-3s: $(BUILD_DIR)/analyzer_maestro prepare-gtzan-rhythm-tempo-fixture scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_gtzan_rhythm_bpm_3s_source env MUSIC_ANALYZER_MAESTRO_ROOT="$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS=3 $(BUILD_DIR)/analyzer_maestro > "$(GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG).summary" 2> "$(GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG)"
	$(PYTHON) scripts/summarize_immediate_source_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" --input "GTZAN-Rhythm=$(GTZAN_IMMEDIATE_SOURCE_BPM_3S_LOG)"
analyze-egmd-bpm: $(BUILD_DIR)/analyzer_egmd tests/generate_egmd_fixture.py scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	rm -rf "$(REAL_GOAL_EGMD_FIXTURE_DIR)"
	$(PYTHON) tests/generate_egmd_fixture.py "$(REAL_GOAL_EGMD_FIXTURE_DIR)"
	+$(MAKE) measure-egmd-bpm-cached

measure-egmd-bpm-cached: $(BUILD_DIR)/analyzer_egmd scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_egmd_bpm_fixture env MUSIC_ANALYZER_EGMD_ROOT="$(REAL_GOAL_EGMD_FIXTURE_DIR)" MUSIC_ANALYZER_EGMD_SOURCE_NAME="E-GMD percussion" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(EGMD_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(EGMD_BPM_LOG).summary" 2> "$(EGMD_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(EGMD_BPM_LOG)"

summarize-egmd-bpm: scripts/analyze_egmd_tempo.py $(EGMD_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(EGMD_BPM_LOG)"

analyze-real-egmd-bpm: $(BUILD_DIR)/analyzer_egmd scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_real_egmd_bpm env MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=20 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=80 MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS=20 MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(EGMD_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(REAL_EGMD_BPM_LOG).summary" 2> "$(REAL_EGMD_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(REAL_EGMD_BPM_LOG)"

analyze-mdb-bpm: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_mdb_bpm env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VALIDATE_BPM=1 MUSIC_ANALYZER_EGMD_REQUIRED_TEMPO_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_EGMD_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_EGMD_BPM_MAX_SECONDS="$(MDB_BPM_MAX_SECONDS)" MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO=1 MUSIC_ANALYZER_EGMD_VERBOSE_TEMPO_LIMIT=4000 $(BUILD_DIR)/analyzer_egmd > "$(MDB_BPM_LOG).summary" 2> "$(MDB_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(MDB_BPM_LOG)"

analyze-maestro-bpm: $(BUILD_DIR)/analyzer_maestro prepare-maestro-real-samples scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_maestro_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAESTRO_REAL_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=20 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(MAESTRO_BPM_LOG).summary" 2> "$(MAESTRO_BPM_LOG)"
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(MAESTRO_BPM_LOG)"

analyze-kraisler-bpm: $(BUILD_DIR)/analyzer_maestro extract-kraisler scripts/prepare_kraisler_tempo_fixture.py scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(PYTHON) scripts/prepare_kraisler_tempo_fixture.py --root "$(KRAISLER_EXTRACT_DIR)/KRAISLER" --output "$(KRAISLER_TEMPO_FIXTURE_DIR)"
	+$(MAKE) measure-kraisler-bpm-cached

measure-kraisler-bpm-cached: $(BUILD_DIR)/analyzer_maestro $(KRAISLER_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_kraisler_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(KRAISLER_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(KRAISLER_BPM_LOG).summary" 2> "$(KRAISLER_BPM_LOG)"
	+$(MAKE) summarize-kraisler-bpm

summarize-kraisler-bpm: scripts/analyze_egmd_tempo.py $(KRAISLER_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(KRAISLER_BPM_LOG)"

# Ballroom provides manually corrected beat/bar times for real dance mixes.
# Its archive and labels are stored outside the repository; the fixture below
# only symlinks selected WAVs into build/ for the generic tempo harness.
BALLROOM_DOWNLOAD_CONNECTIONS ?= 8
BALLROOM_DOWNLOAD_MAX_RESUME_ATTEMPTS ?= 6

download-ballroom-tempo: configure-instrument-sample-store scripts/download_ballroom_tempo_dataset.sh
	bash scripts/download_ballroom_tempo_dataset.sh "$(INSTRUMENT_SAMPLE_STORE)" "$(CURL)" "" "" "" "$(ARIA2C)" "$(BALLROOM_DOWNLOAD_CONNECTIONS)" "$(BALLROOM_DOWNLOAD_MAX_RESUME_ATTEMPTS)"

test-download-ballroom-tempo-script: tests/test_download_ballroom_tempo_dataset.py scripts/download_ballroom_tempo_dataset.sh
	$(PYTHON) tests/test_download_ballroom_tempo_dataset.py

test-prepare-ballroom-tempo-fixture: tests/test_prepare_ballroom_tempo_fixture.py scripts/prepare_ballroom_tempo_fixture.py
	$(PYTHON) tests/test_prepare_ballroom_tempo_fixture.py

download-ballroom-annotations: configure-instrument-sample-store scripts/download_ballroom_annotations.sh
	bash scripts/download_ballroom_annotations.sh "$(INSTRUMENT_SAMPLE_STORE)"

.PHONY: download-filobass
download-filobass: configure-instrument-sample-store scripts/download_filobass_dataset.sh
	bash scripts/download_filobass_dataset.sh "$(INSTRUMENT_SAMPLE_STORE)" "$(CURL)"

.PHONY: download-gtzan-rhythm
download-gtzan-rhythm: configure-instrument-sample-store scripts/download_gtzan_rhythm_dataset.sh
	bash scripts/download_gtzan_rhythm_dataset.sh "$(INSTRUMENT_SAMPLE_STORE)" "$(CURL)" "$(GTZAN_RHYTHM_AUDIO_URL)" "$(GTZAN_RHYTHM_ANNOTATIONS_URL)"

.PHONY: download-candombe download-candombe-annotations inspect-candombe inspect-candombe-annotations prepare-candombe-tempo-fixture measure-candombe-bpm summarize-candombe-bpm
download-candombe: configure-instrument-sample-store scripts/download_candombe_dataset.sh
	bash scripts/download_candombe_dataset.sh "$(INSTRUMENT_SAMPLE_STORE)" "$(CURL)" "$(ARIA2C)" "$(CANDOMBE_AUDIO_URL)" "$(CANDOMBE_ANNOTATIONS_URL)"

download-candombe-annotations: configure-instrument-sample-store scripts/download_candombe_dataset.sh
	bash scripts/download_candombe_dataset.sh "$(INSTRUMENT_SAMPLE_STORE)" "$(CURL)" "$(ARIA2C)" "$(CANDOMBE_AUDIO_URL)" "$(CANDOMBE_ANNOTATIONS_URL)" annotations-only

inspect-candombe: download-candombe scripts/inspect_candombe_dataset.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_candombe_dataset.py --root "$(CANDOMBE_SOURCE_DIR)" --output "$(CANDOMBE_INSPECTION_OUTPUT)"

inspect-candombe-annotations: download-candombe-annotations scripts/inspect_candombe_dataset.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_candombe_dataset.py --root "$(CANDOMBE_SOURCE_DIR)" --annotations-only --output "$(CANDOMBE_INSPECTION_OUTPUT)"

prepare-candombe-tempo-fixture: inspect-candombe scripts/prepare_candombe_tempo_fixture.py
	$(PYTHON) scripts/prepare_candombe_tempo_fixture.py --root "$(CANDOMBE_SOURCE_DIR)" --output "$(CANDOMBE_TEMPO_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --limit "$(CANDOMBE_BPM_LIMIT)"

measure-candombe-bpm: $(BUILD_DIR)/analyzer_maestro prepare-candombe-tempo-fixture scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_candombe_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(CANDOMBE_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(CANDOMBE_BPM_LOG).summary" 2> "$(CANDOMBE_BPM_LOG)"
	+$(MAKE) summarize-candombe-bpm
	+$(MAKE) update-detection-accuracy-report-cached

summarize-candombe-bpm: scripts/analyze_egmd_tempo.py $(CANDOMBE_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(CANDOMBE_BPM_LOG)"

.PHONY: test-download-candombe-script test-inspect-candombe test-prepare-candombe-tempo-fixture
test-download-candombe-script: scripts/download_candombe_dataset.sh scripts/validate_zip_archive.py
	bash -n scripts/download_candombe_dataset.sh
	$(PYTHON) tests/test_validate_zip_archive.py

test-inspect-candombe: tests/test_inspect_candombe_dataset.py scripts/inspect_candombe_dataset.py
	$(PYTHON) tests/test_inspect_candombe_dataset.py

test-prepare-candombe-tempo-fixture: tests/test_prepare_candombe_tempo_fixture.py scripts/prepare_candombe_tempo_fixture.py
	$(PYTHON) tests/test_prepare_candombe_tempo_fixture.py

.PHONY: inspect-gtzan-rhythm
inspect-gtzan-rhythm: download-gtzan-rhythm scripts/inspect_gtzan_rhythm_dataset.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_gtzan_rhythm_dataset.py --root "$(GTZAN_RHYTHM_SOURCE_DIR)" --output "$(GTZAN_RHYTHM_INSPECTION_OUTPUT)"

.PHONY: test-inspect-gtzan-rhythm
test-inspect-gtzan-rhythm: tests/test_inspect_gtzan_rhythm_dataset.py scripts/inspect_gtzan_rhythm_dataset.py
	$(PYTHON) tests/test_inspect_gtzan_rhythm_dataset.py

.PHONY: prepare-gtzan-rhythm-tempo-fixture measure-gtzan-rhythm-bpm summarize-gtzan-rhythm-bpm
prepare-gtzan-rhythm-tempo-fixture: inspect-gtzan-rhythm scripts/prepare_gtzan_rhythm_tempo_fixture.py | $(BUILD_DIR)
	$(PYTHON) scripts/prepare_gtzan_rhythm_tempo_fixture.py --audio-root "$(GTZAN_RHYTHM_SOURCE_DIR)/audio" --annotations-root "$(GTZAN_RHYTHM_SOURCE_DIR)/annotations" --output "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --limit "$(GTZAN_RHYTHM_BPM_LIMIT)"

.PHONY: test-prepare-gtzan-rhythm-tempo-fixture
test-prepare-gtzan-rhythm-tempo-fixture: tests/test_prepare_gtzan_rhythm_tempo_fixture.py scripts/prepare_gtzan_rhythm_tempo_fixture.py
	$(PYTHON) tests/test_prepare_gtzan_rhythm_tempo_fixture.py

measure-gtzan-rhythm-bpm: $(BUILD_DIR)/analyzer_maestro prepare-gtzan-rhythm-tempo-fixture scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_gtzan_rhythm_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(GTZAN_RHYTHM_BPM_LOG).summary" 2> "$(GTZAN_RHYTHM_BPM_LOG)"
	+$(MAKE) summarize-gtzan-rhythm-bpm
	+$(MAKE) update-detection-accuracy-report-cached

summarize-gtzan-rhythm-bpm: scripts/analyze_egmd_tempo.py $(GTZAN_RHYTHM_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(GTZAN_RHYTHM_BPM_LOG)"

.PHONY: inspect-filobass test-inspect-filobass
inspect-filobass: download-filobass scripts/inspect_filobass_dataset.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_filobass_dataset.py --root "$(FILOBASS_EXTRACT_DIR)" --output "$(FILOBASS_INSPECTION_OUTPUT)" --min-pairs 20

test-inspect-filobass: tests/test_inspect_filobass_dataset.py scripts/inspect_filobass_dataset.py
	$(PYTHON) tests/test_inspect_filobass_dataset.py

.PHONY: test-prepare-filobass-tempo-fixture
test-prepare-filobass-tempo-fixture: tests/test_prepare_filobass_tempo_fixture.py scripts/prepare_filobass_tempo_fixture.py
	$(PYTHON) tests/test_prepare_filobass_tempo_fixture.py

prepare-filobass-tempo-fixture: inspect-filobass scripts/prepare_filobass_tempo_fixture.py | $(BUILD_DIR)
	$(PYTHON) scripts/prepare_filobass_tempo_fixture.py --root "$(FILOBASS_EXTRACT_DIR)" --pairs "$(FILOBASS_INSPECTION_OUTPUT)" --output "$(FILOBASS_TEMPO_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --limit "$(FILOBASS_BPM_LIMIT)"

measure-filobass-bpm: $(BUILD_DIR)/analyzer_maestro prepare-filobass-tempo-fixture scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_filobass_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(FILOBASS_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(FILOBASS_BPM_LOG).summary" 2> "$(FILOBASS_BPM_LOG)"
	+$(MAKE) summarize-filobass-bpm

summarize-filobass-bpm: scripts/analyze_egmd_tempo.py $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

inspect-filobass-tempo-onsets: prepare-filobass-tempo-fixture scripts/inspect_bass_tempo_onsets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_bass_tempo_onsets.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(FILOBASS_ONSET_DIAGNOSTICS)"

test-inspect-bass-tempo-onsets: tests/test_inspect_bass_tempo_onsets.py scripts/inspect_bass_tempo_onsets.py
	$(PYTHON) tests/test_inspect_bass_tempo_onsets.py

prepare-ballroom-tempo-fixture: download-ballroom-tempo scripts/prepare_ballroom_tempo_fixture.py | $(BUILD_DIR)
	$(PYTHON) scripts/prepare_ballroom_tempo_fixture.py --audio-root "$(BALLROOM_AUDIO_DIR)" --annotations-root "$(BALLROOM_ANNOTATIONS_DIR)" --output "$(BALLROOM_TEMPO_FIXTURE_DIR)" --limit "$(BALLROOM_BPM_LIMIT)"

measure-ballroom-bpm: $(BUILD_DIR)/analyzer_maestro prepare-ballroom-tempo-fixture scripts/analyze_egmd_tempo.py scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_ballroom_bpm env MUSIC_ANALYZER_MAESTRO_ROOT="$(BALLROOM_TEMPO_FIXTURE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_INSPECT_ONLY=1 MUSIC_ANALYZER_MAESTRO_VALIDATE_BPM=1 MUSIC_ANALYZER_MAESTRO_MEASURE_ALL_TEMPO=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_TEMPO_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_MIN_BPM_PASS_PERCENT=0 MUSIC_ANALYZER_MAESTRO_BPM_TOLERANCE="$(BPM_DIAG_TOLERANCE)" MUSIC_ANALYZER_MAESTRO_BPM_MAX_SECONDS="$(MAESTRO_BPM_MAX_SECONDS)" $(BUILD_DIR)/analyzer_maestro > "$(BALLROOM_BPM_LOG).summary" 2> "$(BALLROOM_BPM_LOG)"
	+$(MAKE) summarize-ballroom-bpm
	+$(MAKE) update-detection-accuracy-report-cached

summarize-ballroom-bpm: scripts/analyze_egmd_tempo.py $(BALLROOM_BPM_LOG)
	$(PYTHON) scripts/analyze_egmd_tempo.py --prefix "MAESTRO tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"

inspect-tempo-candidate-feasibility: scripts/inspect_tempo_candidate_feasibility.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_candidate_feasibility.py --tolerance "$(BPM_DIAG_TOLERANCE)" --comparison-log "$(FILOBASS_BPM_LOG)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_candidate_feasibility.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

inspect-tempo-confidence-calibration: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

download-permissive-beat-tracker: scripts/fetch_permissive_beat_tracker.sh | $(BUILD_DIR)
	bash scripts/fetch_permissive_beat_tracker.sh

measure-permissive-beat-tracker: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(BALLROOM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv $(FILOBASS_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" > "$(BTT_BALLROOM_LOG)"
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" > "$(BTT_FILOBASS_LOG)"

measure-permissive-beat-tracker-egmd: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(REAL_GOAL_EGMD_FIXTURE_DIR)/e-gmd-v1.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(REAL_GOAL_EGMD_FIXTURE_DIR)" --metadata e-gmd-v1.0.0.csv --probe "$(BTT_PROBE)" --seconds 8 > "$(BTT_EGMD_LOG)"

measure-permissive-beat-tracker-gtzan-rhythm: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" > "$(BTT_GTZAN_RHYTHM_LOG)"

.PHONY: measure-permissive-beat-tracker-gtzan-rhythm-range-sweep summarize-permissive-beat-tracker-gtzan-rhythm-range-sweep test-summarize-btt-tempo-sweep
measure-permissive-beat-tracker-gtzan-rhythm-range-sweep: $(BTT_PROBE) scripts/sweep_permissive_beat_tracker.py $(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/sweep_permissive_beat_tracker.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempos "$(BTT_GTZAN_RHYTHM_RANGE_SWEEP_MINS)" > "$(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)"

summarize-permissive-beat-tracker-gtzan-rhythm-range-sweep: scripts/summarize_btt_tempo_sweep.py $(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)
	$(PYTHON) scripts/summarize_btt_tempo_sweep.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)"

test-summarize-btt-tempo-sweep: tests/test_summarize_btt_tempo_sweep.py scripts/summarize_btt_tempo_sweep.py
	$(PYTHON) tests/test_summarize_btt_tempo_sweep.py

.PHONY: inspect-beat-this-environment
inspect-beat-this-environment: scripts/inspect_beat_this_environment.py
	$(PYTHON) scripts/inspect_beat_this_environment.py

.PHONY: inspect-fretspark-sdk
inspect-fretspark-sdk: scripts/inspect_fretspark_sdk.sh
	bash scripts/inspect_fretspark_sdk.sh

.PHONY: inspect-fretspark-sdk-path
inspect-fretspark-sdk-path: scripts/inspect_fretspark_sdk.sh
	@test -n "$(FRETSPARK_SDK_PATH)"
	bash scripts/inspect_fretspark_sdk.sh FretSpark/fretspark_sdk $(FRETSPARK_SDK_PATH)

.PHONY: report-beat-this-gtzan-job
report-beat-this-gtzan-job: scripts/inspect_beat_this_environment.py
	$(PYTHON) scripts/inspect_beat_this_environment.py --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --diagnostic-log "$(BEAT_THIS_DIAGNOSTIC_LOG)"

.PHONY: install-beat-this-diagnostic test-measure-beat-this-bpm test-measure-beat-this-rolling-bpm test-beat-this-live-sidecar test-measure-beat-this-live-sidecar test-summarize-beat-this-sidecar-replay test-beat-this-obs-sidecar measure-beat-this-gtzan-rhythm measure-beat-this-ballroom measure-beat-this-filobass measure-beat-this-rolling-ballroom measure-beat-this-rolling-filobass measure-beat-this-continuous-ballroom measure-beat-this-continuous-filobass measure-beat-this-sidecar-ballroom measure-beat-this-sidecar-filobass measure-beat-this-sidecar-ballroom-prepared measure-beat-this-sidecar-filobass-prepared summarize-beat-this-sidecar-ballroom summarize-beat-this-sidecar-filobass audit-beat-this-continuous-interval-gate test-audit-beat-this-continuous-interval-gate summarize-beat-this-gtzan-rhythm summarize-beat-this-real-tempo summarize-beat-this-rolling-tempo
install-beat-this-diagnostic: configure-instrument-sample-store scripts/setup_beat_this_diagnostic.sh
	bash scripts/setup_beat_this_diagnostic.sh "$(BEAT_THIS_DIAGNOSTIC_ROOT)" "$(BEAT_THIS_RUNTIME_ROOT)" "$(PYTHON)"

test-measure-beat-this-bpm: tests/test_measure_beat_this_bpm.py scripts/measure_beat_this_bpm.py
	$(PYTHON) tests/test_measure_beat_this_bpm.py

test-measure-beat-this-rolling-bpm: tests/test_measure_beat_this_rolling_bpm.py scripts/measure_beat_this_rolling_bpm.py scripts/measure_beat_this_bpm.py
	$(PYTHON) tests/test_measure_beat_this_rolling_bpm.py

test-beat-this-live-sidecar: tests/test_beat_this_live_sidecar.py scripts/beat_this_live_sidecar.py scripts/measure_beat_this_bpm.py
	$(PYTHON) tests/test_beat_this_live_sidecar.py

test-measure-beat-this-live-sidecar: tests/test_measure_beat_this_live_sidecar.py scripts/measure_beat_this_live_sidecar.py scripts/beat_this_live_sidecar.py scripts/measure_beat_this_bpm.py
	$(PYTHON) tests/test_measure_beat_this_live_sidecar.py

test-beat-this-obs-sidecar: tests/test_beat_this_obs_sidecar.py src/plugin.cpp src/beat_this_sidecar_client.cpp
	$(PYTHON) tests/test_beat_this_obs_sidecar.py

test-summarize-beat-this-sidecar-replay: tests/test_summarize_beat_this_sidecar_replay.py scripts/summarize_beat_this_sidecar_replay.py
	$(PYTHON) tests/test_summarize_beat_this_sidecar_replay.py

test-summarize-beat-this-bpm: tests/test_summarize_beat_this_bpm.py scripts/summarize_beat_this_bpm.py
	$(PYTHON) tests/test_summarize_beat_this_bpm.py

measure-beat-this-gtzan-rhythm: install-beat-this-diagnostic prepare-gtzan-rhythm-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_DIAGNOSTIC_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-rolling-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_ROLLING_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-rolling-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_ROLLING_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)"

measure-beat-this-continuous-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --cadence-seconds 10 --minimum-stable-seconds 10

measure-beat-this-continuous-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_rolling_bpm.py
	env TORCH_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" XDG_CACHE_HOME="$(BEAT_THIS_DIAGNOSTIC_ROOT)/cache" $(PYTHON) scripts/measure_beat_this_rolling_bpm.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --cadence-seconds 10 --minimum-stable-seconds 10

measure-beat-this-sidecar-ballroom: install-beat-this-diagnostic prepare-ballroom-tempo-fixture scripts/measure_beat_this_live_sidecar.py
	+$(MAKE) measure-beat-this-sidecar-ballroom-prepared

measure-beat-this-sidecar-ballroom-prepared: scripts/measure_beat_this_live_sidecar.py
	$(PYTHON) scripts/measure_beat_this_live_sidecar.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_SIDECAR_BALLROOM_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --start "$(BEAT_THIS_SIDECAR_REPLAY_START)" --limit "$(BEAT_THIS_SIDECAR_REPLAY_LIMIT)"

measure-beat-this-sidecar-filobass: install-beat-this-diagnostic prepare-filobass-tempo-fixture scripts/measure_beat_this_live_sidecar.py
	+$(MAKE) measure-beat-this-sidecar-filobass-prepared

measure-beat-this-sidecar-filobass-prepared: scripts/measure_beat_this_live_sidecar.py
	$(PYTHON) scripts/measure_beat_this_live_sidecar.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --output "$(BEAT_THIS_SIDECAR_FILOBASS_LOG)" --runtime-root "$(BEAT_THIS_RUNTIME_ROOT)" --model-cache-root "$(BEAT_THIS_DIAGNOSTIC_ROOT)" --checkpoint "$(BEAT_THIS_DIAGNOSTIC_MODEL)" --start "$(BEAT_THIS_SIDECAR_REPLAY_START)" --limit "$(BEAT_THIS_SIDECAR_REPLAY_LIMIT)"

summarize-beat-this-sidecar-ballroom: scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_BALLROOM_LOG)
	$(PYTHON) scripts/summarize_beat_this_sidecar_replay.py "$(BEAT_THIS_SIDECAR_BALLROOM_LOG)" --output "$(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)"
	cat "$(BEAT_THIS_SIDECAR_BALLROOM_AUDIT)"

summarize-beat-this-sidecar-filobass: scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_FILOBASS_SHARD_LOGS)
	$(PYTHON) scripts/summarize_beat_this_sidecar_replay.py $(BEAT_THIS_SIDECAR_FILOBASS_SHARD_LOGS) --output "$(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)"
	cat "$(BEAT_THIS_SIDECAR_FILOBASS_AUDIT)"

audit-beat-this-continuous-interval-gate: scripts/audit_beat_this_continuous_interval_gate.py $(BEAT_THIS_CONTINUOUS_BALLROOM_LOG) $(BEAT_THIS_CONTINUOUS_FILOBASS_LOG) | $(BUILD_DIR)
	$(PYTHON) scripts/audit_beat_this_continuous_interval_gate.py "$(BEAT_THIS_CONTINUOUS_BALLROOM_LOG)" "$(BEAT_THIS_CONTINUOUS_FILOBASS_LOG)" --output "$(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)"
	cat "$(BEAT_THIS_CONTINUOUS_INTERVAL_GATE_AUDIT)"

test-audit-beat-this-continuous-interval-gate: scripts/audit_beat_this_continuous_interval_gate.py tests/test_audit_beat_this_continuous_interval_gate.py
	$(PYTHON) tests/test_audit_beat_this_continuous_interval_gate.py

summarize-beat-this-gtzan-rhythm: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_DIAGNOSTIC_LOG)"

summarize-beat-this-real-tempo: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_BALLROOM_LOG) $(BEAT_THIS_FILOBASS_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_BALLROOM_LOG)"
	$(PYTHON) scripts/summarize_beat_this_bpm.py --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_FILOBASS_LOG)"

summarize-beat-this-rolling-tempo: scripts/summarize_beat_this_bpm.py $(BEAT_THIS_ROLLING_BALLROOM_LOG) $(BEAT_THIS_ROLLING_FILOBASS_LOG)
	$(PYTHON) scripts/summarize_beat_this_bpm.py --prefix "Beat This rolling tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_ROLLING_BALLROOM_LOG)"
	$(PYTHON) scripts/summarize_beat_this_bpm.py --prefix "Beat This rolling tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BEAT_THIS_ROLLING_FILOBASS_LOG)"

summarize-permissive-beat-tracker-gtzan-rhythm: scripts/inspect_tempo_confidence_calibration.py $(BTT_GTZAN_RHYTHM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_GTZAN_RHYTHM_LOG)"

.PHONY: inspect-tempo-tracker-consensus test-inspect-tempo-tracker-consensus inspect-three-tempo-tracker-consensus inspect-high-tempo-three-tracker-consensus test-inspect-three-tempo-tracker-consensus
inspect-tempo-tracker-consensus: scripts/inspect_tempo_tracker_consensus.py $(BALLROOM_BPM_LOG) $(BTT_BALLROOM_LOG) $(FILOBASS_BPM_LOG) $(BTT_FILOBASS_LOG) $(GTZAN_RHYTHM_BPM_LOG) $(BTT_GTZAN_RHYTHM_LOG)
	$(PYTHON) scripts/inspect_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --phase-gates "$(TEMPO_CONSENSUS_PHASE_GATES)" --btt-gates "$(TEMPO_CONSENSUS_BTT_GATES)" --agreement-gates "$(TEMPO_CONSENSUS_AGREEMENT_GATES)" --corpus Ballroom "$(BALLROOM_BPM_LOG)" "$(BTT_BALLROOM_LOG)" --corpus FiloBass "$(FILOBASS_BPM_LOG)" "$(BTT_FILOBASS_LOG)" --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_GTZAN_RHYTHM_LOG)"

test-inspect-tempo-tracker-consensus: tests/test_inspect_tempo_tracker_consensus.py scripts/inspect_tempo_tracker_consensus.py
	$(PYTHON) tests/test_inspect_tempo_tracker_consensus.py

inspect-three-tempo-tracker-consensus: scripts/inspect_three_tempo_tracker_consensus.py $(BALLROOM_BPM_LOG) $(BTT_BALLROOM_LOG) $(BEAT_THIS_BALLROOM_LOG) $(FILOBASS_BPM_LOG) $(BTT_FILOBASS_LOG) $(BEAT_THIS_FILOBASS_LOG) $(GTZAN_RHYTHM_BPM_LOG) $(BTT_GTZAN_RHYTHM_LOG) $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/inspect_three_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --corpus Ballroom "$(BALLROOM_BPM_LOG)" "$(BTT_BALLROOM_LOG)" "$(BEAT_THIS_BALLROOM_LOG)" --corpus FiloBass "$(FILOBASS_BPM_LOG)" "$(BTT_FILOBASS_LOG)" "$(BEAT_THIS_FILOBASS_LOG)" --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_GTZAN_RHYTHM_LOG)" "$(BEAT_THIS_DIAGNOSTIC_LOG)" --output "$(THREE_TEMPO_TRACKER_CONSENSUS_LOG)"
	cat "$(THREE_TEMPO_TRACKER_CONSENSUS_LOG)"

inspect-high-tempo-three-tracker-consensus: scripts/inspect_three_tempo_tracker_consensus.py $(GTZAN_RHYTHM_BPM_LOG) $(BTT_HIGH_TEMPO_GTZAN_LOG) $(BEAT_THIS_DIAGNOSTIC_LOG)
	$(PYTHON) scripts/inspect_three_tempo_tracker_consensus.py --tolerance "$(BPM_DIAG_TOLERANCE)" --min-expected 150 --corpus GTZAN "$(GTZAN_RHYTHM_BPM_LOG)" "$(BTT_HIGH_TEMPO_GTZAN_LOG)" "$(BEAT_THIS_DIAGNOSTIC_LOG)" --output "$(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)"
	cat "$(HIGH_TEMPO_THREE_TEMPO_TRACKER_CONSENSUS_LOG)"

test-inspect-three-tempo-tracker-consensus: tests/test_inspect_three_tempo_tracker_consensus.py scripts/inspect_three_tempo_tracker_consensus.py
	$(PYTHON) tests/test_inspect_three_tempo_tracker_consensus.py

measure-permissive-beat-tracker-high-tempo: measure-permissive-beat-tracker-high-tempo-ballroom measure-permissive-beat-tracker-high-tempo-filobass measure-permissive-beat-tracker-high-tempo-gtzan-rhythm

measure-permissive-beat-tracker-high-tempo-ballroom: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(BALLROOM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(BALLROOM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_BALLROOM_LOG)"

measure-permissive-beat-tracker-high-tempo-filobass: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(FILOBASS_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(FILOBASS_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_FILOBASS_LOG)"

measure-permissive-beat-tracker-high-tempo-gtzan-rhythm: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py $(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)/maestro-v3.0.0.csv
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(GTZAN_RHYTHM_TEMPO_FIXTURE_DIR)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" > "$(BTT_HIGH_TEMPO_GTZAN_LOG)"

.PHONY: test-extract-btt-range-sweep measure-permissive-beat-tracker-tempo-chunk merge-permissive-beat-tracker-tempo-chunks extract-permissive-beat-tracker-high-tempo-gtzan-rhythm
test-extract-btt-range-sweep: tests/test_extract_btt_range_sweep.py scripts/extract_btt_range_sweep.py
	$(PYTHON) tests/test_extract_btt_range_sweep.py

measure-permissive-beat-tracker-tempo-chunk: $(BTT_PROBE) scripts/measure_permissive_beat_tracker.py
	$(PYTHON) scripts/measure_permissive_beat_tracker.py --root "$(BTT_TEMPO_CHUNK_ROOT)" --probe "$(BTT_PROBE)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)" --start-index "$(BTT_TEMPO_CHUNK_START)" --limit "$(BTT_TEMPO_CHUNK_LIMIT)" > "$(BTT_TEMPO_CHUNK_OUTPUT)"

merge-permissive-beat-tracker-tempo-chunks:
	cat $(BTT_TEMPO_CHUNK_INPUTS) > "$(BTT_TEMPO_CHUNK_OUTPUT)"

extract-permissive-beat-tracker-high-tempo-gtzan-rhythm: scripts/extract_btt_range_sweep.py $(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)
	$(PYTHON) scripts/extract_btt_range_sweep.py --input "$(BTT_GTZAN_RHYTHM_RANGE_SWEEP_LOG)" --output "$(BTT_HIGH_TEMPO_GTZAN_LOG)" --min-tempo "$(BTT_HIGH_TEMPO_MIN)"

summarize-permissive-beat-tracker-high-tempo: scripts/inspect_tempo_confidence_calibration.py $(BTT_HIGH_TEMPO_BALLROOM_LOG) $(BTT_HIGH_TEMPO_FILOBASS_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_HIGH_TEMPO_BALLROOM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_HIGH_TEMPO_FILOBASS_LOG)"

summarize-permissive-beat-tracker: scripts/inspect_tempo_confidence_calibration.py $(BTT_BALLROOM_LOG) $(BTT_FILOBASS_LOG) $(BTT_EGMD_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_BALLROOM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_FILOBASS_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "BTT tempo diag" --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BTT_EGMD_LOG)"

inspect-live-permissive-tracker: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

.PHONY: inspect-live-permissive-tracker-borderline
inspect-live-permissive-tracker-borderline: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" --details-min-confidence "$(LIVE_BTT_DETAILS_MIN_CONFIDENCE)" --details-max-confidence "$(LIVE_BTT_DETAILS_MAX_CONFIDENCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field backend_raw --confidence-field backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" --details-min-confidence "$(LIVE_BTT_DETAILS_MIN_CONFIDENCE)" --details-max-confidence "$(LIVE_BTT_DETAILS_MAX_CONFIDENCE)" "$(FILOBASS_BPM_LOG)"

.PHONY: inspect-live-high-tempo-tracker
inspect-live-high-tempo-tracker: scripts/inspect_tempo_confidence_calibration.py $(BALLROOM_BPM_LOG) $(FILOBASS_BPM_LOG)
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field high_backend_raw --confidence-field high_backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(BALLROOM_BPM_LOG)"
	$(PYTHON) scripts/inspect_tempo_confidence_calibration.py --prefix "MAESTRO tempo diag" --estimate-field high_backend_raw --confidence-field high_backend_confidence --fallback-only-field phase_confidence --tolerance "$(BPM_DIAG_TOLERANCE)" "$(FILOBASS_BPM_LOG)"

inspect-beat-tracker-backends: scripts/inspect_beat_tracker_backends.py
	$(PYTHON) scripts/inspect_beat_tracker_backends.py

analyze-bpm-diagnostics: analyze-egmd-bpm

test-core-parallel: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) test_core_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) test-visualizer-renderer test-analyzer-internal test-analyzer-smoke test-analyzer-cases test-analyzer-midi-ranges test-analyzer-urmp test-analyzer-musicnet test-analyzer-multtipop test-analyzer-guitarset test-analyzer-maestro test-analyzer-egmd

ANALYSIS_SCRIPT_TEST_TARGETS := inspect-real-dataset-catalog inspect-real-goal-coverage test-musicnet-remote test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-synthsod-remote test-synthsod-archive-extract test-synthsod-inspector test-synthsod-prepare test-polyvocal-inspector test-polyvocal-prepare test-prepared-multitrack-inspector test-prepared-multitrack-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-drum-sample-prepare test-hf-drum-kit-prepare test-idmt-drums-prepare test-mdb-drums-prepare test-star-drums-prepare test-medley-solos-prepare test-maps-piano-prepare test-bach10-mf0-synth-prepare test-instrument-sample-attribute-summary test-instrument-sample-owner-buckets test-filter-instrument-attribute-rows test-filter-drum-attribute-rows test-instrument-owner-patterns test-refresh-analyzer-detected-attribute-rows test-print-analyzer-detected-attributes test-analyzer-pattern-report test-measure-analyzer-patterns-target test-build-sharded-tsv test-drum-sample-shard-check test-egmd-shard-check test-maestro-shard-check test-instrument-family-shard-check test-musicnet-shard-check test-real-note-full-mix-shard-check test-real-note-sample-shard-check test-guitarset-shard-check test-philharmonia-prepare test-good-sounds-prepare test-iowa-piano-prepare test-iowa-zip-prepare test-idmt-bass-lines-prepare test-idmt-guitar-prepare test-tinysol-prepare test-vocadito-prepare test-vocalset-prepare test-guitar-fretboard-note-prepare test-guitar-techs-prepare test-guitar-techs-chord-prepare test-guitar-chord-mix-prepare test-gaps-guitar-prepare test-guitarset-miss-analysis test-guitarset-attribute-summary test-guitarset-attribute-buckets test-guitarset-attribute-patterns test-guitar-chord-recovery-analysis test-guitar-primary-order-analysis test-guitar-chord-extra-components-analysis test-real-note-miss-analysis test-real-note-attribute-summary test-real-note-attribute-buckets test-real-note-attribute-patterns test-real-note-attribute-rule test-real-note-display-shadow-eval test-egmd-miss-analysis test-egmd-drum-attribute-summary test-egmd-drum-recovery-eval test-drum-debug-row-analysis test-drum-primary-analysis test-drum-gate-matrix-summary test-drum-active-threshold-simulation test-drum-active-false-summary test-drum-active-false-patterns test-real-goal-script android-check
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-rule-flag-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-vocal-exact-note-cross-corpus
ANALYSIS_SCRIPT_TEST_TARGETS += test-maps-piano-attribute-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-compare-drum-gate-summaries
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-octave-display-aliases
ANALYSIS_SCRIPT_TEST_TARGETS += test-real-note-vocal-display-fallback-eval
ANALYSIS_SCRIPT_TEST_TARGETS += test-detector-route-report-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-drum-sample-skip-patterns
ANALYSIS_SCRIPT_TEST_TARGETS += test-sample-manifest-summary
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-drum-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-real-note-candidate-rows
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-detector-coverage-candidates test-compare-drum-primary-scores
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-good-sounds-archive-coverage
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-polyphonic-candidate-capacity test-inspect-harmonic-product-octave-evidence test-detection-accuracy-report test-summarize-isolated-guitar-visual
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-tempo-candidate-feasibility
ANALYSIS_SCRIPT_TEST_TARGETS += test-inspect-urmp-bass-timing
ANALYSIS_SCRIPT_TEST_TARGETS += test-search-egmd-false-positive-caps
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-drum-false-positive-caps
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-drum-false-positive-contexts
ANALYSIS_SCRIPT_TEST_TARGETS += test-audit-chord-primary-components

test-drum-sample-shard-check: tests/test_check_drum_sample_shards.py scripts/check_drum_sample_shards.py
	$(PYTHON) tests/test_check_drum_sample_shards.py

test-maps-piano-attribute-summary: tests/test_analyze_maps_piano_attributes.py scripts/analyze_maps_piano_attributes.py
	$(PYTHON) tests/test_analyze_maps_piano_attributes.py

test-instrument-family-attribute-summary: tests/test_summarize_instrument_family_attributes.py scripts/summarize_instrument_family_attributes.py
	$(PYTHON) tests/test_summarize_instrument_family_attributes.py

test-inspect-drum-candidate-rows: tests/test_inspect_drum_candidate_rows.py scripts/inspect_drum_candidate_rows.py
	$(PYTHON) tests/test_inspect_drum_candidate_rows.py

test-inspect-real-note-candidate-rows: tests/test_inspect_real_note_candidate_rows.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_real_note_candidate_rows.py

test-inspect-detector-coverage-candidates: tests/test_inspect_detector_coverage_candidates.py scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	$(PYTHON) tests/test_inspect_detector_coverage_candidates.py

test-inspect-good-sounds-archive-coverage: tests/test_inspect_good_sounds_archive_coverage.py scripts/inspect_good_sounds_archive_coverage.py scripts/prepare_good_sounds_samples.py
	$(PYTHON) tests/test_inspect_good_sounds_archive_coverage.py

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

DRUM_PRIMARY_ROUTE_EXPECTED ?= hihat
DRUM_PRIMARY_ROUTE_PRIMARY ?= none
DRUM_PRIMARY_ROUTE_LIMIT ?= 5

.PHONY: inspect-drum-primary-route
inspect-drum-primary-route: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/inspect_drum_primary_route.py
	$(PYTHON) scripts/inspect_drum_primary_route.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --expected "$(DRUM_PRIMARY_ROUTE_EXPECTED)" --primary "$(DRUM_PRIMARY_ROUTE_PRIMARY)" --limit "$(DRUM_PRIMARY_ROUTE_LIMIT)"

.PHONY: summarize-drum-primary-routes
summarize-drum-primary-routes: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/summarize_drum_primary_routes.py
	$(PYTHON) scripts/summarize_drum_primary_routes.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"

.PHONY: inspect-analyzer-ride-hihat
inspect-analyzer-ride-hihat: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "ride_hihat"

.PHONY: inspect-fret-zealot
inspect-fret-zealot: scripts/inspect_fret_zealot.py
	$(PYTHON) scripts/inspect_fret_zealot.py

.PHONY: inspect-fret-zealot-packet
inspect-fret-zealot-packet: scripts/inspect_source_range.py src/fret_control.cpp
	$(PYTHON) scripts/inspect_source_range.py src/fret_control.cpp 390 500

.PHONY: inspect-fret-zealot-integration
inspect-fret-zealot-integration: scripts/inspect_fret_zealot_integration.py
	$(PYTHON) scripts/inspect_fret_zealot_integration.py

.PHONY: inspect-fret-zealot-frames
inspect-fret-zealot-frames: scripts/inspect_fret_zealot_frames.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java
	$(PYTHON) scripts/inspect_fret_zealot_frames.py

.PHONY: inspect-fret-zealot-update-path
inspect-fret-zealot-update-path: scripts/inspect_source_range.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java
	$(PYTHON) scripts/inspect_source_range.py android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java 90 250

.PHONY: inspect-fret-zealot-android-tests
inspect-fret-zealot-android-tests: scripts/inspect_source_range.py tests/check_android_project.py
	$(PYTHON) scripts/inspect_source_range.py tests/check_android_project.py 1 90

.PHONY: test-fret-zealot-android-dispatch
test-fret-zealot-android-dispatch: tests/check_android_project.py
	$(PYTHON) tests/check_android_project.py

.PHONY: list-android-make-targets
list-android-make-targets: scripts/list_android_make_targets.py Makefile
	$(PYTHON) scripts/list_android_make_targets.py

.PHONY: inspect-android-native-cmake
inspect-android-native-cmake: scripts/inspect_source_range.py android/app/src/main/cpp/CMakeLists.txt
	$(PYTHON) scripts/inspect_source_range.py android/app/src/main/cpp/CMakeLists.txt 1 220

.PHONY: inspect-basic-pitch-android-guards
inspect-basic-pitch-android-guards: scripts/inspect_basic_pitch_android_guards.py
	$(PYTHON) scripts/inspect_basic_pitch_android_guards.py

.PHONY: inspect-basic-pitch-runtime
inspect-basic-pitch-runtime: scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.cpp
	$(PYTHON) scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.cpp 1 230

.PHONY: inspect-basic-pitch-runtime-header
inspect-basic-pitch-runtime-header: scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.hpp
	$(PYTHON) scripts/inspect_source_range.py src/basic_pitch_onnx_runtime.hpp 1 180

.PHONY: repository-state
repository-state: scripts/report_repository_state.sh
	$(SHELL) scripts/report_repository_state.sh

.PHONY: report-analyzer-case-processes
report-analyzer-case-processes: scripts/report_analyzer_case_processes.sh
	$(SHELL) scripts/report_analyzer_case_processes.sh

.PHONY: report-drum-pattern-processes
report-drum-pattern-processes: scripts/report_drum_pattern_processes.sh
	$(SHELL) scripts/report_drum_pattern_processes.sh

.PHONY: report-egmd-processes
report-egmd-processes: scripts/report_egmd_processes.sh
	$(SHELL) scripts/report_egmd_processes.sh

.PHONY: wait-for-drum-pattern-processes
wait-for-drum-pattern-processes: scripts/wait_for_drum_pattern_processes.py
	$(PYTHON) scripts/wait_for_drum_pattern_processes.py

.PHONY: analyze-tom-snare-primary
analyze-tom-snare-primary: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/analyze_tom_snare_primary.py
	$(PYTHON) scripts/analyze_tom_snare_primary.py

.PHONY: inspect-analyzer-tom-snare
inspect-analyzer-tom-snare: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "tom_from_snare_primary_recovery"

.PHONY: analyze-hihat-none
analyze-hihat-none: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/analyze_hihat_none.py
	$(PYTHON) scripts/analyze_hihat_none.py

.PHONY: inspect-drum-debug-flags
inspect-drum-debug-flags: scripts/inspect_analyzer_section.py src/analyzer.hpp
	$(PYTHON) scripts/inspect_analyzer_section.py --source src/analyzer.hpp --topic "DrumDebug"

.PHONY: inspect-analyzer-hihat-activation
inspect-analyzer-hihat-activation: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "drum_level_[HiHat] ="

.PHONY: inspect-analyzer-hihat-caps
inspect-analyzer-hihat-caps: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "cap_drum_level(HiHat"

.PHONY: inspect-analyzer-drum-activation-block
inspect-analyzer-drum-activation-block: scripts/inspect_source_range.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_source_range.py src/analyzer.cpp 31700 32200

.PHONY: inspect-analyzer-drum-transient
inspect-analyzer-drum-transient: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "drum_transient ="

.PHONY: inspect-analyzer-drum-transient-threshold
inspect-analyzer-drum-transient-threshold: scripts/inspect_analyzer_section.py src/analyzer.cpp
	$(PYTHON) scripts/inspect_analyzer_section.py --topic "kDrumTransientRatio"

.PHONY: evaluate-hihat-activation-candidate
evaluate-hihat-activation-candidate: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/evaluate_hihat_activation_candidate.py
	$(PYTHON) scripts/evaluate_hihat_activation_candidate.py

.PHONY: inspect-mdb-drum-shards
inspect-mdb-drum-shards: scripts/inspect_mdb_drum_shards.py
	$(PYTHON) scripts/inspect_mdb_drum_shards.py

.PHONY: inspect-egmd-test-options
inspect-egmd-test-options: scripts/inspect_egmd_test_options.py tests/analyzer_egmd.cpp
	$(PYTHON) scripts/inspect_egmd_test_options.py

.PHONY: inspect-mdb-hihat-misses
inspect-mdb-hihat-misses: scripts/inspect_mdb_hihat_misses.py
	$(PYTHON) scripts/inspect_mdb_hihat_misses.py

.PHONY: mine-mdb-hihat-selectors
mine-mdb-hihat-selectors: analyze-mdb-drum-windows scripts/mine_mdb_hihat_selectors.py
	$(PYTHON) scripts/mine_mdb_hihat_selectors.py

.PHONY: inspect-mdb-drum-target
inspect-mdb-drum-target: scripts/inspect_source_range.py Makefile
	$(PYTHON) scripts/inspect_source_range.py Makefile 3440 3520

.PHONY: inspect-egmd-recovery-evaluator
inspect-egmd-recovery-evaluator: scripts/inspect_source_range.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) scripts/inspect_source_range.py scripts/evaluate_egmd_drum_recovery.py 1 360

.PHONY: stop-analyzer-case-processes
stop-analyzer-case-processes: scripts/stop_analyzer_case_processes.py
	$(PYTHON) scripts/stop_analyzer_case_processes.py

.PHONY: inspect-fret-zealot-dispatch
inspect-fret-zealot-dispatch: scripts/inspect_fret_zealot_dispatch.py
	$(PYTHON) scripts/inspect_fret_zealot_dispatch.py

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

test-pitch-shifted-violin-prepare: tests/test_prepare_pitch_shifted_violin_samples.py scripts/prepare_pitch_shifted_violin_samples.py
	$(PYTHON) tests/test_prepare_pitch_shifted_violin_samples.py

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

test-good-sounds-bass-miss-inspector: tests/test_inspect_good_sounds_bass_misses.py scripts/inspect_good_sounds_bass_misses.py
	$(PYTHON) tests/test_inspect_good_sounds_bass_misses.py

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

.PHONY: test-search-egmd-false-positive-caps
test-search-egmd-false-positive-caps: tests/test_search_egmd_false_positive_caps.py scripts/search_egmd_false_positive_caps.py scripts/evaluate_egmd_drum_recovery.py
	$(PYTHON) tests/test_search_egmd_false_positive_caps.py

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

.PHONY: download-real-urmp inspect-real-urmp-download prepare-real-urmp inspect-urmp-bass-timing test-inspect-urmp-bass-timing analyze-real-urmp-traits analyze-real-urmp-miss-traits summarize-real-urmp-miss-traits summarize-real-urmp-chord-miss-traits summarize-real-urmp-wrong-notes prepare-urmp-sax-exact-fixture measure-urmp-sax-exact measure-urmp-sax-full-mix find-urmp-sax-full-mix-row-confusion-patterns find-urmp-sax-full-mix-first-row-confusion-patterns find-urmp-good-sounds-sax-shared-routing-patterns analyze-urmp-sax-exact test-prepare-urmp-sax-exact-fixture test-urmp-download-scripts test-urmp-archive-extract download-real-musicnet inspect-real-musicnet-download prepare-real-musicnet inspect-downloaded-real-musicnet-20-traits analyze-downloaded-real-musicnet-recording analyze-downloaded-real-musicnet-chord-misses test-downloaded-real-musicnet-20 test-downloaded-real-musicnet-full test-musicnet-archive-extract test-run-musicnet-gate test-summarize-musicnet-attributes
download-real-urmp: $(URMP_ARCHIVE)

inspect-real-urmp-download: scripts/urmp_download_status.sh
	$(SHELL) scripts/urmp_download_status.sh "$(URMP_ARCHIVE)"

test-urmp-download-scripts: scripts/download_urmp_archive.sh scripts/urmp_download_status.sh tests/test_urmp_download_scripts.py
	$(PYTHON) -m pytest -q tests/test_urmp_download_scripts.py

prepare-real-urmp: $(URMP_ARCHIVE) scripts/extract_urmp_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/extract_urmp_archive.sh "$(URMP_ARCHIVE)" "$(URMP_EXTRACT_DIR)"

inspect-urmp-bass-timing: scripts/inspect_urmp_bass_timing.py | $(BUILD_DIR)
	@test -d "$(URMP_EXTRACT_DIR)/Dataset" || { printf '%s\n' "missing extracted URMP Dataset; run make prepare-real-urmp"; exit 2; }
	$(PYTHON) scripts/inspect_urmp_bass_timing.py --root "$(URMP_EXTRACT_DIR)" --output "$(URMP_BASS_TIMING_AUDIT)"

test-inspect-urmp-bass-timing: tests/test_inspect_urmp_bass_timing.py scripts/inspect_urmp_bass_timing.py
	$(PYTHON) tests/test_inspect_urmp_bass_timing.py

prepare-urmp-sax-exact-fixture: prepare-real-urmp $(URMP_SAX_EXACT_FIXTURE_MANIFEST)

$(URMP_SAX_EXACT_FIXTURE_MANIFEST): scripts/prepare_urmp_sax_exact_fixture.py | $(BUILD_DIR)
	@test -d "$(URMP_EXTRACT_DIR)/Dataset" || { printf '%s\n' "missing extracted URMP Dataset; run make prepare-real-urmp"; exit 1; }
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=urmp_sax_exact_fixture
	$(PYTHON) scripts/prepare_urmp_sax_exact_fixture.py --source-root "$(URMP_EXTRACT_DIR)/Dataset" --output "$(URMP_SAX_EXACT_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)"

test-prepare-urmp-sax-exact-fixture: tests/test_prepare_urmp_sax_exact_fixture.py scripts/prepare_urmp_sax_exact_fixture.py
	$(PYTHON) tests/test_prepare_urmp_sax_exact_fixture.py

measure-urmp-sax-exact: $(BUILD_DIR)/analyzer_real_note_samples $(URMP_SAX_EXACT_FIXTURE_MANIFEST) | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(URMP_SAX_EXACT_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(URMP_SAX_EXACT_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(URMP_SAX_EXACT_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(URMP_SAX_EXACT_OUTPUT)"

measure-urmp-sax-full-mix: $(BUILD_DIR)/analyzer_real_note_samples $(URMP_SAX_EXACT_FIXTURE_MANIFEST) | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(URMP_SAX_FULL_MIX_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(URMP_SAX_EXACT_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(URMP_SAX_FULL_MIX_OUTPUT)"

find-urmp-good-sounds-sax-shared-routing-patterns: $(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)
	@cat "$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)"

$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT): FORCE $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV) $(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV) $(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV) $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@raw="$@.$$$$.raw"; tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --extra-protected-path "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" --bucket "row_confusion:other/*->piano" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --show-examples 2 --show-near-misses 12 --protected-scope all --profile-fields 8 > "$$raw" 2>&1; status="$$?"; count="$$(awk '/^  \+.*net_rows=/ { count += 1 } END { print count + 0 }' "$$raw")"; { printf 'shared_sax_candidates=%s\n' "$$count"; cat "$$raw"; } > "$$tmp"; rm -f "$$raw"; mv "$$tmp" "$@"; exit "$$status"

.PHONY: find-cross-corpus-octave-correction-patterns
find-cross-corpus-octave-correction-patterns: $(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)
	@cat "$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)"

# A detector-level octave correction must work across unrelated orchestral
# captures and preserve all existing real-note, saxophone, and duet evidence.
$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT): FORCE scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(KRAISLER_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached octave-audit input: $$path"; exit 2; }; done
	@raw="$@.$$$$.raw"; tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --extra-candidate-path "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" --extra-candidate-path "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" --extra-protected-path "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(KRAISLER_ATTRIBUTE_OUTPUT)" --bucket "octave_displacement:other/*->+36" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 4 --show-examples 3 --show-near-misses 10 --protected-scope all --profile-fields 10 > "$$raw" 2>&1; status="$$?"; count="$$(awk '/^  \+.*net_rows=/ { count += 1 } END { print count + 0 }' "$$raw")"; { printf 'shared_octave_correction_candidates=%s\n' "$$count"; cat "$$raw"; } > "$$tmp"; rm -f "$$raw"; mv "$$tmp" "$@"; exit "$$status"

find-urmp-sax-full-mix-row-confusion-patterns: $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

find-urmp-sax-full-mix-first-row-confusion-patterns: $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

analyze-urmp-sax-exact: $(URMP_SAX_EXACT_ATTRIBUTE_TSV) scripts/analyze_exact_midi_misses.py
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(URMP_SAX_EXACT_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

analyze-real-urmp-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_measurement.sh
	$(SHELL) scripts/capture_urmp_measurement.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_MEASUREMENT_OUTPUT)"

analyze-real-urmp-miss-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_trait_sample.sh
	$(SHELL) scripts/capture_urmp_trait_sample.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_MEASUREMENT_OUTPUT)"

summarize-real-urmp-miss-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-chord-miss-traits: scripts/summarize_urmp_chord_misses.py
	$(PYTHON) scripts/summarize_urmp_chord_misses.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-wrong-notes: scripts/summarize_urmp_wrong_notes.py
	$(PYTHON) scripts/summarize_urmp_wrong_notes.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

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

analyze-downloaded-real-musicnet-chord-misses: scripts/analyze_musicnet_chord_misses.py
	$(PYTHON) scripts/analyze_musicnet_chord_misses.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

.PHONY: summarize-downloaded-real-musicnet-attributes summarize-downloaded-real-musicnet-routing test-summarize-musicnet-routing audit-dominant-seventh-extension test-audit-dominant-seventh-extension
summarize-downloaded-real-musicnet-attributes: scripts/summarize_musicnet_attributes.py
	$(PYTHON) scripts/summarize_musicnet_attributes.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

summarize-downloaded-real-musicnet-routing: $(MUSICNET_FULL_ATTRIBUTE_OUTPUT) scripts/summarize_musicnet_routing.py
	$(PYTHON) scripts/summarize_musicnet_routing.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" --output "$(MUSICNET_ROUTING_OUTPUT)"

# Compare the same normalized raw-chroma predicate across independent chord
# corpora before any dominant-seventh display extension is considered.
audit-dominant-seventh-extension: scripts/audit_dominant_seventh_extensions.py
	@for path in "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached dominant-seventh audit input: $$path"; exit 2; }; done
	@tmp="$(DOMINANT_SEVENTH_EXTENSION_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_dominant_seventh_extensions.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" > "$$tmp" && mv "$$tmp" "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)"
	@cat "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)"

test-audit-dominant-seventh-extension: tests/test_audit_dominant_seventh_extensions.py scripts/audit_dominant_seventh_extensions.py
	$(PYTHON) tests/test_audit_dominant_seventh_extensions.py

.PHONY: analyze-choir-chord-traits
analyze-choir-chord-traits: scripts/summarize_musicnet_attributes.py
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached choir chord input: $$path"; exit 2; }; done
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do printf '%s\n' "=== $$path ==="; $(PYTHON) scripts/summarize_musicnet_attributes.py "$$path"; done

.PHONY: audit-global-chord-confidence
audit-global-chord-confidence: scripts/audit_global_chord_confidence.py
	@for path in "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached global-chord confidence input: $$path"; exit 2; }; done
	@tmp="$(GLOBAL_CHORD_CONFIDENCE_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_global_chord_confidence.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)" && cat "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)"

.PHONY: test-audit-global-chord-confidence
test-audit-global-chord-confidence: tests/test_audit_global_chord_confidence.py scripts/audit_global_chord_confidence.py
	$(PYTHON) tests/test_audit_global_chord_confidence.py

test-summarize-musicnet-routing: tests/test_summarize_musicnet_routing.py scripts/summarize_musicnet_routing.py
	$(PYTHON) tests/test_summarize_musicnet_routing.py

.PHONY: inspect-downloaded-real-musicnet-chord-traits
inspect-downloaded-real-musicnet-chord-traits: scripts/inspect_musicnet_chord_traits.py
	$(PYTHON) scripts/inspect_musicnet_chord_traits.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

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
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 $(BUILD_DIR)/analyzer_guitarset

test-real-guitarset-full: $(BUILD_DIR)/analyzer_guitarset tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=360 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1440 $(BUILD_DIR)/analyzer_guitarset

test-real-maestro-20: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-real-maestro-full: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1276 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=5104 $(BUILD_DIR)/analyzer_maestro

test-real-egmd-20: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 $(BUILD_DIR)/analyzer_egmd

test-real-egmd-full: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=45537 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=182148 $(BUILD_DIR)/analyzer_egmd

.PHONY: inspect-instrument-sample-store configure-instrument-sample-store test-instrument-sample-store inspect-sample-build-migration migrate-sample-build-directories inspect-build-sample-relocation compare-build-sample-relocation-conflicts relocate-build-sample-directories deduplicate-build-sample-directories merge-build-sample-directories test-sample-build-migration test-instrument-family-miss-inspector

inspect-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --status --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

configure-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

inspect-sample-build-migration: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --status --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

migrate-sample-build-directories: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

inspect-build-sample-relocation: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --dry-run

compare-build-sample-relocation-conflicts: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --compare-conflicts

relocate-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --apply

deduplicate-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --deduplicate-identical

merge-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --merge-nonconflicting

test-instrument-sample-store: tests/test_configure_instrument_sample_store.py scripts/configure_instrument_sample_store.py
	$(PYTHON) tests/test_configure_instrument_sample_store.py

test-sample-build-migration: tests/test_migrate_sample_build_directories.py scripts/migrate_sample_build_directories.py
	$(PYTHON) tests/test_migrate_sample_build_directories.py

test-instrument-family-miss-inspector: tests/test_inspect_instrument_family_misses.py scripts/inspect_instrument_family_misses.py
	$(PYTHON) tests/test_inspect_instrument_family_misses.py

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
	mkdir -p $(OBS_USER_PLUGIN_DATA_DIR)
	cp $(ONNXRUNTIME_LIBRARY) $(OBS_USER_PLUGIN_DATA_DIR)/libonnxruntime.so
	cp $(BASIC_PITCH_ONNX_MODEL) $(OBS_USER_PLUGIN_DATA_DIR)/nmp.onnx

.PHONY: clean-legacy-basic-pitch-user-data
# One-time cleanup for the path used before OBS_USER_PLUGIN_ROOT was resolved
# correctly.  It targets only files installed by this plugin revision.
clean-legacy-basic-pitch-user-data:
	rm -rf "$(OBS_USER_PLUGIN_ROOT)/bin/data/basic_pitch"

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
inspect-analyzer-hihat-cap-sites:
	$(PYTHON) scripts/inspect_hihat_cap_sites.py
summarize-mdb-hihat-cap:
	$(PYTHON) scripts/summarize_mdb_hihat_cap.py
inspect-egmd-verbose-output:
	$(PYTHON) scripts/inspect_egmd_verbose_output.py
list-mdb-early-hihat-candidates:
	$(PYTHON) scripts/list_mdb_early_hihat_candidates.py
mine-mdb-drum-selectors:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/mine_mdb_drum_selectors.py
inspect-analyzer-kick-cap-sites:
	$(PYTHON) scripts/inspect_kick_cap_sites.py
mine-mdb-drum-pair-selectors:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/mine_mdb_drum_pair_selectors.py
list-mdb-snare-candidates:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/list_mdb_snare_candidates.py
summarize-mdb-crash-recovery:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/summarize_mdb_crash_recovery.py
analyze-star-drums-verbose-windows:
	$(PYTHON) scripts/analyze_star_drum_verbose_windows.py

list-star-hihat-misses:
	$(MAKE) analyze-star-drums-verbose-windows
	$(PYTHON) scripts/list_star_hihat_misses.py
inspect-fret-zealot-auto-root:
	python3 scripts/inspect_fret_zealot_auto_root.py
report-idmt-drums-processes:
	python3 scripts/report_idmt_drums_processes.py
wait-idmt-drums-processes:
	python3 scripts/wait_idmt_drums_processes.py
summarize-idmt-drums-results:
	python3 scripts/summarize_idmt_drums_results.py
inspect-analyzer-case-hihat-regression:
	python3 scripts/inspect_analyzer_case_hihat_regression.py
wait-analyzer-cases-process:
	python3 scripts/wait_analyzer_cases_process.py
report-analyzer-cases-process:
	python3 scripts/report_analyzer_cases_process.py
plan-stop-duplicate-analyzer-cases:
	python3 scripts/manage_duplicate_analyzer_cases.py plan

apply-stop-duplicate-analyzer-cases:
	python3 scripts/manage_duplicate_analyzer_cases.py apply
test-analyzer-hihat-regression:
	/bin/sh scripts/run_analyzer_hihat_regression.sh
inspect-drum-transient-gate:
	python3 scripts/inspect_drum_transient_gate.py
inspect-mdb-hihat-trigger-evidence:
	python3 scripts/inspect_mdb_hihat_trigger_evidence.py
inspect-analyzer-test-object-rule:
	python3 scripts/inspect_analyzer_test_object_rule.py
test-analyzer-cases-logged:
	python3 scripts/run_analyzer_cases_logged.py

summarize-analyzer-cases-log:
	python3 scripts/summarize_analyzer_cases_log.py
list-real-note-test-targets:
	python3 scripts/list_real_note_test_targets.py
inspect-analyzer-cases-main:
	python3 scripts/inspect_analyzer_cases_main.py
summarize-hf-ride-primary-misses:
	python3 scripts/summarize_hf_ride_primary_misses.py
inspect-drum-sample-verbose-controls:
	python3 scripts/inspect_drum_sample_verbose_controls.py

print-drum-sample-verbose-controls:
	python3 scripts/print_drum_sample_verbose_controls.py

inspect-drum-sample-verbose-output:
	python3 scripts/inspect_drum_sample_verbose_output.py

inspect-hf-drum-kit-target:
	python3 scripts/inspect_make_target.py

report-hf-ride-primary-attributes: build/hf_drum_kit_primary_attribute_rows_ride.tsv
	python3 scripts/report_hf_ride_primary_attributes.py

inspect-primary-drum-arbitration:
	python3 scripts/inspect_primary_drum_arbitration.py

inspect-hihat-ride-arbitration:
	python3 scripts/inspect_hihat_ride_arbitration.py

evaluate-hihat-ride-primary-recovery: build/hf_drum_kit_primary_attribute_rows_ride.tsv build/hf_drum_kit_primary_attribute_rows_hihat.tsv
	python3 scripts/evaluate_hihat_ride_primary_recovery.py

report-hf-drum-test-status:
	python3 scripts/report_hf_drum_test_status.py

report-hf-snare-ride-hihat-collisions: build/hf_drum_kit_primary_attribute_rows_snare.tsv
	python3 scripts/report_hf_snare_ride_hihat_collisions.py

verify-drum-regression-targets:
	python3 scripts/verify_drum_regression_targets.py

test-drum-regressions-parallel: verify-drum-regression-targets
	python3 scripts/run_drum_regressions_parallel.py

report-drum-regression-logs:
	python3 scripts/report_drum_regression_logs.py

report-drum-test-controls:
	python3 scripts/report_drum_test_controls.py

report-external-fixture-links:
	python3 scripts/report_external_fixture_links.py

profile-drum-primary-confusions: build/analyzer_drum_samples
	python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-hihat: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=hihat python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-snare: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=snare python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-ride: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=ride python3 scripts/profile_drum_primary_confusions.py

test-drum-tom-primary-regression: build/analyzer_drum_samples
	python3 scripts/test_drum_tom_primary_regression.py

report-drum-tom-body-snare-tie-tom: build/analyzer_drum_samples
	DRUM_RULE_HIT_CATEGORY=tom python3 scripts/report_drum_rule_hits.py

report-drum-tom-body-snare-tie-snare: build/analyzer_drum_samples
	DRUM_RULE_HIT_CATEGORY=snare python3 scripts/report_drum_rule_hits.py

report-drum-classifier-source:
	python3 scripts/report_drum_classifier_source.py

report-spread-rim-ride-hihat-collisions: build/drum_spread_exact_attribute_rows_rim.tsv
	python3 scripts/report_spread_rim_ride_hihat_collisions.py

report-spread-drum-shards:
	python3 scripts/report_spread_drum_shards.py

inspect-complex-real-timbres:
	python3 scripts/inspect_complex_real_timbres.py

list-ready-real-audio-evidence:
	python3 scripts/list_ready_real_audio_evidence.py

summarize-gaps-guitar-attributes:
	python3 scripts/summarize_gaps_guitar_attributes.py

inspect-caged-root-regression:
	python3 scripts/inspect_caged_root_regression.py

inspect-analyzer-hihat-regression-test:
	python3 scripts/inspect_analyzer_hihat_regression_test.py

inspect-analyzer-caged-root-runtime: build/analyzer_test.o tests/analyzer_caged_root_regression.cpp scripts/run_analyzer_caged_root_regression.sh
	sh scripts/run_analyzer_caged_root_regression.sh

inspect-analysis-snapshot:
	python3 scripts/inspect_analysis_snapshot.py

inspect-chord-template-ranking:
	python3 scripts/inspect_chord_template_ranking.py

inspect-global-chord-path:
	python3 scripts/inspect_global_chord_path.py

inspect-global-chord-tracking:
	python3 scripts/inspect_global_chord_tracking.py

inspect-mixed-global-display-chord:
	python3 scripts/inspect_mixed_global_display_chord.py

inspect-stronger-chord:
	python3 scripts/inspect_stronger_chord.py

inspect-global-chroma-construction:
	python3 scripts/inspect_global_chroma_construction.py

plan-stage-verified-drum-changes:
	python3 scripts/plan_stage_verified_drum_changes.py

list-idmt-drum-evidence:
	python3 scripts/list_idmt_drum_evidence.py

summarize-idmt-hihat-attributes:
	python3 scripts/summarize_idmt_hihat_attributes.py

evaluate-idmt-hihat-recovery:
	python3 scripts/evaluate_idmt_hihat_recovery.py
.PHONY: inspect-idmt-hihat-suppression
inspect-idmt-hihat-suppression:
	python3 scripts/inspect_idmt_hihat_suppression.py
.PHONY: evaluate-gaps-guitar-misses
evaluate-gaps-guitar-misses:
	python3 scripts/evaluate_gaps_guitar_misses.py
.PHONY: inspect-make-targets
inspect-make-targets:
	python3 scripts/inspect_make_targets.py
.PHONY: inspect-vocal-make-targets
inspect-vocal-make-targets:
	python3 scripts/inspect_make_targets.py vocal
.PHONY: report-vocalset-test-state
report-vocalset-test-state:
	python3 scripts/report_vocalset_test_state.py
.PHONY: wait-vocalset-test-state
wait-vocalset-test-state:
	python3 scripts/wait_vocalset_test_state.py
.PHONY: inspect-guitar-chord-primary-promotion
inspect-guitar-chord-primary-promotion:
	python3 scripts/inspect_guitar_chord_primary_promotion.py
.PHONY: inspect-guitar-extension-promotion-core
inspect-guitar-extension-promotion-core:
	$(PYTHON) scripts/inspect_source_range.py src/analyzer.cpp 18670 18870
.PHONY: report-analyzer-build-state
report-analyzer-build-state:
	python3 scripts/report_analyzer_build_state.py
.PHONY: test-gaps-guitar-full-primary-display
test-gaps-guitar-full-primary-display: analyze-gaps-guitar-full-attributes
	python3 tests/check_gaps_guitar_primary_display.py build/gaps_guitar_full_attributes.tsv 177
.PHONY: summarize-real-audio-fixture-coverage
summarize-real-audio-fixture-coverage:
	python3 scripts/summarize_real_audio_fixture_coverage.py
.PHONY: inspect-fret-zealot-current
inspect-fret-zealot-current:
	python3 scripts/inspect_fret_zealot_current.py

.PHONY: inspect-real-audio-targets
inspect-real-audio-targets:
	python3 scripts/inspect_make_target_name.py summarize-real-audio-fixture-coverage list-ready-real-audio-evidence

.PHONY: list-real-note-corpus-targets
list-real-note-corpus-targets:
	python3 scripts/list_make_targets_matching.py bass piano vocal real-note musicnet maestro maps iowa urmp

.PHONY: audit-high-bass-ownership
audit-high-bass-ownership:
	python3 scripts/audit_high_bass_ownership.py

.PHONY: inspect-bass-recovery-source
inspect-bass-recovery-source:
	python3 scripts/inspect_bass_recovery_source.py

.PHONY: inspect-other-display-source
inspect-other-display-source:
	python3 scripts/inspect_other_display_source.py
.PHONY: inspect-fret-zealot-scale
inspect-fret-zealot-scale:
	python3 scripts/diagnose_fret_zealot_scale.py

.PHONY: test-fret-zealot-scale-reconciliation
test-fret-zealot-scale-reconciliation:
	python3 tests/check_fret_zealot_scale_reconciliation.py

.PHONY: summarize-melodic-drum-false-positives
summarize-melodic-drum-false-positives:
	python3 scripts/summarize_melodic_drum_false_positives.py build/real_note_full_mix_attributes.tsv

summarize-real-note-row-confusion:
	python3 scripts/summarize_real_note_row_confusion.py build/real_note_full_mix_attributes.tsv

inspect-note-owner-classifier:
	python3 scripts/inspect_note_owner_classifier.py

inspect-guitar-octave-shadow:
	python3 scripts/inspect_guitar_octave_shadow.py

inspect-analyzer-case-hihat-decay:
	python3 scripts/inspect_analyzer_case_context.py 'OBS hihat decay guard'

inspect-analyzer-case-distorted-guitar-chord:
	python3 scripts/inspect_analyzer_case_context.py 'complex real timbre distorted guitar chord'

inspect-chord-dim-alias:
	python3 scripts/inspect_chord_dim_alias.py

list-analyzer-test-targets:
	python3 scripts/list_analyzer_test_targets.py

.PHONY: inspect-fret-zealot-sync
inspect-fret-zealot-sync:
	python3 scripts/inspect_fret_zealot_sync.py

.PHONY: inspect-fret-zealot-diff
inspect-fret-zealot-diff:
	python3 scripts/inspect_fret_zealot_diff.py

.PHONY: test-fret-zealot-auto-root-guard
test-fret-zealot-auto-root-guard:
	python3 tests/check_fret_zealot_auto_root_guard.py

.PHONY: list-android-targets
list-android-targets:
	python3 scripts/list_android_targets.py

.PHONY: inspect-android-project-guard
inspect-android-project-guard:
	python3 scripts/inspect_android_project_guard.py

.PHONY: inspect-guitar-chord-mix-shards
inspect-guitar-chord-mix-shards:
	python3 scripts/inspect_guitar_chord_mix_shards.py

.PHONY: inspect-guitarset-primary-measurement
inspect-guitarset-primary-measurement:
	python3 scripts/inspect_guitarset_primary_measurement.py

.PHONY: debug-guitar-chord-primary-misses
debug-guitar-chord-primary-misses:
	python3 scripts/debug_guitar_chord_primary_misses.py

.PHONY: collect-guitar-chord-primary-attributes
collect-guitar-chord-primary-attributes:
	python3 scripts/collect_guitar_chord_primary_attributes.py

.PHONY: summarize-guitar-chord-primary-attributes
summarize-guitar-chord-primary-attributes:
	python3 scripts/summarize_guitar_chord_primary_attributes.py

.PHONY: inspect-chord-ranking
inspect-chord-ranking:
	python3 scripts/inspect_chord_ranking.py

.PHONY: inspect-chord-alias-order
inspect-chord-alias-order:
	python3 scripts/inspect_chord_alias_order.py

.PHONY: inspect-guitar-primary-promotion
inspect-guitar-primary-promotion:
	python3 scripts/inspect_guitar_primary_promotion.py

inspect-real-note-piano-guitar-attributes:
	python3 scripts/inspect_real_note_sample_attributes.py keyboard_electronic_078-042-025

.PHONY: inspect-hihat-detector
inspect-hihat-detector:
	python3 scripts/diagnose_hihat_detector.py

.PHONY: inspect-real-note-full-mix-replay
inspect-real-note-full-mix-replay:
	python3 scripts/diagnose_real_note_full_mix.py

.PHONY: inspect-drum-fixture-debug
inspect-drum-fixture-debug:
	python3 scripts/diagnose_drum_fixture_debug.py

.PHONY: debug-hf-hihat-fixtures
debug-hf-hihat-fixtures:
	sh scripts/run_hihat_fixture_debug.sh

.PHONY: debug-real-note-hihat-false-positives
debug-real-note-hihat-false-positives:
	sh scripts/run_real_note_hihat_false_debug.sh

.PHONY: test-hihat-early-recovery-guard
test-hihat-early-recovery-guard:
	python3 tests/check_hihat_early_recovery_guard.py

test-tonal-hihat-regressions: build/analyzer_real_note_samples
	python3 tests/check_tonal_hihat_regressions.py

inspect-hihat-early-recovery-guard:
	python3 scripts/inspect_hihat_early_recovery_guard.py

inspect-hihat-recovery-change:
	python3 scripts/inspect_hihat_recovery_change.py

.PHONY: summarize-real-note-full-mix-shards
summarize-real-note-full-mix-shards:
	python3 scripts/summarize_real_note_full_mix_shards.py

.PHONY: debug-real-note-top-hihat-brass
debug-real-note-top-hihat-brass:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_059-043-075

debug-real-note-top-hihat-brass-016:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_016-082-100

debug-real-note-top-hihat-brass-016-mid:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_016-069-100

debug-real-note-piano-guitar-confusion:
	sh scripts/run_real_note_sample_debug.sh keyboard_electronic_078-042-025
inspect-guitar-chord-callsite:
	python3 scripts/inspect_guitar_chord_callsite.py

inspect-guitar-chord-finalization:
	python3 scripts/inspect_guitar_chord_finalization.py

inspect-drum-score-arbitration:
	python3 scripts/inspect_drum_score_arbitration.py

inspect-synthetic-drum-case-context:
	python3 scripts/inspect_synthetic_drum_case_context.py

inspect-analyzer-cases-runner:
	python3 scripts/inspect_analyzer_cases_runner.py

test-analyzer-synthetic-drums: build/analyzer_cases
	env MUSIC_ANALYZER_CASE_GROUP=synthetic-drums build/analyzer_cases

inspect-snare-caps:
	python3 scripts/inspect_snare_caps.py

inspect-snare-debug-fields:
	python3 scripts/inspect_snare_debug_fields.py

inspect-git-scope:
	python3 scripts/inspect_git_scope.py

plan-verified-guitar-anchor-commit:
	python3 scripts/commit_verified_guitar_anchor.py plan

inspect-verified-guitar-anchor-stage:
	python3 scripts/commit_verified_guitar_anchor.py inspect

stage-verified-guitar-anchor-commit:
	python3 scripts/commit_verified_guitar_anchor.py stage

commit-verified-guitar-anchor:
	python3 scripts/commit_verified_guitar_anchor.py commit
.PHONY: diagnose-fret-zealot-partial-scale
diagnose-fret-zealot-partial-scale:
	python3 scripts/diagnose_fret_zealot_partial_scale.py
.PHONY: plan-stage-fret-zealot-batching
plan-stage-fret-zealot-batching:
	python3 scripts/plan_stage_fret_zealot_batching.py
.PHONY: commit-verified-fret-zealot-batching
commit-verified-fret-zealot-batching:
	python3 scripts/commit_verified_fret_zealot_batching.py
.PHONY: diagnose-upbeat-kick-suppression
diagnose-upbeat-kick-suppression:
	python3 scripts/diagnose_upbeat_kick_suppression.py
.PHONY: commit-verified-drum-recovery
commit-verified-drum-recovery:
	python3 scripts/commit_verified_drum_recovery.py
.PHONY: diagnose-guitar-extension-chords
diagnose-guitar-extension-chords:
	python3 scripts/diagnose_guitar_extension_chords.py
diagnose-fret-zealot-led-queue:
	python3 scripts/diagnose_fret_zealot_led_queue.py
commit-verified-fret-zealot-fallback:
	python3 scripts/commit_verified_fret_zealot_fallback.py
diagnose-guitar-extension-template-selection:
	python3 scripts/diagnose_guitar_extension_template_selection.py
test-guitar-caged-voicings:
	python3 scripts/run_analyzer_cases_guitar_caged.py
diagnose-analyzer-cases-runner:
	python3 scripts/diagnose_analyzer_cases_runner.py
test-extended-chords:
	python3 scripts/run_analyzer_cases_extended_chords.py
.PHONY: diagnose-fret-zealot-partial-updates
diagnose-fret-zealot-partial-updates: scripts/diagnose_fret_zealot_partial_updates.py
	python3 scripts/diagnose_fret_zealot_partial_updates.py
.PHONY: test-fret-zealot-batch-settle
test-fret-zealot-batch-settle: scripts/check_fret_zealot_batch_settle.py
	python3 scripts/check_fret_zealot_batch_settle.py
.PHONY: diagnose-android-fret-zealot-checks
diagnose-android-fret-zealot-checks: scripts/diagnose_android_fret_zealot_checks.py
	python3 scripts/diagnose_android_fret_zealot_checks.py
.PHONY: diagnose-fret-zealot-auto-sender
diagnose-fret-zealot-auto-sender: scripts/diagnose_fret_zealot_auto_sender.py
	python3 scripts/diagnose_fret_zealot_auto_sender.py
.PHONY: commit-fret-zealot-batch-pacing
commit-fret-zealot-batch-pacing: scripts/commit_verified_fret_zealot_batch_pacing.py
	python3 scripts/commit_verified_fret_zealot_batch_pacing.py
.PHONY: diagnose-guitar-residue-clear
diagnose-guitar-residue-clear: scripts/diagnose_guitar_residue_clear.py
	python3 scripts/diagnose_guitar_residue_clear.py
.PHONY: diagnose-extended-chord-test-diff
diagnose-extended-chord-test-diff: scripts/diagnose_extended_chord_test_diff.py
	python3 scripts/diagnose_extended_chord_test_diff.py
.PHONY: commit-guitar-extension-recovery
commit-guitar-extension-recovery: scripts/commit_verified_guitar_extension_recovery.py
	python3 scripts/commit_verified_guitar_extension_recovery.py
.PHONY: diagnose-piano-minor-chord-case
diagnose-piano-minor-chord-case: scripts/diagnose_piano_minor_chord_case.py
	python3 scripts/diagnose_piano_minor_chord_case.py
.PHONY: test-public-multitrack-style
test-public-multitrack-style: build/analyzer_cases scripts/run_analyzer_cases_public_multitrack_style.py
	python3 scripts/run_analyzer_cases_public_multitrack_style.py
.PHONY: report-real-world-samples-process
report-real-world-samples-process: scripts/report_real_world_samples_process.py
	python3 scripts/report_real_world_samples_process.py
.PHONY: wait-real-world-samples-process
wait-real-world-samples-process: scripts/wait_real_world_samples_process.py
	python3 scripts/wait_real_world_samples_process.py
.PHONY: inspect-other-new-note-filter
inspect-other-new-note-filter:
	python3 scripts/inspect_other_new_note_filter.py

.PHONY: inspect-monophonic-other-tests
inspect-monophonic-other-tests:
	python3 scripts/inspect_monophonic_other_tests.py

.PHONY: locate-urmp-fixture
locate-urmp-fixture:
	python3 scripts/locate_urmp_fixture.py

.PHONY: inspect-quiet-monophonic-visual-test
inspect-quiet-monophonic-visual-test:
	python3 scripts/inspect_quiet_monophonic_visual_test.py

.PHONY: inspect-detector-improvement-routes-target
inspect-detector-improvement-routes-target:
	python3 scripts/inspect_detector_improvement_routes_target.py
.PHONY: inspect-makefile-text
inspect-makefile-text: scripts/inspect_makefile_text.py
	@$(PYTHON) scripts/inspect_makefile_text.py

.PHONY: inspect-hihat-suppression-path
inspect-hihat-suppression-path: scripts/inspect_hihat_suppression_path.py
	@$(PYTHON) scripts/inspect_hihat_suppression_path.py

.PHONY: inspect-hihat-caps
inspect-hihat-caps: scripts/inspect_hihat_caps.py
	@$(PYTHON) scripts/inspect_hihat_caps.py

.PHONY: inspect-hihat-initial-classification
inspect-hihat-initial-classification: scripts/inspect_hihat_initial_classification.py
	@$(PYTHON) scripts/inspect_hihat_initial_classification.py

.PHONY: inspect-makefile-drum-targets
inspect-makefile-drum-targets: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source Makefile --topic "analyzer_drum_samples"

.PHONY: inspect-makefile-test-drum-targets
inspect-makefile-test-drum-targets: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source Makefile --topic "test-drum-samples"

.PHONY: report-real-drum-test-status
report-real-drum-test-status: scripts/report_real_drum_test_status.py
	@$(PYTHON) scripts/report_real_drum_test_status.py

.PHONY: inspect-egmd-drum-debug-output
inspect-egmd-drum-debug-output: scripts/inspect_analyzer_section.py
	@$(PYTHON) scripts/inspect_analyzer_section.py --source tests/analyzer_egmd.cpp --topic "drum_debug_rule_flags"

.PHONY: report-dense-hihat-recovery
report-dense-hihat-recovery: scripts/report_dense_hihat_recovery.py
	@$(PYTHON) scripts/report_dense_hihat_recovery.py

.PHONY: measure-mdb-dense-hihat-recovery
measure-mdb-dense-hihat-recovery: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/run_with_duration.sh scripts/report_dense_hihat_recovery.py
	$(RUN_WITH_DURATION) analyzer_mdb_dense_hihat_recovery env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="80" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_ALL=1 $(BUILD_DIR)/analyzer_egmd > "$(BUILD_DIR)/mdb_dense_hihat_recovery.out" 2> "$(BUILD_DIR)/mdb_dense_hihat_recovery.log"
	@$(PYTHON) scripts/report_dense_hihat_recovery.py

.PHONY: inspect-hihat-test-diagnostics
inspect-hihat-test-diagnostics: scripts/inspect_hihat_test_diagnostics.py
	@$(PYTHON) scripts/inspect_hihat_test_diagnostics.py
.PHONY: inspect-real-note-harness
inspect-real-note-harness:
	python3 scripts/inspect_real_note_harness.py
.PHONY: analyze-real-note-ownership
analyze-real-note-ownership: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_ownership.py

.PHONY: report-real-note-ownership
report-real-note-ownership:
	python3 scripts/analyze_real_note_ownership.py --report

.PHONY: report-real-note-shard-errors
report-real-note-shard-errors:
	python3 scripts/analyze_real_note_ownership.py --shard-errors
.PHONY: debug-real-note-sample
debug-real-note-sample: build/analyzer_real_note_samples
	python3 scripts/debug_real_note_sample.py

.PHONY: debug-real-note-guitar-reference
debug-real-note-guitar-reference: build/analyzer_real_note_samples
	python3 scripts/debug_real_note_sample.py guitar_acoustic_010-046-025
.PHONY: inspect-full-mix-arbitration
inspect-full-mix-arbitration:
	python3 scripts/inspect_full_mix_arbitration.py
.PHONY: analyze-real-note-guitar-ownership
analyze-real-note-guitar-ownership: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_guitar_ownership.py
.PHONY: analyze-real-note-guitar-misses
analyze-real-note-guitar-misses: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_guitar_misses.py
.PHONY: test-real-note-guitar-full-mix-recall
test-real-note-guitar-full-mix-recall: analyze-real-note-guitar-misses
	python3 scripts/check_real_note_guitar_full_mix_recall.py
.PHONY: report-real-note-guitar-misses
report-real-note-guitar-misses:
	python3 scripts/analyze_real_note_guitar_misses.py --report
.PHONY: analyze-real-note-piano-guitar-routes
analyze-real-note-piano-guitar-routes: build/analyzer_real_note_samples
	python3 scripts/analyze_real_note_piano_guitar_routes.py
.PHONY: inspect-full-mix-guitar-row
inspect-full-mix-guitar-row:
	python3 scripts/inspect_full_mix_guitar_row.py
analyze-real-note-low-guitar-shapes:
	python3 scripts/analyze_real_note_low_guitar_shapes.py
report-low-guitar-shape-separation:
	python3 scripts/report_low_guitar_shape_separation.py
test-real-note-low-electronic-piano-guitar-shadow: build/analyzer_real_note_samples
	python3 scripts/check_real_note_low_electronic_piano_guitar_shadow.py
inspect-full-mix-ownership-classifier:
	python3 scripts/inspect_full_mix_ownership_classifier.py
report-piano-guitar-owner-aliases:
	python3 scripts/report_piano_guitar_owner_aliases.py
report-same-pitch-guitar-owner-separation:
	python3 scripts/report_same_pitch_guitar_owner_separation.py
list-fixture-import-tools:
	python3 scripts/list_fixture_import_tools.py
report-real-audio-fixture-coverage:
	python3 scripts/summarize_real_audio_fixture_coverage.py
report-guitarset-miss-process:
	python3 scripts/report_guitarset_miss_process.py
inspect-guitarset-chord-selection:
	python3 scripts/inspect_guitarset_chord_selection.py
guitarset-debug-windows: build/analyzer_guitarset
	python3 scripts/run_guitarset_debug_windows.py
report-guitarset-major-minor-debug:
	python3 scripts/report_guitarset_major_minor_debug.py

.PHONY: check-fret-zealot-auto-recovery
check-fret-zealot-auto-recovery:
	python3 scripts/check_fret_zealot_auto_recovery.py
.PHONY: stop-low-electronic-piano-guitar-shadow
stop-low-electronic-piano-guitar-shadow:
	python3 scripts/stop_low_electronic_piano_guitar_shadow.py
.PHONY: inspect-real-note-vocal-routes
inspect-real-note-vocal-routes:
	python3 scripts/inspect_real_note_vocal_routes.py
.PHONY: inspect-full-mix-vocal-scoring
inspect-full-mix-vocal-scoring:
	python3 scripts/inspect_full_mix_vocal_scoring.py
.PHONY: inspect-vocal-display-weight
inspect-vocal-display-weight:
	python3 scripts/inspect_vocal_display_weight.py
.PHONY: inspect-full-mix-debug-candidate
inspect-full-mix-debug-candidate:
	python3 scripts/inspect_full_mix_debug_candidate.py
.PHONY: inspect-real-note-debug-output
inspect-real-note-debug-output:
	python3 scripts/inspect_real_note_debug_output.py
.PHONY: collect-real-note-vocal-attributes
collect-real-note-vocal-attributes: build/analyzer_real_note_samples
	python3 scripts/collect_real_note_vocal_attributes.py
.PHONY: inspect-full-mix-vocal-profile
inspect-full-mix-vocal-profile:
	python3 scripts/inspect_full_mix_vocal_profile.py
.PHONY: inspect-vocal-row-population
inspect-vocal-row-population:
	python3 scripts/inspect_vocal_row_population.py
.PHONY: status-guitar-chord-primary-collection
status-guitar-chord-primary-collection:
	python3 scripts/status_guitar_chord_primary_collection.py
.PHONY: find-high-soprano-vocal-mirror-flag
find-high-soprano-vocal-mirror-flag:
	python3 scripts/find_high_soprano_vocal_mirror_flag.py
.PHONY: status-real-note-full-mix
status-real-note-full-mix:
	python3 scripts/status_real_note_full_mix.py
.PHONY: plan-mir1k-vocal-fixtures
plan-mir1k-vocal-fixtures:
	python3 scripts/plan_mir1k_vocal_fixtures.py
.PHONY: import-mir1k-vocal-archive
import-mir1k-vocal-archive:
	python3 scripts/import_mir1k_vocal_archive.py
.PHONY: status-mir1k-vocal-import
status-mir1k-vocal-import:
	python3 scripts/status_mir1k_vocal_import.py
.PHONY: inspect-mir1k-vocal-layout
inspect-mir1k-vocal-layout:
	python3 scripts/inspect_mir1k_vocal_layout.py

.PHONY: inspect-mir1k-vocal-pitch-labels
inspect-mir1k-vocal-pitch-labels:
	python3 scripts/inspect_mir1k_vocal_pitch_labels.py

.PHONY: inspect-real-note-sample-test-contract
inspect-real-note-sample-test-contract:
	python3 scripts/inspect_real_note_sample_test_contract.py

.PHONY: prepare-mir1k-vocal-fixtures
prepare-mir1k-vocal-fixtures:
	python3 scripts/prepare_mir1k_vocal_fixtures.py

.PHONY: test-mir1k-clean-vocal-fixtures
test-mir1k-clean-vocal-fixtures:
	python3 scripts/run_mir1k_vocal_fixture_test.py

.PHONY: test-mir1k-clean-vocal-fixtures-full-mix
test-mir1k-clean-vocal-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix

.PHONY: test-mir1k-vocal-mix-fixtures-full-mix
test-mir1k-vocal-mix-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --mixed-fixtures

.PHONY: measure-mir1k-vocal-mix-fixtures-full-mix
measure-mir1k-vocal-mix-fixtures-full-mix:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --mixed-fixtures --measure-only

.PHONY: probe-mir1k-vocal-linear-separation
probe-mir1k-vocal-linear-separation:
	python3 scripts/probe_mir1k_vocal_linear_separation.py

.PHONY: inspect-full-mix-ownership-application
inspect-full-mix-ownership-application:
	python3 scripts/inspect_full_mix_ownership_application.py

.PHONY: probe-mir1k-vocal-tree-separation
probe-mir1k-vocal-tree-separation:
	python3 scripts/probe_mir1k_vocal_tree_separation.py

.PHONY: stage-mir1k-vocal-fixture-commit
stage-mir1k-vocal-fixture-commit:
	python3 scripts/stage_mir1k_vocal_fixture_commit.py

.PHONY: commit-push-mir1k-vocal-fixture
commit-push-mir1k-vocal-fixture:
	python3 scripts/commit_push_mir1k_vocal_fixture.py

.PHONY: inspect-runtime-model-assets
inspect-runtime-model-assets:
	python3 scripts/inspect_runtime_model_assets.py

.PHONY: inspect-basic-pitch-vocal-fusion-contract
inspect-basic-pitch-vocal-fusion-contract:
	python3 scripts/inspect_basic_pitch_vocal_fusion_contract.py

.PHONY: status-guitarset-miss-analysis
status-guitarset-miss-analysis:
	python3 scripts/status_guitarset_miss_analysis.py

.PHONY: summarize-latest-guitarset-miss-run
summarize-latest-guitarset-miss-run:
	python3 scripts/summarize_latest_guitarset_miss_run.py

.PHONY: inspect-guitarset-basic-pitch-usage
inspect-guitarset-basic-pitch-usage:
	python3 scripts/inspect_guitarset_basic_pitch_usage.py

.PHONY: summarize-current-real-audio-fixture-coverage
summarize-current-real-audio-fixture-coverage:
	python3 scripts/summarize_current_real_audio_fixture_coverage.py

.PHONY: plan-idmt-bass-import
plan-idmt-bass-import:
	python3 scripts/plan_idmt_bass_import.py

.PHONY: import-idmt-bass-archive
import-idmt-bass-archive:
	python3 scripts/import_idmt_bass_archive.py

.PHONY: inspect-idmt-bass-layout
inspect-idmt-bass-layout:
	python3 scripts/inspect_idmt_bass_layout.py

.PHONY: status-idmt-bass-import
status-idmt-bass-import:
	python3 scripts/status_idmt_bass_import.py

.PHONY: stop-idmt-bass-import
stop-idmt-bass-import:
	python3 scripts/stop_idmt_bass_import.py

.PHONY: import-idmt-bass-single-track-archive
import-idmt-bass-single-track-archive:
	python3 scripts/import_idmt_bass_single_track_archive.py

.PHONY: inspect-idmt-bass-single-track-layout
inspect-idmt-bass-single-track-layout:
	python3 scripts/inspect_idmt_bass_single_track_layout.py

.PHONY: collect-mir1k-clean-vocal-attributes
collect-mir1k-clean-vocal-attributes:
	python3 scripts/run_mir1k_vocal_fixture_test.py --full-mix --attributes

.PHONY: summarize-mir1k-clean-vocal-attributes
summarize-mir1k-clean-vocal-attributes:
	python3 scripts/summarize_mir1k_vocal_attributes.py

.PHONY: inspect-full-mix-owner-scoring
inspect-full-mix-owner-scoring:
	python3 scripts/inspect_full_mix_owner_scoring.py

.PHONY: collect-real-note-full-mix-attributes
collect-real-note-full-mix-attributes:
	python3 scripts/collect_real_note_full_mix_attributes.py

.PHONY: summarize-real-note-full-mix-attributes
summarize-real-note-full-mix-attributes:
	python3 scripts/summarize_real_note_full_mix_attributes.py

.PHONY: status-real-note-full-mix-attribute-collection
status-real-note-full-mix-attribute-collection:
	python3 scripts/status_real_note_full_mix_attribute_collection.py

.PHONY: compare-mir1k-vocal-feature-distributions
compare-mir1k-vocal-feature-distributions:
	python3 scripts/compare_mir1k_vocal_feature_distributions.py

.PHONY: evaluate-mir1k-vocal-recovery-rules
evaluate-mir1k-vocal-recovery-rules:
	python3 scripts/evaluate_mir1k_vocal_recovery_rules.py

.PHONY: plan-mir1k-vocal-test-fixtures
inspect-mir1k-vocal-fixture-pipeline:
	python3 scripts/inspect_mir1k_vocal_fixture_pipeline.py

.PHONY: inspect-mir1k-vocal-fixture-pipeline
plan-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py plan

.PHONY: apply-mir1k-vocal-test-fixtures
apply-mir1k-vocal-test-fixtures:
	python3 scripts/sync_mir1k_vocal_test_fixtures.py apply

.PHONY: test-mir1k-vocal-full-mix
test-mir1k-vocal-full-mix: $(BUILD_DIR)/analyzer_real_note_samples tests/fixtures/mir1k_clean_vocals/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mir1k_vocal_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=221 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="tests/fixtures/mir1k_clean_vocals" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=221 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=70 $(BUILD_DIR)/analyzer_real_note_samples
.PHONY: stage-mir1k-vocal-fixture-gate
stage-mir1k-vocal-fixture-gate: scripts/stage_mir1k_vocal_fixture_gate.py
	python3 scripts/stage_mir1k_vocal_fixture_gate.py
.PHONY: commit-mir1k-vocal-fixture-gate
commit-mir1k-vocal-fixture-gate: scripts/commit_mir1k_vocal_fixture_gate.py
	python3 scripts/commit_mir1k_vocal_fixture_gate.py

MIR1K_VOCAL_ATTRIBUTE_TSV ?= $(BUILD_DIR)/mir1k_vocal_full_mix_attributes.tsv
.PHONY: collect-mir1k-vocal-full-mix-attributes
collect-mir1k-vocal-full-mix-attributes: $(BUILD_DIR)/analyzer_real_note_samples tests/fixtures/mir1k_clean_vocals/manifest.tsv scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mir1k_vocal_full_mix_attributes env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=221 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="tests/fixtures/mir1k_clean_vocals" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=221 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(MIR1K_VOCAL_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	@printf '%s\n' "attribute TSV: $(MIR1K_VOCAL_ATTRIBUTE_TSV)"

.PHONY: summarize-mir1k-vocal-ownership
summarize-mir1k-vocal-ownership: $(MIR1K_VOCAL_ATTRIBUTE_TSV) build/real_note_full_mix_attributes.tsv scripts/summarize_mir1k_vocal_ownership.py
	python3 scripts/summarize_mir1k_vocal_ownership.py

.PHONY: plan-clean-mir1k-vocal-test-fixture-stale
plan-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py plan

.PHONY: apply-clean-mir1k-vocal-test-fixture-stale
apply-clean-mir1k-vocal-test-fixture-stale:
	python3 scripts/clean_mir1k_vocal_test_fixture_stale.py apply

.PHONY: status-detection-data-worktree
status-detection-data-worktree:
	python3 scripts/status_detection_data_worktree.py

.PHONY: show-mir1k-makefile-blocks
show-mir1k-makefile-blocks:
	python3 scripts/show_mir1k_makefile_blocks.py
.PHONY: inspect-fret-zealot-scale-path
inspect-fret-zealot-scale-path:
	@python3 scripts/inspect_fret_zealot_scale_path.py

.PHONY: inspect-fret-zealot-controller
inspect-fret-zealot-controller:
	@python3 scripts/inspect_fret_zealot_controller.py

.PHONY: inspect-fret-zealot-callers
inspect-fret-zealot-callers:
	@python3 scripts/inspect_fret_zealot_callers.py

.PHONY: test-fret-zealot-frame-settle
test-fret-zealot-frame-settle:
	@python3 tests/check_fret_zealot_frame_settle.py

.PHONY: show-fret-zealot-worktree-diff
show-fret-zealot-worktree-diff:
	@python3 scripts/show_fret_zealot_worktree_diff.py

.PHONY: check-idmt-bass-single-track-setup
check-idmt-bass-single-track-setup:
	@python3 scripts/check_idmt_bass_single_track_setup.py

.PHONY: inspect-idmt-bass-single-track-importer
inspect-idmt-bass-single-track-importer:
	@python3 scripts/inspect_idmt_bass_single_track_importer.py

.PHONY: diagnose-idmt-bass-single-track-archive
diagnose-idmt-bass-single-track-archive:
	@python3 scripts/diagnose_idmt_bass_single_track_archive.py

.PHONY: status-idmt-bass-single-track-import
status-idmt-bass-single-track-import:
	@python3 scripts/status_idmt_bass_single_track_import.py

.PHONY: summarize-idmt-bass-single-track-annotations
summarize-idmt-bass-single-track-annotations:
	@python3 scripts/summarize_idmt_bass_single_track_annotations.py

.PHONY: inspect-real-note-fixture-pipeline
inspect-real-note-fixture-pipeline:
	@python3 scripts/inspect_real_note_fixture_pipeline.py

.PHONY: prepare-idmt-bass-single-track-fixture test-prepare-idmt-bass-single-track-fixture measure-idmt-bass-single-track test-idmt-bass-single-track
prepare-idmt-bass-single-track-fixture: import-idmt-bass-single-track-archive
	@python3 scripts/prepare_idmt_bass_single_track_fixture.py

test-prepare-idmt-bass-single-track-fixture: prepare-idmt-bass-single-track-fixture
	@python3 tests/test_prepare_idmt_bass_single_track_fixture.py

measure-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py

test-idmt-bass-single-track: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --min-recall 95

.PHONY: status-idmt-bass-single-track-measurement
status-idmt-bass-single-track-measurement:
	@python3 scripts/status_idmt_bass_single_track_measurement.py

.PHONY: summarize-idmt-bass-single-track-measurement
summarize-idmt-bass-single-track-measurement:
	@python3 scripts/summarize_idmt_bass_single_track_measurement.py

.PHONY: inspect-bass-tuning-detector
inspect-bass-tuning-detector:
	@python3 scripts/inspect_bass_tuning_detector.py

IDMT_BASS_SAMPLE_ID ?= idmt_bass_005_056
.PHONY: inspect-idmt-bass-sample-attributes
inspect-idmt-bass-sample-attributes:
	@python3 scripts/inspect_idmt_bass_sample_attributes.py --sample-id "$(IDMT_BASS_SAMPLE_ID)"

.PHONY: inspect-idmt-bass-high-register-attributes
inspect-idmt-bass-high-register-attributes:
	@python3 scripts/inspect_idmt_bass_sample_attributes.py --sample-id idmt_bass_017_004

.PHONY: debug-idmt-bass-single-track-sample
debug-idmt-bass-single-track-sample: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --debug-sample "$(IDMT_BASS_SAMPLE_ID)"

.PHONY: debug-idmt-bass-high-register-sample
debug-idmt-bass-high-register-sample: $(BUILD_DIR)/analyzer_real_note_samples test-prepare-idmt-bass-single-track-fixture
	@python3 scripts/run_idmt_bass_single_track_measurement.py --debug-sample idmt_bass_017_004

.PHONY: inspect-idmt-bass-recording-017
inspect-idmt-bass-recording-017:
	@python3 scripts/inspect_idmt_bass_recording_017.py

.PHONY: stage-idmt-bass-single-track-fixture show-staged-idmt-bass-single-track-fixture commit-and-push-idmt-bass-single-track-fixture
stage-idmt-bass-single-track-fixture:
	@python3 scripts/stage_idmt_bass_single_track_fixture.py

show-staged-idmt-bass-single-track-fixture:
	@python3 scripts/show_staged_idmt_bass_single_track_fixture.py

commit-and-push-idmt-bass-single-track-fixture:
	@python3 scripts/commit_and_push_idmt_bass_single_track_fixture.py

.PHONY: inspect-bass-note-path
inspect-bass-note-path:
	@python3 scripts/inspect_bass_note_path.py
.PHONY: status-real-note-sample-test
status-real-note-sample-test:
	@python3 scripts/status_real_note_sample_test.py

.PHONY: inspect-real-note-sample-test
inspect-real-note-sample-test:
	@python3 scripts/inspect_real_note_sample_test.py

.PHONY: summarize-real-note-sample-shards
summarize-real-note-sample-shards:
	@python3 scripts/summarize_real_note_sample_shards.py

.PHONY: inspect-real-note-shard-output
inspect-real-note-shard-output:
	@python3 scripts/inspect_real_note_shard_output.py

.PHONY: inspect-bass-natural-harmonic-path
inspect-bass-natural-harmonic-path:
	@python3 scripts/inspect_bass_natural_harmonic_path.py

.PHONY: inspect-idmt-bass-debug-target
inspect-idmt-bass-debug-target:
	@python3 scripts/inspect_idmt_bass_debug_target.py

.PHONY: status-idmt-bass-debug
status-idmt-bass-debug:
	@python3 scripts/status_idmt_bass_debug.py

.PHONY: plan-clean-idmt-bass-single-track-fixture-tmp clean-idmt-bass-single-track-fixture-tmp
plan-clean-idmt-bass-single-track-fixture-tmp:
	@python3 scripts/clean_idmt_bass_single_track_fixture_tmp.py plan

clean-idmt-bass-single-track-fixture-tmp:
	@python3 scripts/clean_idmt_bass_single_track_fixture_tmp.py apply

.PHONY: inspect-fret-zealot-settle-change
inspect-fret-zealot-settle-change:
	@python3 scripts/inspect_fret_zealot_settle_change.py

.PHONY: inspect-fret-zealot-auto-scheduler
inspect-fret-zealot-auto-scheduler:
	@python3 scripts/inspect_fret_zealot_auto_scheduler.py

.PHONY: test-fret-zealot-initial-auto-scale
test-fret-zealot-initial-auto-scale: tests/test_fret_zealot_initial_auto_scale.py
	@python3 tests/test_fret_zealot_initial_auto_scale.py

.PHONY: evaluate-guitarset-extension-promotion
evaluate-guitarset-extension-promotion: scripts/evaluate_guitarset_extension_promotion.py
	@python3 scripts/evaluate_guitarset_extension_promotion.py

.PHONY: inspect-chord-label-parsers
inspect-chord-label-parsers: scripts/inspect_chord_label_parsers.py
	@python3 scripts/inspect_chord_label_parsers.py

.PHONY: inspect-guitar-same-root-alias-guard
inspect-guitar-same-root-alias-guard: scripts/inspect_guitar_same_root_alias_guard.py
	@python3 scripts/inspect_guitar_same_root_alias_guard.py

NSYNTH_SPLIT ?= test
.PHONY: plan-nsynth-acoustic-bass-fixture prepare-nsynth-acoustic-bass-fixture quarantine-nsynth-acoustic-bass-fixture plan-nsynth-acoustic-bass-valid-fixture prepare-nsynth-acoustic-bass-valid-fixture quarantine-nsynth-acoustic-bass-valid-fixture plan-nsynth-acoustic-bass-train-fixture prepare-nsynth-acoustic-bass-train-fixture
plan-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

quarantine-nsynth-acoustic-bass-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="$(NSYNTH_SPLIT)" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py quarantine

plan-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

quarantine-nsynth-acoustic-bass-valid-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py quarantine

plan-nsynth-acoustic-bass-train-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="train" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py plan

prepare-nsynth-acoustic-bass-train-fixture: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="train" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py apply

.PHONY: inspect-nsynth-acoustic-bass-importer
inspect-nsynth-acoustic-bass-importer: scripts/inspect_nsynth_fixture_importer.py
	@python3 scripts/inspect_nsynth_fixture_importer.py

.PHONY: probe-nsynth-acoustic-bass-valid-range
probe-nsynth-acoustic-bass-valid-range: scripts/prepare_nsynth_acoustic_bass_fixture.py
	@NSYNTH_SPLIT="valid" python3 scripts/prepare_nsynth_acoustic_bass_fixture.py probe

.PHONY: plan-stage-fret-zealot-frame-settle stage-fret-zealot-frame-settle
plan-stage-fret-zealot-frame-settle:
	@python3 scripts/stage_fret_zealot_frame_settle.py plan

stage-fret-zealot-frame-settle:
	@python3 scripts/stage_fret_zealot_frame_settle.py apply

.PHONY: commit-fret-zealot-frame-settle
commit-fret-zealot-frame-settle:
	@python3 scripts/commit_fret_zealot_frame_settle.py

.PHONY: evaluate-ambiguous-display-recovery
evaluate-ambiguous-display-recovery:
	@python3 scripts/evaluate_ambiguous_display_recovery.py

.PHONY: inspect-full-mix-display-mirror-support
inspect-full-mix-display-mirror-support:
	@python3 scripts/inspect_full_mix_display_mirror_support.py

.PHONY: inspect-shared-note-cases
inspect-shared-note-cases:
	@python3 scripts/inspect_shared_note_cases.py

.PHONY: check-real-note-guitar-full-mix-recall
check-real-note-guitar-full-mix-recall:
	@python3 scripts/check_real_note_guitar_full_mix_recall.py

.PHONY: test-ambiguous-display-recovery
test-ambiguous-display-recovery: analyze-real-note-attributes tests/test_ambiguous_display_recovery.py
	@python3 tests/test_ambiguous_display_recovery.py

.PHONY: test-high-soprano-vocal-mirror
test-high-soprano-vocal-mirror: tests/test_high_soprano_vocal_mirror.py
	$(PYTHON) tests/test_high_soprano_vocal_mirror.py

.PHONY: inspect-high-soprano-vocal-mirror-change
inspect-high-soprano-vocal-mirror-change: scripts/inspect_high_soprano_vocal_mirror_change.py
	$(PYTHON) scripts/inspect_high_soprano_vocal_mirror_change.py

.PHONY: summarize-high-soprano-vocal-mirror-result
summarize-high-soprano-vocal-mirror-result: scripts/summarize_high_soprano_mirror_result.py
	$(PYTHON) scripts/summarize_high_soprano_mirror_result.py
.PHONY: stage-high-soprano-vocal-mirror
stage-high-soprano-vocal-mirror: scripts/stage_high_soprano_vocal_mirror.py
	$(PYTHON) scripts/stage_high_soprano_vocal_mirror.py
.PHONY: commit-high-soprano-vocal-mirror
commit-high-soprano-vocal-mirror: scripts/commit_high_soprano_vocal_mirror.py
	$(PYTHON) scripts/commit_high_soprano_vocal_mirror.py

.PHONY: plan-stage-ambiguous-display-recovery stage-ambiguous-display-recovery commit-ambiguous-display-recovery
plan-stage-ambiguous-display-recovery:
	@python3 scripts/stage_ambiguous_display_recovery.py plan

stage-ambiguous-display-recovery:
	@python3 scripts/stage_ambiguous_display_recovery.py apply

commit-ambiguous-display-recovery:
	@python3 scripts/commit_ambiguous_display_recovery.py
plan-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py plan

stage-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py stage

unstage-code-baseline-commit:
	python3 scripts/unstage_code_baseline_commit.py

commit-code-baseline:
	python3 scripts/manage_code_baseline_commit.py commit

verify-code-baseline-commit:
	python3 scripts/manage_code_baseline_commit.py verify

push-code-baseline:
	python3 scripts/manage_code_baseline_commit.py push

report-instrument-sample-storage:
	python3 scripts/report_instrument_sample_storage.py

plan-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py plan --store "$(INSTRUMENT_SAMPLE_STORE)"

prepare-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py apply --store "$(INSTRUMENT_SAMPLE_STORE)"

verify-sneakybass-fixture:
	$(PYTHON) scripts/prepare_sneakybass_fixture.py verify --store "$(INSTRUMENT_SAMPLE_STORE)"

analyze-sneakybass-fixture: build/analyzer_instrument_samples verify-sneakybass-fixture
	$(PYTHON) scripts/run_sneakybass_fixture_audit.py --binary "$(BUILD_DIR)/analyzer_instrument_samples" --fixture-root "$(INSTRUMENT_SAMPLE_STORE)/real-fixtures/sneakybass" --log "$(BUILD_DIR)/sneakybass_fixture_audit.log" --attributes "$(BUILD_DIR)/sneakybass_fixture_attributes.tsv" --jobs "$(PARALLEL_TEST_JOBS)" --source-name "$(SNEAKYBASS_SOURCE_NAME)"

analyze-sneakybass-fixture-regular-bass: build/analyzer_instrument_samples verify-sneakybass-fixture
	$(PYTHON) scripts/run_sneakybass_fixture_audit.py --binary "$(BUILD_DIR)/analyzer_instrument_samples" --fixture-root "$(INSTRUMENT_SAMPLE_STORE)/real-fixtures/sneakybass" --log "$(BUILD_DIR)/sneakybass_fixture_regular_bass_audit.log" --attributes "$(BUILD_DIR)/sneakybass_fixture_regular_bass_attributes.tsv" --jobs "$(PARALLEL_TEST_JOBS)" --source-name "bass"

report-sneakybass-fixture-audit:
	$(PYTHON) scripts/report_sneakybass_fixture_audit.py --log "$(BUILD_DIR)/sneakybass_fixture_audit.log"

report-sneakybass-fixture-attributes:
	$(PYTHON) scripts/report_sneakybass_fixture_attributes.py --attributes "$(BUILD_DIR)/sneakybass_fixture_attributes.tsv"
commit-real-bass-fixture-audit:
	python3 scripts/commit_staged_source_changes.py --message "test: add external real bass fixture audit"
SNEAKYBASS_SOURCE_NAME ?= double bass
test-instrument-vocal-voice-oohs-g3: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="vocals" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="voice_oohs" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="G3" build/analyzer_instrument_samples

analyze-instrument-vocal-voice-oohs-g3: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="vocals" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="voice_oohs" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="G3" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$(BUILD_DIR)/voice_oohs_g3_attributes.tsv" build/analyzer_instrument_samples

report-instrument-vocal-voice-oohs-g3:
	$(PYTHON) scripts/report_voice_oohs_g3_attributes.py --attributes "$(BUILD_DIR)/voice_oohs_g3_attributes.tsv"
commit-vocal-source-hint-recovery:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover low vocals from keyboard ownership"

commit-synthetic-overtone-pruning:
	python3 scripts/commit_staged_source_changes.py --message "fix: prefer synthetic note fundamentals over overtones"

commit-synthetic-c5-fundamentals:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover high synthetic fundamentals from subharmonics"

commit-generated-gm-hihat-recovery:
	python3 scripts/commit_staged_source_changes.py --message "fix: recover generated GM hi-hat tails"

commit-real-bass-tracking-diagnostics:
	python3 scripts/commit_staged_source_changes.py --message "test: add external bass tracking diagnostics"

commit-fixture-source-inventory:
	python3 scripts/commit_staged_source_changes.py --message "test: inventory external fixture sources"

inspect-drum-fixture-harness:
	python3 scripts/inspect_drum_fixture_harness.py

test-drum-kit-hihat: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="hihat" build/analyzer_instrument_samples

analyze-drum-kit-hihat: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="hihat" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="build/drum_hihat_attributes.tsv" build/analyzer_instrument_samples

inspect-hihat-suppression:
	python3 scripts/inspect_hihat_suppression.py

inspect-hihat-drum-policy:
	python3 scripts/inspect_analyzer_source_range.py 31480 31740

inspect-bass-detector-paths:
	python3 scripts/inspect_bass_detector_paths.py

inspect-bass-alias-policy:
	python3 scripts/inspect_analyzer_source_range.py 1000 1245

report-sneakybass-octave-aliases:
	python3 scripts/report_sneakybass_octave_aliases.py

report-sneakybass-tracking-alignment:
	python3 scripts/report_sneakybass_tracking_alignment.py

inventory-external-fixture-sources:
	python3 scripts/inventory_external_fixture_sources.py

inspect-instrument-route-logic:
	python3 scripts/inspect_instrument_route_logic.py

report-full-mix-route-examples:
	python3 scripts/report_full_mix_route_examples.py

test-real-note-samples-full-mix-route-examples:
	MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_ROUTE_EXAMPLE_LIMIT=48 $(MAKE) test-real-note-samples-full-mix

debug-real-note-piano-guitar-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh keyboard_electronic_001-071-025

debug-real-note-piano-guitar-visual-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh keyboard_electronic_002-033-050

debug-real-note-vocal-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocadito_35_A1_004_A2

debug-real-note-vocal-vibrato-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocalset_f7_scales_vibrato_i_19_C_4

debug-real-note-vocal-piano-miss-route: build/analyzer_real_note_samples
	sh scripts/run_real_note_debug_sample.sh vocalset_f7_scales_belt_u_3_D_4

report-real-note-debug-sample:
	python3 scripts/report_real_note_debug_sample.py

report-real-note-fixture-coverage:
	python3 scripts/report_real_note_fixture_coverage.py

report-external-fixture-inventory:
	python3 scripts/report_external_fixture_inventory.py

audit-real-note-vocals: build/analyzer_real_note_samples
	sh scripts/run_real_note_vocal_audit.sh

report-real-note-vocal-audit:
	python3 scripts/report_real_note_vocal_audit.py

report-real-note-full-mix-shards:
	python3 scripts/report_real_note_full_mix_shards.py

test-real-note-vocal-display-recall: audit-real-note-vocals
	python3 scripts/test_real_note_vocal_display_recall.py

inspect-external-vocal-manifests:
	python3 scripts/inspect_external_vocal_manifests.py

plan-real-note-vocal-fixture:
	python3 scripts/manage_real_note_vocal_fixture.py plan

apply-real-note-vocal-fixture:
	python3 scripts/manage_real_note_vocal_fixture.py apply

commit-instrument-route-inspection:
	python3 scripts/commit_staged_source_changes.py --message "test: inspect instrument route logic"

commit-full-mix-route-observability:
	python3 scripts/commit_staged_source_changes.py --message "test: expose full mix route examples"

test-instrument-synth-c5: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C5" build/analyzer_instrument_samples

analyze-instrument-synth-c5: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="build" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C5" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="build/synth_c5_attributes.tsv" build/analyzer_instrument_samples

report-instrument-synth-c5:
	python3 scripts/report_synth_c5_attributes.py

inspect-synth-c5-display-path:
	python3 scripts/inspect_analyzer_source_range.py 37890 37945

inspect-synth-c5-ranking-path:
	python3 scripts/inspect_synth_c5_ranking_symbols.py

inspect-synth-c5-low-octave-policy:
	python3 scripts/inspect_analyzer_source_range.py 15062 15375

inspect-synth-c5-pre-display-policy:
	python3 scripts/inspect_analyzer_source_range.py 37850 37895

inspect-synth-c5-visible-lower-policy:
	python3 scripts/inspect_analyzer_source_range.py 13664 13750
test-instrument-synth-saw-lead-c4: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="saw_lead" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C4" build/analyzer_instrument_samples

analyze-instrument-synth-saw-lead-c4: build/analyzer_instrument_samples
	MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_FAMILY="synth" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PROGRAM="saw_lead" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="C4" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$(BUILD_DIR)/saw_lead_c4_attributes.tsv" build/analyzer_instrument_samples

report-instrument-synth-saw-lead-c4:
	$(PYTHON) scripts/report_voice_oohs_g3_attributes.py --attributes "$(BUILD_DIR)/saw_lead_c4_attributes.tsv"
inspect-synth-harmonic-paths:
	python3 scripts/inspect_synth_harmonic_paths.py
export-real-note-vocal-attributes: build/analyzer_real_note_samples
	python3 scripts/export_real_note_vocal_attributes.py

report-real-note-vocal-attributes:
	python3 scripts/report_real_note_vocal_attributes.py
test-external-prepared-multitrack-20:
	sh scripts/run_external_prepared_multitrack_test.sh

export-external-prepared-multitrack-attributes: build/analyzer_musicnet
	python3 scripts/export_prepared_multitrack_attributes.py

report-external-prepared-multitrack-attributes:
	python3 scripts/report_prepared_multitrack_attributes.py
profile-real-note-vocal-misses:
	python3 scripts/profile_real_note_vocal_misses.py

report-code-baseline-diff:
	python3 scripts/report_code_baseline_diff.py

test-real-note-vocal-recall-regression: audit-real-note-vocals
	python3 scripts/check_real_note_vocal_recall.py build/real_note_vocal_audit.out --minimum-hits 167
