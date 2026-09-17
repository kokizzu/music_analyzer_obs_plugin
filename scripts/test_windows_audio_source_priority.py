#!/usr/bin/env python3
"""Ensure Windows starts with native speaker loopback before SDL monitors."""

from pathlib import Path


SOURCE = (Path(__file__).resolve().parents[1] / "src" / "standalone.cpp").read_text(encoding="utf-8")


def require(needle: str, label: str) -> None:
    if needle not in SOURCE:
        raise SystemExit(f"missing {label}: {needle}")


require(
    'if (options.prefer_output_monitor)\n\t\tsources.push_back(LiveAudioSource{LiveAudioSourceKind::WindowsLoopback, "SPEAKER LOOPBACK"});',
    "unconditional Windows loopback source",
)
require(
    'if (sources[i].kind == LiveAudioSourceKind::WindowsLoopback)\n\t\t\t\treturn i;',
    "Windows loopback initial-source preference",
)
require(
    "#if !defined(_WIN32)\n\tbool has_monitor = false;",
    "non-Windows monitor-only fallback guard",
)

print("Windows audio source priority checks: ok")
