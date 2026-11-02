.PHONY: test-routing-duration-score
test-routing-duration-score: tests/test_routing_duration_score.py
	$(PYTHON) tests/test_routing_duration_score.py

.PHONY: build-routing-duration-primary measure-routing-duration-baseline
build-routing-duration-primary: scripts/routing_duration_baseline.py
	$(PYTHON) scripts/routing_duration_baseline.py
measure-routing-duration-baseline: scripts/routing_duration_baseline.py scripts/routing_duration_score.py
	$(PYTHON) scripts/routing_duration_baseline.py --measure

.PHONY: capture-routing-candidates
capture-routing-candidates: scripts/capture_routing_candidates.py tests/routing_candidate_replay.cpp
	$(PYTHON) scripts/capture_routing_candidates.py

.PHONY: publish-routing-duration-checkpoint
publish-routing-duration-checkpoint: scripts/manage_routing_duration_goal.py
	$(PYTHON) scripts/manage_routing_duration_goal.py
