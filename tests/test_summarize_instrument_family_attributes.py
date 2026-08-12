#!/usr/bin/env python3

import importlib.util
from pathlib import Path
import tempfile


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "summarize_instrument_family_attributes.py"
SPEC = importlib.util.spec_from_file_location("summarize_instrument_family_attributes", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


HEADER = (
    "sample_id\tfamily\tinstrument\tsubset\tbuffer_index\texpected_row_hit"
    "\tguitar_active\tpiano_active\tvocals_active\tother_active"
    "\tguitar_confidence\tpiano_confidence\tvocals_confidence\tother_confidence"
    "\tguitar_label\tpiano_label\tvocals_label\tother_label\n"
)


def row(sample_id, family, instrument, hit, active):
    active_values = ["1" if name in active else "0" for name in MODULE.FAMILIES]
    return "\t".join(
        [sample_id, family, instrument, "test", "0", str(int(hit)), *active_values,
         "0", "0", "0", "0", "--", "--", "--", "--"]
    ) + "\n"


with tempfile.TemporaryDirectory() as temporary:
    path = Path(temporary) / "attributes.tsv"
    path.write_text(
        HEADER
        + row("sax-1", "other", "tenor sax", False, {"piano"})
        + row("sax-1", "other", "tenor sax", True, {"other", "piano"})
        + row("violin-1", "other", "violin", False, {"guitar"}),
        encoding="utf-8",
    )
    output = MODULE.summarize(path)

assert output[0] == "instrument_family_attribute_summary: windows=3", output
assert "other=1/3 (33.3%)" in output[1], output
assert "other->piano=1" in output[2], output
assert "other->guitar=1" in output[2], output
assert "other/tenor sax=1/2 (50.0%)" in output[3], output
