.PHONY: inspect-windows-standalone
inspect-windows-standalone:
	python3 scripts/windows_standalone.py inspect

.PHONY: prepare-windows-standalone windows-standalone
prepare-windows-standalone:
	python3 scripts/windows_standalone.py prepare

windows-standalone:
	python3 scripts/windows_standalone.py build

.PHONY: verify-windows-standalone package-windows-standalone
verify-windows-standalone:
	python3 scripts/windows_standalone.py verify

package-windows-standalone:
	python3 scripts/windows_standalone.py package

.PHONY: smoke-windows-standalone
smoke-windows-standalone:
	python3 scripts/windows_standalone.py smoke

.PHONY: smoke-windows-hardware
smoke-windows-hardware:
	python3 scripts/smoke_windows_hardware_probe.py

.PHONY: inspect-windows-loopback
inspect-windows-loopback:
	python3 scripts/inspect_windows_loopback.py

.PHONY: inspect-standalone-audio-source
inspect-standalone-audio-source:
	python3 scripts/inspect_standalone_audio_source.py

.PHONY: inspect-windows-self-test-log
inspect-windows-self-test-log:
	python3 scripts/inspect_windows_self_test_log.py

.PHONY: inspect-standalone-self-test
inspect-standalone-self-test:
	python3 scripts/inspect_standalone_self_test.py

.PHONY: inspect-audio-capture-lifecycles
inspect-audio-capture-lifecycles:
	python3 scripts/inspect_audio_capture_lifecycles.py

.PHONY: test-audio-capture-recovery
test-audio-capture-recovery:
	python3 scripts/test_audio_capture_recovery.py

.PHONY: inspect-android-audio-contract
inspect-android-audio-contract:
	python3 scripts/inspect_android_audio_contract.py

.PHONY: test-windows-hardware-reconnect
test-windows-hardware-reconnect:
	python3 scripts/test_windows_hardware_reconnect.py

.PHONY: test-windows-hardware-probe
test-windows-hardware-probe:
	python3 scripts/test_windows_hardware_probe.py

.PHONY: test-windows-audio-diagnostics
test-windows-audio-diagnostics:
	python3 scripts/test_windows_audio_diagnostics.py

.PHONY: test-windows-audio-source-priority
test-windows-audio-source-priority:
	python3 scripts/test_windows_audio_source_priority.py

.PHONY: inspect-audio-capture-configuration
inspect-audio-capture-configuration:
	python3 scripts/inspect_audio_capture_configuration.py

.PHONY: test-usb-audio-routes
test-usb-audio-routes:
	python3 scripts/test_usb_audio_routes.py

.PHONY: inspect-windows-share-artifact
inspect-windows-share-artifact:
	python3 scripts/inspect_windows_share_artifact.py

.PHONY: inspect-windows-hardware-output
inspect-windows-hardware-output:
	python3 scripts/inspect_windows_hardware_output.py

.PHONY: test-windows-deploy-marker
test-windows-deploy-marker:
	PYTHONPATH=scripts python3 scripts/test_windows_deploy_marker.py

.PHONY: inspect-suspicious-worktree-artifacts
inspect-suspicious-worktree-artifacts:
	python3 scripts/inspect_suspicious_worktree_artifacts.py

.PHONY: plan-cleanup-suspicious-empty-artifacts cleanup-suspicious-empty-artifacts
plan-cleanup-suspicious-empty-artifacts:
	python3 scripts/cleanup_suspicious_empty_artifacts.py plan

cleanup-suspicious-empty-artifacts:
	python3 scripts/cleanup_suspicious_empty_artifacts.py apply

.PHONY: plan-commit-windows-hardware commit-windows-hardware
plan-commit-windows-hardware:
	python3 scripts/commit_windows_hardware.py plan

commit-windows-hardware:
	python3 scripts/commit_windows_hardware.py apply
.PHONY: review-worktree-changes
review-worktree-changes:
	python3 scripts/review_worktree_changes.py

.PHONY: review-worktree-file
review-worktree-file:
	python3 scripts/review_worktree_file.py $(FILE)

.PHONY: review-gnumakefile
review-gnumakefile:
	python3 scripts/review_worktree_file.py GNUmakefile

.PHONY: review-main-makefile
review-main-makefile:
	python3 scripts/review_worktree_file.py Makefile

.PHONY: inspect-windows-signing
inspect-windows-signing:
	python3 scripts/inspect_windows_signing.py

.PHONY: plan-sign-windows-standalone sign-windows-standalone package-signed-windows-standalone
plan-sign-windows-standalone:
	python3 scripts/sign_windows_standalone.py plan

sign-windows-standalone:
	python3 scripts/sign_windows_standalone.py apply

package-signed-windows-standalone: sign-windows-standalone
	python3 scripts/windows_standalone.py package

.PHONY: test-windows-signing
test-windows-signing:
	python3 scripts/test_windows_signing.py

.PHONY: inspect-standalone-hardware-only
inspect-standalone-hardware-only:
	python3 scripts/inspect_standalone_hardware_only.py

.PHONY: test-windows-hardware-status
test-windows-hardware-status:
	python3 scripts/test_windows_hardware_status.py

.PHONY: test-windows-hardware-status-runtime
test-windows-hardware-status-runtime:
	python3 scripts/test_windows_hardware_status_runtime.py

inspect-windows-hardware-protocol:
	python3 scripts/inspect_windows_hardware_protocol.py

test-windows-hardware-protocol:
	python3 scripts/test_windows_hardware_protocol.py

push-windows-hardware:
	python3 scripts/push_windows_hardware.py

report-windows-share-inventory:
	python3 scripts/report_windows_share_inventory.py
