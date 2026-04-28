from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from report_generator import generate_plots, generate_report
from simulated_eps import SimulatedEPS
from simulated_load import ProgrammableLoad
from simulated_sensor import SimulatedSensor
from simulated_solar import OrbitPhase, SolarSimulator


OUTPUT_FOLDER = "results"
LOG_FILE = "results/eps_test_log.csv"


def build_solar_simulator() -> SolarSimulator:
    phases = [
        OrbitPhase("Sunlight", 0.0, 25.0, 28.0),
        OrbitPhase("Partial Shadow", 25.0, 50.0, 18.0),
        OrbitPhase("Eclipse", 50.0, 80.0, 0.0),
        OrbitPhase("Sunlight", 80.0, 120.0, 28.0),
    ]
    return SolarSimulator(phases=phases)


def build_loads() -> List[ProgrammableLoad]:
    return [
        ProgrammableLoad.step_profile("3.3V", baseline=0.4, step=1.0, step_time=20.0),
        ProgrammableLoad.sine_profile("5V", baseline=0.8, amplitude=0.6, frequency=0.03),
        ProgrammableLoad.random_profile("12V", baseline=0.6, noise_amplitude=0.6, seed=42),
    ]


def estimate_input_current(input_voltage: float, rails: Dict[str, Dict[str, float]]) -> float:
    total_power = sum(data["voltage"] * data["current"] for data in rails.values())
    if input_voltage <= 0.0:
        return 0.0
    return total_power / max(input_voltage * 0.85, 1e-6)


def run_test_sequence(duration_s: float = 120.0, dt: float = 0.5) -> pd.DataFrame:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    eps = SimulatedEPS()
    solar = build_solar_simulator()
    loads = build_loads()
    sensor = SimulatedSensor()

    records: List[Dict[str, float]] = []
    faults: List[str] = []
    next_fault_injection = {40.0: ("5V", 1.0), 70.0: ("12V", 0.8)}

    current_time = 0.0
    while current_time <= duration_s:
        input_voltage, phase_name = solar.voltage_at(current_time)
        load_currents = {load.name: load.update(current_time) for load in loads}

        injection_key = next(
            (key for key in next_fault_injection if abs(current_time - key) < 1e-6),
            None,
        )
        if injection_key is not None:
            rail_name, extra = next_fault_injection[injection_key]
            eps.inject_overcurrent(rail_name, extra)
            print(f"[Fault injection] {rail_name} extra {extra:.2f} A at {current_time:.1f}s")

        output_voltages = eps.update(input_voltage, load_currents, dt)
        if eps.fault_history:
            for fault in eps.fault_history:
                if fault not in faults:
                    faults.append(fault)

        measured_input_voltage = sensor.measure_voltage(input_voltage)
        estimated_input_current = estimate_input_current(input_voltage, eps.get_status())
        measured_input_current = sensor.measure_current(estimated_input_current)

        row = {
            "time_s": current_time,
            "orbit_phase": phase_name,
            "solar_voltage": measured_input_voltage,
            "input_voltage": measured_input_voltage,
            "input_current": measured_input_current,
        }

        for rail_name, status in eps.get_status().items():
            row[f"{rail_name}_voltage"] = sensor.measure_voltage(status["voltage"])
            row[f"{rail_name}_current"] = sensor.measure_current(status["current"])
            row[f"{rail_name}_temperature"] = status["temperature"]
            row[f"{rail_name}_fault"] = 1 if status["fault"] != "OK" else 0

        records.append(row)

        if int(current_time * 10) % int(1.0 * 10) == 0:
            status_line = (
                f"{current_time:6.1f}s | Phase={phase_name:13} | "
                f"In={measured_input_voltage:5.2f}V {measured_input_current:4.2f}A | "
                f"3.3V={row['3.3V_voltage']:4.2f}V {row['3.3V_current']:4.2f}A | "
                f"5V={row['5V_voltage']:4.2f}V {row['5V_current']:4.2f}A | "
                f"12V={row['12V_voltage']:5.2f}V {row['12V_current']:4.2f}A"
            )
            if eps.fault_history:
                status_line += f" | Faults={', '.join(eps.fault_history)}"
            print(status_line)

        current_time += dt

    df = pd.DataFrame(records)
    df.to_csv(LOG_FILE, index=False)

    plot_files = generate_plots(df, OUTPUT_FOLDER)
    report_path = generate_report(df, faults, OUTPUT_FOLDER)

    print(f"\nTest completed. Log saved to: {LOG_FILE}")
    print(f"Plots saved to: {', '.join(plot_files.values())}")
    print(f"Summary report saved to: {report_path}")

    return df


if __name__ == "__main__":
    start_time = datetime.now()
    print("Starting CubeSat EPS Simulation Test...")
    print(f"Start time: {start_time:%Y-%m-%d %H:%M:%S}")
    run_test_sequence(duration_s=120.0, dt=0.5)
    end_time = datetime.now()
    print(f"End time: {end_time:%Y-%m-%d %H:%M:%S}")
    print(f"Total elapsed: {end_time - start_time}")
