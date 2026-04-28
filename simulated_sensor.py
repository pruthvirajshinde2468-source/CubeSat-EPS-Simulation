from __future__ import annotations

import math
import random
from typing import Tuple


class SimulatedSensor:
    """Simulated INA226-style measurement sensor with noise and quantization."""

    def __init__(self, voltage_range: Tuple[float, float] = (0.0, 30.0), current_range: Tuple[float, float] = (0.0, 5.0), noise_std: float = 0.02, bits: int = 12) -> None:
        self.voltage_min, self.voltage_max = voltage_range
        self.current_min, self.current_max = current_range
        self.noise_std = noise_std
        self.resolution = 2 ** bits - 1

    def _quantize(self, measured: float, min_value: float, max_value: float) -> float:
        clamped = max(min(measured, max_value), min_value)
        step = (max_value - min_value) / max(self.resolution, 1)
        return round(clamped / step) * step

    def _apply_noise(self, value: float, scale: float) -> float:
        return value + random.gauss(0.0, self.noise_std * scale)

    def measure_voltage(self, voltage: float) -> float:
        noisy = self._apply_noise(voltage, max(abs(voltage), 1.0))
        return self._quantize(noisy, self.voltage_min, self.voltage_max)

    def measure_current(self, current: float) -> float:
        noisy = self._apply_noise(current, max(abs(current), 1.0))
        return self._quantize(noisy, self.current_min, self.current_max)
