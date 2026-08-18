#!/usr/bin/env python3
"""Extract timing-related XML metadata from IDMT-SMT-Bass single tracks.

Note CSVs provide precise onsets, but note onsets alone are not an editorial
beat grid. This inspector records timing and pattern fields supplied by the
corpus itself before it is considered for BPM validation.
"""

import argparse
import csv
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


XML_RE = re.compile(r"^annotation/(\d{3})\.xml$")
TIMING_WORDS = ("tempo", "bpm", "beat", "meter", "metre", "pattern", "bar", "grid")


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def timing_related(name):
    return any(word in name.lower() for word in TIMING_WORDS)


def leaf_parameters(root):
    global_parameter = next(
        (element for element in root.iter() if local_name(element.tag) == "globalParameter"),
        None,
    )
    if global_parameter is None:
        return []
    parameters = []
    for element in global_parameter.iter():
        if element is global_parameter or list(element):
            continue
        value = (element.text or "").strip()
        if value:
            parameters.append((local_name(element.tag), value))
    return sorted(parameters, key=lambda item: (item[0].lower(), item[0], item[1]))


def inspect_archive(archive_path):
    rows = []
    with zipfile.ZipFile(archive_path) as archive:
        members = []
        for member in archive.namelist():
            match = XML_RE.match(member)
            if match:
                members.append((match.group(1), member))
        for track_id, member in sorted(members):
            root = ET.fromstring(archive.read(member))
            for name, value in leaf_parameters(root):
                rows.append((track_id, name, value, "yes" if timing_related(name) else ""))
    return rows


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(("track_id", "parameter", "value", "timing_or_pattern_field"))
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.archive.is_file():
        raise SystemExit(f"inspect_idmt_bass_tempo_metadata: missing archive: {args.archive}")
    try:
        rows = inspect_archive(args.archive)
    except (OSError, ET.ParseError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"inspect_idmt_bass_tempo_metadata: {exc}") from exc
    write_rows(args.output, rows)
    tracks = {row[0] for row in rows}
    timing = sorted({row[1] for row in rows if row[3]})
    print(
        "inspect_idmt_bass_tempo_metadata: "
        f"tracks={len(tracks)} fields={len(rows)} timing_fields={','.join(timing) or 'none'} "
        f"output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
