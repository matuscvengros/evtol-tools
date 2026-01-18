"""Electric charge/capacity quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Capacity(BaseQuantity):
    """Represents an electric charge quantity (battery capacity).

    This represents electric charge in amp-hours, commonly used
    for battery capacity ratings.
    """

    _quantity_type = 'capacity'
    _dimensionality = '[current] * [time]'
