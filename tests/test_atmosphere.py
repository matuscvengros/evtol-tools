"""Unit tests for the Atmosphere class and ISA calculations."""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from evtoltools.common import (
    Atmosphere,
    atmosphere_at_altitude,
    sea_level_atmosphere,
    ISA_SEA_LEVEL_TEMPERATURE,
    ISA_SEA_LEVEL_PRESSURE,
    ISA_SEA_LEVEL_DENSITY,
    ISA_SEA_LEVEL_SPEED_OF_SOUND,
    Length,
    Temperature,
    Pressure,
    Density,
    Velocity,
)


class TestISAConstants:
    """Test ISA sea level reference constants."""

    def test_sea_level_temperature(self):
        """Test ISA sea level temperature is 288.15 K (15 degC)."""
        assert ISA_SEA_LEVEL_TEMPERATURE.in_units_of('K') == pytest.approx(288.15, rel=1e-4)

    def test_sea_level_pressure(self):
        """Test ISA sea level pressure is 101325 Pa."""
        assert ISA_SEA_LEVEL_PRESSURE.in_units_of('Pa') == pytest.approx(101325, rel=1e-4)

    def test_sea_level_density(self):
        """Test ISA sea level density is 1.225 kg/m^3."""
        assert ISA_SEA_LEVEL_DENSITY.in_units_of('kg/m^3') == pytest.approx(1.225, rel=1e-3)

    def test_sea_level_speed_of_sound(self):
        """Test ISA sea level speed of sound is ~340.29 m/s."""
        assert ISA_SEA_LEVEL_SPEED_OF_SOUND.in_units_of('m/s') == pytest.approx(340.294, rel=1e-3)


class TestAtmosphereConstruction:
    """Test Atmosphere construction with various inputs."""

    def test_construction_meters(self):
        """Test construction with altitude in meters."""
        atm = Atmosphere(Length(5000, 'm'))
        assert atm.altitude.in_units_of('m') == pytest.approx(5000, rel=1e-6)

    def test_construction_feet(self):
        """Test construction with altitude in feet."""
        atm = Atmosphere(Length(10000, 'ft'))
        assert atm.altitude.in_units_of('ft') == pytest.approx(10000, rel=1e-6)

    def test_construction_with_temperature_offset(self):
        """Test construction with temperature offset."""
        atm = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))
        assert atm.temperature_offset.in_units_of('K') == pytest.approx(20, rel=1e-6)

    def test_construction_no_offset(self):
        """Test construction without temperature offset."""
        atm = Atmosphere(Length(5000, 'm'))
        assert atm.temperature_offset is None


class TestAtmosphereSeaLevel:
    """Test atmospheric properties at sea level."""

    def test_sea_level_temperature(self):
        """Test temperature at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        assert atm.temperature.in_units_of('K') == pytest.approx(288.15, rel=1e-4)

    def test_sea_level_pressure(self):
        """Test pressure at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        assert atm.pressure.in_units_of('Pa') == pytest.approx(101325, rel=1e-4)

    def test_sea_level_density(self):
        """Test density at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        assert atm.density.in_units_of('kg/m^3') == pytest.approx(1.225, rel=1e-3)

    def test_sea_level_speed_of_sound(self):
        """Test speed of sound at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        assert atm.speed_of_sound.in_units_of('m/s') == pytest.approx(340.294, rel=1e-3)


class TestAtmosphereAltitude:
    """Test atmospheric properties at various altitudes."""

    def test_properties_5000m(self):
        """Test properties at 5000m altitude."""
        atm = Atmosphere(Length(5000, 'm'))

        # Expected values from ISA tables
        assert atm.temperature.in_units_of('K') == pytest.approx(255.65, rel=1e-2)
        assert atm.pressure.in_units_of('Pa') == pytest.approx(54019, rel=1e-2)
        assert atm.density.in_units_of('kg/m^3') == pytest.approx(0.7361, rel=1e-2)
        assert atm.speed_of_sound.in_units_of('m/s') == pytest.approx(320.5, rel=1e-2)

    def test_properties_10000m(self):
        """Test properties at 10000m altitude."""
        atm = Atmosphere(Length(10000, 'm'))

        # Expected values from ISA tables
        assert atm.temperature.in_units_of('K') == pytest.approx(223.15, rel=1e-2)
        assert atm.pressure.in_units_of('Pa') == pytest.approx(26436, rel=1e-2)
        assert atm.density.in_units_of('kg/m^3') == pytest.approx(0.4127, rel=1e-2)

    def test_properties_11000m_tropopause(self):
        """Test properties at 11000m (tropopause)."""
        atm = Atmosphere(Length(11000, 'm'))

        # Temperature should be at tropopause value (~216.65 K)
        assert atm.temperature.in_units_of('K') == pytest.approx(216.65, rel=1e-2)

    def test_isa_properties_match(self):
        """Test that ISA properties match when no offset."""
        atm = Atmosphere(Length(5000, 'm'))

        assert atm.temperature.in_units_of('K') == atm.isa_temperature.in_units_of('K')
        assert atm.density.in_units_of('kg/m^3') == atm.isa_density.in_units_of('kg/m^3')
        assert atm.speed_of_sound.in_units_of('m/s') == atm.isa_speed_of_sound.in_units_of('m/s')


class TestAtmosphereTemperatureOffset:
    """Test temperature offset (ISA+/-) effects."""

    def test_hot_day_temperature(self):
        """Test temperature increases with positive offset."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))

        temp_diff = atm_hot.temperature.in_units_of('K') - atm_std.temperature.in_units_of('K')
        assert temp_diff == pytest.approx(20, rel=1e-6)

    def test_cold_day_temperature(self):
        """Test temperature decreases with negative offset."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_cold = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(-10, 'K'))

        temp_diff = atm_std.temperature.in_units_of('K') - atm_cold.temperature.in_units_of('K')
        assert temp_diff == pytest.approx(10, rel=1e-6)

    def test_hot_day_reduces_density(self):
        """Test that hot day reduces density."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))

        # Hot day should have lower density
        assert atm_hot.density.in_units_of('kg/m^3') < atm_std.density.in_units_of('kg/m^3')

    def test_cold_day_increases_density(self):
        """Test that cold day increases density."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_cold = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(-10, 'K'))

        # Cold day should have higher density
        assert atm_cold.density.in_units_of('kg/m^3') > atm_std.density.in_units_of('kg/m^3')

    def test_pressure_unaffected_by_offset(self):
        """Test that pressure is unaffected by temperature offset."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))

        # Pressure should be the same (based on geometric altitude)
        assert atm_hot.pressure.in_units_of('Pa') == pytest.approx(
            atm_std.pressure.in_units_of('Pa'), rel=1e-6
        )

    def test_hot_day_increases_speed_of_sound(self):
        """Test that hot day increases speed of sound."""
        atm_std = Atmosphere(Length(5000, 'm'))
        atm_hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))

        # Speed of sound increases with temperature
        assert atm_hot.speed_of_sound.in_units_of('m/s') > atm_std.speed_of_sound.in_units_of('m/s')

    def test_isa_properties_unchanged_with_offset(self):
        """Test that ISA properties are unaffected by offset."""
        atm_hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))
        atm_std = Atmosphere(Length(5000, 'm'))

        assert atm_hot.isa_temperature.in_units_of('K') == atm_std.isa_temperature.in_units_of('K')
        assert atm_hot.isa_density.in_units_of('kg/m^3') == atm_std.isa_density.in_units_of('kg/m^3')
        assert atm_hot.isa_speed_of_sound.in_units_of('m/s') == atm_std.isa_speed_of_sound.in_units_of('m/s')

    def test_density_ideal_gas_relationship(self):
        """Test that density follows ideal gas law: rho = P / (R * T)."""
        atm = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))

        R = 287.05287  # J/(kg*K)
        P = atm.pressure.in_units_of('Pa')
        T = atm.temperature.in_units_of('K')
        expected_density = P / (R * T)

        assert atm.density.in_units_of('kg/m^3') == pytest.approx(expected_density, rel=1e-4)


class TestAtmosphereFromPressure:
    """Test creation from pressure altitude."""

    def test_from_pressure_sea_level(self):
        """Test creating atmosphere from sea level pressure."""
        atm = Atmosphere.from_pressure_altitude(Pressure(101325, 'Pa'))
        assert atm.altitude.in_units_of('m') == pytest.approx(0, abs=10)

    def test_from_pressure_mid_altitude(self):
        """Test creating atmosphere from mid-altitude pressure."""
        # Get pressure at 5000m, then recreate atmosphere from it
        atm_original = Atmosphere(Length(5000, 'm'))
        pressure = atm_original.pressure

        atm_recreated = Atmosphere.from_pressure_altitude(pressure)
        assert atm_recreated.altitude.in_units_of('m') == pytest.approx(5000, abs=10)

    def test_pressure_altitude_classmethod(self):
        """Test pressure_altitude class method."""
        altitude = Atmosphere.pressure_altitude(Pressure(54019, 'Pa'))
        assert altitude.in_units_of('m') == pytest.approx(5000, abs=100)


class TestAtmosphereFromDensity:
    """Test creation from density altitude."""

    def test_from_density_sea_level(self):
        """Test creating atmosphere from sea level density."""
        atm = Atmosphere.from_density_altitude(Density(1.225, 'kg/m^3'))
        assert atm.altitude.in_units_of('m') == pytest.approx(0, abs=10)

    def test_from_density_mid_altitude(self):
        """Test creating atmosphere from mid-altitude density."""
        # Get density at 5000m, then recreate atmosphere from it
        atm_original = Atmosphere(Length(5000, 'm'))
        density = atm_original.density

        atm_recreated = Atmosphere.from_density_altitude(density)
        assert atm_recreated.altitude.in_units_of('m') == pytest.approx(5000, abs=10)

    def test_density_altitude_classmethod(self):
        """Test density_altitude class method."""
        altitude = Atmosphere.density_altitude(Density(0.7361, 'kg/m^3'))
        assert altitude.in_units_of('m') == pytest.approx(5000, abs=100)


class TestAtmosphereArraySupport:
    """Test NumPy array support for altitude."""

    def test_array_altitude_construction(self):
        """Test construction with array of altitudes."""
        altitudes = np.array([0, 1000, 2000, 3000, 4000, 5000])
        atm = Atmosphere(Length(altitudes, 'm'))

        # Should return array of temperatures
        temps = atm.temperature.magnitude
        assert isinstance(temps, np.ndarray)
        assert len(temps) == 6

    def test_array_temperature_decreases(self):
        """Test temperature decreases with altitude in troposphere."""
        altitudes = np.array([0, 2000, 4000, 6000, 8000, 10000])
        atm = Atmosphere(Length(altitudes, 'm'))

        temps = atm.temperature.magnitude
        # Each temperature should be less than the previous (in troposphere)
        for i in range(1, len(temps)):
            assert temps[i] < temps[i - 1]

    def test_array_pressure_decreases(self):
        """Test pressure decreases with altitude."""
        altitudes = np.array([0, 2000, 4000, 6000, 8000, 10000])
        atm = Atmosphere(Length(altitudes, 'm'))

        pressures = atm.pressure.magnitude
        for i in range(1, len(pressures)):
            assert pressures[i] < pressures[i - 1]

    def test_array_density_decreases(self):
        """Test density decreases with altitude."""
        altitudes = np.array([0, 2000, 4000, 6000, 8000, 10000])
        atm = Atmosphere(Length(altitudes, 'm'))

        densities = atm.density.magnitude
        for i in range(1, len(densities)):
            assert densities[i] < densities[i - 1]

    def test_array_with_temperature_offset(self):
        """Test array support with temperature offset."""
        altitudes = np.array([0, 5000, 10000])
        atm_std = Atmosphere(Length(altitudes, 'm'))
        atm_hot = Atmosphere(Length(altitudes, 'm'), temperature_offset=Temperature(15, 'K'))

        # All temperatures should be 15K higher
        temp_diff = atm_hot.temperature.magnitude - atm_std.temperature.magnitude
        assert_array_almost_equal(temp_diff, np.array([15, 15, 15]), decimal=4)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_atmosphere_at_altitude(self):
        """Test atmosphere_at_altitude function."""
        atm = atmosphere_at_altitude(Length(5000, 'm'))

        assert isinstance(atm, Atmosphere)
        assert atm.altitude.in_units_of('m') == pytest.approx(5000, rel=1e-6)

    def test_atmosphere_at_altitude_with_offset(self):
        """Test atmosphere_at_altitude with temperature offset."""
        atm = atmosphere_at_altitude(
            Length(5000, 'm'),
            temperature_offset=Temperature(10, 'K')
        )

        assert atm.temperature_offset.in_units_of('K') == pytest.approx(10, rel=1e-6)

    def test_sea_level_atmosphere(self):
        """Test sea_level_atmosphere function."""
        atm = sea_level_atmosphere()

        assert isinstance(atm, Atmosphere)
        assert atm.altitude.in_units_of('m') == pytest.approx(0, abs=1e-6)
        assert atm.temperature.in_units_of('K') == pytest.approx(288.15, rel=1e-4)


class TestAtmosphereRepresentation:
    """Test string representations."""

    def test_repr_standard(self):
        """Test repr for standard atmosphere."""
        atm = Atmosphere(Length(5000, 'm'))
        repr_str = repr(atm)

        assert 'Atmosphere' in repr_str
        assert '5000' in repr_str

    def test_repr_with_offset(self):
        """Test repr with temperature offset."""
        atm = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))
        repr_str = repr(atm)

        assert 'ISA+20' in repr_str

    def test_repr_with_negative_offset(self):
        """Test repr with negative temperature offset."""
        atm = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(-10, 'K'))
        repr_str = repr(atm)

        assert 'ISA-10' in repr_str

    def test_str_output(self):
        """Test str output."""
        atm = Atmosphere(Length(5000, 'm'))
        str_output = str(atm)

        assert 'Atmosphere' in str_output
        assert 'T=' in str_output
        assert 'P=' in str_output
        assert 'rho=' in str_output


class TestAtmosphereViscosity:
    """Test viscosity properties."""

    def test_kinematic_viscosity_sea_level(self):
        """Test kinematic viscosity at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        # Sea level kinematic viscosity is approximately 1.46e-5 m^2/s
        assert atm.kinematic_viscosity == pytest.approx(1.46e-5, rel=0.1)

    def test_dynamic_viscosity_sea_level(self):
        """Test dynamic viscosity at sea level."""
        atm = Atmosphere(Length(0, 'm'))
        # Sea level dynamic viscosity is approximately 1.79e-5 Pa*s
        assert atm.dynamic_viscosity == pytest.approx(1.79e-5, rel=0.1)


class TestAtmosphereEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_high_altitude(self):
        """Test at very high altitude (stratosphere)."""
        atm = Atmosphere(Length(20000, 'm'))

        # Temperature in stratosphere is roughly constant around 216.65 K
        assert atm.temperature.in_units_of('K') == pytest.approx(216.65, rel=0.05)

    def test_unit_conversion_consistency(self):
        """Test that unit conversions are consistent."""
        atm_m = Atmosphere(Length(5000, 'm'))
        atm_ft = Atmosphere(Length(5000, 'm').to('ft'))

        # Should give same results regardless of input units
        assert atm_m.temperature.in_units_of('K') == pytest.approx(
            atm_ft.temperature.in_units_of('K'), rel=1e-4
        )
        assert atm_m.pressure.in_units_of('Pa') == pytest.approx(
            atm_ft.pressure.in_units_of('Pa'), rel=1e-4
        )


class TestAtmosphereIntegration:
    """Integration tests for realistic use cases."""

    def test_evtol_cruise_altitude_comparison(self):
        """Compare conditions at typical eVTOL operating altitudes."""
        sea_level = Atmosphere(Length(0, 'm'))
        cruise_1000ft = Atmosphere(Length(1000, 'ft'))
        cruise_3000ft = Atmosphere(Length(3000, 'ft'))

        # Verify expected trends
        assert cruise_1000ft.density.in_units_of('kg/m^3') < sea_level.density.in_units_of('kg/m^3')
        assert cruise_3000ft.density.in_units_of('kg/m^3') < cruise_1000ft.density.in_units_of('kg/m^3')

    def test_hot_day_performance_impact(self):
        """Test hot day impact on air density at typical heliport altitude."""
        # Typical heliport at 1000ft
        altitude = Length(1000, 'ft')

        std_day = Atmosphere(altitude)
        hot_day = Atmosphere(altitude, temperature_offset=Temperature(20, 'K'))  # ISA+20

        # Calculate density ratio (impacts hover power)
        density_ratio = hot_day.density.in_units_of('kg/m^3') / std_day.density.in_units_of('kg/m^3')

        # Hot day should have ~93% density (rough approximation)
        assert density_ratio < 1.0
        assert density_ratio > 0.9

    def test_mission_altitude_profile(self):
        """Test atmosphere across a mission altitude profile."""
        # Typical eVTOL mission: takeoff, climb, cruise, descent, landing
        altitudes = np.array([0, 500, 1000, 1500, 1000, 500, 0])
        atm = Atmosphere(Length(altitudes, 'ft'))

        # Get density profile for power calculations
        densities = atm.density.magnitude

        # Verify we get an array of correct length
        assert len(densities) == 7

        # Verify symmetry (approximately) - takeoff and landing should match
        assert densities[0] == pytest.approx(densities[6], rel=1e-6)
