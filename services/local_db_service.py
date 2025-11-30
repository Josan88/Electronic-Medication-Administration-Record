"""
Local Database Service Module for Electronic Medication Administration Record (eMAR).

This module provides a local JSON-based database service that acts as the primary
data storage, with data structured to be compatible with ThingSpeak's bulk write API format.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from threading import Lock
from datetime import datetime, timezone

from utils.logging_config import logger


class LocalDatabaseError(Exception):
    """Raised when local database operations fail."""
    pass


class LocalDatabase:
    """
    Local JSON-based database service for eMAR data.
    
    Features:
    - JSON file-based storage for patients, prescriptions, and tracking
    - Data structure aligned with ThingSpeak bulk write format
    - Thread-safe operations
    - Automatic persistence
    - CRUD operations
    """
    
    def __init__(self, base_path=None):
        """
        Initialize local database.
        
        Args:
            base_path: Base directory for database files (defaults to config value or /tmp/emar_local_db)
        """
        if base_path is None:
            try:
                from config import config
                base_path = config.LOCAL_DB_PATH
            except:
                base_path = "/tmp/emar_local_db"
        
        self.base_path = base_path
        self.lock = Lock()
        
        # Define channel storage files
        self.channels = {
            'patient_info': os.path.join(base_path, 'patient_info.json'),
            'medicine_prescription': os.path.join(base_path, 'medicine_prescription.json'),
            'medicine_track': os.path.join(base_path, 'medicine_track.json')
        }
        
        # Field mappings (same as ThingSpeak for compatibility)
        self.field_mappings = {
            'patient_info': {
                'field1': 'patient_id',
                'field2': 'name',
                'field3': 'floor',
                'field4': 'room',
                'field5': 'bed',
                'field6': 'age',
                'field7': 'gender',
                'field8': 'notes'
            },
            'medicine_prescription': {
                'field1': 'patient_id',
                'field2': 'medicine_name',
                'field3': 'dosage',
                'field4': 'frequency',
                'field5': 'start_date',
                'field6': 'end_date',
                'field7': 'time_slot'
            },
            'medicine_track': {
                'field1': 'patient_id',
                'field2': 'medicine_name',
                'field3': 'dosage',
                'field4': 'consume_date',
                'field5': 'time_slot'
            }
        }
        
        self._initialize_storage()
        logger.info(f"LocalDatabase initialized with base_path: {self.base_path}")
    
    def _initialize_storage(self):

        """Create storage directory and initialize empty channel files if they don't exist."""
        try:
            os.makedirs(self.base_path, exist_ok=True)
            
            for channel_name, file_path in self.channels.items():
                if not os.path.exists(file_path):
                    initial_data = {
                        'channel': channel_name,
                        'feeds': [],
                        'metadata': {
                            'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            'last_updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            'entry_count': 0
                        }

                    }
                    self._write_channel_file(file_path, initial_data)
                    logger.info(f"Initialized local database channel: {channel_name}")
        except Exception as e:
            logger.error(f"Failed to initialize local database storage: {e}", exc_info=True)
            raise LocalDatabaseError(f"Failed to initialize storage: {e}")
    
    def _read_channel_file(self, file_path: str) -> Dict[str, Any]:
        """Read channel data from file."""
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                logger.warning(f"File not found at {abs_path}, returning empty struct")
                return {'channel': 'unknown', 'feeds': []}

            with open(abs_path, 'r') as f:
                data = json.load(f)
                feeds = data.get('feeds', [])
                logger.info(f"DEBUG_READ: Reading {abs_path}: found {len(feeds)} entries. Feeds content sample: {str(feeds)[:100]}")
                return data
        except Exception as e:
            logger.error(f"Failed to read channel file {file_path}: {e}")
            raise LocalDatabaseError(f"Failed to read channel file: {e}")
    
    def _write_channel_file(self, file_path: str, data: Dict[str, Any]):
        """Write channel data to file (atomic operation)."""
        try:
            abs_path = os.path.abspath(file_path)
            temp_path = f"{abs_path}.tmp"
            feeds = data.get('feeds', [])
            logger.info(f"DEBUG_WRITE: Writing to {abs_path}: {len(feeds)} entries. Last entry: {str(feeds[-1]) if feeds else 'None'}")
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, abs_path)
        except Exception as e:
            logger.error(f"Failed to write channel file {file_path}: {e}", exc_info=True)
            raise LocalDatabaseError(f"Failed to write channel file: {e}")
    
    def _map_data_to_feed(self, data: Dict[str, Any], channel_name: str) -> Dict[str, Any]:
        """
        Map user-friendly data to ThingSpeak-compatible feed format.
        
        Args:
            data: Dictionary with lowercase field names (e.g., 'patient_id', 'name')
            channel_name: Name of the channel
            
        Returns:
            Feed entry in ThingSpeak format
        """
        field_mapping = self.field_mappings[channel_name]
        feed_entry = {}
        
        # Map data to field1-field8
        for field_key, field_name in field_mapping.items():
            if field_name in data:
                feed_entry[field_key] = data[field_name]
        
        return feed_entry
    
    def _map_feed_to_data(self, feed: Dict[str, Any], channel_name: str) -> Dict[str, Any]:
        """
        Map ThingSpeak feed format to user-friendly data.
        
        Args:
            feed: Feed entry in ThingSpeak format
            channel_name: Name of the channel
            
        Returns:
            Dictionary with lowercase field names
        """
        field_mapping = self.field_mappings[channel_name]
        mapped_data = {
            'entry_id': feed.get('entry_id'),
            'created_at': feed.get('created_at')
        }
        
        # Map field1-field8 to readable names
        for field_key, field_name in field_mapping.items():
            if field_key in feed:
                mapped_data[field_name] = feed[field_key]
        
        # Compute status for medicine_track records
        if channel_name == 'medicine_track':
            consume_date = mapped_data.get('consume_date')
            time_slot = mapped_data.get('time_slot')
            if consume_date and time_slot:
                from utils.status_calculator import calculate_status
                mapped_data['status'] = calculate_status(consume_date, time_slot)
        
        return mapped_data
    
    def read_channel(self, channel_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read data from a local channel.
        
        Args:
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)
            limit: Maximum number of records to return. If None, return all records.
            
        Returns:
            List of dictionaries with mapped field names
            
        Raises:
            LocalDatabaseError: If the operation fails
        """
        with self.lock:
            try:
                file_path = self.channels[channel_name]
                channel_data = self._read_channel_file(file_path)
                feeds = channel_data.get('feeds', [])
                
                # Return most recent entries up to limit (if provided)
                if limit is not None and len(feeds) > limit:
                    feeds = feeds[-limit:]
                
                # Map to user-friendly format
                return [self._map_feed_to_data(feed, channel_name) for feed in feeds]
                
            except Exception as e:
                logger.error(f"Failed to read from local channel {channel_name}: {e}")
                raise LocalDatabaseError(f"Failed to read from local channel: {e}")

    
    def write_to_channel(self, channel_name: str, data: Dict[str, Any]) -> int:
        """
        Write data to a local channel.
        
        Args:
            channel_name: Name of the channel
            data: Dictionary with field values (keys should match field names in lowercase)
            
        Returns:
            Entry ID (integer)
            
        Raises:
            LocalDatabaseError: If the operation fails
        """
        with self.lock:
            try:
                file_path = self.channels[channel_name]
                channel_data = self._read_channel_file(file_path)
                
                # Generate entry_id
                entry_id = channel_data['metadata']['entry_count'] + 1
                
                # Create feed entry
                feed_entry = self._map_data_to_feed(data, channel_name)
                feed_entry['entry_id'] = entry_id
                feed_entry['created_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                
                # Add to feeds
                channel_data['feeds'].append(feed_entry)
                channel_data['metadata']['entry_count'] = entry_id
                channel_data['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

                
                # Save to disk
                self._write_channel_file(file_path, channel_data)
                
                logger.info(f"Wrote entry {entry_id} to local channel {channel_name}")
                return entry_id
                
            except Exception as e:
                logger.error(f"Failed to write to local channel {channel_name}: {e}")
                raise LocalDatabaseError(f"Failed to write to local channel: {e}")
    
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
            field_name: Name of the field to search (lowercase, e.g., 'patient_id')
            value: Value to search for
            
        Returns:
            List of matching records
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
        """
        results = self.find_by_field('patient_info', 'patient_id', patient_id)
        return results[0] if results else None
    
    def get_patient_prescriptions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all prescriptions for a specific patient.
        
        Args:
            patient_id: Patient ID to search for
            
        Returns:
            List of prescription dictionaries
        """
        return self.find_by_field('medicine_prescription', 'patient_id', patient_id)
    
    def get_patient_tracking(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all medication tracking records for a specific patient.
        
        Args:
            patient_id: Patient ID to search for
            
        Returns:
            List of tracking record dictionaries
        """
        return self.find_by_field('medicine_track', 'patient_id', patient_id)
    
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
        except LocalDatabaseError:
            return False
    
    def get_feeds_for_bulk_write(
        self,
        channel_name: str,
        since_entry_id: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get feeds in ThingSpeak bulk write format.
        
        Args:
            channel_name: Name of the channel
            since_entry_id: Only return entries with entry_id > this value
            
        Returns:
            List of feed entries in ThingSpeak format (with field1-field8)
        """
        with self.lock:
            try:
                file_path = self.channels[channel_name]
                channel_data = self._read_channel_file(file_path)
                feeds = channel_data.get('feeds', [])
                
                # Filter feeds by entry_id
                if since_entry_id > 0:
                    feeds = [f for f in feeds if f.get('entry_id', 0) > since_entry_id]
                
                return feeds
                
            except Exception as e:
                logger.error(f"Failed to get feeds for bulk write from {channel_name}: {e}")
                raise LocalDatabaseError(f"Failed to get feeds for bulk write: {e}")
    
    def get_channel_metadata(self, channel_name: str) -> Dict[str, Any]:
        """
        Get metadata for a channel.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Metadata dictionary
        """
        with self.lock:
            try:
                file_path = self.channels[channel_name]
                channel_data = self._read_channel_file(file_path)
                return channel_data.get('metadata', {})
            except Exception as e:
                logger.error(f"Failed to get metadata for {channel_name}: {e}")
                raise LocalDatabaseError(f"Failed to get channel metadata: {e}")


# Global local database instance
local_db = LocalDatabase()
