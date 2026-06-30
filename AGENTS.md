# Repository Guidelines

## Project Structure & Module Organization
Core integration code lives in `custom_components/systemair/`. Platform entry points such as `climate.py`, `sensor.py`, `switch.py`, and `config_flow.py` expose Home Assistant entities and setup flows. Shared coordination and transport logic is in `coordinator.py`, `api.py`, `modbus.py`, and `homesolution.py`. The bundled client library is under `custom_components/systemair/systemair_api/`. Translations live in `custom_components/systemair/translations/`. Reference material and vendor assets are kept in `docs/`; local Home Assistant runtime data belongs in `config/` and should not be committed.

## Build, Test, and Development Commands
Run `scripts/setup` on Linux/macOS or `.\scripts\setup.ps1` on Windows once to install Python dependencies and register pre-commit hooks. Use `scripts/develop` or `.\scripts\develop.ps1` to start a local Home Assistant instance with `config/` as the config directory and `custom_components/` added to `PYTHONPATH`. Use `scripts/lint` or `.\scripts\lint.ps1` before opening a PR; it runs `ruff format .` and `ruff check . --fix`. For manual checks, `pre-commit run --all-files` mirrors the local hook set. CI also runs Ruff, `hassfest`, and HACS validation on pushes and pull requests.

## Coding Style & Naming Conventions
Follow the repository Ruff config in `.ruff.toml`: Python target is 3.14, line length is 140, and formatting is enforced by Ruff. Use 4-space indentation, type hints where practical, and clear snake_case for modules, functions, and variables. Keep Home Assistant platform files named by platform (`binary_sensor.py`, `number.py`, `select.py`). Preserve existing JSON translation keys and manifest field naming.

## Testing Guidelines
Automated regression tests live in `tests/` and use the standard-library `unittest` runner. Run `python.exe -m unittest discover -s tests` plus `scripts/lint` or `.\scripts\lint.ps1` before submitting changes; use `pre-commit run --all-files` when you need to mirror the full local hook set. Keep new tests in `tests/`, name files `test_*.py`, and prefer focused coverage for manifest requirements, config-flow validation, entity state mapping, and API or Modbus error handling. For Home Assistant behavior changes, also manually verify the affected workflow in a local instance: config flow, entity setup, coordinator refreshes, and the relevant connection mode (Modbus TCP, RS485, or Web API).

## Commit & Pull Request Guidelines
Keep commit messages short, imperative, and prefixed when appropriate, for example `ci: fix ruff checkout for fork pull requests` or `style: make alarm options descriptions consistent`. PRs should target `main`, describe the user-visible change, note affected connection modes (Modbus TCP, RS485, Web API), and mention any config-flow or translation updates. Include screenshots only when UI text or Home Assistant flows change.
