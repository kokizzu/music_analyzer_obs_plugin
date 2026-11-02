# Independent instrument evidence for experimental note recovery.
.PHONY: test-piano-context-features capture-piano-context
test-piano-context-features: tests/test_piano_context_features.py scripts/piano_context_features.py
	.separator-venv/bin/python tests/test_piano_context_features.py
capture-piano-context: scripts/capture_piano_context.py
	.separator-venv/bin/python scripts/capture_piano_context.py

.PHONY: evaluate-piano-context
evaluate-piano-context: scripts/evaluate_piano_context.py
	.separator-venv/bin/python scripts/evaluate_piano_context.py

.PHONY: audit-piano-context-recovery
audit-piano-context-recovery: scripts/audit_piano_context_recovery.py
	.separator-venv/bin/python scripts/audit_piano_context_recovery.py

.PHONY: verify-piano-context stage-piano-context publish-piano-context
verify-piano-context: scripts/checkpoint_piano_context.py
	.separator-venv/bin/python scripts/checkpoint_piano_context.py
stage-piano-context: scripts/checkpoint_piano_context.py
	.separator-venv/bin/python scripts/checkpoint_piano_context.py --stage
publish-piano-context: scripts/checkpoint_piano_context.py
	.separator-venv/bin/python scripts/checkpoint_piano_context.py --publish
