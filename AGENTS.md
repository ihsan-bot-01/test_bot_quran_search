# Repository Guidelines

## Project Structure & Module Organization
- Keep runtime code in `src/` with clear subpackages: `src/bot/` for Telegram handlers, `src/services/` for search pipelines, and `src/utils/` for shared helpers.
- Place ingestion artifacts under `data/` (raw inputs in `data/raw/`, cleaned verse embeddings in `data/processed/`), and configuration defaults in `config/`.
- Automation scripts (index rebuilds, dataset sync) belong in `scripts/`; deployment manifests and Docker assets reside in `deploy/`.
- Tests mirror the package layout in `tests/`, using folder names that match the modules under test.

## Build, Test, and Development Commands
- `python -m venv .venv` then `.venv\Scripts\activate` to create and activate the local environment.
- `pip install -r requirements.txt` syncs dependencies; rerun after editing dependencies.
- `python -m src.bot.app` starts the development bot against the default configuration.
- `pytest -q` executes the full test suite; use `pytest tests/bot/test_handlers.py -k verse` to target a feature during triage.

## Coding Style & Naming Conventions
- Target Python 3.11, format with `black` (line length 100) and import-sort with `isort`; run `ruff check src tests` before committing.
- Use snake_case for modules/functions, PascalCase for classes, and UPPER_CASE for constants.
- Name Telegram command handlers as `<command>_handler` and vector search helpers as `<resource>_repository` for clarity.

## Testing Guidelines
- Write Pytest cases under `tests/` mirroring the package path (`tests/bot/test_app.py` for `src/bot/app.py`).
- Focus on deterministic fixtures for Quran text; store reusable samples in `tests/fixtures/`.
- Require coverage reports via `pytest --cov=src --cov-report=term-missing`; investigate any drop below 85%.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat: add verse chunking`, `fix: prevent empty queries`) to keep history searchable.
- Each PR must include a one-paragraph summary, linked issue or task ID, validation notes (`pytest`, manual bot run), and screenshots/GIFs when UI surfaces change.
- Request review only after lint and tests pass locally; keep PRs under ~400 lines of effective change.

## Security & Configuration Tips
- Store secrets in `.env.local` files ignored by git; reference them via `config/settings.py`.
- Rotate API keys monthly and document required environment variables in `config/README.md`.
