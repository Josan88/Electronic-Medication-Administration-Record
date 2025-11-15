# Deployment Guide

This comprehensive guide covers deploying the Electronic Medication Administration Record (eMAR) system in various environments, from local development to production deployments.

## Table of Contents

- [Quick Start (Local Development)](#quick-start-local-development)
- [Environment Configuration](#environment-configuration)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Network Deployment](#network-deployment)
- [Troubleshooting](#troubleshooting)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Quick Start (Local Development)

### Prerequisites

**Required:**
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for ThingSpeak API access)

**Optional:**
- Git (for cloning repository)
- Virtual environment tool (venv, virtualenv, or conda)

### Installation Steps

1. **Clone the repository:**

```bash
git clone https://github.com/Josan88/Electronic-Medication-Administration-Record.git
cd Electronic-Medication-Administration-Record
```

2. **Create and activate a virtual environment (recommended):**

```bash
# Using venv (Python 3.3+)
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your ThingSpeak API keys
# (See Environment Configuration section below)
```

5. **Start the application:**

```bash
python app.py
```

6. **Access the application:**

Open your browser and navigate to:
- **Main UI**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/api/health

---

## Environment Configuration

### ThingSpeak Setup

Before configuring the application, you need to set up three ThingSpeak channels:

1. **Create a ThingSpeak Account**
   - Visit https://thingspeak.com
   - Sign up for a free account

2. **Create Three Channels**

   **Channel 1: Patient Information**
   - Name: eMAR - Patient Info
   - Fields:
     - Field1: Patient_ID
     - Field2: Name
     - Field3: Floor
     - Field4: Room
     - Field5: Bed
     - Field6: Age
     - Field7: Gender
     - Field8: Notes

   **Channel 2: Medicine Prescriptions**
   - Name: eMAR - Prescriptions
   - Fields:
     - Field1: Patient_ID
     - Field2: Medicine_Name
     - Field3: Dosage
     - Field4: Frequency
     - Field5: Start_Date
     - Field6: End_Date
     - Field7: Time_Slot

   **Channel 3: Medication Tracking**
   - Name: eMAR - Tracking
   - Fields:
     - Field1: Patient_ID
     - Field2: Medicine_Name
     - Field3: Dosage
     - Field4: Consume_Date
     - Field5: Time_Slot

3. **Get API Keys**

   For each channel, navigate to:
   - Channel Settings → API Keys
   - Copy the Write API Key and Read API Key (or Channel ID for Read)

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-to-random-string

# ThingSpeak Patient Information Channel
PATIENT_CHANNEL_ID=your_patient_channel_id
PATIENT_WRITE_KEY=your_patient_write_key
PATIENT_READ_KEY=your_patient_read_key

# ThingSpeak Medicine Prescription Channel
PRESCRIPTION_CHANNEL_ID=your_prescription_channel_id
PRESCRIPTION_WRITE_KEY=your_prescription_write_key
PRESCRIPTION_READ_KEY=your_prescription_read_key

# ThingSpeak Medicine Tracking Channel
TRACKING_CHANNEL_ID=your_tracking_channel_id
TRACKING_WRITE_KEY=your_tracking_write_key
TRACKING_READ_KEY=your_tracking_read_key
```

### Generating a Secret Key

The `SECRET_KEY` is used by Flask for session management and CSRF protection. Generate a strong random key:

```python
# Python method
import secrets
print(secrets.token_hex(32))
```

Or use:

```bash
# Unix/Linux/macOS
python -c "import secrets; print(secrets.token_hex(32))"

# Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"
```

### Environment Variable Validation

The application will validate all environment variables on startup. If any are missing or invalid, you'll see an error message like:

```
ConfigError: Missing required environment variable: PATIENT_WRITE_KEY
```

Fix the issue by updating your `.env` file and restart the application.

---

## Development Deployment

### Running the Development Server

The Flask development server is suitable for local development and testing:

```bash
python app.py
```

**Features:**
- Auto-reload on code changes (debug mode enabled)
- Detailed error messages in browser
- Interactive debugger
- Runs on http://0.0.0.0:5000 (accessible from all network interfaces)

**Limitations:**
- Not suitable for production use
- Single-threaded (handles one request at a time)
- Less secure (debug mode exposes sensitive information)
- Lower performance

### Development Best Practices

1. **Use a Virtual Environment**
   - Isolates project dependencies
   - Prevents conflicts with system Python packages

2. **Enable Logging**
   - Check console output for errors
   - Monitor background worker activity
   - Review ThingSpeak API responses

3. **Test API Endpoints**
   - Use Swagger UI at http://localhost:5000/api/docs
   - Run automated tests: `python -m pytest` (if pytest is installed)
   - Test rate limit handling

4. **Monitor Queue Status**
   - Check queue status: http://localhost:5000/api/queue/status
   - Monitor failed items and retry attempts
   - Clear failed items if needed

5. **Version Control**
   - Never commit `.env` file (add to `.gitignore`)
   - Use `.env.example` as a template
   - Document any configuration changes

---

## Production Deployment

### Overview

Production deployments require additional considerations for security, performance, and reliability.

### Using a Production WSGI Server

Replace Flask's development server with a production-grade WSGI server:

#### Option 1: Gunicorn (Recommended for Linux/Unix)

1. **Install Gunicorn:**

```bash
pip install gunicorn
```

2. **Start the application:**

```bash
# Basic usage
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile access.log \
  --error-logfile error.log \
  --log-level info \
  app:app

# With worker timeout (for long-running requests)
gunicorn -w 4 -b 0.0.0.0:5000 \
  --timeout 60 \
  --worker-class sync \
  app:app
```

**Configuration Options:**
- `-w 4`: Number of worker processes (recommend 2-4 × CPU cores)
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--timeout 60`: Worker timeout in seconds
- `--worker-class sync`: Worker type (sync, gevent, eventlet)

#### Option 2: uWSGI (Alternative)

1. **Install uWSGI:**

```bash
pip install uwsgi
```

2. **Create a uWSGI configuration file (`uwsgi.ini`):**

```ini
[uwsgi]
module = app:app
master = true
processes = 4
threads = 2
socket = 0.0.0.0:5000
protocol = http
vacuum = true
die-on-term = true
logto = /var/log/emar/uwsgi.log
```

3. **Start the application:**

```bash
uwsgi --ini uwsgi.ini
```

#### Option 3: Waitress (Windows-compatible)

1. **Install Waitress:**

```bash
pip install waitress
```

2. **Create a startup script (`serve.py`):**

```python
from waitress import serve
from app import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=4)
```

3. **Start the application:**

```bash
python serve.py
```

### Reverse Proxy Setup

Use a reverse proxy (Nginx or Apache) in front of the WSGI server for:
- SSL/TLS termination
- Load balancing
- Static file serving
- Security headers
- Rate limiting

#### Nginx Configuration

1. **Install Nginx:**

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. **Create Nginx configuration (`/etc/nginx/sites-available/emar`):**

```nginx
upstream emar_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Certificate Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client body size (for file uploads)
    client_max_body_size 10M;
    
    # Static files
    location /static {
        alias /path/to/emar/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API and application
    location / {
        proxy_pass http://emar_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /api/health {
        proxy_pass http://emar_app/api/health;
        access_log off;
    }
}
```

3. **Enable the configuration:**

```bash
sudo ln -s /etc/nginx/sites-available/emar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/TLS Certificate Setup

#### Using Let's Encrypt (Free)

1. **Install Certbot:**

```bash
# Ubuntu/Debian
sudo apt-get install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

2. **Obtain certificate:**

```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal:**

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

### Systemd Service (Linux)

Create a systemd service for automatic startup and management:

1. **Create service file (`/etc/systemd/system/emar.service`):**

```ini
[Unit]
Description=eMAR Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/emar
Environment="PATH=/path/to/emar/venv/bin"
ExecStart=/path/to/emar/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

2. **Enable and start the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable emar
sudo systemctl start emar
sudo systemctl status emar
```

3. **Manage the service:**

```bash
# Start
sudo systemctl start emar

# Stop
sudo systemctl stop emar

# Restart
sudo systemctl restart emar

# View logs
sudo journalctl -u emar -f
```

### Environment-Specific Configuration

#### Disabling Debug Mode

Edit `app.py` and change the last line:

```python
# Development (debug=True)
app.run(debug=True, host="0.0.0.0", port=5000)

# Production (debug=False)
app.run(debug=False, host="127.0.0.1", port=8000)
```

Or better, use environment variables:

```python
import os

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    port = int(os.getenv('FLASK_PORT', 8000))
    app.run(debug=debug_mode, host="127.0.0.1", port=port)
```

#### Queue Storage Location

For production, store the queue file in a persistent location:

Edit `services/queue_service.py` and update the queue file path:

```python
# Development
queue_file = "/tmp/prescription_queue.json"

# Production
queue_file = "/var/lib/emar/prescription_queue.json"
```

Make sure the directory exists and has proper permissions:

```bash
sudo mkdir -p /var/lib/emar
sudo chown www-data:www-data /var/lib/emar
sudo chmod 755 /var/lib/emar
```

---

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for queue storage
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=False

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  emar:
    build: .
    container_name: emar-app
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - PATIENT_CHANNEL_ID=${PATIENT_CHANNEL_ID}
      - PATIENT_WRITE_KEY=${PATIENT_WRITE_KEY}
      - PATIENT_READ_KEY=${PATIENT_READ_KEY}
      - PRESCRIPTION_CHANNEL_ID=${PRESCRIPTION_CHANNEL_ID}
      - PRESCRIPTION_WRITE_KEY=${PRESCRIPTION_WRITE_KEY}
      - PRESCRIPTION_READ_KEY=${PRESCRIPTION_READ_KEY}
      - TRACKING_CHANNEL_ID=${TRACKING_CHANNEL_ID}
      - TRACKING_WRITE_KEY=${TRACKING_WRITE_KEY}
      - TRACKING_READ_KEY=${TRACKING_READ_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Build and Run

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

---

## Network Deployment

### Local Network Access

To make the application accessible from other devices on your local network:

1. **Find your IP address:**

```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
# or
ip addr show
```

2. **Start the application binding to all interfaces:**

```bash
python app.py
# (Already configured to bind to 0.0.0.0)
```

3. **Configure firewall (if needed):**

```bash
# Windows Firewall
netsh advfirewall firewall add rule name="eMAR" dir=in action=allow protocol=TCP localport=5000

# Linux (ufw)
sudo ufw allow 5000/tcp

# Linux (firewalld)
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

4. **Access from other devices:**

Open a browser and navigate to:
- `http://YOUR_IP:5000`
- Example: `http://192.168.1.100:5000`

### Port Configuration

To change the port, edit `app.py`:

```python
# Change port to 8080
app.run(debug=True, host="0.0.0.0", port=8080)
```

Or use an environment variable:

```python
import os
port = int(os.getenv('FLASK_PORT', 5000))
app.run(debug=True, host="0.0.0.0", port=port)
```

---

## Troubleshooting

### Application Won't Start

**Symptom:** Application exits immediately or shows import errors

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

4. **Check for port conflicts:**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   
   # Linux/macOS
   lsof -i :5000
   ```

### ThingSpeak Connection Issues

**Symptom:** API returns 500 errors, logs show connection failures

**Solutions:**

1. **Verify internet connection:**
   ```bash
   ping thingspeak.com
   ```

2. **Check API keys:**
   - Verify keys in `.env` are correct
   - Test keys directly on ThingSpeak website

3. **Check rate limits:**
   - Wait 15 seconds between write operations
   - Check queue status for backed-up items

4. **Verify channel IDs:**
   - Ensure channel IDs match your ThingSpeak channels
   - Check channel privacy settings

### Queue Not Processing

**Symptom:** Prescriptions queued but never written to ThingSpeak

**Solutions:**

1. **Check background worker:**
   ```bash
   # Look for "Prescription queue worker started" in logs
   python app.py
   ```

2. **Check queue status:**
   ```bash
   curl http://localhost:5000/api/queue/status
   ```

3. **Check queue file permissions:**
   ```bash
   ls -l /tmp/prescription_queue.json
   # or wherever queue is stored
   ```

4. **Clear failed items:**
   ```bash
   curl -X POST http://localhost:5000/api/queue/clear-failed
   ```

### Rate Limit Errors

**Symptom:** HTTP 429 errors or "rate limit exceeded" messages

**Solutions:**

1. **Wait for rate limit to reset** (15 seconds per channel)

2. **Use prescription queue** instead of direct writes

3. **Upgrade ThingSpeak account** for higher rate limits

### Page Not Loading / 404 Errors

**Symptom:** Browser shows "404 Not Found"

**Solutions:**

1. **Check application is running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Verify URL:**
   - Main page: `http://localhost:5000`
   - Not: `http://localhost:5000/index.html`

3. **Check reverse proxy configuration** (if using Nginx/Apache)

### Data Not Appearing

**Symptom:** Data submitted but not showing in UI

**Solutions:**

1. **Wait 2-3 seconds** for ThingSpeak sync delay

2. **Click Refresh button** in UI

3. **Check ThingSpeak directly:**
   - Visit your channels on thingspeak.com
   - Verify data was written

4. **Check browser console** for JavaScript errors (F12)

---

## Monitoring and Maintenance

### Application Monitoring

#### Health Check

The `/api/health` endpoint provides a simple health check:

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Electronic Medication Administration Record API is running"
}
```

#### Queue Status Monitoring

Monitor the prescription queue:

```bash
curl http://localhost:5000/api/queue/status
```

Response includes:
- Current queue size
- Failed items count
- Processing statistics
- Failed items details

#### Log Monitoring

Application logs provide detailed information:

```bash
# View logs in real-time
tail -f /var/log/emar/app.log

# Search for errors
grep ERROR /var/log/emar/app.log

# View systemd logs
sudo journalctl -u emar -f
```

### Performance Monitoring

#### System Resources

Monitor system resources:

```bash
# CPU and memory usage
top
# or
htop

# Disk usage
df -h

# Network connections
netstat -an | grep :5000
```

#### Application Metrics

Consider integrating monitoring tools:

- **Prometheus** for metrics collection
- **Grafana** for visualization
- **ELK Stack** (Elasticsearch, Logstash, Kibana) for log analysis
- **New Relic** or **Datadog** for APM

### Backup and Recovery

#### Queue Backup

The prescription queue is automatically persisted to disk. Backup the queue file:

```bash
# Daily backup
cp /var/lib/emar/prescription_queue.json /backup/prescription_queue_$(date +%Y%m%d).json

# Restore from backup
cp /backup/prescription_queue_20251115.json /var/lib/emar/prescription_queue.json
sudo systemctl restart emar
```

#### ThingSpeak Backup

ThingSpeak data is stored in the cloud. To backup:

1. Export data from each channel:
   - Channel Settings → Data Import/Export
   - Export as CSV or JSON

2. Automate with ThingSpeak API:
   ```python
   import requests
   
   channel_id = "YOUR_CHANNEL_ID"
   read_key = "YOUR_READ_KEY"
   url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}&results=8000"
   
   response = requests.get(url)
   with open(f"backup_{channel_id}.json", "w") as f:
       f.write(response.text)
   ```

### Updates and Upgrades

#### Updating the Application

1. **Backup current version:**
   ```bash
   cp -r /path/to/emar /backup/emar_$(date +%Y%m%d)
   ```

2. **Pull latest code:**
   ```bash
   cd /path/to/emar
   git pull origin main
   ```

3. **Update dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Restart application:**
   ```bash
   sudo systemctl restart emar
   ```

5. **Verify:**
   ```bash
   curl http://localhost:5000/api/health
   ```

#### Dependency Updates

Regularly update dependencies for security patches:

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade flask

# Update all packages (use with caution)
pip install -r requirements.txt --upgrade

# Test after updates
python -m pytest
```

### Security Maintenance

1. **Regular security audits:**
   ```bash
   # Check for known vulnerabilities
   pip install safety
   safety check
   ```

2. **Update SSL certificates:**
   ```bash
   sudo certbot renew
   ```

3. **Review access logs:**
   ```bash
   sudo tail -f /var/log/nginx/access.log
   ```

4. **Monitor failed login attempts** (if authentication is implemented)

5. **Keep system updated:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get upgrade
   
   # CentOS/RHEL
   sudo yum update
   ```

---

## Production Checklist

Before deploying to production, verify:

- [ ] All environment variables configured in `.env`
- [ ] `.env` file added to `.gitignore`
- [ ] Secret key is strong and random
- [ ] Debug mode disabled (`debug=False`)
- [ ] Using production WSGI server (Gunicorn/uWSGI/Waitress)
- [ ] Reverse proxy configured (Nginx/Apache)
- [ ] SSL/TLS certificate installed and configured
- [ ] Firewall rules configured
- [ ] Queue storage location is persistent
- [ ] Systemd service created (Linux)
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Health check endpoint accessible
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security headers configured
- [ ] Rate limiting configured (if needed)
- [ ] CORS configured (if needed for external API access)

---

## Support

For additional help:

- **Documentation**: See README.md and ARCHITECTURE.md
- **API Reference**: http://localhost:5000/api/docs
- **Issues**: https://github.com/Josan88/Electronic-Medication-Administration-Record/issues
- **ThingSpeak Support**: https://www.mathworks.com/help/thingspeak/

---

*Last Updated: November 15, 2025*
