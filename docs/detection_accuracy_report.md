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

This tracks the empirical candidate search. A route is actionable only when its measured gain has no protected-row regression and positive evidence from two independently prepared corpora.

Source: `build/detector_improvement_route_summary.txt`

| Metric | Routes / total | Other routes |
| --- | ---: | ---: |
| Routes meeting protected and cross-corpus gates | 0 / 252 (0.0%) | 252 |
| Routes awaiting additional fixture coverage | 0 / 252 (0.0%) | 252 |
| Routes lacking independent-corpus replication | 123 / 252 (48.8%) | 129 |

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
| Import CSD sources and labels | 1 / 1 (100.0%) | 0 | tested prepared-multitrack manifest |
| Measure CSD note, octave, and pitch-class recall | 1 / 1 (100.0%) | 0 | real CSD x/total results |
| Measure CSD vocal ownership and current-note routing | 1 / 1 (100.0%) | 0 | real CSD routing x/total results |
| Measure CSD chord accuracy | 1 / 1 (100.0%) | 0 | real CSD chord x/total results |
| Recheck any candidate across DCS, CSD, and cached vocal corpora | 0 / 1 (0.0%) | 1 | latest scan rejects DCS/CSD-only key rules: no cached-corpus support without regressions |

## Choral Singing Dataset (CSD) real-audio measurement

Each CSD recording is a sum of four synchronised, individually recorded SATB stems. Per-part ownership is strict; current-note routing credits the monophonic vocal display when it matches any active SATB score pitch.

Source: `build/choral_singing_dataset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD All CSD chord windows — Exact chord accuracy | 43 / 144 (29.9%) | 101 |
| CSD All CSD chord windows — Simplified chord accuracy | 72 / 144 (50.0%) | 72 |
| CSD All CSD vocal windows — Current-note vocal ownership | 53 / 144 (36.8%) | 91 |
| CSD All CSD vocal windows — Visible current-note vocal routing | 30 / 144 (20.8%) | 114 |
| CSD All SATB notes — Exact-MIDI recall | 418 / 576 (72.6%) | 158 |
| CSD All SATB notes — Pitch-class recall | 463 / 576 (80.4%) | 113 |
| CSD All SATB notes — Visible vocal routing | 31 / 576 (5.4%) | 545 |
| CSD All SATB notes — Vocal ownership | 61 / 576 (10.6%) | 515 |

### CSD SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD SATB range — Alto — Exact-MIDI recall | 113 / 144 (78.5%) | 31 |
| CSD SATB range — Alto — Pitch-class recall | 120 / 144 (83.3%) | 24 |
| CSD SATB range — Alto — Visible vocal routing | 14 / 144 (9.7%) | 130 |
| CSD SATB range — Alto — Vocal ownership | 28 / 144 (19.4%) | 116 |
| CSD SATB range — Bass — Exact-MIDI recall | 97 / 144 (67.4%) | 47 |
| CSD SATB range — Bass — Pitch-class recall | 111 / 144 (77.1%) | 33 |
| CSD SATB range — Bass — Visible vocal routing | 4 / 144 (2.8%) | 140 |
| CSD SATB range — Bass — Vocal ownership | 7 / 144 (4.9%) | 137 |
| CSD SATB range — Soprano — Exact-MIDI recall | 104 / 144 (72.2%) | 40 |
| CSD SATB range — Soprano — Pitch-class recall | 115 / 144 (79.9%) | 29 |
| CSD SATB range — Soprano — Visible vocal routing | 8 / 144 (5.6%) | 136 |
| CSD SATB range — Soprano — Vocal ownership | 13 / 144 (9.0%) | 131 |
| CSD SATB range — Tenor — Exact-MIDI recall | 104 / 144 (72.2%) | 40 |
| CSD SATB range — Tenor — Pitch-class recall | 117 / 144 (81.2%) | 27 |
| CSD SATB range — Tenor — Visible vocal routing | 5 / 144 (3.5%) | 139 |
| CSD SATB range — Tenor — Vocal ownership | 13 / 144 (9.0%) | 131 |

### CSD recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD Configuration — CSD_ER_Singer1 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ER_Singer1 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_ER_Singer1 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ER_Singer1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer1 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ER_Singer2 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ER_Singer2 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer2 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer3 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| CSD Configuration — CSD_ER_Singer3 — Pitch-class recall | 41 / 48 (85.4%) | 7 |
| CSD Configuration — CSD_ER_Singer3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ER_Singer3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer3 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ER_Singer4 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_ER_Singer4 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_ER_Singer4 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer4 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer4 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer4 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| CSD Configuration — CSD_LI_Singer1 — Current-note vocal ownership | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_LI_Singer1 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer1 — Exact-MIDI recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_LI_Singer1 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_LI_Singer1 — Simplified chord accuracy | 9 / 12 (75.0%) | 3 |
| CSD Configuration — CSD_LI_Singer1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_LI_Singer1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_LI_Singer1 — Vocal ownership | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_LI_Singer2 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_LI_Singer2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_LI_Singer2 — Exact-MIDI recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_LI_Singer2 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_LI_Singer2 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_LI_Singer2 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_LI_Singer2 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_LI_Singer2 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| CSD Configuration — CSD_LI_Singer3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer3 — Exact-MIDI recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_LI_Singer3 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| CSD Configuration — CSD_LI_Singer3 — Simplified chord accuracy | 10 / 12 (83.3%) | 2 |
| CSD Configuration — CSD_LI_Singer3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_LI_Singer3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| CSD Configuration — CSD_LI_Singer3 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| CSD Configuration — CSD_LI_Singer4 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer4 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| CSD Configuration — CSD_LI_Singer4 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_LI_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_LI_Singer4 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ND_Singer1 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer1 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ND_Singer1 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| CSD Configuration — CSD_ND_Singer1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer1 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| CSD Configuration — CSD_ND_Singer2 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer2 — Exact-MIDI recall | 26 / 48 (54.2%) | 22 |
| CSD Configuration — CSD_ND_Singer2 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| CSD Configuration — CSD_ND_Singer2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ND_Singer2 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer3 — Current-note vocal ownership | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer3 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer3 — Exact-MIDI recall | 27 / 48 (56.2%) | 21 |
| CSD Configuration — CSD_ND_Singer3 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| CSD Configuration — CSD_ND_Singer3 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| CSD Configuration — CSD_ND_Singer3 — Vocal ownership | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ND_Singer4 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_ND_Singer4 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer4 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| CSD Configuration — CSD_ND_Singer4 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| CSD Configuration — CSD_ND_Singer4 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer4 — Vocal ownership | 8 / 48 (16.7%) | 40 |

## ESMUC Choir Dataset coverage-gap checklist

ESMUC adds independently labelled, synchronised SATB choir recordings with full takes, isolated sections, and short excerpts. The archive and extracted corpus remain in InstrumentSamples; only prepared measurement fixtures may be produced under `build/`.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store validated ESMUC archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | official archive checksum |
| Extract ESMUC safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extraction marker |
| Inventory ESMUC stems and corrected labels | 1 / 1 (100.0%) | 0 | 495 WAV, 276 note labels, 300 F0 files; FT/IS/SE configurations |
| Import ESMUC sources and labels | 1 / 1 (100.0%) | 0 | tested prepared-multitrack manifest (19 complete SATB recordings) |
| Measure ESMUC note, octave, and pitch-class recall | 1 / 1 (100.0%) | 0 | real ESMUC x/total results |
| Measure ESMUC vocal ownership and current-note routing | 1 / 1 (100.0%) | 0 | real ESMUC routing x/total results |
| Measure ESMUC chord accuracy | 1 / 1 (100.0%) | 0 | real ESMUC chord x/total results |
| Break down ESMUC results by SATB and configuration | 1 / 1 (100.0%) | 0 | S/A/T/B and FT/IS/SE x/total rows |
| Run DCS/CSD/ESMUC/MIR-1K/cached-vocal ownership audit | 1 / 1 (100.0%) | 0 | MIR-1K-inclusive zero-regression pattern report |
| Audit exact-MIDI vocal failures across all six corpora | 1 / 1 (100.0%) | 0 | exact-vocal, foreign-route, octave-alias, and absent evidence x/total |
| Verify a safe cross-corpus detector improvement | 0 / 1 (0.0%) | 1 | zero-protected keyboard candidates remain choir-only; MIR-1K/solo-vocal-supported candidates regress protected vocal rows, so every rule is rejected |

## ESMUC Choir Dataset real-audio measurement

Each recording is a real synchronised four-source SATB mix. Current-note routing is credited when the monophonic vocal display matches any concurrent SATB score pitch.

Source: `build/esmuc_choir_dataset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC All ESMUC chord windows — Exact chord accuracy | 68 / 218 (31.2%) | 150 |
| ESMUC All ESMUC chord windows — Simplified chord accuracy | 88 / 218 (40.4%) | 130 |
| ESMUC All ESMUC vocal windows — Current-note vocal ownership | 104 / 228 (45.6%) | 124 |
| ESMUC All ESMUC vocal windows — Visible current-note vocal routing | 53 / 228 (23.2%) | 175 |
| ESMUC All SATB notes — Exact-MIDI recall | 646 / 902 (71.6%) | 256 |
| ESMUC All SATB notes — Pitch-class recall | 722 / 902 (80.0%) | 180 |
| ESMUC All SATB notes — Visible vocal routing | 59 / 902 (6.5%) | 843 |
| ESMUC All SATB notes — Vocal ownership | 118 / 902 (13.1%) | 784 |

### ESMUC SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC SATB range — Alto — Exact-MIDI recall | 164 / 228 (71.9%) | 64 |
| ESMUC SATB range — Alto — Pitch-class recall | 180 / 228 (78.9%) | 48 |
| ESMUC SATB range — Alto — Visible vocal routing | 28 / 228 (12.3%) | 200 |
| ESMUC SATB range — Alto — Vocal ownership | 35 / 228 (15.4%) | 193 |
| ESMUC SATB range — Bass — Exact-MIDI recall | 182 / 228 (79.8%) | 46 |
| ESMUC SATB range — Bass — Pitch-class recall | 196 / 228 (86.0%) | 32 |
| ESMUC SATB range — Bass — Visible vocal routing | 15 / 228 (6.6%) | 213 |
| ESMUC SATB range — Bass — Vocal ownership | 37 / 228 (16.2%) | 191 |
| ESMUC SATB range — Soprano — Exact-MIDI recall | 136 / 218 (62.4%) | 82 |
| ESMUC SATB range — Soprano — Pitch-class recall | 161 / 218 (73.9%) | 57 |
| ESMUC SATB range — Soprano — Visible vocal routing | 7 / 218 (3.2%) | 211 |
| ESMUC SATB range — Soprano — Vocal ownership | 15 / 218 (6.9%) | 203 |
| ESMUC SATB range — Tenor — Exact-MIDI recall | 164 / 228 (71.9%) | 64 |
| ESMUC SATB range — Tenor — Pitch-class recall | 185 / 228 (81.1%) | 43 |
| ESMUC SATB range — Tenor — Visible vocal routing | 9 / 228 (3.9%) | 219 |
| ESMUC SATB range — Tenor — Vocal ownership | 31 / 228 (13.6%) | 197 |

### ESMUC recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact-MIDI recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact-MIDI recall | 33 / 48 (68.8%) | 15 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact-MIDI recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Simplified chord accuracy | 9 / 12 (75.0%) | 3 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible current-note vocal routing | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible vocal routing | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact chord accuracy | 5 / 10 (50.0%) | 5 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Simplified chord accuracy | 5 / 10 (50.0%) | 5 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Current-note vocal ownership | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible vocal routing | 0 / 48 (0.0%) | 48 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Vocal ownership | 0 / 48 (0.0%) | 48 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact-MIDI recall | 19 / 38 (50.0%) | 19 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Pitch-class recall | 23 / 38 (60.5%) | 15 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Simplified chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible vocal routing | 2 / 38 (5.3%) | 36 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Vocal ownership | 4 / 38 (10.5%) | 34 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Pitch-class recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Vocal ownership | 5 / 48 (10.4%) | 43 |

## MIR-1K vocal-with-accompaniment coverage-gap checklist

MIR-1K provides real karaoke vocal/accompaniment clips and manual frame-level vocal pitch annotations. It is the independent non-choir corpus needed to test whether proposed vocal routing improvements generalise beyond isolated singers and SATB mixtures.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store validated MIR-1K archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | published archive checksum |
| Extract MIR-1K safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extraction marker |
| Inventory audio, pitch, and vocal-activity annotations | 1 / 1 (100.0%) | 0 | 3,000 WAV, 1,000 pitch, 1,000 vocal, and 1,000 unvoiced labels |
| Import labelled vocal-plus-accompaniment clips | 1 / 1 (100.0%) | 0 | tested measurement manifest |
| Measure vocal pitch-class and exact-MIDI recall | 1 / 1 (100.0%) | 0 | real MIR-1K x/total results |
| Measure vocal ownership and visible current-note routing | 1 / 1 (100.0%) | 0 | real MIR-1K routing x/total results |
| Re-audit ownership rules across choir, solo-vocal, and MIR-1K corpora | 1 / 1 (100.0%) | 0 | zero-regression cross-corpus report |

## MIR-1K full-mix vocal routing

Each probe is cut from the supplied vocal-plus-accompaniment mix at the centre of its longest stable manually annotated 20 ms vocal-pitch run. The vocal stem is not used as measurement audio.

Source: `build/mir1k_vocal_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MIR-1K vocals — Any detected note | 300 / 300 (100.0%) | 0 |
| MIR-1K vocals — Expected instrument row | 224 / 300 (74.7%) | 76 |
| MIR-1K vocals — Lit expected pitch class | 123 / 300 (41.0%) | 177 |
| MIR-1K vocals — Primary display row | 46 / 300 (15.3%) | 254 |
| MIR-1K vocals — Visual primary row | 42 / 300 (14.0%) | 258 |
| MIR-1K vocals — Vocals — exact expected MIDI note | 173 / 300 (57.7%) | 127 |

## Saraga-Carnatic-Melody-Synth (SCMS) coverage-gap checklist

SCMS supplies real 30-second vocal-plus-accompaniment mixtures with time-aligned continuous vocal-melody annotations. Its archive stays in InstrumentSamples; the layout must be inspected before a traversal-safe extractor or labelled measurement importer is added.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store validated SCMS archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | official Zenodo MD5 |
| Inspect SCMS audio and CSV/LAB annotation inventory | 1 / 1 (100.0%) | 0 | non-extracting ZIP inventory |
| Extract SCMS safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extraction marker |
| Prepare labelled vocal-plus-accompaniment windows | 1 / 1 (100.0%) | 0 | tested measurement manifest |
| Measure current-note exact-MIDI and pitch-class recall | 1 / 1 (100.0%) | 0 | real SCMS x/total results |
| Measure vocal ownership and visible current-note routing | 1 / 1 (100.0%) | 0 | real SCMS routing x/total results |
| Re-audit protected routes with SCMS and existing vocal corpora | 1 / 1 (100.0%) | 0 | cross-corpus baseline report |

## SCMS full-mix vocal routing

Each probe is measured from its labelled vocal-plus-accompaniment mixture; annotations are used only as ground truth, never as analyzer input.

Source: `build/scms_vocal_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| SCMS vocals — Any detected note | 998 / 999 (99.9%) | 1 |
| SCMS vocals — Expected instrument row | 755 / 999 (75.6%) | 244 |
| SCMS vocals — Lit expected pitch class | 491 / 999 (49.1%) | 508 |
| SCMS vocals — Primary display row | 121 / 999 (12.1%) | 878 |
| SCMS vocals — Visual primary row | 90 / 999 (9.0%) | 909 |
| SCMS vocals — Vocals — exact expected MIDI note | 647 / 999 (64.8%) | 352 |

## Cross-corpus vocal exact-MIDI evidence

Exact vocal means the annotated MIDI pitch is present in the vocal row. Foreign-route means the exact pitch is present only in another row; pitch-class-only means the pitch class is detected in the wrong octave.

Source: `build/vocal_exact_note_cross_corpus.tsv`

| Corpus / outcome | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD — exact MIDI in vocal row | 50 / 576 (8.7%) | 526 |
| CSD — exact MIDI only in foreign row | 368 / 576 (63.9%) | 208 |
| CSD — pitch class only (wrong octave) | 45 / 576 (7.8%) | 531 |
| CSD — no expected pitch class | 113 / 576 (19.6%) | 463 |
| DCS — exact MIDI in vocal row | 73 / 984 (7.4%) | 911 |
| DCS — exact MIDI only in foreign row | 495 / 984 (50.3%) | 489 |
| DCS — pitch class only (wrong octave) | 140 / 984 (14.2%) | 844 |
| DCS — no expected pitch class | 276 / 984 (28.0%) | 708 |
| ESMUC — exact MIDI in vocal row | 76 / 902 (8.4%) | 826 |
| ESMUC — exact MIDI only in foreign row | 570 / 902 (63.2%) | 332 |
| ESMUC — pitch class only (wrong octave) | 76 / 902 (8.4%) | 826 |
| ESMUC — no expected pitch class | 180 / 902 (20.0%) | 722 |
| MIR1K — exact MIDI in vocal row | 501 / 2280 (22.0%) | 1779 |
| MIR1K — exact MIDI only in foreign row | 1408 / 2280 (61.8%) | 872 |
| MIR1K — pitch class only (wrong octave) | 233 / 2280 (10.2%) | 2047 |
| MIR1K — no expected pitch class | 138 / 2280 (6.1%) | 2142 |
| SCMS — exact MIDI in vocal row | 1712 / 7095 (24.1%) | 5383 |
| SCMS — exact MIDI only in foreign row | 4040 / 7095 (56.9%) | 3055 |
| SCMS — pitch class only (wrong octave) | 673 / 7095 (9.5%) | 6422 |
| SCMS — no expected pitch class | 670 / 7095 (9.4%) | 6425 |
| Vocadito — exact MIDI in vocal row | 545 / 2284 (23.9%) | 1739 |
| Vocadito — exact MIDI only in foreign row | 1274 / 2284 (55.8%) | 1010 |
| Vocadito — pitch class only (wrong octave) | 137 / 2284 (6.0%) | 2147 |
| Vocadito — no expected pitch class | 328 / 2284 (14.4%) | 1956 |
| VocalSet — exact MIDI in vocal row | 2660 / 17344 (15.3%) | 14684 |
| VocalSet — exact MIDI only in foreign row | 9396 / 17344 (54.2%) | 7948 |
| VocalSet — pitch class only (wrong octave) | 1130 / 17344 (6.5%) | 16214 |
| VocalSet — no expected pitch class | 4158 / 17344 (24.0%) | 13186 |

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

## Iowa piano full-mix routing

This independently labelled real-piano library is measured in the same full-mix routing mode as the detector audit. It supplies independent evidence before a piano-to-guitar routing rule can be accepted.

Source: `build/iowa_piano_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Iowa piano — Any detected note | 85 / 85 (100.0%) | 0 |
| Iowa piano — Expected instrument row | 80 / 85 (94.1%) | 5 |
| Iowa piano — Lit expected pitch class | 73 / 85 (85.9%) | 12 |
| Iowa piano — Primary display row | 20 / 85 (23.5%) | 65 |
| Iowa piano — Visual primary row | 25 / 85 (29.4%) | 60 |

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
| MAPS real piano — recordings with eligible chord windows | 2924 / 3000 (97.5%) | 76 |
| MAPS real piano — expected pitch classes | 8052 / 11662 (69.0%) | 3610 |
| MAPS real piano — keyboard detected-note precision | 8052 / 11975 (67.2%) | 3923 false predictions |
| MAPS real piano — exact chord windows | 144 / 2231 (6.5%) | 2087 |
| MAPS real piano — keyboard chord precision | 144 / 884 (16.3%) | 740 false predictions |

## Independent piano cross-corpus coverage checklist

MAESTRO is independent external paired WAV/MIDI evidence. It remains separate from MAPS until a protected cross-piano rule is verified.

| Task | Complete / total | Remaining |
| --- | ---: | ---: |
| Prepare external MAESTRO paired-audio subset | 1 / 1 (100.0%) | 0 |
| Measure MAESTRO note and chord outcomes | 1 / 1 (100.0%) | 0 |
| Mine a protected cross-piano detector rule | 0 / 1 (0.0%) | 1 |

### MAESTRO external-piano measurement

Source: `build/maestro_real_measurement.out`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MAESTRO external piano — recordings with eligible chord windows | 320 / 320 (100.0%) | 0 |
| MAESTRO external piano — expected pitch classes | 4450 / 5726 (77.7%) | 1276 |
| MAESTRO external piano — keyboard detected-note precision | 4450 / 6664 (66.8%) | 2214 false predictions |
| MAESTRO external piano — exact chord windows | 137 / 1280 (10.7%) | 1143 |
| MAESTRO external piano — keyboard chord precision | 137 / 651 (21.0%) | 514 false predictions |

### Independent-piano runtime-state mining

Source: `build/independent_piano_chord_states.txt`

| Metric | Candidate states / shared states | Remaining |
| --- | ---: | ---: |
| No-label states with complete pitch-class recovery in every corpus | 0 / 15 (0.0%) | 15 |

## KRAISLER independent piano–violin coverage checklist

KRAISLER is an independent real piano–violin duet corpus with separately recorded stems, summed mixtures, Disklavier piano MIDI, and reviewed violin note labels.

| Task | Complete / total | Remaining |
| --- | ---: | ---: |
| Validate external KRAISLER archive | 1 / 1 (100.0%) | 0 |
| Extract KRAISLER safely in InstrumentSamples | 1 / 1 (100.0%) | 0 |
| Import dry piano/violin stems and labels | 1 / 1 (100.0%) | 0 |
| Measure real KRAISLER note and chord outcomes | 0 / 1 (0.0%) | 1 |
| Mine a protected KRAISLER cross-corpus detector rule | 0 / 1 (0.0%) | 1 |

## MAPS chord-miss evidence

This isolates misses where note evidence is already present from misses that still lack a keyboard chord label.

| Metric | Affected / chord misses | Other misses |
| --- | ---: | ---: |
| Expected pitch classes are all present | 33 / 118 (28.0%) | 85 |
| No keyboard chord label | 85 / 118 (72.0%) | 33 |

## Independent piano chord-outcome evidence

These compatible MAPS and MAESTRO labels establish shared failure outcomes, not a detector rule by themselves.

| Corpus | Exact chord hit | Missing chord label | Wrong chord label |
| --- | ---: | ---: | ---: |
| MAPS | 17 / 135 (12.6%) | 85 / 135 (63.0%) | 33 / 135 (24.4%) |
| MAESTRO | 137 / 1280 (10.7%) | 629 / 1280 (49.1%) | 514 / 1280 (40.2%) |

## MAPS isolated-piano note gate

This separate Disklavier subset contains isolated notes with aligned MIDI annotations.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MAPS isolated piano — recordings with annotated note windows | 735 / 735 (100.0%) | 0 |
| MAPS isolated piano — expected pitch classes | 725 / 942 (77.0%) | 217 |
| MAPS isolated piano — keyboard detected-note precision | 725 / 2603 (27.9%) | 1878 false predictions |

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
