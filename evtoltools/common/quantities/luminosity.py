"""Luminous intensity quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Luminosity(BaseQuantity):
    """Represents a luminous intensity quantity."""

    _quantity_type = 'luminosity'
    _dimensionality = '[luminosity]'
