"""Tests for all concrete quantity classes."""

from __future__ import annotations

import pytest
from pint import Quantity as PintQuantity

from evtol_tools.units.config import SI_DEFAULTS
from evtol_tools.units.quantities import (
    AngularVelocity,
    Area,
    Capacity,
    Current,
    Density,
    Energy,
    Force,
    Length,
    Mass,
    Moment,
    Power,
    Pressure,
    Temperature,
    Time,
    Velocity,
    Voltage,
    Volume,
)

QUANTITY_CLASSES = [
    Mass,
    Length,
    Time,
    Temperature,
    Velocity,
    Force,
    Moment,
    Power,
    Energy,
    Area,
    Volume,
    Density,
    Pressure,
    AngularVelocity,
    Voltage,
    Current,
    Capacity,
]

# Alternate units for testing conversion on each type.
ALT_UNITS: dict[str, str] = {
    "mass": "lb",
    "length": "ft",
    "time": "min",
    "temperature": "degF",
    "velocity": "ft/s",
    "force": "lbf",
    "moment": "lbf*ft",
    "power": "hp",
    "energy": "kJ",
    "area": "ft**2",
    "volume": "L",
    "density": "lb/ft**3",
    "pressure": "psi",
    "angular_velocity": "rpm",
    "voltage": "mV",
    "current": "mA",
    "capacity": "mA*h",
}


class TestDefaultSIUnit:
    """Each quantity type constructs with SI default when no unit is given."""

    @pytest.mark.parametrize("cls", QUANTITY_CLASSES, ids=lambda c: c.__name__)
    def test_default_si_unit(self, cls):
        q = cls(1.0)
        si_unit = SI_DEFAULTS[cls._quantity_type]
        # Verify the stored unit is the expected SI unit (pint may expand abbreviations)
        from evtol_tools.units.registry import ureg

        expected_unit = str(ureg.parse_expression(si_unit).units)
        assert q.units == expected_unit


class TestConversion:
    """Each quantity type converts to an alternate unit and back."""

    @pytest.mark.parametrize("cls", QUANTITY_CLASSES, ids=lambda c: c.__name__)
    def test_roundtrip_conversion(self, cls):
        original_value = 100.0
        q = cls(original_value)
        alt_unit = ALT_UNITS[cls._quantity_type]

        # Convert to alt unit
        q_alt = q(alt_unit)
        assert isinstance(q_alt, cls)

        # Convert back to SI
        from evtol_tools.units.registry import ureg

        si_unit = SI_DEFAULTS[cls._quantity_type]
        q_back = q_alt(str(ureg.parse_expression(si_unit).units))
        assert pytest.approx(q_back.value, rel=1e-6) == original_value


class TestSpecificConversions:
    """Spot-check specific well-known conversions."""

    def test_mass_kg_to_lb(self):
        m = Mass(1, "kg")
        assert pytest.approx(m("lb").value, rel=1e-3) == 2.20462

    def test_length_m_to_ft(self):
        length = Length(1, "m")
        assert pytest.approx(length("ft").value, rel=1e-3) == 3.28084

    def test_velocity_ms_to_fts(self):
        v = Velocity(1, "m/s")
        assert pytest.approx(v("ft/s").value, rel=1e-3) == 3.28084

    def test_force_n_to_lbf(self):
        f = Force(1, "N")
        assert pytest.approx(f("lbf").value, rel=1e-3) == 0.224809

    def test_power_w_to_hp(self):
        p = Power(746, "W")
        assert pytest.approx(p("hp").value, rel=1e-2) == 1.0

    def test_pressure_pa_to_psi(self):
        p = Pressure(6894.76, "Pa")
        assert pytest.approx(p("psi").value, rel=1e-3) == 1.0

    def test_temperature_k_to_degf(self):
        t = Temperature(373.15, "K")
        assert pytest.approx(t("degF").value, rel=1e-2) == 212.0

    def test_angular_velocity_rads_to_rpm(self):
        av = AngularVelocity(1, "rad/s")
        assert pytest.approx(av("rpm").value, rel=1e-3) == 60 / (2 * 3.14159265)

    def test_energy_j_to_kj(self):
        e = Energy(1000, "J")
        assert pytest.approx(e("kJ").value, rel=1e-6) == 1.0

    def test_area_m2_to_ft2(self):
        a = Area(1, "m**2")
        assert pytest.approx(a("ft**2").value, rel=1e-3) == 10.7639

    def test_volume_m3_to_l(self):
        v = Volume(1, "m**3")
        assert pytest.approx(v("L").value, rel=1e-6) == 1000.0

    def test_density_kgm3_to_lbft3(self):
        d = Density(1, "kg/m**3")
        assert pytest.approx(d("lb/ft**3").value, rel=1e-3) == 0.062428

    def test_voltage_v_to_mv(self):
        v = Voltage(1, "V")
        assert pytest.approx(v("mV").value, rel=1e-6) == 1000.0

    def test_current_a_to_ma(self):
        c = Current(1, "A")
        assert pytest.approx(c("mA").value, rel=1e-6) == 1000.0

    def test_capacity_ah_to_mah(self):
        c = Capacity(1, "A*h")
        assert pytest.approx(c("mA*h").value, rel=1e-6) == 1000.0

    def test_moment_nm_to_lbf_ft(self):
        m = Moment(1, "N*m")
        assert pytest.approx(m("lbf*ft").value, rel=1e-3) == 0.737562


class TestCrossTypeArithmetic:
    """Cross-type arithmetic returns raw pint Quantity."""

    def test_force_div_mass(self):
        f = Force(100, "N")
        m = Mass(10, "kg")
        result = f / m
        assert isinstance(result, PintQuantity)

    def test_mass_mul_velocity(self):
        m = Mass(10, "kg")
        v = Velocity(5, "m/s")
        result = m * v
        assert isinstance(result, PintQuantity)

    def test_power_div_velocity(self):
        p = Power(1000, "W")
        v = Velocity(10, "m/s")
        result = p / v
        assert isinstance(result, PintQuantity)
