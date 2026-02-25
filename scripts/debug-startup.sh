#!/usr/bin/env bash
#
# Start the game and write unbuffered output to __debug/out.log.

set -euo pipefail

mkdir -p "__debug"
timeout 5s .venv/bin/python -u fooproj/cli.py 2>&1 | tee "__debug/out.log"
