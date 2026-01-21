"""Temperature quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Temperature(BaseQuantity):
    """Represents a temperature quantity."""

    _quantity_type = 'temperature'
    _dimensionality = UnitsContainer({'[temperature]': 1})
