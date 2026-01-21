"""Unit tests for the BaseQuantity abstract class.

These tests use Mass as a concrete implementation to test the base functionality.
"""

import pytest
import numpy as np
from evtoltools.common import Mass
from evtoltools.common.base import BaseQuantity


class TestBaseQuantityAbstract:
    """Test that BaseQuantity is properly abstract."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseQuantity cannot be instantiated directly."""
        with pytest.raises((TypeError, NotImplementedError)):
            BaseQuantity(100, 'kg')

    def test_subclass_must_define_quantity_type(self):
        """Test that subclasses must define _quantity_type."""

        class IncompleteQuantity(BaseQuantity):
            pass

        with pytest.raises(NotImplementedError):
            IncompleteQuantity(100)


class TestBaseQuantityValidation:
    """Test validation logic in BaseQuantity."""

    def test_unit_validation(self):
        """Test that invalid units are caught."""
        with pytest.raises(ValueError, match="not recognized"):
            Mass(100, 'invalid_unit')

    def test_dimensionality_validation(self):
        """Test that dimensionality is validated (indirectly through Mass)."""
        # Mass should accept mass units
        m = Mass(100, 'kg')
        assert m.magnitude == 100

        # But not length units
        with pytest.raises(ValueError):
            Mass(100, 'm')


class TestBaseQuantityConversion:
    """Test conversion methods in BaseQuantity."""

    def test_to_method_returns_same_type(self):
        """Test that to() returns instance of same type."""
        m = Mass(100, 'kg')
        m_lbs = m.to('lbs')
        assert isinstance(m_lbs, Mass)
        assert type(m_lbs) == type(m)

    def test_to_creates_new_instance(self):
        """Test that to() creates a new instance (immutability)."""
        m1 = Mass(100, 'kg')
        m2 = m1.to('lbs')
        assert m1 is not m2
        assert m1.units != m2.units

    def test_to_default_uses_config(self):
        """Test that to_default() uses configured default unit."""
        m = Mass(100, 'lbs')
        m_default = m.to_default()
        # Default for mass should be kg
        assert 'kg' in m_default.units or 'kilogram' in m_default.units

    def test_in_units_of_returns_magnitude(self):
        """Test that in_units_of() returns numeric value, not instance."""
        m = Mass(100, 'kg')
        value = m.in_units_of('lbs')
        assert isinstance(value, (float, np.floating, np.ndarray))
        assert not isinstance(value, Mass)


class TestBaseQuantityArithmetic:
    """Test arithmetic operations defined in BaseQuantity."""

    def test_operations_return_new_instances(self):
        """Test that arithmetic operations don't modify original."""
        m1 = Mass(100, 'kg')
        m2 = Mass(50, 'kg')
        original_m1_value = m1.magnitude

        m3 = m1 + m2

        # Original should be unchanged
        assert m1.magnitude == original_m1_value
        # Result should be new instance
        assert m3 is not m1
        assert m3 is not m2

    def test_mixed_type_operations(self):
        """Test operations between BaseQuantity and pint Quantity."""
        from evtoltools.common import Q_

        m = Mass(100, 'kg')
        q = Q_(50, 'kg')

        result = m + q
        assert isinstance(result, Mass)
        assert result.magnitude == 150

    def test_division_by_same_type_returns_dimensionless(self):
        """Test that dividing quantities returns dimensionless pint Quantity."""
        m1 = Mass(200, 'kg')
        m2 = Mass(100, 'kg')

        ratio = m1 / m2
        # Should return pint Quantity, not Mass
        from pint import Quantity as PintQuantity
        assert isinstance(ratio, PintQuantity)
        assert not isinstance(ratio, Mass)
        assert abs(ratio.magnitude - 2.0) < 0.001


class TestBaseQuantityComparison:
    """Test comparison operations defined in BaseQuantity."""

    def test_comparison_with_different_units(self):
        """Test that comparisons work across units."""
        m1 = Mass(1, 'kg')
        m2 = Mass(1, 'lbs')
        # 1 kg > 1 lbs
        assert m1 > m2

    def test_equality_with_tolerance(self):
        """Test equality comparison."""
        m1 = Mass(100.0, 'kg')
        m2 = Mass(100.0, 'kg')
        assert m1 == m2

    def test_array_comparisons_return_arrays(self):
        """Test that array comparisons return boolean arrays."""
        m1 = Mass(np.array([100, 200, 300]), 'kg')
        m2 = Mass(150, 'kg')

        result = m1 > m2
        assert isinstance(result, np.ndarray)
        assert result.dtype == bool
        assert result.shape == (3,)


class TestBaseQuantityProperties:
    """Test properties defined in BaseQuantity."""

    def test_magnitude_property(self):
        """Test magnitude property."""
        m = Mass(123.456, 'kg')
        assert m.magnitude == 123.456

    def test_value_alias(self):
        """Test that value is alias for magnitude."""
        m = Mass(100, 'kg')
        assert m.value == m.magnitude

    def test_units_property(self):
        """Test units property returns string."""
        m = Mass(100, 'kg')
        assert isinstance(m.units, str)
        assert 'kg' in m.units or 'kilogram' in m.units

    def test_properties_with_arrays(self):
        """Test properties work with array values."""
        values = np.array([1, 2, 3])
        m = Mass(values, 'kg')
        assert isinstance(m.magnitude, np.ndarray)
        assert np.array_equal(m.magnitude, values)


class TestBaseQuantityRepresentation:
    """Test representation methods defined in BaseQuantity."""

    def test_repr_contains_class_name(self):
        """Test __repr__ contains class name."""
        m = Mass(100, 'kg')
        assert 'Mass' in repr(m)

    def test_repr_contains_value(self):
        """Test __repr__ contains value."""
        m = Mass(123.456, 'kg')
        assert '123.456' in repr(m)

    def test_str_is_readable(self):
        """Test __str__ produces readable output."""
        m = Mass(100, 'kg')
        s = str(m)
        assert '100' in s
        # Should contain some form of unit
        assert 'kg' in s or 'kilogram' in s

    def test_format_with_spec(self):
        """Test __format__ with format specification."""
        m = Mass(1234.5678, 'kg')
        formatted = f"{m:.2f}"
        assert '1234.57' in formatted

    def test_repr_with_array(self):
        """Test __repr__ with array values."""
        m = Mass(np.array([1, 2, 3]), 'kg')
        repr_str = repr(m)
        assert 'Mass' in repr_str
        assert 'array' in repr_str or '[1' in repr_str


class TestBaseQuantityImmutability:
    """Test that quantities are immutable."""

    def test_operations_dont_modify_original(self):
        """Test that operations create new instances."""
        m1 = Mass(100, 'kg')
        m1_original_mag = m1.magnitude
        m1_original_units = m1.units

        # Perform various operations
        m2 = m1 + Mass(50, 'kg')
        m3 = m1 * 2
        m4 = m1.to('lbs')

        # Verify original is unchanged
        assert m1.magnitude == m1_original_mag
        assert m1.units == m1_original_units

    def test_conversion_creates_new_instance(self):
        """Test that unit conversion creates new instance."""
        m1 = Mass(100, 'kg')
        m2 = m1.to('lbs')

        # Different instances
        assert m1 is not m2
        # Different units
        assert m1.units != m2.units


class TestBaseQuantityArraySupport:
    """Test numpy array support in BaseQuantity."""

    def test_array_magnitude_type(self):
        """Test that array input preserves array type."""
        values = np.array([1.0, 2.0, 3.0])
        m = Mass(values, 'kg')
        assert isinstance(m.magnitude, np.ndarray)

    def test_scalar_magnitude_type(self):
        """Test that scalar input has scalar magnitude."""
        m = Mass(100, 'kg')
        # Magnitude should be numeric (could be float or numpy scalar)
        assert isinstance(m.magnitude, (int, float, np.number))

    def test_array_broadcasting_in_operations(self):
        """Test that broadcasting works in array operations."""
        m_array = Mass(np.array([100, 200, 300]), 'kg')
        m_scalar = Mass(10, 'kg')

        # Array + scalar should broadcast
        result = m_array + m_scalar
        expected = np.array([110, 210, 310])
        np.testing.assert_array_almost_equal(result.magnitude, expected)

        # Scalar + array should also work
        result2 = m_scalar + m_array
        np.testing.assert_array_almost_equal(result2.magnitude, expected)

    def test_element_wise_array_operations(self):
        """Test element-wise operations on arrays."""
        m1 = Mass(np.array([100, 200, 300]), 'kg')
        m2 = Mass(np.array([10, 20, 30]), 'kg')

        result = m1 + m2
        expected = np.array([110, 220, 330])
        np.testing.assert_array_almost_equal(result.magnitude, expected)


class TestEquivalentUnitStrings:
    """Test that equivalent unit strings are accepted."""

    def test_pressure_n_per_m2(self):
        """Pressure accepts N/m^2 as equivalent to Pa."""
        from evtoltools.common import Pressure
        p = Pressure(1, 'N/m^2')
        assert abs(p.in_units_of('Pa') - 1.0) < 0.001

    def test_pressure_convert_to_n_per_m2(self):
        """Pressure can convert to N/m^2."""
        from evtoltools.common import Pressure
        p = Pressure(1, 'Pa')
        p2 = p.to('N/m^2')
        assert abs(p2.magnitude - 1.0) < 0.001

    def test_force_kg_m_per_s2(self):
        """Force accepts kg*m/s^2 as equivalent to N."""
        from evtoltools.common import Force
        f = Force(10, 'kg*m/s^2')
        assert abs(f.in_units_of('N') - 10.0) < 0.001

    def test_velocity_equivalent_forms(self):
        """Velocity accepts equivalent unit forms."""
        from evtoltools.common import Velocity
        v = Velocity(10, 'm*s^-1')
        assert abs(v.in_units_of('m/s') - 10.0) < 0.001

    def test_wrong_dimensionality_rejected(self):
        """Wrong dimensionality is still rejected."""
        from evtoltools.common import Pressure
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Pressure(1, 'kg')

    def test_unknown_unit_rejected(self):
        """Unknown units are still rejected."""
        from evtoltools.common import Pressure
        with pytest.raises(ValueError, match="not recognized"):
            Pressure(1, 'foobar')


class TestInUnitsOfHelper:
    """Test the in_units_of helper function."""

    def test_with_base_quantity(self):
        """in_units_of works with BaseQuantity instances."""
        from evtoltools.common import in_units_of
        m = Mass(1, 'kg')
        assert abs(in_units_of(m, 'g') - 1000) < 0.01

    def test_with_pint_quantity_multiplication(self):
        """in_units_of works with multiplication results."""
        from evtoltools.common import Area, in_units_of
        area = Area(10, 'm^2')
        mass = Mass(5, 'kg')
        result = area * mass
        assert abs(in_units_of(result, 'kg*m^2') - 50.0) < 0.01

    def test_with_pint_quantity_division(self):
        """in_units_of works with division results."""
        from evtoltools.common import Force, Area, in_units_of
        force = Force(100, 'N')
        area = Area(2, 'm^2')
        result = force / area
        assert abs(in_units_of(result, 'Pa') - 50.0) < 0.01

    def test_type_error_for_invalid_input(self):
        """in_units_of raises TypeError for invalid input."""
        from evtoltools.common import in_units_of
        with pytest.raises(TypeError, match="Expected BaseQuantity or pint Quantity"):
            in_units_of(123, 'kg')

    def test_with_array_quantity(self):
        """in_units_of works with array quantities."""
        from evtoltools.common import in_units_of
        m = Mass(np.array([1, 2, 3]), 'kg')
        result = in_units_of(m, 'g')
        np.testing.assert_array_almost_equal(result, np.array([1000, 2000, 3000]))
