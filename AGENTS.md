# Agent Guidelines for eMAR

## Build & Test
- **Run all tests:** `python -m pytest`
- **Run single test file:** `python -m pytest tests/test_validation.py`
- **Run single test case:** `python -m pytest tests/test_validation.py::TestClassName::test_method_name`
- **Install deps:** `pip install -r requirements.txt`
- **Start app:** `python app.py`

## Code Style & Conventions
- **Python:** PEP 8, 4 spaces indent, max 88 chars. Docstrings (triple quotes) required for all funcs/classes.
- **JavaScript:** 2 spaces indent, camelCase, consistent semicolons.
- **Imports:** Group standard, third-party, local.
- **Error Handling:** Use `utils.errors` (e.g., `error_response`, `ValidationError`). Catch specific exceptions.
- **Logging:** Use `utils.logging_config.logger` (debug, info, warning, error).
- **Architecture:** Routes -> Validators -> Services -> Utils. Keep business logic in Services.
- **Docs:** Update `swagger.yaml` for API changes.

## Specific Constraints
- **ThingSpeak:** Respect 15s rate limit per channel. Use Queue service for Prescriptions.
- **Paths:** Always use absolute paths in tool calls.
