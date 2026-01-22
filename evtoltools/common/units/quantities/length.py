"""Length quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Length(BaseQuantity):
    """Represents a length/distance quantity."""

    _quantity_type = 'length'
    _dimensionality = UnitsContainer({'[length]': 1})
