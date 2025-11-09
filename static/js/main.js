// Electronic Medication Administration Record - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  console.log("eMAR System Loaded");

  // Check API health
  checkAPIHealth();

  // Initialize event listeners
  initializeEventListeners();

  // Load initial data
  // The showDashboard function will trigger initial tab loading
  // Ensure the Nurse Dashboard is active by default
  showDashboard("dutyDashboard");
  loadPatients();
  loadPrescriptions();
  loadTracking();
  updateStats();
});

// Time slots options constant
const FIXED_TIME_SLOTS = [
  { value: "08:00", label: "8:00 AM" },
  { value: "13:00", label: "1:00 PM" },
  { value: "18:00", label: "6:00 PM" },
];

let managementChart = null;
let managementChartTimer = null;
let managementRoundTimeout = null;

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

window.showDashboard = showDashboard; // Expose globally

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

  // Append the new group
  container.appendChild(newGroup);
}
window.addMedicineField = addMedicineField;

function removeMedicineField(button) {
  // Traverse up to the parent '.medicine-group' and remove it
  button.closest(".medicine-group").remove();
}
window.removeMedicineField = removeMedicineField;

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

  // Add time slot options
  const options = [
    { value: "08:00", label: "8:00 AM" },
    { value: "13:00", label: "1:00 PM" },
    { value: "18:00", label: "6:00 PM" },
  ];

  options.forEach((opt) => {
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
}
window.addTimeField = addTimeField;

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
      !prescriptionData.start_date
    ) {
      showMessage(
        "error",
        `Skipping an incomplete medicine entry. Fill out required fields.`
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
      }
    } catch (error) {
      failureCount++;
      console.error("Error adding prescription entry:", error.message);
    }
  }

  // Show final status and reset form
  if (successCount > 0) {
    showMessage(
      "success",
      `${successCount} prescription(s) added successfully! (${failureCount} failed)`
    );
  } else {
    showMessage(
      "error",
      `Failed to add any prescriptions. ${failureCount} attempt(s) failed.`
    );
  }

  // Reset form and dynamic fields
  document.getElementById("prescriptionForm").reset();
  document.getElementById("medicineFieldsContainer").innerHTML = ""; // Clear all dynamic fields
  addMedicineField(); // Add one fresh field
  setTimeout(() => loadPrescriptions(), 2000);
}

// Utility Functions

function openModal(modalId) {
  document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}
window.closeModal = closeModal;

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
      data.start_date
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

window.showPrescriptionPreview = showPrescriptionPreview;

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
  const patientId = document.getElementById("patientSearchInput").value.trim();
  const resultContainer = document.getElementById("patientMedsResult");

  if (!patientId) {
    resultContainer.innerHTML = "<p>Please enter a patient ID</p>";
    return;
  }

  try {
    const res = await fetch(
      `/api/patient/${encodeURIComponent(patientId)}/prescriptions`
    );
    if (!res.ok) throw new Error("No prescriptions endpoint / data available");

    const data = await res.json();
    const meds = data.success && Array.isArray(data.data) ? data.data : [];

    const today = new Date().toISOString().split("T")[0];
    const activeMeds = meds.filter((m) => {
      if (!m.start_date) return false;
      if (m.start_date > today) return false;
      if (m.end_date && m.end_date < today) return false;
      return true;
    });

    if (activeMeds.length > 0) {
      resultContainer.innerHTML = activeMeds
        .map(
          (med) => `
        <div class="data-item">
          <strong>${med.medicine_name || "N/A"}</strong> - ${
            med.dosage || "N/A"
          } - ${med.frequency || "N/A"}<br>
          <small>From: ${med.start_date || "N/A"} To: ${
            med.end_date || "Ongoing"
          }</small>
        </div>`
        )
        .join("");
    } else {
      resultContainer.innerHTML = "<p>No active medications found</p>";
    }
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
        item.innerHTML = `
          <h4>${record.medicine_name || "N/A"} - Patient ID: ${
          record.patient_id || "N/A"
        }</h4>
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

// Patient Dashboard Lookup
async function lookupPatient() {
  const patientId = document.getElementById("lookup_patient_id").value;

  if (!patientId) {
    showMessage("error", "Please enter a Patient ID");
    return;
  }

  try {
    // Get patient info
    const patientResponse = await fetch(`/api/patient/${patientId}`);
    const patientResult = await patientResponse.json();

    // Get prescriptions
    const prescResponse = await fetch(
      `/api/patient/${patientId}/prescriptions`
    );
    const prescResult = await prescResponse.json();

    // Get tracking
    const trackResponse = await fetch(`/api/patient/${patientId}/tracking`);
    const trackResult = await trackResponse.json();

    if (patientResult.success) {
      document.getElementById("patientDashboard").style.display = "block";

      // Display patient info
      const patient = patientResult.data;
      document.getElementById("patientInfo").innerHTML = `
        <div class="info-grid">
          <div class="info-item"><strong>Name:</strong> ${
            patient.name || "N/A"
          }</div>
          <div class="info-item"><strong>Patient ID:</strong> ${
            patient.patient_id || "N/A"
          }</div>
          <div class="info-item"><strong>Age:</strong> ${
            patient.age || "N/A"
          }</div>
          <div class="info-item"><strong>Gender:</strong> ${
            patient.gender || "N/A"
          }</div>
          <div class="info-item"><strong>Floor:</strong> ${
            patient.floor || "N/A"
          }</div>
          <div class="info-item"><strong>Room:</strong> ${
            patient.room || "N/A"
          }</div>
          <div class="info-item"><strong>Bed:</strong> ${
            patient.bed || "N/A"
          }</div>
          <div class="info-item"><strong>Notes:</strong> ${
            patient.notes || "None"
          }</div>
        </div>
      `;

      // Display prescriptions
      if (prescResult.success && prescResult.data.length > 0) {
        let prescHTML = "";
        prescResult.data.forEach((presc) => {
          prescHTML += `
            <div class="data-item">
              <h4>${presc.medicine_name || "N/A"}</h4>
              <p><strong>Dosage:</strong> ${
                presc.dosage || "N/A"
              } | <strong>Frequency:</strong> ${presc.frequency || "N/A"}</p>
              <p><strong>Duration:</strong> ${presc.start_date || "N/A"} to ${
            presc.end_date || "Ongoing"
          }</p>
            </div>
          `;
        });
        document.getElementById("patientPrescriptions").innerHTML = prescHTML;
      } else {
        document.getElementById("patientPrescriptions").innerHTML =
          '<div class="empty-state">No prescriptions found</div>';
      }

      // Display tracking
      if (trackResult.success && trackResult.data.length > 0) {
        let trackHTML = "";
        trackResult.data.forEach((track) => {
          trackHTML += `
            <div class="data-item">
              <h4>${track.medicine_name || "N/A"}</h4>
              <p><strong>Dosage:</strong> ${track.dosage || "N/A"}</p>
              <p><strong>Administered:</strong> ${
                track.consume_date || "N/A"
              } at ${track.time_slot || "N/A"}</p>
            </div>
          `;
        });
        document.getElementById("patientTracking").innerHTML = trackHTML;
      } else {
        document.getElementById("patientTracking").innerHTML =
          '<div class="empty-state">No administration records found</div>';
      }
    } else {
      document.getElementById("patientDashboard").style.display = "none";
      showMessage("error", "Patient not found");
    }
  } catch (error) {
    showMessage("error", "Error looking up patient: " + error.message);
  }
}
window.lookupPatient = lookupPatient; // Expose globally

// Update Statistics
async function updateStats() {
  try {
    // Get patients count
    const patientsResponse = await fetch("/api/patients");
    const patientsResult = await patientsResponse.json();
    const patientsCount = patientsResult.success
      ? patientsResult.data.length
      : 0;
    document.getElementById("totalPatients").textContent = patientsCount;

    // Get prescriptions count
    const prescResponse = await fetch("/api/prescriptions");
    const prescResult = await prescResponse.json();
    const prescCount = prescResult.success ? prescResult.data.length : 0;
    document.getElementById("totalPrescriptions").textContent = prescCount;

    // Get today's administrations
    const trackResponse = await fetch("/api/medication-tracking");
    const trackResult = await trackResponse.json();
    const today = new Date().toISOString().split("T")[0];
    let todayCount = 0;
    if (trackResult.success) {
      todayCount = trackResult.data.filter(
        (record) => record.consume_date === today
      ).length;
    }
    document.getElementById("todayAdministrations").textContent = todayCount;
  } catch (error) {
    console.error("Error updating stats:", error);
  }
}

// Utility Functions
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleString();
}

function showMessage(type, message) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type}`;
  messageDiv.textContent = message;

  const main = document.querySelector("main");
  main.insertBefore(messageDiv, main.firstChild);

  setTimeout(() => {
    messageDiv.remove();
  }, 5000);
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
window.showDutyTab = showDutyTab;

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

    // Create patients lookup map
    const patientsMap = new Map(patients.map((p) => [p.patient_id, p]));

    // Group by time slot with patient details
    const grouped = {};
    prescriptions.forEach((p) => {
      const patient = patientsMap.get(p.patient_id) || {};
      const slots = (p.time_slot || "Unknown").split(",").map((s) => s.trim());

      slots.forEach((slot) => {
        if (!grouped[slot]) grouped[slot] = [];
        grouped[slot].push({
          patient_id: p.patient_id,
          floor: patient.floor || "N/A",
          room: patient.room || "N/A",
          bed: patient.bed || "N/A",
          served: isServed(p, tracking),
        });
      });
    });

    renderTimelineTable(grouped);
  } catch (err) {
    container.innerHTML = `<p class="error">Failed to load Duty Dashboard: ${err.message}</p>`;
    console.error("Duty Dashboard Error:", err);
  }
}

function isServed(prescription, tracking) {
  const today = new Date().toISOString().split("T")[0];
  return tracking.some(
    (t) =>
      t.patient_id === prescription.patient_id &&
      t.medicine_name === prescription.medicine_name &&
      t.time_slot === prescription.time_slot &&
      t.consume_date === today
  );
}

function renderTimelineTable(grouped) {
  const container = document.querySelector("#timeline-tables");
  if (!container) {
    console.error("#timeline-tables container not found.");
    return;
  }

  container.innerHTML = "";
  const today = new Date().toISOString().split("T")[0];
  const currentHour = new Date().getHours();

  // Define time ranges for auto-expansion
  const shouldExpand = {
    "08:00": currentHour >= 4 && currentHour < 13, // 4:00 AM - 12:59 PM
    "13:00": currentHour >= 13 && currentHour < 18, // 1:00 PM - 5:59 PM
    "18:00": currentHour >= 18 || currentHour < 4, // 6:00 PM - 3:59 AM
  };

  FIXED_TIME_SLOTS.forEach(({ value: slot, label }) => {
    const medsToday = (grouped[slot] || []).filter((p) => !p.served);
    const accordionItem = document.createElement("div");
    accordionItem.className = "accordion-item";

    const header = document.createElement("div");
    header.className = "accordion-header";
    header.innerHTML = `⏰ ${label} (${medsToday.length} pending)`;

    if (medsToday.length > 0) {
      header.classList.add("has-pending");
    }

    const body = document.createElement("div");
    body.className = "accordion-body";

    // Auto-expand if it's the current time slot
    if (shouldExpand[slot]) {
      body.classList.add("active");
      header.classList.add("current-round");
    }

    if (medsToday.length === 0) {
      body.innerHTML =
        '<p class="text-center">No pending medications for this time slot</p>';
    } else {
      const table = document.createElement("table");
      table.className = "table table-sm table-bordered";

      const thead = document.createElement("thead");
      thead.innerHTML = `
        <tr>
          <th>Patient ID</th>
          <th>Floor</th>
          <th>Room</th>
          <th>Bed</th>
          <th>Status</th>
        </tr>
      `;

      const tbody = document.createElement("tbody");
      // Sort medsToday array - pending first, served last
      const sortedMeds = medsToday.sort((a, b) => {
        if (a.served === b.served) return 0;
        return a.served ? 1 : -1; // Push served items to the bottom
      });

      sortedMeds.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${p.patient_id}</td>
          <td>${p.floor}</td>
          <td>${p.room}</td>
          <td>${p.bed}</td>
          <td class="${p.served ? "text-success" : "text-warning"}">
            ${p.served ? "✔ Served" : "⏳ Pending"}
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
          data: [0, 0, 0],
          stack: "Stack 0",
        },
        {
          label: "Pending",
          backgroundColor: "#ffc107",
          data: [0, 0, 0],
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

window.initManagementChart = initManagementChart;

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

    const today = new Date().toISOString().split("T")[0];

    // Prepare counts per slot: index order matches FIXED_TIME_SLOTS
    const totals = FIXED_TIME_SLOTS.map(() => 0);
    const completed = FIXED_TIME_SLOTS.map(() => 0);

    // helper: normalize various slot formats to canonical values
    function normalizeSlotToken(tok) {
      if (!tok && tok !== 0) return "";
      let s = String(tok).trim().toLowerCase();
      // common exact forms
      if (
        s === "08:00" ||
        s === "8:00" ||
        s === "8:00 am" ||
        s === "8am" ||
        s === "8 am" ||
        s === "8"
      )
        return "08:00";
      if (
        s === "13:00" ||
        s === "1:00" ||
        s === "1:00 pm" ||
        s === "1pm" ||
        s === "1 pm" ||
        s === "13"
      )
        return "13:00";
      if (
        s === "18:00" ||
        s === "6:00" ||
        s === "6:00 pm" ||
        s === "6pm" ||
        s === "6 pm" ||
        s === "18"
      )
        return "18:00";
      // try to match numbers
      if (s.match(/^8\b/)) return "08:00";
      if (s.match(/^13\b/) || s.match(/^1\b/)) return "13:00";
      if (s.match(/^18\b/) || s.match(/^6\b/)) return "18:00";
      // fallback: return upper-case token if already exact
      const up = tok.toString().trim().toUpperCase();
      if (["08:00", "13:00", "18:00"].includes(up)) return up;
      return "";
    }

    // helper: extract YYYY-MM-DD from date-like string
    function dateOnly(d) {
      if (!d) return null;
      return String(d).split("T")[0];
    }

    // Count prescriptions per normalized slot
    prescriptions.forEach((p) => {
      const start = dateOnly(p.start_date);
      const end = dateOnly(p.end_date);
      // active today?
      if (start && start > today) return;
      if (end && end < today) return;

      // support array or comma-separated string for time_slot
      let slots = [];
      if (Array.isArray(p.time_slot)) slots = p.time_slot;
      else if (typeof p.time_slot === "string" && p.time_slot.trim() !== "") {
        slots = p.time_slot
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
      }

      // if no slots defined, skip (or optionally count them under a default bucket)
      if (slots.length === 0) return;

      slots.forEach((raw) => {
        const norm = normalizeSlotToken(raw);
        const idx = FIXED_TIME_SLOTS.findIndex((s) => s.value === norm);
        if (idx === -1) return;
        totals[idx] += 1;

        // check if served: normalize tracking entries similarly
        const servedHere = tracking.some((t) => {
          const tDate = dateOnly(t.consume_date);
          const tSlotNorm = normalizeSlotToken(t.time_slot);
          return (
            t.patient_id === p.patient_id &&
            t.medicine_name === p.medicine_name &&
            tDate === today &&
            tSlotNorm === norm
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
    // update chart datasets
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

  // compute next occurrence of 08:00, 13:00, 18:00
  const now = new Date();
  const targets = [8, 13, 18].map((hour) => {
    const t = new Date(now);
    t.setHours(hour, 0, 0, 0);
    if (t <= now) t.setDate(t.getDate() + 1); // next day if passed
    return t;
  });

  // find nearest target
  let next = targets[0];
  targets.forEach((t) => {
    if (t < next) next = t;
  });

  const ms = next - now;
  managementRoundTimeout = setTimeout(() => {
    updateManagementChart().catch(() => {});
    // reschedule next round refresh
    scheduleRoundRefresh();
  }, ms + 250); // slight offset to let server state settle
}

// call initManagementChart when management dashboard shown
// ensure this runs when Dashboard is displayed
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
window.showTab = showTab;
window.loadPatients = loadPatients;
window.loadPrescriptions = loadPrescriptions;
window.loadTracking = loadTracking;
