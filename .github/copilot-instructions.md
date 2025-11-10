# Electronic Medication Administration Record (eMAR) - AI Coding Guide

## Architecture Overview

This is a **Flask-based web application** that integrates with **ThingSpeak IoT Platform** for cloud data storage. The system manages patient records, medication prescriptions, and tracks medication administration in real-time.

### Three-Channel ThingSpeak Architecture

The app uses **three separate ThingSpeak channels**, each with 8-field data constraints:

1. **Patient Info Channel** (ID: 3124887): Stores patient demographics
2. **Prescription Channel** (ID: 3124898): Stores medication prescriptions with queueing system
3. **Tracking Channel** (ID: 3131200): Records actual medication administration

### Critical Rate Limiting

**ThingSpeak free tier enforces a 15-second minimum interval between writes per channel**. The codebase implements:

- `TS_RATE_LIMIT_SECONDS = 15` global constant
- **Background queue processor** (`process_prescription_queue()`) runs in a daemon thread to handle prescription submissions
- Prescription POST returns HTTP 202 (Accepted) immediately, then queues for background processing
- Uses thread-safe `deque` with `Lock` for queue management
- **Patient and tracking endpoints write directly** (no queue) - enforces ThingSpeak rate limit per channel, user must wait 15 seconds between submissions to same channel
- **Queue is NOT persisted** - prescription queue clears on app restart (in-memory `deque`)

## Key Files & Responsibilities

- **`app.py`**: Flask backend with all REST API endpoints, ThingSpeak integration, and background worker thread
- **`templates/index.html`**: Single-page application with three main dashboards (Duty, Nurse, Management)
- **`static/js/main.js`**: Handles all frontend logic, AJAX calls, dashboard switching, and UI updates
- **`test_api.py`**: Comprehensive API test suite with 15-second delays built in
- **`.env`**: Contains ThingSpeak API keys (channel IDs, read/write keys) and Flask SECRET_KEY

## Development Workflow

### Running the Application

```powershell
# Activate virtual environment (if using .venv)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Flask server (defaults to http://0.0.0.0:5000)
python app.py
```

### Testing the API

```powershell
# Run comprehensive test suite (includes automatic 15-second delays between writes)
# Takes ~50 seconds due to ThingSpeak rate limits
python test_api.py

# Quick health check via PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# Test with custom BASE_URL (e.g., network device)
# Edit BASE_URL in test_api.py line 12 before running
```

### Debugging Tips

- Check ThingSpeak write queue: Monitor terminal for `"Successfully posted entry"` messages from background worker
- Rate limit errors: Look for `response.raise_for_status()` exceptions in logs
- Frontend issues: Use browser DevTools Network tab to see AJAX responses

## Project-Specific Conventions

### Data Flow Pattern

All endpoints follow: **Client → Flask API → ThingSpeak REST API → Cloud Storage**

- GET requests: Fetch from ThingSpeak, transform JSON field1-field8 to readable keys
- POST requests: Accept JSON, map to ThingSpeak field parameters, use GET method for ThingSpeak update (quirk of ThingSpeak API)

### Field Mapping Convention

ThingSpeak channels use generic `field1`-`field8` names. The code maintains field mappings in `THINGSPEAK_CHANNELS` dict:

```python
"fields": {
    "field1": "Patient_ID",
    "field2": "Medicine_Name",
    # ...
}
```

When reading ThingSpeak data, always map `feed.get("field1")` to the semantic name (e.g., `patient["patient_id"]`).

### Frontend Dashboard Structure

Three main dashboards accessible via burger menu (`.sidenav`):

1. **Duty Dashboard**: Round timeline view + patient medication search
2. **Nurse Dashboard**: Patient management + prescription entry (active by default)
3. **Management Dashboard**: Statistics and charts

Use `showDashboard('dashboardId')` to switch, which handles visibility and data loading.

### Error Handling Pattern

```python
try:
    # Operation
    response.raise_for_status()
    return jsonify({"success": True, "data": result})
except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500
```

Frontend checks `response.success` before processing data.

## Critical Integration Points

### Environment Variables Required

```
SECRET_KEY=<flask-secret-key>
PATIENT_CHANNEL_ID=3124887
PATIENT_WRITE_KEY=<key>
PATIENT_READ_KEY=<key>
PRESCRIPTION_CHANNEL_ID=3124898
PRESCRIPTION_WRITE_KEY=<key>
PRESCRIPTION_READ_KEY=<key>
TRACKING_CHANNEL_ID=3131200
TRACKING_WRITE_KEY=<key>
TRACKING_READ_KEY=<key>
```

### ThingSpeak API Usage

- **Base URL**: `https://api.thingspeak.com`
- **Write**: `GET /update?api_key=<write_key>&field1=value1&field2=value2...` (15-second rate limit per channel)
- **Read**: `GET /channels/<channel_id>/feeds.json?api_key=<read_key>&results=100`
- Always use `results=100` parameter to limit API response size
- **Pagination concern**: As data grows beyond 100 entries per channel, older records are inaccessible without pagination strategy (ThingSpeak supports `start` and `end` parameters for date-based queries)

### Background Worker Thread

Initialized at app startup: `worker_thread = Thread(target=process_prescription_queue, daemon=True)`

- Daemon thread ensures clean shutdown with Flask
- Polls `prescription_queue` every 1 second
- Only writes when `time.time() - last_ts_write_time >= 15`
- **Queue is volatile** - prescription submissions in queue are lost on app restart
- Prescription endpoint is the **ONLY** endpoint using background queue to avoid blocking UI

## Common Patterns

### Adding New Endpoints

1. Define route with proper HTTP method
2. Parse `request.json` with null check
3. Map data to ThingSpeak channel fields
4. Handle ThingSpeak response (returns entry_id as plain text)
5. Return JSON with `success` boolean

### Patient ID Validation

Use `/api/check_patient/<patient_id>` endpoint before adding prescriptions/tracking to validate patient exists.

### Frontend Form Submission

```javascript
async function addPatient() {
  const patientData = {
    /* collect form fields */
  };
  const response = await fetch("/api/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patientData),
  });
  const result = await response.json();
  if (result.success) {
    showSuccess("Patient added!");
  }
}
```

## Technology Stack

- **Backend**: Flask 3.0.0, python-dotenv, requests
- **Frontend**: Vanilla JavaScript (ES6+), CSS Grid/Flexbox
- **Data Storage**: ThingSpeak IoT Platform (REST API) - Free tier with 15-second write rate limit
- **No database**: All persistence via ThingSpeak cloud channels
- **Concurrency**: Threading module for background queue processing (prescriptions only)

## Known Limitations & Considerations

1. **Data Loss on Restart**: Prescription queue (in-memory) clears on app restart
2. **Rate Limiting UX**: Patient/tracking endpoints block for 15 seconds due to direct ThingSpeak writes
3. **Data Pagination**: Only last 100 records accessible per channel without implementing date-range queries
4. **No Transactions**: ThingSpeak writes are independent - no rollback if related data fails (e.g., prescription without patient)
5. **Single Writer**: Background worker serializes prescription writes - high volume could cause queue buildup
