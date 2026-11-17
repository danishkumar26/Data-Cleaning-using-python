# Data-Cleaning-using-python

**A lightweight, config-driven data-cleaning library and CLI** for Python.

Turn messy CSV/JSON datasets into clean, analysis-ready tables with a declarative YAML rules file — deterministic, tested, and dependency-light. Built as a portfolio project demonstrating real software engineering: modular design, automated testing, CI/CD, and containerized delivery.

## Problem

Real-world data is dirty: duplicate rows, missing values, inconsistent date formats, mixed types, and malformed strings. Existing options force a choice between heavy enterprise data-quality platforms (cleanlab, Great Expectations, Soda Core) and throwaway student Jupyter notebooks with no packaging, tests, or CI. There's no lightweight, open-source middle ground that lets an analyst define cleaning rules once, run them reproducibly from the CLI, and get a before/after quality report — without notebook glue code.

## Features

| Category | Capability |
|----------|------------|
| **Deduplication** | Remove exact and near-duplicate rows, with configurable key columns |
| **Missing values** | Drop rows/columns or impute (mean, median, mode, constant) per column |
| **Date normalization** | Parse mixed date formats (DD-MM-YYYY, YYYY-MM-DD, MM/DD/YYYY) into ISO 8601 |
| **Type casting** | Coerce columns to int, float, string, bool, or datetime with error handling |
| **Column ops** | Rename, drop, reorder, and whitelist columns |
| **Config-driven** | Declare the entire cleaning pipeline in a single YAML rules file |
| **Quality report** | Before/after stats: row counts, null counts, duplicates removed, type changes |
| **CLI-first** | `dataclean clean data.csv --rules rules.yaml --out clean.csv --report report.md` |
| **Packaged** | pip-installable, Docker image, GitHub Actions CI |

## Quick Start

```bash
# Install
pip install dataclean

# Create a rules file (see config.yaml.example / cleaning-rules.yaml.example)
cat > cleaning-rules.yaml <<'EOF'
drop_duplicates: true
missing_values:
  age: strategy=mean
  date_of_birth: strategy=drop
date_columns:
  date_of_birth:
    input_formats: ["%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]
    output_format: "%Y-%m-%d"
type_cast:
  age: int
  salary: float
columns:
  keep: [name, age, date_of_birth, email]
  rename:
    date_of_birth: dob
EOF

# Run
dataclean clean employee_data.txt --rules cleaning-rules.yaml --out cleaned.csv --report report.md
```

## Installation

```bash
# From PyPI
pip install dataclean

# From source
git clone https://github.com/danishkumar26/Data-Cleaning-using-python.git
cd Data-Cleaning-using-python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Clean with a rules file
dataclean clean input.csv --rules rules.yaml --out output.csv

# JSON input/output
dataclean clean input.json --format json --out output.json

# Dry run: see what would change without writing
dataclean clean input.csv --rules rules.yaml --dry-run

# Report formats: markdown (default), json
dataclean clean input.csv --rules rules.yaml --report json --out report.json
```

See `cleaning-rules.yaml.example` for the full rules reference.

## Project Structure

```
Data-Cleaning-using-python/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .env.example
├── cleaning-rules.yaml.example
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── src/dataclean/
│   ├── __init__.py
│   ├── cli.py           # Typer CLI: clean, version, config
│   ├── config.py        # Settings (yaml + env overrides)
│   ├── rules.py         # Cleaning rules schema & validation
│   ├── cleaners/        # Individual cleaning transforms
│   │   ├── __init__.py
│   │   ├── base.py      # BaseCleaner + CleanResult
│   │   ├── dedupe.py
│   │   ├── missing.py
│   │   ├── dates.py
│   │   ├── types.py
│   │   └── columns.py
│   ├── pipeline.py      # Orchestrates cleaners in order
│   ├── report.py        # Before/after quality report (Markdown/JSON)
│   └── io.py            # CSV/JSON readers & writers
├── tests/
│   ├── test_cleaners.py
│   ├── test_pipeline.py
│   ├── test_report.py
│   └── test_cli.py
└── samples/
    ├── employee_data.txt      # raw dirty sample
    ├── expected_clean.csv     # expected output
    └── rules.yaml             # sample rules
```

## Cleaning Rules Reference

```yaml
# cleaning-rules.yaml
drop_duplicates: true
subset: null                      # columns to consider for duplicates (null = all)

missing_values:
  age: "strategy=mean"           # drop | mean | median | mode | constant=<value>
  email: "strategy=drop"         # drop rows where this column is null

date_columns:
  date_of_birth:
    input_formats: ["%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]
    output_format: "%Y-%m-%d"

type_cast:
  age: int
  salary: float
  is_active: bool

columns:
  keep: null                      # null = keep all
  drop: []
  rename:
    date_of_birth: dob
```

## Testing

```bash
pytest
```

CI runs `pytest` + `ruff` + `mypy` on every push via GitHub Actions.

## Roadmap

- [x] v0.1.0 — CLI scaffold: CSV/JSON I/O, dedupe, missing values, date normalization, type casting, Markdown/JSON reports
- [ ] v0.2.0 — Column rename/drop/reorder, constant imputation, outlier flagging
- [ ] v0.3.0 — Pandas-backed engine option for large files
- [ ] v0.4.0 — Interactive rules wizard (`dataclean init`)
- [ ] v1.0.0 — Stable release, semantic versioning, Docker image on GHCR

## License

MIT License. See [LICENSE](LICENSE).

## Author

Built by [danishkumar26](https://github.com/danishkumar26) — Cybersecurity | AI Engineering | Intelligent Automation | Backend Systems.

---

*Intended for legitimate data preprocessing on datasets you own or have permission to process. Never use to manipulate, falsify, or obscure data in ways that misrepresent reality or violate data-integrity policies.*