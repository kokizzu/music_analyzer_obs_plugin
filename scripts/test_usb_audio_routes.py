#!/usr/bin/env python3
"""Static regression checks for USB audio route and format recovery."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WINDOWS = (ROOT / "src/windows_loopback.hpp").read_text(encoding="utf-8")
ANDROID = (ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/MainActivity.java").read_text(
    encoding="utf-8"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"USB audio route check failed: {message}")


require("eMultimedia" in WINDOWS, "Windows capture should prefer the multimedia render endpoint")
require("endpoint_changed" in WINDOWS and "GetId" in WINDOWS,
        "Windows capture should notice a changed default render endpoint")
require("format_->nBlockAlign / format_->nChannels" in WINDOWS,
        "Windows sample decoding should use the actual per-channel byte stride")
require("format_->wBitsPerSample == 24" in WINDOWS,
        "Windows capture should retain packed PCM24 support")

require("AudioFormat.ENCODING_PCM_16BIT" in ANDROID,
        "Android capture should fall back to PCM16 for USB interfaces")
require("short[]" in ANDROID and "read(pcmSamples" in ANDROID,
        "Android PCM16 fallback should use a preallocated short buffer")
require("pcmSamples[i] / 32768.0f" in ANDROID,
        "Android PCM16 input should be converted to the native float analyzer format")
require("preferredInputDeviceId" in ANDROID and "refreshInputDevices(true)" in ANDROID,
        "Android route recovery should restore the selected USB input")

print("USB audio route checks: ok")
