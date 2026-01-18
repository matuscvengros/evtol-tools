"""Volume quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Volume(BaseQuantity):
    """Represents a volume quantity."""

    _quantity_type = 'volume'
    _dimensionality = '[length] ** 3'
