"""Unit tests for the Mass quantity class."""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal
from evtoltools.common import Mass


class TestMassConstruction:
    """Test Mass construction with various inputs."""

    def test_default_unit(self):
        """Test that default unit is kg."""
        m = Mass(100)
        assert m.magnitude == 100
        assert m.units == 'kilogram'

    def test_explicit_unit_kg(self):
        """Test construction with explicit kg unit."""
        m = Mass(100, 'kg')
        assert m.magnitude == 100
        assert m.units == 'kilogram'

    def test_explicit_unit_lbs(self):
        """Test construction with pounds."""
        m = Mass(100, 'lbs')
        assert m.magnitude == 100
        assert m.units == 'pound'

    def test_array_input(self):
        """Test construction with numpy array."""
        values = np.array([100, 200, 300])
        m = Mass(values, 'kg')
        assert_array_almost_equal(m.magnitude, values)
        assert m.units == 'kilogram'

    def test_list_input(self):
        """Test construction with list."""
        values = [100, 200, 300]
        m = Mass(values, 'kg')
        assert_array_almost_equal(m.magnitude, np.array(values))
        assert m.units == 'kilogram'

    def test_invalid_unit(self):
        """Test that invalid units raise ValueError."""
        with pytest.raises(ValueError, match="Unit 'm' not allowed"):
            Mass(100, 'm')

    def test_pint_quantity_input(self):
        """Test construction from existing pint Quantity."""
        from evtoltools.common import Q_
        q = Q_(100, 'kg')
        m = Mass(q)
        assert m.magnitude == 100
        assert m.units == 'kilogram'


class TestMassConversion:
    """Test unit conversions."""

    def test_kg_to_lbs(self):
        """Test conversion from kg to lbs."""
        m = Mass(1, 'kg')
        m_lbs = m.to('lbs')
        assert m_lbs.units == 'pound'
        assert abs(m_lbs.magnitude - 2.20462) < 0.001

    def test_lbs_to_kg(self):
        """Test conversion from lbs to kg."""
        m = Mass(100, 'lbs')
        m_kg = m.to('kg')
        assert m_kg.units == 'kilogram'
        assert abs(m_kg.magnitude - 45.359237) < 0.001

    def test_to_default(self):
        """Test conversion to default unit."""
        m = Mass(100, 'lbs')
        m_default = m.to_default()
        assert m_default.units == 'kilogram'

    def test_in_units_of_returns_float(self):
        """Test in_units_of returns numeric value."""
        m = Mass(100, 'kg')
        lbs = m.in_units_of('lbs')
        assert isinstance(lbs, (float, np.floating))
        assert abs(lbs - 220.462) < 0.01

    def test_array_conversion(self):
        """Test conversion with arrays."""
        masses = Mass(np.array([1, 2, 3]), 'kg')
        masses_lbs = masses.to('lbs')
        expected = np.array([2.20462, 4.40924, 6.61387])
        assert_array_almost_equal(masses_lbs.magnitude, expected, decimal=4)

    @pytest.mark.parametrize("value,from_unit,to_unit,expected", [
        (1000, 'g', 'kg', 1),
        (1, 'ton', 'kg', 907.18474),
        (16, 'oz', 'lbs', 1),
        (1, 'tonne', 'kg', 1000),
    ])
    def test_various_conversions(self, value, from_unit, to_unit, expected):
        """Test various unit conversions."""
        m = Mass(value, from_unit)
        converted = m.to(to_unit)
        assert abs(converted.magnitude - expected) < 0.01


class TestMassArithmetic:
    """Test arithmetic operations."""

    def test_addition_same_units(self):
        """Test addition with same units."""
        m1 = Mass(100, 'kg')
        m2 = Mass(50, 'kg')
        result = m1 + m2
        assert isinstance(result, Mass)
        assert result.magnitude == 150
        assert result.units == 'kilogram'

    def test_addition_different_units(self):
        """Test addition with different units (automatic conversion)."""
        m1 = Mass(1, 'kg')
        m2 = Mass(1, 'lbs')
        result = m1 + m2
        assert isinstance(result, Mass)
        # Result should be in units of first operand
        assert result.units == 'kilogram'
        assert abs(result.magnitude - 1.453592) < 0.001

    def test_subtraction(self):
        """Test subtraction."""
        m1 = Mass(100, 'kg')
        m2 = Mass(50, 'kg')
        result = m1 - m2
        assert isinstance(result, Mass)
        assert result.magnitude == 50
        assert result.units == 'kilogram'

    def test_scalar_multiplication(self):
        """Test multiplication by scalar."""
        m = Mass(100, 'kg')
        result = m * 2
        assert isinstance(result, Mass)
        assert result.magnitude == 200
        assert result.units == 'kilogram'

    def test_scalar_division(self):
        """Test division by scalar."""
        m = Mass(100, 'kg')
        result = m / 2
        assert isinstance(result, Mass)
        assert result.magnitude == 50
        assert result.units == 'kilogram'

    def test_array_addition(self):
        """Test addition with arrays."""
        m1 = Mass(np.array([100, 200, 300]), 'kg')
        m2 = Mass(np.array([10, 20, 30]), 'kg')
        result = m1 + m2
        expected = np.array([110, 220, 330])
        assert_array_almost_equal(result.magnitude, expected)

    def test_array_scalar_addition(self):
        """Test adding scalar to array (broadcasting)."""
        m_array = Mass(np.array([100, 200, 300]), 'kg')
        m_scalar = Mass(10, 'kg')
        result = m_array + m_scalar
        expected = np.array([110, 210, 310])
        assert_array_almost_equal(result.magnitude, expected)

    def test_array_scalar_multiplication(self):
        """Test multiplying array by scalar."""
        m = Mass(np.array([100, 200, 300]), 'kg')
        result = m * 2
        expected = np.array([200, 400, 600])
        assert_array_almost_equal(result.magnitude, expected)

    def test_reverse_operations(self):
        """Test reverse operations (2 * mass)."""
        m = Mass(100, 'kg')
        result = 2 * m
        assert isinstance(result, Mass)
        assert result.magnitude == 200


class TestMassComparisons:
    """Test comparison operations."""

    def test_equality_same_units(self):
        """Test equality with same units."""
        m1 = Mass(100, 'kg')
        m2 = Mass(100, 'kg')
        assert m1 == m2

    def test_equality_different_units(self):
        """Test equality with different units."""
        m1 = Mass(1, 'kg')
        m2 = Mass(2.20462, 'lbs')
        # Pint handles unit conversion in comparisons
        assert abs((m1 - m2).magnitude) < 0.001

    def test_less_than(self):
        """Test less than comparison."""
        m1 = Mass(100, 'kg')
        m2 = Mass(200, 'kg')
        assert m1 < m2
        assert not m2 < m1

    def test_greater_than(self):
        """Test greater than comparison."""
        m1 = Mass(200, 'kg')
        m2 = Mass(100, 'kg')
        assert m1 > m2
        assert not m2 > m1

    def test_less_than_or_equal(self):
        """Test less than or equal."""
        m1 = Mass(100, 'kg')
        m2 = Mass(100, 'kg')
        m3 = Mass(200, 'kg')
        assert m1 <= m2
        assert m1 <= m3

    def test_greater_than_or_equal(self):
        """Test greater than or equal."""
        m1 = Mass(100, 'kg')
        m2 = Mass(100, 'kg')
        m3 = Mass(50, 'kg')
        assert m1 >= m2
        assert m1 >= m3

    def test_array_comparison(self):
        """Test comparisons with arrays."""
        m1 = Mass(np.array([100, 200, 300]), 'kg')
        m2 = Mass(150, 'kg')
        result = m1 > m2
        expected = np.array([False, True, True])
        assert_array_almost_equal(result, expected)


class TestMassRepresentation:
    """Test string representations and formatting."""

    def test_repr(self):
        """Test __repr__ output."""
        m = Mass(100, 'kg')
        repr_str = repr(m)
        assert 'Mass' in repr_str
        assert '100' in repr_str
        assert 'kg' in repr_str or 'kilogram' in repr_str

    def test_str(self):
        """Test __str__ output."""
        m = Mass(100, 'kg')
        str_output = str(m)
        assert '100' in str_output
        assert 'kg' in str_output or 'kilogram' in str_output

    def test_format_precision(self):
        """Test formatting with precision."""
        m = Mass(1234.5678, 'kg')
        formatted = f"{m:.2f}"
        assert '1234.57' in formatted


class TestMassProperties:
    """Test properties and accessors."""

    def test_magnitude_property(self):
        """Test magnitude property."""
        m = Mass(100, 'kg')
        assert m.magnitude == 100

    def test_value_property(self):
        """Test value property (alias for magnitude)."""
        m = Mass(100, 'kg')
        assert m.value == m.magnitude

    def test_units_property(self):
        """Test units property."""
        m = Mass(100, 'kg')
        assert 'kg' in m.units or 'kilogram' in m.units

    def test_array_magnitude(self):
        """Test magnitude property with arrays."""
        values = np.array([100, 200, 300])
        m = Mass(values, 'kg')
        assert_array_almost_equal(m.magnitude, values)


class TestMassEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_mass(self):
        """Test with zero value."""
        m = Mass(0, 'kg')
        assert m.magnitude == 0

    def test_negative_mass(self):
        """Test with negative value (physically invalid but mathematically allowed)."""
        m = Mass(-100, 'kg')
        assert m.magnitude == -100

    def test_very_large_value(self):
        """Test with very large value."""
        m = Mass(1e10, 'kg')
        assert m.magnitude == 1e10

    def test_very_small_value(self):
        """Test with very small value."""
        m = Mass(1e-10, 'kg')
        assert m.magnitude == 1e-10

    def test_empty_array(self):
        """Test with empty array."""
        m = Mass(np.array([]), 'kg')
        assert len(m.magnitude) == 0


class TestMassIntegration:
    """Integration tests for realistic use cases."""

    def test_aircraft_weight_calculation(self):
        """Test realistic aircraft weight calculation."""
        empty_weight = Mass(2500, 'kg')
        payload = Mass(500, 'kg')
        fuel = Mass(300, 'kg')

        total_weight = empty_weight + payload + fuel
        assert isinstance(total_weight, Mass)
        assert total_weight.magnitude == 3300
        assert total_weight.to('lbs').magnitude > 7200  # Approximately 7275 lbs

    def test_weight_fractions(self):
        """Test calculation of weight fractions."""
        total = Mass(1000, 'kg')
        battery = Mass(300, 'kg')

        # Weight fraction (returns pint Quantity, dimensionless)
        fraction = battery / total
        # Convert to float for comparison
        assert abs(fraction.magnitude - 0.3) < 0.001

    def test_component_masses_array(self):
        """Test managing multiple component masses."""
        components = Mass(np.array([100, 200, 150, 250, 300]), 'kg')

        # Total mass
        total = components.magnitude.sum()
        assert total == 1000

        # Convert all to lbs
        components_lbs = components.to('lbs')
        total_lbs = components_lbs.magnitude.sum()
        assert abs(total_lbs - 2204.62) < 1  # Allow small rounding error
