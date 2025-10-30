"""
Test script for eMAR API endpoints
Run the Flask app first: python app.py
Then run this script: python test_api.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_add_patient():
    print_section("Testing Add Patient")
    patient_data = {
        "patient_id": "P001",
        "name": "John Doe",
        "floor": "3",
        "room": "301",
        "bed": "A",
        "age": "45",
        "gender": "Male",
        "notes": "Diabetic patient - Test data",
    }
    try:
        response = requests.post(f"{BASE_URL}/api/patients", json=patient_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_patients():
    print_section("Testing Get All Patients")
    try:
        response = requests.get(f"{BASE_URL}/api/patients")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get("success"):
            print(f"Found {len(result.get('data', []))} patients")
            print(f"Response: {json.dumps(result, indent=2)}")
        return result.get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_add_prescription():
    print_section("Testing Add Prescription")
    today = datetime.now().strftime("%Y-%m-%d")
    prescription_data = {
        "patient_id": "P001",
        "medicine_name": "Metformin",
        "dosage": "500mg",
        "frequency": "Twice daily",
        "start_date": today,
        "end_date": "",
        "time_slot": "8AM, 8PM",
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/prescriptions", json=prescription_data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_prescriptions():
    print_section("Testing Get All Prescriptions")
    try:
        response = requests.get(f"{BASE_URL}/api/prescriptions")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get("success"):
            print(f"Found {len(result.get('data', []))} prescriptions")
            print(f"Response: {json.dumps(result, indent=2)}")
        return result.get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_add_tracking():
    print_section("Testing Add Medication Tracking")
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    tracking_data = {
        "patient_id": "P001",
        "medicine_name": "Metformin",
        "dosage": "500mg",
        "consume_date": today,
        "time_slot": current_time,
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/medication-tracking", json=tracking_data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_tracking():
    print_section("Testing Get All Tracking Records")
    try:
        response = requests.get(f"{BASE_URL}/api/medication-tracking")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get("success"):
            print(f"Found {len(result.get('data', []))} tracking records")
            print(f"Response: {json.dumps(result, indent=2)}")
        return result.get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_patient_by_id():
    print_section("Testing Get Patient By ID")
    try:
        response = requests.get(f"{BASE_URL}/api/patient/P001")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_patient_prescriptions():
    print_section("Testing Get Patient Prescriptions")
    try:
        response = requests.get(f"{BASE_URL}/api/patient/P001/prescriptions")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_patient_tracking():
    print_section("Testing Get Patient Tracking History")
    try:
        response = requests.get(f"{BASE_URL}/api/patient/P001/tracking")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json().get("success", False)
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Electronic Medication Administration Record (eMAR)      ║")
    print("║              API Testing Suite                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("\nStarting tests...\n")

    results = {}

    # Test 1: Health Check
    results["Health Check"] = test_health()
    time.sleep(1)

    # Test 2: Add Patient
    results["Add Patient"] = test_add_patient()
    print("\nWaiting 15 seconds (ThingSpeak rate limit)...")
    time.sleep(15)

    # Test 3: Get Patients
    results["Get Patients"] = test_get_patients()
    time.sleep(2)

    # Test 4: Add Prescription
    results["Add Prescription"] = test_add_prescription()
    print("\nWaiting 15 seconds (ThingSpeak rate limit)...")
    time.sleep(15)

    # Test 5: Get Prescriptions
    results["Get Prescriptions"] = test_get_prescriptions()
    time.sleep(2)

    # Test 6: Add Tracking
    results["Add Tracking"] = test_add_tracking()
    print("\nWaiting 15 seconds (ThingSpeak rate limit)...")
    time.sleep(15)

    # Test 7: Get Tracking
    results["Get Tracking"] = test_get_tracking()
    time.sleep(2)

    # Test 8: Get Patient by ID
    results["Get Patient by ID"] = test_get_patient_by_id()
    time.sleep(1)

    # Test 9: Get Patient Prescriptions
    results["Get Patient Prescriptions"] = test_get_patient_prescriptions()
    time.sleep(1)

    # Test 10: Get Patient Tracking
    results["Get Patient Tracking"] = test_get_patient_tracking()

    # Print Summary
    print_section("TEST RESULTS SUMMARY")
    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")


if __name__ == "__main__":
    main()
