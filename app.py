from flask import Flask, render_template, request, jsonify  # type: ignore
import time
from threading import Thread
from threading import Lock
from collections import deque
from config import config
from services.thingspeak_service import thingspeak_service, ThingSpeakError
from utils.logging_config import logger

# Global variable to track the last successful ThingSpeak write time
last_ts_write_time = 0
# Global variable to hold prescriptions waiting for ThingSpeak
prescription_queue = deque()
# Global lock to ensure only one thread modifies the queue at a time
queue_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

# ThingSpeak rate limit (used by background worker)
TS_RATE_LIMIT_SECONDS = config.THINGSPEAK_RATE_LIMIT_SECONDS


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
        patients = thingspeak_service.read_channel("patient_info")
        return jsonify({"success": True, "data": patients})
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patients", methods=["POST"])
def add_patient():
    """Add a new patient to ThingSpeak"""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        entry_id = thingspeak_service.write_to_channel("patient_info", data)
        return jsonify(
            {
                "success": True,
                "entry_id": entry_id,
                "message": "Patient added successfully",
            }
        )
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Medicine Prescription Endpoints
@app.route("/api/prescriptions", methods=["GET"])
def get_prescriptions():
    """Get all medicine prescriptions from ThingSpeak"""
    try:
        prescriptions = thingspeak_service.read_channel("medicine_prescription")
        return jsonify({"success": True, "data": prescriptions})
    except ThingSpeakError as e:
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
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Prescription queued successfully for background processing.",
                }
            ),
            202,
        )  # HTTP 202 Accepted status code

    except Exception as e:
        # Note: This only catches errors in the queuing process, not the ThingSpeak write
        return jsonify({"success": False, "error": str(e)}), 500


# Medicine Tracking Endpoints
@app.route("/api/medication-tracking", methods=["GET"])
def get_medication_tracking():
    """Get all medication tracking records from ThingSpeak"""
    try:
        tracking = thingspeak_service.read_channel("medicine_track")
        return jsonify({"success": True, "data": tracking})
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/medication-tracking", methods=["POST"])
def add_medication_tracking():
    """Add a new medication tracking record to ThingSpeak"""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        entry_id = thingspeak_service.write_to_channel("medicine_track", data)
        return jsonify(
            {
                "success": True,
                "entry_id": entry_id,
                "message": "Medication tracking record added successfully",
            }
        )
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Query by Patient ID
@app.route("/api/patient/<patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    """Get patient information by Patient ID"""
    try:
        patient = thingspeak_service.get_patient(patient_id)
        if patient:
            return jsonify({"success": True, "data": patient})
        else:
            return jsonify({"success": False, "message": "Patient not found"}), 404
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patient/<patient_id>/prescriptions", methods=["GET"])
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for a specific patient"""
    try:
        prescriptions = thingspeak_service.get_patient_prescriptions(patient_id)
        return jsonify({"success": True, "data": prescriptions})
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/patient/<patient_id>/tracking", methods=["GET"])
def get_patient_tracking(patient_id):
    """Get all medication tracking records for a specific patient"""
    try:
        tracking = thingspeak_service.get_patient_tracking(patient_id)
        return jsonify({"success": True, "data": tracking})
    except ThingSpeakError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/check_patient/<patient_id>", methods=["GET"])
def check_patient(patient_id):
    """Check if a patient exists by Patient ID."""
    try:
        exists = thingspeak_service.patient_exists(patient_id)
        return jsonify({"exists": exists})
    except Exception as e:
        return jsonify({"exists": False, "error": str(e)}), 500


def process_prescription_queue():
    """Background worker to process the prescription queue at the ThingSpeak rate limit."""
    global last_ts_write_time
    
    logger.info("Prescription queue worker started")

    while True:
        try:
            # Check if an entry is waiting and the rate limit has passed
            current_time = time.time()
            time_since_last_write = current_time - last_ts_write_time

            if time_since_last_write >= TS_RATE_LIMIT_SECONDS:
                with queue_lock:
                    if prescription_queue:
                        data = prescription_queue.popleft()  # Get the oldest entry
                    else:
                        data = None

                if data:
                    # Write to ThingSpeak using service
                    entry_id = thingspeak_service.write_to_channel("medicine_prescription", data)
                    logger.info(f"Successfully posted prescription entry {entry_id} for patient {data.get('patient_id', 'unknown')}")
                    
                    # Update the last successful write time
                    last_ts_write_time = time.time()

            # Sleep for 1 second before checking the queue again
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error in prescription queue worker: {e}", exc_info=True)
            time.sleep(5)  # Wait longer on error before retrying


# Start the background worker thread when the app starts
worker_thread = Thread(target=process_prescription_queue, daemon=True)
worker_thread.start()
logger.info("Electronic Medication Administration Record (eMAR) application initialized")

if __name__ == "__main__":
    logger.info("Starting Flask development server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
