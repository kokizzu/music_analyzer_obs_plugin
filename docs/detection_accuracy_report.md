# Real-audio detection accuracy

This dashboard is generated from the deterministic full-mix real-note attribute TSV. Each denominator is the number of unique audio samples; a sample is accurate when any analyzed buffer meets the stated condition.

Source: `build/real_note_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Any detected note | 2212 / 2212 (100.0%) | 0 |
| Expected instrument row | 2212 / 2212 (100.0%) | 0 |
| Lit expected pitch class | 2015 / 2212 (91.1%) | 197 |
| Primary display row | 772 / 2212 (34.9%) | 1440 |
| Visual primary row | 870 / 2212 (39.3%) | 1342 |
| Bass — Any detected note | 137 / 137 (100.0%) | 0 |
| Bass — Expected instrument row | 137 / 137 (100.0%) | 0 |
| Bass — Lit expected pitch class | 137 / 137 (100.0%) | 0 |
| Bass — Primary display row | 45 / 137 (32.8%) | 92 |
| Bass — Visual primary row | 50 / 137 (36.5%) | 87 |
| Guitar — Any detected note | 346 / 346 (100.0%) | 0 |
| Guitar — Expected instrument row | 346 / 346 (100.0%) | 0 |
| Guitar — Lit expected pitch class | 288 / 346 (83.2%) | 58 |
| Guitar — Primary display row | 152 / 346 (43.9%) | 194 |
| Guitar — Visual primary row | 60 / 346 (17.3%) | 286 |
| Other — Any detected note | 590 / 590 (100.0%) | 0 |
| Other — Expected instrument row | 590 / 590 (100.0%) | 0 |
| Other — Lit expected pitch class | 519 / 590 (88.0%) | 71 |
| Other — Primary display row | 117 / 590 (19.8%) | 473 |
| Other — Visual primary row | 209 / 590 (35.4%) | 381 |
| Piano — Any detected note | 1117 / 1117 (100.0%) | 0 |
| Piano — Expected instrument row | 1117 / 1117 (100.0%) | 0 |
| Piano — Lit expected pitch class | 1050 / 1117 (94.0%) | 67 |
| Piano — Primary display row | 452 / 1117 (40.5%) | 665 |
| Piano — Visual primary row | 545 / 1117 (48.8%) | 572 |
| Vocals — Any detected note | 22 / 22 (100.0%) | 0 |
| Vocals — Expected instrument row | 22 / 22 (100.0%) | 0 |
| Vocals — Lit expected pitch class | 21 / 22 (95.5%) | 1 |
| Vocals — Primary display row | 6 / 22 (27.3%) | 16 |
| Vocals — Visual primary row | 6 / 22 (27.3%) | 16 |

## Detector-improvement route coverage

This tracks the empirical candidate search. A route is actionable only when its measured gain has no protected-row regression; coverage-blocked routes need more independent positive fixture samples before any detector rule is considered.

Source: `build/detector_improvement_route_summary.txt`

| Metric | Routes / total | Other routes |
| --- | ---: | ---: |
| Routes with direct zero-regression support | 0 / 226 (0.0%) | 226 |
| Routes awaiting additional fixture coverage | 80 / 226 (35.4%) | 146 |

## Dagstuhl ChoirSet (DCS) coverage-gap checklist

DCS is an independent real vocal-ensemble corpus. Generated fixtures never count as DCS measurements; completion requires validated public audio plus score-aligned results.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store DCS archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | validated archive and checksum |
| Extract DCS safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extraction record |
| Inspect real DCS audio and annotations | 1 / 1 (100.0%) | 0 | corpus inventory by song/take/microphone |
| Import DCS sources and labels | 1 / 1 (100.0%) | 0 | tested prepared-multitrack manifest |
| Measure note and pitch-class recall | 1 / 1 (100.0%) | 0 | real DCS x/total results |
| Measure octave accuracy | 1 / 1 (100.0%) | 0 | real DCS exact-MIDI x/total results |
| Measure vocal ownership and display routing | 1 / 1 (100.0%) | 0 | real DCS row-routing x/total results |
| Measure chord accuracy | 1 / 1 (100.0%) | 0 | real DCS chord x/total results |
| Break down results by SATB range | 1 / 1 (100.0%) | 0 | S/A/T/B x/total rows |
| Break down results by recording configuration | 1 / 1 (100.0%) | 0 | setting/take/microphone x/total rows |
| Verify a safe cross-corpus detector improvement | 0 / 1 (0.0%) | 1 | DCS and protected-corpus regression evidence |

## Choral Singing Dataset (CSD) coverage-gap checklist

CSD is the next independent labelled SATB corpus. It contains isolated singers and synchronised MIDI; every step below must remain external to the repository through `build/InstrumentSamples`.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store current CSD archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | validated official archive and checksum |
| Extract CSD safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extraction record |
| Inspect CSD audio, stems, and MIDI | 1 / 1 (100.0%) | 0 | corpus inventory by work and section |
| Import CSD sources and labels | 0 / 1 (0.0%) | 1 | tested prepared-multitrack manifest |
| Measure CSD note, octave, and pitch-class recall | 0 / 1 (0.0%) | 1 | real CSD x/total results |
| Measure CSD vocal ownership and current-note routing | 0 / 1 (0.0%) | 1 | real CSD routing x/total results |
| Measure CSD chord accuracy | 0 / 1 (0.0%) | 1 | real CSD chord x/total results |
| Recheck any candidate across DCS, CSD, and cached vocal corpora | 0 / 1 (0.0%) | 1 | no protected-row regressions |

## Dagstuhl ChoirSet (DCS) real-audio measurement

The SATB rows count every score-active singer at a stable center-of-note window in a real, summed four-singer recording. Vocal ownership and routing require the expected pitch class in the vocal row; visible routing additionally requires visual level at least 0.25. Current-note vocal rows are separate window-level metrics: because the UI is monophonic, they count success when its one displayed note matches any concurrent SATB score pitch.

Source: `build/dagstuhl_choirset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS All DCS chord windows — Exact chord accuracy | 49 / 240 (20.4%) | 191 |
| DCS All DCS chord windows — Simplified chord accuracy | 82 / 240 (34.2%) | 158 |
| DCS All DCS vocal windows — Current-note vocal ownership | 86 / 240 (35.8%) | 154 |
| DCS All DCS vocal windows — Visible current-note vocal routing | 52 / 240 (21.7%) | 188 |
| DCS All SATB notes — Exact-MIDI recall | 568 / 984 (57.7%) | 416 |
| DCS All SATB notes — Pitch-class recall | 708 / 984 (72.0%) | 276 |
| DCS All SATB notes — Visible vocal routing | 58 / 984 (5.9%) | 926 |
| DCS All SATB notes — Vocal ownership | 109 / 984 (11.1%) | 875 |

### DCS SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS SATB range — Alto — Exact-MIDI recall | 162 / 240 (67.5%) | 78 |
| DCS SATB range — Alto — Pitch-class recall | 178 / 240 (74.2%) | 62 |
| DCS SATB range — Alto — Visible vocal routing | 20 / 240 (8.3%) | 220 |
| DCS SATB range — Alto — Vocal ownership | 36 / 240 (15.0%) | 204 |
| DCS SATB range — Bass — Exact-MIDI recall | 95 / 264 (36.0%) | 169 |
| DCS SATB range — Bass — Pitch-class recall | 185 / 264 (70.1%) | 79 |
| DCS SATB range — Bass — Visible vocal routing | 8 / 264 (3.0%) | 256 |
| DCS SATB range — Bass — Vocal ownership | 21 / 264 (8.0%) | 243 |
| DCS SATB range — Soprano — Exact-MIDI recall | 129 / 240 (53.8%) | 111 |
| DCS SATB range — Soprano — Pitch-class recall | 151 / 240 (62.9%) | 89 |
| DCS SATB range — Soprano — Visible vocal routing | 8 / 240 (3.3%) | 232 |
| DCS SATB range — Soprano — Vocal ownership | 18 / 240 (7.5%) | 222 |
| DCS SATB range — Tenor — Exact-MIDI recall | 182 / 240 (75.8%) | 58 |
| DCS SATB range — Tenor — Pitch-class recall | 194 / 240 (80.8%) | 46 |
| DCS SATB range — Tenor — Visible vocal routing | 22 / 240 (9.2%) | 218 |
| DCS SATB range — Tenor — Vocal ownership | 34 / 240 (14.2%) | 206 |

### DCS recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Current-note vocal ownership | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact-MIDI recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Vocal ownership | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Pitch-class recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible current-note vocal routing | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible vocal routing | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Current-note vocal ownership | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible vocal routing | 0 / 48 (0.0%) | 48 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Vocal ownership | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact-MIDI recall | 27 / 48 (56.2%) | 21 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact-MIDI recall | 15 / 48 (31.2%) | 33 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Pitch-class recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact-MIDI recall | 30 / 52 (57.7%) | 22 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Pitch-class recall | 43 / 52 (82.7%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible vocal routing | 4 / 52 (7.7%) | 48 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact-MIDI recall | 28 / 52 (53.8%) | 24 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Pitch-class recall | 39 / 52 (75.0%) | 13 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible vocal routing | 0 / 52 (0.0%) | 52 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Vocal ownership | 3 / 52 (5.8%) | 49 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact-MIDI recall | 20 / 52 (38.5%) | 32 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Pitch-class recall | 30 / 52 (57.7%) | 22 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Visible vocal routing | 2 / 52 (3.8%) | 50 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Vocal ownership | 8 / 52 (15.4%) | 44 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Current-note vocal ownership | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Exact-MIDI recall | 18 / 52 (34.6%) | 34 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Pitch-class recall | 26 / 52 (50.0%) | 26 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Visible vocal routing | 1 / 52 (1.9%) | 51 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Vocal ownership | 4 / 52 (7.7%) | 48 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact chord accuracy | 8 / 12 (66.7%) | 4 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact-MIDI recall | 38 / 52 (73.1%) | 14 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Pitch-class recall | 50 / 52 (96.2%) | 2 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Simplified chord accuracy | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible vocal routing | 6 / 52 (11.5%) | 46 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact-MIDI recall | 39 / 52 (75.0%) | 13 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Pitch-class recall | 46 / 52 (88.5%) | 6 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Visible current-note vocal routing | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Visible vocal routing | 11 / 52 (21.2%) | 41 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Vocal ownership | 16 / 52 (30.8%) | 36 |

## Vocadito full-mix vocal routing

This separate real-vocal corpus measures how often the vocal row remains visible when the analyzer also proposes instrumental rows.

Source: `build/vocadito_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Vocadito vocals — Any detected note | 354 / 354 (100.0%) | 0 |
| Vocadito vocals — Expected instrument row | 288 / 354 (81.4%) | 66 |
| Vocadito vocals — Lit expected pitch class | 166 / 354 (46.9%) | 188 |
| Vocadito vocals — Primary display row | 45 / 354 (12.7%) | 309 |
| Vocadito vocals — Visual primary row | 20 / 354 (5.6%) | 334 |

## VocalSet full-mix vocal routing

This larger, varied real-vocal corpus measures whether the detected note remains on the vocal row when the analyzer also proposes instrumental rows.

Source: `build/vocalset_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| VocalSet vocals — Any detected note | 2371 / 2389 (99.2%) | 18 |
| VocalSet vocals — Expected instrument row | 1301 / 2389 (54.5%) | 1088 |
| VocalSet vocals — Lit expected pitch class | 781 / 2389 (32.7%) | 1608 |
| VocalSet vocals — Primary display row | 199 / 2389 (8.3%) | 2190 |
| VocalSet vocals — Visual primary row | 173 / 2389 (7.2%) | 2216 |

### Focused clean-vowel regression

This cached VocalSet C5 fixture exercises the measured clean high-vowel profile
and is regenerated from its one-fixture attribute TSV.

Source: `build/vocalset_clean_vowel_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| VocalSet clean C5 vowel — Expected instrument row | 1 / 1 (100.0%) | 0 |

## Good Sounds full-mix acoustic routing

This independent acoustic-instrument corpus is measured in full-mix mode. It is a coverage benchmark, not a release threshold, and includes bass plus woodwind, brass, and violin samples.

Source: `build/good_sounds_full_mix_attributes.tsv`

The cached Good Sounds archive has been inventoried without extraction: all 1,318 usable labelled recordings are already in this fixture (661 violin, 453 tenor sax, 159 bass, and 45 other winds/brass). The remaining catalogue rows have no matching packed audio, so this corpus cannot supply independent additional examples for coverage-blocked route rules.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Good Sounds — Any detected note | 1317 / 1318 (99.9%) | 1 |
| Good Sounds — Expected instrument row | 1201 / 1318 (91.1%) | 117 |
| Good Sounds — Lit expected pitch class | 962 / 1318 (73.0%) | 356 |
| Good Sounds — Primary display row | 158 / 1318 (12.0%) | 1160 |
| Good Sounds — Visual primary row | 321 / 1318 (24.4%) | 997 |
| Good Sounds — Bass — Any detected note | 159 / 159 (100.0%) | 0 |
| Good Sounds — Bass — Expected instrument row | 142 / 159 (89.3%) | 17 |
| Good Sounds — Bass — Lit expected pitch class | 141 / 159 (88.7%) | 18 |
| Good Sounds — Bass — Primary display row | 3 / 159 (1.9%) | 156 |
| Good Sounds — Bass — Visual primary row | 6 / 159 (3.8%) | 153 |
| Good Sounds — Other — Any detected note | 1158 / 1159 (99.9%) | 1 |
| Good Sounds — Other — Expected instrument row | 1059 / 1159 (91.4%) | 100 |
| Good Sounds — Other — Lit expected pitch class | 821 / 1159 (70.8%) | 338 |
| Good Sounds — Other — Primary display row | 155 / 1159 (13.4%) | 1004 |
| Good Sounds — Other — Visual primary row | 315 / 1159 (27.2%) | 844 |

## Controlled octave-down violin fixture

Twenty real Philharmonia G3–B3 violin recordings are shifted down one octave. This explicitly derived fixture covers pitch-shifted/sample-playback violin below the acoustic violin range; it is kept separate from real-acoustic aggregate accuracy.

Source: `build/pitch_shifted_violin_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Pitch-shifted violin — Any detected note | 20 / 20 (100.0%) | 0 |
| Pitch-shifted violin — Expected instrument row | 20 / 20 (100.0%) | 0 |
| Pitch-shifted violin — Lit expected pitch class | 20 / 20 (100.0%) | 0 |
| Pitch-shifted violin — Primary display row | 20 / 20 (100.0%) | 0 |
| Pitch-shifted violin — Visual primary row | 20 / 20 (100.0%) | 0 |

## Philharmonia isolated exact-note coverage

This independent real acoustic corpus requires the annotated MIDI octave, not merely the pitch class, to appear in its expected instrument row.

Source: `build/philharmonia_full_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Philharmonia — Exact expected MIDI note | 7234 / 7285 (99.3%) | 51 |
| Philharmonia — Guitar — exact expected MIDI note | 144 / 146 (98.6%) | 2 |
| Philharmonia — Other — exact expected MIDI note | 6621 / 6668 (99.3%) | 47 |
| Philharmonia — Bass — exact expected MIDI note | 469 / 471 (99.6%) | 2 |

## Iowa orchestra isolated-note coverage

This independent real acoustic corpus includes brass, woodwind, strings, pitched percussion, and double bass. The strict rows require the annotated MIDI octave, while the routing rows distinguish octave errors from absent or misrouted notes.

Source: `build/iowa_orchestra_full_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Iowa orchestra — Any detected note | 681 / 682 (99.9%) | 1 |
| Iowa orchestra — Expected instrument row | 681 / 682 (99.9%) | 1 |
| Iowa orchestra — Lit expected pitch class | 681 / 682 (99.9%) | 1 |
| Iowa orchestra — Primary display row | 681 / 682 (99.9%) | 1 |
| Iowa orchestra — Visual primary row | 681 / 682 (99.9%) | 1 |
| Iowa orchestra — Bass — Any detected note | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Expected instrument row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Lit expected pitch class | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Primary display row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Visual primary row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Other — Any detected note | 656 / 657 (99.8%) | 1 |
| Iowa orchestra — Other — Expected instrument row | 656 / 657 (99.8%) | 1 |
| Iowa orchestra — Other — Lit expected pitch class | 656 / 657 (99.8%) | 1 |
| Iowa orchestra — Other — Primary display row | 656 / 657 (99.8%) | 1 |
| Iowa orchestra — Other — Visual primary row | 656 / 657 (99.8%) | 1 |
| Iowa orchestra — Exact expected MIDI note | 673 / 682 (98.7%) | 9 |
| Iowa orchestra — Other — exact expected MIDI note | 651 / 657 (99.1%) | 6 |
| Iowa orchestra — Bass — exact expected MIDI note | 22 / 25 (88.0%) | 3 |

## TinySOL isolated wind and brass exact-note coverage

This fresh symlink-only independent fixture checks whether the unresolved Philharmonia oboe and trombone octave aliases recur in a second library. Its exact-MIDI rows are measured in isolated-note mode before any recovery rule is considered.

Source: `build/tinysol_wind_exact_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| TinySOL — Oboe — exact expected MIDI note | 102 / 102 (100.0%) | 0 |
| TinySOL — Trombone — exact expected MIDI note | 116 / 117 (99.1%) | 1 |

## Iowa saxophone full-mix routing

This symlink-only 60-sample subset of the independent Iowa orchestra corpus covers alto and soprano saxophones in full-mix mode. It is a focused routing benchmark for woodwinds whose pitch is detected but can be assigned to another row.

Source: `build/iowa_sax_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Iowa saxophones — Any detected note | 60 / 60 (100.0%) | 0 |
| Iowa saxophones — Expected instrument row | 60 / 60 (100.0%) | 0 |
| Iowa saxophones — Lit expected pitch class | 38 / 60 (63.3%) | 22 |
| Iowa saxophones — Primary display row | 8 / 60 (13.3%) | 52 |
| Iowa saxophones — Visual primary row | 18 / 60 (30.0%) | 42 |

## TinySOL alto-saxophone full-mix routing

This independent 98-recording alto-saxophone subset is symlinked from TinySOL and measured in full-mix mode. Together with Iowa saxophones, it distinguishes a general saxophone routing failure from a single-library artifact.

Source: `build/tinysol_sax_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| TinySOL alto saxophone — Any detected note | 98 / 98 (100.0%) | 0 |
| TinySOL alto saxophone — Expected instrument row | 95 / 98 (96.9%) | 3 |
| TinySOL alto saxophone — Lit expected pitch class | 47 / 98 (48.0%) | 51 |
| TinySOL alto saxophone — Primary display row | 7 / 98 (7.1%) | 91 |
| TinySOL alto saxophone — Visual primary row | 11 / 98 (11.2%) | 87 |

## TinySOL flute full-mix routing

This independent 118-recording flute subset is symlinked from TinySOL and measured in full-mix mode. It expands woodwind ownership coverage before any flute recovery rule is allowed to change the detector.

Source: `build/tinysol_flute_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| TinySOL flute — Any detected note | 118 / 118 (100.0%) | 0 |
| TinySOL flute — Expected instrument row | 75 / 118 (63.6%) | 43 |
| TinySOL flute — Lit expected pitch class | 35 / 118 (29.7%) | 83 |
| TinySOL flute — Primary display row | 10 / 118 (8.5%) | 108 |
| TinySOL flute — Visual primary row | 15 / 118 (12.7%) | 103 |

## Real A2S tenor-saxophone score-aligned probes

These are 489 timed notes cut silently from twelve real tenor-saxophone major-scale recordings and three exercises, aligned to their bundled **kern scores. The source notation is shifted down one octave to its measured sounding pitch before scoring. This is an independent real-tenor diagnostic, not yet a broad generalization gate.

Source: `build/real_a2s_tenor_scale_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Real A2S tenor saxophone — Any detected note | 488 / 489 (99.8%) | 1 |
| Real A2S tenor saxophone — Expected instrument row | 423 / 489 (86.5%) | 66 |
| Real A2S tenor saxophone — Lit expected pitch class | 333 / 489 (68.1%) | 156 |
| Real A2S tenor saxophone — Primary display row | 100 / 489 (20.4%) | 389 |
| Real A2S tenor saxophone — Visual primary row | 163 / 489 (33.3%) | 326 |
| Real A2S tenor saxophone — Other — Any detected note | 488 / 489 (99.8%) | 1 |
| Real A2S tenor saxophone — Other — Expected instrument row | 423 / 489 (86.5%) | 66 |
| Real A2S tenor saxophone — Other — Lit expected pitch class | 333 / 489 (68.1%) | 156 |
| Real A2S tenor saxophone — Other — Primary display row | 100 / 489 (20.4%) | 389 |
| Real A2S tenor saxophone — Other — Visual primary row | 163 / 489 (33.3%) | 326 |
| Real A2S tenor saxophone — Exact expected MIDI note | 408 / 489 (83.4%) | 81 |
| Real A2S tenor saxophone — Other — exact expected MIDI note | 408 / 489 (83.4%) | 81 |

## URMP isolated saxophone exact-note coverage

This independent real multitrack fixture uses stable center-of-note clips cut silently from official URMP saxophone stems with timestamp, frequency, and duration annotations. It measures exact sounding MIDI octave separately from the score-aligned A2S probes.

Source: `build/urmp_sax_exact_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP saxophones — Exact expected MIDI note | 393 / 395 (99.5%) | 2 |
| URMP saxophones — Other — exact expected MIDI note | 393 / 395 (99.5%) | 2 |

## URMP saxophone full-mix-mode routing

The same independent, annotated URMP saxophone clips are analyzed in full-mix mode. This isolates row-routing behavior from the exact-octave isolated-note benchmark.

Source: `build/urmp_sax_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP saxophones — Any detected note | 393 / 395 (99.5%) | 2 |
| URMP saxophones — Expected instrument row | 277 / 395 (70.1%) | 118 |
| URMP saxophones — Lit expected pitch class | 162 / 395 (41.0%) | 233 |
| URMP saxophones — Primary display row | 33 / 395 (8.4%) | 362 |
| URMP saxophones — Visual primary row | 57 / 395 (14.4%) | 338 |
| URMP saxophones — Other — Any detected note | 393 / 395 (99.5%) | 2 |
| URMP saxophones — Other — Expected instrument row | 277 / 395 (70.1%) | 118 |
| URMP saxophones — Other — Lit expected pitch class | 162 / 395 (41.0%) | 233 |
| URMP saxophones — Other — Primary display row | 33 / 395 (8.4%) | 362 |
| URMP saxophones — Other — Visual primary row | 57 / 395 (14.4%) | 338 |
| URMP saxophones — Exact expected MIDI note | 237 / 395 (60.0%) | 158 |
| URMP saxophones — Other — exact expected MIDI note | 237 / 395 (60.0%) | 158 |

## Medley Solos instrument routing

This independent corpus contains 300 three-second isolated performances from each of eight instruments. It is measured in full-mix mode; a sample is accurate when any analyzed buffer activates its expected instrument row. It supplies routing coverage, not pitch or chord ground truth.

Source: `build/medley_solos_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Medley Solos — Expected instrument row | 2376 / 2400 (99.0%) | 24 |
| Medley Solos — Family Other expected row | 1483 / 1500 (98.9%) | 17 |
| Medley Solos — Instrument Clarinet expected row | 295 / 300 (98.3%) | 5 |
| Medley Solos — Family Guitar expected row | 300 / 300 (100.0%) | 0 |
| Medley Solos — Instrument Distorted Electric Guitar expected row | 300 / 300 (100.0%) | 0 |
| Medley Solos — Family Vocals expected row | 293 / 300 (97.7%) | 7 |
| Medley Solos — Instrument Female Singer expected row | 293 / 300 (97.7%) | 7 |
| Medley Solos — Instrument Flute expected row | 293 / 300 (97.7%) | 7 |
| Medley Solos — Family Piano expected row | 300 / 300 (100.0%) | 0 |
| Medley Solos — Instrument Piano expected row | 300 / 300 (100.0%) | 0 |
| Medley Solos — Instrument Tenor Saxophone expected row | 297 / 300 (99.0%) | 3 |
| Medley Solos — Instrument Trumpet expected row | 299 / 300 (99.7%) | 1 |
| Medley Solos — Instrument Violin expected row | 299 / 300 (99.7%) | 1 |

## Cached isolated-guitar chord gates

These rows count expected labeled chord-analysis windows (not full-mix samples). They are included only when the corresponding cached attribute TSV exists.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar Chord Mix — exact chord windows | 485 / 511 (94.9%) | 26 |
| Guitar Chord Mix — primary displayed chord windows | 400 / 511 (78.3%) | 111 |
| Guitar Chord Mix — expected guitar pitch classes | 1276 / 1533 (83.2%) | 257 |
| Guitar Techs Chord — exact chord windows | 7249 / 7484 (96.9%) | 235 |
| Guitar Techs Chord — primary displayed chord windows | 3577 / 7484 (47.8%) | 3907 |
| Guitar Techs Chord — expected guitar pitch classes | 24406 / 26738 (91.3%) | 2332 |
| Guitar Techs Music — exact chord windows | 412 / 500 (82.4%) | 88 |
| Guitar Techs Music — primary displayed chord windows | 242 / 500 (48.4%) | 258 |
| Guitar Techs Music — expected guitar pitch classes | 1609 / 1838 (87.5%) | 229 |
| Guitar Techs Music — power-chord exact windows | 6 / 26 (23.1%) | 20 |
| Gaps Guitar Full — exact chord windows | 361 / 540 (66.9%) | 179 |
| Gaps Guitar Full — primary displayed chord windows | 176 / 540 (32.6%) | 364 |
| Gaps Guitar Full — expected guitar pitch classes | 1519 / 1957 (77.6%) | 438 |
| Gaps Guitar Full — power-chord exact windows | 22 / 39 (56.4%) | 17 |
| Guitarset — exact chord windows | 1141 / 1491 (76.5%) | 350 |
| Guitarset — primary displayed chord windows | 622 / 1491 (41.7%) | 869 |
| Guitarset — expected guitar pitch classes | 4356 / 5340 (81.6%) | 984 |
| Guitarset — power-chord exact windows | 1 / 2 (50.0%) | 1 |

## URMP real multitrack gate

This downloaded real chamber-music corpus measures the same performances as provided mixes and as sums of their isolated tracks, with official note and MIDI annotations.
Instrument rows below show exact isolated-note recall for each measured instrument.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP — real pieces loadable | 44 / 44 (100.0%) | 0 |
| URMP — selected annotated windows | 528 / 528 (100.0%) | 0 |
| URMP — isolated-track exact notes | 1689 / 1788 (94.5%) | 99 |
| URMP — isolated-track detected notes | 1715 / 1788 (95.9%) | 73 |
| URMP — isolated-track precision | 1689 / 1783 (94.7%) | 94 false notes |
| URMP — provided-mix exact chords | 190 / 527 (36.1%) | 337 |
| URMP — provided stream chord windows | 224 / 527 (42.5%) | 303 |
| URMP — provided sequence chord windows | 214 / 527 (40.6%) | 313 |
| URMP — bassoon isolated exact notes | 35 / 36 (97.2%) | 1 |
| URMP — clarinet isolated exact notes | 120 / 120 (100.0%) | 0 |
| URMP — double bass isolated exact notes | 31 / 36 (86.1%) | 5 |
| URMP — flute isolated exact notes | 202 / 216 (93.5%) | 14 |
| URMP — horn isolated exact notes | 59 / 60 (98.3%) | 1 |
| URMP — oboe isolated exact notes | 69 / 72 (95.8%) | 3 |
| URMP — saxophone isolated exact notes | 129 / 132 (97.7%) | 3 |
| URMP — tuba isolated exact notes | 57 / 60 (95.0%) | 3 |
| URMP — trombone isolated exact notes | 83 / 96 (86.5%) | 13 |
| URMP — trumpet isolated exact notes | 253 / 264 (95.8%) | 11 |
| URMP — viola isolated exact notes | 145 / 156 (92.9%) | 11 |
| URMP — cello isolated exact notes | 121 / 132 (91.7%) | 11 |
| URMP — violin isolated exact notes | 385 / 408 (94.4%) | 23 |

## Bach10-mf0-synth multitrack stress gate

This F0-derived, resynthesized four-part corpus is reported separately from real-recording metrics. It measures expected active note slots and global chord windows.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Bach10-mf0-synth — expected note slots | 146 / 160 (91.2%) | 14 |
| Bach10-mf0-synth — exact chord windows | 28 / 40 (70.0%) | 12 |
| Bach10-mf0-synth — simplified chord windows | 34 / 40 (85.0%) | 6 |

## MusicNet real-mixture gate

This open CC-BY corpus measures real classical mixtures; unlike Bach10, it has no isolated stems. A recording is eligible for its chord rows only when annotations provide a window with at least two active instruments and two pitch classes.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MusicNet real mixes — recordings with eligible chord windows | 154 / 330 (46.7%) | 176 |
| MusicNet real mixes — expected pitch classes | 5690 / 7478 (76.1%) | 1788 |
| MusicNet real mixes — exact chord windows | 561 / 1847 (30.4%) | 1286 |
| MusicNet real mixes — simplified chord windows | 835 / 1847 (45.2%) | 1012 |

## MAPS real-piano gate

This real Disklavier corpus uses aligned MIDI annotations. The four stored shard summaries are combined here; rows remain visible even when the aggregate quality gate fails.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MAPS real piano — recordings with eligible chord windows | 78 / 80 (97.5%) | 2 |
| MAPS real piano — expected pitch classes | 419 / 604 (69.4%) | 185 |
| MAPS real piano — keyboard detected-note precision | 419 / 615 (68.1%) | 196 false predictions |
| MAPS real piano — exact chord windows | 17 / 135 (12.6%) | 118 |
| MAPS real piano — keyboard chord precision | 17 / 54 (31.5%) | 37 false predictions |

## MAPS chord-miss evidence

This isolates misses where note evidence is already present from misses that still lack a keyboard chord label.

| Metric | Affected / chord misses | Other misses |
| --- | ---: | ---: |
| Expected pitch classes are all present | 33 / 118 (28.0%) | 85 |
| No keyboard chord label | 85 / 118 (72.0%) | 33 |

## MAPS isolated-piano note gate

This separate Disklavier subset contains isolated notes with aligned MIDI annotations.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MAPS isolated piano — recordings with annotated note windows | 240 / 240 (100.0%) | 0 |
| MAPS isolated piano — expected pitch classes | 196 / 249 (78.7%) | 53 |
| MAPS isolated piano — keyboard detected-note precision | 196 / 725 (27.0%) | 529 false predictions |

## Full drum primary-classification gate

These rows count one-shot samples by the instrument shown as the primary drum. The latest completed full gate is reported even when a threshold fails, so its remaining classifications remain visible.

Source: `build/drum_full_exact_attribute_rows.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Full drum gate — primary kick | 6213 / 6505 (95.5%) | 292 |
| Full drum gate — primary snare | 4015 / 5390 (74.5%) | 1375 |
| Full drum gate — primary hihat | 1990 / 2358 (84.4%) | 368 |
| Full drum gate — primary crash | 569 / 788 (72.2%) | 219 |
| Full drum gate — primary tom | 1936 / 2861 (67.7%) | 925 |
| Full drum gate — primary ride | 241 / 352 (68.5%) | 111 |
| Full drum gate — primary rim | 332 / 504 (65.9%) | 172 |

## High-fidelity drum-kit primary-classification gate

These independent one-shot samples are sharded by expected instrument; the seven shard matrices are combined here so primary-label changes remain visible.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| High-fidelity drum kit — primary kick | 286 / 300 (95.3%) | 14 |
| High-fidelity drum kit — primary snare | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary hihat | 299 / 300 (99.7%) | 1 |
| High-fidelity drum kit — primary crash | 282 / 300 (94.0%) | 18 |
| High-fidelity drum kit — primary tom | 283 / 300 (94.3%) | 17 |
| High-fidelity drum kit — primary ride | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary rim | 283 / 300 (94.3%) | 17 |

## STAR Drums preview multitrack gate

This independent real-music preview measures annotated drum-event recall and false activations across mixed recordings.

Source: `build/star_drums_misses.log.summary`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| STAR Drums preview — annotated drum events detected | 39 / 56 (69.6%) | 17 |
| STAR Drums preview — detected-drum precision | 39 / 51 (76.5%) | 12 false predictions |
| STAR Drums preview — windows without a false drum | 6 / 16 (37.5%) | 10 false-positive windows |

## MDB Drums multitrack gate

This independent real-music fixture measures annotated drum-event recall and false activations across a larger variety of mixed recordings.

Source: `build/mdb_drums_misses.log.summary`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MDB Drums — annotated drum events detected | 192 / 192 (100.0%) | 0 |
| MDB Drums — detected-drum precision | 192 / 271 (70.8%) | 79 false predictions |
| MDB Drums — windows without a false drum | 41 / 92 (44.6%) | 51 false-positive windows |

Refresh with `make update-detection-accuracy-report`. Whenever a verified detection metric changes, update this report in the same commit.
