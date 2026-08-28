#!/bin/sh
# Inspect official DREANSS-linked source pages for direct archive URLs only.
set -eu

for page in \
	'https://www.upf.edu/web/mtg/mass' \
	'https://bass-db.gforge.inria.fr/bss_oracle/'
do
	printf 'source_page=%s\n' "$page"
	content=$(curl -fsSL --max-time 20 -A 'Mozilla/5.0' "$page" 2>/dev/null || true)
	if [ -z "$content" ]; then
		printf 'result=unavailable\n'
		continue
	fi
	printf '%s\n' "$content" |
		rg -io 'https?://[^"'"'"' <>]+\.(zip|tar|tar\.gz|tgz)(\?[^"'"'"' <>]+)?' |
		sort -u || true
done
