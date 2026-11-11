#!/bin/sh
set -eu

case_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project_dir=$(CDPATH= cd -- "$case_dir/../../.." && pwd)
exec python -B "$project_dir/scripts/run_seed_simulation.py" "$case_dir"
