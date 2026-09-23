#!/usr/bin/env bash
# Local v2 build. Install FFmpeg first; no Python packages or model API required.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -eq 0 ]; then
  echo 'Usage: ./run.sh RELEASE_FOLDER --out NEW_OUTPUT_FOLDER [--example]' >&2
  exit 2
fi
exec "${PYTHON:-python3}" "$ROOT/launch_factory.py" build "$@"
