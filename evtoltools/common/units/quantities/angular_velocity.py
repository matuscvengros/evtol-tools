"""Angular velocity quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class AngularVelocity(BaseQuantity):
    """Represents an angular velocity quantity."""

    _quantity_type = 'angular_velocity'
    _dimensionality = UnitsContainer({'[time]': -1})
