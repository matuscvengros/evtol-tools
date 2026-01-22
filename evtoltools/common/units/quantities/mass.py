"""Mass quantity implementation for evtol-tools.

This module provides the Mass class for representing and manipulating
mass/weight values with automatic unit conversion.
"""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Mass(BaseQuantity):
    """Represents a mass/weight quantity.

    Supports scalar values, lists, and numpy arrays for batch calculations.

    Examples:
        >>> m = Mass(1500, 'kg')
        >>> m.to('lbs')
        Mass(3306.9339, 'lbs')

        >>> empty_weight = Mass(2500, 'kg')
        >>> payload = Mass(500, 'kg')
        >>> total = empty_weight + payload
        >>> total.to('lbs').magnitude
        6613.867865546327

        >>> Mass(100, 'lbs').in_units_of('kg')
        45.359237

        >>> import numpy as np
        >>> masses = Mass(np.array([100, 200, 300]), 'kg')
        >>> masses.to('lbs').magnitude
        array([220.46226218, 440.92452437, 661.38678655])
    """

    _quantity_type = 'mass'
    _dimensionality = UnitsContainer({'[mass]': 1})
