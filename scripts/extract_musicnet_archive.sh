#!/bin/sh
# Extract a validated MusicNet archive without ever placing corpus audio under build/.
set -eu

archive=${1:?missing MusicNet archive path}
destination=${2:?missing MusicNet extraction destination}

has_musicnet_layout() {
    [ -d "$1/train_data" ] || [ -d "$1/test_data" ]
}

if [ ! -f "$archive" ]; then
    echo "MusicNet archive is missing: $archive" >&2
    exit 1
fi

if has_musicnet_layout "$destination"; then
    echo "MusicNet extraction is ready: $destination"
    exit 0
fi

if [ -e "$destination" ]; then
    echo "refusing to replace incomplete MusicNet destination: $destination" >&2
    exit 1
fi

case "$destination" in
    */*) parent=${destination%/*} ;;
    *) parent=. ;;
esac
stage="$destination.extracting"

rm -rf "$stage"
mkdir -p "$stage/archive"
tar -xzf "$archive" -C "$stage/archive"
# Archives may retain restrictive directory modes.  This is a private staging
# tree, so make it removable and traversable before inspecting it.
chmod -R u+rwX "$stage"

candidate=
if has_musicnet_layout "$stage/archive"; then
    candidate="$stage/archive"
else
    for child in "$stage/archive"/*; do
        if [ -d "$child" ] && has_musicnet_layout "$child"; then
            if [ -n "$candidate" ]; then
                echo "MusicNet archive contains multiple possible layouts" >&2
                rm -rf "$stage"
                exit 1
            fi
            candidate=$child
        fi
    done
fi

if [ -z "$candidate" ]; then
    echo "MusicNet archive does not contain train_data or test_data" >&2
    rm -rf "$stage"
    exit 1
fi

mkdir -p "$parent"
mv "$candidate" "$destination"
rm -rf "$stage"
echo "MusicNet extraction is ready: $destination"
