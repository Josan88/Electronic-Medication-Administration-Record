"""
Prescription data validation for Electronic Medication Administration Record (eMAR).

This module validates prescription information before it's sent to ThingSpeak.
"""

import re
import html
from datetime import datetime
from typing import Dict, Any
from utils.errors import ValidationError


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # HTML escape to prevent XSS
    sanitized = html.escape(value.strip())
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_patient_id(patient_id: str) -> str:
    """
    Validate patient ID format.
    
    Args:
        patient_id: Patient ID to validate
    
    Returns:
        Validated and sanitized patient ID
    
    Raises:
        ValidationError: If patient ID is invalid
    """
    if not patient_id:
        raise ValidationError("Patient ID is required")
    
    patient_id = sanitize_string(patient_id, max_length=50)
    
    # Patient ID should be alphanumeric with optional hyphens/underscores
    if not re.match(r'^[A-Za-z0-9_-]+$', patient_id):
        raise ValidationError(
            "Patient ID must contain only letters, numbers, hyphens, or underscores"
        )
    
    if len(patient_id) < 2:
        raise ValidationError("Patient ID must be at least 2 characters long")
    
    return patient_id


def validate_medicine_name(medicine_name: str) -> str:
    """
    Validate medicine name.
    
    Args:
        medicine_name: Medicine name to validate
    
    Returns:
        Validated and sanitized medicine name
    
    Raises:
        ValidationError: If medicine name is invalid
    """
    if not medicine_name:
        raise ValidationError("Medicine name is required")
    
    medicine_name = sanitize_string(medicine_name, max_length=100)
    
    # Medicine name should contain letters, numbers, spaces, and basic punctuation
    if not re.match(r'^[A-Za-z0-9\s\.\-\(\)]+$', medicine_name):
        raise ValidationError(
            "Medicine name must contain only letters, numbers, spaces, and basic punctuation (. - ())"
        )
    
    if len(medicine_name) < 2:
        raise ValidationError("Medicine name must be at least 2 characters long")
    
    return medicine_name


def validate_dosage(dosage: str) -> str:
    """
    Validate dosage information.
    
    Args:
        dosage: Dosage to validate
    
    Returns:
        Validated and sanitized dosage
    
    Raises:
        ValidationError: If dosage is invalid
    """
    if not dosage:
        raise ValidationError("Dosage is required")
    
    dosage = sanitize_string(dosage, max_length=50)
    
    # Dosage should contain numbers, units (mg, ml, etc.), and basic punctuation
    # Use a simple character class check to avoid ReDoS
    if not re.match(r'^[0-9.\sA-Za-z/]+$', dosage):
        raise ValidationError(
            "Dosage must be in a valid format (e.g., 500mg, 1.5ml, 2 tablets)"
        )
    
    # Additional check: must have at least one digit
    if not any(c.isdigit() for c in dosage):
        raise ValidationError(
            "Dosage must contain at least one number"
        )
    
    return dosage


def validate_frequency(frequency: str) -> str:
    """
    Validate frequency information.
    
    Args:
        frequency: Frequency to validate
    
    Returns:
        Validated and sanitized frequency
    
    Raises:
        ValidationError: If frequency is invalid
    """
    if not frequency:
        raise ValidationError("Frequency is required")
    
    frequency = sanitize_string(frequency, max_length=100)
    
    # Frequency can contain letters, numbers, spaces, and basic punctuation
    if not re.match(r'^[A-Za-z0-9\s\,\.\-\/]+$', frequency):
        raise ValidationError(
            "Frequency must contain only letters, numbers, spaces, and basic punctuation (, . - /)"
        )
    
    return frequency


def validate_date(date_str: str, field_name: str) -> str:
    """
    Validate date format.
    
    Args:
        date_str: Date string to validate
        field_name: Name of the field (for error messages)
    
    Returns:
        Validated date string
    
    Raises:
        ValidationError: If date is invalid
    """
    if not date_str:
        raise ValidationError(f"{field_name} is required")
    
    date_str = sanitize_string(date_str, max_length=10)
    
    # Accept common date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
    
    valid_date = False
    for date_format in date_formats:
        try:
            datetime.strptime(date_str, date_format)
            valid_date = True
            break
        except ValueError:
            continue
    
    if not valid_date:
        raise ValidationError(
            f"{field_name} must be in a valid date format (YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY)"
        )
    
    return date_str


def validate_start_date(start_date: str) -> str:
    """
    Validate start date.
    
    Args:
        start_date: Start date to validate
    
    Returns:
        Validated start date
    
    Raises:
        ValidationError: If start date is invalid
    """
    return validate_date(start_date, "Start date")


def validate_end_date(end_date: str) -> str:
    """
    Validate end date.
    
    Args:
        end_date: End date to validate
    
    Returns:
        Validated end date
    
    Raises:
        ValidationError: If end date is invalid
    """
    return validate_date(end_date, "End date")


def validate_time_slot(time_slot: str) -> str:
    """
    Validate time slot information.
    
    Args:
        time_slot: Time slot to validate
    
    Returns:
        Validated and sanitized time slot
    
    Raises:
        ValidationError: If time slot is invalid
    """
    if not time_slot:
        raise ValidationError("Time slot is required")
    
    time_slot = sanitize_string(time_slot, max_length=100)
    
    # Time slot can contain times (8AM, 14:00), commas, spaces
    if not re.match(r'^[A-Za-z0-9\s\,\:\.\-]+$', time_slot):
        raise ValidationError(
            "Time slot must contain only letters, numbers, spaces, and basic punctuation (, : . -)"
        )
    
    return time_slot


def validate_date_range(start_date: str, end_date: str) -> None:
    """
    Validate that end date is after start date.
    
    Args:
        start_date: Start date string
        end_date: End date string
    
    Raises:
        ValidationError: If date range is invalid
    """
    # Parse dates to compare them
    start_parsed = None
    end_parsed = None
    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
    
    for date_format in date_formats:
        try:
            start_parsed = datetime.strptime(start_date, date_format)
            break
        except ValueError:
            continue
    
    for date_format in date_formats:
        try:
            end_parsed = datetime.strptime(end_date, date_format)
            break
        except ValueError:
            continue
    
    if start_parsed and end_parsed:
        if end_parsed < start_parsed:
            raise ValidationError("End date must be after or equal to start date")


def validate_prescription_data(data: Dict[str, Any], check_patient: bool = False) -> Dict[str, Any]:
    """
    Validate all prescription data fields.
    
    Args:
        data: Dictionary containing prescription data
        check_patient: Whether to check if patient exists (requires service call)
    
    Returns:
        Dictionary with validated and sanitized data
    
    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("Prescription data must be a valid JSON object")
    
    # Validate required fields
    patient_id = validate_patient_id(data.get('patient_id', ''))
    medicine_name = validate_medicine_name(data.get('medicine_name', ''))
    dosage = validate_dosage(data.get('dosage', ''))
    frequency = validate_frequency(data.get('frequency', ''))
    start_date = validate_start_date(data.get('start_date', ''))
    end_date = validate_end_date(data.get('end_date', ''))
    time_slot = validate_time_slot(data.get('time_slot', ''))
    
    # Validate date range
    validate_date_range(start_date, end_date)
    
    # Check patient exists if requested
    if check_patient:
        from services.thingspeak_service import thingspeak_service
        if not thingspeak_service.patient_exists(patient_id):
            raise ValidationError(f"Patient with ID '{patient_id}' does not exist")
    
    validated_data = {
        'patient_id': patient_id,
        'medicine_name': medicine_name,
        'dosage': dosage,
        'frequency': frequency,
        'start_date': start_date,
        'end_date': end_date,
        'time_slot': time_slot,
    }
    
    return validated_data
