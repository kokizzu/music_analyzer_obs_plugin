#!/usr/bin/env bash
set -euo pipefail

git diff --check
git diff -- src/analyzer.cpp
git status --short
