"""
Medication status calculation utilities for Electronic Medication Administration Record (eMAR).

This module provides functionality to determine medication administration status
based on consume date/time and prescribed time slots.
"""

from datetime import datetime, timedelta, time
from typing import Optional


def parse_time_from_string(time_str: str) -> Optional[time]:
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


def is_time_within_slot(consume_datetime: datetime, time_slot: str) -> bool:
    """
    Check if a consume datetime falls between sequential time slots.
    
    A medication is considered "within" a time slot if it was administered
    after the slot's start time and before the start of the next slot.
    
    Args:
        consume_datetime: The actual datetime when medication was consumed
        time_slot: Comma-separated time slots (e.g., "09:00, 13:00, 17:00, 21:00")
    
    Returns:
        True if consume_datetime falls between any pair of sequential slots, False otherwise
    
    Example:
        >>> dt = datetime(2025, 11, 13, 14, 30)  # 2:30 PM
        >>> is_time_within_slot(dt, "09:00, 13:00, 17:00, 21:00")
        True  # Between 13:00 and 17:00 slots
        
        >>> dt = datetime(2025, 11, 13, 8, 0)  # 8:00 AM
        >>> is_time_within_slot(dt, "09:00, 13:00, 17:00, 21:00")
        False  # Before the first slot of the day
    """
    if not time_slot or not isinstance(time_slot, str):
        return False
    
    # Parse time slots (comma-separated)
    slots = [s.strip() for s in time_slot.split(',') if s.strip()]
    
    if not slots:
        return False
    
    consume_date = consume_datetime.date()
    slot_datetimes = []
    
    for slot in slots:
        slot_time = parse_time_from_string(slot)
        if slot_time is None:
            continue
        slot_datetimes.append(datetime.combine(consume_date, slot_time))
    
    if not slot_datetimes:
        return False
    
    slot_datetimes.sort()
    
    for index, slot_start in enumerate(slot_datetimes):
        next_index = (index + 1) % len(slot_datetimes)
        next_start = slot_datetimes[next_index]
        
        if next_index == 0:
            next_start += timedelta(days=1)
        
        if slot_start <= consume_datetime < next_start:
            return True
    
    return False


def calculate_status(consume_date: str, time_slot: str) -> str:
    """
    Calculate medication administration status based on consume date and time slot.
    
    Status is "complete" if the consume_date time falls between the start of a time slot
    and the start of the next time slot. Otherwise, status is "pending".
    
    Args:
        consume_date: Date/time string when medication was consumed
                     Supports formats: "YYYY-MM-DD HH:MM:SS", "YYYY-MM-DD", etc.
        time_slot: Comma-separated time slots (e.g., "09:00, 13:00, 17:00, 21:00")
    
    Returns:
        "complete" if time matches a slot, "pending" otherwise
    
    Example:
        >>> calculate_status("2025-11-13 17:16:27", "09:00, 13:00, 17:00, 21:00")
        'complete'  # 17:16 is between 17:00 and 21:00 slots
        
        >>> calculate_status("2025-11-13 14:30:00", "09:00, 13:00, 17:00, 21:00")
        'complete'  # Between the 13:00 and 17:00 slots
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
