from __future__ import annotations
import os
import pandas as pd
from simulated_eps import SimulatedEPS
from simulated_load import ProgrammableLoad
from simulated_sensor import SimulatedSensor
from battery import BatterySystem
from orbit import OrbitPropagator
from solar_array import SolarArray
from eps_controller import EPSController
from report_generator import generate_plots, generate_report

def run_test_sequence(duration_s: float = 6000.0, dt: float = 10.0):
    os.makedirs("results", exist_ok=True)
    eps = SimulatedEPS(); controller = EPSController(eps)
    battery = BatterySystem(capacity_ah=5.0, nominal_voltage=28.0)
    orbit = OrbitPropagator(altitude_km=550.0, inclination_deg=97.0)
    solar = SolarArray(); sensor = SimulatedSensor()
    loads = [
        ProgrammableLoad.step_profile("3.3V", 0.4, 0.2, 50.0),
        ProgrammableLoad.sine_profile("5V", 0.6, 0.4, 0.01),
        ProgrammableLoad.random_profile("12V", 0.5, 0.3, 42)
    ]
    records = []; faults = []
    print(f"Starting High-Fidelity Orbit Simulation ({duration_s}s)...")
    current_time = 0.0
    while current_time <= duration_s:
        sun_vec, in_eclipse = orbit.get_state(current_time)
        solar_power_w = solar.get_power(sun_vec)
        load_currents = {load.name: load.update(current_time) for load in loads}
        mode = controller.update_logic(battery.soc); controller.handle_faults()
        eps.update(battery.current_voltage, load_currents, dt)
        load_p_w = sum(eps.rails[n].output_voltage * eps.rails[n].output_current for n in eps.rails) / 0.85
        net_p_w = solar_power_w - load_p_w
        bat_state = battery.update(net_p_w / max(battery.current_voltage, 10.0), dt)
        if eps.fault_history:
            for f in eps.fault_history:
                if f not in faults: faults.append(f"T={current_time:.1f}s: {f}")
        records.append({
            "time_s": current_time, "mode": mode.value, "in_eclipse": 1 if in_eclipse else 0,
            "solar_power_w": sensor.measure_current(solar_power_w), "battery_voltage": sensor.measure_voltage(bat_state.voltage),
            "battery_soc": bat_state.soc, "battery_current": sensor.measure_current(bat_state.current),
            "net_power_w": net_p_w, "3.3V_voltage": sensor.measure_voltage(eps.rails["3.3V"].output_voltage),
            "5V_voltage": sensor.measure_voltage(eps.rails["5V"].output_voltage), "12V_voltage": sensor.measure_voltage(eps.rails["12V"].output_voltage)
        })
        if int(current_time) % 1000 == 0:
            print(f"T={current_time:5.0f}s | Mode={mode.value:8} | SoC={bat_state.soc*100:4.1f}% | Solar={solar_power_w:5.1f}W")
        current_time += dt
    df = pd.DataFrame(records); df.to_csv("results/eps_test_log.csv", index=False)
    generate_plots(df, "results"); generate_report(df, faults, "results")
    print("\nSimulation completed. Results in 'results/'")

if __name__ == "__main__": run_test_sequence()
