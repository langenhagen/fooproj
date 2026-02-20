# fooproj

Third-person 3D Ursina driving sandbox in Python.

This project is nearly entirely vibe coded.

## Requirements

- `pyenv`
- `uv`

## Quick start

```bash
pyenv install -s 3.14.3
pyenv local 3.14.3
uv sync
uv run fooproj
```

## Controls

- Arrow keys: move (forward/back + strafe left/right)
- Page Up / Page Down: rotate car left/right
- Mouse move: orbit camera (captured cursor)
- Mouse wheel: zoom in/out (zoom-in is clamped, zoom-out unbounded)

## Full setup and checks

```bash
# install and activate the pinned Python version
pyenv install -s 3.14.3
pyenv local 3.14.3

# create/update virtual environment and dependencies
uv sync

# launch the Ursina sandbox
uv run fooproj

# run quality checks
uv run ruff check .
uv run ruff format .
uv run mypy fooproj
uv run pytest

# install git hooks
uv run pre-commit install

# run all hooks once manually
uv run pre-commit run --all-files

# optional: install and run extended lint stack
uv sync --group lint
uv run --group lint pylint fooproj tests
uv run --group lint vulture fooproj tests
```

## Project layout

- `fooproj/`: application package and CLI entrypoint
- `fooproj/game/`: runtime, input/camera controls, scene setup, lighting
- `tests/`: test suite
- `pyproject.toml`: project metadata and tool/lint configuration

## Notes

- Project defaults use reproducible `uv run ...` commands.
