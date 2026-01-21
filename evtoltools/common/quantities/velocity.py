"""Velocity quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Velocity(BaseQuantity):
    """Represents a velocity/speed quantity."""

    _quantity_type = 'velocity'
    _dimensionality = UnitsContainer({'[length]': 1, '[time]': -1})
