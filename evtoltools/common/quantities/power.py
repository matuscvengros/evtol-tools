"""Power quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Power(BaseQuantity):
    """Represents a power quantity."""

    _quantity_type = 'power'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': 2, '[time]': -3})
