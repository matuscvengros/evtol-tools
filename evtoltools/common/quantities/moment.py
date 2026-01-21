"""Moment/Torque quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Moment(BaseQuantity):
    """Represents a moment/torque quantity."""

    _quantity_type = 'moment'
    _dimensionality = UnitsContainer({'[mass]': 1, '[length]': 2, '[time]': -2})
