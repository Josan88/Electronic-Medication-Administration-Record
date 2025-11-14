"""
Integration test for medication tracking with status calculation.

This test verifies that the status is correctly calculated based on
consume_date and time_slot when reading tracking records.
"""

import sys
from validators import validate_tracking_data
from utils.status_calculator import calculate_status


def test_tracking_status_calculation():
    """Test that status is correctly calculated for tracking records"""
    print("\n" + "="*60)
    print("TRACKING STATUS CALCULATION INTEGRATION TEST")
    print("="*60)
    
    test_cases = [
        {
            "name": "Complete - time within slot",
            "data": {
                "patient_id": "P001",
                "medicine_name": "Metformin",
                "dosage": "500mg",
                "consume_date": "2025-11-13 17:16:27",
                "time_slot": "09:00, 13:00, 17:00, 21:00"
            },
            "expected_status": "complete"
        },
        {
            "name": "Complete - exact time match",
            "data": {
                "patient_id": "P001",
                "medicine_name": "Aspirin",
                "dosage": "100mg",
                "consume_date": "2025-11-13 09:00:00",
                "time_slot": "09:00, 13:00, 17:00, 21:00"
            },
            "expected_status": "complete"
        },
        {
            "name": "Pending - time between slots",
            "data": {
                "patient_id": "P001",
                "medicine_name": "Lisinopril",
                "dosage": "10mg",
                "consume_date": "2025-11-13 14:30:00",
                "time_slot": "09:00, 13:00, 17:00, 21:00"
            },
            "expected_status": "pending"
        },
        {
            "name": "Pending - time too far from slot",
            "data": {
                "patient_id": "P001",
                "medicine_name": "Atorvastatin",
                "dosage": "20mg",
                "consume_date": "2025-11-13 18:00:00",
                "time_slot": "09:00, 13:00, 17:00, 21:00"
            },
            "expected_status": "pending"
        },
        {
            "name": "Complete - within morning slot",
            "data": {
                "patient_id": "P002",
                "medicine_name": "Insulin",
                "dosage": "10 units",
                "consume_date": "2025-11-13 09:15:00",
                "time_slot": "09:00, 13:00, 17:00, 21:00"
            },
            "expected_status": "complete"
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            # Validate the data (this doesn't compute status, just validates)
            validated_data = validate_tracking_data(test_case["data"], check_patient=False)
            
            # Compute status using the same logic as thingspeak_service
            actual_status = calculate_status(
                validated_data["consume_date"],
                validated_data["time_slot"]
            )
            expected_status = test_case["expected_status"]
            
            if actual_status == expected_status:
                print(f"✓ {test_case['name']}")
                print(f"  Data: {test_case['data']['consume_date']} @ {test_case['data']['time_slot']}")
                print(f"  Status: {actual_status}")
                passed += 1
            else:
                print(f"✗ {test_case['name']}")
                print(f"  Expected: {expected_status}, Got: {actual_status}")
                failed += 1
        except Exception as e:
            print(f"✗ {test_case['name']}")
            print(f"  Error: {str(e)}")
            failed += 1
            print(f"  Error: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Integration tests: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("MEDICATION TRACKING STATUS - INTEGRATION TEST SUITE")
    print("="*60)
    
    success = test_tracking_status_calculation()
    
    if success:
        print("\n✓ ALL INTEGRATION TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME INTEGRATION TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
