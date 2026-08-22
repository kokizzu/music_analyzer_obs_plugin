#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
	printf '%s\n' 'usage: run_repo_script.sh scripts/<name>.sh [args...]' >&2
	exit 2
fi

script=$1
shift

case "$script" in
	scripts/*.sh) ;;
	*)
		printf 'refusing non-repository script: %s\n' "$script" >&2
		exit 2
		;;
esac

if [ ! -f "$script" ]; then
	printf 'missing repository script: %s\n' "$script" >&2
	exit 2
fi

exec /bin/sh "$script" "$@"
