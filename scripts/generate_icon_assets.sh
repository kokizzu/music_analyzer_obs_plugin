#!/bin/sh
set -eu

if [ "$#" -gt 1 ]; then
	printf '%s\n' 'usage: generate_icon_assets.sh [source.png]' >&2
	exit 2
fi

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_image=${1:-"$root/assets/music-analyzer-icon.png"}
master="$root/assets/music-analyzer-icon.png"
header="$root/src/app_icon_rgba.hpp"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

if [ ! -f "$source_image" ]; then
	printf 'icon source not found: %s\n' "$source_image" >&2
	exit 1
fi

mkdir -p "$root/assets"
convert "$source_image" -auto-orient -resize '1024x1024^' -gravity center \
	-extent 1024x1024 -strip "PNG32:$tmp_dir/master.png"
mv "$tmp_dir/master.png" "$master"

for entry in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
	density=${entry%%:*}
	size=${entry##*:}
	destination="$root/android/app/src/main/res/mipmap-$density/ic_launcher.png"
	mkdir -p "$(dirname -- "$destination")"
	convert "$master" -filter Lanczos -resize "${size}x${size}" -strip "PNG32:$destination"
done

convert "$master" -filter Lanczos -resize '64x64' -depth 8 "RGBA:$tmp_dir/icon.rgba"
byte_count=$(wc -c < "$tmp_dir/icon.rgba" | tr -d ' ')
if [ "$byte_count" -ne 16384 ]; then
	printf 'unexpected standalone icon byte count: %s\n' "$byte_count" >&2
	exit 1
fi

{
	printf '%s\n' '#pragma once' '' '#include <array>' '#include <cstdint>' '' 'namespace mao::generated {' ''
	printf '%s\n' 'inline constexpr int kAppIconWidth = 64;' 'inline constexpr int kAppIconHeight = 64;'
	printf '%s\n' 'inline constexpr std::array<std::uint8_t, 16384> kAppIconRgba = {'
	od -An -v -t u1 "$tmp_dir/icon.rgba" | awk '
		{
			for (i = 1; i <= NF; ++i) {
				if (column == 0)
					printf "\t";
				printf "%s,", $i;
				column++;
				if (column == 24) {
					printf "\n";
					column = 0;
				} else {
					printf " ";
				}
			}
		}
		END {
			if (column != 0)
				printf "\n";
		}'
	printf '%s\n' '};' '' '} // namespace mao::generated'
} > "$tmp_dir/app_icon_rgba.hpp"
sed -i 's/[[:space:]]*$//' "$tmp_dir/app_icon_rgba.hpp"
mv "$tmp_dir/app_icon_rgba.hpp" "$header"

printf 'generated icon assets from %s\n' "$source_image"
