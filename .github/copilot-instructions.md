# GitHub Copilot Instructions for eMAR

## Project Overview

Electronic Medication Administration Record (eMAR) is a Flask-based web application with a **hybrid data architecture**. It uses a local JSON database for real-time performance and ThingSpeak IoT platform for cloud backup and synchronization.

## Architecture & Data Flow

**Pattern:** Routes → Validators → Services → Utils

### Critical Data Flow (Read This First!)

1. **All writes go through `hybrid_service.py`:**

   - **Immediate:** Write to `local_db_service.py` (JSON files, thread-safe)
   - **Queued:** Add to `sync_queue` for ThingSpeak sync via `thingspeak_bulk_service.py`
   - **Never write directly to ThingSpeak** from routes (bypasses rate limit protection)

2. **Two background workers in `app.py`:**

   - `process_prescription_queue()`: Processes prescription queue every 1s
   - `process_thingspeak_sync()`: Syncs local DB to ThingSpeak every 5 min (respects 15s rate limit per channel)

3. **Field mappings are critical:**
   - ThingSpeak uses `field1`, `field2`, etc.
   - Local DB uses human-readable names (`patient_id`, `name`, etc.)
   - Mappings defined in `local_db_service.py` and `config.py` **must match exactly**

### Entry Points

- `app.py`: Flask initialization, blueprint registration, starts 2 background workers
- `routes/__init__.py`: Calls `register_blueprints()` to mount all route blueprints
- `config.py`: Loads `.env` file, validates required environment variables

## Development Workflow

```bash
# Start server (http://localhost:5000)
python app.py

# Run all tests (from repo root, includes Playwright e2e with video)
python -m pytest

# Run specific test file
python -m pytest tests/test_validation.py

# Run single test
python -m pytest tests/test_validation.py::TestPatientValidation::test_valid_patient_id

# Install dependencies
pip install -r requirements.txt
```

**Test Configuration:** `pytest.ini` enables `--video on --headed` by default for Playwright tests. Videos saved to `test-results/videos/`.

**API Documentation:** View Swagger UI at `/api/docs` after starting server. Update `swagger.yaml` when modifying routes.

## Coding Conventions

### Python Style

- **PEP 8** with docstrings for all public functions/classes
- **Import order:** Standard library → 3rd party → Local modules
- **Logging:** Use `utils.logging_config.logger` (never `print`)
  ```python
  from utils.logging_config import logger
  logger.info("Operation completed")
  logger.error("Failed to process", exc_info=True)
  ```

### Error Handling Pattern

```python
from utils.errors import ValidationError, NotFoundError, error_response, success_response

# In routes:
try:
    validated_data = validate_patient_data(data)
    result = hybrid_service.write_to_channel("patient_info", validated_data)
    return success_response(data={"entry_id": result}, message="Patient added")
except ValidationError as e:
    return error_response(str(e), 400)
except HybridDataServiceError as e:
    return error_response(str(e), 500)
```

### Validation Pattern

**Always validate before passing to services:**

```python
from validators import validate_patient_data, validate_prescription_data

# In route handlers:
data = request.json
validated_data = validate_patient_data(data)  # Raises ValidationError
# Now safe to pass to service layer
```

Validators **sanitize inputs** using `html.escape()` to prevent XSS. See `validators/patient_validator.py` for examples.

## Critical Constraints

### ThingSpeak Rate Limits

- **15 seconds** between writes to the same channel (enforced by ThingSpeak)
- Background worker tracks `last_write_times` per channel
- Use `sync_queue.add_sync()` to queue writes (never bypass)
- Bulk writes via `thingspeak_bulk_service.py` preferred for efficiency

### Thread Safety

- `LocalDatabase` uses `threading.Lock()` for all read/write operations
- `PersistentQueue` and `SyncQueue` also use locks
- **Never** modify JSON files directly, always use service methods

### Path Handling

```python
# Config defines base paths
LOCAL_DB_PATH = os.environ.get("LOCAL_DB_PATH", "/tmp/emar_local_db")

# In services, use config-defined paths:
from config import config
self.base_path = config.LOCAL_DB_PATH
channel_file = os.path.join(self.base_path, 'patient_info.json')
```

**Always use `os.path.join()` for cross-platform compatibility.**

## Key Files & Their Roles

- **`app.py`**: Flask app, background workers, blueprint registration
- **`config.py`**: Environment variables, ThingSpeak channel config, field mappings
- **`services/hybrid_service.py`**: Main entry point for all data operations
- **`services/local_db_service.py`**: Thread-safe JSON database (primary storage)
- **`services/thingspeak_bulk_service.py`**: Bulk write API for ThingSpeak sync
- **`services/sync_service.py`**: Sync queue with retry logic and exponential backoff
- **`services/queue_service.py`**: Prescription queue with persistence
- **`routes/__init__.py`**: Blueprint registration (`patients.py`, `prescriptions.py`, `tracking.py`, `queue.py`)
- **`validators/`**: Input validation and sanitization (XSS prevention)
- **`utils/errors.py`**: Custom exceptions and standardized response helpers
- **`tests/conftest.py`**: Pytest fixtures (Flask server, Playwright setup, video recording)

## Common Patterns

### Adding a New Route

1. Create route in appropriate blueprint (e.g., `routes/patients.py`)
2. Validate input using `validators/`
3. Call `hybrid_service` methods (never call `local_db` or `thingspeak_service` directly)
4. Return standardized responses
5. Update `swagger.yaml`

### Adding a New Field

1. Update ThingSpeak channel field mappings in `config.py`
2. Update local DB field mappings in `local_db_service.py`
3. Update validator in `validators/`
4. Update `swagger.yaml`

### Debugging Sync Issues

- Check `app.py` background worker logs
- Inspect `sync_queue` status via `/api/sync/status` endpoint
- Verify field mappings match between local DB and ThingSpeak
- Check ThingSpeak rate limit compliance (15s interval per channel)
