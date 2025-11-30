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

## Writing New Tests

The project follows two distinct patterns for testing:

### 1. Unit & Integration Tests (Hybrid Pattern)

Tests located in the root directory (e.g., `test_validation.py`, `test_queue_integration.py`) follow a hybrid pattern. They can be run as standalone Python scripts or discovered by `pytest`.

**Template:**

```python
import sys
from utils.errors import ValidationError

def test_my_new_feature():
    """Test description"""
    print("\n" + "="*60)
    print("MY NEW FEATURE TEST")
    print("="*60)
    
    tests_passed = 0
    
    # Test Case 1
    print("\nTest 1: Verify basic functionality")
    try:
        # Setup & Act
        result = my_function(input_data)
        
        # Assert
        assert result == expected_value
        print(f"✓ PASS: Result matched expected value")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise  # Re-raise to ensure pytest marks it as failed

    return tests_passed

def main():
    # Run all tests in this file
    try:
        test_my_new_feature()
        print("\n✓ ALL TESTS PASSED")
        return 0
    except:
        print("\n✗ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 2. End-to-End Tests (Playwright Pattern)

Tests located in the `tests/` directory (e.g., `test_e2e.py`) use standard `pytest` classes and fixtures with Playwright.

**Template:**

```python
import pytest
from playwright.sync_api import Page, expect

class TestMyFeatureWorkflow:
    """
    Test the user workflow for My Feature.
    """

    def test_user_can_perform_action(self, page: Page, app_url: str):
        """Test that a user can perform X action."""
        # 1. Navigate
        page.goto(f"{app_url}/dashboard")

        # 2. Interact
        page.click("#my-button")
        page.fill("#input-field", "test value")
        
        # 3. Verify
        expect(page.locator(".success-message")).to_be_visible()
        expect(page.locator("#result")).to_contain_text("test value")
```
