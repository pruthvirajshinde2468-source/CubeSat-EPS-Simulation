from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass
class Vector3:
    x: float; y: float; z: float
    def dot(self, other: Vector3) -> float: return self.x * other.x + self.y * other.y + self.z * other.z
    def magnitude(self) -> float: return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self) -> Vector3:
        mag = self.magnitude()
        return Vector3(self.x/mag, self.y/mag, self.z/mag) if mag > 0 else Vector3(0,0,0)

class OrbitPropagator:
    def __init__(self, altitude_km: float = 500.0, inclination_deg: float = 97.4):
        self.r_earth = 6371.0
        self.mu = 398600.4418
        self.radius = self.r_earth + altitude_km
        self.inclination = math.radians(inclination_deg)
        self.period = 2 * math.pi * math.sqrt(self.radius**3 / self.mu)
        self.angular_velocity = 2 * math.pi / self.period

    def get_state(self, time_s: float) -> tuple[Vector3, bool]:
        angle = self.angular_velocity * time_s
        sat_pos = Vector3(self.radius * math.cos(angle), self.radius * math.sin(angle) * math.cos(self.inclination), self.radius * math.sin(angle) * math.sin(self.inclination))
        sun_vec_inertial = Vector3(1, 0, 0)
        dot_product = sat_pos.dot(sun_vec_inertial)
        in_eclipse = False
        if dot_product < 0:
            dist_sq = (sat_pos.x - dot_product * sun_vec_inertial.x)**2 + (sat_pos.y - dot_product * sun_vec_inertial.y)**2 + (sat_pos.z - dot_product * sun_vec_inertial.z)**2
            if math.sqrt(dist_sq) < self.r_earth: in_eclipse = True
        body_sun_vec = Vector3(math.cos(angle * 0.1), math.sin(angle * 0.1), math.cos(angle * 0.05)).normalize()
        return (Vector3(0,0,0), True) if in_eclipse else (body_sun_vec, False)
