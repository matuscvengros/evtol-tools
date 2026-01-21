"""Tests for the vehicle weight calculator example script."""

import math
import pytest

import aerosandbox as asb

from evtoltools.common import (
    Mass,
    Length,
    Energy,
    Voltage,
    Capacity,
    Force,
    Power,
)
from evtoltools.components import (
    Payload,
    Battery,
    PropulsionSystem,
    Motor,
    Propeller,
)


def solve_mtow(
    payload_kg: float,
    propulsion_kg: float,
    battery_kg: float,
    structure_fraction: float,
    avionics_fraction: float,
) -> dict:
    """Solve for wet mass using aerosandbox optimizer.

    Duplicated from the example script for testing purposes.
    """
    fixed_mass = payload_kg + propulsion_kg + battery_kg

    opti = asb.Opti()
    mtow = opti.variable(init_guess=fixed_mass * 2)

    structure_mass = mtow * structure_fraction
    avionics_mass = mtow * avionics_fraction

    opti.subject_to(
        mtow == fixed_mass + structure_mass + avionics_mass
    )

    sol = opti.solve(verbose=False)

    return {
        'mtow_kg': sol(mtow),
        'structure_kg': sol(structure_mass),
        'avionics_kg': sol(avionics_mass),
        'payload_kg': payload_kg,
        'propulsion_kg': propulsion_kg,
        'battery_kg': battery_kg,
    }


class TestMtowSolver:
    """Tests for the wet mass solver using aerosandbox."""

    def test_basic_mtow_solution(self):
        """Test that solver finds correct wet mass."""
        payload = 100
        propulsion = 20
        battery = 30
        struct_frac = 0.25
        avionics_frac = 0.05

        solution = solve_mtow(
            payload_kg=payload,
            propulsion_kg=propulsion,
            battery_kg=battery,
            structure_fraction=struct_frac,
            avionics_fraction=avionics_frac,
        )

        # Analytical solution: wet = fixed / (1 - fractions)
        fixed = payload + propulsion + battery
        expected_wet = fixed / (1 - struct_frac - avionics_frac)

        assert abs(solution['mtow_kg'] - expected_wet) < 1e-6

    def test_structure_is_fraction_of_mtow(self):
        """Test that structure mass equals fraction × MTOW."""
        solution = solve_mtow(
            payload_kg=120,
            propulsion_kg=20,
            battery_kg=40,
            structure_fraction=0.30,
            avionics_fraction=0.05,
        )

        expected_structure = solution['mtow_kg'] * 0.30
        assert abs(solution['structure_kg'] - expected_structure) < 1e-6

    def test_avionics_is_fraction_of_mtow(self):
        """Test that avionics mass equals fraction × MTOW."""
        solution = solve_mtow(
            payload_kg=120,
            propulsion_kg=20,
            battery_kg=40,
            structure_fraction=0.30,
            avionics_fraction=0.05,
        )

        expected_avionics = solution['mtow_kg'] * 0.05
        assert abs(solution['avionics_kg'] - expected_avionics) < 1e-6

    def test_mass_balance_closes(self):
        """Test that all components sum to wet mass."""
        solution = solve_mtow(
            payload_kg=100,
            propulsion_kg=25,
            battery_kg=50,
            structure_fraction=0.28,
            avionics_fraction=0.07,
        )

        total = (
            solution['payload_kg'] +
            solution['propulsion_kg'] +
            solution['battery_kg'] +
            solution['structure_kg'] +
            solution['avionics_kg']
        )

        assert abs(total - solution['mtow_kg']) < 1e-6

    def test_higher_battery_increases_mtow(self):
        """Test that increasing battery mass increases MTOW nonlinearly."""
        base_solution = solve_mtow(
            payload_kg=100,
            propulsion_kg=20,
            battery_kg=30,
            structure_fraction=0.30,
            avionics_fraction=0.05,
        )

        heavy_battery_solution = solve_mtow(
            payload_kg=100,
            propulsion_kg=20,
            battery_kg=60,  # Double the battery
            structure_fraction=0.30,
            avionics_fraction=0.05,
        )

        # MTOW should increase by more than just the battery difference
        # because structure/avionics also grow
        battery_diff = 30  # kg
        mtow_diff = heavy_battery_solution['mtow_kg'] - base_solution['mtow_kg']

        # With 35% fractions, adding 30kg battery should add 30/(1-0.35) = 46.15 kg to MTOW
        expected_mtow_diff = battery_diff / (1 - 0.30 - 0.05)
        assert abs(mtow_diff - expected_mtow_diff) < 1e-6

    def test_zero_fractions_gives_simple_sum(self):
        """Test that zero fractions give simple mass sum."""
        solution = solve_mtow(
            payload_kg=100,
            propulsion_kg=20,
            battery_kg=30,
            structure_fraction=0.0,
            avionics_fraction=0.0,
        )

        expected = 100 + 20 + 30
        assert abs(solution['mtow_kg'] - expected) < 1e-6
        assert abs(solution['structure_kg']) < 1e-6
        assert abs(solution['avionics_kg']) < 1e-6


class TestVehicleWeightCalculation:
    """Tests for vehicle weight calculation logic."""

    def test_battery_sizing_from_energy(self):
        """Test battery sizing from target energy."""
        battery = Battery.from_target_energy(
            target_energy=Energy(10, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion',
        )

        # Should size to at least target energy
        actual_energy = battery.energy_capacity.in_units_of('kWh')
        assert actual_energy >= 10.0

        # Should have configuration info
        assert 'configuration' in battery.info
        assert battery.info['configuration'] is not None

    def test_propulsion_system_setup(self):
        """Test propulsion system configuration."""
        motor = Motor(
            max_power=Power(20, 'kW'),
            efficiency=0.90,
            mass=Mass(5, 'kg'),
        )

        propeller = Propeller(
            diameter=Length(2, 'm'),
            num_blades=2,
            efficiency_hover=0.70,
        )

        propulsion = PropulsionSystem(
            motors=[motor],
            propellers=[propeller],
            num_units=4,
        )

        # Verify system properties
        assert propulsion.num_units == 4
        assert len(propulsion.motors) == 4
        assert len(propulsion.propellers) == 4
        assert abs(propulsion.average_motor_efficiency - 0.90) < 0.001
        assert abs(propulsion.average_figure_of_merit - 0.70) < 0.001

        # Total disk area = 4 * pi * (1m)^2 = 4 * pi m^2
        expected_area = 4 * math.pi * 1.0**2
        assert abs(propulsion.total_disk_area.in_units_of('m^2') - expected_area) < 0.01

        # Total max power = 4 * 20 kW = 80 kW
        assert abs(propulsion.total_max_electrical_power.in_units_of('kW') - 80) < 0.001


class TestHoverPowerCalculation:
    """Tests for hover power calculation logic."""

    def test_hover_power_chain(self):
        """Test the hover power calculation chain: ideal -> shaft -> electrical."""
        motor = Motor(
            max_power=Power(20, 'kW'),
            efficiency=0.90,
        )

        propeller = Propeller(
            diameter=Length(2, 'm'),
            efficiency_hover=0.70,
        )

        propulsion = PropulsionSystem(
            motors=[motor],
            propellers=[propeller],
            num_units=4,
        )

        # Create a test thrust (approx 350 kg vehicle)
        test_mass_kg = 350
        thrust = Force(test_mass_kg * 9.81, 'N')

        # Calculate power chain
        ideal_power = propulsion.hover_power_ideal(thrust)
        shaft_power = propulsion.hover_shaft_power(thrust)
        electrical_power = propulsion.hover_electrical_power(thrust)

        # Verify power increases through chain
        ideal_w = ideal_power.in_units_of('W')
        shaft_w = shaft_power.in_units_of('W')
        electrical_w = electrical_power.in_units_of('W')

        assert shaft_w > ideal_w
        assert electrical_w > shaft_w

        # Verify relationships
        # shaft = ideal / (FM * installation_eff)
        fm = propulsion.average_figure_of_merit
        inst_eff = propulsion.installation_efficiency
        expected_shaft = ideal_w / (fm * inst_eff)
        assert abs(shaft_w - expected_shaft) < 1.0

        # electrical = shaft / motor_eff
        motor_eff = propulsion.average_motor_efficiency
        expected_electrical = shaft_w / motor_eff
        assert abs(electrical_w - expected_electrical) < 1.0

    def test_ideal_hover_power_formula(self):
        """Test ideal hover power matches momentum theory formula."""
        propeller = Propeller(diameter=Length(2, 'm'))
        motor = Motor(max_power=Power(10, 'kW'))
        propulsion = PropulsionSystem(
            motors=[motor],
            propellers=[propeller],
            num_units=4,
        )

        thrust_n = 3000  # N
        rho = 1.225  # kg/m^3 (sea level)
        area_m2 = propulsion.total_disk_area.in_units_of('m^2')

        # P_ideal = T^(3/2) / sqrt(2 * rho * A)
        expected_power = thrust_n ** 1.5 / math.sqrt(2 * rho * area_m2)

        thrust = Force(thrust_n, 'N')
        actual_power = propulsion.hover_power_ideal(thrust).in_units_of('W')

        assert abs(actual_power - expected_power) < 1.0


class TestIntegration:
    """Integration tests for complete vehicle weight calculation."""

    def test_full_vehicle_calculation_with_mtow(self):
        """Test complete vehicle weight calculation using wet mass fractions."""
        # Configuration
        structure_fraction = 0.30
        avionics_fraction = 0.05
        payload_mass = Mass(120, 'kg')

        # Create components
        payload = Payload(payload_mass)
        payload_kg = payload.mass.in_units_of('kg')

        battery = Battery.from_target_energy(
            target_energy=Energy(10, 'kWh'),
            target_voltage=Voltage(48, 'V'),
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
        )
        battery_kg = battery.mass.in_units_of('kg')

        motor = Motor(
            max_power=Power(20, 'kW'),
            efficiency=0.90,
            mass=Mass(5, 'kg'),
        )

        propeller = Propeller(
            diameter=Length(2, 'm'),
            efficiency_hover=0.70,
        )

        propulsion = PropulsionSystem(
            motors=[motor],
            propellers=[propeller],
            num_units=4,
        )
        propulsion_kg = propulsion.mass.in_units_of('kg')

        # Solve for wet mass
        solution = solve_mtow(
            payload_kg=payload_kg,
            propulsion_kg=propulsion_kg,
            battery_kg=battery_kg,
            structure_fraction=structure_fraction,
            avionics_fraction=avionics_fraction,
        )

        mtow_kg = solution['mtow_kg']

        # Verify structure and avionics are correct fractions
        assert abs(solution['structure_kg'] / mtow_kg - structure_fraction) < 1e-6
        assert abs(solution['avionics_kg'] / mtow_kg - avionics_fraction) < 1e-6

        # Calculate hover power
        thrust = Force(mtow_kg * 9.81, 'N')
        electrical_power = propulsion.hover_electrical_power(thrust)

        # Verify power is reasonable and within motor limits
        power_kw = electrical_power.in_units_of('kW')
        max_power_kw = propulsion.total_max_electrical_power.in_units_of('kW')

        assert power_kw > 0
        assert power_kw < max_power_kw  # Should have power margin

    def test_weight_fractions_match_input(self):
        """Test that solved weight fractions match input fractions."""
        struct_frac = 0.28
        avionics_frac = 0.07

        solution = solve_mtow(
            payload_kg=150,
            propulsion_kg=25,
            battery_kg=45,
            structure_fraction=struct_frac,
            avionics_fraction=avionics_frac,
        )

        # Calculate actual fractions from solution
        actual_struct_frac = solution['structure_kg'] / solution['mtow_kg']
        actual_avionics_frac = solution['avionics_kg'] / solution['mtow_kg']

        assert abs(actual_struct_frac - struct_frac) < 1e-6
        assert abs(actual_avionics_frac - avionics_frac) < 1e-6
