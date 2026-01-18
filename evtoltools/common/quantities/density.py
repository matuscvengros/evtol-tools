"""Density quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Density(BaseQuantity):
    """Represents a density quantity."""

    _quantity_type = 'density'
    _dimensionality = '[mass] / [length] ** 3'
