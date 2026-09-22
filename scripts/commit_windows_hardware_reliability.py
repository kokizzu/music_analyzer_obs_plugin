#!/usr/bin/env python3
"""Plan or commit only the Windows hardware reliability change set."""

from __future__ import annotations

import argparse
import difflib
import subprocess
from pathlib import Path


FILES = (
	"src/fret_control.cpp",
	"src/fret_control.hpp",
	"src/capture_queue.hpp",
	"src/windows_input_capture.hpp",
	"src/windows_loopback.hpp",
	"src/windows_hardware_control.cpp",
	"src/windows_device_notifications.hpp",
	"src/windows_hardware_worker.hpp",
    "src/windows_hardware_retry.hpp",
    "src/windows_hardware_write.hpp",
    "tests/fret_zealot_protocol.cpp",
    "scripts/report_fret_zealot_sdk.py",
    "scripts/report_fret_zealot_sdk_usage.py",
    "scripts/report_windows_deploy_source.py",
    "scripts/report_windows_hardware_source.py",
    "scripts/report_windows_source_range.py",
    "scripts/report_windows_worker_source.py",
    "scripts/report_windows_audio_source.py",
    "scripts/report_windows_audio_diff.py",
    "scripts/test_windows_audio_recovery_contract.py",
    "scripts/test_windows_hardware_device_contract.py",
    "scripts/test_windows_hardware_retry_contract.py",
    "scripts/test_windows_hardware_status.py",
    "scripts/test_windows_hardware_worker_contract.py",
    "scripts/test_windows_hardware_retry_runtime.py",
	"scripts/test_windows_hardware_write_runtime.py",
	"scripts/test_capture_queue_runtime.py",
	"scripts/test_fret_control_protocol.py",
	"scripts/test_windows_hardware_worker_runtime.py",
	"scripts/test_windows_toolchains.py",
    "scripts/test_windows_hardware_reconnect.py",
    "scripts/test_windows_loopback_recovery.py",
    "scripts/windows_hardware_checklist.py",
    "scripts/inspect_scoped_windows_hardware_diff.py",
    "scripts/commit_windows_hardware_reliability.py",
    "tests/windows_hardware_retry_runtime.cpp",
	"tests/windows_hardware_write_runtime.cpp",
	"tests/capture_queue_runtime.cpp",
	"tests/fret_control_protocol.cpp",
	"tests/windows_hardware_worker_runtime.cpp",
)

MAKEFILE_BLOCK = """.PHONY: report-windows-hardware-source
report-windows-hardware-source:
\tpython3 scripts/report_windows_hardware_source.py

.PHONY: report-fret-zealot-sdk
report-fret-zealot-sdk:
\tpython3 scripts/report_fret_zealot_sdk.py

.PHONY: report-fret-zealot-sdk-usage
report-fret-zealot-sdk-usage:
\tpython3 scripts/report_fret_zealot_sdk_usage.py

.PHONY: report-windows-worker-source
report-windows-worker-source:
\tpython3 scripts/report_windows_worker_source.py

.PHONY: report-windows-audio-source
report-windows-audio-source:
\tpython3 scripts/report_windows_audio_source.py

.PHONY: report-windows-audio-diff
report-windows-audio-diff:
\tpython3 scripts/report_windows_audio_diff.py

.PHONY: test-windows-hardware-worker-contract
test-windows-hardware-worker-contract:
\tpython3 scripts/test_windows_hardware_worker_contract.py

.PHONY: test-windows-hardware-device-contract
test-windows-hardware-device-contract:
\tpython3 scripts/test_windows_hardware_device_contract.py

.PHONY: test-windows-audio-recovery-contract
test-windows-audio-recovery-contract:
\tpython3 scripts/test_windows_audio_recovery_contract.py

WINDOWS_FRET_ZEALOT_PROTOCOL_TEST_BIN := $(BUILD_DIR)/fret_zealot_protocol_tests

$(WINDOWS_FRET_ZEALOT_PROTOCOL_TEST_BIN): tests/fret_zealot_protocol.cpp src/fret_control.cpp src/fret_control.hpp | $(BUILD_DIR)
\t$(CXX) $(CXXFLAGS) -Isrc tests/fret_zealot_protocol.cpp src/fret_control.cpp -o $@

.PHONY: test-fret-zealot-protocol
test-fret-zealot-protocol: $(WINDOWS_FRET_ZEALOT_PROTOCOL_TEST_BIN)
\t$(WINDOWS_FRET_ZEALOT_PROTOCOL_TEST_BIN)

.PHONY: report-windows-litejam-source
report-windows-litejam-source:
\tpython3 scripts/report_windows_source_range.py

.PHONY: test-windows-hardware-retry-contract
test-windows-hardware-retry-contract:
\tpython3 scripts/test_windows_hardware_retry_contract.py

.PHONY: test-windows-hardware-retry-runtime
test-windows-hardware-retry-runtime:
\tpython3 scripts/test_windows_hardware_retry_runtime.py

.PHONY: test-windows-hardware-write-runtime
test-windows-hardware-write-runtime:
\tpython3 scripts/test_windows_hardware_write_runtime.py

.PHONY: report-windows-deploy-source
report-windows-deploy-source:
\tpython3 scripts/report_windows_deploy_source.py

.PHONY: inspect-scoped-windows-hardware-diff
inspect-scoped-windows-hardware-diff:
\tpython3 scripts/inspect_scoped_windows_hardware_diff.py

.PHONY: verify-windows-hardware-checklist
verify-windows-hardware-checklist: test-windows-hardware-retry-contract test-windows-hardware-worker-contract test-windows-hardware-device-contract test-windows-hardware-reconnect test-windows-hardware-status test-windows-hardware-status-runtime test-windows-diagnostic-output test-windows-midi-protocol test-fret-zealot-protocol test-windows-loopback-recovery test-windows-audio-recovery-contract test-windows-hardware-retry-runtime test-windows-hardware-write-runtime verify-windows-standalone verify-windows-runtime-bundle
\tpython3 scripts/windows_hardware_checklist.py

.PHONY: plan-commit-windows-hardware-reliability commit-windows-hardware-reliability
plan-commit-windows-hardware-reliability:
\tpython3 scripts/commit_windows_hardware_reliability.py plan

commit-windows-hardware-reliability:
\tpython3 scripts/commit_windows_hardware_reliability.py apply
"""

MAKEFILE_ADDITIONS = """test-capture-queue-runtime:
\tpython3 scripts/test_capture_queue_runtime.py

test-fret-control-protocol:
\tpython3 scripts/test_fret_control_protocol.py

test-windows-hardware-worker-runtime:
\tpython3 scripts/test_windows_hardware_worker_runtime.py

test-windows-toolchains:
\tpython3 scripts/test_windows_toolchains.py
"""


def run(arguments: list[str], *, input_text: str | None = None) -> None:
    result = subprocess.run(arguments, check=False, text=True, input=input_text)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def staged_makefile_patch() -> str:
    head = subprocess.check_output(["git", "show", "HEAD:windows.mk"], text=True)
    if MAKEFILE_ADDITIONS.strip() in head:
        return ""
    anchor = "test-windows-hardware-write-runtime:\n\tpython3 scripts/test_windows_hardware_write_runtime.py\n"
    if anchor not in head:
        raise SystemExit("windows.mk runtime target anchor is missing from HEAD")
    desired = head.replace(anchor, anchor + "\n" + MAKEFILE_ADDITIONS, 1)
    checklist_anchor = " test-windows-hardware-write-runtime verify-windows-standalone"
    checklist_replacement = (
        " test-windows-hardware-write-runtime test-capture-queue-runtime"
        " test-fret-control-protocol test-windows-hardware-worker-runtime"
        " test-windows-toolchains verify-windows-standalone"
    )
    if checklist_anchor not in desired:
        raise SystemExit("windows.mk checklist anchor is missing from HEAD")
    desired = desired.replace(checklist_anchor, checklist_replacement, 1)
    patch = "".join(
        difflib.unified_diff(
            head.splitlines(keepends=True),
            desired.splitlines(keepends=True),
            fromfile="a/windows.mk",
            tofile="b/windows.mk",
        )
    )
    return patch


def plan() -> None:
    print("Windows hardware reliability files:")
    for path in (*FILES, "windows.mk"):
        print(f"  {path}")
    run(["git", "status", "--short", "--", *FILES, "windows.mk"])
    run(["git", "diff", "--stat", "--", *FILES, "windows.mk"])


def apply() -> None:
    makefile_patch = staged_makefile_patch()
    if makefile_patch:
        run(["git", "apply", "--cached", "--whitespace=nowarn"], input_text=makefile_patch)
    run(["git", "add", "--", *FILES])
    run(["git", "diff", "--cached", "--check"])
    run(["git", "commit", "-m", "Improve Windows hardware and audio recovery"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()
    if args.mode == "plan":
        plan()
    else:
        apply()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
