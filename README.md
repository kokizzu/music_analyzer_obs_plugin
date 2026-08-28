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
