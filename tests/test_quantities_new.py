"""Tests for new quantity types: Voltage, Energy, Capacity."""

import pytest
import numpy as np

from evtoltools.common import Voltage, Energy, Capacity


class TestVoltageConstruction:
    """Tests for Voltage quantity construction."""

    def test_default_unit(self):
        v = Voltage(12)
        assert v.units == 'volt'
        assert v.magnitude == 12

    def test_explicit_unit_v(self):
        v = Voltage(3.7, 'V')
        assert v.magnitude == 3.7

    def test_explicit_unit_mv(self):
        v = Voltage(3700, 'mV')
        assert v.magnitude == 3700

    def test_explicit_unit_kv(self):
        v = Voltage(1.5, 'kV')
        assert v.magnitude == 1.5

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Voltage(12, 'W')  # Wrong unit type


class TestVoltageConversion:
    """Tests for Voltage unit conversion."""

    def test_v_to_mv(self):
        v = Voltage(3.7, 'V')
        v_mv = v.to('mV')
        assert abs(v_mv.magnitude - 3700) < 0.01

    def test_mv_to_v(self):
        v = Voltage(3700, 'mV')
        v_v = v.to('V')
        assert abs(v_v.magnitude - 3.7) < 0.001

    def test_v_to_kv(self):
        v = Voltage(1500, 'V')
        v_kv = v.to('kV')
        assert abs(v_kv.magnitude - 1.5) < 0.001


class TestVoltageArithmetic:
    """Tests for Voltage arithmetic operations."""

    def test_addition(self):
        v1 = Voltage(3.7, 'V')
        v2 = Voltage(3.7, 'V')
        result = v1 + v2
        assert abs(result.magnitude - 7.4) < 0.001

    def test_scalar_multiplication(self):
        v = Voltage(3.7, 'V')
        result = v * 10  # 10 cells in series
        assert abs(result.magnitude - 37) < 0.001

    def test_subtraction(self):
        v1 = Voltage(4.2, 'V')
        v2 = Voltage(2.8, 'V')
        result = v1 - v2
        assert abs(result.magnitude - 1.4) < 0.001


class TestEnergyConstruction:
    """Tests for Energy quantity construction."""

    def test_default_unit(self):
        e = Energy(1000)
        assert e.units == 'joule'

    def test_explicit_unit_j(self):
        e = Energy(3600, 'J')
        assert e.magnitude == 3600

    def test_explicit_unit_wh(self):
        e = Energy(100, 'Wh')
        assert e.magnitude == 100

    def test_explicit_unit_kwh(self):
        e = Energy(50, 'kWh')
        assert e.magnitude == 50

    def test_explicit_unit_mj(self):
        e = Energy(1, 'MJ')
        assert e.magnitude == 1

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Energy(100, 'V')


class TestEnergyConversion:
    """Tests for Energy unit conversion."""

    def test_j_to_wh(self):
        e = Energy(3600, 'J')
        e_wh = e.to('Wh')
        assert abs(e_wh.magnitude - 1) < 0.001

    def test_wh_to_kwh(self):
        e = Energy(1000, 'Wh')
        e_kwh = e.to('kWh')
        assert abs(e_kwh.magnitude - 1) < 0.001

    def test_kwh_to_j(self):
        e = Energy(1, 'kWh')
        e_j = e.to('J')
        assert abs(e_j.magnitude - 3600000) < 1

    def test_kwh_to_mj(self):
        e = Energy(1, 'kWh')
        e_mj = e.to('MJ')
        assert abs(e_mj.magnitude - 3.6) < 0.001

    def test_mwh_to_wh(self):
        e = Energy(100, 'mWh')
        e_wh = e.to('Wh')
        assert abs(e_wh.magnitude - 0.1) < 0.001


class TestEnergyArithmetic:
    """Tests for Energy arithmetic operations."""

    def test_addition(self):
        e1 = Energy(50, 'kWh')
        e2 = Energy(25, 'kWh')
        result = e1 + e2
        assert abs(result.magnitude - 75) < 0.001

    def test_addition_different_units(self):
        e1 = Energy(1, 'kWh')
        e2 = Energy(500, 'Wh')
        result = e1 + e2
        # Result should be in first operand's units (kWh)
        assert abs(result.in_units_of('kWh') - 1.5) < 0.001


class TestCapacityConstruction:
    """Tests for Capacity (electric charge) quantity construction."""

    def test_default_unit(self):
        c = Capacity(5)
        assert c.units == 'ampere_hour'

    def test_explicit_unit_ah(self):
        c = Capacity(5, 'Ah')
        assert c.magnitude == 5

    def test_explicit_unit_mah(self):
        c = Capacity(5000, 'mAh')
        assert c.magnitude == 5000

    def test_explicit_unit_coulombs(self):
        c = Capacity(3600, 'C')
        assert c.magnitude == 3600

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="wrong dimensionality"):
            Capacity(5, 'V')


class TestCapacityConversion:
    """Tests for Capacity unit conversion."""

    def test_mah_to_ah(self):
        c = Capacity(5000, 'mAh')
        c_ah = c.to('Ah')
        assert abs(c_ah.magnitude - 5) < 0.001

    def test_ah_to_mah(self):
        c = Capacity(5, 'Ah')
        c_mah = c.to('mAh')
        assert abs(c_mah.magnitude - 5000) < 0.1

    def test_ah_to_coulombs(self):
        c = Capacity(1, 'Ah')
        c_c = c.to('C')
        assert abs(c_c.magnitude - 3600) < 0.1


class TestCapacityArithmetic:
    """Tests for Capacity arithmetic operations."""

    def test_addition(self):
        c1 = Capacity(5, 'Ah')
        c2 = Capacity(5, 'Ah')
        result = c1 + c2
        assert abs(result.magnitude - 10) < 0.001

    def test_scalar_multiplication(self):
        c = Capacity(5, 'Ah')
        result = c * 4  # 4 cells in parallel
        assert abs(result.magnitude - 20) < 0.001


class TestQuantityArraySupport:
    """Tests for array support in new quantities."""

    def test_voltage_array(self):
        voltages = Voltage(np.array([3.7, 4.0, 4.2]), 'V')
        assert len(voltages.magnitude) == 3
        converted = voltages.to('mV')
        assert abs(converted.magnitude[0] - 3700) < 0.1

    def test_energy_array(self):
        energies = Energy(np.array([10, 20, 30]), 'kWh')
        assert len(energies.magnitude) == 3
        converted = energies.to('Wh')
        assert abs(converted.magnitude[0] - 10000) < 1

    def test_capacity_array(self):
        capacities = Capacity(np.array([5000, 6000, 7000]), 'mAh')
        assert len(capacities.magnitude) == 3
        converted = capacities.to('Ah')
        assert abs(converted.magnitude[0] - 5) < 0.001
