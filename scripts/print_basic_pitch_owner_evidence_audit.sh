#!/bin/sh
set -eu

input=${1:?usage: print_basic_pitch_owner_evidence_audit.sh <owner-evidence.tsv>}
exec python3 scripts/summarize_basic_pitch_owner_evidence.py "$input"
