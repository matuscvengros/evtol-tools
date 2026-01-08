"""Default unit configuration for evtol-tools.

This module defines the default units for each physical quantity type.
These defaults are used when converting quantities without specifying
a target unit, and for standardized output formats.
"""

from typing import Dict

# Default units for each quantity type
DEFAULT_UNITS: Dict[str, str] = {
    'mass': 'kg',
    'length': 'm',
    'velocity': 'm/s',
    'power': 'W',
    'force': 'N',
    'moment': 'N*m',
    'angular_velocity': 'rad/s',
    'density': 'kg/m**3',
    'area': 'm**2',
    'volume': 'm**3',
}

# Allowed alternative units for each quantity type
ALLOWED_UNITS: Dict[str, list[str]] = {
    'mass': ['kg', 'g', 'lb', 'lbs', 'ton', 'tonne', 'oz'],
    'length': ['m', 'cm', 'mm', 'ft', 'in', 'mi', 'km', 'nmi'],
    'velocity': ['m/s', 'km/h', 'mph', 'knots', 'ft/s'],
    'power': ['W', 'kW', 'MW', 'hp', 'bhp'],
    'force': ['N', 'kN', 'lbf', 'kgf'],
    'moment': ['N*m', 'ft*lbf', 'in*lbf'],
    'angular_velocity': ['rad/s', 'rpm', 'deg/s'],
    'density': ['kg/m**3', 'g/cm**3', 'lb/ft**3'],
    'area': ['m**2', 'cm**2', 'ft**2', 'in**2'],
    'volume': ['m**3', 'L', 'gal', 'ft**3'],
}

__all__ = ['DEFAULT_UNITS', 'ALLOWED_UNITS']
