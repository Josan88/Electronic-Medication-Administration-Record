"""
Test suite for Queue Management functionality in eMAR.

This test suite verifies:
- Queue persistence (save and load)
- Queue operations (add, get, mark success/failure)
- Queue size limits and overflow handling
- Failed item tracking and retry logic
- Queue monitoring endpoint
"""

import sys
import time
import json
import os
import tempfile
from services.queue_service import PersistentQueue, QueueItem


def test_queue_item_serialization():
    """Test QueueItem to_dict and from_dict methods"""
    print("\n" + "="*60)
    print("QUEUE ITEM SERIALIZATION TEST")
    print("="*60)
    
    try:
        # Create a QueueItem
        data = {
            'patient_id': 'P001',
            'medicine_name': 'Test Medicine',
            'dosage': '500mg'
        }
        item = QueueItem(data)
        
        # Convert to dict
        item_dict = item.to_dict()
        assert 'data' in item_dict, "Missing 'data' in dict"
        assert 'item_id' in item_dict, "Missing 'item_id' in dict"
        assert 'attempts' in item_dict, "Missing 'attempts' in dict"
        assert item_dict['data'] == data, "Data mismatch"
        print("✓ QueueItem.to_dict() works correctly")
        
        # Convert back from dict
        new_item = QueueItem.from_dict(item_dict)
        assert new_item.data == data, "Data mismatch after deserialization"
        assert new_item.item_id == item.item_id, "Item ID mismatch"
        assert new_item.attempts == 0, "Attempts should be 0"
        print("✓ QueueItem.from_dict() works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_persistence():
    """Test queue save and load from disk"""
    print("\n" + "="*60)
    print("QUEUE PERSISTENCE TEST")
    print("="*60)
    
    try:
        # Create temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create queue and add items
        queue1 = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        data1 = {'patient_id': 'P001', 'medicine_name': 'Med1'}
        data2 = {'patient_id': 'P002', 'medicine_name': 'Med2'}
        
        queue1.add(data1)
        queue1.add(data2)
        assert queue1.size() == 2, f"Expected queue size 2, got {queue1.size()}"
        print(f"✓ Added 2 items to queue (size: {queue1.size()})")
        
        # Load queue from same file
        queue2 = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        assert queue2.size() == 2, f"Expected loaded queue size 2, got {queue2.size()}"
        print(f"✓ Loaded queue from disk (size: {queue2.size()})")
        
        # Verify data
        item = queue2.get_next()
        assert item is not None, "Queue should not be empty"
        assert item.data['patient_id'] == 'P001', "First item patient_id mismatch"
        print("✓ Queue data preserved correctly")
        
        # Cleanup
        os.unlink(temp_path)
        print("✓ Test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_operations():
    """Test basic queue operations"""
    print("\n" + "="*60)
    print("QUEUE OPERATIONS TEST")
    print("="*60)
    
    try:
        # Create temporary queue
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        queue = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        
        # Test add
        data = {'patient_id': 'P001', 'medicine_name': 'Test'}
        queue.add(data)
        assert queue.size() == 1, "Queue should have 1 item"
        print("✓ add() works correctly")
        
        # Test get_next
        item = queue.get_next()
        assert item is not None, "get_next() should return an item"
        assert item.data == data, "Data mismatch"
        print("✓ get_next() works correctly")
        
        # Test mark_success
        queue.mark_success(item)
        assert queue.size() == 0, "Queue should be empty after marking success"
        print("✓ mark_success() works correctly")
        
        # Test mark_failure with retry
        queue.add(data)
        item = queue.get_next()
        queue.mark_failure(item, "Test error")
        assert queue.size() == 1, "Item should be back in queue after failure"
        print("✓ mark_failure() with retry works correctly")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_size_limit():
    """Test queue size limit enforcement"""
    print("\n" + "="*60)
    print("QUEUE SIZE LIMIT TEST")
    print("="*60)
    
    try:
        # Create queue with small limit
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        queue = PersistentQueue(storage_path=temp_path, max_size=3, max_retry_attempts=3)
        
        # Add items up to limit
        queue.add({'patient_id': 'P001', 'medicine_name': 'Med1'})
        queue.add({'patient_id': 'P002', 'medicine_name': 'Med2'})
        queue.add({'patient_id': 'P003', 'medicine_name': 'Med3'})
        assert queue.size() == 3, "Queue should have 3 items"
        print("✓ Added items up to max size (3)")
        
        # Try to add beyond limit
        try:
            queue.add({'patient_id': 'P004', 'medicine_name': 'Med4'})
            print("✗ FAIL: Should have raised ValueError for full queue")
            return False
        except ValueError as e:
            assert "full" in str(e).lower(), "Error message should mention queue is full"
            print("✓ Correctly rejected item when queue is full")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_logic():
    """Test failed item retry and max attempts"""
    print("\n" + "="*60)
    print("RETRY LOGIC TEST")
    print("="*60)
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        queue = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        
        # Add item
        data = {'patient_id': 'P001', 'medicine_name': 'Test'}
        queue.add(data)
        
        # Fail it 3 times (max attempts)
        for attempt in range(3):
            item = queue.get_next()
            assert item is not None, f"Item should exist on attempt {attempt + 1}"
            queue.mark_failure(item, f"Error attempt {attempt + 1}")
            
            if attempt < 2:
                assert queue.size() == 1, f"Item should still be in queue after attempt {attempt + 1}"
                print(f"✓ Retry {attempt + 1}: Item moved to back of queue")
            else:
                assert queue.size() == 0, "Queue should be empty after max retries"
                print(f"✓ Retry {attempt + 1}: Item moved to failed list")
        
        # Check failed items
        status = queue.get_status()
        assert status['failed_count'] == 1, "Should have 1 failed item"
        assert len(status['failed_items']) == 1, "Failed items list should have 1 item"
        print("✓ Failed item correctly tracked")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_status():
    """Test queue status reporting"""
    print("\n" + "="*60)
    print("QUEUE STATUS TEST")
    print("="*60)
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        queue = PersistentQueue(storage_path=temp_path, max_size=10, max_retry_attempts=3)
        
        # Get initial status
        status = queue.get_status()
        assert 'queue_size' in status, "Status should include queue_size"
        assert 'failed_count' in status, "Status should include failed_count"
        assert 'max_size' in status, "Status should include max_size"
        assert 'is_full' in status, "Status should include is_full"
        assert 'stats' in status, "Status should include stats"
        print("✓ Status contains all required fields")
        
        # Add items and check status
        queue.add({'patient_id': 'P001', 'medicine_name': 'Med1'})
        queue.add({'patient_id': 'P002', 'medicine_name': 'Med2'})
        
        status = queue.get_status()
        assert status['queue_size'] == 2, "Queue size should be 2"
        assert status['is_full'] == False, "Queue should not be full"
        print("✓ Status correctly reports queue size and is_full")
        
        # Check stats
        assert status['stats']['total_added'] == 2, "Should show 2 items added"
        print("✓ Statistics tracked correctly")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clear_failed_items():
    """Test clearing failed items"""
    print("\n" + "="*60)
    print("CLEAR FAILED ITEMS TEST")
    print("="*60)
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        queue = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=2)
        
        # Add and fail 2 items
        for i in range(2):
            data = {'patient_id': f'P00{i+1}', 'medicine_name': f'Med{i+1}'}
            queue.add(data)
            
            # Fail it max times
            for _ in range(2):
                item = queue.get_next()
                queue.mark_failure(item, "Test error")
        
        status = queue.get_status()
        assert status['failed_count'] == 2, "Should have 2 failed items"
        print(f"✓ Created 2 failed items")
        
        # Clear failed items
        count = queue.clear_failed_items()
        assert count == 2, "Should have cleared 2 items"
        print(f"✓ Cleared {count} failed items")
        
        status = queue.get_status()
        assert status['failed_count'] == 0, "Failed items should be cleared"
        print("✓ Failed items list is empty")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_api_endpoints():
    """Test queue monitoring API endpoints"""
    print("\n" + "="*60)
    print("QUEUE API ENDPOINTS TEST")
    print("="*60)
    
    try:
        import app
        
        # Check that queue blueprint is registered
        assert 'queue' in app.app.blueprints, "Queue blueprint not registered"
        print("✓ Queue blueprint registered")
        
        # Check routes
        routes = [rule.rule for rule in app.app.url_map.iter_rules()]
        assert '/api/queue/status' in routes, "/api/queue/status route not found"
        assert '/api/queue/clear-failed' in routes, "/api/queue/clear-failed route not found"
        print("✓ Queue endpoints registered:")
        print("  - /api/queue/status")
        print("  - /api/queue/clear-failed")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all queue management tests"""
    print("="*60)
    print("QUEUE MANAGEMENT TEST SUITE")
    print("="*60)
    
    tests = [
        test_queue_item_serialization,
        test_queue_persistence,
        test_queue_operations,
        test_queue_size_limit,
        test_retry_logic,
        test_queue_status,
        test_clear_failed_items,
        test_queue_api_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        time.sleep(0.3)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL QUEUE MANAGEMENT TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
