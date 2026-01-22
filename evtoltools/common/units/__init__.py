"""Units system for evtol-tools.

This package provides a type-safe, object-oriented interface to physical
quantities using the pint library under the hood.

Subpackages:
    quantities: Individual physical quantity type implementations

Modules:
    base: BaseQuantity abstract class
    config: Default and allowed units configuration
    registry: Pint UnitRegistry singleton
"""

# Core infrastructure
from evtoltools.common.units.registry import ureg, Q_
from evtoltools.common.units.config import DEFAULT_UNITS, ALLOWED_UNITS
from evtoltools.common.units.base import BaseQuantity

# All quantity types
from evtoltools.common.units.quantities import (
    Mass,
    Length,
    Time,
    Temperature,
    Current,
    Substance,
    Luminosity,
    Velocity,
    Area,
    Volume,
    Force,
    Power,
    Density,
    Moment,
    AngularVelocity,
    Voltage,
    Energy,
    Capacity,
    Pressure,
    Frequency,
    Resistance,
)

__all__ = [
    # Core infrastructure
    'ureg',
    'Q_',
    'DEFAULT_UNITS',
    'ALLOWED_UNITS',
    'BaseQuantity',

    # Quantity types
    'Mass',
    'Length',
    'Time',
    'Temperature',
    'Current',
    'Substance',
    'Luminosity',
    'Velocity',
    'Area',
    'Volume',
    'Force',
    'Power',
    'Density',
    'Moment',
    'AngularVelocity',
    'Voltage',
    'Energy',
    'Capacity',
    'Pressure',
    'Frequency',
    'Resistance',
]
