#!/usr/bin/env python3
"""Regression checks for the resumable external URMP download helpers."""

from pathlib import Path


def test_download_script_keeps_partial_archive_external_and_verifies_zip() -> None:
    text = Path("scripts/download_urmp_archive.sh").read_text(encoding="utf-8")
    assert 'partial="${archive}.part"' in text
    assert 'curl -fL -C - -o "$partial" "$url"' in text
    assert 'unzip -tqq "$partial"' in text
    assert 'mv -f "$partial" "$archive"' in text


def test_status_script_reports_partial_or_verified_archive() -> None:
    text = Path("scripts/urmp_download_status.sh").read_text(encoding="utf-8")
    assert "URMP archive ready" in text
    assert "URMP download in progress" in text
    assert "not transfer progress" in text
