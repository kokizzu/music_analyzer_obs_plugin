# Music Analyzer OBS Plugin

Native OBS Studio plugin that analyzes a music mix and displays an instrument-oriented overlay:

- Drums: bass drum/kick, snare, hi-hat, crash, toms, ride, and rightmost rim/side-stick one-second scrolling hit charts
- Bass: detected note, with conservative full-mix switching so one-frame low-note spikes do not immediately replace the current bass
- Keyboard: three-row piano view covering C1-B6 in two-octave bands, with lower notes folded into octave 1, higher notes folded into octave 6, and detected keys highlighted
- Vocal and other instruments: two-row 12-note octave matrix with active octaves shown as colored text
- Guitar: standard-tuning six-string fretboard view with open string plus frets 1-15 highlighted from detected notes
- Note highlights fade with detected velocity/amplitude so quiet or sustaining notes are dimmer instead of full intensity
- Chord labels use short-lived analytical note evidence separate from the longer visual note fade, so old highlights do not keep forming chords
- Notes outside the chromatic tuning window, about +/-9 cents from the equal-tempered center, are ignored instead of rounded to the nearest note
- Keyboard, guitar, and other instruments: compact chord labels; vocal stays note-only
- `SUSTAIN` keeps the recent sustained/high-confidence chord or note; chord sustain is simplified to plain major/minor labels such as `C` or `Dm`, and low-level decaying highlights do not refresh it
- Keyboard chord labels are resolved from filtered notes inside a plausible hand-span cluster, so far-apart bass/melody notes are not collapsed into impossible hand chords
- Guitar chord labels are resolved from the filtered fretboard notes with CAGED-style voicing preference, so full-mix bass/root hints do not rename the guitar shape
- Full-mix routing exposes a primary global chord in the shared analyzer snapshot, while instrument rows remain conservative estimates
- Explicit isolated input modes keep single-instrument sources in their matching row instead of filling unrelated keyboard, guitar, vocal, or other rows
- Full-mix ownership uses shared note evidence with harmonic fit, harmonic balance, spectral centroid/slope, local spectral noise, periodicity, onset/decay/stability history, and simultaneous-onset grouping before assigning a note to an instrument row; vocal candidates and sparse `Other` candidates also need short temporal confirmation before becoming row notes
- Source-name hints remain as a compatibility adapter for tests and direct analyzer use: `guitar`, `key`, `piano`, `organ`, `synth`, `brass`, `horn`, `violin`, and `string` resolve to isolated modes when the caller does not set an input mode explicitly
- Root: rolling 15-second root candidates with confidence, using the full-mix global chord plus confidence-gated bass evidence so inversions do not rename the harmonic root; the primary root is held until sustained modulation or silence
- BPM: estimated tempo and confidence are shown at the bottom right when rhythmic transients provide enough evidence
- Chords: compact major, minor, lowercase power-chord `pow`, sus2, sus4, diminished, augmented, 6, minor 6, dominant 7, major 7, minor 7, diminished 7, half-diminished, add9, 9, major 9, and minor 9 labels such as `C`, `Dm`, `Cpow`, `Cdim`, `Caug`, `C6`, `Dm6`, `G7`, `Cmaj7`, `Dm7`, `Cdim7`, `Bm7b5`, `Cadd9`, `G9`, `Cmaj9`, and `Dm9`
- Equivalent chord names for the same detected pitch classes are shown together, such as `Csus2=Gsus4` or `Dm7=F6`
- Explicit instrument sources use the full chord template set; mixed sources keep conservative chord labels to avoid false extensions from other instruments
- Bass + Guitar layout: a smaller renderer that keeps drums, bass, guitar, root, and BPM while omitting keyboard, vocal, and other rows

The analyzer is designed for real-time OBS use. It uses bounded DSP heuristics rather than a large ML stem-separation model: audio is downmixed into a fixed ring buffer, analyzer windows are copied to a worker thread at a configurable interval, and the OBS audio callback returns immediately after lightweight buffering. By default, OBS and standalone analyze a rolling 100 ms audio window every 50 ms. The old 4096-sample window is still available as a legacy option. The overlay source renders a single reusable RGBA texture.

OBS and the standalone speaker-monitor executable explicitly analyze their inputs as `FullMix`, because they receive finished mixer/speaker audio. The shared analyzer still supports isolated modes for direct analyzer callers and tests; those modes are intended for real isolated bass, guitar, keyboard, vocal, or other-instrument stems.

## Analyzer Modes and Limits

`FullMix` is the mode used by the OBS plugin and the standalone speaker monitor. It expects a finished music mix from an OBS mixer channel, source filter, speaker monitor, file, or raw PCM stream. In this mode, the analyzer extracts pitch candidates once, assigns each candidate to at most one confident instrument owner, or marks it as ambiguous when the evidence is not strong enough. Ambiguous notes can still support the global chord, but they are not duplicated into keyboard, guitar, vocal, and other rows just to improve recall.

Full-mix per-instrument rows are conservative estimates. A finished stereo mix cannot always be separated reliably with bounded real-time DSP, so a missing uncertain row note is preferred over a confident wrong instrument. For precise per-instrument transcription of crowded mixes, run a separate stem separator before the analyzer and feed real isolated stems to analyzer callers that support isolated modes.

The primary chord for OBS and standalone output is the shared global chord. Keyboard, guitar, and other chord labels are secondary and require confidently owned notes for that row. Full-mix chord labels intentionally stay simpler than isolated-source labels when extension evidence could come from another instrument, so a full-mix `G7` may be displayed as `G` while isolated keyboard/guitar/other stems can use the full template set.

`IsolatedBass`, `IsolatedGuitar`, `IsolatedKeyboard`, `IsolatedVocal`, and `IsolatedOther` are for real single-instrument stems. In isolated modes, only the matching row is populated, vocal remains note-only, and input-mode changes reset incompatible tracking state. Source-name hints such as `guitar`, `piano`, or `vocal` are only a compatibility adapter when a direct analyzer caller leaves the input mode on `Auto`; OBS and standalone do not rely on those labels for speaker/mixer audio.

## OBS Usage

1. Build and install the plugin to your OBS user plugin directory:

   ```sh
   make install-user
   ```

3. Restart OBS.
4. Pick the OBS audio channel that carries the music.
   - If you use the default OBS mixer, use `Desktop Audio`, `Mic/Aux`, or whichever mixer channel meter moves with the music.
   - If you use a source in the `Sources` list, use `Audio Output Capture`, `Audio Input Capture`, or `Media Source`.
5. Add the analyzer filter to that audio channel:
   - In `Audio Mixer`, open the gear/three-dots menu for the channel, then choose `Filters`.
   - Or in `Sources`, right-click an audio source and choose `Filters`.
   - Under `Audio Filters`, click `+`, choose `Music Analyzer Filter`, then click `OK`
6. Add the on-screen overlay:
   - In `Sources`, click `+`
   - Choose `Music Analyzer Overlay`

If the overlay says `ADD MUSIC ANALYZER FILTER TO AN AUDIO SOURCE`, the overlay is loaded but it has not received analyzer data yet. Add `Music Analyzer Filter` to the actual music/audio source, not to the overlay source.

## Overlay Diagnostics

The small status text at the top is for checking whether the analyzer is receiving and processing audio:

- `RMS`: current overall loudness of the analyzer window.
- `LOW`, `MID`, `HIGH`: rough percentage split of detected low, mid, and high-frequency energy.
- `AGE`: seconds since the overlay last received a new analyzer snapshot. If this keeps increasing while music is playing, the visualizer is not receiving fresh analyzer data. Stale-age redraws are throttled so the overlay does not repaint continuously only for this counter.
- `DROP`: analyzer windows skipped because a newer audio window arrived before the worker consumed the previous one.
- `CPU`: process CPU usage sampled about once per second. In OBS this is the OBS process, including the plugin; in standalone and Android this is the app process. `100%` means roughly one full CPU core.
- `RAM`: process RAM usage in MB. In OBS this is the OBS process, including the plugin; in standalone and Android this is the app process.
- `BPM`: bottom-right estimated tempo. The percentage is confidence from recent transient timing, so sparse intros, rubato, or weak drums may show `BPM --` or a low-confidence estimate.

`Analyzer interval (ms)` controls how often a new rolling window is evaluated. The default is 50 ms. `Analysis window (ms)` controls the amount of recent audio inside each evaluation window. The default is 100 ms, so consecutive evaluations overlap. Enable `Use legacy 4096-sample analysis window` to switch back to the original fixed-size window.

## Standalone Usage

Build the standalone executable:

```sh
make standalone
```

This builds both desktop standalone binaries:

- `build/music-analyzer-standalone`: complete layout
- `build/music-analyzer-bass-guitar`: smaller Bass + Guitar layout with drums, bass, guitar, root, and BPM

To build only the compact binary:

```sh
make standalone-bass-guitar
```

If SDL2 development headers are not installed system-wide, the Makefile downloads and extracts `libsdl2-dev` under `build/deps` for the standalone build. SDL2 is used only by the standalone binaries; the OBS plugin target does not include or link SDL.

Run live from speaker/system output. The window title includes the standalone build version as `YYYY.MMDD.HHMM.shortCommitHash`. On Linux PulseAudio/PipeWire this auto-prefers an SDL capture device named like an output `monitor` or `loopback`; if SDL does not expose one, it captures `@DEFAULT_MONITOR@` through `ffmpeg`:

```sh
build/music-analyzer-standalone
build/music-analyzer-bass-guitar
```

In live capture mode, press Space to switch to the next audio source. When more than one live source is available, the title/status source label is shown as `X/Y Name`, for example `2/4 Monitor of Built-in Audio Analog Stereo`.

The standalone window is resizable. During resize or maximize, the SDL window snaps back to the configured overlay aspect ratio and the overlay scales uniformly, using letterbox/pillarbox bars as a fallback instead of stretching the UI.

List capture devices and pick one explicitly. Output monitors are marked in the list:

```sh
build/music-analyzer-standalone --list-devices
build/music-analyzer-standalone --device "device name"
```

Use `--default-input` if you intentionally want the default microphone/aux-in capture input instead of speaker/system output.

Print the standalone build version:

```sh
build/music-analyzer-standalone --version
```

Analyze an audio file through `ffmpeg` while showing the same renderer in a standalone window:

```sh
build/music-analyzer-standalone --input /path/to/song.flac --source "song"
```

For direct float PCM input:

```sh
build/music-analyzer-standalone --raw-f32le /path/to/audio.f32 --sample-rate 48000
```

Useful options include `--width`, `--height`, `--update-ms`, `--window-ms`, `--legacy-window`, `--fps`, `--sensitivity`, and `--hold`. `--update-ms` controls how often analysis runs. `--window-ms` controls the rolling audio window length and defaults to 100 ms. `--legacy-window` switches back to the original 4096-sample analyzer window.

The complete standalone can also render the compact layout with `--layout bass-guitar`; the compact binary uses that layout by default.

## Android Usage

The Android app shares `src/analyzer.cpp` and `src/visualizer_renderer.cpp` through JNI. It has two product flavors:

- `complete`: original complete layout
- `bassGuitar`: smaller Bass + Guitar layout

Install the local Android SDK, NDK, CMake, build-tools, platform, and Gradle distribution under `build/`:

```sh
make setup-android
```

Build both APKs:

```sh
make android
```

Build one flavor:

```sh
make android-complete
make android-bass-guitar
```

The debug APKs are written under `android/app/build/outputs/apk/complete/debug/` and `android/app/build/outputs/apk/bassGuitar/debug/`.

Set up a local Android Emulator package, Android 35 Google APIs x86_64 system image, and repo-local AVD:

```sh
make setup-android-emulator
```

Start that AVD:

```sh
make android-emulator
```

Stop the emulator:

```sh
make android-emulator-stop
```

The default AVD is named `music_analyzer_api35_x86_64` and its files live under `build/android-avd`. Override `ANDROID_EMULATOR_API`, `ANDROID_EMULATOR_IMAGE`, `ANDROID_EMULATOR_ABI`, or `ANDROID_AVD_NAME` if you need a different image, for example:

```sh
ANDROID_EMULATOR_ABI=arm64-v8a make setup-android-emulator
```

Android uses `AudioRecord` with `RECORD_AUDIO`, so it captures microphone, aux-in, or USB audio input. It prefers Android's unprocessed audio source when available and falls back to default capture when the device/emulator does not expose it. Android does not generally allow ordinary apps to capture speaker/system playback directly without a separate media-projection workflow, so route speaker output into an input if you need the same behavior as the desktop speaker-monitor standalone.

Press Space or tap the Android analyzer view to cycle available Android recording inputs. The source label shows `X/Y Name` when multiple inputs are exposed by Android, for example `2/3 USB Scarlett Solo`. USB audio interfaces work when Android lists them as input devices through `AudioManager`; the app selects the active input with `AudioRecord.setPreferredDevice`.

Mic/input pass-through is not automatic on Android. The app explicitly creates an `AudioTrack` monitor stream and sends captured input to a non-speaker output when Android exposes one, preferring USB audio, wired headphones/headset, line out, then Bluetooth/HDMI. If only the built-in speaker is available, monitoring is disabled to avoid feedback, but the analyzer still uses the microphone/input.

Basic Android test flow:

```sh
make setup-android
make android-bass-guitar
adb install -r android/app/build/outputs/apk/bassGuitar/debug/app-bassGuitar-debug.apk
```

For the repo-local emulator, use:

```sh
make setup-android-emulator
make android-emulator
build/android-sdk/platform-tools/adb install -r android/app/build/outputs/apk/bassGuitar/debug/app-bassGuitar-debug.apk
```

Or build, install, and launch the compact app on the currently connected emulator/device:

```sh
make android-run
```

Explicit variants are also available:

```sh
make android-run-bass-guitar
make android-run-complete
```

To feed current desktop/speaker audio into the Android emulator as microphone input on PipeWire/PulseAudio:

```sh
make android-route-desktop-audio
```

Run that after the emulator and app are open. If Android asks for microphone permission, grant it first, then rerun the command. By default it moves the emulator recording stream to the current default speaker monitor source, such as `<default-sink>.monitor`. To use a specific source:

```sh
ANDROID_MIC_SOURCE=alsa_output.pci-0000_12_00.4.analog-stereo.monitor make android-route-desktop-audio
```

If routing stops after a song changes, the emulator likely recreated its microphone recording stream. Leave the persistent route watcher running in a separate terminal while testing:

```sh
make android-route-desktop-audio-watch
```

The watcher checks once per second by default and moves any new emulator recording stream back to the desktop monitor source. Override the poll interval with `ANDROID_ROUTE_INTERVAL=0.25` if you need faster recovery.

Connect headphones, a USB audio interface, or Bluetooth audio before launching the app. Grant microphone permission, play or speak into the selected input, and verify that the visualization updates. With a non-speaker output connected, the captured input should also be heard from that output. Without headphones or an external output, test the analyzer visually; passthrough will intentionally stay muted.

## Build

With the Makefile:

```sh
make
```

If the system OBS headers require SIMDe and `libsimde-dev` is not installed, `make` fetches and extracts that header-only package under `build/deps` without using sudo.

Build only the standalone executables:

```sh
make standalone
make standalone-bass-guitar
```

Build Android after local SDK setup:

```sh
make setup-android
make android
```

Run the analyzer tests:

```sh
make test
```

Run the focused MIDI/synthetic range regression:

```sh
make test-midi-ranges
```

Prepare and test local one-shot drum samples, defaulting to `/media/kyz/sshflashtor/DrumSamples`:

```sh
make prepare-drum-samples
make test-drum-samples
make test-drum-samples-spread
make test-drum-samples-full
```

Override `DRUM_SAMPLE_SOURCE_DIR`, `DRUM_SAMPLE_BUILD_DIR`, `DRUM_SAMPLE_LIMIT`, `DRUM_SAMPLE_SELECTION`, or set `DRUM_SAMPLE_REFRESH=1` if your sample library is elsewhere, you want a different per-category sample count or selection strategy, or you need to force a rescan of an existing complete manifest. The importer reads plain WAV files, ZIP archives, and RAR archives when `unrar` is installed. The default `DRUM_SAMPLE_SELECTION=first` local one-shot gate copies up to 160 samples per category, for 1,120 real drum samples when the configured library has enough material, and stops scanning once every category reaches the configured limit. The importer treats compact drum-machine closed/open-hat aliases such as `707oh`, `Realch1`, and `HHOD4`, plus `Hat Pedal`, as hi-hats even when they live under a generic `Cymbals` folder. The harness warms the analyzer with a neutral low-level bed instead of pitched notes, credits the expected drum if it appears across the first 50 ms analyzer hop, then keeps unrelated false-positive counts anchored to the onset frame. It prints recall, precision, false positives, a 7x7 active matrix, and a primary matrix that separates no-hit samples from saturated ambiguous strongest-label ties. The default gate also enforces `MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=20`, `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=55`, `MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RIM_RECALL_PERCENT=73`, and `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=20`, so kick/snare/cymbal/rim one-shots cannot regress into excessive whole-kit lighting, excessive false tom lighting, or lost side-stick/rim coverage. The current default gate runs in about 32.76 seconds and passes with recall/precision kick 111/160 and 111/365, snare 95/160 and 95/456, hi-hat 150/160 and 150/529, crash 158/160 and 158/474, toms 137/160 and 137/633, ride 147/160 and 147/453, and rim 139/160 and 139/309.

`make test-drum-samples-spread` is the faster broad-data tuning loop. It uses deterministic spread selection across plain-WAV source folders and intentionally passes `--no-archives`, so it avoids slow ZIP/RAR extraction on mounted sample libraries. Override `DRUM_SAMPLE_SPREAD_BUILD_DIR`, `DRUM_SAMPLE_SPREAD_LIMIT`, `DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT`, or `DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT` for this target. The default spread gate now enforces at least 40% recall and 15% precision per category. On the current local drum library, the bounded spread gate prepares 857 real one-shots in about 23.40 seconds: kick=160, snare=160, hi-hat=160, crash=120, tom=160, ride=44, and rim=53. Current spread recall/precision is kick 100/160 and 100/290, snare 109/160 and 109/331, hi-hat 152/160 and 152/381, crash 118/120 and 118/304, toms 129/160 and 129/502, ride 41/44 and 41/253, and rim 44/53 and 44/175.

`make test-drum-samples-full` uses `DRUM_SAMPLE_FULL_BUILD_DIR`, `DRUM_SAMPLE_FULL_LIMIT`, `DRUM_SAMPLE_FULL_MIN_RECALL_PERCENT`, and `DRUM_SAMPLE_FULL_MIN_PRECISION_PERCENT`. It is intentionally separate from `make test` because the current local library audit found kick=5,500, snare=4,684, hihat=2,123, crash=561, tom=3,915, ride=352, and rim=500 one-shots; two unreadable snare WAVs are skipped by the harness. Complete manifests are reused unless `DRUM_SAMPLE_REFRESH=1` is set, so repeated full sweeps do not re-extract ZIP/RAR members before the analyzer phase. The cached full analyzer phase currently takes about 429.37 seconds and enforces at least 35% recall plus a 3% precision floor. Current full-library recall/precision is kick 2,919/5,500 and 2,919/5,760, snare 3,303/4,682 and 3,303/5,794, hi-hat 2,055/2,123 and 2,055/5,769, crash 554/561 and 554/2,986, toms 2,680/3,915 and 2,680/9,494, ride 336/352 and 336/2,775, and rim 418/500 and 418/2,129. Treat this as a broad diagnostic benchmark for improving drum classification, not a precision claim. `make test-real-world-samples-full` also runs this full local drum sweep when `DRUM_SAMPLE_SOURCE_DIR` exists, and skips it otherwise so the full internet-backed benchmark stays portable.

Prepare and test MIDI-rendered single-note fixtures for piano, guitar, bass, synth, strings, vocals, and GM drum kits:

```sh
make prepare-instrument-samples
make test-instrument-samples
```

This target renders build-local WAV fixtures under `build/piano_samples`, `build/guitar_samples`, `build/bass_samples`, `build/synth_samples`, `build/strings_samples`, `build/vocals_samples`, and `build/drum_kit_samples` using FluidSynth. By default it uses the system FluidR3 GM SoundFont, or downloads/extracts the internet-sourced `fluid-soundfont-gm` package into `build/instrument_sample_sources` if needed. The default fixture target is at least 1000 one-note files per family; the current FluidR3 GM set renders 1024 piano, 1040 guitar, 1030 bass, 1080 synth, 1116 strings, 1020 vocals, and 1008 GM drum-kit samples. The gate currently runs 7,384 checks in about 163.75 seconds, including same-pitch C4 source-mode checks across piano, guitar, bass, synth, strings, and vocals plus same-pitch full-mix C and C-E-G chord checks from rendered samples. Override `INSTRUMENT_SAMPLE_TARGET_PER_FAMILY`, `INSTRUMENT_SAMPLE_JOBS`, `INSTRUMENT_SAMPLE_SOUNDFONT`, `INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE`, `INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY`, or `INSTRUMENT_SAMPLE_DRUM_KITS` to change the rendered fixture set. Known non-one-note SoundFont cells are excluded from the one-note manifests and recorded in `build/instrument_sample_exclusions.tsv` with reasons. FluidR3 GM is MIT-licensed; only generated files under `build/` are written.

Download and test internet-sourced real-world sample fixtures:

```sh
make test-real-note-samples
make test-guitar-fretboard-note-samples
make test-hf-drum-kit-samples
make test-downloaded-guitarset
make analyze-guitarset-misses
make test-guitar-techs-samples
make test-guitar-chord-mix-samples
make test-philharmonia-samples
make test-philharmonia-samples-full
make test-iowa-piano-samples
make test-iowa-bass-samples
make test-idmt-bass-lines-samples
make test-tinysol-samples
make test-vocadito-samples
make test-real-world-samples
make test-real-world-samples-full
```

`make test-real-note-samples` downloads the public [NSynth test split](https://magenta.tensorflow.org/datasets/nsynth) into `build/real_sample_sources`, prepares one-note real-audio fixtures under `build/real_note_samples`, and checks exact pitch/instrument-family detection. The current prepared set has 2,212 accepted samples: 137 bass, 346 guitar, 1,117 piano/keyboard, 22 vocal, and 590 other-instrument examples. It excludes out-of-range notes, synthetic-source examples, metadata-marked non-one-note qualities such as `multiphonic` and `tempo-synced`, plus seven exact unstable pitch-reference examples. The gate now enforces per-family minimum coverage with `REAL_NOTE_MIN_BASS`, `REAL_NOTE_MIN_GUITAR`, `REAL_NOTE_MIN_PIANO`, `REAL_NOTE_MIN_VOCALS`, and `REAL_NOTE_MIN_OTHER`, so a future dataset-preparation change cannot silently collapse coverage to one family. The archive is about 333 MB, is cached under `build/`, and the cached local test currently runs in about 16.16 seconds.

`make test-vocadito-samples` downloads [Vocadito](https://zenodo.org/records/5578807), a 58.5 MB CC BY 4.0 dataset of 40 short solo monophonic vocal recordings with trained-musician F0, note, lyric, and language annotations. The preparer keeps only A1 note annotations that are long enough for a stable mid-note clip, inside the analyzer vocal range, and within `VOCADITO_MAX_CENTS` of a chromatic MIDI note, then writes derived WAV snippets under `build/vocadito_samples`. The current default gate prepares 370 real vocal clips across 27 note names from F2-G#4 and requires at least `VOCADITO_MIN_VOCALS=300` clips. Current local results are 368/370 isolated-vocal detections with two tolerated misses, and the cached analyzer phase currently runs in about 6.26 seconds. Override `VOCADITO_ANNOTATOR`, `VOCADITO_SAMPLE_LIMIT`, `VOCADITO_MIN_VOCALS`, `VOCADITO_MAX_CENTS`, or `VOCADITO_MIN_NOTE_DURATION` to tune the sweep.

`make test-guitar-fretboard-note-samples` downloads the public [Guitar Single-Note Recordings](https://huggingface.co/datasets/collegefishiesd/guitar-fretboard-notes) dataset through the Hugging Face row API, writes build-local WAV fixtures under `build/guitar_fretboard_notes_samples`, and runs the shared isolated real-note gate in guitar mode. The dataset contains 390 labeled acoustic/electric guitar single notes across standard-tuned strings and frets 0-12, covering MIDI 40-76. The preparer uses only Python standard-library HTTP/JSON/WAV handling and prints progress every 25 samples; reruns skip already-downloaded WAV files. Current local results are 389/390 isolated-guitar detections in about 9.17 seconds after download. One row, `train_0073_ele_high_E_f5_A4`, is kept visible as a tolerated dataset outlier: metadata says A4, but the downloaded audio is dominated by other pitches in the analyzer inspection. Override `GUITAR_FRETBOARD_NOTES_LIMIT`, `GUITAR_FRETBOARD_NOTES_MIN_GUITAR`, or `GUITAR_FRETBOARD_NOTES_MAX_FAILURES` if you want a smaller smoke run or stricter handling of that row.

`make test-hf-drum-kit-samples` downloads the public [airasoul/drum-kit](https://huggingface.co/datasets/airasoul/drum-kit) one-shot dataset through the Hugging Face row API, keeps the unambiguous labels that match the analyzer's drum categories, and writes build-local WAV fixtures under `build/hf_drum_kit_samples`. It maps `hat` to hi-hat and skips labels outside the current UI model such as `clap`, `conga`, and generic `cymbal`. The current prepared set has 2,100 real drum one-shots: 300 each for kick, snare, hi-hat, crash, tom, ride, and rim. Reruns validate and reuse a complete cached manifest before touching the Hugging Face API, so a temporary remote `429` does not break an already-prepared local gate. The gate currently enforces a broad diagnostic floor with `HF_DRUM_KIT_MIN_RECALL_PERCENT=20` and `HF_DRUM_KIT_MIN_PRECISION_PERCENT=18`, then prints the same active and primary matrices as the local drum-sample gates. Current cached local results are kick 238/300, snare 285/300, hi-hat 299/300, crash 295/300, tom 300/300, ride 300/300, and rim 143/300 recall. Primary-label hits are kick 238/300, snare 188/300, hi-hat 270/300, crash 253/300, tom 160/300, ride 287/300, and rim 106/300. Treat this as a broad real one-shot diagnostic benchmark for reducing cross-class drum lighting, especially rim/snare/kick/tom confusion. Override `HF_DRUM_KIT_LIMIT_PER_CATEGORY` for a smaller loop; use `0` for the full 2,100-sample sweep.

`make test-downloaded-guitarset` downloads [GuitarSet](https://zenodo.org/records/3371780) annotations plus the mono microphone audio into `build/real_sample_sources/guitarset`, prepares `build/guitarset-manifest.tsv`, and runs isolated-guitar note/chord regression over all usable annotated chord windows. `make analyze-guitarset-misses` reruns the same manifest with verbose chord-miss logging, writes `build/guitarset_verbose.log`, and prints the largest expected-quality, same-root quality, exact same-root label miss pairs, actionable miss buckets, expected-tone coverage, full-tone label misses, and third-state breakdown for plain major/minor chords that collapse to same-root power chords. The miss buckets separate root-shift/spurious chords, same-root-but-missing-tone cases, expected-tone-missing no-chord cases, full-tones-present root shifts, full-tones-present same-root wrong-quality cases, full-tones-present no-chord cases, and no-guitar-note cases. The prepared manifest contains 360 excerpts; the current usable mono-mic gate covers 209 excerpts, 1,528 selected windows, and 1,491 chord-checkable windows, reporting pitch recall, guitar-row precision/recall/F1, cross-row contamination, exact chord precision/recall, simplified root/quality chord recall, major/minor versus other chord hits, and per-quality chord hits. Current local results are 4,276/5,451 pitch-class hits, 67.94% guitar precision, 78.44% guitar recall, 72.81% guitar F1, and 749/1,491 exact chord hits: 496/752 major/minor opportunities and 253/739 other-chord opportunities. The same run reports 875/1,491 simplified-compatible chord hits, including 507/752 major/minor opportunities; this distinguishes missed extensions from completely wrong chord roots. The Makefile gate now enforces minimum real-audio floors for pitch recall/precision, guitar-row recall, exact chord recall/precision, exact major/minor recall, exact other-chord recall, simplified overall recall, simplified major/minor recall, and simplified other-chord recall through the `GUITARSET_MIN_*` knobs, currently 75/65/75/50/53/65/33/58/67/49 percent respectively. The quality breakdown currently shows major 341/500 exact and 351/500 simplified, minor 148/255 exact and 151/255 simplified, sus2 42/88, sus4 36/88, 7th 59/160, maj7 46/202, m7 39/173, 9th 13/38, add9 18/61, 6th 33/173, m6 15/57, dim 5/26, and augmented/diminished-seventh/power shapes still weak. This is a real-audio detector benchmark, not a perfect-truth pass/fail for every chord shape: major/minor chords are prioritized, while sus, diminished, augmented, seventh, ninth, add9, sixth, and power-chord templates are still counted and reported. The cached analyzer phase currently runs in about 19.81 seconds after extraction; first download is about 663 MB and can take much longer.

`make test-guitar-chord-mix-samples` downloads a bounded, label-spread subset of the public [Guitar Chord Mix](https://huggingface.co/datasets/ryangowe/guitar-chord-mix) WAV/JAMS clips into `build/guitar_chord_mix_samples`, writes a GuitarSet-shaped manifest from the per-string `note_midi` annotations, and runs the isolated-guitar note/chord harness. The default `GUITAR_CHORD_MIX_LIMIT=120` keeps the first run moderate; set `GUITAR_CHORD_MIX_LIMIT=0` to prepare all matched WAV/JAMS pairs. The current cached default gate prepares 120 clips with 618 note annotations across 16 chord labels and passes with 79.30% guitar recall, 75.06% guitar precision, 56.45% exact chord recall, and 66.04% exact chord precision. This is real guitar chord audio coverage and is included in `make test-real-world-samples-full`.

`make test-philharmonia-samples` downloads the public [Philharmonia sound sample library](https://philharmonia.co.uk/resources/sound-samples/) Woodwind, Brass, and Strings archives into `build/real_sample_sources/philharmonia`, prepares balanced one-note fixtures under `build/philharmonia_samples`, and checks isolated bass, guitar-family, and other-instrument pitch detection. The importer skips undecodable archive members and pitch references outside the analyzer's strict chromatic-note model: a candidate must validate in at least two analyzer-style windows, remain within the tuning probe tolerance, beat adjacent semitone ambiguity, and reject high-note files dominated by low-frequency artifacts. The current prepared set has 2,967 decoded real samples: 128 bass, 146 guitar-family, and 2,693 other woodwind/brass/string examples. Five mandolin notes above the analyzer's documented guitar range stay in `other`. The gate enforces at least `PHILHARMONIA_MIN_BASS` real bass samples, `PHILHARMONIA_MIN_GUITAR` guitar-family samples, and `PHILHARMONIA_MIN_OTHER` other-instrument samples. Current local results are bass 128/128, guitar 146/146, and other 2,693/2,693; the cached analyzer phase currently runs in about 54.05 seconds. `make test-philharmonia-samples-full` reuses the same cached archives, prepares all balanced one-note candidates into `build/philharmonia_samples_full`, prints conversion progress, writes `manifest.tsv.partial` on interruption or under-coverage, and enforces the larger `PHILHARMONIA_FULL_MIN_*` coverage thresholds. Complete existing manifests are reused unless `PHILHARMONIA_REFRESH=1` is set, so rerunning the full real-world sweep does not spend minutes revalidating the same converted WAVs. The current full fixture has 7,285 decoded real samples: 471 bass, 146 guitar-family, and 6,668 other woodwind/brass/string examples. Current full local results are bass 471/471, guitar 146/146, and other 6,668/6,668; the cached full analyzer phase currently runs in about 143.50 seconds. The three archives are about 522 MB total and are cached under `build/`.

`make test-iowa-piano-samples` downloads the public [University of Iowa Musical Instrument Samples piano page](https://theremin.music.uiowa.edu/MISpiano.html), converts selected AIFF notes into `build/iowa_piano_samples`, and checks isolated keyboard pitch detection. It is also included in `make test-real-world-samples` so the broad real-audio benchmark covers acoustic piano notes in addition to NSynth, GuitarSet, Philharmonia, and Iowa double bass. That host can be slow for direct AIFF transfer, so the importer uses resumable `.part` downloads, bounded curl timeouts, configurable retry/resume attempts via `IOWA_PIANO_DOWNLOAD_RETRIES`, temporary WAV conversion, per-file progress output, and a deterministic URL-pattern fallback if the HTML page stalls. The prepare step now enforces the same minimum piano coverage as the analyzer gate; if the remote host times out before enough files are prepared, it writes `manifest.tsv.partial` and fails instead of silently testing a tiny subset. Reruns reuse cached page, AIFF, and WAV files. Use `IOWA_PIANO_SAMPLE_LIMIT=0` to prepare every discovered piano note file or keep the default 84-file gate for a smaller acoustic-piano sweep. The current default gate prepares 84 real acoustic piano notes and passes 84/84 isolated-keyboard detections; the cached analyzer phase currently runs in about 2.50 seconds. The generated audio is cached under `build/` and is not committed.

`make test-iowa-bass-samples` downloads the public University of Iowa post-2012 double-bass pizzicato ZIP `Bass.pizz.ff.sulE.stereo.zip`, converts one-note AIF members into `build/iowa_bass_samples`, and checks isolated bass pitch detection. The generic `scripts/prepare_iowa_zip_samples.py` importer supports `family|nsynth_family|source|zip_url` specs, resumable ZIP downloads, temporary WAV conversion, and a pitch-reference filter so exact-note tests keep the strict chromatic model instead of accepting out-of-tune or mislabeled files. The current default gate inspects 24 ZIP members, skips 4 pitch-reference failures, prepares 20 tuned real double-bass notes, and passes 20/20 isolated-bass detections. The ZIP is about 15 MB, can download slowly from the Iowa host, is cached under `build/real_sample_sources/iowa_bass`, and is not committed.

`make test-idmt-bass-lines-samples` downloads [IDMT-SMT-Bass-Single-Track](https://zenodo.org/records/7544099), a 20.5 MB real electric-bass dataset with 17 bass lines and note-level onset, offset, MIDI pitch, string, fret, plucking-style, and expression-style annotations. The preparer extracts stable mid-note clips from expression-style `NO` notes into `build/idmt_bass_lines_samples`, preserving fingerstyle, picked, muted, slap-thumb, and slap-pluck examples. The current default gate prepares 640 real bass-line clips across 22 note names from E1-D3 and requires at least `IDMT_BASS_LINES_MIN_BASS=600` clips. Current local results are 617/640 isolated-bass detections with 23 tolerated misses, and the cached analyzer phase currently runs in about 12.79 seconds. Treat the misses as useful evidence for future bass-detector tuning rather than pruned dataset noise. Override `IDMT_BASS_LINES_EXPRESSIONS`, `IDMT_BASS_LINES_SAMPLE_LIMIT`, `IDMT_BASS_LINES_MIN_BASS`, `IDMT_BASS_LINES_MAX_FAILURES`, or `IDMT_BASS_LINES_MIN_NOTE_DURATION` to tune the sweep.

`make test-tinysol-samples` downloads [TinySOL](https://zenodo.org/records/3632193), a public CC BY 4.0 dataset of 2,478 real isolated musical notes with CSV metadata and MIDI pitch IDs. The preparer accepts both the older `Instrument Name` metadata header and the current `Instrument (in full)` header, matches TinySOL's ZIP layout from metadata family/instrument/technique fields, copies non-resampled WAV files from `TinySOL.zip` into `build/tinysol_samples`, maps contrabass to bass, accordion to keyboard/piano, and brass/woodwind/string instruments to other, then runs the shared isolated real-note analyzer gate. The gate is explicit opt-in because the archive is about 898 MB; interrupted archive downloads are kept as `TinySOL.zip.part`, reruns use `aria2c` with parallel resume when available and fall back to `curl -C -`, and the Makefile validates the ZIP before promoting it to the final archive path. The current prepared set has 2,435 non-resampled real samples: 303 bass, 251 piano/keyboard, and 1,881 other brass/woodwind/string examples. Current local results are bass 303/303, piano 251/251, and other 1,881/1,881; the cached analyzer phase currently runs in about 57.82 seconds. Override `TINYSOL_SAMPLE_LIMIT`, `TINYSOL_MIN_SAMPLES`, `TINYSOL_MIN_BASS`, `TINYSOL_MIN_PIANO`, or `TINYSOL_MIN_OTHER` to tune the sweep; set `TINYSOL_INCLUDE_RESAMPLED=1` if you intentionally want TinySOL pitch-shifted rows included. `make test-real-world-samples-full` runs the regular real-world sample benchmark plus Guitar-TECHS, Guitar Chord Mix, Philharmonia-full, TinySOL, and the full local drum sweep when `DRUM_SAMPLE_SOURCE_DIR` exists.

Measure standalone CPU and memory with a deterministic generated raw-audio profile:

```sh
make profile-standalone
```

Measure the currently running Android app through adb:

```sh
make android-profile
```

Latest local profile from July 16, 2026:

| Target | CPU | Memory | Notes |
| --- | ---: | ---: | --- |
| Standalone Bass + Guitar | 14.8% estimated real-time CPU | 14,792 KB max RSS | `make profile-standalone`; synthetic 20-second raw-audio profile; AMD Ryzen 9 5950X, 32 logical CPUs |
| Standalone complete | 17.0% estimated real-time CPU | 15,992 KB max RSS | `make profile-standalone`; synthetic 20-second raw-audio profile; AMD Ryzen 9 5950X, 32 logical CPUs |
| Android Bass + Guitar emulator app | 22.1% app CPU, 27.6% total device CPU | 35,574 KB app PSS | `make android-profile-bass-guitar`; repo-local Android emulator |
| Android complete emulator app | 19.5% app CPU, 24.8% total device CPU | 36,343 KB app PSS | `make android-profile-complete`; repo-local Android emulator |

For `make profile-standalone`, `JobCPU` is the CPU used while processing the generated raw audio as fast as possible. `RealtimeCPU` is the estimated CPU if the same workload runs at live 1x audio speed, expressed as one-core CPU percentage. Android `app CPU` from `make android-profile*` is process CPU as a share of total emulator CPU capacity; the in-app `CPU` status is app process CPU used relative to one core, and `RAM` is app RAM usage in MB. OBS overlay `CPU` and `RAM` are measured from the hosting OBS process, so they include OBS itself plus the plugin. Android numbers are emulator-specific; physical devices will vary by CPU, Android audio stack, screen refresh, and input route.

`make test` builds standalone analyzer executables outside OBS and also runs `make test-standalone`, which verifies the SDL standalone target, the shared renderer, and the Makefile/CMake isolation that keeps SDL out of the OBS plugin target. It first validates the checked real-dataset catalog used to decide which public datasets can provide note-ground-truth coverage. Each core analyzer executable is run through `scripts/run_with_duration.sh`, so the test log includes wall-clock duration lines. `analyzer_smoke` covers the basic signal path. `analyzer_cases` runs broad synthetic note, instrument, chord, note-matrix, quiet-note rejection, realistic harmonic chord, same-note timbre split, isolated-source spillover rejection, explicit input-mode behavior, BPM estimation, mixed-source timbre routing, multi-instrument mix, URMP same-song multitrack metadata fixtures, and root-candidate cases, including bass B0-G4, guitar E2-E6, keyboard/other A0-C8, and vocal E2-C6. `analyzer_midi_ranges` covers GM drum MIDI notes, rim/side-stick detection, normal bass/piano/guitar/synth/string/vocal note ranges, and a combined full-mix MIDI arrangement. When `DRUM_SAMPLE_SOURCE_DIR` exists, `make test` also runs both `make test-drum-samples` and `make test-drum-samples-spread`, which copy classified one-shot kick, snare, hi-hat, crash, tom, ride, and rim WAV samples into build-local sample folders and check per-category recall across first-file and deterministic spread selections. When FluidSynth is available, `make test` also runs `make test-instrument-samples`, which renders and verifies 1000+ SoundFont-backed fixtures per piano, guitar, bass, synth, string, vocal/choir, and GM drum-kit family, plus crowded-combination and rendered same-pitch full-mix chord cases. The internet-downloaded NSynth, guitar-fretboard, Guitar-TECHS, Guitar Chord Mix, HF drum-kit, GuitarSet, Philharmonia, Iowa piano, Iowa bass, IDMT bass lines, TinySOL, and Vocadito gates are intentionally separate because first-run downloads are large or slow; run `make test-real-world-samples` for the regular real-audio benchmark and `make test-real-world-samples-full` when you want the larger Guitar-TECHS, Guitar Chord Mix, Philharmonia-full, TinySOL, and available full local drum-library sweeps.

The full-mix regression cases model public multitrack dataset layouts without downloading dataset audio. They include 20+ Slakh2100-style MIDI-rendered song fixtures, 20 ChoralSynth-style vocal multitrack fixtures, 20 CocoChorales-style chamber-ensemble fixtures, 20 SynthSOD-style orchestra/ensemble fixtures, 20 Vocal Ensemble F0 Aggregate-style real-vocal F0 fixtures, plus additional MUSDB18/MUSDB18-HQ, DSD100/Mixing Secrets, MedleyDB/2.0, MoisesDB, URMP, Bach10, TRIOS, PHENICX-Anechoic, MIREX Woodwind Quintet, RawStems, MulTTiPop, GuitarSet, MAESTRO, E-GMD, ACMID, Spheres, MDX, and Open Multitrack Testbed-style fixtures. See [docs/real_audio_dataset_candidates.md](docs/real_audio_dataset_candidates.md) for real recorded dataset candidates that can verify notes and instruments.

Optional real-audio URMP regression coverage runs when a local URMP dataset is available:

```sh
make real-dataset-sources
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-goal-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-goal-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-multitrack-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-multitrack-full
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-full
make inspect-real-musicnet-remote
MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make inspect-real-musicnet
MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make test-real-musicnet-20
MUSIC_ANALYZER_MEDLEYDB_ROOT=/path/to/MedleyDB MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=/path/to/medleydb/medleydb/data/Annotations make inspect-real-medleydb
MUSIC_ANALYZER_MEDLEYDB_ROOT=/path/to/MedleyDB MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=/path/to/medleydb/medleydb/data/Annotations make test-real-medleydb-20
MUSIC_ANALYZER_MUSDB_ROOT=/path/to/MUSDB18-HQ make inspect-real-musdb
MUSIC_ANALYZER_SLAKH_ROOT=/path/to/Slakh2100_flac_redux make inspect-real-slakh
MUSIC_ANALYZER_SLAKH_ROOT=/path/to/Slakh2100_flac_redux make test-real-slakh-20
MUSIC_ANALYZER_CHORALSYNTH_ROOT=/path/to/ChoralSynth make inspect-real-choralsynth
MUSIC_ANALYZER_CHORALSYNTH_ROOT=/path/to/ChoralSynth make test-real-choralsynth-20
MUSIC_ANALYZER_COCOCHORALES_ROOT=/path/to/CocoChorales make inspect-real-cocochorales
MUSIC_ANALYZER_COCOCHORALES_ROOT=/path/to/CocoChorales make test-real-cocochorales-20
make inspect-real-synthsod-remote
MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP=/path/to/SynthSOD-sample.zip MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP=/path/to/SynthSOD_aligned_scores.zip make extract-real-synthsod-archives
MUSIC_ANALYZER_SYNTHSOD_ROOT=/path/to/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=/path/to/SynthSOD-aligned-scores make inspect-real-synthsod
MUSIC_ANALYZER_SYNTHSOD_ROOT=/path/to/SynthSOD-data MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=/path/to/SynthSOD-aligned-scores make test-real-synthsod-20
MUSIC_ANALYZER_POLYVOCAL_ROOT=/path/to/prepared-vocal-f0 make inspect-real-polyvocal
MUSIC_ANALYZER_POLYVOCAL_ROOT=/path/to/prepared-vocal-f0 make test-real-polyvocal-20
MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=/path/to/prepared-multitrack make inspect-real-prepared-multitrack
MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=/path/to/prepared-multitrack make test-real-prepared-multitrack-20
MUSIC_ANALYZER_MULTTIPOP_ROOT=/path/to/multtipop make inspect-real-multtipop
MUSIC_ANALYZER_MULTTIPOP_ROOT=/path/to/multtipop MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1 make test-real-multtipop-20
MUSIC_ANALYZER_SPHERES_ROOT=/path/to/TheSpheresDataset make inspect-real-spheres
MUSIC_ANALYZER_GUITARSET_ROOT=/path/to/GuitarSet make inspect-real-guitarset
MUSIC_ANALYZER_GUITARSET_ROOT=/path/to/GuitarSet make test-real-guitarset-20
make test-guitar-techs-samples
MUSIC_ANALYZER_MAESTRO_ROOT=/path/to/maestro-v3.0.0 make test-real-maestro-20
MUSIC_ANALYZER_EGMD_ROOT=/path/to/e-gmd-v1.0.0 make test-real-egmd-20
```

`make real-dataset-sources` prints the checked public dataset sources and the exact local URMP commands. `make inspect-real-goal-20` is the combined setup preflight: it requires the URMP multitrack layout check, then runs the optional MusicNet, MedleyDB, MUSDB18, Slakh2100, ChoralSynth, CocoChorales, SynthSOD, Vocal Ensemble F0 Aggregate, prepared multitrack note-truth, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD gates when their roots are configured. The URMP preflight uses the same minimum active-track and pitch-class density knobs as the analyzer gate, and reports matched-track, candidate active-track, and candidate pitch-class min/average/max values.

`make test-real-goal-20` is the combined acceptance gate for the requested 20+ real same-song multitrack test. It requires the URMP analyzer gate, then runs the optional MusicNet real-mix gate, the MedleyDB summed-stem melody-F0 analyzer gate, MUSDB18/Spheres/GuitarSet preflights, the Slakh2100 rendered multitrack analyzer gate, the ChoralSynth synthetic vocal multitrack analyzer gate, the CocoChorales synthetic chamber-ensemble analyzer gate, the SynthSOD synthetic orchestra/ensemble analyzer gate, the Vocal Ensemble F0 Aggregate real-vocal F0 analyzer gate, the prepared multitrack note-truth analyzer gate, the MulTTiPop real-pop analyzer gate when local WAV segments are available or `MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1` is set, the MAESTRO piano analyzer gate, and the E-GMD drum analyzer gate when configured. The official URMP page routes the full package through dataset download registration, so the project does not attempt an unattended 12.5 GB download. Without `MUSIC_ANALYZER_URMP_ROOT`, the real-data check is built but skipped during normal `make test`; `make inspect-real-goal-20`, `make test-real-multitrack-20`, and `make test-real-goal-20` fail instead, so they can be used as the required 20+ real-song gate once the real URMP package is available. `inspect-real-multitrack-20` checks only the local URMP dataset layout before analyzer work.

`make test` also runs `make test-direct-fit-small-fixture`, which unpacks the committed compact direct-fit-small FLAC fixture from `tests/fixtures/direct-fit-small.tar.gz`, decodes it under `build/`, and reuses the URMP analyzer path to verify 20 pieces modeled after Bach10, TRIOS, PHENICX-Anechoic, and MIREX Woodwind Quintet instrumentation across separated sources, provided mix, summed mix, streaming mix, stateful sequence, and chord paths. The URMP analyzer output includes isolated-track precision, exact recall, F1, cross-row contamination, octave-error rate, ambiguous assignment count, expected-instrument to detected-instrument confusion, and global-chord precision/recall/F1 for each full-mix path so false positives are visible instead of hidden by union pitch recall. `make update-direct-fit-small-fixture` refreshes that archive from the deterministic generator. `make test-bach10-fixture` remains available as the smaller Bach10-only generated regression.

`make test` also runs `make test-real-goal-fixture`, which unpacks the committed URMP-shaped 20-piece lossless FLAC fixture from `tests/fixtures/urmp-mini.tar.gz`, decodes it to disposable WAV files under `build/` with `ffmpeg`, generates 20-recording MusicNet-shaped plus MedleyDB-shaped, MUSDB18-shaped, Slakh2100-shaped, ChoralSynth-shaped, CocoChorales-shaped, SynthSOD-shaped, Vocal Ensemble F0 Aggregate-shaped, prepared-multitrack-shaped, audio-backed MulTTiPop-shaped, Spheres-shaped, GuitarSet-shaped, MAESTRO-shaped, and E-GMD-shaped fixtures, sends all configured roots through the combined setup preflight, and then sends them through the combined goal gate. It also runs `make test-multtipop-audio-root-fixture`, which keeps MulTTiPop metadata and WAV segments in separate directories to prove `MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT` works. The generated Vocal Ensemble F0 fixture now requires per-voice source WAV files and sums those voices before analysis. The generated prepared-multitrack fixture uses a manifest with four source WAVs and per-source note CSVs per piece, sums the source WAVs, and verifies note/chord recall. The generated SynthSOD fixture uses the documented close-mic source folder plus aligned score text, sums source tracks, and verifies note/chord recall. That exercises WAV, Notes, MIDI score, full-mix, summed-stem, real-mix-label, MedleyDB summed-stem melody-F0 audio analysis, MUSDB18/Spheres stem-layout, Slakh2100 rendered-stem/MIDI layout, ChoralSynth vocal score/voice-track layout, CocoChorales chamber stem/MIDI layout, SynthSOD close-mic stem/aligned-score layout, vocal F0 contour-to-note conversion with source-voice summing, generic prepared source-note summing, MulTTiPop multitrack-MIDI audio analysis, GuitarSet JAMS/hex-audio preflight, MAESTRO MIDI/WAV piano analysis, E-GMD MIDI/WAV drum analysis, and chord paths without downloading external datasets. Override the decoder with `FFMPEG=/path/to/ffmpeg` if needed.

The URMP fixture is marker-file tagged and rejected by the real-data gate unless `MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1` is set by the fixture test target. Refresh that fixture with `make update-urmp-fixture` when the fixture generator changes. When pointed at a real URMP dataset, the harness requires official URMP piece folder IDs, reads URMP `AuMix`, `AuSep`, `Notes`, and `Sco` MIDI files, validates that the MIDI score pitch classes agree with the note annotations, requires at least 20 usable same-song pieces and at least 80 annotated note windows by default, checks separated tracks, then checks both the provided `AuMix` and a synthesized mix made by summing all separated tracks. It also replays each selected full-mix and summed-mix window through a short multi-frame analyzer sequence, and keeps one stateful provided-mix analyzer plus one stateful summed-mix analyzer per piece across selected windows, so note/chord smoothing is tested against same-song mixed audio instead of only fresh single-window analyzer state. Selected windows must contain at least two active source tracks and two pitch classes by default, and the coverage line reports source-track, active-track, and pitch-class min/average/max values.

`make inspect-real-goal-full` and `make test-real-goal-full` raise the required URMP gate to all 44 official pieces and at least 176 annotated windows. It prints discovered/loadable piece and window counts to diagnose incomplete dataset layouts. Set `MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE`, `MUSIC_ANALYZER_URMP_REQUIRED_PIECES`, and `MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS` to lower or raise the coverage gate. Set `MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW`, `MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW`, `MUSIC_ANALYZER_URMP_MIN_WINDOW_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_TRACK_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_TRACK_PRECISION_PERCENT`, `MUSIC_ANALYZER_URMP_MAX_TRACK_CONTAMINATION_PERCENT`, `MUSIC_ANALYZER_URMP_MAX_TRACK_OCTAVE_ERROR_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_MIX_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_CHORD_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_GLOBAL_CHORD_PRECISION_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_GLOBAL_CHORD_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_CHORD_CHECKS`, and `MUSIC_ANALYZER_URMP_VERBOSE_CHORD_MISSES=1` to tighten, relax, or debug the quality gate.

`make inspect-real-medleydb` is a partial second real-data preflight for MedleyDB/MedleyDB 2.0. It requires at least 20 local songs with mix plus stems and at least 20 melody-annotated multitracks by default. `make test-real-medleydb-20` converts selected melody F0 annotations into a temporary MusicNet-shaped label set, sums the local source stems into playback audio, and checks analyzer melody pitch-class recall. MedleyDB is useful for real stem and melody-F0 coverage, but it does not replace the URMP gate because it lacks full per-source note/chord ground truth.

`make inspect-real-musdb` is an optional weak-truth preflight for MUSDB18-HQ or a decoded MUSDB18 layout. It requires at least 20 complete same-song tracks with readable `mixture`, `drums`, `bass`, `other`, and `vocals` WAV stems by default. MUSDB18 is useful for real full-song stem playback and broad timbre routing, but it does not replace URMP because it has no MIDI/note/chord truth.

`make inspect-real-slakh` is an optional synthesized multitrack truth preflight for Slakh2100. It requires at least 20 complete same-song rendered tracks with mix audio, 4+ stem audio files, readable MIDI, and metadata containing piano, bass, guitar, and drum classes by default. `make test-real-slakh-20` prepares those tracks as a temporary MusicNet-shaped WAV/CSV layout by summing the per-source stem audio, then runs the existing MusicNet analyzer gate against that played-together stem mix for pitch-class and chord recall. Slakh2100 is useful for large same-song stem/MIDI note and chord coverage, but it does not replace URMP because its audio is MIDI-rendered with virtual instruments rather than real recorded performances.

`make inspect-real-choralsynth` is an optional synthesized vocal multitrack truth preflight for ChoralSynth. It requires 20 pieces with `score.musicxml`, readable `score.midi`, and 4+ voice audio files by default. `make test-real-choralsynth-20` mixes the voices into a temporary MusicNet-shaped WAV/CSV layout, parses the score MIDI as note truth, and runs the existing MusicNet analyzer gate for pitch-class and chord recall. ChoralSynth is useful for vocal polyphony coverage, but it does not replace URMP because its audio is singing-synthesized rather than real recorded.

`make inspect-real-cocochorales` is an optional synthesized chamber-ensemble truth preflight for CocoChorales. It requires 20 local examples with readable score MIDI, mix audio, and 4+ stem audio files by default. `make test-real-cocochorales-20` sums the stems into a temporary MusicNet-shaped WAV/CSV layout, parses the score MIDI as note truth, and runs the existing MusicNet analyzer gate for pitch-class and chord recall. CocoChorales is useful for large stem/MIDI stress coverage, but it does not replace URMP because its audio is generated by the Chamber Ensemble Generator rather than real recorded.

`make inspect-real-synthsod-remote` checks the current Zenodo metadata for the SynthSOD audio archive and the separate aligned-score archive before downloading large files. It reports the full/sample archive sizes, licenses, direct content URLs, and the exact local `MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP`/`MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP` extraction command shape. After downloading those ZIP files, `make extract-real-synthsod-archives` safely extracts them under `build/synthsod-archives` and prints the resulting `MUSIC_ANALYZER_SYNTHSOD_ROOT`/`MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT` commands. `make inspect-real-synthsod` is an optional synthesized orchestra/ensemble truth preflight for an extracted SynthSOD dataset. It expects `MUSIC_ANALYZER_SYNTHSOD_ROOT=/path/to/SynthSOD-data` plus `MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=/path/to/SynthSOD-aligned-scores`, requires 20 pieces with 4+ close-mic source tracks and aligned note text by default, and reports source-track, note-row, pitch-class, channel, sample-rate, and duration coverage. `make test-real-synthsod-20` sums the close-mic stems into a temporary MusicNet-shaped WAV/CSV layout, converts the aligned score text into note labels, and runs the existing MusicNet analyzer gate for pitch-class and chord recall. SynthSOD is useful for larger orchestral stem/note stress coverage, but it does not replace URMP because its audio is synthesized from MIDI rather than real recorded.

`make inspect-real-polyvocal` is an optional real vocal multitrack F0 preflight for the Vocal Ensemble F0 Aggregate described by Cuesta, McFee, and Gomez. It expects a local prepared `mtracks_info.json` layout from the companion workflow, with mixture audio plus four or more per-voice F0 CSV/JAMS annotations. If `source_audio_files` and `source_audio_folder` are present, `make test-real-polyvocal-20` sums those source voices into the temporary MusicNet-shaped WAV/CSV layout before running the existing analyzer pitch-class and chord recall gate; set `MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1` to require that source-voice path. This adds 20+ real vocal same-song multi-source note/chord coverage, but it is vocal-only and does not replace URMP's mixed-instrument source gate.

`make inspect-real-prepared-multitrack` is an optional generic preflight for local prepared real multitrack datasets such as Ensemble Expressive Performance or combined small direct-fit sets after their source audio and note annotations are mapped into `manifest.json`. Each manifest piece lists `sources`, and each source lists `audio`, `notes`, and optional `instrument`. `make test-real-prepared-multitrack-20` sums the source WAVs into a temporary MusicNet-shaped layout, combines the per-source note CSVs, and runs the analyzer pitch-class/chord recall gate. This is a local-layout bridge for datasets whose public archive layout is not stable enough to hard-code.

`make inspect-real-multtipop` is an optional preflight for MulTTiPop. It checks 20+ aligned multitrack MIDI files and YouTube timing metadata by default, and can require local audio segments with `MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1`. `make test-real-multtipop-20` expects local WAV audio segments beside each segment directory as `audio.wav`, `segment.wav`, or `<id>.wav`, or under `MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT`; it parses `aligned.mid`, selects multi-part note/chord windows, and reports real-pop pitch-class recall/precision/F1 and global chord recall/precision/F1. Useful knobs include `MUSIC_ANALYZER_MULTTIPOP_MIN_RECALL_PERCENT` (default 40), `MUSIC_ANALYZER_MULTTIPOP_MIN_PRECISION_PERCENT` (default 35), `MUSIC_ANALYZER_MULTTIPOP_MIN_CHORD_RECALL_PERCENT` (default 20), and `MUSIC_ANALYZER_MULTTIPOP_MIN_GLOBAL_CHORD_PRECISION_PERCENT` (default 20). `make test-multtipop-audio-root-fixture` is the generated regression for the separate-audio-root layout. MulTTiPop adds real-pop transcription coverage once audio segments are locally available, but the official release references commercial audio instead of shipping stems.

`make inspect-real-spheres` is an optional weak-truth preflight for The Spheres Dataset. It checks that the local release exposes the expected real orchestral piece folders with readable stereo/mix audio, separate source-audio folders, enough source files, and enough audio duration to make summed-stem playback meaningful. Spheres adds timbre and stem-layout coverage, but it has only two full works and no full MIDI/note truth, so it does not replace the URMP or MusicNet note/chord checks.

`make inspect-real-guitarset` is an optional focused preflight for GuitarSet. It requires 20+ local GuitarSet excerpts with JAMS note/chord annotations and 6-channel hex pickup WAV audio by default. `make test-real-guitarset-20` turns those JAMS files into a temporary manifest, reads the selected real WAV windows in explicit isolated-guitar mode, and reports pitch-class recall, guitar-row precision/recall/F1, cross-row contamination, false-vocal windows, and isolated guitar-chord precision/recall. Useful knobs include `MUSIC_ANALYZER_GUITARSET_MIN_PRECISION_PERCENT` (default 90), `MUSIC_ANALYZER_GUITARSET_MIN_GUITAR_RECALL_PERCENT` (default 90), `MUSIC_ANALYZER_GUITARSET_MAX_CONTAMINATION_PERCENT` (default 5), `MUSIC_ANALYZER_GUITARSET_MAX_FALSE_VOCAL_PERCENT` (default 5), and `MUSIC_ANALYZER_GUITARSET_MIN_CHORD_PRECISION_PERCENT` (default 85). GuitarSet is useful for guitar row, fretboard, and chord-shape regressions, but it is a single-instrument dataset and does not replace the URMP mixed-source gate.

`make test-guitar-techs-samples` is an optional focused analyzer gate for Guitar-TECHS single notes. It downloads the P1/P2 single-note ZIPs from Zenodo under `build/real_sample_sources/guitar_techs`, extracts the aligned MIDI plus DI and amplifier-mic WAV perspectives into `build/guitar_techs_samples`, writes short labeled WAV excerpts, and runs the shared real-note analyzer gate in isolated-guitar mode. With the current P1/P2 ZIPs the default prep produced 547 tested clips after 11 pitch-reference skips, and the analyzer gate detected 547/547 guitar notes. Useful knobs include `GUITAR_TECHS_SAMPLE_LIMIT`, `GUITAR_TECHS_MIN_GUITAR` (default 200), `GUITAR_TECHS_MAX_FAILURES` (default 25), `GUITAR_TECHS_PERSPECTIVES`, and `GUITAR_TECHS_SKIP_PITCH_CHECK=1`. This is real electric-guitar note coverage; Guitar-TECHS chord/technique/scales archives are not part of the default target yet.

`make test-guitar-chord-mix-samples` is an optional focused analyzer gate for real guitar chords. It downloads Hugging Face Guitar Chord Mix WAV/JAMS clips under `build/guitar_chord_mix_samples`, prepares a GuitarSet-shaped manifest from the six per-string `note_midi` annotations, and runs `analyzer_guitarset` in isolated-guitar mode. Useful knobs include `GUITAR_CHORD_MIX_LIMIT` (default 120, `0` for all matched pairs), `GUITAR_CHORD_MIX_MIN_EXCERPTS`, `GUITAR_CHORD_MIX_MIN_WINDOWS`, and the `GUITAR_CHORD_MIX_MIN_*` threshold variables for pitch, guitar-row, and chord recall.

`make test-real-maestro-20` is an optional focused analyzer gate for MAESTRO. It expects the official metadata CSV plus paired WAV/MIDI files, parses the aligned MIDI, selects polyphonic piano/chord windows in explicit isolated-keyboard mode, and reports pitch-class recall, keyboard-row precision/recall/F1, cross-row contamination, false non-keyboard windows, and isolated keyboard-chord precision/recall on real piano audio. Useful knobs include `MUSIC_ANALYZER_MAESTRO_MIN_PRECISION_PERCENT` (default 90), `MUSIC_ANALYZER_MAESTRO_MIN_KEYBOARD_RECALL_PERCENT` (default 90), `MUSIC_ANALYZER_MAESTRO_MAX_CONTAMINATION_PERCENT` (default 5), `MUSIC_ANALYZER_MAESTRO_MAX_FALSE_NON_KEYBOARD_PERCENT` (default 5), and `MUSIC_ANALYZER_MAESTRO_MIN_CHORD_PRECISION_PERCENT` (default 85). MAESTRO is useful for keyboard row, sustain, and chord regressions, but it is a single-instrument dataset and does not replace the URMP mixed-source gate.

`make test-real-egmd-20` is an optional focused analyzer gate for E-GMD. It expects the official metadata CSV plus paired WAV/MIDI files, parses drum MIDI and velocity hits, selects drum-hit windows, and reports drum-category recall/precision/F1 plus false-positive drum windows on real drum audio. Useful knobs include `MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT` (default 35), `MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT` (default 50), and `MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT` (default 75). E-GMD is useful for bass drum/snare/hi-hat/tom/cymbal regressions, but it is a drum-only dataset and does not replace the URMP mixed-source gate.

`make inspect-real-musicnet-remote` checks the current Zenodo metadata for MusicNet before downloading the large archive. It verifies the open CC-BY-4.0 record, the `musicnet.tar.gz` WAV/CSV audio-label archive, `musicnet_metadata.csv`, `musicnet_midis.tar.gz`, and description text that promises note timing and instrument labels. `make test-real-musicnet-20` is an optional complementary real-mix gate for an extracted MusicNet dataset. It reports real-mix pitch-class recall/precision/F1 and global chord recall/precision/F1; useful knobs include `MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT` (default 40), `MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT` (default 35), `MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT` (default 20), and `MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT` (default 20). MusicNet does not have isolated source audio, so it does not replace URMP's same-song stem/summed-mix gate, but it adds 20+ real chamber recordings with CSV note/instrument labels to stress note and chord detection on real mixed audio.

Optional CMake build, assuming the OBS development dependencies are installed system-wide:

```sh
/usr/bin/cmake -S . -B build-cmake -DCMAKE_BUILD_TYPE=Release
/usr/bin/cmake --build build-cmake
```

## Performance Notes

The plugin intentionally avoids expensive per-frame work:

- No allocation in the OBS audio callback after source creation.
- Analyzer work runs on a worker thread and drops stale windows instead of queueing unbounded work.
- A fixed maximum ring buffer, configurable analysis windows, and configurable update intervals bound CPU use.
- Notes/chords use precomputed Goertzel probes instead of per-callback FFT allocation.
- The overlay updates a single texture at a capped frame rate.

This is approximate mix detection, not true isolated stem separation. For precise separation of crowded mixes, an offline or GPU-backed ML stem separator would be needed before OBS receives the audio.
