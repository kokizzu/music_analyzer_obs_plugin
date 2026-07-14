# Music Analyzer OBS Plugin

Native OBS Studio plugin that analyzes a music mix and displays an instrument-oriented overlay:

- Drums: bass drum/kick, snare, hi-hat, crash, toms, and ride one-second scrolling hit charts
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
- Full-mix ownership uses shared note evidence with harmonic fit, harmonic balance, spectral centroid/slope, local spectral noise, periodicity, onset/decay/stability history, and simultaneous-onset grouping before assigning a note to an instrument row
- Source-name hints remain as a compatibility adapter for tests and direct analyzer use: `guitar`, `key`, `piano`, `organ`, `synth`, `brass`, `horn`, `violin`, and `string` resolve to isolated modes when the caller does not set an input mode explicitly
- Root: rolling 15-second root candidates with confidence, using the full-mix global chord plus confidence-gated bass evidence so inversions do not rename the harmonic root; the primary root is held until sustained modulation or silence
- BPM: estimated tempo and confidence are shown at the bottom right when rhythmic transients provide enough evidence
- Chords: compact major, minor, lowercase power-chord `pow`, sus2, sus4, diminished, augmented, 6, minor 6, dominant 7, major 7, minor 7, diminished 7, half-diminished, add9, 9, major 9, and minor 9 labels such as `C`, `Dm`, `Cpow`, `Cdim`, `Caug`, `C6`, `Dm6`, `G7`, `Cmaj7`, `Dm7`, `Cdim7`, `Bm7b5`, `Cadd9`, `G9`, `Cmaj9`, and `Dm9`
- Equivalent chord names for the same detected pitch classes are shown together, such as `Csus2=Gsus4` or `Dm7=F6`
- Explicit instrument sources use the full chord template set; mixed sources keep conservative chord labels to avoid false extensions from other instruments

The analyzer is designed for real-time OBS use. It uses bounded DSP heuristics rather than a large ML stem-separation model: audio is downmixed into a fixed ring buffer, analyzer windows are copied to a worker thread at a configurable interval, and the OBS audio callback returns immediately after lightweight buffering. The overlay source renders a single reusable RGBA texture.

OBS and the standalone speaker-monitor executable explicitly analyze their inputs as `FullMix`, because they receive finished mixer/speaker audio. The shared analyzer still supports isolated modes for direct analyzer callers and tests; those modes are intended for real isolated bass, guitar, keyboard, vocal, or other-instrument stems.

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
- `BPM`: bottom-right estimated tempo. The percentage is confidence from recent transient timing, so sparse intros, rubato, or weak drums may show `BPM --` or a low-confidence estimate.

## Standalone Usage

Build the standalone executable:

```sh
make standalone
```

If SDL2 development headers are not installed system-wide, the Makefile downloads and extracts `libsdl2-dev` under `build/deps` for the standalone build. SDL2 is used only by `build/music-analyzer-standalone`; the OBS plugin target does not include or link SDL.

Run live from speaker/system output. The window title includes the standalone build version as `YYYY.MMDD.HHMM.shortCommitHash`. On Linux PulseAudio/PipeWire this auto-prefers an SDL capture device named like an output `monitor` or `loopback`; if SDL does not expose one, it captures `@DEFAULT_MONITOR@` through `ffmpeg`:

```sh
build/music-analyzer-standalone
```

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

Useful options include `--width`, `--height`, `--update-ms`, `--fps`, `--sensitivity`, and `--hold`.

## Build

With the Makefile:

```sh
make
```

If the system OBS headers require SIMDe and `libsimde-dev` is not installed, `make` fetches and extracts that header-only package under `build/deps` without using sudo.

Build only the standalone executable:

```sh
make standalone
```

Run the analyzer tests:

```sh
make test
```

`make test` builds standalone analyzer executables outside OBS and also runs `make test-standalone`, which verifies the SDL standalone target, the shared renderer, and the Makefile/CMake isolation that keeps SDL out of the OBS plugin target. It first validates the checked real-dataset catalog used to decide which public datasets can provide note-ground-truth coverage. `analyzer_smoke` covers the basic signal path, and `analyzer_cases` runs broad synthetic note, instrument, chord, note-matrix, quiet-note rejection, realistic harmonic chord, same-note timbre split, isolated-source spillover rejection, explicit input-mode behavior, BPM estimation, mixed-source timbre routing, multi-instrument mix, URMP same-song multitrack metadata fixtures, and root-candidate cases, including bass B0-G4, guitar E2-E6, keyboard/other A0-C8, and vocal E2-C6.

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
- Fixed 4096-sample windows and configurable update intervals bound CPU use.
- Notes/chords use precomputed Goertzel probes instead of per-callback FFT allocation.
- The overlay updates a single texture at a capped frame rate.

This is approximate mix detection, not true isolated stem separation. For precise separation of crowded mixes, an offline or GPU-backed ML stem separator would be needed before OBS receives the audio.
