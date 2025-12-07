# Appendix B: Wireless Communication Analysis

This appendix provides a detailed technical analysis of the requirements for transitioning the eMAR system to a wireless infrastructure, specifically supporting mobile medication carts.

## B.1 Wireless Modbus TCP Implementation

Modbus TCP is natively compatible with IP-based wireless networks (Wi-Fi), with physical implementation in industrial settings typically taking two forms. The first and most common approach involves the use of wireless bridges or gateways for legacy integration. In this configuration, wired PLCs connect to an Industrial Wireless Client/Bridge, which handles the Wi-Fi connection transparently. Prominent examples include the ProSoft Technology RLX2 series and Siemens SCALANCE W series, both designed to bridge standard Ethernet protocols like Modbus TCP over 802.11 networks [1, 2].

The second consideration relates to protocol adaptation at the data link layer. While standard Modbus TCP packets are wrapped in 802.11 frames without modification, industrial radios often employ specialized packet aggregation algorithms to optimize performance. Standard consumer Wi-Fi aggregation can sometimes delay small industrial packets due to buffering strategies optimized for bulk data transfer. Industrial-grade bridges address this limitation by implementing optimizations that prioritize small, time-critical frames typical of industrial control protocols [2].

## B.2 Industrial Wi-Fi Standards (Wi-Fi 6 / 802.11ax)

For a future-proof eMAR system, Wi-Fi 6 (IEEE 802.11ax) is recommended over the preceding Wi-Fi 5 (802.11ac) standard. Wi-Fi 6 introduces several technical advancements that directly benefit industrial IoT applications in healthcare environments.

### B.2.1 OFDMA and Determinism
The most significant improvement is Orthogonal Frequency-Division Multiple Access (OFDMA), which fundamentally changes how the wireless medium is shared among devices. Unlike previous standards based on OFDM that served one user at a time per channel, OFDMA allows the access point to communicate with multiple devices simultaneously by subdividing the channel into smaller resource units. This architectural change significantly reduces jitter and makes packet arrival times more predictable, which is critical for industrial protocols that rely on consistent timing [3].

### B.2.2 Power Management (TWT)
Wi-Fi 6 also introduces Target Wake Time (TWT), a power management feature particularly relevant for battery-powered devices such as mobile medication carts. TWT allows devices to negotiate specific times to wake up and communicate with the access point, rather than maintaining continuous radio activity. This scheduled approach can reduce radio power consumption by up to 67% compared to legacy standards, extending battery life for mobile healthcare equipment [3].

### B.2.3 Interference Mitigation (BSS Coloring)
The BSS Coloring feature in Wi-Fi 6 enables devices to distinguish between their own network traffic and interference from neighboring networks operating on the same or adjacent channels. In hospital environments where multiple wireless networks coexist (clinical, guest, administrative, and biomedical), this capability prevents unnecessary transmission delays caused by false collision detection with traffic from adjacent networks [3].

## B.3 Security Architecture

Native Modbus TCP lacks built-in authentication or encryption mechanisms, as the protocol was designed for isolated industrial networks. This limitation makes secure transport layers mandatory for any wireless deployment.

### B.3.1 Network Access Control
The deployment should specify WPA3-Enterprise security, which utilizes Simultaneous Authentication of Equals (SAE) as its key exchange protocol. SAE provides resistance to offline dictionary attacks that could compromise WPA2-protected networks. WPA3 also mandates Protected Management Frames (PMF), which encrypt management traffic to prevent deauthentication attacks [4].

### B.3.2 Transport Layer Security
At the application layer, the Modbus Organization has released the Modbus Security specification. This encapsulates standard Modbus packets within a TLS (Transport Layer Security) tunnel, utilizing port 802 instead of the standard port 502. The TLS wrapper provides mutual authentication between client and server, ensuring that only authorized devices can participate in Modbus communications, while also providing confidentiality through encryption [5].

### B.3.3 Network Segmentation
The eMAR traffic should be isolated on a dedicated VLAN (Virtual Local Area Network) with Quality of Service (QoS) priority configured to ensure that medication administration traffic receives preferential treatment over general network traffic [4].

## B.4 Latency and Roaming

### B.4.1 Timeout Configuration
Wireless communication introduces variable latency (jitter). Standard wired Modbus timeouts (100-500ms) are insufficient for wireless deployments. Best practices recommend increasing the application-layer timeout to between 1000ms and 3000ms:

$$T_{timeout} = 1000\text{ms} \text{ to } 3000\text{ms}$$

In addition to extended timeouts, implementing Application Layer Retries provides resilience against transient failures. A typical configuration would attempt three retries before triggering a fault condition [6].

### B.4.2 Fast Roaming (IEEE 802.11r)
Fast roaming capability is essential for mobile medication carts. The network infrastructure should support IEEE 802.11r (Fast Basic Service Set Transition), which caches security credentials across access points to enable roaming transitions in under 50 milliseconds. This rapid handover prevents Modbus TCP connection drops that would otherwise interrupt medication administration workflows [3].

## B.5 Regulatory and Hardware Considerations

### B.5.1 Healthcare Standards
Wireless deployment must comply with IEC 80001-1 ("Application of risk management for IT-networks incorporating medical devices"). Additionally, compliance with ANSI/IEEE C63.27 is recommended for evaluating wireless coexistence to ensure Wi-Fi transmissions do not interfere with life-critical telemetry systems [7, 8].

### B.5.2 Mobile Hardware
Modern healthcare workstations (e.g., Zebra ET5x, Capsa Healthcare carts) are engineered for this environment. Key features include ruggedized housing resistant to disinfectants and LiFePO4 battery systems that provide stable voltage output to maintain consistent radio performance [9].

## B.6 Deployment Checklist

To ensure a reliable wireless eMAR deployment, the following checklist should be verified during installation:

*   **Frequency Band:** [ ] Enable 5GHz band only (disable 2.4GHz) to avoid interference with Bluetooth medical peripherals.
*   **Signal Quality:**
    *   [ ] RSSI > -65 dBm in all patient rooms and hallways.
    *   [ ] SNR (Signal-to-Noise Ratio) > 25 dB.
*   **Roaming Performance:** [ ] Packet loss < 1 packet during transition between Access Points (walking speed).
*   **Network Capacity:** [ ] Maximum channel utilization < 40% during peak hours.

## B.7 Recommended Configuration Profile

Based on the analysis, the recommended wireless profile for the eMAR carts is:

| Parameter | Recommendation | Rationale |
| :--- | :--- | :--- |
| **Standard** | Wi-Fi 6 (802.11ax) | Deterministic latency (OFDMA), Battery life (TWT). |
| **Security** | WPA3-Enterprise | Prevention of offline dictionary attacks; centralized auth. |
| **Roaming** | 802.11r Enabled | Fast transition (<50ms) to maintain Modbus TCP connections. |
| **IP Scheme** | Static or Reserved DHCP | Modbus TCP requires known, fixed IP addresses. |
| **VLAN** | Dedicated "Medical-IoT" | QoS prioritization over guest/admin traffic. |

> **Note:** See the [System Architecture](../ARCHITECTURE.md) document for the complete network topology diagram including the wireless bridge placement.

## B.8 References

| Ref | Source | Description |
|-----|--------|-------------|
| [1] | ProSoft Technology | Industrial Wireless Solutions - RLX2 Series Product Catalog |
| [2] | Siemens | Industrial Wireless LAN (IWLAN) - SCALANCE W Series Documentation |
| [3] | Wi-Fi Alliance | Wi-Fi 6: High Performance, Low Latency Technical Specification |
| [4] | Wi-Fi Alliance | Wi-Fi Certified WPA3: Security Technical Overview |
| [5] | Modbus Organization | Modbus Security Protocol Specification |
| [6] | Real Time Automation | Modbus TCP/IP Unplugged - Addressing, Binding, and Best Practices |
| [7] | U.S. FDA | Radio Frequency Wireless Technology in Medical Devices - Guidance for Industry |
| [8] | IEC | IEC 80001-1:2010 Application of risk management for IT-networks incorporating medical devices |
| [9] | Zebra Technologies | ET5x Series Enterprise Tablets - Healthcare Solutions Documentation |
