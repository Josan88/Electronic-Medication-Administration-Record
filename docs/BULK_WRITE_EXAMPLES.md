# ThingSpeak Bulk Write API Examples

This document provides examples of using the ThingSpeak Bulk Write API for the eMAR system.

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

## Notes

1. **Maximum Updates**: ThingSpeak bulk write API accepts up to 100 updates per request
2. **Rate Limits**: Standard ThingSpeak rate limits apply (15 seconds between requests)
3. **Timestamps**: Use ISO 8601 format with UTC timezone (e.g., "2025-11-20T10:00:00Z")
4. **Field Format**: Use field1-field8 keys matching your channel configuration
5. **Batching**: For large datasets, batch updates to respect the 100-update limit

## References

- [ThingSpeak Bulk Write API Documentation](https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html)
- [ThingSpeak REST API Reference](https://www.mathworks.com/help/thingspeak/rest-api.html)
