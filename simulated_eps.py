from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import abc


class BaseEPS(abc.ABC):
    """Abstract interface for an electrical power system."""

    @abc.abstractmethod
    def update(self, input_voltage: float, load_currents: Dict[str, float], dt: float) -> Dict[str, float]:
        raise NotImplementedError


@dataclass
class RailConfig:
    name: str
    nominal_voltage: float
    max_current: float
    temperature: float = 25.0
    enabled: bool = True
    fault: Optional[str] = None
    output_voltage: float = 0.0
    output_current: float = 0.0
    efficiency: float = 1.0


class SimulatedEPS(BaseEPS):
    """Simulated CubeSat EPS with three regulated output rails."""

    def __init__(self, ambient_temp: float = 25.0) -> None:
        self.ambient_temp = ambient_temp
        self.input_voltage = 0.0
        self.thermal_shutdown_threshold = 80.0
        self.undervoltage_threshold = 10.0
        self.fault_history: List[str] = []
        self.rails: Dict[str, RailConfig] = {
            "3.3V": RailConfig(name="3.3V", nominal_voltage=3.3, max_current=2.0),
            "5V": RailConfig(name="5V", nominal_voltage=5.0, max_current=3.0),
            "12V": RailConfig(name="12V", nominal_voltage=12.0, max_current=1.5),
        }
        self.fault_injection: Dict[str, Dict[str, float]] = {}
        self.survivable_thermal_rise = 30.0

    def _efficiency_curve(self, rail: RailConfig, load_current: float) -> float:
        load_fraction = min(max(load_current / max(rail.max_current, 1e-6), 0.0), 1.0)
        efficiency = 0.80 + 0.18 * math.atan(load_fraction * 4.0) / (math.pi / 2)
        return min(max(efficiency, 0.70), 0.98)

    def _voltage_from_load(self, rail: RailConfig, load_current: float) -> float:
        if load_current <= 0:
            return rail.nominal_voltage

        drop = 0.08 * rail.nominal_voltage * (load_current / rail.max_current)
        transient_drop = 0.05 * rail.nominal_voltage * (load_current / rail.max_current) ** 2
        voltage = rail.nominal_voltage - drop - transient_drop
        return max(voltage, rail.nominal_voltage * 0.80)

    def _update_temperature(self, rail: RailConfig, dt: float) -> None:
        power_loss = (rail.nominal_voltage - rail.output_voltage) * rail.output_current
        rise = 4.0 * (power_loss / max(rail.nominal_voltage * rail.max_current, 1e-6))
        cooling = 0.50 * (rail.temperature - self.ambient_temp)
        rail.temperature += (rise - cooling) * dt
        rail.temperature = min(max(rail.temperature, self.ambient_temp), 120.0)

    def update(self, input_voltage: float, load_currents: Dict[str, float], dt: float) -> Dict[str, float]:
        self.input_voltage = input_voltage
        results: Dict[str, float] = {}
        self.fault_history.clear()

        if input_voltage < self.undervoltage_threshold:
            for rail in self.rails.values():
                rail.fault = "Input undervoltage"
                rail.output_voltage = 0.0
                rail.output_current = 0.0
                rail.efficiency = 0.0
                results[rail.name] = 0.0
            self.fault_history.append("Input undervoltage")
            return results

        for name, rail in self.rails.items():
            requested_current = max(load_currents.get(name, 0.0), 0.0)
            requested_current += self.fault_injection.get(name, {}).get("extra_current", 0.0)

            rail.fault = None
            rail.output_current = requested_current
            rail.efficiency = self._efficiency_curve(rail, requested_current)
            rail.output_voltage = self._voltage_from_load(rail, requested_current)

            if requested_current > rail.max_current:
                rail.fault = "Overcurrent"
                rail.output_current = rail.max_current
                rail.output_voltage *= 0.90
                self.fault_history.append(f"{name} overcurrent")

            if requested_current > 0 and rail.temperature > self.thermal_shutdown_threshold:
                rail.fault = "Thermal shutdown"
                rail.enabled = False
                rail.output_voltage = 0.0
                rail.output_current = 0.0
                self.fault_history.append(f"{name} thermal shutdown")

            if rail.temperature > self.thermal_shutdown_threshold and rail.fault is None:
                rail.fault = "Thermal shutdown"
                rail.enabled = False
                rail.output_voltage = 0.0
                rail.output_current = 0.0
                self.fault_history.append(f"{name} thermal shutdown")

            if rail.fault is None and not rail.enabled:
                rail.output_voltage = 0.0
                rail.output_current = 0.0

            self._update_temperature(rail, dt)
            results[name] = rail.output_voltage

        return results

    def inject_overcurrent(self, rail_name: str, extra_current: float) -> None:
        self.fault_injection.setdefault(rail_name, {})["extra_current"] = extra_current

    def inject_thermal_shutdown(self, rail_name: str) -> None:
        rail = self.rails.get(rail_name)
        if rail is not None:
            rail.temperature = self.thermal_shutdown_threshold + 5.0

    def clear_faults(self) -> None:
        self.fault_injection.clear()
        for rail in self.rails.values():
            rail.fault = None
            rail.enabled = True

    def get_status(self) -> Dict[str, Dict[str, float]]:
        return {
            name: {
                "voltage": rail.output_voltage,
                "current": rail.output_current,
                "temperature": rail.temperature,
                "fault": rail.fault or "OK",
                "efficiency": rail.efficiency,
            }
            for name, rail in self.rails.items()
        }
