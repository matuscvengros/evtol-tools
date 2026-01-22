"""Pressure quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Pressure(BaseQuantity):
    """Represents a pressure quantity."""

    _quantity_type = 'pressure'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': -1, '[time]': -2})
