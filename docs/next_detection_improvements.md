# Next detection improvements

The benchmark tooling and exact tempo-scoring optimization are implemented.
Native spectral Voice verification is experimental and disabled by default.
The BPM accuracy, chord and drum proposals have not passed their improvement
gates. A cached-data screen is not a live accuracy improvement.

| Area | Work and current evidence | Remaining work |
| --- | --- | --- |
| Three-second BPM | Phase/octave and backbeat trials rejected. Exact arithmetic caching preserves 3,000 scorer cases, including the 64/65-peak cache boundary. A necessary-condition early veto matches 250,000 generated selector cases and is integrated locally. | Additional accuracy gain remains unproven. |
| Native timbre | Pure native 100 ms cepstral extractor and two-stage bounded forest; native inference matches 2,940 capture cases. Expanded integrated replay removes 81 wrong Voice cells, including one held-out piano cell, without correct Voice losses or unrelated changes. | Full single-note audit and broader independent piano positives before enabling by default. |
| Chord ambiguity | Defining-tone/chroma reranking introduces three wrong labels; rejected. Strict source-agreement alternative produces no gains; rejected. | No new chord rule is promoted. |
| Drum discrimination | Band/body, attack/decay, periodicity and spectral-shape classifiers tested on independent 29k/Virtuosity samples: no accepted changes. | No new drum model is promoted. |
| Sustained playback | Complete throughput and paced replay with 100 ms windows / 50 ms hops, timing, CPU, RSS, deadlines, transitions and reversals. MIDI-supported duration scoring measured on MAPS. | Broader labelled duration coverage remains useful. |

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
make test-pcm-tempo-score-cache
make test-backbeat-tempo
make screen-backbeat-tempo
make screen-chord-source-agreement
make test-drum-attack-shapes
make evaluate-drum-attack-shapes
make evaluate-drum-spectral-shapes
make test-native-timbre-features
make test-native-timbre-reference
make test-native-mfcc-voice
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

Paced capture `build/sustained_analyzer/026281d2bcc0/report.json` also completes
all three recordings. Native/corrected deadline misses are 2/2, 1/92 and 23/3
respectively. These runs share machine load and do not establish isolated latency.

The exact scorer cache reuses peak square roots and pair weights without changing
candidate or summation order. One 19-peak microbenchmark measures 0.2112 ms for
the frozen reference and 0.1327 ms for cached scoring (about 37% less time).
This is a scorer measurement, not a whole-analyzer latency claim. Native/Python
PCM-energy parity remains valid at fingerprint `native-pcm-parity-d1189877f12e`.

The spectral extractor uses three Hann spectra from the current audio window,
26 mel bands and 12 non-constant cepstral coefficients plus their temporal
differences. It retains rate-dependent geometry, not audio history. Independent
NumPy/native parity covers 18 rate/signal cases. Warm 48 kHz extraction averages
0.2398 ms in its microbenchmark; the integrated hook constructs geometry only
when a proposal exists, so that number is not its complete cold-path cost.

The first Keyboard/Voice forest is a proposal model only: its standalone
integrated audit lost eight correct Voice cells across three protected NSynth
notes. A local-triad guard removed every measured benefit. Neither is enabled
alone. The second-stage spectral verifier blocks those losses and a separate
held-out mixture loss. It uses the frozen parent hash and conservative threshold
rounding in both Python and C++. Canonical models under `models/` preserve
training/input hashes; regeneration does not retrain them.

Expanded paired replay `build/next_detection/integrated-voice-8f6659cc9eaf/report.json`
covers 7,435 windows across piano, singer-disjoint human voices, protected notes,
instrument controls and recording-held-out mixtures. It removes 20 training
piano, one held-out piano, 48 training Voice, three Guitar, five Bass, two Other
and two training mixture wrong Voice cells. Correct Voice losses, unscored
removals, any-row pitch losses and unrelated-output changes are all zero. The
independent gain is only one 50 ms cell; broad timbre accuracy is not established.
Incomplete mixture pitch labels are never counted as wrong-note benefits.

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
