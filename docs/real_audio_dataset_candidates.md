# Real Audio Dataset Candidates

Last checked: 2026-07-13.

This project needs real recorded audio for stronger tests. The strict target is:

- real, non-MIDI-rendered audio;
- per-instrument or per-source audio tracks, not only a finished mix;
- aligned MIDI, note, pitch, or F0 truth so analyzer output can be verified.

Very few public datasets have all three. The practical path is to automate the
direct-fit datasets first, then use single-instrument and partial-label datasets
for focused row-level tests.

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
mixtures, per-instrument notes, and source assignment.

## Real Audio With MIDI Or Note Truth But No Isolated Stems

These are still useful, but they cannot verify source separation because they do
not provide clean per-instrument audio stems for each mixture.

| Dataset | Use | Notes |
| --- | --- | --- |
| [MusicNet](https://arxiv.org/abs/1611.09827) | Mixed classical note/instrument detection | 34 hours, 330 recordings, 11 instruments, over 1M temporal note labels. No isolated stems. |
| [MulTTiPop](https://arxiv.org/abs/2607.08756) | Real pop mix note/instrument stress tests | 572 commercial-pop segments with aligned multitrack MIDI metadata. Audio is sourced via YouTube IDs/timestamps; recommended for evaluation, not training. |
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
| [MedleyDB / MedleyDB 2.0](https://medleydb.weebly.com/) | Real multitrack songs, melody F0, instrument activation | Full multitrack MIDI/note truth. |
| [MUSDB18 / MUSDB18-HQ](https://sigsep.github.io/datasets/musdb.html) | Drums, bass, vocals, other stem layout | MIDI/note truth and fine instrument classes. |
| [MoisesDB](https://arxiv.org/abs/2307.15913) | Fine-grained real stems beyond 4-stem separation | MIDI/note truth. |
| [RawStems](https://arxiv.org/abs/2505.21827) | Large unprocessed stem corpus and stem categories | MIDI/note truth. |
| [ACMID](https://arxiv.org/abs/2510.07840) | Seven-stem instrument source-separation labels | MIDI/note truth and manually verified note labels. |
| [Spheres](https://arxiv.org/abs/2511.21247) | Real orchestral isolated stems, sections, scales, solo material | Verified MIDI/note annotations. It can still help timbre/stem tests. |

## Implementation Notes

- Do not vendor dataset audio into this repository.
- Set `MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP` to run the optional real-audio
  URMP regression harness against local `AuMix`, `AuSep`, and `Notes` files.
  The harness checks each separated track, the provided `AuMix`, and a
  synthesized full mix made by summing every separated track.
- Real-audio tests should skip with a clear message when the dataset is absent.
- URMP should be the first automated target because it gives enough pieces for
  20+ full-mix tests and has both isolated tracks and note truth.
- Current analyzer regressions already model all 44 URMP same-song
  instrumentations as generated per-track fixtures; they do not download or
  decode URMP audio yet.
- `make test` also unpacks the committed compact 20-piece URMP-shaped WAV/Notes
  fixture from `tests/fixtures/urmp-mini.tar.gz` to exercise the optional
  real-audio parser and full-mix path across multiple annotated windows without
  requiring the full dataset. Refresh it with `make update-urmp-fixture` after
  changing `tests/generate_urmp_fixture.py`.
- Bach10 is the next best add-on for a compact, fast regression set.
- Single-instrument datasets should drive focused checks: Guitar-TECHS/GAPS for
  guitar, MAESTRO/PianoVAM for keyboard, E-GMD for drums.
