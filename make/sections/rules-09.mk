prepare-urmp-sax-exact-fixture: prepare-real-urmp $(URMP_SAX_EXACT_FIXTURE_MANIFEST)

$(URMP_SAX_EXACT_FIXTURE_MANIFEST): scripts/prepare_urmp_sax_exact_fixture.py | $(BUILD_DIR)
	@test -d "$(URMP_EXTRACT_DIR)/Dataset" || { printf '%s\n' "missing extracted URMP Dataset; run make prepare-real-urmp"; exit 1; }
	+$(MAKE) ensure-build-sample-storage-link BUILD_SAMPLE_STORAGE_DIR=urmp_sax_exact_fixture
	$(PYTHON) scripts/prepare_urmp_sax_exact_fixture.py --source-root "$(URMP_EXTRACT_DIR)/Dataset" --output "$(URMP_SAX_EXACT_FIXTURE_DIR)" --ffmpeg "$(FFMPEG)"

test-prepare-urmp-sax-exact-fixture: tests/test_prepare_urmp_sax_exact_fixture.py scripts/prepare_urmp_sax_exact_fixture.py
	$(PYTHON) tests/test_prepare_urmp_sax_exact_fixture.py

measure-urmp-sax-exact: $(BUILD_DIR)/analyzer_real_note_samples $(URMP_SAX_EXACT_FIXTURE_MANIFEST) | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(URMP_SAX_EXACT_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(URMP_SAX_EXACT_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(URMP_SAX_EXACT_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(URMP_SAX_EXACT_OUTPUT)"

measure-urmp-sax-full-mix: $(BUILD_DIR)/analyzer_real_note_samples $(URMP_SAX_EXACT_FIXTURE_MANIFEST) | $(BUILD_DIR)
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$(URMP_SAX_FULL_MIX_MIN_SAMPLES)" MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$(URMP_SAX_EXACT_FIXTURE_DIR)" MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" $(BUILD_DIR)/analyzer_real_note_samples > "$(URMP_SAX_FULL_MIX_OUTPUT)"

find-urmp-good-sounds-sax-shared-routing-patterns: $(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)
	@cat "$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT)"

$(URMP_GOOD_SOUNDS_SAX_SHARED_PATTERN_REPORT): FORCE $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) $(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV) $(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV) $(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV) $(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV) $(BUILD_DIR)/real_note_full_mix_attributes.tsv scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@raw="$@.$$$$.raw"; tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-candidate-path "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --extra-protected-path "$(IOWA_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(REAL_A2S_SAX_SCALE_ATTRIBUTE_TSV)" --bucket "row_confusion:other/*->piano" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --show-examples 2 --show-near-misses 12 --protected-scope all --profile-fields 8 > "$$raw" 2>&1; status="$$?"; count="$$(awk '/^  \+.*net_rows=/ { count += 1 } END { print count + 0 }' "$$raw")"; { printf 'shared_sax_candidates=%s\n' "$$count"; cat "$$raw"; } > "$$tmp"; rm -f "$$raw"; mv "$$tmp" "$@"; exit "$$status"

.PHONY: find-cross-corpus-octave-correction-patterns
find-cross-corpus-octave-correction-patterns: $(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)
	@cat "$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT)"

# A detector-level octave correction must work across unrelated orchestral
# captures and preserve all existing real-note, saxophone, and duet evidence.
$(OCTAVE_CORRECTION_CROSS_CORPUS_AUDIT): FORCE scripts/find_real_note_attribute_patterns.py | $(BUILD_DIR)
	@for path in "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" "$(KRAISLER_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached octave-audit input: $$path"; exit 2; }; done
	@raw="$@.$$$$.raw"; tmp="$@.$$$$.tmp"; $(PYTHON) scripts/find_real_note_attribute_patterns.py "$(BUILD_DIR)/real_note_full_mix_attributes.tsv" --extra-candidate-path "$(PHILHARMONIA_FULL_ATTRIBUTE_TSV)" --extra-candidate-path "$(IOWA_ORCHESTRA_FULL_ATTRIBUTE_TSV)" --extra-protected-path "$(GOOD_SOUNDS_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(TINYSOL_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --extra-protected-path "$(KRAISLER_ATTRIBUTE_OUTPUT)" --bucket "octave_displacement:other/*->+36" $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --limit 16 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 4 --show-examples 3 --show-near-misses 10 --protected-scope all --profile-fields 10 > "$$raw" 2>&1; status="$$?"; count="$$(awk '/^  \+.*net_rows=/ { count += 1 } END { print count + 0 }' "$$raw")"; { printf 'shared_octave_correction_candidates=%s\n' "$$count"; cat "$$raw"; } > "$$tmp"; rm -f "$$raw"; mv "$$tmp" "$@"; exit "$$status"

find-urmp-sax-full-mix-row-confusion-patterns: $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

find-urmp-sax-full-mix-first-row-confusion-patterns: $(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV) scripts/find_real_note_attribute_patterns.py
	$(PYTHON) scripts/find_real_note_attribute_patterns.py "$(URMP_SAX_FULL_MIX_ATTRIBUTE_TSV)" --bucket-status first_row_confusion $(REAL_NOTE_RUNTIME_ROW_CONFUSION_EXCLUDES) --jobs "$(REAL_NOTE_PATTERN_JOBS)" --top-buckets 8 --limit 8 --min-positive-samples 5 --max-negative-samples 0 --max-conditions 3 --beam-width 240 --show-examples 3 --profile-fields 5

analyze-urmp-sax-exact: $(URMP_SAX_EXACT_ATTRIBUTE_TSV) scripts/analyze_exact_midi_misses.py
	$(PYTHON) scripts/analyze_exact_midi_misses.py "$(URMP_SAX_EXACT_ATTRIBUTE_TSV)" $(if $(EXACT_MIDI_SAMPLE_ID),--sample-id "$(EXACT_MIDI_SAMPLE_ID)") $(if $(EXACT_MIDI_PRE_OFFSET),--pre-offset "$(EXACT_MIDI_PRE_OFFSET)") $(if $(EXACT_MIDI_SAME_PC_OFFSET),--same-pc-offset "$(EXACT_MIDI_SAME_PC_OFFSET)") $(if $(EXACT_MIDI_SOURCE),--source "$(EXACT_MIDI_SOURCE)") $(if $(EXACT_MIDI_RAW_OFFSET),--raw-offset "$(EXACT_MIDI_RAW_OFFSET)")

analyze-real-urmp-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_measurement.sh
	$(SHELL) scripts/capture_urmp_measurement.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_MEASUREMENT_OUTPUT)"

analyze-real-urmp-miss-traits: $(BUILD_DIR)/analyzer_urmp scripts/capture_urmp_trait_sample.sh
	$(SHELL) scripts/capture_urmp_trait_sample.sh "$(BUILD_DIR)/analyzer_urmp" "$(URMP_EXTRACT_DIR)" "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_MEASUREMENT_OUTPUT)"

summarize-real-urmp-miss-traits: scripts/summarize_urmp_misses.py
	$(PYTHON) scripts/summarize_urmp_misses.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-chord-miss-traits: scripts/summarize_urmp_chord_misses.py
	$(PYTHON) scripts/summarize_urmp_chord_misses.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

summarize-real-urmp-wrong-notes: scripts/summarize_urmp_wrong_notes.py
	$(PYTHON) scripts/summarize_urmp_wrong_notes.py "$(URMP_TRAIT_SAMPLE_OUTPUT)"

test-urmp-archive-extract: scripts/extract_urmp_archive.sh tests/test_extract_urmp_archive.py
	$(PYTHON) tests/test_extract_urmp_archive.py scripts/extract_urmp_archive.sh

$(URMP_ARCHIVE): FORCE scripts/download_urmp_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_urmp_archive.sh "$@" "$(URMP_ARCHIVE_URL)" "$(URMP_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

download-real-musicnet: $(MUSICNET_ARCHIVE) $(MUSICNET_METADATA) $(MUSICNET_MIDI_ARCHIVE)

inspect-real-musicnet-download: scripts/musicnet_download_status.sh
	$(SHELL) scripts/musicnet_download_status.sh "$(MUSICNET_ARCHIVE)"

$(MUSICNET_ARCHIVE): FORCE scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_musicnet_archive.sh "$@" "$(MUSICNET_ARCHIVE_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

$(MUSICNET_METADATA): FORCE | $(BUILD_DIR)
	mkdir -p "$(MUSICNET_SOURCE_DIR)"
	$(CURL) -fL -C - -o "$@.part" "$(MUSICNET_METADATA_URL)"
	mv -f "$@.part" "$@"

$(MUSICNET_MIDI_ARCHIVE): FORCE scripts/download_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/download_musicnet_archive.sh "$@" "$(MUSICNET_MIDI_ARCHIVE_URL)" "$(MUSICNET_DOWNLOAD_CONNECTIONS)" "$(ARIA2C)"

prepare-real-musicnet: $(MUSICNET_ARCHIVE) scripts/extract_musicnet_archive.sh | $(BUILD_DIR)
	$(SHELL) scripts/extract_musicnet_archive.sh "$(MUSICNET_ARCHIVE)" "$(MUSICNET_EXTRACT_DIR)"

test-musicnet-archive-extract: scripts/extract_musicnet_archive.sh tests/test_extract_musicnet_archive.py
	$(PYTHON) tests/test_extract_musicnet_archive.py scripts/extract_musicnet_archive.sh

test-run-musicnet-gate: scripts/run_musicnet_gate.sh tests/test_run_musicnet_gate.py
	$(PYTHON) tests/test_run_musicnet_gate.py scripts/run_musicnet_gate.sh

test-summarize-musicnet-attributes: scripts/summarize_musicnet_attributes.py tests/test_summarize_musicnet_attributes.py
	$(PYTHON) tests/test_summarize_musicnet_attributes.py

inspect-downloaded-real-musicnet: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet
	MUSIC_ANALYZER_MUSICNET_ROOT="$(MUSICNET_EXTRACT_DIR)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_INSPECT_ONLY=1 $(BUILD_DIR)/analyzer_musicnet

analyze-downloaded-real-musicnet-20-traits: scripts/summarize_musicnet_attributes.py
	$(PYTHON) scripts/summarize_musicnet_attributes.py "$(MUSICNET_20_ATTRIBUTE_OUTPUT)"

analyze-downloaded-real-musicnet-chord-misses: scripts/analyze_musicnet_chord_misses.py
	$(PYTHON) scripts/analyze_musicnet_chord_misses.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

.PHONY: summarize-downloaded-real-musicnet-attributes summarize-downloaded-real-musicnet-routing test-summarize-musicnet-routing audit-dominant-seventh-extension test-audit-dominant-seventh-extension
summarize-downloaded-real-musicnet-attributes: scripts/summarize_musicnet_attributes.py
	$(PYTHON) scripts/summarize_musicnet_attributes.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

summarize-downloaded-real-musicnet-routing: $(MUSICNET_FULL_ATTRIBUTE_OUTPUT) scripts/summarize_musicnet_routing.py
	$(PYTHON) scripts/summarize_musicnet_routing.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" --output "$(MUSICNET_ROUTING_OUTPUT)"

# Compare the same normalized raw-chroma predicate across independent chord
# corpora before any dominant-seventh display extension is considered.
audit-dominant-seventh-extension: scripts/audit_dominant_seventh_extensions.py
	@for path in "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)"; do test -s "$$path" || { printf '%s\n' "missing cached dominant-seventh audit input: $$path"; exit 2; }; done
	@tmp="$(DOMINANT_SEVENTH_EXTENSION_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_dominant_seventh_extensions.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" "$(BUILD_DIR)/guitar_chord_mix_attributes.tsv" "$(GUITAR_TECHS_CHORD_ATTRIBUTE_TSV)" > "$$tmp" && mv "$$tmp" "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)"
	@cat "$(DOMINANT_SEVENTH_EXTENSION_AUDIT)"

test-audit-dominant-seventh-extension: tests/test_audit_dominant_seventh_extensions.py scripts/audit_dominant_seventh_extensions.py
	$(PYTHON) tests/test_audit_dominant_seventh_extensions.py

.PHONY: analyze-choir-chord-traits
analyze-choir-chord-traits: scripts/summarize_musicnet_attributes.py
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached choir chord input: $$path"; exit 2; }; done
	@for path in "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do printf '%s\n' "=== $$path ==="; $(PYTHON) scripts/summarize_musicnet_attributes.py "$$path"; done

.PHONY: audit-global-chord-confidence
audit-global-chord-confidence: scripts/audit_global_chord_confidence.py
	@for path in "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)"; do test -s "$$path" || { printf '%s\n' "missing cached global-chord confidence input: $$path"; exit 2; }; done
	@tmp="$(GLOBAL_CHORD_CONFIDENCE_AUDIT).$$$$.tmp"; $(PYTHON) scripts/audit_global_chord_confidence.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)" "$(DAGSTUHL_CHOIRSET_ATTRIBUTE_OUTPUT)" "$(CHORAL_SINGING_DATASET_ATTRIBUTE_OUTPUT)" "$(ESMUC_CHOIR_DATASET_ATTRIBUTE_OUTPUT)" > "$$tmp" && mv "$$tmp" "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)" && cat "$(GLOBAL_CHORD_CONFIDENCE_AUDIT)"

.PHONY: test-audit-global-chord-confidence
test-audit-global-chord-confidence: tests/test_audit_global_chord_confidence.py scripts/audit_global_chord_confidence.py
	$(PYTHON) tests/test_audit_global_chord_confidence.py

test-summarize-musicnet-routing: tests/test_summarize_musicnet_routing.py scripts/summarize_musicnet_routing.py
	$(PYTHON) tests/test_summarize_musicnet_routing.py

.PHONY: inspect-downloaded-real-musicnet-chord-traits
inspect-downloaded-real-musicnet-chord-traits: scripts/inspect_musicnet_chord_traits.py
	$(PYTHON) scripts/inspect_musicnet_chord_traits.py "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

analyze-downloaded-real-musicnet-recording: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	@test -n "$(MUSICNET_ANALYSIS_RECORDING_IDS)" || { printf '%s\n' "set MUSICNET_ANALYSIS_RECORDING_IDS=<MusicNet id>" >&2; exit 2; }
	MUSIC_ANALYZER_MUSICNET_RECORDING_IDS="$(MUSICNET_ANALYSIS_RECORDING_IDS)" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS=1 MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS=1 MUSIC_ANALYZER_MUSICNET_MAX_RECORDINGS="$(MUSICNET_ANALYSIS_MAX_RECORDINGS)" MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING=12 MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_PRECISION_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_SIMPLE_CHORD_RECALL_PERCENT=0 MUSIC_ANALYZER_MUSICNET_MIN_CHORD_CHECKS=1 $(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_RECORDING_MEASUREMENT_OUTPUT)" "" "" "$(MUSICNET_RECORDING_ATTRIBUTE_OUTPUT)"

test-downloaded-real-musicnet-20: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	$(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_20_MEASUREMENT_OUTPUT)" 20 80 "$(MUSICNET_20_ATTRIBUTE_OUTPUT)"

test-downloaded-real-musicnet-full: $(BUILD_DIR)/analyzer_musicnet prepare-real-musicnet scripts/run_musicnet_gate.sh
	$(SHELL) scripts/run_musicnet_gate.sh "$(BUILD_DIR)/analyzer_musicnet" "$(MUSICNET_EXTRACT_DIR)" "$(MUSICNET_FULL_MEASUREMENT_OUTPUT)" "" "" "$(MUSICNET_FULL_ATTRIBUTE_OUTPUT)"

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

test-real-synthsod-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py | $(BUILD_DIR)
	rm -rf $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_synthsod_musicnet_fixture.py $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SYNTHSOD_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-synthsod-full: $(BUILD_DIR)/analyzer_musicnet tests/prepare_synthsod_musicnet_fixture.py tests/inspect_synthsod_dataset.py | $(BUILD_DIR)
	rm -rf $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_SYNTHSOD_PREPARE_PIECES=1000000 $(PYTHON) tests/prepare_synthsod_musicnet_fixture.py $(SYNTHSOD_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(SYNTHSOD_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-polyvocal-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_polyvocal_musicnet_fixture.py tests/inspect_polyvocal_dataset.py | $(BUILD_DIR)
	rm -rf $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_polyvocal_musicnet_fixture.py $(POLYVOCAL_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(POLYVOCAL_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-prepared-multitrack-20: $(BUILD_DIR)/analyzer_musicnet tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py | $(BUILD_DIR)
	rm -rf $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	$(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-prepared-multitrack-full: $(BUILD_DIR)/analyzer_musicnet tests/prepare_prepared_multitrack_musicnet_fixture.py tests/inspect_prepared_multitrack_dataset.py | $(BUILD_DIR)
	rm -rf $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES=1000000 $(PYTHON) tests/prepare_prepared_multitrack_musicnet_fixture.py $(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR)
	MUSIC_ANALYZER_MUSICNET_ROOT=$(PREPARED_MULTITRACK_MUSICNET_FIXTURE_DIR) MUSIC_ANALYZER_MUSICNET_REQUIRED=1 $(BUILD_DIR)/analyzer_musicnet

test-real-multtipop-20: $(BUILD_DIR)/analyzer_multtipop
	MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 $(BUILD_DIR)/analyzer_multtipop

test-real-multtipop-full: $(BUILD_DIR)/analyzer_multtipop
	MUSIC_ANALYZER_MULTTIPOP_REQUIRED=1 MUSIC_ANALYZER_MULTTIPOP_REQUIRED_SEGMENTS=572 MUSIC_ANALYZER_MULTTIPOP_REQUIRED_WINDOWS=2288 $(BUILD_DIR)/analyzer_multtipop

test-real-guitarset-20: $(BUILD_DIR)/analyzer_guitarset tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 $(BUILD_DIR)/analyzer_guitarset

test-real-guitarset-full: $(BUILD_DIR)/analyzer_guitarset tests/prepare_guitarset_manifest.py | $(BUILD_DIR)
	MUSIC_ANALYZER_GUITARSET_ROOT="$(GUITARSET_ROOT)" $(PYTHON) tests/prepare_guitarset_manifest.py $(GUITARSET_MANIFEST)
	MUSIC_ANALYZER_GUITARSET_MANIFEST=$(GUITARSET_MANIFEST) MUSIC_ANALYZER_GUITARSET_REQUIRED=1 MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS=360 MUSIC_ANALYZER_GUITARSET_REQUIRED_WINDOWS=1440 $(BUILD_DIR)/analyzer_guitarset

test-real-maestro-20: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 $(BUILD_DIR)/analyzer_maestro

test-real-maestro-full: $(BUILD_DIR)/analyzer_maestro
	MUSIC_ANALYZER_MAESTRO_REQUIRED=1 MUSIC_ANALYZER_MAESTRO_REQUIRED_RECORDINGS=1276 MUSIC_ANALYZER_MAESTRO_REQUIRED_WINDOWS=5104 $(BUILD_DIR)/analyzer_maestro

test-real-egmd-20: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 $(BUILD_DIR)/analyzer_egmd

test-real-egmd-full: $(BUILD_DIR)/analyzer_egmd
	MUSIC_ANALYZER_EGMD_REQUIRED=1 MUSIC_ANALYZER_EGMD_REQUIRED_RECORDINGS=45537 MUSIC_ANALYZER_EGMD_REQUIRED_WINDOWS=182148 $(BUILD_DIR)/analyzer_egmd

.PHONY: inspect-instrument-sample-store configure-instrument-sample-store test-instrument-sample-store inspect-sample-build-migration migrate-sample-build-directories inspect-build-sample-relocation compare-build-sample-relocation-conflicts relocate-build-sample-directories deduplicate-build-sample-directories merge-build-sample-directories test-sample-build-migration test-instrument-family-miss-inspector

inspect-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --status --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

configure-instrument-sample-store: scripts/configure_instrument_sample_store.py
	$(PYTHON) scripts/configure_instrument_sample_store.py --link "$(INSTRUMENT_SAMPLE_STORE_LINK)" --target "$(INSTRUMENT_SAMPLE_STORE)"

inspect-sample-build-migration: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --status --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

migrate-sample-build-directories: scripts/migrate_sample_build_directories.py
	$(PYTHON) scripts/migrate_sample_build_directories.py --build "$(BUILD_DIR)" --store "$(INSTRUMENT_SAMPLE_STORE)"

inspect-build-sample-relocation: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --dry-run

compare-build-sample-relocation-conflicts: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --compare-conflicts

relocate-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --apply

deduplicate-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --deduplicate-identical

merge-build-sample-directories: scripts/relocate_build_sample_directories.sh
	bash scripts/relocate_build_sample_directories.sh --merge-nonconflicting

test-instrument-sample-store: tests/test_configure_instrument_sample_store.py scripts/configure_instrument_sample_store.py
	$(PYTHON) tests/test_configure_instrument_sample_store.py

test-sample-build-migration: tests/test_migrate_sample_build_directories.py scripts/migrate_sample_build_directories.py
	$(PYTHON) tests/test_migrate_sample_build_directories.py

test-instrument-family-miss-inspector: tests/test_inspect_instrument_family_misses.py scripts/inspect_instrument_family_misses.py
	$(PYTHON) tests/test_inspect_instrument_family_misses.py

inspect-real-urmp: tests/inspect_urmp_dataset.py
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) $(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-urmp-full: tests/inspect_urmp_dataset.py
	MUSIC_ANALYZER_DATASET_ROOT=$(REAL_DATASET_ROOT) MUSIC_ANALYZER_URMP_REQUIRED_PIECES=44 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=176 $(PYTHON) tests/inspect_urmp_dataset.py

inspect-real-multitrack-20: inspect-real-urmp

inspect-real-multitrack-full: inspect-real-urmp-full

inspect-urmp-fixture: $(URMP_FIXTURE_ARCHIVE) tests/inspect_urmp_dataset.py | $(BUILD_DIR)
	rm -rf $(URMP_FIXTURE_DIR)
	$(TAR) -xzf $(URMP_FIXTURE_ARCHIVE) -C $(BUILD_DIR)
	+$(MAKE) decode-urmp-fixture
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
	@if pgrep -x obs >/dev/null 2>&1 || pgrep -x obs-studio >/dev/null 2>&1; then \
		echo "OBS is running; refusing to copy $(BUILD_DIR)/music-analyzer-obs.so. Close OBS first."; \
		exit 1; \
	fi
	mkdir -p $(OBS_USER_PLUGIN_DIR)
	cp $(BUILD_DIR)/music-analyzer-obs.so $(OBS_USER_PLUGIN_DIR)/
	mkdir -p $(OBS_USER_PLUGIN_DATA_DIR)
	cp $(ONNXRUNTIME_LIBRARY) $(OBS_USER_PLUGIN_DATA_DIR)/libonnxruntime.so
	cp $(BASIC_PITCH_ONNX_MODEL) $(OBS_USER_PLUGIN_DATA_DIR)/nmp.onnx

.PHONY: clean-legacy-basic-pitch-user-data
# One-time cleanup for the path used before OBS_USER_PLUGIN_ROOT was resolved
# correctly.  It targets only files installed by this plugin revision.
clean-legacy-basic-pitch-user-data:
	rm -rf "$(OBS_USER_PLUGIN_ROOT)/bin/data/basic_pitch"

clean:
	rm -rf $(BUILD_DIR)

clean-pycache:
	find tests -type d -name '__pycache__' -prune -exec rm -rf {} +
.PHONY: check-worktree
check-worktree: scripts/check_worktree.sh
	bash scripts/check_worktree.sh

.PHONY: commit-verified
commit-verified: scripts/commit_verified.sh
	@test -n "$(COMMIT_MESSAGE)"
	@test -n "$(COMMIT_PATHS)"
	bash scripts/commit_verified.sh "$(COMMIT_MESSAGE)" $(COMMIT_PATHS)

.PHONY: push-current-branch
push-current-branch: scripts/push_current_branch.sh
	bash scripts/push_current_branch.sh

.PHONY: locate-gaps-guitar-sample
locate-gaps-guitar-sample: scripts/locate_gaps_guitar_sample.sh
	@test -n "$(SAMPLE_ID)"
	bash scripts/locate_gaps_guitar_sample.sh "$(SAMPLE_ID)"

.PHONY: inspect-gaps-guitar-full-rows
inspect-gaps-guitar-full-rows: build/gaps_guitar_full_attributes.tsv scripts/inspect_gaps_guitar_full_rows.sh
	@test -n "$(SAMPLE_ID)"
	bash scripts/inspect_gaps_guitar_full_rows.sh "$(SAMPLE_ID)"

.PHONY: analyze-gaps-guitar-power-alias-candidates
analyze-gaps-guitar-power-alias-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_power_alias_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_power_alias_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(POWER_ALIAS_ARGS)

.PHONY: inspect-analyzer-symbol
inspect-analyzer-symbol: scripts/inspect_analyzer_symbol.sh
	@test -n "$(SYMBOL)"
	bash scripts/inspect_analyzer_symbol.sh "$(SYMBOL)"

.PHONY: rebuild-analyzer-guitarset
rebuild-analyzer-guitarset:
	+$(MAKE) -B build/analyzer_guitarset

.PHONY: analyze-gaps-guitar-display-restore-candidates
analyze-gaps-guitar-display-restore-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_display_restore_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_display_restore_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(DISPLAY_RESTORE_ARGS)

.PHONY: analyze-gaps-guitar-major-seventh-candidates
analyze-gaps-guitar-major-seventh-candidates: build/gaps_guitar_full_attributes.tsv scripts/analyze_gaps_guitar_major_seventh_candidates.py
	$(PYTHON) scripts/analyze_gaps_guitar_major_seventh_candidates.py "$(GAPS_GUITAR_FULL_ATTRIBUTE_TSV)" $(MAJOR_SEVENTH_ARGS)
.PHONY: analyze-gaps-guitar-analysis-fifth-power-candidates
analyze-gaps-guitar-analysis-fifth-power-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_fifth_power_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_FIFTH_POWER_ARGS)
.PHONY: analyze-gaps-guitar-low-root-power-candidates
analyze-gaps-guitar-low-root-power-candidates:
	@python3 scripts/analyze_gaps_guitar_low_root_power_candidates.py
.PHONY: find-gaps-guitar-rows
find-gaps-guitar-rows:
	@test -n "$(EXPECTED)"
	@python3 scripts/find_gaps_guitar_rows.py --expected "$(EXPECTED)" $(if $(MISSING),--missing "$(MISSING)") $(FIND_GAPS_GUITAR_ROWS_ARGS)
.PHONY: analyze-gaps-guitar-analysis-note-candidates
analyze-gaps-guitar-analysis-note-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_note_candidates.py $(ANALYSIS_NOTE_ARGS) "$(GUITAR_ANALYSIS_NOTE_PATH)"
.PHONY: analyze-gaps-guitar-analysis-minor-alias-candidates
analyze-gaps-guitar-analysis-minor-alias-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_minor_alias_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_MINOR_ALIAS_ARGS)
.PHONY: analyze-gaps-guitar-analysis-add9-alias-candidates
analyze-gaps-guitar-analysis-add9-alias-candidates:
	@python3 scripts/analyze_gaps_guitar_analysis_add9_alias_candidates.py build/gaps_guitar_full_attributes.tsv $(ANALYSIS_ADD9_ALIAS_ARGS)
.PHONY: analyze-guitar-rootless-dim-candidates
analyze-guitar-rootless-dim-candidates:
	@python3 scripts/analyze_guitar_rootless_dim_candidates.py $(ROOTLESS_DIM_ARGS) build/gaps_guitar_full_attributes.tsv build/guitar_techs_chord_attributes.tsv build/guitar_chord_mix_attributes.tsv
.PHONY: test-gaps-guitar-regressions
test-gaps-guitar-regressions: build/gaps_guitar_full_attributes.tsv
	@python3 scripts/check_gaps_guitar_regressions.py build/gaps_guitar_full_attributes.tsv
.PHONY: search-repo
search-repo:
	@sh scripts/search_repo.sh "$(QUERY)"

.PHONY: show-repo-lines
show-repo-lines:
	@sh scripts/show_repo_lines.sh "$(FILE)" "$(START)" "$(END)"
inspect-analyzer-hihat-cap-sites:
	$(PYTHON) scripts/inspect_hihat_cap_sites.py
summarize-mdb-hihat-cap:
	$(PYTHON) scripts/summarize_mdb_hihat_cap.py
inspect-egmd-verbose-output:
	$(PYTHON) scripts/inspect_egmd_verbose_output.py
list-mdb-early-hihat-candidates:
	$(PYTHON) scripts/list_mdb_early_hihat_candidates.py
mine-mdb-drum-selectors:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/mine_mdb_drum_selectors.py
inspect-analyzer-kick-cap-sites:
	$(PYTHON) scripts/inspect_kick_cap_sites.py
mine-mdb-drum-pair-selectors:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/mine_mdb_drum_pair_selectors.py
list-mdb-snare-candidates:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/list_mdb_snare_candidates.py
summarize-mdb-crash-recovery:
	$(MAKE) analyze-mdb-drum-windows
	$(PYTHON) scripts/summarize_mdb_crash_recovery.py
analyze-star-drums-verbose-windows:
	$(PYTHON) scripts/analyze_star_drum_verbose_windows.py

list-star-hihat-misses:
	$(MAKE) analyze-star-drums-verbose-windows
	$(PYTHON) scripts/list_star_hihat_misses.py
inspect-fret-zealot-auto-root:
	python3 scripts/inspect_fret_zealot_auto_root.py
report-idmt-drums-processes:
	python3 scripts/report_idmt_drums_processes.py
wait-idmt-drums-processes:
	python3 scripts/wait_idmt_drums_processes.py
summarize-idmt-drums-results:
	python3 scripts/summarize_idmt_drums_results.py
inspect-analyzer-case-hihat-regression:
	python3 scripts/inspect_analyzer_case_hihat_regression.py
wait-analyzer-cases-process:
	python3 scripts/wait_analyzer_cases_process.py
report-analyzer-cases-process:
	python3 scripts/report_analyzer_cases_process.py
plan-stop-duplicate-analyzer-cases:
	python3 scripts/manage_duplicate_analyzer_cases.py plan

apply-stop-duplicate-analyzer-cases:
	python3 scripts/manage_duplicate_analyzer_cases.py apply
test-analyzer-hihat-regression:
	/bin/sh scripts/run_analyzer_hihat_regression.sh
inspect-drum-transient-gate:
	python3 scripts/inspect_drum_transient_gate.py
inspect-mdb-hihat-trigger-evidence:
	python3 scripts/inspect_mdb_hihat_trigger_evidence.py
inspect-analyzer-test-object-rule:
	python3 scripts/inspect_analyzer_test_object_rule.py
test-analyzer-cases-logged:
	python3 scripts/run_analyzer_cases_logged.py

summarize-analyzer-cases-log:
	python3 scripts/summarize_analyzer_cases_log.py
list-real-note-test-targets:
	python3 scripts/list_real_note_test_targets.py
inspect-analyzer-cases-main:
	python3 scripts/inspect_analyzer_cases_main.py
summarize-hf-ride-primary-misses:
	python3 scripts/summarize_hf_ride_primary_misses.py
inspect-drum-sample-verbose-controls:
	python3 scripts/inspect_drum_sample_verbose_controls.py

print-drum-sample-verbose-controls:
	python3 scripts/print_drum_sample_verbose_controls.py

inspect-drum-sample-verbose-output:
	python3 scripts/inspect_drum_sample_verbose_output.py

inspect-hf-drum-kit-target:
	python3 scripts/inspect_make_target.py

report-hf-ride-primary-attributes: build/hf_drum_kit_primary_attribute_rows_ride.tsv
	python3 scripts/report_hf_ride_primary_attributes.py

inspect-primary-drum-arbitration:
	python3 scripts/inspect_primary_drum_arbitration.py

inspect-hihat-ride-arbitration:
	python3 scripts/inspect_hihat_ride_arbitration.py

evaluate-hihat-ride-primary-recovery: build/hf_drum_kit_primary_attribute_rows_ride.tsv build/hf_drum_kit_primary_attribute_rows_hihat.tsv
	python3 scripts/evaluate_hihat_ride_primary_recovery.py

report-hf-drum-test-status:
	python3 scripts/report_hf_drum_test_status.py

report-hf-snare-ride-hihat-collisions: build/hf_drum_kit_primary_attribute_rows_snare.tsv
	python3 scripts/report_hf_snare_ride_hihat_collisions.py

verify-drum-regression-targets:
	python3 scripts/verify_drum_regression_targets.py

test-drum-regressions-parallel: verify-drum-regression-targets
	python3 scripts/run_drum_regressions_parallel.py

report-drum-regression-logs:
	python3 scripts/report_drum_regression_logs.py

report-drum-test-controls:
	python3 scripts/report_drum_test_controls.py

report-external-fixture-links:
	python3 scripts/report_external_fixture_links.py

profile-drum-primary-confusions: build/analyzer_drum_samples
	python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-hihat: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=hihat python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-snare: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=snare python3 scripts/profile_drum_primary_confusions.py

profile-drum-primary-confusions-ride: build/analyzer_drum_samples
	DRUM_PROFILE_CATEGORY=ride python3 scripts/profile_drum_primary_confusions.py

test-drum-tom-primary-regression: build/analyzer_drum_samples
	python3 scripts/test_drum_tom_primary_regression.py

report-drum-tom-body-snare-tie-tom: build/analyzer_drum_samples
	DRUM_RULE_HIT_CATEGORY=tom python3 scripts/report_drum_rule_hits.py

report-drum-tom-body-snare-tie-snare: build/analyzer_drum_samples
	DRUM_RULE_HIT_CATEGORY=snare python3 scripts/report_drum_rule_hits.py

report-drum-classifier-source:
	python3 scripts/report_drum_classifier_source.py

report-spread-rim-ride-hihat-collisions: build/drum_spread_exact_attribute_rows_rim.tsv
	python3 scripts/report_spread_rim_ride_hihat_collisions.py

report-spread-drum-shards:
	python3 scripts/report_spread_drum_shards.py

inspect-complex-real-timbres:
	python3 scripts/inspect_complex_real_timbres.py

list-ready-real-audio-evidence:
	python3 scripts/list_ready_real_audio_evidence.py

summarize-gaps-guitar-attributes:
	python3 scripts/summarize_gaps_guitar_attributes.py

inspect-caged-root-regression:
	python3 scripts/inspect_caged_root_regression.py

inspect-analyzer-hihat-regression-test:
	python3 scripts/inspect_analyzer_hihat_regression_test.py

inspect-analyzer-caged-root-runtime: build/analyzer_test.o tests/analyzer_caged_root_regression.cpp scripts/run_analyzer_caged_root_regression.sh
	sh scripts/run_analyzer_caged_root_regression.sh

inspect-analysis-snapshot:
	python3 scripts/inspect_analysis_snapshot.py

inspect-chord-template-ranking:
	python3 scripts/inspect_chord_template_ranking.py

inspect-global-chord-path:
	python3 scripts/inspect_global_chord_path.py

inspect-global-chord-tracking:
	python3 scripts/inspect_global_chord_tracking.py

inspect-mixed-global-display-chord:
	python3 scripts/inspect_mixed_global_display_chord.py

inspect-stronger-chord:
	python3 scripts/inspect_stronger_chord.py

inspect-global-chroma-construction:
	python3 scripts/inspect_global_chroma_construction.py

plan-stage-verified-drum-changes:
	python3 scripts/plan_stage_verified_drum_changes.py

list-idmt-drum-evidence:
	python3 scripts/list_idmt_drum_evidence.py

summarize-idmt-hihat-attributes:
	python3 scripts/summarize_idmt_hihat_attributes.py

evaluate-idmt-hihat-recovery:
	python3 scripts/evaluate_idmt_hihat_recovery.py
.PHONY: inspect-idmt-hihat-suppression
inspect-idmt-hihat-suppression:
	python3 scripts/inspect_idmt_hihat_suppression.py
.PHONY: evaluate-gaps-guitar-misses
evaluate-gaps-guitar-misses:
	python3 scripts/evaluate_gaps_guitar_misses.py
.PHONY: inspect-make-targets
inspect-make-targets:
	python3 scripts/inspect_make_targets.py
.PHONY: inspect-vocal-make-targets
inspect-vocal-make-targets:
	python3 scripts/inspect_make_targets.py vocal
.PHONY: report-vocalset-test-state
report-vocalset-test-state:
	python3 scripts/report_vocalset_test_state.py
.PHONY: wait-vocalset-test-state
wait-vocalset-test-state:
	python3 scripts/wait_vocalset_test_state.py
.PHONY: inspect-guitar-chord-primary-promotion
inspect-guitar-chord-primary-promotion:
	python3 scripts/inspect_guitar_chord_primary_promotion.py
.PHONY: inspect-guitar-extension-promotion-core
inspect-guitar-extension-promotion-core:
	$(PYTHON) scripts/inspect_source_range.py src/analyzer.cpp 18670 18870
.PHONY: report-analyzer-build-state
report-analyzer-build-state:
	python3 scripts/report_analyzer_build_state.py
.PHONY: test-gaps-guitar-full-primary-display
test-gaps-guitar-full-primary-display: analyze-gaps-guitar-full-attributes
	python3 tests/check_gaps_guitar_primary_display.py build/gaps_guitar_full_attributes.tsv 177
.PHONY: summarize-real-audio-fixture-coverage
summarize-real-audio-fixture-coverage:
	python3 scripts/summarize_real_audio_fixture_coverage.py
.PHONY: inspect-fret-zealot-current
inspect-fret-zealot-current:
	python3 scripts/inspect_fret_zealot_current.py

.PHONY: inspect-real-audio-targets
inspect-real-audio-targets:
	python3 scripts/inspect_make_target_name.py summarize-real-audio-fixture-coverage list-ready-real-audio-evidence

.PHONY: list-real-note-corpus-targets
list-real-note-corpus-targets:
	python3 scripts/list_make_targets_matching.py bass piano vocal real-note musicnet maestro maps iowa urmp

.PHONY: audit-high-bass-ownership
audit-high-bass-ownership:
	python3 scripts/audit_high_bass_ownership.py

.PHONY: inspect-bass-recovery-source
inspect-bass-recovery-source:
	python3 scripts/inspect_bass_recovery_source.py

.PHONY: inspect-other-display-source
inspect-other-display-source:
	python3 scripts/inspect_other_display_source.py
.PHONY: inspect-fret-zealot-scale
inspect-fret-zealot-scale:
	python3 scripts/diagnose_fret_zealot_scale.py

.PHONY: test-fret-zealot-scale-reconciliation
test-fret-zealot-scale-reconciliation:
	python3 tests/check_fret_zealot_scale_reconciliation.py

.PHONY: summarize-melodic-drum-false-positives
summarize-melodic-drum-false-positives:
	python3 scripts/summarize_melodic_drum_false_positives.py build/real_note_full_mix_attributes.tsv

summarize-real-note-row-confusion:
	python3 scripts/summarize_real_note_row_confusion.py build/real_note_full_mix_attributes.tsv

inspect-note-owner-classifier:
	python3 scripts/inspect_note_owner_classifier.py

inspect-guitar-octave-shadow:
	python3 scripts/inspect_guitar_octave_shadow.py

inspect-analyzer-case-hihat-decay:
	python3 scripts/inspect_analyzer_case_context.py 'OBS hihat decay guard'

inspect-analyzer-case-distorted-guitar-chord:
	python3 scripts/inspect_analyzer_case_context.py 'complex real timbre distorted guitar chord'

inspect-chord-dim-alias:
	python3 scripts/inspect_chord_dim_alias.py

list-analyzer-test-targets:
	python3 scripts/list_analyzer_test_targets.py

.PHONY: inspect-fret-zealot-sync
inspect-fret-zealot-sync:
	python3 scripts/inspect_fret_zealot_sync.py

.PHONY: inspect-fret-zealot-diff
inspect-fret-zealot-diff:
	python3 scripts/inspect_fret_zealot_diff.py

.PHONY: test-fret-zealot-auto-root-guard
test-fret-zealot-auto-root-guard:
	python3 tests/check_fret_zealot_auto_root_guard.py

.PHONY: list-android-targets
list-android-targets:
	python3 scripts/list_android_targets.py

.PHONY: inspect-android-project-guard
inspect-android-project-guard:
	python3 scripts/inspect_android_project_guard.py

.PHONY: inspect-guitar-chord-mix-shards
inspect-guitar-chord-mix-shards:
	python3 scripts/inspect_guitar_chord_mix_shards.py

.PHONY: inspect-guitarset-primary-measurement
inspect-guitarset-primary-measurement:
	python3 scripts/inspect_guitarset_primary_measurement.py

.PHONY: debug-guitar-chord-primary-misses
debug-guitar-chord-primary-misses:
	python3 scripts/debug_guitar_chord_primary_misses.py

.PHONY: collect-guitar-chord-primary-attributes
collect-guitar-chord-primary-attributes:
	python3 scripts/collect_guitar_chord_primary_attributes.py

.PHONY: summarize-guitar-chord-primary-attributes
summarize-guitar-chord-primary-attributes:
	python3 scripts/summarize_guitar_chord_primary_attributes.py

.PHONY: inspect-chord-ranking
inspect-chord-ranking:
	python3 scripts/inspect_chord_ranking.py

.PHONY: inspect-chord-alias-order
inspect-chord-alias-order:
	python3 scripts/inspect_chord_alias_order.py

.PHONY: inspect-guitar-primary-promotion
inspect-guitar-primary-promotion:
	python3 scripts/inspect_guitar_primary_promotion.py

inspect-real-note-piano-guitar-attributes:
	python3 scripts/inspect_real_note_sample_attributes.py keyboard_electronic_078-042-025

.PHONY: inspect-hihat-detector
inspect-hihat-detector:
	python3 scripts/diagnose_hihat_detector.py

.PHONY: inspect-real-note-full-mix-replay
inspect-real-note-full-mix-replay:
	python3 scripts/diagnose_real_note_full_mix.py

.PHONY: inspect-drum-fixture-debug
inspect-drum-fixture-debug:
	python3 scripts/diagnose_drum_fixture_debug.py

.PHONY: debug-hf-hihat-fixtures
debug-hf-hihat-fixtures:
	sh scripts/run_hihat_fixture_debug.sh

.PHONY: debug-real-note-hihat-false-positives
debug-real-note-hihat-false-positives:
	sh scripts/run_real_note_hihat_false_debug.sh

.PHONY: test-hihat-early-recovery-guard
test-hihat-early-recovery-guard:
	python3 tests/check_hihat_early_recovery_guard.py

test-tonal-hihat-regressions: build/analyzer_real_note_samples
	python3 tests/check_tonal_hihat_regressions.py

inspect-hihat-early-recovery-guard:
	python3 scripts/inspect_hihat_early_recovery_guard.py

inspect-hihat-recovery-change:
	python3 scripts/inspect_hihat_recovery_change.py

.PHONY: summarize-real-note-full-mix-shards
summarize-real-note-full-mix-shards:
	python3 scripts/summarize_real_note_full_mix_shards.py

.PHONY: debug-real-note-top-hihat-brass
debug-real-note-top-hihat-brass:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_059-043-075

debug-real-note-top-hihat-brass-016:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_016-082-100

debug-real-note-top-hihat-brass-016-mid:
	sh scripts/run_real_note_sample_debug.sh brass_acoustic_016-069-100

debug-real-note-piano-guitar-confusion:
	sh scripts/run_real_note_sample_debug.sh keyboard_electronic_078-042-025
inspect-guitar-chord-callsite:
	python3 scripts/inspect_guitar_chord_callsite.py

inspect-guitar-chord-finalization:
	python3 scripts/inspect_guitar_chord_finalization.py

inspect-drum-score-arbitration:
	python3 scripts/inspect_drum_score_arbitration.py

inspect-synthetic-drum-case-context:
	python3 scripts/inspect_synthetic_drum_case_context.py

inspect-analyzer-cases-runner:
	python3 scripts/inspect_analyzer_cases_runner.py

test-analyzer-synthetic-drums: build/analyzer_cases
	env MUSIC_ANALYZER_CASE_GROUP=synthetic-drums build/analyzer_cases

inspect-snare-caps:
	python3 scripts/inspect_snare_caps.py

inspect-snare-debug-fields:
	python3 scripts/inspect_snare_debug_fields.py

inspect-git-scope:
	python3 scripts/inspect_git_scope.py

plan-verified-guitar-anchor-commit:
	python3 scripts/commit_verified_guitar_anchor.py plan

inspect-verified-guitar-anchor-stage:
	python3 scripts/commit_verified_guitar_anchor.py inspect

stage-verified-guitar-anchor-commit:
	python3 scripts/commit_verified_guitar_anchor.py stage

commit-verified-guitar-anchor:
	python3 scripts/commit_verified_guitar_anchor.py commit
.PHONY: diagnose-fret-zealot-partial-scale
diagnose-fret-zealot-partial-scale:
	python3 scripts/diagnose_fret_zealot_partial_scale.py
.PHONY: plan-stage-fret-zealot-batching
plan-stage-fret-zealot-batching:
	python3 scripts/plan_stage_fret_zealot_batching.py
.PHONY: commit-verified-fret-zealot-batching
commit-verified-fret-zealot-batching:
	python3 scripts/commit_verified_fret_zealot_batching.py
.PHONY: diagnose-upbeat-kick-suppression
diagnose-upbeat-kick-suppression:
	python3 scripts/diagnose_upbeat_kick_suppression.py
.PHONY: commit-verified-drum-recovery
commit-verified-drum-recovery:
	python3 scripts/commit_verified_drum_recovery.py
.PHONY: diagnose-guitar-extension-chords
diagnose-guitar-extension-chords:
	python3 scripts/diagnose_guitar_extension_chords.py
diagnose-fret-zealot-led-queue:
	python3 scripts/diagnose_fret_zealot_led_queue.py
commit-verified-fret-zealot-fallback:
	python3 scripts/commit_verified_fret_zealot_fallback.py
diagnose-guitar-extension-template-selection:
	python3 scripts/diagnose_guitar_extension_template_selection.py
test-guitar-caged-voicings:
	python3 scripts/run_analyzer_cases_guitar_caged.py
diagnose-analyzer-cases-runner:
	python3 scripts/diagnose_analyzer_cases_runner.py
test-extended-chords:
	python3 scripts/run_analyzer_cases_extended_chords.py
.PHONY: diagnose-fret-zealot-partial-updates
diagnose-fret-zealot-partial-updates: scripts/diagnose_fret_zealot_partial_updates.py
	python3 scripts/diagnose_fret_zealot_partial_updates.py
.PHONY: test-fret-zealot-batch-settle
test-fret-zealot-batch-settle: scripts/check_fret_zealot_batch_settle.py
	python3 scripts/check_fret_zealot_batch_settle.py
.PHONY: diagnose-android-fret-zealot-checks
diagnose-android-fret-zealot-checks: scripts/diagnose_android_fret_zealot_checks.py
	python3 scripts/diagnose_android_fret_zealot_checks.py
.PHONY: diagnose-fret-zealot-auto-sender
diagnose-fret-zealot-auto-sender: scripts/diagnose_fret_zealot_auto_sender.py
	python3 scripts/diagnose_fret_zealot_auto_sender.py
.PHONY: commit-fret-zealot-batch-pacing
commit-fret-zealot-batch-pacing: scripts/commit_verified_fret_zealot_batch_pacing.py
	python3 scripts/commit_verified_fret_zealot_batch_pacing.py
.PHONY: diagnose-guitar-residue-clear
diagnose-guitar-residue-clear: scripts/diagnose_guitar_residue_clear.py
	python3 scripts/diagnose_guitar_residue_clear.py
.PHONY: diagnose-extended-chord-test-diff
diagnose-extended-chord-test-diff: scripts/diagnose_extended_chord_test_diff.py
	python3 scripts/diagnose_extended_chord_test_diff.py
.PHONY: commit-guitar-extension-recovery
commit-guitar-extension-recovery: scripts/commit_verified_guitar_extension_recovery.py
	python3 scripts/commit_verified_guitar_extension_recovery.py
.PHONY: diagnose-piano-minor-chord-case
diagnose-piano-minor-chord-case: scripts/diagnose_piano_minor_chord_case.py
	python3 scripts/diagnose_piano_minor_chord_case.py
.PHONY: test-public-multitrack-style
test-public-multitrack-style: build/analyzer_cases scripts/run_analyzer_cases_public_multitrack_style.py
	python3 scripts/run_analyzer_cases_public_multitrack_style.py
.PHONY: report-real-world-samples-process
report-real-world-samples-process: scripts/report_real_world_samples_process.py
	python3 scripts/report_real_world_samples_process.py
.PHONY: wait-real-world-samples-process
wait-real-world-samples-process: scripts/wait_real_world_samples_process.py
	python3 scripts/wait_real_world_samples_process.py
.PHONY: inspect-other-new-note-filter
inspect-other-new-note-filter:
	python3 scripts/inspect_other_new_note_filter.py

.PHONY: inspect-monophonic-other-tests
inspect-monophonic-other-tests:
	python3 scripts/inspect_monophonic_other_tests.py

