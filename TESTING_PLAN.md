# Testing Plan for eMAR Dashboards

## Overview
This plan outlines the strategy for automated end-to-end (E2E) testing of the eMAR system's Nurse and Management dashboards. We will use **Playwright for Python** combined with **pytest**.

## Why Playwright?
- **Video Recording:** Playwright has built-in support for recording videos of test executions, which satisfies the requirement to visually verify tests.
- **Reliability:** It waits automatically for elements to be ready, reducing flaky tests.
- **Speed:** Runs tests in parallel and is generally faster than Selenium.
- **Browser Support:** Supports Chromium, Firefox, and WebKit.

## Prerequisites
1.  **Python Packages:**
    -   `pytest`
    -   `pytest-playwright`
2.  **Browser Binaries:**
    -   Playwright browsers (installed via `playwright install`)

## Test Scenarios

### 1. Nurse Dashboard Interactions
*   **Role Selection:** Verify clicking "Nurse" redirects to the correct view.
*   **Patient Management:**
    *   Add a new patient (Form submission).
    *   Verify patient appears in the list.
*   **Prescription Management:**
    *   Add a medication (Form submission).
    *   Add time slots.
    *   Submit and verify in the list.
*   **Duty Dashboard:**
    *   Verify tabs (Round Timeline, Search by Patient).
    *   Perform a patient search.

### 2. Management Dashboard Interactions
*   **Role Selection:** Verify clicking "Management" redirects to the correct view.
*   **Statistics:** Verify the presence of "Total Patients", "Active Prescriptions", etc.
*   **Charts:** Verify the "Rounds Summary" chart is visible.

## Configuration for Video Recording
We will configure `pytest` to record videos for all test runs (or only failed ones).
Command: `pytest --video on`

## Implementation Steps
1.  Install dependencies: `pip install pytest pytest-playwright`
2.  Install browsers: `playwright install`
3.  Create test file: `tests/test_ui_interactions.py`
4.  Run tests: `pytest tests/test_ui_interactions.py --video on`
5.  View videos: Videos will be saved in the `test-results/` directory.
