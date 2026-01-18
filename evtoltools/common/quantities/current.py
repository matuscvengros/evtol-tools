"""Electric current quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Current(BaseQuantity):
    """Represents an electric current quantity."""

    _quantity_type = 'current'
    _dimensionality = '[current]'
