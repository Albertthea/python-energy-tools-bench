"""
run_all.py — runs all static analysis tools against bad_code.py
and saves results to the results/ directory.

Usage:
    python run_all.py
    python run_all.py --tool ruff       # run only one tool
    python run_all.py --tool codecarbon # runtime measurement
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

os.makedirs("results", exist_ok=True)

TARGET = "bad_code.py"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")


def run(cmd: list[str], output_file: str, label: str):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  Output:  results/{output_file}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    path = f"results/{output_file}"
    with open(path, "w") as f:
        f.write(f"# {label}\n# Command: {' '.join(cmd)}\n# Run at: {TS}\n\n")
        f.write(output)
    print(output[:2000])  # print first 2000 chars to terminal
    if len(output) > 2000:
        print(f"  ... (truncated, see {path} for full output)")
    return result.returncode


TOOLS = {
    "ruff": lambda: run(
        ["ruff", "check", TARGET, "--select", "PERF,FURB", "--output-format", "text"],
        "ruff.txt", "Ruff — PERF + FURB rules"
    ),
    "pylint": lambda: run(
        ["pylint", TARGET, "--rcfile", "config/.pylintrc", "--disable=perflint"],
        "pylint.txt", "Pylint — base rules only (no perflint)"
    ),
    "perflint": lambda: run(
        ["pylint", TARGET, "--load-plugins", "perflint", "--rcfile", "config/.pylintrc"],
        "pylint_perflint.txt", "Pylint + perflint plugin — W84xx rules"
    ),
    "radon_cc": lambda: run(
        ["radon", "cc", TARGET, "-s", "-a", "--show-complexity"],
        "radon_cc.txt", "Radon — Cyclomatic Complexity (CC)"
    ),
    "radon_mi": lambda: run(
        ["radon", "mi", TARGET, "-s"],
        "radon_mi.txt", "Radon — Maintainability Index (MI)"
    ),
    "radon_hal": lambda: run(
        ["radon", "hal", TARGET],
        "radon_hal.txt", "Radon — Halstead Metrics (volume, difficulty, effort)"
    ),
    "xenon": lambda: run(
        ["xenon", TARGET, "--max-absolute", "B", "--max-modules", "A", "--max-average", "A"],
        "xenon.txt", "Xenon — CI complexity gate (expected: FAIL)"
    ),
    "codecarbon": lambda: run(
        [sys.executable, "run_codecarbon.py"],
        "codecarbon_log.txt", "CodeCarbon — runtime kWh + CO2eq measurement"
    ),
}


def main():
    parser = argparse.ArgumentParser(description="Run green code analysis tools against bad_code.py")
    parser.add_argument("--tool", choices=list(TOOLS.keys()) + ["all"], default="all",
                        help="Which tool to run (default: all)")
    args = parser.parse_args()

    tools_to_run = TOOLS if args.tool == "all" else {args.tool: TOOLS[args.tool]}

    print(f"\npython-energy-tools-bench — running {len(tools_to_run)} tool(s) against {TARGET}")
    print(f"Timestamp: {TS}\n")

    exit_codes = {}
    for name, fn in tools_to_run.items():
        code = fn()
        exit_codes[name] = code

    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for name, code in exit_codes.items():
        status = "PASS (no issues)" if code == 0 else f"ISSUES FOUND (exit {code})"
        print(f"  {name:<20} {status}")
    print(f"\nAll results saved to results/")


if __name__ == "__main__":
    main()
