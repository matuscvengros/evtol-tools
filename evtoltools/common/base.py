"""Base class for all physical quantity types in evtol-tools.

This module provides the abstract BaseQuantity class that all concrete
quantity classes inherit from. It encapsulates common functionality for
unit conversion, arithmetic operations, and representation.
"""

from abc import ABC
from typing import Union, Optional, Any
import numpy as np
from pint import Quantity as PintQuantity

from evtoltools.common.registry import ureg, Q_
from evtoltools.common.config import DEFAULT_UNITS, ALLOWED_UNITS


class BaseQuantity(ABC):
    """Abstract base class for typed physical quantities.

    This class wraps a pint Quantity and provides a typed, object-oriented
    interface with validation and default unit handling. Supports scalar values,
    lists, and numpy arrays.

    Subclasses must define:
        - _quantity_type: str identifier for the quantity (e.g., 'mass')
        - _dimensionality: Expected pint dimensionality for validation
    """

    # Subclasses must override these
    _quantity_type: str = None
    _dimensionality: str = None

    def __init__(self, value: Union[float, int, list, np.ndarray, PintQuantity],
                 unit: Optional[str] = None):
        """Initialize a quantity with value and unit.

        Args:
            value: Numeric value, list, numpy array, or pint Quantity
            unit: Unit string (e.g., 'kg', 'lbs'). If None and value is numeric,
                  uses the default unit for this quantity type.

        Raises:
            ValueError: If unit is not allowed for this quantity type
            DimensionalityError: If the units have wrong dimensionality
        """
        if self._quantity_type is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define _quantity_type"
            )

        # If value is already a pint Quantity, use it directly
        if isinstance(value, PintQuantity):
            self._quantity = value
        else:
            # Use provided unit or default
            if unit is None:
                unit = DEFAULT_UNITS[self._quantity_type]

            # Validate unit is allowed
            self._validate_unit(unit)

            # Create pint Quantity (pint handles numpy arrays natively)
            self._quantity = Q_(value, unit)

        # Validate dimensionality
        self._validate_dimensionality()

    def _validate_unit(self, unit: str) -> None:
        """Validate that unit is allowed for this quantity type."""
        allowed = ALLOWED_UNITS.get(self._quantity_type, [])
        if unit not in allowed:
            raise ValueError(
                f"Unit '{unit}' not allowed for {self._quantity_type}. "
                f"Allowed units: {', '.join(allowed)}"
            )

    def _validate_dimensionality(self) -> None:
        """Validate that the quantity has the correct dimensionality."""
        if self._dimensionality is not None:
            # Use pint's dimensionality comparison to handle equivalent dimensions
            # Different units can have different string representations but same dimensionality
            expected = ureg.get_dimensionality(self._dimensionality)
            actual = self._quantity.dimensionality

            if actual != expected:
                raise ValueError(
                    f"Expected dimensionality {self._dimensionality} for {self._quantity_type}, "
                    f"got {actual}"
                )

    def to(self, unit: str) -> 'BaseQuantity':
        """Convert to a different unit, returning a new instance.

        Args:
            unit: Target unit string

        Returns:
            New instance of the same type in the target unit

        Raises:
            ValueError: If unit is not allowed for this quantity type
        """
        self._validate_unit(unit)
        converted = self._quantity.to(unit)
        return self.__class__(converted)

    def to_default(self) -> 'BaseQuantity':
        """Convert to the default unit for this quantity type."""
        default_unit = DEFAULT_UNITS[self._quantity_type]
        return self.to(default_unit)

    @property
    def magnitude(self) -> Union[float, np.ndarray]:
        """Get the numeric value(s) in current units.

        Returns:
            Scalar float for scalar quantities, numpy array for array quantities.
        """
        return self._quantity.magnitude

    @property
    def units(self) -> str:
        """Get the current unit as a string."""
        return str(self._quantity.units)

    @property
    def value(self) -> Union[float, np.ndarray]:
        """Alias for magnitude."""
        return self.magnitude

    def in_units_of(self, unit: str) -> Union[float, np.ndarray]:
        """Get the numeric value(s) in specified units without creating new instance.

        Args:
            unit: Target unit string

        Returns:
            Numeric value(s) in target units (scalar or array)
        """
        return self.to(unit).magnitude

    # Arithmetic operations - return new instances
    def __add__(self, other: Union['BaseQuantity', PintQuantity]) -> 'BaseQuantity':
        if isinstance(other, BaseQuantity):
            result = self._quantity + other._quantity
        else:
            result = self._quantity + other
        return self.__class__(result)

    def __sub__(self, other: Union['BaseQuantity', PintQuantity]) -> 'BaseQuantity':
        if isinstance(other, BaseQuantity):
            result = self._quantity - other._quantity
        else:
            result = self._quantity - other
        return self.__class__(result)

    def __mul__(self, other: Union[float, int, 'BaseQuantity', PintQuantity]) -> Any:
        """Multiply by scalar or another quantity.

        Note: Multiplying two quantities may produce a different quantity type
        (e.g., Force * Length = Moment), so we return a pint Quantity.
        """
        if isinstance(other, BaseQuantity):
            return self._quantity * other._quantity
        else:
            # Scalar multiplication returns same type
            if isinstance(other, (int, float, np.ndarray)):
                result = self._quantity * other
                return self.__class__(result)
            return self._quantity * other

    def __truediv__(self, other: Union[float, int, 'BaseQuantity', PintQuantity]) -> Any:
        """Divide by scalar or another quantity."""
        if isinstance(other, BaseQuantity):
            return self._quantity / other._quantity
        else:
            if isinstance(other, (int, float, np.ndarray)):
                result = self._quantity / other
                return self.__class__(result)
            return self._quantity / other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if isinstance(other, BaseQuantity):
            result = other._quantity - self._quantity
        else:
            result = other - self._quantity
        return self.__class__(result)

    def __rmul__(self, other):
        return self.__mul__(other)

    # Comparison operations
    def __eq__(self, other: Union['BaseQuantity', PintQuantity]) -> bool:
        if isinstance(other, BaseQuantity):
            return self._quantity == other._quantity
        return self._quantity == other

    def __lt__(self, other: Union['BaseQuantity', PintQuantity]) -> Union[bool, np.ndarray]:
        if isinstance(other, BaseQuantity):
            return self._quantity < other._quantity
        return self._quantity < other

    def __le__(self, other: Union['BaseQuantity', PintQuantity]) -> Union[bool, np.ndarray]:
        if isinstance(other, BaseQuantity):
            return self._quantity <= other._quantity
        return self._quantity <= other

    def __gt__(self, other: Union['BaseQuantity', PintQuantity]) -> Union[bool, np.ndarray]:
        if isinstance(other, BaseQuantity):
            return self._quantity > other._quantity
        return self._quantity > other

    def __ge__(self, other: Union['BaseQuantity', PintQuantity]) -> Union[bool, np.ndarray]:
        if isinstance(other, BaseQuantity):
            return self._quantity >= other._quantity
        return self._quantity >= other

    # Representation
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.magnitude!r}, '{self.units}')"

    def __str__(self) -> str:
        return f"{self.magnitude} {self.units}"

    def __format__(self, format_spec: str) -> str:
        """Support format specifications.

        Examples:
            f"{mass:.2f}"  -> "1500.00 kg"
            f"{mass:.2f~}"  -> "1500.00 kg" (compact)
        """
        return format(self._quantity, format_spec)
