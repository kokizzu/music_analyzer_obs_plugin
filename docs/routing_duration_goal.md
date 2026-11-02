# Native routing and note-duration goal

Status: active. No new detection behavior is promoted yet.

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
these targets. The objective is not complete merely because these measurements
and tests pass.
