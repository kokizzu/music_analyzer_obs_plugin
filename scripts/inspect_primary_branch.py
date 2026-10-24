#!/usr/bin/env python3
"""Read-only primary-branch, remote identity and dirty-scope inspection."""
import json
import re
import subprocess


def git(*args):
    return subprocess.run(["git", *args], text=True, capture_output=True, timeout=60)


def main():
    branch = git("branch", "--show-current").stdout.strip()
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    status = git("status", "--porcelain=v1")
    remotes = {}
    for remote in git("remote").stdout.splitlines():
        address = git("remote", "get-url", remote).stdout.strip()
        address = re.sub(r"(https?://)[^/@]+@", r"\1[redacted]@", address)
        result = git("ls-remote", "--symref", remote, "HEAD")
        primary = next((line.split()[1].removeprefix("refs/heads/")
                        for line in result.stdout.splitlines() if line.startswith("ref:")), None)
        remotes[remote] = dict(url=address, primary=primary, verified=result.returncode == 0,
                               error=result.stderr.strip() if result.returncode else None)
    header = git("show", "HEAD:src/analyzer.hpp").stdout
    capabilities = {name: name in header for name in ("resolve_analysis_window_samples", "vocal_notes", "other_notes", "global_chord", "experimental_pcm_tempo_correction")}
    print(json.dumps(dict(branch=branch, upstream=upstream.stdout.strip(), remotes=remotes,
                          head_capabilities=capabilities,
                          staged=git("diff", "--cached", "--name-only").stdout.splitlines(),
                          dirty_count=len(status.stdout.splitlines()),
                          dirty_paths=status.stdout.splitlines()[:100]), indent=2))


if __name__ == "__main__":
    main()
