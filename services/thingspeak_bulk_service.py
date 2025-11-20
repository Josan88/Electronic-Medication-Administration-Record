"""
ThingSpeak Bulk Write Service Module for Electronic Medication Administration Record (eMAR).

This module provides functionality to sync local database data to ThingSpeak using
the Bulk Write API: https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html

The Bulk Write API allows sending multiple data points in a single request,
helping to overcome the 15-second rate limit of the standard API.
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime
from config import config
from utils.logging_config import logger


class ThingSpeakBulkError(Exception):
    """Raised when ThingSpeak bulk write operations fail."""
    pass


class ThingSpeakBulkService:
    """
    Service class for ThingSpeak Bulk Write API operations.
    
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
    """
    
    def __init__(self):
        """Initialize ThingSpeak bulk write service with configuration."""
        self.base_url = config.THINGSPEAK_BASE_URL
        self.channels = config.THINGSPEAK_CHANNELS
    
    def bulk_write_to_channel(
        self,
        channel_name: str,
        feeds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Write multiple data points to a ThingSpeak channel using bulk write API.
        
        Args:
            channel_name: Name of the channel (patient_info, medicine_prescription, medicine_track)
            feeds: List of feed dictionaries with field1-field8 and created_at
            
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
        
        try:
            channel = self.channels[channel_name]
            
            # Prepare bulk write payload
            updates = []
            for feed in feeds:
                update = {}
                
                # Add created_at timestamp
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
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            logger.info(
                f"Successfully bulk wrote {len(updates)} entries to ThingSpeak channel {channel_name}. "
                f"Response: {result}"
            )
            
            return {
                'success': True,
                'message': f'Bulk write successful for {channel_name}',
                'feeds_written': len(updates),
                'response': result
            }
            
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
    
    def prepare_feeds_for_bulk_write(
        self,
        feeds: List[Dict[str, Any]],
        max_batch_size: int = 100
    ) -> List[List[Dict[str, Any]]]:
        """
        Prepare feeds for bulk write by batching them.
        
        Args:
            feeds: List of feed dictionaries
            max_batch_size: Maximum number of feeds per batch
            
        Returns:
            List of batches, each containing up to max_batch_size feeds
        """
        batches = []
        for i in range(0, len(feeds), max_batch_size):
            batch = feeds[i:i + max_batch_size]
            batches.append(batch)
        
        logger.debug(f"Prepared {len(batches)} batches from {len(feeds)} feeds")
        return batches


# Global bulk service instance
thingspeak_bulk_service = ThingSpeakBulkService()
