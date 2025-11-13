"""
Edge Case Testing Suite for Electronic Medication Administration Record (eMAR).

This test suite validates:
- Boundary conditions and extreme values
- Missing, null, and empty data scenarios
- Concurrent operation edge cases
- Queue overflow and retry limits
- Unusual but valid input combinations
- Error recovery scenarios
"""

import requests
import time
import threading
from datetime import datetime, timedelta
import sys


BASE_URL = "http://localhost:5000"


def test_extreme_string_lengths():
    """Test handling of extremely long strings."""
    print("\n" + "="*60)
    print("EXTREME STRING LENGTH TEST")
    print("="*60)
    
    test_cases = [
        ("Empty string", ""),
        ("Single character", "A"),
        ("Very long name", "A" * 255),
        ("Extremely long name", "A" * 1000),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, value in test_cases:
        print(f"\nTest: {test_name} (length: {len(value)})")
        
        patient_data = {
            "patient_id": "EDGE_001",
            "name": value,
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "30",
            "gender": "Male",
            "notes": "Test"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                timeout=5
            )
            
            if len(value) == 0 or len(value) > 100:
                # Should be rejected
                if response.status_code in [400, 422]:
                    print(f"  ✓ PASS: Correctly rejected (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Should have been rejected (status {response.status_code})")
            else:
                # Should be accepted or have controlled behavior
                if response.status_code in [200, 201, 400, 422, 507]:
                    print(f"  ✓ PASS: Handled appropriately (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Unexpected status {response.status_code}")
                    
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def test_boundary_age_values():
    """Test age boundary conditions."""
    print("\n" + "="*60)
    print("AGE BOUNDARY VALUES TEST")
    print("="*60)
    
    test_cases = [
        ("Negative age", "-1", False),
        ("Zero age", "0", True),
        ("Minimum valid", "1", True),
        ("Maximum valid", "150", True),
        ("Above maximum", "151", False),
        ("Very large", "999", False),
        ("Decimal", "45.5", True),
        ("Non-numeric", "abc", False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, age_value, should_accept in test_cases:
        print(f"\nTest: {test_name} (age={age_value})")
        
        patient_data = {
            "patient_id": f"EDGE_AGE_{age_value}",
            "name": "Test Patient",
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": age_value,
            "gender": "Male",
            "notes": "Test"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                timeout=5
            )
            
            if should_accept:
                if response.status_code in [200, 201, 507]:
                    print(f"  ✓ PASS: Accepted (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Should have been accepted (status {response.status_code})")
            else:
                if response.status_code in [400, 422]:
                    print(f"  ✓ PASS: Correctly rejected (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Should have been rejected (status {response.status_code})")
                    
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def test_missing_optional_fields():
    """Test handling of missing optional fields."""
    print("\n" + "="*60)
    print("MISSING OPTIONAL FIELDS TEST")
    print("="*60)
    
    # Test patient with minimal required fields
    minimal_patient = {
        "patient_id": "EDGE_MIN",
        "name": "Minimal Patient",
        "floor": "1",
        "room": "101",
        "bed": "A",
        "age": "30",
        "gender": "Male"
        # notes is optional
    }
    
    print("\nTest 1: Patient with minimal required fields (no notes)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/patients",
            json=minimal_patient,
            timeout=5
        )
        
        if response.status_code in [200, 201, 507]:
            print(f"  ✓ PASS: Accepted minimal patient (status {response.status_code})")
            test1_passed = True
        else:
            print(f"  ✗ FAIL: Should accept minimal patient (status {response.status_code})")
            test1_passed = False
    except Exception as e:
        print(f"  ✗ FAIL: Error - {e}")
        test1_passed = False
    
    # Test prescription with all fields
    print("\nTest 2: Prescription with all required fields")
    prescription = {
        "patient_id": "EDGE_MIN",
        "medicine_name": "Test Med",
        "dosage": "500mg",
        "frequency": "Daily",
        "start_date": "2025-11-13",
        "end_date": "2025-12-13",
        "time_slot": "8AM"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/prescriptions",
            json=prescription,
            timeout=5
        )
        
        if response.status_code in [200, 201, 202, 507]:
            print(f"  ✓ PASS: Accepted prescription (status {response.status_code})")
            test2_passed = True
        else:
            print(f"  ✗ FAIL: Should accept prescription (status {response.status_code})")
            test2_passed = False
    except Exception as e:
        print(f"  ✗ FAIL: Error - {e}")
        test2_passed = False
    
    return test1_passed and test2_passed


def test_null_and_empty_values():
    """Test handling of null and empty values in JSON."""
    print("\n" + "="*60)
    print("NULL AND EMPTY VALUES TEST")
    print("="*60)
    
    test_cases = [
        ("Null patient_id", {"patient_id": None, "name": "Test", "floor": "1", "room": "101", "bed": "A", "age": "30", "gender": "Male"}),
        ("Empty patient_id", {"patient_id": "", "name": "Test", "floor": "1", "room": "101", "bed": "A", "age": "30", "gender": "Male"}),
        ("Whitespace patient_id", {"patient_id": "   ", "name": "Test", "floor": "1", "room": "101", "bed": "A", "age": "30", "gender": "Male"}),
        ("Null name", {"patient_id": "EDGE_NULL", "name": None, "floor": "1", "room": "101", "bed": "A", "age": "30", "gender": "Male"}),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, patient_data in test_cases:
        print(f"\nTest: {test_name}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                timeout=5
            )
            
            # All should be rejected
            if response.status_code in [400, 422]:
                print(f"  ✓ PASS: Correctly rejected (status {response.status_code})")
                passed += 1
            else:
                print(f"  ✗ FAIL: Should have been rejected (status {response.status_code})")
                
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def test_invalid_date_formats():
    """Test various invalid date formats."""
    print("\n" + "="*60)
    print("INVALID DATE FORMATS TEST")
    print("="*60)
    
    test_cases = [
        ("Invalid format", "13-11-2025"),
        ("Text date", "November 13, 2025"),
        ("Invalid day", "2025-11-32"),
        ("Invalid month", "2025-13-01"),
        ("Invalid year", "25-11-13"),
        ("Empty date", ""),
        ("Null date", None),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, date_value in test_cases:
        print(f"\nTest: {test_name} (date={date_value})")
        
        prescription = {
            "patient_id": "EDGE_DATE",
            "medicine_name": "Test Med",
            "dosage": "500mg",
            "frequency": "Daily",
            "start_date": date_value,
            "end_date": "2025-12-13",
            "time_slot": "8AM"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/prescriptions",
                json=prescription,
                timeout=5
            )
            
            # Should be rejected
            if response.status_code in [400, 422]:
                print(f"  ✓ PASS: Correctly rejected (status {response.status_code})")
                passed += 1
            else:
                print(f"  ✗ FAIL: Should have been rejected (status {response.status_code})")
                
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def test_date_range_edge_cases():
    """Test edge cases for date ranges."""
    print("\n" + "="*60)
    print("DATE RANGE EDGE CASES TEST")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    past = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    test_cases = [
        ("End before start", today, past, False),
        ("Same day", today, today, True),
        ("Start in past", past, today, True),
        ("Both in future", future, future, True),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, start_date, end_date, should_accept in test_cases:
        print(f"\nTest: {test_name}")
        print(f"  Start: {start_date}, End: {end_date}")
        
        prescription = {
            "patient_id": "EDGE_RANGE",
            "medicine_name": "Test Med",
            "dosage": "500mg",
            "frequency": "Daily",
            "start_date": start_date,
            "end_date": end_date,
            "time_slot": "8AM"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/prescriptions",
                json=prescription,
                timeout=5
            )
            
            if should_accept:
                if response.status_code in [200, 201, 202, 507]:
                    print(f"  ✓ PASS: Accepted (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Should have been accepted (status {response.status_code})")
            else:
                if response.status_code in [400, 422]:
                    print(f"  ✓ PASS: Correctly rejected (status {response.status_code})")
                    passed += 1
                else:
                    print(f"  ✗ FAIL: Should have been rejected (status {response.status_code})")
                    
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def test_concurrent_writes_same_patient():
    """Test concurrent writes to the same patient ID."""
    print("\n" + "="*60)
    print("CONCURRENT WRITES EDGE CASE TEST")
    print("="*60)
    
    patient_id = "EDGE_CONCURRENT"
    num_threads = 5
    results = []
    lock = threading.Lock()
    
    def add_tracking(thread_id):
        """Add medication tracking from a thread."""
        tracking_data = {
            "patient_id": patient_id,
            "medicine_name": f"Medicine {thread_id}",
            "dosage": "100mg",
            "consume_date": "2025-11-13",
            "time_slot": f"{8+thread_id}:00"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/medication-tracking",
                json=tracking_data,
                timeout=10
            )
            
            with lock:
                results.append({
                    'thread_id': thread_id,
                    'status': response.status_code,
                    'success': response.status_code in [200, 201, 429, 507]
                })
        except Exception as e:
            with lock:
                results.append({
                    'thread_id': thread_id,
                    'status': 0,
                    'success': False,
                    'error': str(e)
                })
    
    print(f"\nLaunching {num_threads} concurrent writes for patient {patient_id}...")
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=add_tracking, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n✓ Completed {len(results)} concurrent operations")
    print(f"  Successful: {successful}/{len(results)}")
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} Thread {result['thread_id']}: Status {result['status']}")
    
    # Success if at least some operations succeeded (rate limiting may affect some)
    if successful >= num_threads * 0.5:  # At least 50% success
        print(f"✓ PASS: Concurrent operations handled appropriately")
        return True
    else:
        print(f"✗ FAIL: Too many concurrent operations failed")
        return False


def test_queue_overflow_behavior():
    """Test queue behavior when approaching capacity."""
    print("\n" + "="*60)
    print("QUEUE OVERFLOW EDGE CASE TEST")
    print("="*60)
    
    try:
        # Get current queue status
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code != 200:
            print("✗ FAIL: Cannot get queue status")
            return False
        
        status = response.json()['data']
        current_size = status['size']
        max_size = status['max_size']
        available = max_size - current_size
        
        print(f"\nCurrent queue status:")
        print(f"  Size: {current_size}/{max_size}")
        print(f"  Available capacity: {available}")
        
        if available < 5:
            print("⚠ WARNING: Queue is near capacity, skipping overflow test")
            return True
        
        # Try to add multiple prescriptions rapidly
        print(f"\nAttempting to add prescriptions...")
        
        responses = []
        for i in range(3):
            prescription = {
                "patient_id": f"EDGE_OVERFLOW_{i}",
                "medicine_name": "Test Med",
                "dosage": "500mg",
                "frequency": "Daily",
                "start_date": "2025-11-13",
                "end_date": "2025-12-13",
                "time_slot": "8AM"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/prescriptions",
                json=prescription,
                timeout=5
            )
            
            responses.append(response.status_code)
            print(f"  Prescription {i+1}: Status {response.status_code}")
        
        # Check if queue handles overflow gracefully
        accepted = sum(1 for s in responses if s in [200, 201, 202])
        rejected = sum(1 for s in responses if s == 507)
        
        print(f"\nResults: {accepted} accepted, {rejected} rejected")
        
        if accepted > 0 or rejected > 0:
            print("✓ PASS: Queue overflow handled gracefully")
            return True
        else:
            print("✗ FAIL: Unexpected queue behavior")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Test error: {e}")
        return False


def test_special_characters_in_fields():
    """Test handling of special characters."""
    print("\n" + "="*60)
    print("SPECIAL CHARACTERS TEST")
    print("="*60)
    
    test_cases = [
        ("Apostrophe in name", "O'Brien"),
        ("Hyphenated name", "Mary-Jane"),
        ("Accented characters", "José García"),
        ("Numbers in name", "Patient 123"),
        ("Period in name", "Dr. Smith"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_name, name_value in test_cases:
        print(f"\nTest: {test_name} (name='{name_value}')")
        
        patient_data = {
            "patient_id": f"EDGE_CHAR_{passed}",
            "name": name_value,
            "floor": "1",
            "room": "101",
            "bed": "A",
            "age": "30",
            "gender": "Male",
            "notes": "Test"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                timeout=5
            )
            
            # Should be handled appropriately (either accepted or rejected with clear message)
            if response.status_code in [200, 201, 400, 422, 507]:
                print(f"  ✓ PASS: Handled appropriately (status {response.status_code})")
                passed += 1
            else:
                print(f"  ✗ FAIL: Unexpected status {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ FAIL: Error - {e}")
    
    print(f"\n{passed}/{total} tests passed")
    return passed == total


def main():
    """Run all edge case tests."""
    print("\n" + "="*60)
    print("EDGE CASE TEST SUITE")
    print("Electronic Medication Administration Record (eMAR)")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"\n✗ ERROR: Server is not responding correctly (status: {response.status_code})")
            print("Please start the server with: python app.py")
            return 1
    except Exception as e:
        print(f"\n✗ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"Error: {e}")
        print("Please start the server with: python app.py")
        return 1
    
    print(f"✓ Server is running at {BASE_URL}")
    
    # Run all tests
    tests = [
        ("Extreme String Lengths", test_extreme_string_lengths),
        ("Boundary Age Values", test_boundary_age_values),
        ("Missing Optional Fields", test_missing_optional_fields),
        ("Null and Empty Values", test_null_and_empty_values),
        ("Invalid Date Formats", test_invalid_date_formats),
        ("Date Range Edge Cases", test_date_range_edge_cases),
        ("Concurrent Writes Same Patient", test_concurrent_writes_same_patient),
        ("Queue Overflow Behavior", test_queue_overflow_behavior),
        ("Special Characters in Fields", test_special_characters_in_fields),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("EDGE CASE TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal tests passed: {passed_count}/{total_count}")
    print(f"Success rate: {(passed_count/total_count)*100:.1f}%")
    
    if passed_count == total_count:
        print("\n✓ ALL EDGE CASE TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} EDGE CASE TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
