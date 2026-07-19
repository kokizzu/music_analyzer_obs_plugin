# Real Audio Dataset Candidates

Last checked: 2026-07-18.

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
| Ensemble Expressive Performance / EEP | 23 pieces | URMP survey describes string-quartet audio, note annotations, and bow motion-capture data. The generic `make test-real-prepared-multitrack-20` gate can evaluate it once local source audio and note CSVs are mapped into `manifest.json`. | Need to verify current public archive access, license, and exact annotation layout. Contact microphones may not sound like normal isolated stems. |

Recommendation: start with URMP. It satisfies the user's requested 20+ real
multi-instrument cases by itself and is the clearest source for verifying
mixtures, per-instrument notes, and source assignment. The other direct-fit
datasets found so far are useful add-ons. EEP reaches 20+ pieces in the
literature, but current archive access/layout still needs verification, so it
is supported through the generic prepared-multitrack manifest gate rather than a
hard-coded downloader. Combined, Bach10, TRIOS, WWQ, and PHENICX-Anechoic
account for 20 direct-fit-small pieces; normal `make test` now covers that
combined instrumentation with `make test-direct-fit-small-fixture` as a
generated regression while real-audio access/layout automation remains a future
add-on.

## Synthesized Multitrack Truth

These datasets have same-song stems and symbolic truth, but the audio is
rendered from MIDI rather than real recorded performances. They are useful for
large note/chord regression coverage and should stay separate from the strict
real-audio target.

| Dataset | Use | Notes |
| --- | --- | --- |
| [Slakh2100](https://arxiv.org/abs/1909.08494) | 20+ same-song stem/MIDI analyzer gate with optional `make inspect-real-slakh` and `make test-real-slakh-20` | 2100 rendered songs, 145 hours of mixtures, train/validation/test splits, stems, accompanying MIDI files, and piano/bass/guitar/drum classes in every mixture. Audio is synthesized from Lakh MIDI with virtual instruments, so it does not replace URMP. |
| [ChoralSynth](https://arxiv.org/abs/2311.08350) | 20-piece synthetic vocal multitrack analyzer gate with optional `make inspect-real-choralsynth` and `make test-real-choralsynth-20` | 20 choral pieces, each with MusicXML score, score MIDI, one audio track per voice, beat positions, and metadata. Audio is generated with singing synthesis, so it helps vocal/polyphonic note and chord coverage but does not replace URMP. |
| [CocoChorales](https://arxiv.org/abs/2209.14458) | Large synthetic chamber-ensemble stem/MIDI analyzer gate with optional `make inspect-real-cocochorales` and `make test-real-cocochorales-20` | 240,000 generated chamber-ensemble performances across string, brass, woodwind, and random ensembles, with mixtures, stems, MIDI, note-level performance attributes, F0 curves, loudness, and synthesis parameters. Audio is generated by the Chamber Ensemble Generator using MIDI-DDSP trained on URMP, so it is useful for stress coverage but does not replace real recorded URMP. |
| [SynthSOD](https://arxiv.org/abs/2409.10995) | 20+ synthetic orchestra/ensemble stem plus aligned-score analyzer gate with optional `make inspect-real-synthsod-remote`, `make inspect-real-synthsod`, and `make test-real-synthsod-20` | 47+ hours of synthesized orchestra/ensemble multitrack audio, selected from 596 SOD MIDI files, with close-mic source FLACs in `SynthSOD-data/<song>/Close Mic`. The separate [aligned-score release](https://doi.org/10.5281/zenodo.14971533) provides start/end time, MIDI pitch, and MIDI instrument text for about 85% of songs. It is useful for larger orchestral note/chord stress coverage but remains synthesized audio. |

## Real Vocal Multitrack F0 Truth

These datasets have real same-song source recordings and aligned F0 truth, but
they are vocal-only. They add useful note/chord stress coverage while remaining
separate from URMP's mixed-instrument gate.

| Dataset | Use | Notes |
| --- | --- | --- |
| [Vocal Ensemble F0 Aggregate](https://arxiv.org/abs/2009.04172) | 20+ real vocal quartet F0 analyzer gate with optional `make inspect-real-polyvocal` and `make test-real-polyvocal-20` | The ISMIR paper aggregates multi-track vocal datasets with F0 annotations. The 20+ subset comes from 22 Barbershop Quartet songs and 26 Bach Chorales; the companion code at [helenacuesta/multif0-estimation-vocals](https://github.com/helenacuesta/multif0-estimation-vocals) generates mixture WAV files plus `mtracks_info.json` from per-voice annotations. This repository also supports `source_audio_folder` plus `source_audio_files` entries and can sum those source voices before analysis. The PG Music source pages state the Barbershop Quartet product has separate tenor/lead/baritone/bass tracks and over 20 songs, and the Bach Chorales product has over 25 songs. The audio is commercial/local, so this repository supports a prepared local layout rather than downloading it. |

## Real Audio With MIDI Or Note Truth But No Isolated Stems

These are still useful, but they cannot verify source separation because they do
not provide clean per-instrument audio stems for each mixture.

| Dataset | Use | Notes |
| --- | --- | --- |
| [MusicNet](https://arxiv.org/abs/1611.09827) | Mixed classical note/instrument detection with optional `make inspect-real-musicnet-remote` and `make test-real-musicnet-20` real-mix gates | 34 hours, 330 recordings, 11 instruments, over 1M temporal note labels. No isolated stems. |
| [MulTTiPop](https://gclef-cmu.org/multtipop/) | Real pop mix note/instrument stress tests with optional `make inspect-real-multtipop` metadata/MIDI preflight and `make test-real-multtipop-20` local-audio analyzer gate | 572 commercial-pop segments with aligned multitrack MIDI metadata, published at [HuggingFace](https://huggingface.co/datasets/gclef-cmu/multtipop) and described in the [2026 paper](https://arxiv.org/abs/2607.08756). Audio is sourced via YouTube IDs/timestamps; recommended for evaluation, not training. |
| RWC-Pop | Real pop mix transcription | Cited by MulTTiPop as 100 original pop recordings with multitrack MIDI. Access/licensing needs verification. |
| [POP909](https://arxiv.org/abs/2008.07142) | Pop melody, lead, piano, chord checks | 909 popular-song arrangements with MIDI aligned to original audio plus tempo, beat, key, and chord annotations. Not per-instrument stems. |
| [MAESTRO](https://magenta.tensorflow.org/datasets/maestro) | Keyboard row, sustain, and chord tests with optional `make test-real-maestro-20` analyzer gate | 1,276 real Disklavier piano performances, 198.7 hours, paired WAV/MIDI with about 3 ms alignment, official metadata CSV/JSON, and over 7M note labels. Single instrument only. |
| [PianoVAM](https://arxiv.org/abs/2509.08800) | Keyboard row, fingering/hand plausibility | Piano audio, MIDI, video, hand landmarks, and fingering labels. Single instrument only. |
| [IDMT-SMT-Bass-Single-Track](https://zenodo.org/records/7544099) | Real electric bass-line note gate with `make test-idmt-bass-lines-samples` | 17 real electric-bass lines across styles with note onset, offset, MIDI pitch, string, fret, plucking-style, and expression-style annotations. The implemented target extracts stable expression-style `NO` note clips into `build/idmt_bass_lines_samples` and runs the shared isolated-bass real-note gate. Single instrument only. |
| [IDMT-SMT-Guitar](https://zenodo.org/records/7544110) | Real guitar technique note gate with `make test-idmt-guitar-samples` | Seven real guitars with 44.1 kHz mono WAV recordings, XML note annotations, plucking styles, and expression styles including normal, bending, slide, vibrato, harmonics, and dead notes. The implemented target extracts stable monophonic non-dead-note clips into `build/idmt_guitar_samples`, pitch-checks them against the chromatic model, and runs the shared isolated-guitar real-note gate. Single instrument only. |
| [IDMT-SMT-Drums](https://zenodo.org/records/7544164) | Real kick/snare/hi-hat gate with `make test-idmt-drums-samples` | 608 real drum WAV files with manually annotated SVL/XML onsets for kick drum, snare drum, and hi-hat training tracks. The implemented target extracts balanced annotated hit windows into `build/idmt_drums_samples` and runs the shared drum analyzer gate with only kick/snare/hi-hat marked required. Drum-only. |
| [GuitarSet](https://guitarset.weebly.com/) | Guitar fretboard tests with optional `make inspect-real-guitarset` preflight and `make test-real-guitarset-20` analyzer gate | 360 live guitar excerpts with hexaphonic pickup, per-string audio, microphone audio, JAMS MIDI-note/fret/chord annotations, and Zenodo download at [10.5281/zenodo.3371780](https://zenodo.org/records/3371780). Single instrument only. |
| [Guitar-TECHS](https://guitar-techs.github.io/) | Electric guitar single-note and chord gates with optional `make test-guitar-techs-samples` and `make test-guitar-techs-chord-samples` | 3,732 recordings across single notes, techniques, chords, scales, and excerpts; DI, amp-mic, egocentric, and exocentric perspectives; synchronized per-string MIDI labels; Zenodo download at [10.5281/zenodo.14963133](https://zenodo.org/records/14963133). The implemented targets prepare DI/amp-mic single-note excerpts for the shared real-note analyzer test and chord-window manifests for the isolated-guitar note/chord harness. |
| [Guitar Chord Mix](https://huggingface.co/datasets/ryangowe/guitar-chord-mix) | Real guitar chord gate with optional `make test-guitar-chord-mix-samples` | Hugging Face soundfolder of WAV guitar chord clips with JAMS `note_midi` annotations, assembled from GuitarSet, Guitar-TECHS, EGFxSet, Isolated Guitar Chords, SFZ, and DEMAND. The implemented target downloads all currently matched WAV/JAMS pairs by default and reuses the GuitarSet-shaped analyzer manifest path. Single instrument only. |
| [Vocadito](https://zenodo.org/records/5578807) | Real vocal note gate with `make test-vocadito-samples` | 40 short solo monophonic vocal recordings with trained-musician F0, note, lyric, and language annotations. The implemented target extracts stable near-chromatic vocal note clips from the A1 note annotations into `build/vocadito_samples` and runs the shared isolated real-note gate. Single instrument only. |
| [GAPS](https://huggingface.co/datasets/xavriley/GAPS) | Classical guitar note/fretboard tests with optional `make test-gaps-guitar-samples` | 300 solo guitar performances, about 14 hours, with audio, MIDI, MusicXML, sync points, metadata, and high-resolution note-level MIDI alignments. The implemented target prefilters the Hugging Face `match/` tree, downloads a bounded subset of available aligned performances, parses `.match` note timing into a GuitarSet-shaped manifest, and runs the isolated-guitar analyzer gate. Single instrument only and large. |
| [GOAT](https://arxiv.org/abs/2509.22655) | Electric guitar tablature/fret checks | 5.9 hours of DI electric guitar plus tablature/symbolic labels and augmented tones. Single instrument only. |
| [E-GMD](https://magenta.tensorflow.org/datasets/e-gmd) | Drum hit and velocity tests with optional `make test-real-egmd-20` analyzer gate | 45,537 paired drum WAV/MIDI recordings, 444.5 hours, 43 drum kits, human velocity annotations, and about 2 ms audio/MIDI alignment. Drum-only. |

## Real Stems With Weak Or No MIDI Truth

These can test file layout, source labels, broad timbre routing, and stem
presence, but they should not be treated as precise note/chord ground truth
without additional annotation.

| Dataset | Useful for | Missing for this project |
| --- | --- | --- |
| [MedleyDB / MedleyDB 2.0](https://medleydb.weebly.com/) | Real multitrack songs, melody F0, instrument activation, optional `make test-real-medleydb-20` melody analyzer gate | Full multitrack MIDI/note truth. Audio is on restricted [Zenodo](https://zenodo.org/records/1649325) records; annotations and metadata are public on [GitHub](https://github.com/marl/medleydb). |
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
  gates such as MusicNet, MedleyDB, MUSDB18, Slakh2100, ChoralSynth,
  CocoChorales, SynthSOD, Vocal Ensemble F0 Aggregate, prepared multitrack
  note-truth, MulTTiPop, Spheres, GuitarSet, MAESTRO, and E-GMD. The URMP preflight applies the same
  `MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW` and
  `MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW` density thresholds as the
  analyzer gate, then reports matched-track, candidate active-track, and
  candidate pitch-class min/average/max values. Use `make test-real-goal-20` as
  the combined analyzer acceptance gate. It requires the URMP multitrack gate
  and then runs configured optional add-on gates such as MusicNet, MedleyDB,
  MUSDB18, Slakh2100, ChoralSynth, CocoChorales, SynthSOD, Vocal Ensemble F0
  Aggregate, prepared multitrack note-truth, MulTTiPop, Spheres, GuitarSet,
  MAESTRO, and E-GMD.
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
  Use `make test-real-medleydb-20` to convert selected melody F0 annotations
  into a temporary MusicNet-shaped label set, sum the local source stems into
  playback audio, and check analyzer melody pitch-class recall. This is a
  partial real-stem/melody-F0 check and does not replace the URMP per-source
  note/chord gate.
- Use `make inspect-real-musdb` with
  `MUSIC_ANALYZER_MUSDB_ROOT=/path/to/MUSDB18-HQ` after extracting the
  uncompressed MUSDB18-HQ archive or decoding MUSDB18 STEMS files to WAV. The
  preflight requires 20+ same-song tracks with readable `mixture`, `drums`,
  `bass`, `other`, and `vocals` WAV stems by default and reports stem count,
  channels, sample-rate variants, and audio duration. MUSDB18 strengthens real
  full-song stem playback and broad timbre routing coverage, but it does not
  replace URMP because it lacks per-source MIDI/note/chord truth.
- Use `make inspect-real-slakh` with
  `MUSIC_ANALYZER_SLAKH_ROOT=/path/to/Slakh2100_flac_redux` after extracting
  Slakh2100. The preflight requires 20+ same-song rendered tracks with mix
  audio, 4+ stem audio files, readable MIDI, and metadata containing piano,
  bass, guitar, and drum classes by default. It reports stem count, readable
  MIDI count, channel/sample-rate coverage, and audio duration. Use
  `make test-real-slakh-20` to convert selected Slakh tracks into a temporary
  MusicNet-shaped WAV/CSV layout by summing the per-source stem audio, then run
  the existing analyzer pitch-class and chord recall gate on the played-together
  stem mix. Slakh2100 gives large
  coherent stem/MIDI truth coverage, but it does not replace URMP because its
  audio is MIDI-rendered rather than real recorded.
- Use `make inspect-real-choralsynth` with
  `MUSIC_ANALYZER_CHORALSYNTH_ROOT=/path/to/ChoralSynth` after extracting the
  ChoralSynth release. The preflight requires 20 pieces with `score.musicxml`,
  readable `score.midi`, and 4+ voice audio files by default. Use
  `make test-real-choralsynth-20` to mix the voice tracks into a temporary
  MusicNet-shaped WAV/CSV layout, parse the score MIDI as note truth, and run
  the existing analyzer pitch-class and chord recall gate. ChoralSynth adds
  synthetic vocal multitrack coverage, but it does not replace URMP because its
  audio is singing-synthesized rather than real recorded.
- Use `make inspect-real-cocochorales` with
  `MUSIC_ANALYZER_COCOCHORALES_ROOT=/path/to/CocoChorales` after extracting the
  CocoChorales release. The preflight looks for local examples with readable
  score MIDI, mix audio, and 4+ stem audio files by default. Use
  `make test-real-cocochorales-20` to sum the local stem audio into a temporary
  MusicNet-shaped WAV/CSV layout, parse the score MIDI as note truth, and run
  the existing analyzer pitch-class and chord recall gate. CocoChorales adds
  large chamber-ensemble stem/MIDI stress coverage, but it does not replace
  URMP because the audio is generated by the Chamber Ensemble Generator rather
  than real recorded.
- Use `make inspect-real-synthsod-remote` before downloading SynthSOD to verify
  the current Zenodo metadata. It checks the audio record, the full
  `SynthSOD.zip` archive, the smaller `SynthSOD-sample.zip` archive, the
  separate `SynthSOD_aligned_scores.zip` release, licenses, sizes, direct
  content URLs, and whether the aligned-score description still promises note
  start/end time, MIDI pitch, and MIDI instrument fields.
- After downloading the sample or full audio ZIP plus
  `SynthSOD_aligned_scores.zip`, use `make extract-real-synthsod-archives` with
  `MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP=/path/to/SynthSOD-sample.zip` and
  `MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP=/path/to/SynthSOD_aligned_scores.zip`.
  The extractor validates ZIP paths, rejects unsafe archive members, extracts
  into `build/synthsod-archives`, discovers the `SynthSOD-data` and aligned
  score roots, and prints the exact preflight/analyzer commands to run next.
- Use `make inspect-real-synthsod` with
  `MUSIC_ANALYZER_SYNTHSOD_ROOT=/path/to/SynthSOD-data` and
  `MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=/path/to/SynthSOD-aligned-scores` after
  extracting the SynthSOD audio archive and the separate aligned-score archive.
  The preflight uses the documented `SynthSOD-data/<song>/Close Mic` source
  FLAC layout, requires 20+ pieces with 4+ source tracks and aligned note text
  by default, and reports source-track, score-note, pitch-class, channel,
  sample-rate, and duration coverage. Use `make test-real-synthsod-20` to sum
  the close-mic source audio into a temporary MusicNet-shaped WAV/CSV layout,
  convert the aligned score text into note labels, and run the existing analyzer
  pitch-class and chord recall gate. SynthSOD adds large orchestral same-song
  stem/note stress coverage, but it does not replace URMP because its audio is
  synthesized from MIDI.
- Use `make inspect-real-polyvocal` with
  `MUSIC_ANALYZER_POLYVOCAL_ROOT=/path/to/prepared-vocal-f0` after preparing
  the vocal ensemble data with the companion workflow from
  `helenacuesta/multif0-estimation-vocals`. The preflight expects
  `mtracks_info.json`, mixture audio, and four or more per-voice F0 CSV/JAMS
  annotations per piece. When the metadata also provides `source_audio_folder`
  and `source_audio_files`, use `MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO=1`
  to require those per-voice audio tracks. Use `make test-real-polyvocal-20` to
  convert selected F0 contours into a temporary MusicNet-shaped WAV/CSV layout;
  it sums source voices when available before running the existing analyzer
  pitch-class and chord recall gate. This provides 20+ real vocal same-song
  multi-source F0 cases and chord opportunities, but it does not replace URMP
  because it is vocal-only and does not exercise mixed instrument
  timbre/source assignment.
- Use `make inspect-real-prepared-multitrack` with
  `MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT=/path/to/prepared-multitrack` for
  local real datasets whose public archive layout is not stable enough to
  hard-code, including EEP or a combined Bach10/TRIOS/PHENICX/WWQ preparation.
  The root must contain a `manifest.json` with a `pieces` list. Each piece has
  `sources`, and each source has `audio`, `notes`, and optional `instrument`.
  Note CSV files use `start`, `end`, `note`, and optional `instrument` columns.
  Use `make test-real-prepared-multitrack-20` to sum the source WAVs into a
  temporary MusicNet-shaped WAV/CSV layout and run the analyzer pitch-class and
  chord recall gate. Normal `make test` covers this path with
  `make test-prepared-multitrack-fixture`, a 20-piece generated regression that
  verifies four simultaneous source tracks per piece.
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
  `audio.wav`, `segment.wav`, or `<id>.wav` beside each segment, or under a
  separate `MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT`; that target parses
  `aligned.mid`, selects windows with multiple active MIDI parts and pitch
  classes, and checks analyzer pitch-class recall/precision/F1 and global chord
  recall/precision/F1 against the local real-pop mix segment. The default gates
  are `MUSIC_ANALYZER_MULTTIPOP_MIN_RECALL_PERCENT=40`,
  `MUSIC_ANALYZER_MULTTIPOP_MIN_PRECISION_PERCENT=35`,
  `MUSIC_ANALYZER_MULTTIPOP_MIN_CHORD_RECALL_PERCENT=20`, and
  `MUSIC_ANALYZER_MULTTIPOP_MIN_GLOBAL_CHORD_PRECISION_PERCENT=20`.
  `make test-multtipop-audio-root-fixture` is the generated regression for that
  separate-audio-root layout. MulTTiPop strengthens real-pop note/chord coverage
  once local audio segments are available, but it does not replace URMP because
  the official release references commercial audio instead of shipping isolated
  stems.
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
  read selected real WAV windows in explicit isolated-guitar mode, and check
  analyzer pitch-class recall, guitar-row precision/recall/F1, cross-row
  contamination, false-vocal windows, and isolated guitar-chord
  precision/recall. GuitarSet is a focused guitar/fretboard real-audio add-on;
  it should improve coverage for guitar note/fret/chord-shape behavior, but it
  does not replace URMP because it is a single-instrument dataset.
- Use `make test-guitar-techs-samples` to download the Guitar-TECHS P1/P2
  single-note ZIPs from Zenodo and prepare short DI plus amp-mic WAV excerpts
  from the aligned MIDI labels. The target runs those excerpts through the
  shared real-note analyzer in isolated-guitar mode and keeps all downloaded
  archives and generated clips under `build/`. On the current P1/P2 single-note
  archives it prepares 547 tested clips after 11 pitch-reference skips, and the
  analyzer gate detected 547/547 guitar notes. `make test-guitar-techs-chord-samples`
  uses the full P1/P2 chord ZIP sweep by default, writes GuitarSet-shaped
  `AUDIO`/`NOTE` manifests, and runs the isolated-guitar note/chord harness
  over 7000+ real chord clips. Scales, techniques, and music archives still
  need separate gates.
- Use `make test-guitar-chord-mix-samples` to download all currently matched
  public Hugging Face Guitar Chord Mix WAV/JAMS clips into
  `build/guitar_chord_mix_samples`, write a GuitarSet-shaped `AUDIO`/`NOTE`
  manifest, and run the isolated-guitar note/chord analyzer harness. The
  default `GUITAR_CHORD_MIX_LIMIT=0` uses all 500 matched pairs observed in the
  current public tree; set a positive limit only for a smaller local tuning
  loop. This adds real guitar chord audio to the regression set without pulling
  the much larger Guitar-TECHS chord archives into the default workflow.
- Use `make test-vocadito-samples` to download the 58.5 MB Vocadito ZIP from
  Zenodo, extract stable solo-vocal note clips from the trained-musician A1 note
  annotations, and run them through the shared isolated-vocal real-note gate.
  The current default prepares 370 near-chromatic clips across 27 note names and
  detects 368/370 with two tolerated misses. This fills the previous real vocal
  one-note coverage gap while staying separate from URMP because it is a
  single-instrument dataset.
- Use `make test-idmt-bass-lines-samples` to download the 20.5 MB
  IDMT-SMT-Bass-Single-Track ZIP from Zenodo, extract stable annotated
  expression-style `NO` electric-bass note clips from the 17 real bass lines,
  and run them through the shared isolated-bass real-note gate. The current
  default prepares 640 clips across 22 note names from E1-D3 and detects
  625/640 with 15 tolerated misses. This adds real bass-line timing, plucking,
  and transient coverage while keeping the remaining misses visible for future
  bass-detector tuning.
- Use `make test-idmt-guitar-samples` to download the 1.3 GB
  IDMT-SMT-Guitar ZIP from Zenodo, parse XML note events, keep stable
  monophonic non-dead-note clips, pitch-check them against strict chromatic
  tuning, and run them through the shared isolated-guitar real-note gate. This
  adds real guitar technique and pickup/instrument variation coverage beyond
  clean single-note and chord datasets.
- Use `make test-idmt-drums-samples` to download the 287.1 MB
  IDMT-SMT-Drums ZIP from Zenodo, parse the SVL frame annotations, and extract
  balanced real hit windows from the isolated `#KD#train.wav`, `#SD#train.wav`,
  and `#HH#train.wav` tracks. The current default prepares 900 clips, 300 each
  for kick, snare, and hi-hat, and runs the shared drum analyzer gate with only
  those three categories marked required. Current cached recall/primary/precision
  is kick 299/300, 298/300, and 299/349; snare 275/300, 224/300, and 275/494;
  and hi-hat 290/300, 152/300, and 290/327. Crash/tom/ride/rim false activations
  remain printed as diagnostics
  because IDMT-SMT-Drums does not label those classes in this target.
- Use `make test-real-maestro-20` with
  `MUSIC_ANALYZER_MAESTRO_ROOT=/path/to/maestro-v3.0.0` after extracting the
  official MAESTRO archive. The analyzer gate expects the official metadata CSV
  with `audio_filename` and `midi_filename`, reads the paired WAV/MIDI files,
  selects polyphonic piano/chord windows in explicit isolated-keyboard mode, and
  checks pitch-class recall, keyboard-row precision/recall/F1, cross-row
  contamination, false non-keyboard windows, and isolated keyboard-chord
  precision/recall. MAESTRO is a focused keyboard/piano real-audio add-on; it
  does not replace URMP because it is a single-instrument dataset, but it gives
  much stronger piano sustain and chord coverage than generated fixtures alone.
- Use `make test-real-egmd-20` with
  `MUSIC_ANALYZER_EGMD_ROOT=/path/to/e-gmd-v1.0.0` after extracting the official
  E-GMD archive. The analyzer gate expects the official metadata CSV with
  `audio_filename` and `midi_filename`, reads the paired WAV/MIDI files, parses
  MIDI drum hit and velocity events, selects drum-hit windows, and checks
  drum-category recall/precision/F1 plus false-positive drum windows. The
  default gates are `MUSIC_ANALYZER_EGMD_MIN_RECALL_PERCENT=35`,
  `MUSIC_ANALYZER_EGMD_MIN_PRECISION_PERCENT=50`, and
  `MUSIC_ANALYZER_EGMD_MAX_FALSE_POSITIVE_WINDOWS_PERCENT=75`. E-GMD is a
  focused drum real-audio add-on; it does not replace URMP because it is
  drum-only, but it gives much stronger bass-drum/snare/hi-hat/tom/cymbal
  coverage than generated fixtures alone.
- Use `make inspect-real-musicnet-remote` before downloading MusicNet to verify
  the current Zenodo metadata. It checks the open CC-BY-4.0 record, the
  `musicnet.tar.gz` WAV/CSV audio-label archive, `musicnet_metadata.csv`,
  `musicnet_midis.tar.gz`, direct content URLs, and description text promising
  note timing and instrument-label semantics.
- Use `make inspect-real-musicnet` and `make test-real-musicnet-20` with
  `MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet` after extracting the open
  Zenodo MusicNet archive. The target expects `train_data`/`test_data` WAV
  folders and matching `train_labels`/`test_labels` CSV folders, selects windows
  with at least two active notes, two labeled instruments, and two pitch classes
  by default, then checks real-mix pitch-class recall/precision/F1 and global
  chord recall/precision/F1. The default gates are
  `MUSIC_ANALYZER_MUSICNET_MIN_RECALL_PERCENT=40`,
  `MUSIC_ANALYZER_MUSICNET_MIN_PRECISION_PERCENT=35`,
  `MUSIC_ANALYZER_MUSICNET_MIN_CHORD_RECALL_PERCENT=20`, and
  `MUSIC_ANALYZER_MUSICNET_MIN_GLOBAL_CHORD_PRECISION_PERCENT=20`. This
  strengthens real audio note/chord coverage, but because MusicNet has no
  isolated stems it remains complementary to the URMP multitrack gate.
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
  MedleyDB-shaped summed-stem melody-F0, MUSDB18-shaped five-stem, Slakh2100-shaped
  rendered stem/MIDI, ChoralSynth-shaped vocal score/voice-track,
  CocoChorales-shaped chamber stem/MIDI, Vocal Ensemble F0-shaped per-voice F0,
  prepared source-audio/note manifests, audio-backed MulTTiPop-shaped
  multitrack-MIDI metadata, Spheres-shaped stem-layout, GuitarSet-shaped
  JAMS/hex-audio, MAESTRO-shaped MIDI/WAV, and E-GMD-shaped MIDI/WAV fixtures,
  sends all configured roots through the
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
  local preflight and downloaded mono-mic analyzer gate, Guitar-TECHS now has a
  downloaded real electric-guitar single-note gate, GAPS now has a 40+ excerpt
  real classical-guitar note/chord gate, MAESTRO now has a local analyzer gate,
  and E-GMD now has a local drum analyzer gate.
