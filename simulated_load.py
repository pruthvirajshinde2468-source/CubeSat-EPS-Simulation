from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class LoadProfile:
    profile_type: str
    baseline_current: float
    amplitude: float
    frequency: float = 0.05
    step_time: float = 30.0
    random_seed: Optional[int] = None
    partial_shadow: float = 1.0
    custom_function: Optional[Callable[[float], float]] = None

    def current_at(self, time_s: float) -> float:
        if self.profile_type == "step":
            return self._step_current(time_s)
        if self.profile_type == "sine":
            return self._sine_current(time_s)
        if self.profile_type == "random":
            return self._random_current(time_s)
        if self.profile_type == "custom" and self.custom_function is not None:
            return max(0.0, self.custom_function(time_s))
        return max(0.0, self.baseline_current)

    def _step_current(self, time_s: float) -> float:
        return self.baseline_current + self.amplitude if time_s >= self.step_time else self.baseline_current

    def _sine_current(self, time_s: float) -> float:
        return max(0.0, self.baseline_current + self.amplitude * math.sin(2 * math.pi * self.frequency * time_s))

    def _random_current(self, time_s: float) -> float:
        if self.random_seed is not None:
            random.seed(int(time_s) + self.random_seed)
        noise = random.uniform(-self.amplitude, self.amplitude)
        return max(0.0, self.baseline_current + noise)


class ProgrammableLoad:
    """A simulated electronic load that follows a time-dependent current profile."""

    def __init__(self, name: str, profile: LoadProfile) -> None:
        self.name = name
        self.profile = profile
        self.last_current = 0.0

    def update(self, time_s: float) -> float:
        self.last_current = self.profile.current_at(time_s)
        return self.last_current

    @classmethod
    def step_profile(cls, name: str, baseline: float, step: float, step_time: float) -> ProgrammableLoad:
        return cls(name, LoadProfile(profile_type="step", baseline_current=baseline, amplitude=step, step_time=step_time))

    @classmethod
    def sine_profile(cls, name: str, baseline: float, amplitude: float, frequency: float) -> ProgrammableLoad:
        return cls(name, LoadProfile(profile_type="sine", baseline_current=baseline, amplitude=amplitude, frequency=frequency))

    @classmethod
    def random_profile(cls, name: str, baseline: float, noise_amplitude: float, seed: int) -> ProgrammableLoad:
        return cls(name, LoadProfile(profile_type="random", baseline_current=baseline, amplitude=noise_amplitude, random_seed=seed))

    @classmethod
    def custom_profile(cls, name: str, func: Callable[[float], float]) -> ProgrammableLoad:
        return cls(name, LoadProfile(profile_type="custom", baseline_current=0.0, amplitude=0.0, custom_function=func))
