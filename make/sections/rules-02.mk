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

