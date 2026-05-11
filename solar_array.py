from __future__ import annotations
import math
from dataclasses import dataclass
from orbit import Vector3

@dataclass
class Panel:
    name: str; normal: Vector3; area_m2: float; efficiency: float = 0.30; temp_coeff: float = -0.004

class SolarArray:
    def __init__(self, cube_size: str = "3U"):
        s1 = 0.1 * 0.3; s2 = 0.1 * 0.1
        self.panels = [
            Panel("X+", Vector3(1,0,0), s1), Panel("X-", Vector3(-1,0,0), s1),
            Panel("Y+", Vector3(0,1,0), s1), Panel("Y-", Vector3(0,-1,0), s1),
            Panel("Z+", Vector3(0,0,1), s2), Panel("Z-", Vector3(0,0,-1), s2),
        ]
        self.solar_constant = 1361.0
        self.mppt_efficiency = 0.95

    def get_power(self, sun_vector: Vector3, ambient_temp: float = 25.0) -> float:
        if sun_vector.magnitude() < 0.1: return 0.0
        total_power = 0.0
        for panel in self.panels:
            cos_theta = panel.normal.dot(sun_vector)
            if cos_theta > 0:
                p_in = self.solar_constant * panel.area_m2 * cos_theta
                panel_temp = ambient_temp + (cos_theta * 40.0)
                temp_factor = 1.0 + panel.temp_coeff * (panel_temp - 25.0)
                total_power += p_in * panel.efficiency * temp_factor
        return total_power * self.mppt_efficiency
