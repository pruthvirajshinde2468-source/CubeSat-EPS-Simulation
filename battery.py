from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass
class BatteryState:
    soc: float
    voltage: float
    current: float
    temperature: float
    capacity_ah: float
    internal_resistance: float

class BatterySystem:
    def __init__(self, capacity_ah: float = 10.0, nominal_voltage: float = 28.0):
        self.capacity_ah = capacity_ah
        self.nominal_voltage = nominal_voltage
        self.soc = 0.8
        self.temp = 25.0
        self.r_int = 0.05
        self.v_max = 32.0
        self.v_min = 22.0
        self.current_voltage = self.get_ocv(self.soc)

    def get_ocv(self, soc: float) -> float:
        return self.v_min + (self.v_max - self.v_min) * (soc ** 0.5)

    def update(self, net_current_a: float, dt_s: float) -> BatteryState:
        delta_soc = (net_current_a * (dt_s / 3600.0)) / self.capacity_ah
        self.soc = max(0.0, min(1.0, self.soc + delta_soc))
        ocv = self.get_ocv(self.soc)
        self.current_voltage = ocv + (net_current_a * self.r_int)
        power_loss = (net_current_a ** 2) * self.r_int
        self.temp += power_loss * dt_s * 0.0001
        self.temp -= (self.temp - 20.0) * 0.01 * dt_s
        return BatteryState(self.soc, self.current_voltage, net_current_a, self.temp, self.capacity_ah, self.r_int)
