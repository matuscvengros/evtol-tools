"""Moment/Torque quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Moment(BaseQuantity):
    """Represents a moment/torque quantity."""

    _quantity_type = 'moment'
    _dimensionality = '[mass] * [length] ** 2 / [time] ** 2'
