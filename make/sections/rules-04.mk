commit-fret-zealot-auto-stabilization: scripts/commit_verified_fret_zealot_auto_stabilization.py
	$(PYTHON) scripts/commit_verified_fret_zealot_auto_stabilization.py apply

.PHONY: inspect-fret-zealot-scale-update
inspect-fret-zealot-scale-update: scripts/inspect_fret_zealot_scale_update.py
	$(PYTHON) scripts/inspect_fret_zealot_scale_update.py

.PHONY: test-fret-zealot-auto-root-stability
test-fret-zealot-auto-root-stability: tests/check_fret_zealot_auto_root_stability.py
	$(PYTHON) tests/check_fret_zealot_auto_root_stability.py

inspect-detection-make-target: scripts/list_detection_make_targets.py
	$(PYTHON) scripts/list_detection_make_targets.py "$(MAKE_TARGET_NAME)"

inspect-detector-source: scripts/inspect_detector_source.py
	$(PYTHON) scripts/inspect_detector_source.py "$(DETECTOR_SOURCE_TERM)" --context "$(or $(DETECTOR_SOURCE_CONTEXT),3)"

.PHONY: inspect-project-source
inspect-project-source: scripts/inspect_project_source.py
	$(PYTHON) scripts/inspect_project_source.py "$(PROJECT_SOURCE_TERM)" --context "$(or $(PROJECT_SOURCE_CONTEXT),3)"

print-real-a2s-tenor-index: download-real-a2s-sax-samples
	$(TAR) -xOzf "$(REAL_A2S_SAX_ARCHIVE)" real_a2s_sax_dataset/Tenor_Sax_Index.csv

inspect-real-a2s-tenor-index-cached: scripts/inspect_real_a2s_tenor_index.py
	$(PYTHON) scripts/inspect_real_a2s_tenor_index.py --index "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/Tenor_Sax_Index.csv"

inspect-real-a2s-sax-score-members: download-real-a2s-sax-samples
	$(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" --wildcards '*.krn'

.PHONY: extract-real-a2s-sax-scale-probes
extract-real-a2s-sax-scale-probes: download-real-a2s-sax-samples
	mkdir -p "$(REAL_A2S_SAX_PROBE_DIR)"
	$(TAR) -xzf "$(REAL_A2S_SAX_ARCHIVE)" -C "$(REAL_A2S_SAX_PROBE_DIR)" $(foreach recording,$(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES),real_a2s_sax_dataset/real/tenor/$(recording).wav)

.PHONY: extract-real-a2s-sax-exercise-probes
extract-real-a2s-sax-exercise-probes: download-real-a2s-sax-samples
	mkdir -p "$(REAL_A2S_SAX_PROBE_DIR)"
	$(TAR) -xzf "$(REAL_A2S_SAX_ARCHIVE)" -C "$(REAL_A2S_SAX_PROBE_DIR)" real_a2s_sax_dataset/real/tenor/Ex1.wav real_a2s_sax_dataset/real/tenor/Ex2.wav real_a2s_sax_dataset/real/tenor/Ex3.wav

.PHONY: inspect-real-a2s-sax-scale-probes
inspect-real-a2s-sax-scale-probes: extract-real-a2s-sax-scale-probes scripts/inspect_real_a2s_sax_scale.py
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn"


.PHONY: inspect-real-a2s-sax-scale-probes-cached
inspect-real-a2s-sax-scale-probes-cached: scripts/inspect_real_a2s_sax_scale.py
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" || { printf '%s\n' "missing scale probe; run make extract-real-a2s-sax-scale-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn" || { printf '%s\n' "missing tenor score; run make extract-real-a2s-sax-metadata first"; exit 2; }
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/GMajScale.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/GMajScale.krn"

.PHONY: inspect-real-a2s-sax-exercise-probes-cached
inspect-real-a2s-sax-exercise-probes-cached: scripts/inspect_real_a2s_sax_scale.py
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex1.krn"
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex2.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex2.krn"
	$(PYTHON) scripts/inspect_real_a2s_sax_scale.py --wav "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex3.wav" --kern "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/Ex3.krn"

.PHONY: test-inspect-real-a2s-sax-scale
test-inspect-real-a2s-sax-scale: tests/test_inspect_real_a2s_sax_scale.py scripts/inspect_real_a2s_sax_scale.py
	$(PYTHON) tests/test_inspect_real_a2s_sax_scale.py

.PHONY: prepare-real-a2s-tenor-scale-probes prepare-real-a2s-tenor-scale-probes-cached test-prepare-real-a2s-tenor-scale-probes measure-real-a2s-tenor-scale-probes analyze-real-a2s-tenor-scale-probes find-real-a2s-tenor-scale-routing-patterns
prepare-real-a2s-tenor-scale-probes: extract-real-a2s-sax-scale-probes extract-real-a2s-sax-metadata scripts/prepare_real_a2s_sax_scale_fixture.py
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=real_a2s_tenor_scale_fixture
	$(PYTHON) scripts/prepare_real_a2s_sax_scale_fixture.py $(REAL_A2S_SAX_TENOR_SCALE_INPUTS) $(REAL_A2S_SAX_TENOR_EXERCISE_INPUTS) --output "$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --midi-offset "$(REAL_A2S_SAX_SCALE_MIDI_OFFSET)"

prepare-real-a2s-tenor-scale-probes-cached: scripts/prepare_real_a2s_sax_scale_fixture.py
	@for recording in $(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES); do test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/$$recording.wav" || { printf '%s\n' "missing scale probe; run make extract-real-a2s-sax-scale-probes first"; exit 2; }; done
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex1.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex2.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@test -s "$(REAL_A2S_SAX_PROBE_DIR)/real_a2s_sax_dataset/real/tenor/Ex3.wav" || { printf '%s\n' "missing exercise probe; run make extract-real-a2s-sax-exercise-probes first"; exit 2; }
	@for recording in $(REAL_A2S_SAX_TENOR_MAJOR_SCALE_PROBES); do test -s "$(REAL_A2S_SAX_METADATA_DIR)/real_a2s_sax_dataset/krn/tenor/$$recording.krn" || { printf '%s\n' "missing tenor score; run make extract-real-a2s-sax-metadata first"; exit 2; }; done
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=real_a2s_tenor_scale_fixture
	$(PYTHON) scripts/prepare_real_a2s_sax_scale_fixture.py $(REAL_A2S_SAX_TENOR_SCALE_INPUTS) $(REAL_A2S_SAX_TENOR_EXERCISE_INPUTS) --output "$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)" --midi-offset "$(REAL_A2S_SAX_SCALE_MIDI_OFFSET)"

test-prepare-real-a2s-tenor-scale-probes: tests/test_prepare_real_a2s_sax_scale_fixture.py scripts/prepare_real_a2s_sax_scale_fixture.py
	$(PYTHON) tests/test_prepare_real_a2s_sax_scale_fixture.py

measure-real-a2s-tenor-scale-probes: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-a2s-tenor-scale-probes-cached | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(REAL_A2S_SAX_SCALE_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_A2S_SAX_SCALE_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples

analyze-real-a2s-tenor-scale-probes: $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) scripts/analyze_exact_midi_misses.py
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

find-real-a2s-tenor-scale-routing-patterns: $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" --bucket-status first_row_confusion --top-buckets 6 --min-positive-samples 3 --max-negative-samples 0 --include-row-context --profile-fields 10 --show-examples 2

$(REAL_A2S_SAX_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(REAL_A2S_SAX_SOURCE_DIR)"
	if [ -s "$(REAL_A2S_SAX_ARCHIVE)" ] && ! $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(REAL_A2S_SAX_ARCHIVE)" "$(REAL_A2S_SAX_ARCHIVE).part"; fi
	if [ ! -s "$(REAL_A2S_SAX_ARCHIVE)" ] && [ -s "$(REAL_A2S_SAX_ARCHIVE).part" ] && $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE).part" >/dev/null 2>&1; then mv "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE)"; fi
	if [ ! -s "$(REAL_A2S_SAX_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 8 -s 8 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(REAL_A2S_SAX_SOURCE_DIR)" --out "real_a2s_sax_dataset.tgz.part" "$(REAL_A2S_SAX_ARCHIVE_URL)"; else curl -fL -C - -o "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE_URL)"; fi; fi
	if [ -s "$(REAL_A2S_SAX_ARCHIVE).part" ]; then $(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE).part" >/dev/null; mv "$(REAL_A2S_SAX_ARCHIVE).part" "$(REAL_A2S_SAX_ARCHIVE)"; fi
	$(TAR) -tzf "$(REAL_A2S_SAX_ARCHIVE)" >/dev/null

$(MEDLEY_SOLOS_METADATA): | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	curl -fL -C - -o "$(MEDLEY_SOLOS_METADATA)" "$(MEDLEY_SOLOS_METADATA_URL)"

$(MEDLEY_SOLOS_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(MEDLEY_SOLOS_SOURCE_DIR)"
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && ! $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(MEDLEY_SOLOS_ARCHIVE)" "$(MEDLEY_SOLOS_ARCHIVE).part"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ] && [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ] && $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null 2>&1; then mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	if [ ! -s "$(MEDLEY_SOLOS_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 8 -s 8 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(MEDLEY_SOLOS_SOURCE_DIR)" --out "Medley-solos-DB.tar.gz.part" "$(MEDLEY_SOLOS_URL)"; else curl -fL -C - -o "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_URL)"; fi; fi
	if [ -s "$(MEDLEY_SOLOS_ARCHIVE).part" ]; then $(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE).part" >/dev/null; mv "$(MEDLEY_SOLOS_ARCHIVE).part" "$(MEDLEY_SOLOS_ARCHIVE)"; fi
	$(TAR) -tzf "$(MEDLEY_SOLOS_ARCHIVE)" >/dev/null

prepare-medley-solos-samples: scripts/prepare_medley_solos_samples.py download-medley-solos-samples | $(BUILD_DIR)
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=medley_solos_samples
	MEDLEY_SOLOS_METADATA="$(MEDLEY_SOLOS_METADATA)" MEDLEY_SOLOS_ARCHIVE="$(MEDLEY_SOLOS_ARCHIVE)" MEDLEY_SOLOS_SAMPLE_DIR="$(MEDLEY_SOLOS_SAMPLE_DIR)" MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT="$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" MEDLEY_SOLOS_MIN_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MEDLEY_SOLOS_MIN_COUNTS="$(MEDLEY_SOLOS_MIN_COUNTS)" FFMPEG="$(FFMPEG)" $(PYTHON) scripts/prepare_medley_solos_samples.py --metadata "$(MEDLEY_SOLOS_METADATA)" --archive "$(MEDLEY_SOLOS_ARCHIVE)" --output "$(MEDLEY_SOLOS_SAMPLE_DIR)" --limit-per-instrument "$(MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT)" --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-counts "$(MEDLEY_SOLOS_MIN_COUNTS)" --ffmpeg "$(FFMPEG)"

test-medley-solos-samples: test-medley-solos-samples-parallel

$(MEDLEY_SOLOS_ATTRIBUTE_TSV): $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_instrument_family_samples > "$@.out"

# Recompute metrics from the prepared corpus without forcing its download/prepare
# prerequisite.  This is safe for routine detector iterations and keeps the
# persisted report synchronized with the analyzer currently under test.
refresh-medley-solos-attributes-cached: $(BUILD_DIR)/analyzer_instrument_family_samples scripts/run_with_lock.sh | $(BUILD_DIR)
	@test -s "$(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv; run make prepare-medley-solos-samples first"; exit 2; }
	@rm -f "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	+$(SHELL) scripts/run_with_lock.sh "$(MEDLEY_SOLOS_LOCK_DIR)" -- env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_ATTRIBUTE_TSV="$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_instrument_family_samples

analyze-medley-solos-attributes: $(MEDLEY_SOLOS_ATTRIBUTE_TSV) scripts/summarize_instrument_family_attributes.py
	$(PYTHON) scripts/summarize_instrument_family_attributes.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	@printf '%s\n' "Medley Solos attribute TSV: $(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

analyze-medley-solos-attributes-cached: scripts/summarize_instrument_family_attributes.py
	@test -s "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MEDLEY_SOLOS_ATTRIBUTE_TSV); run make refresh-medley-solos-attributes-cached first"; exit 2; }
	$(PYTHON) scripts/summarize_instrument_family_attributes.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"
	@printf '%s\n' "Medley Solos cached attribute TSV: $(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-misses: $(MEDLEY_SOLOS_ATTRIBUTE_TSV) scripts/inspect_instrument_family_misses.py
	$(PYTHON) scripts/inspect_instrument_family_misses.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-misses-cached: scripts/inspect_instrument_family_misses.py
	@test -s "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)" || { printf '%s\n' "missing $(MEDLEY_SOLOS_ATTRIBUTE_TSV); run make inspect-medley-solos-misses first"; exit 2; }
	$(PYTHON) scripts/inspect_instrument_family_misses.py "$(MEDLEY_SOLOS_ATTRIBUTE_TSV)"

inspect-medley-solos-debug-cached: $(BUILD_DIR)/analyzer_instrument_family_samples
	@test -n "$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set MEDLEY_SOLOS_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(MEDLEY_SOLOS_SAMPLE_DIR)/manifest.tsv; run make prepare-medley-solos-samples first"; exit 2; }
	env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ID="$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_DEBUG_SAMPLE_ID="$(MEDLEY_SOLOS_DEBUG_SAMPLE_ID)" $(BUILD_DIR)/analyzer_instrument_family_samples

test-medley-solos-samples-serial: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_medley_solos_samples env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES="$(MEDLEY_SOLOS_MIN_SAMPLES)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT="$(MEDLEY_SOLOS_MIN_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_instrument_family_samples

test-medley-solos-samples-parallel: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/check_instrument_family_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_medley_solos_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MEDLEY_SOLOS_LOCK_DIR)" -- "$(MAKE)" test-medley-solos-samples-parallel-unlocked

test-medley-solos-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/check_instrument_family_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MEDLEY_SOLOS_TEST_MAKE_JOBS) $(MEDLEY_SOLOS_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_medley_solos_shards $(PYTHON) scripts/check_instrument_family_shards.py --min-samples "$(MEDLEY_SOLOS_MIN_SAMPLES)" --min-recall-percent "$(MEDLEY_SOLOS_MIN_RECALL_PERCENT)" $(MEDLEY_SOLOS_SHARD_OUTS)

test-medley-solos-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_instrument_family_samples prepare-medley-solos-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_medley_solos_samples_shard_$* env MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SAMPLE_ROOT="$(MEDLEY_SOLOS_SAMPLE_DIR)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_COUNT="$(MEDLEY_SOLOS_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_FAMILY_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_instrument_family_samples > "$(BUILD_DIR)/medley_solos_samples_shard_$*.out" 2> "$(BUILD_DIR)/medley_solos_samples_shard_$*.err"

download-maps-piano-samples: $(MAPS_PIANO_ARCHIVE)

$(MAPS_PIANO_ARCHIVE): FORCE | $(BUILD_DIR)
	mkdir -p "$(MAPS_PIANO_SOURCE_DIR)"
	if [ -s "$(MAPS_PIANO_ARCHIVE)" ] && ! $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(MAPS_PIANO_ARCHIVE)" "$(MAPS_PIANO_ARCHIVE).part"; fi
	if [ ! -s "$(MAPS_PIANO_ARCHIVE)" ] && [ -s "$(MAPS_PIANO_ARCHIVE).part" ] && $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE).part" >/dev/null 2>&1; then mv "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_ARCHIVE)"; fi
	if [ ! -s "$(MAPS_PIANO_ARCHIVE)" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x "$(MAPS_PIANO_DOWNLOAD_CONNECTIONS)" -s "$(MAPS_PIANO_DOWNLOAD_CONNECTIONS)" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(MAPS_PIANO_SOURCE_DIR)" --out "ENSTDkCl.zip.part" "$(MAPS_PIANO_URL)"; else curl -fL -C - -o "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_URL)"; fi; fi
	if [ -s "$(MAPS_PIANO_ARCHIVE).part" ]; then $(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE).part" >/dev/null; mv "$(MAPS_PIANO_ARCHIVE).part" "$(MAPS_PIANO_ARCHIVE)"; fi
	$(PYTHON) -m zipfile -t "$(MAPS_PIANO_ARCHIVE)" >/dev/null

prepare-maps-piano-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MAPS_PIANO_KINDS="$(MAPS_PIANO_KINDS)" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_SAMPLE_DIR)" --limit "$(MAPS_PIANO_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --kinds "$(MAPS_PIANO_KINDS)"

# MAESTRO is a second independently recorded Disklavier corpus.  Its archive
# and the selected WAV/MIDI fixture remain under InstrumentSamples; build only
# retains the stable symlink used by analyzer targets.
download-maestro-real-samples: scripts/validate_maestro_subset_archive.py scripts/prepare_maps_piano_samples.py | $(BUILD_DIR)
	mkdir -p "$(MAESTRO_REAL_SOURCE_DIR)"
	test -s "$(MAESTRO_REAL_ARCHIVE)" || curl -fL -C - -o "$(MAESTRO_REAL_ARCHIVE).part" "$(MAESTRO_REAL_URL)"
	@test ! -s "$(MAESTRO_REAL_ARCHIVE).part" || mv "$(MAESTRO_REAL_ARCHIVE).part" "$(MAESTRO_REAL_ARCHIVE)"
	$(PYTHON) scripts/validate_maestro_subset_archive.py --archive "$(MAESTRO_REAL_ARCHIVE)" --kinds OTHER --min-pairs "$(MAESTRO_REAL_MIN_RECORDINGS)"

.PHONY: download-kraisler validate-kraisler-archive extract-kraisler prepare-kraisler measure-kraisler summarize-kraisler test-validate-kraisler-archive test-extract-kraisler test-prepare-kraisler test-summarize-kraisler
download-kraisler: configure-instrument-sample-store $(KRAISLER_ARCHIVE) validate-kraisler-archive

$(KRAISLER_ARCHIVE): scripts/validate_kraisler_archive.py
	mkdir -p "$(KRAISLER_SOURCE_DIR)"
	if test -s "$@"; then $(PYTHON) scripts/validate_kraisler_archive.py --archive "$@" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"; elif command -v aria2c >/dev/null 2>&1; then aria2c --continue=true --allow-overwrite=true --auto-file-renaming=false --file-allocation=none --max-tries=5 --retry-wait=5 --max-connection-per-server=8 --split=8 --min-split-size=1M --dir "$(KRAISLER_SOURCE_DIR)" --out "KRAISLER.zip.part" "$(KRAISLER_ARCHIVE_URL)" && mv "$@.part" "$@"; else curl -fL -C - -o "$@.part" "$(KRAISLER_ARCHIVE_URL)" && mv "$@.part" "$@"; fi

validate-kraisler-archive: $(KRAISLER_ARCHIVE) scripts/validate_kraisler_archive.py
	$(PYTHON) scripts/validate_kraisler_archive.py --archive "$(KRAISLER_ARCHIVE)" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

extract-kraisler: validate-kraisler-archive scripts/extract_kraisler.py
	$(PYTHON) scripts/extract_kraisler.py --archive "$(KRAISLER_ARCHIVE)" --output "$(KRAISLER_EXTRACT_DIR)" --expected-md5 "$(KRAISLER_ARCHIVE_MD5)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

prepare-kraisler: extract-kraisler scripts/prepare_kraisler_manifest.py
	$(PYTHON) scripts/prepare_kraisler_manifest.py --root "$(KRAISLER_EXTRACT_DIR)" --output "$(KRAISLER_PREPARED_DIR)" --minimum-tracks "$(KRAISLER_MIN_TRACKS)"

measure-kraisler: $(BUILD_DIR)/analyzer_musicnet prepare-kraisler tests/prepare_prepared_multitrack_musicnet_fixture.py scripts/summarize_kraisler_measurement.py | $(BUILD_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$(KRAISLER_PREPARED_DIR)" MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_SOURCES=2 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py "$(KRAISLER_MUSICNET_DIR)"
	MUSIC_ANALYZER_MUSICNET_ROOT="$(KRAISLER_MUSICNET_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(KRAISLER_MIN_PIECES)" MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$(KRAISLER_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) summarize-kraisler

summarize-kraisler: $(KRAISLER_ATTRIBUTE_OUTPUT) prepare-kraisler scripts/summarize_kraisler_measurement.py
	$(PYTHON) scripts/summarize_kraisler_measurement.py --attributes "$(KRAISLER_ATTRIBUTE_OUTPUT)" --manifest "$(KRAISLER_PREPARED_DIR)/manifest.json" --output "$(KRAISLER_MEASUREMENT_OUTPUT)"

.PHONY: download-irmas validate-irmas extract-irmas inspect-irmas prepare-irmas measure-irmas test-irmas-scripts
download-irmas: $(IRMAS_ARCHIVES)

validate-irmas: $(IRMAS_ARCHIVES)

define IRMAS_ARCHIVE_RULE
$(1): FORCE scripts/validate_irmas_archive.py | $(BUILD_DIR)
	mkdir -p "$(IRMAS_SOURCE_DIR)"
	if [ -s "$$@" ] && ! $(PYTHON) scripts/validate_irmas_archive.py --archive "$$@" --md5 "$(2)" >/dev/null 2>&1; then mv -f "$$@" "$$@.corrupt"; fi
	if [ ! -s "$$@" ]; then if command -v "$(ARIA2C)" >/dev/null 2>&1; then "$(ARIA2C)" -c -x 4 -s 4 -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$(IRMAS_SOURCE_DIR)" --out "$(notdir $(1)).part" "$(3)"; else curl -fL -C - -o "$$@.part" "$(3)"; fi; fi
	if [ -s "$$@.part" ]; then $(PYTHON) scripts/validate_irmas_archive.py --archive "$$@.part" --md5 "$(2)"; mv -f "$$@.part" "$$@"; fi
	$(PYTHON) scripts/validate_irmas_archive.py --archive "$$@" --md5 "$(2)"
endef
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART1_ARCHIVE),$(IRMAS_TEST_PART1_MD5),$(IRMAS_TEST_PART1_URL)))
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART2_ARCHIVE),$(IRMAS_TEST_PART2_MD5),$(IRMAS_TEST_PART2_URL)))
$(eval $(call IRMAS_ARCHIVE_RULE,$(IRMAS_TEST_PART3_ARCHIVE),$(IRMAS_TEST_PART3_MD5),$(IRMAS_TEST_PART3_URL)))

extract-irmas: download-irmas scripts/extract_irmas.py
	$(PYTHON) scripts/extract_irmas.py $(foreach archive,$(IRMAS_ARCHIVES),--archive "$(archive)") --output "$(IRMAS_EXTRACT_DIR)"

inspect-irmas: extract-irmas scripts/inspect_irmas.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_irmas.py --root "$(IRMAS_EXTRACT_DIR)" > "$(IRMAS_INVENTORY_OUTPUT)"
	cat "$(IRMAS_INVENTORY_OUTPUT)"

prepare-irmas: extract-irmas scripts/prepare_irmas_manifest.py
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=irmas_labelled_samples
	$(PYTHON) scripts/prepare_irmas_manifest.py --root "$(IRMAS_EXTRACT_DIR)" --output "$(IRMAS_PREPARED_DIR)" --max-per-label "$(IRMAS_MAX_SAMPLES_PER_LABEL)" --minimum-samples "$(IRMAS_MIN_SAMPLES)"

measure-irmas: $(BUILD_DIR)/analyzer_real_note_samples prepare-irmas | $(BUILD_DIR)
	MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(IRMAS_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(IRMAS_PREPARED_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_LABEL_ONLY=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(IRMAS_ATTRIBUTE_OUTPUT)" $(BUILD_DIR)/analyzer_real_note_samples > "$(IRMAS_MEASUREMENT_OUTPUT)"

test-irmas-scripts: tests/test_irmas_scripts.py scripts/validate_irmas_archive.py scripts/extract_irmas.py scripts/prepare_irmas_manifest.py scripts/inspect_irmas.py
	$(PYTHON) tests/test_irmas_scripts.py

test-validate-kraisler-archive: tests/test_validate_kraisler_archive.py scripts/validate_kraisler_archive.py
	$(PYTHON) tests/test_validate_kraisler_archive.py

test-extract-kraisler: tests/test_extract_kraisler.py scripts/extract_kraisler.py scripts/validate_kraisler_archive.py
	$(PYTHON) tests/test_extract_kraisler.py

test-prepare-kraisler: tests/test_prepare_kraisler_manifest.py scripts/prepare_kraisler_manifest.py
	$(PYTHON) tests/test_prepare_kraisler_manifest.py

test-summarize-kraisler: tests/test_summarize_kraisler_measurement.py scripts/summarize_kraisler_measurement.py
	$(PYTHON) tests/test_summarize_kraisler_measurement.py

prepare-maestro-real-samples: scripts/prepare_maps_piano_samples.py download-maestro-real-samples | $(BUILD_DIR)
	+$(MAKE) BUILD_SAMPLE_STORAGE_DIR=maestro_real_samples ensure-build-sample-storage-link
	MAPS_PIANO_ARCHIVE="$(MAESTRO_REAL_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAESTRO_REAL_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAESTRO_REAL_SAMPLE_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAESTRO_REAL_MIN_RECORDINGS)" MAPS_PIANO_KINDS=OTHER $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAESTRO_REAL_ARCHIVE)" --output "$(MAESTRO_REAL_SAMPLE_DIR)" --limit "$(MAESTRO_REAL_SAMPLE_LIMIT)" --min-recordings "$(MAESTRO_REAL_MIN_RECORDINGS)" --kinds OTHER

measure-maestro-real-samples: $(BUILD_DIR)/analyzer_maestro prepare-maestro-real-samples scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) maestro_real_measurement env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAESTRO_REAL_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAESTRO_REAL_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$(MAESTRO_REAL_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_maestro > "$(MAESTRO_REAL_MEASUREMENT_OUTPUT)"
	@# Keep the committed accuracy dashboard synchronized with a new real result.
	@if test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)"; then $(MAKE) analyze-independent-piano-chord-evidence analyze-independent-piano-chord-states; else printf '%s\n' "independent piano comparison skipped: missing $(MAPS_PIANO_ATTRIBUTE_TSV)"; fi
	@if test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv"; then $(MAKE) update-detection-accuracy-report-cached; else printf '%s\n' "accuracy dashboard refresh skipped: missing $(BUILD_DIR)/real_note_full_mix_attributes.tsv"; fi

test-maps-piano-samples: test-maps-piano-samples-parallel

test-maps-piano-samples-serial: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT="$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT="$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT="$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT="$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(BUILD_DIR)/analyzer_maestro

test-maps-piano-samples-parallel: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_maps_piano_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MAPS_PIANO_LOCK_DIR)" -- "$(MAKE)" test-maps-piano-samples-parallel-unlocked

test-maps-piano-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/check_maestro_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MAPS_PIANO_TEST_MAKE_JOBS) $(MAPS_PIANO_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_maps_piano_shards $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_REQUIRED_WINDOWS)" --min-recall-percent "$(MAPS_PIANO_MIN_RECALL_PERCENT)" --min-precision-percent "$(MAPS_PIANO_MIN_PRECISION_PERCENT)" --min-keyboard-recall-percent "$(MAPS_PIANO_MIN_KEYBOARD_RECALL_PERCENT)" --max-contamination-percent "$(MAPS_PIANO_MAX_CONTAMINATION_PERCENT)" --max-false-non-keyboard-percent "$(MAPS_PIANO_MAX_FALSE_NON_KEYBOARD_PERCENT)" --min-chord-recall-percent "$(MAPS_PIANO_MIN_CHORD_RECALL_PERCENT)" --min-chord-precision-percent "$(MAPS_PIANO_MIN_CHORD_PRECISION_PERCENT)" --min-chord-checks "$(MAPS_PIANO_MIN_CHORD_CHECKS)" $(MAPS_PIANO_SHARD_OUTS)

test-maps-piano-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS="$(MAPS_PIANO_MIN_CHORD_CHECKS)" MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_samples_shard_$*.err"

capture-analyzer-cases: $(BUILD_DIR)/analyzer_cases scripts/run_with_duration.sh | $(BUILD_DIR)
	$(RUN_WITH_DURATION) analyzer_cases_capture $(BUILD_DIR)/analyzer_cases > "$(BUILD_DIR)/analyzer_cases_capture.out" 2>&1

# Measure the prepared MAPS chord fixture without archive checks, preparation,
# or downloading.  The regular test target remains the policy gate.
measure-maps-piano-cached: $(BUILD_DIR)/analyzer_maestro scripts/check_maestro_shards.py scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_SAMPLE_DIR)/maps" || { printf '%s\n' "missing prepared MAPS piano CSV or audio under $(MAPS_PIANO_SAMPLE_DIR); run make prepare-maps-piano-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) analyzer_maps_piano_cached $(MAKE) $(MAPS_PIANO_TEST_MAKE_JOBS) $(addprefix measure-maps-piano-cached-shard-,$(MAPS_PIANO_SHARD_INDEXES))
	$(RUN_WITH_DURATION) check_maps_piano_cached $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_REQUIRED_WINDOWS)" --min-recall-percent 0 --min-precision-percent 0 --min-keyboard-recall-percent 0 --max-contamination-percent 100 --max-false-non-keyboard-percent 100 --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_SHARD_OUTS)

measure-maps-piano-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_samples_shard_$*.err"

$(MAPS_PIANO_ATTRIBUTE_TSV): $(MAPS_PIANO_ATTRIBUTE_PARTS) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(BUILD_DIR)/maps_piano_attributes.lock" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(MAPS_PIANO_TEST_MAKE_JOBS)" $(MAPS_PIANO_ATTRIBUTE_PARTS)

$(BUILD_DIR)/maps_piano_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$*" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_attributes.shard-$*.out"

analyze-maps-piano-attributes: $(MAPS_PIANO_ATTRIBUTE_TSV)
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

# Inspect already generated MAPS traits without entering the preparation graph.
analyze-maps-piano-attributes-cached: scripts/analyze_maps_piano_attributes.py
	@test -s "$(MAPS_PIANO_ATTRIBUTE_TSV)" || { printf '%s\n' "missing cached $(MAPS_PIANO_ATTRIBUTE_TSV)"; exit 2; }
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

summarize-maps-piano-attributes: scripts/analyze_maps_piano_attributes.py
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_ATTRIBUTE_TSV)"

summarize-maps-piano-note-attributes: scripts/analyze_maps_piano_attributes.py
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

.PHONY: inspect-maps-piano-low-miss-rows
inspect-maps-piano-low-miss-rows: scripts/inspect_maps_piano_low_miss_rows.py
	$(PYTHON) scripts/inspect_maps_piano_low_miss_rows.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

prepare-maps-piano-note-samples: scripts/prepare_maps_piano_samples.py download-maps-piano-samples | $(BUILD_DIR)
	MAPS_PIANO_ARCHIVE="$(MAPS_PIANO_ARCHIVE)" MAPS_PIANO_SAMPLE_DIR="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MAPS_PIANO_RECORDING_LIMIT="$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" MAPS_PIANO_MIN_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MAPS_PIANO_KINDS="ISOL" $(PYTHON) scripts/prepare_maps_piano_samples.py --archive "$(MAPS_PIANO_ARCHIVE)" --output "$(MAPS_PIANO_NOTE_SAMPLE_DIR)" --limit "$(MAPS_PIANO_NOTE_RECORDING_LIMIT)" --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --kinds "ISOL"

test-maps-piano-note-samples: test-maps-piano-note-samples-parallel

test-maps-piano-note-samples-serial: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_maps_piano_note_samples env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS="$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS="$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT="$(MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT="$(MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT="$(MAPS_PIANO_NOTE_MAX_CONTAMINATION_PERCENT)" MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT="$(MAPS_PIANO_NOTE_MAX_FALSE_NON_KEYBOARD_PERCENT)" MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 $(BUILD_DIR)/analyzer_maestro

test-maps-piano-note-samples-parallel: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/check_maestro_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_maps_piano_note_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(MAPS_PIANO_NOTE_LOCK_DIR)" -- "$(MAKE)" test-maps-piano-note-samples-parallel-unlocked

test-maps-piano-note-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/check_maestro_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(MAPS_PIANO_NOTE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_maps_piano_note_shards $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" --min-recall-percent "$(MAPS_PIANO_NOTE_MIN_RECALL_PERCENT)" --min-precision-percent "$(MAPS_PIANO_NOTE_MIN_PRECISION_PERCENT)" --min-keyboard-recall-percent "$(MAPS_PIANO_NOTE_MIN_KEYBOARD_RECALL_PERCENT)" --max-contamination-percent "$(MAPS_PIANO_NOTE_MAX_CONTAMINATION_PERCENT)" --max-false-non-keyboard-percent "$(MAPS_PIANO_NOTE_MAX_FALSE_NON_KEYBOARD_PERCENT)" --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_NOTE_SHARD_OUTS)

test-maps-piano-note-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_note_samples_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.err"

# Measure the prepared MAPS isolated-piano fixture without preparing or
# downloading it.  This is intentionally non-gating: the current benchmark
# records its low precision as evidence in the dashboard.
measure-maps-piano-note-cached: $(BUILD_DIR)/analyzer_maestro scripts/check_maestro_shards.py scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maps/isol" || { printf '%s\n' "missing prepared MAPS isolated-piano CSV or audio under $(MAPS_PIANO_NOTE_SAMPLE_DIR); run make prepare-maps-piano-note-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) analyzer_maps_piano_note_cached $(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(addprefix measure-maps-piano-note-cached-shard-,$(MAPS_PIANO_NOTE_SHARD_INDEXES))
	$(RUN_WITH_DURATION) check_maps_piano_note_cached $(PYTHON) scripts/check_maestro_shards.py --min-recordings "$(MAPS_PIANO_NOTE_MIN_RECORDINGS)" --min-windows "$(MAPS_PIANO_NOTE_REQUIRED_WINDOWS)" --min-recall-percent 0 --min-precision-percent 0 --min-keyboard-recall-percent 0 --max-contamination-percent 100 --max-false-non-keyboard-percent 100 --min-chord-recall-percent 0 --min-chord-precision-percent 0 --min-chord-checks 100000 $(MAPS_PIANO_NOTE_SHARD_OUTS)

measure-maps-piano-note-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_maps_piano_note_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.out" 2> "$(BUILD_DIR)/maps_piano_note_samples_shard_$*.err"

# Regenerate diagnostic traits from the already-prepared external MAPS cache.
# This must not prepare or download samples, and remains non-gating.
refresh-maps-piano-note-attributes-cached: $(BUILD_DIR)/analyzer_maestro scripts/merge_tsv_parts.sh scripts/run_with_duration.sh
	@test -s "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maestro-v3.0.0.csv" && test -d "$(MAPS_PIANO_NOTE_SAMPLE_DIR)/maps/isol" || { printf '%s\n' "missing prepared MAPS isolated-piano CSV or audio under $(MAPS_PIANO_NOTE_SAMPLE_DIR); run make prepare-maps-piano-note-samples first"; exit 2; }
	+$(RUN_WITH_DURATION) refresh_maps_piano_note_attributes_cached $(MAKE) $(MAPS_PIANO_NOTE_TEST_MAKE_JOBS) $(addprefix refresh-maps-piano-note-attributes-cached-shard-,$(MAPS_PIANO_NOTE_SHARD_INDEXES))
	$(RUN_WITH_DURATION) merge_maps_piano_note_attributes_cached $(SHELL) scripts/merge_tsv_parts.sh "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)" $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS)

refresh-maps-piano-note-attributes-cached-shard-%: FORCE $(BUILD_DIR)/analyzer_maestro scripts/run_with_duration.sh | $(BUILD_DIR)
	@shard="$*"; $(RUN_WITH_DURATION) refresh_maps_piano_note_attributes_cached_shard_$* env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$$shard" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.tsv" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.out" 2> "$(BUILD_DIR)/maps_piano_note_attributes.shard-$$shard.err"

$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV): $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS) scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	$(SHELL) scripts/run_with_lock.sh "$(BUILD_DIR)/maps_piano_note_attributes.lock" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(MAPS_PIANO_NOTE_TEST_MAKE_JOBS)" $(MAPS_PIANO_NOTE_ATTRIBUTE_PARTS)

$(BUILD_DIR)/maps_piano_note_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_maestro prepare-maps-piano-note-samples | $(BUILD_DIR)
	env MUSIC_ANALYZER_MAESTRO_ROOT="$(MAPS_PIANO_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MAESTRO_MAX_WINDOWS_PER_RECORDING="$(MAPS_PIANO_NOTE_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MAESTRO_MIN_ACTIVE_NOTES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_PITCH_CLASSES_PER_WINDOW=1 MUSIC_ANALYZER_MAESTRO_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT=0 MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT=100 MUSIC_ANALYZER_MAESTRO_MIN_CHORD_CHECKS=100000 MUSIC_ANALYZER_MAESTRO_SHARD_COUNT="$(MAPS_PIANO_NOTE_SHARDS)" MUSIC_ANALYZER_MAESTRO_SHARD_INDEX="$*" MUSIC_ANALYZER_MAESTRO_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_maestro > "$(BUILD_DIR)/maps_piano_note_attributes.shard-$*.out"

analyze-maps-piano-note-attributes: $(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

# Inspect already generated isolated-piano traits without preparing or downloading.
analyze-maps-piano-note-attributes-cached: scripts/analyze_maps_piano_attributes.py
	@test -s "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)" || { printf '%s\n' "missing cached $(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"; exit 2; }
	$(PYTHON) scripts/analyze_maps_piano_attributes.py "$(MAPS_PIANO_NOTE_ATTRIBUTE_TSV)"

download-bach10-mf0-synth-samples: $(BACH10_MF0_SYNTH_ARCHIVE)

$(BACH10_MF0_SYNTH_ARCHIVE): scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	mkdir -p "$(BACH10_MF0_SYNTH_SOURCE_DIR)"
	$(SHELL) scripts/download_musicnet_archive.sh "$(BACH10_MF0_SYNTH_ARCHIVE)" "$(BACH10_MF0_SYNTH_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

prepare-bach10-mf0-synth-samples: scripts/prepare_bach10_mf0_synth_musicnet_fixture.py | $(BUILD_DIR)
	+if [ -z "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" ]; then $(MAKE) download-bach10-mf0-synth-samples; fi
	BACH10_MF0_SYNTH_ARCHIVE="$(BACH10_MF0_SYNTH_ARCHIVE)" BACH10_MF0_SYNTH_SOURCE_ROOT="$(BACH10_MF0_SYNTH_SOURCE_ROOT)" BACH10_MF0_SYNTH_SAMPLE_DIR="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" BACH10_MF0_SYNTH_RECORDING_LIMIT="$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" BACH10_MF0_SYNTH_MIN_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" $(PYTHON) scripts/prepare_bach10_mf0_synth_musicnet_fixture.py --archive "$(BACH10_MF0_SYNTH_ARCHIVE)" --source-root "$(BACH10_MF0_SYNTH_SOURCE_ROOT)" --output "$(BACH10_MF0_SYNTH_SAMPLE_DIR)" --limit "$(BACH10_MF0_SYNTH_RECORDING_LIMIT)" --min-recordings "$(BACH10_MF0_SYNTH_MIN_RECORDINGS)"

test-bach10-mf0-synth-samples: test-bach10-mf0-synth-samples-parallel

test-bach10-mf0-synth-samples-serial: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT)" $(BUILD_DIR)/analyzer_musicnet

test-bach10-mf0-synth-samples-parallel: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/check_musicnet_shards.py scripts/run_with_lock.sh scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples_parallel $(SHELL) scripts/run_with_lock.sh "$(BACH10_MF0_SYNTH_LOCK_DIR)" -- "$(MAKE)" test-bach10-mf0-synth-samples-parallel-unlocked

test-bach10-mf0-synth-samples-parallel-unlocked: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/check_musicnet_shards.py scripts/run_with_duration.sh
	+$(MAKE) $(BACH10_MF0_SYNTH_TEST_MAKE_JOBS) $(BACH10_MF0_SYNTH_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_bach10_mf0_synth_shards $(PYTHON) scripts/check_musicnet_shards.py --min-recordings "$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" --min-windows "$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" --min-recall-percent "$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" --min-precision-percent "$(BACH10_MF0_SYNTH_MIN_PRECISION_PERCENT)" --min-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_CHORD_RECALL_PERCENT)" --min-simple-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_SIMPLE_CHORD_RECALL_PERCENT)" --min-global-chord-precision-percent "$(BACH10_MF0_SYNTH_MIN_CHORD_PRECISION_PERCENT)" --min-global-simple-chord-precision-percent "$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT)" --min-global-simple-chord-recall-percent "$(BACH10_MF0_SYNTH_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT)" --min-chord-checks 5 $(BACH10_MF0_SYNTH_SHARD_OUTS)

test-bach10-mf0-synth-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	@shard="$*"; $(RUN_WITH_DURATION) analyzer_bach10_mf0_synth_samples_shard_$* env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT="$(BACH10_MF0_SYNTH_MIN_RECALL_PERCENT)" MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_SHARD_COUNT="$(BACH10_MF0_SYNTH_SHARDS)" MUSIC_ANALYZER_MUSICNET_SHARD_INDEX="$$shard" $(BUILD_DIR)/analyzer_musicnet > "$(BUILD_DIR)/bach10_mf0_synth_samples_shard_$*.out" 2> "$(BUILD_DIR)/bach10_mf0_synth_samples_shard_$*.err"

analyze-bach10-mf0-synth-chord-misses: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyze_bach10_mf0_synth_chord_misses env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 MUSIC_ANALYZER_MUSICNET_VERBOSE_CHORD_MISSES=1 $(BUILD_DIR)/analyzer_musicnet

analyze-bach10-mf0-synth-pitch-misses: $(BUILD_DIR)/analyzer_musicnet prepare-bach10-mf0-synth-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyze_bach10_mf0_synth_pitch_misses env MUSIC_ANALYZER_MUSICNET_ROOT="$(BACH10_MF0_SYNTH_SAMPLE_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$(BACH10_MF0_SYNTH_MIN_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$(BACH10_MF0_SYNTH_REQUIRED_WINDOWS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$(BACH10_MF0_SYNTH_MAX_WINDOWS_PER_RECORDING)" MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_NOTES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_ACTIVE_INSTRUMENTS_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_PITCH_CLASSES_PER_WINDOW=3 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 MUSIC_ANALYZER_MUSICNET_VERBOSE_PITCH_MISSES=1 $(BUILD_DIR)/analyzer_musicnet

prepare-instrument-samples: scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	INSTRUMENT_SAMPLE_BUILD_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" INSTRUMENT_SAMPLE_SOURCE_DIR="$(INSTRUMENT_SAMPLE_SOURCE_DIR)" INSTRUMENT_SAMPLE_SOUNDFONT="$(INSTRUMENT_SAMPLE_SOUNDFONT)" INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE="$(INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE)" INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY="$(INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY)" INSTRUMENT_SAMPLE_DRUM_KITS="$(INSTRUMENT_SAMPLE_DRUM_KITS)" INSTRUMENT_SAMPLE_TARGET_PER_FAMILY="$(INSTRUMENT_SAMPLE_TARGET_PER_FAMILY)" INSTRUMENT_SAMPLE_JOBS="$(INSTRUMENT_SAMPLE_JOBS)" $(PYTHON) scripts/prepare_instrument_samples.py --output-root "$(INSTRUMENT_SAMPLE_BUILD_ROOT)" --download-dir "$(INSTRUMENT_SAMPLE_SOURCE_DIR)"

$(INSTRUMENT_SAMPLE_MANIFEST_STAMP): scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	+$(MAKE) prepare-instrument-samples
	@touch "$@"

test-instrument-samples: test-instrument-samples-parallel

test-instrument-samples-serial: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" $(BUILD_DIR)/analyzer_instrument_samples

.PHONY: test-instrument-samples-hihat
test-instrument-samples-hihat: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples_hihat env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_FILTER_PATH="hihat" $(BUILD_DIR)/analyzer_instrument_samples

test-instrument-samples-parallel: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_instrument_samples_parallel $(MAKE) $(INSTRUMENT_SAMPLE_TEST_MAKE_JOBS) $(INSTRUMENT_SAMPLE_SHARD_TARGETS)

test-instrument-samples-shard-%: FORCE $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_instrument_samples_shard_$* env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT="$(INSTRUMENT_SAMPLE_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_instrument_samples

$(BUILD_DIR)/instrument_sample_attributes.tsv: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/prepare_instrument_samples.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+$(SHELL) scripts/run_with_lock.sh "$(INSTRUMENT_SAMPLE_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(INSTRUMENT_SAMPLE_ATTRIBUTE_MAKE_JOBS)" $(INSTRUMENT_SAMPLE_ATTRIBUTE_PARTS)

$(BUILD_DIR)/instrument_sample_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_instrument_samples $(INSTRUMENT_SAMPLE_MANIFEST_STAMP) scripts/prepare_instrument_samples.py | $(BUILD_DIR)
	-env MUSIC_ANALYZER_INSTRUMENT_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT="$(INSTRUMENT_SAMPLE_BUILD_ROOT)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT="$(INSTRUMENT_SAMPLE_SHARDS)" MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX="$*" MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV="$@" $(BUILD_DIR)/analyzer_instrument_samples > "$(BUILD_DIR)/instrument_sample_attributes.shard-$*.out"

analyze-instrument-sample-attributes: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/summarize_instrument_sample_attributes.py
	$(PYTHON) scripts/summarize_instrument_sample_attributes.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSTRUMENT_ATTRIBUTE_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/instrument_sample_attributes.tsv"

inspect-instrument-sample-owner-buckets: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/inspect_instrument_sample_owner_buckets.py
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(INSPECT_INSTRUMENT_OWNER_ARGS)

find-instrument-owner-patterns: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py
	$(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(PATTERN_ARGS)

find-instrument-status-patterns: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py
	$(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(if $(PATTERN_ARGS),--status-top-buckets 0 $(PATTERN_ARGS),$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS))

filter-instrument-attribute-rows: $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/filter_instrument_attribute_rows.py
	$(PYTHON) scripts/filter_instrument_attribute_rows.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" $(FILTER_ATTRIBUTE_ARGS)

filter-drum-primary-attribute-rows: $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(FILTER_DRUM_ATTRIBUTE_ARGS)

filter-hf-drum-primary-attribute-rows: $(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS) scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(HF_DRUM_KIT_PRIMARY_ATTRIBUTE_ROWS)" $(FILTER_DRUM_ATTRIBUTE_ARGS)

filter-drum-full-attribute-rows: $(BUILD_DIR)/drum_full_attribute_rows.tsv scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(FILTER_DRUM_ATTRIBUTE_ARGS)

filter-drum-full-exact-attribute-rows: $(DRUM_FULL_EXACT_ATTRIBUTE_ROWS) scripts/filter_drum_attribute_rows.py
	$(PYTHON) scripts/filter_drum_attribute_rows.py "$(DRUM_FULL_EXACT_ATTRIBUTE_ROWS)" $(FILTER_DRUM_ATTRIBUTE_ARGS)

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

$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/inspect_instrument_sample_owner_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_instrument_sample_owner_buckets.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --dump-rows > "$@"

$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows > "$@"

$(REAL_NOTE_MISS_ATTRIBUTE_ROWS): $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --dump-rows --misses-only > "$@"

$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS): $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows > "$@"

$(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS): $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	$(PYTHON) scripts/inspect_guitarset_attribute_buckets.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" --dump-rows --misses-only > "$@"

measure-analyzer-attribute-rows:
	+$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) analyze-instrument-sample-attributes analyze-real-note-attributes analyze-guitar-chord-mix-attributes analyze-drum-primary-attribute-rows
	+$(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_ROW_DUMPS)
	@printf '%s\n' "attribute row dumps:"
	@printf '%s\n' "  $(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(REAL_NOTE_MISS_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(GUITAR_CHORD_MISS_ATTRIBUTE_ROWS)"
	@printf '%s\n' "  $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv"
	@if [ -f "$(BUILD_DIR)/drum_full_attribute_rows.tsv" ]; then printf '%s\n' "  $(BUILD_DIR)/drum_full_attribute_rows.tsv"; else printf '%s\n' "  full drum rows skipped; run make measure-analyzer-attribute-rows-full for exhaustive drum rows"; fi

measure-analyzer-attribute-rows-full: measure-analyzer-attribute-rows analyze-drum-rule-grid $(BUILD_DIR)/drum_full_attribute_rows.tsv
	@printf '%s\n' "full drum attribute row dump:"
	@printf '%s\n' "  $(BUILD_DIR)/drum_full_attribute_rows.tsv"

require-cached-analyzer-attribute-rows:
	@missing=0; for rows in $(CACHED_ANALYZER_PATTERN_INPUT_PATHS); do if [ ! -f "$$rows" ]; then printf '%s\n' "missing cached analyzer pattern input: $$rows"; missing=1; fi; done; if [ "$$missing" -ne 0 ]; then printf '%s\n' "run make measure-analyzer-attribute-rows to regenerate cached analyzer rows"; exit 2; fi

refresh-analyzer-detected-attribute-rows: scripts/refresh_analyzer_detected_attribute_rows.py
	$(PYTHON) scripts/refresh_analyzer_detected_attribute_rows.py --build-dir "$(BUILD_DIR)" --python "$(PYTHON)" --jobs "$(REFRESH_ANALYZER_ATTRIBUTE_JOBS)"

print-analyzer-detected-attributes: $(MEASURE_ANALYZER_ROW_DUMPS) $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_DEPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_detected_attributes $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) $(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)

print-analyzer-detected-attributes-cached: scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_detected_attributes_cached $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) $(PRINT_ANALYZER_DETECTED_ATTRIBUTES_ARGS)

measure-analyzer-detected-attributes: measure-analyzer-attribute-rows
	+$(MAKE) print-analyzer-detected-attributes

measure-analyzer-detected-attributes-full: measure-analyzer-attribute-rows-full
	+$(MAKE) print-analyzer-detected-attributes

$(MEASURE_ANALYZER_PATTERN_DETECTED_REPORT): FORCE $(MEASURE_ANALYZER_ROW_DUMPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/print_analyzer_detected_attributes.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; $(MAKE) print-analyzer-detected-attributes > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_SUMMARY_REPORT): FORCE $(MEASURE_ANALYZER_ROW_DUMPS) $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/report_analyzer_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/report_analyzer_attribute_patterns.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(PATTERN_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_OWNER_REPORT): FORCE $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument owner pattern candidates:"; $(MAKE) find-instrument-owner-patterns PATTERN_ARGS="$(MEASURE_INSTRUMENT_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_INSTRUMENT_STATUS_REPORT): FORCE $(BUILD_DIR)/instrument_sample_attributes.tsv scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument final-status pattern candidates:"; $(MAKE) find-instrument-status-patterns PATTERN_ARGS="$(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_SUMMARY_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix coverage summary:"; $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(MEASURE_REAL_NOTE_SUMMARY_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix pattern candidates:"; $(MAKE) find-real-note-attribute-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OWNERSHIP_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note ownership-miss pattern candidates:"; $(MAKE) find-real-note-ownership-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note octave-displacement pattern candidates:"; $(MAKE) find-real-note-octave-displacement-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note strongest-row confusion pattern candidates:"; $(MAKE) find-real-note-row-confusion-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note visual-row confusion pattern candidates:"; $(MAKE) find-real-note-visual-row-confusion-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak expected-row pattern candidates:"; $(MAKE) find-real-note-weak-expected-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT): FORCE $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak visual expected-row pattern candidates:"; $(MAKE) find-real-note-weak-visual-expected-patterns PATTERN_ARGS="$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord pattern candidates:"; $(MAKE) find-guitar-chord-mix-attribute-patterns PATTERN_ARGS="$(MEASURE_GUITAR_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_PRIMARY_ORDER_REPORT): FORCE $(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS) scripts/analyze_guitar_primary_order.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord primary-order analysis:"; $(MAKE) analyze-guitar-chord-primary-order PRIMARY_ORDER_ARGS="$(PRIMARY_ORDER_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_RECOVERY_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_recovery.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord recovery threshold simulation:"; $(MAKE) analyze-guitar-chord-mix-recovery RECOVERY_ARGS="$(RECOVERY_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_GUITAR_CHORD_EXTRA_REPORT): FORCE $(BUILD_DIR)/guitar_chord_mix_attributes.tsv scripts/analyze_guitar_chord_extra_components.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord extra component analysis:"; $(MAKE) analyze-guitar-chord-mix-extra-components EXTRA_COMPONENT_ARGS="$(EXTRA_COMPONENT_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_PRIMARY_REPORT): FORCE $(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum primary pattern candidates:"; $(MAKE) find-drum-primary-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/summarize_drum_gate_matrix.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum spread exact gate matrix:"; if [ -d "$(DRUM_SAMPLE_SOURCE_DIR)" ]; then $(MAKE) analyze-drum-spread-gate-matrix; elif [ -f "$(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)" ]; then printf '%s\n' "skipped regeneration; using existing $(DRUM_SPREAD_EXACT_ATTRIBUTE_ROWS)"; else printf '%s\n' "skipped; missing $(DRUM_SAMPLE_SOURCE_DIR)"; fi; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_PROTECTED_DRUM_PRIMARY_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) $(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP) scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "protected drum primary pattern candidates:"; $(MAKE) find-protected-drum-primary-attribute-patterns PATTERN_ARGS="$(MEASURE_PROTECTED_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_ACTIVE_FALSE_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) $(MEASURE_ANALYZER_PATTERN_DRUM_PROTECTED_ROWS_STAMP) scripts/summarize_drum_active_false_rows.py scripts/find_drum_active_false_patterns.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum active false-row summary:"; $(MAKE) analyze-drum-active-false-rows; printf '%s\n' ""; printf '%s\n' "drum active false pattern candidates:"; $(MAKE) find-drum-active-false-patterns $(if $(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS),DRUM_ACTIVE_EXTRA_PROTECTED_ROWS="$(MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS)") PATTERN_ARGS="$(MEASURE_DRUM_ACTIVE_FALSE_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_EXACT_REPORT): FORCE $(MEASURE_ANALYZER_PATTERN_DRUM_SPREAD_MATRIX_REPORT) scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum spread exact pattern candidates:"; $(MAKE) find-drum-spread-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_SKIP_REPORT): FORCE | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { if [ "$(REPORT_FULL_DRUM_SKIP)" = "1" ]; then printf '%s\n' ""; printf '%s\n' "protected drum full-row pattern candidates:"; printf '%s\n' "skipped; run make measure-analyzer-patterns-full for exhaustive protected full-drum rows"; fi; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "protected drum full-row pattern candidates:"; $(MAKE) find-protected-drum-full-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_FULL_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_PATTERN_FULL_DRUM_EXACT_REPORT): FORCE $(BUILD_DIR)/analyzer_drum_samples scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	+@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum full exact pattern candidates:"; $(MAKE) find-drum-full-exact-attribute-patterns PATTERN_ARGS="$(MEASURE_DRUM_FULL_PATTERN_ARGS)"; } > "$$tmp" && mv "$$tmp" "$@"

measure-analyzer-pattern-report-sections: $(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)
	@true

report-analyzer-patterns-from-rows: scripts/run_with_duration.sh scripts/report_analyzer_attribute_patterns.py scripts/print_analyzer_detected_attributes.py
	+$(RUN_WITH_DURATION) analyzer_pattern_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) measure-analyzer-pattern-report-sections
	@cat $(MEASURE_ANALYZER_PATTERN_SECTION_OUTPUTS)

$(MEASURE_ANALYZER_CACHED_PATTERN_DETECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/print_analyzer_detected_attributes.py scripts/run_with_duration.sh | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(RUN_WITH_DURATION) analyzer_detected_attributes_cached $(PYTHON) scripts/print_analyzer_detected_attributes.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum-primary "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --drum-full "$(BUILD_DIR)/drum_full_attribute_rows.tsv" $(REAL_NOTE_SAMPLE_ATTRIBUTE_EXTRA_ARGS) $(ATTRIBUTE_ROW_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_SUMMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/report_analyzer_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/report_analyzer_attribute_patterns.py --instrument "$(INSTRUMENT_DETECTED_ATTRIBUTE_ROWS)" --real-note "$(REAL_NOTE_DETECTED_ATTRIBUTE_ROWS)" --guitar-chord "$(GUITAR_CHORD_DETECTED_ATTRIBUTE_ROWS)" --drum "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" $(PATTERN_REPORT_ARGS) > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_OWNER_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument owner pattern candidates:"; $(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(MEASURE_INSTRUMENT_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_INSTRUMENT_STATUS_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_instrument_owner_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "generated instrument final-status pattern candidates:"; $(PYTHON) scripts/find_instrument_owner_patterns.py "$(BUILD_DIR)/instrument_sample_attributes.tsv" --jobs "$(INSTRUMENT_PATTERN_JOBS)" $(MEASURE_INSTRUMENT_STATUS_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_SUMMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/summarize_real_note_attributes.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix coverage summary:"; $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(MEASURE_REAL_NOTE_SUMMARY_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note full-mix pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OWNERSHIP_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note ownership-miss pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_OCTAVE_DISPLACEMENT_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note octave-displacement pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status octave_displacement --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_ROW_CONFUSION_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note strongest-row confusion pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_ROW_CONFUSION_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_VISUAL_ROW_CONFUSION_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note visual-row confusion pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_EXPECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak expected-row pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status weak_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_REAL_NOTE_WEAK_VISUAL_EXPECTED_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "real-note weak visual expected-row pattern candidates:"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) --bucket-status weak_visual_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_GUITAR_CHORD_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_guitarset_attribute_patterns.py scripts/inspect_guitarset_attribute_buckets.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "guitar chord pattern candidates:"; $(PYTHON) scripts/find_guitarset_attribute_patterns.py "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" $(MEASURE_GUITAR_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

$(MEASURE_ANALYZER_CACHED_PATTERN_DRUM_PRIMARY_REPORT): FORCE require-cached-analyzer-attribute-rows scripts/find_drum_attribute_patterns.py scripts/analyze_drum_primary_debug.py | $(BUILD_DIR)
	@tmp="$@.$$$$.tmp"; { printf '%s\n' ""; printf '%s\n' "drum primary pattern candidates:"; $(PYTHON) scripts/find_drum_attribute_patterns.py "$(BUILD_DIR)/drum_primary_miss_attribute_rows.tsv" --jobs "$(DRUM_PATTERN_JOBS)" $(MEASURE_DRUM_PATTERN_ARGS); } > "$$tmp" && mv "$$tmp" "$@"

report-analyzer-patterns-from-cached-rows: require-cached-analyzer-attribute-rows scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) analyzer_cached_pattern_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS)
	@cat $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS)

$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY): $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS) scripts/summarize_detector_route_report.py | $(BUILD_DIR)
	@tmp_report="$@.$$$$.report"; tmp="$@.$$$$.tmp"; cat $(MEASURE_ANALYZER_CACHED_PATTERN_SECTION_OUTPUTS) > "$$tmp_report" && $(PYTHON) scripts/summarize_detector_route_report.py "$$tmp_report" > "$$tmp"; status="$$?"; rm -f "$$tmp_report"; if [ "$$status" -eq 0 ]; then mv "$$tmp" "$@"; else rm -f "$$tmp"; exit "$$status"; fi

measure-analyzer-patterns-cached-summary: $(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY) scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py
	@cat "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"
	+@$(MAKE) measure-analyzer-patterns-cached-coverage

measure-analyzer-patterns-cached-coverage: scripts/inspect_detector_coverage_candidates.py scripts/inspect_real_note_candidate_rows.py | $(BUILD_DIR)
	+@if [ ! -f "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" ]; then $(MAKE) "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)"; fi
	@tmp="$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY).$$$$.tmp"; $(PYTHON) scripts/inspect_detector_coverage_candidates.py "$(MEASURE_ANALYZER_CACHED_PATTERN_CANDIDATE_SUMMARY)" $(DETECTOR_COVERAGE_SUMMARY_ARGS) $(DETECTOR_COVERAGE_CANDIDATE_ROW_PATHS) > "$$tmp" && mv "$$tmp" "$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY)"
	@cat "$(MEASURE_ANALYZER_CACHED_PATTERN_COVERAGE_SUMMARY)"

report-analyzer-patterns-from-rows-full:
	+$(MAKE) report-analyzer-patterns-from-rows REPORT_FULL_DRUM_SKIP=0 MEASURE_DRUM_ACTIVE_EXTRA_PROTECTED_ROWS="$(MEASURE_DRUM_ACTIVE_FULL_EXTRA_PROTECTED_ROWS)"
	+$(RUN_WITH_DURATION) analyzer_pattern_full_report_sections $(MAKE) $(MEASURE_ANALYZER_MAKE_JOBS) $(MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS)
	@cat $(MEASURE_ANALYZER_PATTERN_FULL_SECTION_OUTPUTS)

measure-analyzer-patterns: measure-analyzer-attribute-rows
	+$(MAKE) report-analyzer-patterns-from-rows

measure-analyzer-patterns-cached: require-cached-analyzer-attribute-rows
	+$(MAKE) report-analyzer-patterns-from-cached-rows

measure-analyzer-patterns-full: measure-analyzer-attribute-rows analyze-drum-full-gate-matrix-parallel analyze-drum-full-merged-expected-attribute-rows analyze-drum-tom-bleed-caps-cached
	+$(MAKE) report-analyzer-patterns-from-rows-full

measure-analyzer-pattern-report: | $(BUILD_DIR)
	+$(MAKE) -s measure-analyzer-patterns | tee "$(MEASURE_ANALYZER_REPORT)"
	@printf '%s\n' "measurement report: $(MEASURE_ANALYZER_REPORT)"

download-real-note-samples: FORCE | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if [ -s "$(NSYNTH_SAMPLE_ARCHIVE)" ] && ! $(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_ARCHIVE).corrupt"; fi
	@if [ ! -s "$(NSYNTH_SAMPLE_ARCHIVE)" ]; then curl -fL -C - -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	@$(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null

$(NSYNTH_SAMPLE_ARCHIVE): | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if [ ! -s "$(NSYNTH_SAMPLE_ARCHIVE)" ]; then curl -fL -C - -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	@$(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null

$(NSYNTH_SAMPLE_ROOT)/examples.json: $(NSYNTH_SAMPLE_ARCHIVE) | $(BUILD_DIR)
	mkdir -p "$(REAL_SAMPLE_SOURCE_DIR)"
	@if ! $(TAR) -tzf "$(NSYNTH_SAMPLE_ARCHIVE)" >/dev/null 2>&1; then mv -f "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_ARCHIVE).corrupt"; curl -fL -o "$(NSYNTH_SAMPLE_ARCHIVE)" "$(NSYNTH_SAMPLE_URL)"; fi
	$(TAR) -xzf "$(NSYNTH_SAMPLE_ARCHIVE)" -C "$(REAL_SAMPLE_SOURCE_DIR)"
	touch "$@"

prepare-real-note-samples: scripts/prepare_nsynth_samples.py $(NSYNTH_SAMPLE_ROOT)/examples.json | $(BUILD_DIR)
	NSYNTH_SAMPLE_ROOT="$(NSYNTH_SAMPLE_ROOT)" REAL_NOTE_SAMPLE_DIR="$(REAL_NOTE_SAMPLE_DIR)" REAL_NOTE_SAMPLE_LIMIT="$(REAL_NOTE_SAMPLE_LIMIT)" $(PYTHON) scripts/prepare_nsynth_samples.py --nsynth-root "$(NSYNTH_SAMPLE_ROOT)" --output "$(REAL_NOTE_SAMPLE_DIR)" --limit "$(REAL_NOTE_SAMPLE_LIMIT)"

test-real-note-sample-shards: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_sample_shards.py
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_locked $(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_SAMPLE_LOCK_DIR)" -- $(RUN_REAL_NOTE_SAMPLE_SHARDS_UNLOCKED)

test-real-note-sample-shards-unlocked: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_parallel $(MAKE) $(REAL_NOTE_SAMPLE_TEST_MAKE_JOBS) $(REAL_NOTE_SAMPLE_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_shards $(PYTHON) scripts/check_real_note_sample_shards.py --min-bass "$(REAL_NOTE_SAMPLE_MIN_BASS)" --min-guitar "$(REAL_NOTE_SAMPLE_MIN_GUITAR)" --min-piano "$(REAL_NOTE_SAMPLE_MIN_PIANO)" --min-vocals "$(REAL_NOTE_SAMPLE_MIN_VOCALS)" --min-other "$(REAL_NOTE_SAMPLE_MIN_OTHER)" $(REAL_NOTE_SAMPLE_HIT_PERCENT_ARGS) --max-failures "$(REAL_NOTE_SAMPLE_MAX_FAILURES)" $(REAL_NOTE_SAMPLE_SHARD_OUTS)

test-real-note-sample-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples_$(REAL_NOTE_SAMPLE_TAG)_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(REAL_NOTE_SAMPLE_REQUIRED_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_ROOT)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES="$(REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES)" MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES="$(REAL_NOTE_SAMPLE_MAX_FAILURE_LINES)" MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_SAMPLE_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.out" 2> "$(BUILD_DIR)/real_note_$(REAL_NOTE_SAMPLE_TAG)_shard_$*.err"

test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_TAG := nsynth
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_ROOT := $(REAL_NOTE_SAMPLE_DIR)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS := $(REAL_NOTE_MIN_BASS)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR := $(REAL_NOTE_MIN_GUITAR)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO := $(REAL_NOTE_MIN_PIANO)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS := $(REAL_NOTE_MIN_VOCALS)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER := $(REAL_NOTE_MIN_OTHER)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT := $(REAL_NOTE_MIN_BASS_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT := $(REAL_NOTE_MIN_GUITAR_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT := $(REAL_NOTE_MIN_PIANO_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT := $(REAL_NOTE_MIN_VOCALS_HIT_PERCENT)
test-real-note-samples test-real-note-samples-parallel: REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT := $(REAL_NOTE_MIN_OTHER_HIT_PERCENT)
test-real-note-samples: test-real-note-samples-parallel

test-real-note-samples-parallel: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh scripts/check_real_note_sample_shards.py
	+$(RUN_REAL_NOTE_SAMPLE_SHARDS)

test-real-note-samples-full-mix: test-real-note-samples-full-mix-parallel

test-real-note-samples-full-mix-serial: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" $(REAL_NOTE_FULL_MIX_GATE_ENV) $(BUILD_DIR)/analyzer_real_note_samples

test-real-note-samples-full-mix-parallel: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/run_with_lock.sh scripts/check_real_note_full_mix_shards.py
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_parallel $(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_FULL_MIX_LOCK_DIR)" -- "$(MAKE)" REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX="$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)" test-real-note-samples-full-mix-parallel-unlocked

test-real-note-samples-full-mix-parallel-unlocked: $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh scripts/check_real_note_full_mix_shards.py
	+$(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX="$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)" $(REAL_NOTE_FULL_MIX_SHARD_TARGETS)
	$(RUN_WITH_DURATION) check_real_note_full_mix_shards $(PYTHON) scripts/check_real_note_full_mix_shards.py --min-any-hit-percent "$(REAL_NOTE_FULL_MIX_MIN_ANY_HIT_PERCENT)" --min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT)" --min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_FIRST_ROW_PERCENT)" --min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT)" --bass-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT)" --guitar-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT)" --piano-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT)" --vocals-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT)" --other-min-expected-row-percent "$(REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT)" --bass-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_BASS_FIRST_ROW_PERCENT)" --guitar-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_FIRST_ROW_PERCENT)" --piano-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_FIRST_ROW_PERCENT)" --vocals-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_FIRST_ROW_PERCENT)" --other-min-first-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_FIRST_ROW_PERCENT)" --bass-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_BASS_VISUAL_ROW_PERCENT)" --guitar-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT)" --piano-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_PIANO_VISUAL_ROW_PERCENT)" --vocals-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_VOCALS_VISUAL_ROW_PERCENT)" --other-min-visual-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT)" --max-drum-active-percent "$(REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT)" $(REAL_NOTE_FULL_MIX_SOURCE_ROUTE_LIMIT_ARGS) $(REAL_NOTE_FULL_MIX_SHARD_OUTS)

test-real-note-samples-full-mix-detector-parallel: REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX := detector_real_note_full_mix_shard
test-real-note-samples-full-mix-detector-parallel: test-real-note-samples-full-mix-parallel

test-real-note-samples-full-mix-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	$(RUN_WITH_DURATION) analyzer_real_note_samples_full_mix_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 $(REAL_NOTE_FULL_MIX_SHARD_GATE_ENV) $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.out" 2> "$(BUILD_DIR)/$(REAL_NOTE_FULL_MIX_SHARD_OUTPUT_PREFIX)_$*.err"

analyze-real-note-misses: analyze-real-note-misses-parallel

analyze-real-note-misses-serial: $(BUILD_DIR)/analyzer_real_note_samples prepare-real-note-samples scripts/analyze_real_note_misses.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS="$(REAL_NOTE_MIN_BASS)" MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR="$(REAL_NOTE_MIN_GUITAR)" MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO="$(REAL_NOTE_MIN_PIANO)" MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS="$(REAL_NOTE_MIN_VOCALS)" MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER="$(REAL_NOTE_MIN_OTHER)" $(REAL_NOTE_FULL_MIX_GATE_ENV) MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_verbose.out" 2> "$(BUILD_DIR)/real_note_full_mix_verbose.err"
	$(PYTHON) scripts/analyze_real_note_misses.py "$(BUILD_DIR)/real_note_full_mix_verbose.err"

analyze-real-note-misses-parallel: $(BUILD_DIR)/analyzer_real_note_samples scripts/analyze_real_note_misses.py scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose_parallel $(MAKE) $(REAL_NOTE_FULL_MIX_TEST_MAKE_JOBS) $(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_TARGETS)
	$(PYTHON) scripts/analyze_real_note_misses.py $(REAL_NOTE_FULL_MIX_VERBOSE_SHARD_ERRS)

analyze-real-note-misses-shard-%: FORCE $(BUILD_DIR)/analyzer_real_note_samples scripts/run_with_duration.sh
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	$(RUN_WITH_DURATION) analyzer_real_note_full_mix_verbose_shard_$* env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURE_LINES=120 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_verbose_shard_$*.out" 2> "$(BUILD_DIR)/real_note_full_mix_verbose_shard_$*.err"

$(BUILD_DIR)/real_note_full_mix_attributes.tsv: $(BUILD_DIR)/analyzer_real_note_samples scripts/prepare_nsynth_samples.py scripts/build_sharded_tsv.sh scripts/run_with_lock.sh | $(BUILD_DIR)
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	+$(SHELL) scripts/run_with_lock.sh "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_LOCK_DIR)" -- "$(SHELL)" scripts/build_sharded_tsv.sh "$@" "$(MAKE)" "$(REAL_NOTE_FULL_MIX_ATTRIBUTE_MAKE_JOBS)" $(REAL_NOTE_FULL_MIX_ATTRIBUTE_PARTS)

$(BUILD_DIR)/real_note_full_mix_attributes.shard-%.tsv: $(BUILD_DIR)/analyzer_real_note_samples scripts/prepare_nsynth_samples.py | $(BUILD_DIR)
	+@if [ ! -f "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ] || [ "scripts/prepare_nsynth_samples.py" -nt "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" ]; then $(MAKE) prepare-real-note-samples; fi
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SHARD_COUNT="$(REAL_NOTE_FULL_MIX_SHARDS)" MUSIC_ANALYZER_REAL_NOTE_SHARD_INDEX="$*" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$@" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 $(BUILD_DIR)/analyzer_real_note_samples > "$(BUILD_DIR)/real_note_full_mix_attributes.shard-$*.out"

test-real-note-visual-strength: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_visual_strength $(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_FULL_MIX_VISUAL_STRENGTH_ARGS)

analyze-real-note-attributes: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/summarize_real_note_attributes.py
	$(PYTHON) scripts/summarize_real_note_attributes.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)
	@printf '%s\n' "attribute TSV: $(BUILD_DIR)/real_note_full_mix_attributes.tsv"

update-detection-accuracy-report: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT) $(GUITAR_CHORD_TONE_RECOVERY_AUDIT) $(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT) $(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT) $(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT) $(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT) inspect-urmp-bass-timing inspect-harmonic-product-octave-evidence-cached audit-dominant-seventh-extension audit-global-chord-confidence audit-same-root-guitar-quality evaluate-owner-classifier-loco evaluate-owner-classifier-quality-loco evaluate-drum-primary-loco audit-drum-false-positive-caps audit-mdb-full-mix-false-positive-caps audit-mdb-full-mix-competing-active-contexts audit-drum-false-positive-contexts audit-chord-primary-components audit-independent-piano-exact-chord-fallback audit-piano-chord-confirmation audit-piano-chord-confirm3 audit-piano-chord-tone018 audit-piano-chord-margin060 audit-piano-chord-bassbonus000 inspect-mdb-rim-coverage inspect-fsd50k-rim-metadata inspect-commons-rimshot-candidate measure-pixabay-rimshot-candidate measure-pixabay-rimshot-f-candidate measure-pixabay-rim-shot-candidate audit-beat-this-continuous-interval-gate inspect-high-vocal-octave-evidence-cached scripts/write_detection_accuracy_report.py
	$(PYTHON) scripts/write_detection_accuracy_report.py --input "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(DETECTION_ACCURACY_CHORD_ARGS) $(DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_ARG) $(DETECTION_ACCURACY_URMP_GATE_ARG) $(DETECTION_ACCURACY_BACH10_GATE_ARGS) $(DETECTION_ACCURACY_MUSICNET_GATE_ARG) $(DETECTION_ACCURACY_MAPS_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_NOTE_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_CROSS_CORPUS_CHORD_ARGS) $(DETECTION_ACCURACY_DRUM_GATE_ARG) $(DETECTION_ACCURACY_HF_DRUM_GATE_ARGS) $(DETECTION_ACCURACY_STAR_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_ROUTE_SUMMARY_ARG) $(DETECTION_ACCURACY_GOOD_SOUNDS_FULL_MIX_ARG) $(DETECTION_ACCURACY_IRMAS_LABELLED_ARG) $(DETECTION_ACCURACY_PITCH_SHIFTED_VIOLIN_ARG) $(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_PHILHARMONIA_FULL_ARG) $(DETECTION_ACCURACY_IOWA_ORCHESTRA_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_WIND_EXACT_ARG) $(DETECTION_ACCURACY_IOWA_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_IOWA_PIANO_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_SAX_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_ARG) $(DETECTION_ACCURACY_REAL_A2S_TENOR_SCALE_ARG) $(DETECTION_ACCURACY_URMP_SAX_EXACT_ARG) $(DETECTION_ACCURACY_URMP_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_VALIDATION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_INSPECTION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_EXTRACT_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_MANIFEST_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MEASUREMENT_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_ARCHIVE_ARG) $(DETECTION_ACCURACY_KRAISLER_EXTRACT_ARG) $(DETECTION_ACCURACY_KRAISLER_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG) $(DETECTION_ACCURACY_KRAISLER_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_BPM_ARG) $(DETECTION_ACCURACY_BALLROOM_ANNOTATIONS_ARG) $(DETECTION_ACCURACY_EGMD_BPM_ARG) $(DETECTION_ACCURACY_BTT_ARGS) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_INSPECTION_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_PATTERN_REPORT_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_ARCHIVE_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_MIR1K_FULL_MIX_ARG) $(DETECTION_ACCURACY_SCMS_ARCHIVE_ARG) $(DETECTION_ACCURACY_SCMS_INSPECTION_ARG) $(DETECTION_ACCURACY_SCMS_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCAL_EXACT_NOTE_CROSS_CORPUS_ARG) $(DETECTION_ACCURACY_HIGH_VOCAL_OCTAVE_AUDIT_ARG) $(DETECTION_ACCURACY_HIGH_SOPRANO_VOCAL_MIRROR_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_TONE_RECOVERY_AUDIT_ARG) $(DETECTION_ACCURACY_URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_ARG) $(DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG) $(DETECTION_ACCURACY_GLOBAL_CHORD_CONFIDENCE_AUDIT_ARG) $(DETECTION_ACCURACY_SAME_ROOT_GUITAR_QUALITY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITARSET_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_OTHER_DETECTION_ARG) $(DETECTION_ACCURACY_BASIC_PITCH_ONNX_ARGS) --output "$(DETECTION_ACCURACY_REPORT)"

# Choir corpus preparation rewrites shared manifests, so keep this refresh
# serialized even when a caller runs make with -j.
.PHONY: refresh-choir-chord-accuracy
refresh-choir-chord-accuracy:
	+$(MAKE) -B $(BUILD_DIR)/analyzer_musicnet
	+$(MAKE) measure-dagstuhl-choirset
	+$(MAKE) measure-choral-singing-dataset
	+$(MAKE) measure-esmuc-choir-dataset
	+$(MAKE) update-detection-accuracy-report-cached

.PHONY: inspect-satb-missing-pitch-evidence test-inspect-satb-missing-pitch-evidence
inspect-satb-missing-pitch-evidence: scripts/inspect_satb_missing_pitch_evidence.py
	$(PYTHON) scripts/inspect_satb_missing_pitch_evidence.py --input "DCS=$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"

.PHONY: audit-satb-relative-chroma-selector test-audit-satb-relative-chroma-selector
audit-satb-relative-chroma-selector: $(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)
	@cat "$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)"

$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT): scripts/audit_satb_relative_chroma_selector.py | $(BUILD_DIR)
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached SATB selector input: $$path"; exit 2; }; done
	@tmp="$@.$$$$.tmp"; $(PYTHON) scripts/audit_satb_relative_chroma_selector.py --input "DCS=$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" --input "CSD=$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" --input "ESMUC=$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$@"

test-audit-satb-relative-chroma-selector: tests/test_audit_satb_relative_chroma_selector.py scripts/audit_satb_relative_chroma_selector.py
	$(PYTHON) tests/test_audit_satb_relative_chroma_selector.py

test-inspect-satb-missing-pitch-evidence: tests/test_inspect_satb_missing_pitch_evidence.py scripts/inspect_satb_missing_pitch_evidence.py
	$(PYTHON) tests/test_inspect_satb_missing_pitch_evidence.py

.PHONY: update-detection-accuracy-report-cached
update-detection-accuracy-report-cached: DETECTION_ACCURACY_OTHER_DETECTION_ARG += $(DETECTION_ACCURACY_BASIC_PITCH_ONNX_ARGS)
update-detection-accuracy-report-cached: scripts/write_detection_accuracy_report.py
	@test -f "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing build/real_note_full_mix_attributes.tsv; run make update-detection-accuracy-report first"; exit 2; }
	@for path in "$(GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT)" "$(GUITAR_CHORD_TONE_RECOVERY_AUDIT)" "$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)" "$(URMP_BASS_TIMING_AUDIT)" "$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)" "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)" "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)" "$(SAME_ROOT_GUITAR_QUALITY_AUDIT)" "$(OWNER_CLASSIFIER_LOCO_AUDIT)" "$(OWNER_CLASSIFIER_QUALITY_LOCO_AUDIT)" "$(DRUM_PRIMARY_LOCO_AUDIT)" "$(DRUM_FALSE_POSITIVE_CAP_AUDIT)" "$(MDB_FULL_MIX_FALSE_POSITIVE_CAP_AUDIT)" "$(MDB_FULL_MIX_COMPETING_ACTIVE_CONTEXT_AUDIT)" "$(DRUM_FALSE_POSITIVE_CONTEXT_AUDIT)" "$(CHORD_PRIMARY_COMPONENT_AUDIT)" "$(INDEPENDENT_PIANO_EXACT_CHORD_FALLBACK_AUDIT)" "$(PIANO_CHORD_CONFIRMATION_AUDIT)" "$(PIANO_CHORD_CONFIRM3_AUDIT)" "$(PIANO_CHORD_TONE018_AUDIT)" "$(PIANO_CHORD_MARGIN060_AUDIT)" "$(PIANO_CHORD_BASSBONUS000_AUDIT)" "$(MDB_RIM_COVERAGE_AUDIT)" "$(FSD50K_RIM_METADATA_AUDIT)" "$(PIXABAY_RIMSHOT_MEASUREMENT_AUDIT)" "$(PIXABAY_RIMSHOT_F_MEASUREMENT_AUDIT)" "$(PIXABAY_RIM_SHOT_MEASUREMENT_AUDIT)" "$(POLYPHONIC_CANDIDATE_CAPACITY_AUDIT)" "$(HARMONIC_PRODUCT_OCTAVE_AUDIT)" "$(SATB_RELATIVE_CHROMA_SELECTOR_AUDIT)"; do test -s "$$path" || { printf '%s\n' "missing cached accuracy audit: $$path"; exit 2; }; done
	$(PYTHON) scripts/write_detection_accuracy_report.py --input "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(DETECTION_ACCURACY_CHORD_ARGS) $(DETECTION_ACCURACY_VOCAL_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCALSET_CLEAN_VOWEL_ARG) $(DETECTION_ACCURACY_URMP_GATE_ARG) $(DETECTION_ACCURACY_BACH10_GATE_ARGS) $(DETECTION_ACCURACY_MUSICNET_GATE_ARG) $(DETECTION_ACCURACY_MAPS_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_NOTE_GATE_ARGS) $(DETECTION_ACCURACY_MAPS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_DRUM_GATE_ARG) $(DETECTION_ACCURACY_HF_DRUM_GATE_ARGS) $(DETECTION_ACCURACY_STAR_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_MDB_DRUMS_GATE_ARG) $(DETECTION_ACCURACY_ROUTE_SUMMARY_ARG) $(DETECTION_ACCURACY_GOOD_SOUNDS_FULL_MIX_ARG) $(DETECTION_ACCURACY_IRMAS_LABELLED_ARG) $(DETECTION_ACCURACY_PITCH_SHIFTED_VIOLIN_ARG) $(DETECTION_ACCURACY_MEDLEY_SOLOS_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_PHILHARMONIA_FULL_ARG) $(DETECTION_ACCURACY_IOWA_ORCHESTRA_FULL_ARG) $(DETECTION_ACCURACY_TINYSOL_WIND_EXACT_ARG) $(DETECTION_ACCURACY_IOWA_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_IOWA_PIANO_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_TINYSOL_FLUTE_FULL_MIX_ARG) $(DETECTION_ACCURACY_REAL_A2S_TENOR_SCALE_ARG) $(DETECTION_ACCURACY_URMP_SAX_EXACT_ARG) $(DETECTION_ACCURACY_URMP_SAX_FULL_MIX_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_VALIDATION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_INSPECTION_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_EXTRACT_ARG) $(DETECTION_ACCURACY_DAGSTUHL_CHOIRSET_MANIFEST_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MEASUREMENT_ARG) $(DETECTION_ACCURACY_MAESTRO_REAL_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_ARCHIVE_ARG) $(DETECTION_ACCURACY_KRAISLER_EXTRACT_ARG) $(DETECTION_ACCURACY_KRAISLER_MANIFEST_ARG) $(DETECTION_ACCURACY_KRAISLER_MEASUREMENT_ARG) $(DETECTION_ACCURACY_BTT_ARGS) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_INSPECTION_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_CHORAL_SINGING_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MANIFEST_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_MEASUREMENT_ARG) $(DETECTION_ACCURACY_ESMUC_CHOIR_DATASET_PATTERN_REPORT_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_ARCHIVE_ARG) $(DETECTION_ACCURACY_MIR1K_DATASET_EXTRACT_ARG) $(DETECTION_ACCURACY_MIR1K_FULL_MIX_ARG) $(DETECTION_ACCURACY_SCMS_ARCHIVE_ARG) $(DETECTION_ACCURACY_SCMS_INSPECTION_ARG) $(DETECTION_ACCURACY_SCMS_FULL_MIX_ARG) $(DETECTION_ACCURACY_VOCAL_EXACT_NOTE_CROSS_CORPUS_ARG) $(DETECTION_ACCURACY_HIGH_VOCAL_OCTAVE_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_PRIMARY_DISPLAY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITAR_CHORD_TONE_RECOVERY_AUDIT_ARG) $(DETECTION_ACCURACY_URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_ARG) $(DETECTION_ACCURACY_OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT_ARG) $(DETECTION_ACCURACY_DOMINANT_SEVENTH_EXTENSION_AUDIT_ARG) $(DETECTION_ACCURACY_GLOBAL_CHORD_CONFIDENCE_AUDIT_ARG) $(DETECTION_ACCURACY_SAME_ROOT_GUITAR_QUALITY_AUDIT_ARG) $(DETECTION_ACCURACY_GUITARSET_ATTRIBUTE_ARG) $(DETECTION_ACCURACY_OTHER_DETECTION_ARG) --output "$(DETECTION_ACCURACY_REPORT)"

test-detection-accuracy-report: tests/test_write_detection_accuracy_report.py scripts/write_detection_accuracy_report.py
	$(PYTHON) tests/test_write_detection_accuracy_report.py

test-summarize-isolated-guitar-visual: tests/test_summarize_isolated_guitar_visual.py scripts/summarize_isolated_guitar_visual.py
	$(PYTHON) tests/test_summarize_isolated_guitar_visual.py

.PHONY: test-analyzer-real-note-label-only
test-analyzer-real-note-label-only: $(BUILD_DIR)/analyzer_real_note_samples tests/test_analyzer_real_note_label_only.py
	$(PYTHON) tests/test_analyzer_real_note_label_only.py

inspect-real-note-attribute-buckets: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/inspect_real_note_attribute_buckets.py
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(INSPECT_BUCKET),--bucket "$(INSPECT_BUCKET)") $(INSPECT_ARGS)

inspect-real-note-full-mix-debug-cached: $(BUILD_DIR)/analyzer_real_note_samples
	@test -n "$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" || { printf '%s\n' "set REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID to a manifest sample id"; exit 2; }
	@test -s "$(REAL_NOTE_SAMPLE_DIR)/manifest.tsv" || { printf '%s\n' "missing $(REAL_NOTE_SAMPLE_DIR)/manifest.tsv; prepare samples separately before inspecting"; exit 2; }
	@rm -f "$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)"
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(REAL_NOTE_SAMPLE_DIR)" MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES=1 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples
	$(PYTHON) scripts/inspect_real_note_attribute_buckets.py "$(REAL_NOTE_FULL_MIX_DEBUG_ATTRIBUTE_TSV)" --sample-id "$(REAL_NOTE_FULL_MIX_DEBUG_SAMPLE_ID)" $(REAL_NOTE_ATTRIBUTE_SUMMARY_ARGS)

find-real-note-attribute-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(PATTERN_ARGS)

find-real-note-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),--top-buckets 8 --limit 10 --max-negative-samples 0 --max-conditions 3 --beam-width 120 --show-near-misses 4 --show-examples 1)

find-real-note-practical-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-focused-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-coverage-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-first-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_PRACTICAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-focused-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_FOCUSED_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-coverage-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-first-visual-row-confusion-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status visual_first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_COVERAGE_VISUAL_ROW_CONFUSION_PATTERN_ARGS))

find-real-note-ownership-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status ownership_miss $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OWNERSHIP_PATTERN_ARGS))

find-real-note-octave-displacement-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

find-real-note-octave-displacement-runtime-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

# Mine an existing real-note export without rebuilding or preparing NSynth.
find-real-note-octave-displacement-cached: scripts/find_real_note_attribute_patterns.py
	@test -s "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" || { printf '%s\n' "missing build/real_note_full_mix_attributes.tsv; run make analyze-real-note-attributes first"; exit 2; }
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status octave_displacement $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_OCTAVE_DISPLACEMENT_PATTERN_ARGS))

find-real-note-weak-expected-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status weak_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_WEAK_EXPECTED_PATTERN_ARGS))

find-real-note-weak-visual-expected-patterns: $(BUILD_DIR)/real_note_full_mix_attributes.tsv $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_PATHS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_PATHS) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(REAL_NOTE_PATTERN_EXTRA_CANDIDATE_ARGS) $(REAL_NOTE_PATTERN_EXTRA_PROTECTED_ARGS) $(if $(PATTERN_BUCKET),--bucket "$(PATTERN_BUCKET)") --bucket-status weak_visual_expected_row $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" $(or $(PATTERN_ARGS),$(MEASURE_REAL_NOTE_WEAK_VISUAL_EXPECTED_PATTERN_ARGS))

measure-real-note-octave-display-aliases: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/measure_real_note_octave_display_aliases.py
	$(PYTHON) scripts/measure_real_note_octave_display_aliases.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(OCTAVE_ALIAS_ARGS)

evaluate-real-note-display-shadow: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_display_shadow $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(DISPLAY_SHADOW_ARGS),--summary-only --jobs "$(DISPLAY_SHADOW_JOBS)")

.PHONY: evaluate-real-note-display-shadow-all
evaluate-real-note-display-shadow-all: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_display_shadow_all $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(DISPLAY_SHADOW_ARGS),--shadow-row all --target-row all --compact-routes --threshold-search --max-protected 0 --min-threshold-extra-hits 20 --threshold-limit 8 --jobs "$(DISPLAY_SHADOW_JOBS)")

evaluate-real-note-vocal-shadow-safety: scripts/run_with_duration.sh
	+$(RUN_WITH_DURATION) real_note_vocal_shadow_safety_parallel $(MAKE) $(PARALLEL_TEST_MAKE_JOBS) evaluate-real-note-vocal-shadow-safety-nsynth evaluate-real-note-vocal-shadow-safety-vocadito

evaluate-real-note-vocal-shadow-safety-nsynth: $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_shadow_nsynth $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --shadow-row other --target-row vocals --compact-routes --threshold-search --max-protected 0 --threshold-limit 4

evaluate-real-note-vocal-shadow-safety-vocadito: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) scripts/evaluate_real_note_display_shadow.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_shadow_vocadito $(PYTHON) scripts/evaluate_real_note_display_shadow.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --shadow-row other --target-row vocals --compact-routes --threshold-search --max-protected 0 --threshold-limit 4

evaluate-real-note-vocal-display-fallback: $(VOCADITO_FULL_MIX_ATTRIBUTE_TSV) $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/evaluate_real_note_vocal_display_fallback.py scripts/run_with_duration.sh
	$(RUN_WITH_DURATION) real_note_vocal_display_fallback $(PYTHON) scripts/evaluate_real_note_vocal_display_fallback.py "$(VOCADITO_FULL_MIX_ATTRIBUTE_TSV)" --compare-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" $(or $(VOCAL_DISPLAY_FALLBACK_ARGS),--summary-only --top 12)

