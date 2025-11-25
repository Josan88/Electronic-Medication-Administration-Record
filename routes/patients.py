"""
Patient Management Routes

This module contains all Flask routes related to patient management,
including CRUD operations and patient-specific queries.
"""

from flask import Blueprint, request
from services.hybrid_service import hybrid_service, HybridDataServiceError
from utils.errors import error_response, success_response, ValidationError, NotFoundError
from validators import validate_patient_data

patients_bp = Blueprint('patients', __name__, url_prefix='/api')


@patients_bp.route("/patients", methods=["GET"])
def get_patients():
    """Get all patient information from local database (with ThingSpeak fallback)"""
    try:
        patients = hybrid_service.read_channel("patient_info")
        return success_response(data=patients)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@patients_bp.route("/patients", methods=["POST"])
def add_patient():
    """Add a new patient to local database (with async ThingSpeak sync)"""
    try:
        data = request.json
        if data is None:
            raise ValidationError("Invalid JSON data")

        # Validate and sanitize input data
        validated_data = validate_patient_data(data)

        entry_id = hybrid_service.write_to_channel("patient_info", validated_data)
        return success_response(
            data={"entry_id": entry_id},
            message="Patient added successfully"
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@patients_bp.route("/patient/<patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    """Get patient information by Patient ID"""
    try:
        patient = hybrid_service.get_patient(patient_id)
        if patient:
            return success_response(data=patient)
        else:
            raise NotFoundError("Patient not found")
    except NotFoundError as e:
        return error_response(str(e), 404)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@patients_bp.route("/patient/<patient_id>/prescriptions", methods=["GET"])
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for a specific patient"""
    try:
        prescriptions = hybrid_service.get_patient_prescriptions(patient_id)
        return success_response(data=prescriptions)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@patients_bp.route("/patient/<patient_id>/tracking", methods=["GET"])
def get_patient_tracking(patient_id):
    """Get all medication tracking records for a specific patient"""
    try:
        tracking = hybrid_service.get_patient_tracking(patient_id)
        return success_response(data=tracking)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@patients_bp.route("/check_patient/<patient_id>", methods=["GET"])
def check_patient(patient_id):
    """Check if a patient exists by Patient ID."""
    try:
        exists = hybrid_service.patient_exists(patient_id)
        from flask import jsonify
        return jsonify({"exists": exists})
    except HybridDataServiceError as e:
        from flask import jsonify
        return jsonify({"exists": False, "error": str(e)}), 500
