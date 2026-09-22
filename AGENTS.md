# Optuna Agent Guidelines

## Setup

- **Install deps:** `uv sync` (editable install into `.venv`)
- **Test deps:** `uv sync --group test --extra optional`
- **Checking deps:** `uv sync --group checking`
- **Doc deps:** `uv sync --extra document`
- All commands run through `uv run` — do not assume `pytest`, `ruff`, or `mypy` are on PATH.

## Verify Changes

Run in this order:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
uv run pytest
```

Or use pre-commit (installed via `uv tool install pre-commit`):

```bash
pre-commit run --all-files
```

## Testing

- **All tests:** `uv run pytest`
- **Single file:** `uv run pytest tests/<file>`
- **Single test:** `uv run pytest tests/<file> -k <function_name>`
- **Skip slow tests:** `uv run pytest -m "not slow"`
- Tests mirror `optuna/` subpackages: `optuna/samplers/` → `tests/samplers_tests/`, etc.
- `optuna.testing.pytest_*` modules are rewritten by pytest for assert introspection (registered in `tests/conftest.py`).

## Code Style

- **Formatter/linter:** ruff (line-length 99, target py39)
- **Type checking:** mypy strict mode (disallow untyped calls/defs, no implicit optional, strict equality, etc.)
- **isort:** single-line imports, force-sort within sections, order-by-type off
- **Excluded from linting:** `tutorial/**`, `**/alembic/versions/*.py` (isort only)
- **Excluded from mypy:** `.venv`, `venv`, `build`, `docs`, `tutorial`, alembic dir, gRPC auto-generated code

## Architecture

- **Single Python package:** `optuna/` — no monorepo subpackages.
- **Top-level entrypoints:** `create_study`, `Study`, `Trial` (in `optuna/__init__.py`)
- **Lazy imports:** `artifacts`, `importance`, `visualization` are `_LazyImport` — not loaded until first use.
- **Subpackages:** `samplers/`, `pruners/`, `storages/`, `study/`, `trial/`, `integration/`, `testing/`, `_gp/`, `_hypervolume/`
- **Storage:** RDB storage uses Alembic migrations (`optuna/storages/_rdb/alembic/`). Do not edit migration files manually — use Alembic CLI.
- **gRPC storage:** auto-generated code at `optuna/storages/_grpc/auto_generated/` — excluded from lint/mypy.
- **CLI:** `optuna.cli:main` (entry point `optuna`).

## Documentation

- Built with Sphinx from `docs/source/`.
- Tutorials live in `tutorial/` as `.py` files, processed by Sphinx-Gallery into `.rst`/`.ipynb` in `docs/source/tutorial/`.
- **Build docs:** `uv sync --extra document && cd docs && uv run make html`
- Tutorial `.py` files are **executed** during doc build — keep runtime under 3 minutes (use `timeout=180`).
- Tutorials sorted by filename prefix: `10_key_features/` for core features, `20_recipes/` for advanced patterns. New recipes go in `20_recipes/` with consecutive numbering.

## Gotchas

- **Windows:** `tests/conftest.py` resets the logger root on Windows only — don't assume cross-platform behavior without checking.
- **PyTorch sources:** `torch`/`torchvision` resolve from `pytorch-cpu` index (see `pyproject.toml` `tool.uv.sources`). Do not add PyPI as a fallback.
- **torchvision stray wheel:** `torchvision!=0.27.1+df56172` constraint is pinned to avoid a misplaced ARM64 wheel.
- **Version:** read from `optuna/version.py` (setuptools `attr` directive). Currently `5.1.0.dev`.
- **PRs from LLMs:** the project explicitly rejects PRs that appear primarily LLM-generated without contributor understanding/validation.

## External Resources

- Full contribution guidelines: `CONTRIBUTING.md`
- Coding style, deprecation, and test policies: [Optuna Wiki](https://github.com/optuna/optuna/wiki)
- OpenCode config: `opencode.json` (model: `aristote/qwen-3.6-35b-instruct`, context 262k)
