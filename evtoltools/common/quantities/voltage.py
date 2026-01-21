"""Voltage quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Voltage(BaseQuantity):
    """Represents an electrical voltage/potential difference quantity."""

    _quantity_type = 'voltage'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': 2, '[current]': -1, '[time]': -3})
