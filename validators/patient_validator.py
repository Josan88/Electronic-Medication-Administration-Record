"""
Patient data validation for Electronic Medication Administration Record (eMAR).

This module validates patient information before it's sent to ThingSpeak.
"""

import re
import html
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


def validate_name(name: str) -> str:
    """
    Validate patient name.
    
    Args:
        name: Patient name to validate
    
    Returns:
        Validated and sanitized name
    
    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError("Patient name is required")
    
    name = sanitize_string(name, max_length=255)
    
    # Name should contain letters and spaces, with optional punctuation
    if not re.match(r'^[A-Za-z\s\.\'-]+$', name):
        raise ValidationError(
            "Patient name must contain only letters, spaces, and basic punctuation (. ' -)"
        )
    
    if len(name) < 1:
        raise ValidationError("Patient name must be at least 1 character long")
    
    return name


def validate_floor(floor: str) -> str:
    """
    Validate floor number/identifier.
    
    Args:
        floor: Floor to validate
    
    Returns:
        Validated and sanitized floor
    
    Raises:
        ValidationError: If floor is invalid
    """
    if not floor:
        raise ValidationError("Floor is required")
    
    floor = sanitize_string(floor, max_length=10)
    
    # Floor can be numeric or alphanumeric (e.g., "1", "2A", "Ground")
    if not re.match(r'^[A-Za-z0-9\s-]+$', floor):
        raise ValidationError("Floor must contain only letters, numbers, spaces, or hyphens")
    
    return floor


def validate_room(room: str) -> str:
    """
    Validate room number/identifier.
    
    Args:
        room: Room to validate
    
    Returns:
        Validated and sanitized room
    
    Raises:
        ValidationError: If room is invalid
    """
    if not room:
        raise ValidationError("Room is required")
    
    room = sanitize_string(room, max_length=10)
    
    # Room can be alphanumeric
    if not re.match(r'^[A-Za-z0-9\s-]+$', room):
        raise ValidationError("Room must contain only letters, numbers, spaces, or hyphens")
    
    return room


def validate_bed(bed: str) -> str:
    """
    Validate bed identifier.
    
    Args:
        bed: Bed to validate
    
    Returns:
        Validated and sanitized bed
    
    Raises:
        ValidationError: If bed is invalid
    """
    if not bed:
        raise ValidationError("Bed is required")
    
    bed = sanitize_string(bed, max_length=10)
    
    # Bed can be alphanumeric (e.g., "A", "1", "B2")
    if not re.match(r'^[A-Za-z0-9\s-]+$', bed):
        raise ValidationError("Bed must contain only letters, numbers, spaces, or hyphens")
    
    return bed


def validate_age(age: str) -> str:
    """
    Validate patient age.
    
    Args:
        age: Age to validate
    
    Returns:
        Validated age as string
    
    Raises:
        ValidationError: If age is invalid
    """
    if not age:
        raise ValidationError("Age is required")
    
    age = sanitize_string(age, max_length=5)
    
    # Age should be numeric (allow decimal for precision)
    try:
        age_float = float(age)
    except ValueError:
        raise ValidationError("Age must be a number")
    
    if age_float < 0 or age_float > 150:
        raise ValidationError("Age must be between 0 and 150")
    
    return age


def validate_gender(gender: str) -> str:
    """
    Validate patient gender.
    
    Args:
        gender: Gender to validate
    
    Returns:
        Validated and sanitized gender
    
    Raises:
        ValidationError: If gender is invalid
    """
    if not gender:
        raise ValidationError("Gender is required")
    
    gender = sanitize_string(gender, max_length=20)
    
    # Accept common gender values
    valid_genders = ['male', 'female', 'other', 'm', 'f', 'o']
    if gender.lower() not in valid_genders:
        raise ValidationError(
            "Gender must be one of: Male, Female, Other, M, F, O"
        )
    
    return gender


def validate_notes(notes: str) -> str:
    """
    Validate and sanitize patient notes.
    
    Args:
        notes: Notes to validate
    
    Returns:
        Validated and sanitized notes
    """
    if not notes:
        return ""
    
    # Allow longer notes but sanitize them
    notes = sanitize_string(notes, max_length=500)
    
    return notes


def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate all patient data fields.
    
    Args:
        data: Dictionary containing patient data
    
    Returns:
        Dictionary with validated and sanitized data
    
    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("Patient data must be a valid JSON object")
    
    # Validate required fields
    validated_data = {
        'patient_id': validate_patient_id(data.get('patient_id', '')),
        'name': validate_name(data.get('name', '')),
        'floor': validate_floor(data.get('floor', '')),
        'room': validate_room(data.get('room', '')),
        'bed': validate_bed(data.get('bed', '')),
        'age': validate_age(data.get('age', '')),
        'gender': validate_gender(data.get('gender', '')),
        'notes': validate_notes(data.get('notes', '')),
    }
    
    return validated_data
