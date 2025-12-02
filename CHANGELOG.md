# Changelog

All notable changes to the Electronic Medication Administration Record (eMAR) project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- User authentication and authorization
- Role-based access control (doctors, nurses, administrators)
- Barcode scanning for patient and medication identification
- Automated alerts for missed medications
- Mobile application
- Integration with hospital management systems

---

## [3.0.0] - 2025-11-20

### Added
- **Local Database System**: JSON file-based local storage as primary data source
  - Instant writes with no rate limits
  - Located at `/tmp/emar_local_db/` (configurable via `LOCAL_DB_PATH`)
  - Three storage files: `patient_info.json`, `medicine_prescription.json`, `medicine_track.json`
- **ThingSpeak Bulk Write Backup**: Automatic periodic sync to ThingSpeak cloud
  - Batches up to 100 records per API call
  - Configurable sync interval (default: 5 minutes)
  - Retry logic with exponential backoff (5 attempts max)
- **Hybrid Service Layer**: Unified interface for data operations
  - Local database as primary storage
  - Automatic fallback to ThingSpeak for reads if local unavailable
  - Backward compatible with existing API
- **New API Endpoints**:
  - `GET /api/queue/sync-status` - Monitor sync queue status
  - `POST /api/queue/sync-clear-failed` - Clear failed sync items
  - `GET /api/queue/thingspeak-health` - Check ThingSpeak channel availability
- **Sync Service**: Background worker for ThingSpeak synchronization
  - Rate limit enforcement (15-second delay between channel writes)
  - Deduplication of pending sync operations
  - Persistent queue state

### Changed
- Data architecture shifted from ThingSpeak-primary to local-database-primary
- Write operations now return immediately (no 15-second wait for patients/tracking)
- Improved error handling with channel-specific error messages

### Performance
- ~99% reduction in write latency (instant vs 15 seconds)
- ~99% reduction in bulk sync time (100 records in ~2 seconds vs 25 minutes)

---

## [2.0.0] - 2025-11-15

### Added
- **Interactive API Documentation**: Swagger UI at `/api/docs`
  - Complete OpenAPI 3.0 specification (`swagger.yaml`)
  - Interactive "Try it out" functionality
  - Request/response schemas with examples
- **Comprehensive Documentation Suite**:
  - `docs/ARCHITECTURE.md` - System architecture with Mermaid diagrams
  - `docs/DEPLOYMENT.md` - Development and production deployment guide
  - `docs/API_EXAMPLES.md` - Examples in curl, PowerShell, Python, JavaScript
  - `docs/CONTRIBUTING.md` - Contributor guidelines and coding standards
- **Node-RED Integration**: Bridge between cloud data and HMI/PLC
  - Modbus TCP server for HMI communication
  - ThingSpeak data fetching and filtering
  - Dashboard for manual testing

### Changed
- Updated README.md with documentation links and improved structure
- Enhanced error messages with more context

---

## [1.3.0] - 2025-11-13

### Added
- **Route Blueprints**: Organized routes into domain-specific modules
  - `routes/patients.py` - Patient management (6 endpoints)
  - `routes/prescriptions.py` - Prescription routes (2 endpoints)
  - `routes/tracking.py` - Medication tracking (2 endpoints)
  - `routes/queue.py` - Queue management (2 endpoints)
- **Blueprint Tests**: `test_blueprints.py` with 100% pass rate

### Changed
- Reduced `app.py` from 237 lines to 86 lines (64% reduction)
- Improved code organization following Flask best practices

---

## [1.2.0] - 2025-11-13

### Added
- **Persistent Prescription Queue**: Queue survives application restarts
  - Stored at `/tmp/prescription_queue.json`
  - Configurable max size (default: 1000 items)
- **Queue Monitoring API**:
  - `GET /api/queue/status` - Current queue size, failed items, statistics
  - `POST /api/queue/clear-failed` - Clear failed items from queue
- **Retry Mechanism**: Automatic retry for failed prescriptions
  - Max 3 attempts with exponential backoff
  - Failed items tracked separately
- **Queue Statistics**: Track total added, processed, failed, retried items

### Changed
- Prescription writes now return HTTP 202 (Accepted) immediately
- Background worker processes queue with rate limit compliance

---

## [1.1.0] - 2025-11-11

### Added
- **Input Validation Layer**: Comprehensive validation for all API endpoints
  - `validators/patient_validator.py`
  - `validators/prescription_validator.py`
  - `validators/tracking_validator.py`
- **Security Enhancements**:
  - HTML escaping for XSS prevention
  - Fixed ReDoS vulnerability in dosage validation
  - Patient existence checks before prescription/tracking
- **Validation Tests**: 18 unit tests + 10 API integration tests (100% pass)

### Changed
- All POST endpoints now validate input before processing
- Improved error messages with field-specific feedback

---

## [1.0.0] - 2025-11-09

### Added
- **Core Application**: Flask-based eMAR system
- **Patient Management**:
  - Add, view, and manage patient information
  - Store location (floor, room, bed) and clinical notes
- **Prescription System**:
  - Record medication orders with dosage and frequency
  - Define treatment duration and time slots
  - Background queue processing
- **Medication Tracking**:
  - Real-time recording of medication administration
  - Automatic status calculation (complete/pending)
  - Multiple datetime format support
- **Dashboard Views**:
  - Duty Dashboard: Timeline view + patient search
  - Nurse Dashboard: Patient management + prescription entry
  - Management Dashboard: Statistics and charts
- **ThingSpeak Integration**: Three-channel cloud storage
  - Patient Information Channel
  - Medicine Prescription Channel
  - Medicine Tracking Channel
- **Configuration Management**: Centralized config with environment validation
- **Structured Logging**: Python logging module with rotation
- **Error Handling**: Custom exceptions and standardized responses

### Technical
- Flask 3.0.0 backend
- Vanilla JavaScript frontend (ES6+)
- RESTful API design
- Threading for background processing

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 3.0.0 | 2025-11-20 | Local database, bulk sync, hybrid architecture |
| 2.0.0 | 2025-11-15 | Swagger UI, comprehensive docs, Node-RED |
| 1.3.0 | 2025-11-13 | Route blueprints, code organization |
| 1.2.0 | 2025-11-13 | Persistent queue, monitoring API |
| 1.1.0 | 2025-11-11 | Input validation, security fixes |
| 1.0.0 | 2025-11-09 | Initial release |

---

[Unreleased]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Josan88/Electronic-Medication-Administration-Record/releases/tag/v1.0.0
