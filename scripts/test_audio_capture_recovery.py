#!/usr/bin/env python3
"""Check that live audio capture keeps the platform recovery paths enabled."""

from pathlib import Path


def require(text: str, fragment: str, path: Path) -> None:
    if fragment not in text:
        raise SystemExit(f"{path}: missing required capture recovery fragment: {fragment}")


def main() -> int:
    windows_path = Path("src/standalone.cpp")
    windows_loopback_path = Path("src/windows_loopback.hpp")
    android_path = Path("android/app/src/main/java/dev/benalu/musicanalyzer/MainActivity.java")
    windows = windows_path.read_text(encoding="utf-8")
    loopback = windows_loopback_path.read_text(encoding="utf-8")
    android = android_path.read_text(encoding="utf-8")

    for fragment in (
        "bool loopback_reconnect_pending = false;",
        "open_live_source(live_source_index)",
        "WASAPI speaker loopback lost; attempting automatic recovery",
        "std::chrono::milliseconds(delay_ms)",
    ):
        require(windows, fragment, windows_path)
    require(loopback, "constexpr REFERENCE_TIME kBufferDuration = 100 * 10000;", windows_loopback_path)
    require(loopback, "AUDCLNT_STREAMFLAGS_LOOPBACK", windows_loopback_path)
    require(loopback, "format_->wBitsPerSample == 24", windows_loopback_path)
    require(loopback, "0x00800000", windows_loopback_path)
    if "SDL_ShowSimpleMessageBox" in windows:
        raise SystemExit("src/standalone.cpp: live loopback failure must not block recovery with a modal dialog")

    for fragment in (
        "private boolean runAudioCaptureSession(int bufferFrames, float[] samples, short[] pcmSamples)",
        "count == AudioRecord.ERROR_DEAD_OBJECT || count < 0",
        "AudioRecord read failed; retrying the input route",
        "private static final long AUDIO_RESTART_DELAY_MS = 250L;",
        "SystemClock.sleep(AUDIO_RESTART_DELAY_MS)",
    ):
        require(android, fragment, android_path)

    print("audio capture recovery checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
