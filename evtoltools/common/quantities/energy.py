"""Energy quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Energy(BaseQuantity):
    """Represents an energy quantity."""

    _quantity_type = 'energy'
    _dimensionality = '[length] ** 2 * [mass] / [time] ** 2'
