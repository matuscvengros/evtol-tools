"""Electric current quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Current(BaseQuantity):
    """Represents an electric current quantity."""

    _quantity_type = 'current'
    _dimensionality = UnitsContainer({'[current]': 1})
