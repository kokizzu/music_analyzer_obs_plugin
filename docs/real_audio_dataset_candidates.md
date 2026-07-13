# Real Audio Dataset Candidates

Last checked: 2026-07-14.

This project needs real recorded audio for stronger tests. The strict target is:

- real, non-MIDI-rendered audio;
- per-instrument or per-source audio tracks, not only a finished mix;
- aligned MIDI, note, pitch, or F0 truth so analyzer output can be verified.

Very few public datasets have all three. The practical path is to automate the
direct-fit datasets first, then use single-instrument and partial-label datasets
for focused row-level tests.

The checked catalog for this decision lives in
`tests/real_dataset_catalog.json` and is validated by
`make inspect-real-dataset-catalog`. That validator requires at least one
20-piece direct-fit dataset and currently pins URMP as the only automated
20+ real-audio gate.

## Direct Fit

These are the best candidates for full-mix and per-instrument verification.

| Dataset | Size | Why it fits | Caveat |
| --- | ---: | --- | --- |
| [URMP](https://labsites.rochester.edu/air/projects/URMP.html) | 44 pieces | Real classical duets, trios, quartets, and quintets. Each piece has isolated instrument audio, assembled mixture, MIDI score, and frame/note annotations. | Large download, about 12.5 GB. Classical chamber instruments, not pop rhythm-section stems. |
| [Bach10](https://arxiv.org/abs/1612.08727) | 10 pieces | Four-part Bach chorales with isolated anechoic recordings for bassoon, alto saxophone, clarinet, and violin. The literature describes pitch/note transcriptions and audio-score alignment. `make test-bach10-fixture` mirrors this instrumentation as a compact generated regression add-on, and `make test-direct-fit-small-fixture` includes it in the 20-piece generated direct-fit-small suite. | Small; useful as a regression add-on, not enough alone for 20+ cases. |
| TRIOS | 5 pieces | URMP survey describes 5 multitrack trio recordings with MIDI transcriptions. `make test-direct-fit-small-fixture` includes a generated trio-shaped fixture set. | Need to locate current download and license before real-audio automation. |
| MIREX Woodwind Quintet / WWQ | 1 piece | URMP survey describes individual recordings and note annotations for a classical quintet. `make test-direct-fit-small-fixture` includes a generated woodwind-quintet-shaped fixture. | Only a 54-second excerpt is publicly available according to the URMP survey. |
| PHENICX-Anechoic / Aalto Anechoic Orchestra | 4 pieces | URMP survey describes 8-10 isolated orchestral parts per piece with denoised recordings and note annotations. `make test-direct-fit-small-fixture` includes generated eight-part orchestral fixtures. | Need to verify current access, license, and annotation format before real-audio automation. |

Recommendation: start with URMP. It satisfies the user's requested 20+ real
multi-instrument cases by itself and is the clearest source for verifying
mixtures, per-instrument notes, and source assignment. The other direct-fit
datasets found so far are useful add-ons. Combined, Bach10, TRIOS, WWQ, and
PHENICX-Anechoic account for 20 direct-fit-small pieces; normal `make test`
now covers that combined instrumentation with `make test-direct-fit-small-fixture`
as a generated regression while real-audio access/layout automation remains a
future add-on.

## Real Audio With MIDI Or Note Truth But No Isolated Stems

These are still useful, but they cannot verify source separation because they do
not provide clean per-instrument audio stems for each mixture.

| Dataset | Use | Notes |
| --- | --- | --- |
| [MusicNet](https://arxiv.org/abs/1611.09827) | Mixed classical note/instrument detection with optional `make test-real-musicnet-20` real-mix gate | 34 hours, 330 recordings, 11 instruments, over 1M temporal note labels. No isolated stems. |
| [MulTTiPop](https://gclef-cmu.org/multtipop/) | Real pop mix note/instrument stress tests with optional `make inspect-real-multtipop` metadata/MIDI preflight and `make test-real-multtipop-20` local-audio analyzer gate | 572 commercial-pop segments with aligned multitrack MIDI metadata, published at [HuggingFace](https://huggingface.co/datasets/gclef-cmu/multtipop). Audio is sourced via YouTube IDs/timestamps; recommended for evaluation, not training. |
| RWC-Pop | Real pop mix transcription | Cited by MulTTiPop as 100 original pop recordings with multitrack MIDI. Access/licensing needs verification. |
| [POP909](https://arxiv.org/abs/2008.07142) | Pop melody, lead, piano, chord checks | 909 popular-song arrangements with MIDI aligned to original audio plus tempo, beat, key, and chord annotations. Not per-instrument stems. |
| [MAESTRO](https://magenta.tensorflow.org/datasets/maestro) | Keyboard row, sustain, and chord tests with optional `make test-real-maestro-20` analyzer gate | 1,276 real Disklavier piano performances, 198.7 hours, paired WAV/MIDI with about 3 ms alignment, official metadata CSV/JSON, and over 7M note labels. Single instrument only. |
| [PianoVAM](https://arxiv.org/abs/2509.08800) | Keyboard row, fingering/hand plausibility | Piano audio, MIDI, video, hand landmarks, and fingering labels. Single instrument only. |
| [GuitarSet](https://guitarset.weebly.com/) | Guitar fretboard tests with optional `make inspect-real-guitarset` preflight and `make test-real-guitarset-20` analyzer gate | 360 live guitar excerpts with hexaphonic pickup, per-string audio, microphone audio, JAMS MIDI-note/fret/chord annotations, and Zenodo download at [10.5281/zenodo.3371780](https://zenodo.org/records/3371780). Single instrument only. |
| [Guitar-TECHS](https://arxiv.org/abs/2501.03720) | Electric guitar notes, chords, scales, techniques | Over 5 hours, DI/mic/amp perspectives, synchronized six-track MIDI labels. Single instrument only. |
| [GAPS](https://arxiv.org/abs/2408.08653) | Classical guitar note/fretboard tests | 14 hours of real guitar audio with high-resolution note-level MIDI alignments. Single instrument only. |
| [GOAT](https://arxiv.org/abs/2509.22655) | Electric guitar tablature/fret checks | 5.9 hours of DI electric guitar plus tablature/symbolic labels and augmented tones. Single instrument only. |
| [E-GMD](https://magenta.tensorflow.org/datasets/e-gmd) | Drum hit and velocity tests with optional `make test-real-egmd-20` analyzer gate | 45,537 paired drum WAV/MIDI recordings, 444.5 hours, 43 drum kits, human velocity annotations, and about 2 ms audio/MIDI alignment. Drum-only. |
| [Vocal quartet F0 datasets](https://arxiv.org/abs/2009.04172) | Vocal row and multiple-F0 checks | Multi-track vocal quartets with F0 annotations. Vocal-only, not instrumental. |

## Real Stems With Weak Or No MIDI Truth

These can test file layout, source labels, broad timbre routing, and stem
presence, but they should not be treated as precise note/chord ground truth
without additional annotation.

| Dataset | Useful for | Missing for this project |
| --- | --- | --- |
| [MedleyDB / MedleyDB 2.0](https://medleydb.weebly.com/) | Real multitrack songs, melody F0, instrument activation | Full multitrack MIDI/note truth. Audio is on restricted [Zenodo](https://zenodo.org/records/1649325) records; annotations and metadata are public on [GitHub](https://github.com/marl/medleydb). |
| [MUSDB18 / MUSDB18-HQ](https://sigsep.github.io/datasets/musdb.html) | Drums, bass, vocals, other stem layout with optional `make inspect-real-musdb` preflight | MIDI/note truth and fine instrument classes. |
| [MoisesDB](https://arxiv.org/abs/2307.15913) | Fine-grained real stems beyond 4-stem separation | MIDI/note truth. |
| [RawStems](https://arxiv.org/abs/2505.21827) | Large unprocessed stem corpus and stem categories | MIDI/note truth. |
| [ACMID](https://arxiv.org/abs/2510.07840) | Seven-stem instrument source-separation labels | MIDI/note truth and manually verified note labels. |
| [The Spheres Dataset](https://arxiv.org/abs/2511.21247) | Real orchestral isolated stems, section stems, stereo/main mixes, room impulse responses, scales, and solo material | Full MIDI/note truth and 20+ same-song pieces. It has two full orchestral works, so it can help timbre/stem tests but cannot replace URMP. |

## Implementation Notes

- Run `make real-dataset-sources` to print the checked dataset source URLs and
  the exact local real-data commands. Use `make inspect-real-goal-20` as the
  combined setup preflight for the requested 20+ real same-song multitrack
  test. It requires the URMP layout preflight and then runs configured optional
  gates such as MusicNet, MedleyDB, MUSDB18, MulTTiPop, Spheres, GuitarSet,
  MAESTRO, and E-GMD. The URMP preflight applies the same
  `MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW` and
  `MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW` density thresholds as the
  analyzer gate, then reports matched-track, candidate active-track, and
  candidate pitch-class min/average/max values. Use `make test-real-goal-20` as
  the combined analyzer acceptance gate. It requires the URMP multitrack gate
  and then runs configured optional add-on gates such as MusicNet, MedleyDB,
  MUSDB18, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD.
  The official URMP full package is distributed through a registration form
  rather than a stable direct archive URL, so this repository intentionally does
  not try to download the 12.5 GB package automatically.
- Do not vendor dataset audio into this repository.
- Set `MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP`, run
  `make inspect-real-multitrack-20` to preflight the local layout, then run
  `make test-real-multitrack-20` to require the real-audio URMP regression
  harness against local `AuMix`, `AuSep`, `Notes`, and `Sco` MIDI files.
  The harness requires official URMP piece folder IDs, validates that MIDI score
  pitch classes agree with note annotations, checks each separated track, the
  provided `AuMix`, and a synthesized full mix made by summing every separated
  track. It also replays each selected provided and summed full-mix window
  through a short multi-frame analyzer sequence, and keeps one stateful provided
  mix analyzer plus one stateful summed mix analyzer per piece across selected
  windows, so note/chord smoothing is checked against same-song mixed audio. By
  default it samples up to 12 annotated windows per piece, requires at least 80
  windows, and only selects windows with at least two active source tracks and
  two pitch classes. The coverage summary prints source-track, active-track,
  and pitch-class min/average/max values, so the run proves that the selected
  windows are actually multi-instrument, multi-note mixes and that the summed
  path used the loaded separated source tracks. Set
  `MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE`,
  `MUSIC_ANALYZER_URMP_REQUIRED_PIECES`, and
  `MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS` for quicker or deeper runs. Set
  `MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW` and
  `MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW` to adjust the selected
  window density.
- Use `make inspect-real-multitrack-full` and
  `make test-real-multitrack-full` when the full URMP package is available.
  Those targets require all 44 official pieces and at least 176 annotated test
  windows.
- Use `make test-bach10-fixture` for a compact Bach10-style generated
  regression. It creates 10 four-part pieces with bassoon, alto saxophone,
  clarinet, and violin source WAV files plus note annotations, then reuses the
  URMP analyzer harness to check separated-source, provided-mix, summed-mix,
  streaming, stateful sequence, and chord recall. This does not replace URMP or
  the real Bach10 dataset, but it keeps that direct-fit instrumentation covered
  in normal `make test`.
- Use `make test-direct-fit-small-fixture` for the broader generated
  direct-fit-small suite. It unpacks the committed compact FLAC archive at
  `tests/fixtures/direct-fit-small.tar.gz`, decodes it under `build/`, and
  runs 20 URMP-compatible pieces shaped after the public Bach10, TRIOS,
  PHENICX-Anechoic, and MIREX Woodwind Quintet layouts through the same
  separated-source, provided-mix, summed-mix, streaming, stateful sequence, and
  chord recall checks. Refresh the archive with
  `make update-direct-fit-small-fixture` after changing
  `tests/generate_direct_fit_small_fixture.py`. This does not replace the real
  datasets; it keeps the combined 20-piece direct-fit-small instrumentation
  under regression coverage while access and licensing remain unresolved.
- Use `make inspect-real-medleydb` with
  `MUSIC_ANALYZER_MEDLEYDB_ROOT=/path/to/MedleyDB` and, if annotations are not
  inside that tree,
  `MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=/path/to/medleydb/medleydb/data/Annotations`
  to preflight the second real multitrack source. It requires at least 20 songs
  with mix plus stems and at least 20 melody-annotated multitracks by default.
  This is a partial real-stem/melody-F0 check and does not replace the URMP
  per-source note/chord gate.
- Use `make inspect-real-musdb` with
  `MUSIC_ANALYZER_MUSDB_ROOT=/path/to/MUSDB18-HQ` after extracting the
  uncompressed MUSDB18-HQ archive or decoding MUSDB18 STEMS files to WAV. The
  preflight requires 20+ same-song tracks with readable `mixture`, `drums`,
  `bass`, `other`, and `vocals` WAV stems by default and reports stem count,
  channels, sample-rate variants, and audio duration. MUSDB18 strengthens real
  full-song stem playback and broad timbre routing coverage, but it does not
  replace URMP because it lacks per-source MIDI/note/chord truth.
- Use `make inspect-real-multtipop` with
  `MUSIC_ANALYZER_MULTTIPOP_ROOT=/path/to/multtipop` after cloning or
  extracting the Hugging Face dataset. The preflight expects the official
  `dev/<id>/aligned.mid`, `dev/<id>/meta.json`, `test/<id>/aligned.mid`, and
  `test/<id>/meta.json` structure; verifies YouTube ID/start/end metadata;
  parses the MIDI files; and reports note-bearing MIDI-part, note-count, and
  pitch-class min/average/max values. Set
  `MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO=1` and optionally
  `MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT=/path/to/segments` to require locally
  obtained audio segments beside the metadata. Use
  `make test-real-multtipop-20` when those WAV segments are available as
  `audio.wav`, `segment.wav`, or `<id>.wav`; that target parses `aligned.mid`,
  selects windows with multiple active MIDI parts and pitch classes, and checks
  analyzer pitch-class and chord recall against the local real-pop mix segment.
  MulTTiPop strengthens real-pop note/chord coverage once local audio segments
  are available, but it does not replace URMP because the official release
  references commercial audio instead of shipping isolated stems.
- Use `make inspect-real-spheres` with
  `MUSIC_ANALYZER_SPHERES_ROOT=/path/to/TheSpheresDataset` to preflight The
  Spheres Dataset when it is available. This checks the real orchestral
  stem/mix folder layout only: each accepted piece needs readable mix/stereo
  audio, separate source-audio folders, multiple source files, and enough audio
  duration to make summed-stem playback meaningful. Spheres has two full works
  and no full MIDI/note truth for those works, so it is an optional
  timbre/stem-layout add-on and does not replace URMP for the 20+ note/chord
  gate.
- Use `make inspect-real-guitarset` with
  `MUSIC_ANALYZER_GUITARSET_ROOT=/path/to/GuitarSet` after extracting the
  GuitarSet annotation and audio archives from Zenodo. The preflight requires
  20+ JAMS files with 6+ `note_midi` annotations, 2+ chord annotations, 12+
  note events, and 6-channel hex pickup WAV audio by default. Use
  `make test-real-guitarset-20` to prepare a temporary JAMS-derived manifest,
  read selected real WAV windows, and check analyzer pitch-class plus chord
  recall. GuitarSet is a focused guitar/fretboard real-audio add-on; it should
  improve coverage for guitar note/fret/chord-shape behavior, but it does not
  replace URMP because it is a single-instrument dataset.
- Use `make test-real-maestro-20` with
  `MUSIC_ANALYZER_MAESTRO_ROOT=/path/to/maestro-v3.0.0` after extracting the
  official MAESTRO archive. The analyzer gate expects the official metadata CSV
  with `audio_filename` and `midi_filename`, reads the paired WAV/MIDI files,
  selects polyphonic piano/chord windows, and checks pitch-class plus chord
  recall. MAESTRO is a focused keyboard/piano real-audio add-on; it does not
  replace URMP because it is a single-instrument dataset, but it gives much
  stronger piano sustain and chord coverage than generated fixtures alone.
- Use `make test-real-egmd-20` with
  `MUSIC_ANALYZER_EGMD_ROOT=/path/to/e-gmd-v1.0.0` after extracting the official
  E-GMD archive. The analyzer gate expects the official metadata CSV with
  `audio_filename` and `midi_filename`, reads the paired WAV/MIDI files, parses
  MIDI drum hit and velocity events, selects drum-hit windows, and checks
  drum-category recall. E-GMD is a focused drum real-audio add-on; it does not
  replace URMP because it is drum-only, but it gives much stronger
  bass-drum/snare/hi-hat/tom/cymbal coverage than generated fixtures alone.
- Use `make inspect-real-musicnet` and `make test-real-musicnet-20` with
  `MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet` after extracting the open
  Zenodo MusicNet archive. The target expects `train_data`/`test_data` WAV
  folders and matching `train_labels`/`test_labels` CSV folders, selects windows
  with at least two active notes, two labeled instruments, and two pitch classes
  by default, then checks real-mix pitch-class and chord recall. This strengthens
  real audio note/chord coverage, but because MusicNet has no isolated stems it
  remains complementary to the URMP multitrack gate.
- Real-audio tests should skip with a clear message when the dataset is absent.
- URMP should be the first automated target because it gives enough pieces for
  20+ full-mix tests and has both isolated tracks and note truth.
- Current analyzer regressions already model all 44 URMP same-song
  instrumentations as generated per-track fixtures; they do not download or
  decode URMP audio yet.
- `make test` also runs `make test-real-goal-fixture`, which unpacks the
  committed compact 20-piece URMP-shaped lossless FLAC/Notes/MIDI fixture from
  `tests/fixtures/urmp-mini.tar.gz`, decodes it to disposable WAV files under
  `build/` with `ffmpeg`, generates 20-recording MusicNet-shaped WAV/CSV and
  MedleyDB-shaped stem-layout, MUSDB18-shaped five-stem,
  audio-backed MulTTiPop-shaped multitrack-MIDI
  metadata, Spheres-shaped stem-layout, GuitarSet-shaped JAMS/hex-audio,
  MAESTRO-shaped MIDI/WAV, and E-GMD-shaped MIDI/WAV fixtures, sends all
  configured roots through the
  combined setup preflight, and then sends them through the combined goal gate.
  The URMP fixture is marker-file tagged and is rejected by the real-data gate
  unless fixture mode is explicitly allowed. Override the decoder with
  `FFMPEG=/path/to/ffmpeg` if needed. Refresh it with
  `make update-urmp-fixture` after changing
  `tests/generate_urmp_fixture.py`.
- Bach10 is represented by `make test-bach10-fixture` as a compact, fast
  generated regression set, and Bach10/TRIOS/PHENICX-Anechoic/MIREX Woodwind
  Quintet are represented together by `make test-direct-fit-small-fixture`
  while real access/layout automation remains a future add-on.
- Single-instrument datasets should drive focused checks: GuitarSet now has a
  local preflight, MAESTRO now has a local analyzer gate, E-GMD now has a local
  drum analyzer gate, Guitar-TECHS/GAPS are next guitar add-ons, and PianoVAM is
  a keyboard add-on.
