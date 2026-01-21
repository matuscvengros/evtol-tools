"""Tests for Pressure and Frequency quantity types."""

import pytest
import numpy as np

from evtoltools.common import Pressure, Frequency


class TestPressureConstruction:
    """Tests for Pressure construction."""

    def test_default_unit(self):
        """Pressure should default to Pa."""
        pressure = Pressure(101325)
        assert pressure.units == 'pascal'
        assert pressure.magnitude == 101325

    def test_explicit_unit_pa(self):
        """Pressure can be created with explicit Pa."""
        pressure = Pressure(101325, 'Pa')
        assert pressure.magnitude == 101325

    def test_explicit_unit_kpa(self):
        """Pressure can be created in kPa."""
        pressure = Pressure(101.325, 'kPa')
        assert abs(pressure.in_units_of('Pa') - 101325) < 1

    def test_explicit_unit_bar(self):
        """Pressure can be created in bar."""
        pressure = Pressure(1, 'bar')
        assert abs(pressure.in_units_of('Pa') - 100000) < 1

    def test_explicit_unit_psi(self):
        """Pressure can be created in psi."""
        pressure = Pressure(14.696, 'psi')
        # 14.696 psi ≈ 101325 Pa (1 atm)
        assert abs(pressure.in_units_of('Pa') - 101325) < 100

    def test_explicit_unit_atm(self):
        """Pressure can be created in atm."""
        pressure = Pressure(1, 'atm')
        assert abs(pressure.in_units_of('Pa') - 101325) < 1

    def test_invalid_unit(self):
        """Invalid unit should raise ValueError."""
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Pressure(100, 'kg')


class TestPressureConversion:
    """Tests for Pressure unit conversions."""

    def test_pa_to_kpa(self):
        """Convert Pa to kPa."""
        pressure = Pressure(100000, 'Pa')
        pressure_kpa = pressure.to('kPa')
        assert abs(pressure_kpa.magnitude - 100) < 0.001

    def test_atm_to_pa(self):
        """Convert atm to Pa."""
        pressure = Pressure(1, 'atm')
        pressure_pa = pressure.to('Pa')
        assert abs(pressure_pa.magnitude - 101325) < 1

    def test_bar_to_psi(self):
        """Convert bar to psi."""
        pressure = Pressure(1, 'bar')
        pressure_psi = pressure.to('psi')
        # 1 bar ≈ 14.5038 psi
        assert abs(pressure_psi.magnitude - 14.5038) < 0.01


class TestPressureArithmetic:
    """Tests for Pressure arithmetic operations."""

    def test_addition_same_units(self):
        """Add two pressures in same units."""
        p1 = Pressure(100000, 'Pa')
        p2 = Pressure(50000, 'Pa')
        result = p1 + p2
        assert isinstance(result, Pressure)
        assert abs(result.in_units_of('Pa') - 150000) < 1

    def test_addition_different_units(self):
        """Add pressures in different units."""
        p1 = Pressure(100, 'kPa')
        p2 = Pressure(50000, 'Pa')
        result = p1 + p2
        assert isinstance(result, Pressure)
        assert abs(result.in_units_of('Pa') - 150000) < 1

    def test_scalar_multiplication(self):
        """Multiply pressure by scalar."""
        pressure = Pressure(100, 'kPa')
        result = pressure * 2
        assert isinstance(result, Pressure)
        assert abs(result.in_units_of('kPa') - 200) < 0.001

    def test_scalar_division(self):
        """Divide pressure by scalar."""
        pressure = Pressure(200, 'kPa')
        result = pressure / 2
        assert isinstance(result, Pressure)
        assert abs(result.in_units_of('kPa') - 100) < 0.001


class TestPressureComparison:
    """Tests for Pressure comparison operations."""

    def test_equality(self):
        """Test equality comparison."""
        p1 = Pressure(100, 'kPa')
        p2 = Pressure(100000, 'Pa')
        assert p1 == p2

    def test_less_than(self):
        """Test less than comparison."""
        p1 = Pressure(1, 'bar')
        p2 = Pressure(2, 'bar')
        assert p1 < p2

    def test_greater_than(self):
        """Test greater than comparison."""
        p1 = Pressure(1, 'atm')
        p2 = Pressure(0.5, 'atm')
        assert p1 > p2


class TestPressureArray:
    """Tests for Pressure with numpy arrays."""

    def test_array_construction(self):
        """Pressure can be created with numpy array."""
        pressures = Pressure(np.array([100, 200, 300]), 'kPa')
        assert len(pressures.magnitude) == 3
        assert pressures.magnitude[1] == 200

    def test_array_conversion(self):
        """Array pressure can be converted."""
        pressures = Pressure(np.array([100, 200, 300]), 'kPa')
        pressures_pa = pressures.to('Pa')
        assert pressures_pa.magnitude[0] == 100000
        assert pressures_pa.magnitude[2] == 300000


class TestFrequencyConstruction:
    """Tests for Frequency construction."""

    def test_default_unit(self):
        """Frequency should default to Hz."""
        freq = Frequency(50)
        assert freq.units == 'hertz'
        assert freq.magnitude == 50

    def test_explicit_unit_hz(self):
        """Frequency can be created with explicit Hz."""
        freq = Frequency(60, 'Hz')
        assert freq.magnitude == 60

    def test_explicit_unit_khz(self):
        """Frequency can be created in kHz."""
        freq = Frequency(1, 'kHz')
        assert abs(freq.in_units_of('Hz') - 1000) < 0.01

    def test_explicit_unit_mhz(self):
        """Frequency can be created in MHz."""
        freq = Frequency(2.4, 'MHz')
        assert abs(freq.in_units_of('Hz') - 2400000) < 1

    def test_explicit_unit_mhz_lowercase(self):
        """Frequency can be created in mHz (millihertz)."""
        freq = Frequency(1000, 'mHz')
        assert abs(freq.in_units_of('Hz') - 1) < 0.001

    def test_invalid_unit(self):
        """Invalid unit should raise ValueError."""
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Frequency(100, 'kg')


class TestFrequencyConversion:
    """Tests for Frequency unit conversions."""

    def test_hz_to_khz(self):
        """Convert Hz to kHz."""
        freq = Frequency(1000, 'Hz')
        freq_khz = freq.to('kHz')
        assert abs(freq_khz.magnitude - 1) < 0.001

    def test_khz_to_mhz(self):
        """Convert kHz to MHz."""
        freq = Frequency(1000, 'kHz')
        freq_mhz = freq.to('MHz')
        assert abs(freq_mhz.magnitude - 1) < 0.001

    def test_hz_to_mhz_millihertz(self):
        """Convert Hz to mHz (millihertz)."""
        freq = Frequency(0.5, 'Hz')
        freq_mhz = freq.to('mHz')
        assert abs(freq_mhz.magnitude - 500) < 0.1


class TestFrequencyArithmetic:
    """Tests for Frequency arithmetic operations."""

    def test_addition_same_units(self):
        """Add two frequencies in same units."""
        f1 = Frequency(100, 'Hz')
        f2 = Frequency(50, 'Hz')
        result = f1 + f2
        assert isinstance(result, Frequency)
        assert abs(result.in_units_of('Hz') - 150) < 0.01

    def test_addition_different_units(self):
        """Add frequencies in different units."""
        f1 = Frequency(1, 'kHz')
        f2 = Frequency(500, 'Hz')
        result = f1 + f2
        assert isinstance(result, Frequency)
        assert abs(result.in_units_of('Hz') - 1500) < 0.1

    def test_scalar_multiplication(self):
        """Multiply frequency by scalar."""
        freq = Frequency(100, 'Hz')
        result = freq * 3
        assert isinstance(result, Frequency)
        assert abs(result.in_units_of('Hz') - 300) < 0.01

    def test_scalar_division(self):
        """Divide frequency by scalar."""
        freq = Frequency(300, 'Hz')
        result = freq / 3
        assert isinstance(result, Frequency)
        assert abs(result.in_units_of('Hz') - 100) < 0.01


class TestFrequencyComparison:
    """Tests for Frequency comparison operations."""

    def test_equality(self):
        """Test equality comparison."""
        f1 = Frequency(1, 'kHz')
        f2 = Frequency(1000, 'Hz')
        assert f1 == f2

    def test_less_than(self):
        """Test less than comparison."""
        f1 = Frequency(50, 'Hz')
        f2 = Frequency(60, 'Hz')
        assert f1 < f2

    def test_greater_than(self):
        """Test greater than comparison."""
        f1 = Frequency(1, 'MHz')
        f2 = Frequency(500, 'kHz')
        assert f1 > f2


class TestFrequencyArray:
    """Tests for Frequency with numpy arrays."""

    def test_array_construction(self):
        """Frequency can be created with numpy array."""
        frequencies = Frequency(np.array([50, 60, 100]), 'Hz')
        assert len(frequencies.magnitude) == 3
        assert frequencies.magnitude[1] == 60

    def test_array_conversion(self):
        """Array frequency can be converted."""
        frequencies = Frequency(np.array([1000, 2000, 3000]), 'Hz')
        frequencies_khz = frequencies.to('kHz')
        assert frequencies_khz.magnitude[0] == 1
        assert frequencies_khz.magnitude[2] == 3


class TestFrequencyRepr:
    """Tests for Frequency representation."""

    def test_repr(self):
        """Test string representation."""
        freq = Frequency(440, 'Hz')
        repr_str = repr(freq)
        assert 'Frequency' in repr_str
        assert '440' in repr_str

    def test_str(self):
        """Test string conversion."""
        freq = Frequency(440, 'Hz')
        str_repr = str(freq)
        assert '440' in str_repr
        assert 'hertz' in str_repr


class TestPressureRepr:
    """Tests for Pressure representation."""

    def test_repr(self):
        """Test string representation."""
        pressure = Pressure(101325, 'Pa')
        repr_str = repr(pressure)
        assert 'Pressure' in repr_str
        assert '101325' in repr_str

    def test_str(self):
        """Test string conversion."""
        pressure = Pressure(101325, 'Pa')
        str_repr = str(pressure)
        assert '101325' in str_repr
        assert 'pascal' in str_repr
