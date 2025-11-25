# Local Database with ThingSpeak Bulk Write Backup

## Overview

This document describes the local database system with ThingSpeak bulk write backup implementation for the eMAR system. This architecture overcomes ThingSpeak's 15-second write rate limit by using a local JSON database as primary storage with periodic synchronization to ThingSpeak as a backup.

## Architecture

### Components

1. **Local Database Service** (`services/local_db_service.py`)
   - JSON file-based storage for patients, prescriptions, and tracking data
   - Data structure aligned with ThingSpeak's field format
   - No write rate limits
   - Thread-safe operations

2. **ThingSpeak Bulk Write Service** (`services/thingspeak_bulk_service.py`)
   - Implements ThingSpeak Bulk Write API
   - Batches multiple records into single API calls
   - Handles up to 100 records per batch

3. **Sync Service** (`services/sync_service.py`)
   - Manages periodic synchronization queue
   - Implements retry logic with exponential backoff
   - Persists queue state to disk
   - Tracks last synced entry_id per channel

4. **Hybrid Service** (`services/hybrid_service.py`)
   - Unified interface for data operations
   - Uses local database as primary storage
   - Falls back to ThingSpeak for reads if local data unavailable
   - Maintains backward compatibility with existing API

### Data Flow

```
Client Request
    ↓
API Route
    ↓
Hybrid Service
    ↓
Local Database (Primary)     →     Sync Queue     →     ThingSpeak (Backup)
    ↓                                   ↓                      ↓
Immediate Response              Background Worker        Bulk Write API
```

## Configuration

### Environment Variables

Add these optional variables to your `.env` file:

```bash
# Local Database Configuration
LOCAL_DB_PATH=/tmp/emar_local_db              # Default: /tmp/emar_local_db
SYNC_INTERVAL_SECONDS=300                      # Default: 300 (5 minutes)
```

### Storage Locations

- **Local Database**: `${LOCAL_DB_PATH}/` (default: `/tmp/emar_local_db/`)
  - `patient_info.json`
  - `medicine_prescription.json`
  - `medicine_track.json`

- **Sync Queue**: `/tmp/emar_sync_queue.json`

- **Prescription Queue**: `/tmp/prescription_queue.json` (legacy queue for prescription writes)

## Local Database Format

### Channel Structure

Each channel is stored as a JSON file with the following structure:

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
      "field8": "Test notes"
    }
  ],
  "metadata": {
    "created_at": "2025-11-20T09:00:00Z",
    "last_updated": "2025-11-20T10:00:00Z",
    "entry_count": 1
  }
}
```

### Field Mappings

The local database uses the same field mappings as ThingSpeak for compatibility:

#### Patient Info (patient_info)
- `field1`: Patient_ID
- `field2`: Name
- `field3`: Floor
- `field4`: Room
- `field5`: Bed
- `field6`: Age
- `field7`: Gender
- `field8`: Notes

#### Medicine Prescription (medicine_prescription)
- `field1`: Patient_ID
- `field2`: Medicine_Name
- `field3`: Dosage
- `field4`: Frequency
- `field5`: Start_Date
- `field6`: End_Date
- `field7`: Time_Slot

#### Medicine Tracking (medicine_track)
- `field1`: Patient_ID
- `field2`: Medicine_Name
- `field3`: Dosage
- `field4`: Consume_Date
- `field5`: Time_Slot

## ThingSpeak Bulk Write API

### API Endpoint

```
POST https://api.thingspeak.com/channels/{channel_id}/bulk_update.json
```

### Request Format

```json
{
  "write_api_key": "YOUR_CHANNEL_WRITE_API_KEY",
  "updates": [
    {
      "created_at": "2025-11-20T10:00:00Z",
      "field1": "value1",
      "field2": "value2",
      "field3": "value3"
    },
    {
      "created_at": "2025-11-20T10:05:00Z",
      "field1": "value4",
      "field2": "value5",
      "field3": "value6"
    }
  ]
}
```

### Response Format

```json
{
  "success": true,
  "status": "accepted",
  "channel_id": "123456"
}
```

### Rate Limits

- Maximum 100 updates per request
- Standard ThingSpeak API rate limits apply (15 seconds between requests)

### REST API Enhancements

The bulk write service now includes enhanced features from the ThingSpeak REST API:

**Channel Validation**
- Pre-write channel availability checks using REST API
- Validates channel status before attempting bulk writes
- Reduces failed write attempts due to channel unavailability

**Enhanced Error Handling**
- Accepts both 200 (OK) and 202 (Accepted) status codes as successful responses
- Status code-specific error messages (400, 401, 404, 429)
- Timeout configuration (30 seconds default)
- Detailed error logging with API response details

**Health Monitoring**
- Channel health check endpoint
- Last entry ID tracking per channel
- Channel update timestamp monitoring

**Write Verification** (Optional)
- Post-write verification to ensure data integrity
- Compares expected vs actual entry count
- Available via `verify_after_write` parameter

## Synchronization Process

### Automatic Sync

The system automatically syncs data to ThingSpeak in the background:

1. **Trigger**: Every 5 minutes (configurable via `SYNC_INTERVAL_SECONDS`)
2. **Process**:
   - Identify new entries since last sync (using entry_id tracking)
   - Batch entries (max 100 per batch)
   - Send to ThingSpeak using bulk write API
   - Update last synced entry_id on success
   - Retry with exponential backoff on failure

### Rate Limiting

To prevent ThingSpeak API rate limit errors:

- **Deduplication**: Only one sync operation per channel can be pending at a time
- **Rate Limit Enforcement**: 15-second minimum delay between writes to the same channel
- **Batch Delays**: 15-second delay between batches for the same channel
- **Smart Queuing**: Sync operations wait if rate limit not yet satisfied

### Retry Logic

- **Max Attempts**: 5 per sync operation
- **Backoff Strategy**: Exponential (60s, 120s, 240s, 480s, 960s)
- **Failed Items**: Tracked separately and can be cleared via API

## API Endpoints

### Sync Status Monitoring

#### Get Sync Status

```http
GET /api/queue/sync-status
```

**Response:**

```json
{
  "success": true,
  "data": {
    "pending_count": 0,
    "failed_count": 0,
    "stats": {
      "total_synced": 150,
      "total_failed": 2,
      "total_retried": 5,
      "last_sync_time": 1700475600.0
    },
    "last_synced_entry_ids": {
      "patient_info": 50,
      "medicine_prescription": 75,
      "medicine_track": 100
    },
    "next_sync_times": {},
    "failed_items": []
  }
}
```

#### Clear Failed Sync Items

```http
POST /api/queue/sync-clear-failed
```

**Response:**

```json
{
  "success": true,
  "message": "Cleared 2 failed sync items",
  "data": {
    "cleared_count": 2
  }
}
```

#### Get ThingSpeak Backup Health Status

```http
GET /api/queue/thingspeak-health
```

**Response:**

```json
{
  "success": true,
  "data": {
    "healthy": true,
    "channels": {
      "patient_info": {
        "available": true,
        "last_entry_id": 150,
        "updated_at": "2025-11-20T10:00:00Z"
      },
      "medicine_prescription": {
        "available": true,
        "last_entry_id": 200,
        "updated_at": "2025-11-20T10:05:00Z"
      },
      "medicine_track": {
        "available": true,
        "last_entry_id": 300,
        "updated_at": "2025-11-20T10:10:00Z"
      }
    },
    "timestamp": "2025-11-20T10:15:00Z"
  }
}
```

This endpoint uses the ThingSpeak REST API to validate channel availability and retrieve current status before sync operations.

## Error Handling

### Local Database Unavailable

If the local database is unavailable:

1. **Reads**: Automatically fall back to ThingSpeak
2. **Writes**: Return error to client (local database is primary)

### ThingSpeak Unavailable

If ThingSpeak is unavailable during sync:

1. Sync operation is marked as failed
2. Retry with exponential backoff
3. Data remains in local database
4. No data loss occurs
5. Failed syncs are tracked and can be retried

### Recovery Scenarios

#### Scenario 1: ThingSpeak Temporarily Down

```
1. Write to local database succeeds
2. Sync to ThingSpeak fails
3. Sync operation queued for retry
4. Automatic retry after 60 seconds
5. Sync succeeds on retry
```

#### Scenario 2: Local Database Corruption

```
1. Read from local database fails
2. Automatic fallback to ThingSpeak
3. Data retrieved from ThingSpeak backup
4. Manual intervention needed to fix local database
```

## Performance Benefits

### Write Operations

- **Before**: 15 second delay per write (ThingSpeak rate limit)
- **After**: Instant write to local database, async sync to ThingSpeak
- **Improvement**: ~99% reduction in write latency

### Batch Efficiency

- **Single Writes**: 100 records = 25 minutes (100 × 15s)
- **Bulk Write**: 100 records = 1 request (~2 seconds)
- **Improvement**: ~99% reduction in sync time

## Testing

### Run Integration Tests

```bash
python test_local_db_integration.py
```

### Test Coverage

1. **Local Database Operations**
   - CRUD operations
   - Field mapping
   - Bulk write format generation

2. **Sync Queue Operations**
   - Queue management
   - Retry logic
   - State persistence

3. **Hybrid Service Integration**
   - Read/write operations
   - Fallback behavior
   - Patient existence checks

4. **Bulk Write Format**
   - Batch preparation
   - Large batch handling

## Monitoring

### Health Checks

Monitor these metrics to ensure system health:

1. **Sync Queue Status** (`/api/queue/sync-status`)
   - Pending sync count (should be low)
   - Failed sync count (should be zero or low)
   - Time since last successful sync

2. **Local Database**
   - Disk space usage
   - Entry counts per channel
   - File integrity

3. **ThingSpeak Backup**
   - Last synced entry_ids
   - Sync success rate
   - Error patterns

### Alerts

Set up alerts for:

- Failed sync count > 10
- Time since last sync > 15 minutes
- Disk space usage > 80%
- High error rates in logs

## Troubleshooting

### Sync Not Working

1. Check sync status: `GET /api/queue/sync-status`
2. Review logs for errors
3. Verify ThingSpeak API credentials
4. Check network connectivity
5. Clear failed items: `POST /api/queue/sync-clear-failed`

### Local Database Issues

1. Check disk space: `df -h /tmp`
2. Verify file permissions
3. Check for corruption: inspect JSON files
4. Clear and reinitialize if needed

### High Failed Sync Count

1. Check ThingSpeak API status
2. Verify API keys are valid
3. Review error messages in failed items
4. Check for rate limit issues
5. Consider increasing sync interval

## Migration Guide

### Migrating Existing Data

If you have existing data in ThingSpeak:

1. **Read from ThingSpeak**: The hybrid service will automatically fall back to ThingSpeak for reads
2. **New Writes**: Go to local database immediately
3. **Sync**: New data syncs to ThingSpeak as backup
4. **Convergence**: Over time, all active data will exist in both locations

### Rollback Plan

To rollback to ThingSpeak-only:

1. Stop the application
2. Update routes to use `thingspeak_service` instead of `hybrid_service`
3. Remove sync worker from `app.py`
4. Restart the application

## Best Practices

1. **Backup**: Regularly backup local database files
2. **Monitoring**: Monitor sync status and error rates
3. **Disk Space**: Ensure adequate disk space for local database
4. **Network**: Ensure reliable network for ThingSpeak sync
5. **Testing**: Test failover scenarios regularly

## References

- [ThingSpeak Bulk Write API Documentation](https://www.mathworks.com/help/thingspeak/bulkwritejsondata.html)
- [eMAR Architecture Documentation](docs/ARCHITECTURE.md)
- [eMAR API Documentation](swagger.yaml)
