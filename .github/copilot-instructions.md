## AI Coding Agent Instructions for eMAR

### Project Overview

This is a web-based Electronic Medication Administration Record (eMAR) system built with Flask, using ThingSpeak IoT as the cloud data store. The app manages patients, prescriptions, and medication tracking, with all data persisted in three separate ThingSpeak channels (no local DB).

### Architecture & Data Flow

- **Backend:** `app.py` (Flask app, REST API, background worker for prescription queue)
- **Frontend:** `static/js/main.js`, `templates/index.html` (single-page app, AJAX, dashboard switching)
- **Data Access Layer:** `services/thingspeak_service.py` (all ThingSpeak API logic, field mapping, and queries)
- **Config:** `config.py` (loads/validates env vars, channel config)
- **Utilities:** `utils/errors.py` (standardized error/response), `utils/logging_config.py` (structured logging)
- **No local DB:** All persistent data is on ThingSpeak; prescription queue is in-memory only (lost on restart).

#### Data Channels

- `patient_info`: Patient demographics (ID, name, location, etc.)
- `medicine_prescription`: Medication orders (queued, background write)
- `medicine_track`: Medication administration events

#### Data Flow

Client → Flask API → ThingSpeak REST API → Cloud Storage

- GET: Reads from ThingSpeak, maps fields to readable keys
- POST: Accepts JSON, maps to ThingSpeak fields
- Prescriptions: Queued, written by background thread (see `process_prescription_queue` in `app.py`)
- Patients/Tracking: Direct write, 15s enforced wait (rate limit)

### Developer Workflows

- **Run app:** `python app.py` (Flask dev server, port 5000)
- **Install deps:** `pip install -r requirements.txt`
- **Configure:** Copy `.env.example` to `.env` and fill in ThingSpeak keys
- **Test API:** `python test_api.py` (comprehensive, rate-limited)
- **Web UI:** http://localhost:5000 (SPA, 3 dashboards)
- **Logs:** Console by default; enable file logging in `utils/logging_config.py` if needed

### Key Conventions & Patterns

- **All ThingSpeak access** is via `services/thingspeak_service.py` (never call API directly in routes)
- **Error handling:** Use `utils/errors.py` for all API responses (see `error_response`, `success_response`)
- **Logging:** Use the `logger` from `utils/logging_config.py` (no print statements)
- **Environment:** All secrets/API keys in `.env` (never hardcode)
- **Rate limits:** 15s enforced per channel (see `config.py`)
- **Prescription queue:** In-memory only; lost on restart (see `app.py`)
- **Frontend:** Uses AJAX to call Flask API; updates UI dynamically (see `main.js`)
- **Field mapping:** All ThingSpeak fields mapped to readable keys in service layer

### Integration Points

- **ThingSpeak:** All persistent data (patients, prescriptions, tracking)
- **No local DB:** Do not add DB logic unless explicitly requested
- **API endpoints:** See `README.md` for full list; all are RESTful and return standardized JSON

### Project Structure Highlights

- `app.py`: Flask app, API routes, background worker
- `services/thingspeak_service.py`: All ThingSpeak logic
- `config.py`: Loads/validates env vars, channel config
- `utils/errors.py`: Error/response utilities
- `utils/logging_config.py`: Logging setup
- `static/js/main.js`: All frontend logic (AJAX, UI updates)
- `test_api.py`: Automated API test suite

### Patterns to Follow

- **Add new endpoints:** Use service layer for all ThingSpeak access; return responses via `utils/errors.py`
- **Add new config:** Extend `Config` class in `config.py`; update `.env.example`
- **Add new logging:** Use `logger` from `utils/logging_config.py`
- **Add new frontend features:** Use AJAX to call Flask API; update UI in `main.js`

### Known Limitations

- **Prescription queue is not persistent** (lost on restart)
- **ThingSpeak rate limits** (15s per channel)
- **No data pagination** (only last 100 records per channel)
- **No user authentication** (dev only)

### Examples

- **Add patient:** POST `/api/patients` with JSON body (see `README.md`)
- **Add prescription:** POST `/api/prescriptions` (queued, HTTP 202)
- **Record administration:** POST `/api/medication-tracking`
- **Test API:** `python test_api.py` (see output for pass/fail)

---

For more, see `README.md` and `IMPROVEMENTS.md` for architecture, conventions, and recent changes.
