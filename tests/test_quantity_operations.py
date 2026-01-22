"""Unit tests for extended quantity mathematical operations.

Tests cover:
- Exponentiation (__pow__)
- Negation (__neg__)
- Absolute value (__abs__)
- Reverse division (__rtruediv__)
- Float conversion (__float__)
- sqrt() helper function
- Integration tests for physics formulas
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal
from pint import Quantity as PintQuantity

from evtoltools.common import (
    Mass, Length, Time, Area, Volume, Force, Power, Density, Velocity,
    AngularVelocity, Frequency, sqrt, in_units_of
)


class TestQuantityPower:
    """Test exponentiation operations."""

    def test_power_integer_exponent(self):
        """Test raising quantity to integer power."""
        length = Length(2, 'm')
        result = length ** 2
        assert isinstance(result, PintQuantity)
        assert abs(in_units_of(result, 'm^2') - 4) < 0.001

    def test_power_float_exponent(self):
        """Test raising quantity to float power."""
        force = Force(1000, 'N')
        result = force ** 1.5
        assert isinstance(result, PintQuantity)
        # 1000^1.5 = 31622.776...
        assert abs(result.magnitude - 31622.776) < 0.1

    def test_square_root_via_power(self):
        """Test square root via ** 0.5."""
        area = Area(100, 'm^2')
        result = area ** 0.5
        assert isinstance(result, PintQuantity)
        assert abs(in_units_of(result, 'm') - 10) < 0.001

    def test_cube_root_via_power(self):
        """Test cube root via ** (1/3)."""
        volume = Volume(27, 'm^3')
        result = volume ** (1/3)
        assert isinstance(result, PintQuantity)
        assert abs(in_units_of(result, 'm') - 3) < 0.001

    def test_power_with_array(self):
        """Test exponentiation with array quantities."""
        areas = Area(np.array([1, 4, 9, 16]), 'm^2')
        result = areas ** 0.5
        expected = np.array([1, 2, 3, 4])
        assert_array_almost_equal(result.magnitude, expected)

    def test_power_preserves_units(self):
        """Test that power changes units appropriately."""
        length = Length(2, 'm')
        squared = length ** 2
        # Should be in m^2
        assert 'm ** 2' in str(squared.units) or 'meter ** 2' in str(squared.units)

    def test_power_invalid_exponent(self):
        """Test that invalid exponent returns NotImplemented."""
        length = Length(2, 'm')
        result = length.__pow__('invalid')
        assert result is NotImplemented


class TestQuantityNegation:
    """Test negation operations."""

    def test_negation_positive(self):
        """Test negating positive quantity."""
        m = Mass(100, 'kg')
        result = -m
        assert isinstance(result, Mass)
        assert result.magnitude == -100
        assert result.units == 'kilogram'

    def test_negation_negative(self):
        """Test negating negative quantity."""
        m = Mass(-100, 'kg')
        result = -m
        assert isinstance(result, Mass)
        assert result.magnitude == 100

    def test_negation_zero(self):
        """Test negating zero."""
        m = Mass(0, 'kg')
        result = -m
        assert isinstance(result, Mass)
        assert result.magnitude == 0

    def test_negation_array(self):
        """Test negating array quantity."""
        m = Mass(np.array([100, -200, 300]), 'kg')
        result = -m
        expected = np.array([-100, 200, -300])
        assert_array_almost_equal(result.magnitude, expected)

    def test_double_negation(self):
        """Test that double negation returns original value."""
        m = Mass(100, 'kg')
        result = --m
        assert result.magnitude == 100


class TestQuantityAbsoluteValue:
    """Test absolute value operations."""

    def test_abs_negative(self):
        """Test absolute value of negative quantity."""
        m = Mass(-100, 'kg')
        result = abs(m)
        assert isinstance(result, Mass)
        assert result.magnitude == 100
        assert result.units == 'kilogram'

    def test_abs_positive(self):
        """Test absolute value of positive quantity."""
        m = Mass(100, 'kg')
        result = abs(m)
        assert isinstance(result, Mass)
        assert result.magnitude == 100

    def test_abs_zero(self):
        """Test absolute value of zero."""
        m = Mass(0, 'kg')
        result = abs(m)
        assert isinstance(result, Mass)
        assert result.magnitude == 0

    def test_abs_array(self):
        """Test absolute value with array."""
        m = Mass(np.array([-100, 200, -300]), 'kg')
        result = abs(m)
        expected = np.array([100, 200, 300])
        assert_array_almost_equal(result.magnitude, expected)


class TestQuantityReverseDivision:
    """Test reverse division (scalar / quantity)."""

    def test_scalar_divided_by_time(self):
        """Test 1 / time = frequency."""
        t = Time(2, 's')
        result = 1 / t
        assert isinstance(result, PintQuantity)
        assert abs(in_units_of(result, 'Hz') - 0.5) < 0.001

    def test_scalar_divided_by_length(self):
        """Test scalar / length."""
        length = Length(4, 'm')
        result = 10 / length
        assert isinstance(result, PintQuantity)
        # Should be 2.5 / m
        assert abs(result.magnitude - 2.5) < 0.001

    def test_scalar_divided_by_mass(self):
        """Test scalar / mass."""
        m = Mass(2, 'kg')
        result = 100 / m
        assert isinstance(result, PintQuantity)
        # Should be 50 / kg
        assert abs(result.magnitude - 50) < 0.001

    def test_rtruediv_with_integer(self):
        """Test integer / quantity."""
        t = Time(4, 's')
        result = 2 / t
        assert abs(in_units_of(result, 'Hz') - 0.5) < 0.001

    def test_rtruediv_invalid_type(self):
        """Test that invalid divisor returns NotImplemented."""
        m = Mass(100, 'kg')
        result = m.__rtruediv__('invalid')
        assert result is NotImplemented


class TestQuantityFloatConversion:
    """Test float conversion."""

    def test_float_scalar(self):
        """Test converting scalar quantity to float."""
        m = Mass(100.5, 'kg')
        result = float(m)
        assert isinstance(result, float)
        assert result == 100.5

    def test_float_single_element_array(self):
        """Test converting single-element array to float."""
        m = Mass(np.array([100.5]), 'kg')
        result = float(m)
        assert isinstance(result, float)
        assert result == 100.5

    def test_float_multi_element_array_raises(self):
        """Test that multi-element array raises TypeError."""
        m = Mass(np.array([100, 200, 300]), 'kg')
        with pytest.raises(TypeError, match="Cannot convert array quantity"):
            float(m)

    def test_float_preserves_magnitude(self):
        """Test that float conversion gives magnitude value."""
        m = Mass(100, 'kg')
        assert float(m) == m.magnitude


class TestQuantityReversePower:
    """Test reverse power (base ** quantity)."""

    def test_rpow_with_non_dimensionless_raises(self):
        """Test base ** quantity raises error for non-dimensionless quantities."""
        from pint.errors import DimensionalityError
        # Time has dimensions, so 2 ** Time should fail
        t = Time(2, 's')
        with pytest.raises(DimensionalityError):
            2 ** t

    def test_rpow_invalid_type(self):
        """Test that invalid base returns NotImplemented."""
        t = Time(2, 's')
        result = t.__rpow__('invalid')
        assert result is NotImplemented


class TestSqrtHelper:
    """Test sqrt() helper function."""

    def test_sqrt_area(self):
        """Test sqrt of area gives length."""
        area = Area(100, 'm^2')
        result = sqrt(area)
        assert isinstance(result, PintQuantity)
        assert abs(in_units_of(result, 'm') - 10) < 0.001

    def test_sqrt_pint_quantity(self):
        """Test sqrt with raw pint Quantity."""
        from evtoltools.common import Q_
        q = Q_(100, 'm^2')
        result = sqrt(q)
        assert isinstance(result, PintQuantity)
        assert abs(result.magnitude - 10) < 0.001

    def test_sqrt_preserves_unit_relationship(self):
        """Test that sqrt(x)^2 ≈ x."""
        area = Area(100, 'm^2')
        root = sqrt(area)
        squared = root ** 2
        assert abs(in_units_of(squared, 'm^2') - 100) < 0.001

    def test_sqrt_array(self):
        """Test sqrt with array quantities."""
        areas = Area(np.array([1, 4, 9, 16, 25]), 'm^2')
        result = sqrt(areas)
        expected = np.array([1, 2, 3, 4, 5])
        assert_array_almost_equal(result.magnitude, expected)

    def test_sqrt_invalid_type(self):
        """Test sqrt with invalid input raises TypeError."""
        with pytest.raises(TypeError, match="Expected"):
            sqrt("not a quantity")

    def test_sqrt_invalid_numeric(self):
        """Test sqrt with plain numeric raises TypeError."""
        with pytest.raises(TypeError, match="Expected"):
            sqrt(100)


class TestIntegrationPhysicsFormulas:
    """Integration tests for real physics formulas using quantity operations."""

    def test_hover_power_formula(self):
        """Test P = T^1.5 / sqrt(2*rho*A) with quantities.

        This is the ideal hover power formula from momentum theory.
        """
        thrust = Force(5000, 'N')
        density = Density(1.225, 'kg/m^3')
        disk_area = Area(10, 'm^2')

        # New approach with quantity operations
        power_pint = thrust ** 1.5 / sqrt(2 * density * disk_area)
        power = Power(power_pint.to('W'))

        # Calculate expected value manually
        T = 5000
        rho = 1.225
        A = 10
        expected = T ** 1.5 / np.sqrt(2 * rho * A)

        assert abs(power.in_units_of('W') - expected) < 1

    def test_induced_velocity_formula(self):
        """Test v_i = sqrt(T / (2*rho*A)) with quantities.

        This is the induced velocity formula from momentum theory.
        """
        thrust = Force(5000, 'N')
        density = Density(1.225, 'kg/m^3')
        disk_area = Area(10, 'm^2')

        # New approach
        v_pint = sqrt(thrust / (2 * density * disk_area))
        velocity = Velocity(v_pint.to('m/s'))

        # Expected
        expected = np.sqrt(5000 / (2 * 1.225 * 10))

        assert abs(velocity.in_units_of('m/s') - expected) < 0.001

    def test_frequency_from_period(self):
        """Test f = 1/T with quantities."""
        period = Time(0.5, 's')
        freq_pint = 1 / period
        freq = Frequency(freq_pint.to('Hz'))

        assert abs(freq.in_units_of('Hz') - 2) < 0.001

    def test_tip_speed_formula(self):
        """Test v_tip = omega * r with quantities."""
        omega = AngularVelocity(100, 'rad/s')
        radius = Length(0.5, 'm')

        v_tip_pint = omega * radius
        velocity = Velocity(v_tip_pint.to('m/s'))

        assert abs(velocity.in_units_of('m/s') - 50) < 0.001

    def test_disk_loading(self):
        """Test disk loading = thrust / area."""
        thrust = Force(10000, 'N')
        disk_area = Area(20, 'm^2')

        # This gives a pressure-like quantity
        dl = thrust / disk_area

        assert abs(in_units_of(dl, 'N/m^2') - 500) < 0.001

    def test_power_loading(self):
        """Test power loading = power / mass."""
        power = Power(100000, 'W')
        mass = Mass(2000, 'kg')

        # Specific power
        specific_power = power / mass

        assert abs(in_units_of(specific_power, 'W/kg') - 50) < 0.001


class TestQuantityOperationsChaining:
    """Test chaining multiple operations together."""

    def test_chain_arithmetic(self):
        """Test chaining add, sub, mul, div."""
        m1 = Mass(100, 'kg')
        m2 = Mass(50, 'kg')
        m3 = Mass(25, 'kg')

        result = (m1 + m2 - m3) * 2 / 2
        assert isinstance(result, Mass)
        assert result.magnitude == 125

    def test_chain_with_negation(self):
        """Test chaining with negation."""
        m = Mass(100, 'kg')
        result = abs(-m * 2)
        assert isinstance(result, Mass)
        assert result.magnitude == 200

    def test_complex_formula(self):
        """Test a complex formula with multiple operations."""
        # Kinetic energy: KE = 0.5 * m * v^2
        mass = Mass(100, 'kg')
        velocity = Velocity(10, 'm/s')

        v_squared = velocity ** 2
        ke_pint = 0.5 * mass * v_squared

        # KE = 0.5 * 100 * 100 = 5000 J
        assert abs(in_units_of(ke_pint, 'J') - 5000) < 0.001


class TestQuantityOperationsWithDifferentUnits:
    """Test operations maintain correct unit handling."""

    def test_power_different_units(self):
        """Test exponentiation with different input units."""
        area_ft = Area(100, 'ft^2')
        result = area_ft ** 0.5

        # Result should be in feet
        assert abs(in_units_of(result, 'ft') - 10) < 0.001

    def test_sqrt_different_units(self):
        """Test sqrt with different input units."""
        area_in = Area(144, 'in^2')  # 12^2
        result = sqrt(area_in)

        assert abs(in_units_of(result, 'in') - 12) < 0.001

    def test_cross_unit_multiplication_then_power(self):
        """Test multiplying different unit quantities then power."""
        length1 = Length(3, 'm')
        length2 = Length(4, 'm')

        area = length1 * length2
        side = area ** 0.5

        # sqrt(12) ≈ 3.464
        assert abs(in_units_of(side, 'm') - np.sqrt(12)) < 0.001
