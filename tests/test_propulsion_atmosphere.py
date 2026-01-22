"""Integration tests for propulsion components with atmosphere support."""

import pytest
import math

from evtoltools.common import (
    Length, Force, Velocity, Density, AngularVelocity, Power, Temperature, Mass
)
from evtoltools.common.atmosphere import Atmosphere
from evtoltools.components import PropulsionSystem, Motor, Propeller


class TestPropellerAtmosphereIntegration:
    """Tests for Propeller methods with atmosphere parameter."""

    def test_max_tip_speed_with_atmosphere_object(self):
        """Test max_tip_speed with Atmosphere instance."""
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)
        atm = Atmosphere(Length(5000, 'm'))

        max_tip = prop.max_tip_speed(atmosphere=atm)

        # Speed of sound at 5000m is lower, so max tip speed should be lower
        expected = atm.speed_of_sound.in_units_of('m/s') * 0.85
        assert abs(max_tip.in_units_of('m/s') - expected) < 0.1

    def test_max_tip_speed_with_altitude(self):
        """Test max_tip_speed with Length altitude (auto-creates Atmosphere)."""
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)

        max_tip = prop.max_tip_speed(atmosphere=Length(5000, 'm'))

        atm = Atmosphere(Length(5000, 'm'))
        expected = atm.speed_of_sound.in_units_of('m/s') * 0.85
        assert abs(max_tip.in_units_of('m/s') - expected) < 0.1

    def test_max_tip_speed_sea_level_vs_altitude(self):
        """Test that max tip speed decreases with altitude."""
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)

        tip_sea_level = prop.max_tip_speed(atmosphere=Length(0, 'm'))
        tip_5000m = prop.max_tip_speed(atmosphere=Length(5000, 'm'))

        # Speed of sound decreases with altitude in troposphere
        assert tip_5000m.in_units_of('m/s') < tip_sea_level.in_units_of('m/s')

    def test_max_angular_velocity_with_atmosphere(self):
        """Test max_angular_velocity with atmosphere."""
        prop = Propeller(diameter=Length(2.0, 'm'), tip_mach_limit=0.85)

        omega_sl = prop.max_angular_velocity(atmosphere=Length(0, 'm'))
        omega_5k = prop.max_angular_velocity(atmosphere=Length(5000, 'm'))

        # Max angular velocity decreases at altitude
        assert omega_5k.in_units_of('rad/s') < omega_sl.in_units_of('rad/s')

    def test_tip_mach_number_with_atmosphere(self):
        """Test tip_mach_number with atmosphere."""
        prop = Propeller(diameter=Length(2.0, 'm'))  # r = 1m
        omega = AngularVelocity(200, 'rad/s')  # V_tip = 200 m/s

        mach_sl = prop.tip_mach_number(omega, atmosphere=Length(0, 'm'))
        mach_5k = prop.tip_mach_number(omega, atmosphere=Length(5000, 'm'))

        # Same tip speed but lower speed of sound at altitude = higher Mach
        assert mach_5k > mach_sl

    def test_backwards_compatibility_without_atmosphere(self):
        """Test that methods work without atmosphere (backwards compatible)."""
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)

        # Should use default speed of sound (343 m/s)
        max_tip = prop.max_tip_speed()
        expected = 343 * 0.85
        assert abs(max_tip.in_units_of('m/s') - expected) < 0.1


class TestPropulsionSystemAtmosphereIntegration:
    """Tests for PropulsionSystem methods with atmosphere parameter."""

    @pytest.fixture
    def quad_rotor(self):
        """Create a typical quad-rotor propulsion system."""
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        prop = Propeller(diameter=Length(2.0, 'm'), efficiency_hover=0.70)
        return PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
            installation_efficiency=0.95,
        )

    def test_hover_power_ideal_with_atmosphere(self, quad_rotor):
        """Test hover_power_ideal with Atmosphere instance."""
        thrust = Force(10000, 'N')
        atm = Atmosphere(Length(5000, 'm'))

        power = quad_rotor.hover_power_ideal(thrust, atmosphere=atm)

        # Calculate expected
        rho = atm.density.in_units_of('kg/m^3')
        area = quad_rotor.total_disk_area.in_units_of('m^2')
        expected = 10000 ** 1.5 / math.sqrt(2 * rho * area)

        assert abs(power.in_units_of('W') - expected) < 100

    def test_hover_power_ideal_with_altitude(self, quad_rotor):
        """Test hover_power_ideal with Length altitude."""
        thrust = Force(10000, 'N')

        power = quad_rotor.hover_power_ideal(thrust, atmosphere=Length(5000, 'm'))

        # Should work with altitude directly
        assert power.in_units_of('W') > 0

    def test_hover_power_increases_with_altitude(self, quad_rotor):
        """Test that hover power increases with altitude (lower density)."""
        thrust = Force(10000, 'N')

        power_sl = quad_rotor.hover_power_ideal(thrust, atmosphere=Length(0, 'm'))
        power_5k = quad_rotor.hover_power_ideal(thrust, atmosphere=Length(5000, 'm'))

        # Lower density at altitude requires more power
        assert power_5k.in_units_of('W') > power_sl.in_units_of('W')

    def test_hover_shaft_power_with_atmosphere(self, quad_rotor):
        """Test hover_shaft_power with atmosphere."""
        thrust = Force(10000, 'N')
        atm = Atmosphere(Length(3000, 'm'))

        shaft_power = quad_rotor.hover_shaft_power(thrust, atmosphere=atm)
        ideal_power = quad_rotor.hover_power_ideal(thrust, atmosphere=atm)

        # Shaft power should be higher than ideal (accounting for FM)
        assert shaft_power.in_units_of('W') > ideal_power.in_units_of('W')

    def test_hover_electrical_power_with_atmosphere(self, quad_rotor):
        """Test hover_electrical_power with atmosphere."""
        thrust = Force(10000, 'N')
        atm = Atmosphere(Length(3000, 'm'))

        elec_power = quad_rotor.hover_electrical_power(thrust, atmosphere=atm)
        shaft_power = quad_rotor.hover_shaft_power(thrust, atmosphere=atm)

        # Electrical power should be higher than shaft (motor efficiency)
        assert elec_power.in_units_of('W') > shaft_power.in_units_of('W')

    def test_induced_velocity_with_atmosphere(self, quad_rotor):
        """Test induced_velocity with atmosphere."""
        thrust = Force(10000, 'N')

        vi_sl = quad_rotor.induced_velocity(thrust, atmosphere=Length(0, 'm'))
        vi_5k = quad_rotor.induced_velocity(thrust, atmosphere=Length(5000, 'm'))

        # Lower density = higher induced velocity
        assert vi_5k.in_units_of('m/s') > vi_sl.in_units_of('m/s')

    def test_max_tip_speed_with_atmosphere(self, quad_rotor):
        """Test max_tip_speed with atmosphere."""
        tip_sl = quad_rotor.max_tip_speed(atmosphere=Length(0, 'm'))
        tip_5k = quad_rotor.max_tip_speed(atmosphere=Length(5000, 'm'))

        # Lower speed of sound at altitude = lower max tip speed
        assert tip_5k.in_units_of('m/s') < tip_sl.in_units_of('m/s')

    def test_atmosphere_priority_over_explicit_density(self, quad_rotor):
        """Test that atmosphere parameter takes priority over air_density."""
        thrust = Force(10000, 'N')

        # Use an unrealistic density to verify atmosphere takes priority
        wrong_density = Density(2.0, 'kg/m^3')
        atm = Atmosphere(Length(5000, 'm'))

        power_with_both = quad_rotor.hover_power_ideal(
            thrust,
            air_density=wrong_density,
            atmosphere=atm
        )
        power_atm_only = quad_rotor.hover_power_ideal(thrust, atmosphere=atm)

        # Should give same result (atmosphere takes priority)
        assert power_with_both.in_units_of('W') == pytest.approx(
            power_atm_only.in_units_of('W'), rel=1e-6
        )

    def test_backwards_compatibility_without_atmosphere(self, quad_rotor):
        """Test that methods work without atmosphere (backwards compatible)."""
        thrust = Force(10000, 'N')

        # Should use default density (1.225 kg/m^3)
        power = quad_rotor.hover_power_ideal(thrust)

        expected_area = quad_rotor.total_disk_area.in_units_of('m^2')
        expected = 10000 ** 1.5 / math.sqrt(2 * 1.225 * expected_area)
        assert abs(power.in_units_of('W') - expected) < 100


class TestAtmosphereWithTemperatureOffset:
    """Tests for atmosphere with temperature offset in propulsion."""

    @pytest.fixture
    def evtol_system(self):
        """Create a typical eVTOL propulsion system."""
        motor = Motor(max_power=Power(75, 'kW'), efficiency=0.92)
        prop = Propeller(diameter=Length(1.8, 'm'), efficiency_hover=0.72)
        return PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=6,
        )

    def test_hot_day_requires_more_power(self, evtol_system):
        """Test that hot day conditions require more hover power."""
        thrust = Force(15000, 'N')
        altitude = Length(1000, 'ft')

        std_day = Atmosphere(altitude)
        hot_day = Atmosphere(altitude, temperature_offset=Temperature(20, 'K'))

        power_std = evtol_system.hover_power_ideal(thrust, atmosphere=std_day)
        power_hot = evtol_system.hover_power_ideal(thrust, atmosphere=hot_day)

        # Hot day has lower density, requires more power
        assert power_hot.in_units_of('W') > power_std.in_units_of('W')

    def test_cold_day_requires_less_power(self, evtol_system):
        """Test that cold day conditions require less hover power."""
        thrust = Force(15000, 'N')
        altitude = Length(1000, 'ft')

        std_day = Atmosphere(altitude)
        cold_day = Atmosphere(altitude, temperature_offset=Temperature(-15, 'K'))

        power_std = evtol_system.hover_power_ideal(thrust, atmosphere=std_day)
        power_cold = evtol_system.hover_power_ideal(thrust, atmosphere=cold_day)

        # Cold day has higher density, requires less power
        assert power_cold.in_units_of('W') < power_std.in_units_of('W')


class TestRealisticMissionScenarios:
    """Integration tests for realistic eVTOL mission scenarios."""

    @pytest.fixture
    def air_taxi(self):
        """Create a typical air taxi propulsion system."""
        motor = Motor(max_power=Power(80, 'kW'), efficiency=0.93, mass=Mass(12, 'kg'))
        prop = Propeller(
            diameter=Length(1.6, 'm'),
            num_blades=5,
            efficiency_hover=0.75,
            tip_mach_limit=0.80,
        )
        return PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=8,
            installation_efficiency=0.92,
        )

    def test_takeoff_to_cruise_power_profile(self, air_taxi):
        """Test power requirements from takeoff through cruise altitude."""
        # Assuming 2000 kg MTOW
        weight = Force(2000 * 9.81, 'N')

        # Power at different altitudes
        altitudes = [Length(0, 'm'), Length(500, 'm'), Length(1000, 'm'), Length(1500, 'm')]
        powers = []

        for alt in altitudes:
            atm = Atmosphere(alt)
            power = air_taxi.hover_electrical_power(weight, atmosphere=atm)
            powers.append(power.in_units_of('kW'))

        # Power should increase with altitude
        for i in range(1, len(powers)):
            assert powers[i] > powers[i - 1]

    def test_max_rpm_at_different_altitudes(self, air_taxi):
        """Test maximum RPM constraint at different altitudes."""
        altitudes = [0, 2000, 4000]  # meters

        max_rpms = []
        for alt in altitudes:
            atm = Atmosphere(Length(alt, 'm'))
            max_omega = air_taxi.propellers[0].max_angular_velocity(atmosphere=atm)
            max_rpms.append(max_omega.in_units_of('rpm'))

        # Max RPM should decrease at higher altitudes (lower speed of sound)
        assert max_rpms[1] < max_rpms[0]
        assert max_rpms[2] < max_rpms[1]

    def test_vertiport_comparison(self):
        """Compare operations at sea level vs high altitude vertiport."""
        motor = Motor(max_power=Power(60, 'kW'), efficiency=0.91)
        prop = Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0.72)
        system = PropulsionSystem(motors=[motor], propellers=[prop], num_units=4)

        weight = Force(1500 * 9.81, 'N')

        # Sea level vertiport (e.g., coastal city)
        atm_sl = Atmosphere(Length(0, 'm'))
        power_sl = system.hover_electrical_power(weight, atmosphere=atm_sl)

        # High altitude vertiport (e.g., Denver at 5280 ft)
        atm_denver = Atmosphere(Length(5280, 'ft'))
        power_denver = system.hover_electrical_power(weight, atmosphere=atm_denver)

        # Denver requires more power
        power_increase_pct = (
            (power_denver.in_units_of('kW') - power_sl.in_units_of('kW'))
            / power_sl.in_units_of('kW')
            * 100
        )

        # Expect roughly 8-15% more power at Denver altitude
        assert 5 < power_increase_pct < 20
