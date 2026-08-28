#!/bin/sh
# Report whether the external target can hold the directly downloadable E-GMD archive.
set -eu

directory=${1:?usage: check_egmd_storage.sh DIRECTORY REQUIRED_BYTES}
required_bytes=${2:?usage: check_egmd_storage.sh DIRECTORY REQUIRED_BYTES}

mkdir -p "$directory"
available_kib=$(df -Pk "$directory" | awk 'NR == 2 { print $4 }')
case "$available_kib" in
    ''|*[!0-9]*)
        printf '%s\n' "check_egmd_storage: could not determine free space for $directory" >&2
        exit 2
        ;;
esac
available_bytes=$((available_kib * 1024))
printf 'storage_path=%s\nrequired_bytes=%s\navailable_bytes=%s\n' "$directory" "$required_bytes" "$available_bytes"
if [ "$available_bytes" -lt "$required_bytes" ]; then
    printf '%s\n' "check_egmd_storage: insufficient external storage" >&2
    exit 2
fi
