"""
ThingSpeak Bulk Write Service Module for Electronic Medication Administration Record (eMAR).

This module provides functionality to sync local database data to ThingSpeak using
the Bulk Write API: https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html
and REST API: https://www.mathworks.com/help/thingspeak/rest-api.html

The Bulk Write API allows sending multiple data points in a single request,
helping to overcome the 15-second rate limit of the standard API.

Enhanced with additional REST API features for improved reliability and validation.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import config
from utils.logging_config import logger


class ThingSpeakBulkError(Exception):
    """Raised when ThingSpeak bulk write operations fail."""
    pass


class ThingSpeakAPIError(Exception):
    """Raised when ThingSpeak API operations fail."""
    pass


class ThingSpeakBulkService:
    """
    Service class for ThingSpeak Bulk Write API operations with REST API enhancements.
    
    The bulk write endpoint accepts JSON with the following structure:
    {
        "write_api_key": "YOUR_CHANNEL_WRITE_API_KEY",
        "updates": [
            {
                "created_at": "2023-10-25T10:30:00Z",
                "field1": "value1",
                "field2": "value2",
                ...
            },
            ...
        ]
    }
    
    Enhanced with REST API features:
    - Channel status validation
    - Read-after-write verification
    - Improved error handling with API-specific codes
    - Timezone support
    """
    
    def __init__(self):
        """Initialize ThingSpeak bulk write service with configuration."""
        self.base_url = config.THINGSPEAK_BASE_URL
        self.channels = config.THINGSPEAK_CHANNELS
        self.request_timeout = 30  # seconds
    
    def get_channel_status(self, channel_name: str) -> Dict[str, Any]:
        """
        Get channel status from ThingSpeak API.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Dictionary with channel status information
            
        Raises:
            ThingSpeakAPIError: If the API request fails
        """
        try:
            channel = self.channels[channel_name]
            url = f"{self.base_url}/channels/{channel['channel_id']}/feeds.json"
            params = {
                'api_key': channel['read_api_key'],
                'results': 1  # Just get latest entry for status check
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            channel_info = data.get('channel', {})
            
            logger.debug(f"Retrieved status for channel {channel_name}: {channel_info.get('name', 'Unknown')}")
            
            return {
                'channel_id': channel_info.get('id'),
                'name': channel_info.get('name'),
                'description': channel_info.get('description'),
                'last_entry_id': channel_info.get('last_entry_id'),
                'created_at': channel_info.get('created_at'),
                'updated_at': channel_info.get('updated_at'),
                'available': True
            }
            
        except requests.RequestException as e:
            logger.warning(f"Failed to get channel status for {channel_name}: {str(e)}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def validate_channel_before_write(self, channel_name: str) -> bool:
        """
        Validate that a channel is available before attempting bulk write.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            True if channel is available, False otherwise
        """
        status = self.get_channel_status(channel_name)
        is_available = status.get('available', False)
        
        if is_available:
            logger.debug(f"Channel {channel_name} validated and ready for write")
        else:
            logger.warning(f"Channel {channel_name} validation failed: {status.get('error', 'Unknown error')}")
        
        return is_available
    
    def bulk_write_to_channel(
        self,
        channel_name: str,
        feeds: List[Dict[str, Any]],
        validate_before_write: bool = True,
        verify_after_write: bool = False
    ) -> Dict[str, Any]:
        """
        Write multiple data points to a ThingSpeak channel using bulk write API.
        
        Args:
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)
            feeds: List of feed dictionaries with field1-field8 and created_at
            validate_before_write: Check channel status before writing (default: True)
            verify_after_write: Verify data was written correctly (default: False)
            
        Returns:
            Response dictionary with success status and details
            
        Raises:
            ThingSpeakBulkError: If the API request fails
        
        Example feed format:
            {
                "entry_id": 1,
                "created_at": "2023-10-25T10:30:00Z",
                "field1": "P001",
                "field2": "John Doe",
                ...
            }
        """
        if not feeds:
            logger.warning(f"No feeds to write for channel {channel_name}")
            return {
                'success': True,
                'message': 'No data to sync',
                'feeds_written': 0
            }
        
        # Validate channel availability before write
        if validate_before_write:
            if not self.validate_channel_before_write(channel_name):
                error_msg = f"Channel {channel_name} is not available for writing"
                logger.error(error_msg)
                raise ThingSpeakBulkError(error_msg)
        
        try:
            channel = self.channels[channel_name]
            
            # Prepare bulk write payload
            updates = []
            for feed in feeds:
                update = {}
                
                # Add created_at timestamp in ISO 8601 format with UTC timezone
                if 'created_at' in feed:
                    update['created_at'] = feed['created_at']
                else:
                    update['created_at'] = datetime.utcnow().isoformat() + 'Z'
                
                # Add field data (field1-field8)
                for i in range(1, 9):
                    field_key = f'field{i}'
                    if field_key in feed and feed[field_key] is not None:
                        update[field_key] = str(feed[field_key])
                
                updates.append(update)
            
            # Prepare request payload
            payload = {
                'write_api_key': channel['write_api_key'],
                'updates': updates
            }
            
            # Make bulk write request
            url = f"{self.base_url}/channels/{channel['channel_id']}/bulk_update.json"
            
            logger.debug(f"Sending bulk write to ThingSpeak channel {channel_name} with {len(updates)} updates")
            
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.request_timeout
            )
            
            # Enhanced error handling based on status codes
            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"Successfully bulk wrote {len(updates)} entries to ThingSpeak channel {channel_name}. "
                    f"Response: {result}"
                )
                
                # Optional verification after write
                verification_result = None
                if verify_after_write:
                    verification_result = self._verify_write(channel_name, len(updates))
                
                return {
                    'success': True,
                    'message': f'Bulk write successful for {channel_name}',
                    'feeds_written': len(updates),
                    'response': result,
                    'verification': verification_result
                }
            elif response.status_code == 400:
                error_msg = f"Bad request to ThingSpeak API for {channel_name}: Invalid data format"
                logger.error(f"{error_msg}. Response: {response.text}")
                raise ThingSpeakBulkError(error_msg)
            elif response.status_code == 401:
                error_msg = f"Authentication failed for {channel_name}: Invalid API key"
                logger.error(error_msg)
                raise ThingSpeakBulkError(error_msg)
            elif response.status_code == 404:
                error_msg = f"Channel {channel_name} not found (404)"
                logger.error(error_msg)
                raise ThingSpeakBulkError(error_msg)
            elif response.status_code == 429:
                error_msg = f"Rate limit exceeded for {channel_name}"
                logger.warning(error_msg)
                raise ThingSpeakBulkError(error_msg)
            else:
                error_msg = f"Unexpected status code {response.status_code} for {channel_name}: {response.text}"
                logger.error(error_msg)
                raise ThingSpeakBulkError(error_msg)
            
        except requests.Timeout as e:
            error_msg = f"Request timeout for {channel_name}: {str(e)}"
            logger.error(error_msg)
            raise ThingSpeakBulkError(error_msg)
        except requests.RequestException as e:
            error_msg = f"Failed to bulk write to {channel_name}: {str(e)}"
            logger.error(error_msg)
            
            # Try to extract error details from response
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_details = e.response.text
                    logger.error(f"ThingSpeak error details: {error_details}")
                    error_msg = f"{error_msg}. Details: {error_details}"
            except:
                pass
            
            raise ThingSpeakBulkError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during bulk write to {channel_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ThingSpeakBulkError(error_msg)
    
    def _verify_write(self, channel_name: str, expected_count: int) -> Dict[str, Any]:
        """
        Verify that data was written correctly to ThingSpeak.
        
        Args:
            channel_name: Name of the channel
            expected_count: Number of entries expected to be written
            
        Returns:
            Verification result dictionary
        """
        try:
            channel = self.channels[channel_name]
            url = f"{self.base_url}/channels/{channel['channel_id']}/feeds.json"
            params = {
                'api_key': channel['read_api_key'],
                'results': expected_count
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            actual_count = len(data.get('feeds', []))
            
            verification_passed = actual_count >= expected_count
            
            logger.debug(
                f"Write verification for {channel_name}: "
                f"expected={expected_count}, found={actual_count}, passed={verification_passed}"
            )
            
            return {
                'verified': verification_passed,
                'expected_count': expected_count,
                'actual_count': actual_count
            }
            
        except Exception as e:
            logger.warning(f"Failed to verify write for {channel_name}: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    def prepare_feeds_for_bulk_write(
        self,
        feeds: List[Dict[str, Any]],
        max_batch_size: int = 100
    ) -> List[List[Dict[str, Any]]]:
        """
        Prepare feeds for bulk write by batching them.
        
        Args:
            feeds: List of feed dictionaries
            max_batch_size: Maximum number of feeds per batch (ThingSpeak limit)
            
        Returns:
            List of batches, each containing up to max_batch_size feeds
        """
        batches = []
        for i in range(0, len(feeds), max_batch_size):
            batch = feeds[i:i + max_batch_size]
            batches.append(batch)
        
        logger.debug(f"Prepared {len(batches)} batches from {len(feeds)} feeds")
        return batches
    
    def get_last_entry_id(self, channel_name: str) -> Optional[int]:
        """
        Get the last entry ID from a ThingSpeak channel.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Last entry ID or None if channel is empty or error occurs
        """
        try:
            status = self.get_channel_status(channel_name)
            if status.get('available'):
                last_entry_id = status.get('last_entry_id')
                if last_entry_id:
                    logger.debug(f"Last entry ID for {channel_name}: {last_entry_id}")
                    return int(last_entry_id)
            return None
        except Exception as e:
            logger.warning(f"Failed to get last entry ID for {channel_name}: {str(e)}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on all configured ThingSpeak channels.
        
        Returns:
            Dictionary with health status for each channel
        """
        health_status = {}
        
        for channel_name in self.channels.keys():
            try:
                status = self.get_channel_status(channel_name)
                health_status[channel_name] = {
                    'available': status.get('available', False),
                    'last_entry_id': status.get('last_entry_id'),
                    'updated_at': status.get('updated_at')
                }
            except Exception as e:
                health_status[channel_name] = {
                    'available': False,
                    'error': str(e)
                }
        
        all_healthy = all(status.get('available', False) for status in health_status.values())
        
        return {
            'healthy': all_healthy,
            'channels': health_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# Global bulk service instance
thingspeak_bulk_service = ThingSpeakBulkService()
