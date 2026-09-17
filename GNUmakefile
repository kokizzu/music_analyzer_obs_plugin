# GNU make loads GNUmakefile before Makefile. Keep the existing Makefile as the
# canonical build definition, then extend its OBS target with the Audacious-only
# sources and renderer redirection.
include Makefile
include windows.mk

AUDACIOUS_TITLE_OBJ := $(BUILD_DIR)/audacious_title.o
AUDACIOUS_OVERLAY_OBJ := $(BUILD_DIR)/audacious_overlay.o
UNICODE_TITLE_RENDERER_OBJ := $(BUILD_DIR)/unicode_title_renderer.o
AUDACIOUS_OBJS := $(AUDACIOUS_TITLE_OBJ) $(AUDACIOUS_OVERLAY_OBJ) $(UNICODE_TITLE_RENDERER_OBJ)
AUDACIOUS_TITLE_TEST_BIN := $(BUILD_DIR)/audacious_title_tests
UNICODE_TITLE_TEST_BIN := $(BUILD_DIR)/unicode_title_renderer_tests
DL_LIBS ?= -ldl

# The original Makefile's prerequisite list is expanded before this file can
# append to PLUGIN_OBJS, so add the Audacious objects directly to the existing
# shared-library target. Pango/Cairo are loaded at runtime, so only libdl is
# needed at link time and no extra development package is required.
$(BUILD_DIR)/music-analyzer-obs.so: $(AUDACIOUS_OBJS)
$(BUILD_DIR)/music-analyzer-obs.so: OBS_LIBS += $(DL_LIBS)

# Redirect only plugin.cpp's analyzer-render calls. OBS source registration and
# final texture drawing retain the repository's original, known-good behavior.
$(BUILD_DIR)/plugin.o: GNUmakefile src/audacious_plugin_redirect.hpp src/audacious_overlay.hpp
$(BUILD_DIR)/plugin.o: CXXFLAGS += -include src/audacious_plugin_redirect.hpp

$(AUDACIOUS_TITLE_OBJ): src/audacious_title.cpp src/audacious_title.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(AUDACIOUS_OVERLAY_OBJ): src/audacious_overlay.cpp src/audacious_overlay.hpp src/audacious_poll_schedule.hpp src/audacious_title.hpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(UNICODE_TITLE_RENDERER_OBJ): src/unicode_title_renderer.cpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(AUDACIOUS_TITLE_TEST_BIN): tests/audacious_title.cpp src/audacious_poll_schedule.hpp src/audacious_title.cpp src/audacious_title.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc tests/audacious_title.cpp src/audacious_title.cpp -o $@

$(UNICODE_TITLE_TEST_BIN): tests/unicode_title_renderer.cpp src/unicode_title_renderer.cpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc tests/unicode_title_renderer.cpp src/unicode_title_renderer.cpp $(DL_LIBS) -o $@

.PHONY: test-audacious-title test-audacious-unicode
test-audacious-title: $(AUDACIOUS_TITLE_TEST_BIN)
	$(AUDACIOUS_TITLE_TEST_BIN)

test-audacious-unicode: $(UNICODE_TITLE_TEST_BIN)
	$(UNICODE_TITLE_TEST_BIN)

test: test-audacious-title test-audacious-unicode
.PHONY: list-windows-targets
list-windows-targets:
	$(PYTHON) scripts/list_windows_targets.py

.PHONY: inspect-hardware-control-sources
inspect-hardware-control-sources:
	$(PYTHON) scripts/inspect_hardware_control_sources.py

.PHONY: inspect-fret-control-source
inspect-fret-control-source:
	$(PYTHON) scripts/inspect_fret_control_source.py

.PHONY: inspect-android-hardware-controller
inspect-android-hardware-controller:
	$(PYTHON) scripts/inspect_android_hardware_controller.py

.PHONY: inspect-android-midi-controller
inspect-android-midi-controller:
	$(PYTHON) scripts/inspect_android_midi_controller.py

.PHONY: inspect-windows-standalone-source
inspect-windows-standalone-source:
	$(PYTHON) scripts/inspect_windows_standalone_source.py

.PHONY: inspect-windows-build-script
inspect-windows-build-script:
	$(PYTHON) scripts/inspect_windows_build_script.py

.PHONY: inspect-windows-bluetooth-headers
inspect-windows-bluetooth-headers:
	$(PYTHON) scripts/inspect_windows_bluetooth_headers.py

.PHONY: inspect-windows-hardware-integration
inspect-windows-hardware-integration:
	$(PYTHON) scripts/inspect_windows_hardware_integration.py

.PHONY: verify-windows-hardware-sources
verify-windows-hardware-sources:
	$(PYTHON) scripts/verify_windows_hardware_sources.py

.PHONY: inspect-windows-hardware-api
inspect-windows-hardware-api:
	$(PYTHON) scripts/inspect_windows_hardware_api.py

.PHONY: inspect-windows-standalone-doc
inspect-windows-standalone-doc:
	$(PYTHON) scripts/inspect_windows_standalone_doc.py


.PHONY: plan-deploy-windows-mounted deploy-windows-mounted
plan-deploy-windows-mounted:
	$(PYTHON) scripts/deploy_windows_mounted.py plan

deploy-windows-mounted: windows-standalone
	$(PYTHON) scripts/deploy_windows_mounted.py apply
inspect-windows-litejam-protocol:
	python3 scripts/inspect_windows_litejam_protocol.py
verify-windows-runtime-bundle:
	python3 scripts/verify_windows_runtime_bundle.py
inspect-windows-fret-zealot-protocol:
	python3 scripts/inspect_windows_fret_zealot_protocol.py
review-windows-hardware-diff:
	python3 scripts/review_windows_hardware_diff.py
inspect-windows-deployment:
	python3 scripts/inspect_windows_deployment.py
