#!/usr/bin/env python3
"""Summarize active and inactive IDMT hi-hat rows by detector evidence."""

import csv
from collections import Counter
from pathlib import Path


PATH = Path("build/idmt_drums_primary_attribute_rows_hihat.tsv")


def main() -> None:
    with PATH.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    print("fields=" + ",".join(rows[0]))
    inactive = [row for row in rows if row.get("hihat_level") in {"", "0.000000"}]
    weak = [row for row in rows if 0.0 < float(row.get("hihat_level", "0")) <= 0.30]
    print(f"rows={len(rows)} inactive={len(inactive)} subthreshold={len(weak)}")
    for name, selected in (("inactive", inactive), ("subthreshold", weak)):
        print(name)
        for row in selected[:80]:
            print(
                f"  {row['sample']} level={row['hihat_level']} band={row['hihat_band']} "
                f"seg={row['hihat_seg']} trigger={row['hihat_trigger']} "
                f"threshold={row['hihat_threshold']} got={row['got']} "
                f"kick={row['kick_level']} snare={row['snare_level']} crash={row['crash_level']} "
                f"tom={row['tom_level']} ride={row['ride_level']} rim={row['rim_level']} "
                f"high={row.get('energy_high', '')} flags={row['rule_flags']}"
            )
        print("flags=" + ", ".join(f"{flag}:{count}" for flag, count in Counter(row['rule_flags'] for row in selected).most_common()))


if __name__ == "__main__":
    main()
