# Electronic Medication Administration Record (eMAR)

A Flask-based web application for managing and tracking medication administration records electronically.

## Features

- Patient Management
- Medication Tracking
- Administration Records
- Reports & Analytics

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

````bash
git clone <repository-url>
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

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
````

2. **Start the application:**

   ```powershell
   python app.py
   ```

3. **Open your browser:**
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
- Wait 15 seconds (ThingSpeak rate limit), then refresh

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

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Storage**: ThingSpeak IoT Platform
- **API**: RESTful API design

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
- **POST** `/api/prescriptions` - Add new prescription

### Medication Tracking

- **GET** `/api/medication-tracking` - Get all tracking records
- **POST** `/api/medication-tracking` - Add new tracking record

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
python test_api.py
```

**Note**: Test script takes several minutes due to ThingSpeak rate limits (15 seconds between requests)

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

- **Free accounts**: 1 update every 15 seconds per channel
- Wait 15 seconds between adding records
- Data appears after 2-3 second sync delay

### Data Persistence

- All data is stored on ThingSpeak cloud
- Data persists even after closing the application
- Refresh the page to see latest data

### Browser Compatibility

- Works best in modern browsers (Chrome, Firefox, Edge, Safari)
- JavaScript must be enabled

## Project Structure

```
Electronic-Medication-Administration-Record/
├── app.py                      # Flask application with API endpoints
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── static/
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── main.js            # Frontend JavaScript
└── templates/
    └── index.html             # Main HTML template
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

### Medication Tracking

- Real-time recording of medication administration
- Track exact date and time of administration
- Monitor compliance with prescriptions
- Generate administration history

### Dashboard Analytics

- Quick patient lookup
- Comprehensive patient view
- Statistics overview
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
2. Check API keys in `app.py` are correct
3. Wait 15 seconds between requests (rate limit)

## 🔐 Security Considerations

**This is a development setup!**

For production use:

- ✅ Enable user authentication
- ✅ Use HTTPS
- ✅ Secure API keys with environment variables
- ✅ Configure ThingSpeak channel privacy
- ✅ Use a production WSGI server (not Flask development server)
- ✅ Implement role-based access control

## Future Enhancements

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

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Built with Flask web framework
- Data storage powered by ThingSpeak IoT platform
- UI inspired by modern healthcare applications

---

**Version:** 1.0.0  
**Last Updated:** October 30, 2025

````

2. Create a virtual environment:

```bash
python -m venv .venv
````

3. Activate the virtual environment:

- Windows:
  ```bash
  .venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Set up environment variables:

- Copy `.env` and update the values as needed
- Change the `SECRET_KEY` in production

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
Electronic-Medication-Administration-Record/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── README.md          # Project documentation
├── templates/         # HTML templates
│   └── index.html
└── static/           # Static files (CSS, JS, images)
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/health` - Health check endpoint

## Development

To run in development mode with auto-reload:

```bash
python app.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
#   4 0 0 1 1  
 #   4 0 0 1 1  
 