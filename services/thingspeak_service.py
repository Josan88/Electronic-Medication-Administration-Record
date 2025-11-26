"""
ThingSpeak Service Module for Electronic Medication Administration Record (eMAR).

This module provides a data access layer for ThingSpeak API interactions,
centralizing all read/write operations and field mapping logic.
"""

import requests
from typing import Dict, List, Optional, Any
from config import config
import logging

# Get logger instance
logger = logging.getLogger("eMAR")


class ThingSpeakError(Exception):
    """Raised when ThingSpeak API operations fail."""
    pass


class ThingSpeakService:
    """Service class for ThingSpeak API operations."""

    def __init__(self):
        """Initialize ThingSpeak service with configuration."""
        self.base_url = config.THINGSPEAK_BASE_URL
        self.channels = config.THINGSPEAK_CHANNELS
        self.results_limit = config.THINGSPEAK_RESULTS_LIMIT

    def _map_feed_to_dict(self, feed: Dict[str, Any], channel_name: str) -> Dict[str, Any]:
        """
        Map ThingSpeak feed fields to readable dictionary.

        Args:
            feed: Raw feed data from ThingSpeak
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)

        Returns:
            Dictionary with mapped field names
        """
        channel = self.channels[channel_name]
        mapped_data = {
            "entry_id": feed.get("entry_id"),
            "created_at": feed.get("created_at"),
        }

        # Map field1-field8 to readable names
        for field_key, field_name in channel["fields"].items():
            # Convert field name to lowercase with underscores (e.g., "Patient_ID" -> "patient_id")
            key = field_name.lower()
            mapped_data[key] = feed.get(field_key)
        
        # Compute status for medicine_track records based on consume_date and time_slot
        if channel_name == "medicine_track":
            # Accept either Consume_Date or Consume_DateTime label from ThingSpeak metadata
            consume_date = (
                mapped_data.get("consume_date")
                or mapped_data.get("consume_datetime")
                or feed.get("field4")
            )
            time_slot = mapped_data.get("time_slot") or feed.get("field5")
            if consume_date and time_slot:
                from utils.status_calculator import calculate_status
                mapped_data["status"] = calculate_status(consume_date, time_slot)


        return mapped_data

    def read_channel(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Read all data from a ThingSpeak channel.

        Args:
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)

        Returns:
            List of dictionaries with mapped field names

        Raises:
            ThingSpeakError: If the API request fails
        """
        try:
            channel = self.channels[channel_name]
            url = f"{self.base_url}/channels/{channel['channel_id']}/feeds.json"
            params = {
                "api_key": channel["read_api_key"],
                "results": self.results_limit
            }

            logger.debug(f"Reading from ThingSpeak channel: {channel_name}")
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            feeds = data.get("feeds", [])
            
            logger.info(f"Successfully read {len(feeds)} records from {channel_name}")

            # Map each feed to readable format
            return [self._map_feed_to_dict(feed, channel_name) for feed in feeds]

        except requests.RequestException as e:
            logger.error(f"Failed to read from {channel_name}: {str(e)}")
            raise ThingSpeakError(f"Failed to read from {channel_name}: {str(e)}")

    def write_to_channel(self, channel_name: str, data: Dict[str, str]) -> str:
        """
        Write data to a ThingSpeak channel.

        Args:
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)
            data: Dictionary with field values (keys should match field names in lowercase)

        Returns:
            Entry ID as string

        Raises:
            ThingSpeakError: If the API request fails
        """
        try:
            channel = self.channels[channel_name]
            field_mapping = channel["fields"]

            # Reverse map: readable names to field1-field8
            params = {"api_key": channel["write_api_key"]}

            for field_key, field_name in field_mapping.items():
                key = field_name.lower()
                if key in data:
                    params[field_key] = data.get(key, "")

            logger.debug(f"Writing to ThingSpeak channel: {channel_name}")
            url = f"{self.base_url}/update"
            response = requests.get(url, params=params)
            response.raise_for_status()

            entry_id = response.text.strip()
            logger.info(f"Successfully wrote entry {entry_id} to {channel_name}")
            return entry_id

        except requests.RequestException as e:
            logger.error(f"Failed to write to {channel_name}: {str(e)}")
            raise ThingSpeakError(f"Failed to write to {channel_name}: {str(e)}")

    def find_by_field(
        self,
        channel_name: str,
        field_name: str,
        value: str
    ) -> List[Dict[str, Any]]:
        """
        Find records in a channel by a specific field value.

        Args:
            channel_name: Name of the channel
            field_name: Name of the field to search (in lowercase, e.g., "patient_id")
            value: Value to search for

        Returns:
            List of matching records

        Raises:
            ThingSpeakError: If the API request fails
        """
        all_records = self.read_channel(channel_name)
        return [record for record in all_records if record.get(field_name) == value]

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific patient by ID.

        Args:
            patient_id: Patient ID to search for

        Returns:
            Patient data dictionary or None if not found

        Raises:
            ThingSpeakError: If the API request fails
        """
        results = self.find_by_field("patient_info", "patient_id", patient_id)
        return results[0] if results else None

    def get_patient_prescriptions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all prescriptions for a specific patient.

        Args:
            patient_id: Patient ID to search for

        Returns:
            List of prescription dictionaries

        Raises:
            ThingSpeakError: If the API request fails
        """
        return self.find_by_field("medicine_prescription", "patient_id", patient_id)

    def get_patient_tracking(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all medication tracking records for a specific patient.

        Args:
            patient_id: Patient ID to search for

        Returns:
            List of tracking record dictionaries

        Raises:
            ThingSpeakError: If the API request fails
        """
        return self.find_by_field("medicine_track", "patient_id", patient_id)

    def patient_exists(self, patient_id: str) -> bool:
        """
        Check if a patient exists.

        Args:
            patient_id: Patient ID to check

        Returns:
            True if patient exists, False otherwise
        """
        try:
            return self.get_patient(patient_id) is not None
        except ThingSpeakError:
            return False


# Global service instance
thingspeak_service = ThingSpeakService()
