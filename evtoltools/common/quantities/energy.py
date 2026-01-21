"""Energy quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Energy(BaseQuantity):
    """Represents an energy quantity."""

    _quantity_type = 'energy'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': 2, '[time]': -2})
