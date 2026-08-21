#!/bin/sh
# Record the exact upstream revision for the openly licensed Virtuosity Drums
# source before any samples are transferred into external InstrumentSamples.
set -eu

if [ "$#" -ne 2 ]; then
    printf '%s\n' "probe_virtuosity_drums_source: usage: REPOSITORY_URL BRANCH" >&2
    exit 2
fi

repository_url=$1
branch=$2

case "$repository_url" in
    https://github.com/sfzinstruments/virtuosity_drums.git) ;;
    *)
        printf '%s\n' "probe_virtuosity_drums_source: refusing unverified repository=$repository_url" >&2
        exit 2
        ;;
esac

case "$branch" in
    main|master) ;;
    *)
        printf '%s\n' "probe_virtuosity_drums_source: refusing unverified branch=$branch" >&2
        exit 2
        ;;
esac

revision=$(git ls-remote --refs "$repository_url" "refs/heads/$branch" | awk 'NR == 1 { print $1 }')
case "$revision" in
    [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) ;;
    *)
        printf '%s\n' "probe_virtuosity_drums_source: missing 40-hex revision for branch=$branch" >&2
        exit 1
        ;;
esac

printf '%s\n' "virtuosity_drums_source: repository=$repository_url branch=$branch commit=$revision licence=CC0-1.0"
