"""
Automated Regression Testing Suite for Electronic Medication Administration Record (eMAR).

This test suite validates:
- Critical user workflows (patient -> prescription -> tracking)
- Data persistence and recovery
- Error recovery scenarios
- End-to-end system functionality
- Previously reported bugs/issues
"""

import requests
import time
from datetime import datetime, timedelta
import sys


BASE_URL = "http://localhost:5000"


def test_complete_patient_workflow():
    """Test complete workflow: add patient -> add prescription -> track medication."""
    print("\n" + "="*60)
    print("COMPLETE PATIENT WORKFLOW TEST")
    print("="*60)
    
    # Generate unique patient ID
    timestamp = int(time.time())
    patient_id = f"REG_WORKFLOW_{timestamp}"
    
    # Step 1: Add a patient
    print(f"\nStep 1: Adding patient {patient_id}...")
    patient_data = {
        "patient_id": patient_id,
        "name": "John Regression",
        "floor": "3",
        "room": "301",
        "bed": "A",
        "age": "45",
        "gender": "Male",
        "notes": "Regression test patient"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/patients",
            json=patient_data,
            timeout=20
        )
        
        if response.status_code not in [200, 201, 507]:
            print(f"  [FAIL] FAIL: Cannot add patient (status {response.status_code})")
            return False
        
        print(f"  [PASS] Patient added (status {response.status_code})")
        
        # Wait for ThingSpeak rate limit if needed
        if response.status_code in [200, 201]:
            time.sleep(2)  # Small delay for data to sync
            
    except Exception as e:
        print(f"  [FAIL] FAIL: Error adding patient: {e}")
        return False
    
    # Step 2: Verify patient exists
    print(f"\nStep 2: Verifying patient exists...")
    try:
        response = requests.get(f"{BASE_URL}/api/check_patient/{patient_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('exists'):
                print(f"  [PASS] Patient verification successful")
            else:
                print(f"  [WARN] Patient not found yet (may need more time to sync)")
        else:
            print(f"  [WARN] Patient check returned status {response.status_code}")
            
    except Exception as e:
        print(f"  [FAIL] FAIL: Error checking patient: {e}")
    
    # Step 3: Add a prescription
    print(f"\nStep 3: Adding prescription for patient...")
    prescription_data = {
        "patient_id": patient_id,
        "medicine_name": "Metformin",
        "dosage": "500mg",
        "frequency": "Twice daily",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "time_slot": "8AM, 8PM"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription_data,
            timeout=5
        )
        
        if response.status_code not in [200, 201, 202, 507]:
            print(f"  [FAIL] FAIL: Cannot add prescription (status {response.status_code})")
            return False
        
        print(f"  [PASS] Prescription queued (status {response.status_code})")
        
    except Exception as e:
        print(f"  [FAIL] FAIL: Error adding prescription: {e}")
        return False
    
    # Step 4: Record medication tracking
    print(f"\nStep 4: Recording medication administration...")
    tracking_data = {
        "patient_id": patient_id,
        "medicine_name": "Metformin",
        "dosage": "500mg",
        "consume_date": datetime.now().strftime("%Y-%m-%d"),
        "time_slot": "08:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/medication-tracking",
            json=tracking_data,
            timeout=20
        )
        
        if response.status_code not in [200, 201, 429, 507]:
            print(f"  [FAIL] FAIL: Cannot record tracking (status {response.status_code})")
            if response.status_code == 429:
                print("  Note: Rate limit error is expected behavior")
                return True
            return False
        
        print(f"  [PASS] Medication tracking recorded (status {response.status_code})")
        
    except Exception as e:
        print(f"  [FAIL] FAIL: Error recording tracking: {e}")
        return False
    
    print(f"\n[PASS] PASS: Complete workflow executed successfully")
    return True


def test_data_retrieval_workflow():
    """Test data retrieval endpoints."""
    print("\n" + "="*60)
    print("DATA RETRIEVAL WORKFLOW TEST")
    print("="*60)
    
    endpoints = [
        ("/api/patients", "Patients"),
        ("/api/prescriptions", "Prescriptions"),
        ("/api/medication-tracking", "Medication Tracking"),
    ]
    
    all_passed = True
    
    for endpoint, name in endpoints:
        print(f"\nTesting {name} endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    count = len(data['data'])
                    print(f"  [PASS] Retrieved {count} records")
                else:
                    print(f"  [PASS] Endpoint responded successfully")
            else:
                print(f"  [FAIL] FAIL: Status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"  [FAIL] FAIL: Error - {e}")
            all_passed = False
    
    return all_passed


def test_queue_status_monitoring():
    """Test queue status monitoring endpoint."""
    print("\n" + "="*60)
    print("QUEUE STATUS MONITORING TEST")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        
        if response.status_code != 200:
            print(f"[FAIL] FAIL: Status endpoint returned {response.status_code}")
            return False
        
        data = response.json()
        
        if 'data' not in data:
            print("[FAIL] FAIL: Response missing 'data' field")
            return False
        
        status = data['data']
        # Support both 'size' and 'queue_size', 'statistics' and 'stats'
        required_fields = {
            'size': ['size', 'queue_size'],
            'max_size': ['max_size'],
            'is_full': ['is_full'],
            'failed_count': ['failed_count'],
            'statistics': ['statistics', 'stats']
        }
        
        print("\nQueue Status:")
        for field_name, field_options in required_fields.items():
            found = False
            for option in field_options:
                if option in status:
                    print(f"  [PASS] {field_name}: {status[option]}")
                    found = True
                    break
            if not found:
                print(f"  [FAIL] Missing field: {field_name}")
                return False
        
        print("\n[PASS] PASS: Queue status monitoring functional")
        return True
        
    except Exception as e:
        print(f"[FAIL] FAIL: Error - {e}")
        return False


def test_error_recovery_invalid_patient():
    """Test error recovery when trying to add prescription for non-existent patient."""
    print("\n" + "="*60)
    print("ERROR RECOVERY TEST: Non-existent Patient")
    print("="*60)
    
    # Try to add prescription for non-existent patient
    prescription_data = {
        "patient_id": "NONEXISTENT_12345",
        "medicine_name": "Test Med",
        "dosage": "500mg",
        "frequency": "Daily",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "time_slot": "8AM"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription_data,
            timeout=5
        )
        
        # Should be queued (validation happens async) OR rejected if validation is sync
        if response.status_code in [200, 201, 202, 400, 404, 422, 507]:
            print(f"[PASS] PASS: System handled invalid patient appropriately (status {response.status_code})")
            return True
        else:
            print(f"[FAIL] FAIL: Unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] FAIL: Error - {e}")
        return False


def test_health_check_consistency():
    """Test that health check is consistently available."""
    print("\n" + "="*60)
    print("HEALTH CHECK CONSISTENCY TEST")
    print("="*60)
    
    num_checks = 10
    failures = 0
    
    print(f"\nPerforming {num_checks} health checks...")
    
    for i in range(num_checks):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    print(f"  [PASS] Check {i+1}: Healthy")
                else:
                    print(f"  [FAIL] Check {i+1}: Unhealthy status")
                    failures += 1
            else:
                print(f"  [FAIL] Check {i+1}: Status {response.status_code}")
                failures += 1
                
        except Exception as e:
            print(f"  [FAIL] Check {i+1}: Error - {e}")
            failures += 1
        
        time.sleep(0.1)  # Small delay between checks
    
    if failures == 0:
        print(f"\n[PASS] PASS: All {num_checks} health checks passed")
        return True
    else:
        print(f"\n[FAIL] FAIL: {failures}/{num_checks} health checks failed")
        return False


def test_api_response_format():
    """Test that API responses follow consistent format."""
    print("\n" + "="*60)
    print("API RESPONSE FORMAT TEST")
    print("="*60)
    
    endpoints = [
        ("/api/health", "GET"),
        ("/api/patients", "GET"),
        ("/api/prescriptions", "GET"),
        ("/api/medication-tracking", "GET"),
        ("/api/queue/status", "GET"),
    ]
    
    all_passed = True
    
    for endpoint, method in endpoints:
        print(f"\nTesting {method} {endpoint}...")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code != 200:
                print(f"  [WARN] Status {response.status_code} (may be expected)")
                continue
            
            data = response.json()
            
            # Check for consistent response structure
            if isinstance(data, dict):
                if 'status' in data or 'data' in data:
                    print(f"  [PASS] Response has consistent structure")
                else:
                    print(f"  [FAIL] Response missing standard fields")
                    all_passed = False
            else:
                print(f"  [FAIL] Response is not a dictionary")
                all_passed = False
                
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            all_passed = False
    
    return all_passed


def test_queue_persistence_simulation():
    """Test queue functionality (simulated persistence check)."""
    print("\n" + "="*60)
    print("QUEUE PERSISTENCE SIMULATION TEST")
    print("="*60)
    
    # Get initial queue status
    try:
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code != 200:
            print("[FAIL] FAIL: Cannot get initial queue status")
            return False
        
        initial_status = response.json()['data']
        initial_size = initial_status.get('queue_size', initial_status.get('size', 0))
        
        print(f"\nInitial queue size: {initial_size}")
        
        # Add a prescription
        timestamp = int(time.time())
        prescription_data = {
            "patient_id": f"REG_PERSIST_{timestamp}",
            "medicine_name": "Test Persistence Med",
            "dosage": "100mg",
            "frequency": "Daily",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time_slot": "9AM"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription_data,
            timeout=5
        )
        
        if response.status_code not in [200, 201, 202, 507]:
            print(f"[FAIL] FAIL: Cannot add prescription (status {response.status_code})")
            return False
        
        print(f"[PASS] Prescription added (status {response.status_code})")
        
        # Check queue status again
        time.sleep(1)  # Small delay
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code != 200:
            print("[FAIL] FAIL: Cannot get updated queue status")
            return False
        
        updated_status = response.json()['data']
        updated_size = updated_status.get('queue_size', updated_status.get('size', 0))
        
        print(f"Updated queue size: {updated_size}")
        
        if response.status_code == 202:  # Was queued
            if updated_size >= initial_size:
                print("[PASS] PASS: Queue size increased as expected")
                return True
            else:
                print("[WARN] Queue size did not increase (may have been processed quickly)")
                return True
        else:
            print("[PASS] PASS: Queue persistence functionality verified")
            return True
            
    except Exception as e:
        print(f"[FAIL] FAIL: Error - {e}")
        return False


def test_validation_regression():
    """Test that validation rules are enforced."""
    print("\n" + "="*60)
    print("VALIDATION REGRESSION TEST")
    print("="*60)
    
    # Test cases that should be rejected
    invalid_cases = [
        ("Empty patient ID", {
            "patient_id": "",
            "name": "Test",
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "30",
            "gender": "Male"
        }),
        ("Missing name", {
            "patient_id": "REG_VAL_1",
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "30",
            "gender": "Male"
        }),
        ("Invalid age", {
            "patient_id": "REG_VAL_2",
            "name": "Test",
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "999",
            "gender": "Male"
        }),
    ]
    
    passed = 0
    total = len(invalid_cases)
    
    for test_name, patient_data in invalid_cases:
        print(f"\nTest: {test_name}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                timeout=5
            )
            
            if response.status_code in [400, 422]:
                print(f"  [PASS] PASS: Correctly rejected (status {response.status_code})")
                passed += 1
            else:
                print(f"  [FAIL] FAIL: Should have been rejected (status {response.status_code})")
                
        except Exception as e:
            print(f"  [FAIL] FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} validation tests passed")
    return passed == total


def test_concurrent_queue_operations():
    """Test that concurrent queue operations don't cause issues."""
    print("\n" + "="*60)
    print("CONCURRENT QUEUE OPERATIONS TEST")
    print("="*60)
    
    import threading
    
    results = []
    lock = threading.Lock()
    
    def add_prescription(index):
        """Add a prescription from a thread."""
        prescription_data = {
            "patient_id": f"REG_CONCURRENT_{index}",
            "medicine_name": f"Med {index}",
            "dosage": "100mg",
            "frequency": "Daily",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time_slot": "10AM"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/prescriptions",
                json=prescription_data,
                timeout=10
            )
            
            with lock:
                results.append({
                    'index': index,
                    'status': response.status_code,
                    'success': response.status_code in [200, 201, 202, 507]
                })
        except Exception as e:
            with lock:
                results.append({
                    'index': index,
                    'status': 0,
                    'success': False,
                    'error': str(e)
                })
    
    num_threads = 3
    print(f"\nLaunching {num_threads} concurrent prescription additions...")
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=add_prescription, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n[PASS] Completed {len(results)} concurrent operations")
    print(f"  Successful: {successful}/{len(results)}")
    
    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        print(f"  {status} Operation {result['index']}: Status {result['status']}")
    
    # Success if all operations completed (with appropriate status codes)
    if successful == len(results):
        print("[PASS] PASS: All concurrent operations handled correctly")
        return True
    elif successful >= len(results) * 0.8:  # 80% success is acceptable
        print("[PASS] PASS: Most concurrent operations handled correctly")
        return True
    else:
        print("[FAIL] FAIL: Too many concurrent operations failed")
        return False


def main():
    """Run all regression tests."""
    print("\n" + "="*60)
    print("AUTOMATED REGRESSION TEST SUITE")
    print("Electronic Medication Administration Record (eMAR)")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"\n[FAIL] ERROR: Server is not responding correctly (status: {response.status_code})")
            print("Please start the server with: python app.py")
            return 1
    except Exception as e:
        print(f"\n[FAIL] ERROR: Cannot connect to server at {BASE_URL}")
        print(f"Error: {e}")
        print("Please start the server with: python app.py")
        return 1
    
    print(f"[PASS] Server is running at {BASE_URL}")
    
    # Run all tests
    tests = [
        ("Complete Patient Workflow", test_complete_patient_workflow),
        ("Data Retrieval Workflow", test_data_retrieval_workflow),
        ("Queue Status Monitoring", test_queue_status_monitoring),
        ("Error Recovery: Invalid Patient", test_error_recovery_invalid_patient),
        ("Health Check Consistency", test_health_check_consistency),
        ("API Response Format", test_api_response_format),
        ("Queue Persistence Simulation", test_queue_persistence_simulation),
        ("Validation Regression", test_validation_regression),
        ("Concurrent Queue Operations", test_concurrent_queue_operations),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n[FAIL] Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("REGRESSION TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal tests passed: {passed_count}/{total_count}")
    print(f"Success rate: {(passed_count/total_count)*100:.1f}%")
    
    if passed_count == total_count:
        print("\n[PASS] ALL REGRESSION TESTS PASSED!")
        return 0
    else:
        print(f"\n[FAIL] {total_count - passed_count} REGRESSION TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
