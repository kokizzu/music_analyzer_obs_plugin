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
| Good Sounds — Lit expected pitch class | 960 / 1318 (72.8%) | 358 |
| Good Sounds — Primary display row | 157 / 1318 (11.9%) | 1161 |
| Good Sounds — Visual primary row | 320 / 1318 (24.3%) | 998 |
| Good Sounds — Bass — Any detected note | 159 / 159 (100.0%) | 0 |
| Good Sounds — Bass — Expected instrument row | 142 / 159 (89.3%) | 17 |
| Good Sounds — Bass — Lit expected pitch class | 141 / 159 (88.7%) | 18 |
| Good Sounds — Bass — Primary display row | 3 / 159 (1.9%) | 156 |
| Good Sounds — Bass — Visual primary row | 6 / 159 (3.8%) | 153 |
| Good Sounds — Other — Any detected note | 1158 / 1159 (99.9%) | 1 |
| Good Sounds — Other — Expected instrument row | 1059 / 1159 (91.4%) | 100 |
| Good Sounds — Other — Lit expected pitch class | 819 / 1159 (70.7%) | 340 |
| Good Sounds — Other — Primary display row | 154 / 1159 (13.3%) | 1005 |
| Good Sounds — Other — Visual primary row | 314 / 1159 (27.1%) | 845 |

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
| TinySOL alto saxophone — Lit expected pitch class | 46 / 98 (46.9%) | 52 |
| TinySOL alto saxophone — Primary display row | 7 / 98 (7.1%) | 91 |
| TinySOL alto saxophone — Visual primary row | 11 / 98 (11.2%) | 87 |

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
