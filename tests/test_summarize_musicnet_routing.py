#!/usr/bin/env python3
import csv
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "musicnet.tsv"
        output = root / "routing.tsv"
        source.write_text(
            "active_notes\tbass_notes\tkeys_notes\tguitar_notes\tother_notes\tbass_visual_notes\tkeys_visual_notes\tguitar_visual_notes\tother_visual_notes\n"
            "1:60,41:67\t--\tC4:1\t--\tG4:1\t--\tC4:1\t--\t--\n", encoding="utf-8")
        subprocess.run(["python3", "scripts/summarize_musicnet_routing.py", str(source), "--output", str(output)], check=True)
        rows = list(csv.DictReader(output.open(encoding="utf-8"), delimiter="\t"))
    assert {row["scope"] for row in rows} == {"All", "Other", "Piano"}
    all_exact = next(row for row in rows if row["scope"] == "All" and row["metric"] == "Exact note in expected row")
    assert (all_exact["accurate"], all_exact["total"]) == ("2", "2")
    other_visible = next(row for row in rows if row["scope"] == "Other" and row["metric"] == "Visible exact note in expected row")
    assert (other_visible["accurate"], other_visible["total"]) == ("0", "1")
    print("summarize_musicnet_routing: ok")


if __name__ == "__main__":
    main()
