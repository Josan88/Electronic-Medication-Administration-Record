# Agent Guidelines for eMAR

## Build & Test

- **Test All:** `python -m pytest` (Note: `pytest.ini` has headed/video opts)
- **Test Single:** `python -m pytest tests/test_validation.py` or `::TestClass::test_method`
- **Run App:** `python app.py` (http://localhost:5000)
- **Deps:** `pip install -r requirements.txt` (Ensure pytest/requests installed)

## Code Style & Architecture

- **Stack:** Flask (Python), Vanilla JS. **Pattern:** Routes → Validators → Services → Utils.
- **Style:** PEP 8 (Py), 2-space (JS). Docstrings required. **Imports:** Standard, 3rd-party, Local.
- **Logging/Errors:** Use `utils.logging_config.logger` & `utils.errors` (e.g. `ValidationError`).
- **Data:** Local JSON (Primary/Thread-safe) → ThingSpeak (Backup/Async).
- **Constraints:** **Strict 15s** ThingSpeak rate limit. Use `queue_service` & `thingspeak_bulk_service`.
- **Paths:** ALWAYS use **absolute paths** (resolve against root).

## Rules

- **Validation:** Validate in `validators/` before Services. Sanitize inputs.
- **Sync:** Dual-write to local DB and Queue. Do not block on external API.
- **Docs:** Update `swagger.yaml` on route changes.
