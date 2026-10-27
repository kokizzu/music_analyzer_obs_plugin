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

