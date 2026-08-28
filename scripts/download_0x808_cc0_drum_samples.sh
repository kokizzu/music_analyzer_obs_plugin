#!/bin/sh
# Download the small, independently licensed 0x808 drum-machine source into
# the shared sample store.  It is deliberately idempotent so corpus replays
# never duplicate large files under build/.
set -eu

destination=${1:?usage: download_0x808_cc0_drum_samples.sh DESTINATION REPOSITORY}
repository=${2:?usage: download_0x808_cc0_drum_samples.sh DESTINATION REPOSITORY}

if [ -d "$destination/.git" ]; then
    printf '%s\n' "0x808 CC0 source: reusing $destination"
    exit 0
fi

if [ -e "$destination" ]; then
    printf '%s\n' "0x808 CC0 source: refusing to replace existing $destination" >&2
    exit 1
fi

mkdir -p "$(dirname "$destination")"
git clone --depth 1 "$repository" "$destination"

if [ ! -d "$destination/samples/505" ] || [ ! -f "$destination/samples/LICENSE.md" ]; then
    printf '%s\n' "0x808 CC0 source: expected samples/505 and samples/LICENSE.md" >&2
    exit 1
fi

printf '%s\n' "0x808 CC0 source: downloaded to $destination"
