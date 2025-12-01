// Electronic Medication Administration Record - Main JavaScript

// Time slots options constant
const FIXED_TIME_SLOTS = [
  { value: "09:00", label: "9:00 AM" },
  { value: "13:00", label: "1:00 PM" },
  { value: "17:00", label: "5:00 PM" },
  { value: "21:00", label: "9:00 PM" },
];

// Global variables for charts and timers
let managementChart = null;
let managementChartTimer = null;
let managementRoundTimeout = null;

// Initial Setup
document.addEventListener("DOMContentLoaded", function () {
  console.log("eMAR System Loaded");

  // Check API health
  checkAPIHealth();

  // Initialize event listeners
  initializeEventListeners();

  // Handle role-based access
  const userRole = localStorage.getItem("userRole") || "nurse";
  setupRoleBasedAccess(userRole);

  // Load initial data
  const savedDashboard =
    localStorage.getItem("activeDashboard") || getDefaultDashboard(userRole);
  showDashboard(savedDashboard);
  loadPatients();
  loadPrescriptions();
  loadTracking();
  updateStats();

  // renderDutyTimetable is now part of showDutyDashboard
  // updateDutyTimetableStatus is called after tracking data loads
});

// Role-based access control
function setupRoleBasedAccess(role) {
  const nurseElements = document.querySelectorAll(".nurse-only");
  const managementElements = document.querySelectorAll(".management-only");

  if (role === "management") {
    nurseElements.forEach((el) => (el.style.display = "none"));
    managementElements.forEach((el) => (el.style.display = "block"));
  } else {
    nurseElements.forEach((el) => (el.style.display = "block"));
    managementElements.forEach((el) => (el.style.display = "none"));
  }
}

function getDefaultDashboard(role) {
  return role === "management" ? "managementDashboard" : "dutyDashboard";
}

// API Health Check
async function checkAPIHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    console.log("API Status:", data);
    document.getElementById("apiStatus").textContent = "✓ Online";
    document.getElementById("apiStatus").style.color = "#28a745";
  } catch (error) {
    console.error("Error checking API health:", error);
    document.getElementById("apiStatus").textContent = "✗ Offline";
    document.getElementById("apiStatus").style.color = "#dc3545";
  }
}

// Initialize Event Listeners
function initializeEventListeners() {
  // Patient Form
  document
    .getElementById("patientForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      await addPatient();
    });

  // Prevent native submit on prescription form to avoid page reload / dashboard reset
  const prescriptionForm = document.getElementById("prescriptionForm");
  if (prescriptionForm) {
    prescriptionForm.addEventListener("submit", (e) => {
      e.preventDefault();
    });
  }

  // Confirm button and submission logic
  document
    .getElementById("confirmSubmissionBtn")
    .addEventListener("click", async () => {
      // Close the modal and then run the submission logic
      closeModal("confirmPrescriptionModal");
      await addPrescription();
    });

  const consumeDateInput = document.getElementById("consume_date");
  if (consumeDateInput) {
    consumeDateInput.value = getLocalDateString();
  }
}

// Main Dashboard Navigation (Burger Menu)
function showDashboard(dashboardId) {
  const dashboards = document.querySelectorAll(".main-dashboard");
  dashboards.forEach((d) => d.classList.remove("active"));

  const target = document.getElementById(dashboardId);
  if (target) {
    target.classList.add("active");
    // Save the active dashboard ID to localStorage
    localStorage.setItem("activeDashboard", dashboardId);
  }

  const burgerCheckbox = document.getElementById("burger-menu");
  if (burgerCheckbox) burgerCheckbox.checked = false;

  if (dashboardId === "dutyDashboard") {
    showDutyDashboard().catch(() => {});
  }

  if (dashboardId === "managementDashboard") {
    setTimeout(() => initManagementChart(), 200);
  }
}

// Tab Navigation
function showTab(tabName, clickedElement = event.target) {
  // Hide all tabs within the active dashboard
  const activeDashboard = document.querySelector(".main-dashboard.active");
  if (activeDashboard) {
    const tabs = activeDashboard.querySelectorAll(".tab-content");
    tabs.forEach((tab) => {
      tab.classList.remove("active");
    });

    // Remove active class from all buttons in the current tab set
    const buttons = activeDashboard.querySelectorAll(".tab-button");
    buttons.forEach((button) => {
      button.classList.remove("active");
    });

    // Show selected tab
    document.getElementById(tabName).classList.add("active");

    // Activate button
    clickedElement.classList.add("active");
  }

  // Load data for the tab
  if (tabName === "patients") {
    loadPatients();
  } else if (tabName === "prescriptions") {
    loadPrescriptions();
  } else if (tabName === "tracking") {
    loadTracking();
  }
}

// Patient Management
async function addPatient() {
  const patientData = {
    patient_id: document.getElementById("patient_id").value,
    name: document.getElementById("name").value,
    floor: document.getElementById("floor").value,
    room: document.getElementById("room").value,
    bed: document.getElementById("bed").value,
    age: document.getElementById("age").value,
    gender: document.getElementById("gender").value,
    notes: document.getElementById("notes").value,
  };

  try {
    const response = await fetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patientData),
    });

    const result = await response.json();

    if (result.success) {
      showMessage("success", "Patient added successfully!");
      document.getElementById("patientForm").reset();
      setTimeout(() => loadPatients(), 2000);
    } else {
      showMessage("error", "Error: " + result.error);
    }
  } catch (error) {
    showMessage("error", "Error adding patient: " + error.message);
  }
}

async function loadPatients() {
  const listElement = document.getElementById("patientList");
  listElement.innerHTML = '<div class="loading"></div> Loading patients...';

  try {
    const response = await fetch("/api/patients");
    const result = await response.json();

    if (result.success && result.data.length > 0) {
      listElement.innerHTML = "";

      // Only show latest 5 patients
      const latest = result.data.slice(-5).reverse();

      latest.forEach((patient) => {
        const item = document.createElement("div");
        item.className = "data-item";
        item.innerHTML = `
          <h4>${patient.name || "N/A"} (ID: ${patient.patient_id || "N/A"})</h4>
          <p><strong>Location:</strong> Floor ${patient.floor || "N/A"}, Room ${
          patient.room || "N/A"
        }, Bed ${patient.bed || "N/A"}</p>
          <p><strong>Age:</strong> ${
            patient.age || "N/A"
          } | <strong>Gender:</strong> ${patient.gender || "N/A"}</p>
          <p><strong>Notes:</strong> ${patient.notes || "None"}</p>
          <p class="timestamp">Added: ${formatDate(patient.created_at)}</p>
        `;
        listElement.appendChild(item);
      });
    } else {
      listElement.innerHTML =
        '<div class="empty-state">No patients found</div>';
    }
  } catch (error) {
    listElement.innerHTML =
      '<div class="message error">Error loading patients: ' +
      error.message +
      "</div>";
  }
}

function getLocalDateString() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0"); // months are 0-indexed
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Prescription Management
function addMedicineField() {
  const container = document.getElementById("medicineFieldsContainer");
  const template = document.getElementById("medicineFieldTemplate");

  // Clone the content of the template
  const clone = template.content.cloneNode(true);
  const newGroup = clone.querySelector(".medicine-group");

  // Set default start date to today
  const startDateInput = newGroup.querySelector('input[name="start_date"]');
  if (startDateInput) {
    startDateInput.value = getLocalDateString();
  }

  // Add frequency change listener for auto-population
  const frequencyInput = newGroup.querySelector('input[name="frequency"]');
  if (frequencyInput) {
    frequencyInput.addEventListener("blur", function () {
      autoPopulateTimeSlotsIfNeeded(newGroup);
    });
  }

  // Append the new group
  container.appendChild(newGroup);
}

// Auto-populate time slots if frequency is 4
function autoPopulateTimeSlotsIfNeeded(medicineGroup) {
  const frequencyInput = medicineGroup.querySelector('[name="frequency"]');
  const container = medicineGroup.querySelector(".time-slots-container");

  if (!frequencyInput || !container) return;

  const frequencyValue = parseInt(frequencyInput.value);

  // Only auto-populate if frequency is exactly 4 and no time slots exist yet
  if (frequencyValue === 4 && container.children.length === 0) {
    // Add all 4 standard time slots
    FIXED_TIME_SLOTS.forEach((timeSlot, index) => {
      const wrapper = document.createElement("div");
      wrapper.className = "time-slot-wrapper";

      const selectField = document.createElement("select");
      selectField.name = "time_slots[]";
      selectField.required = true;
      selectField.className = "form-control time-slot-select";
      selectField.style.marginRight = "10px";
      selectField.style.marginBottom = "5px";

      FIXED_TIME_SLOTS.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt.value;
        option.textContent = opt.label;
        selectField.appendChild(option);
      });

      // Pre-select the appropriate time slot
      selectField.value = timeSlot.value;

      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "btn btn-danger btn-sm remove-time";
      removeButton.innerHTML = "✕";
      removeButton.onclick = function () {
        this.parentElement.remove();
      };

      wrapper.appendChild(selectField);
      wrapper.appendChild(removeButton);
      container.appendChild(wrapper);

      // Add validation on change
      selectField.addEventListener("change", function () {
        validateTimeSlots(medicineGroup);
      });
    });

    showMessage(
      "info",
      "Time slots auto-populated for 4 times daily frequency (9AM, 1PM, 5PM, 9PM)"
    );
  }
}

function removeMedicineField(button) {
  // Traverse up to the parent '.medicine-group' and remove it
  button.closest(".medicine-group").remove();
}

function addTimeField(button) {
  const container = button.previousElementSibling; // the div.time-slots-container
  const medicineGroup = button.closest(".medicine-group");

  // Get the frequency value
  const frequencyInput = medicineGroup.querySelector('[name="frequency"]');
  const maxSlots = parseInt(frequencyInput.value) || 0;

  // Count current time slots
  const currentSlots = container.querySelectorAll(
    'select[name="time_slots[]"]'
  ).length;

  if (currentSlots >= maxSlots) {
    showMessage(
      "error",
      `You can only add ${maxSlots} time slot(s) as per the frequency.`
    );
    return;
  }

  // Create new select wrapper div
  const wrapper = document.createElement("div");
  wrapper.className = "time-slot-wrapper";

  // Create select element
  const selectField = document.createElement("select");
  selectField.name = "time_slots[]";
  selectField.required = true;
  selectField.className = "form-control time-slot-select";
  selectField.style.marginRight = "10px";
  selectField.style.marginBottom = "5px";

  FIXED_TIME_SLOTS.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt.value;
    option.textContent = opt.label;
    selectField.appendChild(option);
  });

  // Add remove button
  const removeButton = document.createElement("button");
  removeButton.type = "button";
  removeButton.className = "btn btn-danger btn-sm remove-time";
  removeButton.innerHTML = "✕";
  removeButton.onclick = function () {
    this.parentElement.remove();
  };

  // Assemble and append
  wrapper.appendChild(selectField);
  wrapper.appendChild(removeButton);
  container.appendChild(wrapper);

  // Add validation on change to prevent duplicates
  selectField.addEventListener("change", function () {
    validateTimeSlots(medicineGroup);
  });
}

// Helper function to validate time slots for duplicates
function validateTimeSlots(medicineGroup) {
  const container = medicineGroup.querySelector(".time-slots-container");
  const selects = Array.from(
    container.querySelectorAll('select[name="time_slots[]"]')
  );
  const values = selects.map((s) => s.value);

  // Check for duplicates
  const duplicates = values.filter(
    (item, index) => values.indexOf(item) !== index
  );

  if (duplicates.length > 0) {
    showMessage(
      "error",
      "Duplicate time slots detected. Please select different times."
    );
    // Highlight duplicate selects
    selects.forEach((select) => {
      if (duplicates.includes(select.value)) {
        select.style.borderColor = "red";
      } else {
        select.style.borderColor = "";
      }
    });
    return false;
  } else {
    // Clear any previous error highlighting
    selects.forEach((select) => {
      select.style.borderColor = "";
    });
    return true;
  }
}

async function addPrescription() {
  // Get the common Patient ID
  const patientId = document.getElementById("presc_patient_id").value;
  const medicineGroups = document.querySelectorAll(
    "#medicineFieldsContainer .medicine-group"
  );

  if (!patientId) {
    showMessage("error", "Please enter a Patient ID.");
    return;
  }

  try {
    const res = await fetch(`/api/patient/${patientId}`);
    const data = await res.json();

    if (!data.success || !data.data) {
      showMessage(
        "error",
        `Patient ID '${patientId}' does not exist. Please check again.`
      );
      return; // Stop here!
    }
  } catch (err) {
    showMessage("error", "Error checking patient ID. Try again.");
    return;
  }

  if (medicineGroups.length === 0) {
    showMessage("error", "Please add at least one medicine prescription.");
    return;
  }

  let successCount = 0;
  let failureCount = 0;

  // Loop through each dynamic medicine group
  for (const group of medicineGroups) {
    // Validate time slots for duplicates
    if (!validateTimeSlots(group)) {
      showMessage(
        "error",
        "Please fix duplicate time slots before submitting."
      );
      return;
    }

    // Extract data from the current medicine group using its 'name' attributes
    const prescriptionData = {
      patient_id: patientId,
      medicine_name: group.querySelector('[name="medicine_name"]').value,
      dosage: group.querySelector('[name="dosage"]').value,
      frequency: group.querySelector('[name="frequency"]').value,
      start_date: group.querySelector('[name="start_date"]').value,
      end_date: group.querySelector('[name="end_date"]').value,
      time_slot: Array.from(
        group.querySelectorAll('select[name="time_slots[]"]')
      )
        .map((input) => input.value)
        .join(", "),
    };

    // Skip if mandatory fields are empty
    if (
      !prescriptionData.medicine_name ||
      !prescriptionData.dosage ||
      !prescriptionData.frequency ||
      !prescriptionData.start_date ||
      !prescriptionData.end_date ||
      !prescriptionData.time_slot
    ) {
      showMessage(
        "error",
        `Skipping an incomplete medicine entry. Fill out all required fields.`
      );
      failureCount++;
      continue;
    }

    // Submit the individual entry to the API
    try {
      const response = await fetch("/api/prescriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(prescriptionData),
      });

      const result = await response.json();

      if (result.success) {
        successCount++;
      } else {
        failureCount++;
        console.error("API Error during submission:", result.error);
        showMessage("error", "Error: " + result.error);
      }
    } catch (error) {
      failureCount++;
      console.error("Error adding prescription entry:", error.message);
      showMessage("error", "Error adding prescription: " + error.message);
    }
  }

  // Show final status and reset form only if all succeeded
  if (successCount > 0 && failureCount === 0) {
    showMessage(
      "success",
      `${successCount} prescription(s) added successfully!`
    );
    // Reset form and dynamic fields
    document.getElementById("prescriptionForm").reset();
    document.getElementById("medicineFieldsContainer").innerHTML = ""; // Clear all dynamic fields
    addMedicineField(); // Add one fresh field
    setTimeout(() => loadPrescriptions(), 2000);
  } else if (successCount > 0) {
    showMessage(
      "success",
      `${successCount} prescription(s) added successfully! (${failureCount} failed - form data preserved)`
    );
    setTimeout(() => loadPrescriptions(), 2000);
  } else {
    showMessage(
      "error",
      `Failed to add any prescriptions. ${failureCount} attempt(s) failed. Form data preserved.`
    );
  }
}

// Utility Functions

function openModal(modalId) {
  document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

// Prescription Management
function showPrescriptionPreview() {
  const patientId = document.getElementById("presc_patient_id").value;
  const medicineGroups = document.querySelectorAll(
    "#medicineFieldsContainer .medicine-group"
  );
  const previewContent = document.getElementById("prescriptionPreviewContent");

  if (!patientId || medicineGroups.length === 0) {
    showMessage(
      "error",
      "Please ensure a Patient ID is entered and at least one medicine is added."
    );
    return;
  }

  let previewHTML = `<h3>Patient ID: ${patientId}</h3><hr>`;
  let validCount = 0;

  // Collect data and build the preview content
  medicineGroups.forEach((group, index) => {
    const data = {
      medicine_name: group.querySelector('[name="medicine_name"]').value,
      dosage: group.querySelector('[name="dosage"]').value,
      frequency: group.querySelector('[name="frequency"]').value,
      start_date: group.querySelector('[name="start_date"]').value,
      end_date: group.querySelector('[name="end_date"]').value || "N/A",
      time_slot:
        Array.from(group.querySelectorAll('select[name="time_slots[]"]'))
          .map((input) => input.value)
          .join(", ") || "N/A",
    };

    if (
      data.medicine_name &&
      data.dosage &&
      data.frequency &&
      data.start_date &&
      data.end_date &&
      data.time_slot
    ) {
      validCount++;
      previewHTML += `
                <div class="preview-item">
                    <h4>Medicine ${index + 1}: ${data.medicine_name}</h4>
                    <p>Dosage: ${data.dosage}</p>
                    <p>Frequency: ${data.frequency}</p>
                    <p>Start Date: ${data.start_date} | End Date: ${
        data.end_date
      }</p>
                    <p>Time Slot: ${data.time_slot}</p>
                    <hr>
                </div>
            `;
    }
  });

  if (validCount === 0) {
    showMessage("error", "No complete prescriptions found to submit.");
    return;
  }

  previewContent.innerHTML = previewHTML;

  // Open the modal
  openModal("confirmPrescriptionModal");
}

async function loadPrescriptions() {
  const listElement = document.getElementById("prescriptionList");
  listElement.innerHTML =
    '<div class="loading"></div> Loading prescriptions...';

  try {
    const response = await fetch("/api/prescriptions");
    const result = await response.json();

    if (result.success && result.data.length > 0) {
      listElement.innerHTML = "";

      // only show the latest 8 prescriptions
      const latest = result.data.slice(-8).reverse();

      latest.forEach((prescription) => {
        const item = document.createElement("div");
        item.className = "data-item";
        item.innerHTML = `
          <h4>${prescription.medicine_name || "N/A"} - Patient ID: ${
          prescription.patient_id || "N/A"
        }</h4>
          <p><strong>Dosage:</strong> ${
            prescription.dosage || "N/A"
          } | <strong>Frequency:</strong> ${prescription.frequency || "N/A"}</p>
          <p><strong>Duration:</strong> ${
            prescription.start_date || "N/A"
          } to ${prescription.end_date || "Ongoing"}</p>
          <p><strong>Time Slots:</strong> ${
            prescription.time_slot || "Not specified"
          }</p>
          <p class="timestamp">Prescribed: ${formatDate(
            prescription.created_at
          )}</p>
        `;
        listElement.appendChild(item);
      });
    } else {
      listElement.innerHTML =
        '<div class="empty-state">No prescriptions found</div>';
    }
  } catch (error) {
    listElement.innerHTML =
      '<div class="message error">Error loading prescriptions: ' +
      error.message +
      "</div>";
  }
}

async function loadPatientActiveMeds() {
  const patientIdRaw =
    document.getElementById("patientSearchInput")?.value || "";
  const patientId = patientIdRaw.trim();
  const resultContainer = document.getElementById("patientMedsResult");

  if (!resultContainer) return;
  resultContainer.innerHTML = '<div class="loading"></div>';

  if (!patientId) {
    resultContainer.innerHTML = "<p>Please enter a patient ID</p>";
    return;
  }

  const encodedId = encodeURIComponent(patientId);

  try {
    // Fetch and show patient info first
    let patient = null;
    try {
      const patientRes = await fetch(`/api/patient/${encodedId}`);
      if (patientRes.ok) {
        const pj = await patientRes.json();
        patient = pj.data || pj || null;
      }
    } catch (e) {
      // Patient not found
      patient = null;
    }

    // If patient doesn't exist, show error and stop
    if (!patient) {
      resultContainer.innerHTML = `<div class="message error">Patient ID '${patientId}' not found. Please check the ID and try again.</div>`;
      return;
    }

    const infoHtml = `
      <div class="card patient-info-card" style="margin-top: 1rem;">
        <h4 style="margin-bottom: 1rem; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.75rem;">Patient Information</h4>
        <div class="patient-info-grid">
          <div class="info-row">
            <span class="info-label">Patient ID</span>
            <span class="info-value">${patient.patient_id || patientId}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Name</span>
            <span class="info-value">${patient.name || "N/A"}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Floor</span>
            <span class="info-value">${patient.floor || "N/A"}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Room</span>
            <span class="info-value">${patient.room || "N/A"}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Bed</span>
            <span class="info-value">${patient.bed || "N/A"}</span>
          </div>
        </div>
      </div>`;

    // Show patient card immediately with a static loading message
    resultContainer.innerHTML =
      infoHtml +
      '<p style="margin-top: 1rem; color: #999;">Loading medications...</p>';

    // Fetch prescriptions for this patient
    let prescRes = await fetch(`/api/patient/${encodedId}/prescriptions`);
    let prescs = [];
    if (prescRes.ok) {
      const prescJson = await prescRes.json();
      prescs = prescJson.data || prescJson || [];
    } else {
      // fallback to all prescriptions and filter client-side
      const allRes = await fetch("/api/prescriptions");
      if (allRes.ok) {
        const allJson = await allRes.json();
        prescs = (allJson.data || []).filter(
          (p) => String(p.patient_id) === String(patientId)
        );
      }
    }

    // determine active meds
    const today = getLocalDateString();
    const activeMeds = (prescs || []).filter((m) => {
      if (!m.start_date) return false;
      if (String(m.start_date).split("T")[0] > today) return false;
      if (m.end_date && String(m.end_date).split("T")[0] < today) return false;
      return true;
    });

    // render meds below the patient card with improved format
    let medsHtml = "";
    if (activeMeds.length > 0) {
      medsHtml = activeMeds
        .map(
          (med) => `
        <div class="data-item">
          <strong>${med.medicine_name || "N/A"}</strong><br>
          <span style="margin-left: 1rem;">Dosage: ${
            med.dosage || "N/A"
          }</span><br>
          <span style="margin-left: 1rem;">Frequency: ${
            med.frequency || "N/A"
          } times daily</span><br>
          <span style="margin-left: 1rem;">Times: ${
            med.time_slot || "N/A"
          }</span><br>
          <small style="margin-left: 1rem;">Period: ${
            med.start_date || "N/A"
          } to ${med.end_date || "Ongoing"}</small>
        </div>`
        )
        .join("");
    } else {
      medsHtml = "<p>No active medications found</p>";
    }

    resultContainer.innerHTML = infoHtml + medsHtml;

    // scroll patient info into view
    const infoCard = resultContainer.querySelector(".patient-info-card");
    if (infoCard)
      infoCard.scrollIntoView({ behavior: "smooth", block: "center" });
  } catch (err) {
    resultContainer.innerHTML = "<p>Error loading medications</p>";
    console.error("loadPatientActiveMeds error:", err);
  }
}

async function loadTracking() {
  const listElement = document.getElementById("patientTracking");
  listElement.innerHTML =
    '<div class="loading"></div> Loading tracking records...';

  try {
    const response = await fetch("/api/medication-tracking");
    const result = await response.json();

    if (result.success && result.data.length > 0) {
      listElement.innerHTML = "";
      result.data.reverse().forEach((record) => {
        const item = document.createElement("div");
        item.className = "data-item";

        // Determine status badge styling
        const status = record.status || "pending";
        const statusClass =
          status === "complete" ? "status-complete" : "status-pending";
        const statusLabel = status === "complete" ? "✓ Complete" : "⏳ Pending";

        item.innerHTML = `
          <h4>${record.medicine_name || "N/A"} - Patient ID: ${
          record.patient_id || "N/A"
        } <span class="status-badge ${statusClass}">${statusLabel}</span></h4>
          <p><strong>Dosage:</strong> ${record.dosage || "N/A"}</p>
          <p><strong>Administered:</strong> ${
            record.consume_date || "N/A"
          } at ${record.time_slot || "N/A"}</p>
          <p class="timestamp">Recorded: ${formatDate(record.created_at)}</p>
        `;
        listElement.appendChild(item);
      });
    } else {
      listElement.innerHTML =
        '<div class="empty-state">No tracking records found</div>';
    }
  } catch (error) {
    listElement.innerHTML =
      '<div class="message error">Error loading tracking records: ' +
      error.message +
      "</div>";
  }
}

// Utility Functions
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleString();
}

// Stats Overview
async function updateStats() {
  try {
    const [patientsRes, prescRes, trackRes] = await Promise.all([
      fetch("/api/patients"),
      fetch("/api/prescriptions"),
      fetch("/api/medication-tracking"),
    ]);

    const patientsData = await patientsRes.json();
    const prescData = await prescRes.json();
    const trackData = await trackRes.json();

    const patients = patientsData.data || [];
    const prescriptions = prescData.data || [];
    const tracking = trackData.data || [];

    // Count totals
    const totalPatients = patients.length;
    const activePrescriptions = prescriptions.length;

    // Count completed today
    const today = getLocalDateString();
    const completedToday = tracking.filter((r) =>
      (r.consume_date || "").startsWith(today)
    ).length;

    document.getElementById("totalPatients").textContent = totalPatients;
    document.getElementById("totalPrescriptions").textContent =
      activePrescriptions;
    document.getElementById("todayAdministrations").textContent =
      completedToday;
  } catch (error) {
    console.error("updateStats error:", error);
  }
}

function showMessage(type, message) {
  // Get or create toast container
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-atomic", "true");
    document.body.appendChild(container);
  }

  // Create toast element
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.setAttribute("role", "alert");
  toast.setAttribute("aria-live", "assertive");

  // Get icon based on type
  const icons = {
    success: "✓",
    error: "✗",
    info: "ℹ",
  };
  const icon = icons[type] || "ℹ";

  // Get duration based on type (milliseconds)
  const durations = {
    success: 4000,
    error: 7000,
    info: 5000,
  };
  const duration = durations[type] || 5000;

  // Build toast content
  toast.innerHTML = `
    <span class="toast-icon" aria-hidden="true">${icon}</span>
    <div class="toast-content">${escapeHtml(message)}</div>
    <button class="toast-close" aria-label="Close notification" type="button">×</button>
    <div class="toast-progress"></div>
  `;

  // Add to container
  container.appendChild(toast);

  // Setup progress bar animation
  const progressBar = toast.querySelector(".toast-progress");
  setTimeout(() => {
    progressBar.style.transition = `width ${duration}ms linear`;
    progressBar.style.width = "0%";
  }, 10);

  // Setup close button
  const closeBtn = toast.querySelector(".toast-close");
  closeBtn.addEventListener("click", () => {
    removeToast(toast);
  });

  // Auto remove after duration
  setTimeout(() => {
    removeToast(toast);
  }, duration);
}

function removeToast(toast) {
  if (toast.classList.contains("hiding")) return;

  toast.classList.add("hiding");
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);

      // Remove container if empty
      const container = document.querySelector(".toast-container");
      if (container && container.children.length === 0) {
        container.remove();
      }
    }
  }, 300); // Match animation duration
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showDutyTab(tabName) {
  const tabContents = document.querySelectorAll("#dutyDashboard .tab-content");
  const tabButtons = document.querySelectorAll("#dutyDashboard .tab-button");

  tabContents.forEach((content) => content.classList.remove("active"));
  tabButtons.forEach((button) => button.classList.remove("active"));

  // Show the selected tab content
  document.getElementById(tabName).classList.add("active");

  // Highlight the selected tab button
  event.target.classList.add("active");
}

async function showDutyDashboard() {
  const container = document.querySelector("#timeline-tables");
  if (!container) {
    console.error("#timeline-tables container not found.");
    return;
  }
  container.innerHTML = "<p>Loading rounds...</p>";

  try {
    // Fetch patients, prescriptions and tracking data
    const [patientsRes, prescRes, trackRes] = await Promise.all([
      fetch("/api/patients"),
      fetch("/api/prescriptions"),
      fetch("/api/medication-tracking"),
    ]);

    if (!patientsRes.ok || !prescRes.ok || !trackRes.ok) {
      throw new Error("Failed to fetch data");
    }

    const patientsResult = await patientsRes.json();
    const prescResult = await prescRes.json();
    const trackResult = await trackRes.json();

    const patients = patientsResult.data || [];
    const prescriptions = prescResult.data || [];
    const tracking = trackResult.data || [];

    // Get today's date for filtering active prescriptions
    const today = getLocalDateString();

    // Filter prescriptions to only include active ones (today is within start_date and end_date)
    const activePrescriptions = prescriptions.filter((p) => {
      const startDate = p.start_date || "";
      const endDate = p.end_date || "";

      // If no dates specified, include the prescription
      if (!startDate && !endDate) return true;

      // Check if today is on or after start_date
      const afterStart = !startDate || today >= startDate;

      // Check if today is on or before end_date
      const beforeEnd = !endDate || today <= endDate;

      return afterStart && beforeEnd;
    });

    // Create patients lookup map
    const patientsMap = new Map(patients.map((p) => [p.patient_id, p]));

    // Group by time slot with patient details
    const grouped = {};
    activePrescriptions.forEach((p) => {
      const patient = patientsMap.get(p.patient_id) || {};
      const slots = (p.time_slot || "Unknown").split(",").map((s) => s.trim());

      slots.forEach((slot) => {
        if (!grouped[slot]) grouped[slot] = [];
        grouped[slot].push({
          patient_id: p.patient_id,
          medicine_name: p.medicine_name,
          floor: patient.floor || "N/A",
          room: patient.room || "N/A",
          bed: patient.bed || "N/A",
          served: isServed(p, tracking, slot),
        });
      });
    });

    renderTimelineTable(grouped);
  } catch (err) {
    container.innerHTML = `<p class="error">Failed to load Duty Dashboard: ${err.message}</p>`;
    console.error("Duty Dashboard Error:", err);
  }
}

function isServed(prescription, tracking, specificSlot = null) {
  const today = getLocalDateString();

  // Parse prescription time slots (may be comma-separated)
  const prescriptionSlots = (prescription.time_slot || "")
    .split(",")
    .map((s) => s.trim());

  // If a specific slot is provided, only check for that slot
  const slotsToCheck = specificSlot ? [specificSlot] : prescriptionSlots;

  return tracking.some((t) => {
    // Debug logging
    if (t.patient_id === prescription.patient_id) {
      console.log(
        `Checking tracking for ${t.patient_id}: med=${t.medicine_name} vs ${prescription.medicine_name}, date=${t.consume_date}`
      );
    }

    // Check if tracking date is today
    // Handle both "T" and space separators in date format
    const consumeDateStr = String(t.consume_date || "");
    const trackDate = consumeDateStr.split("T")[0].split(" ")[0];
    if (trackDate !== today) return false;

    // Check patient and medicine match
    if (
      t.patient_id !== prescription.patient_id ||
      t.medicine_name !== prescription.medicine_name
    ) {
      return false;
    }

    // Map tracking record to the relevant slot (handles comma-separated schedules)
    const trackSlot = resolveTrackingSlot(t);
    if (!trackSlot) {
      return false;
    }

    // Check if the tracking slot matches any of the slots to check
    if (!slotsToCheck.includes(trackSlot)) {
      return false;
    }

    // IMPORTANT: Validate that the actual consumption time falls within the expected time window
    // Parse the actual consumption time from consume_date
    const consumeTime = consumeDateStr.includes(" ")
      ? consumeDateStr.split(" ")[1] // "2025-11-18 10:20:18" -> "10:20:18"
      : null;

    if (!consumeTime) {
      // If no time component, we can't validate the window
      return true; // Accept it (legacy behavior)
    }

    // Extract hour and minute from consume time (e.g., "10:20:18" -> 10, 20)
    const [consumeHour, consumeMinute] = consumeTime.split(":").map(Number);
    const consumeMinutes = consumeHour * 60 + consumeMinute;

    // Parse the tracked slot time (e.g., "09:00" -> 9, 0)
    const [slotHour, slotMinute] = trackSlot.split(":").map(Number);
    const slotMinutes = slotHour * 60 + slotMinute;

    // Find the next slot time to determine the window
    const allSlots = prescriptionSlots
      .map((s) => {
        const [h, m] = s.split(":").map(Number);
        return h * 60 + m;
      })
      .sort((a, b) => a - b);

    const currentSlotIndex = allSlots.indexOf(slotMinutes);
    if (currentSlotIndex === -1) return false;

    const nextSlotMinutes =
      currentSlotIndex < allSlots.length - 1
        ? allSlots[currentSlotIndex + 1]
        : allSlots[0] + 1440; // Next day's first slot

    // Check if consume time falls within [slotMinutes, nextSlotMinutes)
    if (nextSlotMinutes > 1440) {
      // Window crosses midnight (e.g., 21:00 to 09:00 next day)
      // OR single slot per day (e.g., 13:00 to 13:00 next day)
      if (currentSlotIndex < allSlots.length - 1) {
        // Multiple slots, last one crosses to first one next day
        return (
          consumeMinutes >= slotMinutes ||
          consumeMinutes < nextSlotMinutes - 1440
        );
      } else {
        // Single slot - window is from slot time today until same time tomorrow
        // Only times >= slotMinutes are valid today
        return consumeMinutes >= slotMinutes;
      }
    } else {
      return consumeMinutes >= slotMinutes && consumeMinutes < nextSlotMinutes;
    }
  });
}

// Determine which slot a tracking record corresponds to (handles comma-separated schedules)
function resolveTrackingSlot(record) {
  const slotRaw = String(record.time_slot || "");
  const slots = slotRaw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (slots.length === 0) return "";

  const consumeRaw = String(
    record.consume_date || record.consume_datetime || ""
  );
  if (!consumeRaw) return slots[0];

  const timePart = consumeRaw.includes("T")
    ? consumeRaw.split("T")[1]
    : consumeRaw.split(" ")[1];

  if (!timePart) return slots[0];

  const [consumeHourStr, consumeMinuteStr] = timePart.split(":");
  const consumeHour = Number(consumeHourStr);
  const consumeMinute = Number(consumeMinuteStr || "0");

  if (Number.isNaN(consumeHour) || Number.isNaN(consumeMinute)) return slots[0];

  const consumeMinutes = consumeHour * 60 + consumeMinute;

  const slotMinutes = slots
    .map((s) => {
      const [hStr, mStr] = s.split(":");
      const h = Number(hStr);
      const m = Number(mStr || "0");
      if (Number.isNaN(h) || Number.isNaN(m)) return null;
      return { slot: s, minutes: h * 60 + m };
    })
    .filter(Boolean)
    .sort((a, b) => a.minutes - b.minutes);

  if (slotMinutes.length === 0) return slots[0];

  const first = slotMinutes[0];
  const last = slotMinutes[slotMinutes.length - 1];

  if (consumeMinutes < first.minutes || consumeMinutes >= last.minutes) {
    return last.slot;
  }

  for (let i = 0; i < slotMinutes.length - 1; i++) {
    const current = slotMinutes[i];
    const next = slotMinutes[i + 1];
    if (consumeMinutes >= current.minutes && consumeMinutes < next.minutes) {
      return current.slot;
    }
  }

  return slots[0];
}

async function updateDutyTimetableStatus() {
  try {
    const response = await fetch("/api/medication-tracking");
    const result = await response.json();

    if (!result.success || !Array.isArray(result.data)) return;

    const trackingRecords = result.data;

    // Loop through timetable cells and match with tracking data
    document.querySelectorAll(".timetable-cell").forEach((cell) => {
      const patientId = cell.getAttribute("data-patient-id");
      const timeSlot = cell.getAttribute("data-timeslot");
      const medName = cell.getAttribute("data-medicine");

      const recordFound = trackingRecords.some((r) => {
        if (r.patient_id !== patientId || r.medicine_name !== medName)
          return false;
        const resolvedSlot = resolveTrackingSlot(r);
        return resolvedSlot === timeSlot;
      });

      if (recordFound) {
        cell.classList.add("completed"); // Mark visually completed
        cell.textContent = "Completed"; // Update label if applicable
      }
    });
  } catch (err) {
    console.error("Error updating timetable from tracking:", err);
  }
}

function renderTimelineTable(grouped) {
  const container = document.querySelector("#timeline-tables");
  if (!container) {
    console.error("#timeline-tables container not found.");
    return;
  }

  container.innerHTML = "";
  const today = getLocalDateString();
  const currentHour = new Date().getHours();

  // Define time ranges for auto-expansion
  const shouldExpand = {
    "09:00": currentHour >= 4 && currentHour < 13, // 4:00 AM - 12:59 PM
    "13:00": currentHour >= 13 && currentHour < 17, // 1:00 PM - 4:59 PM
    "17:00": currentHour >= 17 && currentHour < 21, // 5:00 PM - 8:59 PM
    "21:00": currentHour >= 21 || currentHour < 4, // 9:00 PM - 3:59 AM
  };

  FIXED_TIME_SLOTS.forEach(({ value: slot, label }) => {
    const allMeds = grouped[slot] || [];
    const pendingCount = allMeds.filter((p) => !p.served).length;
    const accordionItem = document.createElement("div");
    accordionItem.className = "accordion-item";

    const header = document.createElement("div");
    header.className = "accordion-header";
    header.innerHTML = `⏰ ${label} (${pendingCount} pending)`;

    if (pendingCount > 0) {
      header.classList.add("has-pending");
    }

    const body = document.createElement("div");
    body.className = "accordion-body";

    // Auto-expand if it's the current time slot
    if (shouldExpand[slot]) {
      body.classList.add("active");
      header.classList.add("current-round");
    }

    if (allMeds.length === 0) {
      body.innerHTML =
        '<p class="text-center">No medications scheduled for this time slot</p>';
    } else {
      const table = document.createElement("table");
      table.className = "table table-sm table-bordered";

      const thead = document.createElement("thead");
      thead.innerHTML = `
        <tr>
          <th>Patient ID</th>
          <th>Medicine</th>
          <th>Floor</th>
          <th>Room</th>
          <th>Bed</th>
          <th>Status</th>
        </tr>
      `;

      const tbody = document.createElement("tbody");
      // Sort allMeds array - pending first, complete last
      const sortedMeds = allMeds.sort((a, b) => {
        if (a.served === b.served) return 0;
        return a.served ? 1 : -1; // Push served items to the bottom
      });

      sortedMeds.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${p.patient_id}</td>
          <td>${p.medicine_name || "N/A"}</td>
          <td>${p.floor}</td>
          <td>${p.room}</td>
          <td>${p.bed}</td>
          <td class="${p.served ? "text-success" : "text-warning"}">
            ${p.served ? "✔ Complete" : "⏳ Pending"}
          </td>
        `;
        tbody.appendChild(tr);
      });

      table.appendChild(thead);
      table.appendChild(tbody);
      body.appendChild(table);
    }

    // Only allow toggle for non-current rounds
    header.onclick = () => {
      if (!shouldExpand[slot]) {
        body.classList.toggle("active");
      }
    };

    accordionItem.appendChild(header);
    accordionItem.appendChild(body);
    container.appendChild(accordionItem);
  });

  if (!container.children.length) {
    container.innerHTML =
      '<p class="text-center">No medications scheduled for today</p>';
  }
}

function initManagementChart() {
  const ctx = document.getElementById("managementChart")?.getContext("2d");
  if (!ctx) return;

  if (managementChart) managementChart.destroy();

  const labels = FIXED_TIME_SLOTS.map((s) => s.label);

  managementChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Completed",
          backgroundColor: "#28a745",
          data: FIXED_TIME_SLOTS.map(() => 0),
          stack: "Stack 0",
        },
        {
          label: "Pending",
          backgroundColor: "#ffc107",
          data: FIXED_TIME_SLOTS.map(() => 0),
          stack: "Stack 0",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
      },
      plugins: {
        legend: { position: "top" },
        tooltip: { mode: "index", intersect: false },
      },
    },
  });

  updateManagementChart();
  if (managementChartTimer) clearInterval(managementChartTimer);
  managementChartTimer = setInterval(updateManagementChart, 60 * 1000);
  scheduleRoundRefresh();
}

function normalizeTimeSlot(slot) {
  if (!slot) return null;
  const firstPart = String(slot).split(",")[0].trim();
  if (!firstPart) return null;

  const lower = firstPart.toLowerCase();
  const match = lower.match(/^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/);
  if (match) {
    let hour = parseInt(match[1], 10);
    const minutes = match[2] ? match[2] : "00";
    const meridiem = match[3];

    if (meridiem === "pm" && hour < 12) hour += 12;
    if (meridiem === "am" && hour === 12) hour = 0;

    const hh = String(hour).padStart(2, "0");
    return `${hh}:${minutes}`;
  }

  return firstPart;
}

async function updateManagementChart() {
  if (!managementChart) return;

  try {
    const [prescRes, trackRes] = await Promise.all([
      fetch("/api/prescriptions"),
      fetch("/api/medication-tracking"),
    ]);
    if (!prescRes.ok || !trackRes.ok) return;

    const prescJson = await prescRes.json();
    const trackJson = await trackRes.json();

    const prescriptions = prescJson.data || [];
    const tracking = trackJson.data || [];

    const today = getLocalDateString();

    // Prepare counts per slot: index order matches FIXED_TIME_SLOTS
    const totals = FIXED_TIME_SLOTS.map(() => 0);
    const completed = FIXED_TIME_SLOTS.map(() => 0);

    function dateOnly(d) {
      if (!d) return null;
      // Handle both ISO (T) and space-separated timestamps
      const raw = String(d);
      return raw.includes("T") ? raw.split("T")[0] : raw.split(" ")[0];
    }

    prescriptions.forEach((p) => {
      const start = dateOnly(p.start_date);
      const end = dateOnly(p.end_date);

      // Only count if prescription is active today
      if (start && start > today) return;
      if (end && end < today) return;

      // Convert time_slot to array if stored as CSV
      let slots = [];
      if (Array.isArray(p.time_slot)) {
        slots = p.time_slot;
      } else if (typeof p.time_slot === "string" && p.time_slot.trim() !== "") {
        slots = p.time_slot
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
      }

      if (slots.length === 0) return;

      slots.forEach((rawSlot) => {
        const norm = normalizeTimeSlot(rawSlot);
        const idx = FIXED_TIME_SLOTS.findIndex((s) => s.value === norm);
        if (idx === -1) return;
        totals[idx] += 1;

        // Check if medication was served
        const servedHere = tracking.some((t) => {
          const tDate = dateOnly(t.consume_date);
          const tSlot = normalizeTimeSlot(t.time_slot);
          return (
            t.patient_id === p.patient_id &&
            t.medicine_name === p.medicine_name &&
            tDate === today &&
            tSlot === norm
          );
        });

        if (servedHere) completed[idx] += 1;
      });
    });

    const pending = totals.map((t, i) => Math.max(0, t - completed[i]));

    console.debug("Management chart counts:", {
      today,
      totals,
      completed,
      pending,
    });

    managementChart.data.datasets[0].data = completed;
    managementChart.data.datasets[1].data = pending;
    managementChart.update();
  } catch (err) {
    console.error("updateManagementChart error:", err);
  }
}

function scheduleRoundRefresh() {
  if (managementRoundTimeout) {
    clearTimeout(managementRoundTimeout);
    managementRoundTimeout = null;
  }

  // compute next occurrence of 09:00, 13:00, 17:00, 21:00
  const now = new Date();
  const targets = [9, 13, 17, 21].map((hour) => {
    const t = new Date(now);
    t.setHours(hour, 0, 0, 0);
    if (t <= now) t.setDate(t.getDate() + 1); // move to next day if time already passed
    return t;
  });

  // find soonest scheduled time
  let next = targets[0];
  targets.forEach((t) => {
    if (t < next) next = t;
  });

  const ms = next - now;
  managementRoundTimeout = setTimeout(() => {
    updateManagementChart().catch(() => {});
    scheduleRoundRefresh(); // schedule the next round
  }, ms + 250); // slight delay to ensure data consistency
}

// call initManagementChart when management dashboard shown
const originalShowDashboard = window.showDashboard;
window.showDashboard = function (dashboardId) {
  if (typeof originalShowDashboard === "function")
    originalShowDashboard(dashboardId);
  if (dashboardId === "managementDashboard") {
    // small delay to ensure DOM canvas exists
    setTimeout(() => initManagementChart(), 100);
  }
};

// also init on page load if management dashboard visible
document.addEventListener("DOMContentLoaded", () => {
  const mg = document.getElementById("managementDashboard");
  if (mg && mg.classList.contains("active")) {
    setTimeout(() => initManagementChart(), 100);
  }
});

// Make remaining functions globally available
// Dashboards
window.showDashboard = showDashboard;
window.showDutyTab = showDutyTab;
window.showTab = showTab;
window.loadPatients = loadPatients;
window.loadPrescriptions = loadPrescriptions;
window.loadTracking = loadTracking;
window.initManagementChart = initManagementChart;

// Prescription
window.addMedicineField = addMedicineField;
window.removeMedicineField = removeMedicineField;
window.addTimeField = addTimeField;
window.showPrescriptionPreview = showPrescriptionPreview;
