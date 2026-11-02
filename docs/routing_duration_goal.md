# Native routing and note-duration goal

Status: active. Corroborated native Guitar/Voice duplicate suppression is now
enabled by default on the validated native input geometry. Gains are modest;
attack, early-release and lingering-note improvements remain unfinished.
The earlier single-window experiments stay disabled.

Improve native instrument routing and note duration on the verified upstream
primary branch. Reduce wrong Guitar/Voice routing on solo piano; improve
missed attacks, early release and lingering notes using sustain-aware MIDI.
Require recording-disjoint evaluation, preserved correct notes/unrelated
outputs and acceptable latency before promotion. Preserve unrelated user work.

## Current evidence

The unmodified primary source and vendor trees are exported into a plain build
directory, with no branch or worktree. The replay uses FullMix, native default
settings, 100 ms windows, 50 ms hops and a fixed generic source name. Basic Pitch
is not enabled. The existing local runtime SDK supplies compile-time headers;
the driver downloads no dependencies and changes no running application.

Baseline: `build/routing_duration_baseline/f3c7f7a446eed267/report.json`.
Build: `build/routing_duration_primary/02001c66f49dc729/build.json`.
Eight original-rate PCM prefixes (60 seconds each), 9,600 windows total.
Audio, MIDI, manifests, PCM prefixes, executable, compiler, SDK headers and source
trees are fingerprinted. Per-recording checkpoints support resumption.

Training uses the first four records in `build/maps_piano_samples`; held-out
evaluation uses records 5–8 in `build/maestro_real_samples`. Selection precedes
inspection of analyzer results. Audio/MIDI hashes and PCM prefix hashes are
checked against leakage. Both fixtures use the MAPS preparation schema; directory
names alone do not prove independent corpus provenance. The held-out split is
recording-disjoint, not a claim of verified independent dataset provenance.

| Metric (note-seconds unless stated) | Training, 240 s audio | Held out, 240 s audio |
| --- | ---: | ---: |
| Held-key support, union per MIDI | 810.072 | 410.081 |
| Missing from Keyboard | 422.279 | 250.659 |
| Missing from every row, including Ambiguous | 111.203 | 99.954 |
| Keyboard early release | 92.026 | 42.815 |
| Keyboard internal dropout | 56.000 | 14.950 |
| Guitar display occupancy | 1072.550 | 1197.600 |
| Voice display occupancy | 29.700 | 51.500 |

Guitar is active during 44.9–58.25 seconds per one-minute piano excerpt. All
baseline windows finish within their 50 ms hop budget; measured per-recording
p99 times are 20.03–25.01 ms. This is a direct-engine throughput benchmark on a
shared machine, not proof about physical capture queues or isolated latency.

Candidate evidence: `build/routing_candidate_evidence/42e25eb544a48fc7/report.json`.
The exporter replays every endpoint against the same primary object code and
verifies exact notes in all six rows, chord labels, drum labels, BPM and BPM
confidence against the baseline. All eight recordings pass. It exports native
ownership/onset/harmonic features and current-window cepstra at full precision;
these diagnostics do not modify the analyzer.

Training-only inspection finds 1,532 Guitar and 61 Voice candidate cells with
an independently visible Keyboard pitch, Keyboard score >= .9, Guitar/Voice
scores <= .05 and no vocal profile. These are opportunities to investigate,
not a safe suppression rule: real Guitar/Voice controls have not passed a new
rule yet. Another 5,132 Guitar and 255 Voice displayed cells lack a same-MIDI
raw candidate; recovery/mirror provenance needs separate investigation.

## Scoring semantics and limits

Display state becomes available at its causal analysis endpoint and persists
until the following hop. Startup delay counts; no historical output is moved
backward. Duration scoring merges overlapping support for the same MIDI and
separates initial gaps, internal dropouts, early releases and entirely missing
held spans. It includes the Ambiguous row in any-row recall.

CC64 release extends annotation support, with an explicitly recorded 300 ms
release grace. Unsupported duration is **annotation-unsupported duration**:
MIDI cannot establish whether acoustic decay is audible. It is not reported as
ground-truth acoustic false-note duration.

The initial attack metric matches absent-to-present **display pitch** transitions
to MIDI note-ons, one-to-one, within 150 ms and before key release. It does not
measure envelope re-articulation while a note remains lit. Native onset/level
evidence and audio/MIDI alignment must be checked before classifying those
cases as missed acoustic attacks. Right-censored attacks are excluded, and the
scorer never invents a second attack from a continuously visible pitch.

## Required remaining work

- Verify alignment and capture relevant native onset/display evidence for
  re-articulated notes before interpreting attack errors.
- Calibrate routing candidates using training piano and real Guitar/Voice
  controls; freeze thresholds before held-out evaluation.
- Implement and regression-test native routing and duration improvements.
- Replay actual primary-branch candidate code; preserve correct instrument
  notes, other grids/chords/drums/BPM and duration coverage.
- Check recording-disjoint gains and latency, then promote only validated
  behavior. Keep rejected trials disabled and publish relevant validated code.

Commands:

```sh
make test-routing-duration-score
make build-routing-duration-primary
make measure-routing-duration-baseline
make capture-routing-candidates
```

The scorer has ten focused regression tests. No model is trained or enabled by
the four baseline targets above. The objective is not complete merely because
these measurements and tests pass.

## Controls, alignment and native candidate

`build/routing_controls/84b9eb144888ea8d/report.json` contains 150 original-rate
controls: 48 NSynth Guitar clips, all 22 available NSynth Voice clips and 80
recording-distinct human Voice excerpts. Guitar identity and singer groups are
split before evaluation. The bare Keyboard-duplicate rule would lose 340
correct Guitar cells and 19 correct Voice cells, so it is rejected.

`build/routing_polycontrols/8fc4e60bf6c3a79b/report.json` adds 32 Guitar-TECHS
P1 clips for fitting, 32 P2 clips for held-out testing and 16 acoustic chord
recordings. Every Guitar-row pitch is conservatively protected, even if absent
from note annotations. The early 53-feature model makes 64 protected row
changes; these must not all be called verified correct-note losses. A native
Guitar-owner veto leaves 15 changes, including six annotation-supported notes
and nine unverified pitches. Both variants are rejected. The strict all-native-
candidates-must-be-Keyboard-or-Bass veto gives no held-out piano gain and is
also rejected.

`build/routing_guitarset_controls/9801a45ca6c823e8/report.json` adds actual
ten-second chordal Guitar performances: performers 00/01 for fitting, 02 for
negative cutoff calibration, and 05 held out. Performers 03/04 were reserved
until the expanded evaluation below; they must not subsequently be described
as untouched validation data for a revised model.
The improved model combines 29 native descriptors, 24 current-window cepstra
and nine current-window ownership-context features. It fits 1,787 cells, with
133 separate negative-calibration cells; held-out observations do not set its
weights or cutoff. The cutoff is .9. Near split boundaries the lower of both
branches is used, with uncertainty `(1 + abs(value)) * 1e-10`.

Canonical weights: `models/piano_guitar_verifier.json`, SHA-256
`f5721ff9a0ff45fa45b994fe02f1f99c6f5607db4de0ebedc0a4d3d85759b6d6`.
The generated native forest has 2,004 nodes. C++/Python checks pass 11,012
probability/profile cases from the captured data, with 32 independent-of-audio
frozen vectors for routine tests. Three context tests cover competing Guitar
evidence, candidate-order/history independence and empty-frame markers.

The actual native paired build is
`build/piano_guitar_trial/5423eaeda3f96b38/build.json`. It applies the hook to
primary sources without replacing older worktree edits. With the flag off,
every tested endpoint matches the prior published analyzer. With it on:

| Actual native gate | Windows | Wrong piano Guitar cells removed | Correct Guitar losses / protected chord-row changes |
| --- | ---: | ---: | ---: |
| Eight piano recordings | 9,600 | 1,271 (533 held out) | 0 / 0 |
| 246 single-note, human Voice, recorded-chord and musical controls | 12,819 | Not scored as piano | 0 / 0 |

Reports: `build/piano_guitar_pair/67994976db4bc16f/report.json` (piano) and
`build/piano_guitar_pair/6d370d0731dc86a1/report.json` (controls). Runtime removals
match offline predictions at every endpoint. No surviving Guitar-row cell is
modified; every other note row, chord/root state and drum state compared by the
paired harness is identical. All nine compared tempo values are identical and
no MIDI disappears from the union of rows. No measured before/after call
misses its 50 ms deadline. The experiment uses no external inference worker.

`AnalysisSettings::experimental_piano_guitar_filter` remains `false`. The hook
requires a matching visible Keyboard pitch, no vocal profile, native-only
fusion, and the calibrated 100 ms window / 50 ms hop. It changes only Guitar
display duplication after chord/root analysis; Keyboard note duration and
Voice behavior are unchanged. The same limited insertion is present locally,
and `make test-analyzer-internal` passes all 1,029 existing checks with the
default disabled setting. Remaining older local edits are not published with it.

Alignment audit `build/routing_alignment/6ef01f7387affe42/report.json` compares
spectral novelty with MIDI onset envelopes over each prefix and its thirds.
Whole-prefix peaks are 10–20 ms from zero. This supports absence of a large
systematic offset; it is not independent proof of note-level alignment and
does not correct or shift any labels. Three diagnostic tests cover known
positive/negative offsets, silence and invalid shapes.

Before enabling the native filter by default, extend regression coverage to
the remaining Guitar recordings, untouched piano/performance records, actual
mixed sources where labelled, and the application's 48 kHz input path. Voice
routing and the requested note-duration behavior changes remain unfinished.
Neither these routing gains nor green tests fulfill the full goal by themselves.

## Expanded evaluation and rejected extrapolation

The frozen native implementation was checked against all 346 available NSynth
Guitar clips, preserving the labelled Guitar pitch at all 27,680 original-rate
endpoints. Derived 48 kHz versions cover another 27,680 endpoints, also without
a labelled Guitar-pitch loss. These are resampled copies, not independent
recordings. Reports are under `build/piano_guitar_extensions/`:
`a08d4ff7c59b86cc` (original), `6c86dfbf33340870` and `52c43eb944858288`
(48 kHz shards). No measured enabled call exceeded its 50 ms deadline.

The reserved-performance report `93a449f0b4f656bd` tests eight GuitarSet
performances from players 03/04 and four additional piano recordings, each at
its original rate and derived 48 kHz. It exposes three protected Guitar-row
removals in `03_Jazz3-150-C_comp`, reproduced at both rates (six cells total).
The removed MIDI 54 is absent from that recording's note annotations; these
are **protected row changes**, not six verified correct-note losses. The
predeclared conservative gate nevertheless fails. Do not relax that gate
after observing this recording or enable the filter by default from the
earlier smaller green control set.

`make audit-voice-duration-candidates` screens extrapolating the frozen model
to Voice duplicates and single-hop Keyboard gaps using training recordings
only. No model or cutoff is refit, and no runtime behavior changes. It finds
14 removable piano Voice cells and no protected Voice loss in the sampled
training controls. Voice needs dedicated held-out and native validation.

The same screen proposes eight Keyboard additions. Causal MIDI scoring shows
only 0.15 seconds of recovered held-key coverage and 0.10 seconds of added
annotation-unsupported duration. Reject this gap rule as a runtime fix.
Three regression tests ensure repairs cannot extend themselves, require the
original preceding Keyboard pitch and current Guitar support, and require a
matching visible Keyboard pitch for Voice suppression.

Use `make inspect-routing-replays` for authoritative process inspection in the
command environment. A process inventory from another tool runtime cannot
establish that a replay has stopped. `make verify-routing-extensions` rechecks
every saved endpoint, hash, removed pitch, protected loss and unrelated-state
gate before publishing this negative evidence. The broader goal remains
active: Voice and duration improvements are unfinished.

Identical replay selections now use a nonblocking process lock. A tool-runtime
inventory error initially caused overlapping runs and five TSV hash mismatches;
the exact affected entries were previewed, their checkpoint backed up, and
only those entries invalidated for replay. No mismatched result is accepted by
the publication verifier. `plan-routing-replay-repair` and
`apply-routing-replay-repair` preserve the reviewed selection and rollback copy.

## Voice native replay and duration tracing

The frozen forest was screened on Voice duplicates without refitting or
changing its cutoff. `make evaluate-voice-duplicate` reports 16 training and
83 held-out piano Voice cells removed. Every labelled NSynth Voice pitch and
every VocalSet Voice-row pitch is protected. The diagnostic family predicate
now uses the actual `vocals` identifier; a regression test covers both
NSynth pitch labels and conservative protection of all human Voice pitches.

An isolated primary export adds only the disabled
`experimental_piano_voice_filter` setting and Voice hook. It does not replace
the dirty working analyzer or modify the published primary analyzer. Build:
`build/piano_voice_trial/6c412eed26b1221e/build.json`. Native reports:

| Voice replay | Windows | Removed Voice cells | Protected Voice-row changes |
| --- | ---: | ---: | ---: |
| Eight piano performances | 9,600 | 99 (83 held out) | 0 |
| Existing 246 controls | 12,819 | 0 | 0 |
| 164 extended cases | 18,155 | 53 | 1 |

Reports are `build/piano_voice_pair/79e637eb626694e5/report.json`,
`build/piano_voice_pair/8ede7313ac105261/report.json`, and
`build/piano_voice_extensions/ebc264a1f5031e97/report.json`. Disabled output
matches primary evidence; actual removals match offline predictions wherever
candidate captures exist. Other rows, chords, drums, nine tempo values and
surviving Voice cells are unchanged; no pitch leaves the union of rows. No
measured enabled call misses 50 ms.

The expanded set includes derived 48 kHz versions of all 102 Voice controls,
36 real MIR-1K mixtures, the reserved Guitar/piano cases at both rates, and a
continuous 60-second MedleyDB mixture at original and derived rates. All
mixture Voice rows are preserved, including pitches absent from incomplete
annotations. One 48 kHz VocalSet control loses a protected MIDI 77 cell.
The control's representative labelled pitch is MIDI 53; this is a conservative
protected-row failure, not a proven fundamental loss. The predeclared gate
fails and the candidate is not enabled or integrated into primary.

`make capture-routing-regression-evidence` captures native features for every
observed protected-row regression, with exact disabled-output parity. The
proposed three-hop consensus requires three consecutive same-MIDI eligible
forest decisions. At 100 ms / 50 ms, first and third windows do not overlap.
It resets on a missing decision and between recordings. Offline
`build/routing_consensus_evaluation.json` retains 54 Guitar and nine Voice
held-out piano removals and makes no protected-row change in the existing
controls or known regressions. This is **not native validation**. The observed
failures are regression cases; fresh recording-disjoint controls are required
before promoting a revised implementation. Three tests cover confirmation,
gaps and independent pitch histories.

The duration-specific recovery model fits 370 training rows, including 47
fully held missing-Keyboard cells, with 106 separate negative calibration
rows. Its frozen .95 threshold admits no changes, so it is rejected rather
than called an improvement. `build/keyboard_recovery_evaluation.json` preserves
the model and split evidence. Three tests cover physical eligibility,
nonfinite/profile rejection and causal next-hop label coverage.

`make trace-primary-duration` instruments only an exported primary source
copy to capture Keyboard grids before smoothing, immediately after smoothing,
and after postprocessing, together with tracking envelopes and hit/miss
counts. Every final note row, chord, drum and exported tempo value matches
the original baseline at all 3,600 training endpoints. Trace report:
`build/primary_duration_trace/954041e8c8c9eb7f/report.json`.

| Training performance | Missing held time: raw absent | Confirmation | Postprocessing | Unsupported duration: raw / smoothed / final |
| --- | ---: | ---: | ---: | ---: |
| 1 | 115.11 s | 4.06 s | 4.69 s | 107.66 / 195.08 / 398.80 s |
| 2 | 102.54 s | 4.34 s | 4.17 s | 163.38 / 248.18 / 598.19 s |
| 3 | 74.11 s | 3.94 s | 3.70 s | 93.38 / 184.35 / 402.63 s |

Smoothing-selection loss is zero in these traces. These are causal MIDI
annotation measurements, not acoustic-decay truth. They locate larger errors
before smoothing and in postprocessing; globally lengthening release is not
supported by this evidence. Intersecting the strong-native/Guitar-supported
recovery candidates with surviving smoothed cells yields no training changes
(`build/keyboard_tracking_recovery_audit.json`), so that shortcut is also
insufficient. The full routing, attack and duration goal remains active.

## Promoted native temporal corroboration

`AnalysisSettings::native_piano_duplicate_consensus` is now `true` by default.
It uses the frozen forest and cutoff above, without refitting. A pitch must
remain visibly duplicated in Keyboard and Guitar/Voice, with an eligible
current-window forest decision, for three consecutive analysis hops before
the foreign-row duplicate is removed. Missing predictions, disabled/ineligible
frames, dropped audio, unfinished analysis, source changes, format changes and
engine resets break corroboration. Per-pitch histories are independent and
counters saturate. Keyboard pitches/envelopes are never changed by this filter.

The production path is restricted to native FullMix, 100 ms windows / 50 ms
hops, and 16/44.1/48 kHz input. It is bypassed when Basic Pitch fusion or the
older single-window Guitar experiment is explicitly enabled. Setting
`native_piano_duplicate_consensus = false` restores the original display path.
The older Guitar experiment remains false; the failed single-window Voice and
alias experiments are not integrated into production.

The cached native build is `build/routing_consensus_trial/398797777fb6e1fa`.
Its current-window cepstral extractor retains FFT/filter geometry per engine,
not a history used for classification. Thirty-two exact cold/warm parity
cases cover all supported rates, rate switches and invalid input. Native
consensus tests cover confirmation, reset, missing/dropped/unfinished frames,
independent pitches and counter saturation.

| Actual native gate | Cases | Windows | Guitar / Voice duplicate cells removed | Protected changes |
| --- | ---: | ---: | ---: | ---: |
| Original piano split | 8 | 9,600 | 127 / 9 (held out: 54 / 9) | 0 |
| Original controls | 246 | 12,819 | 0 / 0 | 0 |
| Extended regression and fresh cases | 260 | 30,175 | 63 / 8 | 0 |

Paired reports: `build/routing_consensus_pair/e63350f9b5113f8b/report.json`
and `31e4706686b5b160/report.json` in the same parent. Extended plan and both
shards: `build/routing_consensus_extensions/3aa507e9ead66390/`. The extended
plan includes 96 fresh cases: four additional piano performances, four
previously unused GuitarSet player-05 recordings, and two unused source
recordings per each of 20 singers, each at original and derived 48 kHz.
Voice selection excludes source recordings from prior captures, not merely
adjacent segments. Derived versions are not counted as independent recordings.
Fresh piano cases remove 14 Guitar cells at each rate; fresh Voice gain is zero.

All 52,594 paired endpoints preserve unrelated note grids/chords/drums and nine
compared tempo values; surviving foreign-row cells are identical and no pitch
leaves the union of rows. Actual decisions equal offline three-hop decisions
where native feature captures exist. Every enabled call in the cached-build
quality replays finishes within 50 ms. Gains are deliberately reported as
small routing improvements, not resolution of the larger baseline errors.

The uncached prototype's control run records one 54.6 ms wall-time call and
its five-pass latency test fails the predeclared 2 ms p99 CPU-difference gate
(2.1535 ms). Both failures remain recorded. The cached implementation passes
the unchanged gates in `build/routing_consensus_latency/33f4c14f94b8e79e/`:
1,000 calls, 17.6544 ms wall p99, 18.2782 ms maximum, 18.2279 ms maximum thread
CPU, 0.0717 ms mean added CPU, 1.9436 ms p99 added CPU, and zero deadline misses.
No conclusion about the original outlier's CPU cause is inferred from repeats.

Prospective primary sources with the real default-on constructor are compiled
and replayed at `build/routing_consensus_rollout/682b938120772cd4/`. All 1,200
endpoints match the validated explicit-on reference, including its 29 Guitar
and eight Voice removals. Publication stages these tested primary source blobs
instead of the older dirty analyzer. The limited hook is also merged into the
working analyzer; its 1,029 existing internal checks pass. Older working edits
remain intact and are not included in this publication.

### Alias visibility experiment: regression fixed, no duration gain

The focused primary regression reproduces an invisible Keyboard cell becoming
a visible lower-octave alias. A Keyboard-only, parameter-gated wrapper blocks
that resurrection and preserves the visible-source case. The isolated native
candidate is `build/keyboard_alias_trial/89c9f41afdc094e2/`; its regression
test passes. The baseline demonstration target intentionally fails before
that experimental fix.

However, causal training replays in
`build/keyboard_alias_measurement/5bcd43eafc4fc573/report.json` change no note
sets or durations in any of three performances. An earlier claim of changed
surviving cell levels in 1,043 frames is withdrawn: that counter incorrectly
compared every duplicate-MIDI cell with every other duplicate. A focused
identity regression exposes the error; the corrected comparator matches the
cell multiset one-to-one and tolerates row permutation. The independent
note-set and duration results remain zero. Therefore the duration gate fails: this is not a
measured timing improvement. No held-out data is consulted to rescue this
trial, and the wrapper/flag is not integrated into production. Attack,
premature-release and lingering-note behavior improvements remain required
for completion of the active goal.

### Low-note duration attribution and frozen experimental guard

`make trace-keyboard-stages` observes post-smoothing mutations in an exported
primary analyzer. Its 3,600 training endpoints exactly reconstruct primary
output. The late low-Keyboard recovery writer contributes 772.64 seconds of
annotation-unsupported duration while recovering 9.70 seconds of held coverage.
Trace: `build/keyboard_stage_trace/034803c68151329e/report.json`.

A focused regression proves that higher harmonics alone can manufacture a low
fundamental. The isolated guard requires direct evidence at least .001 of the
strongest probe level. It vetoes emission of the original pitch-class winner,
preserving ranking and normalization. Rejecting before winner selection exposed
an octave runner-up; that failed trial is retained and covered by a regression.
The guard is experimental and is not integrated into the production analyzer.

Frozen native build: `build/low_keyboard_trial/74626cea8617a3c7/build.json`.
Training removes 1.70 seconds of unsupported duration; calibration removes
2.20 seconds. The recording-disjoint held-out split removes only one 50 ms
cell. Correct held/pedal-supported duration, matched attacks, surviving cells,
unrelated grids and tempo remain unchanged. Reports under
`build/low_keyboard_measurement/`: `fee0dc0e64085c38` (training),
`7f84fa46b6edbbf9` (calibration), `7c9cd886327aae31` (held out).

All four shards of `build/low_keyboard_controls/268291bdcd67a2de/` pass:
1,154 original/derived cases, including 324 labelled low-note samples at two
rates and the prior instrument/music suites. There are no protected-note
losses, added Keyboard pitches, unrelated changes or 50 ms deadline misses.
Derived rates are not independent recordings. This preservation result does
not make the very small held-out piano gain a solution to duration accuracy.

Training-only release-grace screens add unsupported duration and remain
rejected (`build/keyboard_grace_audit.json`). A separate causal Hann-window
frequency-projection screen examines longer low-frequency evidence. Its best
loss-free training configuration removes 56.55 seconds of unsupported display,
using a 400 ms window, .01 normalized floor, latched fundamental-or-third
evidence and three prior original-display frames. This is offline evidence,
not a native or held-out result. Report:
`build/low_keyboard_coherence/dc5f99cb5044a9d7/report.json`.

### Native coherence trial: held-out preservation failure

The isolated native implementation keeps 400 ms of causal audio, checks exact
100 ms / 50 ms overlap, and clears history on source/format resets, changed
drop counts, missing/invalid input, unfinished analysis or ineligible settings.
The fundamental and third-harmonic projections use Hann weighting, weighted
DC subtraction and RMS normalization. Evidence remains latched only while the
original, unmodified low pitch stays displayed. Suppression applies only to
newly recovered late low cells; detector tracking, ownership, ranking and
normalization stay unchanged. The trial bypasses Basic Pitch fusion.

`make test-low-keyboard-coherence` first reproduces an unsupported persistent
low conjecture and then passes with the causal guard. Additional history tests
cover continuous decay, missing fundamentals, absence, exact-overlap drop
changes, unfinished frames, nonfinite input and rate switches. Both targets
operate independently of the production analyzer.

Build: `build/low_keyboard_coherence_trial/853fb60c971cb873/build.json`.
Training native replays reproduce the per-recording offline aggregate metrics exactly: 56.55 seconds
of unsupported display removed with no held/pedal-supported duration lost and
unchanged matched attacks. The maximum native training call is 25.6263 ms.
Separate calibration removes 44.55 seconds without protected losses. Parameters
were frozen before held-out replay. Measurement directories under
`build/low_keyboard_coherence_measurement/`: `42d8b5cd0dd12a07` (training),
`829d090513a0e3e9` (calibration), `54c758308a514c37` (held out).

The four-recording held-out split removes 20.8846 seconds of unsupported
display, but recording four loses 14.5833 ms of genuinely held coverage.
The preservation gate therefore fails. This trial remains disabled and is not
integrated into production; its threshold is not adjusted using that failure.
Attack and early-release improvements remain unresolved.

All 1,154 controls finish in
`build/low_keyboard_coherence_controls/4126b0a9fd9c84d1/` (94,834 endpoints).
Shards zero and one pass; shards two and three fail. Piano performances 13 and
15 each lose one protected cell at original and derived 48 kHz rates. These
are two source performances, not four independent recordings. No unrelated,
surviving-cell or tempo changes, added Keyboard pitches, or deadline misses
are recorded. The extra piano losses independently support rejecting the guard.

`make benchmark-low-keyboard-coherence` preserves the existing 50 ms wall p99,
50 ms maximum thread CPU, 1 ms mean added CPU and 2 ms p99 added CPU gates.
Its five paired passes (1,000 endpoints) measure 18.4351 ms wall p99,
20.5695 ms wall maximum, 20.5194 ms CPU maximum, .2688 ms mean added CPU and
2.3104 ms p99 added CPU. There are no deadline misses, but the last gate fails.
Report: `build/low_keyboard_coherence_latency/b1071b59a4aec0fe/report.json`.
Neither the quality nor performance gate is relaxed to enable this trial.

### First-hit confirmation audit

`make audit-keyboard-confirmation` examines the three training recordings only.
It considers a first raw Keyboard hit that is unconfirmed, unsmoothed and absent
from final Keyboard. A hypothetical confirmation bypass adds 65 matched attacks
and 10.95 seconds of held coverage, but also 32.14 seconds of unsupported
display. Requiring strong native Keyboard ownership/scores still adds 14.57
seconds of unsupported display for only six additional matched attacks.
These simple rules are rejected. Attack counts alone do not justify isolated
display additions. `build/keyboard_confirmation_audit.json` preserves the
per-case raw descriptors and tracking state for further causal analysis; no
held-out data or native behavior is changed by the audit.

### Recording-disjoint first-hit verifier screens

`make evaluate-keyboard-confirmation` fits the existing bounded forest on two
training recordings and evaluates the third, rotating the recording held aside.
It uses causal native descriptors, MIDI number, raw level and envelope; labels
are never inputs. A .95 minimum cutoff plus a margin over fitting negatives
admits no fully-held candidates. Allowing the cutoff to depend only on fitting
negatives produces unsupported additions on the other recordings.

`make capture-joint-pitch` explores a different pitch cue: a nonnegative joint
spectral explanation of all 88 piano pitches, using 106 isolated references
from one acoustic piano identity. The references cover 59 pitches; missing
templates use frequency-axis interpolation from the nearest reference pitch.
Each causal 100 ms performance window is independently resampled to 16 kHz,
Hann-windowed and fitted for 80 fixed multiplicative iterations. The first
three training performances contribute 3,600 windows and 980 first-hit cases.
No performance recording fits the dictionary, and no held-out recording is
used. Batched columns are independent; synthetic tests cover harmonic
competition, simultaneous notes, silence and invalid input.

Capture: `build/joint_pitch/143d517357f2b5c2/report.json`. True held first-hit
candidates have median relative activation .438/.631/.344 in recordings
one/two/three, versus .0023/.0092/.0072 for unsupported candidates. Their ranges
still overlap. This separation is diagnostic evidence, not detection accuracy.

Eight exploratory leave-recording-out screens compare native/joint features,
fully-held/pedal-supported labels, and fixed .95/negative-derived cutoffs.
All are rejected. The strict native pedal-support screen initially appears
safe: three additions recover .15 seconds and two matched attacks without
unsupported additions. Inspecting adjacent original display frames shows all
three would be isolated flashes, rather than a confirmation bridge. A focused
continuity regression now prevents these from passing the screen. The joint
strict pedal variant also adds unsupported duration on recording three.

Reports: `build/{keyboard,joint}_confirmation_evaluation*.json` record all
eight variants, fitting-negative cutoffs, model trees, accepted endpoints and
causal timing scores. These are training screens, not independent test results;
neither outside-instrument controls nor calibration/held-out data is consulted
to rescue the failed candidates. No confirmation bypass or joint fit is
integrated into the runtime. The next investigation must address missing raw
pitch evidence and continuous note reconstruction, rather than isolated
first-hit display additions.

### Continuous joint-fit coverage and frozen release-grace calibration

`make capture-joint-note-coverage` retains all 88 pitch activations at all 3,600
training endpoints: 316,800 estimates. It reuses the fixed isolated-reference
dictionary. Tests prove the exact first-window zero padding and that changing
future audio cannot alter earlier windows at 16/44.1/48 kHz. Capture:
`build/joint_note_coverage/017a9ad67bd36e7d/report.json`.

`make screen-joint-note-coverage` records a training-only grid of 125 rules:
current/latched low-writer removal, two release-grace variants, and recovery
of missing Keys pitches already supported by Guitar and strong native scores.
None of the low-removal or Guitar-supported variants combine benefit with zero
protected loss/unsupported additions. Some release-grace variants pass this
exploratory training screen (`build/joint_note_coverage_screen.json`).

The selected rule requires an already smoothed, confirmed Keyboard note with
at least three raw hits and three prior **unmodified** final visible frames.
It can restore one hop only when the last erasure is same-pitch Other cleanup,
and the current joint fit has relative activation at least .8 and explained
projection at least .3. Restorations cannot sustain their own eligibility.
This rule adds 11 training cells, recovering .366264 seconds of held coverage
with zero unsupported additions. The restored cells extend existing display,
rather than introducing isolated first-hit flashes.

`make calibrate-joint-grace` reproduces that exact training selection and writes
`frozen-training.json` **before** accessing recording-four calibration. Two
independent instrumented primary exports reconstruct all 1,200 calibration
endpoints exactly. Applying the frozen rule offline adds three cells: .084002
seconds of held coverage, including .050000 seconds of internal dropout and
.034002 seconds of premature release. Matched attacks are unchanged and
unsupported additions remain zero. Report:
`build/joint_grace_calibration/83a1aabf4a68fee2/report.json`.

This is a prospective release-recovery hypothesis, not a native implementation
or promotion. Instrument controls, recording-disjoint held-out replay, native
numerical parity and latency remain required. No held-out data is used here.

### Native joint fitter parity

`make test-native-joint-pitch` builds the standalone C++ current-window fitter
in `src/joint_piano_fit.hpp`. It reproduces the reference's linear resampling,
Hann window, 4096-point FFT, three-bin smoothing, normalized projection and
80 simultaneous multiplicative updates. Dictionary and Gram geometry are
configured once; no audio history or predictions are used across calls.
The test loads the frozen dictionary from build artifacts; no dictionary
weights are added to the production binary or repository.

All 316,800 training pitch estimates match the reference within 1.60e-13,
with zero .8/.3 eligibility threshold mismatches. Additional silent/tonal/noise
streams at 16/44.1/48 kHz also match within 1.34e-14, including initially padded
windows. The latest training run measures about .60–.61 ms mean fitting time;
its maximum is 3.44 ms. These are isolated fitter wall times, not analyzer
latency-gate results. `build/native_joint_pitch/current.json` identifies the
input-hashed parity report and raw outputs.

`make test-joint-piano-fit-safety` covers unconfigured use, silence, rate
switches, unsupported geometry, nonfinite PCM and invalid dictionaries. Its
regression exposed a rejected dictionary leaving the old model active; failed
configuration now invalidates the fitter. Dictionary columns must be finite,
nonnegative and normalized. The analyzer does not call this helper yet; native
release integration must preserve cleanup provenance and original-display
history before instrument controls, held-out replay and latency qualification.

### Isolated native release trial: held-out attack regression

`make build-joint-grace-trial` builds a disabled-by-default experiment from
an instrumented primary export. It retains all 93 mutator observations so
the last cleanup responsible for each erasure is known. This diagnostic
observer is not a production integration. The model dictionary is generated
only inside the build directory; primary analyzer sources remain unchanged.

Native history tests prove that only three prior original visible frames can
authorize restoration. Missing pitches, changed drop counts, unfinished calls
and explicit resets break the run. The exported engine wires history reset to
source/format resets and disabled/ineligible frames. Restored frames never
update their own history. Restoration tests cover duplicate
rejection, missing source cells, hidden rows and occupied visible rows.

The first native replay exposed a representational gap in the offline model:
the grid has only three rows per pitch class. The native helper initially also
treated hidden cells as occupied. A regression fixes hidden-cell reuse while
preserving visible cells. Both training and calibration comparisons now apply
the native row-capacity limit; no visible note is evicted to force a restore.
The original full-set parity failure remains recorded in
`build/joint_grace_measurement/f680d08dcd07d8cd/` and `449d02cb4b0231aa/`.

Current isolated build: `build/joint_grace_native/900451015dcecef6/build.json`.
Capacity-aware training restores eight cells and .266264 seconds of held
coverage; calibration restores one cell and .050000 seconds. Three training
and two calibration proposals are blocked by occupied visible rows. There are
no protected losses, unsupported additions, surviving visible-cell changes,
unrelated changes or tempo changes. Reports under
`build/joint_grace_measurement/`: `390d754488cad6be` (training),
`c7f454a3d3626fdd` (calibration).

The exact build, thresholds, capacity rule, source hashes and recording-disjoint
selection are frozen before held-out access in
`build/joint_grace_heldout/frozen-eb001a122070725c.json`.

| Held-out recording | Added cells | Held recovery | Unsupported additions | Matched display attacks before / after |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3 | 0 | 0 | 149 / 149 |
| 2 | 5 | .076042 s | 0 | 112 / 111 |
| 3 | 2 | .029167 s | 0 | 104 / 104 |
| 4 | 0 | 0 | 0 | 130 / 130 |

Reports are in the per-recording subdirectories of `build/joint_grace_heldout/`.
Recording three reduces premature release by .029167 seconds, but recording
two loses one matched display attack when a gap is filled. Therefore the trial
fails the unchanged attack gate and stays disabled. Recordings one/four also
fail the per-recording benefit requirement, with no held recovery; these are
distinct from the attack regression. No held or pedal-supported duration is
removed, and no unrelated/surviving visible-cell or tempo changes occur. Maximum
held-out analysis wall time is 26.0785 ms, but a full latency qualification and
outside-instrument preservation suite are not run for this rejected trial.

The scorer's display-onset count does not measure rearticulation while a pitch
remains lit. That existing limitation does not erase this failed gate. A future
release rule must preserve attack behavior with independent evidence rather
than treating every confirmed-note erasure as a duration-only gap.
