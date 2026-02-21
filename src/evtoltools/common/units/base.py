"""Base quantity class with SI-default storage and on-demand conversion."""

from __future__ import annotations

from abc import ABC

import numpy as np
from pint import Quantity as PintQuantity

from evtoltools.common.units.config import SI_DEFAULTS
from evtoltools.common.units.registry import Q_


class BaseQuantity(ABC):
    """Abstract base for dimensioned quantities.

    Stores values internally in SI units. Supports on-demand conversion via
    callable syntax: ``mass("lb")`` returns a new instance in pounds.

    Subclasses must define ``_quantity_type`` matching a key in ``SI_DEFAULTS``.
    """

    _quantity_type: str

    def __init__(self, value: float | np.ndarray | PintQuantity, unit: str | None = None) -> None:
        si_unit = SI_DEFAULTS[self._quantity_type]
        # Always changes to SI after initialisation
        if isinstance(value, PintQuantity):
            self._quantity = value.to(si_unit)
        else:
            if unit is None:
                unit = si_unit
            self._quantity = Q_(value, unit).to(si_unit)

    # -- Properties ----------------------------------------------------------

    @property
    def value(self) -> float | np.ndarray:
        """Raw numeric value in current units."""
        return self._quantity.magnitude

    @property
    def magnitude(self) -> float:
        """Vector magnitude (L2 norm) of the quantity."""
        if isinstance(self._quantity.magnitude, np.ndarray):
            return float(np.linalg.norm(self._quantity.magnitude))
        return float(self._quantity.magnitude)

    @property
    def units(self) -> str:
        """Current unit string."""
        return str(self._quantity.units)

    @property
    def quantity(self) -> PintQuantity:
        """Underlying pint Quantity."""
        return self._quantity

    # -- Conversion ----------------------------------------------------------

    def __call__(self, unit: str) -> BaseQuantity:
        """Return new instance converted to the given unit.

        Args:
            unit: Target unit string (e.g. ``"lb"``, ``"ft/s"``).

        Returns:
            New instance of the same type with the converted value.
        """
        converted = self._quantity.to(unit)
        instance = object.__new__(self.__class__)
        instance._quantity = converted
        return instance

    def to(self, unit: str) -> BaseQuantity:
        """Convert to a different unit. Returns a new instance.

        Args:
            unit: Target unit string.
        """
        return self(unit)

    def in_units_of(self, unit: str) -> float | np.ndarray:
        """Bare numeric value in the specified units.

        Args:
            unit: Target unit string.
        """
        return self(unit).value

    # -- Arithmetic ----------------------------------------------------------

    def __add__(self, other: BaseQuantity) -> BaseQuantity:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return self.__class__(self._quantity + other._quantity)
        return NotImplemented

    def __radd__(self, other: BaseQuantity) -> BaseQuantity:
        return self.__add__(other)

    def __sub__(self, other: BaseQuantity) -> BaseQuantity:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return self.__class__(self._quantity - other._quantity)
        return NotImplemented

    def __rsub__(self, other: BaseQuantity) -> BaseQuantity:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return self.__class__(other._quantity - self._quantity)
        return NotImplemented

    def __mul__(self, other: float | int | np.ndarray) -> BaseQuantity | PintQuantity:
        if isinstance(other, BaseQuantity):
            return self._quantity * other._quantity
        if isinstance(other, (int, float, np.ndarray)):
            return self.__class__(self._quantity * other)
        return NotImplemented

    def __rmul__(self, other: float | int | np.ndarray) -> BaseQuantity | PintQuantity:
        return self.__mul__(other)

    def __truediv__(
        self,
        other: float | int | np.ndarray | BaseQuantity,
    ) -> BaseQuantity | PintQuantity | float:
        if isinstance(other, BaseQuantity):
            if type(self) is type(other):
                result = self._quantity / other._quantity
                return float(result.to("dimensionless").magnitude)
            return self._quantity / other._quantity
        if isinstance(other, (int, float, np.ndarray)):
            return self.__class__(self._quantity / other)
        return NotImplemented

    def __rtruediv__(self, other: float | int) -> PintQuantity:
        if isinstance(other, (int, float)):
            return other / self._quantity
        return NotImplemented

    def __pow__(self, exponent: int | float) -> PintQuantity:
        return self._quantity**exponent

    def __neg__(self) -> BaseQuantity:
        return self.__class__(-self._quantity)

    def __abs__(self) -> BaseQuantity:
        return self.__class__(abs(self._quantity))

    # -- Comparisons ---------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return bool(self._quantity == other._quantity)
        return NotImplemented

    def __lt__(self, other: BaseQuantity) -> bool:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return bool(self._quantity < other._quantity)
        return NotImplemented

    def __le__(self, other: BaseQuantity) -> bool:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return bool(self._quantity <= other._quantity)
        return NotImplemented

    def __gt__(self, other: BaseQuantity) -> bool:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return bool(self._quantity > other._quantity)
        return NotImplemented

    def __ge__(self, other: BaseQuantity) -> bool:
        if isinstance(other, BaseQuantity) and type(self) is type(other):
            return bool(self._quantity >= other._quantity)
        return NotImplemented

    # -- Representation ------------------------------------------------------

    def __repr__(self) -> str:
        mag = self._quantity.magnitude
        if isinstance(mag, np.ndarray):
            return f"{self.__class__.__name__}({mag!r}, '{self.units}')"
        return f"{self.__class__.__name__}({mag:.6g}, '{self.units}')"

    def __str__(self) -> str:
        mag = self._quantity.magnitude
        if isinstance(mag, np.ndarray):
            return f"{mag} {self.units}"
        return f"{mag:.6g} {self.units}"

    def __format__(self, format_spec: str) -> str:
        return format(self._quantity, format_spec)

    def __float__(self) -> float:
        return float(self._quantity.to(SI_DEFAULTS[self._quantity_type]).magnitude)

    def __hash__(self) -> int:
        return hash((self.__class__, float(self)))
