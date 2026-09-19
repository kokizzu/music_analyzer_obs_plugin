.PHONY: inspect-windows-standalone
inspect-windows-standalone:
	python3 scripts/windows_standalone.py inspect

.PHONY: test-visualizer-parentheses
test-visualizer-parentheses:
	python3 scripts/test_visualizer_parentheses.py

.PHONY: test-visualizer-glyph-coverage
test-visualizer-glyph-coverage:
	python3 scripts/test_visualizer_glyph_coverage.py

.PHONY: test-visualizer-label-glyphs
test-visualizer-label-glyphs:
	python3 scripts/test_visualizer_label_glyphs.py

.PHONY: plan-commit-visualizer-label-glyphs commit-visualizer-label-glyphs
plan-commit-visualizer-label-glyphs:
	python3 scripts/commit_visualizer_label_glyphs.py plan

commit-visualizer-label-glyphs:
	python3 scripts/commit_visualizer_label_glyphs.py apply

.PHONY: plan-commit-share-runtime-verifier commit-share-runtime-verifier
plan-commit-share-runtime-verifier:
	python3 scripts/commit_share_runtime_verifier.py plan

commit-share-runtime-verifier:
	python3 scripts/commit_share_runtime_verifier.py apply

.PHONY: plan-commit-windows-runtime-test commit-windows-runtime-test
plan-commit-windows-runtime-test:
	python3 scripts/commit_windows_runtime_test.py plan

commit-windows-runtime-test:
	python3 scripts/commit_windows_runtime_test.py apply

.PHONY: prepare-windows-standalone windows-standalone
prepare-windows-standalone:
	python3 scripts/windows_standalone.py prepare

windows-standalone:
	python3 scripts/windows_standalone.py build

.PHONY: verify-windows-standalone package-windows-standalone
verify-windows-standalone:
	python3 scripts/windows_standalone.py verify

.PHONY: verify-windows-share-runtime
verify-windows-share-runtime:
	python3 scripts/verify_windows_share_runtime.py

.PHONY: verify-windows-signed-runtime
verify-windows-signed-runtime:
	python3 scripts/verify_windows_signed_runtime.py

.PHONY: plan-commit-signed-runtime commit-signed-runtime
plan-commit-signed-runtime:
	python3 scripts/commit_signed_runtime_check.py plan

commit-signed-runtime:
	python3 scripts/commit_signed_runtime_check.py apply

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

.PHONY: inspect-windows-build-log
inspect-windows-build-log:
	python3 scripts/inspect_windows_build_log.py

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

.PHONY: test-windows-loopback-recovery
test-windows-loopback-recovery:
	python3 scripts/test_windows_loopback_recovery.py

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

.PHONY: test-windows-self-signed-deploy-fallback
test-windows-self-signed-deploy-fallback:
	python3 scripts/test_windows_self_signed_deploy_fallback.py

.PHONY: plan-commit-windows-signed-deploy-fallback commit-windows-signed-deploy-fallback
plan-commit-windows-signed-deploy-fallback:
	python3 scripts/commit_windows_signed_deploy_fallback.py plan

commit-windows-signed-deploy-fallback:
	python3 scripts/commit_windows_signed_deploy_fallback.py apply

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

.PHONY: discover-windows-signing-certificate
discover-windows-signing-certificate:
	python3 scripts/discover_windows_signing_certificate.py

.PHONY: inspect-windows-certificate
inspect-windows-certificate:
	python3 scripts/inspect_windows_certificate.py

.PHONY: inspect-windows-self-sign
inspect-windows-self-sign:
	python3 scripts/inspect_windows_self_sign.py

.PHONY: inspect-windows-self-signed-deploy
inspect-windows-self-signed-deploy:
	python3 scripts/inspect_windows_self_signed_deploy.py

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

.PHONY: test-windows-gatt-abi
test-windows-gatt-abi:
	python3 scripts/test_windows_gatt_abi.py

.PHONY: plan-commit-windows-protocol commit-windows-protocol
plan-commit-windows-protocol:
	python3 scripts/commit_windows_protocol.py plan

commit-windows-protocol:
	python3 scripts/commit_windows_protocol.py apply

push-windows-hardware:
	python3 scripts/push_windows_hardware.py
.PHONY: test-windows-gatt-interface
test-windows-gatt-interface:
	python3 scripts/test_windows_gatt_interface.py

.PHONY: test-windows-diagnostic-output
test-windows-diagnostic-output:
	python3 scripts/test_windows_diagnostic_output.py

.PHONY: plan-commit-windows-diagnostic-output commit-windows-diagnostic-output
plan-commit-windows-diagnostic-output:
	python3 scripts/commit_windows_diagnostic_output.py plan

commit-windows-diagnostic-output:
	python3 scripts/commit_windows_diagnostic_output.py apply

.PHONY: plan-commit-windows-gatt-interface commit-windows-gatt-interface
plan-commit-windows-gatt-interface:
	python3 scripts/commit_windows_gatt_interface.py plan

commit-windows-gatt-interface:
	python3 scripts/commit_windows_gatt_interface.py apply


report-windows-share-inventory:
	python3 scripts/report_windows_share_inventory.py

.PHONY: report-windows-hardware-source
report-windows-hardware-source:
	python3 scripts/report_windows_hardware_source.py

.PHONY: report-fret-zealot-sdk
report-fret-zealot-sdk:
	python3 scripts/report_fret_zealot_sdk.py

.PHONY: report-fret-zealot-sdk-usage
report-fret-zealot-sdk-usage:
	python3 scripts/report_fret_zealot_sdk_usage.py

.PHONY: report-windows-litejam-source
report-windows-litejam-source:
	python3 scripts/report_windows_source_range.py

.PHONY: test-windows-hardware-retry-contract
test-windows-hardware-retry-contract:
	python3 scripts/test_windows_hardware_retry_contract.py

.PHONY: report-windows-deploy-source
report-windows-deploy-source:
	python3 scripts/report_windows_deploy_source.py

.PHONY: inspect-scoped-windows-hardware-diff
inspect-scoped-windows-hardware-diff:
	python3 scripts/inspect_scoped_windows_hardware_diff.py

.PHONY: verify-windows-hardware-checklist
verify-windows-hardware-checklist: test-windows-hardware-retry-contract test-windows-hardware-reconnect test-windows-hardware-status test-windows-hardware-status-runtime test-windows-diagnostic-output test-windows-midi-protocol verify-windows-standalone verify-windows-runtime-bundle
	python3 scripts/windows_hardware_checklist.py

.PHONY: plan-commit-windows-hardware-reliability commit-windows-hardware-reliability
plan-commit-windows-hardware-reliability:
	python3 scripts/commit_windows_hardware_reliability.py plan

commit-windows-hardware-reliability:
	python3 scripts/commit_windows_hardware_reliability.py apply

.PHONY: report-windows-hardware-source
report-windows-hardware-source:
	python3 scripts/report_windows_hardware_source.py

.PHONY: report-fret-zealot-sdk
report-fret-zealot-sdk:
	python3 scripts/report_fret_zealot_sdk.py

.PHONY: report-windows-litejam-source
report-windows-litejam-source:
	python3 scripts/report_windows_source_range.py

.PHONY: test-windows-hardware-retry-contract
test-windows-hardware-retry-contract:
	python3 scripts/test_windows_hardware_retry_contract.py

.PHONY: report-windows-deploy-source
report-windows-deploy-source:
	python3 scripts/report_windows_deploy_source.py

.PHONY: inspect-scoped-windows-hardware-diff
inspect-scoped-windows-hardware-diff:
	python3 scripts/inspect_scoped_windows_hardware_diff.py

.PHONY: verify-windows-hardware-checklist
verify-windows-hardware-checklist: test-windows-hardware-retry-contract test-windows-hardware-reconnect test-windows-hardware-status test-windows-hardware-status-runtime test-windows-diagnostic-output test-windows-midi-protocol verify-windows-standalone verify-windows-runtime-bundle
	python3 scripts/windows_hardware_checklist.py

.PHONY: plan-commit-windows-hardware-reliability commit-windows-hardware-reliability
plan-commit-windows-hardware-reliability:
	python3 scripts/commit_windows_hardware_reliability.py plan

commit-windows-hardware-reliability:
	python3 scripts/commit_windows_hardware_reliability.py apply

WINDOWS_MIDI_PROTOCOL_TEST_BIN := $(BUILD_DIR)/windows_midi_protocol_tests

$(WINDOWS_MIDI_PROTOCOL_TEST_BIN): tests/windows_midi_protocol.cpp src/fret_control.cpp src/fret_control.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc tests/windows_midi_protocol.cpp src/fret_control.cpp -o $@

test-windows-midi-protocol: $(WINDOWS_MIDI_PROTOCOL_TEST_BIN)
	$(WINDOWS_MIDI_PROTOCOL_TEST_BIN)
.PHONY: test-windows-deploy-signing-gate
test-windows-deploy-signing-gate:
	$(PYTHON) scripts/test_windows_deploy_signing_gate.py
.PHONY: check-windows-share-connectivity
check-windows-share-connectivity:
	python3 scripts/check_windows_share_connectivity.py

.PHONY: commit-windows-share-connectivity
commit-windows-share-connectivity:
	python3 scripts/commit_windows_share_connectivity.py
