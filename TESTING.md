# Testing Guide

This document describes the testing infrastructure for the Electronic Medication Administration Record (eMAR) system, including unit tests, end-to-end (E2E) tests, and video recording capabilities using Playwright.

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed.
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   pip install pytest playwright pytest-playwright requests
   ```
3. **Playwright Browsers**: Install the necessary browsers:
   ```bash
   playwright install chromium
   ```

## Running Unit & Integration Tests

The project uses `pytest` for all testing. The test suite covers API endpoints, local database integration, queue management, and status logic.

To run the full test suite (excluding E2E browser tests if you wish, though currently they are included in the default discovery):

```bash
# Run from the repository root
python -m pytest
```

If Playwright browsers have not been installed, the E2E suite will be skipped automatically with a message pointing to `playwright install chromium` so the default run still succeeds.

Or to run specific test modules:

```bash
python -m pytest test_api_validation.py
python -m pytest test_queue_management.py
```

## End-to-End (E2E) Tests

The E2E tests use **Playwright** to simulate user interactions in a real browser environment (headless by default). These tests verify critical workflows like nurse login, patient management, and medication tracking.

### Running E2E Tests

To run all E2E tests:

```bash
python -m pytest tests/test_e2e.py
```

To run a specific E2E test class (e.g., Nurse Workflow):

```bash
python -m pytest tests/test_e2e.py::TestNurseWorkflow
```

### Video Recording & Traces

The testing setup automatically records videos and captures execution traces for every test.

- **Videos**: Saved in `test-results/videos/`
  - Format: `.webm`
  - Naming: `tests_<test_file>__<test_name>.webm` (shortened for readability)
- **Traces**: Saved in `test-results/traces/`
  - Format: `.zip`
  - Naming: Matches the video filename.

**Viewing Traces:**
You can inspect a test run step-by-step (including screenshots, network calls, and console logs) using the Playwright Trace Viewer:

```bash
npx playwright show-trace test-results/traces/your_trace_file.zip
```

## Demo Video Generation

A special single-pass test case has been created to generate a continuous "demo" video of the full nurse workflow (Login → Add Patient → Add Prescription → Search → Mark Complete).

To generate this demo video:

```bash
python -m pytest tests/test_e2e.py -k "test_full_nurse_workflow_single_video"
```

The output video will be available at:
`test-results/videos/tests_test_e2e__test_full_nurse_workflow_single_video.webm`

## Coverage

The test suite includes:
- **Unit Tests**: `test_status_calculator.py`, `test_validation.py`
- **Integration Tests**: `test_local_db_integration.py`, `test_queue_integration.py`, `test_tracking_integration.py`
- **API Tests**: `test_api_validation.py`, `test_blueprints.py`
- **E2E Tests**: `tests/test_e2e.py`

All tests use a local file-based database (`patient_data.json`) and temporary files to ensure isolation and no dependency on external services (like ThingSpeak) during testing.
