# GitHub Copilot Instructions for eMAR

## Project Overview

Electronic Medication Administration Record (eMAR) is a Flask-based web application with a hybrid data architecture. It uses a local JSON database for real-time performance and ThingSpeak IoT platform for cloud backup and synchronization.

## Architecture & Data Flow

- **Pattern:** Routes -> Validators -> Services -> Utils
- **Entry Point:** `app.py` initializes Flask, registers blueprints, and starts background services.
- **Data Strategy:**
  - **Primary:** `services/local_db_service.py` (JSON files) for immediate read/write.
  - **Backup:** `services/thingspeak_service.py` & `services/thingspeak_bulk_service.py` for cloud sync.
  - **Coordination:** `services/hybrid_service.py` manages the dual-write strategy (write to local, queue for cloud).
- **Queue System:** `services/queue_service.py` handles asynchronous ThingSpeak updates to respect rate limits.

## Development Workflow

- **Start Server:** `python app.py` (Runs on http://localhost:5000)
- **Run Tests:** `python -m pytest` (Run from root)
  - Single file: `python -m pytest tests/test_validation.py`
- **Dependencies:** `pip install -r requirements.txt`
- **API Docs:** Update `swagger.yaml` when modifying routes. View at `/api/docs`.

## Coding Conventions

- **Python:**
  - Follow PEP 8.
  - Use `utils.logging_config.logger` for logging (not `print`).
  - Use `utils.errors` for exceptions (`ValidationError`, `NotFoundError`).
  - Return standardized responses using `success_response` and `error_response` from `utils.errors`.
- **JavaScript:**
  - Use `static/js/main.js` for frontend logic.
  - 2-space indentation.
- **Validation:**
  - Always validate input using `validators/` modules before passing to services.
  - Sanitize strings to prevent XSS.

## Critical Constraints & Patterns

- **ThingSpeak Rate Limits:**
  - **Strict 15s interval** between writes to the same channel.
  - Use `persistent_queue` for writes to ensure compliance.
  - Bulk updates are preferred via `thingspeak_bulk_service.py`.
- **Local Database:**
  - Thread-safe operations are required (handled by `LocalDatabase` class).
  - Data structure must align with ThingSpeak channel fields.
- **Path Handling:**
  - Always use **absolute paths** or `os.path.join` with `basedir` from config.

## Key Files

- `config.py`: Configuration management (API keys, paths).
- `services/hybrid_service.py`: Main entry point for business logic.
- `routes/__init__.py`: Blueprint registration.
- `AGENTS.md`: Detailed agent-specific guidelines.
