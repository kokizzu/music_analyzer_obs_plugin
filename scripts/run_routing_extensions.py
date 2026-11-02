#!/usr/bin/env python3
"""Serialize identical replay selections to prevent checkpoint/TSV collisions."""
import argparse
import fcntl
import subprocess
import sys

from routing_duration_baseline import ROOT

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=('original', 'rate48', 'reserved'), required=True)
parser.add_argument('--shards', type=int, default=1)
parser.add_argument('--shard', type=int, default=0)
args = parser.parse_args()
assert 0 <= args.shard < args.shards
directory = ROOT / 'build/piano_guitar_extensions'
directory.mkdir(parents=True, exist_ok=True)
with (directory / f'{args.mode}-{args.shards}-{args.shard}.lock').open('a') as lock:
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('This exact replay selection is already running; inspect-routing-replays shows its process.')
    subprocess.run([sys.executable, str(ROOT / 'scripts/validate_piano_guitar_extensions.py'),
                    '--mode', args.mode, '--shards', str(args.shards), '--shard', str(args.shard)], check=True)
