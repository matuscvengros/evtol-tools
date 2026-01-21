"""Frequency quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Frequency(BaseQuantity):
    """Represents a frequency quantity."""

    _quantity_type = 'frequency'
    _dimensionality = UnitsContainer({'[time]': -1})
