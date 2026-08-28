#!/usr/bin/env python3
"""Report active GuitarSet fixture or analyzer processes."""

import subprocess


result = subprocess.run(["ps", "-eo", "pid=,etime=,args="], check=False, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in result.stdout.splitlines():
    if "guitarset" in line.lower() or "audio_mono-mic" in line.lower():
        print(line)
raise SystemExit(result.returncode)
