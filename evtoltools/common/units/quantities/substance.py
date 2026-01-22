"""Amount of substance quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Substance(BaseQuantity):
    """Represents an amount of substance quantity."""

    _quantity_type = 'substance'
    _dimensionality = UnitsContainer({'[substance]': 1})
