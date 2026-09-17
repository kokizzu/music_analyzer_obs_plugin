#!/usr/bin/env python3
"""Verify that Windows loopback recovery tolerates short capture glitches."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOOPBACK = REPO_ROOT / "src" / "windows_loopback.hpp"
STANDALONE = REPO_ROOT / "src" / "standalone.cpp"


def section(source: str, start: str, end: str) -> str:
    return source[source.index(start) : source.index(end, source.index(start))]


def main() -> None:
    loopback = LOOPBACK.read_text(encoding="utf-8")
    standalone = STANDALONE.read_text(encoding="utf-8")

    endpoint = section(loopback, "bool endpoint_changed()", "template<class Feed>")
    assert "kEndpointQueryGraceChecks = 4" in loopback
    assert "kCaptureErrorGraceChecks = 3" in loopback
    assert "endpoint_query_failed(\"default speaker query\"" in endpoint
    assert "endpoint_query_failed(\"speaker identity query\"" in endpoint
    assert "endpoint_query_failures_ = 0" in endpoint
    assert "default speaker query failed; reopening loopback" not in endpoint

    pump = section(loopback, "template<class Feed>", "};\n#endif")
    assert pump.count("AUDCLNT_S_BUFFER_EMPTY") >= 2
    assert "AUDCLNT_E_BUFFER_ERROR" in loopback
    assert pump.index("if (next_result == AUDCLNT_S_BUFFER_EMPTY)") < pump.index(
        'capture_result(next_result, "next packet")'
    )
    assert pump.index("if (buffer_result == AUDCLNT_S_BUFFER_EMPTY)") < pump.index(
        'capture_result(buffer_result, "read packet")'
    )

    assert "std::min<uint32_t>(loopback_reconnect_attempt, 2)" in standalone
    assert "std::min<uint32_t>(500u, 250u << backoff_shift)" in standalone

    print("Windows loopback recovery checks: PASS")


if __name__ == "__main__":
    main()
