"""
Integration test for entry_id == 0 retry behavior.

This test verifies that when ThingSpeak returns entry_id 0,
the prescription is marked as failed and requeued for retry.
"""

import tempfile
import time
from unittest.mock import Mock, patch
from services.queue_service import PersistentQueue
from utils.logging_config import logger


def test_entry_id_zero_retry():
    """Test that entry_id == 0 triggers a retry via mark_failure"""

    print("=" * 60)
    print("ENTRY_ID ZERO RETRY TEST")
    print("=" * 60)

    # Create a temporary queue
    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    temp_path = temp_file.name
    temp_file.close()

    queue = PersistentQueue(storage_path=temp_path, max_size=10, max_retry_attempts=3)

    # Add a test prescription
    test_data = {
        "patient_id": "P001",
        "medicine_name": "Test Medicine",
        "dosage": "10mg",
        "frequency": "daily",
    }

    queue.add(test_data)
    print(f"✓ Added test prescription to queue (size: {queue.size()})")

    # Simulate the worker processing with entry_id == 0
    item = queue.get_next()
    assert item is not None, "Queue should have an item"

    print(f"\n--- Simulating ThingSpeak write returning entry_id = 0 ---")

    # Mock ThingSpeak response with entry_id = 0
    entry_id = 0
    error_msg = "ThingSpeak returned entry_id 0 (write not accepted)"

    # Simulate the worker logic from app.py
    if isinstance(entry_id, int) and entry_id > 0:
        print("✗ Should NOT mark as success for entry_id 0")
        queue.mark_success(item)
    else:
        print(f"✓ Detected entry_id 0, marking as failure: {error_msg}")
        queue.mark_failure(item, error_msg)

    # Verify the item was requeued
    status = queue.get_status()
    print(f"\nQueue Status after first attempt:")
    print(f"  - Queue size: {status['queue_size']}")
    print(f"  - Failed count: {status['failed_count']}")
    print(f"  - Total retried: {status['stats']['total_retried']}")

    assert status["queue_size"] == 1, "Item should still be in queue"
    assert status["failed_count"] == 0, "Item should not be in failed list yet"
    assert status["stats"]["total_retried"] == 1, "Should have 1 retry"

    # Verify the item is at the back of the queue with incremented attempts
    item = queue.get_next()
    assert item is not None, "Item should be in queue for retry"
    assert item.attempts == 1, f"Item should have 1 attempt, got {item.attempts}"
    assert item.last_error == "ThingSpeak returned entry_id 0 (write not accepted)"
    print(f"✓ Item requeued with attempts = {item.attempts}")

    # Simulate second failure
    print(f"\n--- Simulating second write attempt with entry_id = 0 ---")
    queue.mark_failure(item, error_msg)

    item = queue.get_next()
    assert item is not None, "Item should be in queue for second retry"
    assert item.attempts == 2, f"Item should have 2 attempts, got {item.attempts}"
    print(f"✓ Item requeued with attempts = {item.attempts}")

    # Simulate third failure (should move to failed list)
    print(f"\n--- Simulating third write attempt with entry_id = 0 ---")
    queue.mark_failure(item, error_msg)

    status = queue.get_status()
    print(f"\nQueue Status after third attempt:")
    print(f"  - Queue size: {status['queue_size']}")
    print(f"  - Failed count: {status['failed_count']}")
    print(f"  - Total failed: {status['stats']['total_failed']}")

    assert status["queue_size"] == 0, "Queue should be empty"
    assert status["failed_count"] == 1, "Item should be in failed list"
    assert status["stats"]["total_failed"] == 1, "Should have 1 failed item"
    print(f"✓ Item moved to failed list after max retries")

    # Verify failed item details
    if status["failed_items"]:
        failed_item = status["failed_items"][0]
        print(f"\nFailed item details:")
        print(f"  - Patient ID: {failed_item['patient_id']}")
        print(f"  - Medicine: {failed_item['medicine_name']}")
        print(f"  - Attempts: {failed_item['attempts']}")
        print(f"  - Error: {failed_item['last_error']}")
        assert failed_item["attempts"] == 3
        assert "entry_id 0" in failed_item["last_error"]

    print("\n" + "=" * 60)
    print("✓ ENTRY_ID ZERO RETRY TEST PASSED!")
    print("=" * 60)


def test_entry_id_success_after_retry():
    """Test that a successful write (entry_id > 0) after retry removes item from queue"""

    print("\n" + "=" * 60)
    print("SUCCESSFUL WRITE AFTER RETRY TEST")
    print("=" * 60)

    # Create a temporary queue
    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    temp_path = temp_file.name
    temp_file.close()

    queue = PersistentQueue(storage_path=temp_path, max_size=10, max_retry_attempts=3)

    # Add a test prescription
    test_data = {
        "patient_id": "P002",
        "medicine_name": "Test Medicine 2",
        "dosage": "20mg",
        "frequency": "twice daily",
    }

    queue.add(test_data)
    print(f"✓ Added test prescription to queue (size: {queue.size()})")

    # First attempt fails with entry_id = 0
    print(f"\n--- First attempt: entry_id = 0 ---")
    item = queue.get_next()
    error_msg = "ThingSpeak returned entry_id 0 (write not accepted)"
    queue.mark_failure(item, error_msg)
    print(f"✓ Item requeued after failure (attempts: 1)")

    # Second attempt succeeds with entry_id = 123
    print(f"\n--- Second attempt: entry_id = 123 ---")
    item = queue.get_next()
    assert item is not None, "Item should be in queue for second attempt"
    entry_id = 123

    if isinstance(entry_id, int) and entry_id > 0:
        print(f"✓ Detected successful write (entry_id = {entry_id})")
        queue.mark_success(item)

    # Verify queue is now empty
    status = queue.get_status()
    print(f"\nQueue Status after successful write:")
    print(f"  - Queue size: {status['queue_size']}")
    print(f"  - Failed count: {status['failed_count']}")
    print(f"  - Total processed: {status['stats']['total_processed']}")

    assert status["queue_size"] == 0, "Queue should be empty"
    assert status["failed_count"] == 0, "No failed items"
    assert status["stats"]["total_processed"] == 1, "Should have 1 processed item"

    print("\n" + "=" * 60)
    print("✓ SUCCESSFUL WRITE AFTER RETRY TEST PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_entry_id_zero_retry()
        test_entry_id_success_after_retry()

        print("\n" + "=" * 60)
        print("ALL ENTRY_ID RETRY TESTS PASSED! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        raise
