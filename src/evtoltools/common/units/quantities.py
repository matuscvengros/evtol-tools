"""Concrete quantity classes for all supported physical types."""

from __future__ import annotations

from evtoltools.common.units.base import BaseQuantity


class Mass(BaseQuantity):
    _quantity_type = "mass"


class Length(BaseQuantity):
    _quantity_type = "length"


class Time(BaseQuantity):
    _quantity_type = "time"


class Temperature(BaseQuantity):
    _quantity_type = "temperature"


class Velocity(BaseQuantity):
    _quantity_type = "velocity"


class Force(BaseQuantity):
    _quantity_type = "force"


class Moment(BaseQuantity):
    _quantity_type = "moment"


class Power(BaseQuantity):
    _quantity_type = "power"


class Energy(BaseQuantity):
    _quantity_type = "energy"


class Area(BaseQuantity):
    _quantity_type = "area"


class Volume(BaseQuantity):
    _quantity_type = "volume"


class Density(BaseQuantity):
    _quantity_type = "density"


class Pressure(BaseQuantity):
    _quantity_type = "pressure"


class AngularVelocity(BaseQuantity):
    _quantity_type = "angular_velocity"


class Voltage(BaseQuantity):
    _quantity_type = "voltage"


class Current(BaseQuantity):
    _quantity_type = "current"


class Capacity(BaseQuantity):
    _quantity_type = "capacity"
