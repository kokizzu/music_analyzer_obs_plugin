# GNU make loads GNUmakefile before Makefile. Keep the existing Makefile as the
# canonical build definition, then extend its OBS target with the Audacious-only
# sources and renderer redirection.
include Makefile

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

$(AUDACIOUS_OVERLAY_OBJ): src/audacious_overlay.cpp src/audacious_overlay.hpp src/audacious_title.hpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(UNICODE_TITLE_RENDERER_OBJ): src/unicode_title_renderer.cpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(OBS_CFLAGS) $(LOCAL_SIMDE_CFLAGS) -I$(OBS_INCLUDEDIR)/obs -Isrc -c $< -o $@

$(AUDACIOUS_TITLE_TEST_BIN): tests/audacious_title.cpp src/audacious_title.cpp src/audacious_title.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc tests/audacious_title.cpp src/audacious_title.cpp -o $@

$(UNICODE_TITLE_TEST_BIN): tests/unicode_title_renderer.cpp src/unicode_title_renderer.cpp src/unicode_title_renderer.hpp src/visualizer_renderer.hpp GNUmakefile | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc tests/unicode_title_renderer.cpp src/unicode_title_renderer.cpp $(DL_LIBS) -o $@

.PHONY: test-audacious-title test-audacious-unicode
test-audacious-title: $(AUDACIOUS_TITLE_TEST_BIN)
	$(AUDACIOUS_TITLE_TEST_BIN)

test-audacious-unicode: $(UNICODE_TITLE_TEST_BIN)
	$(UNICODE_TITLE_TEST_BIN)

test: test-audacious-title test-audacious-unicode
