"""
Pytest configuration and fixtures for e2e tests.

This module provides:
- Flask application fixture for testing
- Playwright browser and page fixtures
- Video recording configuration
- Helper utilities for test setup
"""

import os
import re
import sys
import time
import threading
import socket
from datetime import datetime
from pathlib import Path
from contextlib import closing

import pytest
from playwright.sync_api import sync_playwright, Playwright



# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_free_port():
    """Find a free port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def flask_port():
    """Get a free port for the Flask test server."""
    return find_free_port()


@pytest.fixture(scope="session")
def flask_server(flask_port):
    """
    Start Flask application in a background thread for testing.
    The server runs for the entire test session.
    
    Note: Environment variables are set before importing the app module to ensure
    the config module picks up these test values during module initialization.
    """
    # Set minimal environment variables for testing BEFORE importing app
    # This ensures config.py uses these test values during initialization
    os.environ.setdefault('SECRET_KEY', 'test-secret-key')
    os.environ.setdefault('PATIENT_CHANNEL_ID', 'test_channel')
    os.environ.setdefault('PATIENT_WRITE_KEY', 'test_key')
    os.environ.setdefault('PATIENT_READ_KEY', 'test_key')
    os.environ.setdefault('PRESCRIPTION_CHANNEL_ID', 'test_channel')
    os.environ.setdefault('PRESCRIPTION_WRITE_KEY', 'test_key')
    os.environ.setdefault('PRESCRIPTION_READ_KEY', 'test_key')
    os.environ.setdefault('TRACKING_CHANNEL_ID', 'test_channel')
    os.environ.setdefault('TRACKING_WRITE_KEY', 'test_key')
    os.environ.setdefault('TRACKING_READ_KEY', 'test_key')

    # Import app after setting env vars to ensure config picks them up
    from app import app
    
    # Configure Flask for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    # Create a thread to run the server
    server_thread = threading.Thread(
        target=lambda: app.run(
            host='127.0.0.1',
            port=flask_port,
            use_reloader=False,
            threaded=True
        ),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start
    server_url = f"http://127.0.0.1:{flask_port}"
    max_retries = 30
    for i in range(max_retries):
        try:
            import requests
            response = requests.get(f"{server_url}/api/health", timeout=1)
            if response.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        pytest.fail("Flask server failed to start")
    
    yield server_url
    
    # Server will be terminated when pytest exits (daemon thread)


@pytest.fixture(scope="session")
def playwright_instance():
    """Start Playwright for the test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright):
    """Launch browser for the test session."""
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser, tmp_path_factory):
    """
    Create a new browser context for each test with video recording.
    Videos are saved to test-results/videos directory.
    """
    # Create video directory under repository for easier access
    video_dir = Path(__file__).resolve().parent.parent / "test-results" / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(
        record_video_dir=str(video_dir),
        record_video_size={"width": 1280, "height": 720},
        viewport={"width": 1280, "height": 720}
    )
    # Stash for downstream fixtures
    context._video_dir = video_dir  # type: ignore[attr-defined]

    yield context
    
    # Close context to finalize video recording
    context.close()





def _safe_video_name(nodeid: str) -> str:
    """Convert a pytest nodeid into a filesystem-safe video filename."""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid)
    safe = safe.strip("_")
    return safe[:180] or "video"


@pytest.fixture(scope="function")
def page(context, flask_server, request):
    """Create a new page for each test and rename video to match test name."""
    page = context.new_page()
    page.set_default_timeout(30000)  # 30 seconds timeout
    yield page

    video = page.video
    page.close()

    if video:
        target = context._video_dir / f"{_safe_video_name(request.node.nodeid)}.webm"  # type: ignore[attr-defined]
        try:
            # Prefer save_as (copies) then remove the original to avoid clutter
            video.save_as(str(target))
            original = Path(video.path())
            if original.exists() and original != target:
                try:
                    original.unlink()
                except Exception:
                    pass
        except Exception:
            pass



@pytest.fixture(scope="session")
def app_url(flask_server):
    """Provide the base URL for the Flask test server (session-scoped)."""
    return flask_server


@pytest.fixture(scope="function")
def test_patient_id():
    """Generate a unique test patient ID."""
    timestamp = int(time.time() * 1000)
    return f"TEST-{timestamp}"


@pytest.fixture(scope="function")
def today_date():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


@pytest.fixture(scope="function")
def tomorrow_date():
    """Get tomorrow's date in YYYY-MM-DD format."""
    from datetime import timedelta
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
