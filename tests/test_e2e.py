import re
import time
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5000"

def test_nurse_workflow(page: Page):
    # 1. Role Selection
    page.goto(BASE_URL)
    expect(page).to_have_title(re.compile("eMAR - Role Selection"))
    page.click("text=Nurse")
    
    # 2. Login
    expect(page).to_have_title(re.compile("eMAR - Nurse Login"))
    page.fill("#username", "nurse")
    page.fill("#password", "nurse123")
    page.click("button[type='submit']")
    
    # Wait for redirection
    page.wait_for_url(f"{BASE_URL}/dashboard?role=nurse")
    expect(page.locator("h2").filter(has_text="Nurse Dashboard")).to_be_visible()

    # 3. Add Patient
    # Ensure we are on the Patient Management tab (it's active by default)
    page.click("text=Patient Management")
    
    # Generate unique patient ID
    patient_id = f"TEST-{int(time.time())}"
    
    page.fill("#patient_id", patient_id)
    page.fill("#name", "Test Patient")
    page.select_option("#floor", "1")
    page.fill("#room", "101")
    page.select_option("#bed", "A")
    page.fill("#age", "30")
    page.select_option("#gender", "Male")
    page.fill("#notes", "Created by automated test")
    
    # Handle alert dialog if any (though this app uses custom toasts or messages)
    # The app uses showMessage() which creates a toast div.
    
    page.click("button:has-text('Add Patient')")
    
    # Verify success toast
    expect(page.locator(".toast.success")).to_be_visible(timeout=5000)
    
    # Verify patient in list (refresh list)
    # The app automatically refreshes list after 2000ms in addPatient()
    page.wait_for_timeout(2500) 
    page.click("text=Refresh")
    expect(page.locator("#patientList")).to_contain_text(patient_id)

    # 4. Add Prescription
    page.click("text=Prescriptions")
    page.fill("#presc_patient_id", patient_id)
    
    # Check if medicine fields are present, if not add one
    if not page.locator("input[name='medicine_name']").is_visible():
        page.click("text=+ Add Another Medicine")

    page.fill("input[name='medicine_name']", "Test Med")
    page.fill("input[name='dosage']", "500mg")
    page.fill("input[name='frequency']", "Daily")
    page.fill("input[name='start_date']", "2025-01-01")
    page.fill("input[name='end_date']", "2025-12-31")
    
    # Add time slot
    # The template has a container .time-slots-container
    # We need to add a time slot.
    page.click("text=+ Add Time")
    page.select_option("select[name='time_slots[]']", "09:00")
    
    # Submit
    page.click("text=Submit All Prescriptions")
    
    # Now the modal is open.
    expect(page.locator("#confirmPrescriptionModal")).to_be_visible()
    page.click("#confirmSubmissionBtn")
    
    # Verify success toast
    expect(page.locator(".toast.success")).to_be_visible(timeout=5000)
    
    # Verify in list
    page.wait_for_timeout(2500)
    page.click("text=Refresh")
    expect(page.locator("#prescriptionList")).to_contain_text("Test Med")

    # 5. Duty Dashboard Search
    page.click("text=Duty Dashboard")
    page.click("text=Search by Patient")
    page.fill("#patientSearchInput", patient_id)
    page.click("text=Search")
    
    # Verify results
    expect(page.locator("#patientMedsResult")).to_contain_text("Test Med")

def test_management_workflow(page: Page):
    # 1. Role Selection
    page.goto(BASE_URL)
    # If we are already logged in or redirected, we might need to logout or force role selection
    # The role selection page is always at /
    expect(page).to_have_title(re.compile("eMAR - Role Selection"))
    page.click("text=Management")
    
    # 2. Login
    expect(page).to_have_title(re.compile("eMAR - Management Login"))
    page.fill("#username", "manager") 
    page.fill("#password", "manager123")
    page.click("button[type='submit']")
    
    page.wait_for_url(f"{BASE_URL}/dashboard?role=management")
    expect(page.locator("h2").filter(has_text="Management Dashboard")).to_be_visible()
    
    # 3. Check Stats
    # Wait for stats to load (they are fetched via API)
    expect(page.locator("#totalPatients")).not_to_have_text("0", timeout=10000) # Assuming there's at least 1 patient now
    expect(page.locator("#managementChart")).to_be_visible()
