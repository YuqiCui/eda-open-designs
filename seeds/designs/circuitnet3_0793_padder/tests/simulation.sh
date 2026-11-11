#!/bin/sh
set -eu

case_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project_dir=$case_dir
while [ ! -f "$project_dir/scripts/run_circuitnet3_testbench.py" ]; do
    if [ "$project_dir" = / ]; then
        echo "CircuitNet simulation runner was not found." >&2
        exit 1
    fi
    project_dir=$(dirname -- "$project_dir")
done
exec python3 -B "$project_dir/scripts/run_circuitnet3_testbench.py" "$case_dir" "$@"
