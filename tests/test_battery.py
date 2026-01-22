"""Tests for Battery chemistry and Battery component.

This module provides comprehensive tests for battery chemistry configurations
and the Battery component class, including construction, factory methods,
voltage/capacity/energy calculations, and current/power limits.

Test Classes:
    TestBatteryChemistryDefinitions: Tests for predefined battery chemistries.
    TestBatteryChemistryMethods: Tests for BatteryChemistry methods.
    TestGetChemistry: Tests for chemistry registry lookup.
    TestBatteryConstruction: Tests for Battery construction.
    TestBatteryVoltageProperties: Tests for Battery voltage calculations.
    TestBatteryCapacityProperties: Tests for Battery capacity calculations.
    TestBatteryEnergyProperties: Tests for Battery energy calculations.
    TestBatteryCurrentLimits: Tests for Battery current limit calculations.
    TestBatteryPowerLimits: Tests for Battery power limit calculations.
    TestBatteryMass: Tests for Battery mass calculations.
    TestBatteryFromTargetVoltage: Tests for Battery.from_target_voltage factory.
    TestBatteryFromTargetEnergy: Tests for Battery.from_target_energy factory.
    TestBatteryProperties: Tests for Battery properties and repr.
"""

import math

import pytest

from evtoltools.common import Capacity, Current, Energy, Mass, Power, Resistance, Temperature, Voltage
from evtoltools.components import (
    LITHIUM_ION,
    LITHIUM_IRON_PHOSPHATE,
    LITHIUM_NMC,
    LITHIUM_POLYMER,
    Battery,
    BatteryChemistry,
    get_chemistry,
)
from evtoltools.components.battery import (
    AnalyticalDischargeModel,
    LookupTableDischargeModel,
    SimpleChargeModel,
)


class TestBatteryChemistryDefinitions:
    """Tests for predefined battery chemistries."""

    def test_lithium_ion_exists(self):
        assert LITHIUM_ION is not None
        assert LITHIUM_ION.name == 'lithium_ion'

    def test_lithium_ion_voltages(self):
        assert LITHIUM_ION.nominal_cell_voltage.in_units_of('V') == 3.7
        assert LITHIUM_ION.max_cell_voltage.in_units_of('V') == 4.2
        assert LITHIUM_ION.min_cell_voltage.in_units_of('V') == 2.8

    def test_lithium_polymer_exists(self):
        assert LITHIUM_POLYMER is not None
        assert LITHIUM_POLYMER.name == 'lithium_polymer'

    def test_lithium_polymer_higher_min_voltage(self):
        # LiPo has higher minimum voltage than Li-ion
        lipo_min = LITHIUM_POLYMER.min_cell_voltage.in_units_of('V')
        lion_min = LITHIUM_ION.min_cell_voltage.in_units_of('V')
        assert lipo_min > lion_min

    def test_lifepo4_exists(self):
        assert LITHIUM_IRON_PHOSPHATE is not None
        assert LITHIUM_IRON_PHOSPHATE.name == 'lithium_iron_phosphate'

    def test_lifepo4_lower_nominal_voltage(self):
        # LiFePO4 has lower nominal voltage (3.2V vs 3.7V)
        lfp_nom = LITHIUM_IRON_PHOSPHATE.nominal_cell_voltage.in_units_of('V')
        lion_nom = LITHIUM_ION.nominal_cell_voltage.in_units_of('V')
        assert lfp_nom < lion_nom

    def test_nmc_exists(self):
        assert LITHIUM_NMC is not None
        assert LITHIUM_NMC.name == 'lithium_nmc'


class TestBatteryChemistryMethods:
    """Tests for BatteryChemistry methods."""

    def test_voltage_range(self):
        # Li-ion: 4.2V - 2.8V = 1.4V
        range_v = LITHIUM_ION.voltage_range.in_units_of('V')
        assert abs(range_v - 1.4) < 0.001

    def test_validate_voltage_valid(self):
        is_valid, msg = LITHIUM_ION.validate_voltage(Voltage(3.8, 'V'))
        assert is_valid is True
        assert "within safe range" in msg

    def test_validate_voltage_too_high(self):
        is_valid, msg = LITHIUM_ION.validate_voltage(Voltage(4.5, 'V'))
        assert is_valid is False
        assert "exceeds max" in msg

    def test_validate_voltage_too_low(self):
        is_valid, msg = LITHIUM_ION.validate_voltage(Voltage(2.5, 'V'))
        assert is_valid is False
        assert "below min" in msg

    def test_chemistry_is_frozen(self):
        with pytest.raises(Exception):  # FrozenInstanceError
            LITHIUM_ION.name = 'modified'


class TestGetChemistry:
    """Tests for chemistry registry lookup."""

    def test_get_lithium_ion_full_name(self):
        chem = get_chemistry('lithium_ion')
        assert chem == LITHIUM_ION

    def test_get_lithium_ion_alias_li_ion(self):
        chem = get_chemistry('li_ion')
        assert chem == LITHIUM_ION

    def test_get_lithium_ion_alias_lion(self):
        chem = get_chemistry('lion')
        assert chem == LITHIUM_ION

    def test_get_lipo_full_name(self):
        chem = get_chemistry('lithium_polymer')
        assert chem == LITHIUM_POLYMER

    def test_get_lipo_alias(self):
        chem = get_chemistry('lipo')
        assert chem == LITHIUM_POLYMER

    def test_get_lifepo4_alias(self):
        chem = get_chemistry('lifepo4')
        assert chem == LITHIUM_IRON_PHOSPHATE

    def test_get_lfp_alias(self):
        chem = get_chemistry('lfp')
        assert chem == LITHIUM_IRON_PHOSPHATE

    def test_get_nmc_alias(self):
        chem = get_chemistry('nmc')
        assert chem == LITHIUM_NMC

    def test_case_insensitive(self):
        chem = get_chemistry('LITHIUM_ION')
        assert chem == LITHIUM_ION

    def test_handles_dashes(self):
        chem = get_chemistry('lithium-ion')
        assert chem == LITHIUM_ION

    def test_invalid_chemistry_raises(self):
        with pytest.raises(ValueError, match="Unknown chemistry"):
            get_chemistry('made_up_chemistry')


class TestBatteryConstruction:
    """Tests for Battery construction."""

    def test_basic_construction(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        assert battery.cells_series == 14
        assert battery.cells_parallel == 4

    def test_chemistry_string_conversion(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        assert battery.chemistry == LITHIUM_ION

    def test_chemistry_alias_string(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lipo',
        )
        assert battery.chemistry == LITHIUM_POLYMER

    def test_default_chemistry(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert battery.chemistry == LITHIUM_ION

    def test_invalid_cells_series_zero(self):
        with pytest.raises(ValueError, match="cells_series"):
            Battery(
                cells_series=0,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                cell_mass=Mass(50, 'g'),
            )

    def test_invalid_cells_parallel_negative(self):
        with pytest.raises(ValueError, match="cells_parallel"):
            Battery(
                cells_series=10,
                cells_parallel=-1,
                cell_capacity=Capacity(5, 'Ah'),
                cell_mass=Mass(50, 'g'),
            )

    def test_invalid_c_rating_charge(self):
        with pytest.raises(ValueError, match="c_rating_charge"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                cell_mass=Mass(50, 'g'),
                c_rating_charge=0,
            )

    def test_invalid_c_rating_discharge(self):
        with pytest.raises(ValueError, match="c_rating_discharge"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                cell_mass=Mass(50, 'g'),
                c_rating_discharge=-1,
            )

    def test_invalid_pack_overhead(self):
        with pytest.raises(ValueError, match="pack_overhead_fraction"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                cell_mass=Mass(50, 'g'),
                pack_overhead_fraction=1.5,
            )


class TestBatteryVoltageProperties:
    """Tests for Battery voltage calculations."""

    def test_nominal_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 3.7V = 51.8V
        assert abs(battery.nominal_voltage.in_units_of('V') - 51.8) < 0.01

    def test_max_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 4.2V = 58.8V
        assert abs(battery.max_voltage.in_units_of('V') - 58.8) < 0.01

    def test_min_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 2.8V = 39.2V
        assert abs(battery.min_voltage.in_units_of('V') - 39.2) < 0.01

    def test_voltage_with_lifepo4(self):
        battery = Battery(
            cells_series=16,
            cells_parallel=2,
            cell_capacity=Capacity(3, 'Ah'),
            cell_mass=Mass(45, 'g'),
            chemistry=LITHIUM_IRON_PHOSPHATE,
        )
        # 16 * 3.2V = 51.2V nominal
        assert abs(battery.nominal_voltage.in_units_of('V') - 51.2) < 0.01


class TestBatteryCapacityProperties:
    """Tests for Battery capacity calculations."""

    def test_total_capacity_ah(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        # 4 * 5Ah = 20Ah
        assert abs(battery.total_capacity.in_units_of('Ah') - 20) < 0.01

    def test_total_capacity_mah(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=3,
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
        )
        # 3 * 5000mAh = 15000mAh = 15Ah
        assert abs(battery.total_capacity.in_units_of('Ah') - 15) < 0.01

    def test_total_cells(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert battery.total_cells == 56


class TestBatteryEnergyProperties:
    """Tests for Battery energy calculations."""

    def test_energy_capacity_wh(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # 51.8V * 20Ah = 1036Wh
        assert abs(battery.energy_capacity.in_units_of('Wh') - 1036) < 1

    def test_energy_capacity_kwh(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        assert abs(battery.energy_capacity.in_units_of('kWh') - 1.036) < 0.01

    def test_energy_capacity_max(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # 58.8V * 20Ah = 1176Wh
        assert abs(battery.energy_capacity_max.in_units_of('Wh') - 1176) < 1


class TestBatteryCurrentLimits:
    """Tests for Battery current limit calculations."""

    def test_max_charge_current_1c(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            c_rating_charge=1.0,
        )
        # 20Ah * 1C = 20A
        assert abs(battery.max_charge_current.in_units_of('A') - 20) < 0.01

    def test_max_discharge_current_2c(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            c_rating_discharge=2.0,
        )
        # 20Ah * 2C = 40A
        assert abs(battery.max_discharge_current.in_units_of('A') - 40) < 0.01

    def test_max_discharge_current_high_c(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            c_rating_discharge=5.0,
        )
        # 20Ah * 5C = 100A
        assert abs(battery.max_discharge_current.in_units_of('A') - 100) < 0.01


class TestBatteryPowerLimits:
    """Tests for Battery power limit calculations."""

    def test_max_charge_power(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
            c_rating_charge=1.0,
        )
        # 51.8V * 20A = 1036W
        assert abs(battery.max_charge_power.in_units_of('W') - 1036) < 1

    def test_max_discharge_power(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
            c_rating_discharge=2.0,
        )
        # 51.8V * 40A = 2072W
        assert abs(battery.max_discharge_power.in_units_of('W') - 2072) < 1

    def test_max_discharge_power_kw(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
            c_rating_discharge=2.0,
        )
        assert abs(battery.max_discharge_power.in_units_of('kW') - 2.072) < 0.01


class TestBatteryMass:
    """Tests for Battery mass calculations."""

    def test_mass_calculation(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            pack_overhead_fraction=0.15,
        )
        # 40 cells * 50g = 2000g = 2kg
        # Plus 15% overhead = 2.3kg
        assert abs(battery.mass.in_units_of('kg') - 2.3) < 0.01

    def test_mass_with_zero_overhead(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            pack_overhead_fraction=0.0,
        )
        # 40 cells * 50g = 2000g = 2kg
        assert abs(battery.mass.in_units_of('kg') - 2.0) < 0.01


class TestBatteryFromTargetVoltage:
    """Tests for Battery.from_target_voltage sizing method."""

    def test_exact_voltage_match(self):
        # 48V / 3.7V = 12.97 cells -> 13 cells -> 48.1V
        battery = Battery.from_target_voltage(
            target_voltage=Voltage(48.1, 'V'),  # 13 * 3.7 = exact
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        assert isinstance(battery, Battery)
        assert battery.cells_series == 13

    def test_voltage_rounds_up(self):
        battery = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        # 48 / 3.7 = 12.97 -> rounds up to 13
        assert battery.cells_series == 13
        assert len(battery.warnings) > 0
        assert "Rounded" in battery.warnings[0]

    def test_voltage_rounds_to_nearest(self):
        # 44.4V / 3.7V = 12.0 -> exactly 12 cells
        # 46V / 3.7V = 12.43 -> rounds down to 12 cells
        # 48V / 3.7V = 12.97 -> rounds up to 13 cells
        battery_down = Battery.from_target_voltage(
            target_voltage=Voltage(46, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        assert battery_down.cells_series == 12  # 12.43 rounds down

        battery_up = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        assert battery_up.cells_series == 13  # 12.97 rounds up

    def test_info_contains_voltage_info(self):
        battery = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert 'target_voltage_v' in battery.info
        assert 'actual_voltage_v' in battery.info
        assert 'cells_exact' in battery.info

    def test_low_voltage_minimum_one_cell(self):
        battery = Battery.from_target_voltage(
            target_voltage=Voltage(1, 'V'),  # Very low
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert battery.cells_series >= 1


class TestBatteryFromTargetEnergy:
    """Tests for Battery.from_target_energy sizing method."""

    def test_basic_energy_sizing(self):
        battery = Battery.from_target_energy(
            target_energy=Energy(1, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )
        # Should have enough capacity for 1kWh
        assert battery.energy_capacity >= Energy(1, 'kWh')

    def test_info_contains_energy_info(self):
        battery = Battery.from_target_energy(
            target_energy=Energy(1, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert 'target_energy_wh' in battery.info
        assert 'actual_energy_wh' in battery.info
        assert 'energy_margin_percent' in battery.info
        assert 'configuration' in battery.info

    def test_configuration_string_format(self):
        battery = Battery.from_target_energy(
            target_energy=Energy(500, 'Wh'),
            target_voltage=Voltage(24, 'V'),
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        config = battery.info['configuration']
        assert 'S' in config
        assert 'P' in config


class TestBatterySINormalization:
    """Tests for Battery SI unit normalization on construction."""

    def test_cell_mass_normalized_to_kg(self):
        """Cell mass should be normalized to kg (SI default)."""
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),  # Input in grams
        )
        assert battery.cell_mass.units == 'kilogram'
        assert abs(battery.cell_mass.magnitude - 0.05) < 0.0001

    def test_cell_capacity_normalized_to_ah(self):
        """Cell capacity should be normalized to Ah (SI default)."""
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5000, 'mAh'),  # Input in mAh
            cell_mass=Mass(50, 'g'),
        )
        assert battery.cell_capacity.units == 'ampere_hour'
        assert abs(battery.cell_capacity.magnitude - 5.0) < 0.0001

    def test_normalized_values_used_in_calculations(self):
        """Verify normalized values are used correctly in calculations."""
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5000, 'mAh'),  # 5 Ah
            cell_mass=Mass(50, 'g'),  # 0.05 kg
            pack_overhead_fraction=0.0,
        )
        # Total capacity should be 4 * 5Ah = 20Ah
        assert abs(battery.total_capacity.in_units_of('Ah') - 20) < 0.01
        # Total mass should be 40 cells * 0.05kg = 2.0kg
        assert abs(battery.mass.in_units_of('kg') - 2.0) < 0.01


class TestBatteryProperties:
    """Tests for Battery properties and repr."""

    def test_component_type(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        assert battery.component_type == 'battery'

    def test_usable_energy_ratio(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        # (3.7 - 2.8) / (4.2 - 2.8) = 0.9 / 1.4 ≈ 0.643
        ratio = battery.usable_energy_ratio
        assert 0.6 < ratio < 0.7

    def test_repr(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )
        repr_str = repr(battery)
        assert 'Battery' in repr_str
        assert '14S4P' in repr_str


class TestBatteryCRateConversion:
    """Tests for Battery C-rate conversion methods."""

    @pytest.fixture
    def battery(self):
        return Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )

    def test_current_from_c_rate_1c(self, battery):
        """1C on 20Ah pack should be 20A."""
        current = battery.current_from_c_rate(1.0)
        assert current.in_units_of('A') == pytest.approx(20)

    def test_current_from_c_rate_2c(self, battery):
        """2C on 20Ah pack should be 40A."""
        current = battery.current_from_c_rate(2.0)
        assert current.in_units_of('A') == pytest.approx(40)

    def test_current_from_c_rate_half(self, battery):
        """0.5C on 20Ah pack should be 10A."""
        current = battery.current_from_c_rate(0.5)
        assert current.in_units_of('A') == pytest.approx(10)

    def test_c_rate_from_current_20a(self, battery):
        """20A on 20Ah pack should be 1C."""
        c_rate = battery.c_rate_from_current(Current(20, 'A'))
        assert c_rate == pytest.approx(1.0)

    def test_c_rate_from_current_40a(self, battery):
        """40A on 20Ah pack should be 2C."""
        c_rate = battery.c_rate_from_current(Current(40, 'A'))
        assert c_rate == pytest.approx(2.0)

    def test_roundtrip_conversion(self, battery):
        """Converting back and forth should preserve value."""
        original_c_rate = 1.5
        current = battery.current_from_c_rate(original_c_rate)
        recovered_c_rate = battery.c_rate_from_current(current)
        assert recovered_c_rate == pytest.approx(original_c_rate)


class TestBatteryDischargeVoltage:
    """Tests for Battery discharge voltage methods."""

    @pytest.fixture
    def battery(self):
        return Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )

    def test_get_cell_voltage_high_soc(self, battery):
        """Cell voltage at high SoC should be near max."""
        v = battery.get_cell_voltage(soc=0.95, c_rate=0.1)
        # Should be close to max (4.2V) but with small I*R drop
        assert v.in_units_of('V') > 4.0
        assert v.in_units_of('V') <= 4.2

    def test_get_cell_voltage_low_soc(self, battery):
        """Cell voltage at low SoC should be lower."""
        v = battery.get_cell_voltage(soc=0.1, c_rate=0.1)
        # Should be closer to min (2.8V)
        assert v.in_units_of('V') < 3.5
        assert v.in_units_of('V') >= 2.8

    def test_get_voltage_pack_scaling(self, battery):
        """Pack voltage should be cell voltage * cells_series."""
        cell_v = battery.get_cell_voltage(soc=0.5, c_rate=1.0)
        pack_v = battery.get_voltage(soc=0.5, c_rate=1.0)
        assert pack_v.in_units_of('V') == pytest.approx(
            cell_v.in_units_of('V') * 14, abs=0.1
        )

    def test_get_voltage_with_current(self, battery):
        """get_voltage should work with current instead of c_rate."""
        v_c_rate = battery.get_voltage(soc=0.5, c_rate=1.0)
        v_current = battery.get_voltage(soc=0.5, current=Current(20, 'A'))
        assert v_c_rate.in_units_of('V') == pytest.approx(
            v_current.in_units_of('V'), abs=0.01
        )

    def test_get_voltage_requires_current_or_c_rate(self, battery):
        """Must provide either current or c_rate."""
        with pytest.raises(ValueError, match="Must provide"):
            battery.get_voltage(soc=0.5)

    def test_get_voltage_not_both(self, battery):
        """Cannot provide both current and c_rate."""
        with pytest.raises(ValueError, match="not both"):
            battery.get_voltage(soc=0.5, current=Current(20, 'A'), c_rate=1.0)

    def test_voltage_decreases_with_soc(self, battery):
        """Pack voltage should decrease as SoC decreases."""
        v_high = battery.get_voltage(soc=0.9, c_rate=1.0)
        v_low = battery.get_voltage(soc=0.1, c_rate=1.0)
        assert v_high > v_low

    def test_voltage_decreases_with_c_rate(self, battery):
        """Pack voltage should decrease as C-rate increases."""
        v_low_c = battery.get_voltage(soc=0.5, c_rate=0.5)
        v_high_c = battery.get_voltage(soc=0.5, c_rate=3.0)
        assert v_low_c > v_high_c


class TestBatteryInternalResistance:
    """Tests for Battery internal resistance methods."""

    def test_pack_resistance_series_only(self):
        """Series cells add resistance."""
        battery = Battery(
            cells_series=10,
            cells_parallel=1,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,  # 30 mohm per cell
        )
        # 10 cells in series * 30 mohm = 300 mohm
        r = battery.internal_resistance
        assert r.in_units_of('mohm') == pytest.approx(300, abs=1)

    def test_pack_resistance_parallel_only(self):
        """Parallel cells reduce resistance."""
        battery = Battery(
            cells_series=1,
            cells_parallel=3,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,  # 30 mohm per cell
        )
        # 1 cell / 3 parallel = 10 mohm
        r = battery.internal_resistance
        assert r.in_units_of('mohm') == pytest.approx(10, abs=1)

    def test_pack_resistance_series_parallel(self):
        """Series/parallel combination."""
        battery = Battery(
            cells_series=2,
            cells_parallel=3,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,  # 30 mohm per cell
        )
        # (30 mohm * 2 series) / 3 parallel = 20 mohm
        r = battery.internal_resistance
        assert r.in_units_of('mohm') == pytest.approx(20, abs=1)

    def test_get_internal_resistance_returns_value(self):
        """get_internal_resistance should return pack resistance."""
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,
        )
        r = battery.get_internal_resistance(soc=0.5)
        assert r is not None
        assert r.in_units_of('mohm') > 0


class TestBatteryHeatGeneration:
    """Tests for Battery heat generation methods."""

    @pytest.fixture
    def battery(self):
        return Battery(
            cells_series=2,
            cells_parallel=3,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            chemistry=LITHIUM_ION,  # 30 mohm per cell
        )

    def test_heat_generation_i2r(self, battery):
        """Heat should be I^2 * R."""
        # Pack R = 20 mohm = 0.02 ohm
        # At 10A: P = 10^2 * 0.02 = 2W
        heat = battery.heat_generation_rate(Current(10, 'A'))
        assert heat.in_units_of('W') == pytest.approx(2, abs=0.1)

    def test_heat_generation_scales_with_current_squared(self, battery):
        """Heat should scale with I^2."""
        heat_10a = battery.heat_generation_rate(Current(10, 'A'))
        heat_20a = battery.heat_generation_rate(Current(20, 'A'))
        # 20A should generate 4x the heat of 10A
        ratio = heat_20a.in_units_of('W') / heat_10a.in_units_of('W')
        assert ratio == pytest.approx(4.0, abs=0.1)

    def test_heat_generation_with_soc(self, battery):
        """Heat generation with SoC-dependent resistance."""
        heat = battery.heat_generation_rate(Current(10, 'A'), soc=0.5)
        assert heat.in_units_of('W') > 0


class TestBatteryDischargeModel:
    """Tests for Battery discharge model integration."""

    @pytest.fixture
    def battery(self):
        return Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
        )

    def test_default_discharge_model(self, battery):
        """Default model should be AnalyticalDischargeModel."""
        model = battery.discharge_model
        assert isinstance(model, AnalyticalDischargeModel)

    def test_set_discharge_model(self, battery):
        """Should be able to set custom discharge model."""
        import numpy as np

        custom_model = LookupTableDischargeModel(
            soc_points=np.array([0.0, 0.5, 1.0]),
            c_rate_points=np.array([0.1, 1.0]),
            voltage_data=np.array([[2.8, 2.7], [3.5, 3.4], [4.2, 4.1]]),
        )
        battery.set_discharge_model(custom_model)
        assert battery.discharge_model is custom_model


class TestBatteryChargeModel:
    """Tests for Battery charge model integration."""

    @pytest.fixture
    def battery(self):
        return Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            cell_mass=Mass(50, 'g'),
            c_rating_charge=1.0,
        )

    def test_default_charge_model(self, battery):
        """Default model should be SimpleChargeModel."""
        model = battery.charge_model
        assert isinstance(model, SimpleChargeModel)

    def test_get_charge_current_cc_phase(self, battery):
        """In CC phase, should get max charge current."""
        current = battery.get_charge_current(soc=0.3)
        # 1C on 20Ah = 20A
        assert current.in_units_of('A') == pytest.approx(20, abs=0.1)

    def test_get_charge_current_cv_phase(self, battery):
        """In CV phase, current should taper."""
        current_low_soc = battery.get_charge_current(soc=0.5)
        current_high_soc = battery.get_charge_current(soc=0.95)
        assert current_high_soc < current_low_soc

    def test_get_charge_efficiency(self, battery):
        """Charge efficiency should be between 0 and 1."""
        eff = battery.get_charge_efficiency(soc=0.5, c_rate=1.0)
        assert 0 < eff < 1

    def test_time_to_charge(self, battery):
        """Time to charge should be positive."""
        time = battery.time_to_charge(start_soc=0.2, end_soc=0.8)
        assert time > 0


class TestBatteryChemistryResistance:
    """Tests for chemistry internal resistance values."""

    def test_lithium_ion_resistance(self):
        """Lithium-ion chemistry should have internal resistance."""
        assert LITHIUM_ION.internal_resistance is not None
        assert LITHIUM_ION.internal_resistance.in_units_of('mohm') == 30

    def test_lithium_polymer_resistance(self):
        """LiPo chemistry should have internal resistance."""
        assert LITHIUM_POLYMER.internal_resistance is not None
        assert LITHIUM_POLYMER.internal_resistance.in_units_of('mohm') == 25

    def test_lifepo4_resistance(self):
        """LiFePO4 chemistry should have internal resistance."""
        assert LITHIUM_IRON_PHOSPHATE.internal_resistance is not None
        assert LITHIUM_IRON_PHOSPHATE.internal_resistance.in_units_of('mohm') == 40

    def test_nmc_resistance(self):
        """NMC chemistry should have internal resistance."""
        assert LITHIUM_NMC.internal_resistance is not None
        assert LITHIUM_NMC.internal_resistance.in_units_of('mohm') == 25


class TestBatteryChemistryThermalLimits:
    """Tests for chemistry thermal limit values."""

    def test_lithium_ion_thermal_limits(self):
        """Lithium-ion chemistry should have thermal limits."""
        assert LITHIUM_ION.max_discharge_temperature is not None
        assert LITHIUM_ION.max_discharge_temperature.in_units_of('degC') == 60
        assert LITHIUM_ION.min_temperature is not None
        assert LITHIUM_ION.min_temperature.in_units_of('degC') == -20

