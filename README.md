# Electronic Medication Administration Record (eMAR)

A comprehensive web-based Electronic Medication Administration Record system that integrates with ThingSpeak IoT platform for real-time data storage and retrieval.

## 🌟 Features

- **Patient Management**: Add, view, and manage patient information
- **Medicine Prescriptions**: Track prescribed medications with dosage, frequency, and duration
- **Medication Tracking**: Record and monitor medication administration in real-time
- **Dashboard**: Quick lookup for patient information with complete medication history
- **Real-time Sync**: Data stored on ThingSpeak cloud platform for accessibility anywhere
- **Statistics**: Visual overview of total patients, prescriptions, and daily administrations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for ThingSpeak API)

### Installation & Setup

1. **Clone the repository:**

   ```powershell
   git clone https://github.com/Josan88/Electronic-Medication-Administration-Record.git
   cd Electronic-Medication-Administration-Record
   ```

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   - Create a `.env` file in the project root
   - Add your ThingSpeak API keys (see Environment Variables section below)

4. **Start the application:**

   ```powershell
   python app.py
   ```

5. **Open your browser:**
   Navigate to **http://localhost:5000**

### First-Time Usage

#### 1. Add Your First Patient

- Click on **"Patient Management"** tab
- Fill in the form with patient details:
  - Patient ID: P001
  - Name: John Doe
  - Floor, Room, Bed details
  - Age, Gender, Notes
- Click **"Add Patient"**
- Wait 2-3 seconds, then click **"Refresh"**

#### 2. Create a Prescription

- Go to **"Prescriptions"** tab
- Enter prescription details:
  - Patient ID: P001
  - Medicine Name: Metformin
  - Dosage: 500mg
  - Frequency: Twice daily
  - Start/End Date, Time Slot
- Click **"Add Prescription"**
- Prescription is queued automatically - wait ~15 seconds for background processing
- Click **"Refresh"** to see the new prescription

#### 3. Record Medication Administration

- Open **"Medication Tracking"** tab
- Enter administration details
- Click **"Record Administration"**
- Wait 15 seconds, then refresh

#### 4. Use the Dashboard

- Go to **"Dashboard"** tab
- Enter Patient ID and click **"Search"**
- View complete patient history

## 💻 Technology Stack

- **Backend**: Flask 3.0.0 (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6+)
- **Data Storage**: ThingSpeak IoT Platform (Cloud-based, no local database)
- **API**: RESTful API design
- **Concurrency**: Threading module for background queue processing

## ThingSpeak Integration

The system uses three ThingSpeak channels:

### 1. Patient Information Channel (ID: 3124887)

**Fields:**

- Field1: Patient_ID
- Field2: Name
- Field3: Floor
- Field4: Room
- Field5: Bed
- Field6: Age
- Field7: Gender
- Field8: Notes

### 2. Medicine Prescription Channel (ID: 3124898)

**Fields:**

- Field1: Patient_ID
- Field2: Medicine_Name
- Field3: Dosage
- Field4: Frequency
- Field5: Start_Date
- Field6: End_Date
- Field7: Time_Slot

### 3. Medicine Prescription Track Channel (ID: 3131200)

**Fields:**

- Field1: Patient_ID
- Field2: Medicine_Name
- Field3: Dosage
- Field4: Consume_Date
- Field5: Time_Slot

## 📱 Accessing the Application

### From Same Computer

- URL: http://localhost:5000

### From Other Devices (Same Network)

- URL: http://YOUR_IP:5000
- Find your IP: Run `ipconfig` in PowerShell
- Example: http://192.168.1.100:5000

## API Endpoints

### Health Check

- **GET** `/api/health` - Check API status

### Patient Management

- **GET** `/api/patients` - Get all patients
- **POST** `/api/patients` - Add new patient
- **GET** `/api/patient/<patient_id>` - Get specific patient
- **GET** `/api/patient/<patient_id>/prescriptions` - Get patient prescriptions
- **GET** `/api/patient/<patient_id>/tracking` - Get patient medication history

### Prescriptions

- **GET** `/api/prescriptions` - Get all prescriptions
- **POST** `/api/prescriptions` - Add new prescription (returns HTTP 202, queued for background processing)
- **GET** `/api/check_patient/<patient_id>` - Check if patient exists

### Medication Tracking

- **GET** `/api/medication-tracking` - Get all tracking records
- **POST** `/api/medication-tracking` - Add new tracking record

### Queue Management

- **GET** `/api/queue/status` - Get current queue status (size, failed items, statistics)
- **POST** `/api/queue/clear-failed` - Clear all failed items from the queue

## 🧪 Testing the API

### Method 1: Web Interface (Recommended)

Simply use the web interface at http://localhost:5000

### Method 2: PowerShell Commands

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# Get All Patients
Invoke-RestMethod -Uri "http://localhost:5000/api/patients"

# Add a Patient
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

Invoke-RestMethod -Uri "http://localhost:5000/api/patients" -Method Post -Body $patientData -ContentType "application/json"
```

### Method 3: Automated Test Script

```powershell
# Run comprehensive test suite (takes ~50 seconds due to rate limits)
python test_api.py

# To test from another device on the network:
# Edit BASE_URL in test_api.py line 12 first
# Change from "http://localhost:5000" to "http://YOUR_IP:5000"
```

**Note**: Test script includes automatic 15-second delays between write operations to comply with ThingSpeak rate limits

## 📋 API Request Examples

### Add a Patient

```json
POST /api/patients
{
  "patient_id": "P001",
  "name": "John Doe",
  "floor": "3",
  "room": "301",
  "bed": "A",
  "age": "45",
  "gender": "Male",
  "notes": "Diabetic patient"
}
```

### Add a Prescription

```json
POST /api/prescriptions
{
  "patient_id": "P001",
  "medicine_name": "Metformin",
  "dosage": "500mg",
  "frequency": "Twice daily",
  "start_date": "2025-10-30",
  "end_date": "2025-11-30",
  "time_slot": "8AM, 8PM"
}
```

### Record Medication Administration

```json
POST /api/medication-tracking
{
  "patient_id": "P001",
  "medicine_name": "Metformin",
  "dosage": "500mg",
  "consume_date": "2025-10-30",
  "time_slot": "08:00"
}
```

## ⚠️ Important Notes

### ThingSpeak Rate Limits

- **Free tier**: 1 update every 15 seconds **per channel**
- **Prescriptions**: Use background queue system - no waiting required (HTTP 202 response)
- **Patients & Tracking**: Direct write to ThingSpeak - 15-second wait enforced per channel
- Data appears after 2-3 second sync delay

### Data Persistence

- All data is stored on ThingSpeak cloud (no local database)
- Data persists even after closing the application
- **Prescription queue is now persistent** - queued items are saved to `/tmp/prescription_queue.json` and survive app restarts
- Failed prescriptions are tracked and automatically retried (max 3 attempts)
- Queue status and statistics available via `/api/queue/status` endpoint
- Refresh the page to see latest data

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-flask-secret-key
PATIENT_CHANNEL_ID=3124887
PATIENT_WRITE_KEY=your-patient-write-key
PATIENT_READ_KEY=your-patient-read-key
PRESCRIPTION_CHANNEL_ID=3124898
PRESCRIPTION_WRITE_KEY=your-prescription-write-key
PRESCRIPTION_READ_KEY=your-prescription-read-key
TRACKING_CHANNEL_ID=3131200
TRACKING_WRITE_KEY=your-tracking-write-key
TRACKING_READ_KEY=your-tracking-read-key
```

### Browser Compatibility

- Works best in modern browsers (Chrome, Firefox, Edge, Safari)
- JavaScript must be enabled

## Project Structure

```
Electronic-Medication-Administration-Record/
├── app.py                      # Flask backend with REST API & background worker
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies (Flask, requests, python-dotenv)
├── README.md                   # Project documentation
├── IMPROVEMENTS.md             # Implementation summary and task tracking
├── VALIDATION_IMPLEMENTATION.md # Input validation documentation
├── .env                        # Environment variables (ThingSpeak API keys)
├── .github/
│   └── copilot-instructions.md # AI coding agent guidelines
├── services/
│   ├── thingspeak_service.py  # Data access layer for ThingSpeak
│   └── queue_service.py       # Persistent queue management
├── routes/
│   ├── __init__.py            # Blueprint registration
│   ├── patients.py            # Patient management routes
│   ├── prescriptions.py       # Prescription routes
│   ├── tracking.py            # Medication tracking routes
│   └── queue.py               # Queue monitoring routes
├── validators/
│   ├── patient_validator.py   # Patient data validation
│   ├── prescription_validator.py # Prescription validation
│   └── tracking_validator.py  # Medication tracking validation
├── utils/
│   ├── errors.py              # Error handling utilities
│   └── logging_config.py      # Logging configuration
├── static/
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── main.js            # Frontend JavaScript (AJAX, dashboard switching)
├── templates/
│   └── index.html             # Single-page application (3 dashboards)
└── tests/
    ├── test_blueprints.py     # Blueprint architecture tests
    ├── test_validation.py     # Validation unit tests
    ├── test_api_validation.py # API validation integration tests
    ├── test_queue_management.py # Queue operations unit tests
    └── test_queue_integration.py # Queue API integration tests
```

## Features in Detail

### Patient Management

- Store comprehensive patient information
- Track location (floor, room, bed)
- Add clinical notes
- View all registered patients

### Prescription System

- Record detailed medication orders
- Track dosage and frequency
- Define treatment duration
- Specify administration time slots
- **Persistent queue processing**: Prescriptions are queued automatically and written to ThingSpeak in the background
- Queue survives application restarts (saved to `/tmp/prescription_queue.json`)
- Automatic retry for failed items (max 3 attempts)
- Failed items tracked and reportable via `/api/queue/status`
- Returns immediately without blocking (HTTP 202 Accepted)

### Queue Management

- **Persistent storage**: Queue data saved to disk and restored on restart
- **Monitoring**: Real-time queue status via `/api/queue/status` endpoint
- **Size limits**: Configurable maximum queue size (default: 1000 items)
- **Retry logic**: Automatic retry for failed items (max 3 attempts)
- **Failed item tracking**: View and manage items that exceed retry limit
- **Statistics**: Track total items added, processed, failed, and retried
- **Management**: Clear failed items via `/api/queue/clear-failed` endpoint

### Medication Tracking

- Real-time recording of medication administration
- Track exact date and time of administration
- Monitor compliance with prescriptions
- Generate administration history

### Dashboard Analytics

- **Duty Dashboard**: Round timeline view + patient medication search
- **Nurse Dashboard**: Patient management + prescription entry (active by default)
- **Management Dashboard**: Statistics and charts
- Quick patient lookup
- Comprehensive patient view
- Real-time data updates

## 🔧 Troubleshooting

### Application Won't Start

```powershell
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Try running again
python app.py
```

### Port 5000 Already in Use

Edit `app.py` and change the port:

```python
app.run(debug=True, host="0.0.0.0", port=5001)
```

### Data Not Showing

1. Wait 2-3 seconds after adding data
2. Click the "Refresh" button
3. Check internet connection (needed for ThingSpeak)
4. Open browser console (F12) to check for errors

### API Errors

1. Verify ThingSpeak is accessible: https://thingspeak.com
2. Check API keys in `.env` file are correct
3. Wait 15 seconds between patient/tracking requests (rate limit per channel)
4. Check terminal for background worker messages: `"Successfully posted entry"`
5. Look for `response.raise_for_status()` exceptions in logs

## 🔐 Security Considerations

**This is a development setup!**

For production use:

- ✅ Enable user authentication
- ✅ Use HTTPS
- ✅ Secure API keys with environment variables (already using `.env` file)
- ✅ Configure ThingSpeak channel privacy
- ✅ Use a production WSGI server (e.g., Gunicorn, not Flask development server)
- ✅ Implement role-based access control
- ✅ Add `.env` to `.gitignore` to prevent exposing secrets
- ✅ Validate patient IDs before adding prescriptions/tracking

## Known Limitations & Considerations

1. **Rate Limiting UX**: Patient/tracking endpoints block for 15 seconds due to direct ThingSpeak writes
2. **Data Pagination**: Only last 100 records accessible per channel without implementing date-range queries
3. **No Transactions**: ThingSpeak writes are independent - no rollback if related data fails (e.g., prescription without patient)
4. **Queue Storage**: Prescription queue stored in `/tmp/prescription_queue.json` - may be cleared by system on some platforms
5. **Max Queue Size**: Queue limited to 1000 items by default - configure via `PersistentQueue` if needed

## Future Enhancements

- Implement ThingSpeak date-range pagination for >100 records
- User authentication and authorization
- Role-based access control (doctors, nurses, administrators)
- Barcode scanning for patient and medication identification
- Automated alerts for missed medications
- Detailed analytics and reporting
- Mobile application
- Integration with hospital management systems
- Prescription validation and drug interaction checking

## 💡 Tips & Tricks

### Quick Data Entry

- Use Tab key to move between form fields
- Forms remember your last entries (browser autocomplete)
- Date fields default to today

### Viewing Raw Data

Visit ThingSpeak channels directly:

- **Patients**: https://thingspeak.com/channels/3124887
- **Prescriptions**: https://thingspeak.com/channels/3124898
- **Tracking**: https://thingspeak.com/channels/3131200

### Clearing Test Data

1. Log into ThingSpeak.com
2. Navigate to each channel
3. Use "Clear Channel" option to remove all data

## Architecture Overview

### Three-Channel ThingSpeak Architecture

The app uses **three separate ThingSpeak channels**, each with 8-field data constraints:

1. **Patient Info Channel** (ID: 3124887): Stores patient demographics
2. **Prescription Channel** (ID: 3124898): Stores medication prescriptions with queueing system
3. **Tracking Channel** (ID: 3131200): Records actual medication administration

### Data Flow

**Client → Flask API → ThingSpeak REST API → Cloud Storage**

- GET requests: Fetch from ThingSpeak, transform generic field1-field8 to readable keys
- POST requests: Accept JSON, map to ThingSpeak field parameters
- Prescription writes: Queued via background thread (daemon) to avoid blocking UI
- Patient/Tracking writes: Direct to ThingSpeak (enforces 15-second wait)

## Acknowledgments

- Built with Flask web framework
- Data storage powered by ThingSpeak IoT platform
- UI inspired by modern healthcare applications
- See `.github/copilot-instructions.md` for detailed development guide

---

**Version:** 1.0.0  
**Last Updated:** November 9, 2025

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For AI-assisted development, see `.github/copilot-instructions.md` for project-specific patterns and conventions.

## License

MIT License
