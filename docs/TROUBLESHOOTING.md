# Troubleshooting Guide

This guide consolidates all troubleshooting information for the eMAR system. Use this as your first resource when encountering issues.

## Table of Contents

- [Quick Diagnostic Commands](#quick-diagnostic-commands)
- [Application Startup Issues](#application-startup-issues)
- [ThingSpeak Connection Issues](#thingspeak-connection-issues)
- [Queue and Sync Issues](#queue-and-sync-issues)
- [Local Database Issues](#local-database-issues)
- [Rate Limit Errors](#rate-limit-errors)
- [UI and Data Display Issues](#ui-and-data-display-issues)
- [Network and Connectivity](#network-and-connectivity)
- [Node-RED Integration Issues](#node-red-integration-issues)
- [Common Error Codes](#common-error-codes)
- [Getting Help](#getting-help)

---

## Quick Diagnostic Commands

Run these commands to quickly diagnose common issues:

```bash
# Check if application is running
curl http://localhost:5000/api/health

# Check Python version (should be 3.8+)
python --version

# Check queue status
curl http://localhost:5000/api/queue/status

# Check sync status (if using local database)
curl http://localhost:5000/api/queue/sync-status

# Check ThingSpeak backup health
curl http://localhost:5000/api/queue/thingspeak-health

# Verify environment configuration
python -c "from config import config; print('Config OK')"

# Check if port 5000 is in use
# Windows
netstat -ano | findstr :5000
# Linux/macOS
lsof -i :5000
```

---

## Application Startup Issues

### Application Won't Start

**Symptom:** Application exits immediately or shows import errors.

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check for missing environment variables:**
   ```bash
   python -c "from config import config"
   # Will show which variable is missing
   ```

4. **Check for syntax errors:**
   ```bash
   python -m py_compile app.py
   ```

### Port 5000 Already in Use

**Symptom:** Error message `Address already in use` or `Port 5000 is in use`.

**Solutions:**

1. **Find and kill the process:**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F

   # Linux/macOS
   lsof -i :5000
   kill -9 <PID>
   ```

2. **Change the port in `app.py`:**
   ```python
   app.run(debug=True, host="0.0.0.0", port=5001)
   ```

### Missing Environment Variables

**Symptom:** `ConfigError: Missing required environment variable: XXXX`

**Solutions:**

1. **Verify `.env` file exists:**
   ```bash
   # Check if .env exists
   ls -la .env

   # Copy from example if missing
   cp .env.example .env
   ```

2. **Check all required variables are set:**
   - `SECRET_KEY`
   - `PATIENT_CHANNEL_ID`, `PATIENT_WRITE_KEY`, `PATIENT_READ_KEY`
   - `PRESCRIPTION_CHANNEL_ID`, `PRESCRIPTION_WRITE_KEY`, `PRESCRIPTION_READ_KEY`
   - `TRACKING_CHANNEL_ID`, `TRACKING_WRITE_KEY`, `TRACKING_READ_KEY`

3. **Ensure no trailing spaces in `.env` values**

---

## ThingSpeak Connection Issues

### API Returns 500 Errors

**Symptom:** API calls fail with internal server errors, logs show ThingSpeak connection failures.

**Solutions:**

1. **Verify internet connection:**
   ```bash
   ping thingspeak.com
   curl https://api.thingspeak.com/channels/public.json
   ```

2. **Check API keys:**
   - Verify keys in `.env` are correct (no typos, no extra spaces)
   - Test keys directly on ThingSpeak website
   - Ensure you're using Write keys for POST and Read keys for GET

3. **Verify channel IDs:**
   - Ensure channel IDs match your ThingSpeak channels
   - Check channel privacy settings (should be accessible with your API keys)

4. **Check ThingSpeak service status:**
   - Visit https://thingspeak.com to see if service is operational

### Authentication Errors (401)

**Symptom:** `HTTP 401 Unauthorized` from ThingSpeak API.

**Solutions:**

1. **Verify API keys match the channel:**
   - Each channel has unique Write and Read API keys
   - Ensure Patient keys are used for Patient channel, etc.

2. **Regenerate API keys on ThingSpeak:**
   - Go to Channel Settings > API Keys
   - Generate new keys and update `.env`

### Channel Not Found (404)

**Symptom:** `HTTP 404 Not Found` when accessing ThingSpeak.

**Solutions:**

1. **Verify channel ID is correct:**
   - Go to ThingSpeak and check the channel ID in the URL

2. **Check channel hasn't been deleted**

3. **Ensure channel is not private without proper keys**

---

## Queue and Sync Issues

### Prescriptions Queued but Not Written

**Symptom:** Prescriptions show as queued but never appear in ThingSpeak.

**Solutions:**

1. **Check background worker is running:**
   ```bash
   # Look for "Prescription queue worker started" in startup logs
   python app.py
   ```

2. **Check queue status:**
   ```bash
   curl http://localhost:5000/api/queue/status
   ```
   Look for:
   - `queue_size`: Should decrease over time
   - `failed_count`: Should be 0 or low
   - `stats.total_processed`: Should increase

3. **Check queue file permissions:**
   ```bash
   ls -l /tmp/prescription_queue.json
   # Ensure the file is readable/writable by the app user
   ```

4. **Clear failed items and retry:**
   ```bash
   curl -X POST http://localhost:5000/api/queue/clear-failed
   ```

5. **Check for rate limit issues (see Rate Limit Errors section)**

### Sync Not Working (Local Database Mode)

**Symptom:** Local database has data but ThingSpeak backup is empty/outdated.

**Solutions:**

1. **Check sync status:**
   ```bash
   curl http://localhost:5000/api/queue/sync-status
   ```
   Look for:
   - `pending_count`: Number of items waiting to sync
   - `failed_count`: Items that failed to sync
   - `last_synced_entry_ids`: Should match local data

2. **Check ThingSpeak health:**
   ```bash
   curl http://localhost:5000/api/queue/thingspeak-health
   ```
   All channels should show `"available": true`

3. **Clear failed sync items:**
   ```bash
   curl -X POST http://localhost:5000/api/queue/sync-clear-failed
   ```

4. **Check sync interval:**
   - Default is 5 minutes (300 seconds)
   - Configure via `SYNC_INTERVAL_SECONDS` in `.env`

### High Failed Count in Queue

**Symptom:** Many items showing as failed in queue status.

**Solutions:**

1. **Review failed items:**
   ```bash
   curl http://localhost:5000/api/queue/status | python -m json.tool
   ```
   Check the `failed_items` array for error messages.

2. **Common causes:**
   - Invalid API keys
   - ThingSpeak rate limits
   - Network connectivity issues
   - Invalid data format

3. **After fixing the cause, clear and retry:**
   ```bash
   curl -X POST http://localhost:5000/api/queue/clear-failed
   ```

---

## Local Database Issues

### Local Database Unavailable

**Symptom:** Writes fail, reads fall back to ThingSpeak.

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h /tmp
   # or wherever LOCAL_DB_PATH points
   ```

2. **Verify directory permissions:**
   ```bash
   ls -la /tmp/emar_local_db/
   # Ensure writable by app user
   ```

3. **Check for file corruption:**
   ```bash
   # Try to parse JSON files
   python -c "import json; json.load(open('/tmp/emar_local_db/patient_info.json'))"
   ```

4. **Reinitialize if corrupted:**
   ```bash
   # Backup first!
   cp -r /tmp/emar_local_db /tmp/emar_local_db_backup
   rm -rf /tmp/emar_local_db
   # Restart app - it will recreate the database
   ```

### Data Mismatch Between Local and ThingSpeak

**Symptom:** Different data shown depending on which storage is queried.

**Solutions:**

1. **Force sync to ThingSpeak:**
   - Wait for next sync interval, or
   - Restart the application to trigger immediate sync check

2. **Check last synced entry IDs:**
   ```bash
   curl http://localhost:5000/api/queue/sync-status
   ```

3. **The local database is authoritative** - ThingSpeak is a backup

---

## Rate Limit Errors

### HTTP 429 Too Many Requests

**Symptom:** API returns 429 errors, "rate limit exceeded" in logs.

**Understanding ThingSpeak Limits:**
- Free tier: 1 write per 15 seconds **per channel**
- Patients, Prescriptions, and Tracking are separate channels
- Each can be written to independently every 15 seconds

**Solutions:**

1. **Wait for rate limit to reset:**
   - 15 seconds between writes to the same channel

2. **Use the prescription queue:**
   - POST to `/api/prescriptions` returns HTTP 202 immediately
   - Background worker handles rate limiting automatically

3. **Batch operations:**
   - For bulk imports, space writes 15+ seconds apart
   - Use the bulk write API for local database sync

4. **Consider upgrading ThingSpeak:**
   - Paid plans have higher rate limits

### Writes Taking Too Long

**Symptom:** Patient or tracking writes take ~15 seconds.

**Explanation:** Direct writes (patients, tracking) wait for rate limit compliance.

**Solutions:**

1. **This is expected behavior** for direct ThingSpeak writes

2. **For better UX, consider:**
   - Using local database mode (instant writes)
   - Showing a progress indicator in the UI
   - Queuing the operation (like prescriptions)

---

## UI and Data Display Issues

### Data Not Appearing After Submission

**Symptom:** Form submitted successfully but data doesn't show.

**Solutions:**

1. **Wait 2-3 seconds** for ThingSpeak sync delay

2. **Click the Refresh button** in the UI

3. **Check ThingSpeak directly:**
   - Visit your channels on thingspeak.com
   - Verify data was written

4. **Check browser console (F12):**
   - Look for JavaScript errors
   - Check network tab for failed API calls

### Page Not Loading / 404 Errors

**Symptom:** Browser shows "404 Not Found" or blank page.

**Solutions:**

1. **Verify application is running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Check URL format:**
   - Correct: `http://localhost:5000`
   - Incorrect: `http://localhost:5000/index.html`

3. **Check reverse proxy configuration** (if using Nginx/Apache)

4. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)

### Dashboard Shows Wrong Status

**Symptom:** Medication status (complete/pending) seems incorrect.

**Solutions:**

1. **Understand status calculation:**
   - **Complete**: Medication given within the time slot window
   - **Pending**: Medication not yet given or given outside window

2. **Check time slot format:**
   - Should be comma-separated times: `"09:00, 13:00, 17:00, 21:00"`
   - 24-hour format

3. **Verify consume_date format:**
   - Should be `"YYYY-MM-DD HH:MM:SS"`
   - Example: `"2025-11-15 17:16:27"`

---

## Network and Connectivity

### Cannot Access from Other Devices

**Symptom:** Application works on localhost but not from other devices.

**Solutions:**

1. **Verify binding address:**
   - Application should bind to `0.0.0.0` (all interfaces)
   - Check `app.py`: `app.run(host="0.0.0.0", ...)`

2. **Find your server IP:**
   ```bash
   # Windows
   ipconfig
   # Linux/macOS
   ifconfig
   # or
   ip addr show
   ```

3. **Configure firewall:**
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="eMAR" dir=in action=allow protocol=TCP localport=5000

   # Linux (ufw)
   sudo ufw allow 5000/tcp

   # Linux (firewalld)
   sudo firewall-cmd --add-port=5000/tcp --permanent
   sudo firewall-cmd --reload
   ```

4. **Check router/network restrictions**

### SSL/HTTPS Issues

**Symptom:** HTTPS not working or certificate errors.

**Solutions:**

1. **For development:** Use HTTP (localhost doesn't need HTTPS)

2. **For production:**
   - Use Let's Encrypt with Certbot
   - Ensure certificate is valid and not expired
   - Check certificate chain is complete

3. **Check certificate:**
   ```bash
   openssl s_client -connect your-domain.com:443
   ```

---

## Node-RED Integration Issues

### Patient ID Not Being Read

**Symptom:** Node-RED doesn't receive patient ID from HMI.

**Solutions:**

1. **Verify Modbus connection:**
   - Check IP address: `192.168.250.2:10502`
   - Ensure HMI is writing to registers 0-9

2. **Check register format:**
   - Patient ID should be ASCII encoded
   - 2 characters per register
   - Registers are polled every 1 second

3. **Enable debug nodes** in Node-RED to inspect payloads

### Medications Not Displaying on Notebook

**Symptom:** Prescription data not appearing on HMI notebook.

**Solutions:**

1. **Verify ThingSpeak fetch:**
   - Check `flow.currentPatientMeds` in Node-RED
   - Ensure prescriptions exist for the patient

2. **Check date/time filters:**
   - Current date must be within prescription start/end dates
   - Current time must match a time slot

3. **Verify Modbus write:**
   - Notebook registers start at address 30
   - 10 words per line, 8 lines max

4. **Check NB Designer configuration:**
   - Ensure notebook expects little-endian word order
   - Verify 20-character line width

### Served Button Not Working

**Symptom:** Pressing served button doesn't log medication or clear screen.

**Solutions:**

1. **Check coil address:**
   - Served button is on coil address 1
   - Read with FC3, reset with FC5

2. **Verify link nodes:**
   - `Send served status` should connect to `link in 7`

3. **Check rate limiting:**
   - ThingSpeak logging has 15-second delay between writes

---

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | No action needed |
| 202 | Accepted (Queued) | Prescription queued, will process in background |
| 400 | Bad Request | Check request body format and required fields |
| 401 | Unauthorized | Verify API keys |
| 404 | Not Found | Check endpoint URL or resource ID |
| 429 | Rate Limited | Wait 15 seconds before retrying |
| 500 | Server Error | Check logs, verify ThingSpeak connectivity |
| 507 | Queue Full | Queue at max capacity (1000 items), clear failed items |

### Validation Error Messages

| Error | Meaning |
|-------|---------|
| `Missing required field: X` | Field X is required but not provided |
| `Invalid patient_id format` | Patient ID should match pattern (e.g., P001) |
| `Patient X does not exist` | Must add patient before prescription/tracking |
| `Invalid date format` | Use YYYY-MM-DD format |
| `Invalid dosage format` | Use format like "500mg" or "10ml" |

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review application logs**
3. **Search existing GitHub issues**
4. **Test with minimal reproduction case**

### Gathering Information

When reporting issues, include:

```
1. Operating System:
2. Python Version:
3. Error Message (full):
4. Steps to Reproduce:
5. Expected Behavior:
6. Actual Behavior:
7. Relevant Logs:
```

### Support Channels

- **Documentation**: See [docs/INDEX.md](INDEX.md) for full documentation list
- **API Reference**: http://localhost:5000/api/docs
- **GitHub Issues**: https://github.com/Josan88/Electronic-Medication-Administration-Record/issues
- **ThingSpeak Support**: https://www.mathworks.com/help/thingspeak/

---

*Last Updated: December 2025*
