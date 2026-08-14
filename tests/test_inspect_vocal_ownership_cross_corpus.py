#!/usr/bin/env python3
"""Regression checks for cross-corpus vocal ownership accounting."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_vocal_ownership_cross_corpus.py"
SPEC = importlib.util.spec_from_file_location("inspect_cross_corpus", SCRIPT)
assert SPEC and SPEC.loader
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.tsv"
        path.write_text(
            "family\tstatus\texpected_midi\tdebug_midi\tdebug_owner\n"
            "vocals\townership_miss\t60\t60\tkeys\n"
            "vocals\thit\t61\t61\tpiano\n"
            "vocals\tmiss\t62\t\t\n"
            "other\townership_miss\t60\t60\tkeys\n",
            encoding="utf-8",
        )
        rows = {(corpus, owner): values for corpus, owner, *values in INSPECT.summarize([("fixture", path)])}
        assert rows[("fixture", "keyboard")] == [1, 1, 0, 2]
        assert rows[("fixture", "none")] == [0, 0, 1, 1]
        assert len(rows) == 2
    print("test_inspect_vocal_ownership_cross_corpus: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
