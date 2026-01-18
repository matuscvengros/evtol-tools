"""Length quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Length(BaseQuantity):
    """Represents a length/distance quantity."""

    _quantity_type = 'length'
    _dimensionality = '[length]'
