#!/usr/bin/env python3
"""List active routing replays without changing or restarting processes."""
import subprocess

result = subprocess.run(['ps', '-eo', 'pid,ppid,etime,args'], text=True, capture_output=True, check=True)
for line in result.stdout.splitlines():
    if any(name in line for name in ('validate_piano_guitar_extensions.py', '5423eaeda3f96b38/pair', 'evaluate_low_keyboard_coherence.py', 'validate_low_keyboard_controls.py')):
        print(line)
