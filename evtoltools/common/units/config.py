"""Default unit configuration for evtol-tools.

This module defines the default units for each physical quantity type.
These defaults are used when converting quantities without specifying
a target unit, and for standardized output formats.
"""

from typing import Dict

# Default units for each quantity type
DEFAULT_UNITS: Dict[str, str] = {
    # SI base quantities
    'mass': 'kg',
    'length': 'm',
    'time': 's',
    'temperature': 'K',
    'current': 'A',
    'substance': 'mol',
    'luminosity': 'cd',
    # Derived quantities
    'velocity': 'm/s',
    'power': 'W',
    'force': 'N',
    'moment': 'N*m',
    'angular_velocity': 'rad/s',
    'density': 'kg/m^3',
    'area': 'm^2',
    'volume': 'm^3',
    'voltage': 'V',
    'energy': 'J',
    'capacity': 'Ah',
    'pressure': 'Pa',
    'frequency': 'Hz',
    'resistance': 'ohm',
}

# Allowed alternative units for each quantity type
ALLOWED_UNITS: Dict[str, list[str]] = {
    # SI base quantities
    'mass': ['kg', 'g', 'lb', 'lbs', 'ton', 'tonne', 'oz'],
    'length': ['m', 'cm', 'mm', 'ft', 'in', 'mi', 'km', 'nmi'],
    'time': ['s', 'ms', 'min', 'hr', 'day'],
    'temperature': ['K', 'degC', 'degF'],
    'current': ['A', 'mA', 'uA', 'kA'],
    'substance': ['mol', 'mmol', 'kmol'],
    'luminosity': ['cd', 'lm'],
    # Derived quantities
    'velocity': ['m/s', 'km/h', 'mph', 'knots', 'ft/s'],
    'power': ['W', 'kW', 'MW', 'hp', 'bhp'],
    'force': ['N', 'kN', 'lbf', 'kgf'],
    'moment': ['N*m', 'ft*lbf', 'in*lbf'],
    'angular_velocity': ['rad/s', 'rpm', 'deg/s'],
    'density': ['kg/m^3', 'g/cm^3', 'lb/ft^3'],
    'area': ['m^2', 'cm^2', 'ft^2', 'in^2'],
    'volume': ['m^3', 'L', 'gal', 'ft^3'],
    'voltage': ['V', 'mV', 'kV'],
    'energy': ['J', 'kJ', 'MJ', 'Wh', 'kWh', 'mWh'],
    'capacity': ['Ah', 'mAh', 'C'],
    'pressure': ['Pa', 'kPa', 'bar', 'psi', 'atm'],
    'frequency': ['Hz', 'kHz', 'MHz', 'mHz'],
    'resistance': ['ohm', 'mohm', 'kohm', 'Mohm'],
}

__all__ = ['DEFAULT_UNITS', 'ALLOWED_UNITS']
