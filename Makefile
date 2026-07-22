CXX ?= g++
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
TAR ?= tar
FFMPEG ?= ffmpeg
CURL ?= curl
ARIA2C ?= aria2c
BUILD_DIR ?= build
ANDROID_SDK_ROOT ?= $(CURDIR)/$(BUILD_DIR)/android-sdk
ANDROID_GRADLE_VERSION ?= 8.10.2
ANDROID_EMULATOR_API ?= 35
ANDROID_EMULATOR_ABI ?= x86_64
ANDROID_EMULATOR_IMAGE ?= google_apis
ANDROID_AVD_NAME ?= music_analyzer_api$(ANDROID_EMULATOR_API)_$(ANDROID_EMULATOR_ABI)
ANDROID_AVD_HOME ?= $(CURDIR)/$(BUILD_DIR)/android-avd
ANDROID_ROUTE_INTERVAL ?= 1
ANDROID_ADB := $(ANDROID_SDK_ROOT)/platform-tools/adb
ANDROID_PROFILE_PACKAGE ?= dev.benalu.musicanalyzer.bassguitar
BASS_GUITAR_APK := android/app/build/outputs/apk/bassGuitar/debug/app-bassGuitar-debug.apk
COMPLETE_APK := android/app/build/outputs/apk/complete/debug/app-complete-debug.apk
ANDROID_GRADLE_BIN := $(BUILD_DIR)/gradle/gradle-$(ANDROID_GRADLE_VERSION)/bin/gradle
GRADLE ?= $(if $(wildcard $(ANDROID_GRADLE_BIN)),$(ANDROID_GRADLE_BIN),gradle)
DEPS_DIR ?= $(BUILD_DIR)/deps
BUILD_TIME := $(shell date +%Y.%m%d.%H%M)
BUILD_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
STANDALONE_VERSION := $(BUILD_TIME).$(BUILD_COMMIT)
RUN_WITH_DURATION := $(SHELL) scripts/run_with_duration.sh
REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS ?=
MEASURE_INSTRUMENT_PATTERN_ARGS ?= --limit 4 --min-positive-samples 20 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 1
MEASURE_REAL_NOTE_PATTERN_ARGS ?= --limit 4 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 3 --beam-width 160 --show-examples 1
MEASURE_GUITAR_PATTERN_ARGS ?= --top-buckets 4 --limit 4 --min-positive-recordings 3 --max-negative-recordings 0 --max-conditions 3 --beam-width 180 --show-examples 1
MEASURE_DRUM_PATTERN_ARGS ?= --top-routes 4 --limit 4 --min-positive-samples 3 --max-negative-samples 0 --max-conditions 3 --beam-width 220 --show-examples 1
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
DRUM_SAMPLE_SOURCE_DIR ?= /media/kyz/sshflashtor/DrumSamples
DRUM_SAMPLE_BUILD_DIR ?= $(BUILD_DIR)/drum_samples
DRUM_SAMPLE_LIMIT ?= 160
DRUM_SAMPLE_SELECTION ?= first
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
UNRAR ?= unrar
DRUM_SAMPLE_SPREAD_BUILD_DIR ?= $(BUILD_DIR)/drum_samples_spread
DRUM_SAMPLE_SPREAD_LIMIT ?= 160
DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT ?= 40
DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT ?= 15
DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT ?= 55
DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT ?= 80
DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT ?= 90
DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT ?= 95
DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT ?= 78
DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT ?= 88
DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT ?= 86
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
DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT ?= 88
DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT ?= 60
DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT ?= 60
DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT ?= 58
DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT ?= 20
DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT ?= 50
DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT ?= 66
DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT ?= 45
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
HF_DRUM_KIT_SAMPLE_DIR ?= $(BUILD_DIR)/hf_drum_kit_samples
HF_DRUM_KIT_LIMIT_PER_CATEGORY ?= 0
HF_DRUM_KIT_MIN_RECALL_PERCENT ?= 20
HF_DRUM_KIT_MIN_PRECISION_PERCENT ?= 18
HF_DRUM_KIT_MIN_KICK_PRIMARY_PERCENT ?= 60
HF_DRUM_KIT_MIN_SNARE_PRIMARY_PERCENT ?= 90
HF_DRUM_KIT_MIN_HIHAT_PRIMARY_PERCENT ?= 95
HF_DRUM_KIT_MIN_CRASH_PRIMARY_PERCENT ?= 90
HF_DRUM_KIT_MIN_TOM_PRIMARY_PERCENT ?= 85
HF_DRUM_KIT_MIN_RIDE_PRIMARY_PERCENT ?= 95
HF_DRUM_KIT_MIN_RIM_PRIMARY_PERCENT ?= 45
HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT ?= 12
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
MDB_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/mdb_drums_samples
MDB_DRUMS_SOURCE_ROOT ?=
MDB_DRUMS_RECORDING_LIMIT ?= 0
MDB_DRUMS_MIN_RECORDINGS ?= 20
MDB_DRUMS_REQUIRED_WINDOWS ?= 80
MDB_DRUMS_MIN_RECALL_PERCENT ?= 45
MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT ?= 0
MDB_DRUMS_MIN_PRECISION_PERCENT ?= 45
MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT ?= 75
MDB_DRUMS_MISS_LOG ?= $(BUILD_DIR)/mdb_drums_misses.log
STAR_DRUMS_URL ?= https://zenodo.org/records/15690078/files/STAR_Drums_preview.zip?download=1
STAR_DRUMS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/star_drums
STAR_DRUMS_ARCHIVE ?= $(STAR_DRUMS_SOURCE_DIR)/STAR_Drums_preview.zip
STAR_DRUMS_SAMPLE_DIR ?= $(BUILD_DIR)/star_drums_preview_samples
STAR_DRUMS_AUDIO_FLAVOR ?= mix
STAR_DRUMS_RECORDING_LIMIT ?= 0
STAR_DRUMS_MIN_RECORDINGS ?= 4
STAR_DRUMS_REQUIRED_WINDOWS ?= 12
STAR_DRUMS_MIN_RECALL_PERCENT ?= 25
STAR_DRUMS_MIN_WINDOW_RECALL_PERCENT ?= 0
STAR_DRUMS_MIN_PRECISION_PERCENT ?= 20
STAR_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT ?= 100
STAR_DRUMS_MISS_LOG ?= $(BUILD_DIR)/star_drums_misses.log
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
MAPS_PIANO_MIN_CHORD_RECALL_PERCENT ?= 20
MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT ?= 70
MAPS_PIANO_MIN_CHORD_CHECKS ?= 20
MAPS_PIANO_KINDS ?= UCHO,RAND,MUS
MAPS_PIANO_NOTE_RECORDING_LIMIT ?= 240
MAPS_PIANO_NOTE_MIN_RECORDINGS ?= 160
MAPS_PIANO_NOTE_REQUIRED_WINDOWS ?= 160
MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING ?= 2
MAPS_PIANO_NOTE_MIN_RECALL_PERCENT ?= 70
MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT ?= 80
MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT ?= 90
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
REAL_SAMPLE_SOURCE_DIR ?= $(BUILD_DIR)/real_sample_sources
NSYNTH_SAMPLE_URL ?= http://download.magenta.tensorflow.org/datasets/nsynth/nsynth-test.jsonwav.tar.gz
NSYNTH_SAMPLE_ARCHIVE ?= $(REAL_SAMPLE_SOURCE_DIR)/nsynth-test.jsonwav.tar.gz
NSYNTH_SAMPLE_ROOT ?= $(REAL_SAMPLE_SOURCE_DIR)/nsynth-test
REAL_NOTE_SAMPLE_DIR ?= $(BUILD_DIR)/real_note_samples
REAL_NOTE_SAMPLE_LIMIT ?= 0
GUITAR_FRETBOARD_NOTES_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_fretboard_notes_samples
GUITAR_FRETBOARD_NOTES_LIMIT ?= 0
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
GUITAR_TECHS_SAMPLE_LIMIT ?= 0
GUITAR_TECHS_MIN_GUITAR ?= 200
GUITAR_TECHS_MAX_FAILURES ?= 0
GUITAR_TECHS_CHORD_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_techs_chord_samples
GUITAR_TECHS_CHORD_SAMPLE_LIMIT ?= 0
GUITAR_TECHS_CHORD_MIN_EXCERPTS ?= 7000
GUITAR_TECHS_CHORD_MIN_WINDOWS ?= 7000
GUITAR_TECHS_CHORD_MIN_RECALL_PERCENT ?= 80
GUITAR_TECHS_CHORD_MIN_PRECISION_PERCENT ?= 80
GUITAR_TECHS_CHORD_MIN_GUITAR_RECALL_PERCENT ?= 80
GUITAR_TECHS_CHORD_MIN_CHORD_RECALL_PERCENT ?= 88
GUITAR_TECHS_CHORD_MIN_CHORD_PRECISION_PERCENT ?= 87
GUITAR_TECHS_CHORD_MAX_CONTAMINATION_PERCENT ?= 5
GUITAR_TECHS_CHORD_MAX_FALSE_VOCAL_PERCENT ?= 5
GUITAR_TECHS_DOWNLOAD_CONNECTIONS ?= 8
GUITAR_CHORD_MIX_SAMPLE_DIR ?= $(BUILD_DIR)/guitar_chord_mix_samples
GUITAR_CHORD_MIX_LIMIT ?= 0
GUITAR_CHORD_MIX_MIN_EXCERPTS ?= 500
GUITAR_CHORD_MIX_MIN_WINDOWS ?= 500
GUITAR_CHORD_MIX_MIN_RECALL_PERCENT ?= 75
GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT ?= 65
GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT ?= 75
GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT ?= 80
GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT ?= 84
GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT ?= 20
GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT ?= 5
GUITAR_CHORD_MIX_MISS_LOG ?= $(BUILD_DIR)/guitar_chord_mix_misses.log
EGFXSET_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/egfxset_guitar_samples
EGFXSET_GUITAR_SAMPLE_LIMIT ?= 0
EGFXSET_GUITAR_DOWNLOAD_JOBS ?= 8
EGFXSET_GUITAR_MIN_EXCERPTS ?= 490
EGFXSET_GUITAR_MIN_WINDOWS ?= 490
EGFXSET_GUITAR_MIN_RECALL_PERCENT ?= 75
EGFXSET_GUITAR_MIN_PRECISION_PERCENT ?= 65
EGFXSET_GUITAR_MIN_GUITAR_RECALL_PERCENT ?= 75
EGFXSET_GUITAR_MAX_CONTAMINATION_PERCENT ?= 35
EGFXSET_GUITAR_MAX_FALSE_VOCAL_PERCENT ?= 10
EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT ?= 20
GAPS_GUITAR_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/gaps
GAPS_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/gaps_guitar_samples
GAPS_GUITAR_METADATA_URL ?= https://huggingface.co/datasets/xavriley/GAPS/raw/main/gaps_metadata_with_splits.csv
GAPS_GUITAR_BASE_URL ?= https://huggingface.co/datasets/xavriley/GAPS/resolve/main
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
GAPS_GUITAR_FULL_SAMPLE_LIMIT ?= 0
GAPS_GUITAR_FULL_MIN_EXCERPTS ?= 250
GAPS_GUITAR_FULL_MIN_WINDOWS ?= 1000
GAPS_GUITAR_FULL_MISS_LOG ?= $(BUILD_DIR)/gaps_guitar_full_misses.log
GUITARSET_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/guitarset
GUITARSET_ROOT ?= $(BUILD_DIR)/guitarset
GUITARSET_MISS_LOG ?= $(BUILD_DIR)/guitarset_verbose.log
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
PHILHARMONIA_SAMPLE_LIMIT ?= 5000
PHILHARMONIA_BASE_URL ?= https://philharmonia-assets.s3-eu-west-1.amazonaws.com/uploads/2020/02/12112005
PHILHARMONIA_FULL_SAMPLE_DIR ?= $(BUILD_DIR)/philharmonia_samples_full
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
GOOD_SOUNDS_SAMPLE_LIMIT ?= 1000
GOOD_SOUNDS_MIN_SAMPLES ?= 500
GOOD_SOUNDS_MIN_BASS ?= 50
GOOD_SOUNDS_MIN_OTHER ?= 450
GOOD_SOUNDS_MAX_FAILURES ?= 20
IOWA_PIANO_PAGE_URL ?= https://theremin.music.uiowa.edu/MISpiano.html
IOWA_PIANO_FILE_BASE_URL ?= https://theremin.music.uiowa.edu/sound files/MIS/Piano_Other/piano/
IOWA_PIANO_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_piano
IOWA_PIANO_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_piano_samples
IOWA_PIANO_SAMPLE_LIMIT ?= 85
IOWA_PIANO_MIN_PIANO ?= 85
IOWA_PIANO_DOWNLOAD_RETRIES ?= 4
IOWA_BASS_ZIP_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Double Bass/Bass.pizz.ff.sulE.stereo.zip
IOWA_BASS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_bass
IOWA_BASS_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_bass_samples
IOWA_BASS_SAMPLE_LIMIT ?= 24
IOWA_BASS_MIN_BASS ?= 20
IOWA_ZIP_DOWNLOAD_RETRIES ?= 4
IOWA_STRINGS_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_strings
IOWA_STRINGS_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_strings_samples
IOWA_STRINGS_SAMPLE_LIMIT ?= 20
IOWA_STRINGS_MIN_SAMPLES ?= 18
IOWA_STRINGS_MIN_BASS ?= 0
IOWA_STRINGS_MIN_OTHER ?= 18
IOWA_STRINGS_MAX_FAILURES ?= 2
IOWA_STRINGS_VIOLIN_ARCO_SULG_URL ?= https://theremin.music.uiowa.edu/sound files/MIS Pitches - 2014/Strings/Violin/Violin.arco.ff.sulG.stereo.zip
IOWA_ORCHESTRA_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/iowa_orchestra
IOWA_ORCHESTRA_SAMPLE_DIR ?= $(BUILD_DIR)/iowa_orchestra_samples
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
IDMT_BASS_LINES_SAMPLE_LIMIT ?= 0
IDMT_BASS_LINES_MIN_BASS ?= 600
IDMT_BASS_LINES_MAX_FAILURES ?= 2
IDMT_BASS_LINES_EXPRESSIONS ?= NO
IDMT_BASS_LINES_MIN_NOTE_DURATION ?= 0.18
IDMT_GUITAR_URL ?= https://zenodo.org/api/records/7544110/files/IDMT-SMT-GUITAR_V2.zip/content
IDMT_GUITAR_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/idmt_guitar
IDMT_GUITAR_ARCHIVE ?= $(IDMT_GUITAR_SOURCE_DIR)/IDMT-SMT-GUITAR_V2.zip
IDMT_GUITAR_SAMPLE_DIR ?= $(BUILD_DIR)/idmt_guitar_samples
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
VOCADITO_SAMPLE_LIMIT ?= 0
VOCADITO_MIN_VOCALS ?= 300
VOCADITO_MAX_FAILURES ?= 1
VOCADITO_ANNOTATOR ?= A1
VOCADITO_MAX_CENTS ?= 25
VOCADITO_MIN_NOTE_DURATION ?= 0.22
VOCALSET_URL ?= https://zenodo.org/api/records/10200775/files/VocalSet.zip/content
VOCALSET_SOURCE_DIR ?= $(REAL_SAMPLE_SOURCE_DIR)/vocalset
VOCALSET_ARCHIVE ?= $(VOCALSET_SOURCE_DIR)/VocalSet.zip
VOCALSET_SAMPLE_DIR ?= $(BUILD_DIR)/vocalset_samples
VOCALSET_SAMPLE_LIMIT ?= 1200
VOCALSET_MIN_VOCALS ?= 800
VOCALSET_MAX_FAILURES ?= 30
VOCALSET_MAX_CENTS ?= 25
VOCALSET_MIN_NOTE_DURATION ?= 0.22
VOCALSET_ALLOWED_TECHNIQUES ?= belt,breathy,fast_forte,fast_piano,forte,lip_trill,messa,slow_forte,slow_piano,straight,trill,trillo,vibrato
REAL_NOTE_MIN_BASS ?= 100
REAL_NOTE_MIN_GUITAR ?= 300
REAL_NOTE_MIN_PIANO ?= 1000
REAL_NOTE_MIN_VOCALS ?= 20
REAL_NOTE_MIN_OTHER ?= 500
REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT ?= 99
REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT ?= 80
REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT ?= 65
REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT ?= 70
REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT ?= 85
REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT ?= 90
REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT ?= 75
REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT ?= 25
REAL_NOTE_FULL_MIX_MAX_FAILURES ?= 0
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
TEST_BINS := $(BUILD_DIR)/analyzer_smoke $(BUILD_DIR)/analyzer_cases $(BUILD_DIR)/analyzer_midi_ranges $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd $(BUILD_DIR)/analyzer_drum_samples $(BUILD_DIR)/analyzer_instrument_samples $(BUILD_DIR)/analyzer_real_note_samples $(BUILD_DIR)/analyzer_instrument_family_samples
STANDALONE_BIN := $(BUILD_DIR)/music-analyzer-standalone
BASS_GUITAR_STANDALONE_BIN := $(BUILD_DIR)/music-analyzer-bass-guitar

.PHONY: FORCE all standalone standalone-bass-guitar setup-android setup-android-emulator android-emulator android-emulator-stop android-stop-apps android-uninstall-old-packages android-profile android-profile-bass-guitar android-profile-complete android-audio-status android-route-desktop-audio android-route-desktop-audio-watch android-grant-permissions android-install-bass-guitar android-install-complete android-run android-run-bass-guitar android-run-complete android android-complete android-bass-guitar android-check check-standalone-deps install-standalone-deps test-standalone profile-standalone prepare-drum-samples test-drum-samples prepare-drum-samples-spread test-drum-samples-spread analyze-drum-primary-misses analyze-drum-rule-grid find-drum-attribute-patterns prepare-drum-samples-full test-drum-samples-full prepare-drum-machine-samples test-drum-machine-samples prepare-hf-drum-kit-samples test-hf-drum-kit-samples download-idmt-drums-samples prepare-idmt-drums-samples test-idmt-drums-samples prepare-mdb-drums-samples test-mdb-drums-samples analyze-mdb-drums-misses analyze-mdb-drum-attributes download-star-drums-samples prepare-star-drums-samples test-star-drums-samples analyze-star-drums-misses analyze-star-drum-attributes test-drum-real-world-samples test-drum-real-world-samples-full download-medley-solos-samples prepare-medley-solos-samples test-medley-solos-samples download-maps-piano-samples prepare-maps-piano-samples test-maps-piano-samples prepare-maps-piano-note-samples test-maps-piano-note-samples download-bach10-mf0-synth-samples prepare-bach10-mf0-synth-samples test-bach10-mf0-synth-samples prepare-instrument-samples test-instrument-samples analyze-instrument-sample-attributes download-real-note-samples prepare-real-note-samples test-real-note-samples test-real-note-samples-full-mix analyze-real-note-misses analyze-real-note-attributes inspect-real-note-attribute-buckets find-real-note-attribute-patterns prepare-guitar-fretboard-note-samples test-guitar-fretboard-note-samples download-guitar-techs-samples prepare-guitar-techs-samples test-guitar-techs-samples download-guitar-techs-chord-samples prepare-guitar-techs-chord-samples test-guitar-techs-chord-samples prepare-guitar-chord-mix-samples test-guitar-chord-mix-samples analyze-guitar-chord-mix-misses analyze-guitar-chord-mix-attributes inspect-guitar-chord-mix-attribute-buckets find-guitar-chord-mix-attribute-patterns prepare-egfxset-guitar-samples test-egfxset-guitar-samples prepare-gaps-guitar-samples test-gaps-guitar-samples analyze-gaps-guitar-misses download-guitarset-samples prepare-downloaded-guitarset test-downloaded-guitarset analyze-guitarset-misses download-philharmonia-samples prepare-philharmonia-samples test-philharmonia-samples prepare-philharmonia-samples-full test-philharmonia-samples-full download-good-sounds-samples prepare-good-sounds-samples test-good-sounds-samples prepare-iowa-piano-samples test-iowa-piano-samples prepare-iowa-bass-samples test-iowa-bass-samples prepare-iowa-strings-samples test-iowa-strings-samples prepare-iowa-orchestra-samples test-iowa-orchestra-samples prepare-iowa-orchestra-full-samples test-iowa-orchestra-full-samples download-idmt-bass-lines-samples prepare-idmt-bass-lines-samples test-idmt-bass-lines-samples download-idmt-guitar-samples prepare-idmt-guitar-samples test-idmt-guitar-samples download-tinysol-samples prepare-tinysol-samples test-tinysol-samples download-vocadito-samples prepare-vocadito-samples test-vocadito-samples download-vocalset-samples prepare-vocalset-samples test-vocalset-samples test-configured-real-world-samples test-real-world-samples test-real-world-samples-full test-real-world-samples-max test-midi-ranges clean clean-pycache deps install-user test real-dataset-sources inspect-real-dataset-catalog inspect-real-goal-coverage inspect-real-goal-20 inspect-real-goal-full inspect-real-medleydb inspect-real-musdb inspect-real-slakh inspect-real-choralsynth inspect-real-cocochorales inspect-real-synthsod-remote inspect-real-synthsod extract-real-synthsod-archives inspect-real-polyvocal inspect-real-prepared-multitrack inspect-real-multtipop inspect-real-musicnet-remote inspect-real-musicnet inspect-real-musicnet-full inspect-real-spheres inspect-real-guitarset inspect-real-maestro inspect-real-egmd test-musicnet-remote test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-synthsod-remote test-synthsod-archive-extract test-synthsod-inspector test-synthsod-prepare test-polyvocal-inspector test-polyvocal-prepare test-prepared-multitrack-inspector test-prepared-multitrack-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-drum-sample-prepare test-hf-drum-kit-prepare test-idmt-drums-prepare test-mdb-drums-prepare test-star-drums-prepare test-medley-solos-prepare test-maps-piano-prepare test-bach10-mf0-synth-prepare test-instrument-sample-attribute-summary test-philharmonia-prepare test-good-sounds-prepare test-iowa-piano-prepare test-iowa-zip-prepare test-idmt-bass-lines-prepare test-idmt-guitar-prepare test-tinysol-prepare test-vocadito-prepare test-vocalset-prepare test-guitar-fretboard-note-prepare test-guitar-techs-prepare test-guitar-techs-chord-prepare test-guitar-chord-mix-prepare test-gaps-guitar-prepare test-guitarset-miss-analysis test-guitarset-attribute-summary test-guitarset-attribute-buckets test-guitarset-attribute-patterns test-real-note-miss-analysis test-real-note-attribute-summary test-real-note-attribute-buckets test-real-note-attribute-patterns test-egmd-miss-analysis test-egmd-drum-attribute-summary test-drum-primary-analysis test-real-goal-script test-real-goal-fixture test-musicnet-fixture test-medleydb-fixture test-slakh-fixture test-choralsynth-fixture test-cocochorales-fixture test-synthsod-fixture test-polyvocal-fixture test-prepared-multitrack-fixture test-multtipop-audio-root-fixture test-guitarset-fixture test-maestro-fixture test-egmd-fixture test-bach10-fixture test-direct-fit-small-fixture test-urmp-fixture test-real-goal-20 test-real-goal-full test-real-multitrack-20 test-real-multitrack-full test-real-urmp test-real-urmp-full test-real-musicnet-20 test-real-musicnet-full test-real-medleydb-20 test-real-slakh-20 test-real-slakh-full test-real-choralsynth-20 test-real-cocochorales-20 test-real-synthsod-20 test-real-synthsod-full test-real-polyvocal-20 test-real-prepared-multitrack-20 test-real-prepared-multitrack-full test-real-multtipop-20 test-real-multtipop-full test-real-guitarset-20 test-real-guitarset-full test-real-maestro-20 test-real-maestro-full test-real-egmd-20 test-real-egmd-full inspect-real-multitrack-20 inspect-real-multitrack-full inspect-real-urmp inspect-real-urmp-full inspect-urmp-fixture decode-urmp-fixture decode-direct-fit-small-fixture update-urmp-fixture update-direct-fit-small-fixture
.PHONY: prepare-gaps-guitar-samples-full test-gaps-guitar-samples-full analyze-gaps-guitar-misses-full
.PHONY: measure-analyzer-attributes measure-analyzer-attribute-rows measure-analyzer-patterns inspect-instrument-sample-owner-buckets find-instrument-owner-patterns test-instrument-sample-owner-buckets test-instrument-owner-patterns test-analyzer-pattern-report test-measure-analyzer-patterns-target analyze-drum-tom-bleed-caps

.PRECIOUS: $(NSYNTH_SAMPLE_ARCHIVE) $(TINYSOL_ARCHIVE) $(GOOD_SOUNDS_ARCHIVE) $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P1_CHORDS_ARCHIVE) $(GUITAR_TECHS_P2_CHORDS_ARCHIVE) $(IDMT_DRUMS_ARCHIVE) $(IDMT_GUITAR_ARCHIVE) $(STAR_DRUMS_ARCHIVE) $(MEDLEY_SOLOS_ARCHIVE) $(MAPS_PIANO_ARCHIVE) $(BACH10_MF0_SYNTH_ARCHIVE) $(VOCALSET_ARCHIVE)

FORCE:

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

android-grant-permissions:
	"$(ANDROID_ADB)" wait-for-device
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.RECORD_AUDIO
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.RECORD_AUDIO

android-install-bass-guitar: android-bass-guitar
	"$(ANDROID_ADB)" wait-for-device
	"$(ANDROID_ADB)" install -r "$(BASS_GUITAR_APK)"
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.bassguitar android.permission.RECORD_AUDIO

android-install-complete: android-complete
	"$(ANDROID_ADB)" wait-for-device
	"$(ANDROID_ADB)" install -r "$(COMPLETE_APK)"
	-"$(ANDROID_ADB)" shell pm grant dev.benalu.musicanalyzer.complete android.permission.RECORD_AUDIO

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

$(BUILD_DIR)/visualizer_renderer.o: src/visualizer_renderer.cpp src/visualizer_renderer.hpp src/analyzer.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/standalone.o: src/standalone.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(SDL2_DEP) FORCE | $(BUILD_DIR)
	$(MAKE) check-standalone-deps
	$(CXX) $(CXXFLAGS) $(SDL2_CFLAGS) -DMAO_STANDALONE_WITH_SDL=1 -DMAO_STANDALONE_VERSION=\"$(STANDALONE_VERSION)\" -Isrc -c $< -o $@

$(BUILD_DIR)/standalone_bass_guitar.o: src/standalone.cpp src/analyzer.hpp src/visualizer_renderer.hpp $(SDL2_DEP) FORCE | $(BUILD_DIR)
	$(MAKE) check-standalone-deps
	$(CXX) $(CXXFLAGS) $(SDL2_CFLAGS) -DMAO_STANDALONE_WITH_SDL=1 -DMAO_STANDALONE_BASS_GUITAR=1 -DMAO_STANDALONE_VERSION=\"$(STANDALONE_VERSION)\" -Isrc -c $< -o $@

$(STANDALONE_BIN): $(ANALYZER_TEST_OBJ) $(RENDERER_OBJ) $(BUILD_DIR)/standalone.o
	$(CXX) -o $@ $^ $(SDL2_LIBS) -lm -pthread

$(BASS_GUITAR_STANDALONE_BIN): $(ANALYZER_TEST_OBJ) $(RENDERER_OBJ) $(BUILD_DIR)/standalone_bass_guitar.o
	$(CXX) -o $@ $^ $(SDL2_LIBS) -lm -pthread

$(BUILD_DIR)/analyzer_test.o: src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	tmp="$@.$$$$.tmp"; $(CXX) $(CXXFLAGS) -Isrc -c $< -o "$$tmp"; mv "$$tmp" "$@"

$(BUILD_DIR)/analyzer_smoke.o: tests/analyzer_smoke.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_cases.o: tests/analyzer_cases.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_midi_ranges.o: tests/analyzer_midi_ranges.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_urmp.o: tests/analyzer_urmp.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_musicnet.o: tests/analyzer_musicnet.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_multtipop.o: tests/analyzer_multtipop.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_guitarset.o: tests/analyzer_guitarset.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_maestro.o: tests/analyzer_maestro.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_egmd.o: tests/analyzer_egmd.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_drum_samples.o: tests/analyzer_drum_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_instrument_samples.o: tests/analyzer_instrument_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_real_note_samples.o: tests/analyzer_real_note_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_instrument_family_samples.o: tests/analyzer_instrument_family_samples.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_smoke: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_smoke.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_cases: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_cases.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_midi_ranges: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_midi_ranges.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_urmp: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_urmp.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_musicnet: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_musicnet.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_multtipop: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_multtipop.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_guitarset: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_guitarset.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_maestro: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_maestro.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_egmd: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_egmd.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_drum_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_drum_samples.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_instrument_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_instrument_samples.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_real_note_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_real_note_samples.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_instrument_family_samples: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_instrument_family_samples.o
	$(CXX) -o $@ $^ -lm -pthread

test-standalone: $(STANDALONE_BIN) $(BASS_GUITAR_STANDALONE_BIN) tests/check_standalone_isolation.py android-check scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) check_standalone_isolation $(PYTHON) tests/check_standalone_isolation.py
	$(RUN_WITH_DURATION) check_standalone_version_complete $(PYTHON) tests/check_standalone_version.py $(STANDALONE_BIN)
	$(RUN_WITH_DURATION) check_standalone_version_bass_guitar $(PYTHON) tests/check_standalone_version.py $(BASS_GUITAR_STANDALONE_BIN)
	$(RUN_WITH_DURATION) standalone_self_test env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(STANDALONE_BIN) --self-test
	$(RUN_WITH_DURATION) standalone_bass_guitar_self_test env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(BASS_GUITAR_STANDALONE_BIN) --self-test

profile-standalone: standalone scripts/profile_standalone.sh
	BUILD_DIR="$(BUILD_DIR)" $(SHELL) scripts/profile_standalone.sh

prepare-drum-samples: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_LIMIT)" DRUM_SAMPLE_SELECTION="$(DRUM_SAMPLE_SELECTION)" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_LIMIT)" --selection "$(DRUM_SAMPLE_SELECTION)" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --unrar "$(UNRAR)"

test-drum-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=20 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples

prepare-drum-samples-spread: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_SPREAD_LIMIT)" DRUM_SAMPLE_SELECTION="spread" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_SPREAD_LIMIT)" --selection "spread" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --no-archives

test-drum-samples-spread: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-spread scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_spread env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_SPREAD_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_SPREAD_MAX_TOM_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples

analyze-drum-primary-misses: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-spread scripts/analyze_drum_primary_debug.py
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=kick MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=kick MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/kick_primary_debug.out" 2> "$(BUILD_DIR)/kick_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=tom MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=tom MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/tom_primary_debug.out" 2> "$(BUILD_DIR)/tom_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=snare MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=snare MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/snare_primary_debug.out" 2> "$(BUILD_DIR)/snare_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=hihat MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=hihat MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/hihat_primary_debug.out" 2> "$(BUILD_DIR)/hihat_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=crash MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=crash MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/crash_primary_debug.out" 2> "$(BUILD_DIR)/crash_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=ride MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=ride MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/ride_primary_debug.out" 2> "$(BUILD_DIR)/ride_primary_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=220 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_SPREAD_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/rim_primary_debug.out" 2> "$(BUILD_DIR)/rim_primary_debug.err"
	$(PYTHON) scripts/analyze_drum_primary_debug.py "$(BUILD_DIR)/kick_primary_debug.err" "$(BUILD_DIR)/tom_primary_debug.err" "$(BUILD_DIR)/snare_primary_debug.err" "$(BUILD_DIR)/hihat_primary_debug.err" "$(BUILD_DIR)/crash_primary_debug.err" "$(BUILD_DIR)/ride_primary_debug.err" "$(BUILD_DIR)/rim_primary_debug.err"

analyze-drum-rule-grid: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-full scripts/analyze_drum_debug_rows.py scripts/evaluate_drum_rule_grid.py
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=kick MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=kick MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=6000 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_kick_debug.out" 2> "$(BUILD_DIR)/full_kick_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=snare MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=snare MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=5200 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_snare_debug.out" 2> "$(BUILD_DIR)/full_snare_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=tom MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=tom MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=2500 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_tom_debug.out" 2> "$(BUILD_DIR)/full_tom_debug.err"
	env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES=rim MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY=rim MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1 MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY_LIMIT=900 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=100 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" $(BUILD_DIR)/analyzer_drum_samples > "$(BUILD_DIR)/full_rim_debug.out" 2> "$(BUILD_DIR)/full_rim_debug.err"
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected tom --focus tom --against snare --examples 8 "$(BUILD_DIR)/full_tom_debug.err"
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected snare --focus tom --against snare --examples 8 "$(BUILD_DIR)/full_snare_debug.err"
	$(PYTHON) scripts/analyze_drum_debug_rows.py --expected kick --focus tom --against kick --examples 8 "$(BUILD_DIR)/full_kick_debug.err"
	$(PYTHON) scripts/evaluate_drum_rule_grid.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" --top 80

analyze-drum-tom-bleed-caps: scripts/evaluate_drum_tom_bleed_caps.py
	@if [ ! -f "$(BUILD_DIR)/full_kick_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_snare_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_tom_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_rim_debug.err" ]; then $(MAKE) analyze-drum-rule-grid; fi
	$(PYTHON) scripts/evaluate_drum_tom_bleed_caps.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" $(DRUM_TOM_BLEED_ARGS)

find-drum-attribute-patterns: scripts/find_drum_attribute_patterns.py
	@if [ ! -f "$(BUILD_DIR)/full_kick_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_snare_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_tom_debug.err" ] || [ ! -f "$(BUILD_DIR)/full_rim_debug.err" ]; then $(MAKE) analyze-drum-rule-grid; fi
	$(PYTHON) scripts/find_drum_attribute_patterns.py "$(BUILD_DIR)/full_kick_debug.err" "$(BUILD_DIR)/full_snare_debug.err" "$(BUILD_DIR)/full_tom_debug.err" "$(BUILD_DIR)/full_rim_debug.err" $(if $(PATTERN_ROUTE),--route "$(PATTERN_ROUTE)") $(PATTERN_ARGS)

prepare-drum-samples-full: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_SAMPLE_FULL_LIMIT)" DRUM_SAMPLE_SELECTION="$(DRUM_SAMPLE_SELECTION)" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_SAMPLE_SOURCE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_SAMPLE_FULL_BUILD_DIR)" --limit-per-category "$(DRUM_SAMPLE_FULL_LIMIT)" --selection "$(DRUM_SAMPLE_SELECTION)" --source-filter "$(DRUM_SAMPLE_SOURCE_FILTER)" --unrar "$(UNRAR)"

test-drum-samples-full: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-samples-full scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_samples_full env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_SAMPLE_FULL_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(DRUM_SAMPLE_FULL_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_SAMPLE_FULL_MAX_TOM_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

prepare-drum-machine-samples: scripts/prepare_drum_samples.py | $(BUILD_DIR)
	DRUM_SAMPLE_SOURCE_DIR="$(DRUM_SAMPLE_SOURCE_DIR)" DRUM_SAMPLE_BUILD_DIR="$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" DRUM_SAMPLE_LIMIT="$(DRUM_MACHINE_SAMPLE_LIMIT)" DRUM_SAMPLE_SELECTION="spread" DRUM_SAMPLE_SOURCE_FILTER="$(DRUM_MACHINE_SAMPLE_FILTER)" $(PYTHON) scripts/prepare_drum_samples.py --source "$(DRUM_SAMPLE_SOURCE_DIR)" --output "$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" --limit-per-category "$(DRUM_MACHINE_SAMPLE_LIMIT)" --selection "spread" --source-filter "$(DRUM_MACHINE_SAMPLE_FILTER)" --unrar "$(UNRAR)"

test-drum-machine-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-drum-machine-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_drum_machine_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(DRUM_MACHINE_SAMPLE_BUILD_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(DRUM_MACHINE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_RECALL_PERCENT="$(DRUM_MACHINE_MIN_KICK_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(DRUM_MACHINE_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_RECALL_PERCENT="$(DRUM_MACHINE_MIN_HIHAT_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_RECALL_PERCENT="$(DRUM_MACHINE_MIN_CRASH_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_RECALL_PERCENT="$(DRUM_MACHINE_MIN_TOM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RIDE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT="$(DRUM_MACHINE_MIN_RIM_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(DRUM_MACHINE_MAX_KICK_FALSE_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT="$(DRUM_MACHINE_MAX_TOM_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

prepare-hf-drum-kit-samples: scripts/prepare_hf_drum_kit_samples.py | $(BUILD_DIR)
	HF_DRUM_KIT_SAMPLE_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" HF_DRUM_KIT_LIMIT_PER_CATEGORY="$(HF_DRUM_KIT_LIMIT_PER_CATEGORY)" $(PYTHON) scripts/prepare_hf_drum_kit_samples.py --output "$(HF_DRUM_KIT_SAMPLE_DIR)"

test-hf-drum-kit-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-hf-drum-kit-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_hf_drum_kit_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(HF_DRUM_KIT_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(HF_DRUM_KIT_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_KICK_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_KICK_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_SNARE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_HIHAT_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_HIHAT_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_CRASH_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_CRASH_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_TOM_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_TOM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIDE_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RIDE_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_PRIMARY_RECALL_PERCENT="$(HF_DRUM_KIT_MIN_RIM_PRIMARY_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

download-idmt-drums-samples: $(IDMT_DRUMS_ARCHIVE)

$(IDMT_DRUMS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(IDMT_DRUMS_SOURCE_DIR)"
	if [ -s "$(IDMT_DRUMS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(IDMT_DRUMS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(IDMT_DRUMS_ARCHIVE)" "$(IDMT_DRUMS_ARCHIVE).part"; fi
	if [ ! -s "$(IDMT_DRUMS_ARCHIVE)" ] && [ -s "$(IDMT_DRUMS_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(IDMT_DRUMS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(IDMT_DRUMS_ARCHIVE).part" "$(IDMT_DRUMS_ARCHIVE)"; fi
	if [ ! -s "$(IDMT_DRUMS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(IDMT_DRUMS_DOWNLOAD_CONNECTIONS)" -s "$(IDMT_DRUMS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(IDMT_DRUMS_SOURCE_DIR)" --out "IDMT-SMT-DRUMS-V2.zip.part" "$(IDMT_DRUMS_URL)"; else curl -fL -C - -o "$(IDMT_DRUMS_ARCHIVE).part" "$(IDMT_DRUMS_URL)"; fi; fi
	if [ -s "$(IDMT_DRUMS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(IDMT_DRUMS_ARCHIVE).part" >/dev/null; mv "$(IDMT_DRUMS_ARCHIVE).part" "$(IDMT_DRUMS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(IDMT_DRUMS_ARCHIVE)" >/dev/null

prepare-idmt-drums-samples: scripts/prepare_idmt_drums_samples.py download-idmt-drums-samples | $(BUILD_DIR)
	IDMT_DRUMS_ARCHIVE="$(IDMT_DRUMS_ARCHIVE)" IDMT_DRUMS_SAMPLE_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" IDMT_DRUMS_LIMIT_PER_CATEGORY="$(IDMT_DRUMS_LIMIT_PER_CATEGORY)" IDMT_DRUMS_MIN_PER_CATEGORY="$(IDMT_DRUMS_MIN_PER_CATEGORY)" $(PYTHON) scripts/prepare_idmt_drums_samples.py --archive "$(IDMT_DRUMS_ARCHIVE)" --output "$(IDMT_DRUMS_SAMPLE_DIR)" --limit-per-category "$(IDMT_DRUMS_LIMIT_PER_CATEGORY)" --min-per-category "$(IDMT_DRUMS_MIN_PER_CATEGORY)"

test-idmt-drums-samples: $(BUILD_DIR)/analyzer_drum_samples prepare-idmt-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_drums_samples env MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_DRUM_SAMPLES_DIR="$(IDMT_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES="kick,snare,hihat" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT="$(IDMT_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_RECALL_PERCENT="$(IDMT_DRUMS_MIN_SNARE_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_SNARE_PRIMARY_RECALL_PERCENT="$(IDMT_DRUMS_MIN_SNARE_PRIMARY_RECALL_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT="$(IDMT_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT="$(IDMT_DRUMS_MAX_KICK_FALSE_PERCENT)" $(BUILD_DIR)/analyzer_drum_samples

prepare-mdb-drums-samples: scripts/prepare_mdb_drums_samples.py | $(BUILD_DIR)
	MDB_DRUMS_SAMPLE_DIR="$(MDB_DRUMS_SAMPLE_DIR)" MDB_DRUMS_SOURCE_ROOT="$(MDB_DRUMS_SOURCE_ROOT)" MDB_DRUMS_RECORDING_LIMIT="$(MDB_DRUMS_RECORDING_LIMIT)" MDB_DRUMS_MIN_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_mdb_drums_samples.py --output "$(MDB_DRUMS_SAMPLE_DIR)" --source-root "$(MDB_DRUMS_SOURCE_ROOT)" --limit "$(MDB_DRUMS_RECORDING_LIMIT)" --min-recordings "$(MDB_DRUMS_MIN_RECORDINGS)"

test-mdb-drums-samples: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_mdb_drums_samples env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT="$(MDB_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT="$(MDB_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT="$(MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(BUILD_DIR)/analyzer_egmd

analyze-mdb-drums-misses: $(BUILD_DIR)/analyzer_egmd prepare-mdb-drums-samples scripts/analyze_egmd_misses.py
	env MUSIC_ANALYZER_EGMD_ROOT="$(MDB_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(MDB_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(MDB_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_MISSES=1 MUSIC_ANALYZER_EGMD_VERBOSE_MISS_LIMIT=240 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVES=1 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVE_LIMIT=240 $(BUILD_DIR)/analyzer_egmd > "$(MDB_DRUMS_MISS_LOG).summary" 2> "$(MDB_DRUMS_MISS_LOG)"
	$(PYTHON) scripts/analyze_egmd_misses.py "$(MDB_DRUMS_MISS_LOG)"

analyze-mdb-drum-attributes: analyze-mdb-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(MDB_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-star-drums-samples: $(STAR_DRUMS_ARCHIVE)

$(STAR_DRUMS_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(STAR_DRUMS_SOURCE_DIR)"
	curl -fL -C - -o "$(STAR_DRUMS_ARCHIVE)" "$(STAR_DRUMS_URL)"
	$(PYTHON) -m zipfile -t "$(STAR_DRUMS_ARCHIVE)" >/dev/null

prepare-star-drums-samples: scripts/prepare_star_drums_samples.py download-star-drums-samples | $(BUILD_DIR)
	STAR_DRUMS_ARCHIVE="$(STAR_DRUMS_ARCHIVE)" STAR_DRUMS_SAMPLE_DIR="$(STAR_DRUMS_SAMPLE_DIR)" STAR_DRUMS_AUDIO_FLAVOR="$(STAR_DRUMS_AUDIO_FLAVOR)" STAR_DRUMS_RECORDING_LIMIT="$(STAR_DRUMS_RECORDING_LIMIT)" STAR_DRUMS_MIN_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_star_drums_samples.py --archive "$(STAR_DRUMS_ARCHIVE)" --output "$(STAR_DRUMS_SAMPLE_DIR)" --audio-flavor "$(STAR_DRUMS_AUDIO_FLAVOR)" --limit "$(STAR_DRUMS_RECORDING_LIMIT)" --min-recordings "$(STAR_DRUMS_MIN_RECORDINGS)" --ffmpeg "$(FFMPEG)"

test-star-drums-samples: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_star_drums_samples env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(STAR_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT="$(STAR_DRUMS_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT="$(STAR_DRUMS_MIN_WINDOW_RECALL_PERCENT)" MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT="$(STAR_DRUMS_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT="$(STAR_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT)" $(BUILD_DIR)/analyzer_egmd

analyze-star-drums-misses: $(BUILD_DIR)/analyzer_egmd prepare-star-drums-samples scripts/analyze_egmd_misses.py
	env MUSIC_ANALYZER_EGMD_ROOT="$(STAR_DRUMS_SAMPLE_DIR)" MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS="$(STAR_DRUMS_MIN_RECORDINGS)" MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS="$(STAR_DRUMS_REQUIRED_WINDOWS)" MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=100 MUSIC_ANALYZER_EGMD_VERBOSE_MISSES=1 MUSIC_ANALYZER_EGMD_VERBOSE_MISS_LIMIT=120 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVES=1 MUSIC_ANALYZER_EGMD_VERBOSE_FALSE_POSITIVE_LIMIT=120 $(BUILD_DIR)/analyzer_egmd > "$(STAR_DRUMS_MISS_LOG).summary" 2> "$(STAR_DRUMS_MISS_LOG)"
	$(PYTHON) scripts/analyze_egmd_misses.py "$(STAR_DRUMS_MISS_LOG)"

analyze-star-drum-attributes: analyze-star-drums-misses scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) scripts/summarize_egmd_drum_attributes.py "$(STAR_DRUMS_MISS_LOG)" $(DRUM_ATTRIBUTE_ARGS)

download-medley-solos-samples: $(MEDLEY_SOLOS_METADATA) $(MEDLEY_SOLOS_ARCHIVE)

$(MEDLEY_SOLOS_METADATA): | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	curl -fL -C - -o "$(MEDLEY_SOLOS_METADATA)" "$(MEDLEY_SOLOS_METADATA_URL)"

$(MEDLEY_SOLOS_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	curl -fL -C - -o "$(MEDLEY_SOLOS_ARCHIVE)" "$(MEDLEY_SOLOS_URL)"
	$(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null

prepare-medley-solos-samples: scripts/prepare_medley_solos_samples.py download-medley-solos-samples | $(BUILD_DIR)
	MEDLEY_SOLOS_METADATA="$(MEDLEY_SOLOS_METADATA)" MEDLEY_SOLOS_ARCHIVE="$(MEDLEY_SOLOS_ARCHIVE)" MEDLEY_SOLOS_SAMPLE_DIR="$(MEDLEY_SOLOS_SAMPLE_DIR)" MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT="$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" MEDLEY_SOLOS_MIN_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MEDLEY_SOLOS_MIN_COUNTS="$(MEDLEY_SOLOS_MIN_COUNTS)" $(PYTHON) scripts/prepare_medley_solos_samples.py --metadata "$(MEDLEY_SOLOS_METADATA)" --archive "$(MEDLEY_SOLOS_ARCHIVE)" --output "$(MEDLEY_SOLOS_SAMPLE_DIR)" --limit-per-instrument "$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-counts "$(MEDLEY_SOLOS_MIN_COUNTS)"

test-medley-solos-samples: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_medley_solos_samples env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT="$(MEDLEY_SOLOS_MIN_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_instrument_family_samples

download-maps-piano-samples: $(MAPS_PIANO_ARCHIVE)

$(MAPS_PIANO_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(MAPS_PIANO_SOURCE_DIR)"
	curl -fL -C - -o "$(MAPS_PIANO_ARCHIVE)" "$(MAPS_PIANO_URL)"
	$(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null

prepare-maps-piano-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MAPS_PIANO_KINDS="$(MAPS_PIANO_KINDS)" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_SAMPLE_DIR)" --limit "$(MAPS_PIANO_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --kinds "$(MAPS_PIANO_KINDS)"

test-maps-piano-samples: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT="$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT="$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(BUILD_DIR)/analyzer_maestro

prepare-maps-piano-note-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MAPS_PIANO_KINDS="ISOL" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_NOTE_SAMPLE_DIR)" --limit "$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --kinds "ISOL"

test-maps-piano-note-samples: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_note_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 $(BUILD_DIR)/analyzer_maestro

download-bach10-mf0-synth-samples: $(BACH10_MF0_SYNTH_ARCHIVE)

$(BACH10_MF0_SYNTH_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(BACH10_MF0_SYNTH_SOURCE_DIR)"
	curl -fL -C - -o "$(BACH10_MF0_SYNTH_ARCHIVE)" "$(BACH10_MF0_SYNTH_URL)"
	$(TAR) -tzf "$(BACH10_MF0_SYNTH_ARCHIVE)" >/dev/null

prepare-bach10-mf0-synth-samples: scripts/prepare_bach10_mf0_synth_musicnet_fixture.py | $(BUILD_DIR)
	if [ -z "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" ]; then $(MAKE) download-bach10-mf0-synth-samples; fi
	BACH10_MF0_SYNTH_ARCHIVE="$(BACH10_MF0_SYNTH_ARCHIVE)" BACH10_MF0_SYNTH_SOURCE_ROOT="$(BACH10_MF0_SYNTH_SOURCE_ROOT)" BACH10_MF0_SYNTH_SAMPLE_DIR="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" BACH10_MF0_SYNTH_RECORDING_LIMIT="$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" BACH10_MF0_SYNTH_MIN_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_bach10_mf0_synth_musicnet_fixture.py --archive "$(BACH10_MF0_SYNTH_ARCHIVE)" --source-root "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" --output "$(BACH10_MF0_SYNTH_SAMPLE_DIR)" --limit "$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" --min-recordings "$(BACH10_MF0_SYNTH_MIN_RECORDINGS)"

test-bach10-mf0-synth-samples: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_musicnet

prepare-instrument-samples: scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	INSTRUMENT_SAMPLE_BUILD_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" INSTRUMENT_SAMPLE_SOURCE_DIR="$(INSTRUMENT_SAMPLE_SOURCE_DIR)" INSTRUMENT_SAMPLE_SOUNDFONT="$(INSTRUMENT_SAMPLE_SOUNDFONT)" INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE="$(INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE)" INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY="$(INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY)" INSTRUMENT_SAMPLE_DRUM_KITS="$(INSTRUMENT_SAMPLE_DRUM_KITS)" INSTRUMENT_SAMPLE_TARGET_PER_FAMILY="$(INSTRUMENT_SAMPLE_TARGET_PER_FAMILY)" INSTRUMENT_SAMPLE_JOBS="$(INSTRUMENT_SAMPLE_JOBS)" $(PYTHON) scripts/prepare_instrument_samples.py --output-root "$(INSTRUMENT_SAMPLE_BUILD_ROOT)" --download-dir "$(INSTRUMENT_SAMPLE_SOURCE_DIR)"

test-instrument-samples: $(BUILD_DIR)/analyzer_instrument_samples prepare-instrument-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" $(BUILD_DIR)/analyzer_instrument_samples

analyze-instrument-sample-attributes: $(BUILD_DIR)/analyzer_instrument_samples prepare-instrument-samples scripts/summarize_instrument_sample_attributes.py
	env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$(BUILD_DIR)/instrument_sample_attributes.tsv" $(BUILD_DIR)/analyzer_instrument_samples > "$(BUILD_DIR)/instrument_sample_attributes.out"
	$(PYTHON) scripts/summarize_instrument_sample_attributes.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSTRUMENT_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/instrument_sample_attributes.tsv"

inspect-instrument-sample-owner-buckets: scripts/inspect_instrument_sample_owner_buckets.py
	@if [ ! -f "$(BUILD_DIR)/instrument_sample_attributes.tsv" ]; then $(MAKE) analyze-instrument-sample-attributes; fi
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSPECT_INSTRUMENT_OWNER_ARGS)

find-instrument-owner-patterns: scripts/find_instrument_owner_patterns.py
	@if [ ! -f "$(BUILD_DIR)/instrument_sample_attributes.tsv" ]; then $(MAKE) analyze-instrument-sample-attributes; fi
	$(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") $(PATTERN_ARGS)

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

measure-analyzer-attribute-rows: analyze-instrument-sample-attributes analyze-real-note-attributes analyze-guitar-chord-mix-attributes analyze-drum-primary-misses
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --dump-rows > "$(BUILD_DIR)/instrument_detected_attribute_rows.tsv"
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows > "$(BUILD_DIR)/real_note_detected_attribute_rows.tsv"
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows --misses-only > "$(BUILD_DIR)/real_note_miss_attribute_rows.tsv"
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows > "$(BUILD_DIR)/guitar_chord_detected_attribute_rows.tsv"
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows --misses-only > "$(BUILD_DIR)/guitar_chord_miss_attribute_rows.tsv"
	$(PYTHON) scripts/analyze_drum_primary_debug.py --dump-rows "$(BUILD_DIR)/kick_primary_debug.err" "$(BUILD_DIR)/tom_primary_debug.err" "$(BUILD_DIR)/snare_primary_debug.err" "$(BUILD_DIR)/hihat_primary_debug.err" "$(BUILD_DIR)/crash_primary_debug.err" "$(BUILD_DIR)/ride_primary_debug.err" "$(BUILD_DIR)/rim_primary_debug.err" > "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"
	@printf '%s\n' "attribute row dumps:"
	@printf '%s\n' "  $(BUILD_DIR)/instrument_detected_attribute_rows.tsv"
	@printf '%s\n' "  $(BUILD_DIR)/real_note_detected_attribute_rows.tsv"
	@printf '%s\n' "  $(BUILD_DIR)/real_note_miss_attribute_rows.tsv"
	@printf '%s\n' "  $(BUILD_DIR)/guitar_chord_detected_attribute_rows.tsv"
	@printf '%s\n' "  $(BUILD_DIR)/guitar_chord_miss_attribute_rows.tsv"
	@printf '%s\n' "  $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"

measure-analyzer-patterns: measure-analyzer-attribute-rows analyze-drum-tom-bleed-caps scripts/report_analyzer_attribute_patterns.py
	$(PYTHON) scripts/report_analyzer_attribute_patterns.py --instrument "$(BUILD_DIR)/instrument_detected_attribute_rows.tsv" --real-note "$(BUILD_DIR)/real_note_detected_attribute_rows.tsv" --guitar-chord "$(BUILD_DIR)/guitar_chord_detected_attribute_rows.tsv" --drum "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(PATTERN_REPORT_ARGS)
	@printf '%s\n' ""
	@printf '%s\n' "generated instrument owner pattern candidates:"
	$(MAKE) find-instrument-owner-patterns PATTERN_ARGS="$(MEASURE_INSTRUMENT_PATTERN_ARGS)"
	@printf '%s\n' ""
	@printf '%s\n' "real-note full-mix pattern candidates:"
	$(MAKE) find-real-note-attribute-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_PATTERN_ARGS)"
	@printf '%s\n' ""
	@printf '%s\n' "guitar chord pattern candidates:"
	$(MAKE) find-guitar-chord-mix-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_PATTERN_ARGS)"
	@printf '%s\n' ""
	@printf '%s\n' "drum primary pattern candidates:"
	$(MAKE) find-drum-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"

download-real-note-samples: $(NSYNTH_SAMPLE_ARCHIVE)

$(NSYNTH_SAMPLE_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	curl -L -C - -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"

$(NSYNTH_SAMPLE_ROOT)/examples.json: $(NSYNTH_SAMPLE_ARCHIVE) | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	$(TAR) -xzf "$(NSYNTH_SAMPLE_ARCHIVE)" -C "$(REAL_SAMPLE_SOURCE_DIR)"

prepare-real-note-samples: scripts/prepare_nsynth_samples.py $(NSYNTH_SAMPLE_ROOT)/examples.json | $(BUILD_DIR)
	NSYNTH_SAMPLE_ROOT="$(NSYNTH_SAMPLE_ROOT)" REAL_NOTE_SAMPLE_DIR="$(REAL_NOTE_SAMPLE_DIR)" REAL_NOTE_SAMPLE_LIMIT="$(REAL_NOTE_SAMPLE_LIMIT)" $(PYTHON) scripts/prepare_nsynth_samples.py --nsynth-root "$(NSYNTH_SAMPLE_ROOT)" --output "$(REAL_NOTE_SAMPLE_DIR)" --limit "$(REAL_NOTE_SAMPLE_LIMIT)"

test-real-note-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" $(BUILD_DIR)/analyzer_real_note_samples

test-real-note-samples-full-mix: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT="$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_FULL_MIX_MAX_FAILURES)" $(BUILD_DIR)/analyzer_real_note_samples

analyze-real-note-misses: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/analyze_real_note_misses.py
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT="$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_FULL_MIX_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_verbose.out" 2> "$(BUILD_DIR)/real_note_full_mix_verbose.err"
	$(PYTHON) scripts/analyze_real_note_misses.py "$(BUILD_DIR)/real_note_full_mix_verbose.err"

analyze-real-note-attributes: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/summarize_real_note_attributes.py
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(BUILD_DIR)/real_note_full_mix_attributes.tsv" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT="$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT="$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_FULL_MIX_MAX_FAILURES)" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_attributes.out"
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/real_note_full_mix_attributes.tsv"

inspect-real-note-attribute-buckets: scripts/inspect_real_note_attribute_buckets.py
	@if [ ! -f "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" ]; then $(MAKE) analyze-real-note-attributes; fi
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(INSPECT_ARGS)

find-real-note-attribute-patterns: scripts/find_real_note_attribute_patterns.py
	@if [ ! -f "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" ]; then $(MAKE) analyze-real-note-attributes; fi
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") $(PATTERN_ARGS)

prepare-guitar-fretboard-note-samples: scripts/prepare_guitar_fretboard_notes.py | $(BUILD_DIR)
	GUITAR_FRETBOARD_NOTES_SAMPLE_DIR="$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)" GUITAR_FRETBOARD_NOTES_LIMIT="$(GUITAR_FRETBOARD_NOTES_LIMIT)" $(PYTHON) scripts/prepare_guitar_fretboard_notes.py --output "$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)"

test-guitar-fretboard-note-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-guitar-fretboard-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_fretboard_note_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GUITAR_FRETBOARD_NOTES_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GUITAR_FRETBOARD_NOTES_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(GUITAR_FRETBOARD_NOTES_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(GUITAR_FRETBOARD_NOTES_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

download-guitar-techs-samples: $(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE) $(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)

$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part"; fi
	if [ -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" >/dev/null 2>&1; then rm -f "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part"; fi
	if [ ! -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P1_singlenotes.zip.part" "$(GUITAR_TECHS_P1_SINGLENOTES_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P1_SINGLENOTES_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" >/dev/null

$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part"; fi
	if [ -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" >/dev/null 2>&1; then rm -f "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part"; fi
	if [ ! -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P2_singlenotes.zip.part" "$(GUITAR_TECHS_P2_SINGLENOTES_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P2_SINGLENOTES_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE).part" "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" >/dev/null

prepare-guitar-techs-samples: scripts/prepare_guitar_techs_samples.py download-guitar-techs-samples | $(BUILD_DIR)
	GUITAR_TECHS_SAMPLE_DIR="$(GUITAR_TECHS_SAMPLE_DIR)" GUITAR_TECHS_SAMPLE_LIMIT="$(GUITAR_TECHS_SAMPLE_LIMIT)" GUITAR_TECHS_MIN_SAMPLES="$(GUITAR_TECHS_MIN_GUITAR)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_samples.py --archive "$(GUITAR_TECHS_P1_SINGLENOTES_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_SINGLENOTES_ARCHIVE)" --output "$(GUITAR_TECHS_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_MIN_GUITAR)" --ffmpeg "$(FFMPEG)"

test-guitar-techs-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-guitar-techs-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_techs_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GUITAR_TECHS_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GUITAR_TECHS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(GUITAR_TECHS_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(GUITAR_TECHS_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

download-guitar-techs-chord-samples: $(GUITAR_TECHS_P1_CHORDS_ARCHIVE) $(GUITAR_TECHS_P2_CHORDS_ARCHIVE)

$(GUITAR_TECHS_P1_CHORDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part"; fi
	if [ -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" >/dev/null 2>&1; then rm -f "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part"; fi
	if [ ! -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P1_chords.zip.part" "$(GUITAR_TECHS_P1_CHORDS_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P1_CHORDS_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" >/dev/null

$(GUITAR_TECHS_P2_CHORDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GUITAR_TECHS_SOURCE_DIR)"
	if [ -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part"; fi
	if [ -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" ] && ! $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" >/dev/null 2>&1; then rm -f "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part"; fi
	if [ ! -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -s "$(GUITAR_TECHS_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(GUITAR_TECHS_SOURCE_DIR)" --out "P2_chords.zip.part" "$(GUITAR_TECHS_P2_CHORDS_URL)"; else curl -fL -C - -o "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P2_CHORDS_URL)"; fi; fi
	if [ -s "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" >/dev/null; mv -f "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE).part" "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" >/dev/null

prepare-guitar-techs-chord-samples: scripts/prepare_guitar_techs_chord_samples.py download-guitar-techs-chord-samples | $(BUILD_DIR)
	GUITAR_TECHS_CHORD_SAMPLE_DIR="$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" GUITAR_TECHS_CHORD_SAMPLE_LIMIT="$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" GUITAR_TECHS_CHORD_MIN_EXCERPTS="$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_guitar_techs_chord_samples.py --archive "$(GUITAR_TECHS_P1_CHORDS_ARCHIVE)" --archive "$(GUITAR_TECHS_P2_CHORDS_ARCHIVE)" --output "$(GUITAR_TECHS_CHORD_SAMPLE_DIR)" --limit "$(GUITAR_TECHS_CHORD_SAMPLE_LIMIT)" --min-samples "$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" --ffmpeg "$(FFMPEG)"

test-guitar-techs-chord-samples: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-techs-chord-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_techs_chord_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_TECHS_CHORD_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_TECHS_CHORD_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_TECHS_CHORD_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_TECHS_CHORD_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_TECHS_CHORD_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_TECHS_CHORD_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_TECHS_CHORD_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_TECHS_CHORD_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_TECHS_CHORD_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_TECHS_CHORD_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_TECHS_CHORD_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

prepare-guitar-chord-mix-samples: scripts/prepare_hf_guitar_chord_mix.py | $(BUILD_DIR)
	GUITAR_CHORD_MIX_SAMPLE_DIR="$(GUITAR_CHORD_MIX_SAMPLE_DIR)" GUITAR_CHORD_MIX_LIMIT="$(GUITAR_CHORD_MIX_LIMIT)" GUITAR_CHORD_MIX_MIN_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(GUITAR_CHORD_MIX_SAMPLE_DIR)" --limit "$(GUITAR_CHORD_MIX_LIMIT)" --min-samples "$(GUITAR_CHORD_MIX_MIN_EXCERPTS)"

test-guitar-chord-mix-samples: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitar_chord_mix_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

analyze-guitar-chord-mix-misses: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GUITAR_CHORD_MIX_MISS_LOG).summary" 2> "$(GUITAR_CHORD_MIX_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GUITAR_CHORD_MIX_MISS_LOG)"

analyze-guitar-chord-mix-attributes: $(BUILD_DIR)/analyzer_guitarset prepare-guitar-chord-mix-samples scripts/summarize_guitarset_attributes.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITAR_CHORD_MIX_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GUITAR_CHORD_MIX_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=4 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=3 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=3 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GUITAR_CHORD_MIX_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GUITAR_CHORD_MIX_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITAR_CHORD_MIX_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GUITAR_CHORD_MIX_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_ATTRIBUTE_TSV="$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(BUILD_DIR)/analyzer_guitarset > "$(BUILD_DIR)/guitar_chord_mix_attributes.out"
	$(PYTHON) scripts/summarize_guitarset_attributes.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv"
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/guitar_chord_mix_attributes.tsv"

inspect-guitar-chord-mix-attribute-buckets: scripts/inspect_guitarset_attribute_buckets.py
	@if [ ! -f "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" ]; then $(MAKE) analyze-guitar-chord-mix-attributes; fi
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(INSPECT_ARGS)

find-guitar-chord-mix-attribute-patterns: scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py
	@if [ ! -f "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" ]; then $(MAKE) analyze-guitar-chord-mix-attributes; fi
	$(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") $(PATTERN_ARGS)

prepare-egfxset-guitar-samples: scripts/prepare_hf_guitar_chord_mix.py | $(BUILD_DIR)
	EGFXSET_GUITAR_SAMPLE_DIR="$(EGFXSET_GUITAR_SAMPLE_DIR)" EGFXSET_GUITAR_SAMPLE_LIMIT="$(EGFXSET_GUITAR_SAMPLE_LIMIT)" EGFXSET_GUITAR_MIN_EXCERPTS="$(EGFXSET_GUITAR_MIN_EXCERPTS)" EGFXSET_GUITAR_DOWNLOAD_JOBS="$(EGFXSET_GUITAR_DOWNLOAD_JOBS)" $(PYTHON) scripts/prepare_hf_guitar_chord_mix.py --output "$(EGFXSET_GUITAR_SAMPLE_DIR)" --sources "egfxset" --limit "$(EGFXSET_GUITAR_SAMPLE_LIMIT)" --min-samples "$(EGFXSET_GUITAR_MIN_EXCERPTS)" --min-notes 1 --min-pitch-classes 1 --jobs "$(EGFXSET_GUITAR_DOWNLOAD_JOBS)"

test-egfxset-guitar-samples: $(BUILD_DIR)/analyzer_guitarset prepare-egfxset-guitar-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_egfxset_guitar_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(EGFXSET_GUITAR_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(EGFXSET_GUITAR_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(EGFXSET_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=1 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=1 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=1 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(EGFXSET_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(EGFXSET_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(EGFXSET_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(EGFXSET_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(EGFXSET_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=0 MUSIC_ANALYZER_GUITARSET_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT="$(EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

prepare-gaps-guitar-samples: scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

test-gaps-guitar-samples: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_gaps_guitar_samples env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

analyze-gaps-guitar-misses: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GAPS_GUITAR_MISS_LOG).summary" 2> "$(GAPS_GUITAR_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GAPS_GUITAR_MISS_LOG)"

prepare-gaps-guitar-samples-full: scripts/prepare_gaps_guitar_samples.py | $(BUILD_DIR)
	GAPS_GUITAR_SOURCE_DIR="$(GAPS_GUITAR_SOURCE_DIR)" GAPS_GUITAR_SAMPLE_DIR="$(GAPS_GUITAR_FULL_SAMPLE_DIR)" GAPS_GUITAR_METADATA_URL="$(GAPS_GUITAR_METADATA_URL)" GAPS_GUITAR_BASE_URL="$(GAPS_GUITAR_BASE_URL)" GAPS_GUITAR_SAMPLE_LIMIT="$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" GAPS_GUITAR_MIN_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" GAPS_GUITAR_MIN_NOTES="$(GAPS_GUITAR_MIN_NOTES)" $(PYTHON) scripts/prepare_gaps_guitar_samples.py --source-dir "$(GAPS_GUITAR_SOURCE_DIR)" --output "$(GAPS_GUITAR_FULL_SAMPLE_DIR)" --metadata-url "$(GAPS_GUITAR_METADATA_URL)" --base-url "$(GAPS_GUITAR_BASE_URL)" --limit "$(GAPS_GUITAR_FULL_SAMPLE_LIMIT)" --min-samples "$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" --min-notes "$(GAPS_GUITAR_MIN_NOTES)"

test-gaps-guitar-samples-full: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples-full scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_gaps_guitar_samples_full env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_FULL_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

analyze-gaps-guitar-misses-full: $(BUILD_DIR)/analyzer_guitarset prepare-gaps-guitar-samples-full scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GAPS_GUITAR_FULL_SAMPLE_DIR)/manifest.tsv" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS="$(GAPS_GUITAR_FULL_MIN_EXCERPTS)" MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=6 MUSIC_ANALYZER_GUITARSET_MIN_ACTIVE_NOTES=2 MUSIC_ANALYZER_GUITARSET_MIN_PITCH_CLASSES=2 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GAPS_GUITAR_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GAPS_GUITAR_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT="$(GAPS_GUITAR_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT="$(GAPS_GUITAR_MAX_FALSE_VOCAL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GAPS_GUITAR_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GAPS_GUITAR_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS="$(GAPS_GUITAR_FULL_MIN_WINDOWS)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GAPS_GUITAR_FULL_MISS_LOG).summary" 2> "$(GAPS_GUITAR_FULL_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GAPS_GUITAR_FULL_MISS_LOG)"

download-guitarset-samples: | $(BUILD_DIR)
	mkdir -p "$(GUITARSET_SOURCE_DIR)"
	test -f "$(GUITARSET_SOURCE_DIR)/annotation.zip" || curl -L -C - -o "$(GUITARSET_SOURCE_DIR)/annotation.zip" "$(GUITARSET_ANNOTATION_URL)"
	test -f "$(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip" || curl -L -C - -o "$(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip" "$(GUITARSET_AUDIO_URL)"

prepare-downloaded-guitarset: download-guitarset-samples
	mkdir -p "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_SOURCE_DIR)/annotation.zip" "$(GUITARSET_ROOT)"
	$(PYTHON) -m zipfile -e "$(GUITARSET_SOURCE_DIR)/audio_mono-mic.zip" "$(GUITARSET_ROOT)"
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py "$(GUITARSET_MANIFEST)"

test-downloaded-guitarset: $(BUILD_DIR)/analyzer_guitarset prepare-downloaded-guitarset scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_guitarset_downloaded env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=200 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1000 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITARSET_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITARSET_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITARSET_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=1000 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITARSET_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_guitarset

analyze-guitarset-misses: $(BUILD_DIR)/analyzer_guitarset prepare-downloaded-guitarset scripts/analyze_guitarset_misses.py
	env MUSIC_ANALYZER_GUITARSET_MANIFEST="$(GUITARSET_MANIFEST)" MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_USE_ALL=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=200 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1000 MUSIC_ANALYZER_GUITARSET_MAX_WINDOWS_PER_EXCERPT=8 MUSIC_ANALYZER_GUITARSET_MIN_WINDOW_RECALL_PERCENT=0 MUSIC_ANALYZER_GUITARSET_MIN_RECALL_PERCENT="$(GUITARSET_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT="$(GUITARSET_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT="$(GUITARSET_MIN_GUITAR_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_CHECKS=1000 MUSIC_ANALYZER_GUITARSET_MIN_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT="$(GUITARSET_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_MAJOR_MINOR_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT="$(GUITARSET_MIN_SIMPLE_OTHER_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_GUITARSET_MAX_FAILURE_LINES=0 MUSIC_ANALYZER_GUITARSET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_guitarset > "$(GUITARSET_MISS_LOG).summary" 2> "$(GUITARSET_MISS_LOG)"
	$(PYTHON) scripts/analyze_guitarset_misses.py "$(GUITARSET_MISS_LOG)"

download-philharmonia-samples: | $(BUILD_DIR)
	mkdir -p "$(PHILHARMONIA_SOURCE_DIR)"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Woodwind.zip" "$(PHILHARMONIA_BASE_URL)/Woodwind.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Brass.zip" "$(PHILHARMONIA_BASE_URL)/Brass.zip"
	test -f "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" || curl -L -C - -o "$(PHILHARMONIA_SOURCE_DIR)/Strings.zip" "$(PHILHARMONIA_BASE_URL)/Strings.zip"

prepare-philharmonia-samples: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	PHILHARMONIA_SOURCE_DIR="$(PHILHARMONIA_SOURCE_DIR)" PHILHARMONIA_SAMPLE_DIR="$(PHILHARMONIA_SAMPLE_DIR)" PHILHARMONIA_SAMPLE_LIMIT="$(PHILHARMONIA_SAMPLE_LIMIT)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_philharmonia_samples.py --source "$(PHILHARMONIA_SOURCE_DIR)" --output "$(PHILHARMONIA_SAMPLE_DIR)" --limit "$(PHILHARMONIA_SAMPLE_LIMIT)" --min-samples 1000 --ffmpeg "$(FFMPEG)"

test-philharmonia-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-philharmonia-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_philharmonia_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1000 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PHILHARMONIA_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(PHILHARMONIA_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(PHILHARMONIA_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(PHILHARMONIA_MIN_OTHER)" $(BUILD_DIR)/analyzer_real_note_samples

prepare-philharmonia-samples-full: scripts/prepare_philharmonia_samples.py download-philharmonia-samples | $(BUILD_DIR)
	PHILHARMONIA_SOURCE_DIR="$(PHILHARMONIA_SOURCE_DIR)" PHILHARMONIA_SAMPLE_DIR="$(PHILHARMONIA_FULL_SAMPLE_DIR)" PHILHARMONIA_SAMPLE_LIMIT="$(PHILHARMONIA_FULL_SAMPLE_LIMIT)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_philharmonia_samples.py --source "$(PHILHARMONIA_SOURCE_DIR)" --output "$(PHILHARMONIA_FULL_SAMPLE_DIR)" --limit "$(PHILHARMONIA_FULL_SAMPLE_LIMIT)" --min-samples "$(PHILHARMONIA_FULL_MIN_SAMPLES)" --progress-every "$(PHILHARMONIA_FULL_PROGRESS_EVERY)" --ffmpeg "$(FFMPEG)"

test-philharmonia-samples-full: $(BUILD_DIR)/analyzer_real_note_samples prepare-philharmonia-samples-full scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_philharmonia_samples_full env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(PHILHARMONIA_FULL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(PHILHARMONIA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(PHILHARMONIA_FULL_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(PHILHARMONIA_FULL_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(PHILHARMONIA_FULL_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(PHILHARMONIA_FULL_MAX_FAILURES)" $(BUILD_DIR)/analyzer_real_note_samples

download-good-sounds-samples: $(GOOD_SOUNDS_ARCHIVE)

$(GOOD_SOUNDS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(GOOD_SOUNDS_SOURCE_DIR)"
	if [ -s "$(GOOD_SOUNDS_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(GOOD_SOUNDS_ARCHIVE)" "$(GOOD_SOUNDS_ARCHIVE).part"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ] && [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi
	if [ ! -s "$(GOOD_SOUNDS_ARCHIVE)" ]; then curl -fL -C - -o "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_URL)"; fi
	if [ -s "$(GOOD_SOUNDS_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE).part" >/dev/null; mv "$(GOOD_SOUNDS_ARCHIVE).part" "$(GOOD_SOUNDS_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(GOOD_SOUNDS_ARCHIVE)" >/dev/null

prepare-good-sounds-samples: scripts/prepare_good_sounds_samples.py download-good-sounds-samples | $(BUILD_DIR)
	GOOD_SOUNDS_ARCHIVE="$(GOOD_SOUNDS_ARCHIVE)" GOOD_SOUNDS_SAMPLE_DIR="$(GOOD_SOUNDS_SAMPLE_DIR)" GOOD_SOUNDS_SAMPLE_LIMIT="$(GOOD_SOUNDS_SAMPLE_LIMIT)" GOOD_SOUNDS_MIN_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_good_sounds_samples.py --archive "$(GOOD_SOUNDS_ARCHIVE)" --output "$(GOOD_SOUNDS_SAMPLE_DIR)" --limit "$(GOOD_SOUNDS_SAMPLE_LIMIT)" --min-samples "$(GOOD_SOUNDS_MIN_SAMPLES)" --ffmpeg "$(FFMPEG)"

test-good-sounds-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-good-sounds-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_good_sounds_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(GOOD_SOUNDS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(GOOD_SOUNDS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(GOOD_SOUNDS_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(GOOD_SOUNDS_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(GOOD_SOUNDS_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

prepare-iowa-piano-samples: scripts/prepare_iowa_piano_samples.py | $(BUILD_DIR)
	IOWA_PIANO_PAGE_URL="$(IOWA_PIANO_PAGE_URL)" IOWA_PIANO_FILE_BASE_URL="$(IOWA_PIANO_FILE_BASE_URL)" IOWA_PIANO_SOURCE_DIR="$(IOWA_PIANO_SOURCE_DIR)" IOWA_PIANO_SAMPLE_DIR="$(IOWA_PIANO_SAMPLE_DIR)" IOWA_PIANO_SAMPLE_LIMIT="$(IOWA_PIANO_SAMPLE_LIMIT)" IOWA_PIANO_MIN_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" IOWA_PIANO_DOWNLOAD_RETRIES="$(IOWA_PIANO_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_piano_samples.py --page-url "$(IOWA_PIANO_PAGE_URL)" --file-base-url "$(IOWA_PIANO_FILE_BASE_URL)" --source-dir "$(IOWA_PIANO_SOURCE_DIR)" --output "$(IOWA_PIANO_SAMPLE_DIR)" --limit "$(IOWA_PIANO_SAMPLE_LIMIT)" --min-samples "$(IOWA_PIANO_MIN_PIANO)" --download-retries "$(IOWA_PIANO_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-piano-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-piano-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_iowa_piano_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_PIANO_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(IOWA_PIANO_MIN_PIANO)" $(BUILD_DIR)/analyzer_real_note_samples

prepare-iowa-bass-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_BASS_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_BASS_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_BASS_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_BASS_MIN_BASS)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py --spec "bass|bass|iowa-double-bass-pizz-sulE|$(IOWA_BASS_ZIP_URL)" --source-dir "$(IOWA_BASS_SOURCE_DIR)" --output "$(IOWA_BASS_SAMPLE_DIR)" --limit "$(IOWA_BASS_SAMPLE_LIMIT)" --min-samples "$(IOWA_BASS_MIN_BASS)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-bass-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-bass-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_iowa_bass_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_BASS_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_BASS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(IOWA_BASS_MIN_BASS)" $(BUILD_DIR)/analyzer_real_note_samples

prepare-iowa-strings-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_STRINGS_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_STRINGS_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_STRINGS_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_STRINGS_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py --spec "other|strings|iowa-violin-arco-2012|$(IOWA_STRINGS_VIOLIN_ARCO_SULG_URL)" --source-dir "$(IOWA_STRINGS_SOURCE_DIR)" --output "$(IOWA_STRINGS_SAMPLE_DIR)" --limit "$(IOWA_STRINGS_SAMPLE_LIMIT)" --min-samples "$(IOWA_STRINGS_MIN_SAMPLES)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-strings-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-strings-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_iowa_strings_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_STRINGS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_STRINGS_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(IOWA_STRINGS_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(IOWA_STRINGS_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(IOWA_STRINGS_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

prepare-iowa-orchestra-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_ORCHESTRA_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_ORCHESTRA_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_ORCHESTRA_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_ORCHESTRA_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ZIP_DOWNLOAD_RETRIES)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py $(IOWA_ORCHESTRA_SPEC_ARGS) --source-dir "$(IOWA_ORCHESTRA_SOURCE_DIR)" --output "$(IOWA_ORCHESTRA_SAMPLE_DIR)" --limit "$(IOWA_ORCHESTRA_SAMPLE_LIMIT)" --min-samples "$(IOWA_ORCHESTRA_MIN_SAMPLES)" --download-retries "$(IOWA_ZIP_DOWNLOAD_RETRIES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-orchestra-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-orchestra-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_iowa_orchestra_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_ORCHESTRA_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_ORCHESTRA_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(IOWA_ORCHESTRA_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(IOWA_ORCHESTRA_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(IOWA_ORCHESTRA_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

prepare-iowa-orchestra-full-samples: scripts/prepare_iowa_zip_samples.py | $(BUILD_DIR)
	IOWA_ZIP_SOURCE_DIR="$(IOWA_ORCHESTRA_FULL_SOURCE_DIR)" IOWA_ZIP_SAMPLE_DIR="$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" IOWA_ZIP_SAMPLE_LIMIT="$(IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT)" IOWA_ZIP_MIN_SAMPLES="$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" IOWA_ZIP_DOWNLOAD_TIMEOUT="$(IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT)" IOWA_ZIP_DOWNLOAD_RETRIES="$(IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES)" IOWA_ZIP_MAX_DOWNLOAD_FAILURES="$(IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES)" IOWA_ZIP_MAX_ZIPS_PER_PAGE="$(IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE)" FFMPEG="$(FFMPEG)" CURL="$(CURL)" $(PYTHON) scripts/prepare_iowa_zip_samples.py $(IOWA_ORCHESTRA_FULL_SPEC_ARGS) $(IOWA_ORCHESTRA_FULL_PAGE_ARGS) --source-dir "$(IOWA_ORCHESTRA_FULL_SOURCE_DIR)" --output "$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" --limit "$(IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT)" --min-samples "$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" --max-zips-per-page "$(IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE)" --download-timeout "$(IOWA_ORCHESTRA_FULL_DOWNLOAD_TIMEOUT)" --download-retries "$(IOWA_ORCHESTRA_FULL_DOWNLOAD_RETRIES)" --max-download-failures "$(IOWA_ORCHESTRA_FULL_MAX_DOWNLOAD_FAILURES)" --ffmpeg "$(FFMPEG)" --curl "$(CURL)"

test-iowa-orchestra-full-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-iowa-orchestra-full-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_iowa_orchestra_full_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IOWA_ORCHESTRA_FULL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IOWA_ORCHESTRA_FULL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(IOWA_ORCHESTRA_FULL_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(IOWA_ORCHESTRA_FULL_MIN_OTHER)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(IOWA_ORCHESTRA_FULL_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples

download-idmt-bass-lines-samples: $(IDMT_BASS_LINES_ARCHIVE)

$(IDMT_BASS_LINES_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(IDMT_BASS_LINES_SOURCE_DIR)"
	if [ ! -s "$(IDMT_BASS_LINES_ARCHIVE)" ] || ! $(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null 2>&1; then curl -fL -C - -o "$(IDMT_BASS_LINES_ARCHIVE)" "$(IDMT_BASS_LINES_URL)"; fi
	$(PYTHON) -m zipfile -t "$(IDMT_BASS_LINES_ARCHIVE)" >/dev/null

prepare-idmt-bass-lines-samples: scripts/prepare_idmt_bass_lines_samples.py download-idmt-bass-lines-samples | $(BUILD_DIR)
	IDMT_BASS_LINES_ARCHIVE="$(IDMT_BASS_LINES_ARCHIVE)" IDMT_BASS_LINES_SAMPLE_DIR="$(IDMT_BASS_LINES_SAMPLE_DIR)" IDMT_BASS_LINES_SAMPLE_LIMIT="$(IDMT_BASS_LINES_SAMPLE_LIMIT)" IDMT_BASS_LINES_MIN_BASS="$(IDMT_BASS_LINES_MIN_BASS)" IDMT_BASS_LINES_EXPRESSIONS="$(IDMT_BASS_LINES_EXPRESSIONS)" IDMT_BASS_LINES_MIN_NOTE_DURATION="$(IDMT_BASS_LINES_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_idmt_bass_lines_samples.py --archive "$(IDMT_BASS_LINES_ARCHIVE)" --output "$(IDMT_BASS_LINES_SAMPLE_DIR)" --limit "$(IDMT_BASS_LINES_SAMPLE_LIMIT)" --min-samples "$(IDMT_BASS_LINES_MIN_BASS)" --expressions "$(IDMT_BASS_LINES_EXPRESSIONS)" --min-note-duration "$(IDMT_BASS_LINES_MIN_NOTE_DURATION)"

test-idmt-bass-lines-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-idmt-bass-lines-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_bass_lines_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IDMT_BASS_LINES_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IDMT_BASS_LINES_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(IDMT_BASS_LINES_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(IDMT_BASS_LINES_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

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

test-idmt-guitar-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-idmt-guitar-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_idmt_guitar_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IDMT_GUITAR_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IDMT_GUITAR_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(IDMT_GUITAR_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(IDMT_GUITAR_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

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

test-tinysol-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-tinysol-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_tinysol_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(TINYSOL_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(TINYSOL_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(TINYSOL_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(TINYSOL_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(TINYSOL_MIN_OTHER)" $(BUILD_DIR)/analyzer_real_note_samples

download-vocadito-samples: $(VOCADITO_ARCHIVE)

$(VOCADITO_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(VOCADITO_SOURCE_DIR)"
	if [ ! -s "$(VOCADITO_ARCHIVE)" ] || ! $(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE)" >/dev/null 2>&1; then curl -fL -C - -o "$(VOCADITO_ARCHIVE)" "$(VOCADITO_URL)"; fi
	$(PYTHON) -m zipfile -t "$(VOCADITO_ARCHIVE)" >/dev/null

prepare-vocadito-samples: scripts/prepare_vocadito_samples.py download-vocadito-samples | $(BUILD_DIR)
	VOCADITO_ARCHIVE="$(VOCADITO_ARCHIVE)" VOCADITO_SAMPLE_DIR="$(VOCADITO_SAMPLE_DIR)" VOCADITO_SAMPLE_LIMIT="$(VOCADITO_SAMPLE_LIMIT)" VOCADITO_MIN_VOCALS="$(VOCADITO_MIN_VOCALS)" VOCADITO_ANNOTATOR="$(VOCADITO_ANNOTATOR)" VOCADITO_MAX_CENTS="$(VOCADITO_MAX_CENTS)" VOCADITO_MIN_NOTE_DURATION="$(VOCADITO_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_vocadito_samples.py --archive "$(VOCADITO_ARCHIVE)" --output "$(VOCADITO_SAMPLE_DIR)" --limit "$(VOCADITO_SAMPLE_LIMIT)" --min-samples "$(VOCADITO_MIN_VOCALS)" --annotator "$(VOCADITO_ANNOTATOR)" --max-cents "$(VOCADITO_MAX_CENTS)" --min-note-duration "$(VOCADITO_MIN_NOTE_DURATION)"

test-vocadito-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocadito-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_vocadito_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCADITO_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCADITO_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(VOCADITO_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(VOCADITO_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=80 $(BUILD_DIR)/analyzer_real_note_samples

download-vocalset-samples: $(VOCALSET_ARCHIVE)

$(VOCALSET_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(VOCALSET_SOURCE_DIR)"
	if [ -s "$(VOCALSET_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(VOCALSET_ARCHIVE)" "$(VOCALSET_ARCHIVE).part"; fi
	if [ ! -s "$(VOCALSET_ARCHIVE)" ] && [ -s "$(VOCALSET_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE).part" >/dev/null 2>&1; then mv "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_ARCHIVE)"; fi
	if [ ! -s "$(VOCALSET_ARCHIVE)" ]; then curl -fL -C - -o "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_URL)"; fi
	if [ -s "$(VOCALSET_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE).part" >/dev/null; mv "$(VOCALSET_ARCHIVE).part" "$(VOCALSET_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(VOCALSET_ARCHIVE)" >/dev/null

prepare-vocalset-samples: scripts/prepare_vocalset_samples.py download-vocalset-samples | $(BUILD_DIR)
	VOCALSET_ARCHIVE="$(VOCALSET_ARCHIVE)" VOCALSET_SAMPLE_DIR="$(VOCALSET_SAMPLE_DIR)" VOCALSET_SAMPLE_LIMIT="$(VOCALSET_SAMPLE_LIMIT)" VOCALSET_MIN_VOCALS="$(VOCALSET_MIN_VOCALS)" VOCALSET_ALLOWED_TECHNIQUES="$(VOCALSET_ALLOWED_TECHNIQUES)" VOCALSET_MAX_CENTS="$(VOCALSET_MAX_CENTS)" VOCALSET_MIN_NOTE_DURATION="$(VOCALSET_MIN_NOTE_DURATION)" $(PYTHON) scripts/prepare_vocalset_samples.py --archive "$(VOCALSET_ARCHIVE)" --output "$(VOCALSET_SAMPLE_DIR)" --limit "$(VOCALSET_SAMPLE_LIMIT)" --min-samples "$(VOCALSET_MIN_VOCALS)" --allowed-techniques "$(VOCALSET_ALLOWED_TECHNIQUES)" --max-cents "$(VOCALSET_MAX_CENTS)" --min-note-duration "$(VOCALSET_MIN_NOTE_DURATION)"

test-vocalset-samples: $(BUILD_DIR)/analyzer_real_note_samples prepare-vocalset-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_vocalset_samples env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(VOCALSET_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(VOCALSET_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(VOCALSET_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples

test-drum-real-world-samples: test-hf-drum-kit-samples test-idmt-drums-samples test-mdb-drums-samples test-star-drums-samples
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-samples; $(MAKE) test-drum-samples-spread; else printf '%s\n' "test-drum-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi

test-drum-real-world-samples-full: test-drum-real-world-samples
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-machine-samples; $(MAKE) test-drum-samples-full; else printf '%s\n' "test-drum-samples-full: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi

test-real-world-samples: test-real-note-samples test-real-note-samples-full-mix test-guitar-fretboard-note-samples test-hf-drum-kit-samples test-idmt-drums-samples test-mdb-drums-samples test-star-drums-samples test-downloaded-guitarset test-philharmonia-samples test-iowa-piano-samples test-iowa-bass-samples test-idmt-bass-lines-samples test-vocadito-samples

test-configured-real-world-samples: tests/run_real_goal_gate.py
	$(PYTHON) tests/run_real_goal_gate.py optional-20 "$(MAKE)"

test-real-world-samples-full: test-real-world-samples test-guitar-techs-samples test-guitar-techs-chord-samples test-guitar-chord-mix-samples test-egfxset-guitar-samples test-gaps-guitar-samples test-idmt-guitar-samples test-iowa-strings-samples test-iowa-orchestra-samples test-iowa-orchestra-full-samples test-philharmonia-samples-full test-tinysol-samples
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-machine-samples; else printf '%s\n' "test-drum-machine-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-samples-full; else printf '%s\n' "test-drum-samples-full: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi
	if [ -s "$(GOOD_SOUNDS_ARCHIVE)" ]; then $(MAKE) test-good-sounds-samples; else printf '%s\n' "test-good-sounds-samples: skipped; missing $(GOOD_SOUNDS_ARCHIVE)"; fi
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE)" ]; then $(MAKE) test-medley-solos-samples; else printf '%s\n' "test-medley-solos-samples: skipped; missing $(MEDLEY_SOLOS_ARCHIVE)"; fi
	if [ -s "$(MAPS_PIANO_ARCHIVE)" ]; then $(MAKE) test-maps-piano-samples; else printf '%s\n' "test-maps-piano-samples: skipped; missing $(MAPS_PIANO_ARCHIVE)"; fi
	if [ -s "$(MAPS_PIANO_ARCHIVE)" ]; then $(MAKE) test-maps-piano-note-samples; else printf '%s\n' "test-maps-piano-note-samples: skipped; missing $(MAPS_PIANO_ARCHIVE)"; fi
	if [ -n "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" ] || [ -s "$(BACH10_MF0_SYNTH_ARCHIVE)" ]; then $(MAKE) test-bach10-mf0-synth-samples; else printf '%s\n' "test-bach10-mf0-synth-samples: skipped; missing $(BACH10_MF0_SYNTH_ARCHIVE)"; fi
	if [ -s "$(VOCALSET_ARCHIVE)" ]; then $(MAKE) test-vocalset-samples; else printf '%s\n' "test-vocalset-samples: skipped; missing $(VOCALSET_ARCHIVE)"; fi
	$(MAKE) test-configured-real-world-samples

test-real-world-samples-max:
	$(MAKE) test-real-world-samples
	$(MAKE) test-guitar-techs-samples
	$(MAKE) test-guitar-techs-chord-samples
	$(MAKE) test-guitar-chord-mix-samples
	$(MAKE) test-egfxset-guitar-samples
	$(MAKE) test-gaps-guitar-samples-full
	$(MAKE) test-idmt-guitar-samples
	$(MAKE) IOWA_PIANO_SAMPLE_LIMIT=0 test-iowa-piano-samples
	$(MAKE) test-iowa-strings-samples
	$(MAKE) test-iowa-orchestra-samples
	$(MAKE) IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT=0 IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE=0 test-iowa-orchestra-full-samples
	$(MAKE) test-philharmonia-samples-full
	$(MAKE) test-tinysol-samples
	$(MAKE) GOOD_SOUNDS_SAMPLE_LIMIT=0 test-good-sounds-samples
	$(MAKE) MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=0 test-medley-solos-samples
	$(MAKE) MAPS_PIANO_RECORDING_LIMIT=0 test-maps-piano-samples
	$(MAKE) MAPS_PIANO_NOTE_RECORDING_LIMIT=0 test-maps-piano-note-samples
	$(MAKE) test-bach10-mf0-synth-samples
	$(MAKE) test-vocalset-samples
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-machine-samples; else printf '%s\n' "test-drum-machine-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-samples-full; else printf '%s\n' "test-drum-samples-full: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi
	$(MAKE) test-configured-real-world-samples

test-midi-ranges: $(BUILD_DIR)/analyzer_midi_ranges scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_midi_ranges $(BUILD_DIR)/analyzer_midi_ranges

test: $(TEST_BINS) scripts/run_with_duration.sh
	$(MAKE) test-standalone
	$(MAKE) inspect-real-dataset-catalog
	$(MAKE) inspect-real-goal-coverage
	$(MAKE) test-musicnet-remote
	$(MAKE) test-medleydb-inspector
	$(MAKE) test-medleydb-prepare
	$(MAKE) test-musdb-inspector
	$(MAKE) test-slakh-inspector
	$(MAKE) test-slakh-prepare
	$(MAKE) test-choralsynth-inspector
	$(MAKE) test-choralsynth-prepare
	$(MAKE) test-cocochorales-inspector
	$(MAKE) test-cocochorales-prepare
	$(MAKE) test-synthsod-remote
	$(MAKE) test-synthsod-archive-extract
	$(MAKE) test-synthsod-inspector
	$(MAKE) test-synthsod-prepare
	$(MAKE) test-polyvocal-inspector
	$(MAKE) test-polyvocal-prepare
	$(MAKE) test-prepared-multitrack-inspector
	$(MAKE) test-prepared-multitrack-prepare
	$(MAKE) test-multtipop-inspector
	$(MAKE) test-spheres-inspector
	$(MAKE) test-guitarset-inspector
	$(MAKE) test-urmp-inspector
	$(MAKE) test-drum-sample-prepare
	$(MAKE) test-hf-drum-kit-prepare
	$(MAKE) test-idmt-drums-prepare
	$(MAKE) test-mdb-drums-prepare
	$(MAKE) test-star-drums-prepare
	$(MAKE) test-medley-solos-prepare
	$(MAKE) test-maps-piano-prepare
	$(MAKE) test-bach10-mf0-synth-prepare
	$(MAKE) test-instrument-sample-attribute-summary
	$(MAKE) test-instrument-sample-owner-buckets
	$(MAKE) test-instrument-owner-patterns
	$(MAKE) test-analyzer-pattern-report
	$(MAKE) test-measure-analyzer-patterns-target
	$(MAKE) test-philharmonia-prepare
	$(MAKE) test-good-sounds-prepare
	$(MAKE) test-iowa-piano-prepare
	$(MAKE) test-iowa-zip-prepare
	$(MAKE) test-idmt-bass-lines-prepare
	$(MAKE) test-idmt-guitar-prepare
	$(MAKE) test-tinysol-prepare
	$(MAKE) test-vocadito-prepare
	$(MAKE) test-vocalset-prepare
	$(MAKE) test-guitar-fretboard-note-prepare
	$(MAKE) test-guitar-techs-prepare
	$(MAKE) test-guitar-techs-chord-prepare
	$(MAKE) test-guitar-chord-mix-prepare
	$(MAKE) test-gaps-guitar-prepare
	$(MAKE) test-guitarset-miss-analysis
	$(MAKE) test-guitarset-attribute-summary
	$(MAKE) test-guitarset-attribute-buckets
	$(MAKE) test-guitarset-attribute-patterns
	$(MAKE) test-real-note-miss-analysis
	$(MAKE) test-real-note-attribute-summary
	$(MAKE) test-real-note-attribute-buckets
	$(MAKE) test-real-note-attribute-patterns
	$(MAKE) test-egmd-miss-analysis
	$(MAKE) test-egmd-drum-attribute-summary
	$(MAKE) test-drum-primary-analysis
	$(MAKE) test-real-goal-script
	$(RUN_WITH_DURATION) analyzer_smoke $(BUILD_DIR)/analyzer_smoke
	$(RUN_WITH_DURATION) analyzer_cases $(BUILD_DIR)/analyzer_cases
	$(RUN_WITH_DURATION) analyzer_midi_ranges $(BUILD_DIR)/analyzer_midi_ranges
	$(RUN_WITH_DURATION) analyzer_urmp $(BUILD_DIR)/analyzer_urmp
	$(RUN_WITH_DURATION) analyzer_musicnet $(BUILD_DIR)/analyzer_musicnet
	$(RUN_WITH_DURATION) analyzer_multtipop $(BUILD_DIR)/analyzer_multtipop
	$(RUN_WITH_DURATION) analyzer_guitarset $(BUILD_DIR)/analyzer_guitarset
	$(RUN_WITH_DURATION) analyzer_maestro $(BUILD_DIR)/analyzer_maestro
	$(RUN_WITH_DURATION) analyzer_egmd $(BUILD_DIR)/analyzer_egmd
	if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) test-drum-samples; $(MAKE) test-drum-samples-spread; else printf '%s\n' "test-drum-samples: skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi
	if command -v fluidsynth >/dev/null 2>&1; then $(MAKE) test-instrument-samples; else printf '%s\n' "test-instrument-samples: skipped; missing fluidsynth"; fi
	$(MAKE) test-direct-fit-small-fixture
	$(MAKE) test-synthsod-fixture
	$(MAKE) test-prepared-multitrack-fixture
	$(MAKE) test-multtipop-audio-root-fixture
	$(MAKE) test-real-goal-fixture

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

test-real-note-miss-analysis: tests/test_analyze_real_note_misses.py scripts/analyze_real_note_misses.py
	$(PYTHON) tests/test_analyze_real_note_misses.py

test-real-note-attribute-summary: tests/test_summarize_real_note_attributes.py scripts/summarize_real_note_attributes.py
	$(PYTHON) tests/test_summarize_real_note_attributes.py

test-real-note-attribute-buckets: tests/test_inspect_real_note_attribute_buckets.py scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) tests/test_inspect_real_note_attribute_buckets.py

test-real-note-attribute-patterns: tests/test_find_real_note_attribute_patterns.py scripts/find_real_note_attribute_patterns.py
	$(PYTHON) tests/test_find_real_note_attribute_patterns.py

test-instrument-sample-attribute-summary: tests/test_summarize_instrument_sample_attributes.py scripts/summarize_instrument_sample_attributes.py
	$(PYTHON) tests/test_summarize_instrument_sample_attributes.py

test-instrument-sample-owner-buckets: tests/test_inspect_instrument_sample_owner_buckets.py scripts/inspect_instrument_sample_owner_buckets.py
	$(PYTHON) tests/test_inspect_instrument_sample_owner_buckets.py

test-instrument-owner-patterns: tests/test_find_instrument_owner_patterns.py scripts/find_instrument_owner_patterns.py
	$(PYTHON) tests/test_find_instrument_owner_patterns.py

test-analyzer-pattern-report: tests/test_report_analyzer_attribute_patterns.py scripts/report_analyzer_attribute_patterns.py
	$(PYTHON) tests/test_report_analyzer_attribute_patterns.py

test-measure-analyzer-patterns-target: tests/test_measure_analyzer_patterns_makefile.py Makefile
	$(PYTHON) tests/test_measure_analyzer_patterns_makefile.py

test-egmd-miss-analysis: tests/test_analyze_egmd_misses.py scripts/analyze_egmd_misses.py
	$(PYTHON) tests/test_analyze_egmd_misses.py

test-egmd-drum-attribute-summary: tests/test_summarize_egmd_drum_attributes.py scripts/summarize_egmd_drum_attributes.py
	$(PYTHON) tests/test_summarize_egmd_drum_attributes.py

test-drum-primary-analysis: tests/test_analyze_drum_primary_debug.py tests/test_evaluate_drum_rule_grid.py tests/test_evaluate_drum_tom_bleed_caps.py tests/test_find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py scripts/evaluate_drum_rule_grid.py scripts/evaluate_drum_tom_bleed_caps.py scripts/find_drum_attribute_patterns.py
	$(PYTHON) tests/test_analyze_drum_primary_debug.py
	$(PYTHON) tests/test_evaluate_drum_rule_grid.py
	$(PYTHON) tests/test_evaluate_drum_tom_bleed_caps.py
	$(PYTHON) tests/test_find_drum_attribute_patterns.py

test-real-goal-script: tests/test_run_real_goal_gate.py tests/run_real_goal_gate.py
	$(PYTHON) tests/test_run_real_goal_gate.py

test-real-goal-fixture: $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd $(URMP_FIXTURE_ARCHIVE) tests/generate_musicnet_fixture.py tests/generate_medleydb_fixture.py tests/generate_musdb_fixture.py tests/generate_slakh_fixture.py tests/generate_choralsynth_fixture.py tests/generate_cocochorales_fixture.py tests/generate_synthsod_fixture.py tests/generate_polyvocal_fixture.py tests/generate_prepared_multitrack_fixture.py tests/generate_multtipop_fixture.py tests/generate_spheres_fixture.py tests/generate_guitarset_fixture.py tests/prepare_guitarset_manifest.py tests/generate_maestro_fixture.py tests/generate_egmd_fixture.py tests/run_real_goal_gate.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_FIXTURE_DIR)
	mkdir -p $(REAL_GOAL_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(REAL_GOAL_FIXTURE_DIR)
	$(MAKE) decode-urmp-fixture URMP_FIXTURE_DIR=$(REAL_GOAL_URMP_FIXTURE_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(REAL_GOAL_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	$(PYTHON) tests/generate_musdb_fixture.py $(REAL_GOAL_MUSDB_FIXTURE_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio
	$(PYTHON) tests/generate_spheres_fixture.py $(REAL_GOAL_SPHERES_FIXTURE_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)
	MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)"
	MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)"

test-musicnet-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/generate_musicnet_fixture.py $(MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-medleydb-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_medleydb_fixture.py tests/prepare_medleydb_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	$(PYTHON) tests/generate_medleydb_fixture.py $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)
	MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) $(MAKE) test-real-medleydb-20

test-slakh-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_slakh_fixture.py tests/prepare_slakh_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	$(PYTHON) tests/generate_slakh_fixture.py $(REAL_GOAL_SLAKH_FIXTURE_DIR)
	MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) $(MAKE) test-real-slakh-20

test-choralsynth-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_choralsynth_fixture.py tests/prepare_choralsynth_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	$(PYTHON) tests/generate_choralsynth_fixture.py $(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR)
	MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) $(MAKE) test-real-choralsynth-20

test-cocochorales-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_cocochorales_fixture.py tests/prepare_cocochorales_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	$(PYTHON) tests/generate_cocochorales_fixture.py $(REAL_GOAL_COCOCHORALES_FIXTURE_DIR)
	MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) $(MAKE) test-real-cocochorales-20

test-synthsod-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_synthsod_fixture.py tests/prepare_synthsod_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	$(PYTHON) tests/generate_synthsod_fixture.py $(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)
	MUSIC_ANALYZER_SYNTHSOD_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=$(REAL_GOAL_SYNTHSOD_FIXTURE_DIR)/SynthSOD-aligned-scores $(MAKE) test-real-synthsod-20

test-polyvocal-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_polyvocal_fixture.py tests/prepare_polyvocal_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 $(MAKE) test-real-polyvocal-20

test-prepared-multitrack-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_prepared_multitrack_fixture.py tests/prepare_prepared_multitrack_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	$(PYTHON) tests/generate_prepared_multitrack_fixture.py $(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=$(REAL_GOAL_PREPARED_MULTITRACK_FIXTURE_DIR) $(MAKE) test-real-prepared-multitrack-20

test-multtipop-audio-root-fixture: $(BUILD_DIR)/analyzer_multtipop tests/generate_multtipop_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio $(REAL_GOAL_MULTTIPOP_AUDIO_DIR)
	MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT=$(REAL_GOAL_MULTTIPOP_AUDIO_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 $(BUILD_DIR)/analyzer_multtipop

test-guitarset-fixture: $(BUILD_DIR)/analyzer_guitarset tests/generate_guitarset_fixture.py tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 $(BUILD_DIR)/analyzer_guitarset

test-maestro-fixture: $(BUILD_DIR)/analyzer_maestro tests/generate_maestro_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-egmd-fixture: $(BUILD_DIR)/analyzer_egmd tests/generate_egmd_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_EGMD_FIXTURE_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)
	MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_REQUIRED=1 $(BUILD_DIR)/analyzer_egmd

test-bach10-fixture: $(BUILD_DIR)/analyzer_urmp tests/generate_bach10_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_bach10_fixture.py $(BACH10_FIXTURE_DIR)
	MUSIC_ANALYZER_URMP_ROOT=$(BACH10_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=10 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=40 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=4 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-direct-fit-small-fixture: $(BUILD_DIR)/analyzer_urmp $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(DIRECT_FIT_SMALL_FIXTURE_DIR)
	$(TAR) -xzf $(DIRECT_FIT_SMALL_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	$(MAKE) decode-direct-fit-small-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(DIRECT_FIT_SMALL_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=20 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=80 MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW=3 MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW=3 $(BUILD_DIR)/analyzer_urmp

test-urmp-fixture: $(BUILD_DIR)/analyzer_urmp $(URMP_FIXTURE_ARCHIVE) | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	$(MAKE) decode-urmp-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_URMP_REQUIRED=1 $(BUILD_DIR)/analyzer_urmp

test-real-urmp-full: $(BUILD_DIR)/analyzer_urmp
	MUSIC_ANALYZER_URMP_REQUIRED=1 MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(BUILD_DIR)/analyzer_urmp

test-real-multitrack-20: test-real-urmp

test-real-multitrack-full: test-real-urmp-full

test-real-goal-20: tests/run_real_goal_gate.py
	$(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)"

test-real-goal-full: tests/run_real_goal_gate.py
	$(PYTHON) tests/run_real_goal_gate.py full "$(MAKE)"

inspect-real-goal-20: tests/run_real_goal_gate.py
	$(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)"

inspect-real-goal-full: tests/run_real_goal_gate.py
	$(PYTHON) tests/run_real_goal_gate.py inspect-full "$(MAKE)"

test-real-musicnet-20: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet
	MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=330 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1320 $(BUILD_DIR)/analyzer_musicnet

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

inspect-real-urmp: tests/inspect_urmp_dataset.py
	$(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-urmp-full: tests/inspect_urmp_dataset.py
	MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-multitrack-20: inspect-real-urmp

inspect-real-multitrack-full: inspect-real-urmp-full

inspect-urmp-fixture: $(URMP_FIXTURE_ARCHIVE) tests/inspect_urmp_dataset.py | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	$(MAKE) decode-urmp-fixture
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
