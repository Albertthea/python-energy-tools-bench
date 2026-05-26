# python-energy-tools-bench

A test repository for evaluating open-source Python static analysis tools focused on **energy efficiency, code performance, and emissions**.

The file `bad_code.py` is intentionally written with every anti-pattern covered by the tools below. Run the tools against it and compare results.

---

## Tools covered

| # | Tool | Type | Install |
|---|------|------|---------|
| 1 | Ruff (PERF + FURB) | Static | `pip install ruff` |
| 2 | Pylint | Static | `pip install pylint` |
| 3 | perflint | Static (Pylint plugin) | `pip install perflint` |
| 4 | Radon | Static (complexity) | `pip install radon` |
| 5 | Xenon | Static (CI gate) | `pip install xenon` |
| 6 | Wily | Static (trends) | `pip install wily` |
| 7 | CodeCarbon | Runtime | `pip install codecarbon` |

> EcoCode and GreenCodeAnalyzer require separate setup — see their sections below.

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_ORG/python-energy-tools-bench
cd python-energy-tools-bench
pip install -r requirements.txt

# 2. Run all tools at once
python run_all.py

# 3. Or run individually — see sections below
```

---

## Running each tool

### 1. Ruff — PERF + FURB rules
```bash
ruff check bad_code.py --select PERF,FURB
```
Config: `config/ruff.toml`

Expected flags: PERF101, PERF102, PERF203, PERF205, PERF401, PERF403, FURB118, FURB131, FURB136, FURB161

---

### 2. Pylint
```bash
pylint bad_code.py --rcfile config/.pylintrc
```
Expected flags: C0200, R1702, R0913, R0914, W0612

---

### 3. perflint (Pylint plugin)
```bash
pylint bad_code.py --load-plugins perflint --rcfile config/.pylintrc
```
Expected flags: W8401, W8402, W8403, W8404, W8405, W8406, W8407

---

### 4. Radon — cyclomatic complexity
```bash
# Cyclomatic complexity per function (rank A–F)
radon cc bad_code.py -s -a

# Maintainability index
radon mi bad_code.py -s

# Halstead metrics (volume, difficulty, effort — energy proxy)
radon hal bad_code.py
```
Watch for: `high_complexity_function` and `deeply_nested_logic` — both should rank D or worse.

---

### 5. Xenon — CI complexity gate
```bash
xenon bad_code.py --max-absolute B --max-modules A --max-average A
```
This will **exit non-zero** (fail) because `high_complexity_function` breaches the threshold. That's the point.

---

### 6. Wily — complexity trends over git history
```bash
# Build the index (needs at least 1 commit)
wily build bad_code.py

# Show metrics
wily report bad_code.py

# Graph a metric over time
wily graph bad_code.py maintainability_index
```
Note: Wily requires the file to be committed to git history. Run `git init && git add . && git commit -m "init"` first.

---

### 7. CodeCarbon — runtime emissions
```bash
python run_codecarbon.py
```
Wraps `bad_code.py` functions with the CodeCarbon tracker and logs kWh + kg CO₂eq to `results/codecarbon_emissions.csv`.

---

## EcoCode (SonarQube plugin)

Requires a running SonarQube instance. Quickest way via Docker:

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

Then install the [ecocode-python plugin](https://github.com/green-code-initiative/ecocode) and run:

```bash
sonar-scanner \
  -Dsonar.projectKey=python-energy-tools-bench \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN
```

---

## GreenCodeAnalyzer

Requires an Anthropic API key.

```bash
pip install green-code-analyzer
export ANTHROPIC_API_KEY=your_key_here
green-code-analyzer analyze bad_code.py
```

---

## Results

After running, results are saved to `results/`:

| File | Tool | Content |
|------|------|---------|
| `results/ruff.txt` | Ruff | Violation list |
| `results/pylint.txt` | Pylint | Full report |
| `results/pylint_perflint.txt` | perflint | W84xx violations |
| `results/radon_cc.txt` | Radon | CC ranks per function |
| `results/radon_mi.txt` | Radon | Maintainability index |
| `results/radon_hal.txt` | Radon | Halstead metrics |
| `results/xenon.txt` | Xenon | CI gate result |
| `results/codecarbon_emissions.csv` | CodeCarbon | kWh + CO₂eq |

---

## Anti-patterns covered in bad_code.py

| Pattern | Rule(s) | Tool(s) |
|---------|---------|---------|
| Unnecessary `list()` cast | W8401 / PERF101 | perflint, Ruff |
| Incorrect dict iterator | W8402 / PERF102 | perflint, Ruff |
| Loop-invariant statement | W8403 / PERF203 | perflint, Ruff |
| `try/except` in loop | W8404 / PERF203 | perflint, Ruff |
| Dotted import in loop | W8405 / PERF205 | perflint, Ruff |
| `bytes` slicing in loop | W8406 | perflint |
| List instead of tuple | W8407 / PERF301 | perflint, Ruff |
| Manual list accumulation | PERF401 | Ruff |
| Manual dict building | PERF403 | Ruff |
| Reimplemented operator | FURB118 | Ruff |
| Manual dict clear | FURB131 | Ruff |
| Ternary instead of min/max | FURB136 | Ruff |
| Manual bit counting | FURB161 | Ruff |
| `range(len())` | C0200 | Pylint |
| Too many nested blocks | R1702 | Pylint, Radon |
| Too many arguments | R0913 | Pylint |
| Too many locals | R0914 | Pylint |
| Unused loop variable | W0612 | Pylint |
| `iterrows` usage | — | GreenCodeAnalyzer, EcoCode |
| Chain indexing | — | GreenCodeAnalyzer |
| Sequential Pandas ops | — | EcoCode |
| High cyclomatic complexity | CC > 10 | Radon, Xenon, Wily |

---

## Licence

MIT. Examples in `bad_code.py` partially adapted from [tonybaloney/perflint](https://github.com/tonybaloney/perflint) (MIT, Anthony Shaw).
