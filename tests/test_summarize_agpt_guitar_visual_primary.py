#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_agpt_guitar_visual_primary.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        source = work / "attributes.tsv"
        output = work / "summary.tsv"
        source.write_text(
            "sample_id\tfamily\texpected_note\tvisual_first_row\tguitar_visual_notes\n"
            "one\tguitar\tE2\tguitar\tE2:1.00,E3:0.50\n"
            "one\tguitar\tE2\tpiano\tE2:1.00\n"
            "two\tguitar\tF2\tguitar\tF3:1.00\n"
            "two\tguitar\tF2\tguitar\tF2:0.62\n"
            "three\tguitar\tG2\tamb\tG2:1.00\n",
            encoding="utf-8",
        )
        subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--output", str(output)], check=True)
        assert output.read_text(encoding="utf-8") == (
            "corpus\tmetric\taccurate\ttotal\tremaining\n"
            "AG-PT\tGuitar visual primary row (buffer)\t3\t5\t2\n"
            "AG-PT\tGuitar visual primary row (sample)\t2\t3\t1\n"
            "AG-PT\texpected exact note on Guitar visual primary (buffer)\t2\t5\t3\n"
            "AG-PT\texpected exact note on Guitar visual primary (sample)\t2\t3\t1\n"
        )
    print("test_summarize_agpt_guitar_visual_primary: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
