"""
Configuration module for Electronic Medication Administration Record (eMAR) application.

This module handles:
- Environment variable loading and validation
- ThingSpeak channel configuration
- Application settings
"""

import os
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid or incomplete."""
    pass


class Config:
    """Application configuration class."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._validate_environment()

    def _validate_environment(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            "SECRET_KEY",
            "PATIENT_CHANNEL_ID",
            "PATIENT_WRITE_KEY",
            "PATIENT_READ_KEY",
            "PRESCRIPTION_CHANNEL_ID",
            "PRESCRIPTION_WRITE_KEY",
            "PRESCRIPTION_READ_KEY",
            "TRACKING_CHANNEL_ID",
            "TRACKING_WRITE_KEY",
            "TRACKING_READ_KEY",
        ]

        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @property
    def SECRET_KEY(self):
        """Flask secret key for session management."""
        return os.environ.get("SECRET_KEY")

    @property
    def THINGSPEAK_BASE_URL(self):
        """Base URL for ThingSpeak API."""
        return "https://api.thingspeak.com"

    @property
    def THINGSPEAK_RATE_LIMIT_SECONDS(self):
        """Rate limit in seconds between ThingSpeak writes (per channel)."""
        return 15

    @property
    def THINGSPEAK_RESULTS_LIMIT(self):
        """Maximum number of results to retrieve from ThingSpeak."""
        return 100

    @property
    def THINGSPEAK_CHANNELS(self):
        """ThingSpeak channel configuration."""
        return {
            "patient_info": {
                "channel_id": os.environ.get("PATIENT_CHANNEL_ID"),
                "write_api_key": os.environ.get("PATIENT_WRITE_KEY"),
                "read_api_key": os.environ.get("PATIENT_READ_KEY"),
                "fields": {
                    "field1": "Patient_ID",
                    "field2": "Name",
                    "field3": "Floor",
                    "field4": "Room",
                    "field5": "Bed",
                    "field6": "Age",
                    "field7": "Gender",
                    "field8": "Notes",
                },
            },
            "medicine_prescription": {
                "channel_id": os.environ.get("PRESCRIPTION_CHANNEL_ID"),
                "write_api_key": os.environ.get("PRESCRIPTION_WRITE_KEY"),
                "read_api_key": os.environ.get("PRESCRIPTION_READ_KEY"),
                "fields": {
                    "field1": "Patient_ID",
                    "field2": "Medicine_Name",
                    "field3": "Dosage",
                    "field4": "Frequency",
                    "field5": "Start_Date",
                    "field6": "End_Date",
                    "field7": "Time_Slot",
                },
            },
            "medicine_track": {
                "channel_id": os.environ.get("TRACKING_CHANNEL_ID"),
                "write_api_key": os.environ.get("TRACKING_WRITE_KEY"),
                "read_api_key": os.environ.get("TRACKING_READ_KEY"),
                "fields": {
                    "field1": "Patient_ID",
                    "field2": "Medicine_Name",
                    "field3": "Dosage",
                    "field4": "Consume_Date",
                    "field5": "Time_Slot",
                },
            },
        }


# Global configuration instance
config = Config()
