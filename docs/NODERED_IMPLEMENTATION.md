# Node-RED Implementation (eMAR)

This document summarizes the Node-RED flows stored in `nodered/` and how they bridge the cloud prescription data in ThingSpeak with the on-prem HMI/PLC over Modbus.

## Artifacts
- `nodered/eMar - modbus.json` — Modbus TCP server + protocol adapters to the HMI/PLC.
- `nodered/eMAR- frontend.json` — business logic, ThingSpeak IO, dashboard, and formatting for the HMI notebook.
- `nodered/REPORT.md` — detailed flow-by-flow report (source for this summary).

## Architecture Overview
- **Modbus layer** (tab: "Modbus"): exposes a Modbus TCP server (`192.168.250.2:10502`) that reads patient IDs and serves notebook/button registers for the HMI.
- **Logic/UI layer** (tab: "Frontend"): fetches prescriptions from ThingSpeak, filters by patient/date/time, formats the notebook payload, logs administrations, and provides a dashboard for manual testing on the IRIV PiControl (CM5 Core).
- **Link nodes** decouple layers:
  - `Set Patient ID (Modbus backend)` → `link in 3` (passes decoded patient ID).
  - `Write MedicationList to Notebook` → `link in 4` (register array for notebook display).
  - `Send served status` → `link in 7` (button press event to trigger logging/clearing/reset).

## Modbus Mapping (HMI/PLC)
- **Patient ID read**: Holding registers `0-9` (FC3), polled every 1s; registers are decoded as ASCII (2 chars/register), trimming empties.
- **Notebook write**: Holding registers starting at address `30`, length `80` (FC16). Lines are padded to 20 chars; up to 8 lines are sent (10 registers/line).
- **Served button**: Coil address `1` — read (FC3) for button state; write (FC5) with `0` to reset after handling.

## ThingSpeak Integration
- **Read prescriptions**: `https://api.thingspeak.com/channels/3124898/feeds.json` (read key in flow URL). Filters by `patient_id`, and ensures `currentDate` is within `start_date`/`end_date`.
- **Log administrations**: `https://api.thingspeak.com/update` with API key `LOFTBPN6E2O124FE`; fields include patient ID, medicine, dosage, timestamp (+8h offset), and time slot.
- **Retry policy**: both read/write HTTP requests retry up to 5 times with delay/backoff via dedicated retry function nodes.

## Scheduling & Display Logic
- **Medication rounds**: cron injects at `09:00`, `13:00`, `17:00`, `21:00`; dashboard buttons can trigger the same logic manually.
- **Filtering**: uses `flow.currentPatientMeds` (set after a successful ThingSpeak fetch) and `flow.currentTime` (from schedule or manual override) to match slots (`hh:mm`, comma-separated allowed). Matches exact minutes.
- **Formatting**: medicines are combined as `<medicine> - <dosage>`, padded to 8×20 characters, then converted to 16-bit register values for the notebook.
- **Clearing**: when a dose is served, an all-spaces payload is sent to the notebook registers to clear the screen.

## Served Workflow
1. Modbus coil `1` goes high → frontend receives via `link in 7`.
2. `servingMedList` is read from context; each record triggers a ThingSpeak `update` call (rate-limited delay node).
3. After success: clear `servingMedList`, reset coil `1` to `0`, and clear the notebook registers.

## Dashboard (Testing)
- Tab: **IRIV PiControl (CM5 Core) Dashboard** (`/ui`).
- Widgets:
  - Manual `currentDate` and `currentTime` text inputs to override the filters.
  - "Get full patient medication list" button (fetch prescriptions immediately).
  - "Get medication for medication round" button (run time-slot filter immediately).
- Useful for dry-runs without the PLC/HMI connected.

## Setup
1. Install Node-RED and import both flow JSON files.
2. Ensure modules are available (per flow `global-config`):
   - `node-red-dashboard@3.6.6`
   - `node-red-contrib-modbus@5.44.1`
3. Configure endpoints as needed:
   - Modbus host/port (`192.168.250.2:10502`) to match the HMI/PLC network.
   - ThingSpeak read URL/API key and write API key (replace the hard-coded keys if rotating credentials).
4. Deploy flows and open the dashboard at `/ui` for checks.
5. Confirm PLC register mapping matches the NB Designer notebook configuration (address 30+, 10 words/line, 8 lines).

## Operational Checklist
- HMI writes the patient ID into holding registers 0-9 (ASCII, 2 chars/register).
- After any patient-ID change, the frontend flow fetches prescriptions and stores them in `flow.currentPatientMeds`.
- The scheduled or manual trigger filters by time slot and pushes the notebook payload over link `Write MedicationList to Notebook`.
- A served button press logs to ThingSpeak, clears the notebook, and resets the coil.

## Troubleshooting & Notes
- Debug nodes remain enabled in both tabs for quick inspection; use the sidebar to verify payloads.
- If no meds appear: check `flow.patientID`, `currentDate`/`currentTime` overrides, and confirm ThingSpeak feed includes required fields (1–7).
- If the notebook shows garbled text: verify NB Designer expects little-endian word order and 20-char lines; adjust padding/addresses if your HMI differs.
- Retries stop after 5 attempts; persistent failures leave the last payload in `flow.currentSendingData` for inspection.

For a detailed step-by-step narrative of each node, see `nodered/REPORT.md`.
