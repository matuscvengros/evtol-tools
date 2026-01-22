"""Area quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Area(BaseQuantity):
    """Represents an area quantity."""

    _quantity_type = 'area'
    _dimensionality = UnitsContainer({'[length]': 2})
