# Shared Analyzer Investigation

This note started as the shared analyzer integration baseline before the
spillover rewrite. It now records both that baseline investigation and the
current shared-engine checkpoint so future changes can be audited against the
same root cause.

## Shared API

The OBS plugin, standalone executable, and test harnesses all call:

```cpp
mao::AnalysisEngine::analyze(const float *samples,
                             std::size_t count,
                             const mao::AnalysisSettings &settings,
                             const char *source_name,
                             uint64_t dropped_windows)
```

`AnalysisSettings` now contains an explicit `AnalysisInputMode`. `Auto` remains
as a backward-compatible source-name adapter for direct analyzer callers and
older tests, but OBS and the standalone monitor set `FullMix` explicitly because
they analyze finished mixer/speaker audio.

The fixed analysis window is `mao::kAnalysisWindow == 4096` samples.

## Frontend Callers

### OBS Plugin

`src/plugin.cpp` has two analyzer paths:

* `publish_filter_ready()` constructs a temporary `AnalysisEngine` and calls
  `analyze(nullptr, 0, ...)` to publish the initial "filter ready" snapshot.
* `analyzer_worker()` owns one persistent `AnalysisEngine` per filter instance
  and calls `analyze()` on copied audio windows.

OBS sample rate comes from `obs_get_audio_info()`, defaulting to `48000` when
OBS does not report one. The filter downmixes available audio planes into one
mono ring buffer and copies the latest 4096 samples to the worker.

The hop interval is controlled by the `update_ms` property. The default is
`50 ms`, clamped to at least `20 ms`; the stored hop is:

```text
hop_samples = sample_rate * update_ms / 1000
analysis_interval_seconds = hop_samples / sample_rate
```

The source name passed to the analyzer is the parent audio source name when the
filter has one. If direct filter audio is not available, the master-audio
fallback passes the literal source label `OBS MIX`.

No blocking analyzer work runs in the OBS audio callback. The callback only
updates the ring buffer and wakes the worker when a hop is ready.

### Standalone Executable

`src/standalone.cpp` has three analyzer paths:

* `run_self_test()` creates one local engine and feeds repeated synthetic
  keyboard frames.
* `StandaloneAnalyzer` constructs one persistent `AnalysisEngine`, first calls
  `analyze(nullptr, 0, ...)`, then reuses the same engine for every hop.
* The live/file main loop feeds samples into `StandaloneAnalyzer`.

Standalone defaults:

```text
sample_rate = 48000
update_ms = 50
hop_samples = sample_rate * update_ms / 1000
analysis_interval_seconds = update_ms / 1000
window = 4096 samples
source_name = STANDALONE
```

For file input, ffmpeg decodes to mono `f32le` at the configured sample rate and
the source name becomes `STANDALONE FILE` unless `--source` is provided.

For live speaker monitoring, the program first looks for an SDL output
monitor/loopback device. If none is found and output monitoring is preferred, it
uses ffmpeg Pulse/PipeWire capture from `@DEFAULT_MONITOR@` and names the source
`SPEAKER MONITOR`. If that path is not used, it opens an SDL capture device and
uses the device name or `SDL CAPTURE DEFAULT`.

The standalone monitor analyzes a complete mono speaker/capture mix, not
isolated instrument channels.

### Tests And Dataset Harnesses

The deterministic smoke and case tests call the shared analyzer directly:

* `tests/analyzer_smoke.cpp`
* `tests/analyzer_cases.cpp`
* `tests/analyzer_test_utils.hpp`

`tests/analyzer_test_utils.hpp` uses a default `48000 Hz` sample rate, a
4096-sample buffer, and `analysis_interval_seconds = 0.25`.

Real/dataset harnesses also call the same shared analyzer:

* `tests/analyzer_urmp.cpp`
* `tests/analyzer_musicnet.cpp`
* `tests/analyzer_egmd.cpp`
* `tests/analyzer_guitarset.cpp`
* `tests/analyzer_maestro.cpp`
* `tests/analyzer_multtipop.cpp`

Those harnesses read fixture WAV sample rates and set `settings.sample_rate`
accordingly. Full-mix truth gates such as URMP mix/summed-mix, MusicNet,
MulTTiPop, and E-GMD now set `AnalysisInputMode::FullMix` explicitly. Focused
single-instrument gates set isolated modes where available, such as GuitarSet
using `IsolatedGuitar` and MAESTRO using `IsolatedKeyboard`. Older direct case
tests still exercise `Auto` as the backward-compatible source-name adapter.

## Shared Logic Confirmation

OBS and standalone both converge on `AnalysisEngine::analyze`, so note probing,
tuning gates, temporal note smoothing, timbre filtering, drum detection, root
tracking, and chord stabilization are shared. The renderer only displays the
resulting `AnalysisSnapshot`; it does not perform instrument classification.

The failure mode therefore belongs in the shared analyzer first. OBS routing,
overlay selection, and standalone capture device choice can change which audio
is fed into the analyzer, but they do not explain identical spillover behavior
when both paths analyze the same mixed audio.

## Original Baseline Spillover Paths

The `v0.1` baseline had the architecture targeted by the rewrite:

* Input mode is inferred from free-form `source_name` strings.
* One shared pitch-power array is scanned independently by bass, keyboard,
  guitar, vocal, and other processing.
* Mixed-source keyboard, guitar, and other rows each build their own timbre mask
  from the same `note_powers` / `detection_note_powers` arrays.
* `process_other()` force-allows MIDI notes `73..kOtherMaxMidi` in mixed-source
  mode, so high notes can enter `Other` without ownership evidence.
* `process_vocal()` accepts a single strongest note in the vocal range for mixed
  sources without a separate vocal-evidence stage.
* `tracked_note_active(int midi)` checks whether a MIDI note is active in any
  instrument row and uses that to relax tuning for every row.
* Instrument-specific chords are detected from instrument note grids that may
  already contain duplicated mixed-spectrum candidates.
* Root detection consumes bass notes and instrument chord labels from the
  current snapshot, so weak or duplicated low-note evidence can bias the root.

## Current Rewrite Checkpoint

The current shared analyzer has moved the central architecture away from those
baseline paths:

* `AnalysisSettings::input_mode` selects `FullMix` or an isolated instrument
  mode before any note routing happens.
* `src/plugin.cpp` and `src/standalone.cpp` set `FullMix` explicitly for OBS
  filter/master audio and live/file standalone analysis.
* Full-mix analysis builds one `FullMixOwnership` result from shared pitch
  candidates. Each candidate receives one confident owner or becomes
  `Ambiguous`; the same mixed-spectrum candidate is not intentionally copied
  into keyboard, guitar, vocal, and other rows.
* Full-mix ownership now carries explicit per-note evidence: spectral level,
  pitch confidence, harmonicity, harmonic-fit residual, spectral centroid,
  spectral slope, local spectral noise, normalized ownership scores, and final
  owner confidence. Simultaneous high-note clusters suppress vocal ownership so
  instrumental chords do not become monophonic vocal guesses. Single high notes
  also require a clean sustained vocal-like partial profile before they can
  enter the vocal row, so piano-like upper notes remain global or ambiguous
  evidence instead of automatic vocal detections.
* `AnalysisSnapshot` exposes `global_chord` and `ambiguous_notes`. Full-mix
  chord detection uses global chroma, while instrument-specific chords are
  secondary and are based on owned notes.
* Full-mix bass detection now uses a bass-specific candidate score with
  harmonic support, octave-error suppression, and a confidence gate against the
  strongest low-mid candidate. A bass pitch class is exposed to global chord and
  root logic only after the displayed bass note is accepted, and the bass-root
  hint only recovers a missing global chord rather than replacing a valid
  no-hint harmonic-context chord.
* Tuning hysteresis checks the active input mode, so a note tracked in one
  isolated mode does not relax tuning thresholds for unrelated instrument rows.
* Empty input/status snapshots reset the full analyzer state for the current
  source, including root, tempo, drum, note, and chord history. This prevents a
  restarted frontend from inheriting stale analysis from the previous capture
  stream.
* Instrument-specific chord recovery uses short-lived analytical chord-note
  trackers. Those trackers are separate from the longer visual note envelopes,
  so a fading note highlight does not keep producing chord evidence.
* Chord scoring now records a candidate margin and uncertainty flag. Barely
  valid low-confidence candidates are suppressed when an incompatible template
  is too close, and same-root extensions only replace a simpler chord when the
  added tone has enough analytical weight.
* Dataset gates now report precision, contamination, confusion, octave-error,
  false-row, and global/per-instrument chord metrics instead of union recall
  alone for the configured real-data paths that have enough truth data.

Remaining limitations are still heuristic: reliable per-instrument
transcription from a finished stereo mix cannot always be achieved without
optional delayed source separation. The current real-time path keeps separation
bounded and deterministic, and ambiguous ownership is preferred over confident
cross-row duplication.
