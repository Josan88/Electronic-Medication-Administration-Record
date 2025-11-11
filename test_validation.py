"""
Test suite for input validation in Electronic Medication Administration Record (eMAR).

This test suite validates that the input validation layer properly:
- Accepts valid data
- Rejects invalid data with meaningful error messages
- Sanitizes inputs to prevent XSS attacks
- Validates data constraints and formats
"""

import sys
import time
from datetime import datetime


def test_patient_validation():
    """Test patient data validation"""
    print("\n" + "="*60)
    print("PATIENT VALIDATION TESTS")
    print("="*60)
    
    from validators import validate_patient_data
    from utils.errors import ValidationError
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Valid patient data
    tests_total += 1
    print("\nTest 1: Valid patient data")
    try:
        valid_patient = {
            'patient_id': 'P001',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Male',
            'notes': 'Diabetic patient'
        }
        result = validate_patient_data(valid_patient)
        print(f"✓ PASS: Valid patient accepted - {result['patient_id']}, {result['name']}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 2: Missing required field (name)
    tests_total += 1
    print("\nTest 2: Missing required field (name)")
    try:
        invalid_patient = {
            'patient_id': 'P002',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Male'
        }
        result = validate_patient_data(invalid_patient)
        print("✗ FAIL: Should have rejected missing name")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 3: Invalid patient ID (special characters)
    tests_total += 1
    print("\nTest 3: Invalid patient ID format")
    try:
        invalid_patient = {
            'patient_id': 'P@001!',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Male',
            'notes': ''
        }
        result = validate_patient_data(invalid_patient)
        print("✗ FAIL: Should have rejected invalid patient ID")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 4: XSS attempt in name
    tests_total += 1
    print("\nTest 4: XSS prevention in name")
    try:
        xss_patient = {
            'patient_id': 'P003',
            'name': 'John<script>alert("xss")</script>Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Male',
            'notes': 'Test'
        }
        result = validate_patient_data(xss_patient)
        print("✗ FAIL: XSS attempt not properly rejected")
    except ValidationError as e:
        print(f"✓ PASS: XSS rejected - {e}")
        tests_passed += 1
    
    # Test 5: Invalid age (out of range)
    tests_total += 1
    print("\nTest 5: Invalid age (out of range)")
    try:
        invalid_patient = {
            'patient_id': 'P004',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '200',
            'gender': 'Male',
            'notes': ''
        }
        result = validate_patient_data(invalid_patient)
        print("✗ FAIL: Should have rejected invalid age")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 6: Invalid age (non-numeric)
    tests_total += 1
    print("\nTest 6: Invalid age (non-numeric)")
    try:
        invalid_patient = {
            'patient_id': 'P005',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': 'forty-five',
            'gender': 'Male',
            'notes': ''
        }
        result = validate_patient_data(invalid_patient)
        print("✗ FAIL: Should have rejected non-numeric age")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 7: Invalid gender
    tests_total += 1
    print("\nTest 7: Invalid gender")
    try:
        invalid_patient = {
            'patient_id': 'P006',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Unknown',
            'notes': ''
        }
        result = validate_patient_data(invalid_patient)
        print("✗ FAIL: Should have rejected invalid gender")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 8: XSS in notes (should be sanitized, not rejected)
    tests_total += 1
    print("\nTest 8: XSS sanitization in notes")
    try:
        xss_patient = {
            'patient_id': 'P007',
            'name': 'John Doe',
            'floor': '3',
            'room': '301',
            'bed': 'A',
            'age': '45',
            'gender': 'Male',
            'notes': 'Patient has <script>alert("xss")</script> condition'
        }
        result = validate_patient_data(xss_patient)
        # Check if HTML entities are escaped
        if '&lt;' in result['notes'] or '<script>' not in result['notes']:
            print(f"✓ PASS: XSS sanitized in notes - {result['notes']}")
            tests_passed += 1
        else:
            print(f"✗ FAIL: XSS not properly sanitized - {result['notes']}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    print(f"\nPatient Validation: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


def test_prescription_validation():
    """Test prescription data validation"""
    print("\n" + "="*60)
    print("PRESCRIPTION VALIDATION TESTS")
    print("="*60)
    
    from validators import validate_prescription_data
    from utils.errors import ValidationError
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Valid prescription data
    tests_total += 1
    print("\nTest 1: Valid prescription data")
    try:
        valid_prescription = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '2025-10-30',
            'end_date': '2025-11-30',
            'time_slot': '8AM, 8PM'
        }
        result = validate_prescription_data(valid_prescription, check_patient=False)
        print(f"✓ PASS: Valid prescription accepted - {result['medicine_name']}, {result['dosage']}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 2: Missing required field
    tests_total += 1
    print("\nTest 2: Missing required field (medicine_name)")
    try:
        invalid_prescription = {
            'patient_id': 'P001',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '2025-10-30',
            'end_date': '2025-11-30',
            'time_slot': '8AM'
        }
        result = validate_prescription_data(invalid_prescription, check_patient=False)
        print("✗ FAIL: Should have rejected missing medicine_name")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 3: Invalid date format
    tests_total += 1
    print("\nTest 3: Invalid date format")
    try:
        invalid_prescription = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '30-10-2025',
            'end_date': '2025-11-30',
            'time_slot': '8AM'
        }
        result = validate_prescription_data(invalid_prescription, check_patient=False)
        print("✗ FAIL: Should have rejected invalid date format")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 4: Invalid date range (end before start)
    tests_total += 1
    print("\nTest 4: Invalid date range (end before start)")
    try:
        invalid_prescription = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '2025-11-30',
            'end_date': '2025-10-30',
            'time_slot': '8AM'
        }
        result = validate_prescription_data(invalid_prescription, check_patient=False)
        print("✗ FAIL: Should have rejected invalid date range")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 5: XSS in medicine name
    tests_total += 1
    print("\nTest 5: XSS prevention in medicine name")
    try:
        xss_prescription = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin<script>alert("xss")</script>',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '2025-10-30',
            'end_date': '2025-11-30',
            'time_slot': '8AM'
        }
        result = validate_prescription_data(xss_prescription, check_patient=False)
        print("✗ FAIL: XSS attempt not properly rejected")
    except ValidationError as e:
        print(f"✓ PASS: XSS rejected - {e}")
        tests_passed += 1
    
    # Test 6: Valid alternative date format
    tests_total += 1
    print("\nTest 6: Valid alternative date format (DD/MM/YYYY)")
    try:
        valid_prescription = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': '30/10/2025',
            'end_date': '30/11/2025',
            'time_slot': '8AM'
        }
        result = validate_prescription_data(valid_prescription, check_patient=False)
        print(f"✓ PASS: Alternative date format accepted - {result['start_date']}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    print(f"\nPrescription Validation: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


def test_tracking_validation():
    """Test medication tracking data validation"""
    print("\n" + "="*60)
    print("MEDICATION TRACKING VALIDATION TESTS")
    print("="*60)
    
    from validators import validate_tracking_data
    from utils.errors import ValidationError
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Valid tracking data
    tests_total += 1
    print("\nTest 1: Valid tracking data")
    try:
        valid_tracking = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'consume_date': '2025-10-30',
            'time_slot': '08:00'
        }
        result = validate_tracking_data(valid_tracking, check_patient=False)
        print(f"✓ PASS: Valid tracking accepted - {result['medicine_name']}, {result['time_slot']}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 2: Missing required field
    tests_total += 1
    print("\nTest 2: Missing required field (dosage)")
    try:
        invalid_tracking = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'consume_date': '2025-10-30',
            'time_slot': '08:00'
        }
        result = validate_tracking_data(invalid_tracking, check_patient=False)
        print("✗ FAIL: Should have rejected missing dosage")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 3: Invalid date format
    tests_total += 1
    print("\nTest 3: Invalid date format")
    try:
        invalid_tracking = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'consume_date': 'October 30, 2025',
            'time_slot': '08:00'
        }
        result = validate_tracking_data(invalid_tracking, check_patient=False)
        print("✗ FAIL: Should have rejected invalid date format")
    except ValidationError as e:
        print(f"✓ PASS: Correctly rejected - {e}")
        tests_passed += 1
    
    # Test 4: XSS in time slot
    tests_total += 1
    print("\nTest 4: XSS prevention in time slot")
    try:
        xss_tracking = {
            'patient_id': 'P001',
            'medicine_name': 'Metformin',
            'dosage': '500mg',
            'consume_date': '2025-10-30',
            'time_slot': '08:00<script>alert("xss")</script>'
        }
        result = validate_tracking_data(xss_tracking, check_patient=False)
        print("✗ FAIL: XSS attempt not properly rejected")
    except ValidationError as e:
        print(f"✓ PASS: XSS rejected - {e}")
        tests_passed += 1
    
    print(f"\nTracking Validation: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("INPUT VALIDATION TEST SUITE")
    print("Electronic Medication Administration Record (eMAR)")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_passed = 0
    total_tests = 0
    
    # Run patient validation tests
    passed, total = test_patient_validation()
    total_passed += passed
    total_tests += total
    
    # Run prescription validation tests
    passed, total = test_prescription_validation()
    total_passed += passed
    total_tests += total
    
    # Run tracking validation tests
    passed, total = test_tracking_validation()
    total_passed += passed
    total_tests += total
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION TEST SUMMARY")
    print("="*60)
    print(f"Total tests passed: {total_passed}/{total_tests}")
    print(f"Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total_tests - total_passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
