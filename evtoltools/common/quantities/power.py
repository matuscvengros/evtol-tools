"""Power quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Power(BaseQuantity):
    """Represents a power quantity."""

    _quantity_type = 'power'
    _dimensionality = '[mass] * [length] ** 2 / [time] ** 3'
