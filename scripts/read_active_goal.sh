#!/bin/sh
# Print the active pasted goal through the repository's Makefile helper.
set -eu

goal_file=${1:?usage: read_active_goal.sh <goal-file>}
exec sed -n '1,240p' "$goal_file"
