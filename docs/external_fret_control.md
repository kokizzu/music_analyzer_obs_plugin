# External fretboard and root control

The Android app can drive a LiteJam RGB guitar or Fret Zealot fretboard from the analyzer root while accepting root controls from an Akai APC mini mk2 or M-VAVE Chocolate Plus. All four devices are optional and discovered independently.

## Root and scale behavior

- `AUTO` follows the analyzer's most recent valid detected root. An empty/uncertain analyzer frame does not erase the last valid root.
- `MAN` retains a separate manually selected root. Changing the manual root while `AUTO` is active does not silently switch modes.
- Both modes render a major scale in standard guitar tuning. The degree colors are root red, second orange, third yellow, fourth green, fifth cyan, sixth blue, and seventh purple.
- LiteJam receives frets 0-24. Fret Zealot's 15 physical fret positions (musical frets 1-15) are encoded as LED indices 0-14.

The status immediately before BPM shows the effective mode/root and each connection:

```text
AUTO C  LJ+ FZ? APC- MV!
```

`+` is connected, `?` is searching, `~` is connecting, `!` is an error, and `-` is disabled. `LJ`, `FZ`, `APC`, and `MV` mean LiteJam, Fret Zealot, APC mini mk2, and M-VAVE. Long-press anywhere on the analyzer view to turn device autoconnect off or back on; `OFF` appears beside the root while disabled. A normal tap still cycles the audio input.

## APC mini mk2

The upper six physical pad rows contain twelve 2x2 root blocks:

```text
C   C#  D   D#
E   F   F#  G
G#  A   A#  B
```

The bottom two physical rows are one 3x2 semitone-down area, one 2x2 Auto/Manual toggle, and one 3x2 semitone-up area. Root and semitone pads update the retained manual root; use the center pads to make it effective.

The app sends a complete 8x8 LED refresh after connection and after every effective-root/mode change. Each control block has a distinct solid palette color. The requested C/D/E/F/G/A/B glyph is black, and the sharp glyph is white with precedence over both the letter and background. The implementation uses APC notes 0-63 and Akai's full-brightness solid Note On status `0x96`.

Connect the APC mini mk2 by USB. Android must expose at least one MIDI output port for pad input; an input port is additionally required for LED feedback.

## M-VAVE Chocolate Plus

Every M-VAVE MIDI packet is captured before control mapping, regardless of its channel or configured data number. The FootCtrlPlus factory custom controls CC32, CC33, CC34, and CC35 map directly to A, B, C, and D; other Note and CC numbers use modulo positions 0-3. FootCtrlPlus Program Change display values ending in 1-4 map to A-D; display values ending in 5-6 are the E/F combination controls and are captured but do not trigger an A-D action. SysEx is also captured for diagnostics but does not imply a root-control action.

For predictable press-versus-hold behavior, the recommended vendor-editor preset uses momentary Note messages on MIDI channel 1:

| Switch | Note | Short release | Hold at least 600 ms |
| --- | ---: | --- | --- |
| A | 36 | down one semitone | down two semitones (one whole tone) |
| B | 37 | up one semitone | up two semitones (one whole tone) |
| C | 38 | set manual root to G | set manual root to C |
| D | 39 | toggle Auto/Manual | toggle Auto/Manual |

Each switch should send Note On when pressed and Note Off (or Note On with velocity zero) when released. The short action happens on press, while releasing after 600 ms completes the long action. Note-On-only presets therefore still provide repeatable short actions. Notes 0-3 and 60-63 are accepted as alternate four-note banks. Any CC is accepted: a high value followed by a low value provides press/release timing, while a single low-valued CC (including the factory CC32-35 behavior) is treated as a short press. Program Change also works as a short-press fallback because it has no release event.

USB MIDI and BLE MIDI are supported. The scanner recognizes names containing `Chocolate`, `M-VAVE`, `MVAVE`, or `FootCtrl`. USB controllers use Android MIDI ports. BLE controllers are opened directly through the standard BLE-MIDI service `03b80e5a-ede8-4b33-a751-6ce34ec4c700` and I/O characteristic `7772e5db-3868-4112-a1a9-f2669d106bf3`, bypassing Android's Bluetooth MIDI bridge when it opens a port but delivers no packets. The app also opens a matching bonded controller directly, which covers a `FootCtrlPlus` that stops advertising before the app starts.

The vendor's current download center lists `FootCtrlPlus` under the newer MidiSuite editor, while the older Chocolate remains listed under CubeSuite: <https://www.m-vave.com/download>.

## BLE transport notes

LiteJam discovery recognizes the vendor prefix `Lite Jam RGB` plus `LiteJam` variants. It writes one complete packet without response to service `000000ee-0000-1000-8000-00805f9b34fb`, characteristic `0000ee04-0000-1000-8000-00805f9b34fb`:

```text
segment count
  repeated per color:
    fret count
    repeated per fret: fret, six-string bit mask
    red, green, blue
0x45 0x4e 0x44 ("END")
```

String bit 0 is string 1/high E and bit 5 is string 6/low E. The vendor references `NLJ-LED Control-210425-052233.pdf` and `NLJ-LED Perform mode-210425-052308.pdf` may be kept locally under `docs/`; both paths are intentionally git-ignored. The independent [litejam-alphajams implementation](https://github.com/jsmadja/litejam-alphajams) confirms the advertising prefix, UUIDs, packet terminator, and write-without-response behavior.

Fret Zealot v1 uses service `6e400001-b5a3-f393-e0a9-e50e24dcca9e` and write characteristic `6e400002-b5a3-f393-e0a9-e50e24dcca9e`. Fret Zealot 2 uses service `fb1e4001-54ae-4a28-9f74-dfccb248601d` and write characteristic `fb1e4002-54ae-4a28-9f74-dfccb248601d`. The normal four-byte LED command is:

```text
byte 0: command in high nibble, effect in low nibble
byte 1: fret in high nibble, red in low nibble
byte 2: green in high nibble, blue in low nibble
byte 3: 1 << (zero-based string + 1); the default right-handed map is bit 1 low E through bit 6 high E
```

The app sends `40 00 00 00` to clear before the new scale and paces commands in 20-byte chunks. These Fret Zealot interoperability details were independently derived from the vendor Android client's BLE library; no vendor code or app asset is included here.

## Hardware validation

Automated tests validate mode retention, chromatic wrapping, controller maps, glyph precedence, LiteJam segment/string encoding, and Fret Zealot nibble packing. An APK build validates all JNI and Android APIs. Physical hardware is still required to validate advertised names on a particular firmware, left-handed/custom tuning expectations, BLE write pacing, and the selected MidiSuite preset.
