# eMAR System Architecture

This document provides comprehensive architecture diagrams and explanations for the Electronic Medication Administration Record (eMAR) system.

## Table of Contents
- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow Diagrams](#data-flow-diagrams)
- [ThingSpeak Integration](#thingspeak-integration)
- [Queue Management System](#queue-management-system)

---

## System Overview

The eMAR system is a web-based application that manages patient information, medication prescriptions, and administration tracking using ThingSpeak IoT platform for cloud data storage.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        UI[HTML/CSS/JavaScript UI]
    end
    
    subgraph "Application Layer"
        Flask[Flask Web Server]
        Routes[Route Blueprints]
        Services[Service Layer]
        Validators[Input Validators]
        Utils[Utility Modules]
        Queue[Prescription Queue]
    end
    
    subgraph "Data Layer"
        TS1[ThingSpeak Channel 1<br/>Patient Info]
        TS2[ThingSpeak Channel 2<br/>Prescriptions]
        TS3[ThingSpeak Channel 3<br/>Tracking]
        QFile[Queue Storage<br/>prescription_queue.json]
    end
    
    Browser --> UI
    UI <-->|AJAX/REST| Flask
    Flask --> Routes
    Routes --> Validators
    Validators --> Services
    Services --> Queue
    Services <-->|API Calls| TS1
    Services <-->|API Calls| TS2
    Services <-->|API Calls| TS3
    Queue <-->|Persist| QFile
```

---

## Component Architecture

### Backend Components

```mermaid
graph LR
    subgraph "Flask Application (app.py)"
        Main[Main App]
        Worker[Background Worker Thread]
        Swagger[Swagger UI]
    end
    
    subgraph "Routes (Blueprints)"
        PatientsR[patients.py]
        PrescriptionsR[prescriptions.py]
        TrackingR[tracking.py]
        QueueR[queue.py]
    end
    
    subgraph "Services"
        TSService[thingspeak_service.py<br/>Data Access Layer]
        QService[queue_service.py<br/>Persistent Queue]
    end
    
    subgraph "Validators"
        PatientV[patient_validator.py]
        PrescriptionV[prescription_validator.py]
        TrackingV[tracking_validator.py]
    end
    
    subgraph "Utilities"
        Errors[errors.py<br/>Error Handling]
        Logging[logging_config.py<br/>Structured Logging]
        Status[status_calculator.py<br/>Status Logic]
    end
    
    Main --> PatientsR
    Main --> PrescriptionsR
    Main --> TrackingR
    Main --> QueueR
    Main --> Worker
    Main --> Swagger
    
    PatientsR --> PatientV
    PrescriptionsR --> PrescriptionV
    TrackingR --> TrackingV
    
    PatientV --> TSService
    PrescriptionV --> QService
    TrackingV --> TSService
    
    QService --> TSService
    Worker --> QService
    Worker --> TSService
    
    TSService --> Errors
    TSService --> Logging
    TrackingV --> Status
```

### Frontend Components

```mermaid
graph TB
    subgraph "Templates"
        Role[role_selection.html<br/>Landing Page]
        Nurse[nurse_login.html<br/>Nurse Login]
        Mgmt[management_login.html<br/>Management Login]
        Index[index.html<br/>Main Dashboard]
    end
    
    subgraph "Static Assets"
        CSS[style.css<br/>UI Styling]
        JS[main.js<br/>AJAX & UI Logic]
    end
    
    subgraph "Main Dashboard Tabs"
        Duty[Duty Dashboard<br/>Timeline & Search]
        NurseDash[Nurse Dashboard<br/>Forms & Management]
        MgmtDash[Management Dashboard<br/>Statistics & Charts]
    end
    
    Role --> Nurse
    Role --> Mgmt
    Nurse --> Index
    Mgmt --> Index
    Index --> Duty
    Index --> NurseDash
    Index --> MgmtDash
    
    Index --> CSS
    Index --> JS
    
    JS -->|AJAX Calls| API[Flask REST API]
```

#### Frontend Logic & Patterns

While the system is backend-focused, the frontend implements several key patterns to support the architecture:

1.  **Dual-Mode Interaction**:
    - **Blocking Operations**: For Patient and Tracking updates, the frontend awaits the HTTP response (which may take 15s due to backend rate limiting).
    - **Non-Blocking Operations**: For Prescriptions, the frontend accepts an HTTP 202 immediately and refreshes the list asynchronously after a short delay, relying on the backend queue.

2.  **Client-Side Status Calculation**:
    - The Duty Dashboard (`renderTimelineTable` in `main.js`) replicates the backend's status calculation logic (`isServed`).
    - This allows for real-time visual updates of the timeline without constant round-trips for status computation.
    - **Logic Mirroring**: The frontend validates time windows (e.g., ensuring a medication consumed at 09:15 falls within the 09:00 slot) exactly as the backend `status_calculator.py` does.

3.  **Role-Based Visibility**:
    - Uses `localStorage` ("userRole") to toggle visibility of UI elements (`.nurse-only`, `.management-only`).
    - **Note**: This is a UX feature only; strict security is enforced at the backend API level (if authentication were fully implemented).

4.  **Dashboard Refresh Strategy**:
    - **Management Dashboard**: Uses a timer (`setInterval`) to poll for statistics updates every minute.
    - **Duty Dashboard**: Refreshes on load and upon specific actions (e.g., recording a medication).

---

## Data Flow Diagrams

### Patient Management Flow

```mermaid
sequenceDiagram
    participant Client as Web Browser
    participant Flask as Flask API
    participant Validator as Patient Validator
    participant Service as ThingSpeak Service
    participant TS as ThingSpeak Cloud
    
    Note over Client,TS: Add Patient Flow
    Client->>Flask: POST /api/patients (patient data)
    Flask->>Validator: validate_patient_data()
    Validator->>Validator: Sanitize HTML (XSS prevention)
    Validator->>Validator: Validate fields & formats
    Validator-->>Flask: Validated data
    Flask->>Service: write_to_channel("patient_info", data)
    Service->>Service: Enforce 15s rate limit
    Service->>TS: HTTP POST with API key
    TS-->>Service: entry_id
    Service-->>Flask: entry_id
    Flask-->>Client: 200 OK {entry_id}
    
    Note over Client,TS: Get Patient Flow
    Client->>Flask: GET /api/patient/{id}
    Flask->>Service: get_patient(id)
    Service->>TS: HTTP GET with read key
    TS-->>Service: Raw JSON (field1-8)
    Service->>Service: Map fields to readable names
    Service-->>Flask: Patient object
    Flask-->>Client: 200 OK {patient data}
```

### Prescription Management Flow (Queued)

```mermaid
sequenceDiagram
    participant Client as Web Browser
    participant Flask as Flask API
    participant Validator as Prescription Validator
    participant Queue as Persistent Queue
    participant Worker as Background Worker
    participant Service as ThingSpeak Service
    participant TS as ThingSpeak Cloud
    participant File as prescription_queue.json
    
    Note over Client,File: Add Prescription Flow
    Client->>Flask: POST /api/prescriptions (prescription data)
    Flask->>Validator: validate_prescription_data()
    Validator->>Service: patient_exists(patient_id)
    Service->>TS: Check patient channel
    TS-->>Service: Patient exists: true/false
    Service-->>Validator: Validation result
    Validator->>Validator: Validate all fields
    Validator-->>Flask: Validated data
    Flask->>Queue: add(prescription)
    Queue->>File: Save queue to disk
    File-->>Queue: Saved
    Queue-->>Flask: Success
    Flask-->>Client: 202 Accepted (queued)
    
    Note over Worker,TS: Background Processing
    loop Every 1 second
        Worker->>Queue: get_next()
        Queue-->>Worker: Next item (if available)
        Worker->>Worker: Check 15s rate limit
        Worker->>Service: write_to_channel("medicine_prescription", data)
        Service->>TS: HTTP POST with API key
        TS-->>Service: entry_id (or 0 on failure)
        alt Success (entry_id > 0)
            Service-->>Worker: entry_id
            Worker->>Queue: mark_success(item)
            Queue->>File: Update queue on disk
        else Failure (entry_id == 0)
            Service-->>Worker: 0
            Worker->>Queue: mark_failure(item, error)
            Queue->>Queue: Retry count++
            alt Max retries exceeded (3)
                Queue->>Queue: Move to failed list
            else Can retry
                Queue->>Queue: Requeue with backoff
            end
            Queue->>File: Update queue on disk
        end
    end
```

### Medication Tracking Flow

```mermaid
sequenceDiagram
    participant Client as Web Browser
    participant Flask as Flask API
    participant Validator as Tracking Validator
    participant Service as ThingSpeak Service
    participant StatusCalc as Status Calculator
    participant TS as ThingSpeak Cloud
    
    Note over Client,TS: Record Administration
    Client->>Flask: POST /api/medication-tracking (tracking data)
    Flask->>Validator: validate_tracking_data()
    Validator->>Service: patient_exists(patient_id)
    Service-->>Validator: Patient exists: true/false
    Validator->>Validator: Validate fields & datetime
    Validator-->>Flask: Validated data
    Flask->>Service: write_to_channel("medicine_track", data)
    Service->>Service: Enforce 15s rate limit
    Service->>TS: HTTP POST with API key
    TS-->>Service: entry_id
    Service-->>Flask: entry_id
    Flask-->>Client: 200 OK {entry_id}
    
    Note over Client,TS: Get Tracking Records
    Client->>Flask: GET /api/medication-tracking
    Flask->>Service: read_channel("medicine_track")
    Service->>TS: HTTP GET with read key
    TS-->>Service: Raw JSON (field1-5)
    Service->>Service: Map fields to readable names
    Service->>StatusCalc: calculate_status(consume_date, time_slot)
    StatusCalc->>StatusCalc: Parse time slots
    StatusCalc->>StatusCalc: Check if time falls in slot
    StatusCalc-->>Service: Status ("complete" or "pending")
    Service-->>Flask: Tracking records with status
    Flask-->>Client: 200 OK {tracking data}
```

---

## ThingSpeak Integration

### Channel Configuration

```mermaid
graph TB
    subgraph "ThingSpeak Cloud"
        subgraph "Channel 1: Patient Info (3124887)"
            P1[Field1: Patient_ID]
            P2[Field2: Name]
            P3[Field3: Floor]
            P4[Field4: Room]
            P5[Field5: Bed]
            P6[Field6: Age]
            P7[Field7: Gender]
            P8[Field8: Notes]
        end
        
        subgraph "Channel 2: Prescriptions (3124898)"
            R1[Field1: Patient_ID]
            R2[Field2: Medicine_Name]
            R3[Field3: Dosage]
            R4[Field4: Frequency]
            R5[Field5: Start_Date]
            R6[Field6: End_Date]
            R7[Field7: Time_Slot]
        end
        
        subgraph "Channel 3: Tracking (3131200)"
            T1[Field1: Patient_ID]
            T2[Field2: Medicine_Name]
            T3[Field3: Dosage]
            T4[Field4: Consume_Date]
            T5[Field5: Time_Slot]
        end
    end
    
    subgraph "API Keys (from .env)"
        PW[Patient Write Key]
        PR[Patient Read Key]
        RW[Prescription Write Key]
        RR[Prescription Read Key]
        TW[Tracking Write Key]
        TR[Tracking Read Key]
    end
    
    PW -.->|Write| P1
    PR -.->|Read| P1
    RW -.->|Write| R1
    RR -.->|Read| R1
    TW -.->|Write| T1
    TR -.->|Read| T1
```

### Rate Limit Management

```mermaid
graph LR
    subgraph "ThingSpeak Rate Limits"
        RL[Free Tier: 1 write per 15 seconds per channel]
    end
    
    subgraph "eMAR Implementation"
        PC[Patient Channel<br/>Direct Write<br/>15s enforced]
        RC[Prescription Channel<br/>Queue + Background Worker<br/>15s between writes]
        TC[Tracking Channel<br/>Direct Write<br/>15s enforced]
    end
    
    subgraph "User Experience"
        PUX[Patient: 15s wait<br/>Blocking]
        RUX[Prescription: Instant<br/>HTTP 202 Accepted]
        TUX[Tracking: 15s wait<br/>Blocking]
    end
    
    RL --> PC
    RL --> RC
    RL --> TC
    
    PC --> PUX
    RC --> RUX
    TC --> TUX
```

---

## Queue Management System

### Queue Architecture

```mermaid
graph TB
    subgraph "PersistentQueue Class"
        Q[Queue Items List]
        F[Failed Items List]
        S[Statistics Counter]
        Lock[Thread Lock]
    end
    
    subgraph "Queue Item"
        Data[Prescription Data]
        Attempts[Retry Attempts]
        Error[Last Error Message]
        Timestamp[Added At]
    end
    
    subgraph "Storage"
        JSON[prescription_queue.json]
    end
    
    subgraph "Operations"
        Add[add: Add new item]
        Get[get_next: Get next pending]
        Success[mark_success: Remove on success]
        Failure[mark_failure: Retry or fail]
        Clear[clear_failed: Remove failed items]
    end
    
    Q --> Data
    F --> Data
    Q --> JSON
    F --> JSON
    S --> JSON
    
    Add --> Q
    Get --> Q
    Success --> Q
    Failure --> Q
    Failure --> F
    Clear --> F
```

### Retry Logic Flow

```mermaid
stateDiagram-v2
    [*] --> Queued: add()
    Queued --> Processing: get_next()
    Processing --> Success: mark_success()<br/>(entry_id > 0)
    Processing --> Retry1: mark_failure()<br/>(attempt 1)
    Retry1 --> Processing: Requeue after backoff
    Retry1 --> Retry2: mark_failure()<br/>(attempt 2)
    Retry2 --> Processing: Requeue after backoff
    Retry2 --> Failed: mark_failure()<br/>(attempt 3, max reached)
    Success --> [*]
    Failed --> [*]: clear_failed()
    
    note right of Retry1
        Exponential backoff:
        - Attempt 1: No delay
        - Attempt 2: Delay
        - Attempt 3: Max retries
    end note
    
    note right of Failed
        Failed items tracked
        separately and reported
        in queue status
    end note
```

### Queue Monitoring

```mermaid
graph LR
    subgraph "Queue Status API"
        Status[GET /api/queue/status]
    end
    
    subgraph "Metrics Returned"
        Size[Current Queue Size]
        Failed[Failed Items Count]
        Stats[Statistics:<br/>- Total Added<br/>- Total Processed<br/>- Total Failed<br/>- Total Retried]
        Items[Failed Items Details:<br/>- Data<br/>- Attempts<br/>- Last Error<br/>- Timestamp]
    end
    
    Status --> Size
    Status --> Failed
    Status --> Stats
    Status --> Items
```

---

## Security Architecture

### Input Validation Layer

```mermaid
graph TB
    Input[User Input] --> Validator
    
    subgraph "Validation Process"
        Validator[Validator Module]
        Validator --> Sanitize[HTML Escaping<br/>XSS Prevention]
        Sanitize --> TypeCheck[Type Validation]
        TypeCheck --> FormatCheck[Format Validation<br/>Regex Patterns]
        FormatCheck --> RangeCheck[Range Validation<br/>Length, Age, etc.]
        RangeCheck --> LogicCheck[Business Logic<br/>Patient Exists, Dates, etc.]
    end
    
    LogicCheck --> Valid{Valid?}
    Valid -->|Yes| Clean[Clean Data]
    Valid -->|No| Error[ValidationError<br/>HTTP 400]
    
    Clean --> Service[ThingSpeak Service]
    Error --> Client[Client]
```

### Error Handling Flow

```mermaid
graph TB
    Request[API Request] --> Route[Route Handler]
    
    Route --> TryCatch{Try/Catch}
    
    TryCatch -->|ValidationError| E400[error_response<br/>HTTP 400]
    TryCatch -->|NotFoundError| E404[error_response<br/>HTTP 404]
    TryCatch -->|RateLimitError| E429[error_response<br/>HTTP 429]
    TryCatch -->|ThingSpeakError| E500[error_response<br/>HTTP 500]
    TryCatch -->|QueueFullError| E507[error_response<br/>HTTP 507]
    TryCatch -->|Success| S200[success_response<br/>HTTP 200/202]
    
    E400 --> Logger[Structured Logger]
    E404 --> Logger
    E429 --> Logger
    E500 --> Logger
    E507 --> Logger
    S200 --> Logger
    
    Logger --> Response[JSON Response]
```

---

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        Code[Source Code]
        Env[.env Configuration]
        Python[Python 3.8+]
        Flask[Flask Dev Server<br/>Port 5000]
    end
    
    subgraph "Network"
        Local[localhost:5000]
        LAN[192.168.x.x:5000]
    end
    
    subgraph "Cloud Services"
        TS[ThingSpeak API<br/>thingspeak.com]
    end
    
    Code --> Python
    Env --> Python
    Python --> Flask
    Flask --> Local
    Flask --> LAN
    Flask <-->|HTTPS| TS
```

### Production Considerations

```mermaid
graph TB
    subgraph "Production Setup (Recommended)"
        LB[Load Balancer<br/>HTTPS/SSL]
        WSGI[WSGI Server<br/>Gunicorn/uWSGI]
        App1[eMAR Instance 1]
        App2[eMAR Instance 2]
        Redis[Redis/Queue Service<br/>Shared Queue]
    end
    
    subgraph "Security"
        Auth[Authentication<br/>OAuth/SAML]
        RBAC[Role-Based Access Control]
        Secrets[Secrets Management<br/>Vault/KMS]
    end
    
    subgraph "Monitoring"
        Logs[Centralized Logging<br/>ELK/Splunk]
        Metrics[Metrics & Monitoring<br/>Prometheus/Grafana]
        Alerts[Alerting System]
    end
    
    LB --> WSGI
    WSGI --> App1
    WSGI --> App2
    App1 <--> Redis
    App2 <--> Redis
    
    LB --> Auth
    Auth --> RBAC
    WSGI --> Secrets
    
    App1 --> Logs
    App2 --> Logs
    App1 --> Metrics
    App2 --> Metrics
    Metrics --> Alerts
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | User interface and interactions |
| **Backend** | Flask 3.0.0 (Python) | Web framework and REST API |
| **Data Storage** | ThingSpeak IoT Platform | Cloud-based data persistence |
| **Queue** | In-memory with JSON persistence | Prescription background processing |
| **API Documentation** | OpenAPI 3.0, Swagger UI | Interactive API documentation |
| **Logging** | Python logging module | Structured application logging |
| **Validation** | Custom validators | Input sanitization and validation |
| **Testing** | Python unittest | Unit and integration testing |

---

## Key Design Decisions

### 1. **No Local Database**
- All persistent data stored on ThingSpeak cloud
- Simplifies deployment (no DB setup/maintenance)
- Data accessible from anywhere with internet
- Trade-off: Subject to ThingSpeak rate limits

### 2. **Background Queue for Prescriptions**
- Prescriptions use queue + background worker
- Avoids blocking UI for 15 seconds
- Queue persists to disk (survives restarts)
- Automatic retry mechanism (max 3 attempts)

### 3. **Direct Write for Patients/Tracking**
- Patient and tracking operations write directly
- 15-second wait enforced per channel
- Simpler implementation (no queue complexity)
- Acceptable UX for these operations

### 4. **Blueprint Architecture**
- Routes organized by domain (patients, prescriptions, tracking, queue)
- Clear separation of concerns
- Easy to extend and maintain
- Follows Flask best practices

### 5. **Status Calculation at Read Time**
- Medication status computed dynamically
- Not stored in ThingSpeak (saves a field)
- Always accurate based on current data
- Implemented in utils/status_calculator.py

---

## Performance Considerations

### Rate Limiting Strategy
- **ThingSpeak Limit**: 1 write per 15 seconds per channel
- **Patient Channel**: Direct write, enforced wait
- **Prescription Channel**: Queue system, no user wait
- **Tracking Channel**: Direct write, enforced wait

### Scalability Limits
- **Queue Size**: Max 1000 items (configurable)
- **Data Retrieval**: Last 100 records per channel
- **Concurrent Users**: Limited by Flask dev server (use WSGI in production)
- **Background Worker**: Single thread (one write at a time)

### Optimization Opportunities
- Implement date-range pagination for >100 records
- Use production WSGI server (Gunicorn) for concurrency
- Add caching layer (Redis) for frequently accessed data
- Implement database for local caching/faster queries

---

## Future Architecture Enhancements

1. **Database Integration**
   - Add PostgreSQL/MySQL for local data storage
   - Keep ThingSpeak as backup/cloud sync
   - Improve query performance and enable complex queries

2. **Microservices Architecture**
   - Separate patient, prescription, and tracking services
   - Independent scaling and deployment
   - Service mesh for inter-service communication

3. **Message Queue System**
   - Replace in-memory queue with RabbitMQ/Kafka
   - Better reliability and distributed processing
   - Enable multiple worker instances

4. **API Gateway**
   - Add API gateway (Kong, AWS API Gateway)
   - Rate limiting, authentication, analytics
   - Version management and routing

5. **Real-time Features**
   - WebSocket support for live updates
   - Server-sent events for notifications
   - Real-time dashboard updates

---

*Last Updated: November 15, 2025*
