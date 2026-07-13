# Music Analyzer OBS Plugin

Native OBS Studio plugin that analyzes a music mix and displays an instrument-oriented overlay:

- Drums: bass drum/kick, snare, hi-hat, crash, toms, and ride one-second scrolling hit charts
- Bass: detected note
- Keyboard: three-row piano view covering C1-B6 in two-octave bands, with lower notes folded into octave 1, higher notes folded into octave 6, and detected keys highlighted
- Vocal and other instruments: two-row 12-note octave matrix with active octaves shown as colored text
- Guitar: standard-tuning six-string fretboard view with open string plus frets 1-15 highlighted from detected notes
- Note highlights fade with detected velocity/amplitude so quiet or sustaining notes are dimmer instead of full intensity
- Notes outside the chromatic tuning window, about +/-9 cents from the equal-tempered center, are ignored instead of rounded to the nearest note
- Keyboard, guitar, and other instruments: compact chord labels; vocal stays note-only
- Keyboard chord labels are resolved from filtered notes inside a plausible hand-span cluster, so far-apart bass/melody notes are not collapsed into impossible hand chords
- Guitar chord labels are resolved from the filtered fretboard notes with CAGED-style voicing preference, so full-mix bass/root hints do not rename the guitar shape
- Mixed-source routing: duplicated pitches are not claimed by row order; keyboard, guitar, and other rows use harmonic timbre masks, while bass and vocal use conservative range gates
- Source-name hints: `guitar`, `key`, `piano`, `organ`, `synth`, `brass`, `horn`, `violin`, and `string` route detection toward the matching row
- Root: rolling 15-second root candidates with confidence, with the primary root held until sustained modulation or silence
- Chords: compact major, minor, power, sus2, sus4, diminished, augmented, 6, minor 6, dominant 7, major 7, minor 7, diminished 7, half-diminished, add9, 9, major 9, and minor 9 labels such as `C`, `Dm`, `Cdim`, `Caug`, `C6`, `Dm6`, `G7`, `Cmaj7`, `Dm7`, `Cdim7`, `Bm7b5`, `Cadd9`, `G9`, `Cmaj9`, and `Dm9`
- Equivalent chord names for the same detected pitch classes are shown together, such as `Csus2=Gsus4` or `Dm7=F6`
- Explicit instrument sources use the full chord template set; mixed sources keep conservative chord labels to avoid false extensions from other instruments

The analyzer is designed for real-time OBS use. It uses bounded DSP heuristics rather than a large ML stem-separation model: audio is downmixed into a fixed ring buffer, analyzer windows are copied to a worker thread at a configurable interval, and the OBS audio callback returns immediately after lightweight buffering. The overlay source renders a single reusable RGBA texture.

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

## Build

With the Makefile:

```sh
make
```

If the system OBS headers require SIMDe and `libsimde-dev` is not installed, `make` fetches and extracts that header-only package under `build/deps` without using sudo.

Run the analyzer tests:

```sh
make test
```

`make test` builds standalone analyzer executables outside OBS. It first validates the checked real-dataset catalog used to decide which public datasets can provide note-ground-truth coverage. `analyzer_smoke` covers the basic signal path, and `analyzer_cases` runs broad synthetic note, instrument, chord, note-matrix, quiet-note rejection, realistic harmonic chord, same-note timbre split, mixed-source timbre routing, multi-instrument mix, URMP same-song multitrack metadata fixtures, and root-candidate cases, including bass B0-G4, guitar E2-E6, keyboard/other A0-C8, and vocal E2-C6.

The full-mix regression cases model public multitrack dataset layouts without downloading dataset audio. They include 20+ Slakh2100-style MIDI-rendered song fixtures plus additional MUSDB18/MUSDB18-HQ, DSD100/Mixing Secrets, MedleyDB/2.0, MoisesDB, URMP, RawStems, MulTTiPop, ACMID, Spheres, MDX, and Open Multitrack Testbed-style fixtures. See [docs/real_audio_dataset_candidates.md](docs/real_audio_dataset_candidates.md) for real recorded dataset candidates that can verify notes and instruments.

Optional real-audio URMP regression coverage runs when a local URMP dataset is available:

```sh
make real-dataset-sources
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-goal-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-multitrack-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-20
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-multitrack-full
MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-full
MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make inspect-real-musicnet
MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make test-real-musicnet-20
MUSIC_ANALYZER_MEDLEYDB_ROOT=/path/to/MedleyDB MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=/path/to/medleydb/medleydb/data/Annotations make inspect-real-medleydb
```

`make real-dataset-sources` prints the checked public dataset sources and the exact local URMP commands. `make test-real-goal-20` is the combined acceptance gate for the requested 20+ real same-song multitrack test: it requires the URMP multitrack gate, then runs the optional MusicNet real-mix gate and MedleyDB stem preflight when their roots are configured. The official URMP page routes the full package through dataset download registration, so the project does not attempt an unattended 12.5 GB download. Without `MUSIC_ANALYZER_URMP_ROOT`, the real-data check is built but skipped during normal `make test`; `make test-real-multitrack-20` and `make test-real-goal-20` fail instead, so they can be used as the required 20+ real-song gate once the real URMP package is available. `inspect-real-multitrack-20` checks the local dataset layout before analyzer work. `make test` also runs `make test-real-goal-fixture`, which unpacks the committed URMP-shaped 20-piece lossless FLAC fixture from `tests/fixtures/urmp-mini.tar.gz`, decodes it to disposable WAV files under `build/` with `ffmpeg`, generates 20-recording MusicNet-shaped and MedleyDB-shaped fixtures, and sends all configured roots through the combined goal gate. That exercises WAV, Notes, MIDI score, full-mix, summed-stem, real-mix-label, MedleyDB stem-layout, and chord paths without downloading external datasets. Override the decoder with `FFMPEG=/path/to/ffmpeg` if needed. The URMP fixture is marker-file tagged and rejected by the real-data gate unless `MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE=1` is set by the fixture test target. Refresh that fixture with `make update-urmp-fixture` when the fixture generator changes. When pointed at a real URMP dataset, the harness requires official URMP piece folder IDs, reads URMP `AuMix`, `AuSep`, `Notes`, and `Sco` MIDI files, validates that the MIDI score pitch classes agree with the note annotations, requires at least 20 usable same-song pieces and at least 80 annotated note windows by default, checks separated tracks, then checks both the provided `AuMix` and a synthesized mix made by summing all separated tracks. It also replays each selected full-mix and summed-mix window through a short multi-frame analyzer sequence, and keeps one stateful provided-mix analyzer plus one stateful summed-mix analyzer per piece across selected windows, so note/chord smoothing is tested against same-song mixed audio instead of only fresh single-window analyzer state. Selected windows must contain at least two active source tracks and two pitch classes by default, and the coverage line reports active-track and pitch-class min/average/max values. `make test-real-goal-full` raises the required URMP gate to all 44 official pieces and at least 176 annotated windows. It prints discovered/loadable piece and window counts to diagnose incomplete dataset layouts. Set `MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE`, `MUSIC_ANALYZER_URMP_REQUIRED_PIECES`, and `MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS` to lower or raise the coverage gate. Set `MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW`, `MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW`, `MUSIC_ANALYZER_URMP_MIN_WINDOW_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_TRACK_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_MIX_RECALL_PERCENT`, `MUSIC_ANALYZER_URMP_MIN_CHORD_RECALL_PERCENT`, and `MUSIC_ANALYZER_URMP_MIN_CHORD_CHECKS` to tighten or relax the quality gate.

`make inspect-real-medleydb` is a partial second real-data preflight for MedleyDB/MedleyDB 2.0. It requires at least 20 local songs with mix plus stems and at least 20 melody-annotated multitracks by default. MedleyDB is useful for real stem and melody-F0 coverage, but it does not replace the URMP gate because it lacks full per-source note/chord ground truth.

`make test-real-musicnet-20` is an optional complementary real-mix gate for MusicNet. MusicNet does not have isolated source audio, so it does not replace URMP's same-song stem/summed-mix gate, but it adds 20+ real chamber recordings with CSV note/instrument labels to stress note and chord detection on real mixed audio.

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
