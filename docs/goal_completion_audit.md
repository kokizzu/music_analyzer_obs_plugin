# Shared Analyzer Goal Completion Audit

This audit maps the cross-instrument-spillover goal to current repository
evidence. It is intentionally evidence-based: each item lists the source,
test, documentation, or command that proves the current state.

## Scope And Investigation

Status: verified.

Evidence:

* `docs/shared_analyzer_investigation.md` lists every
  `AnalysisEngine::analyze` caller group: OBS plugin, standalone executable,
  deterministic tests, and dataset harnesses.
* The same document records OBS and standalone sample rate defaults, fixed
  `4096`-sample window, hop interval, source names, engine lifetime, and
  whether the standalone path receives a complete speaker/capture mix.
* `src/plugin.cpp` and `src/standalone.cpp` both call the shared
  `AnalysisEngine`; the renderer consumes only `AnalysisSnapshot`.

## Architecture Requirements

Status: verified.

Evidence:

* Explicit input mode: `src/analyzer.hpp` defines `AnalysisInputMode` and
  `AnalysisSettings::input_mode`.
* Frontend integration: `src/plugin.cpp` and `src/standalone.cpp` set
  `AnalysisInputMode::FullMix` for OBS and standalone mixer/speaker audio.
* Global chord and ambiguity: `AnalysisSnapshot` exposes `global_chord` and
  `ambiguous_notes`.
* Shared candidate extraction: `src/analyzer.cpp` builds one
  `FullMixOwnership` from bounded `NoteCandidateList` storage.
* Central ownership: full-mix routing compares ownership probabilities, writes
  candidates into at most one confident row, and writes uncertain candidates to
  `ambiguous`.
* Instrument-local tracking: `tracked_note_active(AnalysisInputMode, int)` and
  separate row/full-mix tracking arrays avoid using one row's note state to
  relax every other row.
* Evidence-only chords: instrument and global chord stabilizers use short-lived
  analytical chord-note tracking, not the longer visual display fade.

## Removed Spillover Behavior

Status: verified.

Evidence:

* `tests/inspect_real_goal_coverage.py` rejects legacy mixed-source row scans
  and `allowed_midis = mixed_source`-style fallback wiring.
* `tests/analyzer_cases.cpp` contains regressions for piano-only full mix,
  guitar-only full mix, high instrumental notes, same-MIDI timbre ambiguity,
  sparse `Other` confirmation, and vocal temporal confirmation.
* `tests/analyzer_cases.cpp` checks that the same MIDI candidate is not
  duplicated across confident full-mix owner rows without explicit supporting
  evidence.

## Chord And Root Accuracy

Status: verified.

Evidence:

* `tests/analyzer_cases.cpp` covers weak-bass root bias, full-mix inversion
  root guidance, keyboard inversion handling, and CAGED guitar root
  independence.
* Required chord transitions are covered for C->G, C->Am, Dm7->G7, Csus4->C,
  C->Cmaj7, Cmaj7->C, and G->Em.
* `src/analyzer.cpp` tracks chord candidate confidence, margin, uncertainty,
  simplified full-mix extensions, and a hold/switch stabilizer.
* Single-note full-mix regressions require keyboard, guitar, and other chord
  labels to remain empty rather than inventing per-instrument chords.

## Reset And Real-Time Safety

Status: verified.

Evidence:

* `AnalysisEngine::reset()` and empty-input/status snapshots share the analyzer
  reset path.
* `tests/analyzer_cases.cpp` covers explicit reset, empty-input reset,
  source-change reset, sample-rate reset, and input-mode-change reset.
* `docs/shared_analyzer_investigation.md` documents that OBS audio callbacks
  only buffer/wake the worker; analyzer DSP runs outside the callback path.
* The standalone and OBS build isolation checks keep SDL/standalone-only code
  out of the OBS plugin target.

## Tests And Metrics

Status: verified.

Evidence:

* Deterministic `analyzer_cases` covers spillover, contamination, ambiguity,
  chord transitions, frontend equivalence, reset behavior, and root behavior.
* `tests/analyzer_urmp.cpp` reports isolated precision, recall, F1,
  contamination, octave-error rate, ambiguous assignment count, row metrics,
  confusion matrix, and global chord precision/recall/F1.
* `tests/analyzer_guitarset.cpp` and `tests/analyzer_maestro.cpp` enforce the
  stated 90% row precision/recall, <=5% contamination, <=5% false-row windows,
  and >=85% isolated chord precision targets for real guitar and real piano
  when those datasets are configured.
* `tests/analyzer_musicnet.cpp`, `tests/analyzer_multtipop.cpp`, and
  `tests/analyzer_egmd.cpp` report precision/recall/F1-style real-data metrics
  where the available truth supports them.
* `make test` exercises the committed 20-piece/20-recording generated fixture
  gates for direct-fit/URMP-shaped multitrack data, MusicNet, MedleyDB, MUSDB18,
  Slakh2100, ChoralSynth, CocoChorales, SynthSOD, Vocal Ensemble F0 Aggregate,
  prepared multitrack, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD paths.

## Documentation Deliverables

Status: verified.

Evidence:

* `README.md` explains full-mix limitations, isolated modes, ambiguous
  ownership, global versus per-instrument chords, expected OBS setup, expected
  standalone setup, and real-data gate commands.
* `docs/shared_analyzer_investigation.md` contains the final implementation
  summary: confirmed root causes, architecture changes, selected algorithms,
  before/after measurement approach, and remaining heuristic limitations.
* Optional delayed source separation is documented as a future extension, not a
  required dependency for the normal OBS or standalone builds.

## Verification Commands

Latest green checkpoint commands:

```text
make inspect-real-goal-coverage
make test
make all
make test-standalone
```

The remote `v0.1` tag is intentionally kept at the historical release point and
is pushed before branch checkpoints.
