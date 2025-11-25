"""
Test suite for medication status calculator.

Tests the logic that determines if a medication was administered
within the correct time slot window.
"""

import sys
from datetime import datetime
from utils.status_calculator import calculate_status, is_time_within_slot, parse_time_from_string


def test_parse_time_from_string():
    """Test time parsing from various formats"""
    print("\n" + "="*60)
    print("TIME PARSING TESTS")
    print("="*60)
    
    test_cases = [
        ("09:00", True, "9:00 AM"),
        ("9:00", True, "9:00 AM"),
        ("17:00", True, "5:00 PM"),
        ("21:00", True, "9:00 PM"),
        ("9AM", True, "9:00 AM"),
        ("9PM", True, "9:00 PM"),
        ("invalid", False, None),
        ("", False, None),
    ]
    
    passed = 0
    failed = 0
    
    for time_str, should_parse, expected_desc in test_cases:
        result = parse_time_from_string(time_str)
        if should_parse and result is not None:
            print(f"✓ Successfully parsed '{time_str}' -> {result}")
            passed += 1
        elif not should_parse and result is None:
            print(f"✓ Correctly rejected '{time_str}'")
            passed += 1
        else:
            print(f"✗ Failed to parse '{time_str}' correctly (got: {result})")
            failed += 1
    
    print(f"\nParsing tests: {passed} passed, {failed} failed")
    assert failed == 0, f"Parsing tests had {failed} failures"



def test_is_time_within_slot():
    """Test time slot matching logic"""
    print("\n" + "="*60)
    print("TIME SLOT MATCHING TESTS")
    print("="*60)
    
    test_cases = [
        # (consume_datetime, time_slot, expected_result, description)
        (datetime(2025, 11, 13, 17, 16), "09:00, 13:00, 17:00, 21:00", True, "17:16 matches 17:00 slot"),
        (datetime(2025, 11, 13, 17, 0), "09:00, 13:00, 17:00, 21:00", True, "17:00 exactly matches 17:00 slot"),
        (datetime(2025, 11, 13, 17, 29), "09:00, 13:00, 17:00, 21:00", True, "17:29 between 17:00 and 21:00 slot starts"),
        (datetime(2025, 11, 13, 16, 31), "09:00, 13:00, 17:00, 21:00", True, "16:31 between 13:00 and 17:00 slots"),
        (datetime(2025, 11, 13, 18, 0), "09:00, 13:00, 17:00, 21:00", True, "18:00 between 17:00 and 21:00 slots"),
        (datetime(2025, 11, 13, 14, 30), "09:00, 13:00, 17:00, 21:00", True, "14:30 between 13:00 and 17:00 slots"),
        (datetime(2025, 11, 13, 9, 15), "09:00, 13:00, 17:00, 21:00", True, "9:15 matches 09:00 slot"),
        (datetime(2025, 11, 13, 21, 10), "09:00, 13:00, 17:00, 21:00", True, "21:10 matches 21:00 slot"),
        (datetime(2025, 11, 13, 8, 0), "09:00, 13:00, 17:00, 21:00", False, "8:00 before the first slot"),
    ]
    
    passed = 0
    failed = 0
    
    for consume_dt, time_slot, expected, description in test_cases:
        result = is_time_within_slot(consume_dt, time_slot)
        if result == expected:
            print(f"✓ {description}: {result}")
            passed += 1
        else:
            print(f"✗ {description}: expected {expected}, got {result}")
            failed += 1
    
    print(f"\nMatching tests: {passed} passed, {failed} failed")
    assert failed == 0, f"Matching tests had {failed} failures"



def test_calculate_status():
    """Test status calculation based on consume date and time slot"""
    print("\n" + "="*60)
    print("STATUS CALCULATION TESTS")
    print("="*60)
    
    test_cases = [
        # (consume_date, time_slot, expected_status, description)
        ("2025-11-13 17:16:27", "09:00, 13:00, 17:00, 21:00", "complete", "Within 17:00 slot"),
        ("2025-11-13 17:00:00", "09:00, 13:00, 17:00, 21:00", "complete", "Exactly at 17:00"),
        ("2025-11-13 17:29:00", "09:00, 13:00, 17:00, 21:00", "complete", "Between 17:00 and 21:00 slots"),
        ("2025-11-13 18:00:00", "09:00, 13:00, 17:00, 21:00", "complete", "Between 17:00 and 21:00 slots"),
        ("2025-11-13 14:30:00", "09:00, 13:00, 17:00, 21:00", "complete", "Between 13:00 and 17:00 slots"),
        ("2025-11-13 09:15:00", "09:00, 13:00, 17:00, 21:00", "complete", "Within 09:00 slot"),
        ("2025-11-13 13:10:00", "09:00, 13:00, 17:00, 21:00", "complete", "Within 13:00 slot"),
        ("2025-11-13 21:00:00", "09:00, 13:00, 17:00, 21:00", "complete", "Within 21:00 slot"),
        ("2025-11-13", "09:00, 13:00, 17:00, 21:00", "pending", "Date only (midnight)"),
    ]
    
    passed = 0
    failed = 0
    
    for consume_date, time_slot, expected_status, description in test_cases:
        result = calculate_status(consume_date, time_slot)
        if result == expected_status:
            print(f"✓ {description}: '{result}'")
            passed += 1
        else:
            print(f"✗ {description}: expected '{expected_status}', got '{result}'")
            failed += 1
    
    print(f"\nStatus tests: {passed} passed, {failed} failed")
    assert failed == 0, f"Status tests had {failed} failures"



def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("MEDICATION STATUS CALCULATOR TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    # Run individual test suites
    if not test_parse_time_from_string():
        all_passed = False
    
    if not test_is_time_within_slot():
        all_passed = False
    
    if not test_calculate_status():
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
