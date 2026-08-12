# Real-audio detection accuracy

This dashboard is generated from the deterministic full-mix real-note attribute TSV. Each denominator is the number of unique audio samples; a sample is accurate when any analyzed buffer meets the stated condition.

Source: `build/real_note_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Any detected note | 2212 / 2212 (100.0%) | 0 |
| Expected instrument row | 2212 / 2212 (100.0%) | 0 |
| Lit expected pitch class | 2015 / 2212 (91.1%) | 197 |
| Primary display row | 774 / 2212 (35.0%) | 1438 |
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
| Other — Primary display row | 119 / 590 (20.2%) | 471 |
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
| Routes with direct zero-regression support | 7 / 236 (3.0%) | 229 |
| Routes awaiting additional fixture coverage | 92 / 236 (39.0%) | 144 |

## Vocadito full-mix vocal routing

This separate real-vocal corpus measures how often the vocal row remains visible when the analyzer also proposes instrumental rows.

Source: `build/vocadito_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Vocadito vocals — Any detected note | 354 / 354 (100.0%) | 0 |
| Vocadito vocals — Expected instrument row | 284 / 354 (80.2%) | 70 |
| Vocadito vocals — Lit expected pitch class | 153 / 354 (43.2%) | 201 |
| Vocadito vocals — Primary display row | 39 / 354 (11.0%) | 315 |
| Vocadito vocals — Visual primary row | 20 / 354 (5.6%) | 334 |

## VocalSet full-mix vocal routing

This larger, varied real-vocal corpus measures whether the detected note remains on the vocal row when the analyzer also proposes instrumental rows.

Source: `build/vocalset_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| VocalSet vocals — Any detected note | 2371 / 2389 (99.2%) | 18 |
| VocalSet vocals — Expected instrument row | 1295 / 2389 (54.2%) | 1094 |
| VocalSet vocals — Lit expected pitch class | 777 / 2389 (32.5%) | 1612 |
| VocalSet vocals — Primary display row | 199 / 2389 (8.3%) | 2190 |
| VocalSet vocals — Visual primary row | 176 / 2389 (7.4%) | 2213 |

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

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Good Sounds — Any detected note | 1317 / 1318 (99.9%) | 1 |
| Good Sounds — Expected instrument row | 1201 / 1318 (91.1%) | 117 |
| Good Sounds — Lit expected pitch class | 957 / 1318 (72.6%) | 361 |
| Good Sounds — Primary display row | 157 / 1318 (11.9%) | 1161 |
| Good Sounds — Visual primary row | 317 / 1318 (24.1%) | 1001 |
| Good Sounds — Bass — Any detected note | 159 / 159 (100.0%) | 0 |
| Good Sounds — Bass — Expected instrument row | 142 / 159 (89.3%) | 17 |
| Good Sounds — Bass — Lit expected pitch class | 141 / 159 (88.7%) | 18 |
| Good Sounds — Bass — Primary display row | 3 / 159 (1.9%) | 156 |
| Good Sounds — Bass — Visual primary row | 6 / 159 (3.8%) | 153 |
| Good Sounds — Other — Any detected note | 1158 / 1159 (99.9%) | 1 |
| Good Sounds — Other — Expected instrument row | 1059 / 1159 (91.4%) | 100 |
| Good Sounds — Other — Lit expected pitch class | 816 / 1159 (70.4%) | 343 |
| Good Sounds — Other — Primary display row | 154 / 1159 (13.3%) | 1005 |
| Good Sounds — Other — Visual primary row | 311 / 1159 (26.8%) | 848 |

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
| Philharmonia — Exact expected MIDI note | 7231 / 7285 (99.3%) | 54 |
| Philharmonia — Guitar — exact expected MIDI note | 144 / 146 (98.6%) | 2 |
| Philharmonia — Other — exact expected MIDI note | 6618 / 6668 (99.3%) | 50 |
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
| Iowa orchestra — Exact expected MIDI note | 663 / 682 (97.2%) | 19 |
| Iowa orchestra — Other — exact expected MIDI note | 645 / 657 (98.2%) | 12 |
| Iowa orchestra — Bass — exact expected MIDI note | 18 / 25 (72.0%) | 7 |

## Medley Solos instrument routing

This independent corpus contains three-second isolated performances from eight instruments. It is measured in full-mix mode; a sample is accurate when any analyzed buffer activates its expected instrument row. It supplies routing coverage, not pitch or chord ground truth.

Source: `build/medley_solos_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Medley Solos — Expected instrument row | 953 / 960 (99.3%) | 7 |
| Medley Solos — Family Other expected row | 598 / 600 (99.7%) | 2 |
| Medley Solos — Instrument Clarinet expected row | 119 / 120 (99.2%) | 1 |
| Medley Solos — Family Guitar expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Instrument Distorted Electric Guitar expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Family Vocals expected row | 115 / 120 (95.8%) | 5 |
| Medley Solos — Instrument Female Singer expected row | 115 / 120 (95.8%) | 5 |
| Medley Solos — Instrument Flute expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Family Piano expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Instrument Piano expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Instrument Tenor Saxophone expected row | 120 / 120 (100.0%) | 0 |
| Medley Solos — Instrument Trumpet expected row | 119 / 120 (99.2%) | 1 |
| Medley Solos — Instrument Violin expected row | 120 / 120 (100.0%) | 0 |

## Cached isolated-guitar chord gates

These rows count expected labeled chord-analysis windows (not full-mix samples). They are included only when the corresponding cached attribute TSV exists.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar Chord Mix — exact chord windows | 485 / 511 (94.9%) | 26 |
| Guitar Chord Mix — primary displayed chord windows | 400 / 511 (78.3%) | 111 |
| Guitar Chord Mix — expected guitar pitch classes | 1276 / 1533 (83.2%) | 257 |
| Guitar Techs Chord — exact chord windows | 7234 / 7484 (96.7%) | 250 |
| Guitar Techs Chord — primary displayed chord windows | 3577 / 7484 (47.8%) | 3907 |
| Guitar Techs Chord — expected guitar pitch classes | 24404 / 26738 (91.3%) | 2334 |
| Guitar Techs Music — exact chord windows | 388 / 500 (77.6%) | 112 |
| Guitar Techs Music — primary displayed chord windows | 221 / 500 (44.2%) | 279 |
| Guitar Techs Music — expected guitar pitch classes | 1609 / 1838 (87.5%) | 229 |
| Guitar Techs Music — power-chord exact windows | 6 / 26 (23.1%) | 20 |
| Gaps Guitar Full — exact chord windows | 361 / 540 (66.9%) | 179 |
| Gaps Guitar Full — primary displayed chord windows | 176 / 540 (32.6%) | 364 |
| Gaps Guitar Full — expected guitar pitch classes | 1518 / 1957 (77.6%) | 439 |
| Gaps Guitar Full — power-chord exact windows | 22 / 39 (56.4%) | 17 |
| Guitarset — exact chord windows | 1140 / 1491 (76.5%) | 351 |
| Guitarset — primary displayed chord windows | 622 / 1491 (41.7%) | 869 |
| Guitarset — expected guitar pitch classes | 4357 / 5340 (81.6%) | 983 |
| Guitarset — power-chord exact windows | 1 / 2 (50.0%) | 1 |

## URMP real multitrack gate

This downloaded real chamber-music corpus measures the same performances as provided mixes and as sums of their isolated tracks, with official note and MIDI annotations.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP — real pieces loadable | 44 / 44 (100.0%) | 0 |
| URMP — selected annotated windows | 528 / 528 (100.0%) | 0 |
| URMP — isolated-track exact notes | 1577 / 1788 (88.2%) | 211 |
| URMP — isolated-track detected notes | 1634 / 1788 (91.4%) | 154 |
| URMP — isolated-track precision | 1577 / 1756 (89.8%) | 179 false notes |
| URMP — provided-mix exact chords | 190 / 527 (36.1%) | 337 |
| URMP — provided stream chord windows | 224 / 527 (42.5%) | 303 |
| URMP — provided sequence chord windows | 214 / 527 (40.6%) | 313 |

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
| MAPS real piano — keyboard detected-note precision | 419 / 612 (68.5%) | 193 false predictions |
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
| MAPS isolated piano — keyboard detected-note precision | 196 / 729 (26.9%) | 533 false predictions |

## Full drum primary-classification gate

These rows count one-shot samples by the instrument shown as the primary drum. The latest completed full gate is reported even when a threshold fails, so its remaining classifications remain visible.

Source: `build/drum_samples_full_gate.out`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Full drum gate — primary kick | 6213 / 6505 (95.5%) | 292 |
| Full drum gate — primary snare | 4015 / 5390 (74.5%) | 1375 |
| Full drum gate — primary hihat | 1990 / 2358 (84.4%) | 368 |
| Full drum gate — primary crash | 562 / 788 (71.3%) | 226 |
| Full drum gate — primary tom | 1941 / 2861 (67.8%) | 920 |
| Full drum gate — primary ride | 241 / 352 (68.5%) | 111 |
| Full drum gate — primary rim | 333 / 504 (66.1%) | 171 |

## High-fidelity drum-kit primary-classification gate

These independent one-shot samples are sharded by expected instrument; the seven shard matrices are combined here so primary-label changes remain visible.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| High-fidelity drum kit — primary kick | 286 / 300 (95.3%) | 14 |
| High-fidelity drum kit — primary snare | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary hihat | 299 / 300 (99.7%) | 1 |
| High-fidelity drum kit — primary crash | 273 / 300 (91.0%) | 27 |
| High-fidelity drum kit — primary tom | 283 / 300 (94.3%) | 17 |
| High-fidelity drum kit — primary ride | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary rim | 283 / 300 (94.3%) | 17 |

Refresh with `make update-detection-accuracy-report`. Whenever a verified detection metric changes, update this report in the same commit.
