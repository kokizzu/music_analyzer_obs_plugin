#!/usr/bin/env python3
"""Resolve the public Pixabay URL for the isolated CC0-origin Rimshot clip.

This only inspects the published detail page.  A later acquisition step must
pin the resolved file checksum before it is considered measurement input.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
from urllib.request import Request, urlopen


PAGE_URL = "https://pixabay.com/sound-effects/musical-rimshot-sweet-107111/"
MP3_RE = re.compile(r"https?(?::|%3A)(?:/|%2F){2}cdn\.pixabay\.com(?:/|%2F)download(?:/|%2F)audio[^\"'<> ]+?\.mp3[^\"'<> ]*", re.I)


def resolve() -> str:
    request = Request(PAGE_URL, headers={"User-Agent": "music-analyzer-obs-plugin/1.0"})
    with urlopen(request, timeout=30) as response:  # nosec B310: pinned public source page
        page = response.read().decode("utf-8", errors="replace")
    required = ("Rimshot (sweet)", "Sajmund", "Free for use")
    if not all(value in page for value in required):
        raise ValueError("Pixabay page no longer identifies the expected isolated Rimshot")
    matches = []
    for value in MP3_RE.findall(page):
        resolved = html.unescape(value).replace("\\/", "/").replace("%3A", ":").replace("%2F", "/")
        if resolved not in matches:
            matches.append(resolved)
    if len(matches) != 1:
        raise ValueError(f"expected one public MP3 URL, found {len(matches)}")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        url = resolve()
    except (OSError, ValueError) as error:
        parser.error(str(error))
    text = (
        "pixabay_rimshot_candidate: source_labelled=1 isolated_duration_seconds=1.072 "
        "origin_license=CC0 acquisition_license=Pixabay-Content-License checksum_pinned=0\n"
        f"pixabay_rimshot_candidate: page={PAGE_URL} resolved_mp3={url}\n"
    )
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"pixabay_rimshot_candidate: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
