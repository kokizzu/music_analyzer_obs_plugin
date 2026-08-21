# External fretboard and root control

The Android app can drive a LiteJam RGB guitar, Fret Zealot fretboard, or AUPHY SCT-86PRO from the analyzer root while accepting root controls from an Akai APC mini mk2 or M-VAVE Chocolate Plus. All five devices are optional and discovered independently.

## Root and scale behavior

- `AUTO` follows the analyzer's most recent valid detected root. An empty/uncertain analyzer frame does not erase the last valid root.
- `MAN` retains a separate manually selected root. Changing the manual root while `AUTO` is active does not silently switch modes.
- Both modes render a major scale in standard guitar tuning. The degree colors are root red, second orange, third yellow, fourth green, fifth cyan, sixth blue, and seventh purple.
- LiteJam receives frets 0-24. Fret Zealot's 15 physical fret positions (musical frets 1-15) are encoded as LED indices 0-14. AUPHY receives fret-major LED indices starting at the open strings, with its physical string 0 as high E.

The status immediately before BPM shows the effective mode/root and each connection:

```text
AUTO C  LJ+ FZ? APC- MV! AU+
```

`+` is connected, `?` is searching, `~` is connecting, `!` is an error, and `-` is disabled. `LJ`, `FZ`, `APC`, `MV`, and `AU` mean LiteJam, Fret Zealot, APC mini mk2, M-VAVE, and AUPHY SCT-86PRO. Fret Zealot and APC autoconnect are enabled by default; LiteJam, M-VAVE, and AUPHY are disabled by default. Tap one of the five device labels to toggle autoconnect only for that device. Disabling a label disconnects that device and leaves the other four unchanged. Long-press anywhere on the analyzer view to turn the global device autoconnect switch off or back on; `OFF` appears beside the root while globally disabled. Tap only the current input-source label in the top header to cycle the audio input; ordinary taps elsewhere do nothing.

For physical debug validation, `make android-set-root ROOT=G` switches the already-running debug app to `MAN G` and refreshes connected LiteJam, Fret Zealot, AUPHY, APC, and M-VAVE output without restarting audio capture. This ADB-only entry point is guarded by `BuildConfig.DEBUG`, so release builds retain normal analyzer/controller behavior.

## APC mini mk2

The upper six physical pad rows contain twelve 2x2 root blocks:

```text
C   C#  D   D#
E   F   F#  G
G#  A   A#  B
```

The bottom two physical rows are one 3x2 semitone-down area, one 2x2 Auto/Manual toggle, and one 3x2 semitone-up area. Root and semitone pads update the retained manual root; use the center pads to make it effective.

The app sends a complete 8x8 LED refresh after connection and after every effective-root/mode change. The rainbow rotates with the effective root: the root is red, followed chromatically by red-orange, orange, gold, yellow, green, turquoise, light blue, periwinkle, purple, violet, and pink. For example, G is red when the root is G, while C is red when the root is C. The bottom previous control is dark forest green and the next control is medium green, using two Akai colors that are absent from the root rainbow. The center toggle is light grey in Auto mode to contrast the dark root/sharp glyph, and dark grey in Manual mode to contrast the white glyph. The implementation uses APC notes 0-63 and Akai's full-brightness solid Note On status `0x96`.

Connect the APC mini mk2 by USB. Android must expose at least one MIDI output port for pad input; an input port is additionally required for LED feedback.

## M-VAVE Chocolate Plus

Every M-VAVE MIDI packet is captured before control mapping, regardless of its channel or configured data number. The FootCtrlPlus factory custom controls CC32, CC33, CC34, and CC35 map directly to A, B, C, and D; other Note and CC numbers use modulo positions 0-3. FootCtrlPlus Program Change display values ending in 1-4 map to A-D; display values ending in 5-6 are the E/F combination controls and are captured but do not trigger an A-D action. SysEx is also captured for diagnostics but does not imply a root-control action.

For predictable press-versus-hold behavior, the recommended vendor-editor preset uses momentary Note messages on MIDI channel 1:

| Switch | Note | Short release | Hold at least 600 ms |
| --- | ---: | --- | --- |
| A | 36 | down one semitone | down two semitones (one whole tone) |
| B | 37 | up one semitone | up two semitones (one whole tone) |
| C | 38 | toggle manual root G/C | no extra action |
| D | 39 | toggle Auto/Manual | toggle Auto/Manual |

Each switch should send Note On when pressed and Note Off (or Note On with velocity zero) when released. The short action happens on press, while releasing A or B after 600 ms completes the long action. C and D are press-only; holding C does not toggle again on release. Note-On-only presets therefore still provide repeatable short actions. Notes 0-3 and 60-63 are accepted as alternate four-note banks. Any CC is accepted: a high value followed by a low value provides press/release timing, while a single low-valued CC (including the factory CC32-35 behavior) is treated as a short press. Program Change also works as a short-press fallback because it has no release event.

USB MIDI and BLE MIDI are supported. The scanner recognizes names containing `Chocolate`, `M-VAVE`, `MVAVE`, or `FootCtrl`. USB controllers use Android MIDI ports. BLE controllers are opened directly through the standard BLE-MIDI service `03b80e5a-ede8-4b33-a751-6ce34ec4c700` and I/O characteristic `7772e5db-3868-4112-a1a9-f2669d106bf3`, bypassing Android's Bluetooth MIDI bridge when it opens a port but delivers no packets. The app also opens a matching bonded controller directly, which covers a `FootCtrlPlus` that stops advertising before the app starts.

The vendor's current download center lists `FootCtrlPlus` under the newer MidiSuite editor, while the older Chocolate remains listed under CubeSuite: <https://www.m-vave.com/download>.

## LiteJam BLE transport

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

## Fret Zealot (original and Fret Zealot 2)

Fret Zealot is not driven through LiteJam's segment protocol. The shared native encoder, `build_fret_zealot_major_scale_packet`, converts the selected major scale into one four-byte LED command per lit string/fret cell. It covers the six standard-tuned strings and physical musical frets 1-15 only. Fret Zealot LED index 0 means musical fret 1, while index 14 means fret 15; open strings and frets above 15 have no Fret Zealot LED.

The packet begins with a reset marker (`0x40 0x00 0x00 0x00`) and then uses these LED commands:

```text
byte 0: command in high nibble, effect in low nibble
byte 1: fret in high nibble, red in low nibble
byte 2: blue in high nibble, green in low nibble
byte 3: 1 << (zero-based string + 1); the default right-handed map is bit 1 low E through bit 6 high E
```

### Discovery and transport selection

`ExternalDeviceManager` recognizes Fret Zealot advertising names and delegates the GATT lifecycle to the bundled Android-15-compatible adaptation of Edge Tech Labs' official [`fz-android-sdk`](https://github.com/edgetechlabs/fz-android-sdk), based on SDK commit `6da6d1b`. The manager itself does not write raw Fret Zealot characteristics.

- Original Fret Zealot uses the LED service `6e400001-b5a3-f393-e0a9-e50e24dcca9e` and LED write characteristic `6e400002-b5a3-f393-e0a9-e50e24dcca9e`.
- Fret Zealot 2 exposes `fb1e4001-54ae-4a28-9f74-dfccb248601d` / `fb1e4002-54ae-4a28-9f74-dfccb248601d`. The SDK detects that Fret Zealot 2 characteristic to select its modern transport sizing, but retains the documented `6e40...` LED endpoint for scale commands. The `fb1e...` endpoint is not used as a generic LED UART by this app.

The SDK requests a 517-byte MTU and a high-priority connection before service discovery. When the Fret Zealot 2 characteristic is present, it sends a command batch of up to 500 bytes (or the negotiated GATT payload limit); original boards keep callback-paced 20-byte writes with a 20-ms settling delay. This difference is essential: applying Fret Zealot 2's large batches to an original board can leave only a prefix of a scale visible.

### Scale-frame safety

`FretZealotSdkController` translates the shared packet to the SDK's `set` and flush calls, reverses the native low-E-to-high-E string order to the SDK's physical high-E-to-low-E pixel order, and reduces shared RGB values to Fret Zealot's four-bit channel range. It uses a calibrated dim palette and SDK intensity 3 so degree hues remain distinguishable at low brightness.

On connection, the first reset marker performs the one full-board clear. Manual changes are then deltas: new/recolored LEDs are written before obsolete LEDs are cleared, avoiding a visible black-board blink. AUTO-root changes wait 1.25 seconds for the root to stabilize. The controller reasserts all target LEDs, waits for the legacy frame to settle, and only then clears stale pixels. If an AUTO update arrives while a frame is in flight, only the newest request is retained. These precautions primarily protect first-generation hardware; Fret Zealot 2 still follows the same frame semantics, but completes its larger writes much faster.

The app briefly shows a rainbow `MUSIC` connection glyph, then displays the selected scale. The SDK module intentionally preserves only the LED API and modern BLE lifecycle; obsolete upstream UI and firmware-update dependencies are not bundled.

## AUPHY SCT-86PRO (FretSpark)

The SCT-86PRO adapter is implemented from the official open-source [FretSpark SDK](https://github.com/FretSpark/fretspark_sdk), using its `auphy` brand configuration. Discovery accepts runtime advertisements matching `SCT-86PRO-XXXX` (with the SDK's supported separator variants); OTA advertisements are deliberately excluded because this app only drives live LED boards.

The controller requests MTU 247, discovers service `0000fff0-0000-1000-8000-00805f9b34fb`, writes FFF3 (`0000fff3-0000-1000-8000-00805f9b34fb`), and enables notifications on FFF4 (`0000fff4-0000-1000-8000-00805f9b34fb`). It uses the SDK framing exactly:

```text
app -> board: [0xBC, command, parameter length, parameters..., 0x55]
board -> app: [0xCC, command, data length, data..., 0xAA]
```

After notification setup it selects matrix layout (`0x02, 0x00`), powers the panel on, and queries firmware/version (`0x1E`), LED count (`0x1F`), and LED index mode (`0x28`). The SDK-compatible initial LED count is 90; when FFF4 reports the real count, the current scale is rebuilt for `ledCount / 6 - 1` frets. This prevents a shorter SCT-86PRO board from receiving out-of-range pixels while allowing longer boards to light their full fret range.

The shared native encoder converts the analyzer's low-E-to-high-E tuning into FretSpark's high-E-to-low-E string numbering: `index = fret * 6 + (5 - nativeString)`. It preserves the same seven major-scale degree colors as LiteJam. Each complete root update first clears learning LEDs (`0x22, [0x00]`), then uses the SDK learning-multiple command (`0x22, [0x02, count, index/r/g/b...]`) for up to 59 pixels. Larger boards use the SDK batch sequence `0x1C`, one or more `0x16` chunks of at most 59 pixels, and `0x1D`. Frames remain FIFO with the initial configuration and query commands, matching FretSpark's send-queue semantics.

## Hardware validation

Automated tests validate mode retention, chromatic wrapping, controller maps, glyph precedence, LiteJam segment/string encoding, Fret Zealot nibble packing, AUPHY high-E-first pixel encoding, and delegation through the SDK-derived transport. An APK build validates all JNI and Android APIs. Physical hardware is still required to validate advertised names on a particular firmware, actual LED count/index direction, BLE write pacing, left-handed/custom tuning expectations, and the selected MidiSuite preset.
