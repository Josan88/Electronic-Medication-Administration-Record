# ThingSpeak Bulk Write API Examples

This document provides examples of using the ThingSpeak Bulk Write API and REST API enhancements for the eMAR system.

## REST API Reference

- **Bulk Write API**: https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html
- **REST API**: https://www.mathworks.com/help/thingspeak/rest-api.html

## Enhanced Features

The eMAR system now includes REST API enhancements:
- Channel status validation before writes
- Health check endpoints
- Enhanced error handling (accepts 200/202 success codes, handles 400, 401, 404, 429 errors)
- Optional write verification
- Last entry ID tracking

## Example 1: Bulk Write Patient Data

### Local Database Format

```json
{
  "channel": "patient_info",
  "feeds": [
    {
      "entry_id": 1,
      "created_at": "2025-11-20T10:00:00Z",
      "field1": "P001",
      "field2": "John Doe",
      "field3": "1",
      "field4": "101",
      "field5": "A",
      "field6": "45",
      "field7": "M",
      "field8": "Test patient"
    },
    {
      "entry_id": 2,
      "created_at": "2025-11-20T10:05:00Z",
      "field1": "P002",
      "field2": "Jane Smith",
      "field3": "2",
      "field4": "202",
      "field5": "B",
      "field6": "35",
      "field7": "F",
      "field8": "Another patient"
    }
  ]
}
```

### ThingSpeak Bulk Write Request

```bash
curl -X POST \
  https://api.thingspeak.com/channels/PATIENT_CHANNEL_ID/bulk_update.json \
  -H 'Content-Type: application/json' \
  -d '{
    "write_api_key": "YOUR_PATIENT_WRITE_KEY",
    "updates": [
      {
        "created_at": "2025-11-20T10:00:00Z",
        "field1": "P001",
        "field2": "John Doe",
        "field3": "1",
        "field4": "101",
        "field5": "A",
        "field6": "45",
        "field7": "M",
        "field8": "Test patient"
      },
      {
        "created_at": "2025-11-20T10:05:00Z",
        "field1": "P002",
        "field2": "Jane Smith",
        "field3": "2",
        "field4": "202",
        "field5": "B",
        "field6": "35",
        "field7": "F",
        "field8": "Another patient"
      }
    ]
  }'
```

### Expected Response

```json
{
  "success": true,
  "status": "accepted",
  "channel_id": "PATIENT_CHANNEL_ID"
}
```

## Example 2: Bulk Write Prescription Data

### Local Database Format

```json
{
  "channel": "medicine_prescription",
  "feeds": [
    {
      "entry_id": 1,
      "created_at": "2025-11-20T10:00:00Z",
      "field1": "P001",
      "field2": "Aspirin",
      "field3": "100mg",
      "field4": "Once daily",
      "field5": "2025-11-20",
      "field6": "2025-11-27",
      "field7": "08:00"
    },
    {
      "entry_id": 2,
      "created_at": "2025-11-20T10:10:00Z",
      "field1": "P001",
      "field2": "Metformin",
      "field3": "500mg",
      "field4": "Twice daily",
      "field5": "2025-11-20",
      "field6": "2025-12-20",
      "field7": "08:00, 20:00"
    }
  ]
}
```

### ThingSpeak Bulk Write Request

```bash
curl -X POST \
  https://api.thingspeak.com/channels/PRESCRIPTION_CHANNEL_ID/bulk_update.json \
  -H 'Content-Type: application/json' \
  -d '{
    "write_api_key": "YOUR_PRESCRIPTION_WRITE_KEY",
    "updates": [
      {
        "created_at": "2025-11-20T10:00:00Z",
        "field1": "P001",
        "field2": "Aspirin",
        "field3": "100mg",
        "field4": "Once daily",
        "field5": "2025-11-20",
        "field6": "2025-11-27",
        "field7": "08:00"
      },
      {
        "created_at": "2025-11-20T10:10:00Z",
        "field1": "P001",
        "field2": "Metformin",
        "field3": "500mg",
        "field4": "Twice daily",
        "field5": "2025-11-20",
        "field6": "2025-12-20",
        "field7": "08:00, 20:00"
      }
    ]
  }'
```

## Example 3: Bulk Write Tracking Data

### Local Database Format

```json
{
  "channel": "medicine_track",
  "feeds": [
    {
      "entry_id": 1,
      "created_at": "2025-11-20T08:00:00Z",
      "field1": "P001",
      "field2": "Aspirin",
      "field3": "100mg",
      "field4": "2025-11-20 08:00:00",
      "field5": "08:00"
    },
    {
      "entry_id": 2,
      "created_at": "2025-11-20T08:05:00Z",
      "field1": "P001",
      "field2": "Metformin",
      "field3": "500mg",
      "field4": "2025-11-20 08:05:00",
      "field5": "08:00"
    }
  ]
}
```

### ThingSpeak Bulk Write Request

```bash
curl -X POST \
  https://api.thingspeak.com/channels/TRACKING_CHANNEL_ID/bulk_update.json \
  -H 'Content-Type: application/json' \
  -d '{
    "write_api_key": "YOUR_TRACKING_WRITE_KEY",
    "updates": [
      {
        "created_at": "2025-11-20T08:00:00Z",
        "field1": "P001",
        "field2": "Aspirin",
        "field3": "100mg",
        "field4": "2025-11-20 08:00:00",
        "field5": "08:00"
      },
      {
        "created_at": "2025-11-20T08:05:00Z",
        "field1": "P001",
        "field2": "Metformin",
        "field3": "500mg",
        "field4": "2025-11-20 08:05:00",
        "field5": "08:00"
      }
    ]
  }'
```

## Example 4: Python Code for Bulk Write

```python
import requests
import json
from datetime import datetime

def bulk_write_to_thingspeak(channel_id, write_api_key, updates):
    """
    Send bulk updates to ThingSpeak channel.
    
    Args:
        channel_id: ThingSpeak channel ID
        write_api_key: Write API key for the channel
        updates: List of update dictionaries
        
    Returns:
        Response dictionary
    """
    url = f"https://api.thingspeak.com/channels/{channel_id}/bulk_update.json"
    
    payload = {
        "write_api_key": write_api_key,
        "updates": updates
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    response.raise_for_status()
    return response.json()


# Example usage: Sync patient data
updates = [
    {
        "created_at": "2025-11-20T10:00:00Z",
        "field1": "P001",
        "field2": "John Doe",
        "field3": "1",
        "field4": "101",
        "field5": "A",
        "field6": "45",
        "field7": "M",
        "field8": "Test patient"
    },
    {
        "created_at": "2025-11-20T10:05:00Z",
        "field1": "P002",
        "field2": "Jane Smith",
        "field3": "2",
        "field4": "202",
        "field5": "B",
        "field6": "35",
        "field7": "F",
        "field8": "Another patient"
    }
]

result = bulk_write_to_thingspeak(
    channel_id="YOUR_PATIENT_CHANNEL_ID",
    write_api_key="YOUR_PATIENT_WRITE_KEY",
    updates=updates
)

print(f"Sync result: {result}")
```

## Example 5: Batch Processing for Large Datasets

```python
def batch_sync_to_thingspeak(channel_id, write_api_key, all_updates, batch_size=100):
    """
    Sync large dataset to ThingSpeak in batches.
    
    Args:
        channel_id: ThingSpeak channel ID
        write_api_key: Write API key
        all_updates: List of all updates to sync
        batch_size: Maximum updates per batch (default 100)
        
    Returns:
        List of results from each batch
    """
    results = []
    
    for i in range(0, len(all_updates), batch_size):
        batch = all_updates[i:i + batch_size]
        
        print(f"Syncing batch {i//batch_size + 1} ({len(batch)} updates)...")
        
        result = bulk_write_to_thingspeak(
            channel_id=channel_id,
            write_api_key=write_api_key,
            updates=batch
        )
        
        results.append(result)
        
        # Small delay between batches
        if i + batch_size < len(all_updates):
            time.sleep(1)
    
    return results


# Example: Sync 250 updates in batches of 100
all_updates = [
    {
        "created_at": f"2025-11-20T{10 + i//60:02d}:{i%60:02d}:00Z",
        "field1": f"P{i:03d}",
        "field2": f"Patient {i}",
        # ... other fields
    }
    for i in range(250)
]

results = batch_sync_to_thingspeak(
    channel_id="YOUR_CHANNEL_ID",
    write_api_key="YOUR_WRITE_KEY",
    all_updates=all_updates,
    batch_size=100
)

print(f"Synced {len(all_updates)} updates in {len(results)} batches")
```

## Example 6: Error Handling

```python
def safe_bulk_write(channel_id, write_api_key, updates, max_retries=3):
    """
    Bulk write with retry logic.
    
    Args:
        channel_id: ThingSpeak channel ID
        write_api_key: Write API key
        updates: List of updates
        max_retries: Maximum retry attempts
        
    Returns:
        Response dictionary or None on failure
    """
    for attempt in range(max_retries):
        try:
            result = bulk_write_to_thingspeak(channel_id, write_api_key, updates)
            return result
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries exceeded")
                return None


# Example usage with error handling
updates = [
    {
        "created_at": "2025-11-20T10:00:00Z",
        "field1": "P001",
        "field2": "John Doe"
    }
]

result = safe_bulk_write(
    channel_id="YOUR_CHANNEL_ID",
    write_api_key="YOUR_WRITE_KEY",
    updates=updates
)

if result:
    print("Sync successful!")
else:
    print("Sync failed after retries")
```

## Example 7: Using REST API Enhancements

### Check Channel Status Before Writing

```python
from services.thingspeak_bulk_service import thingspeak_bulk_service

# Check channel health before bulk write
health = thingspeak_bulk_service.health_check()

if health['healthy']:
    print("All channels are healthy, proceeding with sync...")
    
    # Get status for specific channel
    status = thingspeak_bulk_service.get_channel_status('patient_info')
    print(f"Channel: {status.get('name')}")
    print(f"Last Entry ID: {status.get('last_entry_id')}")
    print(f"Updated: {status.get('updated_at')}")
else:
    print("Some channels are unavailable:")
    for channel, info in health['channels'].items():
        if not info.get('available'):
            print(f"  - {channel}: {info.get('error')}")
```

### Bulk Write with Validation and Verification

```python
from services.thingspeak_bulk_service import thingspeak_bulk_service, ThingSpeakBulkError

# Prepare updates
updates = [
    {
        "created_at": "2025-11-20T10:00:00Z",
        "field1": "P001",
        "field2": "John Doe",
        "field3": "1",
        "field4": "101"
    }
]

# Prepare feeds in ThingSpeak format
feeds = []
for update in updates:
    feed = {
        'created_at': update['created_at'],
        'field1': update['field1'],
        'field2': update['field2'],
        'field3': update['field3'],
        'field4': update['field4']
    }
    feeds.append(feed)

try:
    # Write with validation (checks channel status first)
    # and verification (confirms write succeeded)
    result = thingspeak_bulk_service.bulk_write_to_channel(
        channel_name='patient_info',
        feeds=feeds,
        validate_before_write=True,  # Check channel status first
        verify_after_write=True       # Verify write succeeded
    )
    
    print(f"✓ Wrote {result['feeds_written']} entries")
    
    if result.get('verification'):
        verification = result['verification']
        if verification['verified']:
            print(f"✓ Write verified: {verification['actual_count']} entries confirmed")
        else:
            print(f"⚠ Write verification failed")
            
except ThingSpeakBulkError as e:
    print(f"✗ Bulk write failed: {e}")
```

### Get Last Entry ID for Sync Tracking

```python
from services.thingspeak_bulk_service import thingspeak_bulk_service

# Get last entry ID to know where to start next sync
for channel in ['patient_info', 'medicine_prescription', 'medicine_track']:
    last_id = thingspeak_bulk_service.get_last_entry_id(channel)
    if last_id:
        print(f"{channel}: Last entry ID = {last_id}")
    else:
        print(f"{channel}: No entries or channel unavailable")
```

### Enhanced Error Handling

```python
from services.thingspeak_bulk_service import thingspeak_bulk_service, ThingSpeakBulkError
import requests

try:
    result = thingspeak_bulk_service.bulk_write_to_channel(
        channel_name='patient_info',
        feeds=feeds
    )
except ThingSpeakBulkError as e:
    error_msg = str(e)
    
    # Check for specific error types
    if "400" in error_msg or "Bad request" in error_msg:
        print("Invalid data format - check field values")
    elif "401" in error_msg or "Authentication failed" in error_msg:
        print("Invalid API key - check credentials")
    elif "404" in error_msg or "not found" in error_msg:
        print("Channel not found - verify channel ID")
    elif "429" in error_msg or "Rate limit" in error_msg:
        print("Rate limit exceeded - wait before retrying")
    elif "timeout" in error_msg.lower():
        print("Request timeout - check network connection")
    else:
        print(f"Unexpected error: {error_msg}")
```

## Notes

1. **Maximum Updates**: ThingSpeak bulk write API accepts up to 100 updates per request
2. **Rate Limits**: Standard ThingSpeak rate limits apply (15 seconds between requests)
3. **Timestamps**: Use ISO 8601 format with UTC timezone (e.g., "2025-11-20T10:00:00Z")
4. **Field Format**: Use field1-field8 keys matching your channel configuration
5. **Batching**: For large datasets, batch updates to respect the 100-update limit
6. **Validation**: Enable `validate_before_write=True` to check channel status before writing
7. **Verification**: Enable `verify_after_write=True` to confirm data was written correctly
8. **Timeout**: Default timeout is 30 seconds, configurable in ThingSpeakBulkService
9. **Success Codes**: ThingSpeak Bulk Write API returns 200 (OK) or 202 (Accepted) for successful writes

## References

- [ThingSpeak Bulk Write API Documentation](https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html)
- [ThingSpeak REST API Reference](https://www.mathworks.com/help/thingspeak/rest-api.html)
