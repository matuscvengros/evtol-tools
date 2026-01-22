"""Common utilities for evtol-tools including units system and atmosphere.

This module provides a type-safe, object-oriented interface to physical
quantities using the pint library under the hood, plus atmospheric calculations.

Examples:
    >>> from evtoltools.common import Mass
    >>> aircraft_weight = Mass(1500, 'kg')
    >>> weight_lbs = aircraft_weight.to('lbs')
    >>> print(f"Aircraft weighs {weight_lbs}")

    >>> import numpy as np
    >>> component_masses = Mass(np.array([100, 200, 300]), 'kg')
    >>> total = component_masses.magnitude.sum()

    >>> # Cross-type arithmetic with in_units_of helper
    >>> from evtoltools.common import Area, Mass, in_units_of
    >>> result = Area(10, 'm^2') * Mass(5, 'kg')
    >>> in_units_of(result, 'kg*m^2')
    50.0
"""

from typing import Union
import numpy as np
from pint import Quantity as PintQuantity

# Import all quantities from units package
from evtoltools.common.units import (
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
    BaseQuantity,
    ureg,
    Q_,
)

# Import atmosphere module
from evtoltools.common.atmosphere import (
    Altitude,
    Atmosphere,
    atmosphere_at_altitude,
    sea_level_atmosphere,
    ISA_SEA_LEVEL_TEMPERATURE,
    ISA_SEA_LEVEL_PRESSURE,
    ISA_SEA_LEVEL_DENSITY,
    ISA_SEA_LEVEL_SPEED_OF_SOUND,
)


def in_units_of(quantity: Union[BaseQuantity, PintQuantity], unit: str) -> Union[float, np.ndarray]:
    """Get numeric value of a quantity in specified units.

    Works with both BaseQuantity instances and raw pint Quantities (such as
    those returned from cross-type arithmetic operations).

    Args:
        quantity: A BaseQuantity instance or pint Quantity
        unit: Target unit string

    Returns:
        Numeric value in target units (scalar or array)

    Examples:
        >>> from evtoltools.common import Area, Mass, in_units_of
        >>>
        >>> # Works with BaseQuantity
        >>> area = Area(10, 'm^2')
        >>> in_units_of(area, 'ft^2')
        107.639...
        >>>
        >>> # Works with derived pint Quantities
        >>> mass = Mass(5, 'kg')
        >>> result = area * mass  # Returns pint Quantity
        >>> in_units_of(result, 'kg*m^2')
        50.0
    """
    if isinstance(quantity, BaseQuantity):
        return quantity._quantity.to(unit).magnitude
    elif isinstance(quantity, PintQuantity):
        return quantity.to(unit).magnitude
    else:
        raise TypeError(
            f"Expected BaseQuantity or pint Quantity, got {type(quantity).__name__}"
        )


__all__ = [
    # Primary API - quantity classes
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

    # Atmosphere API
    'Altitude',
    'Atmosphere',
    'atmosphere_at_altitude',
    'sea_level_atmosphere',
    'ISA_SEA_LEVEL_TEMPERATURE',
    'ISA_SEA_LEVEL_PRESSURE',
    'ISA_SEA_LEVEL_DENSITY',
    'ISA_SEA_LEVEL_SPEED_OF_SOUND',

    # Advanced API - direct pint access
    'ureg',
    'Q_',

    # Helper functions
    'in_units_of',
]

__version__ = '0.1.0'
