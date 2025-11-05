from flask import Flask, render_template, request, jsonify # type: ignore
import os
import requests # type: ignore
from datetime import datetime
from dotenv import load_dotenv # type: ignore
import time
from threading import Thread
from threading import Lock
from collections import deque

# Global variable to track the last successful ThingSpeak write time
last_ts_write_time = 0
TS_RATE_LIMIT_SECONDS = 15  # 15 seconds limit per entry
# Global variable to hold prescriptions waiting for ThingSpeak
prescription_queue = deque()
# Global lock to ensure only one thread modifies the queue at a time
queue_lock = Lock()

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("SECRET_KEY environment variable is not set")

# ThingSpeak Channel Configuration
THINGSPEAK_CHANNELS = {
    "patient_info": {
        "channel_id": os.environ.get("PATIENT_CHANNEL_ID"),
        "write_api_key": os.environ.get("PATIENT_WRITE_KEY"),
        "read_api_key": os.environ.get("PATIENT_READ_KEY"),
        "fields": {
            "field1": "Patient_ID",
            "field2": "Name",
            "field3": "Floor",
            "field4": "Room",
            "field5": "Bed",
            "field6": "Age",
            "field7": "Gender",
            "field8": "Notes",
        },
    },
    "medicine_prescription": {
        "channel_id": os.environ.get("PRESCRIPTION_CHANNEL_ID"),
        "write_api_key": os.environ.get("PRESCRIPTION_WRITE_KEY"),
        "read_api_key": os.environ.get("PRESCRIPTION_READ_KEY"),
        "fields": {
            "field1": "Patient_ID",
            "field2": "Medicine_Name",
            "field3": "Dosage",
            "field4": "Frequency",
            "field5": "Start_Date",
            "field6": "End_Date",
            "field7": "Time_Slot",
        },
    },
    "medicine_track": {
        "channel_id": os.environ.get("TRACKING_CHANNEL_ID"),
        "write_api_key": os.environ.get("TRACKING_WRITE_KEY"),
        "read_api_key": os.environ.get("TRACKING_READ_KEY"),
        "fields": {
            "field1": "Patient_ID",
            "field2": "Medicine_Name",
            "field3": "Dosage",
            "field4": "Consume_Date",
            "field5": "Time_Slot",
        },
    },
}

THINGSPEAK_BASE_URL = "https://api.thingspeak.com"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "message": "Electronic Medication Administration Record API is running",
        }
    )


# Patient Information Endpoints
@app.route("/api/patients", methods=["GET"])
def get_patients():
    """Get all patient information from ThingSpeak"""
    try:
        channel = THINGSPEAK_CHANNELS["patient_info"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        patients = []

        for feed in data.get("feeds", []):
            patient = {
                "entry_id": feed.get("entry_id"),
                "created_at": feed.get("created_at"),
                "patient_id": feed.get("field1"),
                "name": feed.get("field2"),
                "floor": feed.get("field3"),
                "room": feed.get("field4"),
                "bed": feed.get("field5"),
                "age": feed.get("field6"),
                "gender": feed.get("field7"),
                "notes": feed.get("field8"),
            }
            patients.append(patient)

        return jsonify({"success": True, "data": patients})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patients", methods=["POST"])
def add_patient():
    """Add a new patient to ThingSpeak"""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        channel = THINGSPEAK_CHANNELS["patient_info"]

        url = f"{THINGSPEAK_BASE_URL}/update"
        params = {
            "api_key": channel["write_api_key"],
            "field1": data.get("patient_id", ""),
            "field2": data.get("name", ""),
            "field3": data.get("floor", ""),
            "field4": data.get("room", ""),
            "field5": data.get("bed", ""),
            "field6": data.get("age", ""),
            "field7": data.get("gender", ""),
            "field8": data.get("notes", ""),
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        entry_id = response.text
        return jsonify(
            {
                "success": True,
                "entry_id": entry_id,
                "message": "Patient added successfully",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Medicine Prescription Endpoints
@app.route("/api/prescriptions", methods=["GET"])
def get_prescriptions():
    """Get all medicine prescriptions from ThingSpeak"""
    try:
        channel = THINGSPEAK_CHANNELS["medicine_prescription"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        prescriptions = []

        for feed in data.get("feeds", []):
            prescription = {
                "entry_id": feed.get("entry_id"),
                "created_at": feed.get("created_at"),
                "patient_id": feed.get("field1"),
                "medicine_name": feed.get("field2"),
                "dosage": feed.get("field3"),
                "frequency": feed.get("field4"),
                "start_date": feed.get("field5"),
                "end_date": feed.get("field6"),
                "time_slot": feed.get("field7"),
            }
            prescriptions.append(prescription)

        return jsonify({"success": True, "data": prescriptions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/prescriptions", methods=["POST"])
def add_prescription():
    """Add a new medicine prescription to the internal queue instantly."""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        # Add data to the thread-safe queue instantly
        with queue_lock:
            prescription_queue.append(data)

        # Return success immediately to the frontend, removing the 15s lag
        return jsonify(
            {
                "success": True,
                "message": "Prescription queued successfully for background processing.",
            }
        ), 202 # HTTP 202 Accepted status code

    except Exception as e:
        # Note: This only catches errors in the queuing process, not the ThingSpeak write
        return jsonify({"success": False, "error": str(e)}), 500

# Medicine Tracking Endpoints
@app.route("/api/medication-tracking", methods=["GET"])
def get_medication_tracking():
    """Get all medication tracking records from ThingSpeak"""
    try:
        channel = THINGSPEAK_CHANNELS["medicine_track"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        tracking = []

        for feed in data.get("feeds", []):
            record = {
                "entry_id": feed.get("entry_id"),
                "created_at": feed.get("created_at"),
                "patient_id": feed.get("field1"),
                "medicine_name": feed.get("field2"),
                "dosage": feed.get("field3"),
                "consume_date": feed.get("field4"),
                "time_slot": feed.get("field5"),
            }
            tracking.append(record)

        return jsonify({"success": True, "data": tracking})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/medication-tracking", methods=["POST"])
def add_medication_tracking():
    """Add a new medication tracking record to ThingSpeak"""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        channel = THINGSPEAK_CHANNELS["medicine_track"]

        url = f"{THINGSPEAK_BASE_URL}/update"
        params = {
            "api_key": channel["write_api_key"],
            "field1": data.get("patient_id", ""),
            "field2": data.get("medicine_name", ""),
            "field3": data.get("dosage", ""),
            "field4": data.get("consume_date", ""),
            "field5": data.get("time_slot", ""),
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        entry_id = response.text
        return jsonify(
            {
                "success": True,
                "entry_id": entry_id,
                "message": "Medication tracking record added successfully",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Query by Patient ID
@app.route("/api/patient/<patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    """Get patient information by Patient ID"""
    try:
        channel = THINGSPEAK_CHANNELS["patient_info"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        patient = None

        for feed in data.get("feeds", []):
            if feed.get("field1") == patient_id:
                patient = {
                    "entry_id": feed.get("entry_id"),
                    "created_at": feed.get("created_at"),
                    "patient_id": feed.get("field1"),
                    "name": feed.get("field2"),
                    "floor": feed.get("field3"),
                    "room": feed.get("field4"),
                    "bed": feed.get("field5"),
                    "age": feed.get("field6"),
                    "gender": feed.get("field7"),
                    "notes": feed.get("field8"),
                }
                break

        if patient:
            return jsonify({"success": True, "data": patient})
        else:
            return jsonify({"success": False, "message": "Patient not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patient/<patient_id>/prescriptions", methods=["GET"])
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for a specific patient"""
    try:
        channel = THINGSPEAK_CHANNELS["medicine_prescription"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        prescriptions = []

        for feed in data.get("feeds", []):
            if feed.get("field1") == patient_id:
                prescription = {
                    "entry_id": feed.get("entry_id"),
                    "created_at": feed.get("created_at"),
                    "patient_id": feed.get("field1"),
                    "medicine_name": feed.get("field2"),
                    "dosage": feed.get("field3"),
                    "frequency": feed.get("field4"),
                    "start_date": feed.get("field5"),
                    "end_date": feed.get("field6"),
                    "time_slot": feed.get("field7"),
                }
                prescriptions.append(prescription)

        return jsonify({"success": True, "data": prescriptions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patient/<patient_id>/tracking", methods=["GET"])
def get_patient_tracking(patient_id):
    """Get all medication tracking records for a specific patient"""
    try:
        channel = THINGSPEAK_CHANNELS["medicine_track"]
        url = f"{THINGSPEAK_BASE_URL}/channels/{channel['channel_id']}/feeds.json"
        params = {"api_key": channel["read_api_key"], "results": 100}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        tracking = []

        for feed in data.get("feeds", []):
            if feed.get("field1") == patient_id:
                record = {
                    "entry_id": feed.get("entry_id"),
                    "created_at": feed.get("created_at"),
                    "patient_id": feed.get("field1"),
                    "medicine_name": feed.get("field2"),
                    "dosage": feed.get("field3"),
                    "consume_date": feed.get("field4"),
                    "time_slot": feed.get("field5"),
                }
                tracking.append(record)

        return jsonify({"success": True, "data": tracking})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def process_prescription_queue():
    """Background worker to process the prescription queue at the ThingSpeak rate limit."""
    global last_ts_write_time

    while True:
        try:
            # Check if an entry is waiting and the rate limit has passed
            current_time = time.time()
            time_since_last_write = current_time - last_ts_write_time
            
            if time_since_last_write >= TS_RATE_LIMIT_SECONDS:
                with queue_lock:
                    if prescription_queue:
                        data = prescription_queue.popleft() # Get the oldest entry
                    else:
                        data = None
                
                if data:
                    # Write to ThingSpeak (reusing logic from add_prescription)
                    channel = THINGSPEAK_CHANNELS["medicine_prescription"]
                    url = f"{THINGSPEAK_BASE_URL}/update"
                    
                    params = {
                        "api_key": channel["write_api_key"],
                        "field1": data.get("patient_id", ""),
                        "field2": data.get("medicine_name", ""),
                        "field3": data.get("dosage", ""),
                        "field4": data.get("frequency", ""),
                        "field5": data.get("start_date", ""),
                        "field6": data.get("end_date", ""),
                        "field7": data.get("time_slot", ""),
                    }
                    
                    response = requests.get(url, params=params)
                    response.raise_for_status() # Raises exception on bad status
                    
                    # Log or update status if needed
                    print(f"Successfully posted entry {response.text} to ThingSpeak.")
                    
                    # Update the last successful write time
                    last_ts_write_time = time.time() 

            # Sleep for 1 second before checking the queue again
            time.sleep(1)

        except Exception as e:
            print(f"Error in background worker: {e}")
            time.sleep(5) # Wait longer on error before retrying
            
# Start the background worker thread when the app starts
worker_thread = Thread(target=process_prescription_queue, daemon=True)
worker_thread.start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
