# AGENTS.md

Practical guidance for humans and coding agents working in this repository.

## Intent

- Keep changes small, reviewable, and aligned with existing repo conventions.
- Prefer reliable, non-interactive commands and deterministic output.
- Assume files may change while you work; re-read before final writes and commits.

## Project Stack

- Language: Python.
- Runtime/version management: `pyenv`.
- Package/dependency/task workflow: `uv`.
- Test framework: `pytest`.
- Lint/format: `ruff`.
- Type checking: `mypy`.

## Repo Layout

- `fooproj/`: application package.
- `tests/`: unit and integration tests.
- `pyproject.toml`: project metadata and tool configuration.
- `.python-version`: pinned Python version for `pyenv`.

## Local Workflow

Prefer repo-local, reproducible commands:

- Sync dependencies: `uv sync`.
- Run app entrypoint: `uv run fooproj`.
- Run tests: `uv run pytest`.
- Run linter: `uv run ruff check .`.
- Format code: `uv run ruff format .`.
- Run type checks: `uv run mypy fooproj`.

Personal helper scripts (if available in `PATH`):

- `rf [path]`: quick Ruff formatter and autofix pass.
- `l3 [path]`: broad multi-tool lint pass (non-mutating).

When these scripts are available, use them as a fast taste-driven check layer,
but keep repo-level `uv run ...` commands as the baseline, reproducible checks.

Do not run full test suites automatically unless requested; use focused checks for touched files/areas first.

## User Shorthand Conventions

Interpret these tokens as explicit workflow commands:

- `prose`
  - Provide a clear prose walkthrough of the topic or changes.
  - Prioritize rationale, tradeoffs, and how pieces fit together.

- `eli5`
  - Provide an Explain Like I am 5 explanation of the current issue.
  - Keep it short, concrete, and technically correct.

- `sw`
  - Explicitly search the web before answering.
  - Use web results as supporting context in the response.

- `mc` or `commit`
  - Create a git commit.
  - Commit message must follow this structure:
    - First line: short summary (50 chars or less), imperative mood.
    - Second line: blank.
    - Optional body wrapped to about 72 chars with normal newlines (not with `\n`).
  - Do not use prefixes like `fix:`, `feat:`, `chore:`.
  - Include both the commit message and a prose walkthrough of what changed and why.

## Commit Workflow Expectations

When asked to commit:

1. Inspect `git status`, full diff, and recent commit style.
2. Stage only relevant files.
3. Run focused checks for touched areas.
4. Commit with a plain imperative summary line, no Conventional Commit prefix.
5. Report commit hash, message, and a short prose walkthrough.

Commit message DO:

- Start the summary in imperative mood (for example `Add`, `Fix`, `Change`).
- Keep the second line blank.
- Wrap body text to about 72 columns.
- Use simple line wraps in the body and keep one paragraph by default.
- Add extra blank lines only when you intentionally start a new paragraph.
Commit message DON'T:

- Do not use Conventional Commit prefixes.
- Do not end the summary line with a period.
- Do not include literal `\n` text in commit messages; use real newlines.

Never include secrets in commits (`.env*`, tokens, private keys, auth dumps).

## Git and Editing Safety

- Do not revert unrelated user changes.
- Do not use destructive git commands unless explicitly requested.
- Avoid interactive commands in automation.
- If a patch fails or context looks stale, re-read files before retrying.

## Output Character Policy

- Prefer plain ASCII in output and docs unless a file already requires Unicode.
- Avoid fancy punctuation and hidden/special spacing characters.
- Normalize pasted external text to plain characters before finalizing.
