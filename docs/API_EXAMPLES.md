# API Usage Examples

This guide provides practical examples for using the eMAR API with various tools and languages.

## Table of Contents

- [Quick Start](#quick-start)
- [Using Swagger UI](#using-swagger-ui)
- [curl Examples](#curl-examples)
- [PowerShell Examples](#powershell-examples)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [Error Handling](#error-handling)

---

## Quick Start

### Base URL

```
http://localhost:5000
```

For network access, replace `localhost` with your server's IP address.

### Authentication

Currently, the API does not require authentication. This is suitable for development but should be implemented for production use.

### Response Format

All API responses follow a consistent JSON format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Using Swagger UI

The easiest way to explore and test the API is through the interactive Swagger UI:

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open Swagger UI:**
   Navigate to http://localhost:5000/api/docs

3. **Explore endpoints:**
   - Click on any endpoint to expand it
   - View request/response schemas
   - See example payloads

4. **Test endpoints:**
   - Click "Try it out" button
   - Fill in parameters or request body
   - Click "Execute"
   - View the response

---

## curl Examples

### Health Check

```bash
curl -X GET http://localhost:5000/api/health
```

### Get All Patients

```bash
curl -X GET http://localhost:5000/api/patients
```

### Get Specific Patient

```bash
curl -X GET http://localhost:5000/api/patient/P001
```

### Add a Patient

```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "name": "John Doe",
    "floor": "3",
    "room": "301",
    "bed": "A",
    "age": "45",
    "gender": "Male",
    "notes": "Diabetic patient"
  }'
```

### Check if Patient Exists

```bash
curl -X GET http://localhost:5000/api/check_patient/P001
```

### Get Patient Prescriptions

```bash
curl -X GET http://localhost:5000/api/patient/P001/prescriptions
```

### Get All Prescriptions

```bash
curl -X GET http://localhost:5000/api/prescriptions
```

### Add a Prescription (Queued)

```bash
curl -X POST http://localhost:5000/api/prescriptions \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "medicine_name": "Metformin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "start_date": "2025-10-30",
    "end_date": "2025-11-30",
    "time_slot": "8AM, 8PM"
  }'
```

**Note:** Returns HTTP 202 (Accepted) - prescription is queued for background processing.

### Get All Medication Tracking Records

```bash
curl -X GET http://localhost:5000/api/medication-tracking
```

### Record Medication Administration

```bash
curl -X POST http://localhost:5000/api/medication-tracking \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "medicine_name": "Metformin",
    "dosage": "500mg",
    "consume_date": "2025-11-15 17:16:27",
    "time_slot": "09:00, 13:00, 17:00, 21:00"
  }'
```

### Get Patient Tracking History

```bash
curl -X GET http://localhost:5000/api/patient/P001/tracking
```

### Get Queue Status

```bash
curl -X GET http://localhost:5000/api/queue/status
```

### Clear Failed Queue Items

```bash
curl -X POST http://localhost:5000/api/queue/clear-failed
```

### Pretty Print JSON Response

```bash
curl -X GET http://localhost:5000/api/patients | python -m json.tool
```

Or use `jq` if available:

```bash
curl -X GET http://localhost:5000/api/patients | jq
```

---

## PowerShell Examples

### Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/health"
```

### Get All Patients

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/patients"
```

### Get Specific Patient

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/patient/P001"
```

### Add a Patient

```powershell
$patientData = @{
    patient_id = "P001"
    name = "John Doe"
    floor = "3"
    room = "301"
    bed = "A"
    age = "45"
    gender = "Male"
    notes = "Diabetic patient"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/patients" `
  -Method Post `
  -Body $patientData `
  -ContentType "application/json"
```

### Add a Prescription

```powershell
$prescriptionData = @{
    patient_id = "P001"
    medicine_name = "Metformin"
    dosage = "500mg"
    frequency = "Twice daily"
    start_date = "2025-10-30"
    end_date = "2025-11-30"
    time_slot = "8AM, 8PM"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/prescriptions" `
  -Method Post `
  -Body $prescriptionData `
  -ContentType "application/json"
```

### Record Medication Administration

```powershell
$trackingData = @{
    patient_id = "P001"
    medicine_name = "Metformin"
    dosage = "500mg"
    consume_date = "2025-11-15 17:16:27"
    time_slot = "09:00, 13:00, 17:00, 21:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/medication-tracking" `
  -Method Post `
  -Body $trackingData `
  -ContentType "application/json"
```

### Get Queue Status

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/queue/status"
```

### Error Handling in PowerShell

```powershell
try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/api/patient/P999" `
      -ErrorAction Stop
    Write-Host "Patient found: $($result.data.name)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "Error: HTTP $statusCode"
    Write-Host $_.ErrorDetails.Message
}
```

---

## Python Examples

### Using requests Library

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Health Check
def check_health():
    response = requests.get(f"{BASE_URL}/api/health")
    return response.json()

# Get All Patients
def get_patients():
    response = requests.get(f"{BASE_URL}/api/patients")
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error: {response.status_code}")
        return None

# Get Specific Patient
def get_patient(patient_id):
    response = requests.get(f"{BASE_URL}/api/patient/{patient_id}")
    if response.status_code == 200:
        return response.json()["data"]
    elif response.status_code == 404:
        print(f"Patient {patient_id} not found")
        return None
    else:
        print(f"Error: {response.status_code}")
        return None

# Add a Patient
def add_patient(patient_data):
    response = requests.post(
        f"{BASE_URL}/api/patients",
        json=patient_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
if __name__ == "__main__":
    # Add a patient
    patient = {
        "patient_id": "P001",
        "name": "John Doe",
        "floor": "3",
        "room": "301",
        "bed": "A",
        "age": "45",
        "gender": "Male",
        "notes": "Diabetic patient"
    }
    
    result = add_patient(patient)
    if result and result["success"]:
        print(f"Patient added successfully! Entry ID: {result['data']['entry_id']}")
    
    # Get patient details
    patient_data = get_patient("P001")
    if patient_data:
        print(f"Patient: {patient_data['name']}, Age: {patient_data['age']}")
```

### Add Prescription

```python
def add_prescription(prescription_data):
    response = requests.post(
        f"{BASE_URL}/api/prescriptions",
        json=prescription_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Prescriptions return HTTP 202 (Accepted)
    if response.status_code == 202:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
prescription = {
    "patient_id": "P001",
    "medicine_name": "Metformin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "start_date": "2025-10-30",
    "end_date": "2025-11-30",
    "time_slot": "8AM, 8PM"
}

result = add_prescription(prescription)
if result:
    print(f"Prescription queued: {result['message']}")
```

### Record Medication Administration

```python
from datetime import datetime

def record_medication(tracking_data):
    response = requests.post(
        f"{BASE_URL}/api/medication-tracking",
        json=tracking_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
tracking = {
    "patient_id": "P001",
    "medicine_name": "Metformin",
    "dosage": "500mg",
    "consume_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "time_slot": "09:00, 13:00, 17:00, 21:00"
}

result = record_medication(tracking)
if result and result["success"]:
    print(f"Medication recorded! Entry ID: {result['data']['entry_id']}")
```

### Get Queue Status

```python
def get_queue_status():
    response = requests.get(f"{BASE_URL}/api/queue/status")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"Queue Size: {data['queue_size']}")
        print(f"Failed Count: {data['failed_count']}")
        print(f"Statistics: {data['stats']}")
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
queue_status = get_queue_status()
```

### Error Handling

```python
def safe_api_call(url, method="GET", json_data=None):
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=10)
        
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection Error: Unable to connect to the API")
    except requests.exceptions.Timeout:
        print("Timeout Error: Request took too long")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    
    return None

# Example usage
result = safe_api_call(f"{BASE_URL}/api/patients")
if result:
    print(f"Found {len(result['data'])} patients")
```

---

## JavaScript Examples

### Using Fetch API

```javascript
const BASE_URL = "http://localhost:5000";

// Health Check
async function checkHealth() {
  try {
    const response = await fetch(`${BASE_URL}/api/health`);
    const data = await response.json();
    console.log("API Status:", data.status);
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
}

// Get All Patients
async function getPatients() {
  try {
    const response = await fetch(`${BASE_URL}/api/patients`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Error fetching patients:", error);
  }
}

// Get Specific Patient
async function getPatient(patientId) {
  try {
    const response = await fetch(`${BASE_URL}/api/patient/${patientId}`);
    if (response.status === 404) {
      console.log(`Patient ${patientId} not found`);
      return null;
    }
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Error fetching patient:", error);
  }
}

// Add a Patient
async function addPatient(patientData) {
  try {
    const response = await fetch(`${BASE_URL}/api/patients`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(patientData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    const data = await response.json();
    console.log("Patient added:", data.data.entry_id);
    return data;
  } catch (error) {
    console.error("Error adding patient:", error);
  }
}

// Example usage
(async () => {
  const patient = {
    patient_id: "P001",
    name: "John Doe",
    floor: "3",
    room: "301",
    bed: "A",
    age: "45",
    gender: "Male",
    notes: "Diabetic patient",
  };
  
  const result = await addPatient(patient);
  if (result && result.success) {
    console.log("Success!");
  }
})();
```

### Add Prescription

```javascript
async function addPrescription(prescriptionData) {
  try {
    const response = await fetch(`${BASE_URL}/api/prescriptions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(prescriptionData),
    });
    
    // Prescriptions return HTTP 202 (Accepted)
    if (response.status !== 202) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    const data = await response.json();
    console.log("Prescription queued:", data.message);
    return data;
  } catch (error) {
    console.error("Error adding prescription:", error);
  }
}

// Example usage
const prescription = {
  patient_id: "P001",
  medicine_name: "Metformin",
  dosage: "500mg",
  frequency: "Twice daily",
  start_date: "2025-10-30",
  end_date: "2025-11-30",
  time_slot: "8AM, 8PM",
};

addPrescription(prescription);
```

### Record Medication Administration

```javascript
async function recordMedication(trackingData) {
  try {
    const response = await fetch(`${BASE_URL}/api/medication-tracking`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(trackingData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    const data = await response.json();
    console.log("Medication recorded:", data.data.entry_id);
    return data;
  } catch (error) {
    console.error("Error recording medication:", error);
  }
}

// Example usage with current timestamp
const tracking = {
  patient_id: "P001",
  medicine_name: "Metformin",
  dosage: "500mg",
  consume_date: new Date().toISOString().slice(0, 19).replace("T", " "),
  time_slot: "09:00, 13:00, 17:00, 21:00",
};

recordMedication(tracking);
```

### Get Queue Status

```javascript
async function getQueueStatus() {
  try {
    const response = await fetch(`${BASE_URL}/api/queue/status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    const data = result.data;
    
    console.log("Queue Status:");
    console.log(`  Queue Size: ${data.queue_size}`);
    console.log(`  Failed Count: ${data.failed_count}`);
    console.log(`  Total Processed: ${data.stats.total_processed}`);
    
    return data;
  } catch (error) {
    console.error("Error fetching queue status:", error);
  }
}

getQueueStatus();
```

### Complete Example with Error Handling

```javascript
class EmarAPI {
  constructor(baseUrl = "http://localhost:5000") {
    this.baseUrl = baseUrl;
  }
  
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }
  
  async getPatients() {
    const result = await this.request("/api/patients");
    return result.data;
  }
  
  async getPatient(patientId) {
    const result = await this.request(`/api/patient/${patientId}`);
    return result.data;
  }
  
  async addPatient(patientData) {
    const result = await this.request("/api/patients", {
      method: "POST",
      body: JSON.stringify(patientData),
    });
    return result;
  }
  
  async addPrescription(prescriptionData) {
    const result = await this.request("/api/prescriptions", {
      method: "POST",
      body: JSON.stringify(prescriptionData),
    });
    return result;
  }
  
  async recordMedication(trackingData) {
    const result = await this.request("/api/medication-tracking", {
      method: "POST",
      body: JSON.stringify(trackingData),
    });
    return result;
  }
  
  async getQueueStatus() {
    const result = await this.request("/api/queue/status");
    return result.data;
  }
}

// Usage
const api = new EmarAPI();

(async () => {
  try {
    const patients = await api.getPatients();
    console.log(`Found ${patients.length} patients`);
    
    const patient = await api.getPatient("P001");
    console.log("Patient:", patient.name);
  } catch (error) {
    console.error("Error:", error.message);
  }
})();
```

---

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **202 Accepted**: Request accepted (prescriptions - queued for processing)
- **400 Bad Request**: Invalid input data
- **404 Not Found**: Resource not found (e.g., patient doesn't exist)
- **429 Too Many Requests**: Rate limit exceeded (ThingSpeak limitation)
- **500 Internal Server Error**: Server error (check logs)
- **507 Insufficient Storage**: Queue is full (max 1000 items)

### Error Response Format

All errors return a JSON response:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

### Common Validation Errors

**Missing Required Field:**
```json
{
  "success": false,
  "error": "Missing required field: patient_id"
}
```

**Invalid Format:**
```json
{
  "success": false,
  "error": "Invalid dosage format. Expected format: '500mg', '10ml', etc."
}
```

**Patient Not Found:**
```json
{
  "success": false,
  "error": "Patient P999 does not exist. Please add the patient first."
}
```

### Rate Limiting

ThingSpeak has a rate limit of 1 write per 15 seconds per channel:

- **Patients**: Direct write, 15s wait enforced
- **Prescriptions**: Queued, no waiting (HTTP 202)
- **Tracking**: Direct write, 15s wait enforced

If you hit the rate limit, you'll see an error. Wait 15 seconds before retrying.

---

## Additional Resources

- **[Interactive API Documentation](http://localhost:5000/api/docs)**: Swagger UI
- **[Architecture Guide](ARCHITECTURE.md)**: System design and data flow
- **[Deployment Guide](DEPLOYMENT.md)**: Setup and deployment instructions
- **[Contributing Guide](../CONTRIBUTING.md)**: Development guidelines

---

*Last Updated: November 15, 2025*
