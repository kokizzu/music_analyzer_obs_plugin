#!/usr/bin/env python3
"""Plan/apply the tested Windows standalone and hardware support commit."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ".gitignore",
    "GNUmakefile",
    "docs/windows_standalone.md",
    "src/fret_control.cpp",
    "src/fret_control.hpp",
    "src/standalone.cpp",
    "src/windows_loopback.hpp",
    "src/windows_bluetooth_gatt.hpp",
    "src/windows_hardware_control.cpp",
    "src/windows_hardware_control.hpp",
    "src/windows_loopback.hpp",
    "tests/fret_control.cpp",
    "windows.mk",
    "scripts/cleanup_suspicious_empty_artifacts.py",
    "scripts/commit_windows_hardware.py",
    "scripts/deploy_windows_mounted.py",
    "scripts/deploy_windows_self_signed.py",
    "scripts/inspect_android_audio_contract.py",
    "scripts/inspect_audio_capture_configuration.py",
    "scripts/inspect_audio_capture_lifecycles.py",
    "scripts/inspect_standalone_audio_source.py",
    "scripts/inspect_standalone_self_test.py",
    "scripts/inspect_suspicious_worktree_artifacts.py",
    "scripts/inspect_windows_loopback.py",
    "scripts/inspect_windows_build_log.py",
    "scripts/inspect_windows_build_log.py",
    "scripts/inspect_windows_self_test_log.py",
    "scripts/inspect_windows_share_artifact.py",
    "scripts/inspect_windows_signing.py",
    "scripts/discover_windows_signing_certificate.py",
    "scripts/inspect_windows_certificate.py",
    "scripts/inspect_windows_self_sign.py",
    "scripts/inspect_windows_self_signed_deploy.py",
    "scripts/discover_windows_signing_certificate.py",
    "scripts/inspect_standalone_hardware_only.py",
    "scripts/review_worktree_changes.py",
    "scripts/review_worktree_file.py",
    "scripts/sign_windows_standalone.py",
    "scripts/windows_self_sign.py",
    "scripts/smoke_windows_hardware_probe.py",
    "scripts/test_audio_capture_recovery.py",
    "scripts/test_usb_audio_routes.py",
    "scripts/test_windows_audio_diagnostics.py",
    "scripts/test_windows_audio_source_priority.py",
    "scripts/test_windows_loopback_recovery.py",
    "scripts/test_windows_deploy_marker.py",
    "scripts/test_windows_hardware_probe.py",
    "scripts/inspect_windows_hardware_protocol.py",
    "scripts/push_windows_hardware.py",
    "scripts/report_windows_share_inventory.py",
    "scripts/test_windows_hardware_protocol.py",
    "scripts/test_windows_deploy_signing_gate.py",
    "tests/windows_midi_protocol.cpp",
    "scripts/test_windows_hardware_reconnect.py",
    "scripts/test_windows_hardware_status.py",
    "scripts/test_windows_hardware_status_runtime.py",
    "scripts/verify_windows_share_runtime.py",
    "scripts/test_windows_signing.py",
    "scripts/verify_windows_hardware_sources.py",
    "scripts/verify_windows_runtime_bundle.py",
    "scripts/windows_standalone.py",
)


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, check=check, text=True)


def plan() -> None:
    print("scoped Windows commit paths:")
    run(["git", "status", "--short", "--", *FILES])
    print("diff summary:")
    run(["git", "diff", "--stat", "--", *FILES])
    print("untracked paths are listed explicitly above; no dataset glob is staged")


def apply() -> None:
    run(["git", "add", "--", *FILES])
    run(["git", "diff", "--cached", "--check"])
    run(["git", "commit", "-m", "windows: stabilize standalone capture and hardware outputs"])


if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
    raise SystemExit("usage: commit_windows_hardware.py plan|apply")
if sys.argv[1] == "plan":
    plan()
else:
    apply()
