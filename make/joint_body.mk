# Stable-body release experiments and their independent validation.
.PHONY: test-joint-grace-body build-joint-body-trial
$(BUILD_DIR)/joint_grace_body: tests/joint_grace_body.cpp src/joint_grace_body.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -Isrc $< -o $@
test-joint-grace-body: $(BUILD_DIR)/joint_grace_body
	$(BUILD_DIR)/joint_grace_body
build-joint-body-trial: scripts/build_joint_body_trial.py
	$(PYTHON) scripts/build_joint_body_trial.py

.PHONY: measure-joint-body-training measure-joint-body-calibration
measure-joint-body-training: scripts/measure_joint_body.py
	$(PYTHON) scripts/measure_joint_body.py
measure-joint-body-calibration: scripts/measure_joint_body.py
	$(PYTHON) scripts/measure_joint_body.py --calibration

.PHONY: freeze-joint-body-fresh measure-joint-body-fresh-a measure-joint-body-fresh-b measure-joint-body-fresh-c measure-joint-body-fresh-d
freeze-joint-body-fresh: scripts/run_joint_body_fresh.py
	$(PYTHON) scripts/run_joint_body_fresh.py --freeze
measure-joint-body-fresh-a: scripts/run_joint_body_fresh.py
	$(PYTHON) scripts/run_joint_body_fresh.py --record 17
measure-joint-body-fresh-b: scripts/run_joint_body_fresh.py
	$(PYTHON) scripts/run_joint_body_fresh.py --record 18
measure-joint-body-fresh-c: scripts/run_joint_body_fresh.py
	$(PYTHON) scripts/run_joint_body_fresh.py --record 19
measure-joint-body-fresh-d: scripts/run_joint_body_fresh.py
	$(PYTHON) scripts/run_joint_body_fresh.py --record 20

.PHONY: plan-joint-body-controls validate-joint-body-controls-a validate-joint-body-controls-b validate-joint-body-controls-c validate-joint-body-controls-d
plan-joint-body-controls: scripts/validate_joint_body_controls.py
	$(PYTHON) scripts/validate_joint_body_controls.py --plan
validate-joint-body-controls-a: scripts/validate_joint_body_controls.py
	$(PYTHON) scripts/validate_joint_body_controls.py --shard 0
validate-joint-body-controls-b: scripts/validate_joint_body_controls.py
	$(PYTHON) scripts/validate_joint_body_controls.py --shard 1
validate-joint-body-controls-c: scripts/validate_joint_body_controls.py
	$(PYTHON) scripts/validate_joint_body_controls.py --shard 2
validate-joint-body-controls-d: scripts/validate_joint_body_controls.py
	$(PYTHON) scripts/validate_joint_body_controls.py --shard 3

.PHONY: audit-joint-body-context
audit-joint-body-context: scripts/audit_joint_body_context.py
	$(PYTHON) scripts/audit_joint_body_context.py

.PHONY: stage-joint-body publish-joint-body
stage-joint-body: scripts/checkpoint_joint_body.py
	$(PYTHON) scripts/checkpoint_joint_body.py --stage
publish-joint-body: scripts/checkpoint_joint_body.py
	$(PYTHON) scripts/checkpoint_joint_body.py --publish
