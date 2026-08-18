# Real-audio detection accuracy

This dashboard is generated from the deterministic full-mix real-note attribute TSV. Each denominator is the number of unique audio samples; a sample is accurate when any analyzed buffer meets the stated condition.

Source: `build/real_note_full_mix_attributes.tsv`

## Runtime OTHERS output

The catch-all OTHERS detector and renderer are intentionally disabled. Its historical rows remain below as baseline evidence only; they are not active runtime output.

| Work item | Complete / total | Remaining |
| --- | ---: | ---: |
| Disable OTHERS detection and rendering | 1 / 1 (100.0%) | 0 |

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Any detected note | 2212 / 2212 (100.0%) | 0 |
| Expected instrument row | 1622 / 2212 (73.3%) | 590 |
| Lit expected pitch class | 1496 / 2212 (67.6%) | 716 |
| Primary display row | 699 / 2212 (31.6%) | 1513 |
| Visual primary row | 745 / 2212 (33.7%) | 1467 |
| Bass — Any detected note | 137 / 137 (100.0%) | 0 |
| Bass — Expected instrument row | 137 / 137 (100.0%) | 0 |
| Bass — Lit expected pitch class | 137 / 137 (100.0%) | 0 |
| Bass — Primary display row | 46 / 137 (33.6%) | 91 |
| Bass — Visual primary row | 57 / 137 (41.6%) | 80 |
| Guitar — Any detected note | 346 / 346 (100.0%) | 0 |
| Guitar — Expected instrument row | 346 / 346 (100.0%) | 0 |
| Guitar — Lit expected pitch class | 288 / 346 (83.2%) | 58 |
| Guitar — Primary display row | 159 / 346 (46.0%) | 187 |
| Guitar — Visual primary row | 71 / 346 (20.5%) | 275 |
| Other — Any detected note | 590 / 590 (100.0%) | 0 |
| Other — Expected instrument row | 0 / 590 (0.0%) | 590 |
| Other — Lit expected pitch class | 0 / 590 (0.0%) | 590 |
| Other — Primary display row | 0 / 590 (0.0%) | 590 |
| Other — Visual primary row | 0 / 590 (0.0%) | 590 |
| Piano — Any detected note | 1117 / 1117 (100.0%) | 0 |
| Piano — Expected instrument row | 1117 / 1117 (100.0%) | 0 |
| Piano — Lit expected pitch class | 1050 / 1117 (94.0%) | 67 |
| Piano — Primary display row | 488 / 1117 (43.7%) | 629 |
| Piano — Visual primary row | 611 / 1117 (54.7%) | 506 |
| Vocals — Any detected note | 22 / 22 (100.0%) | 0 |
| Vocals — Expected instrument row | 22 / 22 (100.0%) | 0 |
| Vocals — Lit expected pitch class | 21 / 22 (95.5%) | 1 |
| Vocals — Primary display row | 6 / 22 (27.3%) | 16 |
| Vocals — Visual primary row | 6 / 22 (27.3%) | 16 |

## SATB multi-pitch candidate-capacity audit

The full-mix extractor considers up to 24 independently scored pitch candidates. This audit checks whether that cap, rather than pitch scoring, truncated labelled SATB windows.

Source: `build/polyphonic_candidate_capacity_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| SATB corpora reaching the 24-candidate cap | 0 / 3 (0.0%) | 3 |
| Missing pitch-class windows explained by capacity | 0 / 427 (0.0%) | 427 |
| 4% full-mix candidate-floor trial safe across SATB corpora | 0 / 1 (0.0%) | 1 |

No SATB corpus reaches the cap, so expanding candidate capacity is not an evidence-based recall fix. The 4% floor trial reduced visible vocal routing in the prepared SATB fixtures, so the 8% floor is retained.

## Harmonic-product octave-correction audit

Each full-mix candidate now exports a geometric direct/2x/3x/4x support score and the lower-subharmonic ratio before row routing. The audit treats an upper-octave-only candidate as a possible recovery and every labelled direct candidate as protected.

Source: `build/harmonic_product_octave_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Zero-regression harmonic-product thresholds across all SATB corpora | 0 / 6 (0.0%) | 6 |
| Independently labelled SATB corpora audited | 3 / 3 (100.0%) | 0 |
| Runtime harmonic-product octave correction eligible | 0 / 1 (0.0%) | 1 |

Every tested threshold—and every compact pairing with pitch confidence, periodicity, fit error, or noise—still moves at least one labelled correct pitch downward, so harmonic-product evidence remains diagnostic and no pre-routing correction is enabled.

## Detector-improvement route coverage

This tracks the empirical candidate search. A route is actionable only when its measured gain has no protected-row regression and positive evidence from two independently prepared corpora.

Source: `build/detector_improvement_route_summary.txt`

| Metric | Routes / total | Other routes |
| --- | ---: | ---: |
| Routes meeting protected and cross-corpus gates | 0 / 252 (0.0%) | 252 |
| Routes awaiting additional fixture coverage | 0 / 252 (0.0%) | 252 |
| Routes lacking independent-corpus replication | 123 / 252 (48.8%) | 129 |

## Electronic-piano-to-Guitar safety audit

The leading three-signal electronic-piano display profile is audited against the independent MAPS and MAESTRO piano corpora before any routing change.

Source: `build/electronic_piano_guitar_route_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Independent piano corpora reproducing the profile | 0 / 2 (0.0%) | 2 |
| Runtime routing change eligible | 0 / 1 (0.0%) | 1 |

The originating cached corpus has 10 matching electronic-piano samples; neither independent corpus reproduces the profile, so the rule is rejected.

## SCMS vocal-to-Other safety audit

The leading SCMS visual vocal-route profile is audited against independent Vocadito, VocalSet, and MIR-1K vocal corpora before any display change.

Source: `build/scms_vocal_other_route_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Independent vocal corpora reproducing the profile | 1 / 3 (33.3%) | 2 |
| Runtime display change eligible | 0 / 1 (0.0%) | 1 |

The originating SCMS corpus has 5 matching vocal samples. Only one independent corpus reproduces the profile, so the rule is rejected.

## Tenor-saxophone-to-Piano safety audit

The leading Good Sounds tenor-saxophone routing profile is audited against independent Iowa, TinySOL, real tenor-saxophone, and URMP saxophone fixtures before any reroute.

Source: `build/tenor_sax_piano_route_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Independent saxophone corpora reproducing the profile | 0 / 4 (0.0%) | 4 |
| Runtime routing change eligible | 0 / 1 (0.0%) | 1 |

The originating Good Sounds corpus has 3 matching tenor-saxophone samples; none of the 4 independent saxophone fixtures reproduces the profile, so the rule is rejected.

## URMP/Good Sounds saxophone shared-routing audit

URMP other-to-Piano routing failures are mined jointly with Good Sounds and protected against the general real-note, Iowa, TinySOL, and real A2S saxophone fixtures before any runtime reroute.

Source: `build/urmp_good_sounds_sax_shared_patterns.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Shared protected zero-regression routing selector found | 0 / 1 (0.0%) | 1 |

No shared zero-regression selector was found, so no saxophone routing change is permitted.

## Cross-corpus octave-correction audit

Large +36-semitone Other-instrument octave overshoots are mined jointly from the real-note, Philharmonia, and Iowa orchestral evidence, then protected against Good Sounds, TinySOL saxophone, URMP saxophone, and KRAISLER.

Source: `build/octave_correction_cross_corpus_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Shared protected zero-regression octave selector found | 0 / 1 (0.0%) | 1 |

No shared zero-regression octave selector was found, so broad octave correction is not permitted.

## Cross-corpus dominant-seventh extension audit

A plain major label may gain a dominant-seventh alias only when the complete four-tone pitch-class set and raw seventh evidence recur without chord regressions across independent corpora.

Source: `build/dominant_seventh_extension_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Corpora with a zero-regression dominant-seventh gain | 0 / 4 (0.0%) | 4 |
| Runtime dominant-seventh extension eligible | 0 / 1 (0.0%) | 1 |

The cached sweep found 3 regression(s), so the extension is rejected.

## Global chord confidence calibration audit

The chord label is assessed separately from the Bass and Vocal current-note displays. A higher display threshold is eligible only if it suppresses wrong labels without hiding a correct label in every confidence-capable corpus.

Source: `build/global_chord_confidence_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Corpora with zero-regression suppression at best floor (0.45) | 1 / 4 (25.0%) | 3 |
| Common zero-regression confidence floor found | 0 / 1 (0.0%) | 1 |
| Runtime global-chord confidence gate eligible | 0 / 1 (0.0%) | 1 |

No common zero-regression threshold was found, so the current chord display gate is retained.

## Expanded live GuitarSet baseline

GuitarSet contributes microphone-recorded live guitar with note and chord annotations. It is independent evidence for polyphonic guitar changes; this is a baseline, not a gate relaxation.

Source: `build/guitarset_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar pitch-class recall | 4446 / 5451 (81.6%) | 1005 |
| Exact guitar chord recall | 1141 / 1491 (76.5%) | 350 |

## Cross-corpus same-root guitar-quality audit

A same-root power chord may be promoted to a measured major/minor quality only when raw third evidence improves a missed label without regressing any correct label.

Source: `build/same_root_guitar_quality_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Corpora with a zero-regression same-root quality gain | 0 / 4 (0.0%) | 4 |
| Runtime same-root quality promotion eligible | 0 / 1 (0.0%) | 1 |

The best tested raw-third floor (0.040) still has 169 regression(s), so the promotion is rejected.

## Owner-classifier leave-one-corpus-out audit

A small nearest-centroid classifier is evaluated from the analyzer's existing owner scores, with every corpus held out in turn. It is an offline calibration experiment, not a runtime model.

Source: `build/owner_classifier_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current owner | 4 / 9 (44.4%) | 5 |
| Aggregate current-owner accuracy | 12807 / 61501 (20.8%) | 48694 |
| Aggregate centroid-model accuracy | 11176 / 61501 (18.2%) | 50325 |
| Runtime owner classifier eligible | 0 / 1 (0.0%) | 1 |

The model is retained only as an offline baseline because it regresses at least one held-out corpus.

## Extended owner-classifier leave-one-corpus-out audit

This offline nearest-centroid experiment adds pitch confidence, periodicity, harmonic shape, local noise, and adjacent-pitch features to the owner-score baseline. It remains a diagnostic model until it improves every held-out corpus.

Source: `build/owner_classifier_quality_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current owner | 8 / 9 (88.9%) | 1 |
| Aggregate current-owner accuracy | 12807 / 61643 (20.8%) | 48836 |
| Aggregate quality-model accuracy | 16088 / 61643 (26.1%) | 45555 |
| Runtime quality-model classifier eligible | 0 / 1 (0.0%) | 1 |
| Shared confidence-margin overrides with a protected gain | 0 / 11 (0.0%) | 11 |

The model is a stronger offline baseline, but its held-out real-note regression keeps runtime ownership unchanged. A shared 0.00--25.60 centroid-distance margin sweep also found no protected gain: high margins remove the benefit before they remove every regression.

## Owner-score calibration leave-one-corpus-out audit

A small class-bias calibration is fitted only on the non-held-out corpora and applied to the analyzer's existing owner scores. It is an offline experiment, not a runtime model.

Source: `build/owner_score_calibration_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current owner | 5 / 9 (55.6%) | 4 |
| Aggregate current-owner accuracy | 12807 / 61501 (20.8%) | 48694 |
| Aggregate calibrated-score accuracy | 12211 / 61501 (19.9%) | 49290 |
| Runtime score calibration eligible | 0 / 1 (0.0%) | 1 |

The calibration remains offline unless it improves every independently held-out corpus.

## Violin-to-Guitar safety audit

The leading Good Sounds violin routing profile is audited against independent Iowa strings and KRAISLER piano--violin mixture evidence before any reroute.

Source: `build/violin_guitar_route_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Independent violin corpora reproducing the profile | 0 / 2 (0.0%) | 2 |
| Runtime routing change eligible | 0 / 1 (0.0%) | 1 |

The originating Good Sounds corpus has 4 matching violin samples; neither independent violin corpus reproduces the profile, so the rule is rejected.

## Guitar chord tone-recovery safety audit

Third and fifth recovery rules are checked against the independent GAPS, Guitar Chord Mix, and Guitar-TECHS corpora before changing chord construction.

Source: `build/guitar_chord_tone_recovery_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Minor-third recovery corpora | 1 / 3 (33.3%) | 2 |
| Major-third recovery corpora | 2 / 3 (66.7%) | 1 |
| Major-third protected false promotions avoided | 0 / 1 (0.0%) | 1 |
| Minor-fifth recovery corpora | 0 / 3 (0.0%) | 3 |
| Major-fifth recovery corpora | 0 / 3 (0.0%) | 3 |
| Runtime tone-recovery change eligible | 0 / 2 (0.0%) | 2 |

Minor third is source-local; major third has 6 protected false promotions; neither fifth route has candidates. No tone-recovery rule is permitted.

## Guitar chord primary-display safety audit

The primary label may only be reordered when the same runtime-safe predicate is supported by both the isolated Guitar Chord Mix and full-performance GAPS corpora.

Source: `build/guitar_chord_primary_display_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar Chord Mix primary displayed chord | 400 / 511 (78.3%) | 111 |
| GAPS full-performance primary displayed chord | 176 / 540 (32.6%) | 364 |
| Corpora with any zero-regression local reorder rule | 1 / 2 (50.0%) | 1 |
| Shared runtime display change eligible | 0 / 1 (0.0%) | 1 |

GAPS has 12 local zero-regression rule candidates, but Guitar Chord Mix has 0; no shared rule exists, so no runtime reorder is permitted.

## High-soprano octave safety audit

A high F5/F#5 vocal recovery is only eligible if it improves at least two independent choir corpora with no protected-instrument reroutes. The lower-octave gate selects protected keyboard candidates; all tested zero-overlap multi-signal profiles reduced protected visual accuracy, so no behavior change is permitted.

Source: `build/high_vocal_octave_evidence.txt`

high-vocal octave safety audit: midi=77,78
| Lower-octave ratio cap | DCS candidates | CSD candidates | ESMUC candidates | Corpora with candidates | Protected risks |
| --- | ---: | ---: | ---: | ---: | ---: |
| <= 0.05 | 13 / 15 | 0 / 0 | 6 / 7 | 2 / 3 | 107 / 115 |
| <= 0.10 | 14 / 15 | 0 / 0 | 6 / 7 | 2 / 3 | 107 / 115 |
| <= 0.20 | 14 / 15 | 0 / 0 | 6 / 7 | 2 / 3 | 113 / 115 |
| <= 0.35 | 15 / 15 | 0 / 0 | 7 / 7 | 2 / 3 | 114 / 115 |
| <= 0.50 | 15 / 15 | 0 / 0 | 7 / 7 | 2 / 3 | 114 / 115 |
| <= 0.75 | 15 / 15 | 0 / 0 | 7 / 7 | 2 / 3 | 114 / 115 |
| <= 1.00 | 15 / 15 | 0 / 0 | 7 / 7 | 2 / 3 | 115 / 115 |

| Multi-signal route profile | DCS candidates | CSD candidates | ESMUC candidates | Corpora with candidates | Protected risks |
| --- | ---: | ---: | ---: | ---: | ---: |
| upper-adjacent >= 0.053; centroid 0.013..0.116 | 8 / 15 | 0 / 0 | 1 / 7 | 2 / 3 | 0 / 115 |

## Rejected three-corpus keys-to-vocal routing trial

A zero-static-risk `keys`-owned vocal subset spanning DCS, CSD, and ESMUC was trialled as a Vocal route. It did not improve DCS and reduced protected first-row accuracy, so the runtime change was removed.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS note hits during trial | 659 / 925 (71.2%) | 266 |
| DCS exact chord hits during trial | 49 / 240 (20.4%) | 191 |
| Protected full-mix first-row accuracy during trial | 771 / 2212 (34.9%) | 1441 |
| Protected full-mix first-row baseline | 772 / 2212 (34.9%) | 1440 |

The one protected-row regression violates the zero-regression gate despite the cross-corpus static evidence.

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
| CSD All CSD chord windows — Exact chord accuracy | 45 / 144 (31.2%) | 99 |
| CSD All CSD chord windows — Simplified chord accuracy | 64 / 144 (44.4%) | 80 |
| CSD All CSD vocal windows — Current-note vocal ownership | 68 / 144 (47.2%) | 76 |
| CSD All CSD vocal windows — Visible current-note vocal routing | 30 / 144 (20.8%) | 114 |
| CSD All SATB notes — Exact-MIDI recall | 366 / 576 (63.5%) | 210 |
| CSD All SATB notes — Pitch-class recall | 465 / 576 (80.7%) | 111 |
| CSD All SATB notes — Visible vocal routing | 31 / 576 (5.4%) | 545 |
| CSD All SATB notes — Vocal ownership | 79 / 576 (13.7%) | 497 |

### CSD SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD SATB range — Alto — Exact-MIDI recall | 103 / 144 (71.5%) | 41 |
| CSD SATB range — Alto — Pitch-class recall | 119 / 144 (82.6%) | 25 |
| CSD SATB range — Alto — Visible vocal routing | 14 / 144 (9.7%) | 130 |
| CSD SATB range — Alto — Vocal ownership | 39 / 144 (27.1%) | 105 |
| CSD SATB range — Bass — Exact-MIDI recall | 70 / 144 (48.6%) | 74 |
| CSD SATB range — Bass — Pitch-class recall | 106 / 144 (73.6%) | 38 |
| CSD SATB range — Bass — Visible vocal routing | 4 / 144 (2.8%) | 140 |
| CSD SATB range — Bass — Vocal ownership | 9 / 144 (6.2%) | 135 |
| CSD SATB range — Soprano — Exact-MIDI recall | 97 / 144 (67.4%) | 47 |
| CSD SATB range — Soprano — Pitch-class recall | 116 / 144 (80.6%) | 28 |
| CSD SATB range — Soprano — Visible vocal routing | 8 / 144 (5.6%) | 136 |
| CSD SATB range — Soprano — Vocal ownership | 13 / 144 (9.0%) | 131 |
| CSD SATB range — Tenor — Exact-MIDI recall | 96 / 144 (66.7%) | 48 |
| CSD SATB range — Tenor — Pitch-class recall | 124 / 144 (86.1%) | 20 |
| CSD SATB range — Tenor — Visible vocal routing | 5 / 144 (3.5%) | 139 |
| CSD SATB range — Tenor — Vocal ownership | 18 / 144 (12.5%) | 126 |

### CSD recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD Configuration — CSD_ER_Singer1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_ER_Singer1 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Exact-MIDI recall | 26 / 48 (54.2%) | 22 |
| CSD Configuration — CSD_ER_Singer1 — Pitch-class recall | 30 / 48 (62.5%) | 18 |
| CSD Configuration — CSD_ER_Singer1 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer1 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| CSD Configuration — CSD_ER_Singer2 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| CSD Configuration — CSD_ER_Singer2 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ER_Singer2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer2 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| CSD Configuration — CSD_ER_Singer3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_ER_Singer3 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_ER_Singer3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ER_Singer3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer3 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ER_Singer4 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_ER_Singer4 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| CSD Configuration — CSD_ER_Singer4 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer4 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer4 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer4 — Vocal ownership | 11 / 48 (22.9%) | 37 |
| CSD Configuration — CSD_LI_Singer1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer1 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_LI_Singer1 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_LI_Singer1 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_LI_Singer1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_LI_Singer1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_LI_Singer1 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_LI_Singer2 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_LI_Singer2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer2 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| CSD Configuration — CSD_LI_Singer2 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| CSD Configuration — CSD_LI_Singer2 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_LI_Singer2 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_LI_Singer2 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_LI_Singer2 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| CSD Configuration — CSD_LI_Singer3 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer3 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer3 — Exact-MIDI recall | 37 / 48 (77.1%) | 11 |
| CSD Configuration — CSD_LI_Singer3 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_LI_Singer3 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_LI_Singer3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_LI_Singer3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| CSD Configuration — CSD_LI_Singer3 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_LI_Singer4 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer4 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_LI_Singer4 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_LI_Singer4 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_LI_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_LI_Singer4 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ND_Singer1 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer1 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| CSD Configuration — CSD_ND_Singer1 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_ND_Singer1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| CSD Configuration — CSD_ND_Singer2 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer2 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| CSD Configuration — CSD_ND_Singer2 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_ND_Singer2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ND_Singer2 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer3 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer3 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer3 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| CSD Configuration — CSD_ND_Singer3 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ND_Singer3 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| CSD Configuration — CSD_ND_Singer3 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| CSD Configuration — CSD_ND_Singer4 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_ND_Singer4 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer4 — Exact-MIDI recall | 27 / 48 (56.2%) | 21 |
| CSD Configuration — CSD_ND_Singer4 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_ND_Singer4 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer4 — Vocal ownership | 9 / 48 (18.8%) | 39 |

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
| ESMUC All ESMUC chord windows — Exact chord accuracy | 65 / 218 (29.8%) | 153 |
| ESMUC All ESMUC chord windows — Simplified chord accuracy | 85 / 218 (39.0%) | 133 |
| ESMUC All ESMUC vocal windows — Current-note vocal ownership | 128 / 228 (56.1%) | 100 |
| ESMUC All ESMUC vocal windows — Visible current-note vocal routing | 56 / 228 (24.6%) | 172 |
| ESMUC All SATB notes — Exact-MIDI recall | 650 / 902 (72.1%) | 252 |
| ESMUC All SATB notes — Pitch-class recall | 764 / 902 (84.7%) | 138 |
| ESMUC All SATB notes — Visible vocal routing | 62 / 902 (6.9%) | 840 |
| ESMUC All SATB notes — Vocal ownership | 151 / 902 (16.7%) | 751 |

### ESMUC SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC SATB range — Alto — Exact-MIDI recall | 168 / 228 (73.7%) | 60 |
| ESMUC SATB range — Alto — Pitch-class recall | 193 / 228 (84.6%) | 35 |
| ESMUC SATB range — Alto — Visible vocal routing | 29 / 228 (12.7%) | 199 |
| ESMUC SATB range — Alto — Vocal ownership | 40 / 228 (17.5%) | 188 |
| ESMUC SATB range — Bass — Exact-MIDI recall | 182 / 228 (79.8%) | 46 |
| ESMUC SATB range — Bass — Pitch-class recall | 206 / 228 (90.4%) | 22 |
| ESMUC SATB range — Bass — Visible vocal routing | 17 / 228 (7.5%) | 211 |
| ESMUC SATB range — Bass — Vocal ownership | 48 / 228 (21.1%) | 180 |
| ESMUC SATB range — Soprano — Exact-MIDI recall | 130 / 218 (59.6%) | 88 |
| ESMUC SATB range — Soprano — Pitch-class recall | 168 / 218 (77.1%) | 50 |
| ESMUC SATB range — Soprano — Visible vocal routing | 7 / 218 (3.2%) | 211 |
| ESMUC SATB range — Soprano — Vocal ownership | 19 / 218 (8.7%) | 199 |
| ESMUC SATB range — Tenor — Exact-MIDI recall | 170 / 228 (74.6%) | 58 |
| ESMUC SATB range — Tenor — Pitch-class recall | 197 / 228 (86.4%) | 31 |
| ESMUC SATB range — Tenor — Visible vocal routing | 9 / 228 (3.9%) | 219 |
| ESMUC SATB range — Tenor — Vocal ownership | 44 / 228 (19.3%) | 184 |

### ESMUC recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible current-note vocal routing | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible vocal routing | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Vocal ownership | 13 / 48 (27.1%) | 35 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact chord accuracy | 4 / 10 (40.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact-MIDI recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Pitch-class recall | 46 / 48 (95.8%) | 2 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Simplified chord accuracy | 4 / 10 (40.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_SE_short3 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact-MIDI recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Pitch-class recall | 45 / 48 (93.8%) | 3 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact-MIDI recall | 20 / 38 (52.6%) | 18 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Pitch-class recall | 28 / 38 (73.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Simplified chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible vocal routing | 2 / 38 (5.3%) | 36 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Vocal ownership | 5 / 38 (13.2%) | 33 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact-MIDI recall | 33 / 48 (68.8%) | 15 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Simplified chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact chord accuracy | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact-MIDI recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Vocal ownership | 11 / 48 (22.9%) | 37 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact-MIDI recall | 33 / 48 (68.8%) | 15 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Vocal ownership | 7 / 48 (14.6%) | 41 |

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
| CSD — exact MIDI in vocal row | 68 / 576 (11.8%) | 508 |
| CSD — exact MIDI only in foreign row | 274 / 576 (47.6%) | 302 |
| CSD — pitch class only (wrong octave) | 94 / 576 (16.3%) | 482 |
| CSD — no expected pitch class | 140 / 576 (24.3%) | 436 |
| DCS — exact MIDI in vocal row | 78 / 984 (7.9%) | 906 |
| DCS — exact MIDI only in foreign row | 355 / 984 (36.1%) | 629 |
| DCS — pitch class only (wrong octave) | 221 / 984 (22.5%) | 763 |
| DCS — no expected pitch class | 330 / 984 (33.5%) | 654 |
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
| Vocadito — exact MIDI in vocal row | 744 / 2284 (32.6%) | 1540 |
| Vocadito — exact MIDI only in foreign row | 937 / 2284 (41.0%) | 1347 |
| Vocadito — pitch class only (wrong octave) | 251 / 2284 (11.0%) | 2033 |
| Vocadito — no expected pitch class | 352 / 2284 (15.4%) | 1932 |
| VocalSet — exact MIDI in vocal row | 3065 / 17344 (17.7%) | 14279 |
| VocalSet — exact MIDI only in foreign row | 7963 / 17344 (45.9%) | 9381 |
| VocalSet — pitch class only (wrong octave) | 1909 / 17344 (11.0%) | 15435 |
| VocalSet — no expected pitch class | 4407 / 17344 (25.4%) | 12937 |

## Dagstuhl ChoirSet (DCS) real-audio measurement

The SATB rows count every score-active singer at a stable center-of-note window in a real, summed four-singer recording. Vocal ownership and routing require the expected pitch class in the vocal row; visible routing additionally requires visual level at least 0.25. Current-note vocal rows are separate window-level metrics: because the UI is monophonic, they count success when its one displayed note matches any concurrent SATB score pitch.

Source: `build/dagstuhl_choirset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS All DCS chord windows — Exact chord accuracy | 38 / 240 (15.8%) | 202 |
| DCS All DCS chord windows — Simplified chord accuracy | 72 / 240 (30.0%) | 168 |
| DCS All DCS vocal windows — Current-note vocal ownership | 89 / 240 (37.1%) | 151 |
| DCS All DCS vocal windows — Visible current-note vocal routing | 52 / 240 (21.7%) | 188 |
| DCS All SATB notes — Exact-MIDI recall | 473 / 984 (48.1%) | 511 |
| DCS All SATB notes — Pitch-class recall | 719 / 984 (73.1%) | 265 |
| DCS All SATB notes — Visible vocal routing | 58 / 984 (5.9%) | 926 |
| DCS All SATB notes — Vocal ownership | 114 / 984 (11.6%) | 870 |

### DCS SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS SATB range — Alto — Exact-MIDI recall | 150 / 240 (62.5%) | 90 |
| DCS SATB range — Alto — Pitch-class recall | 184 / 240 (76.7%) | 56 |
| DCS SATB range — Alto — Visible vocal routing | 20 / 240 (8.3%) | 220 |
| DCS SATB range — Alto — Vocal ownership | 37 / 240 (15.4%) | 203 |
| DCS SATB range — Bass — Exact-MIDI recall | 69 / 264 (26.1%) | 195 |
| DCS SATB range — Bass — Pitch-class recall | 187 / 264 (70.8%) | 77 |
| DCS SATB range — Bass — Visible vocal routing | 8 / 264 (3.0%) | 256 |
| DCS SATB range — Bass — Vocal ownership | 21 / 264 (8.0%) | 243 |
| DCS SATB range — Soprano — Exact-MIDI recall | 124 / 240 (51.7%) | 116 |
| DCS SATB range — Soprano — Pitch-class recall | 158 / 240 (65.8%) | 82 |
| DCS SATB range — Soprano — Visible vocal routing | 8 / 240 (3.3%) | 232 |
| DCS SATB range — Soprano — Vocal ownership | 18 / 240 (7.5%) | 222 |
| DCS SATB range — Tenor — Exact-MIDI recall | 130 / 240 (54.2%) | 110 |
| DCS SATB range — Tenor — Pitch-class recall | 190 / 240 (79.2%) | 50 |
| DCS SATB range — Tenor — Visible vocal routing | 22 / 240 (9.2%) | 218 |
| DCS SATB range — Tenor — Vocal ownership | 38 / 240 (15.8%) | 202 |

### DCS recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact-MIDI recall | 24 / 48 (50.0%) | 24 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact-MIDI recall | 19 / 48 (39.6%) | 29 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible current-note vocal routing | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible vocal routing | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact-MIDI recall | 22 / 48 (45.8%) | 26 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible vocal routing | 0 / 48 (0.0%) | 48 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact-MIDI recall | 15 / 48 (31.2%) | 33 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Pitch-class recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact-MIDI recall | 24 / 48 (50.0%) | 24 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact-MIDI recall | 27 / 52 (51.9%) | 25 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Pitch-class recall | 43 / 52 (82.7%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible vocal routing | 4 / 52 (7.7%) | 48 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact-MIDI recall | 23 / 52 (44.2%) | 29 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Pitch-class recall | 39 / 52 (75.0%) | 13 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible vocal routing | 0 / 52 (0.0%) | 52 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Vocal ownership | 3 / 52 (5.8%) | 49 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact-MIDI recall | 19 / 52 (36.5%) | 33 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Pitch-class recall | 33 / 52 (63.5%) | 19 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Visible vocal routing | 2 / 52 (3.8%) | 50 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Vocal ownership | 8 / 52 (15.4%) | 44 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Current-note vocal ownership | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Exact-MIDI recall | 18 / 52 (34.6%) | 34 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Pitch-class recall | 35 / 52 (67.3%) | 17 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Visible vocal routing | 1 / 52 (1.9%) | 51 |
| DCS Configuration — DCS_TP_FullChoir_Take04 — Vocal ownership | 4 / 52 (7.7%) | 48 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact chord accuracy | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact-MIDI recall | 36 / 52 (69.2%) | 16 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Pitch-class recall | 50 / 52 (96.2%) | 2 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible vocal routing | 6 / 52 (11.5%) | 46 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact-MIDI recall | 34 / 52 (65.4%) | 18 |
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
| Vocadito vocals — Expected instrument row | 309 / 354 (87.3%) | 45 |
| Vocadito vocals — Lit expected pitch class | 172 / 354 (48.6%) | 182 |
| Vocadito vocals — Primary display row | 47 / 354 (13.3%) | 307 |
| Vocadito vocals — Visual primary row | 34 / 354 (9.6%) | 320 |

## VocalSet full-mix vocal routing

This larger, varied real-vocal corpus measures whether the detected note remains on the vocal row when the analyzer also proposes instrumental rows.

Source: `build/vocalset_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| VocalSet vocals — Any detected note | 2365 / 2389 (99.0%) | 24 |
| VocalSet vocals — Expected instrument row | 1390 / 2389 (58.2%) | 999 |
| VocalSet vocals — Lit expected pitch class | 795 / 2389 (33.3%) | 1594 |
| VocalSet vocals — Primary display row | 216 / 2389 (9.0%) | 2173 |
| VocalSet vocals — Visual primary row | 209 / 2389 (8.7%) | 2180 |

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
| Good Sounds — Any detected note | 1316 / 1318 (99.8%) | 2 |
| Good Sounds — Expected instrument row | 143 / 1318 (10.8%) | 1175 |
| Good Sounds — Lit expected pitch class | 142 / 1318 (10.8%) | 1176 |
| Good Sounds — Primary display row | 3 / 1318 (0.2%) | 1315 |
| Good Sounds — Visual primary row | 7 / 1318 (0.5%) | 1311 |
| Good Sounds — Bass — Any detected note | 159 / 159 (100.0%) | 0 |
| Good Sounds — Bass — Expected instrument row | 143 / 159 (89.9%) | 16 |
| Good Sounds — Bass — Lit expected pitch class | 142 / 159 (89.3%) | 17 |
| Good Sounds — Bass — Primary display row | 3 / 159 (1.9%) | 156 |
| Good Sounds — Bass — Visual primary row | 7 / 159 (4.4%) | 152 |
| Good Sounds — Other — Any detected note | 1157 / 1159 (99.8%) | 2 |
| Good Sounds — Other — Expected instrument row | 0 / 1159 (0.0%) | 1159 |
| Good Sounds — Other — Lit expected pitch class | 0 / 1159 (0.0%) | 1159 |
| Good Sounds — Other — Primary display row | 0 / 1159 (0.0%) | 1159 |
| Good Sounds — Other — Visual primary row | 0 / 1159 (0.0%) | 1159 |

## IRMAS independent instrument-routing coverage

IRMAS supplies real musical excerpts labelled for their predominant instrument. It has no time-aligned pitch truth, so these rows measure only runtime candidate availability and instrument/display routing; they are never used as note- or chord-accuracy claims.

Source: `build/irmas_labelled_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| IRMAS — Any runtime pitch candidate | 1847 / 1847 (100.0%) | 0 |
| IRMAS — Labelled instrument pitch-class row | 1830 / 1847 (99.1%) | 17 |
| IRMAS — Strongest raw routing row | 1771 / 1847 (95.9%) | 76 |
| IRMAS — Strongest visible routing row | 1774 / 1847 (96.0%) | 73 |
| IRMAS — Guitar — Any runtime pitch candidate | 384 / 384 (100.0%) | 0 |
| IRMAS — Guitar — Labelled instrument pitch-class row | 383 / 384 (99.7%) | 1 |
| IRMAS — Guitar — Strongest raw routing row | 381 / 384 (99.2%) | 3 |
| IRMAS — Guitar — Strongest visible routing row | 382 / 384 (99.5%) | 2 |
| IRMAS — Other — Any runtime pitch candidate | 887 / 887 (100.0%) | 0 |
| IRMAS — Other — Labelled instrument pitch-class row | 887 / 887 (100.0%) | 0 |
| IRMAS — Other — Strongest raw routing row | 872 / 887 (98.3%) | 15 |
| IRMAS — Other — Strongest visible routing row | 883 / 887 (99.5%) | 4 |
| IRMAS — Piano — Any runtime pitch candidate | 384 / 384 (100.0%) | 0 |
| IRMAS — Piano — Labelled instrument pitch-class row | 384 / 384 (100.0%) | 0 |
| IRMAS — Piano — Strongest raw routing row | 384 / 384 (100.0%) | 0 |
| IRMAS — Piano — Strongest visible routing row | 384 / 384 (100.0%) | 0 |
| IRMAS — Vocals — Any runtime pitch candidate | 192 / 192 (100.0%) | 0 |
| IRMAS — Vocals — Labelled instrument pitch-class row | 176 / 192 (91.7%) | 16 |
| IRMAS — Vocals — Strongest raw routing row | 134 / 192 (69.8%) | 58 |
| IRMAS — Vocals — Strongest visible routing row | 125 / 192 (65.1%) | 67 |

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
| Iowa orchestra — Any detected note | 672 / 673 (99.9%) | 1 |
| Iowa orchestra — Expected instrument row | 672 / 673 (99.9%) | 1 |
| Iowa orchestra — Lit expected pitch class | 672 / 673 (99.9%) | 1 |
| Iowa orchestra — Primary display row | 672 / 673 (99.9%) | 1 |
| Iowa orchestra — Visual primary row | 672 / 673 (99.9%) | 1 |
| Iowa orchestra — Bass — Any detected note | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Expected instrument row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Lit expected pitch class | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Primary display row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Visual primary row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Other — Any detected note | 647 / 648 (99.8%) | 1 |
| Iowa orchestra — Other — Expected instrument row | 647 / 648 (99.8%) | 1 |
| Iowa orchestra — Other — Lit expected pitch class | 647 / 648 (99.8%) | 1 |
| Iowa orchestra — Other — Primary display row | 647 / 648 (99.8%) | 1 |
| Iowa orchestra — Other — Visual primary row | 647 / 648 (99.8%) | 1 |
| Iowa orchestra — Exact expected MIDI note | 664 / 673 (98.7%) | 9 |
| Iowa orchestra — Other — exact expected MIDI note | 642 / 648 (99.1%) | 6 |
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

### MusicNet annotated instrument-routing

Each active annotated note is checked against its General-MIDI family row. These are real-mixture routing measurements, separate from the global chord gate.

Source: `build/musicnet_routing.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MusicNet All — Exact note in expected row | 3229 / 13079 (24.7%) | 9850 |
| MusicNet All — Pitch class in expected row | 6583 / 13079 (50.3%) | 6496 |
| MusicNet All — Visible exact note in expected row | 3229 / 13079 (24.7%) | 9850 |
| MusicNet All — Visible pitch class in expected row | 6583 / 13079 (50.3%) | 6496 |
| MusicNet Other — Exact note in expected row | 2069 / 8566 (24.2%) | 6497 |
| MusicNet Other — Pitch class in expected row | 3797 / 8566 (44.3%) | 4769 |
| MusicNet Other — Visible exact note in expected row | 2069 / 8566 (24.2%) | 6497 |
| MusicNet Other — Visible pitch class in expected row | 3797 / 8566 (44.3%) | 4769 |
| MusicNet Piano — Exact note in expected row | 1160 / 4513 (25.7%) | 3353 |
| MusicNet Piano — Pitch class in expected row | 2786 / 4513 (61.7%) | 1727 |
| MusicNet Piano — Visible exact note in expected row | 1160 / 4513 (25.7%) | 3353 |
| MusicNet Piano — Visible pitch class in expected row | 2786 / 4513 (61.7%) | 1727 |

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
| Measure real KRAISLER note and chord outcomes | 1 / 1 (100.0%) | 0 |
| Complete protected KRAISLER cross-corpus rule audit | 1 / 1 (100.0%) | 0 |

### KRAISLER real piano–violin measurement

Source: `build/kraisler_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| KRAISLER All KRAISLER chord windows — Exact chord accuracy | 213 / 720 (29.6%) | 507 |
| KRAISLER All KRAISLER chord windows — Simplified chord accuracy | 275 / 720 (38.2%) | 445 |
| KRAISLER All KRAISLER notes — Exact-MIDI recall | 2048 / 4242 (48.3%) | 2194 |
| KRAISLER All KRAISLER notes — Expected instrument row | 1981 / 4242 (46.7%) | 2261 |
| KRAISLER All KRAISLER notes — Pitch-class recall | 3505 / 4242 (82.6%) | 737 |
| KRAISLER All KRAISLER notes — Visible expected instrument row | 1659 / 4242 (39.1%) | 2583 |
| KRAISLER Configuration — dry — Exact chord accuracy | 71 / 240 (29.6%) | 169 |
| KRAISLER Configuration — dry — Exact-MIDI recall | 693 / 1414 (49.0%) | 721 |
| KRAISLER Configuration — dry — Expected instrument row | 672 / 1414 (47.5%) | 742 |
| KRAISLER Configuration — dry — Pitch-class recall | 1160 / 1414 (82.0%) | 254 |
| KRAISLER Configuration — dry — Simplified chord accuracy | 88 / 240 (36.7%) | 152 |
| KRAISLER Configuration — dry — Visible expected instrument row | 548 / 1414 (38.8%) | 866 |
| KRAISLER Configuration — hall — Exact chord accuracy | 62 / 240 (25.8%) | 178 |
| KRAISLER Configuration — hall — Exact-MIDI recall | 666 / 1414 (47.1%) | 748 |
| KRAISLER Configuration — hall — Expected instrument row | 636 / 1414 (45.0%) | 778 |
| KRAISLER Configuration — hall — Pitch-class recall | 1161 / 1414 (82.1%) | 253 |
| KRAISLER Configuration — hall — Simplified chord accuracy | 84 / 240 (35.0%) | 156 |
| KRAISLER Configuration — hall — Visible expected instrument row | 533 / 1414 (37.7%) | 881 |
| KRAISLER Configuration — studio — Exact chord accuracy | 80 / 240 (33.3%) | 160 |
| KRAISLER Configuration — studio — Exact-MIDI recall | 689 / 1414 (48.7%) | 725 |
| KRAISLER Configuration — studio — Expected instrument row | 673 / 1414 (47.6%) | 741 |
| KRAISLER Configuration — studio — Pitch-class recall | 1184 / 1414 (83.7%) | 230 |
| KRAISLER Configuration — studio — Simplified chord accuracy | 103 / 240 (42.9%) | 137 |
| KRAISLER Configuration — studio — Visible expected instrument row | 578 / 1414 (40.9%) | 836 |
| KRAISLER KRAISLER Piano notes — Exact-MIDI recall | 1614 / 3339 (48.3%) | 1725 |
| KRAISLER KRAISLER Piano notes — Expected instrument row | 1981 / 3339 (59.3%) | 1358 |
| KRAISLER KRAISLER Piano notes — Pitch-class recall | 2736 / 3339 (81.9%) | 603 |
| KRAISLER KRAISLER Piano notes — Visible expected instrument row | 1659 / 3339 (49.7%) | 1680 |
| KRAISLER KRAISLER Violin notes — Exact-MIDI recall | 434 / 903 (48.1%) | 469 |
| KRAISLER KRAISLER Violin notes — Expected instrument row | 0 / 903 (0.0%) | 903 |
| KRAISLER KRAISLER Violin notes — Pitch-class recall | 769 / 903 (85.2%) | 134 |
| KRAISLER KRAISLER Violin notes — Visible expected instrument row | 0 / 903 (0.0%) | 903 |

### KRAISLER annotated-tempo diagnostic

Source: `build/kraisler_bpm_diagnostics.log`. Each row is real KRAISLER mixture audio paired with a stable, reviewed beat-time interval; it is diagnostic evidence, not a release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 0 / 11 (0.0%) | 11 |

## Ballroom real-mix annotated-tempo diagnostic

Source: `build/ballroom_bpm_diagnostics.log`. Ballroom supplies manually corrected beat and bar times for real dance mixes; this is rhythm-heavy independent tempo evidence, not a release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 1 / 64 (1.6%) | 63 |

## FiloBass real bass-led annotated-tempo diagnostic

Source: `build/filobass_bpm_diagnostics.log`. FiloBass pairs real jazz bass stems with reviewed downbeat syncpoints and a MIDI time signature; BPM references are derived only from those corpus annotations.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 0 / 24 (0.0%) | 24 |

### FiloBass source-grid energy feasibility diagnostic

The corpus harness forces the labelled BPM into the final diagnostic slot, then compares its bass energy with the selected candidate. This is not a score-ranked candidate and does not change BPM selection.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Labelled BPM exported through harness-only probe | 24 / 24 (100.0%) | 0 |
| Present labelled candidate has higher bass grid-energy | 4 / 24 (16.7%) | 20 |
| Present labelled candidate ties selected bass grid-energy | 4 / 24 (16.7%) | 20 |
| Present labelled candidate has lower bass grid-energy | 16 / 24 (66.7%) | 8 |

### FiloBass raw bass-attack feasibility diagnostic

Source: `build/filobass_bass_onset_diagnostics.tsv`. This offline analysis ranks tempos from raw bass-envelope attacks only. It is a feature-feasibility check, not a live-output result or release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Reviewed BPM ranked first by raw bass attacks | 1 / 24 (4.2%) | 23 |
| Reviewed BPM ranked in top five by raw bass attacks | 10 / 24 (41.7%) | 14 |

## E-GMD generated percussion tempo diagnostic

Source: `build/egmd_bpm_diagnostics.log`. This generated aligned-MIDI fixture exercises kick/snare phase recovery; it is a regression benchmark, not independent real-audio evidence.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 20 / 20 (100.0%) | 0 |

## IDMT real-bass timing-ground-truth audit

Source: `build/idmt_bass_lines_tempo_metadata.tsv`. IDMT provides real bass audio and reviewed note onsets, but only corpus-supplied tempo, beat, or pattern fields qualify it as BPM ground truth.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Tracks with corpus-supplied tempo, beat, or pattern metadata | 0 / 17 (0.0%) | 17 |

## Tempo coverage-gap checklist

Tempo estimates are only displayed at calibrated confidence. Source-specific phase evidence is tested separately from corpus coverage so a synthetic regression fixture cannot be mistaken for independent real-audio validation.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Separate kick, bass, snare, and tonal onset histories | 1 / 1 (100.0%) | 0 | source-specific phase coverage in debug candidates |
| Preserve simultaneous kick+bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer case verifies both kick and bass phase coverage on the same downbeats |
| Require repeated source evidence on the selected beat grid | 1 / 1 (100.0%) | 0 | confidence cap below display floor without repeated alignment |
| Resolve half/double-time candidates with kick/bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer cases retain the beat grid through sparse-kick half-time and dense-subdivision alternatives |
| Adaptive tempo history for percussive vs sparse tonal input | 1 / 1 (100.0%) | 0 | 8 s percussion / 18 s sparse-source policy |
| Generated drum phase regression measured | 1 / 1 (100.0%) | 0 | E-GMD x/total BPM diagnostic |
| Retrieve versioned Ballroom beat/bar annotations | 1 / 1 (100.0%) | 0 | CPJKU BallroomAnnotations checkout in InstrumentSamples |
| Rhythm-heavy real-mix beat validation measured | 1 / 1 (100.0%) | 0 | up to 64 genre-balanced Ballroom stable sections with manually corrected beat/bar annotations |
| IDMT real-bass timing metadata qualifies as beat truth | 0 / 17 (0.0%) | 17 | only corpus-supplied tempo/beat/pattern fields count; note onsets are insufficient |
| Independent real bass-led beat-labelled validation measured | 1 / 1 (100.0%) | 0 | FiloBass real bass stems plus reviewed downbeats and MIDI time signature |
| Assess raw bass-attack BPM evidence | 1 / 1 (100.0%) | 0 | offline FiloBass rank-one/top-five diagnostic |
| Assess bass source-grid energy before a selector | 1 / 1 (100.0%) | 0 | FiloBass expected candidate shows higher bass alignment in 4/24 eligible rows |
| Reject unproven meter/bass candidate reweighting | 1 / 1 (100.0%) | 0 | feasibility audit: Ballroom meter/bass selectors stay at 4 / 61; FiloBass stays at 4 / 24, so neither is a safe BPM selector |
| Reject unproven normalized-recurrence selector | 1 / 1 (100.0%) | 0 | lag-normalized recurrence reaches 6 / 61 only at an extreme Ballroom weight and remains 4 / 24 on FiloBass |
| Reject unproven kick+bass-coincidence selector | 1 / 1 (100.0%) | 0 | same-frame coincidence reaches 5 / 61 on Ballroom but stays 4 / 24 on FiloBass, so it cannot safely resolve meter alone |
| Reject longer percussive phase history | 1 / 1 (100.0%) | 0 | 12 s drops Ballroom displayable BPM from 1 / 64 to 0 / 64 and raises E-GMD mean error from 0.21 to 0.32 BPM; retain the 8 s policy |
| Local advanced beat-tracker backend available | 0 / 2 (0.0%) | 2 | `aubio` and `essentia` are unavailable through pkg-config; next step is a dependency-free tracker or an added backend |
| Demonstrate a bass-attack feature improves real bass BPM | 0 / 1 (0.0%) | 1 | improve FiloBass displayable BPM without regressing E-GMD |
| Hide BPM when calibrated confidence is insufficient | 1 / 1 (100.0%) | 0 | renderer keeps `BPM --` below 0.60 confidence |

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
| High-fidelity drum kit — primary kick | 288 / 300 (96.0%) | 12 |
| High-fidelity drum kit — primary snare | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary hihat | 299 / 300 (99.7%) | 1 |
| High-fidelity drum kit — primary crash | 283 / 300 (94.3%) | 17 |
| High-fidelity drum kit — primary tom | 282 / 300 (94.0%) | 18 |
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
