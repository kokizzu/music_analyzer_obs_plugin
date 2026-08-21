# Beat This! live sidecar protocol

The Beat This! model remains disabled by default. The OBS filter now exposes an experimental opt-in backend, but it cannot start unless the user supplies explicit local paths for Python, this runner, the external runtime, and the external model cache. Model loading and inference never run in the audio callback.

## Boundary

```text
OBS audio callback → existing bounded analyzer ring → two preallocated 20 s buffers
                                                     ↓
                                         persistent sidecar process
                                                     ↓
                                      gated BPM reply or no BPM reply
```

The callback only writes samples into preallocated storage. It never spawns a process, waits for the sidecar, allocates a packet/model, imports Python, or replaces a normal BPM value. The optional worker warms one persistent child after opt-in and permits only one outstanding request. Its stdin is nonblocking and deadline-bounded; a timeout, malformed response, child exit, or late result is discarded. A ready sidecar BPM is used only while the existing analyzer BPM is below its calibrated display threshold, and expires after 25 seconds.

## Packet contract

`scripts/beat_this_live_sidecar.py` accepts a repeated stdin stream of:

| Field | Encoding | Requirement |
| --- | --- | --- |
| magic | 8 bytes: `MAOBT1\0\0` | versioned protocol marker |
| sample rate | little-endian `uint32` | 8,000–192,000 Hz |
| sample count | little-endian `uint32` | exactly `20 × sample rate` |
| audio | little-endian float32 mono samples | finite values only |

It emits exactly one newline-delimited compact JSON record per valid packet on stdout. Human diagnostics go only to stderr, so a client can treat any malformed or missing JSON response as unavailable.

## Display gate

A reply has `status: "ready"` only when all of these are true:

| Condition | Value |
| --- | --- |
| received audio duration | exactly 20 seconds |
| usable Beat This intervals | at least 44 |
| derived BPM | finite and positive |

Otherwise the sidecar emits `status: "gated"` with `bpm: 0.0`. This preserves the interval gate from the causal replay: 23/23 selected Ballroom outputs and 8/8 selected FiloBass outputs were within 8 BPM, with zero observed wrong values. The OBS boundary uses the same packet and reply gate; its model-free persistent-child test sends two exact packets and its static guard verifies callback isolation, normal-BPM precedence, expiry, and bounded I/O.

## Model and storage constraints

The process loads one `Audio2Beats` instance at startup. `--runtime-root` and `--model-cache-root` are required; the runner resolves only `cache/hub/checkpoints/beat_this-<checkpoint>.ckpt` beneath that external cache and passes its local filename to the model. A missing or path-like checkpoint name is rejected, so the model library cannot fall back to downloading. The project’s `build/InstrumentSamples` symlink resolves to `/media/kyz/sshflashtor/InstrumentSamples`, so large runtime/model files remain outside the worktree.

## Verification

Run `make test-beat-this-live-sidecar test-measure-beat-this-live-sidecar test-beat-this-sidecar-client test-beat-this-obs-sidecar`. These model-free checks validate packet sizing, clean EOF, rejection of a short window, the 44-interval gate, response validation, a C++ persistent-child replay, and the OBS callback/worker safety boundary without loading Beat This or playing audio.

For an offline model replay, run `make measure-beat-this-sidecar-ballroom measure-beat-this-sidecar-filobass`. The harness sends causal, exact 20-second packets to one persistent sidecar child per corpus and logs `ready`, `withheld`, `hit`, or `miss` outcomes. It remains evidence only; the OBS backend stays disabled until explicitly configured in that filter's properties.
