"""Tests for Battery chemistry and Battery component."""

import pytest
import math

from evtoltools.common import Mass, Voltage, Energy, Capacity, Current, Power
from evtoltools.components import (
    Battery,
    BatteryChemistry,
    get_chemistry,
    LITHIUM_ION,
    LITHIUM_POLYMER,
    LITHIUM_IRON_PHOSPHATE,
    LITHIUM_NMC,
)
from evtoltools.components.base import ComponentResult


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
            chemistry=LITHIUM_ION,
        )
        assert battery.cells_series == 14
        assert battery.cells_parallel == 4

    def test_chemistry_string_conversion(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry='lithium_ion',
        )
        assert battery.chemistry == LITHIUM_ION

    def test_chemistry_alias_string(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry='lipo',
        )
        assert battery.chemistry == LITHIUM_POLYMER

    def test_default_chemistry(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
        )
        assert battery.chemistry == LITHIUM_ION

    def test_invalid_cells_series_zero(self):
        with pytest.raises(ValueError, match="cells_series"):
            Battery(
                cells_series=0,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
            )

    def test_invalid_cells_parallel_negative(self):
        with pytest.raises(ValueError, match="cells_parallel"):
            Battery(
                cells_series=10,
                cells_parallel=-1,
                cell_capacity=Capacity(5, 'Ah'),
            )

    def test_invalid_c_rating_charge(self):
        with pytest.raises(ValueError, match="c_rating_charge"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                c_rating_charge=0,
            )

    def test_invalid_c_rating_discharge(self):
        with pytest.raises(ValueError, match="c_rating_discharge"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                c_rating_discharge=-1,
            )

    def test_invalid_pack_overhead(self):
        with pytest.raises(ValueError, match="pack_overhead_fraction"):
            Battery(
                cells_series=10,
                cells_parallel=2,
                cell_capacity=Capacity(5, 'Ah'),
                pack_overhead_fraction=1.5,
            )


class TestBatteryVoltageProperties:
    """Tests for Battery voltage calculations."""

    def test_nominal_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 3.7V = 51.8V
        assert abs(battery.nominal_voltage.in_units_of('V') - 51.8) < 0.01

    def test_max_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 4.2V = 58.8V
        assert abs(battery.max_voltage.in_units_of('V') - 58.8) < 0.01

    def test_min_voltage(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry=LITHIUM_ION,
        )
        # 14 * 2.8V = 39.2V
        assert abs(battery.min_voltage.in_units_of('V') - 39.2) < 0.01

    def test_voltage_with_lifepo4(self):
        battery = Battery(
            cells_series=16,
            cells_parallel=2,
            cell_capacity=Capacity(3, 'Ah'),
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
        )
        # 4 * 5Ah = 20Ah
        assert abs(battery.total_capacity.in_units_of('Ah') - 20) < 0.01

    def test_total_capacity_mah(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=3,
            cell_capacity=Capacity(5000, 'mAh'),
        )
        # 3 * 5000mAh = 15000mAh = 15Ah
        assert abs(battery.total_capacity.in_units_of('Ah') - 15) < 0.01

    def test_total_cells(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
        )
        assert battery.total_cells == 56


class TestBatteryEnergyProperties:
    """Tests for Battery energy calculations."""

    def test_energy_capacity_wh(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry=LITHIUM_ION,
        )
        # 51.8V * 20Ah = 1036Wh
        assert abs(battery.energy_capacity.in_units_of('Wh') - 1036) < 1

    def test_energy_capacity_kwh(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry=LITHIUM_ION,
        )
        assert abs(battery.energy_capacity.in_units_of('kWh') - 1.036) < 0.01

    def test_energy_capacity_max(self):
        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
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
            c_rating_charge=1.0,
        )
        # 20Ah * 1C = 20A
        assert abs(battery.max_charge_current.in_units_of('A') - 20) < 0.01

    def test_max_discharge_current_2c(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            c_rating_discharge=2.0,
        )
        # 20Ah * 2C = 40A
        assert abs(battery.max_discharge_current.in_units_of('A') - 40) < 0.01

    def test_max_discharge_current_high_c(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
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
            chemistry=LITHIUM_ION,
            c_rating_discharge=2.0,
        )
        assert abs(battery.max_discharge_power.in_units_of('kW') - 2.072) < 0.01


class TestBatteryMass:
    """Tests for Battery mass calculations."""

    def test_mass_without_cell_mass(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
        )
        # Without cell_mass, returns 0
        assert battery.mass.magnitude == 0

    def test_mass_with_cell_mass(self):
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
    """Tests for Battery.from_target_voltage factory method."""

    def test_exact_voltage_match(self):
        # 48V / 3.7V = 12.97 cells -> 13 cells -> 48.1V
        result = Battery.from_target_voltage(
            target_voltage=Voltage(48.1, 'V'),  # 13 * 3.7 = exact
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry='lithium_ion',
        )
        assert isinstance(result, ComponentResult)
        battery = result.value
        assert battery.cells_series == 13

    def test_voltage_rounds_up(self):
        result = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry='lithium_ion',
        )
        battery = result.value
        # 48 / 3.7 = 12.97 -> rounds up to 13
        assert battery.cells_series == 13
        assert len(result.warnings) > 0
        assert "Rounded" in result.warnings[0]

    def test_voltage_round_nearest(self):
        result = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
            chemistry='lithium_ion',
            round_up=False,
        )
        battery = result.value
        # 48 / 3.7 = 12.97 -> rounds to 13
        assert battery.cells_series == 13

    def test_metadata_contains_voltage_info(self):
        result = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5, 'Ah'),
        )
        assert 'target_voltage_v' in result.metadata
        assert 'actual_voltage_v' in result.metadata
        assert 'cells_exact' in result.metadata

    def test_low_voltage_minimum_one_cell(self):
        result = Battery.from_target_voltage(
            target_voltage=Voltage(1, 'V'),  # Very low
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
        )
        battery = result.value
        assert battery.cells_series >= 1


class TestBatteryFromEnergyRequirement:
    """Tests for Battery.from_energy_requirement factory method."""

    def test_basic_energy_sizing(self):
        result = Battery.from_energy_requirement(
            required_energy=Energy(1, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            chemistry='lithium_ion',
            cell_capacity=Capacity(5, 'Ah'),
        )
        battery = result.value
        # Should have enough capacity for 1kWh
        assert battery.energy_capacity.in_units_of('kWh') >= 1.0

    def test_default_cell_capacity(self):
        result = Battery.from_energy_requirement(
            required_energy=Energy(500, 'Wh'),
            target_voltage=Voltage(24, 'V'),
        )
        # Should use default 5Ah cell capacity
        assert "default cell capacity" in result.warnings[0].lower()

    def test_metadata_contains_energy_info(self):
        result = Battery.from_energy_requirement(
            required_energy=Energy(1, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            cell_capacity=Capacity(5, 'Ah'),
        )
        assert 'required_energy_wh' in result.metadata
        assert 'actual_energy_wh' in result.metadata
        assert 'energy_margin_percent' in result.metadata
        assert 'configuration' in result.metadata

    def test_configuration_string_format(self):
        result = Battery.from_energy_requirement(
            required_energy=Energy(500, 'Wh'),
            target_voltage=Voltage(24, 'V'),
            cell_capacity=Capacity(5, 'Ah'),
        )
        config = result.metadata['configuration']
        assert 'S' in config
        assert 'P' in config


class TestBatteryProperties:
    """Tests for Battery properties and repr."""

    def test_component_type(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
        )
        assert battery.component_type == 'battery'

    def test_usable_energy_ratio(self):
        battery = Battery(
            cells_series=10,
            cells_parallel=2,
            cell_capacity=Capacity(5, 'Ah'),
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
        )
        repr_str = repr(battery)
        assert 'Battery' in repr_str
        assert '14S4P' in repr_str

