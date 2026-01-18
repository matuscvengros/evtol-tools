"""Temperature quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Temperature(BaseQuantity):
    """Represents a temperature quantity."""

    _quantity_type = 'temperature'
    _dimensionality = '[temperature]'
