"""Velocity quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class Velocity(BaseQuantity):
    """Represents a velocity/speed quantity."""

    _quantity_type = 'velocity'
    _dimensionality = '[length] / [time]'
