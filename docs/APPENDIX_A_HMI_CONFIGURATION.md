# Appendix A: HMI Configuration Guide (NB Designer)

This appendix provides a step-by-step configuration guide for the Omron NB-series HMI using NB Designer software.

## Communication Setting

| Device | IP Address | Port No. | Protocol | Master/Slave | Station No. |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HMI0 | 192.168.250.4 | 10502 | Modbus TCP | Master | |
| PLC0 | 192.168.250.2 | 10502 | Modbus TCP | Slave | 1 |

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/ce8ac7abc0f98532b6555a4570bd4d48448421bc92a79f03fc71c6e9de12236b.jpg)

## Screen 0: Main Menu

The main menu allows navigation to the Patient ID entry screen and the Medication display screen.

**Function Keys:**
- **FK0 (Set Patient ID):** Navigates to Screen 10.
- **FK1 (See Medication):** Navigates to Screen 11.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/0e89220e81f390a0b40798cd2091dc0a8d7578f942cea1cc4d62b3ed5bff889a.jpg)
*Figure A.1: Main Menu Screen Design*

## Screen 10: Set Patient ID

This screen allows the user to input the Patient ID.

**Components:**
- **Text Input:** Mapped to Holding Registers 0-9 (Word Length: 10).
- **Function Key (<):** Returns to the Main Menu.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/20fd7e9a8d9977041cdf3d19076c0a5f7b70c35fdc9223b0da5d8e7d0058cc58.jpg)
*Figure A.2: Patient ID Entry Screen*

### Component Configuration Details

**Text Input Settings:**
- Word Length: 10 (20 characters)
- Address Type: Holding Registers

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/31e8152783bb044eafc66c0ac9b4ae775744226388d8efb92a4a090d737199c7.jpg)

## Screen 11: Medication Display

This screen displays the list of medications for the identified patient and scheduled time.

**Components:**
- **Notebook:** Displays text lines (8 lines x 20 chars). Mapped to Holding Registers starting at address 30.
- **Bit Switch (Served):** Mapped to Coil 1. Used to confirm administration.
- **Function Key (<):** Returns to the Main Menu.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/b0393dae0fe70aa3d1a05ce18126463b5da610e937ccc6e1c04a23063e80f9a3.jpg)
*Figure A.3: Medication List Screen*

### Component Configuration Details

**Notebook Settings:**
- Start Address: 30
- Words per line: 10
- Number of lines: 8

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/36bb926a80d18229ee68362f6efb22dbf7b9b00b00ae76135d9cea86a59f4354.jpg)

**Bit Switch Settings:**
- Address: Coil 1
- Function: Toggle or Momentary (handled by logic)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-01/07348aac-b865-4ac6-bd69-cd06bbc512bb/aa3985fdb83b9618b6bbf0c27a0082e1e7d9fcfdf7a35e5a67d2177de1366825.jpg)
