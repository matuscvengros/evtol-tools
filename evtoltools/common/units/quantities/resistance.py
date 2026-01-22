"""Resistance quantity type for evtol-tools."""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class Resistance(BaseQuantity):
    """Represents an electrical resistance quantity (Ohms).

    Dimensionally: [mass] * [length]^2 / ([current]^2 * [time]^3)
    which equals voltage / current = V / A = Ohm.
    """

    _quantity_type = 'resistance'
    _dimensionality = UnitsContainer({
        '[mass]': 1,
        '[length]': 2,
        '[current]': -2,
        '[time]': -3
    })
