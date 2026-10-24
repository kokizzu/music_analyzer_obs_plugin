# Next detection improvements

All five requested areas are in progress. A cached-data screen is not a live
accuracy improvement, and rejected models are not enabled.

| Area | Work and current evidence | Remaining work |
| --- | --- | --- |
| Three-second BPM | Weighted phase coverage, empty-cell penalty and octave-margin screen reproduces the cached baseline, but loses one correct FiloBass result; rejected. A necessary-condition early veto matches 250,000 generated selector cases and is integrated locally to avoid impossible PCM scans. | Verify integrated timing/output preservation and find an additional accuracy gain. |
| Native timbre | Log/ratio features with onset, decay, stability and harmonics, grouped by instrument identity for holdout; linear model makes no accepted changes. The bounded forest produces one wrong held-out reassignment and no gains, so it is rejected. | Richer evidence, current-source replay and independent positives before model promotion. |
| Chord ambiguity | Two-frame, defining-tone/chroma reranking gains three correct frames but introduces three wrong labels across MAPS/MAESTRO; rejected. | A rule that preserves correct chords and avoids new wrong labels, with transition-delay measurements. |
| Drum discrimination | Native band/body/shape classifiers trained on the full one-shot capture and tested on independent 29k/Virtuosity samples; linear and nonlinear models make no accepted changes. | Capture richer attack/decay evidence, then validate a useful rule across protected kits and full mixes. |
| Sustained playback | Complete WAV replay, 100 ms windows / 50 ms hops, throughput and paced modes; reports p50/p95/p99/worst time, CPU, peak-RSS growth, deadline misses, transitions and one-hop reversals. First three-corpus fingerprinted throughput capture completes; deadline misses occur under concurrent load. MIDI-supported duration scoring is implemented and measured on MAPS. | Finish paced replay and broaden labelled duration coverage. |

Commands:

```sh
make test-next-detection
make test-tempo-candidate-gate
make test-sustained-analyzer
make screen-next-bpm
make screen-next-chord
make screen-next-timbre
make screen-next-drums
make screen-next-timbre-forest
make screen-next-drums-forest
make measure-sustained-analyzer
make measure-sustained-analyzer-paced
make test-sustained-piano
make measure-sustained-piano
```

The screens use existing local cached TSVs. NumPy classifiers use the existing
`.separator-venv`; these targets do not install dependencies or fetch audio.
Their reports in `build/next_detection/` pin the inputs and script. Historical
captures are screening evidence only. Native-owner classification is not the
same as integrated note-grid accuracy.

The sustained driver selects the first recording in each existing Ballroom,
FiloBass and GTZAN fixture manifest, without consulting analyzer results. It
never loops short clips. Source, headers, executable and audio are fingerprinted;
per-mode reports are checkpointed and cached frames must match their hashes.
The direct engine does not assign product-host sequence numbers, so independent
hop indices and exact source-sample endpoints verify coverage. Half-sample hops
use the same round-half-up rule as C++, including 22.05 kHz. Missing correction
support in older primary-branch headers is explicitly reported as native-only.

Throughput runs may overlap compilation or classifier work and do not establish
isolated hardware latency. Label transitions and A-B-A reversals are stability
signals, not automatically errors. This native benchmark does not measure model
freshness, physical capture queues or ground-truth false-note duration.

Fingerprint-capture `build/sustained_analyzer/f5c86bd58fec/report.json` completes
602 Ballroom, 6,748 FiloBass and 599 GTZAN windows in each mode. Peak-RSS growth
is zero for these runs. Under concurrent machine load, corrected-mode deadline
misses are 0, 79 and 2 respectively; native misses are 0, 1 and 5. These timings
do not demonstrate an isolated speedup from the early veto.

`build/sustained_piano/7db7c29c6cde/report.json` scores the first 30 seconds of
an aligned MAPS solo-piano recording: 98.70 held-note-seconds, 13.45 missing in
every row and 50.10 missing from Keyboard. Guitar and Voice are active for
28.45 and 28.40 seconds with diagnostic rows enabled. These row-duration
measurements expose routing confusion hidden by any-frame recall. Unsupported
pitch duration uses MIDI pedal plus 300 ms grace; it is not an acoustic
false-note claim because MIDI cannot establish actual decay audibility.

Publication is restricted to explicit new measurement/library paths and a
single Makefile include. The existing dirty analyzer includes unpublished PCM
correction work absent from the primary-branch header. Its small new early-veto
integration cannot be published independently without also including that
pre-existing work, so it is preserved locally pending safe dependency scoping.
