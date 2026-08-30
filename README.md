<p align="center">
  <img src="assets/music-analyzer-icon.png" width="180" alt="Music Analyzer spectrum, fretboard, and keyboard icon">
  <img src="assets/music-analyzer-bass-guitar-icon.png" width="180" alt="HalfMusic Analyzer icon">
</p>

# Music Analyzer OBS Plugin

An OBS Studio audio filter and overlay that detects music activity in real time and visualizes:

- drums, bass, keyboard, guitar, vocals, and other instruments;
- fading note highlights, chord labels, root, sustain, and BPM;
- a complete overlay plus the compact HalfMusic Analyzer layout.

It is designed for live mixed audio. Instrument rows are intentionally conservative: uncertain notes may be shown as ambiguous rather than confidently assigned to the wrong instrument.

## Install and use in OBS

Build and install the plugin:

```sh
make install-user
```

Restart OBS, then add **Music Analyzer Filter** to the audio source that carries your music. Add **Music Analyzer Overlay** as a source in the scene. If the overlay says `ADD MUSIC ANALYZER FILTER TO AN AUDIO SOURCE`, it has not yet received data from a filtered audio source.

The usual input is an OBS mixer channel such as Desktop Audio, an Audio Output Capture source, an Audio Input Capture source, or a Media Source.

## Standalone and Android

Build the desktop standalone windows with:

```sh
make standalone
make standalone-bass-guitar
```

Build the Android variants after local SDK setup with:

```sh
make setup-android
make android
```

## Documentation

- [Real-audio detection accuracy](docs/detection_accuracy_report.md) — current, reproducible `accurate / total` coverage for the full-mix note corpus.
- [Development and testing](docs/development_and_testing.md) — fixture setup, corpus storage, detector measurement, and regression workflows.
- [Audacious overlay integration](docs/audacious_overlay_integration.md) — title display, fallback behavior, and renderer integration details.
- [Basic Pitch Vocal fusion](docs/basic_pitch_vocal_fusion.md) — optional local ONNX configuration and its conservative same-note gate.
- [Real-audio dataset candidates](docs/real_audio_dataset_candidates.md) — supported evaluation corpora and their limits.

## Performance

The plugin uses bounded DSP heuristics rather than a stem-separation model. Audio is buffered through a fixed ring buffer, analyzed on a worker thread, and rendered into one reusable RGBA texture. The OBS audio callback avoids allocation after source creation and stale analysis windows are dropped rather than queued.
## External real-audio fixtures

Large real-audio fixtures are intentionally kept out of Git. The repository links
`build/InstrumentSamples` to the configured external fixture store. The Sneakybass
importer stages the CC0 double-bass source there, creates a labelled manifest, and
never copies WAV data into the checkout:

```sh
make plan-sneakybass-fixture
make prepare-sneakybass-fixture
make verify-sneakybass-fixture
```

The University of Iowa Musical Instrument Samples Steinway Piano corpus extends
the full-mix keyboard coverage with 108 labelled C3-B5 notes at `pp`, `mf`, and
`ff`. The original AIFF files are converted to external FLAC storage; a compact
three-second PCM WAV cache is derived locally only for the existing WAV-based
test runner. No audio asset is added to Git.

```sh
make plan-iowa-piano-midrange-fixtures
make probe-iowa-piano-midrange-fixtures
make start-iowa-piano-midrange-fixtures
make status-iowa-piano-midrange-fixtures
make verify-iowa-piano-midrange-fixtures
make test-iowa-piano-midrange-samples
```

The source is the [University of Iowa Musical Instrument Samples Piano collection](https://theremin.music.uiowa.edu/MISPiano.html).

The official MedleyDB sample archive provides a real multitrack vocal mix with
continuous F0 annotations. The fixture workflow selects semitone-stable windows
from the annotated `LizNelson_Rainfall` female-singer melody and extracts ten
compact full-mix excerpts. The archive and derived audio remain in the external
fixture cache; MedleyDB audio is licensed CC BY-NC-SA.

```sh
make probe-medleydb-sample
make start-medleydb-sample-download
make status-medleydb-sample-download
make inspect-medleydb-sample-archive
make inspect-medleydb-vocal-annotations
make apply-medleydb-vocal-mix-fixtures
make verify-medleydb-vocal-mix-fixtures
make test-medleydb-vocal-mix
make test-medleydb-vocal-stem
```

The matched isolated melody stem uses the same annotated windows as the mix. Its
90% floor separates native Vocal candidate recall from mix masking; the mix has
an 80% floor because it retains the concurrent singers and guitars.

The source is the [MedleyDB sample archive](https://zenodo.org/records/1438309) and its [dataset documentation](https://medleydb.weebly.com/description.html).

Run the isolated, sharded analyzer audit and inspect its persisted recall and raw
tuning evidence with:

```sh
make analyze-sneakybass-fixture
make report-sneakybass-fixture-audit
make report-sneakybass-fixture-attributes
```

The importer currently maps 642 raw Sneakybass WAV samples. The audit limits its
detector expectation to the analyzer's established bass display range, MIDI 28-63;
the complete external corpus remains available for future range work.
