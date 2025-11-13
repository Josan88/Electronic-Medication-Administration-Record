"""
Queue Management Service for Electronic Medication Administration Record (eMAR).

This module provides persistent queue management for prescription data with:
- File-based persistence (survives application restarts)
- Failed item tracking and retry logic
- Queue size limits and overflow handling
- Queue status monitoring
"""

import json
import os
import time
from collections import deque
from threading import Lock
from datetime import datetime
from utils.logging_config import logger


class QueueItem:
    """Represents a single item in the prescription queue."""
    
    def __init__(self, data, item_id=None, attempts=0, last_error=None):
        """
        Initialize a queue item.
        
        Args:
            data: The prescription data dictionary
            item_id: Unique identifier (timestamp-based if None)
            attempts: Number of processing attempts
            last_error: Last error message if failed
        """
        self.data = data
        self.item_id = item_id or f"{time.time()}-{id(data)}"
        self.attempts = attempts
        self.last_error = last_error
        self.created_at = time.time()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'data': self.data,
            'item_id': self.item_id,
            'attempts': self.attempts,
            'last_error': self.last_error,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, d):
        """Create QueueItem from dictionary."""
        item = cls(d['data'], d['item_id'], d['attempts'], d.get('last_error'))
        item.created_at = d.get('created_at', time.time())
        return item


class PersistentQueue:
    """
    Persistent queue implementation with retry logic and monitoring.
    
    Features:
    - JSON file-based persistence
    - Automatic save on modifications
    - Failed item tracking with retry limit
    - Queue size limits
    - Thread-safe operations
    """
    
    def __init__(self, storage_path='/tmp/prescription_queue.json', 
                 max_size=1000, max_retry_attempts=3):
        """
        Initialize the persistent queue.
        
        Args:
            storage_path: Path to JSON storage file
            max_size: Maximum queue size
            max_retry_attempts: Maximum retry attempts for failed items
        """
        self.storage_path = storage_path
        self.max_size = max_size
        self.max_retry_attempts = max_retry_attempts
        self.queue = deque()
        self.failed_items = []
        self.lock = Lock()
        self.stats = {
            'total_processed': 0,
            'total_failed': 0,
            'total_added': 0,
            'total_retried': 0
        }
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load queue data from disk."""
        if os.path.exists(self.storage_path):
            try:
                # Check if file is empty
                if os.path.getsize(self.storage_path) == 0:
                    logger.warning(f"Queue storage file is empty: {self.storage_path}")
                    return
                
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.queue = deque([QueueItem.from_dict(item) for item in data.get('queue', [])])
                    self.failed_items = [QueueItem.from_dict(item) for item in data.get('failed_items', [])]
                    self.stats = data.get('stats', self.stats)
                logger.info(f"Loaded {len(self.queue)} items from queue storage (path: {self.storage_path})")
                if self.failed_items:
                    logger.warning(f"Loaded {len(self.failed_items)} failed items from storage")
            except Exception as e:
                logger.error(f"Error loading queue from disk: {e}")
                # Initialize with empty queue on error
                self.queue = deque()
                self.failed_items = []
    
    def _save_to_disk(self):
        """Save queue data to disk."""
        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {
                'queue': [item.to_dict() for item in self.queue],
                'failed_items': [item.to_dict() for item in self.failed_items],
                'stats': self.stats,
                'last_saved': time.time()
            }
            # Write to temp file first, then rename (atomic operation)
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.storage_path)
        except Exception as e:
            logger.error(f"Error saving queue to disk: {e}")
    
    def add(self, data):
        """
        Add a new item to the queue.
        
        Args:
            data: Prescription data dictionary
            
        Returns:
            bool: True if added successfully, False if queue is full
            
        Raises:
            ValueError: If queue is full
        """
        with self.lock:
            if len(self.queue) >= self.max_size:
                logger.error(f"Queue full: cannot add item (max size: {self.max_size})")
                raise ValueError(f"Queue is full (max size: {self.max_size})")
            
            item = QueueItem(data)
            self.queue.append(item)
            self.stats['total_added'] += 1
            self._save_to_disk()
            logger.info(f"Added item {item.item_id} to queue (queue size: {len(self.queue)})")
            return True
    
    def get_next(self):
        """
        Get the next item from the queue without removing it.
        
        Returns:
            QueueItem or None: Next item to process, or None if queue is empty
        """
        with self.lock:
            if self.queue:
                return self.queue[0]
            return None
    
    def mark_success(self, item):
        """
        Mark an item as successfully processed and remove it from queue.
        
        Args:
            item: QueueItem that was successfully processed
        """
        with self.lock:
            if self.queue and self.queue[0].item_id == item.item_id:
                self.queue.popleft()
                self.stats['total_processed'] += 1
                self._save_to_disk()
                logger.info(f"Successfully processed item {item.item_id} (queue size: {len(self.queue)})")
    
    def mark_failure(self, item, error_message):
        """
        Mark an item as failed. Retry if attempts < max, otherwise move to failed list.
        
        Args:
            item: QueueItem that failed processing
            error_message: Error message describing the failure
        """
        with self.lock:
            if self.queue and self.queue[0].item_id == item.item_id:
                item.attempts += 1
                item.last_error = error_message
                
                if item.attempts >= self.max_retry_attempts:
                    # Max retries exceeded, move to failed items
                    self.queue.popleft()
                    self.failed_items.append(item)
                    self.stats['total_failed'] += 1
                    logger.error(f"Item {item.item_id} failed after {item.attempts} attempts, moved to failed list")
                else:
                    # Retry: move to back of queue
                    self.queue.popleft()
                    self.queue.append(item)
                    self.stats['total_retried'] += 1
                    logger.warning(f"Item {item.item_id} failed (attempt {item.attempts}/{self.max_retry_attempts}), moved to back of queue")
                
                self._save_to_disk()
    
    def get_status(self):
        """
        Get current queue status.
        
        Returns:
            dict: Queue status information
        """
        with self.lock:
            return {
                'queue_size': len(self.queue),
                'failed_count': len(self.failed_items),
                'max_size': self.max_size,
                'is_full': len(self.queue) >= self.max_size,
                'stats': self.stats.copy(),
                'oldest_item_age': self._get_oldest_item_age(),
                'failed_items': [
                    {
                        'patient_id': item.data.get('patient_id'),
                        'medicine_name': item.data.get('medicine_name'),
                        'attempts': item.attempts,
                        'last_error': item.last_error,
                        'age_seconds': time.time() - item.created_at
                    }
                    for item in self.failed_items[:10]  # Return max 10 failed items
                ]
            }
    
    def _get_oldest_item_age(self):
        """Get age of oldest item in queue (in seconds)."""
        if self.queue:
            oldest = min(self.queue, key=lambda x: x.created_at)
            return time.time() - oldest.created_at
        return 0
    
    def clear_failed_items(self):
        """Clear the failed items list."""
        with self.lock:
            count = len(self.failed_items)
            self.failed_items = []
            self._save_to_disk()
            logger.info(f"Cleared {count} failed items from queue")
            return count
    
    def size(self):
        """Get current queue size (thread-safe)."""
        with self.lock:
            return len(self.queue)


# Global persistent queue instance
persistent_queue = PersistentQueue()
