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
        track_date = str(t.get("consume_date", "")).split("T")[0] if t.get("consume_date") else None
        if track_date != today:
            continue
        
        # Check patient and medicine match
        if t.get("patient_id") != prescription.get("patient_id") or \
           t.get("medicine_name") != prescription.get("medicine_name"):
            continue
        
        # Check if tracking time slot matches any of the slots to check
        track_slot = str(t.get("time_slot", "")).strip()
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
    
    if result == expected:
        print(f"✓ Single slot prescription correctly matched")
        print(f"  Prescription slot: {prescription['time_slot']}")
        print(f"  Tracking slot: {tracking[0]['time_slot']}")
        print(f"  Result: {result}")
        return True
    else:
        print(f"✗ Single slot prescription failed")
        print(f"  Expected: {expected}, Got: {result}")
        return False


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
    
    passed = True
    
    if result_any == expected_any:
        print(f"✓ Any slot check: {result_any}")
    else:
        print(f"✗ Any slot check failed: Expected {expected_any}, Got {result_any}")
        passed = False
    
    if result_09 == expected_09:
        print(f"✓ Specific slot 09:00 check: {result_09}")
    else:
        print(f"✗ Specific slot 09:00 check failed: Expected {expected_09}, Got {result_09}")
        passed = False
    
    if result_13 == expected_13:
        print(f"✓ Specific slot 13:00 check: {result_13}")
    else:
        print(f"✗ Specific slot 13:00 check failed: Expected {expected_13}, Got {result_13}")
        passed = False
    
    return passed


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
    
    passed = True
    
    if result_09 == expected_09:
        print(f"✓ Slot 09:00 check: {result_09}")
    else:
        print(f"✗ Slot 09:00 check failed: Expected {expected_09}, Got {result_09}")
        passed = False
    
    if result_13 == expected_13:
        print(f"✓ Slot 13:00 check: {result_13}")
    else:
        print(f"✗ Slot 13:00 check failed: Expected {expected_13}, Got {result_13}")
        passed = False
    
    if result_17 == expected_17:
        print(f"✓ Slot 17:00 check: {result_17}")
    else:
        print(f"✗ Slot 17:00 check failed: Expected {expected_17}, Got {result_17}")
        passed = False
    
    return passed


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
    
    if result == expected:
        print(f"✓ Different patient correctly not matched")
        return True
    else:
        print(f"✗ Different patient check failed: Expected {expected}, Got {result}")
        return False


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
    
    if result == expected:
        print(f"✓ Different medicine correctly not matched")
        return True
    else:
        print(f"✗ Different medicine check failed: Expected {expected}, Got {result}")
        return False


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
    
    if result == expected:
        print(f"✓ Different date correctly not matched")
        print(f"  Today: {today}, Tracking date: {yesterday}")
        return True
    else:
        print(f"✗ Different date check failed: Expected {expected}, Got {result}")
        return False


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("DASHBOARD MEDICATION STATUS DISPLAY TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    # Run individual test suites
    if not test_single_slot_prescription():
        all_passed = False
    
    if not test_multiple_slot_prescription_first_slot():
        all_passed = False
    
    if not test_multiple_slot_prescription_middle_slot():
        all_passed = False
    
    if not test_different_patient_no_match():
        all_passed = False
    
    if not test_different_medicine_no_match():
        all_passed = False
    
    if not test_different_date_no_match():
        all_passed = False
    
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
