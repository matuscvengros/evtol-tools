"""Volume quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Volume(BaseQuantity):
    """Represents a volume quantity."""

    _quantity_type = 'volume'
    _dimensionality = UnitsContainer({'[length]': 3})
