#!/bin/sh
# Print the persistent user objective without treating it as executable input.
set -eu

goal_path=${1:?usage: show_active_goal.sh GOAL_PATH}
cat "$goal_path"
