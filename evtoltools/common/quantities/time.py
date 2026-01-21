"""Time quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.base import BaseQuantity


class Time(BaseQuantity):
    """Represents a time/duration quantity."""

    _quantity_type = 'time'
    _dimensionality = UnitsContainer({'[time]': 1})
