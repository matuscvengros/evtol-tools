"""Angular velocity quantity type for evtol-tools."""

from evtoltools.common.base import BaseQuantity


class AngularVelocity(BaseQuantity):
    """Represents an angular velocity quantity."""

    _quantity_type = 'angular_velocity'
    _dimensionality = '1 / [time]'
