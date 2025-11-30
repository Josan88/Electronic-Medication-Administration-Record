# E2E Testing Plan for eMAR System

This document outlines the automated end-to-end testing strategy for the Electronic Medication Administration Record (eMAR) system using Playwright and pytest.

## Overview

The e2e tests validate the complete user workflows from the browser perspective, ensuring the application works correctly end-to-end including UI interactions, API calls, and data persistence.

## Test Framework

- **Test Runner**: pytest
- **Browser Automation**: Playwright
- **Video Recording**: Enabled for test evidence
- **Test Environment**: Local Flask development server

## Test Scenarios

### 1. Nurse Workflow Test

**Objective**: Verify the complete nurse workflow from login to patient management.

**Steps**:
1. Navigate to the role selection page (`/`)
2. Click "Nurse" role card
3. Log in with demo credentials (`nurse` / `nurse123`)
4. Verify redirect to dashboard with nurse role
5. Navigate to "Nurse Dashboard"
6. Add a new patient with test data:
   - Patient ID: `TEST-{timestamp}`
   - Name: "Test Patient"
   - Floor: 1
   - Room: "101"
   - Bed: "A"
   - Age: 30
   - Gender: "Male"
7. Verify success message appears
8. Navigate to Prescriptions tab
9. Add a prescription for the test patient:
   - Medicine Name: "Test Med"
   - Dosage: "500mg"
   - Frequency: 1
   - Start Date: Today
   - End Date: Tomorrow
   - Time Slot: "09:00"
10. Verify prescription queued successfully
11. Navigate to Duty Dashboard
12. Search for the test patient
13. Verify patient information displays correctly
14. Verify prescription appears in active medications

### 2. Management Workflow Test

**Objective**: Verify management dashboard access and statistics display.

**Steps**:
1. Navigate to the role selection page (`/`)
2. Click "Management" role card
3. Log in with demo credentials (`manager` / `manager123`)
4. Verify redirect to dashboard with management role
5. Verify Management Dashboard is visible
6. Verify statistics cards display:
   - Total Patients count
   - Active Prescriptions count
   - Medications Administered Today count
7. Verify the Rounds Summary chart is rendered
8. Verify the chart shows correct labels (9am / 1pm / 5pm / 9pm)

### 3. Status Simulation Test (Complete Status)

**Objective**: Verify that marking a medication as taken changes status from "Pending" to "Complete".

**Steps**:
1. Add a test patient via API (`POST /api/patients`)
2. Add a prescription via API (`POST /api/prescriptions`)
3. Wait for prescription to be processed
4. Navigate to Duty Dashboard as nurse
5. Verify medication shows "Pending" status (Yellow indicator)
6. Call tracking API to mark medication as complete:
   ```json
   {
     "patient_id": "TEST-ID",
     "medicine_name": "Test Med",
     "status": "complete",
     "consume_date": "2025-01-01T09:00:00",
     "time_slot": "09:00"
   }
   ```
7. Reload the dashboard
8. Verify status changed to "Complete" (Green indicator)
9. Navigate to Management Dashboard
10. Verify the chart reflects the completed medication

## Video Recording Configuration

Video recording is enabled for all tests to provide visual evidence of test execution:

```python
browser = playwright.chromium.launch(
    headless=True,
    args=['--no-sandbox']
)
context = browser.new_context(
    record_video_dir="./test-results/videos/",
    record_video_size={"width": 1280, "height": 720}
)
```

Videos are saved to `./test-results/videos/` directory.

## Test Data Management

- Test patient IDs use timestamp suffixes to ensure uniqueness
- Tests clean up after themselves where possible
- The local database is used (no ThingSpeak dependency for tests)

## Running Tests

```bash
# Install dependencies
pip install pytest playwright
playwright install chromium

# Run all e2e tests
pytest tests/test_e2e.py -v

# Run with video recording
pytest tests/test_e2e.py -v --headed

# Run specific test
pytest tests/test_e2e.py::TestNurseWorkflow -v
```

## Acceptance Criteria

- [ ] Nurse Workflow test passes (Add Patient → Add Prescription → Search)
- [ ] Management Workflow test passes (Login → Check Stats)
- [ ] Status Simulation: Test successfully posts to tracking API and visually verifies green "Complete" status
- [ ] Video recording is enabled and working
