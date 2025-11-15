## AI Coding Agent Instructions for eMAR

### Project Overview

This is a web-based Electronic Medication Administration Record (eMAR) system built with Flask, using ThingSpeak IoT as the cloud data store. The app manages patients, prescriptions, and medication tracking, with all data persisted in three separate ThingSpeak channels (no local DB).

### Documentation Resources

- **[Architecture Guide](../docs/ARCHITECTURE.md)**: Complete system architecture, component diagrams, data flow visualizations
- **[Deployment Guide](../docs/DEPLOYMENT.md)**: Development and production deployment instructions
- **[Contributing Guide](../CONTRIBUTING.md)**: Code standards, testing guidelines, PR process
- **[API Documentation](http://localhost:5000/api/docs)**: Interactive Swagger UI (when app is running)
- **[OpenAPI Spec](../swagger.yaml)**: Complete API specification in OpenAPI 3.0 format

### Architecture & Data Flow

- **Backend:** `app.py` (Flask app, REST API, background worker for prescription queue, Swagger UI)
- **Frontend:** `static/js/main.js`, `templates/index.html` (single-page app, AJAX, dashboard switching)
- **Data Access Layer:** `services/thingspeak_service.py` (all ThingSpeak API logic, field mapping, and queries)
- **Queue Management:** `services/queue_service.py` (persistent queue with retry logic and monitoring)
- **Config:** `config.py` (loads/validates env vars, channel config)
- **Utilities:** `utils/errors.py` (standardized error/response), `utils/logging_config.py` (structured logging)
- **Validators:** `validators/` (input validation and sanitization for patients, prescriptions, tracking)
- **Routes:** `routes/` (Flask blueprints organized by domain)
- **No local DB:** All persistent data is on ThingSpeak; prescription queue persists to `/tmp/prescription_queue.json`

#### Data Channels

- `patient_info`: Patient demographics (ID, name, location, etc.)
- `medicine_prescription`: Medication orders (queued, background write)
- `medicine_track`: Medication administration events

#### Data Flow

Client → Flask API → Validators → Services → ThingSpeak REST API → Cloud Storage

- GET: Reads from ThingSpeak, maps fields to readable keys
- POST: Accepts JSON, validates, maps to ThingSpeak fields
- Prescriptions: Queued, written by background thread (see `process_prescription_queue` in `app.py`)
- Patients/Tracking: Direct write, 15s enforced wait (rate limit)

### Developer Workflows

- **Run app:** `python app.py` (Flask dev server, port 5000)
- **Install deps:** `pip install -r requirements.txt`
- **Configure:** Copy `.env.example` to `.env` and fill in ThingSpeak keys
- **Test API:** Use Swagger UI at http://localhost:5000/api/docs or run test files
- **Web UI:** http://localhost:5000 (SPA, 3 dashboards)
- **View API docs:** http://localhost:5000/api/docs (interactive Swagger UI)
- **Logs:** Console by default; enable file logging in `utils/logging_config.py` if needed

### Key Conventions & Patterns

- **All ThingSpeak access** is via `services/thingspeak_service.py` (never call API directly in routes)
- **Error handling:** Use `utils/errors.py` for all API responses (see `error_response`, `success_response`)
- **Logging:** Use the `logger` from `utils/logging_config.py` (no print statements)
- **Environment:** All secrets/API keys in `.env` (never hardcode)
- **Rate limits:** 15s enforced per channel (see `config.py`)
- **Prescription queue:** Persists to disk at `/tmp/prescription_queue.json`; survives restarts
- **Frontend:** Uses AJAX to call Flask API; updates UI dynamically (see `main.js`)
- **Field mapping:** All ThingSpeak fields mapped to readable keys in service layer
- **Input validation:** All user input validated and sanitized via validators before processing
- **API Documentation:** All endpoints documented in `swagger.yaml` with request/response examples

### Integration Points

- **ThingSpeak:** All persistent data (patients, prescriptions, tracking)
- **No local DB:** Do not add DB logic unless explicitly requested
- **API endpoints:** See `swagger.yaml` or Swagger UI for complete list; all are RESTful and return standardized JSON
- **Swagger UI:** Interactive API documentation at `/api/docs`

### Project Structure Highlights

- `app.py`: Flask app, Swagger UI setup, background worker
- `swagger.yaml`: OpenAPI 3.0 specification for all API endpoints
- `routes/`: Flask blueprints (patients, prescriptions, tracking, queue)
- `services/thingspeak_service.py`: All ThingSpeak logic
- `services/queue_service.py`: Persistent queue with retry and monitoring
- `validators/`: Input validation for all data types
- `config.py`: Loads/validates env vars, channel config
- `utils/errors.py`: Error/response utilities
- `utils/logging_config.py`: Logging setup
- `static/js/main.js`: All frontend logic (AJAX, UI updates)
- `docs/`: Architecture and deployment documentation

### Patterns to Follow

- **Add new endpoints:** Use service layer for all ThingSpeak access; return responses via `utils/errors.py`; document in `swagger.yaml`
- **Add new config:** Extend `Config` class in `config.py`; update `.env.example`
- **Add new logging:** Use `logger` from `utils/logging_config.py`
- **Add new frontend features:** Use AJAX to call Flask API; update UI in `main.js`
- **Update API:** Update `swagger.yaml` with new endpoints, parameters, or responses
- **Add validation:** Create validator in `validators/` and integrate in route handlers

### Known Limitations

- **Prescription queue storage:** Queue stored in `/tmp/prescription_queue.json` - may be cleared by system on some platforms
- **ThingSpeak rate limits** (15s per channel)
- **No data pagination** (only last 100 records per channel)
- **No user authentication** (dev only)

### Examples

- **Add patient:** POST `/api/patients` with JSON body (see `swagger.yaml` or Swagger UI)
- **Add prescription:** POST `/api/prescriptions` (queued, HTTP 202)
- **Record administration:** POST `/api/medication-tracking`
- **View API docs:** Browse http://localhost:5000/api/docs
- **Test endpoints:** Use "Try it out" feature in Swagger UI

---

For more, see:
- **Architecture & Design:** `docs/ARCHITECTURE.md`
- **Deployment:** `docs/DEPLOYMENT.md`
- **Contributing:** `CONTRIBUTING.md`
- **Recent Changes:** `IMPROVEMENTS.md`
- **API Reference:** `swagger.yaml` or http://localhost:5000/api/docs
