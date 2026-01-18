"""Voltage quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Voltage(BaseQuantity):
    """Represents an electrical voltage/potential difference quantity."""

    _quantity_type = 'voltage'
    _dimensionality = '[length] ** 2 * [mass] / [current] / [time] ** 3'
