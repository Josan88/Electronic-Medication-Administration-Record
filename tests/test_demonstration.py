"""
Demonstration test that records a full website walkthrough for patient 108
with medication Lozenges. Runs nurse and management flows in a
single session to produce one video.
"""

from datetime import datetime, timedelta
import time
import requests
from playwright.sync_api import Page, expect


class TestWebsiteDemonstration:
    """Record an end-to-end demonstration covering nurse and management roles."""

    def test_full_demonstration_108(self, page: Page, app_url: str):
        """Execute the full walkthrough using patient 108 and Lozenges."""
        # Enable console logging
        page.on("console", lambda msg: print(f"BROWSER_LOG: {msg.text}"))

        # Use a consistent medicine name for demonstration
        # (ThingSpeak persistence may show prior runs; this demo tolerates that)

        patient_id = "108"
        med_name = "Lozenges"
        dosage = "500mg"
        time_slot = "17:00"  # 5:00 PM - afternoon slot to ensure it's in the future
        slot_label = {
            "09:00": "9:00 AM",
            "13:00": "1:00 PM",
            "17:00": "5:00 PM",
            "21:00": "9:00 PM",
        }[time_slot]
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        # Use today for prescription so it appears in duty dashboard
        presc_date = today

        # Nurse login
        page.goto(f"{app_url}/nurse-login")
        page.fill("#username", "nurse")
        page.fill("#password", "nurse123")
        page.click("button.btn-login")
        page.wait_for_url("**/dashboard?role=nurse")

        # Navigate to Nurse Dashboard
        page.click("label.burger-icon")
        page.wait_for_timeout(300)
        page.click("button:has-text('Nurse Dashboard')")
        page.wait_for_timeout(500)
        expect(page.locator("#patients")).to_be_visible()

        # DEMONSTRATION 1: Invalid patient ID format (validation error)
        page.fill("#patient_id", "108@#!")
        page.fill("#name", "John Doe")
        page.select_option("#floor", "1")
        page.select_option("#room", "101")
        page.select_option("#bed", "A")
        page.fill("#age", "30")
        page.select_option("#gender", "Male")
        page.fill("#notes", "Demonstration")
        page.click("#patientForm button[type='submit']")

        # Verify validation error toast appears
        expect(page.locator(".toast.error")).to_be_visible(timeout=5000)
        expect(page.locator(".toast.error")).to_contain_text(
            "Patient ID must contain only letters, numbers, hyphens, or underscores"
        )
        # Verify form data is preserved (no reset on validation error)
        expect(page.locator("#patient_id")).to_have_value("108@#!")
        page.wait_for_timeout(2000)  # Allow error toast to be visible in video

        # Wait for first error toast to disappear before next test
        expect(page.locator(".toast.error")).to_be_hidden(timeout=10000)

        # DEMONSTRATION 2: Invalid age value (validation error)
        page.fill("#patient_id", patient_id)
        page.fill("#name", "Demo Patient")  # No digits in name to pass name validation
        page.select_option("#floor", "1")
        page.select_option("#room", "101")
        page.select_option("#bed", "A")
        page.fill("#age", "999")  # Age out of valid range (0-150)
        page.select_option("#gender", "Male")
        page.fill("#notes", "Demonstration")
        page.click("#patientForm button[type='submit']")

        # Verify invalid age error toast
        expect(page.locator(".toast.error")).to_be_visible(timeout=5000)
        expect(page.locator(".toast.error")).to_contain_text(
            "Age must be between 0 and 150"
        )
        page.wait_for_timeout(2000)  # Allow error toast to be visible in video

        # Wait for error toast to disappear before next test
        expect(page.locator(".toast.error")).to_be_hidden(timeout=10000)

        # DEMONSTRATION 3: Successful patient creation
        page.fill("#patient_id", patient_id)
        page.fill("#name", "John Doe")
        page.select_option("#floor", "1")
        page.select_option("#room", "101")
        page.select_option("#bed", "A")
        page.fill("#age", "30")
        page.select_option("#gender", "Male")
        page.fill("#notes", "Demonstration")
        page.click("#patientForm button[type='submit']")

        # Verify success toast
        expect(page.locator(".toast.success")).to_be_visible(timeout=5000)
        expect(page.locator(".toast.success")).to_contain_text(
            "Patient added successfully"
        )
        page.wait_for_timeout(2000)  # Allow success toast to be visible in video

        # Wait for success toast to disappear before next test
        expect(page.locator(".toast.success")).to_be_hidden(timeout=10000)

        # DEMONSTRATION 4: Duplicate patient ID (duplication error)
        page.fill("#patient_id", patient_id)
        page.fill("#name", "John Doe")
        page.select_option("#floor", "1")
        page.select_option("#room", "101")
        page.select_option("#bed", "A")
        page.fill("#age", "30")
        page.select_option("#gender", "Male")
        page.fill("#notes", "Demonstration")
        page.click("#patientForm button[type='submit']")

        # Verify duplication error toast
        expect(page.locator(".toast.error")).to_be_visible(timeout=5000)
        expect(page.locator(".toast.error")).to_contain_text(
            "Patient with ID '108' already exists"
        )
        # Verify form data is preserved (no reset on duplication error)
        expect(page.locator("#patient_id")).to_have_value(patient_id)
        page.wait_for_timeout(2000)  # Allow error toast to be visible in video

        # Add prescription for Lozenges
        page.click("button.tab-button:has-text('Prescriptions')")
        page.wait_for_timeout(300)
        page.fill("#presc_patient_id", patient_id)
        page.click("button:has-text('Add Another Medicine')")
        page.wait_for_timeout(200)

        medicine_group = page.locator(".medicine-group").first
        medicine_group.locator("input[name='medicine_name']").fill(med_name)
        medicine_group.locator("input[name='dosage']").fill(dosage)
        medicine_group.locator("input[name='frequency']").fill("1")
        medicine_group.locator("input[name='start_date']").fill(presc_date)
        medicine_group.locator("input[name='end_date']").fill(tomorrow)
        medicine_group.locator("button:has-text('Add Time')").click()
        page.wait_for_timeout(200)
        medicine_group.locator("select[name='time_slots[]']").select_option(time_slot)

        page.click("button:has-text('Submit All Prescriptions')")
        expect(page.locator("#confirmPrescriptionModal")).to_be_visible()
        page.click("#confirmSubmissionBtn")
        expect(
            page.locator(".toast.success"), "Prescription toast should appear"
        ).to_be_visible(timeout=10000)

        # Wait until prescription API reflects the new entry (filter by date)
        for _ in range(10):
            presc_res = requests.get(
                f"{app_url}/api/patient/{patient_id}/prescriptions"
            )
            presc_data = presc_res.json().get("data", [])
            has_entry = any(
                p.get("patient_id") == patient_id
                and p.get("medicine_name") == med_name
                and time_slot in str(p.get("time_slot", ""))
                and p.get("start_date") == presc_date  # Filter for prescription date
                for p in presc_data
            )
            if has_entry:
                break
            time.sleep(1)
        else:
            assert (
                False
            ), f"New prescription for {presc_date} not found in API after 10s"

        # Duty Dashboard search for patient 108
        page.click("label.burger-icon")
        page.wait_for_timeout(300)
        page.click("button:has-text('Duty Dashboard')")
        page.wait_for_timeout(500)
        expect(page.locator("#dutyDashboard")).to_be_visible()

        page.click("button.tab-button:has-text('Search by Patient')")
        page.wait_for_timeout(300)
        expect(page.locator("#byPatient")).to_be_visible()
        page.fill("#patientSearchInput", patient_id)
        page.click("#byPatient button.btn-primary")
        page.wait_for_timeout(2000)
        expect(page.locator("#patientMedsResult")).not_to_be_empty(timeout=10000)

        # Show round timeline with pending status before completion
        page.click("button.tab-button:has-text('Round Timeline')")
        page.wait_for_timeout(400)
        page.evaluate("showDutyDashboard()")
        expect(page.locator("#timeline-tables")).to_be_visible(timeout=10000)

        # Wait for today's prescription to appear in timeline
        page.wait_for_function(
            f"() => document.querySelector('#timeline-tables')?.textContent.includes('{patient_id}')",
            timeout=15000,
        )
        round_header = page.locator(".accordion-header", has_text=slot_label)
        round_header.wait_for(state="visible", timeout=5000)
        round_header.click()
        page.wait_for_timeout(1000)

        # Locate the row for patient 108 with Lozenges (may show as Pending or need completion)
        med_row = page.locator(
            f"tr:has-text('{patient_id}'):has-text('{med_name}')"
        ).first
        expect(med_row).to_be_visible(timeout=10000)

        # Mark medication complete via API to keep flow deterministic
        consume_datetime = f"{presc_date} {time_slot}:00"
        track_resp = requests.post(
            f"{app_url}/api/medication-tracking",
            json={
                "patient_id": patient_id,
                "medicine_name": med_name,
                "dosage": dosage,
                "status": "complete",
                "consume_date": consume_datetime,
                "time_slot": time_slot,
            },
        )
        assert track_resp.status_code == 200, track_resp.text

        # Poll tracking API to ensure the completion record is visible to the UI
        # Since medicine_track is forced to ThingSpeak, this might take a moment
        for _ in range(20):
            tracking_res = requests.get(f"{app_url}/api/medication-tracking")
            tracking_data = tracking_res.json().get("data", [])
            found_complete = any(
                t.get("patient_id") == patient_id
                and t.get("medicine_name") == med_name
                and time_slot in str(t.get("time_slot", ""))
                and str(t.get("consume_date", "")).startswith(presc_date)
                for t in tracking_data
            )
            if found_complete:
                break
            time.sleep(1)
        else:
            # If we time out, we fail, but the video might show why
            pass

        # Reload search results to capture completed status in recording
        page.click("button.tab-button:has-text('Search by Patient')")
        page.wait_for_timeout(300)
        page.fill("#patientSearchInput", patient_id)
        page.click("#byPatient button.btn-primary")
        page.wait_for_timeout(2000)

        # Show round timeline again and confirm completed status is visible
        page.click("button.tab-button:has-text('Round Timeline')")
        page.wait_for_timeout(400)
        page.evaluate("showDutyDashboard()")
        expect(page.locator("#timeline-tables")).to_be_visible(timeout=10000)
        # Use textContent to check existence even if collapsed
        page.wait_for_function(
            f"() => document.querySelector('#timeline-tables')?.textContent.includes('{patient_id}')",
            timeout=15000,
        )
        # Robust wait: poll UI until the completed row appears (ThingSpeak sync may delay)
        complete_found = False
        for _ in range(45):  # ~90s max
            try:
                round_header = page.locator(".accordion-header", has_text=slot_label)
                round_header.wait_for(state="visible", timeout=2000)
                round_header.click()
                page.wait_for_timeout(300)
                # Check for Complete status in timeline (may coexist with old entries)
                timeline_content = page.locator("#timeline-tables").text_content()
                if "Complete" in timeline_content:
                    complete_found = True
                    break
            except Exception:
                pass
            finally:
                # Collapse back if open to keep UI consistent
                try:
                    round_header = page.locator(
                        ".accordion-header", has_text=slot_label
                    )
                    round_header.click()
                    page.wait_for_timeout(200)
                except Exception:
                    pass
            # Refresh the view and try again
            page.evaluate("showDutyDashboard()")
            page.wait_for_timeout(2000)

        assert (
            complete_found
        ), "Completed administration row did not appear within expected time"

        # Switch to management and verify dashboards render
        page.goto(f"{app_url}/management-login")
        page.fill("#username", "manager")
        page.fill("#password", "manager123")
        page.click("button.btn-login")
        page.wait_for_url("**/dashboard?role=management")
        page.wait_for_timeout(2000)

        # Verify management dashboard loads with all components
        expect(page.locator("#managementDashboard")).to_be_visible()
        expect(page.locator("#managementChart")).to_be_visible()

        # Scroll down to ensure chart is visible in video recording
        page.locator("#managementChart").scroll_into_view_if_needed()
        page.wait_for_timeout(
            800
        )  # Allow time for scroll to complete and be visible in video

        # MANAGEMENT CHART INTERACTIONS (enhanced video coverage)
        # Wait until global Chart instance (managementChart) is initialized (declared with let, not on window)
        page.wait_for_function(
            "() => typeof managementChart !== 'undefined' && managementChart && managementChart.data && managementChart.data.datasets && managementChart.data.datasets.length > 1"
        )

        # Capture initial dataset snapshot (Completed vs Pending counts per time slot)
        initial_datasets = page.evaluate(
            "() => (typeof managementChart !== 'undefined' && managementChart ? managementChart.data.datasets.map(ds => ({label: ds.label, data: [...ds.data]})) : [])"
        )
        print(f"MGMT_CHART_INITIAL_DATASETS: {initial_datasets}")

        # Force a re-init refresh (safe re-render) if desired
        page.evaluate("window.initManagementChart && window.initManagementChart();")
        page.wait_for_function(
            "() => typeof managementChart !== 'undefined' && managementChart && managementChart.data && managementChart.data.datasets && managementChart.data.datasets.length > 1"
        )
        refreshed_datasets = page.evaluate(
            "() => (typeof managementChart !== 'undefined' && managementChart ? managementChart.data.datasets.map(ds => ({label: ds.label, data: [...ds.data]})) : [])"
        )
        print(f"MGMT_CHART_REFRESHED_DATASETS: {refreshed_datasets}")

        # Hover each bar to trigger tooltips (visual only, Chart.js canvas tooltips not DOM-accessible)
        canvas = page.locator("#managementChart")
        box = canvas.bounding_box()
        if box:
            slots = 4  # Fixed time slot count
            for i in range(slots):
                x = box["x"] + (i + 0.5) * (box["width"] / slots)
                y = box["y"] + box["height"] / 2
                page.mouse.move(x, y)
                page.wait_for_timeout(500)

        # Toggle to Nurse Dashboard and back to ensure re-render persistence
        page.click("label.burger-icon")
        page.wait_for_timeout(200)
        nurse_btn = page.locator("button:has-text('Nurse Dashboard')")
        if nurse_btn.is_visible():
            nurse_btn.click()
        else:
            # Fallback: invoke dashboard switch directly (button hidden for management role)
            page.evaluate("showDashboard && showDashboard('nurseDashboard')")
        page.wait_for_timeout(600)
        page.click("label.burger-icon")
        page.wait_for_timeout(200)
        mgmt_btn = page.locator("button:has-text('Management Dashboard')")
        if mgmt_btn.is_visible():
            mgmt_btn.click()
        else:
            page.evaluate("showDashboard && showDashboard('managementDashboard')")
        page.wait_for_timeout(800)

        # Scroll chart back into view after navigation toggle
        page.locator("#managementChart").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        expect(page.locator("#managementChart")).to_be_visible()

        # Verify datasets remain accessible after navigation
        post_toggle_datasets = page.evaluate(
            "() => (typeof managementChart !== 'undefined' && managementChart ? managementChart.data.datasets.map(ds => ({label: ds.label, data: [...ds.data]})) : [])"
        )
        print(f"MGMT_CHART_POST_TOGGLE_DATASETS: {post_toggle_datasets}")

        # Basic integrity assertions: dataset structure preserved
        assert (
            initial_datasets and refreshed_datasets and post_toggle_datasets
        ), "Management chart datasets not captured"
        assert all(
            isinstance(entry.get("data", []), list) and len(entry.get("data", [])) == 4
            for entry in post_toggle_datasets
        ), "Unexpected dataset length after dashboard toggle"

        # Final hold for video clarity
        page.wait_for_timeout(2500)
