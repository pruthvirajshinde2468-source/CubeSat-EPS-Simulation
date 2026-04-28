from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass
class OrbitPhase:
    name: str
    start_time: float
    end_time: float
    voltage: float


class SolarSimulator:
    """Simulated solar array source for an orbiting CubeSat."""

    def __init__(self, phases: Optional[List[OrbitPhase]] = None) -> None:
        if phases is None:
            phases = [
                OrbitPhase("Sunlight", 0.0, 30.0, 28.0),
                OrbitPhase("Partial Shadow", 30.0, 60.0, 14.0),
                OrbitPhase("Eclipse", 60.0, 90.0, 0.0),
                OrbitPhase("Sunlight", 90.0, 120.0, 28.0),
            ]
        self.phases = phases
        self.custom_voltage_fn: Optional[Callable[[float], float]] = None

    def set_voltage_function(self, fn: Callable[[float], float]) -> None:
        self.custom_voltage_fn = fn

    def voltage_at(self, time_s: float) -> Tuple[float, str]:
        if self.custom_voltage_fn is not None:
            return float(self.custom_voltage_fn(time_s)), "Custom"

        for phase in self.phases:
            if phase.start_time <= time_s < phase.end_time:
                return phase.voltage, phase.name

        last_phase = self.phases[-1]
        return last_phase.voltage, last_phase.name

    def set_orbit_phases(self, phases: List[OrbitPhase]) -> None:
        self.phases = phases

    def description(self) -> str:
        return ", ".join([f"{p.name} [{p.start_time}-{p.end_time}s]= {p.voltage}V" for p in self.phases])
