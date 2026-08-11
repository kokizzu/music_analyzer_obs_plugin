# Real-audio detection accuracy

This dashboard is generated from the deterministic full-mix real-note attribute TSV. Each denominator is the number of unique audio samples; a sample is accurate when any analyzed buffer meets the stated condition.

Source: `build/real_note_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Any detected note | 2212 / 2212 (100.0%) | 0 |
| Expected instrument row | 2212 / 2212 (100.0%) | 0 |
| Primary display row | 773 / 2212 (34.9%) | 1439 |
| Visual primary row | 865 / 2212 (39.1%) | 1347 |
| Bass — Any detected note | 137 / 137 (100.0%) | 0 |
| Bass — Expected instrument row | 137 / 137 (100.0%) | 0 |
| Bass — Primary display row | 45 / 137 (32.8%) | 92 |
| Bass — Visual primary row | 50 / 137 (36.5%) | 87 |
| Guitar — Any detected note | 346 / 346 (100.0%) | 0 |
| Guitar — Expected instrument row | 346 / 346 (100.0%) | 0 |
| Guitar — Primary display row | 152 / 346 (43.9%) | 194 |
| Guitar — Visual primary row | 60 / 346 (17.3%) | 286 |
| Other — Any detected note | 590 / 590 (100.0%) | 0 |
| Other — Expected instrument row | 590 / 590 (100.0%) | 0 |
| Other — Primary display row | 118 / 590 (20.0%) | 472 |
| Other — Visual primary row | 208 / 590 (35.3%) | 382 |
| Piano — Any detected note | 1117 / 1117 (100.0%) | 0 |
| Piano — Expected instrument row | 1117 / 1117 (100.0%) | 0 |
| Piano — Primary display row | 452 / 1117 (40.5%) | 665 |
| Piano — Visual primary row | 541 / 1117 (48.4%) | 576 |
| Vocals — Any detected note | 22 / 22 (100.0%) | 0 |
| Vocals — Expected instrument row | 22 / 22 (100.0%) | 0 |
| Vocals — Primary display row | 6 / 22 (27.3%) | 16 |
| Vocals — Visual primary row | 6 / 22 (27.3%) | 16 |

## Cached isolated-guitar chord gates

These rows count expected labeled chord-analysis windows (not full-mix samples). They are included only when the corresponding cached attribute TSV exists.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar Chord Mix — exact chord windows | 485 / 511 (94.9%) | 26 |
| Guitar Chord Mix — expected guitar pitch classes | 1276 / 1533 (83.2%) | 257 |
| Guitar Techs Chord — exact chord windows | 7203 / 7484 (96.2%) | 281 |
| Guitar Techs Chord — expected guitar pitch classes | 24409 / 26738 (91.3%) | 2329 |
| Gaps Guitar Full — exact chord windows | 361 / 540 (66.9%) | 179 |
| Gaps Guitar Full — expected guitar pitch classes | 1518 / 1957 (77.6%) | 439 |
| Guitarset — exact chord windows | 1140 / 1491 (76.5%) | 351 |
| Guitarset — expected guitar pitch classes | 4357 / 5340 (81.6%) | 983 |

Refresh with `make update-detection-accuracy-report`. Whenever a verified detection metric changes, update this report in the same commit.
