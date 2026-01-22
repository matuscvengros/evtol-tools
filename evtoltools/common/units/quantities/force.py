"""Force quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Force(BaseQuantity):
    """Represents a force quantity."""

    _quantity_type = 'force'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': 1, '[time]': -2})
