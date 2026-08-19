#!/bin/sh
# Promote a fully downloaded partial only after the publisher's checksum passes.
set -eu

archive_path=${1:?usage: finalize_babyslakh_partial.sh ARCHIVE MD5}
expected_md5=${2:?usage: finalize_babyslakh_partial.sh ARCHIVE MD5}
partial_path="$archive_path.part"

if [ ! -s "$partial_path" ]; then
    printf '%s\n' "finalize_babyslakh_partial: missing partial=$partial_path" >&2
    exit 1
fi
printf '%s  %s\n' "$expected_md5" "$partial_path" | md5sum -c -
mv "$partial_path" "$archive_path"
printf '%s\n' "finalize_babyslakh_partial: verified archive=$archive_path"
