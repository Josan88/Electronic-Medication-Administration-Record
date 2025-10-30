// Electronic Medication Administration Record - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  console.log("eMAR System Loaded");

  // Check API health
  checkAPIHealth();

  // Initialize event listeners
  initializeEventListeners();

  // Load initial data
  loadPatients();
  loadPrescriptions();
  loadTracking();
  updateStats();
});

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

  // Prescription Form
  document
    .getElementById("prescriptionForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      await addPrescription();
    });

  // Tracking Form
  document
    .getElementById("trackingForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      await addTracking();
    });

  // Set default date to today
  const today = new Date().toISOString().split("T")[0];
  document.getElementById("start_date").value = today;
  document.getElementById("consume_date").value = today;
}

// Tab Navigation
function showTab(tabName) {
  // Hide all tabs
  const tabs = document.querySelectorAll(".tab-content");
  tabs.forEach((tab) => {
    tab.classList.remove("active");
  });

  // Remove active class from all buttons
  const buttons = document.querySelectorAll(".tab-button");
  buttons.forEach((button) => {
    button.classList.remove("active");
  });

  // Show selected tab
  document.getElementById(tabName).classList.add("active");

  // Activate button
  event.target.classList.add("active");

  // Load data for the tab
  if (tabName === "patients") {
    loadPatients();
  } else if (tabName === "prescriptions") {
    loadPrescriptions();
  } else if (tabName === "tracking") {
    loadTracking();
  } else if (tabName === "dashboard") {
    updateStats();
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
      result.data.reverse().forEach((patient) => {
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

// Prescription Management
async function addPrescription() {
  const prescriptionData = {
    patient_id: document.getElementById("presc_patient_id").value,
    medicine_name: document.getElementById("medicine_name").value,
    dosage: document.getElementById("dosage").value,
    frequency: document.getElementById("frequency").value,
    start_date: document.getElementById("start_date").value,
    end_date: document.getElementById("end_date").value,
    time_slot: document.getElementById("time_slot").value,
  };

  try {
    const response = await fetch("/api/prescriptions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prescriptionData),
    });

    const result = await response.json();

    if (result.success) {
      showMessage("success", "Prescription added successfully!");
      document.getElementById("prescriptionForm").reset();
      const today = new Date().toISOString().split("T")[0];
      document.getElementById("start_date").value = today;
      setTimeout(() => loadPrescriptions(), 2000);
    } else {
      showMessage("error", "Error: " + result.error);
    }
  } catch (error) {
    showMessage("error", "Error adding prescription: " + error.message);
  }
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
      result.data.reverse().forEach((prescription) => {
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

// Medication Tracking
async function addTracking() {
  const trackingData = {
    patient_id: document.getElementById("track_patient_id").value,
    medicine_name: document.getElementById("track_medicine_name").value,
    dosage: document.getElementById("track_dosage").value,
    consume_date: document.getElementById("consume_date").value,
    time_slot: document.getElementById("track_time_slot").value,
  };

  try {
    const response = await fetch("/api/medication-tracking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trackingData),
    });

    const result = await response.json();

    if (result.success) {
      showMessage(
        "success",
        "Medication administration recorded successfully!"
      );
      document.getElementById("trackingForm").reset();
      const today = new Date().toISOString().split("T")[0];
      document.getElementById("consume_date").value = today;
      setTimeout(() => loadTracking(), 2000);
    } else {
      showMessage("error", "Error: " + result.error);
    }
  } catch (error) {
    showMessage("error", "Error recording administration: " + error.message);
  }
}

async function loadTracking() {
  const listElement = document.getElementById("trackingList");
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

// Make functions globally available
window.showTab = showTab;
window.loadPatients = loadPatients;
window.loadPrescriptions = loadPrescriptions;
window.loadTracking = loadTracking;
window.lookupPatient = lookupPatient;
