"""Area quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Area(BaseQuantity):
    """Represents an area quantity."""

    _quantity_type = 'area'
    _dimensionality = '[length] ** 2'
