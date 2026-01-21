#!/usr/bin/env python3
"""Vehicle weight calculator example for eVTOL aircraft.

This script demonstrates how to use the evtoltools package to:
1. Calculate component masses based on MTOW fractions
2. Solve the implicit weight equation using aerosandbox optimizer
3. Compute total vehicle weight (MTOW)
4. Calculate hover power requirements

The key insight is that structure and avionics masses are fractions of MTOW,
but battery mass also contributes to MTOW. This creates a circular dependency
that must be solved numerically:

    MTOW = payload + structure + avionics + propulsion + battery
    where: structure = MTOW × structure_fraction
           avionics = MTOW × avionics_fraction

Run with: python examples/vehicle_weight_calculator.py
"""

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

# =============================================================================
# USER-CONFIGURABLE PARAMETERS
# =============================================================================

# MTOW fractions
STRUCTURE_FRACTION = 0.30                 # Structure as fraction of MTOW
AVIONICS_FRACTION = 0.05                  # Avionics as fraction of MTOW

# Payload
PAYLOAD_MASS = Mass(120, 'kg')           # Payload mass

# Battery configuration
TARGET_BATTERY_ENERGY = Energy(10, 'kWh')  # Target battery energy
TARGET_BATTERY_VOLTAGE = Voltage(48, 'V')  # Target battery voltage
CELL_CAPACITY = Capacity(5000, 'mAh')      # Individual cell capacity
CELL_MASS = Mass(70, 'g')                  # Individual cell mass

# =============================================================================
# FIXED PROPULSION CONFIGURATION
# =============================================================================

NUM_MOTORS = 4                            # Total number of motors
PROPELLER_DIAMETER = Length(2, 'm')       # Propeller diameter
MOTOR_EFFICIENCY = 0.90                   # Motor + ESC efficiency
PROPELLER_FM = 0.70                       # Propeller Figure of Merit

# Motor power (sized generously for hover margin)
MOTOR_MAX_POWER = Power(40, 'kW')         # Per-motor electrical power
MOTOR_MASS = Mass(5, 'kg')                # Per-motor mass

# =============================================================================
# CONSTANTS
# =============================================================================

GRAVITY = 9.81  # m/s^2


def solve_mtow(
    payload_kg: float,
    propulsion_kg: float,
    battery_kg: float,
    structure_fraction: float,
    avionics_fraction: float,
) -> dict:
    """Solve for MTOW using aerosandbox optimizer.

    The implicit equation is:
        MTOW = payload + propulsion + battery + MTOW*(struct_frac + avionics_frac)

    Rearranging:
        MTOW * (1 - struct_frac - avionics_frac) = payload + propulsion + battery

    This could be solved analytically, but we use aerosandbox to demonstrate
    the approach for more complex cases where analytical solutions don't exist.

    Args:
        payload_kg: Payload mass in kg
        propulsion_kg: Propulsion system mass in kg
        battery_kg: Battery mass in kg
        structure_fraction: Structure mass as fraction of MTOW
        avionics_fraction: Avionics mass as fraction of MTOW

    Returns:
        Dictionary with solved masses
    """
    # Fixed masses (don't depend on MTOW)
    fixed_mass = payload_kg + propulsion_kg + battery_kg

    # Set up optimization problem
    opti = asb.Opti()

    # Variable: MTOW
    mtow = opti.variable(init_guess=fixed_mass * 2)  # Initial guess

    # Constraint: MTOW equation
    # MTOW = fixed_mass + structure + avionics
    # MTOW = fixed_mass + MTOW*structure_fraction + MTOW*avionics_fraction
    structure_mass = mtow * structure_fraction
    avionics_mass = mtow * avionics_fraction

    opti.subject_to(
        mtow == fixed_mass + structure_mass + avionics_mass
    )

    # Solve (no objective needed - just finding feasible point)
    sol = opti.solve(verbose=False)

    # Extract solution
    mtow_solved = sol(mtow)
    structure_solved = sol(structure_mass)
    avionics_solved = sol(avionics_mass)

    return {
        'mtow_kg': mtow_solved,
        'structure_kg': structure_solved,
        'avionics_kg': avionics_solved,
        'payload_kg': payload_kg,
        'propulsion_kg': propulsion_kg,
        'battery_kg': battery_kg,
    }


def main():
    """Calculate vehicle weight and hover power requirements."""

    print("=" * 60)
    print("eVTOL Vehicle Weight Calculator (MTOW Fractions)")
    print("=" * 60)
    print()

    # -------------------------------------------------------------------------
    # Create fixed-mass components
    # -------------------------------------------------------------------------

    # Payload
    payload = Payload(PAYLOAD_MASS, description='Passengers/cargo')
    payload_kg = payload.mass.in_units_of('kg')

    # Battery (sized from target energy)
    battery = Battery.from_target_energy(
        target_energy=TARGET_BATTERY_ENERGY,
        target_voltage=TARGET_BATTERY_VOLTAGE,
        cell_capacity=CELL_CAPACITY,
        cell_mass=CELL_MASS,
        chemistry='lithium_ion',
    )
    battery_kg = battery.mass.in_units_of('kg')

    # Propulsion system
    motor = Motor(
        max_power=MOTOR_MAX_POWER,
        efficiency=MOTOR_EFFICIENCY,
        mass=MOTOR_MASS,
    )

    propeller = Propeller(
        diameter=PROPELLER_DIAMETER,
        num_blades=2,
        efficiency_hover=PROPELLER_FM,
    )

    propulsion = PropulsionSystem(
        motors=[motor],
        propellers=[propeller],
        num_units=NUM_MOTORS,
    )
    propulsion_kg = propulsion.mass.in_units_of('kg')

    # -------------------------------------------------------------------------
    # Solve for MTOW
    # -------------------------------------------------------------------------

    print("SOLVING MTOW EQUATION")
    print("-" * 40)
    print(f"  Structure fraction:  {STRUCTURE_FRACTION * 100:.1f}% of MTOW")
    print(f"  Avionics fraction:   {AVIONICS_FRACTION * 100:.1f}% of MTOW")
    print()

    solution = solve_mtow(
        payload_kg=payload_kg,
        propulsion_kg=propulsion_kg,
        battery_kg=battery_kg,
        structure_fraction=STRUCTURE_FRACTION,
        avionics_fraction=AVIONICS_FRACTION,
    )

    mtow_kg = solution['mtow_kg']
    structure_kg = solution['structure_kg']
    avionics_kg = solution['avionics_kg']

    # -------------------------------------------------------------------------
    # Display weight breakdown
    # -------------------------------------------------------------------------

    component_masses = {
        'Payload': payload_kg,
        'Structure': structure_kg,
        'Avionics': avionics_kg,
        'Propulsion': propulsion_kg,
        'Battery': battery_kg,
    }

    print("COMPONENT WEIGHT BREAKDOWN")
    print("-" * 40)

    for name, mass_kg in component_masses.items():
        fraction = mass_kg / mtow_kg * 100
        print(f"  {name:15s}: {mass_kg:8.2f} kg ({fraction:5.1f}%)")

    print("-" * 40)
    print(f"  {'MTOW':15s}: {mtow_kg:8.2f} kg")
    print()

    # Verify solution
    fixed_total = payload_kg + propulsion_kg + battery_kg
    fraction_total = STRUCTURE_FRACTION + AVIONICS_FRACTION
    analytical_mtow = fixed_total / (1 - fraction_total)

    print("SOLUTION VERIFICATION")
    print("-" * 40)
    print(f"  Fixed masses:      {fixed_total:.2f} kg (payload + propulsion + battery)")
    print(f"  Fraction total:    {fraction_total * 100:.1f}% (structure + avionics)")
    print(f"  Analytical MTOW:   {analytical_mtow:.2f} kg")
    print(f"  Numerical MTOW:    {mtow_kg:.2f} kg")
    print(f"  Error:             {abs(mtow_kg - analytical_mtow):.6f} kg")
    print()

    # -------------------------------------------------------------------------
    # Battery details
    # -------------------------------------------------------------------------

    print("BATTERY SIZING DETAILS")
    print("-" * 40)
    print(f"  Configuration:     {battery.info.get('configuration', 'N/A')}")
    print(f"  Cell count:        {battery.total_cells} cells")
    print(f"  Nominal voltage:   {battery.nominal_voltage.in_units_of('V'):.1f} V")
    print(f"  Total capacity:    {battery.total_capacity.in_units_of('Ah'):.1f} Ah")
    print(f"  Energy capacity:   {battery.energy_capacity.in_units_of('Wh'):.1f} Wh "
          f"({battery.energy_capacity.in_units_of('kWh'):.2f} kWh)")
    print(f"  Pack mass:         {battery.mass.in_units_of('kg'):.2f} kg")

    if battery.warnings:
        print()
        print("  Sizing notes:")
        for warning in battery.warnings:
            print(f"    - {warning}")
    print()

    # -------------------------------------------------------------------------
    # Propulsion system
    # -------------------------------------------------------------------------

    # Thrust = Weight (in hover, thrust equals weight)
    thrust = Force(mtow_kg * GRAVITY, 'N')

    print("PROPULSION SYSTEM")
    print("-" * 40)
    print(f"  Number of rotors:  {propulsion.num_units}")
    print(f"  Total disk area:   {propulsion.total_disk_area.in_units_of('m^2'):.2f} m^2")
    print(f"  Motor efficiency:  {propulsion.average_motor_efficiency * 100:.0f}%")
    print(f"  Figure of Merit:   {propulsion.average_figure_of_merit:.2f}")
    print(f"  Disk loading:      {propulsion.disk_loading(thrust):.1f} N/m^2")
    print()

    # -------------------------------------------------------------------------
    # Hover power
    # -------------------------------------------------------------------------

    # Calculate power chain
    ideal_power = propulsion.hover_power_ideal(thrust)
    shaft_power = propulsion.hover_shaft_power(thrust)
    electrical_power = propulsion.hover_electrical_power(thrust)

    print("HOVER POWER REQUIREMENTS")
    print("-" * 40)
    print(f"  Vehicle weight:    {thrust.in_units_of('N'):.1f} N")
    print(f"  Ideal power:       {ideal_power.in_units_of('kW'):.2f} kW")
    print(f"  Shaft power:       {shaft_power.in_units_of('kW'):.2f} kW "
          f"(ideal / FM)")
    print(f"  Electrical power:  {electrical_power.in_units_of('kW'):.2f} kW "
          f"(shaft / motor eff)")
    print()

    # Power margin check
    max_electrical_power = propulsion.total_max_electrical_power.in_units_of('kW')
    power_margin = (max_electrical_power - electrical_power.in_units_of('kW')) / max_electrical_power * 100

    print("POWER MARGIN")
    print("-" * 40)
    print(f"  Max electrical:    {max_electrical_power:.2f} kW")
    print(f"  Hover power:       {electrical_power.in_units_of('kW'):.2f} kW")
    print(f"  Power margin:      {power_margin:.1f}%")
    print()

    # Hover endurance estimate
    usable_energy_wh = battery.energy_capacity.in_units_of('Wh') * 0.8  # 80% usable
    hover_power_w = electrical_power.in_units_of('W')
    hover_endurance_min = (usable_energy_wh / hover_power_w) * 60

    print("HOVER ENDURANCE ESTIMATE")
    print("-" * 40)
    print(f"  Usable energy:     {usable_energy_wh:.0f} Wh (80% of capacity)")
    print(f"  Hover endurance:   {hover_endurance_min:.1f} minutes")
    print()

    print("=" * 60)


if __name__ == '__main__':
    main()
