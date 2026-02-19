# pyhosts — Project Rules

## Quick Reference: gh Workflow Commands

```bash
# List all workflows and their status
gh workflow list

# View recent runs across all workflows
gh run list --limit 10

# Trigger the build workflow manually
gh workflow run build.yml

# Watch a running workflow in real-time
gh run watch

# View the latest build run
gh run list --workflow=build.yml --limit 1

# View details + logs of a specific run
gh run view <run-id>
gh run view <run-id> --log

# View failed steps only
gh run view <run-id> --log-failed

# Re-run failed jobs
gh run rerun <run-id> --failed

# Download artifacts from a run
gh run download <run-id>

# Check workflow status before merging
gh pr checks <pr-number>
```

## Quick Reference: gh PR & Release Commands

```bash
# Create a PR from current branch
gh pr create --title "Title" --body "Description"

# List open PRs
gh pr list

# View PR details, diff, checks
gh pr view <number>
gh pr diff <number>
gh pr checks <number>

# Merge a PR (squash preferred for clean history)
gh pr merge <number> --squash

# Create a release (triggers PyPI publish workflow)
gh release create v1.x.x --generate-notes

# List releases
gh release list
```

## Project Overview

**pyhosts** is a Python library for managing system hosts files (`/etc/hosts`, etc.) in a Pythonic way. It is published on PyPI as `pyhosts`.

- **Repository**: https://github.com/igormilovanovic/pyhosts
- **PyPI**: https://pypi.org/project/pyhosts/
- **License**: MIT
- **Minimum Python**: 3.10

## Architecture

```
pyhosts/
├── __init__.py              # Public API exports, version
├── hosts.py                 # Hosts collection (MutableSequence)
├── models.py                # Host frozen dataclass
├── parser.py                # File I/O, atomic writes
├── platform_resolver.py     # OS-specific hosts file paths
└── py.typed                 # PEP 561 marker

test/
├── test_base.py             # Core functionality tests
└── test_new_features.py     # Modern API tests
```

## Build & Test

```bash
# Install dev dependencies
pip install -r test-requirements.txt
pip install -e .

# Run tests
pytest test/ -v

# Run tests with coverage
pytest test/ -v --cov=pyhosts --cov-report=term

# Lint
pycodestyle pyhosts/ --max-line-length=120

# Type check
mypy pyhosts/
```

## CI/CD Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Build and Test | `build.yml` | push/PR to master | Test matrix: Python 3.10–3.12 × Ubuntu/macOS/Windows |
| CodeQL | `codeql.yml` | push/PR + weekly | Security scanning |
| Upload Python Package | `python-publish.yml` | release published | Build & publish to PyPI |

## Python Package Rules

### Code Style
- **PEP 8** with max line length 100 (ruff) / 120 (pycodestyle)
- **Type hints required** on all public function signatures
- Use Python 3.10+ features: `X | Y` union syntax, `match` statements, `dataclasses`
- **Ruff** for linting: E, W, F, I (isort), B (bugbear), C4 (comprehensions), UP (pyupgrade)
- **mypy** strict mode enabled — no untyped defs, no incomplete defs

### Dependencies
- **Zero external runtime dependencies** — stdlib only (`ipaddress`, `dataclasses`, `pathlib`, etc.)
- Dev dependencies in `test-requirements.txt`
- Keep it lightweight — resist adding dependencies unless absolutely necessary

### Testing
- **pytest** with `--strict-markers` and `-v`
- Tests in `test/` directory, files named `test_*.py`
- All new features require tests
- Use `tempfile` for file I/O tests — never modify system hosts file
- CI runs on 3 OSes × 3 Python versions = 9 matrix combinations

### Versioning & Releases
- Semantic versioning: MAJOR.MINOR.PATCH
- Version declared in `pyhosts/__init__.py` (`__version__`)
- Release via `gh release create vX.Y.Z --generate-notes`
- PyPI publish is automated on release via trusted publishing

### Package Structure
- All config in `pyproject.toml` — no `setup.py`, no `setup.cfg`
- `py.typed` marker present for PEP 561 compliance
- Classifiers kept current with supported Python versions
- `[project.urls]` includes Homepage, Repository, Issues

### Commit & PR Conventions
- Keep commits focused — one logical change per commit
- PR titles should be descriptive and concise
- All CI checks must pass before merging
- Squash merge preferred for clean history

### Security
- Never commit secrets or credentials
- Hosts file operations require elevated permissions — document clearly
- Atomic writes prevent file corruption
- Validate all user-provided IP addresses and hostnames
- CodeQL runs weekly for security analysis

### Documentation
- README.md is the primary documentation — keep it excellent
- Docstrings on all public classes and methods
- Inline comments only where logic is non-obvious
- Update README when adding/changing public API
