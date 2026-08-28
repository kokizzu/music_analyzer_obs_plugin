#!/bin/sh
# Locate the existing labelled-guitar corpus manifest readers and generators.
set -eu

sed -n '1,180p' scripts/download_agpt_guitar_samples.sh
