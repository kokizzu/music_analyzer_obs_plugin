# Next detection improvements

The benchmark tooling and exact tempo-scoring optimization are implemented.
Native spectral Voice verification is experimental, disabled locally by default
and not integrated into the published primary analyzer.
The BPM accuracy, chord and drum proposals have not passed their improvement
gates. A cached-data screen is not a live accuracy improvement.

| Area | Work and current evidence | Remaining work |
| --- | --- | --- |
| Three-second BPM | Phase/octave and backbeat trials rejected. Exact arithmetic caching preserves 3,000 scorer cases, including the 64/65-peak cache boundary. A necessary-condition early veto matches 250,000 generated selector cases and is integrated locally. | Additional accuracy gain remains unproven. |
| Native timbre | Pure native 100 ms cepstral extractor and two-stage bounded forest; native inference matches 2,940 capture cases. Local integrated replay removes 81 wrong Voice cells; full single-note audit removes 1,107 with no correct Voice losses. | Clean primary replay has no held-out gain, so integration is not promoted. |
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
make prepare-native-voice-primary
make measure-native-voice-primary
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
0.2398 ms in its first microbenchmark. A later warm/cold comparison measures
0.2621/0.2983 ms at 48 kHz. The integrated hook constructs geometry only when a
proposal exists, once per window, and retains no audio history. A rate-change
regression verifies that previous extractor geometry/audio cannot affect output.

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

The four complete single-note shards (`7e60b84bac2a`, `8aab17c83b5a`,
`49ea5c7201bc`, `23e0287208bb` under `build/next_detection/integrated-voice-*`)
cover all 2,212 clips and 176,960 windows. They remove 1,107 wrong Voice cells:
579 Piano, 351 Guitar, 58 Bass, 93 Other and 26 wrong pitches in vocal clips.
Correct Voice losses, unscored removals, any-row pitch losses, surviving Voice
cell modifications and unrelated-output changes are zero in all four shards.
These are regression results, not a new unseen-instrument generalization claim.
The default audio-independent model test includes all eight previously failing
correct Voice cases as frozen negative vectors.

`make test-analyzer-internal` passes all 1,029 existing checks with the native
feature disabled, as configured by default. Programmatic experiments set
`AnalysisSettings::experimental_keyboard_voice_suppression = true`; existing
local product hosts retain their defaults. The published primary settings do
not contain this flag. The local flag changes Voice display routing
only when the same pitch remains visible in Keyboard. It does not claim to
identify every instrument's timbre, and source separation is not involved.

`build/sustained_piano/7db7c29c6cde/report.json` scores the first 30 seconds of
an aligned MAPS solo-piano recording: 98.70 held-note-seconds, 13.45 missing in
every row and 50.10 missing from Keyboard. Guitar and Voice are active for
28.45 and 28.40 seconds with diagnostic rows enabled. These row-duration
measurements expose routing confusion hidden by any-frame recall. Unsupported
pitch duration uses MIDI pedal plus 300 ms grace; it is not an acoustic
false-note claim because MIDI cannot establish actual decay audibility.

The clean primary replay (`build/next_detection/integrated-voice-d5693aa017da/report.json`,
primary source export `build/primary_voice_trial/45b669562701`) compiles the
same hook on commit `dc63d31e08ce951b91eea9a2d4723c47c291954f` without the
older dirty analyzer work. It completes all 7,435 windows, removes two training
wrong Voice cells, preserves correct notes and unrelated outputs, but produces
zero held-out gains. It therefore fails promotion. The larger local gains must
not be attributed to the published analyzer. This is a concrete dependency on
the older unpublished detection behavior, not permission to commit that work.

Publication stages explicit measurement/library paths. The research hook is
stored as `src/experimental_keyboard_voice_hook.inc`, excluded from production.
The primary trial script injects it only into a plain temporary source export;
it never edits the working analyzer or creates a branch/worktree. It links the
primary branch's existing Basic Pitch objects against one already installed
SDK header and downloads no dependencies. A paired primary replay is expected
to fail its improvement gate until a useful change is demonstrated.

The early PCM veto still depends on older unpublished correction work and
remains local; the independent exact scorer optimization is published. Capture
targets that require the older unpublished corpus harness remain local. Public
unit tests need no audio corpus; research screens require the corresponding
existing local data and NumPy environment. Chord/drum/timbre promotion remains
unfinished; this report does not claim five successful detection improvements.
