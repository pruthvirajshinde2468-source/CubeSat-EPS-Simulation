from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class LoadProfile:
    profile_type: str
    baseline_current: float
    amplitude: float
    frequency: float = 0.05
    step_time: float = 30.0
    random_seed: Optional[int] = None

    def current_at(self, time_s: float) -> float:
        if self.profile_type == "step":
            return self.baseline_current + self.amplitude if time_s >= self.step_time else self.baseline_current
        if self.profile_type == "sine":
            return max(0.0, self.baseline_current + self.amplitude * math.sin(2 * math.pi * self.frequency * time_s))
        if self.profile_type == "random":
            if self.random_seed is not None: random.seed(int(time_s) + self.random_seed)
            return max(0.0, self.baseline_current + random.uniform(-self.amplitude, self.amplitude))
        return max(0.0, self.baseline_current)

class ProgrammableLoad:
    def __init__(self, name: str, profile: LoadProfile) -> None:
        self.name = name
        self.profile = profile

    def update(self, time_s: float) -> float:
        return self.profile.current_at(time_s)

    @classmethod
    def step_profile(cls, name: str, baseline: float, step: float, step_time: float) -> ProgrammableLoad:
        return cls(name, LoadProfile("step", baseline, step, step_time=step_time))

    @classmethod
    def sine_profile(cls, name: str, baseline: float, amplitude: float, frequency: float) -> ProgrammableLoad:
        return cls(name, LoadProfile("sine", baseline, amplitude, frequency=frequency))

    @classmethod
    def random_profile(cls, name: str, baseline: float, noise: float, seed: int) -> ProgrammableLoad:
        return cls(name, LoadProfile("random", baseline, noise, random_seed=seed))
