#!/bin/sh
set -eu

pidfile=build/visual_mining.pid
logfile=build/visual_mining.log
report=build/agpt_guitar_visual_pattern_report.txt
if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'visual_miner=running pid=%s\n' "$pid"
		ps -o pid=,state=,etimes=,pcpu=,pmem=,command= -p "$pid"
		# The durable launcher is a shell.  Show its worker as well so a
		# sleeping launcher cannot be mistaken for an active Python search.
		children=$(pgrep -P "$pid" 2>/dev/null || true)
		if [ -n "$children" ]; then
			printf '%s\n' 'visual_miner_children:'
			ps -o pid=,ppid=,state=,etimes=,pcpu=,pmem=,command= -p "$children"
		fi
	else
		printf 'visual_miner=not-running pid=%s\n' "${pid:---}"
	fi
else
	printf '%s\n' 'visual_miner=not-started'
fi
if [ -f "$logfile" ]; then
	printf '%s\n' 'log_tail:'
	tail -n 12 "$logfile"
fi
if [ -f "$report" ]; then
	printf 'report_lines=%s\n' "$(wc -l < "$report" | tr -d '[:space:]')"
	sed -n '1,120p' "$report"
fi
