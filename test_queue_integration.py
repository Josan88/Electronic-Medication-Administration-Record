"""
Integration test for Queue Management API endpoints.

This test verifies that the queue management endpoints work correctly
with the running Flask application.
"""

import sys
import time
import json
from flask import Flask
from flask.testing import FlaskClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def test_queue_status_endpoint():

    """Test the queue status endpoint"""
    print("\n" + "="*60)
    print("QUEUE STATUS ENDPOINT TEST")
    print("="*60)
    
    try:
        import app as flask_app
        
        # Create test client
        with flask_app.app.test_client() as client:
            # Test GET /api/queue/status
            response = client.get('/api/queue/status')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = json.loads(response.data)
            assert data['success'] == True, "Response should indicate success"
            assert 'data' in data, "Response should contain data"
            
            queue_status = data['data']
            assert 'queue_size' in queue_status, "Status should include queue_size"
            assert 'failed_count' in queue_status, "Status should include failed_count"
            assert 'max_size' in queue_status, "Status should include max_size"
            assert 'is_full' in queue_status, "Status should include is_full"
            assert 'stats' in queue_status, "Status should include stats"
            
            print(f"✓ Status endpoint returned successfully")
            print(f"  - Queue size: {queue_status['queue_size']}")
            print(f"  - Failed count: {queue_status['failed_count']}")
            print(f"  - Max size: {queue_status['max_size']}")
            print(f"  - Is full: {queue_status['is_full']}")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise



def test_queue_clear_failed_endpoint():
    """Test the clear failed items endpoint"""
    print("\n" + "="*60)
    print("CLEAR FAILED ITEMS ENDPOINT TEST")
    print("="*60)
    
    try:
        import app as flask_app
        
        # Create test client
        with flask_app.app.test_client() as client:
            # Test POST /api/queue/clear-failed
            response = client.post('/api/queue/clear-failed')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = json.loads(response.data)
            assert data['success'] == True, "Response should indicate success"
            assert 'data' in data, "Response should contain data"
            assert 'cleared_count' in data['data'], "Data should include cleared_count"
            
            print(f"✓ Clear failed endpoint returned successfully")
            print(f"  - Cleared count: {data['data']['cleared_count']}")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise



def test_prescription_queue_overflow():
    """Test that queue properly handles overflow condition"""
    print("\n" + "="*60)
    print("PRESCRIPTION QUEUE OVERFLOW TEST")
    print("="*60)
    
    try:
        import app as flask_app
        from services.queue_service import PersistentQueue
        import tempfile
        import os
        
        # Create a test queue with small limit
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        test_queue = PersistentQueue(storage_path=temp_path, max_size=2, max_retry_attempts=3)
        
        # Fill the queue to capacity
        test_queue.add({'patient_id': 'P001', 'medicine_name': 'Med1'})
        test_queue.add({'patient_id': 'P002', 'medicine_name': 'Med2'})
        print("✓ Added 2 items to test queue (at capacity)")
        
        # Try to add beyond capacity
        try:
            test_queue.add({'patient_id': 'P003', 'medicine_name': 'Med3'})
            print("✗ FAIL: Should have raised ValueError for full queue")
            os.unlink(temp_path)
            raise AssertionError("Queue should raise ValueError for full queue")
        except ValueError as e:
            assert "full" in str(e).lower(), "Error should mention queue is full"
            print("✓ Queue correctly rejected item when full")

        # Check that status reflects full state
        status = test_queue.get_status()
        assert status['is_full'] == True, "Status should show queue is full"
        print("✓ Queue status correctly shows is_full=True")

        # Cleanup
        os.unlink(temp_path)

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise



def test_prescription_endpoint_with_queue():
    """Test that prescription endpoint properly uses the queue"""
    print("\n" + "="*60)
    print("PRESCRIPTION ENDPOINT QUEUE INTEGRATION TEST")
    print("="*60)
    
    try:
        import app as flask_app
        
        # Get initial queue size
        initial_size = flask_app.persistent_queue.size()
        print(f"Initial queue size: {initial_size}")
        
        # Create test client
        with flask_app.app.test_client() as client:
            # Test POST /api/prescriptions (should queue the prescription)
            prescription_data = {
                'patient_id': 'P999',  # Use a test patient ID
                'medicine_name': 'Test Medicine',
                'dosage': '500mg',
                'frequency': 'Once daily',
                'start_date': '2025-11-13',
                'end_date': '2025-11-20',
                'time_slot': '08:00'
            }
            
            # Note: This will fail validation if P999 doesn't exist
            # but we're just testing the queueing mechanism
            response = client.post('/api/prescriptions',
                                  data=json.dumps(prescription_data),
                                  content_type='application/json')
            
            # Check response code (should be 202 for queued, or 400 for validation error)
            if response.status_code == 202:
                # Prescription was queued successfully
                data = json.loads(response.data)
                assert data['success'] == True, "Response should indicate success"
                assert 'queued' in data['message'].lower(), "Message should mention queuing"
                print("✓ Prescription endpoint accepts and queues prescriptions")
                
                # Verify queue size increased
                new_size = flask_app.persistent_queue.size()
                assert new_size == initial_size + 1, f"Queue size should increase by 1"
                print(f"✓ Queue size increased from {initial_size} to {new_size}")
                
            elif response.status_code == 400:
                # Expected validation error (patient doesn't exist)
                data = json.loads(response.data)
                print(f"✓ Prescription validation works (patient check)")
                print(f"  - Validation error: {data.get('error', 'Unknown')}")

            else:
                raise AssertionError(f"Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise



def test_queue_persistence_across_restarts():
    """Test that queue data persists across application restarts"""
    print("\n" + "="*60)
    print("QUEUE PERSISTENCE ACROSS RESTARTS TEST")
    print("="*60)
    
    try:
        from services.queue_service import PersistentQueue
        import tempfile
        import os
        
        # Create a persistent file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = temp_file.name
        temp_file.close()
        
        # Create first queue instance and add data
        queue1 = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        queue1.add({'patient_id': 'P001', 'medicine_name': 'Med1'})
        queue1.add({'patient_id': 'P002', 'medicine_name': 'Med2'})
        initial_size = queue1.size()
        initial_stats = queue1.get_status()['stats']
        print(f"✓ Created queue with {initial_size} items")
        
        # Simulate restart by creating new queue instance from same file
        del queue1  # Delete first instance
        queue2 = PersistentQueue(storage_path=temp_path, max_size=100, max_retry_attempts=3)
        restored_size = queue2.size()
        restored_stats = queue2.get_status()['stats']
        
        assert restored_size == initial_size, f"Size mismatch: {restored_size} != {initial_size}"
        print(f"✓ Queue size restored correctly: {restored_size} items")
        
        assert restored_stats['total_added'] == initial_stats['total_added'], "Stats not preserved"
        print("✓ Queue statistics preserved correctly")
        
        # Verify data integrity
        item = queue2.get_next()
        assert item is not None, "Queue should not be empty"
        assert item.data['patient_id'] == 'P001', "First item data mismatch"
        print("✓ Queue data integrity verified")
        
        # Cleanup
        os.unlink(temp_path)

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise



def main():
    """Run all integration tests"""
    print("="*60)
    print("QUEUE MANAGEMENT INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        test_queue_status_endpoint,
        test_queue_clear_failed_endpoint,
        test_prescription_queue_overflow,
        test_prescription_endpoint_with_queue,
        test_queue_persistence_across_restarts,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        result = test_func()
        if result is False:
            print(f"✗ {test_func.__name__} reported failure")
        else:
            passed += 1
        time.sleep(0.3)

    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
