# Basic Pitch Vocal fusion

The OBS filter has an optional Basic Pitch-assisted Vocal display path. It is
disabled by default and never changes native instrument ownership.

When enabled, the analyzer worker appends only the new audio hop to a causal
two-second 22.05 kHz history. A separate Basic Pitch worker loads the model and
performs inference. OBS's audio callback only supplies normal PCM to the
existing analyzer queue; it never loads ONNX, resamples a model window, or runs
inference.

The result may add a Vocal display note only if all of these are true in the
current analyzer frame:

| Gate | Required value |
| --- | --- |
| Basic Pitch confidence | at least 0.80 |
| Native same MIDI candidate | present now |
| Native owner evidence | Guitar with keyboard score at least 0.1817, **or** Keyboard with guitar score at least 0.2059 |

This keeps the native ownership and only mirrors the exact supported note into
the Vocal grid. A stale ONNX result cannot create a note by itself.

## Configure in OBS

1. Run `make install-user`. It installs the validated local runtime and model
   under the OBS plugin's own `data/basic_pitch/` directory.
2. Open the Music Analyzer Filter properties.
3. Enable **Experimental Basic Pitch Vocal fusion**.

The two file properties are optional overrides for another local runtime or
model. Leave them blank to use the guarded installer’s data files. Invalid or
missing paths fail closed: normal native analysis continues, with no model
inference.

The offline owner-evidence replay currently finds 8 correct recoveries and
zero protected false displays across CSD and ESMUC. It is still necessary to
replay a real OBS capture before treating this as a broadly validated runtime
improvement.
