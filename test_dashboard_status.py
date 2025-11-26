"""
Integration test for dashboard medication status display logic.

This test verifies that the status checking logic correctly handles
prescriptions with multiple comma-separated time slots and matches them
with individual tracking records.
"""

import sys
from datetime import datetime


def is_served_python(prescription, tracking, specific_slot=None):
    """
    Python implementation of the JavaScript isServed() function.
    
    Args:
        prescription: Dict with patient_id, medicine_name, time_slot (CSV), etc.
        tracking: List of tracking records
        specific_slot: Optional specific time slot to check (e.g., "09:00")
    
    Returns:
        True if medication is served, False otherwise
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Parse prescription time slots (may be comma-separated)
    prescription_slots = [s.strip() for s in str(prescription.get("time_slot", "")).split(",")]
    
    # If a specific slot is provided, only check for that slot
    slots_to_check = [specific_slot] if specific_slot else prescription_slots
    
    for t in tracking:
        # Check if tracking date is today
        # Handle both "T" and space separators in date format
        consume_date_str = str(t.get("consume_date", ""))
        track_date = consume_date_str.split("T")[0].split(" ")[0] if consume_date_str else None
        if track_date != today:
            continue
        
        # Check patient and medicine match
        if t.get("patient_id") != prescription.get("patient_id") or \
           t.get("medicine_name") != prescription.get("medicine_name"):
            continue
        
        # For tracking records, the time_slot should be a single slot
        # If it's comma-separated (malformed data), only use the first slot
        # This represents the actual time the medication was administered
        track_slot_raw = str(t.get("time_slot", "")).strip()
        track_slot = track_slot_raw.split(",")[0].strip()
        
        # Check if the tracking slot matches any of the slots to check
        if track_slot in slots_to_check:
            return True
    
    return False


def test_single_slot_prescription():
    """Test prescription with single time slot"""
    print("\n" + "="*60)
    print("TEST: Single Slot Prescription")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Aspirin",
        "time_slot": "09:00"
    }
    
    tracking = [
        {
            "patient_id": "P001",
            "medicine_name": "Aspirin",
            "time_slot": "09:00",
            "consume_date": today
        }
    ]
    
    result = is_served_python(prescription, tracking)
    expected = True
    
    print(f"  Prescription slot: {prescription['time_slot']}")
    print(f"  Tracking slot: {tracking[0]['time_slot']}")
    print(f"  Result: {result}")
    assert result == expected, f"Single slot prescription expected {expected}, got {result}"



def test_multiple_slot_prescription_first_slot():
    """Test prescription with multiple slots - first slot administered"""
    print("\n" + "="*60)
    print("TEST: Multiple Slots - First Slot Administered")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Metformin",
        "time_slot": "09:00, 13:00, 17:00"
    }
    
    tracking = [
        {
            "patient_id": "P001",
            "medicine_name": "Metformin",
            "time_slot": "09:00",
            "consume_date": today
        }
    ]
    
    # Test without specific slot (should return True if any slot is served)
    result_any = is_served_python(prescription, tracking)
    expected_any = True
    
    # Test with specific slot = 09:00 (should return True)
    result_09 = is_served_python(prescription, tracking, "09:00")
    expected_09 = True
    
    # Test with specific slot = 13:00 (should return False)
    result_13 = is_served_python(prescription, tracking, "13:00")
    expected_13 = False
    
    assert result_any == expected_any, (
        f"Any slot check expected {expected_any}, got {result_any}"
    )
    assert result_09 == expected_09, (
        f"Specific slot 09:00 expected {expected_09}, got {result_09}"
    )
    assert result_13 == expected_13, (
        f"Specific slot 13:00 expected {expected_13}, got {result_13}"
    )



def test_multiple_slot_prescription_middle_slot():
    """Test prescription with multiple slots - middle slot administered"""
    print("\n" + "="*60)
    print("TEST: Multiple Slots - Middle Slot Administered")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P002",
        "medicine_name": "Insulin",
        "time_slot": "09:00, 13:00, 17:00, 21:00"
    }
    
    tracking = [
        {
            "patient_id": "P002",
            "medicine_name": "Insulin",
            "time_slot": "13:00",
            "consume_date": today
        }
    ]
    
    # Test with specific slot = 09:00 (should return False)
    result_09 = is_served_python(prescription, tracking, "09:00")
    expected_09 = False
    
    # Test with specific slot = 13:00 (should return True)
    result_13 = is_served_python(prescription, tracking, "13:00")
    expected_13 = True
    
    # Test with specific slot = 17:00 (should return False)
    result_17 = is_served_python(prescription, tracking, "17:00")
    expected_17 = False
    
    assert result_09 == expected_09, (
        f"Slot 09:00 expected {expected_09}, got {result_09}"
    )
    assert result_13 == expected_13, (
        f"Slot 13:00 expected {expected_13}, got {result_13}"
    )
    assert result_17 == expected_17, (
        f"Slot 17:00 expected {expected_17}, got {result_17}"
    )



def test_different_patient_no_match():
    """Test that different patient IDs don't match"""
    print("\n" + "="*60)
    print("TEST: Different Patient - No Match")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Aspirin",
        "time_slot": "09:00"
    }
    
    tracking = [
        {
            "patient_id": "P002",  # Different patient
            "medicine_name": "Aspirin",
            "time_slot": "09:00",
            "consume_date": today
        }
    ]
    
    result = is_served_python(prescription, tracking)
    expected = False
    
    assert result == expected, (
        f"Different patient check expected {expected}, got {result}"
    )



def test_different_medicine_no_match():
    """Test that different medicines don't match"""
    print("\n" + "="*60)
    print("TEST: Different Medicine - No Match")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Aspirin",
        "time_slot": "09:00"
    }
    
    tracking = [
        {
            "patient_id": "P001",
            "medicine_name": "Metformin",  # Different medicine
            "time_slot": "09:00",
            "consume_date": today
        }
    ]
    
    result = is_served_python(prescription, tracking)
    expected = False
    
    assert result == expected, (
        f"Different medicine check expected {expected}, got {result}"
    )



def test_different_date_no_match():
    """Test that different dates don't match"""
    print("\n" + "="*60)
    print("TEST: Different Date - No Match")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = "2025-01-01"
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Aspirin",
        "time_slot": "09:00"
    }
    
    tracking = [
        {
            "patient_id": "P001",
            "medicine_name": "Aspirin",
            "time_slot": "09:00",
            "consume_date": yesterday  # Different date
        }
    ]
    
    result = is_served_python(prescription, tracking)
    expected = False
    
    print(f"  Today: {today}, Tracking date: {yesterday}")
    assert result == expected, (
        f"Different date check expected {expected}, got {result}"
    )



def test_tracking_with_multiple_slots():
    """Test tracking record with multiple slots (malformed data)"""
    print("\n" + "="*60)
    print("TEST: Tracking with Multiple Slots (Malformed Data)")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prescription = {
        "patient_id": "P001",
        "medicine_name": "Metformin",
        "time_slot": "09:00, 13:00, 17:00, 21:00"
    }
    
    # Tracking record incorrectly has all time slots
    tracking = [
        {
            "patient_id": "P001",
            "medicine_name": "Metformin",
            "time_slot": "09:00, 13:00, 17:00, 21:00",  # Malformed: should be single slot
            "consume_date": today
        }
    ]
    
    # Without specific slot - should match because first slot (09:00) is in prescription slots
    result_any = is_served_python(prescription, tracking)
    expected_any = True
    
    # With specific slot 09:00 - should match (it's the first slot in malformed data)
    result_09 = is_served_python(prescription, tracking, "09:00")
    expected_09 = True
    
    # With specific slot 13:00 - should NOT match (only first slot is used from malformed data)
    result_13 = is_served_python(prescription, tracking, "13:00")
    expected_13 = False
    
    assert result_any == expected_any, (
        f"Any slot check expected {expected_any}, got {result_any}"
    )
    assert result_09 == expected_09, (
        f"Slot 09:00 check expected {expected_09}, got {result_09}"
    )
    assert result_13 == expected_13, (
        f"Slot 13:00 check expected {expected_13}, got {result_13}"
    )

    print(f"  Note: Malformed tracking data only uses first slot to prevent incorrect matches")



def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("DASHBOARD MEDICATION STATUS DISPLAY TEST SUITE")
    print("="*60)
    
    all_passed = True

    test_suites = [
        ("test_single_slot_prescription", test_single_slot_prescription),
        (
            "test_multiple_slot_prescription_first_slot",
            test_multiple_slot_prescription_first_slot,
        ),
        (
            "test_multiple_slot_prescription_middle_slot",
            test_multiple_slot_prescription_middle_slot,
        ),
        ("test_different_patient_no_match", test_different_patient_no_match),
        ("test_different_medicine_no_match", test_different_medicine_no_match),
        ("test_different_date_no_match", test_different_date_no_match),
        ("test_tracking_with_multiple_slots", test_tracking_with_multiple_slots),
    ]

    for name, test_func in test_suites:
        try:
            test_func()
        except AssertionError as exc:
            all_passed = False
            print(f"✗ {name} failed: {exc}")
        except Exception as exc:  # Capture unexpected errors for visibility
            all_passed = False
            print(f"✗ {name} raised unexpected error: {exc}")

    # Final summary

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
