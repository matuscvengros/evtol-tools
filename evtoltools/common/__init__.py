"""Common utilities for evtol-tools including units system.

This module provides a type-safe, object-oriented interface to physical
quantities using the pint library under the hood.

Examples:
    >>> from evtoltools.common import Mass
    >>> aircraft_weight = Mass(1500, 'kg')
    >>> weight_lbs = aircraft_weight.to('lbs')
    >>> print(f"Aircraft weighs {weight_lbs}")

    >>> import numpy as np
    >>> component_masses = Mass(np.array([100, 200, 300]), 'kg')
    >>> total = component_masses.magnitude.sum()
"""

from evtoltools.common.quantities import (
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
)

# For advanced users who need direct pint access
from evtoltools.common.registry import ureg, Q_

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

    # Advanced API - direct pint access
    'ureg',
    'Q_',
]

__version__ = '0.1.0'
