"""Frequency quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Frequency(BaseQuantity):
    """Represents a frequency quantity."""

    _quantity_type = 'frequency'
    _dimensionality = '1 / [time]'
