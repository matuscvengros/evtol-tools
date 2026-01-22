"""Tests for Propulsion components: Propeller, Motor, PropulsionSystem."""

import pytest
import math

from evtoltools.common import (
    Mass, Power, Length, Area, Velocity, AngularVelocity, Force, Density,
    Pressure, Frequency
)
from evtoltools.components import PropulsionSystem, Motor, Propeller
from evtoltools.components.base import BaseComponent


class TestPropellerConstruction:
    """Tests for Propeller construction."""

    def test_basic_construction(self):
        prop = Propeller(diameter=Length(1.5, 'm'))
        assert prop.diameter.in_units_of('m') == 1.5
        assert prop.num_blades == 2  # Default

    def test_with_all_parameters(self):
        prop = Propeller(
            diameter=Length(2.0, 'm'),
            num_blades=3,
            efficiency_hover=0.75,
            efficiency_cruise=0.82,
            tip_mach_limit=0.8,
        )
        assert prop.num_blades == 3
        assert prop.efficiency_hover == 0.75
        assert prop.efficiency_cruise == 0.82
        assert prop.tip_mach_limit == 0.8

    def test_diameter_in_feet(self):
        prop = Propeller(diameter=Length(5, 'ft'))
        assert abs(prop.diameter.in_units_of('m') - 1.524) < 0.01

    def test_invalid_num_blades(self):
        with pytest.raises(ValueError, match="num_blades"):
            Propeller(diameter=Length(1.5, 'm'), num_blades=1)

    def test_invalid_efficiency_hover_zero(self):
        with pytest.raises(ValueError, match="efficiency_hover"):
            Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0)

    def test_invalid_efficiency_hover_above_one(self):
        with pytest.raises(ValueError, match="efficiency_hover"):
            Propeller(diameter=Length(1.5, 'm'), efficiency_hover=1.5)

    def test_invalid_efficiency_cruise(self):
        with pytest.raises(ValueError, match="efficiency_cruise"):
            Propeller(diameter=Length(1.5, 'm'), efficiency_cruise=0)

    def test_invalid_tip_mach_limit(self):
        with pytest.raises(ValueError, match="tip_mach_limit"):
            Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=1.5)


class TestPropellerGeometry:
    """Tests for Propeller geometry properties."""

    def test_radius(self):
        prop = Propeller(diameter=Length(2.0, 'm'))
        assert abs(prop.radius.in_units_of('m') - 1.0) < 0.001

    def test_disk_area(self):
        prop = Propeller(diameter=Length(2.0, 'm'))
        # Area = pi * r^2 = pi * 1^2 = pi
        expected_area = math.pi
        assert abs(prop.disk_area.in_units_of('m^2') - expected_area) < 0.001

    def test_disk_area_1_5m(self):
        prop = Propeller(diameter=Length(1.5, 'm'))
        # Area = pi * 0.75^2 = pi * 0.5625 ≈ 1.767
        expected_area = math.pi * 0.75 ** 2
        assert abs(prop.disk_area.in_units_of('m^2') - expected_area) < 0.001


class TestPropellerTipSpeed:
    """Tests for Propeller tip speed calculations."""

    def test_tip_speed_from_rad_s(self):
        prop = Propeller(diameter=Length(2.0, 'm'))  # r = 1m
        omega = AngularVelocity(100, 'rad/s')
        # V_tip = omega * r = 100 * 1 = 100 m/s
        tip = prop.tip_speed(omega)
        assert abs(tip.in_units_of('m/s') - 100) < 0.001

    def test_tip_speed_from_rpm(self):
        prop = Propeller(diameter=Length(2.0, 'm'))  # r = 1m
        omega = AngularVelocity(1000, 'rpm')
        # omega_rad_s = 1000 * 2*pi / 60 ≈ 104.72 rad/s
        # V_tip = 104.72 * 1 = 104.72 m/s
        tip = prop.tip_speed(omega)
        expected = 1000 * 2 * math.pi / 60
        assert abs(tip.in_units_of('m/s') - expected) < 0.1

    def test_angular_velocity_from_tip_speed(self):
        prop = Propeller(diameter=Length(2.0, 'm'))  # r = 1m
        tip = Velocity(150, 'm/s')
        omega = prop.angular_velocity_from_tip_speed(tip)
        # omega = V_tip / r = 150 / 1 = 150 rad/s
        assert abs(omega.in_units_of('rad/s') - 150) < 0.001


class TestPropellerMachLimits:
    """Tests for Propeller Mach number calculations."""

    def test_max_tip_speed_default_sound(self):
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)
        max_tip = prop.max_tip_speed()
        # Default speed of sound = 343 m/s
        # Max tip = 343 * 0.85 = 291.55 m/s
        assert abs(max_tip.in_units_of('m/s') - 291.55) < 0.1

    def test_max_tip_speed_custom_sound(self):
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.8)
        speed_of_sound = Velocity(320, 'm/s')
        max_tip = prop.max_tip_speed(speed_of_sound)
        # Max tip = 320 * 0.8 = 256 m/s
        assert abs(max_tip.in_units_of('m/s') - 256) < 0.1

    def test_max_angular_velocity(self):
        prop = Propeller(diameter=Length(2.0, 'm'), tip_mach_limit=0.85)
        max_omega = prop.max_angular_velocity()
        # Max tip = 343 * 0.85 = 291.55 m/s
        # omega = V_tip / r = 291.55 / 1 = 291.55 rad/s
        assert abs(max_omega.in_units_of('rad/s') - 291.55) < 0.1

    def test_tip_mach_number(self):
        prop = Propeller(diameter=Length(2.0, 'm'))  # r = 1m
        omega = AngularVelocity(200, 'rad/s')
        # V_tip = 200 * 1 = 200 m/s
        # Mach = 200 / 343 ≈ 0.583
        mach = prop.tip_mach_number(omega)
        assert abs(mach - 0.583) < 0.01


class TestPropellerFrequency:
    """Tests for Propeller frequency calculations."""

    def test_frequency(self):
        prop = Propeller(diameter=Length(1.5, 'm'))
        omega = AngularVelocity(100, 'rad/s')
        # freq = omega / (2*pi) = 100 / 6.283 ≈ 15.92 Hz
        freq = prop.frequency(omega)
        assert isinstance(freq, Frequency)
        assert abs(freq.in_units_of('Hz') - 15.92) < 0.1


class TestPropellerSINormalization:
    """Tests for Propeller SI unit normalization on construction."""

    def test_diameter_normalized_to_meters(self):
        """Diameter should be normalized to meters (SI default)."""
        prop = Propeller(diameter=Length(150, 'cm'))  # Input in cm
        assert prop.diameter.units == 'meter'
        assert abs(prop.diameter.magnitude - 1.5) < 0.0001

    def test_diameter_from_feet_normalized(self):
        """Diameter in feet should be normalized to meters."""
        prop = Propeller(diameter=Length(5, 'ft'))  # Input in feet
        assert prop.diameter.units == 'meter'
        # 5 ft ≈ 1.524 m
        assert abs(prop.diameter.magnitude - 1.524) < 0.01

    def test_normalized_diameter_used_in_calculations(self):
        """Verify normalized diameter is used correctly in calculations."""
        prop = Propeller(diameter=Length(200, 'cm'))  # 2 meters
        # Radius should be 1m
        assert abs(prop.radius.in_units_of('m') - 1.0) < 0.001
        # Disk area should be pi m^2
        import math
        assert abs(prop.disk_area.in_units_of('m^2') - math.pi) < 0.001


class TestMotorSINormalization:
    """Tests for Motor SI unit normalization on construction."""

    def test_max_power_normalized_to_watts(self):
        """Max power should be normalized to watts (SI default)."""
        motor = Motor(max_power=Power(50, 'kW'))  # Input in kW
        assert motor.max_power.units == 'watt'
        assert abs(motor.max_power.magnitude - 50000) < 0.1

    def test_mass_normalized_to_kg(self):
        """Mass should be normalized to kg (SI default)."""
        motor = Motor(
            max_power=Power(50, 'kW'),
            mass=Mass(8000, 'g'),  # Input in grams
        )
        assert motor.mass.units == 'kilogram'
        assert abs(motor.mass.magnitude - 8.0) < 0.0001

    def test_max_rpm_normalized_to_rad_per_second(self):
        """Max RPM should be normalized to rad/s (SI default)."""
        motor = Motor(
            max_power=Power(50, 'kW'),
            max_rpm=AngularVelocity(6000, 'rpm'),  # Input in RPM
        )
        assert motor.max_rpm.units == 'radian / second'
        # 6000 RPM = 6000 * 2*pi / 60 rad/s ≈ 628.32 rad/s
        import math
        expected = 6000 * 2 * math.pi / 60
        assert abs(motor.max_rpm.magnitude - expected) < 0.1


class TestMotorConstruction:
    """Tests for Motor construction."""

    def test_basic_construction(self):
        motor = Motor(max_power=Power(50, 'kW'))
        assert motor.max_power.in_units_of('kW') == 50
        assert motor.efficiency == 0.92  # Default

    def test_with_all_parameters(self):
        motor = Motor(
            max_power=Power(75, 'kW'),
            efficiency=0.92,
            mass=Mass(8, 'kg'),
            kv_rating=100,
        )
        assert motor.efficiency == 0.92
        assert motor.mass.in_units_of('kg') == 8
        assert motor.kv_rating == 100

    def test_invalid_efficiency_zero(self):
        with pytest.raises(ValueError, match="efficiency"):
            Motor(max_power=Power(50, 'kW'), efficiency=0)

    def test_invalid_efficiency_above_one(self):
        with pytest.raises(ValueError, match="efficiency"):
            Motor(max_power=Power(50, 'kW'), efficiency=1.1)

    def test_invalid_power_zero(self):
        with pytest.raises(ValueError, match="max_power"):
            Motor(max_power=Power(0, 'kW'))


class TestMotorPowerConversions:
    """Tests for Motor power conversion methods."""

    def test_shaft_power(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        # 10kW electrical -> 9kW shaft
        shaft = motor.shaft_power(Power(10, 'kW'))
        assert abs(shaft.in_units_of('kW') - 9) < 0.001

    def test_electrical_power(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        # 9kW shaft -> 10kW electrical
        elec = motor.electrical_power(Power(9, 'kW'))
        assert abs(elec.in_units_of('kW') - 10) < 0.001

    def test_max_shaft_power(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.92)
        # 50kW * 0.92 = 46kW
        assert abs(motor.max_shaft_power.in_units_of('kW') - 46) < 0.001


class TestMotorProperties:
    """Tests for Motor properties."""

    def test_power_to_weight_with_mass(self):
        motor = Motor(
            max_power=Power(50, 'kW'),
            mass=Mass(10, 'kg'),
        )
        # 50 kW / 10 kg = 5 kW/kg
        assert abs(motor.power_to_weight - 5.0) < 0.001

    def test_power_to_weight_without_mass(self):
        motor = Motor(max_power=Power(50, 'kW'))
        assert motor.power_to_weight == 0.0

    def test_repr(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.92)
        repr_str = repr(motor)
        assert 'Motor' in repr_str
        assert '50' in repr_str


class TestPropulsionSystemConstruction:
    """Tests for PropulsionSystem construction."""

    def test_single_unit(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(motors=[motor], propellers=[prop])
        assert system.num_units == 1

    def test_replicated_units(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        assert len(system.motors) == 4
        assert len(system.propellers) == 4

    def test_explicit_units(self):
        motors = [Motor(max_power=Power(50, 'kW')) for _ in range(4)]
        props = [Propeller(diameter=Length(1.5, 'm')) for _ in range(4)]
        system = PropulsionSystem(
            motors=motors,
            propellers=props,
            num_units=4,
        )
        assert len(system.motors) == 4

    def test_mismatched_motors_propellers(self):
        motors = [Motor(max_power=Power(50, 'kW')) for _ in range(3)]
        props = [Propeller(diameter=Length(1.5, 'm')) for _ in range(4)]
        with pytest.raises(ValueError, match="must match"):
            PropulsionSystem(
                motors=motors,
                propellers=props,
                num_units=4,
            )

    def test_invalid_installation_efficiency(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        with pytest.raises(ValueError, match="installation_efficiency"):
            PropulsionSystem(
                motors=[motor],
                propellers=[prop],
                installation_efficiency=1.5,
            )


class TestPropulsionSystemProperties:
    """Tests for PropulsionSystem properties."""

    def test_component_type(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(motors=[motor], propellers=[prop])
        assert system.component_type == 'propulsion'

    def test_is_base_component(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(motors=[motor], propellers=[prop])
        assert isinstance(system, BaseComponent)

    def test_mass_with_motor_mass(self):
        motor = Motor(max_power=Power(50, 'kW'), mass=Mass(10, 'kg'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        # 4 * 10kg = 40kg
        assert abs(system.mass.in_units_of('kg') - 40) < 0.01

    def test_mass_without_motor_mass(self):
        motor = Motor(max_power=Power(50, 'kW'))  # No mass specified
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(motors=[motor], propellers=[prop])
        assert system.mass.in_units_of('kg') == 0

    def test_total_disk_area(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(2.0, 'm'))  # Area = pi m^2
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        # 4 * pi = 4pi m^2
        expected = 4 * math.pi
        assert abs(system.total_disk_area.in_units_of('m^2') - expected) < 0.01

    def test_total_max_electrical_power(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        # 4 * 50kW = 200kW
        assert abs(system.total_max_electrical_power.in_units_of('kW') - 200) < 0.01

    def test_total_max_shaft_power(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        # 4 * 45kW = 180kW
        assert abs(system.total_max_shaft_power.in_units_of('kW') - 180) < 0.01


class TestPropulsionSystemEfficiency:
    """Tests for PropulsionSystem efficiency calculations."""

    def test_average_motor_efficiency(self):
        motors = [
            Motor(max_power=Power(50, 'kW'), efficiency=0.90),
            Motor(max_power=Power(50, 'kW'), efficiency=0.92),
        ]
        props = [Propeller(diameter=Length(1.5, 'm')) for _ in range(2)]
        system = PropulsionSystem(motors=motors, propellers=props, num_units=2)
        # Average = (0.90 + 0.92) / 2 = 0.91
        assert abs(system.average_motor_efficiency - 0.91) < 0.001

    def test_average_figure_of_merit(self):
        motor = Motor(max_power=Power(50, 'kW'))
        props = [
            Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0.70),
            Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0.75),
        ]
        motors = [motor, Motor(max_power=Power(50, 'kW'))]
        system = PropulsionSystem(motors=motors, propellers=props, num_units=2)
        # Average = (0.70 + 0.75) / 2 = 0.725
        assert abs(system.average_figure_of_merit - 0.725) < 0.001


class TestPropulsionSystemHoverPower:
    """Tests for PropulsionSystem hover power calculations."""

    def test_hover_power_ideal(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(2.0, 'm'))  # Area = pi per prop
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        thrust = Force(10000, 'N')
        rho = Density(1.225, 'kg/m^3')

        # P_ideal = T^1.5 / sqrt(2 * rho * A)
        # A = 4 * pi ≈ 12.566 m^2
        # P_ideal = 10000^1.5 / sqrt(2 * 1.225 * 12.566)
        # P_ideal = 1000000 / sqrt(30.79) ≈ 180277 W
        ideal = system.hover_power_ideal(thrust, rho)
        expected = 10000 ** 1.5 / math.sqrt(2 * 1.225 * 4 * math.pi)
        assert abs(ideal.in_units_of('W') - expected) < 100

    def test_hover_power_ideal_default_density(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(motors=[motor], propellers=[prop], num_units=4)
        thrust = Force(15000, 'N')

        # Should use default density of 1.225 kg/m^3
        ideal = system.hover_power_ideal(thrust)
        assert ideal.in_units_of('W') > 0

    def test_hover_shaft_power(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0.70)
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
            installation_efficiency=0.95,
        )
        thrust = Force(10000, 'N')

        # Shaft power = ideal / (FM * installation_eff)
        shaft = system.hover_shaft_power(thrust)
        ideal = system.hover_power_ideal(thrust)
        expected = ideal.in_units_of('W') / (0.70 * 0.95)
        assert abs(shaft.in_units_of('W') - expected) < 100

    def test_hover_electrical_power(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        prop = Propeller(diameter=Length(1.5, 'm'), efficiency_hover=0.70)
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
            installation_efficiency=0.95,
        )
        thrust = Force(10000, 'N')

        # Electrical = shaft / motor_efficiency
        elec = system.hover_electrical_power(thrust)
        shaft = system.hover_shaft_power(thrust)
        expected = shaft.in_units_of('W') / 0.90
        assert abs(elec.in_units_of('W') - expected) < 100


class TestPropulsionSystemPerformanceMetrics:
    """Tests for PropulsionSystem performance metrics."""

    def test_disk_loading(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(2.0, 'm'))  # Area = pi
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        thrust = Force(10000, 'N')

        # Disk loading = T / A = 10000 / (4*pi) ≈ 795.8 N/m^2
        dl = system.disk_loading(thrust)
        assert isinstance(dl, Pressure)
        expected = 10000 / (4 * math.pi)
        assert abs(dl.in_units_of('Pa') - expected) < 1

    def test_power_loading(self):
        motor = Motor(max_power=Power(50, 'kW'), efficiency=0.90)
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        thrust = Force(10000, 'N')

        # Power loading = T / P_shaft = 10000 / 180000 ≈ 0.0556 N/W
        pl = system.power_loading(thrust)
        shaft_power = 4 * 50 * 1000 * 0.90  # 180kW
        expected = 10000 / shaft_power
        assert abs(pl - expected) < 0.001

    def test_induced_velocity(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(2.0, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        thrust = Force(10000, 'N')
        rho = Density(1.225, 'kg/m^3')

        # v_i = sqrt(T / (2 * rho * A))
        v_i = system.induced_velocity(thrust, rho)
        expected = math.sqrt(10000 / (2 * 1.225 * 4 * math.pi))
        assert abs(v_i.in_units_of('m/s') - expected) < 0.1

    def test_max_tip_speed(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'), tip_mach_limit=0.85)
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )

        max_tip = system.max_tip_speed()
        # Should be limited by the propeller's Mach limit
        expected = 343 * 0.85
        assert abs(max_tip.in_units_of('m/s') - expected) < 0.1


class TestPropulsionSystemRepr:
    """Tests for PropulsionSystem representation."""

    def test_repr(self):
        motor = Motor(max_power=Power(50, 'kW'))
        prop = Propeller(diameter=Length(1.5, 'm'))
        system = PropulsionSystem(
            motors=[motor],
            propellers=[prop],
            num_units=4,
        )
        repr_str = repr(system)
        assert 'PropulsionSystem' in repr_str
        assert '4 units' in repr_str

