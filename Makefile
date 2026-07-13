CXX ?= g++
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
TAR ?= tar
FFMPEG ?= ffmpeg
BUILD_DIR ?= build
DEPS_DIR ?= $(BUILD_DIR)/deps
OBS_USER_PLUGIN_DIR ?= $(HOME)/.config/obs-studio/plugins/music-analyzer-obs/bin/64bit
URMP_FIXTURE_ARCHIVE := tests/fixtures/urmp-mini.tar.gz
DIRECT_FIT_SMALL_FIXTURE_ARCHIVE := tests/fixtures/direct-fit-small.tar.gz
URMP_FIXTURE_DIR := $(BUILD_DIR)/urmp-fixture
BACH10_FIXTURE_DIR := $(BUILD_DIR)/bach10-fixture
DIRECT_FIT_SMALL_FIXTURE_DIR := $(BUILD_DIR)/direct-fit-small-fixture
MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/musicnet-fixture
MEDLEYDB_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/medleydb-musicnet-fixture
SLAKH_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/slakh-musicnet-fixture
CHORALSYNTH_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/choralsynth-musicnet-fixture
COCOCHORALES_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/cocochorales-musicnet-fixture
POLYVOCAL_MUSICNET_FIXTURE_DIR := $(BUILD_DIR)/polyvocal-musicnet-fixture
REAL_GOAL_FIXTURE_DIR := $(BUILD_DIR)/real-goal-fixture
REAL_GOAL_URMP_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/urmp-fixture
REAL_GOAL_MUSICNET_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/musicnet-fixture
REAL_GOAL_MEDLEYDB_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/medleydb-fixture
REAL_GOAL_MUSDB_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/musdb-fixture
REAL_GOAL_SLAKH_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/slakh-fixture
REAL_GOAL_CHORALSYNTH_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/choralsynth-fixture
REAL_GOAL_COCOCHORALES_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/cocochorales-fixture
REAL_GOAL_POLYVOCAL_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/polyvocal-fixture
REAL_GOAL_SPHERES_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/spheres-fixture
REAL_GOAL_MULTTIPOP_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/multtipop-fixture
REAL_GOAL_MULTTIPOP_AUDIO_DIR := $(REAL_GOAL_FIXTURE_DIR)/multtipop-audio
REAL_GOAL_GUITARSET_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/guitarset-fixture
GUITARSET_MANIFEST := $(BUILD_DIR)/guitarset-manifest.tsv
REAL_GOAL_MAESTRO_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/maestro-fixture
REAL_GOAL_EGMD_FIXTURE_DIR := $(REAL_GOAL_FIXTURE_DIR)/egmd-fixture
REAL_GOAL_MEDLEYDB_AUDIO_DIR := $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)/MedleyDB
REAL_GOAL_MEDLEYDB_ANNOTATION_DIR := $(REAL_GOAL_MEDLEYDB_FIXTURE_DIR)/Annotations

OBS_CFLAGS_RAW := $(shell $(PKG_CONFIG) --cflags libobs)
OBS_CFLAGS := $(filter-out -std=gnu17 -Werror,$(OBS_CFLAGS_RAW))
OBS_INCLUDEDIR := $(shell $(PKG_CONFIG) --variable=includedir libobs)
SIMDE_SYSTEM_HEADER := $(firstword $(wildcard /usr/include/simde/x86/sse2.h /usr/local/include/simde/x86/sse2.h))
SIMDE_LOCAL_HEADER := $(DEPS_DIR)/usr/include/simde/x86/sse2.h
SIMDE_DEP := $(if $(SIMDE_SYSTEM_HEADER),,$(SIMDE_LOCAL_HEADER))
LOCAL_SIMDE_CFLAGS := $(if $(SIMDE_SYSTEM_HEADER),,-I$(DEPS_DIR)/usr/include)
OBS_LIBS := $(shell $(PKG_CONFIG) --libs libobs)

CXXFLAGS ?= -O2 -g
CXXFLAGS += -std=c++17 -fPIC -Wall -Wextra

PLUGIN_OBJS := $(BUILD_DIR)/analyzer.o $(BUILD_DIR)/plugin.o
ANALYZER_TEST_OBJ := $(BUILD_DIR)/analyzer_test.o
TEST_BINS := $(BUILD_DIR)/analyzer_smoke $(BUILD_DIR)/analyzer_cases $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd

.PHONY: all clean clean-pycache deps install-user test real-dataset-sources inspect-real-dataset-catalog inspect-real-goal-coverage inspect-real-goal-20 inspect-real-goal-full inspect-real-medleydb inspect-real-musdb inspect-real-slakh inspect-real-choralsynth inspect-real-cocochorales inspect-real-polyvocal inspect-real-multtipop inspect-real-musicnet inspect-real-musicnet-full inspect-real-spheres inspect-real-guitarset inspect-real-maestro inspect-real-egmd test-medleydb-inspector test-medleydb-prepare test-musdb-inspector test-slakh-inspector test-slakh-prepare test-choralsynth-inspector test-choralsynth-prepare test-cocochorales-inspector test-cocochorales-prepare test-polyvocal-inspector test-polyvocal-prepare test-multtipop-inspector test-spheres-inspector test-guitarset-inspector test-urmp-inspector test-real-goal-script test-real-goal-fixture test-musicnet-fixture test-medleydb-fixture test-slakh-fixture test-choralsynth-fixture test-cocochorales-fixture test-polyvocal-fixture test-multtipop-audio-root-fixture test-guitarset-fixture test-maestro-fixture test-egmd-fixture test-bach10-fixture test-direct-fit-small-fixture test-urmp-fixture test-real-goal-20 test-real-goal-full test-real-multitrack-20 test-real-multitrack-full test-real-urmp test-real-urmp-full test-real-musicnet-20 test-real-musicnet-full test-real-medleydb-20 test-real-slakh-20 test-real-slakh-full test-real-choralsynth-20 test-real-cocochorales-20 test-real-polyvocal-20 test-real-multtipop-20 test-real-multtipop-full test-real-guitarset-20 test-real-guitarset-full test-real-maestro-20 test-real-maestro-full test-real-egmd-20 test-real-egmd-full inspect-real-multitrack-20 inspect-real-multitrack-full inspect-real-urmp inspect-real-urmp-full inspect-urmp-fixture decode-urmp-fixture decode-direct-fit-small-fixture update-urmp-fixture update-direct-fit-small-fixture

all: $(SIMDE_DEP) $(BUILD_DIR)/music-analyzer-obs.so

deps: $(SIMDE_LOCAL_HEADER)

$(SIMDE_LOCAL_HEADER): | $(DEPS_DIR)
	cd $(DEPS_DIR) && apt-get download libsimde-dev
	dpkg-deb -x $(DEPS_DIR)/libsimde-dev_*.deb $(DEPS_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(DEPS_DIR): | $(BUILD_DIR)
	mkdir -p $(DEPS_DIR)

$(BUILD_DIR)/music-analyzer-obs.so: $(PLUGIN_OBJS)
	$(CXX) -shared -o $@ $^ $(OBS_LIBS) -pthread

$(BUILD_DIR)/plugin.o: src/plugin.cpp src/analyzer.hpp $(SIMDE_DEP) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(BUILD_DIR)/analyzer.o: src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/analyzer_test.o: src/analyzer.cpp src/analyzer.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -c $< -o $@

$(BUILD_DIR)/analyzer_smoke.o: tests/analyzer_smoke.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc -Itests -c $< -o $@

$(BUILD_DIR)/analyzer_cases.o: tests/analyzer_cases.cpp src/analyzer.hpp tests/analyzer_test_utils.hpp | $(BUILD_DIR)
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

$(BUILD_DIR)/analyzer_smoke: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_smoke.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_cases: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_cases.o
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

test: $(TEST_BINS)
	$(MAKE) inspect-real-dataset-catalog
	$(MAKE) inspect-real-goal-coverage
	$(MAKE) test-medleydb-inspector
	$(MAKE) test-medleydb-prepare
	$(MAKE) test-musdb-inspector
	$(MAKE) test-slakh-inspector
	$(MAKE) test-slakh-prepare
	$(MAKE) test-choralsynth-inspector
	$(MAKE) test-choralsynth-prepare
	$(MAKE) test-cocochorales-inspector
	$(MAKE) test-cocochorales-prepare
	$(MAKE) test-polyvocal-inspector
	$(MAKE) test-polyvocal-prepare
	$(MAKE) test-multtipop-inspector
	$(MAKE) test-spheres-inspector
	$(MAKE) test-guitarset-inspector
	$(MAKE) test-urmp-inspector
	$(MAKE) test-real-goal-script
	$(BUILD_DIR)/analyzer_smoke
	$(BUILD_DIR)/analyzer_cases
	$(BUILD_DIR)/analyzer_urmp
	$(BUILD_DIR)/analyzer_musicnet
	$(BUILD_DIR)/analyzer_multtipop
	$(BUILD_DIR)/analyzer_guitarset
	$(BUILD_DIR)/analyzer_maestro
	$(BUILD_DIR)/analyzer_egmd
	$(MAKE) test-direct-fit-small-fixture
	$(MAKE) test-multtipop-audio-root-fixture
	$(MAKE) test-real-goal-fixture

inspect-real-dataset-catalog: tests/inspect_real_dataset_catalog.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md
	$(PYTHON) tests/inspect_real_dataset_catalog.py

inspect-real-goal-coverage: tests/inspect_real_goal_coverage.py tests/real_dataset_catalog.json docs/real_audio_dataset_candidates.md README.md Makefile tests/analyzer_urmp.cpp tests/inspect_urmp_dataset.py tests/generate_direct_fit_small_fixture.py tests/analyzer_musicnet.cpp tests/analyzer_multtipop.cpp tests/analyzer_guitarset.cpp tests/prepare_guitarset_manifest.py tests/analyzer_maestro.cpp tests/analyzer_egmd.cpp tests/run_real_goal_gate.py tests/print_real_dataset_sources.py tests/inspect_medleydb_dataset.py tests/prepare_medleydb_musicnet_fixture.py tests/inspect_musdb_dataset.py tests/inspect_slakh_dataset.py tests/prepare_slakh_musicnet_fixture.py tests/inspect_choralsynth_dataset.py tests/prepare_choralsynth_musicnet_fixture.py tests/inspect_cocochorales_dataset.py tests/prepare_cocochorales_musicnet_fixture.py tests/inspect_polyvocal_dataset.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_multtipop_dataset.py tests/inspect_spheres_dataset.py tests/inspect_guitarset_dataset.py
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

inspect-real-polyvocal: tests/inspect_polyvocal_dataset.py
	$(PYTHON) tests/inspect_polyvocal_dataset.py

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

test-polyvocal-inspector: tests/test_inspect_polyvocal_dataset.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_inspect_polyvocal_dataset.py

test-polyvocal-prepare: tests/test_prepare_polyvocal_musicnet_fixture.py tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py tests/generate_polyvocal_fixture.py
	$(PYTHON) tests/test_prepare_polyvocal_musicnet_fixture.py

test-multtipop-inspector: tests/test_inspect_multtipop_dataset.py tests/inspect_multtipop_dataset.py tests/generate_multtipop_fixture.py
	$(PYTHON) tests/test_inspect_multtipop_dataset.py

test-spheres-inspector: tests/test_inspect_spheres_dataset.py tests/inspect_spheres_dataset.py
	$(PYTHON) tests/test_inspect_spheres_dataset.py

test-guitarset-inspector: tests/test_inspect_guitarset_dataset.py tests/inspect_guitarset_dataset.py tests/generate_guitarset_fixture.py
	$(PYTHON) tests/test_inspect_guitarset_dataset.py

test-urmp-inspector: tests/test_inspect_urmp_dataset.py tests/inspect_urmp_dataset.py
	$(PYTHON) tests/test_inspect_urmp_dataset.py

test-real-goal-script: tests/test_run_real_goal_gate.py tests/run_real_goal_gate.py
	$(PYTHON) tests/test_run_real_goal_gate.py

test-real-goal-fixture: $(BUILD_DIR)/analyzer_urmp $(BUILD_DIR)/analyzer_musicnet $(BUILD_DIR)/analyzer_multtipop $(BUILD_DIR)/analyzer_guitarset $(BUILD_DIR)/analyzer_maestro $(BUILD_DIR)/analyzer_egmd $(URMP_FIXTURE_ARCHIVE) tests/generate_musicnet_fixture.py tests/generate_medleydb_fixture.py tests/generate_musdb_fixture.py tests/generate_slakh_fixture.py tests/generate_choralsynth_fixture.py tests/generate_cocochorales_fixture.py tests/generate_polyvocal_fixture.py tests/generate_multtipop_fixture.py tests/generate_spheres_fixture.py tests/generate_guitarset_fixture.py tests/prepare_guitarset_manifest.py tests/generate_maestro_fixture.py tests/generate_egmd_fixture.py tests/run_real_goal_gate.py | $(BUILD_DIR)
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
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_multtipop_fixture.py $(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) --with-audio
	$(PYTHON) tests/generate_spheres_fixture.py $(REAL_GOAL_SPHERES_FIXTURE_DIR)
	$(PYTHON) tests/generate_guitarset_fixture.py $(REAL_GOAL_GUITARSET_FIXTURE_DIR)
	$(PYTHON) tests/generate_maestro_fixture.py $(REAL_GOAL_MAESTRO_FIXTURE_DIR)
	$(PYTHON) tests/generate_egmd_fixture.py $(REAL_GOAL_EGMD_FIXTURE_DIR)
	MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) $(PYTHON) tests/run_real_goal_gate.py inspect-20 "$(MAKE)"
	MUSIC_ANALYZER_URMP_ROOT=$(REAL_GOAL_URMP_FIXTURE_DIR) MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1 MUSIC_ANALYZER_MUSICNET_ROOT=$(REAL_GOAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MEDLEYDB_ROOT=$(REAL_GOAL_MEDLEYDB_AUDIO_DIR) MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=$(REAL_GOAL_MEDLEYDB_ANNOTATION_DIR) MUSIC_ANALYZER_MUSDB_ROOT=$(REAL_GOAL_MUSDB_FIXTURE_DIR) MUSIC_ANALYZER_SLAKH_ROOT=$(REAL_GOAL_SLAKH_FIXTURE_DIR) MUSIC_ANALYZER_CHORALSYNTH_ROOT=$(REAL_GOAL_CHORALSYNTH_FIXTURE_DIR) MUSIC_ANALYZER_COCOCHORALES_ROOT=$(REAL_GOAL_COCOCHORALES_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 MUSIC_ANALYZER_MULTTIPOP_ROOT=$(REAL_GOAL_MULTTIPOP_FIXTURE_DIR) MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 MUSIC_ANALYZER_SPHERES_ROOT=$(REAL_GOAL_SPHERES_FIXTURE_DIR) MUSIC_ANALYZER_GUITARSET_ROOT=$(REAL_GOAL_GUITARSET_FIXTURE_DIR) MUSIC_ANALYZER_MAESTRO_ROOT=$(REAL_GOAL_MAESTRO_FIXTURE_DIR) MUSIC_ANALYZER_EGMD_ROOT=$(REAL_GOAL_EGMD_FIXTURE_DIR) $(PYTHON) tests/run_real_goal_gate.py 20 "$(MAKE)"

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

test-polyvocal-fixture: $(BUILD_DIR)/analyzer_musicnet tests/generate_polyvocal_fixture.py tests/prepare_polyvocal_musicnet_fixture.py | $(BUILD_DIR)
	rm -rf $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	$(PYTHON) tests/generate_polyvocal_fixture.py $(REAL_GOAL_POLYVOCAL_FIXTURE_DIR)
	MUSIC_ANALYZER_POLYVOCAL_ROOT=$(REAL_GOAL_POLYVOCAL_FIXTURE_DIR) MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1 $(MAKE) test-real-polyvocal-20

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

test-real-polyvocal-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py | $(BUILD_DIR)
	rm -rf $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_polyvocal_musicnet_fixture.py $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(POLYVOCAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

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
	mkdir -p $(OBS_USER_PLUGIN_DIR)
	cp $(BUILD_DIR)/music-analyzer-obs.so $(OBS_USER_PLUGIN_DIR)/

clean:
	rm -rf $(BUILD_DIR)

clean-pycache:
	find tests -type d -name '__pycache__' -prune -exec rm -rf {} +
