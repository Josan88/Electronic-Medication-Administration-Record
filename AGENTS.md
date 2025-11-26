# eMAR Agent Guidelines

## Build & Test

- **Run App:** `python app.py` (http://localhost:5000)
- **Test All:** `python -m pytest` (Defaults to headed w/ video; see `pytest.ini`)
- **Test Single:** `python -m pytest tests/test_validation.py` or `::TestClass::test_method`
- **Dependencies:** `pip install -r requirements.txt`

## Code Style & Architecture

- **Stack:** Flask (Python), Vanilla JS. **Pattern:** Routes → Validators → Services → Utils.
- **Style:** PEP 8 (Py), 2-space (JS). Docstrings on all public methods. **Imports:** Std → 3rd → Local.
- **Logging:** Use `utils.logging_config.logger` (NO `print`). Handle `utils.errors.ValidationError`.
- **Pathing:** ALWAYS use **absolute paths** (resolve against project root).

## Critical Rules (Hybrid Data)

- **Write Flow:** Routes → `validators` → `hybrid_service` (Dual-write: Local DB + Sync Queue).
- **ThingSpeak:** NEVER write directly from routes. STRICT 15s rate limit handled by `sync_service`.
- **Data:** Local JSON is primary/thread-safe. `process_thingspeak_sync` worker handles cloud sync.
- **Docs:** Update `swagger.yaml` for route changes. Sanitize inputs with `html.escape()`.
