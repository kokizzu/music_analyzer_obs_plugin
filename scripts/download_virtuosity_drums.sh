#!/bin/sh
# Fetch the pinned public-domain Virtuosity Drums source into external sample
# storage.  A complete clone is retained because the selected microphone and
# articulation paths are part of the reproducible evaluation provenance.
set -eu

if [ "$#" -ne 3 ]; then
    printf '%s\n' "download_virtuosity_drums: usage: DESTINATION REPOSITORY_URL COMMIT" >&2
    exit 2
fi

destination=$1
repository_url=$2
expected_commit=$3

case "$repository_url" in
    https://github.com/sfzinstruments/virtuosity_drums.git) ;;
    *)
        printf '%s\n' "download_virtuosity_drums: refusing unverified repository=$repository_url" >&2
        exit 2
        ;;
esac

case "$expected_commit" in
    9f04cf9a734527edfbb0a4eee1f674e45bbf71bc) ;;
    *)
        printf '%s\n' "download_virtuosity_drums: refusing unverified commit=$expected_commit" >&2
        exit 2
        ;;
esac

if [ -d "$destination/.git" ]; then
    actual_origin=$(git -C "$destination" config --get remote.origin.url || true)
    actual_commit=$(git -C "$destination" rev-parse HEAD)
    if [ "$actual_origin" = "$repository_url" ] && [ "$actual_commit" = "$expected_commit" ]; then
        if grep -Fqx 'CC0 1.0 Universal' "$destination/LICENSE"; then
            printf '%s\n' "download_virtuosity_drums: reused $destination commit=$actual_commit licence=CC0-1.0"
            exit 0
        fi
        printf '%s\n' "download_virtuosity_drums: missing CC0-1.0 licence text in reused source" >&2
        exit 1
    fi
    printf '%s\n' "download_virtuosity_drums: existing checkout differs from pinned source" >&2
    exit 1
fi

if [ -e "$destination" ]; then
    printf '%s\n' "download_virtuosity_drums: refusing non-checkout destination=$destination" >&2
    exit 1
fi

parent_dir=$(dirname "$destination")
mkdir -p "$parent_dir"
git clone --depth 1 "$repository_url" "$destination"
actual_commit=$(git -C "$destination" rev-parse HEAD)
if [ "$actual_commit" != "$expected_commit" ]; then
    printf '%s\n' "download_virtuosity_drums: expected commit=$expected_commit got=$actual_commit" >&2
    exit 1
fi
if ! grep -Fqx 'CC0 1.0 Universal' "$destination/LICENSE"; then
    printf '%s\n' "download_virtuosity_drums: missing CC0-1.0 licence text" >&2
    exit 1
fi

printf '%s\n' "download_virtuosity_drums: downloaded $destination commit=$actual_commit licence=CC0-1.0"
