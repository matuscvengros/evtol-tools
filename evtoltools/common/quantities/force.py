"""Force quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Force(BaseQuantity):
    """Represents a force quantity."""

    _quantity_type = 'force'
    _dimensionality = '[mass] * [length] / [time] ** 2'
