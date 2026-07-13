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
| [Bach10](https://arxiv.org/abs/2505.17823) | 10 pieces | Four-part Bach chorales with isolated anechoic recordings for bassoon, alto saxophone, clarinet, and violin. The literature describes pitch/note transcriptions and audio-score alignment. | Small; useful as a regression add-on, not enough alone for 20+ cases. |
| TRIOS | 5 pieces | URMP survey describes 5 multitrack trio recordings with MIDI transcriptions. | Need to locate current download and license before automation. |
| MIREX Woodwind Quintet / WWQ | 1 piece | URMP survey describes individual recordings and note annotations for a classical quintet. | Only a 54-second excerpt is publicly available according to the URMP survey. |
| PHENICX-Anechoic / Aalto Anechoic Orchestra | 4 pieces | URMP survey describes 8-10 isolated orchestral parts per piece with denoised recordings and note annotations. | Need to verify current access, license, and annotation format. |

Recommendation: start with URMP. It satisfies the user's requested 20+ real
multi-instrument cases by itself and is the clearest source for verifying
mixtures, per-instrument notes, and source assignment. The other direct-fit
datasets found so far are useful add-ons, but they are too small to satisfy the
20-song gate without combining datasets.

## Real Audio With MIDI Or Note Truth But No Isolated Stems

These are still useful, but they cannot verify source separation because they do
not provide clean per-instrument audio stems for each mixture.

| Dataset | Use | Notes |
| --- | --- | --- |
| [MusicNet](https://arxiv.org/abs/1611.09827) | Mixed classical note/instrument detection with optional `make test-real-musicnet-20` real-mix gate | 34 hours, 330 recordings, 11 instruments, over 1M temporal note labels. No isolated stems. |
| [MulTTiPop](https://gclef-cmu.org/multtipop/) | Real pop mix note/instrument stress tests | 572 commercial-pop segments with aligned multitrack MIDI metadata, published at [HuggingFace](https://huggingface.co/datasets/gclef-cmu/multtipop). Audio is sourced via YouTube IDs/timestamps; recommended for evaluation, not training. |
| RWC-Pop | Real pop mix transcription | Cited by MulTTiPop as 100 original pop recordings with multitrack MIDI. Access/licensing needs verification. |
| [POP909](https://arxiv.org/abs/2008.07142) | Pop melody, lead, piano, chord checks | 909 popular-song arrangements with MIDI aligned to original audio plus tempo, beat, key, and chord annotations. Not per-instrument stems. |
| [MAESTRO](https://arxiv.org/abs/1810.12247) | Keyboard row and sustain tests | Real Disklavier piano audio with tightly aligned MIDI. Single instrument only. |
| [PianoVAM](https://arxiv.org/abs/2509.08800) | Keyboard row, fingering/hand plausibility | Piano audio, MIDI, video, hand landmarks, and fingering labels. Single instrument only. |
| [GuitarSet](https://guitarset.weebly.com/) | Guitar fretboard tests | Live guitar recordings with hexaphonic pickup, per-string audio, and MIDI-note annotations. Single instrument only. |
| [Guitar-TECHS](https://arxiv.org/abs/2501.03720) | Electric guitar notes, chords, scales, techniques | Over 5 hours, DI/mic/amp perspectives, synchronized six-track MIDI labels. Single instrument only. |
| [GAPS](https://arxiv.org/abs/2408.08653) | Classical guitar note/fretboard tests | 14 hours of real guitar audio with high-resolution note-level MIDI alignments. Single instrument only. |
| [GOAT](https://arxiv.org/abs/2509.22655) | Electric guitar tablature/fret checks | 5.9 hours of DI electric guitar plus tablature/symbolic labels and augmented tones. Single instrument only. |
| [E-GMD](https://arxiv.org/abs/2004.00188) | Drum hit and velocity tests | 444 hours of drum audio from 43 kits with paired MIDI and human velocity annotations. Drum-only. |
| [Vocal quartet F0 datasets](https://arxiv.org/abs/2009.04172) | Vocal row and multiple-F0 checks | Multi-track vocal quartets with F0 annotations. Vocal-only, not instrumental. |

## Real Stems With Weak Or No MIDI Truth

These can test file layout, source labels, broad timbre routing, and stem
presence, but they should not be treated as precise note/chord ground truth
without additional annotation.

| Dataset | Useful for | Missing for this project |
| --- | --- | --- |
| [MedleyDB / MedleyDB 2.0](https://medleydb.weebly.com/) | Real multitrack songs, melody F0, instrument activation | Full multitrack MIDI/note truth. Audio is on restricted [Zenodo](https://zenodo.org/records/1649325) records; annotations and metadata are public on [GitHub](https://github.com/marl/medleydb). |
| [MUSDB18 / MUSDB18-HQ](https://sigsep.github.io/datasets/musdb.html) | Drums, bass, vocals, other stem layout | MIDI/note truth and fine instrument classes. |
| [MoisesDB](https://arxiv.org/abs/2307.15913) | Fine-grained real stems beyond 4-stem separation | MIDI/note truth. |
| [RawStems](https://arxiv.org/abs/2505.21827) | Large unprocessed stem corpus and stem categories | MIDI/note truth. |
| [ACMID](https://arxiv.org/abs/2510.07840) | Seven-stem instrument source-separation labels | MIDI/note truth and manually verified note labels. |
| [Spheres](https://arxiv.org/abs/2511.21247) | Real orchestral isolated stems, sections, scales, solo material | Verified MIDI/note annotations. It can still help timbre/stem tests. |

## Implementation Notes

- Run `make real-dataset-sources` to print the checked dataset source URLs and
  the exact local real-data commands. Use `make inspect-real-goal-20` as the
  combined setup preflight for the requested 20+ real same-song multitrack
  test. It requires the URMP layout preflight and then runs configured optional
  preflights such as MusicNet and MedleyDB. Use `make test-real-goal-20` as the
  combined analyzer acceptance gate. It requires the URMP multitrack gate and
  then runs configured optional add-on gates such as MusicNet and MedleyDB. The
  official URMP full package is distributed through a registration form rather
  than a stable direct archive URL, so this repository intentionally does not
  try to download the 12.5 GB package automatically.
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
  two pitch classes. The coverage summary prints active-track and pitch-class
  min/average/max values, so the run proves that the selected windows are
  actually multi-instrument, multi-note mixes. Set
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
- Use `make inspect-real-medleydb` with
  `MUSIC_ANALYZER_MEDLEYDB_ROOT=/path/to/MedleyDB` and, if annotations are not
  inside that tree,
  `MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT=/path/to/medleydb/medleydb/data/Annotations`
  to preflight the second real multitrack source. It requires at least 20 songs
  with mix plus stems and at least 20 melody-annotated multitracks by default.
  This is a partial real-stem/melody-F0 check and does not replace the URMP
  per-source note/chord gate.
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
  MedleyDB-shaped stem-layout fixtures, and sends all configured roots through
  the combined goal gate. The URMP fixture is marker-file tagged and is rejected
  by the real-data gate unless fixture mode is explicitly allowed. Override the
  decoder with `FFMPEG=/path/to/ffmpeg` if needed. Refresh it with
  `make update-urmp-fixture` after changing
  `tests/generate_urmp_fixture.py`.
- Bach10 is the next best add-on for a compact, fast regression set.
- Single-instrument datasets should drive focused checks: Guitar-TECHS/GAPS for
  guitar, MAESTRO/PianoVAM for keyboard, E-GMD for drums.
