"""Density quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Density(BaseQuantity):
    """Represents a density quantity."""

    _quantity_type = 'density'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': -3})
