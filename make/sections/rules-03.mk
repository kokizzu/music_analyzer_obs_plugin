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

