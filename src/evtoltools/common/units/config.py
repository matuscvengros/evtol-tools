"""SI default units for quantity types."""

from __future__ import annotations

#: Mapping of quantity type name to its SI unit string.
SI_DEFAULTS: dict[str, str] = {
    "mass": "kg",
    "length": "m",
    "time": "s",
    "temperature": "K",
    "velocity": "m/s",
    "force": "N",
    "moment": "N*m",
    "power": "W",
    "energy": "J",
    "area": "m**2",
    "volume": "m**3",
    "density": "kg/m**3",
    "pressure": "Pa",
    "angular_velocity": "rad/s",
    "voltage": "V",
    "current": "A",
    "capacity": "A*h",
}
