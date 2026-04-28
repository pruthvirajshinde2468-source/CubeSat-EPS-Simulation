# CubeSat EPS Simulation

This project simulates an automated Electrical Ground Support Equipment (EGSE) test for a CubeSat Electrical Power System (EPS).

## Features

- Simulated EPS with 3.3V, 5V, and 12V rails
- Programmable solar array with sunlight, partial shadow, and eclipse phases
- Programmable electronic loads with step, sine, and random current profiles
- INA226-style sensor simulation with noise and 12-bit quantization
- Automated test sequence running a full 120-second orbit simulation
- CSV logging, PNG plots, and a Markdown summary report
- Fault injection support for overcurrent and thermal shutdown

## Files

- `simulated_eps.py` - DUT model for the EPS rails, efficiency curve, and thermal behavior
- `simulated_load.py` - programmable load definitions and profile generator
- `simulated_solar.py` - solar array source with orbit phase support
- `simulated_sensor.py` - sensor modeling with noise and quantization
- `test_automation.py` - main simulation driver and logging
- `report_generator.py` - plot generation and summary report creation
- `requirements.txt` - Python dependencies

## Requirements

Install dependencies in a virtual environment:

```bash
python -m pip install -r requirements.txt
```

## Run the simulation

```bash
python test_automation.py
```

Results are saved in the `results/` folder:

- `eps_test_log.csv` — measurements and state log
- `voltages.png` — voltage plot
- `currents.png` — current plot
- `input_voltage.png` — solar input plot
- `summary_report.md` — test summary report

## Interpreting outputs

- `voltages.png` shows the measured voltage on each output rail and the solar input voltage over time.
- `currents.png` shows the load current on each rail.
- `input_voltage.png` shows the solar array voltage during sunlit, partial shadow, and eclipse phases.
- `summary_report.md` lists faults detected and min/max/average values for each rail.

## Extending the simulation

To adapt this to real hardware, replace `SimulatedEPS`, `ProgrammableLoad`, and `SimulatedSensor` with actual instrument driver classes in `test_automation.py`. The simulation is modular so the main test flow can remain unchanged.
