"""Run the cocotb simulations registered in a Seed."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

from cocotb_tools.runner import get_runner

MIN_TIMEOUT_SEC = 1800
TIMESCALE_VALUE = re.compile(r"(?:1|10|100)(?:s|ms|us|ns|ps|fs)")


def _run_command(command: list[str], workdir: Path, timeout: float) -> int:
    """Run a test worker and terminate its simulator processes on interruption."""
    try:
        with subprocess.Popen(command, cwd=workdir, start_new_session=True) as process:
            try:
                return process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                print(f"Simulation timed out after {timeout}s", file=sys.stderr)
                return 124
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
    except OSError as error:
        print(f"Could not run simulation: {error}", file=sys.stderr)
        return 1


def _timescale(test: dict[str, object]) -> tuple[str, str] | None:
    """Read an optional Icarus time unit and precision from the test entry."""
    value = test.get("timescale")
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("timescale must contain a time unit and precision")
    unit, precision = value
    if not all(isinstance(item, str) and TIMESCALE_VALUE.fullmatch(item) for item in value):
        raise ValueError("Invalid timescale unit or precision")
    return unit, precision


def _run_test(case: Path, workdir: Path, index: int) -> int:
    """Build the selected test and check its xUnit results."""
    seed = json.loads((case / "seed.json").read_text())
    rtl = seed["rtl"]
    test = seed["verification"]["cocotb"][index]
    test_file = (case / test["file"]).resolve(strict=True)
    sys.path.insert(0, str(test_file.parent))

    for resource in (rtl.get("resources") or []) + (test.get("resources") or []):
        source = (case / resource).resolve(strict=True)
        target = workdir / source.relative_to(case)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    runner = get_runner("icarus")
    runner.build(
        sources=[case / name for name in rtl["files"]],
        includes=[case / name for name in rtl.get("include_dirs") or []],
        defines=rtl.get("defines") or {},
        parameters=rtl.get("parameters") or {},
        hdl_toplevel=rtl["top"],
        build_dir=workdir / "build",
        timescale=_timescale(test),
    )
    results = runner.test(
        hdl_toplevel=rtl["top"],
        test_module=test["module"],
        test_dir=workdir,
    )
    tests = ElementTree.parse(results).findall(".//testcase")
    passed = bool(tests) and all(
        test.find(tag) is None
        for test in tests
        for tag in ("failure", "error", "skipped")
    )
    return 0 if passed else 1


def main() -> int:
    """Run each registered test in an isolated temporary directory.

    Returns:
        Zero when every registered test executes and passes, otherwise nonzero.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--test-index", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    case = args.case.resolve()
    if args.test_index is not None:
        return _run_test(case, Path.cwd(), args.test_index)

    seed = json.loads((case / "seed.json").read_text())
    tests = (seed.get("verification") or {}).get("cocotb")
    if not tests:
        parser.error(f"No cocotb tests registered for {case.name}")

    failed = False
    script = Path(__file__).resolve()
    for index, test in enumerate(tests):
        if test["simulator"] != "icarus":
            parser.error(f"Unsupported simulator for {test['name']}")
        timeout = test.get("timeout_sec")
        if timeout is None:
            timeout = MIN_TIMEOUT_SEC
        if timeout < MIN_TIMEOUT_SEC:
            parser.error(f"Timeout for {test['name']} must be at least {MIN_TIMEOUT_SEC}s")

        print(f"Running {case.name}/{test['name']}", flush=True)
        with TemporaryDirectory(prefix="edaforge-simulation-") as temporary:
            workdir = Path(temporary)
            command = [
                sys.executable, "-B", str(script), str(case), "--test-index", str(index),
            ]
            returncode = _run_command(command, workdir, timeout)
            if returncode != 0:
                failed = True
                print(f"{case.name}/{test['name']}: exited with {returncode}", file=sys.stderr)

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
