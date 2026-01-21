"""Pressure quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Pressure(BaseQuantity):
    """Represents a pressure quantity."""

    _quantity_type = 'pressure'
    _dimensionality = '[mass] / [length] / [time] ** 2'
