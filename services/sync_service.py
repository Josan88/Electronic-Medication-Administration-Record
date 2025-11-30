"""
Synchronization Service for Electronic Medication Administration Record (eMAR).

This module manages the synchronization of local database data to ThingSpeak
using bulk write operations. It includes:
- Periodic sync scheduling
- Sync queue with retry logic
- Error handling and exponential backoff
- Sync status tracking
"""

import json
import os
import time
import tempfile
from threading import Lock, Event
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.logging_config import logger


class SyncQueueItem:
    """Represents a pending sync operation."""
    
    def __init__(self, channel_name: str, since_entry_id: int = 0, item_id: str = None):
        """
        Initialize a sync queue item.
        
        Args:
            channel_name: Name of the channel to sync
            since_entry_id: Sync entries with entry_id > this value
            item_id: Unique identifier for this sync operation
        """
        self.channel_name = channel_name
        self.since_entry_id = since_entry_id
        self.item_id = item_id or f"{channel_name}-{time.time()}"
        self.attempts = 0
        self.last_error = None
        self.created_at = time.time()
        self.next_retry_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'channel_name': self.channel_name,
            'since_entry_id': self.since_entry_id,
            'item_id': self.item_id,
            'attempts': self.attempts,
            'last_error': self.last_error,
            'created_at': self.created_at,
            'next_retry_at': self.next_retry_at
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SyncQueueItem':
        """Create SyncQueueItem from dictionary."""
        item = cls(
            d['channel_name'],
            d.get('since_entry_id', 0),
            d['item_id']
        )
        item.attempts = d.get('attempts', 0)
        item.last_error = d.get('last_error')
        item.created_at = d.get('created_at', time.time())
        item.next_retry_at = d.get('next_retry_at', time.time())
        return item


class SyncQueue:
    """
    Queue for managing ThingSpeak synchronization operations.
    
    Features:
    - Persistent queue (survives restarts)
    - Retry logic with exponential backoff
    - Failed operation tracking
    - Thread-safe operations
    """
    
    def __init__(
        self,
        storage_path: str = None,
        max_retry_attempts: int = 5,
        initial_backoff_seconds: int = 15
    ):

        """
        Initialize sync queue.
        
        Args:
            storage_path: Path to persistent storage file
            max_retry_attempts: Maximum retry attempts per operation
            initial_backoff_seconds: Initial backoff time for retries
        """
        env_storage = os.environ.get('SYNC_QUEUE_PATH')
        self.storage_path = storage_path or env_storage
        if not self.storage_path:
            self.storage_path = os.path.join(tempfile.gettempdir(), 'emar_sync_queue.json')

        self.max_retry_attempts = max_retry_attempts
        self.initial_backoff_seconds = initial_backoff_seconds
        self.lock = Lock()
        self.new_item_event = Event()
        self.pending_items: List[SyncQueueItem] = []
        self.failed_items: List[SyncQueueItem] = []
        self.stats = {
            'total_synced': 0,
            'total_failed': 0,
            'total_retried': 0,
            'last_sync_time': None
        }
        # Track last synced entry_id per channel
        self.last_synced_entry_ids: Dict[str, int] = {
            'patient_info': 0,
            'medicine_prescription': 0,
            'medicine_track': 0
        }
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load queue data from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.pending_items = [
                        SyncQueueItem.from_dict(item)
                        for item in data.get('pending_items', [])
                    ]
                    self.failed_items = [
                        SyncQueueItem.from_dict(item)
                        for item in data.get('failed_items', [])
                    ]
                    self.stats = data.get('stats', self.stats)
                    self.last_synced_entry_ids = data.get(
                        'last_synced_entry_ids',
                        self.last_synced_entry_ids
                    )
                logger.info(
                    f"Loaded sync queue: {len(self.pending_items)} pending, "
                    f"{len(self.failed_items)} failed"
                )
            except Exception as e:
                logger.error(f"Error loading sync queue from disk: {e}", exc_info=True)
                self.pending_items = []
                self.failed_items = []
    
    def _save_to_disk(self):
        """Save queue data to disk."""
        try:
            data = {
                'pending_items': [item.to_dict() for item in self.pending_items],
                'failed_items': [item.to_dict() for item in self.failed_items],
                'stats': self.stats,
                'last_synced_entry_ids': self.last_synced_entry_ids,
                'last_saved': time.time()
            }
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.storage_path)
        except Exception as e:
            logger.error(f"Error saving sync queue to disk: {e}", exc_info=True)
    
    def add_sync_operation(self, channel_name: str, since_entry_id: int = None):
        """
        Add a sync operation to the queue.
        
        Args:
            channel_name: Name of the channel to sync
            since_entry_id: Sync entries with entry_id > this value (None = use last synced)
        """
        with self.lock:
            if since_entry_id is None:
                since_entry_id = self.last_synced_entry_ids.get(channel_name, 0)
            
            # Check if there's already a pending sync for this channel
            # to avoid duplicate sync operations that cause rate limit errors
            for existing_item in self.pending_items:
                if existing_item.channel_name == channel_name:
                    logger.debug(
                        f"Sync operation for {channel_name} already pending, "
                        f"skipping duplicate"
                    )
                    return
            
            item = SyncQueueItem(channel_name, since_entry_id)
            self.pending_items.append(item)
            self._save_to_disk()
            self.new_item_event.set()  # Signal that a new item is available
            logger.info(
                f"Added sync operation for {channel_name} "
                f"(since entry_id {since_entry_id})"
            )
    
    def get_next_ready_item(self) -> Optional[SyncQueueItem]:
        """
        Get the next item ready for processing.
        
        Returns:
            Next item ready to process, or None if no items are ready
        """
        with self.lock:
            current_time = time.time()
            for item in self.pending_items:
                if current_time >= item.next_retry_at:
                    return item
            return None
    
    def mark_success(
        self,
        item: SyncQueueItem,
        highest_synced_entry_id: int
    ):
        """
        Mark a sync operation as successful.
        
        Args:
            item: The sync item that succeeded
            highest_synced_entry_id: The highest entry_id that was synced
        """
        with self.lock:
            if item in self.pending_items:
                self.pending_items.remove(item)
                self.stats['total_synced'] += 1
                self.stats['last_sync_time'] = time.time()
                
                # Update last synced entry_id
                current_last = self.last_synced_entry_ids.get(item.channel_name, 0)
                self.last_synced_entry_ids[item.channel_name] = max(
                    current_last,
                    highest_synced_entry_id
                )
                
                self._save_to_disk()
                logger.info(
                    f"Sync successful for {item.channel_name}, "
                    f"synced up to entry_id {highest_synced_entry_id}"
                )
    
    def mark_failure(self, item: SyncQueueItem, error_message: str):
        """
        Mark a sync operation as failed.
        
        Args:
            item: The sync item that failed
            error_message: Error message describing the failure
        """
        with self.lock:
            if item in self.pending_items:
                item.attempts += 1
                item.last_error = error_message
                
                if item.attempts >= self.max_retry_attempts:
                    # Max retries exceeded, move to failed items
                    self.pending_items.remove(item)
                    self.failed_items.append(item)
                    self.stats['total_failed'] += 1
                    logger.error(
                        f"Sync failed permanently for {item.channel_name} "
                        f"after {item.attempts} attempts"
                    )
                else:
                    # Calculate exponential backoff
                    backoff = self.initial_backoff_seconds * (2 ** (item.attempts - 1))
                    item.next_retry_at = time.time() + backoff
                    self.stats['total_retried'] += 1
                    logger.warning(
                        f"Sync failed for {item.channel_name} "
                        f"(attempt {item.attempts}/{self.max_retry_attempts}), "
                        f"retrying in {backoff} seconds"
                    )
                
                self._save_to_disk()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current sync queue status.
        
        Returns:
            Dictionary with queue status information
        """
        with self.lock:
            return {
                'pending_count': len(self.pending_items),
                'failed_count': len(self.failed_items),
                'stats': self.stats.copy(),
                'last_synced_entry_ids': self.last_synced_entry_ids.copy(),
                'next_sync_times': {
                    item.channel_name: item.next_retry_at
                    for item in self.pending_items
                },
                'failed_items': [
                    {
                        'channel_name': item.channel_name,
                        'attempts': item.attempts,
                        'last_error': item.last_error,
                        'age_seconds': time.time() - item.created_at
                    }
                    for item in self.failed_items[:10]
                ]
            }
    
    def clear_failed_items(self) -> int:
        """
        Clear all failed items from the queue.
        
        Returns:
            Number of items cleared
        """
        with self.lock:
            count = len(self.failed_items)
            self.failed_items = []
            self._save_to_disk()
            logger.info(f"Cleared {count} failed sync items")
            return count
    
    def get_last_synced_entry_id(self, channel_name: str) -> int:
        """
        Get the last synced entry_id for a channel.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Last synced entry_id (0 if never synced)
        """
        with self.lock:
            return self.last_synced_entry_ids.get(channel_name, 0)

    def wait_for_new_item(self, timeout: float = None) -> bool:
        """
        Wait for a new item to be added to the queue.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if event was set, False if timeout occurred
        """
        # Wait for the event
        flag = self.new_item_event.wait(timeout)
        # Clear the event so we can wait again
        if flag:
            self.new_item_event.clear()
        return flag


# Global sync queue instance
sync_queue = SyncQueue()
