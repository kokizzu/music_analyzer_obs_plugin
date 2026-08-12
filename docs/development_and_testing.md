# Development and testing

This page contains the Make targets, fixture setup, and measured detector workflow that are intentionally kept out of the user-facing root README.

## Core checks

Run the normal regression suite with:

```sh
make test
```

Useful narrower loops are:

```sh
make test-parallel
make test-detector-samples
make test-detector-samples-full
make test-real-note-samples-full-mix
make test-guitar-chord-mix-samples
```

Set `PARALLEL_TEST_JOBS=8` (or another appropriate value) to fan out compatible fixture checks. Do not use `make install-user` as part of testing while OBS is running.

## Measured detector workflow

1. Refresh the relevant real-audio gate and attribute TSV.
2. Update the tracked [accuracy dashboard](detection_accuracy_report.md):

   ```sh
   make update-detection-accuracy-report
   ```

   The report always includes the deterministic full-mix real-note sample metrics. When cached Guitar Chord Mix, Guitar-TECHS chord, or full GAPS guitar attribute TSVs are present, it also includes their exact chord-window and expected guitar pitch-class totals without rerunning audio.

3. Print analyzer traits and mine candidate patterns without changing logic:

   ```sh
   make analyze-real-note-attributes
   make find-real-note-focused-row-confusion-patterns
   make find-real-note-focused-visual-row-confusion-patterns
   make find-real-note-octave-displacement-patterns
   make inspect-detector-coverage-candidates
   ```

4. Change the analyzer only when a candidate has independent coverage and does not alter protected passing rows.
5. Re-run affected note/chord/instrument gates, update the dashboard whenever a verified number changes, and include both in the same commit.

The cached audit helpers avoid rebuilding sharded audio analysis when only the inspection scripts changed:

```sh
make detector-improvement-status-cached
make detector-improvement-coverage-cached
make detector-improvement-audit-cached
```

## Analyzer modes and selected gate variables

`FullMix` is the mode used by the OBS plugin and the standalone speaker monitor. Full-mix per-instrument rows are conservative estimates. Ambiguous notes can still support the global chord, but a candidate is not copied into multiple instrument rows merely to increase recall. The primary chord for OBS and standalone output is the shared global chord.

`IsolatedBass`, `IsolatedGuitar`, `IsolatedKeyboard`, `IsolatedVocal`, and `IsolatedOther` are for real single-instrument stems. Source-name hints such as `guitar`, `piano`, or `vocal` are only a compatibility adapter for callers that do not set an explicit input mode.

Frequently adjusted real-data thresholds include `MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT`, `MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT`, `MUSIC_ANALYZER_MULTTIPOP_MIN_PRECISION_PERCENT`, `MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT`, `MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT`, `MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT`, `MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT`, and `MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT`. Their target-specific meanings and defaults are in [real-audio dataset candidates](real_audio_dataset_candidates.md).

## Corpus storage and real-data gates

Large downloaded archives use the external store configured by:

```sh
make configure-instrument-sample-store
make inspect-instrument-sample-store
make inspect-sample-build-migration
make migrate-sample-build-directories
```

`build/InstrumentSamples` is a safe link to `/media/kyz/sshflashtor/InstrumentSamples`. The migration target moves every build-level sample/corpus and audio-fixture directory into `/media/kyz/sshflashtor/InstrumentSamples/build-cache/`, byte-verifies it, then replaces the old build directory with a symlink. Android, Gradle, dependencies, and generic build outputs stay local. `MUSIC_ANALYZER_DATASET_ROOT` defaults to the external store for real-data preflights.

Use the combined dataset preflight after adding an official dataset:

```sh
make inspect-real-goal-20
make test-real-goal-20
```

URMP remains the required real same-song stem/mix/MIDI gate. It expects a dataset root containing the 44 piece folders and `AuMix`, `AuSep`, `Notes`, and `Sco` files. The official site still routes its advertised 12.5-GB package through a registration form, but the public Kaggle mirror is available through `make download-real-urmp`; then run `make prepare-real-urmp test-real-urmp`. Its resumable, ZIP-validated archive and non-overwriting extraction are kept at `build/InstrumentSamples/urmp/`, which resolves to the external sample store. After extraction, `make analyze-real-urmp-traits` refreshes the full offline measurement without revalidating the large archive; `make analyze-real-urmp-miss-traits summarize-real-urmp-miss-traits` captures a bounded candidate-trait sample for missed isolated notes and chord opportunities. Neither target plays audio. See [real-audio dataset candidates](real_audio_dataset_candidates.md) for the source catalogue and the scope/limitations of optional MusicNet, GuitarSet, MedleyDB, MUSDB, Slakh, and other fixtures.

For the open CC-BY MusicNet release, run `make inspect-real-musicnet-remote` to check the current Zenodo metadata, then `make download-real-musicnet` and `make prepare-real-musicnet`. The resumable archive, metadata, MIDI download, and extracted corpus are stored at `build/InstrumentSamples/musicnet` (the external sample store); the archive is validated before being accepted. `make inspect-downloaded-real-musicnet`, `make test-downloaded-real-musicnet-20`, and `make test-downloaded-real-musicnet-full` use that extracted root directly.

## Fixture-specific commands

The common data-backed checks are:

```sh
make test-drum-real-world-samples
make test-instrument-samples
make test-guitar-techs-samples
make test-guitar-techs-chord-samples
make test-gaps-guitar-samples-full
make test-guitar-chord-mix-samples
make test-real-guitarset-20
make test-real-maestro-20
make test-real-egmd-20
```

Some targets download public fixture archives; inspect their source and storage variables in the Makefile first. Local external-data paths and optional datasets are skipped when unavailable rather than treated as a passing quality result.

`make analyze-medley-solos-attributes` writes `build/medley_solos_attributes.tsv` after the real Medley-solos archive is available. Each row records the expected family, source instrument, analysis-buffer position, detected family rows, row confidences, and rendered labels. Use it to mine independent sax, violin, woodwind, piano, guitar, and vocal ownership evidence; it does not play audio.
