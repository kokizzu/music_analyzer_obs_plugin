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
REQUIRED_PAGE_TEXT = ("Rimshot (sweet)", "Sajmund", "Free for use")
MP3_RE = re.compile(r"https?(?::|%3A)(?:/|%2F){2}cdn\.pixabay\.com(?:/|%2F)download(?:/|%2F)audio[^\"'<> ]+?\.mp3[^\"'<> ]*", re.I)


def resolve_page(page: str, required_text: tuple[str, ...], page_html: str | None = None) -> str:
    if not required_text:
        raise ValueError("at least one expected source label is required")
    if page_html is None:
        request = Request(page, headers={"User-Agent": "music-analyzer-obs-plugin/1.0"})
        with urlopen(request, timeout=30) as response:  # nosec B310: pinned public source page
            page_html = response.read().decode("utf-8", errors="replace")
    if not all(value in page_html for value in required_text):
        raise ValueError("Pixabay page no longer identifies the expected isolated Rimshot")
    matches = []
    for value in MP3_RE.findall(page_html):
        resolved = html.unescape(value).replace("\\/", "/").replace("%3A", ":").replace("%2F", "/")
        if resolved not in matches:
            matches.append(resolved)
    if len(matches) != 1:
        raise ValueError(f"expected one public MP3 URL, found {len(matches)}")
    return matches[0]


def resolve(page: str = PAGE_URL, required_text: tuple[str, ...] = REQUIRED_PAGE_TEXT) -> str:
    request = Request(page, headers={"User-Agent": "music-analyzer-obs-plugin/1.0"})
    with urlopen(request, timeout=30) as response:  # nosec B310: pinned public source page
        page = response.read().decode("utf-8", errors="replace")
    return resolve_page(request.full_url, required_text, page)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--page", default=PAGE_URL)
    parser.add_argument("--require", dest="required_text", action="append")
    parser.add_argument("--candidate-name", default="pixabay_rimshot_candidate")
    parser.add_argument("--duration-seconds", default="1.072")
    parser.add_argument("--origin-license", default="CC0")
    args = parser.parse_args(argv)
    required_text = tuple(args.required_text) if args.required_text else REQUIRED_PAGE_TEXT
    try:
        url = resolve(args.page, required_text)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    text = (
        f"{args.candidate_name}: source_labelled=1 isolated_duration_seconds={args.duration_seconds} "
        f"origin_license={args.origin_license} acquisition_license=Pixabay-Content-License checksum_pinned=0\n"
        f"{args.candidate_name}: page={args.page} resolved_mp3={url}\n"
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
