"""Atmosphere module for evtol-tools.

This package provides atmospheric calculations for eVTOL aircraft analysis,
including the International Standard Atmosphere (ISA) model and altitude
quantity handling.

Modules:
    altitude: Altitude quantity class with aviation-specific functionality
    isa: International Standard Atmosphere calculations

Examples:
    >>> from evtoltools.common import Atmosphere, Altitude, Temperature
    >>>
    >>> # Create atmosphere at altitude
    >>> atm = Atmosphere(Altitude(5000, 'ft'))
    >>> print(f"Density: {atm.density}")
    >>>
    >>> # Flight level conversion
    >>> cruise = Altitude.from_flight_level(100)  # FL100 = 10,000 ft
    >>> print(f"Cruise altitude: {cruise}")
    >>>
    >>> # Hot day analysis
    >>> atm_hot = Atmosphere(Altitude(2000, 'ft'), Temperature(20, 'K'))
    >>> print(f"Hot day density: {atm_hot.density}")
"""

# Altitude class
from evtoltools.common.atmosphere.altitude import Altitude, SEA_LEVEL

# ISA Atmosphere class and functions
from evtoltools.common.atmosphere.isa import (
    Atmosphere,
    atmosphere_at_altitude,
    sea_level_atmosphere,
    ISA_SEA_LEVEL_TEMPERATURE,
    ISA_SEA_LEVEL_PRESSURE,
    ISA_SEA_LEVEL_DENSITY,
    ISA_SEA_LEVEL_SPEED_OF_SOUND,
    GAS_CONSTANT_AIR,
    GAMMA_AIR,
)

__all__ = [
    # Altitude
    'Altitude',
    'SEA_LEVEL',

    # Atmosphere
    'Atmosphere',
    'atmosphere_at_altitude',
    'sea_level_atmosphere',

    # ISA Constants
    'ISA_SEA_LEVEL_TEMPERATURE',
    'ISA_SEA_LEVEL_PRESSURE',
    'ISA_SEA_LEVEL_DENSITY',
    'ISA_SEA_LEVEL_SPEED_OF_SOUND',
    'GAS_CONSTANT_AIR',
    'GAMMA_AIR',
]
