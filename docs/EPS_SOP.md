# CubeSat Electrical Power System (EPS) Standard Operating Procedure (SOP)

**Document ID:** CS-EPS-SOP-001  
**Version:** 1.0  
**Status:** Formal Mission Document  
**Date:** 2026-05-11  

---

## 1. Document Control

| Role | Name | Date |
| :--- | :--- | :--- |
| **Prepared By** | Mission Engineering Team | 2026-05-11 |
| **Reviewed By** | EPS Lead Engineer | 2026-05-11 |
| **Approved By** | Flight Director | 2026-05-11 |

---

## 2. Introduction
This document defines the standard operating procedures for the CubeSat Electrical Power System (EPS). It covers startup, health monitoring, nominal operations, and emergency response. All operators must adhere strictly to these steps to ensure mission longevity.

---

## 3. Satellite Startup Procedure (Initialization)

**Objective:** Safely transition the satellite from cold-launch state to Nominal Operations.

| Step | Action | Conditions | Expected Output | Verification |
| :--- | :--- | :--- | :--- | :--- |
| 1.1 | **BATT_ACTIVATE** | Deployment switches closed | Battery voltage > 10.0V | EPS Telemetry "Input_Voltage" active |
| 1.2 | **INITIAL_BOOT** | Solar panels exposed | Input Voltage stabilizing | `simulated_eps.input_voltage` > 10.0V |
| 1.3 | **RAIL_3V3_ENABLE** | Startup delay +30s | 3.3V rail voltage ~3.3V | Rail Status: "3.3V": OK |
| 1.4 | **MODE_TRANSITION** | SoC > 20% | Mode: **SAFE** | `eps_controller.mode` == "Safe" |
| 1.5 | **RAIL_5V_ENABLE** | SoC > 40% | 5.0V rail voltage ~5.0V | Rail Status: "5V": OK |
| 1.6 | **NOMINAL_ENTRY** | All vital rails active | Mode: **NOMINAL** | `eps_controller.mode` == "Nominal" |

---

## 4. Power System Health Check Procedure

**Objective:** Periodic verification of EPS integrity and component health.

| Step | Action | Parameter | Nominal Range | Verification Tool |
| :--- | :--- | :--- | :--- | :--- |
| 2.1 | **VOLTAGE_VERIFY** | Bus Voltage | 10.0V - 14.4V | `get_status()["input_voltage"]` |
| 2.2 | **RAIL_TELEMETRY** | 3.3V / 5V / 12V | ±5% Nominal | `get_status()["rails"]` |
| 2.3 | **THERMAL_AUDIT** | Rail Temperature | < 60°C | `rail.temperature` |
| 2.4 | **LOAD_ANALYSIS** | Total Current | < 5.0A (Aggregate) | `sum(rail.output_current)` |
| 2.5 | **SOC_VALUATION** | State of Charge | 40% - 95% | `battery.soc` |

---

## 5. Data Downlink Procedure (COMMS Mode)

**Objective:** Manage power resources during high-drain communication windows.

| Step | Action | Conditions | Expected Output | Verification |
| :--- | :--- | :--- | :--- | :--- |
| 3.1 | **PRE_DOWNLINK_CHECK** | Ground station in view | SoC > 50% | Proceed to Step 3.2 |
| 3.2 | **PAYLOAD_SHED** | Preparing for Comms | Non-essential rails OFF | 12V Rail: Disabled |
| 3.3 | **COMMS_ACTIVE** | Mode: **COMMS** | Radio Power > 5.0W | High 5V current draw observed |
| 3.4 | **REALTIME_MONITOR** | During downlink | SoC > 25% | No "Undervoltage" faults |
| 3.5 | **POST_COMMS_REST** | Downlink complete | Return to NOMINAL | Mode: **NOMINAL** |

---

## 6. Anomaly Response Procedure (ARP)

**Objective:** Mitigate system damage during hardware or environmental faults.

### 6.1 Anomaly: Thermal Shutdown
*   **Condition:** Rail Temperature > 80.0°C.
*   **System Action:** EPS Controller disables the affected rail.
*   **Procedure:**
    1.  Identify affected rail via `fault_history`.
    2.  Disable all non-essential loads.
    3.  Wait for temperature to drop below 50.0°C.
    4.  **Verification:** Check `rail.fault == None`.

### 6.2 Anomaly: Overcurrent Fault
*   **Condition:** `requested_current` > `max_current`.
*   **Procedure:**
    1.  Immediately switch to **SAFE** mode.
    2.  Check `simulated_load.py` for component failure simulation.
    3.  Sequentially re-enable rails to isolate the short circuit.

### 6.3 Anomaly: Critical Low Power
*   **Condition:** SoC < 20%.
*   **Procedure:**
    1.  **SAFE_MODE_FORCED**: System automatically cuts 5V and 12V rails.
    2.  Orient solar panels to Max Power Point (MPP).
    3.  Disable all beaconing except "Distress Signal".
    4.  **Recovery:** SoC must reach 40% before NOMINAL transition.

---

## 7. Approval and Sign-off

*This document is property of the Mission EPS Group. Unauthorized distribution is prohibited.*

**Controlled by:** CubeSat Control Center (CCC)
