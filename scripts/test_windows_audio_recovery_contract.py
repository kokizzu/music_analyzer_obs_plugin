#!/usr/bin/env python3
"""Check the source-level guarantees of Windows capture recovery."""

from pathlib import Path


LOOPBACK = Path("src/windows_loopback.hpp")
CAPTURE = Path("src/windows_input_capture.hpp")


def main() -> int:
    loopback = LOOPBACK.read_text(encoding="utf-8")
    capture = CAPTURE.read_text(encoding="utf-8")
    required_loopback = (
        "enumerator_->GetDevice(device_id_.c_str(), &current_device)",
        "input_ ? \"capture endpoint query\" : \"default speaker query\"",
        "input_ ? \"capture identity query\" : \"speaker identity query\"",
        "class EndpointNotification final : public IMMNotificationClient",
        "RegisterEndpointNotificationCallback",
        "UnregisterEndpointNotificationCallback",
        "const wchar_t *preferred_input_id = nullptr",
        "if (diagnostics_)\n\t\t\t\t++diagnostic_wait_timeouts_;",
    )
    required_capture = (
        "if (endpoint.endpoint_changed() && !reopen())",
        "auto reopen = [&]()",
        "kInitialDelay = std::chrono::milliseconds(250)",
        "kMaximumDelay = std::chrono::milliseconds(2000)",
        "WASAPI capture recovered",
        "WASAPI capture reopen pending",
        "queue_.clear();",
        "endpoint.open(sample_rate, name.c_str(), endpoint_id.c_str())",
    )
    missing = [fragment for fragment in required_loopback if fragment not in loopback]
    missing.extend(fragment for fragment in required_capture if fragment not in capture)
    if missing:
        raise SystemExit("missing Windows audio recovery contract: " + "; ".join(missing))
    print("Windows audio recovery contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
