"""Tests for Resistance quantity type.

This module provides tests for the Resistance quantity class.
"""

import numpy as np
import pytest

from evtoltools.common import Resistance


class TestResistanceConstruction:
    """Tests for Resistance construction."""

    def test_default_unit_ohm(self):
        """Default unit should be ohm."""
        r = Resistance(100)
        assert r.units == 'ohm'
        assert r.magnitude == 100

    def test_explicit_unit_ohm(self):
        """Construction with explicit ohm unit."""
        r = Resistance(50, 'ohm')
        assert r.magnitude == 50
        assert r.units == 'ohm'

    def test_milliohm_unit(self):
        """Construction with milliohm unit."""
        r = Resistance(30, 'mohm')
        assert r.in_units_of('ohm') == pytest.approx(0.03)

    def test_kilohm_unit(self):
        """Construction with kilohm unit."""
        r = Resistance(1.5, 'kohm')
        assert r.in_units_of('ohm') == pytest.approx(1500)


class TestResistanceConversion:
    """Tests for Resistance unit conversion."""

    def test_ohm_to_mohm(self):
        """Convert ohm to milliohm."""
        r = Resistance(0.05, 'ohm')
        r_mohm = r.to('mohm')
        assert r_mohm.in_units_of('mohm') == pytest.approx(50)

    def test_mohm_to_ohm(self):
        """Convert milliohm to ohm."""
        r = Resistance(30, 'mohm')
        r_ohm = r.to('ohm')
        assert r_ohm.in_units_of('ohm') == pytest.approx(0.03)

    def test_in_units_of_preserves_value(self):
        """in_units_of should return correct numeric value."""
        r = Resistance(1000, 'mohm')
        assert r.in_units_of('ohm') == pytest.approx(1.0)


class TestResistanceArithmetic:
    """Tests for Resistance arithmetic operations."""

    def test_addition(self):
        """Adding resistances."""
        r1 = Resistance(10, 'ohm')
        r2 = Resistance(20, 'ohm')
        result = r1 + r2
        assert result.in_units_of('ohm') == pytest.approx(30)

    def test_addition_mixed_units(self):
        """Adding resistances with different units."""
        r1 = Resistance(1, 'ohm')
        r2 = Resistance(500, 'mohm')
        result = r1 + r2
        assert result.in_units_of('ohm') == pytest.approx(1.5)

    def test_subtraction(self):
        """Subtracting resistances."""
        r1 = Resistance(100, 'mohm')
        r2 = Resistance(30, 'mohm')
        result = r1 - r2
        assert result.in_units_of('mohm') == pytest.approx(70)

    def test_scalar_multiplication(self):
        """Multiplying resistance by scalar."""
        r = Resistance(10, 'ohm')
        result = r * 3
        assert result.in_units_of('ohm') == pytest.approx(30)

    def test_scalar_division(self):
        """Dividing resistance by scalar."""
        r = Resistance(30, 'mohm')
        result = r / 3
        assert result.in_units_of('mohm') == pytest.approx(10)


class TestResistanceComparison:
    """Tests for Resistance comparison operations."""

    def test_equality(self):
        """Resistance equality comparison."""
        r1 = Resistance(30, 'mohm')
        r2 = Resistance(0.03, 'ohm')
        assert r1 == r2

    def test_less_than(self):
        """Resistance less than comparison."""
        r1 = Resistance(20, 'mohm')
        r2 = Resistance(30, 'mohm')
        assert r1 < r2

    def test_greater_than(self):
        """Resistance greater than comparison."""
        r1 = Resistance(1, 'ohm')
        r2 = Resistance(500, 'mohm')
        assert r1 > r2


class TestResistanceArray:
    """Tests for Resistance with numpy arrays."""

    def test_array_construction(self):
        """Resistance with array values."""
        values = np.array([10, 20, 30])
        r = Resistance(values, 'mohm')
        assert len(r.magnitude) == 3
        np.testing.assert_array_almost_equal(r.magnitude, values)

    def test_array_conversion(self):
        """Array resistance conversion."""
        r = Resistance(np.array([10, 20, 30]), 'mohm')
        r_ohm = r.to('ohm')
        np.testing.assert_array_almost_equal(
            r_ohm.magnitude, [0.01, 0.02, 0.03]
        )

    def test_array_scalar_ops(self):
        """Array resistance with scalar operations."""
        r = Resistance(np.array([10, 20, 30]), 'mohm')
        result = r * 2
        np.testing.assert_array_almost_equal(
            result.magnitude, [20, 40, 60]
        )


class TestResistanceRepr:
    """Tests for Resistance string representation."""

    def test_repr(self):
        """Resistance repr format."""
        r = Resistance(30, 'mohm')
        repr_str = repr(r)
        assert 'Resistance' in repr_str
        assert '30' in repr_str

    def test_str(self):
        """Resistance str format."""
        r = Resistance(30, 'mohm')
        str_str = str(r)
        assert '30' in str_str


class TestResistanceValidation:
    """Tests for Resistance validation."""

    def test_invalid_unit_raises(self):
        """Invalid unit should raise ValueError."""
        with pytest.raises(ValueError):
            Resistance(10, 'kg')  # Wrong dimensionality

    def test_invalid_unit_string_raises(self):
        """Unrecognized unit string should raise."""
        with pytest.raises(ValueError):
            Resistance(10, 'megaohms_fake')
