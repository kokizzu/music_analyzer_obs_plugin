# Native routing and note-duration goal

Status: active. The native Piano/Guitar duplicate filter passes its first
integrated gates and is available behind a false-by-default experimental
setting. No default behavior change is promoted yet.

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
