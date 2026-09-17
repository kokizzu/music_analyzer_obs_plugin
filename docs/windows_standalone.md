# Windows 11 x64 portable standalone

For AMD Ryzen / Ryzen AI and Intel x64 laptops. No NPU-specific software,
OBS, Python, FFmpeg, virtual audio cable, or separate C++ runtime installation
is required. Keep the bundled SDL2.dll beside both executables. Windows supplies
the system libraries used for audio, MIDI, Bluetooth GATT, and device discovery.

## Run

1. Extract the entire ZIP to a writable folder (do not run inside the ZIP).
2. Open MusicAnalyzer.exe for the full layout, or HalfMusicAnalyzer.exe for
   the compact drums/bass/keys/guitar layout.
3. Play music: default Windows speaker output is captured using native WASAPI
   loopback. Press Space to cycle through microphone/USB recording devices.
   Escape or Q quits. The console prints startup and audio errors.

Command-line options are the same as the Linux standalone, except compressed
file input (`--input`) is not included. `--raw-f32le filename` accepts mono
float32 little-endian samples at the specified `--sample-rate` (default 48000).
Use regular files rather than a blocking stdin pipe on Windows.
`--default-input` starts with the default microphone/USB recording input;
`--list-devices` lists recording device names for `--device "exact name"`.
Pass `--debug-audio` while troubleshooting Windows capture to print one-second
WASAPI packet, silent-frame, RMS, and peak counters for the active endpoint.
For hardware setup without relying on live root detection, use
`--hardware-root G` (or another note) to send a fixed major scale to matched
hardware outputs.
For a direct device-only check without opening the analyzer or requiring an
audio source, use `--hardware-only --hardware-root G`. It initializes every
selected Windows MIDI/BLE output, sends the scale, waits three seconds for
BLE writes to settle, prints `midi/litejam/fret-zealot` connection results, and
exits. Add `--require-midi`, `--require-litejam`, or `--require-fret-zealot`
to make the check return failure when that output is not connected. For
example, `--hardware-only --hardware-root G --require-fret-zealot
--fret-zealot-device "Fret Zealot"` is a real Fret Zealot probe, while
`--require-midi --midi-output "MPC"` checks an Akai/MPC MIDI output.

## Hardware control

The Windows standalone build can drive the existing external-device outputs
without OBS. It automatically looks for an APC Mini/APC-style or Akai MPC/MPD
MIDI output, a paired LiteJam BLE device, and a paired Fret Zealot BLE device
(including the Fret Zealot 2 GATT service).
Root changes update the MIDI pad map and major-scale LEDs on a worker thread,
so hardware discovery and writes do not block audio analysis.

Use `--list-hardware` to print available Windows MIDI outputs and paired
LiteJam/Fret Zealot BLE interfaces. Use `--midi-output "device name"`,
`--litejam-device "device name"`, or `--fret-zealot-device "device name"` to
select a specific device. Use `--no-hardware` to disable all outputs. The
`--midi-protocol` option accepts `auto`, `apc`, or `mpc-notes`. `auto` keeps the
APC-style 8x8 color protocol for APC names and uses channel-10 note feedback
for MPC/MPD/pad names. `mpc-notes` sends classic pad notes 36 through 51 with
velocity zero for off-scale pads and nonzero velocity for scale pads; the
controller must be configured to light LEDs from MIDI input. Exact LED behavior
and note mapping remain model-specific, so use `--midi-protocol apc` only for
APC-compatible devices and select the exact output name for other controllers.
MPC note feedback can also trigger the selected MIDI program, depending on the
hardware's MIDI-input settings.
LiteJam and Fret Zealot must be paired in Windows Bluetooth settings before
launching.

If a recording input is inaccessible, enable Windows Settings > Privacy &
security > Microphone > Let desktop apps access your microphone. The loopback
source follows the current default output and automatically reacquires the
WASAPI endpoint after a USB soundcard reset or format change. Exclusive-mode
playback and protected content may not be available to shared-mode loopback.

## Latency and scope

The native C++ detector, analysis window, 50 ms analysis update interval,
30 FPS rendering, silence throttling and 2 ms event-loop sleep are preserved.
Microphone capture requests the existing 1024-frame SDL buffer (~21.3 ms at
48 kHz); WASAPI loopback requests a 100 ms shared buffer so the detector can
finish its analysis pass without losing packets when a USB driver is busy. These are not
claims of measured end-to-end latency. Actual latency depends on the laptop's
audio drivers, endpoint buffer, workload, and analyzer window. Prefer wired
headphones/USB audio over Bluetooth for live playing.

The optional Linux ONNX vocal-fusion model is not included. Native heuristic
analysis remains available without model downloads. Android-specific device
managers are not used by this Windows port; it uses native Windows MIDI and
Bluetooth APIs instead.

## Build and verify on Linux

The build requires MinGW-w64 x64 with POSIX threads, Python 3, and Wine for
verification. Those are build-machine tools, not laptop requirements.

    make prepare-windows-standalone
    make windows-standalone
    make verify-windows-standalone
    make package-windows-standalone

SDL 2.32.10 is downloaded from its official release and checked against a
pinned SHA256. Compiler C++/thread runtimes are linked statically; SDL2.dll is
the only non-system DLL bundled in the portable folder. The executables use
Windows' system `winmm.dll`, `setupapi.dll`, and `BluetoothAPIs.dll` for MIDI
and LiteJam/Fret Zealot control. Build output and verification logs live under
build/windows-x64.
Verification checks x64 PE format, every imported DLL, and both executables'
headless analyzer/renderer self-tests under Wine. Physical Windows 11 audio
capture and actual laptop latency still require an on-device check.

## Smart App Control and code signing

The Linux-built portable executables are unsigned by default. Windows Smart App
Control can therefore block them before they start; renaming the executable or
copying more DLLs does not solve that policy decision. A trusted Authenticode
certificate is required. Self-signed certificates are useful for local testing
only and are not a Smart App Control release fix.

Keep the certificate and password outside the repository. With a PKCS#12
certificate available on the build machine, set `WINDOWS_SIGN_PFX`,
`WINDOWS_SIGN_PASSWORD`, and preferably `WINDOWS_SIGN_TIMESTAMP_URL`, then run:

    make plan-sign-windows-standalone
    make sign-windows-standalone
    make package-signed-windows-standalone

The signing target signs both executables in `build/windows-x64/portable` and
uses a temporary output before replacing each file. The certificate chain and
publisher reputation still have to be trusted by the target Windows policy;
the repository cannot bypass Smart App Control without that trust.

Mounted Windows deployment signs both executables before copying them and
refuses to deploy when a trusted signing certificate is not configured.

References: https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording
and https://github.com/libsdl-org/SDL/releases/tag/release-2.32.10
