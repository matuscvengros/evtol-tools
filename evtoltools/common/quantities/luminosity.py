"""Luminous intensity quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Luminosity(BaseQuantity):
    """Represents a luminous intensity quantity."""

    _quantity_type = 'luminosity'
    _dimensionality = UnitsContainer({'[luminosity]': 1})
