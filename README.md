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
make prepare-drum-machine-samples
make test-drum-machine-samples
make analyze-drum-rule-grid
make find-drum-attribute-patterns
make analyze-mdb-drums-misses
make analyze-star-drums-misses
```

Override `DRUM_SAMPLE_SOURCE_DIR`, `DRUM_SAMPLE_BUILD_DIR`, `DRUM_SAMPLE_LIMIT`, `DRUM_SAMPLE_SELECTION`, `DRUM_SAMPLE_SOURCE_FILTER`, or set `DRUM_SAMPLE_REFRESH=1` if your sample library is elsewhere, you want a different per-category sample count, source-label regex, or selection strategy, or you need to force a rescan of an existing complete manifest. The importer reads plain WAV files, ZIP archives, and RAR archives when `unrar` is installed. The default `DRUM_SAMPLE_SELECTION=first` local one-shot gate copies up to 160 samples per category, for 1,120 real drum samples when the configured library has enough material, and stops scanning once every category reaches the configured limit. The importer treats compact drum-machine closed/open-hat aliases such as `707oh`, `Realch1`, and `HHOD4`, plus `Hat Pedal`, as hi-hats even when they live under a generic `Cymbals` folder, and treats `Sidestick`, `Side-Stick`, and the observed `Sideststick` spelling as rim/side-stick hits before snare-folder matching. Tom labels now require a real tom token instead of a substring such as `custom`, and unsupported clap/clave/conga-style filenames are skipped unless the filename also identifies a supported snare/rim category. The harness warms the analyzer with a neutral low-level bed instead of pitched notes, credits the expected drum if it appears across the first 50 ms analyzer hop, then keeps unrelated false-positive counts anchored to the onset frame. It prints recall, precision, false positives, a 7x7 active matrix, and a primary matrix that separates no-hit samples from saturated ambiguous strongest-label ties. Set `MUSIC_ANALYZER_DRUM_SAMPLE_SOURCE_SUMMARY=1` to also print the worst source/kit buckets for ordinary hit misses and primary-label misses; for focused debugging, set `MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY`, `MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_SOURCE`, `MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_PRIMARY=1`, and `MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL=1` to print per-band detector diagnostics for a subset, including shell body ratios, snare crack, upper-tom body, and the selected body-shape family. `make analyze-drum-rule-grid` regenerates full-library kick/snare/tom verbose rows under `build/`, summarizes tom-vs-snare/kick body overlap, prints the current baseline primary counts, and replays candidate tom-promotion rules with per-category and total deltas before changing detector constants. The default gate now enforces `MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT=20`, per-category recall floors for kick/snare/hi-hat/crash/toms/ride/rim of 62/80/88/95/80/88/85 percent, `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=22`, `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=38`, and `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_RIM_FALSE_PERCENT=20`, so kick/snare/cymbal/rim one-shots cannot regress into excessive whole-kit lighting, excessive false kick/tom lighting, or lost side-stick/rim coverage. The current default gate runs in about 28 seconds and passes with recall/precision kick 155/160 and 155/338, snare 137/160 and 137/491, hi-hat 149/160 and 149/486, crash 158/160 and 158/476, toms 132/160 and 132/478, ride 147/160 and 147/456, and rim 144/160 and 144/337.

`make test-drum-samples-spread` is the faster broad-data tuning loop. It uses deterministic spread selection across plain-WAV source folders and intentionally passes `--no-archives`, so it avoids slow ZIP/RAR extraction on mounted sample libraries. Override `DRUM_SAMPLE_SPREAD_BUILD_DIR`, `DRUM_SAMPLE_SPREAD_LIMIT`, `DRUM_SAMPLE_SPREAD_MIN_RECALL_PERCENT`, or `DRUM_SAMPLE_SPREAD_MIN_PRECISION_PERCENT` for this target. The default spread gate now enforces at least 40% recall, 15% precision, category recall floors for kick/snare/hi-hat/crash/toms/ride/rim of 55/80/90/95/78/88/86 percent, `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_KICK_FALSE_PERCENT=24`, and `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=45`. On the current local drum library, the bounded spread gate prepares 858 real one-shots in about 23 seconds: kick=160, snare=160, hi-hat=160, crash=120, tom=160, ride=44, and rim=54. Current spread recall/precision is kick 149/160 and 149/307, snare 139/160 and 139/376, hi-hat 151/160 and 151/332, crash 118/120 and 118/304, toms 128/160 and 128/423, ride 41/44 and 41/253, and rim 47/54 and 47/189.

`make test-drum-machine-samples` is a focused local gate over `Roland TR-909 Drum Samples`, `dr202_samples.zip`, and `JazzFunkKit.rar`, selected with `DRUM_MACHINE_SAMPLE_FILTER`. It prepares 344 classic drum-machine/kit one-shots on the current local library: kick=58, snare=154, hi-hat=48, crash=17, tom=48, ride=8, and rim=11. Current recall/primary/precision is kick 58/58, 50/58, and 58/117; snare 149/154, 101/154, and 149/212; hi-hat 46/48, 33/48, and 46/121; crash 17/17, 12/17, and 17/64; toms 34/48, 18/48, and 34/217; ride 8/8, 6/8, and 8/57; and rim 7/11, 3/11, and 7/64. The gate caps tom false activations with `DRUM_MACHINE_MAX_TOM_FALSE_PERCENT=64`; that ceiling is still higher than the aggregate gate because 909/dr202 kick and snare samples are body-heavy and cross-light the tom row more often, but it now guards the current tom reduction instead of hiding it.

`make test-drum-samples-full` uses `DRUM_SAMPLE_FULL_BUILD_DIR`, `DRUM_SAMPLE_FULL_LIMIT`, and the `DRUM_SAMPLE_FULL_MIN_*` thresholds. It is intentionally separate from `make test` because the current local library audit found kick=5,500, snare=4,683, hihat=2,123, crash=561, tom=1,964, ride=352, and rim=502 supported one-shots after filtering unsupported clap/clave/conga-style percussion; two unreadable snare WAVs are skipped by the harness. Complete manifests are reused unless `DRUM_SAMPLE_REFRESH=1` is set, so repeated full sweeps do not re-extract ZIP/RAR members before the analyzer phase. The cached full analyzer phase currently takes about 6-7 minutes and enforces at least 35% recall, 3% precision, category recall floors for kick/snare/hi-hat/crash/toms/ride/rim of 48/85/94/95/65/90/88 percent, primary-label floors of 88/60/60/58/20/50/66 percent, and `MUSIC_ANALYZER_DRUM_SAMPLE_MAX_TOM_FALSE_PERCENT=45`. Current full-library recall/primary/precision is kick 5,103/5,500, 4,843/5,500, and 5,103/7,135; snare 4,186/4,681, 2,846/4,681, and 4,186/7,177; hi-hat 2,051/2,123, 1,443/2,123, and 2,051/4,281; crash 554/561, 346/561, and 554/2,845; toms 1,418/1,964, 395/1,964, and 1,418/7,442; ride 336/352, 192/352, and 336/2,624; and rim 447/502, 338/502, and 447/2,262. Treat this as a broad diagnostic benchmark for improving drum classification, not a precision claim. `make test-real-world-samples-full` also runs `make test-drum-machine-samples` and this full local drum sweep when `DRUM_SAMPLE_SOURCE_DIR` exists, runs E-GMD's 43-kit real-drum analyzer gate when `MUSIC_ANALYZER_EGMD_ROOT` or `EGMD_PATH` is set, and skips those optional local roots otherwise so the full internet-backed benchmark stays portable.

Prepare and test MIDI-rendered single-note fixtures for piano, guitar, bass, synth, strings, vocals, and GM drum kits:

```sh
make prepare-instrument-samples
make test-instrument-samples
make analyze-instrument-sample-attributes
make inspect-instrument-sample-owner-buckets
make find-instrument-owner-patterns
```

This target renders build-local WAV fixtures under `build/piano_samples`, `build/guitar_samples`, `build/bass_samples`, `build/synth_samples`, `build/strings_samples`, `build/vocals_samples`, and `build/drum_kit_samples` using FluidSynth. By default it uses the system FluidR3 GM SoundFont, or downloads/extracts the internet-sourced `fluid-soundfont-gm` package into `build/instrument_sample_sources` if needed. The default fixture target is at least 1000 one-note files per family; the current FluidR3 GM set renders 1024 piano, 1040 guitar, 1030 bass, 1080 synth, 1116 strings, 1020 vocals, and 1043 GM drum-kit samples. The drum-kit fixture now covers the common GM category alternates: kick 35/36, snare 38/40, rim 37, hi-hat 42/44/46, crash 49/57, toms 41/43/45/47/48/50, and ride 51/53/59. The gate currently runs 7,419 checks with a cached analyzer phase of about 149 seconds, including same-pitch C4 source-mode checks across piano, guitar, bass, synth, strings, and vocals plus same-pitch full-mix C and C-E-G chord checks from rendered samples. `make analyze-instrument-sample-attributes` writes `build/instrument_sample_attributes.tsv` with per-note raw pitch rank, +/-cent probe results, full-mix owner/timbre scores, harmonic ratios, spectral centroid/slope/noise, and drum trigger details. `make inspect-instrument-sample-owner-buckets` groups that TSV by expected family and full-mix debug owner so piano/guitar/synth/string/vocal ownership patterns can be compared before changing detector rules; bass is reported as `bass_debug` because full-mix bass display uses a separate bass path. `make find-instrument-owner-patterns` mines the largest current owner-miss buckets by default, or a focused bucket when `PATTERN_BUCKET='owner_miss:piano->guitar'` is provided. Override `INSTRUMENT_SAMPLE_TARGET_PER_FAMILY`, `INSTRUMENT_SAMPLE_JOBS`, `INSTRUMENT_SAMPLE_SOUNDFONT`, `INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE`, `INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY`, or `INSTRUMENT_SAMPLE_DRUM_KITS` to change the rendered fixture set. Known non-one-note or mislabeled SoundFont cells are excluded from the manifests and recorded in `build/instrument_sample_exclusions.tsv` with reasons; for FluidR3 GM, the orchestra-kit hi-hat cells are excluded because they render as shell-like, non-cymbal audio. FluidR3 GM is MIT-licensed; only generated files under `build/` are written.

Download and test internet-sourced real-world sample fixtures:

```sh
make test-real-note-samples
make test-real-note-samples-full-mix
make analyze-real-note-misses
make test-guitar-fretboard-note-samples
make test-hf-drum-kit-samples
make test-idmt-drums-samples
make test-mdb-drums-samples
make test-star-drums-samples
make test-medley-solos-samples
make test-downloaded-guitarset
make analyze-guitarset-misses
make test-guitar-techs-samples
make test-guitar-techs-chord-samples
make test-guitar-chord-mix-samples
make analyze-guitar-chord-mix-misses
make test-egfxset-guitar-samples
make test-gaps-guitar-samples
make test-gaps-guitar-samples-full
make analyze-gaps-guitar-misses
make analyze-gaps-guitar-misses-full
make test-philharmonia-samples
make test-philharmonia-samples-full
make test-good-sounds-samples
make test-iowa-piano-samples
make test-maps-piano-samples
make test-maps-piano-note-samples
make test-bach10-mf0-synth-samples
make test-iowa-bass-samples
make test-iowa-strings-samples
make test-iowa-orchestra-samples
make test-iowa-orchestra-full-samples
make test-idmt-bass-lines-samples
make test-idmt-guitar-samples
make test-tinysol-samples
make test-vocadito-samples
make test-vocalset-samples
make test-configured-real-world-samples
make test-real-world-samples
make test-real-world-samples-full
make test-real-world-samples-max
```

The cached full real-world sweep on 2026-07-21 passes and gives the current tuning baseline: NSynth covers 2,212 accepted one-note samples in isolated-source mode and now also runs a generic full-mix note/drum false-positive and row-ownership gate; Guitar Fretboard Notes covers 390 guitar notes; HF Drum Kit covers 2,100 one-shots; IDMT-SMT-Drums covers 1,823 annotated kick/snare/hi-hat clips; MDB Drums covers 23 real drum recordings / 92 evaluated windows; STAR Drums preview covers 4 mixed-song drum recordings / 16 evaluated windows; GuitarSet covers 1,491 chord-checkable real guitar windows; Guitar-TECHS covers 547 single-note guitar clips plus 7,788 chord windows; Guitar Chord Mix covers 511 major/minor chord windows; GAPS covers 244 classical-guitar chord windows in the bounded gate and has a dedicated full target for all available performances; IDMT-SMT-Guitar covers 2,173 monophonic guitar clips; Philharmonia full covers 7,285 acoustic one-note samples; Iowa orchestra full covers 682 one-note samples; TinySOL covers 2,435 orchestral one-note samples; Vocadito covers 370 vocal clips; and the local full drum library covers 15,683 usable one-shots when `/media/kyz/sshflashtor/DrumSamples` is present. VocalSet is also wired as a large optional vocal target for cached/full and max runs. The sample evidence shows isolated pitch and broad timbre detection are already strongly covered; the remaining high-value tuning areas are full-mix timbre ownership, real guitar chord recall in performance-style datasets, drum cross-class lighting/primary ambiguity in broad one-shot libraries, and real expressive vocal coverage. The downloaded audio stays under `build/` and is not vendored into git.

Use `make test-real-world-samples-full` for the broad cached benchmark. It runs large optional gates such as Good-sounds, Medley-solos, MAPS, Bach10, and VocalSet only when their archives or source roots are already present under `build/real_sample_sources` or configured by environment variables. Use `make test-real-world-samples-max` when you intentionally want the largest available internet-backed sample sweep; it downloads and runs those optional Good-sounds, Medley-solos, MAPS, Bach10, VocalSet, TinySOL, Guitar-TECHS, GAPS, IDMT, Philharmonia, Iowa, NSynth, drum, and configured-real-dataset gates instead of silently skipping missing archives. The max target also overrides bounded preparation defaults where supported: dedicated full GAPS (`make test-gaps-guitar-samples-full`, writing `build/gaps_guitar_samples_full` with `GAPS_GUITAR_FULL_SAMPLE_LIMIT=0`), unbounded Good-sounds (`GOOD_SOUNDS_SAMPLE_LIMIT=0`), unbounded Medley-solos per-instrument selection (`MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=0`), all MAPS piano/chord and isolated-note recordings, all Iowa piano candidates, and all discovered Iowa orchestra page ZIPs.

`make test-real-note-samples` downloads the public [NSynth test split](https://magenta.tensorflow.org/datasets/nsynth) into `build/real_sample_sources`, prepares one-note real-audio fixtures under `build/real_note_samples`, and checks exact pitch/instrument-family detection. The current prepared set has 2,212 accepted samples: 137 bass, 346 guitar, 1,117 piano/keyboard, 22 vocal, and 590 other-instrument examples. It excludes out-of-range notes, synthetic-source examples, metadata-marked non-one-note qualities such as `multiphonic` and `tempo-synced`, plus seven exact unstable pitch-reference examples. The gate now enforces per-family minimum coverage with `REAL_NOTE_MIN_BASS`, `REAL_NOTE_MIN_GUITAR`, `REAL_NOTE_MIN_PIANO`, `REAL_NOTE_MIN_VOCALS`, and `REAL_NOTE_MIN_OTHER`, so a future dataset-preparation change cannot silently collapse coverage to one family. The archive is about 333 MB, is cached under `build/`, and the cached local test currently runs in about 18 seconds.

`make test-real-note-samples-full-mix` reuses the same NSynth fixtures but analyzes them as a generic full-mix `Speaker Monitor` source. It requires the expected pitch class to appear in any visible note row, scans sustained offsets before deciding expected-family ownership, enforces at least `REAL_NOTE_FULL_MIX_MIN_EXPECTED_ROW_PERCENT` expected-family row ownership (default 80), and caps false drum lighting from melodic one-note audio with `REAL_NOTE_FULL_MIX_MAX_DRUM_ACTIVE_PERCENT` (default 25). It also enforces per-family expected-row floors with `REAL_NOTE_FULL_MIX_MIN_BASS_EXPECTED_ROW_PERCENT`, `REAL_NOTE_FULL_MIX_MIN_GUITAR_EXPECTED_ROW_PERCENT`, `REAL_NOTE_FULL_MIX_MIN_PIANO_EXPECTED_ROW_PERCENT`, `REAL_NOTE_FULL_MIX_MIN_VOCALS_EXPECTED_ROW_PERCENT`, and `REAL_NOTE_FULL_MIX_MIN_OTHER_EXPECTED_ROW_PERCENT`, currently 65/70/85/90/75 percent. Current cached local results are 2,212/2,212 full-mix any-row pitch hits, 2,115/2,212 expected-family row hits, and 150/3,734 analyzed sustain windows with any drum row active after tonal sustain suppression. The gate prints expected-row counts by family plus a first-visible-row confusion matrix, currently showing sustained expected-row hits of bass 137/137, guitar 320/346, piano 1,075/1,117, vocals 21/22, and other 562/590; the cached analyzer phase currently runs in about 23 seconds. This gate is included in `make test-real-world-samples` because it catches the generic speaker/music-source path that isolated-source tests do not exercise.

`make analyze-real-note-misses` reruns the NSynth full-mix gate with guarded verbose miss logging, writes `build/real_note_full_mix_verbose.out` and `build/real_note_full_mix_verbose.err`, then summarizes the remaining hard pitch misses plus expected-row ownership misses by source family, source-to-observed-row pair, expected pitch class, first observed row, strongest detected note, nearest pitch offset, whether the expected pitch was present anywhere in the analyzer's visible or ambiguous note grids, which visible rows contained the expected pitch during the scanned windows, and the collapsed per-buffer row path for that expected pitch. The row-path output separates stable wrong-row ownership from unstable paths such as `guitar>vocals` or `amb+bass`, which makes threshold changes easier to judge against real audio. The summary also prints representative sample IDs for the largest miss buckets, so detector changes can be checked against concrete real-audio examples instead of only aggregate counts. Use this before changing detector constants so improvements are judged against real remaining misses instead of by removing difficult samples from the gate.

`make analyze-real-note-attributes` runs the same NSynth full-mix corpus in diagnostic mode, keeps scanning every sustained offset instead of stopping at the first hit, writes per-buffer detector attributes to `build/real_note_full_mix_attributes.tsv`, and prints a compact summary of status/source/first-row groups plus median ownership scores, pitch confidence, periodicity, fit error, noise, and harmonic partial ratios. `make inspect-real-note-attribute-buckets` prints detailed min/quartile/median/max ranges for the largest current hit and miss buckets from that TSV. `make find-real-note-attribute-patterns` mines the largest current real-note miss buckets by default, or a focused bucket with the `PATTERN_BUCKET='status:family/source->first_row'` grammar. Use these before adding new classifier rules: they show measured timbre patterns for hits and misses across the whole tested corpus instead of only the failure snippets.

`make test-vocadito-samples` downloads [Vocadito](https://zenodo.org/records/5578807), a 58.5 MB CC BY 4.0 dataset of 40 short solo monophonic vocal recordings with trained-musician F0, note, lyric, and language annotations. The preparer keeps only A1 note annotations that are long enough for a stable mid-note clip, inside the analyzer vocal range, and within `VOCADITO_MAX_CENTS` of a chromatic MIDI note, then writes derived WAV snippets under `build/vocadito_samples`. The current default gate prepares 370 real vocal clips across 27 note names from F2-G#4 and requires at least `VOCADITO_MIN_VOCALS=300` clips. Current local results are 369/370 isolated-vocal detections with one tolerated miss, and the cached analyzer phase currently runs in about 7 seconds. Override `VOCADITO_ANNOTATOR`, `VOCADITO_SAMPLE_LIMIT`, `VOCADITO_MIN_VOCALS`, `VOCADITO_MAX_CENTS`, or `VOCADITO_MIN_NOTE_DURATION` to tune the sweep.

`make test-vocalset-samples` downloads [VocalSet with corrected annotations](https://zenodo.org/records/10200775), prepares stable one-note clips from the `extended 4` note CSV truth, and runs the same isolated-vocal real-note analyzer gate under `build/vocalset_samples`. This is intentionally an explicit/large optional target: `make test-real-world-samples-full` runs it only when `build/real_sample_sources/vocalset/VocalSet.zip` is already cached, while `make test-real-world-samples-max` downloads it. The default preparer balances up to `VOCALSET_SAMPLE_LIMIT=1200` chromatic sung-note clips, requires `VOCALSET_MIN_VOCALS=800`, filters non-sung or unstable techniques through `VOCALSET_ALLOWED_TECHNIQUES`, and keeps only segments within `VOCALSET_MAX_CENTS=25` of the expected MIDI pitch.

`make test-guitar-fretboard-note-samples` downloads the public [Guitar Single-Note Recordings](https://huggingface.co/datasets/collegefishiesd/guitar-fretboard-notes) dataset through the Hugging Face row API, writes build-local WAV fixtures under `build/guitar_fretboard_notes_samples`, and runs the shared isolated real-note gate in guitar mode. The dataset contains 390 labeled acoustic/electric guitar single notes across standard-tuned strings and frets 0-12, covering MIDI 40-76. The preparer uses only Python standard-library HTTP/JSON/WAV handling and prints progress every 25 samples; reruns skip already-downloaded WAV files. Current local results are 389/390 isolated-guitar detections in about 17 seconds after download. One row, `train_0073_ele_high_E_f5_A4`, is kept visible as a tolerated dataset outlier: metadata says A4, but the downloaded audio is dominated by other pitches in the analyzer inspection. Override `GUITAR_FRETBOARD_NOTES_LIMIT`, `GUITAR_FRETBOARD_NOTES_MIN_GUITAR`, or `GUITAR_FRETBOARD_NOTES_MAX_FAILURES` if you want a smaller smoke run or stricter handling of that row.

`make test-hf-drum-kit-samples` downloads the public [airasoul/drum-kit](https://huggingface.co/datasets/airasoul/drum-kit) one-shot dataset through the Hugging Face row API, keeps the unambiguous labels that match the analyzer's drum categories, and writes build-local WAV fixtures under `build/hf_drum_kit_samples`. It maps `hat` to hi-hat and skips labels outside the current UI model such as `clap`, `conga`, and generic `cymbal`. The current prepared set has 2,100 real drum one-shots: 300 each for kick, snare, hi-hat, crash, tom, ride, and rim. Reruns validate and reuse a complete cached manifest before touching the Hugging Face API, so a temporary remote `429` does not break an already-prepared local gate. The gate currently enforces a broad diagnostic floor with `HF_DRUM_KIT_MIN_RECALL_PERCENT=20` and `HF_DRUM_KIT_MIN_PRECISION_PERCENT=18`, primary-label floors for kick/snare/hi-hat/crash/tom/ride/rim of 60/90/95/90/85/95/45 percent, and `HF_DRUM_KIT_MAX_KICK_FALSE_PERCENT=12`, then prints the same active and primary matrices as the local drum-sample gates. Current cached local recall is kick 289/300, snare 293/300, hi-hat 299/300, crash 295/300, tom 300/300, ride 300/300, and rim 192/300. Primary-label hits are kick 289/300, snare 288/300, hi-hat 294/300, crash 291/300, tom 294/300, ride 300/300, and rim 146/300, so this gate now passes while still acting as a broad real one-shot diagnostic benchmark for reducing cross-class drum lighting, especially rim/snare/kick/tom confusion. Override `HF_DRUM_KIT_LIMIT_PER_CATEGORY` for a smaller loop; use `0` for the full 2,100-sample sweep.

`make test-idmt-drums-samples` downloads [IDMT-SMT-Drums](https://zenodo.org/records/7544164), a 287.1 MB real drum-loop dataset, then extracts annotated isolated training-hit windows from SVL-labelled `#KD#train.wav`, `#SD#train.wav`, and `#HH#train.wav` tracks into `build/idmt_drums_samples`. The current default prepares every usable annotated hit window, currently 1,823 real clips: kick=697, snare=345, and hi-hat=781. The analyzer gate declares only those three classes as required, keeps crash/tom/ride/rim false activations visible as diagnostics, and enforces `IDMT_DRUMS_MIN_RECALL_PERCENT=70`, `IDMT_DRUMS_MIN_SNARE_RECALL_PERCENT=90`, `IDMT_DRUMS_MIN_SNARE_PRIMARY_RECALL_PERCENT=80`, `IDMT_DRUMS_MIN_PRECISION_PERCENT=50`, and `IDMT_DRUMS_MAX_KICK_FALSE_PERCENT=12`. Current cached local recall/primary/precision is kick 695/697, 688/697, and 695/821; snare 334/345, 291/345, and 334/654; and hi-hat 744/781, 438/781, and 744/784. The cached analyzer phase currently runs in about 44 seconds. This adds real manually annotated kick/snare/hi-hat timing coverage beyond synthetic GM kits and one-shot label folders.

`make test-mdb-drums-samples` downloads the public [MDB Drums](https://github.com/CarlSouthall/MDBDrums) drum-only WAV tracks and subclass onset annotations, converts those annotations into build-local GM drum MIDI files, writes an E-GMD-shaped metadata CSV under `build/mdb_drums_samples`, and reuses the existing E-GMD drum-loop analyzer gate. MDB Drums adds 23 MedleyDB-derived real drum performances with kick, snare, hi-hat, cymbal, tom, ride, rim/side-stick, and brush-style subclass labels. The preparer maps supported subclass labels such as `KD`, `SD`, `SST`, `CHH`, `OHH`, `CRC`, `RDC`, `LFT`, and `MHT` to GM drum MIDI notes, skips unsupported percussion labels such as tambourine, and exposes the skip counts in the prepare log. Useful knobs include `MDB_DRUMS_SOURCE_ROOT` for a local extracted checkout, `MDB_DRUMS_RECORDING_LIMIT` for bounded tuning loops, `MDB_DRUMS_MIN_RECORDINGS` (default 20), `MDB_DRUMS_REQUIRED_WINDOWS` (default 80), `MDB_DRUMS_MIN_RECALL_PERCENT` (default 45 aggregate recall), `MDB_DRUMS_MIN_WINDOW_RECALL_PERCENT` (default 0 because dense human drum-loop frames can have overlapping annotations), `MDB_DRUMS_MIN_PRECISION_PERCENT` (default 45), and `MDB_DRUMS_MAX_FALSE_POSITIVE_WINDOWS_PERCENT` (default 75). Current cached local results on all 23 tracks are 121/192 drum-category hits, 58.45% precision, 63.02% recall, and 55.43% false-positive windows, with per-row recall kick 55/55, snare 32/47, hi-hat 26/59, crash 4/13, tom 1/5, ride 3/12, and rim 0/1; tom over-activation remains the largest diagnostic bucket with 29 false positives. `make analyze-mdb-drums-misses` reruns this gate with guarded verbose miss/false-positive logging, writes `build/mdb_drums_misses.log`, and summarizes the actionable buckets; the current summary reports 61 miss windows and 51 false-positive windows, with misses dominated by hi-hat 33, snare 15, crash 9, ride 9, tom 4, and rim 1, plus false positives dominated by tom 29, kick 17, hi-hat 13, rim 10, and crash 9. This is a real drum-loop regression target, not a one-shot purity test, and is included in `make test-real-world-samples`.

`make test-star-drums-samples` downloads the public [STAR Drums](https://zenodo.org/records/15690078) preview ZIP, converts the preview annotations into build-local GM drum MIDI files, converts the selected FLAC audio flavor to WAV, writes an E-GMD-shaped metadata CSV under `build/star_drums_preview_samples`, and reuses the E-GMD drum-loop analyzer gate. The default `STAR_DRUMS_AUDIO_FLAVOR=mix` uses the final mixed-song previews; set it to `re_synthesized_drum` or `original_drum` for drum-stem-only variants when debugging. The preview currently gives 4 recordings and 16 evaluated hit windows; cached local results are 28/56 drum-category hits, 70.00% precision, 50.00% recall, and 62.50% false-positive windows. `make analyze-star-drums-misses` writes `build/star_drums_misses.log` and summarizes the mixed-song drum buckets; the current summary reports 15 miss windows and 10 false-positive windows, with misses dominated by hi-hat 13, rim 5, ride 4, snare 4, and tom 2, plus false positives dominated by tom 6 and kick 4. STAR Drums is valuable mixed-song drum stress because the non-drum audio comes from real melodic/vocal recordings, but its annotated drum stem is re-synthesized from automatic transcription, so it is a diagnostic complement rather than a replacement for real-drum datasets like E-GMD, IDMT-SMT-Drums, or MDB Drums.

`make test-drum-real-world-samples` runs the drum-focused real-audio sweep without pulling in guitar, piano, vocal, or orchestral gates: HF Drum Kit, IDMT-SMT-Drums, MDB Drums, STAR Drums, and the local bounded first/spread drum-library gates when `DRUM_SAMPLE_SOURCE_DIR` exists. Use `make test-drum-real-world-samples-full` when you also want the local drum-machine and full-library sweeps, including the current 15,683-usable-one-shot full library pass.

`make test-medley-solos-samples` downloads the public [Medley-solos-DB](https://zenodo.org/records/3464194) metadata plus the full audio archive, prepares up to `MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT=120` real three-second solo clips per source instrument under `build/medley_solos_samples`, and runs `analyzer_instrument_family_samples` in full-mix mode. The target maps distorted electric guitar, piano, and female singer to the guitar, keyboard, and vocal rows, while clarinet, flute, tenor saxophone, trumpet, and violin map to `other`. Medley-solos has instrument labels but no pitch/chord labels, so this gate checks broad timbre row activity and prints cross-row diagnostics; it is not a note or chord accuracy gate. The audio archive is about 7.9 GB, so `make test-real-world-samples-full` runs this gate only when `build/real_sample_sources/medley_solos/Medley-solos-DB.tar.gz` is already cached. Use `MEDLEY_SOLOS_MIN_RECALL_PERCENT`, `MEDLEY_SOLOS_MIN_SAMPLES`, and `MEDLEY_SOLOS_MIN_COUNTS` when tuning the row-routing floor.

`make test-downloaded-guitarset` downloads [GuitarSet](https://zenodo.org/records/3371780) annotations plus the mono microphone audio into `build/real_sample_sources/guitarset`, prepares `build/guitarset-manifest.tsv`, and runs isolated-guitar note/chord regression over all usable annotated chord windows.
`make analyze-guitarset-misses` reruns the same manifest with verbose chord-miss logging, writes `build/guitarset_verbose.log`, and prints the largest expected-quality, same-root quality, exact same-root label miss pairs, actionable miss buckets, expected-tone coverage, full-tone label misses, concrete source/time examples for visible-grid, analysis-grid, and smoothed-grid full-tone misses, and third-state breakdown for plain major/minor chords that collapse to same-root power chords.
The miss buckets separate root-shift/spurious chords, same-root-but-missing-tone cases, expected-tone-missing no-chord cases, full-tones-present root shifts, full-tones-present same-root wrong-quality cases, full-tones-present no-chord cases, and no-guitar-note cases.
The prepared manifest contains 360 excerpts; the current usable mono-mic gate covers 209 excerpts, 1,528 selected windows, and 1,491 chord-checkable windows, reporting pitch recall, guitar-row precision/recall/F1, cross-row contamination, exact chord precision/recall, simplified root/quality chord recall, major/minor versus other chord hits, and per-quality chord hits.
Current local results are 4,386/5,451 pitch-class hits, 66.54% guitar precision, 80.46% guitar recall, 72.84% guitar F1, and 1,047/1,491 exact chord hits: 637/752 major/minor opportunities and 410/739 other-chord opportunities.
The same run reports 1,163/1,491 simplified-compatible chord hits, including 647/752 major/minor opportunities and 516/739 other-chord opportunities; this distinguishes missed extensions from completely wrong chord roots. The current miss-analysis report has 444 remaining chord misses, with same-root major/minor opportunities collapsed to power chords still at 5.
The Makefile gate now enforces minimum real-audio floors for pitch recall/precision, guitar-row recall, exact chord recall/precision, exact major/minor recall, exact other-chord recall, simplified overall recall, simplified major/minor recall, and simplified other-chord recall through the `GUITARSET_MIN_*` knobs, currently 75/65/75/69/71/84/52/75/84/65 percent respectively.
The quality breakdown currently shows major 439/500 exact and 448/500 simplified, minor 197/255 exact and 199/255 simplified, sus2 54/88, sus4 44/88, 7th 94/160 exact and 112/160 simplified, maj7 94/202 exact and 136/202 simplified, m7 101/173 exact and 111/173 simplified, 9th 14/38 exact and 25/38 simplified, add9 31/61 exact and 42/61 simplified, 6th 102/173 exact and 124/173 simplified, m6 29/57 exact and 33/57 simplified, dim 14/26, m7b5 30/57, power 1/2, maj9 2/6 exact and 3/6 simplified, aug 9/27, dim7 0/8, and augmented/diminished-seventh shapes still weak.
This is a real-audio detector benchmark, not a perfect-truth pass/fail for every chord shape: major/minor chords are prioritized, while sus, diminished, augmented, seventh, ninth, add9, sixth, and power-chord templates are still counted and reported. Guitar chord labels include common equivalent aliases when the supported note grid justifies them, including omitted-fifth seventh shapes and sixth/seventh equivalences such as `C6=Am7` and `Em6=C#m7b5`.
The cached analyzer phase currently runs in about 19 seconds after extraction; first download is about 663 MB and can take much longer.

`make test-guitar-chord-mix-samples` downloads all currently matched public [Guitar Chord Mix](https://huggingface.co/datasets/ryangowe/guitar-chord-mix) WAV/JAMS clips into `build/guitar_chord_mix_samples`, writes a GuitarSet-shaped manifest from the per-string `note_midi` annotations, and runs the isolated-guitar note/chord harness. The default `GUITAR_CHORD_MIX_LIMIT=0` keeps the gate on the full available matched set; set a positive limit only when you need a smaller local tuning loop. The current cached default gate prepares 500 clips with 2,552 note annotations across 16 chord labels, tests 511 windows, and passes with 82.65% guitar recall, 68.01% guitar precision, 426/511 exact chord hits, 83.37% exact chord recall, and 87.47% exact chord precision. This is real guitar chord audio coverage and is included in `make test-real-world-samples-full`. Use `make analyze-guitar-chord-mix-attributes` before changing guitar chord detection: it writes `build/guitar_chord_mix_attributes.tsv` with expected pitch classes, displayed guitar grid, raw analysis grid, smoothed grid, raw expected-tone levels, and detected chords. Then use `make inspect-guitar-chord-mix-attribute-buckets` to print min/quartile/median/max ranges for the largest chord-hit and chord-miss support buckets. `make find-guitar-chord-mix-attribute-patterns` mines the largest current chord-miss buckets by default; pass `PATTERN_BUCKET='chord_miss:maj:visible2_analysis2_smooth2_rootvis1'` for a focused search against protected passing rows.

`make test-egfxset-guitar-samples` reuses the same Hugging Face Guitar Chord Mix WAV/JAMS preparer against its `egfxset` subtree, writes `build/egfxset_guitar_samples/manifest.tsv`, and runs the GuitarSet-shaped harness as an isolated-guitar single-note gate. The default `EGFXSET_GUITAR_SAMPLE_LIMIT=0` prepares every currently matched EGFxSet clip, with `EGFXSET_GUITAR_MIN_EXCERPTS=490` allowing a small remote-data cushion. The preparer supports `--jobs` and this target defaults `EGFXSET_GUITAR_DOWNLOAD_JOBS=8`, while preserving deterministic manifest order. The current cached gate prepares 493 real effected electric-guitar clips with one note annotation each, covers 493 windows, and passes with 493/493 pitch-class hits, 100.00% guitar recall, 70.53% guitar precision, 82.72% guitar F1, no cross-row contamination, and no false vocal windows. The remaining extra same-row harmonic pitch classes from distorted/effected single notes stay visible as a crowding diagnostic, and the gate caps single-note false chord labels with `EGFXSET_GUITAR_MAX_SINGLE_NOTE_CHORD_FALSE_PERCENT=20`.

`make test-gaps-guitar-samples` downloads a bounded subset of [GAPS](https://huggingface.co/datasets/xavriley/GAPS), the MIT-licensed Guitar-Aligned Performance Scores dataset, into `build/gaps_guitar_samples`, prefilters the Hugging Face `match/` tree so unavailable annotations are skipped before download attempts, parses the corresponding `.match` files into a GuitarSet-shaped `AUDIO`/`NOTE` manifest, and runs the isolated-guitar note/chord harness. GAPS contains 300 real solo classical-guitar performances, about 14 hours of audio, and aligned MIDI/MusicXML/match data. The default `GAPS_GUITAR_SAMPLE_LIMIT=42` prepares 40+ usable excerpts; use `make test-gaps-guitar-samples-full` for the full available local sweep in `build/gaps_guitar_samples_full`. The current cached default gate prepares 42 clips, skips about 130 unavailable match rows up front, tests 41 usable excerpts / 246 windows, and passes with 73.54% guitar recall, 65.23% guitar precision, 133/244 exact chord hits, 54.51% exact chord recall, and 58.33% exact chord precision. The target is included in `make test-real-world-samples-full` as additional real classical-guitar note/chord coverage.

`make test-philharmonia-samples` downloads the public [Philharmonia sound sample library](https://philharmonia.co.uk/resources/sound-samples/) Woodwind, Brass, and Strings archives into `build/real_sample_sources/philharmonia`, prepares balanced one-note fixtures under `build/philharmonia_samples`, and checks isolated bass, guitar-family, and other-instrument pitch detection. The importer skips undecodable archive members and pitch references outside the analyzer's strict chromatic-note model: a candidate must validate in at least two analyzer-style windows, remain within the tuning probe tolerance, beat adjacent semitone ambiguity, and reject high-note files dominated by low-frequency artifacts. The current prepared set has 2,967 decoded real samples: 128 bass, 146 guitar-family, and 2,693 other woodwind/brass/string examples. Five mandolin notes above the analyzer's documented guitar range stay in `other`. The gate enforces at least `PHILHARMONIA_MIN_BASS` real bass samples, `PHILHARMONIA_MIN_GUITAR` guitar-family samples, and `PHILHARMONIA_MIN_OTHER` other-instrument samples. Current local results are bass 128/128, guitar 146/146, and other 2,693/2,693; the cached analyzer phase currently runs in about 63 seconds. `make test-philharmonia-samples-full` reuses the same cached archives, prepares all balanced one-note candidates into `build/philharmonia_samples_full`, prints conversion progress, writes `manifest.tsv.partial` on interruption or under-coverage, and enforces the larger `PHILHARMONIA_FULL_MIN_*` coverage thresholds. Complete existing manifests are reused unless `PHILHARMONIA_REFRESH=1` is set, so rerunning the full real-world sweep does not spend minutes revalidating the same converted WAVs. The current full fixture has 7,285 decoded real samples: 471 bass, 146 guitar-family, and 6,668 other woodwind/brass/string examples. Current full local results are bass 471/471, guitar 146/146, and other 6,668/6,668; the cached full analyzer phase currently runs in about 224 seconds. The three archives are about 522 MB total and are cached under `build/`.

`make test-good-sounds-samples` downloads [Good-sounds](https://zenodo.org/records/820937), a 13.9 GB real monophonic instrument dataset with one 48 kHz mono FLAC per note plus SQLite annotations for `sounds`, `takes`, `packs`, and `ratings`. The preparer reads the database directly from the archive, maps the `bass` instrument to the bass detector and the other Good-sounds instruments to `other`, converts a source-balanced sample set into `build/good_sounds_samples`, and reuses the shared real-note analyzer gate. The default prepares up to `GOOD_SOUNDS_SAMPLE_LIMIT=1000` files, requires at least `GOOD_SOUNDS_MIN_SAMPLES=500` with `GOOD_SOUNDS_MIN_BASS=50` and `GOOD_SOUNDS_MIN_OTHER=450`, and tolerates up to `GOOD_SOUNDS_MAX_FAILURES=20` detector misses so the gate can expose real weak notes without blocking every tuning pass. `make test-real-world-samples-full` runs this gate only when `build/real_sample_sources/good_sounds/good-sounds.zip` is already cached; call `make test-good-sounds-samples` explicitly to download the large archive.

`make test-iowa-piano-samples` downloads the public [University of Iowa Musical Instrument Samples piano page](https://theremin.music.uiowa.edu/MISpiano.html), converts selected AIFF notes into `build/iowa_piano_samples`, and checks isolated keyboard pitch detection. It is also included in `make test-real-world-samples` so the broad real-audio benchmark covers acoustic piano notes in addition to NSynth, GuitarSet, Philharmonia, and Iowa double bass. That host can be slow for direct AIFF transfer, so the importer uses resumable `.part` downloads, bounded curl timeouts, configurable retry/resume attempts via `IOWA_PIANO_DOWNLOAD_RETRIES`, temporary WAV conversion, per-file progress output, and a deterministic URL-pattern fallback if the HTML page stalls. The prepare step now enforces the same minimum piano coverage as the analyzer gate; if the remote host times out before enough files are prepared, it writes `manifest.tsv.partial` and fails instead of silently testing a tiny subset. Reruns reuse cached page, AIFF, and WAV files. Use `IOWA_PIANO_SAMPLE_LIMIT=0` to prepare every discovered piano note file or keep the default 85-file gate for a smaller acoustic-piano sweep. The current default gate prepares 85 real acoustic piano notes from B0-C8 and passes 85/85 isolated-keyboard detections; the cached analyzer phase currently runs in about 2 seconds. The generated audio is cached under `build/` and is not committed.

`make test-maps-piano-samples` downloads [MAPS](https://zenodo.org/records/18160555) `ENSTDkCl.zip`, prepares a bounded MAESTRO-shaped subset under `build/maps_piano_samples`, and reuses `analyzer_maestro` in isolated-keyboard mode. The preparer selects paired WAV/MIDI recordings from MAPS usual-chord, random-chord, and music folders by default (`MAPS_PIANO_KINDS=UCHO,RAND,MUS`), writes `maestro-v3.0.0.csv`, and leaves isolated single-note MAPS files to the separate note-focused target. The default prepares up to `MAPS_PIANO_RECORDING_LIMIT=80` recordings and requires at least `MAPS_PIANO_MIN_RECORDINGS=40` plus `MAPS_PIANO_REQUIRED_WINDOWS=80`. `make test-maps-piano-note-samples` reuses the same archive, selects MAPS isolated-note (`ISOL`) WAV/MIDI pairs into `build/maps_piano_note_samples`, accepts one-note/one-pitch-class windows, and skips chord assertions so it acts as a real Disklavier single-note keyboard gate. The note target defaults to `MAPS_PIANO_NOTE_RECORDING_LIMIT=240`, `MAPS_PIANO_NOTE_MIN_RECORDINGS=160`, and `MAPS_PIANO_NOTE_REQUIRED_WINDOWS=160`. The archive is about 2.6 GB, so call either MAPS target explicitly to download it; `make test-real-world-samples-full` runs both MAPS targets only when `build/real_sample_sources/maps_piano/ENSTDkCl.zip` is already cached.

`make test-bach10-mf0-synth-samples` downloads the public [Bach10-mf0-synth](https://zenodo.org/records/1481156) archive `Bach10-mf0-syth.tar.gz`, converts its `audio_mix` WAV files and per-stem `annotation_stems` F0 CSV files into a MusicNet-shaped fixture under `build/bach10_mf0_synth_musicnet`, and runs the mixed-audio MusicNet analyzer gate. Set `BACH10_MF0_SYNTH_SOURCE_ROOT=/path/to/Bach10-mf0-synth` to prepare an already-extracted copy without downloading. The target covers 10 four-part Bach chorales with bassoon, alto saxophone, clarinet, and violin F0-derived note labels, so it is a compact polyphonic note/chord stress add-on. The audio is synthesized/resynthesized from F0 truth rather than live recordings, so it complements real URMP/MusicNet/MAPS coverage instead of replacing it. The current cached gate evaluates 40 dense four-part windows, passes with 148/160 pitch-class hits, 92.50% recall, 87.06% precision, 22/40 simplified chord hits, 61.11% simplified global-chord precision, and 55.00% simplified global-chord recall. It now gates simplified global-chord precision/recall at 55/50 percent while keeping exact 7th/6th/maj7/dim7 chord-extension matching as a diagnostic instead of a blocking threshold. With `MUSIC_ANALYZER_MUSICNET_VERBOSE_CHORD_MISSES=1`, chord misses include expected and detected pitch classes so extension-name misses can be separated from missing-note evidence. The archive is about 127 MB; call this target explicitly to download it, while `make test-real-world-samples-full` runs it only when a source root is configured or `build/real_sample_sources/bach10_mf0_synth/Bach10-mf0-syth.tar.gz` is already cached.

`make test-iowa-bass-samples` downloads the public University of Iowa post-2012 double-bass pizzicato ZIP `Bass.pizz.ff.sulE.stereo.zip`, converts one-note AIF members into `build/iowa_bass_samples`, and checks isolated bass pitch detection. The generic `scripts/prepare_iowa_zip_samples.py` importer supports `family|nsynth_family|source|zip_url` specs, resumable ZIP downloads, temporary WAV conversion, and a pitch-reference filter so exact-note tests keep the strict chromatic model instead of accepting out-of-tune or mislabeled files. The current default gate inspects 24 ZIP members, skips 4 pitch-reference failures, prepares 20 tuned real double-bass notes, and passes 20/20 isolated-bass detections. The ZIP is about 15 MB, can download slowly from the Iowa host, is cached under `build/real_sample_sources/iowa_bass`, and is not committed.

`make test-iowa-strings-samples` downloads the public University of Iowa post-2012 violin arco sul-G ZIP, converts one-note AIF members into `build/iowa_strings_samples`, and checks isolated `other` pitch detection. The default is intentionally small because the Iowa host can be slow: it prepares 20 real violin notes from G3-D5 and passes 20/20 isolated other-instrument detections in under a second after the ZIP is cached. The generic Iowa ZIP importer also supports `--page-spec family|nsynth_family|source_prefix|page_url`, which discovers ZIP links from a post-2012 Iowa instrument page for larger manual sweeps, plus `--max-zips-per-page` for pulling a bounded representative subset. When a limit is set, the importer now balances selected rows across sources instead of filling the fixture from the first ZIP only. Override `IOWA_STRINGS_SAMPLE_LIMIT`, `IOWA_STRINGS_MIN_SAMPLES`, `IOWA_STRINGS_MIN_OTHER`, or call `scripts/prepare_iowa_zip_samples.py --page-spec ...` through `make --eval` when you want broader Iowa string coverage.

`make test-iowa-orchestra-samples` adds a broader real one-note University of Iowa gate using representative post-2012 ZIP archives for flute, oboe, Bb clarinet, horn, Bb trumpet, violin, double bass, and marimba. The target writes to `build/iowa_orchestra_samples`, caches the remote ZIPs under `build/real_sample_sources/iowa_orchestra`, pitch-checks converted AIF members, and reuses the shared real-note analyzer gate. The current prepared set has 278 tuned real samples after 25 pitch-reference skips: 21 bass and 257 other woodwind/brass/string/mallet examples, all currently detected by the analyzer. The first download can be slow on the Iowa host, but reruns reuse cached archives and the analyzer phase currently runs in about 6 seconds. `make test-real-world-samples-full` includes this target.

`make test-iowa-orchestra-full-samples` expands the Iowa ZIP importer from representative URLs to post-2012 instrument pages for flute, alto flute, bass flute, oboe, Eb/Bb/bass clarinet, bassoon, soprano/alto saxophone, horn, trumpet, trombone, tuba, violin, viola, cello, double bass, marimba, xylophone, vibraphone, bells, and crotales, plus the known double-bass pizzicato ZIP used by the focused bass gate. The target keeps one ZIP per page by default, caches page HTML and archives under `build/real_sample_sources/iowa_orchestra`, prepares up to 720 pitch-checked FLAC snippets under `build/iowa_orchestra_full_samples`, and requires at least 520 tuned real one-note samples with bass plus other-instrument coverage. Current cached local results prepare 682 usable samples after 38 pitch-reference skips and pass with 25/25 bass detections plus 656/657 other-instrument detections; the one tolerated miss is a high crotales outlier that remains visible for future tuning. Use `IOWA_ORCHESTRA_FULL_MAX_ZIPS_PER_PAGE`, `IOWA_ORCHESTRA_FULL_SAMPLE_LIMIT`, or the per-family minimum knobs when doing a larger tuning pass.

`make test-idmt-bass-lines-samples` downloads [IDMT-SMT-Bass-Single-Track](https://zenodo.org/records/7544099), a 20.5 MB real electric-bass dataset with 17 bass lines and note-level onset, offset, MIDI pitch, string, fret, plucking-style, and expression-style annotations. The preparer extracts stable mid-note clips from expression-style `NO` notes into `build/idmt_bass_lines_samples`, preserving fingerstyle, picked, muted, slap-thumb, and slap-pluck examples. The shared real-note harness checks an early stable window as well as later sustain windows, which is important for these short 190-220 ms bass-line notes. The current default gate prepares 640 real bass-line clips across 22 note names from E1-D3 and requires at least `IDMT_BASS_LINES_MIN_BASS=600` clips. Current local results are 638/640 isolated-bass detections with two tolerated slap-style outliers, and the cached analyzer phase currently runs in about 14 seconds. Treat the misses as useful evidence for future bass-detector tuning rather than pruned dataset noise. Override `IDMT_BASS_LINES_EXPRESSIONS`, `IDMT_BASS_LINES_SAMPLE_LIMIT`, `IDMT_BASS_LINES_MIN_BASS`, `IDMT_BASS_LINES_MAX_FAILURES`, or `IDMT_BASS_LINES_MIN_NOTE_DURATION` to tune the sweep.

`make test-idmt-guitar-samples` downloads [IDMT-SMT-Guitar](https://zenodo.org/records/7544110), a real guitar ZIP with isolated WAVs and XML note annotations containing onset, offset, MIDI pitch, string, fret, excitation style, and expression style. The preparer keeps stable monophonic note windows, skips dead-note events and polyphonic overlaps, pitch-checks the converted snippets against the strict chromatic model, writes build-local WAVs under `build/idmt_guitar_samples`, and runs the shared isolated-guitar real-note analyzer gate. The source archive is about 1.3 GB and is cached under `build/real_sample_sources/idmt_guitar`. The current default prepares 2,173 pitch-checked real guitar clips from E2-E6; current local results are 2,168/2,173 isolated-guitar detections with 5 tolerated slide/bend misses, and the cached analyzer phase currently runs in about 48.30 seconds. Override `IDMT_GUITAR_EXPRESSIONS`, `IDMT_GUITAR_SAMPLE_LIMIT`, `IDMT_GUITAR_MIN_GUITAR`, `IDMT_GUITAR_MAX_FAILURES`, or `IDMT_GUITAR_SKIP_PITCH_CHECK=1` to tune the sweep. This adds real electric/acoustic guitar technique coverage beyond single clean notes and chord fixtures.

`make test-tinysol-samples` downloads [TinySOL](https://zenodo.org/records/3632193), a public CC BY 4.0 dataset of 2,478 real isolated musical notes with CSV metadata and MIDI pitch IDs. The preparer accepts both the older `Instrument Name` metadata header and the current `Instrument (in full)` header, matches TinySOL's ZIP layout from metadata family/instrument/technique fields, copies non-resampled WAV files from `TinySOL.zip` into `build/tinysol_samples`, maps contrabass to bass, accordion to keyboard/piano, and brass/woodwind/string instruments to other, then runs the shared isolated real-note analyzer gate. The gate is explicit opt-in because the archive is about 898 MB; interrupted archive downloads are kept as `TinySOL.zip.part`, reruns use `aria2c` with parallel resume when available and fall back to `curl -C -`, and the Makefile validates the ZIP before promoting it to the final archive path. The current prepared set has 2,435 non-resampled real samples: 303 bass, 251 piano/keyboard, and 1,881 other brass/woodwind/string examples. Current local results are bass 303/303, piano 251/251, and other 1,881/1,881; the cached analyzer phase currently runs in about 50 seconds. Override `TINYSOL_SAMPLE_LIMIT`, `TINYSOL_MIN_SAMPLES`, `TINYSOL_MIN_BASS`, `TINYSOL_MIN_PIANO`, or `TINYSOL_MIN_OTHER` to tune the sweep; set `TINYSOL_INCLUDE_RESAMPLED=1` if you intentionally want TinySOL pitch-shifted rows included.

`make test-configured-real-world-samples` runs all configured local real-dataset analyzer gates without requiring URMP. It uses the same root detection as `make test-real-goal-20`, but treats URMP, MusicNet, MedleyDB, MUSDB18, Slakh2100, ChoralSynth, CocoChorales, SynthSOD, Vocal Ensemble F0 Aggregate, prepared multitrack, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD as optional local roots. This target is useful after placing extracted datasets under `MUSIC_ANALYZER_DATASET_ROOT` or setting the dataset-specific `*_ROOT`/`*_PATH` variables: available roots become additional note/chord/instrument regression coverage, missing roots are reported and skipped. `make test-real-world-samples-full` runs the regular real-world sample benchmark plus Guitar-TECHS single notes, Guitar-TECHS chords, Guitar Chord Mix, EGFxSet, GAPS guitar, IDMT guitar, Iowa strings, Iowa orchestra, Iowa full-page orchestra, Philharmonia-full, TinySOL, any cached Good-sounds, Medley-solos, MAPS, and Bach10-mf0-synth archives, including MAPS chord/music and isolated-note gates, the full local drum sweep when `DRUM_SAMPLE_SOURCE_DIR` exists, and this configured-real-dataset sweep. `make test-real-world-samples-max` is the download-heavy version for collecting as much public sample evidence as practical in one run, with the supported dataset limits set to unbounded rather than their regular tuning-loop defaults.

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

`make test` builds standalone analyzer executables outside OBS and also runs `make test-standalone`, which verifies the SDL standalone target, the shared renderer, and the Makefile/CMake isolation that keeps SDL out of the OBS plugin target. It first validates the checked real-dataset catalog used to decide which public datasets can provide note-ground-truth coverage. Each core analyzer executable is run through `scripts/run_with_duration.sh`, so the test log includes wall-clock duration lines. `analyzer_smoke` covers the basic signal path. `analyzer_cases` runs broad synthetic note, instrument, chord, note-matrix, quiet-note rejection, realistic harmonic chord, same-note timbre split, isolated-source spillover rejection, explicit input-mode behavior, BPM estimation, mixed-source timbre routing, multi-instrument mix, URMP same-song multitrack metadata fixtures, and root-candidate cases, including bass B0-G4, guitar E2-E6, keyboard/other A0-C8, and vocal E2-C6. `analyzer_midi_ranges` covers GM drum MIDI notes, rim/side-stick detection, normal bass/piano/guitar/synth/string/vocal note ranges, and a combined full-mix MIDI arrangement. When `DRUM_SAMPLE_SOURCE_DIR` exists, `make test` also runs both `make test-drum-samples` and `make test-drum-samples-spread`, which copy classified one-shot kick, snare, hi-hat, crash, tom, ride, and rim WAV samples into build-local sample folders and check per-category recall across first-file and deterministic spread selections. Use `make analyze-drum-primary-misses` after changing drum scoring or adding drum samples; it reruns the tom, snare, and rim spread subsets with verbose primary diagnostics and summarizes expected-vs-detected body/segment/trigger/level ratios plus low/mid/high energy balance. When FluidSynth is available, `make test` also runs `make test-instrument-samples`, which renders and verifies 1000+ SoundFont-backed fixtures per piano, guitar, bass, synth, string, vocal/choir, and GM drum-kit family, plus crowded-combination and rendered same-pitch full-mix chord cases. The internet-downloaded NSynth isolated/full-mix, guitar-fretboard, Guitar-TECHS single-note/chord, Guitar Chord Mix, GAPS guitar, HF drum-kit, IDMT drums, MDB Drums, STAR Drums, Medley-solos, GuitarSet, Philharmonia, Iowa piano, MAPS piano chord/music and isolated-note, Bach10-mf0-synth, Iowa bass, Iowa strings, Iowa orchestra, IDMT bass lines, IDMT guitar, TinySOL, Vocadito, and VocalSet gates are intentionally separate because first-run downloads are large or slow; run `make test-real-world-samples` for the regular real-audio benchmark, `make test-real-world-samples-full` for the larger cache-friendly sweep, and `make test-real-world-samples-max` when you explicitly want the largest download-heavy public sample sweep. The NSynth full-mix gate prints row-confusion counts so timbre/ownership regressions are visible even when any-row pitch recall stays green.

The full-mix regression cases model public multitrack dataset layouts without downloading dataset audio. They include 20+ Slakh2100-style MIDI-rendered song fixtures, 20 ChoralSynth-style vocal multitrack fixtures, 20 CocoChorales-style chamber-ensemble fixtures, 20 SynthSOD-style orchestra/ensemble fixtures, 20 Vocal Ensemble F0 Aggregate-style real-vocal F0 fixtures, plus additional MUSDB18/MUSDB18-HQ, DSD100/Mixing Secrets, MedleyDB/2.0, MoisesDB, URMP, Bach10, TRIOS, PHENICX-Anechoic, MIREX Woodwind Quintet, RawStems, MulTTiPop, GuitarSet, MAESTRO, E-GMD, ACMID, Spheres, MDX, and Open Multitrack Testbed-style fixtures. See [docs/real_audio_dataset_candidates.md](docs/real_audio_dataset_candidates.md) for real recorded dataset candidates that can verify notes and instruments.

`make analyze-drum-primary-misses` now also prints an overall expected-vs-primary confusion summary and example sample filenames for each miss bucket, which helps compare tom/snare/rim scoring changes against real one-shot regressions.

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
make test-guitar-techs-chord-samples
make test-idmt-guitar-samples
MUSIC_ANALYZER_MAESTRO_ROOT=/path/to/maestro-v3.0.0 make test-real-maestro-20
MUSIC_ANALYZER_EGMD_ROOT=/path/to/e-gmd-v1.0.0 make test-real-egmd-20
```

`make real-dataset-sources` prints the checked public dataset sources and the exact local URMP commands. `make inspect-real-goal-20` is the combined setup preflight: it requires the URMP multitrack layout check, then runs the optional MusicNet, MedleyDB, MUSDB18, Slakh2100, ChoralSynth, CocoChorales, SynthSOD, Vocal Ensemble F0 Aggregate, prepared multitrack note-truth, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD gates when their roots are configured. The URMP preflight uses the same minimum active-track and pitch-class density knobs as the analyzer gate, and reports matched-track, candidate active-track, and candidate pitch-class min/average/max values.

`make test-real-goal-20` is the combined acceptance gate for the requested 20+ real same-song multitrack test. It requires the URMP analyzer gate, then runs the optional MusicNet real-mix gate, the MedleyDB summed-stem melody-F0 analyzer gate, MUSDB18/Spheres/GuitarSet preflights, the Slakh2100 rendered multitrack analyzer gate, the ChoralSynth synthetic vocal multitrack analyzer gate, the CocoChorales synthetic chamber-ensemble analyzer gate, the SynthSOD synthetic orchestra/ensemble analyzer gate, the Vocal Ensemble F0 Aggregate real-vocal F0 analyzer gate, the prepared multitrack note-truth analyzer gate, the MulTTiPop real-pop analyzer gate when local WAV segments are available or `MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1` is set, the MAESTRO piano analyzer gate, and the E-GMD drum analyzer gate when configured. The official URMP page routes the full package through dataset download registration, so the project does not attempt an unattended 12.5 GB download. Without `MUSIC_ANALYZER_URMP_ROOT`, the real-data check is built but skipped during normal `make test`; `make inspect-real-goal-20`, `make test-real-multitrack-20`, and `make test-real-goal-20` fail instead, so they can be used as the required 20+ real-song gate once the real URMP package is available. `inspect-real-multitrack-20` checks only the local URMP dataset layout before analyzer work.

`make test` also runs `make test-direct-fit-small-fixture`, which unpacks the committed compact direct-fit-small FLAC fixture from `tests/fixtures/direct-fit-small.tar.gz`, decodes it under `build/`, and reuses the URMP analyzer path to verify 20 pieces modeled after Bach10, TRIOS, PHENICX-Anechoic, and MIREX Woodwind Quintet instrumentation across separated sources, provided mix, summed mix, streaming mix, stateful sequence, and chord paths. The current fixture gate passes 528 checks with 240/240 provided, summed, streaming, and stateful-sequence full-mix pitch hits, 368/368 isolated-track hits, and 80/80 global-chord hits on each full-mix path. The URMP analyzer output includes isolated-track precision, exact recall, F1, cross-row contamination, octave-error rate, ambiguous assignment count, expected-instrument to detected-instrument confusion, and global-chord precision/recall/F1 for each full-mix path so false positives are visible instead of hidden by union pitch recall. `make update-direct-fit-small-fixture` refreshes that archive from the deterministic generator. `make test-bach10-fixture` remains available as the smaller Bach10-only generated regression.

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

`make test-guitar-techs-samples` is an optional focused analyzer gate for Guitar-TECHS single notes. It downloads the P1/P2 single-note ZIPs from Zenodo under `build/real_sample_sources/guitar_techs`, extracts the aligned MIDI plus DI and amplifier-mic WAV perspectives into `build/guitar_techs_samples`, writes short labeled WAV excerpts, and runs the shared real-note analyzer gate in isolated-guitar mode. With the current P1/P2 ZIPs the default prep produced 547 tested clips after 11 pitch-reference skips, and the analyzer gate detected 547/547 guitar notes in about 12.34 seconds. Useful knobs include `GUITAR_TECHS_SAMPLE_LIMIT`, `GUITAR_TECHS_MIN_GUITAR` (default 200), `GUITAR_TECHS_MAX_FAILURES` (default 0), `GUITAR_TECHS_PERSPECTIVES`, and `GUITAR_TECHS_SKIP_PITCH_CHECK=1`. This is real electric-guitar note coverage; scales and technique archives are still not part of the default target.

`make test-guitar-techs-chord-samples` downloads the P1/P2 Guitar-TECHS chord ZIPs from Zenodo under `build/real_sample_sources/guitar_techs`, extracts MIDI plus DI/amplifier-mic audio, clips candidate chord windows into `build/guitar_techs_chord_samples`, writes a GuitarSet-shaped `AUDIO`/`NOTE` manifest, and runs `analyzer_guitarset` in isolated-guitar mode. The default `GUITAR_TECHS_CHORD_SAMPLE_LIMIT=0` uses the full current P1/P2 chord sweep; set a positive limit only for a smaller local tuning loop. The current full gate prepares 7,016 clips with 25,010 note annotations, tests 7,788 selected windows, and passes with 88.46% guitar recall, 90.44% guitar precision, 89.23% exact chord recall, 87.79% exact chord precision, 94.88% simple major/minor chord recall, and 93.21% simple other-chord recall. Useful knobs include `GUITAR_TECHS_CHORD_MIN_EXCERPTS` (default 7000), `GUITAR_TECHS_CHORD_MIN_WINDOWS` (default 7000), `GUITAR_TECHS_CHORD_PERSPECTIVES`, and the `GUITAR_TECHS_CHORD_MIN_*` threshold variables for pitch, guitar-row, and chord recall/precision. The source chord archives are about 2.2 GB total; the cached analyzer phase currently runs in about 104 seconds.

`make test-guitar-chord-mix-samples` is an optional focused analyzer gate for real guitar chords. It downloads Hugging Face Guitar Chord Mix WAV/JAMS clips under `build/guitar_chord_mix_samples`, prepares a GuitarSet-shaped manifest from the six per-string `note_midi` annotations, and runs `analyzer_guitarset` in isolated-guitar mode. Useful knobs include `GUITAR_CHORD_MIX_LIMIT` (default `0` for all matched pairs; use a positive number for a bounded local loop), `GUITAR_CHORD_MIX_MIN_EXCERPTS` (default 500), `GUITAR_CHORD_MIX_MIN_WINDOWS` (default 500), and the `GUITAR_CHORD_MIX_MIN_*` threshold variables for pitch, guitar-row, and chord recall. The current full gate prepares 500 clips / 511 windows, passes with 423/511 exact chord hits, 86.86% exact chord precision, and 82.78% exact chord recall, and keeps the cached analyzer phase under 5 seconds. `make analyze-guitar-chord-mix-misses` writes verbose misses to `build/guitar_chord_mix_misses.log`; the current miss buckets are 35 root-shift/spurious-chord cases, 28 same-root missing expected tones, and 24 expected tones missing with no chord, with 9 major/minor-to-power misses still caused by missing third evidence. The miss analyzer also reports 12 analysis-grid and 7 smoothed-grid full-tone recovery examples with source names and timestamps so future guitar-chord tuning can target real windows directly.

`make test-gaps-guitar-samples` is an optional focused analyzer gate for GAPS real classical guitar. It downloads the metadata CSV, prefilters the Hugging Face `match/` tree so unavailable annotations are skipped before download attempts, downloads a bounded set of WAV performances plus corresponding `.match` files under `build/gaps_guitar_samples`, converts match-file MIDI tick ranges into `NOTE` rows, and runs `analyzer_guitarset` in isolated-guitar mode. Useful knobs include `GAPS_GUITAR_SAMPLE_LIMIT` (default 42 prepared clips), `GAPS_GUITAR_MIN_EXCERPTS` (default 40 usable excerpts), `GAPS_GUITAR_MIN_WINDOWS`, `GAPS_GUITAR_MATCH_TREE_JSON`, `GAPS_GUITAR_NO_MATCH_TREE=1`, and the `GAPS_GUITAR_MIN_*` threshold variables for pitch, guitar-row, and chord recall. Use `make test-gaps-guitar-samples-full` for the all-available sweep in `build/gaps_guitar_samples_full`; its knobs are `GAPS_GUITAR_FULL_SAMPLE_LIMIT` (default `0`), `GAPS_GUITAR_FULL_MIN_EXCERPTS`, and `GAPS_GUITAR_FULL_MIN_WINDOWS`, and `make test-real-world-samples-max` runs this full target. The current default prepares 42 clips, skips about 130 unavailable match rows up front, tests 41 usable excerpts / 246 windows after the cache is populated, passes with 133/244 exact chord hits, and keeps the analyzer phase under 5 seconds. `make analyze-gaps-guitar-misses` writes verbose misses to `build/gaps_guitar_misses.log`, and `make analyze-gaps-guitar-misses-full` does the same for the full manifest; the current bounded miss buckets are 47 root-shift/spurious-chord cases, 34 same-root missing expected tones, 15 expected tones missing with no chord, 8 full-tone same-root wrong-quality cases, 4 full-tone root-shift cases, and 3 no-guitar-note cases.

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
