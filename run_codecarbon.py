"""
run_codecarbon.py — wraps bad_code.py functions with CodeCarbon to measure
actual kWh and kg CO2eq during execution.

Results are saved to results/codecarbon_emissions.csv
"""

import os
import sys
import pandas as pd
import numpy as np
from codecarbon import EmissionsTracker

os.makedirs("results", exist_ok=True)

# --- import the functions we want to measure ---
sys.path.insert(0, ".")
from bad_code import (
    unnecessary_list_cast_tuple,
    loop_invariant_complex,
    try_except_in_loop,
    manual_list_append,
    deeply_nested_logic,
    high_complexity_function,
    pandas_iterrows_bad,
    sequential_pandas_ops,
)

# Build a small sample DataFrame for Pandas tests
df = pd.DataFrame({
    "value": np.random.rand(5000),
    "score": np.random.rand(5000),
    "label": ["cat"] * 2500 + ["dog"] * 2500,
})

TASKS = [
    ("unnecessary_list_cast_tuple",   lambda: [unnecessary_list_cast_tuple() for _ in range(50_000)]),
    ("loop_invariant_complex",        lambda: loop_invariant_complex()),
    ("try_except_in_loop",            lambda: try_except_in_loop([str(i) for i in range(10_000)])),
    ("manual_list_append",            lambda: manual_list_append()),
    ("deeply_nested_logic",           lambda: deeply_nested_logic(
        [{"value": i} for i in range(500)], threshold=100, mode="strict", flag=True, extra=None
    )),
    ("high_complexity_function_x1000",lambda: [high_complexity_function(i % 10 - 5, "a", True, False, True) for i in range(10_000)]),
    ("pandas_iterrows_bad",           lambda: pandas_iterrows_bad(df)),
    ("sequential_pandas_ops",         lambda: sequential_pandas_ops(df)),
]

print(f"\n{'Task':<40} {'kWh':>12} {'kg CO2eq':>12}")
print("-" * 66)

for name, fn in TASKS:
    tracker = EmissionsTracker(
        project_name=name,
        output_dir="results",
        output_file="codecarbon_emissions.csv",
        log_level="error",
        save_to_file=True,
    )
    tracker.start()
    fn()
    emissions = tracker.stop()
    energy_kwh = tracker._total_energy.kWh if hasattr(tracker, "_total_energy") else float("nan")
    print(f"{name:<40} {energy_kwh:>12.8f} {emissions:>12.8f}")

print("\nDone. Full log saved to results/codecarbon_emissions.csv")
