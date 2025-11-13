"""
Prescription Management Routes

This module contains all Flask routes related to prescription management,
including adding and viewing medicine prescriptions.

Note: Prescription POST operations use a background queue system to avoid
blocking the UI due to ThingSpeak rate limits.
"""

from flask import Blueprint, request, jsonify
from services.thingspeak_service import thingspeak_service, ThingSpeakError
from utils.errors import error_response, success_response, ValidationError
from validators import validate_prescription_data

prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/api')


def init_prescription_routes(queue):
    """
    Initialize prescription routes with access to the global queue.
    
    Args:
        queue: The global persistent_queue instance
    """
    
    @prescriptions_bp.route("/prescriptions", methods=["GET"])
    def get_prescriptions():
        """Get all medicine prescriptions from ThingSpeak"""
        try:
            prescriptions = thingspeak_service.read_channel("medicine_prescription")
            return success_response(data=prescriptions)
        except ThingSpeakError as e:
            return error_response(str(e), 500)

    @prescriptions_bp.route("/prescriptions", methods=["POST"])
    def add_prescription():
        """Add a new medicine prescription to the internal queue instantly."""
        try:
            data = request.json
            if data is None:
                raise ValidationError("Invalid JSON data")

            # Validate and sanitize input data (check patient existence)
            validated_data = validate_prescription_data(data, check_patient=True)

            # Add data to the persistent queue
            try:
                queue.add(validated_data)
            except ValueError as e:
                # Queue is full
                return error_response(str(e), 507)  # HTTP 507 Insufficient Storage

            # Return success immediately to the frontend, removing the 15s lag
            return jsonify(
                {
                    "success": True,
                    "message": "Prescription queued successfully for background processing.",
                }
            ), 202  # HTTP 202 Accepted status code

        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            # Note: This only catches errors in the queuing process, not the ThingSpeak write
            return error_response(str(e), 500)
