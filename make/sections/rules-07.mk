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

.PHONY: android-check-auphy-sct86pro
android-check-auphy-sct86pro: scripts/check_android_auphy_sct86pro_runtime.sh
	bash scripts/check_android_auphy_sct86pro_runtime.sh

.PHONY: test-android-project-static
test-android-project-static: scripts/test_android_project_static.sh
	bash scripts/test_android_project_static.sh

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

