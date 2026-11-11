"""Compile and run the original Verilog testbenches attached to a CircuitNet case."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def _stage_runtime(testbench: Path, sandbox: Path) -> Path:
    """Copy the original runtime assets and select the simulator's working directory."""
    resources = testbench.parent / "runtime"
    if not resources.is_dir():
        return sandbox
    manifest = json.loads((testbench.parent / "runtime.json").read_text(encoding="utf-8"))
    workdir = (sandbox / manifest["working_directory"]).resolve()
    if not workdir.is_relative_to(sandbox.resolve()):
        raise ValueError(f"Working directory escapes the simulation directory: {workdir}")
    shutil.copytree(resources, sandbox, dirs_exist_ok=True)
    workdir.mkdir(parents=True, exist_ok=True)
    return workdir


def _simulate(sources: list[Path], testbench: Path, timeout: int, top: str | None) -> bool:
    """Run one testbench in an isolated directory and report tool failures."""
    print(f"Running {testbench.name}", flush=True)
    with TemporaryDirectory(prefix="circuitnet3-simulation-") as temporary:
        sandbox = Path(temporary)
        executable = sandbox / "simulation.vvp"
        try:
            workdir = _stage_runtime(testbench, sandbox)
        except (OSError, ValueError, KeyError) as error:
            print(f"{testbench.name}: could not stage runtime files: {error}", file=sys.stderr)
            return False
        compile_command = [
            "iverilog", "-g2012", "-o", str(executable),
        ]
        for directory in dict.fromkeys(path.parent for path in [*sources, testbench]):
            compile_command.extend(["-I", str(directory)])
        if top:
            compile_command.extend(["-s", top])
        compile_command.extend(str(path) for path in [*sources, testbench])
        for phase, command in (
            ("compile", compile_command),
            ("simulate", ["vvp", "-N", str(executable)]),
        ):
            if phase == "simulate" and not executable.is_file():
                print(f"{testbench.name}: compile produced no simulation artifact", file=sys.stderr)
                return False
            try:
                subprocess.run(command, cwd=workdir, timeout=timeout, check=True)
            except subprocess.TimeoutExpired:
                print(f"{testbench.name}: {phase} timed out after {timeout}s", file=sys.stderr)
                return False
            except subprocess.CalledProcessError as error:
                print(f"{testbench.name}: {phase} exited with {error.returncode}", file=sys.stderr)
                return False
            except OSError as error:
                print(f"{testbench.name}: could not start {phase}: {error}", file=sys.stderr)
                return False
    return True


def _main() -> int:
    """Run all bundled testbenches or one explicitly selected testbench."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("testbench", nargs="?", help="Bundled filename, such as tb_01.v")
    parser.add_argument("--top", help="Explicit testbench top for a single selected file")
    parser.add_argument("--timeout", type=int, default=60, help="Seconds per phase (default: 60)")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.top and not args.testbench:
        parser.error("--top requires a testbench filename")
    for tool in ("iverilog", "vvp"):
        if shutil.which(tool) is None:
            parser.error(f"{tool} is required on PATH")

    case = args.case.resolve()
    seed_path = case / "seed.json"
    if seed_path.is_file():
        seed = json.loads(seed_path.read_text(encoding="utf-8"))
        sources = [case / name for name in seed["rtl"]["files"]]
    else:
        sources = [case / "rtl/design.v", *sorted((case / "rtl/dependencies").glob("*.v"))]
    sources.extend(sorted((case / "tests/verilog/dependencies").glob("*.v")))
    for source in sources:
        if not source.resolve().is_relative_to(case) or not source.is_file():
            parser.error(f"Invalid RTL source: {source}")
    tests = sorted((case / "tests/verilog").glob("tb_*.v"))
    if args.testbench:
        tests = [path for path in tests if path.name == args.testbench]
    if not tests:
        parser.error(f"No matching testbench in {case / 'tests/verilog'}")

    failures = 0
    for testbench in tests:
        if not _simulate(sources, testbench, args.timeout, args.top):
            failures += 1
    print(f"{case.name}: {len(tests) - failures}/{len(tests)} simulator runs exited cleanly")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(_main())
