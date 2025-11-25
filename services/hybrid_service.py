"""
Hybrid Data Service for Electronic Medication Administration Record (eMAR).

This module provides a unified data service that uses local database as primary
storage and ThingSpeak as backup. It handles:
- Read operations from local database (with ThingSpeak fallback)
- Write operations to local database (with async sync to ThingSpeak)
- Backward compatibility with existing thingspeak_service interface
"""

from typing import Dict, List, Optional, Any
from services.local_db_service import local_db, LocalDatabaseError
from services.thingspeak_service import thingspeak_service, ThingSpeakError
from services.sync_service import sync_queue
from utils.logging_config import logger


class HybridDataServiceError(Exception):
    """Raised when hybrid data service operations fail."""
    pass


class HybridDataService:
    """
    Hybrid data service that uses local database with ThingSpeak backup.
    
    Features:
    - Primary storage: Local JSON database (fast, no rate limits)
    - Backup storage: ThingSpeak (synced periodically via bulk write)
    - Fallback reads from ThingSpeak if local data unavailable
    - Compatible interface with existing thingspeak_service
    """
    
    def __init__(self):
        """Initialize hybrid data service."""
        self.local_db = local_db
        self.thingspeak_service = thingspeak_service
        self.sync_queue = sync_queue
    
    def read_channel(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Read all data from a channel (local database with ThingSpeak fallback).
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            List of dictionaries with mapped field names
            
        Raises:
            HybridDataServiceError: If both local and ThingSpeak reads fail
        """
        try:
            # Try local database first
            data = self.local_db.read_channel(channel_name)
            logger.debug(f"Read {len(data)} records from local database: {channel_name}")
            return data
        except LocalDatabaseError as e:
            # Fallback to ThingSpeak
            logger.warning(
                f"Local database read failed for {channel_name}, "
                f"falling back to ThingSpeak: {e}"
            )
            try:
                data = self.thingspeak_service.read_channel(channel_name)
                logger.info(
                    f"Successfully read {len(data)} records from ThingSpeak "
                    f"fallback: {channel_name}"
                )
                return data
            except ThingSpeakError as ts_error:
                error_msg = (
                    f"Failed to read from both local database and ThingSpeak "
                    f"for {channel_name}: Local error: {e}, ThingSpeak error: {ts_error}"
                )
                logger.error(error_msg)
                raise HybridDataServiceError(error_msg)
    
    def write_to_channel(self, channel_name: str, data: Dict[str, str]) -> str:
        """
        Write data to local channel and queue for ThingSpeak sync.
        
        Args:
            channel_name: Name of the channel
            data: Dictionary with field values
            
        Returns:
            Entry ID as string
            
        Raises:
            HybridDataServiceError: If the write operation fails
        """
        try:
            # Write to local database (primary storage)
            entry_id = self.local_db.write_to_channel(channel_name, data)
            
            # Queue for ThingSpeak sync (async backup)
            # The sync worker will pick this up and bulk write to ThingSpeak
            logger.debug(
                f"Wrote entry {entry_id} to local database {channel_name}, "
                f"queued for ThingSpeak sync"
            )
            
            return str(entry_id)
            
        except LocalDatabaseError as e:
            error_msg = f"Failed to write to local database for {channel_name}: {e}"
            logger.error(error_msg)
            raise HybridDataServiceError(error_msg)
    
    def find_by_field(
        self,
        channel_name: str,
        field_name: str,
        value: str
    ) -> List[Dict[str, Any]]:
        """
        Find records by field value (local database with ThingSpeak fallback).
        
        Args:
            channel_name: Name of the channel
            field_name: Name of the field to search
            value: Value to search for
            
        Returns:
            List of matching records
        """
        try:
            # Try local database first
            results = self.local_db.find_by_field(channel_name, field_name, value)
            logger.debug(
                f"Found {len(results)} records in local database "
                f"for {field_name}={value}"
            )
            return results
        except LocalDatabaseError as e:
            # Fallback to ThingSpeak
            logger.warning(
                f"Local database search failed for {channel_name}, "
                f"falling back to ThingSpeak: {e}"
            )
            try:
                results = self.thingspeak_service.find_by_field(
                    channel_name, field_name, value
                )
                logger.info(
                    f"Successfully found {len(results)} records from ThingSpeak "
                    f"fallback for {field_name}={value}"
                )
                return results
            except ThingSpeakError as ts_error:
                error_msg = (
                    f"Failed to search in both local database and ThingSpeak: "
                    f"Local error: {e}, ThingSpeak error: {ts_error}"
                )
                logger.error(error_msg)
                raise HybridDataServiceError(error_msg)
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific patient by ID.
        
        Args:
            patient_id: Patient ID to search for
            
        Returns:
            Patient data dictionary or None if not found
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
        """
        return self.find_by_field("medicine_prescription", "patient_id", patient_id)
    
    def get_patient_tracking(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all medication tracking records for a specific patient.
        
        Args:
            patient_id: Patient ID to search for
            
        Returns:
            List of tracking record dictionaries
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
        except HybridDataServiceError:
            return False


# Global hybrid service instance
hybrid_service = HybridDataService()
