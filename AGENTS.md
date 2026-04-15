# Repository Guidelines

## Project Structure & Module Organization
Core integration code lives in `custom_components/systemair/`. Platform entry points such as `climate.py`, `sensor.py`, `switch.py`, and `config_flow.py` expose Home Assistant entities and setup flows. Shared coordination and transport logic is in `coordinator.py`, `api.py`, `modbus.py`, and `homesolution.py`. The bundled client library is under `custom_components/systemair/systemair_api/`. Translations live in `custom_components/systemair/translations/`. Reference material and vendor assets are kept in `docs/`; local Home Assistant runtime data belongs in `config/` and should not be committed.

## Build, Test, and Development Commands
Run `scripts/setup` once to install Python dependencies and register pre-commit hooks. Use `scripts/develop` to start a local Home Assistant instance with `config/` as the config directory and `custom_components/` added to `PYTHONPATH`. Use `scripts/lint` before opening a PR; it runs `ruff format .` and `ruff check . --fix`. For manual checks, `pre-commit run --all-files` mirrors the local hook set. CI also runs Ruff, `hassfest`, and HACS validation on pushes and pull requests.

## Coding Style & Naming Conventions
Follow the repository Ruff config in `.ruff.toml`: Python target is 3.13, line length is 140, and formatting is enforced by Ruff. Use 4-space indentation, type hints where practical, and clear snake_case for modules, functions, and variables. Keep Home Assistant platform files named by platform (`binary_sensor.py`, `number.py`, `select.py`). Preserve existing JSON translation keys and manifest field naming.

## Testing Guidelines
There is no dedicated `tests/` suite yet. Treat linting and integration validation as mandatory quality gates: run `scripts/lint`, then verify the relevant workflow expectations by checking config flow, entity setup, and connection-specific behavior locally in Home Assistant. If you add tests later, place them in a top-level `tests/` directory and name files `test_*.py`.

## Commit & Pull Request Guidelines
Keep commit messages short, imperative, and prefixed when appropriate, for example `ci: fix ruff checkout for fork pull requests` or `style: make alarm options descriptions consistent`. PRs should target `main`, describe the user-visible change, note affected connection modes (Modbus TCP, RS485, Web API), and mention any config-flow or translation updates. Include screenshots only when UI text or Home Assistant flows change.
