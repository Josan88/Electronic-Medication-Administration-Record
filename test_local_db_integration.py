"""
Integration Tests for Local Database and ThingSpeak Sync

This test suite validates the local database functionality, bulk write synchronization,
and failover scenarios for the eMAR system.
"""

import sys
import json
import time
import os
from services.local_db_service import LocalDatabase, LocalDatabaseError
from services.thingspeak_bulk_service import thingspeak_bulk_service, ThingSpeakBulkError
from services.sync_service import SyncQueue
from services.hybrid_service import hybrid_service


def test_local_database_operations():
    """Test local database CRUD operations"""
    print("\n" + "="*60)
    print("LOCAL DATABASE OPERATIONS TEST")
    print("="*60)
    
    try:
        # Create a test local database
        test_db_path = '/tmp/test_emar_local_db'
        test_db = LocalDatabase(base_path=test_db_path)
        
        # Test 1: Write patient data
        patient_data = {
            'patient_id': 'TEST001',
            'name': 'Test Patient',
            'floor': '1',
            'room': '101',
            'bed': 'A',
            'age': '45',
            'gender': 'M',
            'notes': 'Test notes'
        }
        
        entry_id = test_db.write_to_channel('patient_info', patient_data)
        assert entry_id > 0, "Entry ID should be positive"
        print(f"✓ PASS: Wrote patient to local database (entry_id: {entry_id})")
        
        # Test 2: Read patient data
        patients = test_db.read_channel('patient_info')
        assert len(patients) > 0, "Should have at least one patient"
        assert patients[-1]['patient_id'] == 'TEST001', "Should find the test patient"
        print(f"✓ PASS: Read patient from local database ({len(patients)} records)")
        
        # Test 3: Find by field
        found_patients = test_db.find_by_field('patient_info', 'patient_id', 'TEST001')
        assert len(found_patients) == 1, "Should find exactly one patient"
        assert found_patients[0]['name'] == 'Test Patient', "Patient name should match"
        print(f"✓ PASS: Find by field working correctly")
        
        # Test 4: Write prescription data
        prescription_data = {
            'patient_id': 'TEST001',
            'medicine_name': 'Test Medicine',
            'dosage': '10mg',
            'frequency': 'Once daily',
            'start_date': '2025-11-20',
            'end_date': '2025-11-27',
            'time_slot': '08:00'
        }
        
        entry_id = test_db.write_to_channel('medicine_prescription', prescription_data)
        assert entry_id > 0, "Entry ID should be positive"
        print(f"✓ PASS: Wrote prescription to local database (entry_id: {entry_id})")
        
        # Test 5: Get feeds for bulk write
        feeds = test_db.get_feeds_for_bulk_write('patient_info', since_entry_id=0)
        assert len(feeds) > 0, "Should have feeds for bulk write"
        assert 'field1' in feeds[0], "Feed should have ThingSpeak field format"
        assert feeds[0]['field1'] == 'TEST001', "Field1 should be patient_id"
        print(f"✓ PASS: Get feeds for bulk write working correctly ({len(feeds)} feeds)")
        
        # Test 6: Test metadata
        metadata = test_db.get_channel_metadata('patient_info')
        assert 'entry_count' in metadata, "Metadata should have entry_count"
        assert metadata['entry_count'] > 0, "Entry count should be positive"
        print(f"✓ PASS: Metadata tracking working correctly")
        
        # Cleanup
        import shutil
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        
        print("\n✅ All local database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sync_queue_operations():
    """Test sync queue operations"""
    print("\n" + "="*60)
    print("SYNC QUEUE OPERATIONS TEST")
    print("="*60)
    
    try:
        # Create a test sync queue
        test_queue_path = '/tmp/test_emar_sync_queue.json'
        test_queue = SyncQueue(storage_path=test_queue_path)
        
        # Test 1: Add sync operation
        test_queue.add_sync_operation('patient_info', since_entry_id=0)
        status = test_queue.get_status()
        assert status['pending_count'] > 0, "Should have pending operations"
        print(f"✓ PASS: Added sync operation (pending: {status['pending_count']})")
        
        # Test 2: Get next ready item
        item = test_queue.get_next_ready_item()
        assert item is not None, "Should get a ready item"
        assert item.channel_name == 'patient_info', "Channel name should match"
        print(f"✓ PASS: Retrieved next ready item")
        
        # Test 3: Mark success
        test_queue.mark_success(item, highest_synced_entry_id=5)
        status = test_queue.get_status()
        assert status['last_synced_entry_ids']['patient_info'] == 5, "Should update last synced entry_id"
        print(f"✓ PASS: Mark success updates tracking correctly")
        
        # Test 4: Test retry logic
        test_queue.add_sync_operation('medicine_prescription', since_entry_id=0)
        item = test_queue.get_next_ready_item()
        assert item is not None, "Should get a ready item for retry test"
        test_queue.mark_failure(item, "Test error")
        
        status = test_queue.get_status()
        assert status['stats']['total_retried'] > 0, "Should have retried items"
        print(f"✓ PASS: Retry logic working (retries: {status['stats']['total_retried']})")
        
        # Cleanup
        if os.path.exists(test_queue_path):
            os.remove(test_queue_path)
        
        print("\n✅ All sync queue tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_service():
    """Test hybrid service integration"""
    print("\n" + "="*60)
    print("HYBRID SERVICE INTEGRATION TEST")
    print("="*60)
    
    try:
        # Test 1: Write to hybrid service (should go to local DB)
        patient_data = {
            'patient_id': 'HYBRID001',
            'name': 'Hybrid Test Patient',
            'floor': '2',
            'room': '202',
            'bed': 'B',
            'age': '50',
            'gender': 'F',
            'notes': 'Hybrid test'
        }
        
        entry_id = hybrid_service.write_to_channel('patient_info', patient_data)
        assert entry_id is not None, "Should return entry_id"
        print(f"✓ PASS: Wrote to hybrid service (entry_id: {entry_id})")
        
        # Test 2: Read from hybrid service (should read from local DB)
        patients = hybrid_service.read_channel('patient_info')
        assert len(patients) > 0, "Should have patients"
        
        # Check if our test patient is in the results
        found = any(p.get('patient_id') == 'HYBRID001' for p in patients)
        assert found, "Should find the hybrid test patient"
        print(f"✓ PASS: Read from hybrid service ({len(patients)} records)")
        
        # Test 3: Find by field
        found_patients = hybrid_service.find_by_field('patient_info', 'patient_id', 'HYBRID001')
        assert len(found_patients) > 0, "Should find the patient"
        assert found_patients[0]['name'] == 'Hybrid Test Patient', "Name should match"
        print(f"✓ PASS: Find by field working in hybrid service")
        
        # Test 4: Patient existence check
        exists = hybrid_service.patient_exists('HYBRID001')
        assert exists, "Patient should exist"
        print(f"✓ PASS: Patient existence check working")
        
        print("\n✅ All hybrid service tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bulk_write_format():
    """Test bulk write data format preparation"""
    print("\n" + "="*60)
    print("BULK WRITE FORMAT TEST")
    print("="*60)
    
    try:
        # Create test feeds in ThingSpeak format
        test_feeds = [
            {
                'entry_id': 1,
                'created_at': '2025-11-20T10:00:00Z',
                'field1': 'P001',
                'field2': 'John Doe',
                'field3': '1',
                'field4': '101',
                'field5': 'A',
                'field6': '45',
                'field7': 'M',
                'field8': 'Test notes'
            },
            {
                'entry_id': 2,
                'created_at': '2025-11-20T10:05:00Z',
                'field1': 'P002',
                'field2': 'Jane Smith',
                'field3': '2',
                'field4': '202',
                'field5': 'B',
                'field6': '35',
                'field7': 'F',
                'field8': 'Another test'
            }
        ]
        
        # Test 1: Prepare batches
        batches = thingspeak_bulk_service.prepare_feeds_for_bulk_write(test_feeds, max_batch_size=1)
        assert len(batches) == 2, "Should create 2 batches with max_batch_size=1"
        print(f"✓ PASS: Batch preparation working ({len(batches)} batches)")
        
        # Test 2: Verify batch content
        assert batches[0][0]['field1'] == 'P001', "First batch should have P001"
        assert batches[1][0]['field1'] == 'P002', "Second batch should have P002"
        print(f"✓ PASS: Batch content correct")
        
        # Test 3: Large batch handling
        large_feeds = [{'entry_id': i, 'field1': f'P{i:03d}'} for i in range(1, 251)]
        batches = thingspeak_bulk_service.prepare_feeds_for_bulk_write(large_feeds, max_batch_size=100)
        assert len(batches) == 3, "Should create 3 batches for 250 items"
        assert len(batches[0]) == 100, "First batch should have 100 items"
        assert len(batches[2]) == 50, "Third batch should have 50 items"
        print(f"✓ PASS: Large batch handling working correctly")
        
        print("\n✅ All bulk write format tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LOCAL DATABASE AND SYNC INTEGRATION TEST SUITE")
    print("Electronic Medication Administration Record (eMAR)")
    print("="*60)
    
    tests = [
        ("Local Database Operations", test_local_database_operations),
        ("Sync Queue Operations", test_sync_queue_operations),
        ("Hybrid Service Integration", test_hybrid_service),
        ("Bulk Write Format", test_bulk_write_format)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n✗ FAIL: {test_name} - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
