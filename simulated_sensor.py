from __future__ import annotations
import random

class SimulatedSensor:
    """Simulates a sensor with noise and quantization (e.g., INA226)."""
    def __init__(self, noise_std: float = 0.02, resolution_bits: int = 12):
        self.noise_std = noise_std
        self.resolution = 2**resolution_bits

    def measure_voltage(self, actual: float) -> float:
        noise = random.gauss(0, self.noise_std)
        return round((actual + noise) * self.resolution / 32.0) * 32.0 / self.resolution

    def measure_current(self, actual: float) -> float:
        noise = random.gauss(0, self.noise_std * 0.5)
        return actual + noise
