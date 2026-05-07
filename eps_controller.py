from __future__ import annotations
from enum import Enum
from simulated_eps import SimulatedEPS

class SatelliteMode(Enum):
    SAFE = "Safe"; NOMINAL = "Nominal"; SCIENCE = "Science"; COMMS = "Comms"

class EPSController:
    def __init__(self, eps: SimulatedEPS):
        self.eps = eps; self.mode = SatelliteMode.NOMINAL
        self.soc_threshold_safe = 0.20; self.soc_threshold_nominal = 0.40; self.soc_threshold_science = 0.70

    def update_logic(self, battery_soc: float) -> SatelliteMode:
        if battery_soc < self.soc_threshold_safe: self.mode = SatelliteMode.SAFE
        elif self.mode == SatelliteMode.SAFE and battery_soc > self.soc_threshold_nominal: self.mode = SatelliteMode.NOMINAL
        elif self.mode == SatelliteMode.NOMINAL and battery_soc > self.soc_threshold_science: self.mode = SatelliteMode.SCIENCE
        elif self.mode == SatelliteMode.SCIENCE and battery_soc < self.soc_threshold_nominal: self.mode = SatelliteMode.NOMINAL

        if self.mode == SatelliteMode.SAFE:
            self.eps.rails["12V"].enabled = False; self.eps.rails["5V"].enabled = False; self.eps.rails["3.3V"].enabled = True
        elif self.mode == SatelliteMode.NOMINAL:
            self.eps.rails["12V"].enabled = False; self.eps.rails["5V"].enabled = True; self.eps.rails["3.3V"].enabled = True
        else:
            self.eps.rails["12V"].enabled = True; self.eps.rails["5V"].enabled = True; self.eps.rails["3.3V"].enabled = True
        return self.mode

    def handle_faults(self):
        for rail in self.eps.rails.values():
            if rail.fault == "Thermal shutdown" and rail.temperature < 50.0:
                rail.enabled = True; rail.fault = None
