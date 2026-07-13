CXX ?= g++
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
BUILD_DIR ?= build
DEPS_DIR ?= $(BUILD_DIR)/deps
OBS_USER_PLUGIN_DIR ?= $(HOME)/.config/obs-studio/plugins/music-analyzer-obs/bin/64bit

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
TEST_BINS := $(BUILD_DIR)/analyzer_smoke $(BUILD_DIR)/analyzer_cases $(BUILD_DIR)/analyzer_urmp

.PHONY: all clean deps install-user test test-urmp-fixture

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

$(BUILD_DIR)/analyzer_smoke: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_smoke.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_cases: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_cases.o
	$(CXX) -o $@ $^ -lm -pthread

$(BUILD_DIR)/analyzer_urmp: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/analyzer_urmp.o
	$(CXX) -o $@ $^ -lm -pthread

test: $(TEST_BINS)
	$(BUILD_DIR)/analyzer_smoke
	$(BUILD_DIR)/analyzer_cases
	$(BUILD_DIR)/analyzer_urmp
	$(MAKE) test-urmp-fixture

test-urmp-fixture: $(BUILD_DIR)/analyzer_urmp tests/generate_urmp_fixture.py | $(BUILD_DIR)
	$(PYTHON) tests/generate_urmp_fixture.py $(BUILD_DIR)/urmp-fixture
	MUSIC_ANALYZER_URMP_ROOT=$(BUILD_DIR)/urmp-fixture $(BUILD_DIR)/analyzer_urmp

install-user: all
	mkdir -p $(OBS_USER_PLUGIN_DIR)
	cp $(BUILD_DIR)/music-analyzer-obs.so $(OBS_USER_PLUGIN_DIR)/

clean:
	rm -rf $(BUILD_DIR)
