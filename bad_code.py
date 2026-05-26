"""
bad_code.py — intentionally inefficient Python code for testing static analysis tools.

Covers:
  perflint / Ruff PERF:  W8401/PERF101, W8402/PERF102, W8403/PERF203 (loop-invariant),
                          W8404/PERF203 (try-except), W8405/PERF205, W8406, W8407/PERF301,
                          PERF401, PERF403
  Ruff FURB:             FURB118, FURB131, FURB136, FURB161
  Pylint:                C0200 (range/len), R1702 (nested blocks), W0612 (unused var),
                         R0913 (too many args), R0914 (too many locals)
  Radon:                 high cyclomatic complexity, low maintainability index
  EcoCode / GreenCodeAnalyzer: iterrows, chain indexing, sequential pandas ops

Examples adapted in part from: https://github.com/tonybaloney/perflint (MIT licence, Anthony Shaw)
"""

import os
import pandas as pd
import numpy as np
import operator


# =============================================================================
# W8401 / PERF101 — unnecessary list() cast around already-iterable type
# (from perflint README, MIT licence)
# =============================================================================

def unnecessary_list_cast_tuple():
    items = (1, 2, 3)
    for i in list(items):          # W8401 / PERF101
        print(i)


def unnecessary_list_cast_set():
    items = {1, 2, 3}
    for i in list(items):          # W8401 / PERF101
        print(i)


def unnecessary_list_cast_dict():
    d = {"a": 1, "b": 2}
    for k in list(d.keys()):       # W8401 / PERF101
        print(k)


# =============================================================================
# W8402 / PERF102 — incorrect dictionary iterator
# (from perflint README, MIT licence)
# =============================================================================

def incorrect_dict_iterator_values():
    fruit = {"a": "Apple", "b": "Banana"}
    for _, value in fruit.items():  # W8402 / PERF102 — discard key, use .values()
        print(value)


def incorrect_dict_iterator_keys():
    fruit = {"a": "Apple", "b": "Banana"}
    for key, _ in fruit.items():   # W8402 / PERF102 — discard value, use .keys()
        print(key)


# =============================================================================
# W8403 / PERF203 (loop-invariant-statement) — expression that never changes
# should be moved outside the loop
# (from perflint README, MIT licence)
# =============================================================================

def loop_invariant_basic():
    x = [1, 2, 3, 4]
    for i in range(10_000):
        print(len(x) * i)          # W8403 — len(x) is invariant, compute once


def loop_invariant_complex():
    x = [1, 2, 3, 4]
    i = 6
    for j in range(10_000):
        print(len(x) * i + j)      # W8403 — len(x) * i is invariant


def loop_invariant_os_path():
    files = ["a.txt", "b.txt", "c.txt"]
    for f in files:
        path = os.path.join("/data", f)   # W8405 / PERF205 — dotted import in loop
        print(path)


# =============================================================================
# W8404 / PERF203 — try/except inside a loop
# =============================================================================

def try_except_in_loop(items):
    results = []
    for item in items:
        try:                        # W8404 / PERF203 — exception handler overhead per iteration
            results.append(int(item))
        except ValueError:
            pass
    return results


def try_except_in_while_loop(data):
    i = 0
    while i < len(data):
        try:                        # W8404 / PERF203
            val = float(data[i])
            print(val)
        except TypeError:
            pass
        i += 1


# =============================================================================
# W8406 — bytes slicing in loop; use memoryview instead
# =============================================================================

def bytes_slicing_in_loop(data: bytes):
    chunk_size = 4
    results = []
    for i in range(0, len(data), chunk_size):
        results.append(data[i:i + chunk_size])  # W8406 — copies bytes each iteration
    return results


# =============================================================================
# W8407 / PERF301 — use tuple instead of list for non-mutated sequence
# =============================================================================

def use_list_as_immutable_sequence():
    COLORS = ["red", "green", "blue"]   # W8407 / PERF301 — never mutated, should be tuple
    for color in COLORS:
        print(color)


# =============================================================================
# PERF401 — manual list accumulation instead of list comprehension
# =============================================================================

def manual_list_append():
    numbers = range(1000)
    result = []
    for n in numbers:
        result.append(n * 2)        # PERF401 — use list comprehension
    return result


def manual_list_append_conditional():
    numbers = range(1000)
    evens = []
    for n in numbers:
        if n % 2 == 0:
            evens.append(n)         # PERF401 — use [n for n in numbers if n % 2 == 0]
    return evens


# =============================================================================
# PERF403 — manual dict building instead of dict comprehension
# =============================================================================

def manual_dict_build():
    keys = ["a", "b", "c"]
    result = {}
    for k in keys:
        result[k] = k.upper()       # PERF403 — use {k: k.upper() for k in keys}
    return result


# =============================================================================
# FURB118 — reimplemented operator (from Refurb)
# =============================================================================

add = lambda x, y: x + y           # FURB118 — use operator.add
mul = lambda x, y: x * y           # FURB118 — use operator.mul
get_first = lambda x: x[0]         # FURB118 — use operator.itemgetter(0)


# =============================================================================
# FURB131 — manual dict clearing loop instead of .clear()
# =============================================================================

def manual_dict_clear(d: dict):
    for key in list(d.keys()):      # FURB131 — use d.clear()
        del d[key]


# =============================================================================
# FURB136 — ternary min/max instead of built-in
# =============================================================================

def manual_max(x, y):
    return x if x > y else y        # FURB136 — use max(x, y)


def manual_min(x, y):
    return x if x < y else y        # FURB136 — use min(x, y)


# =============================================================================
# FURB161 — manual bit counting instead of bin().count()
# =============================================================================

def manual_bit_count(n: int) -> int:
    count = sum(1 for bit in bin(n)[2:] if bit == "1")  # FURB161 — use bin(n).count("1")
    return count


# =============================================================================
# C0200 (Pylint) — range(len()) instead of direct iteration
# =============================================================================

def range_len_antipattern(items):
    for i in range(len(items)):     # C0200 — use: for item in items
        print(items[i])


# =============================================================================
# R1702 (Pylint) — too many nested blocks; also raises Radon cyclomatic complexity
# =============================================================================

def deeply_nested_logic(data, threshold, mode, flag, extra):  # R0913 — too many args
    results = []
    errors = []
    skipped = []
    totals = []
    counts = []
    temps = []                      # R0914 — too many locals

    for item in data:
        if item is not None:
            if isinstance(item, dict):
                if "value" in item:
                    if item["value"] > threshold:
                        if mode == "strict":
                            if flag:
                                try:                # R1702 — 6+ nested blocks
                                    val = item["value"] * 2
                                    results.append(val)
                                    totals.append(val)
                                    counts.append(1)
                                    temps.append(val)
                                except Exception:
                                    errors.append(item)
                            else:
                                skipped.append(item)
                        elif mode == "loose":
                            results.append(item["value"])
                    else:
                        skipped.append(item)
                else:
                    errors.append(item)
            else:
                errors.append(item)
        else:
            skipped.append(item)

    return results, errors, skipped


# =============================================================================
# W0612 (Pylint) — unused loop variable
# =============================================================================

def unused_loop_variable():
    total = 0
    for unused in range(100):       # W0612 — variable never used
        total += 1
    return total


# =============================================================================
# EcoCode / GreenCodeAnalyzer — Pandas iterrows (sequential instead of vectorised)
# =============================================================================

def pandas_iterrows_bad(df: pd.DataFrame) -> list:
    """Iterates row-by-row — flagged by GreenCodeAnalyzer and EcoCode."""
    results = []
    for index, row in df.iterrows():   # energy smell — use vectorised ops
        results.append(row["value"] * 2)
    return results


def pandas_iterrows_with_condition(df: pd.DataFrame) -> list:
    results = []
    for _, row in df.iterrows():       # energy smell
        if row["score"] > 0.5:
            results.append(row["label"])
    return results


# =============================================================================
# EcoCode / GreenCodeAnalyzer — chain indexing
# =============================================================================

def chain_indexing_bad(df: pd.DataFrame):
    """Chain indexing — triggers SettingWithCopyWarning and is energy-inefficient."""
    for i in range(len(df)):
        df["col1"][i] = df["col2"][i] * 2   # chain indexing — use df.loc[i, "col1"]


# =============================================================================
# EcoCode — sequential Pandas ops instead of vectorised
# =============================================================================

def sequential_pandas_ops(df: pd.DataFrame) -> pd.Series:
    """Apply slow Python function row-by-row instead of using vectorised NumPy."""
    def slow_transform(x):
        return x ** 2 + x * 3 + 1

    return df["value"].apply(slow_transform)   # use: df["value"] ** 2 + df["value"] * 3 + 1


# =============================================================================
# Radon — high cyclomatic complexity function (CC > 10)
# =============================================================================

def high_complexity_function(x, mode, flag_a, flag_b, flag_c):
    """Cyclomatic complexity ~12. Radon will rank this E or F."""
    result = 0
    if x > 0:
        if mode == "a":
            result = x * 2
        elif mode == "b":
            result = x * 3
        elif mode == "c":
            if flag_a:
                result = x * 4
            else:
                result = x * 5
        else:
            result = x
    elif x < 0:
        if flag_b and flag_c:
            result = abs(x)
        elif flag_b:
            result = -x * 2
        elif flag_c:
            result = -x * 3
        else:
            result = 0
    else:
        if flag_a or flag_b:
            result = 1
        else:
            result = -1

    return result if result != 0 else None
