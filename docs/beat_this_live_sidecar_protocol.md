# Beat This! live sidecar protocol

The Beat This! model remains disabled by default and is not started by the OBS plugin. This protocol defines the only permissible route for a future opt-in backend, so model loading and inference cannot run in the audio callback.

## Boundary

```text
OBS audio callback → existing bounded analyzer ring → optional worker-owned 20 s buffer
                                                     ↓
                                         persistent sidecar process
                                                     ↓
                                      gated BPM reply or no BPM reply
```

The callback must only copy samples into preallocated storage. It must never spawn a process, wait for the sidecar, allocate model data, import Python, or replace a normal BPM value. The optional worker permits only one outstanding request; a timeout, malformed response, child exit, or late result is discarded and leaves the existing analyzer output unchanged.

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

Otherwise the sidecar emits `status: "gated"` with `bpm: 0.0`. This preserves the interval gate from the causal replay: 23/23 selected Ballroom outputs and 8/8 selected FiloBass outputs were within 8 BPM, with zero observed wrong values. That evidence is still insufficient to enable OBS integration: it must be reproduced by the future worker using this exact protocol and show no wrong displayed BPM across both corpora.

## Model and storage constraints

The process loads one `Audio2Beats` instance at startup. `--runtime-root` and `--model-cache-root` are required; the runner resolves only `cache/hub/checkpoints/beat_this-<checkpoint>.ckpt` beneath that external cache and passes its local filename to the model. A missing or path-like checkpoint name is rejected, so the model library cannot fall back to downloading. The project’s `build/InstrumentSamples` symlink resolves to `/media/kyz/sshflashtor/InstrumentSamples`, so large runtime/model files remain outside the worktree.

## Verification

Run `make test-beat-this-live-sidecar`. It validates packet sizing, clean EOF, rejection of a short window, the 44-interval gate, and an in-memory persistent-stream replay without loading Beat This or playing audio.
