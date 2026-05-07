# High-Fidelity CubeSat EPS Simulation

This project is an advanced, physics-based simulator for a CubeSat Electrical Power System (EPS). It evolves from a simple voltage-source model to a comprehensive energy-balance simulation that accounts for orbital mechanics, solar geometry, battery chemistry, and autonomous power management.

## Key Features

- **Lithium-Ion Battery Model**: Detailed simulation of State of Charge (SoC), Open Circuit Voltage (OCV) curves, internal resistance, and thermal effects.
- **Orbital Mechanics**: Real-time calculation of the satellite's position, Sun vector, and Earth eclipse (umbra) states based on altitude and inclination.
- **6-Face Solar Array**: Models a 3U CubeSat with independent panels on all faces, utilizing the cosine law for incident power and temperature-dependent efficiency drops.
- **Autonomous EPS Controller**: A "Mission Brain" that manages power modes (Safe, Nominal, Science) and performs automatic load shedding when battery levels are critical.
- **Modular Load Profiles**: Simulates various subsystem behaviors using step, sine, and random current patterns.
- **Realistic Sensing**: INA226-style sensor simulation with Gaussian noise and 12-bit quantization.
- **Comprehensive Reporting**: Generates CSV logs and high-quality plots for Voltages, Battery SoC, and Power Balance.

## Project Structure

- `battery.py`: Lithium-Ion battery pack physics.
- `orbit.py`: Orbital propagator and Sun vector geometry.
- `solar_array.py`: Multi-face solar panel power generation.
- `eps_controller.py`: Power mode logic and fault recovery.
- `simulated_eps.py`: Regulated rails (3.3V, 5V, 12V) and DUT thermal behavior.
- `simulated_load.py`: Subsystem current demand profiles.
- `simulated_sensor.py`: Measurement noise and quantization.
- `test_automation.py`: Main simulation driver and orchestration.
- `report_generator.py`: Visualization and Markdown report creation.

## Requirements

Install the necessary Python packages:

```bash
pip install pandas matplotlib
```

## Running the Simulation

Execute the main driver script:

```bash
python test_automation.py
```

By default, the script simulates one full orbit (approx. 100 minutes) with 10-second resolution.

## Interpreting Results

Results are saved in the `results/` folder:

- `battery_soc.png`: Shows the charge/discharge cycle across the orbit.
- `power_balance.png`: Visualizes Solar Generation vs. Load Consumption.
- `voltages.png`: Tracks the stability of regulated rails and the main battery bus.
- `summary_report.md`: Provides a mission overview, final SoC, and any fault logs.

## Simulation Physics

- **Solar Constant**: 1361 W/m² (AMO)
- **Cell Efficiency**: 30% (Triple-junction GaAs equivalent)
- **Temp Coefficient**: -0.4% / °C
- **Battery**: 5.0 Ah Li-Ion pack with CC/CV capability.
- **Orbit**: 550 km Sun-Synchronous (approx. 95 min period).
