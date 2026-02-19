# fooproj

Minimal Python project boilerplate using `pyenv` + `uv`.

## Requirements

- `pyenv`
- `uv`

## Quick start

```bash
# install and activate the pinned Python version
pyenv install -s 3.13.3
pyenv local 3.13.3

# create/update virtual environment and dependencies
uv sync

# run the app
uv run fooproj

# run quality checks
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest

# install git hooks
uv run pre-commit install

# run all hooks once manually
uv run pre-commit run --all-files

# optional: install and run extended lint stack
uv sync --group lint-extra
l3 src tests

# optional: quick autofix pass
rf src tests
```

## Project layout

- `src/fooproj/`: application package
- `tests/`: test suite
- `pyproject.toml`: project metadata and tool config

## Notes

- `l3` and `rf` are personal helper scripts expected from your `PATH`.
- Project defaults still use reproducible `uv run ...` commands.
