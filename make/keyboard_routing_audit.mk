# Development-only attribution; no detector changes or held-out consumption.
.PHONY: test-keyboard-routing-gaps audit-keyboard-routing-gaps
test-keyboard-routing-gaps: tests/test_keyboard_routing_gaps.py scripts/audit_keyboard_routing_gaps.py
	.separator-venv/bin/python tests/test_keyboard_routing_gaps.py
audit-keyboard-routing-gaps: scripts/audit_keyboard_routing_gaps.py
	.separator-venv/bin/python scripts/audit_keyboard_routing_gaps.py
