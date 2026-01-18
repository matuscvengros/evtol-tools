"""Amount of substance quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Substance(BaseQuantity):
    """Represents an amount of substance quantity."""

    _quantity_type = 'substance'
    _dimensionality = '[substance]'
