"""
Input validation module for Electronic Medication Administration Record (eMAR).

This module provides validation utilities for all incoming data to ensure:
- Data integrity and security
- Meaningful error messages
- Prevention of invalid data from reaching ThingSpeak
- Input sanitization against XSS attacks
"""

from .patient_validator import validate_patient_data
from .prescription_validator import validate_prescription_data
from .tracking_validator import validate_tracking_data

__all__ = [
    'validate_patient_data',
    'validate_prescription_data',
    'validate_tracking_data',
]
