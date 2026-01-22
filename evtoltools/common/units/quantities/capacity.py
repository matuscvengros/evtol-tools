"""Electric charge/capacity quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Capacity(BaseQuantity):
    """Represents an electric charge quantity (battery capacity).

    This represents electric charge in amp-hours, commonly used
    for battery capacity ratings.
    """

    _quantity_type = 'capacity'
    _dimensionality = UnitsContainer({'[current]': 1, '[time]': 1})
