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

