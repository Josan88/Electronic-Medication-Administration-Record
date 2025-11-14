"""
Medication status calculation utilities for Electronic Medication Administration Record (eMAR).

This module provides functionality to determine medication administration status
based on consume date/time and prescribed time slots.
"""

from datetime import datetime, timedelta
from typing import Optional


def parse_time_from_string(time_str: str) -> Optional[datetime.time]:
    """
    Parse time from various string formats.
    
    Supports formats:
    - HH:MM (24-hour format, e.g., "09:00", "17:00")
    - H:MM (24-hour format, e.g., "9:00")
    - HHAM/HHPM (12-hour format, e.g., "9AM", "5PM")
    
    Args:
        time_str: Time string to parse
    
    Returns:
        datetime.time object or None if parsing fails
    """
    time_str = time_str.strip().upper()
    
    # Try 24-hour format HH:MM or H:MM
    for fmt in ['%H:%M', '%I:%M']:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.time()
        except ValueError:
            continue
    
    # Try 12-hour format with AM/PM (e.g., "9AM", "5PM")
    if time_str.endswith('AM') or time_str.endswith('PM'):
        try:
            # Handle formats like "9AM" or "09AM"
            dt = datetime.strptime(time_str, '%I%p')
            return dt.time()
        except ValueError:
            pass
    
    return None


def is_time_within_slot(consume_datetime: datetime, time_slot: str, tolerance_minutes: int = 30) -> bool:
    """
    Check if a consume datetime falls within a time slot with tolerance.
    
    A medication is considered "within" a time slot if it was administered
    within ±tolerance_minutes of any scheduled time in the slot.
    
    Args:
        consume_datetime: The actual datetime when medication was consumed
        time_slot: Comma-separated time slots (e.g., "09:00, 13:00, 17:00, 21:00")
        tolerance_minutes: Minutes of tolerance before/after scheduled time (default: 30)
    
    Returns:
        True if consume_datetime falls within any time slot (with tolerance), False otherwise
    
    Example:
        >>> dt = datetime(2025, 11, 13, 17, 15)  # 5:15 PM
        >>> is_time_within_slot(dt, "09:00, 13:00, 17:00, 21:00")
        True  # Within 30 min of 17:00
        
        >>> dt = datetime(2025, 11, 13, 18, 0)  # 6:00 PM
        >>> is_time_within_slot(dt, "09:00, 13:00, 17:00, 21:00")
        False  # More than 30 min from 17:00
    """
    if not time_slot or not isinstance(time_slot, str):
        return False
    
    # Parse time slots (comma-separated)
    slots = [s.strip() for s in time_slot.split(',') if s.strip()]
    
    if not slots:
        return False
    
    consume_time = consume_datetime.time()
    consume_date = consume_datetime.date()
    
    for slot in slots:
        slot_time = parse_time_from_string(slot)
        if slot_time is None:
            continue
        
        # Create datetime objects for comparison
        slot_datetime = datetime.combine(consume_date, slot_time)
        
        # Calculate time difference
        time_diff = abs((consume_datetime - slot_datetime).total_seconds() / 60)  # in minutes
        
        if time_diff <= tolerance_minutes:
            return True
    
    return False


def calculate_status(consume_date: str, time_slot: str) -> str:
    """
    Calculate medication administration status based on consume date and time slot.
    
    Status is "complete" if the consume_date time falls within the prescribed time_slot
    (with 30-minute tolerance). Otherwise, status is "pending".
    
    Args:
        consume_date: Date/time string when medication was consumed
                     Supports formats: "YYYY-MM-DD HH:MM:SS", "YYYY-MM-DD", etc.
        time_slot: Comma-separated time slots (e.g., "09:00, 13:00, 17:00, 21:00")
    
    Returns:
        "complete" if time matches a slot, "pending" otherwise
    
    Example:
        >>> calculate_status("2025-11-13 17:16:27", "09:00, 13:00, 17:00, 21:00")
        'complete'  # 17:16 is within 30 min of 17:00
        
        >>> calculate_status("2025-11-13 14:30:00", "09:00, 13:00, 17:00, 21:00")
        'pending'  # 14:30 is not within 30 min of any slot
    """
    try:
        # Parse consume_date - try multiple formats
        consume_datetime = None
        
        # Common datetime formats
        for fmt in [
            '%Y-%m-%d %H:%M:%S',  # "2025-11-13 17:16:27"
            '%Y-%m-%d %H:%M',     # "2025-11-13 17:16"
            '%Y-%m-%d',           # "2025-11-13" (assume midnight)
            '%d/%m/%Y %H:%M:%S',  # "13/11/2025 17:16:27"
            '%d/%m/%Y',           # "13/11/2025"
            '%m/%d/%Y %H:%M:%S',  # "11/13/2025 17:16:27"
            '%m/%d/%Y',           # "11/13/2025"
        ]:
            try:
                consume_datetime = datetime.strptime(consume_date.strip(), fmt)
                break
            except ValueError:
                continue
        
        if consume_datetime is None:
            # If we can't parse the date, default to pending
            return "pending"
        
        # Check if time is within any slot
        if is_time_within_slot(consume_datetime, time_slot):
            return "complete"
        else:
            return "pending"
    
    except Exception:
        # On any error, default to pending
        return "pending"
