.PHONY: test-visual-row-contract
test-visual-row-contract: tests/test_visual_row_contract.py scripts/visual_row_contract.py
	$(PYTHON) tests/test_visual_row_contract.py

.PHONY: inspect-visual-row-contract publish-visual-row-contract
inspect-visual-row-contract: scripts/manage_visual_row_contract.py
	$(PYTHON) scripts/manage_visual_row_contract.py inspect
publish-visual-row-contract: scripts/manage_visual_row_contract.py
	$(PYTHON) scripts/manage_visual_row_contract.py publish
