# Real-audio detection accuracy

This dashboard is generated from the deterministic full-mix real-note attribute TSV. Each denominator is the number of unique audio samples; a sample is accurate when any analyzed buffer meets the stated condition.

Source: `build/real_note_full_mix_attributes.tsv`

## Active goal-priority tracker

Evidence coverage means the named corpus replay or audit is available. A goal checkpoint counts only a safe enabled change, the required offline veto, or a qualified corpus; diagnostic and rejected trials never count as ready.

| Priority | Evidence coverage | Goal checkpoint | Remaining proof |
| --- | ---: | ---: | --- |
| 1. Calibrate drum detection | 3 / 3 (100.0%) | 1 / 1 (100.0%) | current labelled spread replay: HiHat active 191 / 209 (91.4%), primary 184 / 209 (88.0%), with 0 / 191 active false positives; retain the early-onset HiHat rule and idle-treble OBS guard only while they improve MDB and BabySlakh, preserve STAR, and have no protected false-positive regression |
| 2. Stabilize chord state | 2 / 2 (100.0%) | 1 / 1 (100.0%) | retain the 0.70 keyboard-only display gate only while it lowers wrong labels without correct-frame or flicker loss |
| 3. Improve Tom/Rim/Ride | 5 / 5 (100.0%) | 1 / 1 (100.0%) | retain the cross-acoustic Tom recovery only while all protected one-shot replays remain non-regressing |
| 4. Safe live Beat This! | 2 / 2 (100.0%) | 1 / 1 (100.0%) | optional C++ sidecar preserves the exact 20 s packet and ≥44-interval gate; it never replaces a displayable normal BPM |
| 5. High-tempo GTZAN offline veto | 1 / 1 (100.0%) | 1 / 1 (100.0%) | retain offline-only restriction; it cannot authorize the live BPM display |
| 6. Proper bass tempo corpus | 1 / 1 (100.0%) | 1 / 1 (100.0%) | turn FiloBass evidence into a protected bass-led selector before any runtime BPM change |
| 7. Recover high-soprano Vocal routing | 2 / 2 (100.0%) | 0 / 1 (0.0%) | the broad F5/F#5 mirror is disabled: it activates on 9 protected non-vocal rows; seek a causal selector with zero protected displays |
| 8. Evaluate causal ONNX pitch fusion | 11 / 11 (100.0%) | 1 / 1 (100.0%) | native+ONNX support finds an 8 correct / 0 false CSD+ESMUC Vocal-mirror profile at 0.80 from complementary Guitar↔Keyboard owner-evidence gates; newly created and previously unset OBS filters enable this bounded non-blocking fusion, while an explicit opt-out remains supported. Live OBS capture replay is deferred at user direction because it requires user-provided audio |

## Ranked next accuracy work

These are open improvements, ranked by expected user impact and whether a new, independent measurement can decide them. The fourth column separates completed decision checks from the remaining accuracy deficit, so a completed check is never mistaken for a correct detector result.

| Rank | Accuracy target | Current evidence | Checks run / total; remaining deficit | Next decision-quality check | Guard against regression |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | Immediate source-onset BPM (Kick/Bass/Snare) | Runtime now shows the continuously recomputed trailing 3 s Kick/Bass/Snare window; it never holds an earlier result for a fixed batch or expiry period. E-GMD: 17 / 20 raw starts correct; 3 unsafe aliases vetoed. Ballroom: 0 / 64, GTZAN-Rhythm: 0 / 100, FiloBass: 0 / 48 displayed BPM at 3 s; the raw Ballroom source estimator is available 64 / 64 and accurate 4 / 64 with 60 aliases; raw FiloBass source is available 36 / 48 and accurate 3 / 48 with 33 aliases; raw GTZAN-Rhythm source is available 60 / 100 and accurate 7 / 100 with 53 aliases. Per-source pair agreement: 0 / 3 (0.0%) zero-wrong pairs; a new within-source grid agreement accepts 16 / 50 but is wrong on 34, so it is rejected | 4 / 4 (100.0%) corpus checks run; 3 / 4 (75.0%) need an accurate 3 s output | improve the causal trailing-window scorer without changing its moving-window contract; replay all four annotated corpora | preserve the moving 3 s window; do not reintroduce fixed-packet or retained BPM display |
| 2 | Guitar visual primary row | 69 / 346 (19.9%); GuitarSet, EGFXSet, GAPS isolated, and GAPS full route scans found no zero-side-effect selector across 7,765 protected guitar rows. A focused cross-family visual-row scan likewise found no actionable Guitar correction; its closest rule incurred 49 side-effect rows. IDMT-SMT-Guitar supplies 2,173 independently labelled real electric-guitar clips as an expected-row regression gate | 6 / 6 (100.0%) selector/corpus checks run; 277 / 346 (80.1%) GuitarSet rows still miss the visual primary target | mine a selector that retains GuitarSet/GAPS primary results and IDMT expected-row integrity rather than tuning to one guitar source | preserve all current correct GuitarSet primary rows and every protected Guitar/other ownership row |
| 3 | Current-note Vocal display | Latest visible SATB Vocal routing: CSD 35 / 576 (6.1%), DCS 61 / 984 (6.2%), ESMUC 82 / 902 (9.1%). The final-display mirror recovers 3 / 3 high-confidence ambiguous notes (CSD 1, ESMUC 2) with 0 protected reroutes. The prior high-soprano Keyboard-to-Vocal mirror is disabled after it activated 9 protected non-vocal rows; the cached cross-domain miner has 0 actionable / 14 coverage-blocked routes | 2 / 2 (100.0%) broader-recovery and protected-replay checks run; 2284 / 2462 (92.8%) SATB notes are not visibly routed | seek a causal feature that recovers more than this replicated three-window subset with zero protected displays | retain the ambiguous Vocal mirror and all protected Keyboard/Guitar/Other rows |
| 4 | Ride/Rim primary ownership | 29k Ride primary 324 / 500 (64.8%); the 500-sample cross-kit replay has 379 / 500 (75.8%) Ride recall and 1 false positive. Three independently credited isolated Rim clips reproduce 0 / 3 Rim primary and 3 / 3 Snare primary; Virtuosity Rim is 5 / 28 (17.9%), independent 0x808 Rim is 2 / 7 (28.6%), CC0 Unruly Rimshot is 16 / 96 (16.7%), and licence-confirmed ENST dry-mix Rim is 2 / 3 (66.7%). The checksum-pinned E-GMD archive transfer is active at 89.8 GiB logical bytes; do not use it until final MD5 verification. Official DREANSS annotations are verified locally; matching BSS-Oracle/MASS/SiSEC source audio is deferred at user direction because it cannot be acquired automatically | 7 / 7 (100.0%) Ride and independent-Rim decision checks run; the Unruly cross-source candidate is rejected (8 repairs, 25 protected primary regressions, 29 foreign promotions) | derive a source-neutral Rim feature that improves acoustic and drum-machine labelled Rim sources before any rule; DREANSS audio remains optional replication | retain all protected Tom/Snare/HiHat primary hits and the 29k Ride primary results |
| 5 | Primary chord display | 317 / 1415 (22.4%) after the safe same-root dim7 promotion. GAPS has 12 local zero-regression reorder predicates, while Guitar Chord Mix has 0; score-based promotions create protected false labels. Suppressing speculative post-stabilization global extensions removes 4 regression failures | 2 / 2 (100.0%) primary-order corpus audits run; 1098 / 1415 (77.6%) primary labels remain wrong or absent | keep source-neutral ordering and the safe same-root dim7 promotion | preserve the later-alias successes and the safe same-root dim7 promotion |
| 6 | OBS idle HiHat false activity | 4 / 4 (100.0%) steady multi-tone treble floors now suppress persistent HiHat, including decay from an active HiHat state; generic false-activity scan found 0 broad safe suppressions | 2 / 2 (100.0%) synthetic steady-state and decay audits run; 0 / 1 (0.0%) representative OBS captures replayed | deferred at user direction: replay requires a user-provided silent/high-treble OBS capture | preserve early-onset HiHat gains in MDB and BabySlakh |
| 7 | SATB exact-MIDI recall | 653 / 902 (72.4%) ESMUC notes; causal Basic Pitch has 8 CSD+ESMUC Vocal recoveries / 0 false overlays at 0.80: native Guitar with keyboard score ≥0.1817, or native Keyboard with guitar score ≥0.2059. Newly created and previously unset filters enable the bounded non-blocking worker when installed module data is available; an explicit filter opt-out remains available | 249 / 902 (27.6%) still unrecovered by the live detector | deployed offline evidence is complete; user-provided OBS capture replay is deferred at user direction | retain precision in DCS, CSD, ESMUC, MusicNet, and GuitarSet; candidate capacity, floor/raw-energy, harmonic-product, and relative-chroma trials found no safe selector |

## Runtime OTHERS output

The catch-all OTHERS detector and renderer are intentionally disabled. Its historical rows remain below as baseline evidence only; they are not active runtime output.

| Work item | Complete / total | Remaining |
| --- | ---: | ---: |
| Disable OTHERS detection and rendering | 1 / 1 (100.0%) | 0 |

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Any detected note | 2212 / 2212 (100.0%) | 0 |
| Expected instrument row | 2212 / 2212 (100.0%) | 0 |
| Lit expected pitch class | 2020 / 2212 (91.3%) | 192 |
| Primary display row | 765 / 2212 (34.6%) | 1447 |
| Visual primary row | 894 / 2212 (40.4%) | 1318 |
| Bass — Any detected note | 137 / 137 (100.0%) | 0 |
| Bass — Expected instrument row | 137 / 137 (100.0%) | 0 |
| Bass — Lit expected pitch class | 137 / 137 (100.0%) | 0 |
| Bass — Primary display row | 45 / 137 (32.8%) | 92 |
| Bass — Visual primary row | 49 / 137 (35.8%) | 88 |
| Guitar — Any detected note | 346 / 346 (100.0%) | 0 |
| Guitar — Expected instrument row | 346 / 346 (100.0%) | 0 |
| Guitar — Lit expected pitch class | 289 / 346 (83.5%) | 57 |
| Guitar — Primary display row | 150 / 346 (43.4%) | 196 |
| Guitar — Visual primary row | 60 / 346 (17.3%) | 286 |
| Other — Any detected note | 590 / 590 (100.0%) | 0 |
| Other — Expected instrument row | 590 / 590 (100.0%) | 0 |
| Other — Lit expected pitch class | 519 / 590 (88.0%) | 71 |
| Other — Primary display row | 122 / 590 (20.7%) | 468 |
| Other — Visual primary row | 220 / 590 (37.3%) | 370 |
| Piano — Any detected note | 1117 / 1117 (100.0%) | 0 |
| Piano — Expected instrument row | 1117 / 1117 (100.0%) | 0 |
| Piano — Lit expected pitch class | 1054 / 1117 (94.4%) | 63 |
| Piano — Primary display row | 441 / 1117 (39.5%) | 676 |
| Piano — Visual primary row | 559 / 1117 (50.0%) | 558 |
| Vocals — Any detected note | 22 / 22 (100.0%) | 0 |
| Vocals — Expected instrument row | 22 / 22 (100.0%) | 0 |
| Vocals — Lit expected pitch class | 21 / 22 (95.5%) | 1 |
| Vocals — Primary display row | 7 / 22 (31.8%) | 15 |
| Vocals — Visual primary row | 6 / 22 (27.3%) | 16 |

## SATB multi-pitch candidate-capacity audit

The full-mix extractor considers up to 24 independently scored pitch candidates. This audit checks whether that cap, rather than pitch scoring, truncated labelled SATB windows.

Source: `build/polyphonic_candidate_capacity_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| SATB corpora reaching the 24-candidate cap | 0 / 3 (0.0%) | 3 |
| Missing pitch-class windows explained by capacity | 0 / 427 (0.0%) | 427 |
| 4% full-mix candidate-floor trial safe across SATB corpora | 0 / 1 (0.0%) | 1 |
| 18% raw-fundamental supplement safe across SATB corpora and GuitarSet | 0 / 1 (0.0%) | 1 |
| Raw missing-pitch energy separates labelled tones from extras | 0 / 1 (0.0%) | 1 |
| 45% complex-harmonic tuning fallback safe across SATB corpora | 0 / 1 (0.0%) | 1 |

No SATB corpus reaches the cap, so expanding candidate capacity is not an evidence-based recall fix. The 4% floor trial reduced visible vocal routing in the prepared SATB fixtures, so the 8% floor is retained. The 18% raw-fundamental supplement raised exact chords from DCS/CSD/ESMUC 39/45/67 to 39/46/69, but reduced note precision in every corpus and produced only 398/511 GuitarSet primary chord hits against the 400-hit guard, so it is removed. At the same 18% raw-energy floor, labelled missing pitch classes are only 77/325 DCS, 60/171 CSD, and 50/260 ESMUC, versus 429/512, 385/433, and 811/897 unlabelled extras; raw energy cannot safely distinguish them. Raising only complex-harmonic fallback scale from 38% to 45% improved exact chords to 40/45/69, but reduced note precision from 57.67%/52.01%/45.25% to 57.43%/51.65%/45.24%, so the 38% scale is retained.

## Harmonic-product octave-correction audit

Each full-mix candidate now exports a geometric direct/2x/3x/4x support score and the lower-subharmonic ratio before row routing. The audit treats an upper-octave-only candidate as a possible recovery and every labelled direct candidate as protected.

Source: `build/harmonic_product_octave_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Zero-regression harmonic-product thresholds across all SATB corpora | 0 / 6 (0.0%) | 6 |
| Independently labelled SATB corpora audited | 3 / 3 (100.0%) | 0 |
| Runtime harmonic-product octave correction eligible | 0 / 1 (0.0%) | 1 |

Every tested threshold—and every compact pairing with pitch confidence, periodicity, fit error, or noise—still moves at least one labelled correct pitch downward, so harmonic-product evidence remains diagnostic and no pre-routing correction is enabled.

## SATB relative-chroma recovery audit

This selector normalizes a missing pitch class's raw chroma by the strongest raw-chroma class in the same frame. It is eligible only when one threshold recovers a missing class while creating no extra pitch classes in every corpus.

Source: `build/satb_relative_chroma_selector_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Zero-extra relative-chroma thresholds across SATB corpora | 0 / 9 (0.0%) | 9 |
| Independently labelled SATB corpora audited | 3 / 3 (100.0%) | 0 |
| Runtime relative-chroma recovery eligible | 0 / 1 (0.0%) | 1 |

All nine relative thresholds still promote extras in every corpus, so relative raw chroma is diagnostic only and no recovery is enabled.

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
| Corpora with a zero-regression dominant-seventh gain | 1 / 4 (25.0%) | 3 |
| Runtime dominant-seventh extension eligible | 0 / 1 (0.0%) | 1 |

The cached sweep found 0 regression(s), so the extension is rejected.

## Global chord confidence calibration audit

The chord label is assessed separately from the Bass and Vocal current-note displays. A higher display threshold is eligible only if it suppresses wrong labels without hiding a correct label in every confidence-capable corpus.

Source: `build/global_chord_confidence_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Corpora with zero-regression suppression at best floor (0.45) | 2 / 4 (50.0%) | 2 |
| Common zero-regression confidence floor found | 0 / 1 (0.0%) | 1 |
| Runtime global-chord confidence gate eligible | 0 / 1 (0.0%) | 1 |

No common zero-regression threshold was found, so the current chord display gate is retained.

## Expanded live GuitarSet baseline

GuitarSet contributes microphone-recorded live guitar with note and chord annotations. It is independent evidence for polyphonic guitar changes; this is a baseline, not a gate relaxation.

Source: `build/guitarset_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar pitch-class recall | 4449 / 5451 (81.6%) | 1002 |
| Exact guitar chord recall | 1143 / 1491 (76.7%) | 348 |

## Independent isolated Guitar visual-primary baselines

These independently labelled isolated-guitar corpora measure whether the exact annotated note is visible in the Guitar row. They are regression baselines, not a justification to relax GuitarSet full-mix routing.

| Source | Exact Guitar visual buffers | Remaining | Exact Guitar visual samples | Remaining |
| --- | ---: | ---: | ---: | ---: |
| Guitar-TECHS | 3252 / 3789 (85.8%) | 537 | 547 / 547 (100.0%) | 0 |
| IDMT Guitar | 8987 / 11095 (81.0%) | 2108 | 2168 / 2173 (99.8%) | 5 |

## AG-PT independent guitar expected-note baseline

AG-PT provides independently labelled, real electric-guitar technique recordings. This expected exact-MIDI note result is a regression guard for future Guitar visual-row changes; it is not a substitute for the separate GuitarSet visual-primary metric.

Source: `build/agpt_guitar_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| AG-PT expected exact-MIDI guitar note | 1963 / 2000 (98.2%) | 37 |
| AG-PT Guitar visual primary row — buffer | 2129 / 12540 (17.0%) | 10411 |
| AG-PT Guitar visual primary row — sample | 348 / 2000 (17.4%) | 1652 |
| AG-PT expected exact note on Guitar visual primary — buffer | 1203 / 12540 (9.6%) | 11337 |
| AG-PT expected exact note on Guitar visual primary — sample | 298 / 2000 (14.9%) | 1702 |

Visual-primary source: `build/agpt_guitar_visual_primary.tsv`. These rows are a new independent regression gate; they demonstrate broad Piano/Bass visual confusion and do not justify a Guitar selector change by themselves.

### AG-PT visual-row selector veto

Source: `build/agpt_guitar_visual_pattern_report.txt`. The exhaustive search evaluates all 8 observed AG-PT Guitar visual-row confusions against all protected real-note rows.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Visual-row confusion buckets with a zero-side-effect selector | 0 / 8 (0.0%) | 8 |
| Missed AG-PT samples covered by a safe selector | 0 / 1613 (0.0%) | 1613 |

No mined selector is eligible: retain current Guitar routing and seek different features or a model.

## Cross-corpus same-root guitar-quality audit

A same-root power chord may be promoted to a measured major/minor quality only when raw third evidence improves a missed label without regressing any correct label.

Source: `build/same_root_guitar_quality_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Corpora with a zero-regression same-root quality gain | 0 / 4 (0.0%) | 4 |
| Runtime same-root quality promotion eligible | 0 / 1 (0.0%) | 1 |

The best tested raw-third floor (0.040) still has 173 regression(s), so the promotion is rejected.

## Cross-corpus temporal chord-primary veto

Source: `build/cross_corpus_guitar_primary_order_audit.txt`. Each direction treats the other labelled corpus as protected before a temporal candidate can be considered.

| Focus corpus | Candidate repairs | Focus regressions | Protected-corpus regressions |
| --- | ---: | ---: | ---: |
| Guitar Chord Mix | 3 | 20 | 1068 |
| GAPS | 4 | 44 | 1044 |
| Guitar-TECHS | 29 | 1024 | 64 |

The current onset/hold-style promotion has no shared zero-regression rule, so the chord-primary implementation remains unchanged.

## Owner-classifier leave-one-corpus-out audit

A small nearest-centroid classifier is evaluated from the analyzer's existing owner scores, with every corpus held out in turn. It is an offline calibration experiment, not a runtime model.

Source: `build/owner_classifier_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current owner | 4 / 9 (44.4%) | 5 |
| Aggregate current-owner accuracy | 13067 / 65601 (19.9%) | 52534 |
| Aggregate centroid-model accuracy | 11325 / 65601 (17.3%) | 54276 |
| Runtime owner classifier eligible | 0 / 1 (0.0%) | 1 |

The model is retained only as an offline baseline because it regresses at least one held-out corpus.

## Extended owner-classifier leave-one-corpus-out audit

This offline nearest-centroid experiment adds pitch confidence, periodicity, harmonic shape, local noise, and adjacent-pitch features to the owner-score baseline. It remains a diagnostic model until it improves every held-out corpus.

Source: `build/owner_classifier_quality_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current owner | 8 / 9 (88.9%) | 1 |
| Aggregate current-owner accuracy | 13067 / 65601 (19.9%) | 52534 |
| Aggregate quality-model accuracy | 17394 / 65601 (26.5%) | 48207 |
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

## Drum-primary leave-one-corpus-out classifier audit

A normalized nearest-centroid classifier is trained from the other drum corpora's existing detector evidence and evaluated on one held-out corpus at a time. It is diagnostic-only and cannot change runtime selection unless every held-out corpus improves.

Source: `build/drum_primary_loco_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| LOCO corpora improved over current primary detector | 0 / 3 (0.0%) | 3 |
| Aggregate current-primary accuracy | 18952 / 22681 (83.6%) | 3729 |
| Aggregate classifier accuracy | 14188 / 22681 (62.6%) | 8493 |
| Runtime drum classifier eligible | 0 / 1 (0.0%) | 1 |

The experiment is rejected: held-out classification regresses (tom=-2077 ride=-276 rim=-299) instead of improving the protected Tom/Ride/Rim classes.

## Cross-real drum false-positive cap audit

This replays each simple cap that suppresses a false drum window in both MDB and STAR against protected one-shot primary rows. A cap is runtime-safe only when every required detector feature is available and no correct protected primary hit is removed.

Source: `build/drum_false_positive_cap_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Non-dominated real-mix false-positive cap candidates | 0 / 0 (0.0%) | 0 |
| Cross-real candidates safe on protected one-shot primaries | 0 / 0 (0.0%) | 0 |
| Runtime false-positive cap eligible | 0 / 1 (0.0%) | 1 |

No simple cross-real cap remains after the qualified Ride energy-context guard.

## MDB full-mix drum false-positive cap audit

This probes every non-dominated simple cap that suppresses a false window in the annotated MDB full mixes, then replays it against protected one-shot primary hits.

Source: `build/mdb_full_mix_false_positive_cap_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MDB full-mix false-positive caps examined | 0 / 0 (0.0%) | 0 |
| MDB caps safe on protected one-shot primaries | 0 / 0 (0.0%) | 0 |
| MDB full-mix runtime cap eligible | 0 / 1 (0.0%) | 1 |

No MDB-only simple cap is eligible: every candidate that suppresses a full-mix false positive also removes a protected correct primary hit.

## Cross-real competing-drum context audit

This searches source-scoped class-aware suppression contexts across the annotated MDB and STAR full mixes. Each candidate must preserve annotated target events and every protected one-shot primary row.

Source: `build/mdb_full_mix_competing_active_context_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Remaining competing-drum contexts examined | 3 / 3 (100.0%) | 0 |
| Remaining contexts safe for an isolated runtime experiment | 1 / 3 (33.3%) | 2 |
| Protected-safe contexts replayed through runtime detector | 1 / 1 (100.0%) | 0 |
| Replayed contexts with a verified runtime gain | 0 / 1 (0.0%) | 1 |
| Further source-scoped context work available | 0 / 1 (0.0%) | 1 |

Every currently eligible context was replayed without a verified overall gain; do not enable it.

## Two-feature cross-real drum false-positive context audit

This bounded search combines two detector features for a single active drum category. It requires a false suppression in both MDB and STAR, no annotated real-mix event loss, and then replays each context against every protected one-shot primary row.

Source: `build/drum_false_positive_context_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Zero-true source primitives considered | 30 / 30 (100.0%) | 0 |
| Cross-real two-feature contexts | 0 / 30 (0.0%) | 30 |
| Protected one-shot runtime-safe contexts | 0 / 0 (0.0%) | 0 |
| Remaining runtime context eligible | 0 / 1 (0.0%) | 1 |

The current Ride high/low-energy guard removed the two previously qualified false windows; no additional two-feature context remains.

## Cross-real drum recovery-candidate audit

A recovery shape must add an inactive annotated class in both MDB and STAR while matching no window where that class is unannotated. Candidates remain diagnostic until a rebuilt MDB, STAR, BabySlakh, and protected one-shot replay confirms an overall gain.

Source: `build/drum_recovery_candidate_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Missed annotated events searched across real corpora | 70 / 70 (100.0%) | 0 |
| Independent real corpora represented | 2 / 2 (100.0%) | 0 |
| Zero-false cross-real recovery shapes replayed through runtime gates | 0 / 0 (0.0%) | 0 |
| Recovery shapes with a verified overall runtime gain | 1 / 1 (100.0%) | 0 |

One recovery shape is retained: early-onset HiHat adds true events in MDB and BabySlakh without a false-positive regression, while STAR remains unchanged. Its non-named-source idle-treble guard keeps a settled OBS mix from lighting HiHat without suppressing corroborated transient or named-drum events. The other two shapes are rejected.

| Runtime trial | MDB true / false | STAR true / false | BabySlakh true / false | Decision |
| --- | ---: | ---: | ---: | --- |
| Early Snare onset | 139→140 / 28→28 | 39→40 / 0→0 | 140→140 / 38→39 | reject: BabySlakh precision 78.7%→78.2% |
| Low-transient HiHat | 139→140 / 28→28 | 39→39 / 0→0 | 140→140 / 38→38 | reject: no STAR or BabySlakh gain |
| Early-onset HiHat | 139→142 / 28→28 | 39→39 / 0→0 | 140→142 / 38→38 | retain: +3 MDB and +2 BabySlakh true hits, no false-positive increase |

## Canonical-first chord display audit

The proposed compact display would keep only the first component of a multi-alias keyboard chord. MAPS and independently recorded MAESTRO determine whether that visual simplification preserves correct labelled chords.

Source: `build/chord_primary_component_audit.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Correct chords with any displayed alias | 312 / 1415 (22.0%) | 1103 |
| Correct chords with only the first displayed component | 310 / 1415 (21.9%) | 1105 |
| Correct chords rescued only by a later alias | 2 / 312 (0.6%) | 310 |
| Canonical-first runtime display eligible | 0 / 1 (0.0%) | 1 |
| Correct chords after same-root dim7 promotion | 312 / 1415 (22.0%) | 1103 |
| Same-root dim7 runtime promotions observed | 1 / 1415 (0.1%) | 1414 |
| Known correct-primary labels lost by promotion | 0 / 1415 (0.0%) | 0 |
| Same-root dim7 runtime display eligible | 1 / 1 (100.0%) | 0 |

Canonical-first display is rejected: later aliases account for correct labelled outcomes in both piano corpora. The narrower same-root dim7 promotion remains eligible only when it restores every known alias hit without losing a known first-label hit.

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
| Guitar Chord Mix primary displayed chord | 398 / 511 (77.9%) | 113 |
| GAPS full-performance primary displayed chord | 176 / 540 (32.6%) | 364 |
| Corpora with any zero-regression local reorder rule | 1 / 2 (50.0%) | 1 |
| Shared runtime display change eligible | 0 / 1 (0.0%) | 1 |

GAPS has 12 local zero-regression rule candidates, but Guitar Chord Mix has 0; no shared rule exists, so no runtime reorder is permitted.

## Offline Basic Pitch ONNX fusion feasibility

The optional C++ path is replayed against score-aligned DCS, CSD, and ESMUC mixtures. It is offline-only evidence, not a runtime dependency or enabled detector.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Choir corpora represented | 3 / 3 (100.0%) | 0 |
| Native C API model-load and tensor-shape probe | 1 / 1 (100.0%) | 0 |
| C++ runtime output-buffer wrapper | 1 / 1 (100.0%) | 0 |
| Causal 250 ms-lookahead decoder | 1 / 1 (100.0%) | 0 |
| C++ A4 signal → inference → causal decoder | 1 / 1 (100.0%) | 0 |
| Background inference worker | 1 / 1 (100.0%) | 0 |
| Causal PCM-history sampler | 1 / 1 (100.0%) | 0 |
| C++ true-miss replay available | 1 / 1 (100.0%) | 0 |
| Full choir replay available | 1 / 1 (100.0%) | 0 |
| High-confidence choir replay available | 1 / 1 (100.0%) | 0 |
| Cross-domain zero-false replay available | 1 / 1 (100.0%) | 0 |
| Cross-domain worker-delivery replay available | 1 / 1 (100.0%) | 0 |

The official ONNX model is 230 KB; the optional C++ probe dynamically loads the official 10.5 MB runtime and emits the expected 1x172x88 note/onset and 1x172x264 contour tensors. Its C++ causal path also recovers an A4 sine (0.604 confidence, above the 0.30 threshold).

### C++ causal true-miss replay

At threshold 0.30, the replay selects 12 native-miss windows from each choir corpus.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Native active expected MIDI set | 88 / 144 (61.1%) | 56 |
| Native + ONNX active expected MIDI set | 113 / 144 (78.5%) | 31 |
| Novel ONNX notes that were correct | 25 / 32 (78.1%) | 7 false |

### Full C++ choir false-positive veto

At threshold 0.30, all 204 selected score-aligned choir windows are replayed.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Native active expected MIDI set | 664 / 838 (79.2%) | 174 |
| Native + ONNX active expected MIDI set | 726 / 838 (86.6%) | 112 |
| Novel ONNX notes that were correct | 62 / 91 (68.1%) | 29 false |

### High-confidence C++ choir safety point

At threshold 0.70, fusion recovers 4 exact notes with 0 labelled false additions across 204 windows. This choir-only result does not authorize runtime fusion; a non-choir veto and integrated replay remain required.

### Cross-domain strict C++ safety point

At threshold 0.80, DCS/CSD/ESMUC plus real-mixture MusicNet recover 38 labelled exact notes with 1 labelled false additions across 820 windows. The legacy sequential mode replays only the native analyzer; it does not invoke the ONNX worker and therefore cannot validate delivery. No runtime fusion is enabled.

### Cross-domain zero-false C++ safety point

At threshold 0.85, DCS/CSD/ESMUC plus real-mixture MusicNet recover 3 labelled exact notes with 0 labelled false additions across 820 windows. The worker-delivery replay matches this result after sequence-bound waiting; live runtime fusion still needs a separate non-blocking analyzer integration and full detector regression replay.

## High-soprano octave safety audit

A high F5/F#5 vocal recovery is only eligible if it improves at least two independent choir corpora with no protected-instrument reroutes. The lower-octave gate selects protected keyboard candidates; direct rerouting is therefore rejected. A separately validated mirror may preserve that keyboard candidate while exposing the same note on the Vocal row.

Source: `build/high_vocal_octave_evidence.txt`

high-vocal octave safety audit: midi=77,78
| Lower-octave ratio cap | DCS candidates | CSD candidates | ESMUC candidates | Corpora with candidates | Protected risks |
| --- | ---: | ---: | ---: | ---: | ---: |
| <= 0.05 | 4 / 6 | 0 / 0 | 1 / 2 | 2 / 3 | 114 / 123 |
| <= 0.10 | 5 / 6 | 0 / 0 | 1 / 2 | 2 / 3 | 115 / 123 |
| <= 0.20 | 5 / 6 | 0 / 0 | 1 / 2 | 2 / 3 | 121 / 123 |
| <= 0.35 | 6 / 6 | 0 / 0 | 2 / 2 | 2 / 3 | 122 / 123 |
| <= 0.50 | 6 / 6 | 0 / 0 | 2 / 2 | 2 / 3 | 122 / 123 |
| <= 0.75 | 6 / 6 | 0 / 0 | 2 / 2 | 2 / 3 | 122 / 123 |
| <= 1.00 | 6 / 6 | 0 / 0 | 2 / 2 | 2 / 3 | 123 / 123 |

| Multi-signal route profile | DCS candidates | CSD candidates | ESMUC candidates | Corpora with candidates | Protected risks |
| --- | ---: | ---: | ---: | ---: | ---: |
| upper-adjacent >= 0.053; centroid 0.013..0.116 | 4 / 6 | 0 / 0 | 0 / 2 | 1 / 3 | 0 / 123 |

## Rejected high-soprano Vocal mirror

The F5/F#5 Keyboard-to-Vocal mirror is retained only as disabled replay code. The broader cached full-mix audit found its `noise >= 0.024`, second-partial `>= 0.114` profile on 9 protected non-vocal rows, including string, brass, and reed content. The live flag is therefore false.
Source: `build/high_soprano_vocal_mirror_audit.txt`.
A separate final-display mirror retains the original ambiguous classifier result but exposes the active MIDI on Vocal for the audited `owner=amb`, `confidence >= 0.785`, `other_score=1.0` profile: 1 CSD and 2 ESMUC rows, with 0 protected reroutes.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS profiled high-soprano expected Vocal candidates | 9 / 11 (81.8%) | 2 |
| ESMUC profiled high-soprano expected Vocal candidates | 5 / 6 (83.3%) | 1 |
| Independent choir corpora with candidate evidence | 2 / 2 (100.0%) | 0 |
| Protected non-vocal rows activated by broad mirror | 0 / 9 (0.0%) | 9 |
| Ambiguous choir Vocal display mirror | 3 / 3 (100.0%) | 0 | CSD 1 / 1; ESMUC 2 / 2; 0 protected reroutes |

The candidate evidence is not a live routing recovery: high notes are especially likely to be harmonics of non-vocal instruments, so a safe future rule must pass the full protected replay rather than only choir windows.

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
| Verify the high-soprano recovery safety gate | 1 / 1 (100.0%) | 0 | broad F5/F#5 Vocal mirror rejected: it activates 9 protected non-vocal rows; only the separately audited 3 / 3 ambiguous display mirror remains live |

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
| CSD All CSD chord windows — Exact chord accuracy | 8 / 144 (5.6%) | 136 |
| CSD All CSD chord windows — Simplified chord accuracy | 53 / 144 (36.8%) | 91 |
| CSD All CSD vocal windows — Current-note vocal ownership | 70 / 144 (48.6%) | 74 |
| CSD All CSD vocal windows — Visible current-note vocal routing | 34 / 144 (23.6%) | 110 |
| CSD All SATB notes — Exact-MIDI recall | 368 / 576 (63.9%) | 208 |
| CSD All SATB notes — Pitch-class recall | 465 / 576 (80.7%) | 111 |
| CSD All SATB notes — Visible vocal routing | 35 / 576 (6.1%) | 541 |
| CSD All SATB notes — Vocal ownership | 82 / 576 (14.2%) | 494 |

### CSD SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD SATB range — Alto — Exact-MIDI recall | 104 / 144 (72.2%) | 40 |
| CSD SATB range — Alto — Pitch-class recall | 119 / 144 (82.6%) | 25 |
| CSD SATB range — Alto — Visible vocal routing | 15 / 144 (10.4%) | 129 |
| CSD SATB range — Alto — Vocal ownership | 39 / 144 (27.1%) | 105 |
| CSD SATB range — Bass — Exact-MIDI recall | 70 / 144 (48.6%) | 74 |
| CSD SATB range — Bass — Pitch-class recall | 106 / 144 (73.6%) | 38 |
| CSD SATB range — Bass — Visible vocal routing | 4 / 144 (2.8%) | 140 |
| CSD SATB range — Bass — Vocal ownership | 9 / 144 (6.2%) | 135 |
| CSD SATB range — Soprano — Exact-MIDI recall | 97 / 144 (67.4%) | 47 |
| CSD SATB range — Soprano — Pitch-class recall | 116 / 144 (80.6%) | 28 |
| CSD SATB range — Soprano — Visible vocal routing | 10 / 144 (6.9%) | 134 |
| CSD SATB range — Soprano — Vocal ownership | 15 / 144 (10.4%) | 129 |
| CSD SATB range — Tenor — Exact-MIDI recall | 97 / 144 (67.4%) | 47 |
| CSD SATB range — Tenor — Pitch-class recall | 124 / 144 (86.1%) | 20 |
| CSD SATB range — Tenor — Visible vocal routing | 6 / 144 (4.2%) | 138 |
| CSD SATB range — Tenor — Vocal ownership | 19 / 144 (13.2%) | 125 |

### CSD recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| CSD Configuration — CSD_ER_Singer1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_ER_Singer1 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_ER_Singer1 — Exact-MIDI recall | 26 / 48 (54.2%) | 22 |
| CSD Configuration — CSD_ER_Singer1 — Pitch-class recall | 30 / 48 (62.5%) | 18 |
| CSD Configuration — CSD_ER_Singer1 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_ER_Singer1 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| CSD Configuration — CSD_ER_Singer2 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer2 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_ER_Singer2 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| CSD Configuration — CSD_ER_Singer2 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ER_Singer2 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ER_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer2 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| CSD Configuration — CSD_ER_Singer3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer3 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_ER_Singer3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_ER_Singer3 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_ER_Singer3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ER_Singer3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ER_Singer3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ER_Singer3 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ER_Singer4 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_ER_Singer4 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_ER_Singer4 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| CSD Configuration — CSD_ER_Singer4 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ER_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ER_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ER_Singer4 — Vocal ownership | 12 / 48 (25.0%) | 36 |
| CSD Configuration — CSD_LI_Singer1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer1 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_LI_Singer1 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_LI_Singer1 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| CSD Configuration — CSD_LI_Singer1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_LI_Singer1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_LI_Singer1 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_LI_Singer2 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_LI_Singer2 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_LI_Singer2 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| CSD Configuration — CSD_LI_Singer2 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| CSD Configuration — CSD_LI_Singer2 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer2 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_LI_Singer2 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| CSD Configuration — CSD_LI_Singer2 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| CSD Configuration — CSD_LI_Singer3 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer3 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_LI_Singer3 — Exact-MIDI recall | 37 / 48 (77.1%) | 11 |
| CSD Configuration — CSD_LI_Singer3 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_LI_Singer3 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_LI_Singer3 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_LI_Singer3 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| CSD Configuration — CSD_LI_Singer3 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_LI_Singer4 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer4 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| CSD Configuration — CSD_LI_Singer4 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| CSD Configuration — CSD_LI_Singer4 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_LI_Singer4 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_LI_Singer4 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_LI_Singer4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_LI_Singer4 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ND_Singer1 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| CSD Configuration — CSD_ND_Singer1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| CSD Configuration — CSD_ND_Singer1 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| CSD Configuration — CSD_ND_Singer1 — Pitch-class recall | 44 / 48 (91.7%) | 4 |
| CSD Configuration — CSD_ND_Singer1 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer1 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer1 — Visible vocal routing | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ND_Singer1 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| CSD Configuration — CSD_ND_Singer2 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| CSD Configuration — CSD_ND_Singer2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer2 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| CSD Configuration — CSD_ND_Singer2 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_ND_Singer2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| CSD Configuration — CSD_ND_Singer2 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer2 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ND_Singer2 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| CSD Configuration — CSD_ND_Singer3 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| CSD Configuration — CSD_ND_Singer3 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer3 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| CSD Configuration — CSD_ND_Singer3 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| CSD Configuration — CSD_ND_Singer3 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| CSD Configuration — CSD_ND_Singer3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| CSD Configuration — CSD_ND_Singer3 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| CSD Configuration — CSD_ND_Singer4 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| CSD Configuration — CSD_ND_Singer4 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| CSD Configuration — CSD_ND_Singer4 — Exact-MIDI recall | 27 / 48 (56.2%) | 21 |
| CSD Configuration — CSD_ND_Singer4 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| CSD Configuration — CSD_ND_Singer4 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
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
| Verify the high-soprano recovery safety gate | 1 / 1 (100.0%) | 0 | broad F5/F#5 Vocal mirror rejected: it activates 9 protected non-vocal rows; only the separately audited 3 / 3 ambiguous display mirror remains live |

## ESMUC Choir Dataset real-audio measurement

Each recording is a real synchronised four-source SATB mix. Current-note routing is credited when the monophonic vocal display matches any concurrent SATB score pitch.

Source: `build/esmuc_choir_dataset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC All ESMUC chord windows — Exact chord accuracy | 43 / 218 (19.7%) | 175 |
| ESMUC All ESMUC chord windows — Simplified chord accuracy | 68 / 218 (31.2%) | 150 |
| ESMUC All ESMUC vocal windows — Current-note vocal ownership | 140 / 228 (61.4%) | 88 |
| ESMUC All ESMUC vocal windows — Visible current-note vocal routing | 70 / 228 (30.7%) | 158 |
| ESMUC All SATB notes — Exact-MIDI recall | 653 / 902 (72.4%) | 249 |
| ESMUC All SATB notes — Pitch-class recall | 767 / 902 (85.0%) | 135 |
| ESMUC All SATB notes — Visible vocal routing | 82 / 902 (9.1%) | 820 |
| ESMUC All SATB notes — Vocal ownership | 167 / 902 (18.5%) | 735 |

### ESMUC SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC SATB range — Alto — Exact-MIDI recall | 170 / 228 (74.6%) | 58 |
| ESMUC SATB range — Alto — Pitch-class recall | 195 / 228 (85.5%) | 33 |
| ESMUC SATB range — Alto — Visible vocal routing | 33 / 228 (14.5%) | 195 |
| ESMUC SATB range — Alto — Vocal ownership | 43 / 228 (18.9%) | 185 |
| ESMUC SATB range — Bass — Exact-MIDI recall | 182 / 228 (79.8%) | 46 |
| ESMUC SATB range — Bass — Pitch-class recall | 207 / 228 (90.8%) | 21 |
| ESMUC SATB range — Bass — Visible vocal routing | 20 / 228 (8.8%) | 208 |
| ESMUC SATB range — Bass — Vocal ownership | 50 / 228 (21.9%) | 178 |
| ESMUC SATB range — Soprano — Exact-MIDI recall | 131 / 218 (60.1%) | 87 |
| ESMUC SATB range — Soprano — Pitch-class recall | 168 / 218 (77.1%) | 50 |
| ESMUC SATB range — Soprano — Visible vocal routing | 17 / 218 (7.8%) | 201 |
| ESMUC SATB range — Soprano — Vocal ownership | 28 / 218 (12.8%) | 190 |
| ESMUC SATB range — Tenor — Exact-MIDI recall | 170 / 228 (74.6%) | 58 |
| ESMUC SATB range — Tenor — Pitch-class recall | 197 / 228 (86.4%) | 31 |
| ESMUC SATB range — Tenor — Visible vocal routing | 12 / 228 (5.3%) | 216 |
| ESMUC SATB range — Tenor — Vocal ownership | 46 / 228 (20.2%) | 182 |

### ESMUC recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Exact-MIDI recall | 31 / 48 (64.6%) | 17 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Pitch-class recall | 41 / 48 (85.4%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Visible vocal routing | 6 / 48 (12.5%) | 42 |
| ESMUC Configuration — ESMUC_DG_FT_take1 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_FT_take2 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Exact-MIDI recall | 32 / 48 (66.7%) | 16 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Pitch-class recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DG_FT_take3 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible current-note vocal routing | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Visible vocal routing | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_DG_FT_take4 — Vocal ownership | 14 / 48 (29.2%) | 34 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact chord accuracy | 4 / 10 (40.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Exact-MIDI recall | 37 / 48 (77.1%) | 11 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Pitch-class recall | 46 / 48 (95.8%) | 2 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Simplified chord accuracy | 4 / 10 (40.0%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DG_SE_short2 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
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
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Exact-MIDI recall | 30 / 48 (62.5%) | 18 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_DG_SE_short4 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Exact-MIDI recall | 39 / 48 (81.2%) | 9 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Pitch-class recall | 45 / 48 (93.8%) | 3 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| ESMUC Configuration — ESMUC_DH1_FT_take1 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Exact-MIDI recall | 20 / 38 (52.6%) | 18 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Pitch-class recall | 28 / 38 (73.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Simplified chord accuracy | 0 / 4 (0.0%) | 4 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Visible vocal routing | 2 / 38 (5.3%) | 36 |
| ESMUC Configuration — ESMUC_DH1_SE_short1 — Vocal ownership | 5 / 38 (13.2%) | 33 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Exact-MIDI recall | 28 / 48 (58.3%) | 20 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_DH1_SE_short2 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Current-note vocal ownership | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Exact-MIDI recall | 33 / 48 (68.8%) | 15 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_DH2_FT_take1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_SC1_FT_take1 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_SC1_FT_take2 — Vocal ownership | 11 / 48 (22.9%) | 37 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Exact-MIDI recall | 35 / 48 (72.9%) | 13 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Pitch-class recall | 43 / 48 (89.6%) | 5 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_SC1_FT_take3 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Exact-MIDI recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_SC2_FT_take1 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Current-note vocal ownership | 10 / 12 (83.3%) | 2 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Exact-MIDI recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Pitch-class recall | 42 / 48 (87.5%) | 6 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC2_FT_take2 — Vocal ownership | 11 / 48 (22.9%) | 37 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Current-note vocal ownership | 8 / 12 (66.7%) | 4 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| ESMUC Configuration — ESMUC_SC2_FT_take3 — Vocal ownership | 10 / 48 (20.8%) | 38 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Current-note vocal ownership | 6 / 12 (50.0%) | 6 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Exact-MIDI recall | 38 / 48 (79.2%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| ESMUC Configuration — ESMUC_SC3_FT_take1 — Vocal ownership | 7 / 48 (14.6%) | 41 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact chord accuracy | 1 / 12 (8.3%) | 11 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Exact-MIDI recall | 33 / 48 (68.8%) | 15 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Visible vocal routing | 5 / 48 (10.4%) | 43 |
| ESMUC Configuration — ESMUC_SC3_FT_take2 — Vocal ownership | 8 / 48 (16.7%) | 40 |

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
| MIR-1K vocals — Expected instrument row | 239 / 300 (79.7%) | 61 |
| MIR-1K vocals — Lit expected pitch class | 126 / 300 (42.0%) | 174 |
| MIR-1K vocals — Primary display row | 50 / 300 (16.7%) | 250 |
| MIR-1K vocals — Visual primary row | 51 / 300 (17.0%) | 249 |
| MIR-1K vocals — Vocals — exact expected MIDI note | 193 / 300 (64.3%) | 107 |

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
| CSD — exact MIDI in vocal row | 69 / 576 (12.0%) | 507 |
| CSD — exact MIDI only in foreign row | 299 / 576 (51.9%) | 277 |
| CSD — pitch class only (wrong octave) | 97 / 576 (16.8%) | 479 |
| CSD — no expected pitch class | 111 / 576 (19.3%) | 465 |
| DCS — exact MIDI in vocal row | 80 / 984 (8.1%) | 904 |
| DCS — exact MIDI only in foreign row | 393 / 984 (39.9%) | 591 |
| DCS — pitch class only (wrong octave) | 246 / 984 (25.0%) | 738 |
| DCS — no expected pitch class | 265 / 984 (26.9%) | 719 |
| ESMUC — exact MIDI in vocal row | 114 / 902 (12.6%) | 788 |
| ESMUC — exact MIDI only in foreign row | 539 / 902 (59.8%) | 363 |
| ESMUC — pitch class only (wrong octave) | 114 / 902 (12.6%) | 788 |
| ESMUC — no expected pitch class | 135 / 902 (15.0%) | 767 |
| MIR1K — exact MIDI in vocal row | 647 / 2365 (27.4%) | 1718 |
| MIR1K — exact MIDI only in foreign row | 1147 / 2365 (48.5%) | 1218 |
| MIR1K — pitch class only (wrong octave) | 454 / 2365 (19.2%) | 1911 |
| MIR1K — no expected pitch class | 117 / 2365 (4.9%) | 2248 |
| SCMS — exact MIDI in vocal row | 1712 / 7095 (24.1%) | 5383 |
| SCMS — exact MIDI only in foreign row | 4040 / 7095 (56.9%) | 3055 |
| SCMS — pitch class only (wrong octave) | 673 / 7095 (9.5%) | 6422 |
| SCMS — no expected pitch class | 670 / 7095 (9.4%) | 6425 |
| Vocadito — exact MIDI in vocal row | 764 / 2316 (33.0%) | 1552 |
| Vocadito — exact MIDI only in foreign row | 1017 / 2316 (43.9%) | 1299 |
| Vocadito — pitch class only (wrong octave) | 303 / 2316 (13.1%) | 2013 |
| Vocadito — no expected pitch class | 232 / 2316 (10.0%) | 2084 |
| VocalSet — exact MIDI in vocal row | 3177 / 18039 (17.6%) | 14862 |
| VocalSet — exact MIDI only in foreign row | 9739 / 18039 (54.0%) | 8300 |
| VocalSet — pitch class only (wrong octave) | 2695 / 18039 (14.9%) | 15344 |
| VocalSet — no expected pitch class | 2428 / 18039 (13.5%) | 15611 |

## Dagstuhl ChoirSet (DCS) real-audio measurement

The SATB rows count every score-active singer at a stable center-of-note window in a real, summed four-singer recording. Vocal ownership and routing require the expected pitch class in the vocal row; visible routing additionally requires visual level at least 0.25. Current-note vocal rows are separate window-level metrics: because the UI is monophonic, they count success when its one displayed note matches any concurrent SATB score pitch.

Source: `build/dagstuhl_choirset_measurement.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS All DCS chord windows — Exact chord accuracy | 19 / 240 (7.9%) | 221 |
| DCS All DCS chord windows — Simplified chord accuracy | 63 / 240 (26.2%) | 177 |
| DCS All DCS vocal windows — Current-note vocal ownership | 90 / 240 (37.5%) | 150 |
| DCS All DCS vocal windows — Visible current-note vocal routing | 53 / 240 (22.1%) | 187 |
| DCS All SATB notes — Exact-MIDI recall | 473 / 984 (48.1%) | 511 |
| DCS All SATB notes — Pitch-class recall | 719 / 984 (73.1%) | 265 |
| DCS All SATB notes — Visible vocal routing | 61 / 984 (6.2%) | 923 |
| DCS All SATB notes — Vocal ownership | 117 / 984 (11.9%) | 867 |

### DCS SATB range breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS SATB range — Alto — Exact-MIDI recall | 150 / 240 (62.5%) | 90 |
| DCS SATB range — Alto — Pitch-class recall | 184 / 240 (76.7%) | 56 |
| DCS SATB range — Alto — Visible vocal routing | 20 / 240 (8.3%) | 220 |
| DCS SATB range — Alto — Vocal ownership | 37 / 240 (15.4%) | 203 |
| DCS SATB range — Bass — Exact-MIDI recall | 69 / 264 (26.1%) | 195 |
| DCS SATB range — Bass — Pitch-class recall | 187 / 264 (70.8%) | 77 |
| DCS SATB range — Bass — Visible vocal routing | 10 / 264 (3.8%) | 254 |
| DCS SATB range — Bass — Vocal ownership | 23 / 264 (8.7%) | 241 |
| DCS SATB range — Soprano — Exact-MIDI recall | 124 / 240 (51.7%) | 116 |
| DCS SATB range — Soprano — Pitch-class recall | 158 / 240 (65.8%) | 82 |
| DCS SATB range — Soprano — Visible vocal routing | 9 / 240 (3.8%) | 231 |
| DCS SATB range — Soprano — Vocal ownership | 19 / 240 (7.9%) | 221 |
| DCS SATB range — Tenor — Exact-MIDI recall | 130 / 240 (54.2%) | 110 |
| DCS SATB range — Tenor — Pitch-class recall | 190 / 240 (79.2%) | 50 |
| DCS SATB range — Tenor — Visible vocal routing | 22 / 240 (9.2%) | 218 |
| DCS SATB range — Tenor — Vocal ownership | 38 / 240 (15.8%) | 202 |

### DCS recording-configuration breakdown

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take01 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_FullChoir_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Exact-MIDI recall | 24 / 48 (50.0%) | 24 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Pitch-class recall | 40 / 48 (83.3%) | 8 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_FullChoir_Take03 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Exact-MIDI recall | 19 / 48 (39.6%) | 29 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Pitch-class recall | 36 / 48 (75.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetA_Take01 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Pitch-class recall | 35 / 48 (72.9%) | 13 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible current-note vocal routing | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Visible vocal routing | 2 / 48 (4.2%) | 46 |
| DCS Configuration — DCS_LI_QuartetA_Take02 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Exact-MIDI recall | 20 / 48 (41.7%) | 28 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible current-note vocal routing | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Visible vocal routing | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetA_Take03 — Vocal ownership | 9 / 48 (18.8%) | 39 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Visible vocal routing | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetA_Take04 — Vocal ownership | 6 / 48 (12.5%) | 42 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Pitch-class recall | 33 / 48 (68.8%) | 15 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take05 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Exact-MIDI recall | 22 / 48 (45.8%) | 26 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Simplified chord accuracy | 6 / 12 (50.0%) | 6 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetA_Take06 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Exact-MIDI recall | 34 / 48 (70.8%) | 14 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Pitch-class recall | 38 / 48 (79.2%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible current-note vocal routing | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Visible vocal routing | 0 / 48 (0.0%) | 48 |
| DCS Configuration — DCS_LI_QuartetB_Take01 — Vocal ownership | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Exact-MIDI recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Pitch-class recall | 34 / 48 (70.8%) | 14 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Simplified chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take02 — Vocal ownership | 8 / 48 (16.7%) | 40 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Current-note vocal ownership | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Exact-MIDI recall | 23 / 48 (47.9%) | 25 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Pitch-class recall | 32 / 48 (66.7%) | 16 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take03 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Exact-MIDI recall | 15 / 48 (31.2%) | 33 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Pitch-class recall | 29 / 48 (60.4%) | 19 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Simplified chord accuracy | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Visible vocal routing | 1 / 48 (2.1%) | 47 |
| DCS Configuration — DCS_LI_QuartetB_Take04 — Vocal ownership | 5 / 48 (10.4%) | 43 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact chord accuracy | 0 / 12 (0.0%) | 12 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Exact-MIDI recall | 24 / 48 (50.0%) | 24 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Pitch-class recall | 31 / 48 (64.6%) | 17 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Simplified chord accuracy | 2 / 12 (16.7%) | 10 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible current-note vocal routing | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Visible vocal routing | 3 / 48 (6.2%) | 45 |
| DCS Configuration — DCS_LI_QuartetB_Take05 — Vocal ownership | 4 / 48 (8.3%) | 44 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Current-note vocal ownership | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Exact-MIDI recall | 27 / 52 (51.9%) | 25 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Pitch-class recall | 43 / 52 (82.7%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Simplified chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible current-note vocal routing | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Visible vocal routing | 4 / 52 (7.7%) | 48 |
| DCS Configuration — DCS_TP_FullChoir_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Exact-MIDI recall | 23 / 52 (44.2%) | 29 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Pitch-class recall | 39 / 52 (75.0%) | 13 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible current-note vocal routing | 1 / 12 (8.3%) | 11 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Visible vocal routing | 3 / 52 (5.8%) | 49 |
| DCS Configuration — DCS_TP_FullChoir_Take02 — Vocal ownership | 6 / 52 (11.5%) | 46 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Current-note vocal ownership | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Exact-MIDI recall | 19 / 52 (36.5%) | 33 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Pitch-class recall | 33 / 52 (63.5%) | 19 |
| DCS Configuration — DCS_TP_FullChoir_Take03 — Simplified chord accuracy | 3 / 12 (25.0%) | 9 |
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
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact chord accuracy | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Exact-MIDI recall | 36 / 52 (69.2%) | 16 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Pitch-class recall | 50 / 52 (96.2%) | 2 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Simplified chord accuracy | 8 / 12 (66.7%) | 4 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible current-note vocal routing | 5 / 12 (41.7%) | 7 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Visible vocal routing | 6 / 52 (11.5%) | 46 |
| DCS Configuration — DCS_TP_QuartetA_Take01 — Vocal ownership | 9 / 52 (17.3%) | 43 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Current-note vocal ownership | 9 / 12 (75.0%) | 3 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact chord accuracy | 3 / 12 (25.0%) | 9 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Exact-MIDI recall | 34 / 52 (65.4%) | 18 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Pitch-class recall | 46 / 52 (88.5%) | 6 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Simplified chord accuracy | 4 / 12 (33.3%) | 8 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Visible current-note vocal routing | 7 / 12 (58.3%) | 5 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Visible vocal routing | 11 / 52 (21.2%) | 41 |
| DCS Configuration — DCS_TP_QuartetA_Take02 — Vocal ownership | 16 / 52 (30.8%) | 36 |

## Vocadito full-mix vocal routing

This separate real-vocal corpus measures how often the vocal row remains visible when the analyzer also proposes instrumental rows.

Source: `build/vocadito_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Vocadito vocals — Any detected note | 354 / 354 (100.0%) | 0 |
| Vocadito vocals — Expected instrument row | 290 / 354 (81.9%) | 64 |
| Vocadito vocals — Lit expected pitch class | 172 / 354 (48.6%) | 182 |
| Vocadito vocals — Primary display row | 52 / 354 (14.7%) | 302 |
| Vocadito vocals — Visual primary row | 28 / 354 (7.9%) | 326 |

## VocalSet full-mix vocal routing

This larger, varied real-vocal corpus measures whether the detected note remains on the vocal row when the analyzer also proposes instrumental rows.

Source: `build/vocalset_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| VocalSet vocals — Any detected note | 2388 / 2389 (100.0%) | 1 |
| VocalSet vocals — Expected instrument row | 1409 / 2389 (59.0%) | 980 |
| VocalSet vocals — Lit expected pitch class | 816 / 2389 (34.2%) | 1573 |
| VocalSet vocals — Primary display row | 227 / 2389 (9.5%) | 2162 |
| VocalSet vocals — Visual primary row | 206 / 2389 (8.6%) | 2183 |

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
| Good Sounds — Primary display row | 2 / 1318 (0.2%) | 1316 |
| Good Sounds — Visual primary row | 4 / 1318 (0.3%) | 1314 |
| Good Sounds — Bass — Any detected note | 159 / 159 (100.0%) | 0 |
| Good Sounds — Bass — Expected instrument row | 143 / 159 (89.9%) | 16 |
| Good Sounds — Bass — Lit expected pitch class | 142 / 159 (89.3%) | 17 |
| Good Sounds — Bass — Primary display row | 2 / 159 (1.3%) | 157 |
| Good Sounds — Bass — Visual primary row | 4 / 159 (2.5%) | 155 |
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
| Philharmonia — Exact expected MIDI note | 613 / 7285 (8.4%) | 6672 |
| Philharmonia — Guitar — exact expected MIDI note | 144 / 146 (98.6%) | 2 |
| Philharmonia — Other — exact expected MIDI note | 0 / 6668 (0.0%) | 6668 |
| Philharmonia — Bass — exact expected MIDI note | 469 / 471 (99.6%) | 2 |

## Iowa orchestra isolated-note coverage

This independent real acoustic corpus includes brass, woodwind, strings, pitched percussion, and double bass. The strict rows require the annotated MIDI octave, while the routing rows distinguish octave errors from absent or misrouted notes.

Source: `build/iowa_orchestra_full_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Iowa orchestra — Any detected note | 25 / 673 (3.7%) | 648 |
| Iowa orchestra — Expected instrument row | 25 / 673 (3.7%) | 648 |
| Iowa orchestra — Lit expected pitch class | 25 / 673 (3.7%) | 648 |
| Iowa orchestra — Primary display row | 25 / 673 (3.7%) | 648 |
| Iowa orchestra — Visual primary row | 25 / 673 (3.7%) | 648 |
| Iowa orchestra — Bass — Any detected note | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Expected instrument row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Lit expected pitch class | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Primary display row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Bass — Visual primary row | 25 / 25 (100.0%) | 0 |
| Iowa orchestra — Other — Any detected note | 0 / 648 (0.0%) | 648 |
| Iowa orchestra — Other — Expected instrument row | 0 / 648 (0.0%) | 648 |
| Iowa orchestra — Other — Lit expected pitch class | 0 / 648 (0.0%) | 648 |
| Iowa orchestra — Other — Primary display row | 0 / 648 (0.0%) | 648 |
| Iowa orchestra — Other — Visual primary row | 0 / 648 (0.0%) | 648 |
| Iowa orchestra — Exact expected MIDI note | 22 / 673 (3.3%) | 651 |
| Iowa orchestra — Other — exact expected MIDI note | 0 / 648 (0.0%) | 648 |
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
| Iowa piano — Expected instrument row | 79 / 85 (92.9%) | 6 |
| Iowa piano — Lit expected pitch class | 73 / 85 (85.9%) | 12 |
| Iowa piano — Primary display row | 26 / 85 (30.6%) | 59 |
| Iowa piano — Visual primary row | 37 / 85 (43.5%) | 48 |

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
| URMP saxophones — Exact expected MIDI note | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — exact expected MIDI note | 0 / 395 (0.0%) | 395 |

## URMP saxophone full-mix-mode routing

The same independent, annotated URMP saxophone clips are analyzed in full-mix mode. This isolates row-routing behavior from the exact-octave isolated-note benchmark.

Source: `build/urmp_sax_full_mix_attributes.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP saxophones — Any detected note | 391 / 395 (99.0%) | 4 |
| URMP saxophones — Expected instrument row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Lit expected pitch class | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Primary display row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Visual primary row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — Any detected note | 391 / 395 (99.0%) | 4 |
| URMP saxophones — Other — Expected instrument row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — Lit expected pitch class | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — Primary display row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — Visual primary row | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Exact expected MIDI note | 0 / 395 (0.0%) | 395 |
| URMP saxophones — Other — exact expected MIDI note | 0 / 395 (0.0%) | 395 |

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

## Cached guitar chord gates

These rows count expected labelled chord-analysis windows. Guitar Chord Mix and Guitar-TECHS Chord are isolated clips; Guitar-TECHS Music and GAPS Full are full-mix windows. They are included only when the corresponding cached attribute TSV exists.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Guitar Chord Mix — exact chord windows | 485 / 511 (94.9%) | 26 |
| Guitar Chord Mix — primary displayed chord windows | 398 / 511 (77.9%) | 113 |
| Guitar Chord Mix — expected guitar pitch classes | 1276 / 1533 (83.2%) | 257 |
| Guitar Techs Chord — exact chord windows | 7247 / 7484 (96.8%) | 237 |
| Guitar Techs Chord — primary displayed chord windows | 3563 / 7484 (47.6%) | 3921 |
| Guitar Techs Chord — expected guitar pitch classes | 24405 / 26738 (91.3%) | 2333 |
| Guitar Techs Music — exact chord windows | 412 / 500 (82.4%) | 88 |
| Guitar Techs Music — primary displayed chord windows | 238 / 500 (47.6%) | 262 |
| Guitar Techs Music — expected guitar pitch classes | 1609 / 1838 (87.5%) | 229 |
| Guitar Techs Music — power-chord exact windows | 6 / 26 (23.1%) | 20 |
| Gaps Guitar Full — exact chord windows | 360 / 540 (66.7%) | 180 |
| Gaps Guitar Full — primary displayed chord windows | 177 / 540 (32.8%) | 363 |
| Gaps Guitar Full — expected guitar pitch classes | 1518 / 1957 (77.6%) | 439 |
| Gaps Guitar Full — power-chord exact windows | 22 / 39 (56.4%) | 17 |
| Guitarset — exact chord windows | 1143 / 1491 (76.7%) | 348 |
| Guitarset — primary displayed chord windows | 621 / 1491 (41.6%) | 870 |
| Guitarset — expected guitar pitch classes | 4358 / 5340 (81.6%) | 982 |
| Guitarset — power-chord exact windows | 1 / 2 (50.0%) | 1 |

## URMP real multitrack gate

This downloaded real chamber-music corpus measures the same performances as provided mixes and as sums of their isolated tracks, with official note and MIDI annotations.
Instrument rows below show exact isolated-note recall for each measured instrument.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| URMP — real pieces loadable | 44 / 44 (100.0%) | 0 |
| URMP — selected annotated windows | 528 / 528 (100.0%) | 0 |
| URMP — isolated-track exact notes | 88 / 1788 (4.9%) | 1700 |
| URMP — isolated-track detected notes | 90 / 1788 (5.0%) | 1698 |
| URMP — isolated-track precision | 88 / 94 (93.6%) | 6 false notes |
| URMP — provided-mix exact chords | 172 / 527 (32.6%) | 355 |
| URMP — provided stream chord windows | 193 / 527 (36.6%) | 334 |
| URMP — provided sequence chord windows | 201 / 527 (38.1%) | 326 |
| URMP — bassoon isolated exact notes | 0 / 36 (0.0%) | 36 |
| URMP — clarinet isolated exact notes | 0 / 120 (0.0%) | 120 |
| URMP — double bass isolated exact notes | 31 / 36 (86.1%) | 5 |
| URMP — flute isolated exact notes | 0 / 216 (0.0%) | 216 |
| URMP — horn isolated exact notes | 0 / 60 (0.0%) | 60 |
| URMP — oboe isolated exact notes | 0 / 72 (0.0%) | 72 |
| URMP — saxophone isolated exact notes | 0 / 132 (0.0%) | 132 |
| URMP — tuba isolated exact notes | 57 / 60 (95.0%) | 3 |
| URMP — trombone isolated exact notes | 0 / 96 (0.0%) | 96 |
| URMP — trumpet isolated exact notes | 0 / 264 (0.0%) | 264 |
| URMP — viola isolated exact notes | 0 / 156 (0.0%) | 156 |
| URMP — cello isolated exact notes | 0 / 132 (0.0%) | 132 |
| URMP — violin isolated exact notes | 0 / 408 (0.0%) | 408 |

## Bach10-mf0-synth multitrack stress gate

This F0-derived, resynthesized four-part corpus is reported separately from real-recording metrics. It measures expected active note slots and global chord windows.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Bach10-mf0-synth — expected note slots | 149 / 160 (93.1%) | 11 |
| Bach10-mf0-synth — exact chord windows | 3 / 40 (7.5%) | 37 |
| Bach10-mf0-synth — simplified chord windows | 32 / 40 (80.0%) | 8 |

## MusicNet real-mixture gate

This open CC-BY corpus measures real classical mixtures; unlike Bach10, it has no isolated stems. A recording is eligible for its chord rows only when annotations provide a window with at least two active instruments and two pitch classes.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MusicNet real mixes — recordings with eligible chord windows | 154 / 330 (46.7%) | 176 |
| MusicNet real mixes — expected pitch classes | 5657 / 7478 (75.6%) | 1821 |
| MusicNet real mixes — exact chord windows | 319 / 1847 (17.3%) | 1528 |
| MusicNet real mixes — simplified chord windows | 680 / 1847 (36.8%) | 1167 |

### MusicNet annotated instrument-routing

Each active annotated note is checked against its General-MIDI family row. These are real-mixture routing measurements, separate from the global chord gate.

Source: `build/musicnet_routing.tsv`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MusicNet All — Exact note in expected row | 1192 / 13079 (9.1%) | 11887 |
| MusicNet All — Pitch class in expected row | 2794 / 13079 (21.4%) | 10285 |
| MusicNet All — Visible exact note in expected row | 1192 / 13079 (9.1%) | 11887 |
| MusicNet All — Visible pitch class in expected row | 2794 / 13079 (21.4%) | 10285 |
| MusicNet Other — Exact note in expected row | 0 / 8566 (0.0%) | 8566 |
| MusicNet Other — Pitch class in expected row | 0 / 8566 (0.0%) | 8566 |
| MusicNet Other — Visible exact note in expected row | 0 / 8566 (0.0%) | 8566 |
| MusicNet Other — Visible pitch class in expected row | 0 / 8566 (0.0%) | 8566 |
| MusicNet Piano — Exact note in expected row | 1192 / 4513 (26.4%) | 3321 |
| MusicNet Piano — Pitch class in expected row | 2794 / 4513 (61.9%) | 1719 |
| MusicNet Piano — Visible exact note in expected row | 1192 / 4513 (26.4%) | 3321 |
| MusicNet Piano — Visible pitch class in expected row | 2794 / 4513 (61.9%) | 1719 |

## MAPS real-piano gate

This real Disklavier corpus uses aligned MIDI annotations. The four stored shard summaries are combined here; rows remain visible even when the aggregate quality gate fails.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MAPS real piano — recordings with eligible chord windows | 2924 / 3000 (97.5%) | 76 |
| MAPS real piano — expected pitch classes | 8052 / 11662 (69.0%) | 3610 |
| MAPS real piano — keyboard detected-note precision | 8052 / 11975 (67.2%) | 3923 false predictions |
| MAPS real piano — exact chord windows | 307 / 2231 (13.8%) | 1924 |
| MAPS real piano — keyboard chord precision | 307 / 1409 (21.8%) | 1102 false predictions |

## Independent piano cross-corpus coverage checklist

MAESTRO is independent external paired WAV/MIDI evidence. It remains separate from MAPS until a protected cross-piano rule is verified.

| Task | Complete / total | Remaining |
| --- | ---: | ---: |
| Prepare external MAESTRO paired-audio subset | 1 / 1 (100.0%) | 0 |
| Measure MAESTRO note and chord outcomes | 0 / 1 (0.0%) | 1 |
| Replay continuous chord state on MAPS and MAESTRO | 1 / 1 (100.0%) | 0 |
| Mine a protected cross-piano detector rule | 0 / 1 (0.0%) | 1 |

### Independent-piano runtime-state mining

Source: `build/independent_piano_chord_states.txt`

| Metric | Candidate states / shared states | Remaining |
| --- | ---: | ---: |
| No-label states with complete pitch-class recovery in every corpus | 0 / 16 (0.0%) | 16 |

### Continuous independent-piano chord-state replay

Each sequence reuses one analysis engine across five adjacent annotated stable-chord windows. It measures the OBS switch-confirm and label-hold path rather than independent snapshots.

Source: `build/independent_piano_chord_stability.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Annotated stable chord-state frames with the expected keyboard chord | 96 / 530 (18.1%) | 434 |
| Chord-state frames that retained a label | 321 / 530 (60.6%) | 209 no-label frames |
| Correct-loss-recovery flickers across audited sequences | 106 / 106 (100.0%) | 0 |
| Audited continuous stable-chord sequences | 106 / 106 (100.0%) | 0 |

### Chord switch-confirmation audit

A replacement-confirmation trial is retained only if it improves correct stable-state frames without reintroducing correct-loss-recovery flicker.

| Candidate | Correct stable frames | Wrong labels | Correct-loss-recovery flickers | Decision |
| --- | ---: | ---: | ---: | --- |
| Two-frame replacement confirmation | 96 / 530 (18.1%) | 225 | 0 | retained |
| One-frame replacement confirmation | 104 / 530 (19.6%) | 235 | 3 | rejected; retain 2 frames |
| Three-frame replacement confirmation | 95 / 530 (17.9%) | 244 | 0 | rejected; MAESTRO drops 70→67 correct frames |
| Lower 0.18 pitch-class presence | 99 / 530 (18.7%) | 245 | 0 | rejected; MAESTRO has no correct-frame gain and wrong labels rise 243→244 |
| 0.05 ambiguity margin through 0.60 confidence | 96 / 530 (18.1%) | 240 | 0 | rejected; suppresses 3 wrong MAESTRO labels but gains no correct frame |
| Zero bass-root candidate bonus | 102 / 530 (19.2%) | 237 | 0 | rejected; piano gain fails broad analyzer-case regression coverage |
| Keyboard-only confidence ≥0.70 | 96 / 530 (18.1%) | 219 | 0 | enabled; hides 6 wrong labels with no correct-frame or flicker loss |

Sources: `build/piano_chord_confirmation_audit.txt`, `build/piano_chord_confirm3_audit.txt`, `build/piano_chord_tone018_audit.txt`, `build/piano_chord_margin060_audit.txt`, `build/piano_chord_bassbonus000_audit.txt`, `build/piano_chord_display_gate_audit.txt`

### Independent-piano exact fallback audit

This tests whether an unlabeled exact pitch-class set can safely restore a chord label. A fallback must be correct on every observed no-label window in both independent corpora.

Source: `build/independent_piano_exact_chord_fallback.txt`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Independent piano corpora checked | 2 / 2 (100.0%) | 0 |
| Cross-piano runtime-safe exact pitch-class fallback available | 0 / 1 (0.0%) | 1 |

No exact fallback is eligible; detected pitch-class sets and wrong labels do not agree safely across both corpora.

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
| Displayable BPM at confidence ≥ 0.60 | 0 / 64 (0.0%) | 64 |

## GTZAN-Rhythm annotated-tempo diagnostic

Source: `build/gtzan_rhythm_bpm_diagnostics.log`. GTZAN-Rhythm provides manually annotated beat/downbeat JAMS for real, genre-diverse music; stable BPM segments are derived from those repeated beat intervals.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 0 / 100 (0.0%) | 100 |

## Candombe annotated-tempo diagnostic

Source: `build/candombe_bpm_diagnostics.log`. Candombe supplies expert beat/downbeat annotations for real Uruguayan drum ensembles; stable BPM segments are derived from repeated labelled beat intervals.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 20 / 35 (57.1%) | 15 |

## Beat This! independent neural GTZAN diagnostic

Source: `build/beat_this_final0_gtzan_rhythm_bpm_diagnostics.log`. This is offline-only CPU inference with the MIT-licensed Beat This! `final0` model; its published training excludes GTZAN. It is independent calibration evidence, not a live OBS backend or release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Offline stable-segment BPM within 8 BPM | 87 / 100 (87.0%) | 13 |

## Beat This! offline real-tempo diagnostic

These CPU-only, non-causal checks use the same stable annotated windows as the live tempo audits. They establish cross-corpus accuracy only; Beat This! is not an OBS backend or release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Ballroom offline stable-segment BPM within 8 BPM | 64 / 64 (100.0%) | 0 |
| FiloBass offline stable-segment BPM within 8 BPM | 18 / 48 (37.5%) | 30 |

### Beat This! bounded rolling-window replay

Each estimate receives only the trailing window ending at the annotated stable-window endpoint. This evaluates input causality and CPU throughput, but still does not authorize OBS integration until continuous replay shows zero wrong displayed BPM values.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Ballroom rolling BPM within 8 BPM | 64 / 64 (100.0%) | 0 |
| Ballroom rolling windows processed within their audio duration | 64 / 64 (100.0%) | 0 |
| FiloBass rolling BPM within 8 BPM | 16 / 48 (33.3%) | 32 |
| FiloBass rolling windows processed within their audio duration | 48 / 48 (100.0%) | 0 |

### Beat This! continuous causal replay

Each stable segment is replayed at 10 and 20 seconds using only its trailing 20-second audio window. This is a stronger causal diagnostic, but a corpus with wrong outputs cannot authorize OBS integration.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Ballroom continuous causal BPM within 8 BPM | 126 / 128 (98.4%) | 2 |
| Ballroom continuous outputs processed within their audio duration | 128 / 128 (100.0%) | 0 |
| FiloBass continuous causal BPM within 8 BPM | 38 / 96 (39.6%) | 58 |
| FiloBass continuous outputs processed within their audio duration | 96 / 96 (100.0%) | 0 |

### Beat This! strict causal interval-count gate

Source: `build/beat_this_continuous_interval_gate_audit.txt`. This rejects a Beat This! value unless its bounded causal window contains at least 44 usable beat intervals. The gate removed every observed wrong value in both corpora, but it is diagnostic-only until an optional realtime backend can preserve the exact same gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Ballroom strict-gated BPM within 8 BPM | 23 / 23 (100.0%) | 0 wrong displayed BPM |
| FiloBass strict-gated BPM within 8 BPM | 8 / 8 (100.0%) | 0 wrong displayed BPM |
| Zero-wrong strict causal gate with ≥5 outputs per corpus | 1 / 1 (100.0%) | 0 |

### Beat This! exact persistent-sidecar replay

Sources: `build/beat_this_sidecar_ballroom_replay.txt` and `build/beat_this_sidecar_filobass_replay.txt`. Each row crossed the binary 20-second packet boundary into one persistent external-model process. This validates the protocol and strict gate offline; it does not start or authorize an OBS backend.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Ballroom sidecar-ready BPM within 8 BPM | 22 / 22 (100.0%) | 0 wrong ready BPM; 40 withheld, 2 unavailable |
| FiloBass sidecar-ready BPM within 8 BPM | 8 / 8 (100.0%) | 0 wrong ready BPM; 40 withheld, 0 unavailable |
| Zero-wrong sidecar replay with ≥5 ready rows per corpus | 1 / 1 (100.0%) | 0 |

### Three-tracker offline consensus safety audit

Source: `build/three_tempo_tracker_consensus.log`. A candidate is retained only when phase, the permissive tracker, and Beat This! agree, and each individual estimate is within 8 BPM. This is offline evidence only: Beat This! uses non-causal full-context attention, so this audit cannot enable a live OBS path.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Correct offline three-tracker consensus candidates | 0 / 0 (0.0%) | 0 wrong candidates |
| Audited rows eligible for offline three-tracker consensus | 0 / 212 (0.0%) | 212 |
| Offline consensus candidates newly revealed beyond phase display | 0 / 212 (0.0%) | 212 |

### High-tempo three-tracker offline veto audit

Source: build/high_tempo_three_tempo_tracker_consensus.log. This is restricted to annotated GTZAN Rhythm BPM ≥150 and can only justify an offline veto/post-processing experiment; it cannot alter live BPM display.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Correct high-tempo three-tracker consensus candidates | 5 / 5 (100.0%) | 0 wrong candidates |
| High-tempo annotated rows eligible for consensus | 5 / 18 (27.8%) | 13 |
| High-tempo candidates newly revealed beyond phase display | 5 / 18 (27.8%) | 13 |

## FiloBass real bass-led annotated-tempo diagnostic

Source: `build/filobass_bpm_diagnostics.log`. FiloBass pairs real jazz bass stems with reviewed downbeat syncpoints and a MIDI time signature; BPM references are derived only from those corpus annotations.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 0 / 48 (0.0%) | 48 |

### FiloBass source-grid energy feasibility diagnostic

The corpus harness forces the labelled BPM into the final diagnostic slot, then compares its bass energy with the selected candidate. This is not a score-ranked candidate and does not change BPM selection.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Labelled BPM exported through harness-only probe | 47 / 48 (97.9%) | 1 |
| Present labelled candidate has higher bass grid-energy | 8 / 47 (17.0%) | 39 |
| Present labelled candidate ties selected bass grid-energy | 7 / 47 (14.9%) | 40 |
| Present labelled candidate has lower bass grid-energy | 32 / 47 (68.1%) | 15 |

### FiloBass raw bass-attack feasibility diagnostic

Source: `build/filobass_bass_onset_diagnostics.tsv`. This offline analysis ranks tempos from raw bass-envelope attacks only. It is a feature-feasibility check, not a live-output result or release gate.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Reviewed BPM ranked first by raw bass attacks | 1 / 24 (4.2%) | 23 |
| Reviewed BPM ranked in top five by raw bass attacks | 10 / 24 (41.7%) | 14 |
| Reviewed BPM matches raw bass attacks at direct or double tempo | 16 / 24 (66.7%) | 8 |

## E-GMD generated percussion tempo diagnostic

Source: `build/egmd_bpm_diagnostics.log`. This generated aligned-MIDI fixture exercises kick/snare phase recovery; it is a regression benchmark, not independent real-audio evidence.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Displayable BPM at confidence ≥ 0.60 | 12 / 20 (60.0%) | 8 |

## IDMT real-bass timing-ground-truth audit

Source: `build/idmt_bass_lines_tempo_metadata.tsv`. IDMT provides real bass audio and reviewed note onsets, but only corpus-supplied tempo, beat, or pattern fields qualify it as BPM ground truth.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Tracks with corpus-supplied tempo, beat, or pattern metadata | 0 / 17 (0.0%) | 17 |

## URMP double-bass timing-ground-truth audit

Source: `build/urmp_bass_timing_audit.tsv`. URMP supplies real double-bass stems and audio-aligned note annotations, but its original score MIDI is not an audio-aligned metrical grid. Only an explicit official beat/downbeat/bar annotation would qualify a stem for BPM validation.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Double-bass stems with aligned audio and note annotations | 3 / 3 (100.0%) | 0 |
| Double-bass stems with an explicit official beat/downbeat grid | 0 / 3 (0.0%) | 3 |
| URMP double-bass stems qualifying as tempo truth | 0 / 3 (0.0%) | 3 |

## Tempo coverage-gap checklist

The live BPM field is a sliding trailing-three-second estimate: every analysis hop re-evaluates only the latest Kick, Bass, and Snare onset peaks. Longer phase-history and external-tracker experiments below are retained as historical diagnostics only; they cannot overwrite the live display. Source-specific evidence is tested separately from corpus coverage so a synthetic regression fixture cannot be mistaken for independent real-audio validation.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Keep the live BPM display on a trailing 3 s Kick/Bass/Snare window | 1 / 1 (100.0%) | 0 | every analysis hop derives `estimated_bpm` solely from the latest source-separated 3 s peak history |
| Prevent long-lived phase or external trackers from overriding live BPM | 1 / 1 (100.0%) | 0 | all long-history tracker fallback flags are disabled; a moving-window contract test guards the assignment |
| Separate kick, bass, snare, and tonal onset histories | 1 / 1 (100.0%) | 0 | source-specific phase coverage in debug candidates |
| Preserve simultaneous kick+bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer case verifies both kick and bass phase coverage on the same downbeats |
| Require repeated source evidence on the selected beat grid | 1 / 1 (100.0%) | 0 | confidence cap below display floor without repeated alignment |
| Resolve half/double-time candidates with kick/bass downbeat evidence | 1 / 1 (100.0%) | 0 | analyzer cases retain the beat grid through sparse-kick half-time and dense-subdivision alternatives |
| Historical adaptive phase-history experiment retained for diagnostics | 1 / 1 (100.0%) | 0 | 8 s percussion / 18 s sparse-source policy; it does not control the live BPM field |
| Generated drum phase regression measured | 1 / 1 (100.0%) | 0 | E-GMD x/total BPM diagnostic |
| Retrieve versioned Ballroom beat/bar annotations | 1 / 1 (100.0%) | 0 | CPJKU BallroomAnnotations checkout in InstrumentSamples |
| Rhythm-heavy real-mix beat validation measured | 1 / 1 (100.0%) | 0 | up to 64 genre-balanced Ballroom stable sections with manually corrected beat/bar annotations |
| Genre-diverse real-mix beat validation measured | 1 / 1 (100.0%) | 0 | GTZAN-Rhythm WAV/JAMS pairs; stable BPM segments derived from manually annotated beats |
| Retrieve and validate Candombe beat/downbeat labels | 1 / 1 (100.0%) | 0 | 35 public CSVs with expert beat times and bar/beat positions |
| Independent labelled drumming-corpus validation measured | 1 / 1 (100.0%) | 0 | Candombe FLAC/CSV pairs: 35 real performances with expert beat/downbeat labels |
| Benchmark independent neural tracker on held-out GTZAN | 1 / 1 (100.0%) | 0 | offline Beat This! `final0` output with no OBS/runtime integration |
| Benchmark Beat This! on independent real-tempo corpora | 2 / 2 (100.0%) | 0 | Ballroom and FiloBass annotated stable segments; CPU-only offline evidence |
| Replay bounded trailing Beat This! windows on real-tempo corpora | 2 / 2 (100.0%) | 0 | window ends at each annotated output time; records correctness and processing budget |
| Validate strict causal Beat This! interval gate | 1 / 1 (100.0%) | 0 | ≥44 intervals: Ballroom 23 / 23, FiloBass 8 / 8, zero wrong values in this replay |
| Specify isolated Beat This! sidecar protocol | 1 / 1 (100.0%) | 0 | disabled-by-default 20 s binary packet, persistent external model process, and the exact ≥44-interval gate; see `docs/beat_this_live_sidecar_protocol.md` |
| Replay the exact sidecar protocol on real-tempo corpora | 2 / 2 (100.0%) | 0 | zero wrong ready BPM, ≥5 ready rows per corpus, and no packet shorter than 20 seconds |
| Compile and model-free test the OBS sidecar boundary | 1 / 1 (100.0%) | 0 | a persistent-child test sends two exact 20 s packets; static checks enforce disabled-by-default, callback isolation, timeout-bounded I/O, expiry, and normal-BPM precedence |
| Audit phase/BTT/Beat This! offline agreement | 1 / 1 (100.0%) | 0 | every selected candidate must be correct across Ballroom, FiloBass, and GTZAN |
| Audit high-tempo GTZAN three-tracker offline veto | 1 / 1 (100.0%) | 0 | every selected ≥150 BPM GTZAN candidate must be correct across phase, BTT, and Beat This! |
| Integrate bounded causal Beat This! live use | 1 / 1 (100.0%) | 0 | opt-in OBS worker sends only exact 20 s packets, rejects malformed/gated/late replies, expires fallback BPM, and never replaces a displayable normal BPM |
| IDMT real-bass timing metadata qualifies as beat truth | 0 / 17 (0.0%) | 17 | only corpus-supplied tempo/beat/pattern fields count; note onsets are insufficient |
| Audit URMP double-bass timing provenance | 1 / 1 (100.0%) | 0 | distinguish audio-aligned note annotations from explicit metrical grids |
| URMP double-bass stems qualify as beat truth | 0 / 3 (0.0%) | 3 | original score MIDI alone is not audio-aligned timing evidence |
| Independent real bass-led beat-labelled validation measured | 1 / 1 (100.0%) | 0 | FiloBass real bass stems plus reviewed downbeats and MIDI time signature |
| Reject MUSDB18/BeatNet+ as an authoritative bass BPM benchmark | 1 / 1 (100.0%) | 0 | MUSDB18 access requires academic-use approval, and BeatNet+ labels are documented as added annotations rather than original corpus beat truth |
| Assess raw bass-attack BPM evidence | 1 / 1 (100.0%) | 0 | offline FiloBass rank-one/top-five diagnostic |
| Assess bass source-grid energy before a selector | 1 / 1 (100.0%) | 0 | FiloBass expected candidate shows higher bass alignment in 8/47 eligible rows |
| Reject unproven meter/bass candidate reweighting | 1 / 1 (100.0%) | 0 | current feasibility audit: Ballroom meter/bass selectors peak at 5 / 64 and FiloBass stays at 4 / 47, so neither is a safe BPM selector |
| Reject unproven normalized-recurrence selector | 1 / 1 (100.0%) | 0 | lag-normalized recurrence reaches 6 / 61 only at an extreme Ballroom weight and remains 4 / 24 on FiloBass |
| Reject unproven kick+bass-coincidence selector | 1 / 1 (100.0%) | 0 | same-frame coincidence reaches 8 / 64 on Ballroom and 5 / 47 on FiloBass, but cannot safely resolve meter alone |
| Reject longer percussive phase history | 1 / 1 (100.0%) | 0 | 12 s drops Ballroom displayable BPM from 1 / 64 to 0 / 64 and raises E-GMD mean error from 0.21 to 0.32 BPM; retain the 8 s policy |
| Reject unproven dynamic beat-path selector | 1 / 1 (100.0%) | 0 | dynamic path improves Ballroom labelled-candidate rank from 9 / 64 to 13 / 64 but regresses FiloBass from 4 / 24 to 2 / 24, so it is not a safe BPM selector |
| Reject bass-dominant RMS attack phase feature | 1 / 1 (100.0%) | 0 | a guarded live bass-amplitude attack left FiloBass at 0 / 24 displayed and candidate ranks 4 / 1 / 0 / 1 / 18; Ballroom 1 / 64 and E-GMD 20 / 20 were unchanged, so it adds no value |
| Reject combined bass/coincidence candidate reweighting | 1 / 1 (100.0%) | 0 | shared grid best is kick+bass alignment 4.0 plus recurrence 4.0: 4 / 64→7 / 64 Ballroom and 4 / 47→6 / 47 FiloBass, but 98 / 111 selections are still wrong |
| Reject offline three-tracker consensus as a live gate | 1 / 1 (100.0%) | 0 | the latest offline audit found 18 / 18 correct candidates (11 newly revealed), but the actual live Ballroom replay introduced one double-time display; keep the feature disabled |
| Retain calibrated BPM display-confidence gate | 1 / 1 (100.0%) | 0 | at 0.45 confidence, raw selection is correct only 1 / 5 Ballroom and 0 / 4 FiloBass; lowering the 0.60 display gate would expose mostly wrong BPM |
| Local advanced beat-tracker backend available | 0 / 2 (0.0%) | 2 | `aubio` and `essentia` are unavailable through pkg-config; next step is a dependency-free tracker or an added backend |
| Retrieve license-compatible advanced beat tracker | 1 / 1 (100.0%) | 0 | MIT-licensed Beat-and-Tempo-Tracking source is pinned at `c039090f1af771092d95c3ffc402e557940f7384`; aubio remains unsuitable without a GPL compatibility decision |
| Benchmark permissive beat tracker on both real tempo corpora | 2 / 2 (100.0%) | 0 | source-only MIT tracker measured on the same 20 s annotated stable segments as the analyzer |
| Permissive tracker raw BPM — Ballroom | 41 / 64 (64.1%) | 23 | within 8 BPM; diagnostic source `build/btt_ballroom_bpm_diagnostics.log` |
| Permissive tracker raw BPM — FiloBass | 21 / 48 (43.8%) | 27 | within 8 BPM; diagnostic source `build/btt_filobass_bpm_diagnostics.log` |
| Permissive tracker at 0.60 certainty — Ballroom | 19 / 24 (79.2%) | 5 | correct / displayed; 40 clips remain hidden |
| Permissive tracker at 0.60 certainty — FiloBass | 5 / 12 (41.7%) | 7 | correct / displayed; precision calibration remains required |
| Permissive tracker at 0.75 certainty — Ballroom | 13 / 15 (86.7%) | 2 | correct / displayed; 49 clips remain hidden |
| Permissive tracker at 0.75 certainty — FiloBass | 3 / 3 (100.0%) | 0 | correct / displayed; 45 clips remain hidden |
| Permissive tracker at 0.75 certainty — E-GMD | 3 / 3 (100.0%) | 0 | correct / displayed; generated percussion regression only |
| Permissive tracker at 0.80 certainty — Ballroom | 12 / 13 (92.3%) | 1 | source-only candidates; 51 clips remain hidden; not a live-release gate |
| Permissive tracker at 0.80 certainty — FiloBass | 3 / 3 (100.0%) | 0 | source-only candidates; 45 clips remain hidden; not a live-release gate |
| Repair continuous PCM feed to permissive tracker | 1 / 1 (100.0%) | 0 | feed all host-buffer PCM rather than only the short feature window; this removes artificial inter-buffer gaps in live corpus runs |
| Reject tail-truncated permissive fallback results | 1 / 1 (100.0%) | 0 | earlier 0.75/0.60 live trials omitted each host-buffer tail and produced wrong Ballroom BPM; they do not calibrate the repaired continuous feed |
| Historical strict permissive-tracker fallback audit (disabled) | 3 / 3 (100.0%) | 0 | at 0.80 certainty with phase confidence below 0.60: Ballroom 12 / 64, FiloBass 2 / 24, E-GMD 20 / 20; the fallback remains disabled so it cannot replace the trailing-window display |
| Benchmark constrained high-tempo beat tracker | 2 / 2 (100.0%) | 0 | 120--240 BPM source-only tracker at 0.55 certainty: Ballroom 17 / 17 and FiloBass 7 / 7 correct |
| Reject concurrent high-tempo tracker fallback | 1 / 1 (100.0%) | 0 | live candidates at 0.55 were Ballroom 15 / 15 and FiloBass 5 / 5, but both concurrent and post-phase scheduling raised Ballroom id 8 phase confidence from withheld to ≥0.617 and displayed wrong 158.97 BPM for 128.03; feature remains false |
| Reject high-tempo-only tracker setting | 1 / 1 (100.0%) | 0 | one 120--240 BPM tracker still raises Ballroom id 8 phase confidence to 0.617 and displays wrong 158.97 BPM for 128.03; retain broad 40--240 BPM tracker at 0.80 |
| Demonstrate a bass-attack feature improves real bass BPM | 0 / 1 (0.0%) | 1 | improve FiloBass displayable BPM without regressing E-GMD |
| Keep withheld BPM visually unavailable | 1 / 1 (100.0%) | 0 | renderer shows `BPM --` both before evidence and while a below-threshold estimate is withheld |
| Hide numeric BPM when calibrated confidence is insufficient | 1 / 1 (100.0%) | 0 | renderer keeps the numeric BPM hidden below 0.60 confidence and reserves numbers for calibrated estimates |

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
| MAESTRO | 295 / 1280 (23.0%) | 339 / 1280 (26.5%) | 646 / 1280 (50.5%) |

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
| Full drum gate — primary kick | 6206 / 6505 (95.4%) | 299 |
| Full drum gate — primary snare | 4013 / 5390 (74.5%) | 1377 |
| Full drum gate — primary hihat | 1990 / 2358 (84.4%) | 368 |
| Full drum gate — primary crash | 569 / 788 (72.2%) | 219 |
| Full drum gate — primary tom | 1949 / 2861 (68.1%) | 912 |
| Full drum gate — primary ride | 238 / 352 (67.6%) | 114 |
| Full drum gate — primary rim | 332 / 504 (65.9%) | 172 |

## Tom/rim/ride protected-selector audit

The top zero-regression one-shot selectors are searched against the full, HF, and IDMT attribute sets. A selector also needs a positive match in an independent corpus; duplicate assets shared by the full and spread collections do not count as replication.

| Candidate route | Independent positive corpora | Runtime selector eligible |
| --- | ---: | ---: |
| Tom → Snare | 0 / 2 (0.0%) | 0 / 1 (0.0%) |
| Rim → Snare | 0 / 2 (0.0%) | 0 / 1 (0.0%) |
| Ride → HiHat | 0 / 2 (0.0%) | 0 / 1 (0.0%) |

## High-fidelity drum-kit primary-classification gate

These independent one-shot samples are sharded by expected instrument; the seven shard matrices are combined here so primary-label changes remain visible.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| High-fidelity drum kit — primary kick | 286 / 300 (95.3%) | 14 |
| High-fidelity drum kit — primary snare | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary hihat | 295 / 300 (98.3%) | 5 |
| High-fidelity drum kit — primary crash | 285 / 300 (95.0%) | 15 |
| High-fidelity drum kit — primary tom | 283 / 300 (94.3%) | 17 |
| High-fidelity drum kit — primary ride | 292 / 300 (97.3%) | 8 |
| High-fidelity drum kit — primary rim | 279 / 300 (93.0%) | 21 |

## STAR Drums preview multitrack gate

This independent real-music preview measures annotated drum-event recall and false activations across mixed recordings.

Source: `build/star_drums_misses.log.windows.summary`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| STAR Drums preview — annotated drum events detected | 39 / 56 (69.6%) | 17 |
| STAR Drums preview — detected-drum precision | 39 / 39 (100.0%) | 0 false predictions |
| STAR Drums preview — windows without a false drum | 16 / 16 (100.0%) | 0 false-positive windows |

## MDB Drums multitrack gate

This independent real-music full-mix fixture measures annotated drum-event recall and false activations across a larger variety of accompanied recordings.

Source: `build/mdb_drums_windows.log.summary`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MDB Drums — annotated drum events detected | 135 / 192 (70.3%) | 57 |
| MDB Drums — detected-drum precision | 135 / 152 (88.8%) | 17 false predictions |
| MDB Drums — windows without a false drum | 76 / 92 (82.6%) | 16 false-positive windows |

### MDB annotated Rim-event audit

MDB is already part of the real-mix calibration evidence, so this single side-stick/Rim event does not replace independent acoustic replication.

Source: `build/mdb_rim_coverage.txt`.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| MDB annotated Rim events detected | 0 / 1 (0.0%) | 1 |

### MDB multi-recording Snare-context replay

The best source-scoped offline candidate (`kick_body ≥36.36`, `upper_tom ≤17.85`) covered three MDB false-positive recordings with no protected one-shot loss. In a rebuilt MDB, STAR, and BabySlakh replay it did not suppress an actual active Snare or improve a protected metric. The runtime trial was removed; the tables above and below are refreshed from the retained baseline outputs.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Highest multi-recording MDB Snare candidate replayed | 1 / 1 (100.0%) | 0 |
| Candidate with a measured cross-corpus gain | 0 / 1 (0.0%) | 1 |

## BabySlakh rendered full-mix drum baseline

These 16 kHz rendered multitracks have aligned per-stem MIDI drum truth. They broaden the calibration set, but remain separately reported from real-recording MDB and STAR evidence.

Source: `build/babyslakh_drums_diagnostics.log`

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| BabySlakh rendered mixes — annotated drum events detected | 141 / 259 (54.4%) | 118 |
| BabySlakh rendered mixes — detected-drum precision | 141 / 179 (78.8%) | 38 false predictions |
| BabySlakh rendered mixes — windows without a false drum | 48 / 80 (60.0%) | 32 false-positive windows |

## 29k Drums independent acoustic Tom/Ride baseline

Source: `build/29k_samples_drums_measurement.log`. The fixture uses only published Tom (ft/mt/ht) and Ride (cy) samples; it does not represent Rim or a full mix.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| 29k Drums — Tom detected | 418 / 500 (83.6%) | 82 |
| 29k Drums — Tom primary display | 271 / 500 (54.2%) | 229 |
| 29k Drums — Ride detected | 379 / 500 (75.8%) | 121 |
| 29k Drums — Ride primary display | 324 / 500 (64.8%) | 176 |

### Retained final-arbitration Ride recovery

This runs only for non-generated one-shots with no active Ride candidate, high energy at least 0.82, and Ride/HiHat segment ratio at least 3.091. It was selected on the 29k acoustic fixture. The current full one-shot Ride replay is 316 / 352 (89.8%), one sample below its 90% gate, so this remains local 29k evidence rather than an independent positive replication.

| Metric | Accurate / total | Change from preserved 29k baseline |
| --- | ---: | ---: |
| 29k Ride detected | 379 / 500 (75.8%) | +7 / 500 |
| 29k Ride primary display | 324 / 500 (64.8%) | +7 / 500 |
| Independent positive corpus replications | 1 / 2 (50.0%) | 1 remaining before it can close the Tom/Rim/Ride priority checkpoint |

### Rejected Tom/Ride primary runtime trials

The candidate searches below looked promising locally or had many missed samples, but failed the broader protected one-shot replay and are not enabled.

| Candidate evidence | Positive-route result | Protected one-shot result | Decision |
| --- | ---: | ---: | --- |
| Low-high inactive Tom from Snare | Tom primary 269→318 / 500; Ride 317→317 / 500 | Snare primary 133→87 / 160; Tom false 199→253 | reject: severe Snare regression |
| Ride from HiHat segment tie | Tom primary 269→269 / 500; Ride 317→332 / 500 | HiHat primary 141→136 / 160; Tom primary 126→124 / 160 | reject: protected HiHat and Tom regressions |
| Cached Rim→Snare zero-regression screen | 116 routed Rim samples across the protected one-shot cache | closest selector fixes 12 but touches 237 protected primary labels and creates 152 new active labels | reject: no selector satisfies the zero-regression gate |
| Cached Tom→Snare zero-regression screen | 509 routed Tom samples across the protected one-shot cache | closest selector fixes 52 but breaks 429 protected primary labels and creates 236 new active labels | reject: no selector satisfies the zero-regression gate |
| HF Ride→HiHat zero-regression screen | 3 routed Ride samples in the independent high-fidelity kit | only selector fixes 3 but breaks 259 protected primary labels and creates 76 new active labels | reject: no selector satisfies the zero-regression gate |

## Virtuosity Drums independent CC0 acoustic baseline

Source: `build/virtuosity_drums_measurement.log`. The fixture uses only the library's named overhead-channel Snare Rimshot/Cross-stick, normal Tom, and normal/Bell Ride articulations; it excludes duplicate microphones.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| Virtuosity Drums — Tom detected | 47 / 48 (97.9%) | 1 |
| Virtuosity Drums — Tom primary display | 47 / 48 (97.9%) | 1 |
| Virtuosity Drums — Ride detected | 17 / 21 (81.0%) | 4 |
| Virtuosity Drums — Ride primary display | 1 / 21 (4.8%) | 20 |
| Virtuosity Drums — Rim detected | 18 / 28 (64.3%) | 10 |
| Virtuosity Drums — Rim primary display | 5 / 28 (17.9%) | 23 |

## ENST-Drums independent acoustic baseline

Source: `build/enst_drums_measurement.log`. The direct Zenodo archive is checksum-pinned and stored in external `InstrumentSamples`; the fixture selects one `dry_mix` rendering per declared performance, never duplicate microphone channels. It treats the three declared Rim-shot/Cross-stick performances as Rim even though their source event tokens use `sd`.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| ENST-Drums — Tom detected | 27 / 30 (90.0%) | 3 |
| ENST-Drums — Tom primary display | 25 / 30 (83.3%) | 5 |
| ENST-Drums — Ride detected | 14 / 16 (87.5%) | 2 |
| ENST-Drums — Ride primary display | 12 / 16 (75.0%) | 4 |
| ENST-Drums — Rim detected | 2 / 3 (66.7%) | 1 |
| ENST-Drums — Rim primary display | 2 / 3 (66.7%) | 1 |

## 0x808 independent Rim baseline

Source: `build/0x808_rim_measurement.log`. The reproducible 0x808 acquisition stores its source and generated labelled manifest under `InstrumentSamples`; this replay uses its royalty-free/public-domain drum-machine one-shots.

| Metric | Accurate / total | Remaining |
| --- | ---: | ---: |
| 0x808 Rim detected | 6 / 7 (85.7%) | 1 |
| 0x808 Rim primary display | 2 / 7 (28.6%) | 5 |
| Decision | no source-neutral Rim selector is enabled | preserve protected acoustic one-shot primary labels |

### Cross-source Rim selector veto

Source: `build/rim_primary_candidate_audit.txt`. Candidate `rim_from_snare_cross_source_v1` was mined from the independent 0x808 and Virtuosity Rim→Snare misses, then simulated against every cached protected one-shot row.

| Metric | Samples | Decision |
| --- | ---: | --- |
| Candidate matches | 708 | offline only |
| Rim primary repairs | 45 | promising local evidence |
| Protected correct-primary regressions | 240 | reject |
| Foreign Rim promotions | 210 | reject |

### Retained cross-acoustic Tom primary recovery

At final non-generated one-shot arbitration, this promotes Tom only when Snare currently leads, Tom and Rim are both at least 0.98, mid energy is at least 0.76, and the Snare/Kick shape-score ratio is at least 2.144. The selector was mined with required positives in both acoustic corpora and zero cached protected side effects.

| Replay | Accurate / total | Change / protected outcome |
| --- | ---: | --- |
| 29k Drums — Tom primary display | 271 / 500 (54.2%) | +2 / 500 from the preserved baseline |
| Virtuosity Drums — Tom primary display | 47 / 48 (97.9%) | +2 / 48 from the preserved baseline |
| Full one-shot diagnostic replay | 1949 / 2861 Tom primary (68.1%) | +1 matching Tom row; no new gate failure. Its separate Ride baseline remains 316 / 352 (89.8%), below the unchanged 90% floor. |
| HF and IDMT protected replays | 2 / 2 passed | no affected primary-count regression |

## BabySlakh drum-validation checklist

BabySlakh is an independently rendered 16 kHz multitrack corpus with aligned per-stem MIDI. It strengthens calibration coverage but cannot replace real-recording evidence.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Store checksum-verified archive in InstrumentSamples | 1 / 1 (100.0%) | 0 | archive moved only after the official MD5 passes |
| Extract archive safely in InstrumentSamples | 1 / 1 (100.0%) | 0 | traversal-safe extractor output |
| Inspect and prepare all published drum full mixes | 20 / 20 (100.0%) | 0 | metadata-selected drum MIDI with linked mix WAV |
| Measure rendered full-mix drum baseline | 1 / 1 (100.0%) | 0 | analyzer_egmd x/total summary |
| Re-evaluate a drum change across real MDB/STAR and BabySlakh | 1 / 1 (100.0%) | 0 | independently measured retain-or-change decision |

## Real-drum Tom/Ride/Rim coverage checklist

The full one-shot gate has broad category counts, but its weak Tom/Ride/Rim results need independent real-acoustic replication before a class-specific runtime rule can be trusted. 29k Drums independently covers Tom and Ride; the pinned CC0 Virtuosity Drums fixture adds all three classes. FSD50K's fixed 200-class vocabulary has no Rimshot label. The Commons candidate is checksum-verifiable and openly licensed, but its source supplies no per-roll timestamps, so it cannot yet count as accuracy evidence.

| Work item | Complete / total | Remaining | Evidence required |
| --- | ---: | ---: | --- |
| Checksum-verified 29k Drums archive inspected for Tom/Ride labels | 1 / 1 (100.0%) | 0 | inspection follows successful Zenodo MD5 and ZIP integrity verification |
| Measure independent 29k Drums Tom/Ride baseline | 1 / 1 (100.0%) | 0 | prepared, labelled acoustic one-shot fixture and analyzer x/total results |
| Record all 29k Tom/Ride primary decisions for candidate evaluation | 1 / 1 (100.0%) | 0 | verbose current and missed primary labels become a reproducible TSV; selectors still need cross-corpus runtime replay |
| Measure CC0 Virtuosity Drums Rim/Tom/Ride baseline | 1 / 1 (100.0%) | 0 | Tom primary 47 / 48 (97.9%); Ride primary 1 / 21 (4.8%); Rim primary 5 / 28 (17.9%) |
| Measure independent 0x808 royalty-free/public-domain Rim baseline | 1 / 1 (100.0%) | 0 | Rim detected 6 / 7 (85.7%); primary 2 / 7 (28.6%) |
| Measure MDB annotated side-stick/Rim event coverage | 1 / 1 (100.0%) | 0 | 0 / 1 (0.0%) detected; calibration evidence only, not independent replication |
| Screen FSD50K fixed vocabulary for licence-compatible Rimshot clips | 1 / 1 (100.0%) | 0 | no audio transfer: 0 labelled rows, 0 isolated candidates, 0 permissive-licence candidates |
| Verify licence-free Rimshot recording candidate | 1 / 1 (100.0%) | 0 | checksum, source label, licence, and 4 stated rolls; 0 per-roll timestamps supplied |
| Measure checksum-pinned isolated real Rimshot | 1 / 1 (100.0%) | 0 | detected 1 / 1; Rim primary 0 / 1; Snare primary 1 / 1 |
| Measure separately sourced isolated real Rimshot | 1 / 1 (100.0%) | 0 | detected 0 / 1; Rim primary 0 / 1; Snare primary 1 / 1 |
| Measure third independently sourced isolated Rim Shot | 1 / 1 (100.0%) | 0 | detected 0 / 1; Rim primary 0 / 1; Snare primary 1 / 1 |
| Broaden independent Rim replication beyond one isolated recording | 4 / 4 (100.0%) | 0 | three checksum-pinned, independently credited sources: Rim detected 1 / 3, primary 0 / 3, Snare primary 3 / 3; ENST-Drums direct archive contributes 2 / 3 (66.7%) Rim primary across its declared dry-mix Rim-shot/Cross-stick performances |
| Assess optional E-GMD real-drum Rim data | 0 / 1 (0.0%) | 1 | deferred at user direction: its gate requires a user-provided local E-GMD root and this repository has no direct downloader |

Refresh with `make update-detection-accuracy-report`. Whenever a verified detection metric changes, update this report in the same commit.
