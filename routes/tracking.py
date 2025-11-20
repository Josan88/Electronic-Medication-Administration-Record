"""
Medication Tracking Routes

This module contains all Flask routes related to medication tracking,
including recording and viewing medication administration events.
"""

from flask import Blueprint, request
from services.hybrid_service import hybrid_service, HybridDataServiceError
from utils.errors import error_response, success_response, ValidationError
from validators import validate_tracking_data

tracking_bp = Blueprint('tracking', __name__, url_prefix='/api')


@tracking_bp.route("/medication-tracking", methods=["GET"])
def get_medication_tracking():
    """Get all medication tracking records from local database (with ThingSpeak fallback)"""
    try:
        tracking = hybrid_service.read_channel("medicine_track")
        return success_response(data=tracking)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)


@tracking_bp.route("/medication-tracking", methods=["POST"])
def add_medication_tracking():
    """Add a new medication tracking record to local database (with async ThingSpeak sync)"""
    try:
        data = request.json
        if data is None:
            raise ValidationError("Invalid JSON data")

        # Validate and sanitize input data (check patient existence)
        validated_data = validate_tracking_data(data, check_patient=True)

        entry_id = hybrid_service.write_to_channel("medicine_track", validated_data)
        return success_response(
            data={"entry_id": entry_id},
            message="Medication tracking record added successfully"
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except HybridDataServiceError as e:
        return error_response(str(e), 500)
