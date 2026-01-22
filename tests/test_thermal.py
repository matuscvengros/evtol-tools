"""Tests for Battery thermal framework.

This module provides tests for ThermalLimits and SimpleThermalModel classes.
"""

import pytest

from evtoltools.common import Mass, Power, Temperature, Time
from evtoltools.components.battery import SimpleThermalModel, ThermalLimits


class TestThermalLimitsConstruction:
    """Tests for ThermalLimits construction."""

    def test_default_values(self):
        """Default values should be reasonable."""
        limits = ThermalLimits()
        assert limits.max_charge_temp.in_units_of('degC') == 45
        assert limits.max_discharge_temp.in_units_of('degC') == 60
        assert limits.min_temp.in_units_of('degC') == -20
        assert limits.derate_temp.in_units_of('degC') == 40

    def test_custom_values(self):
        """Custom values should be stored correctly."""
        limits = ThermalLimits(
            max_charge_temp=Temperature(50, 'degC'),
            max_discharge_temp=Temperature(65, 'degC'),
            min_temp=Temperature(-10, 'degC'),
            derate_temp=Temperature(45, 'degC'),
        )
        assert limits.max_charge_temp.in_units_of('degC') == 50
        assert limits.max_discharge_temp.in_units_of('degC') == 65


class TestThermalLimitsWithinLimits:
    """Tests for ThermalLimits.is_within_limits."""

    @pytest.fixture
    def limits(self):
        return ThermalLimits()

    def test_normal_temperature_discharge(self, limits):
        """Normal temperature should be within discharge limits."""
        assert limits.is_within_limits(Temperature(25, 'degC'), is_charging=False)

    def test_normal_temperature_charge(self, limits):
        """Normal temperature should be within charge limits."""
        assert limits.is_within_limits(Temperature(25, 'degC'), is_charging=True)

    def test_high_temperature_discharge_ok(self, limits):
        """Temperature up to 60C should be OK for discharge."""
        assert limits.is_within_limits(Temperature(55, 'degC'), is_charging=False)

    def test_high_temperature_charge_not_ok(self, limits):
        """Temperature above 45C should not be OK for charge."""
        assert not limits.is_within_limits(Temperature(50, 'degC'), is_charging=True)

    def test_too_hot_discharge(self, limits):
        """Temperature above 60C not OK for discharge."""
        assert not limits.is_within_limits(Temperature(65, 'degC'), is_charging=False)

    def test_too_cold(self, limits):
        """Temperature below -20C not OK."""
        assert not limits.is_within_limits(Temperature(-25, 'degC'), is_charging=False)

    def test_at_minimum_temperature(self, limits):
        """At exactly minimum temperature should be OK."""
        assert limits.is_within_limits(Temperature(-20, 'degC'), is_charging=False)


class TestThermalLimitsDerateFactor:
    """Tests for ThermalLimits derate factor calculations."""

    @pytest.fixture
    def limits(self):
        return ThermalLimits(
            derate_temp=Temperature(40, 'degC'),
            max_discharge_temp=Temperature(60, 'degC'),
        )

    def test_no_derate_below_threshold(self, limits):
        """Below derate temperature, factor should be 1.0."""
        factor = limits.get_derate_factor(Temperature(30, 'degC'))
        assert factor == pytest.approx(1.0)

    def test_no_derate_at_threshold(self, limits):
        """At derate temperature, factor should be 1.0."""
        factor = limits.get_derate_factor(Temperature(40, 'degC'))
        assert factor == pytest.approx(1.0)

    def test_partial_derate_midway(self, limits):
        """Halfway between derate and max, factor should be 0.5."""
        factor = limits.get_derate_factor(Temperature(50, 'degC'))
        assert factor == pytest.approx(0.5)

    def test_full_derate_at_max(self, limits):
        """At max temperature, factor should be 0.0."""
        factor = limits.get_derate_factor(Temperature(60, 'degC'))
        assert factor == pytest.approx(0.0)

    def test_full_derate_above_max(self, limits):
        """Above max temperature, factor should be 0.0."""
        factor = limits.get_derate_factor(Temperature(70, 'degC'))
        assert factor == pytest.approx(0.0)


class TestThermalLimitsColdDerate:
    """Tests for cold temperature derating."""

    @pytest.fixture
    def limits(self):
        return ThermalLimits(min_temp=Temperature(-20, 'degC'))

    def test_no_cold_derate_above_zero(self, limits):
        """Above 0C, no cold derating."""
        factor = limits.get_cold_derate_factor(Temperature(10, 'degC'))
        assert factor == pytest.approx(1.0)

    def test_no_cold_derate_at_zero(self, limits):
        """At 0C, no cold derating."""
        factor = limits.get_cold_derate_factor(Temperature(0, 'degC'))
        assert factor == pytest.approx(1.0)

    def test_partial_cold_derate(self, limits):
        """At -10C (halfway to min), factor should be 0.5."""
        factor = limits.get_cold_derate_factor(Temperature(-10, 'degC'))
        assert factor == pytest.approx(0.5)

    def test_full_cold_derate_at_min(self, limits):
        """At minimum temperature, factor should be 0.0."""
        factor = limits.get_cold_derate_factor(Temperature(-20, 'degC'))
        assert factor == pytest.approx(0.0)


class TestSimpleThermalModelConstruction:
    """Tests for SimpleThermalModel construction."""

    def test_basic_construction(self):
        """Basic model construction."""
        model = SimpleThermalModel(
            mass=Mass(5, 'kg'),
            specific_heat=1000,
            cooling_coefficient=10.0,
        )
        assert model.mass.in_units_of('kg') == 5
        assert model.specific_heat == 1000
        assert model.cooling_coefficient == 10.0


class TestSimpleThermalModelTemperature:
    """Tests for SimpleThermalModel temperature predictions."""

    @pytest.fixture
    def model(self):
        return SimpleThermalModel(
            mass=Mass(5, 'kg'),
            specific_heat=1000,
            cooling_coefficient=10.0,
        )

    def test_no_heat_at_ambient(self, model):
        """With no heat and at ambient, temperature should stay constant."""
        initial = Temperature(25, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(0, 'W')

        final = model.temperature_after(
            initial_temp=initial,
            heat_rate=heat,
            duration=Time(60, 's'),
            ambient_temp=ambient,
        )

        assert final.in_units_of('degC') == pytest.approx(25, abs=0.1)

    def test_heating_from_heat_generation(self, model):
        """Heat generation should increase temperature."""
        initial = Temperature(25, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(100, 'W')

        final = model.temperature_after(
            initial_temp=initial,
            heat_rate=heat,
            duration=Time(60, 's'),
            ambient_temp=ambient,
        )

        assert final.in_units_of('degC') > 25

    def test_cooling_to_ambient(self, model):
        """Hot battery should cool towards ambient."""
        initial = Temperature(50, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(0, 'W')

        final = model.temperature_after(
            initial_temp=initial,
            heat_rate=heat,
            duration=Time(300, 's'),
            ambient_temp=ambient,
        )

        # Should be cooler than initial
        assert final.in_units_of('degC') < 50
        # Should still be above ambient
        assert final.in_units_of('degC') > 25

    def test_longer_duration_more_change(self, model):
        """Longer duration should result in more temperature change."""
        initial = Temperature(25, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(50, 'W')

        final_short = model.temperature_after(
            initial_temp=initial,
            heat_rate=heat,
            duration=Time(60, 's'),
            ambient_temp=ambient,
        )
        final_long = model.temperature_after(
            initial_temp=initial,
            heat_rate=heat,
            duration=Time(300, 's'),
            ambient_temp=ambient,
        )

        assert final_long > final_short


class TestSimpleThermalModelSteadyState:
    """Tests for steady-state temperature calculation."""

    @pytest.fixture
    def model(self):
        return SimpleThermalModel(
            mass=Mass(5, 'kg'),
            specific_heat=1000,
            cooling_coefficient=10.0,
        )

    def test_steady_state_with_heat(self, model):
        """Steady state should be above ambient with heat generation."""
        ambient = Temperature(25, 'degC')
        heat = Power(100, 'W')

        steady = model.steady_state_temperature(
            heat_rate=heat,
            ambient_temp=ambient,
        )

        # dT = Q / cooling_coeff = 100 / 10 = 10 K
        assert steady.in_units_of('degC') == pytest.approx(35, abs=0.5)

    def test_steady_state_no_heat(self, model):
        """Steady state with no heat should equal ambient."""
        ambient = Temperature(25, 'degC')
        heat = Power(0, 'W')

        steady = model.steady_state_temperature(
            heat_rate=heat,
            ambient_temp=ambient,
        )

        assert steady.in_units_of('degC') == pytest.approx(25, abs=0.1)


class TestSimpleThermalModelTimeToTemp:
    """Tests for time-to-temperature calculation."""

    @pytest.fixture
    def model(self):
        return SimpleThermalModel(
            mass=Mass(5, 'kg'),
            specific_heat=1000,
            cooling_coefficient=10.0,
        )

    def test_time_to_heat_up(self, model):
        """Time to reach higher temperature with heat generation."""
        initial = Temperature(25, 'degC')
        target = Temperature(30, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(100, 'W')

        time = model.time_to_temperature(
            initial_temp=initial,
            target_temp=target,
            heat_rate=heat,
            ambient_temp=ambient,
        )

        assert time.in_units_of('s') > 0
        assert time.in_units_of('s') < float('inf')

    def test_time_to_unreachable_temp(self, model):
        """Time to unreachable temperature should be infinite."""
        initial = Temperature(25, 'degC')
        target = Temperature(50, 'degC')  # Above steady state
        ambient = Temperature(25, 'degC')
        heat = Power(100, 'W')  # Steady state is 35C

        time = model.time_to_temperature(
            initial_temp=initial,
            target_temp=target,
            heat_rate=heat,
            ambient_temp=ambient,
        )

        assert time.in_units_of('s') == float('inf')

    def test_time_to_cool_down(self, model):
        """Time to cool to lower temperature."""
        initial = Temperature(40, 'degC')
        target = Temperature(30, 'degC')
        ambient = Temperature(25, 'degC')
        heat = Power(0, 'W')

        time = model.time_to_temperature(
            initial_temp=initial,
            target_temp=target,
            heat_rate=heat,
            ambient_temp=ambient,
        )

        assert time.in_units_of('s') > 0
        assert time.in_units_of('s') < float('inf')
