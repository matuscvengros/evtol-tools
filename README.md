# eVTOL Tools

[![Tests](https://github.com/matuscvengros/evtol-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/matuscvengros/evtol-tools/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Python toolkit for electric Vertical Take-Off and Landing (eVTOL) aircraft design and analysis. This package provides physics-based engineering tools for component modeling, performance analysis, atmospheric calculations, and mission planning with rigorous unit handling.

## Why eVTOL Tools?

eVTOL aircraft design requires integrating multiple engineering disciplines - propulsion, aerodynamics, structures, batteries, and atmospherics. This toolkit provides:

- **Physics-based calculations** - Momentum theory, ISA atmosphere, battery chemistry
- **Component-level modeling** - Batteries, motors, propellers, propulsion systems
- **Type-safe units system** - Prevent unit errors with automatic conversions
- **Mission analysis** - Energy consumption, altitude effects, hot day performance
- **Design trade-offs** - Weight fractions, disk loading, power margins

## Key Features

### Propulsion Analysis
- **Multi-rotor systems** - Arbitrary motor/propeller configurations
- **Hover power calculations** - Ideal, shaft, and electrical power from momentum theory
- **Efficiency chain modeling** - Motor efficiency, figure of merit, installation losses
- **Performance metrics** - Disk loading, power loading, induced velocity
- **Tip speed limits** - Mach number constraints, maximum RPM calculations

### Battery Modeling
- **Cell configuration** - Series/parallel string design with automatic sizing
- **Sizing methods** - From target energy, voltage, or capacity requirements
- **Chemistry support** - Lithium-ion, NMC, LFP, LiPo with validated cell parameters
- **Power limits** - C-rating based charge/discharge constraints with thermal derating
- **Mass calculations** - Cells plus BMS/packaging overhead (configurable)
- **Discharge curves** - Voltage vs SoC and C-rate modeling (analytical and lookup table)
- **Internal resistance** - Series/parallel pack resistance calculations with SoC dependence
- **Heat generation** - I²R losses for thermal analysis and cooling system design
- **Charge modeling** - CC-CV profiles with efficiency losses and current tapering
- **Thermal framework** - Temperature limits, power derating, and lumped thermal dynamics
- **Model flexibility** - Abstract interfaces for custom discharge and charge models
- **PyBaMM integration** - Optional high-fidelity electrochemical modeling support

### Atmospheric Calculations
- **ISA model** - International Standard Atmosphere (0-80 km altitude) via ICAO 1993 standard
- **Temperature offsets** - Hot day (ISA+) and cold day (ISA-) analysis for certification scenarios
- **Altitude effects** - Density impact on power, tip speeds, performance degradation
- **Pressure/density altitude** - Conversion between altitude references and standard day corrections
- **NumPy array support** - Batch calculations for altitude profiles and mission segments
- **Physical properties** - Temperature, pressure, density, speed of sound at any altitude
- **Array operations** - Vectorised calculations for flight profile analysis

### Type-Safe Units System
- **20+ physical quantities** - Mass, length, velocity, power, energy, etc.
- **Automatic conversions** - Seamless unit handling with validation
- **NumPy integration** - Vectorized calculations with units
- **Dimensional analysis** - Prevents unit mismatches at compile time
- **Flexible notation** - Accepts any dimensionally-compatible unit string

### Component Models
- **Payload** - Mass and center of gravity tracking
- **Battery** - Cell configuration, energy capacity, power limits
- **Motor** - Power, efficiency, power-to-weight ratio
- **Propeller** - Geometry, disk area, tip speed calculations
- **PropulsionSystem** - Multi-rotor integration with full power chain

## Installation

### Requirements

- Python 3.10 or higher
- NumPy >= 1.20
- Pint >= 0.23
- Ambiance >= 0.3 (ISA atmosphere)
- PyBaMM >= 24.1 (battery chemistry data)

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd evtol-tools

# Install in development mode
pip install -e .

# Or install with dev dependencies (includes pytest)
pip install -e ".[dev]"
```

## Quick Start

### Propulsion System Design

```python
from evtoltools.common import Mass, Length, Power, Force, Density
from evtoltools.components import Motor, Propeller, PropulsionSystem

# Define motor
motor = Motor(
    max_power=Power(50, 'kW'),
    efficiency=0.92,
    mass=Mass(8, 'kg')
)

# Define propeller
propeller = Propeller(
    diameter=Length(1.8, 'm'),
    num_blades=3,
    efficiency_hover=0.72  # Figure of Merit
)

# Create 4-rotor propulsion system
propulsion = PropulsionSystem(
    motors=[motor],
    propellers=[propeller],
    num_units=4,
    installation_efficiency=0.95
)

# Calculate hover power for 1500 kg aircraft
weight = Force(1500 * 9.81, 'N')
air_density = Density(1.225, 'kg/m^3')

ideal_power = propulsion.hover_power_ideal(weight, air_density)
shaft_power = propulsion.hover_shaft_power(weight, air_density)
electrical_power = propulsion.hover_electrical_power(weight, air_density)

print(f"Ideal power:      {ideal_power.to('kW')}")
print(f"Shaft power:      {shaft_power.to('kW')}")
print(f"Electrical power: {electrical_power.to('kW')}")
print(f"Disk loading:     {propulsion.disk_loading(weight).to('Pa')}")
print(f"Induced velocity: {propulsion.induced_velocity(weight, air_density)}")
```

### Battery Sizing

```python
from evtoltools.common import Energy, Voltage, Capacity, Mass
from evtoltools.components import Battery

# Method 1: Size from target energy
battery = Battery.from_target_energy(
    target_energy=Energy(50, 'kWh'),
    target_voltage=Voltage(400, 'V'),
    cell_capacity=Capacity(5000, 'mAh'),
    cell_mass=Mass(70, 'g'),
    chemistry='lithium_ion'
)

print(f"Configuration:    {battery.cells_series}S{battery.cells_parallel}P")
print(f"Total cells:      {battery.total_cells}")
print(f"Pack mass:        {battery.mass.to('kg')}")
print(f"Nominal voltage:  {battery.nominal_voltage}")
print(f"Total capacity:   {battery.total_capacity.to('Ah')}")
print(f"Energy capacity:  {battery.energy_capacity.to('kWh')}")
print(f"Max discharge:    {battery.max_discharge_power.to('kW')}")

# Method 2: Size from target voltage
battery = Battery.from_target_voltage(
    target_voltage=Voltage(48, 'V'),
    cells_parallel=4,
    cell_capacity=Capacity(5000, 'mAh'),
    cell_mass=Mass(50, 'g')
)
```

### Battery Discharge and Thermal Modeling

The battery module provides comprehensive discharge voltage modeling, thermal analysis, and charging behavior.

#### Basic Discharge Modeling

```python
from evtoltools.common import Capacity, Mass, Current, Temperature, Power, Time
from evtoltools.components import Battery

# Create battery pack (14S4P configuration)
battery = Battery(
    cells_series=14,
    cells_parallel=4,
    cell_capacity=Capacity(5, 'Ah'),
    cell_mass=Mass(50, 'g'),
    chemistry='lithium_ion'  # or 'nmc', 'lfp', 'lipo'
)

print(f"Configuration:     {battery.cells_series}S{battery.cells_parallel}P")
print(f"Pack voltage:      {battery.nominal_voltage}")
print(f"Pack capacity:     {battery.total_capacity.to('Ah')}")
print(f"Pack energy:       {battery.energy_capacity.to('kWh')}")
print(f"Pack resistance:   {battery.internal_resistance.to('mohm')}")
print(f"Pack mass:         {battery.mass.to('kg')}")

# C-rate conversions (C-rate is current relative to capacity)
current_1c = battery.current_from_c_rate(1.0)  # 20A for 20Ah pack
current_2c = battery.current_from_c_rate(2.0)  # 40A (aggressive discharge)
c_rate = battery.c_rate_from_current(Current(40, 'A'))  # 2.0C
print(f"1C current: {current_1c}")
print(f"40A is {c_rate:.1f}C discharge rate")

# Discharge voltage varies with State of Charge (SoC) and C-rate
v_full = battery.get_voltage(soc=1.0, c_rate=0.0)  # Open circuit, full charge
v_half = battery.get_voltage(soc=0.5, c_rate=1.0)  # 50% SoC, 1C discharge
v_low = battery.get_voltage(soc=0.2, c_rate=1.0)   # 20% SoC, 1C discharge

print(f"Voltage at 100% SoC, no load:  {v_full.to('V')}")
print(f"Voltage at 50% SoC, 1C:        {v_half.to('V')}")
print(f"Voltage at 20% SoC, 1C:        {v_low.to('V')}")

# Higher C-rate causes more I*R voltage drop
v_1c = battery.get_voltage(soc=0.5, c_rate=1.0)  # 1C discharge
v_3c = battery.get_voltage(soc=0.5, c_rate=3.0)  # 3C discharge (aggressive)
voltage_sag = v_1c - v_3c
print(f"Voltage sag from 1C to 3C: {voltage_sag.to('V')}")

# Internal resistance scaling
# - Series cells ADD resistance: R_total = R_cell * N_series
# - Parallel cells REDUCE resistance: R_total = R_series / N_parallel
cell_r = battery.chemistry.internal_resistance
pack_r = battery.internal_resistance
print(f"Cell resistance:  {cell_r.to('mohm')}")
print(f"Pack resistance:  {pack_r.to('mohm')}")
print(f"Scaling factor:   {battery.cells_series}/{battery.cells_parallel} = {pack_r/cell_r:.2f}")
```

#### Heat Generation and Thermal Analysis

```python
from evtoltools.components.battery import ThermalLimits, SimpleThermalModel

# I²R heat generation (resistive losses during discharge/charge)
# Heat power = I² * R
current_discharge = Current(40, 'A')  # 2C discharge
heat_40a = battery.heat_generation_rate(current_discharge)
heat_80a = battery.heat_generation_rate(Current(80, 'A'))  # 4C

print(f"Heat generation at 40A:  {heat_40a.in_units_of('W'):.1f} W")
print(f"Heat generation at 80A:  {heat_80a.in_units_of('W'):.1f} W")
print(f"Heat scales with I²:     {(80/40)**2:.1f}x increase")

# SoC-dependent resistance (if discharge model supports it)
r_high_soc = battery.get_internal_resistance(soc=0.9)
r_low_soc = battery.get_internal_resistance(soc=0.2)
print(f"Resistance at 90% SoC: {r_high_soc.to('mohm')}")
print(f"Resistance at 20% SoC: {r_low_soc.to('mohm')}")

# Thermal operating limits
limits = ThermalLimits(
    max_discharge_temp=Temperature(60, 'degC'),  # Absolute max
    max_charge_temp=Temperature(45, 'degC'),     # Lower for charging
    derate_temp=Temperature(40, 'degC'),         # Start reducing power here
    min_temp=Temperature(-20, 'degC')            # Cold weather limit
)

# Check if temperature is safe
temp_operating = Temperature(35, 'degC')
is_safe_discharge = limits.is_within_limits(temp_operating, is_charging=False)
is_safe_charge = limits.is_within_limits(temp_operating, is_charging=True)
print(f"Safe for discharge at {temp_operating}: {is_safe_discharge}")
print(f"Safe for charge at {temp_operating}:    {is_safe_charge}")

# Power derating at high temperature (linear between derate_temp and max_temp)
temp_warm = Temperature(40, 'degC')   # At derate threshold
temp_hot = Temperature(50, 'degC')    # Between derate and max
temp_max = Temperature(60, 'degC')    # At maximum

derate_40c = limits.get_derate_factor(temp_warm)  # 1.0 (100% power)
derate_50c = limits.get_derate_factor(temp_hot)   # 0.5 (50% power)
derate_60c = limits.get_derate_factor(temp_max)   # 0.0 (no power)

print(f"Power available at 40°C: {derate_40c * 100:.0f}%")
print(f"Power available at 50°C: {derate_50c * 100:.0f}%")
print(f"Power available at 60°C: {derate_60c * 100:.0f}%")

# Cold temperature derating (reduced performance below 0°C)
temp_cold = Temperature(-10, 'degC')
cold_derate = limits.get_cold_derate_factor(temp_cold)
print(f"Power available at -10°C: {cold_derate * 100:.0f}%")

# Lumped thermal model (simple but effective for mission analysis)
thermal_model = SimpleThermalModel(
    mass=battery.mass,                  # Battery thermal mass
    specific_heat=1000,                 # J/(kg*K) - typical for Li-ion
    cooling_coefficient=10.0            # W/K - depends on cooling design
)

# Predict temperature rise during discharge
initial_temp = Temperature(25, 'degC')
heat_rate = Power(100, 'W')            # From I²R losses
duration = Time(30, 'min')
ambient_temp = Temperature(25, 'degC')

final_temp = thermal_model.temperature_after(
    initial_temp=initial_temp,
    heat_rate=heat_rate,
    duration=duration,
    ambient_temp=ambient_temp
)
print(f"Initial temperature:  {initial_temp.in_units_of('degC'):.1f}°C")
print(f"Final temperature:    {final_temp.in_units_of('degC'):.1f}°C")
print(f"Temperature rise:     {(final_temp - initial_temp).in_units_of('K'):.1f}K")

# Steady-state temperature (equilibrium between generation and cooling)
steady_temp = thermal_model.steady_state_temperature(
    heat_rate=Power(150, 'W'),
    ambient_temp=Temperature(30, 'degC')
)
print(f"Steady-state temperature: {steady_temp.in_units_of('degC'):.1f}°C")

# Time to reach temperature limit
time_to_limit = thermal_model.time_to_temperature(
    initial_temp=Temperature(25, 'degC'),
    target_temp=Temperature(50, 'degC'),
    heat_rate=Power(100, 'W'),
    ambient_temp=Temperature(25, 'degC')
)
print(f"Time to 50°C: {time_to_limit.to('min')}")
```

#### Charge Modeling (CC-CV Profile)

```python
from evtoltools.components.battery import SimpleChargeModel

# Battery uses CC-CV (Constant Current - Constant Voltage) charging
# - CC phase: constant current up to ~80% SoC
# - CV phase: constant voltage, current tapers exponentially

# Get recommended charge current at different SoC levels
charge_30 = battery.get_charge_current(soc=0.3)  # CC phase: full current
charge_85 = battery.get_charge_current(soc=0.85) # CV phase: tapered current
charge_95 = battery.get_charge_current(soc=0.95) # CV phase: low current

print(f"Charge current at 30% SoC:  {charge_30.to('A')}")
print(f"Charge current at 85% SoC:  {charge_85.to('A')}")
print(f"Charge current at 95% SoC:  {charge_95.to('A')}")

# Charging efficiency (decreases at high C-rate and high SoC)
eff_low_soc = battery.get_charge_efficiency(soc=0.3, c_rate=1.0)
eff_high_soc = battery.get_charge_efficiency(soc=0.9, c_rate=1.0)
eff_high_rate = battery.get_charge_efficiency(soc=0.5, c_rate=2.0)

print(f"Charge efficiency at 30% SoC, 1C:  {eff_low_soc * 100:.1f}%")
print(f"Charge efficiency at 90% SoC, 1C:  {eff_high_soc * 100:.1f}%")
print(f"Charge efficiency at 50% SoC, 2C:  {eff_high_rate * 100:.1f}%")

# Estimate charge time (20% to 80% is typical fast-charge window)
charge_time_2080 = battery.time_to_charge(start_soc=0.2, end_soc=0.8)
charge_time_full = battery.time_to_charge(start_soc=0.2, end_soc=1.0)

print(f"Charge time 20% → 80%:  {charge_time_2080 * 60:.1f} minutes")
print(f"Charge time 20% → 100%: {charge_time_full * 60:.1f} minutes")
print(f"Last 20% takes:         {(charge_time_full - charge_time_2080) * 60:.1f} min (CV tapering)")

# Custom charge model with different parameters
custom_charge = SimpleChargeModel(
    cc_cv_transition_soc=0.75,      # Earlier CV transition
    cv_taper_factor=4.0,             # Faster taper
    base_efficiency=0.97,            # Higher base efficiency
    efficiency_c_rate_factor=0.015   # Less C-rate penalty
)
battery.set_charge_model(custom_charge)
new_charge_time = battery.time_to_charge(start_soc=0.2, end_soc=0.8)
print(f"Charge time with custom model: {new_charge_time * 60:.1f} minutes")
```

#### Advanced Discharge Models

```python
from evtoltools.components.battery import (
    AnalyticalDischargeModel,
    LookupTableDischargeModel,
    load_discharge_model
)
import numpy as np

# Default: Analytical model (V = V_oc(SoC) - I*R)
# Fast computation, good for preliminary design
default_model = battery.discharge_model
print(f"Default model type: {type(default_model).__name__}")

# Lookup table model for higher accuracy
# Pre-computed from PyBaMM simulations or test data
soc_points = np.linspace(0, 1, 21)      # 0%, 5%, 10%, ..., 100%
c_rate_points = np.array([0.1, 0.5, 1.0, 2.0, 3.0])

# Voltage data from measurements or simulation (21 × 5 array)
# In practice, populate this from real data
voltage_data = np.zeros((21, 5))
for i, soc in enumerate(soc_points):
    for j, c_rate in enumerate(c_rate_points):
        # Simplified model for demonstration
        v_oc = 2.8 + soc * 1.4  # Linear OCV curve
        v_drop = c_rate * 0.05   # I*R drop
        voltage_data[i, j] = v_oc - v_drop

lookup_model = LookupTableDischargeModel(
    soc_points=soc_points,
    c_rate_points=c_rate_points,
    voltage_data=voltage_data,
    v_min=Voltage(2.8, 'V')
)

# Apply the lookup table model
battery.set_discharge_model(lookup_model)
v_lookup = battery.get_voltage(soc=0.6, c_rate=1.5)  # Interpolated from table
print(f"Voltage from lookup table: {v_lookup.to('V')}")

# Load model by chemistry name (returns analytical model with chemistry parameters)
li_ion_model = load_discharge_model('lithium_ion')
nmc_model = load_discharge_model('nmc')
lfp_model = load_discharge_model('lfp')

print(f"Li-ion nominal voltage: {li_ion_model.v_nominal}")
print(f"NMC nominal voltage:    {nmc_model.v_nominal}")
print(f"LFP nominal voltage:    {lfp_model.v_nominal}")
```

### Atmospheric Calculations

The ISA (International Standard Atmosphere) model provides accurate atmospheric properties for performance analysis and mission planning.

```python
from evtoltools.common import Atmosphere, Altitude, Temperature, Pressure, Density
import numpy as np

# Standard atmosphere at 5000 ft
atm = Atmosphere(Altitude(5000, 'ft'))
print(f"Temperature:     {atm.temperature.to('degC')}")
print(f"Pressure:        {atm.pressure.to('kPa')}")
print(f"Density:         {atm.density.to('kg/m^3')}")
print(f"Speed of sound:  {atm.speed_of_sound.to('m/s')}")

# Hot day analysis (ISA+20K) - critical for certification
atm_hot = Atmosphere(
    altitude=Altitude(5000, 'ft'),
    temperature_offset=Temperature(20, 'K')
)
print(f"Hot day temperature: {atm_hot.temperature.to('degC')}")
print(f"Hot day density:     {atm_hot.density.to('kg/m^3')}")  # Lower density
print(f"Density reduction:   {(1 - atm_hot.density/atm.isa_density) * 100:.1f}%")

# Cold day analysis (ISA-15K)
atm_cold = Atmosphere(
    altitude=Altitude(2000, 'm'),
    temperature_offset=Temperature(-15, 'K')
)
print(f"Cold day density: {atm_cold.density.to('kg/m^3')}")  # Higher density

# Sea level reference
from evtoltools.common import sea_level_atmosphere
atm_sl = sea_level_atmosphere()  # Or Atmosphere(Altitude.sea_level())
print(f"Sea level: {atm_sl.temperature}, {atm_sl.density}")

# Pressure altitude conversion (what altimeter reads)
atm_from_press = Atmosphere.from_pressure_altitude(Pressure(70000, 'Pa'))
print(f"Pressure altitude: {atm_from_press.altitude.to('ft')}")

# Density altitude conversion (altitude for given air density)
atm_from_dens = Atmosphere.from_density_altitude(Density(1.0, 'kg/m^3'))
print(f"Density altitude: {atm_from_dens.altitude.to('ft')}")

# Calculate hover power at altitude and temperature
power_standard = propulsion.hover_electrical_power(weight, atmosphere=atm)
power_hot_day = propulsion.hover_electrical_power(weight, atmosphere=atm_hot)
print(f"Power required (ISA):      {power_standard.to('kW')}")
print(f"Power required (ISA+20):   {power_hot_day.to('kW')}")
print(f"Power increase: {(power_hot_day/power_standard - 1) * 100:.1f}%")

# Array support for mission profile analysis
altitudes_ft = np.array([0, 1000, 2000, 3000, 4000, 5000])
altitudes = Altitude(altitudes_ft, 'ft')
atm_profile = Atmosphere(altitudes)

# Access properties as arrays
temps = atm_profile.temperature  # Array of temperatures
densities = atm_profile.density  # Array of densities
print(f"Altitude profile densities: {densities.to('kg/m^3')}")

# Flight level convenience
cruise_alt = Altitude.from_flight_level(100)  # FL100 = 10,000 ft
atm_cruise = Atmosphere(cruise_alt)
print(f"Cruise at {cruise_alt}: {atm_cruise.density}")
```

### Type-Safe Units

```python
from evtoltools.common import Mass, Length, Velocity
import numpy as np

# Scalar operations
aircraft_mass = Mass(1500, 'kg')
payload_mass = Mass(500, 'lbs')  # Different units OK
total_mass = aircraft_mass + payload_mass  # Automatic conversion

# Get numeric value in specific units
mass_kg = total_mass.in_units_of('kg')  # Returns float

# Array operations
component_masses = Mass(np.array([100, 200, 300, 400]), 'kg')
masses_lbs = component_masses.to('lbs')

# Comparisons work across units
if Mass(1, 'kg') > Mass(1, 'lbs'):
    print("1 kg is heavier than 1 lb")  # True

# Flexible unit notation (any dimensionally-compatible string)
from evtoltools.common import Pressure, Force
p1 = Pressure(1, 'Pa')
p2 = Pressure(1, 'N/m^2')      # Equivalent
p3 = Pressure(1, 'kg/(m*s^2)') # Also valid
```

## Complete Example: eVTOL Sizing

This example demonstrates a real-world eVTOL sizing workflow:

```python
from evtoltools.common import *
from evtoltools.components import *

# Define design requirements
payload = Payload(Mass(320, 'kg'), description='4 passengers @ 80kg')

# Create propulsion system
motor = Motor(max_power=Power(40, 'kW'), efficiency=0.90, mass=Mass(5, 'kg'))
propeller = Propeller(diameter=Length(1.8, 'm'), efficiency_hover=0.70)
propulsion = PropulsionSystem(
    motors=[motor],
    propellers=[propeller],
    num_units=12,
    installation_efficiency=0.95
)

# Size battery for 30-minute hover
target_energy = Energy(80, 'kWh')
battery = Battery.from_target_energy(
    target_energy=target_energy,
    target_voltage=Voltage(500, 'V'),
    cell_capacity=Capacity(5000, 'mAh'),
    cell_mass=Mass(70, 'g')
)

# Calculate total mass (simplified - see examples/ for full MTOW solver)
structure_mass = Mass(400, 'kg')
avionics_mass = Mass(50, 'kg')
total_mass = (payload.mass + structure_mass + avionics_mass +
              propulsion.mass + battery.mass)

# Performance analysis
weight = Force(total_mass.magnitude * 9.81, 'N')
atm_hot = Atmosphere(Length(2000, 'ft'), Temperature(20, 'K'))

hover_power = propulsion.hover_electrical_power(weight, atmosphere=atm_hot)
hover_time_hr = battery.energy_capacity.in_units_of('Wh') / hover_power.in_units_of('W')

print(f"MTOW:             {total_mass.to('kg')}")
print(f"Disk loading:     {propulsion.disk_loading(weight).to('Pa')}")
print(f"Hover power:      {hover_power.to('kW')} (ISA+20, 2000 ft)")
print(f"Hover endurance:  {hover_time_hr * 60:.1f} minutes")
```

See `examples/vehicle_weight_calculator.py` for a complete implementation with MTOW fraction solver.

## Physics and Engineering Details

### Hover Power from Momentum Theory

The toolkit uses momentum theory for hover power calculations:

```
Ideal Power:      P_ideal = T^(3/2) / sqrt(2 * ρ * A)
Shaft Power:      P_shaft = P_ideal / (FM * η_installation)
Electrical Power: P_elec = P_shaft / η_motor

where:
  T = thrust (equals weight in hover)
  ρ = air density
  A = total rotor disk area
  FM = figure of merit (rotor efficiency, typically 0.6-0.8)
  η_installation = installation efficiency (typically 0.95)
  η_motor = motor efficiency (typically 0.90-0.95)
```

### Battery Cell Configuration

Battery packs are configured as series/parallel strings:

```
Voltage:  V_pack = N_series × V_cell
Capacity: Q_pack = N_parallel × Q_cell
Energy:   E_pack = V_pack × Q_pack
Mass:     m_pack = (N_series × N_parallel × m_cell) × (1 + overhead)

where overhead includes BMS, wiring, enclosure (typically 15%)
```

### Battery Discharge Model

Voltage varies with state of charge (SoC) and discharge rate (C-rate):

```
V_cell = V_oc(SoC) - I × R_internal

where:
  V_oc = open-circuit voltage (function of SoC)
  I = discharge current = C_rate × Capacity
  R_internal = cell internal resistance

Pack scaling:
  V_pack = V_cell × N_series
  R_pack = (R_cell × N_series) / N_parallel

Heat generation:
  P_heat = I² × R_pack
```

### Thermal Derating

Power capability is reduced at extreme temperatures:

```
At T < T_derate:     P_available = P_max (100%)
At T_derate < T < T_max:  P_available = P_max × (T_max - T) / (T_max - T_derate)
At T > T_max:        P_available = 0
```

### International Standard Atmosphere (ISA) Model

The toolkit uses the ICAO 1993 International Standard Atmosphere model for atmospheric property calculations:

```
Temperature:  T(h) = T_0 + L × h  (troposphere, h < 11 km)
              T(h) = 216.65 K     (stratosphere, 11 km < h < 20 km)

Pressure:     P(h) = P_0 × (T(h)/T_0)^(-g/(L*R))  (troposphere)

Density:      ρ = P / (R × T)  (ideal gas law)

Speed of sound: a = sqrt(γ × R × T)

where:
  T_0 = 288.15 K (15°C) - sea level temperature
  P_0 = 101325 Pa - sea level pressure
  ρ_0 = 1.225 kg/m³ - sea level density
  L = -0.0065 K/m - temperature lapse rate (troposphere)
  R = 287.05 J/(kg*K) - specific gas constant for dry air
  γ = 1.4 - ratio of specific heats
  g = 9.80665 m/s² - gravitational acceleration
```

**Temperature Offset (ISA±ΔT)**

For hot/cold day analysis, temperature is adjusted while pressure follows standard altitude:

```
T_offset(h) = T_ISA(h) + ΔT
ρ_offset(h) = P_ISA(h) / (R × T_offset(h))

Example: ISA+20K at sea level
  T = 288.15 + 20 = 308.15 K (35°C)
  ρ = 101325 / (287.05 × 308.15) = 1.145 kg/m³ (6.5% reduction)
```

**Altitude References**

- **Geometric altitude**: Height above sea level (what GPS reads)
- **Pressure altitude**: Altitude corresponding to a given pressure in ISA (what altimeter reads)
- **Density altitude**: Altitude corresponding to a given density in ISA (what aircraft performs at)

```
On a hot day:
  Geometric altitude = 5000 ft
  Pressure altitude ≈ 5000 ft (altimeter reading)
  Density altitude > 5000 ft (reduced density, worse performance)
```

**Array Support for Flight Profiles**

The atmosphere model supports NumPy arrays for efficient mission analysis:

```python
import numpy as np
altitudes = Altitude(np.array([0, 1000, 2000, 3000, 4000, 5000]), 'ft')
atm = Atmosphere(altitudes)
# All properties (temperature, pressure, density, etc.) are arrays
densities = atm.density.magnitude  # Array of density values
```

### Atmospheric Effects on eVTOL Performance

Density decreases with altitude, significantly affecting performance:

```
Hover Power:        P ∝ 1/sqrt(ρ)
  At 5000 ft (ρ = 1.055 kg/m³): P increases by ~7% vs sea level
  At 10000 ft (ρ = 0.905 kg/m³): P increases by ~17% vs sea level

Induced Velocity:   v_induced ∝ 1/sqrt(ρ)
  Higher downwash at altitude for same thrust

Tip Speed Limit:    V_tip_max = M_limit × a(h)
  Speed of sound decreases with altitude
  Mach number constraints become more restrictive

Rotor Efficiency:   FM typically decreases slightly with altitude
  Compressibility effects at higher Mach numbers

where:
  ρ = air density
  a(h) = speed of sound at altitude h
  M_limit = tip Mach limit (typically 0.7-0.9)
  FM = figure of merit (rotor efficiency)
```

**Hot Day Performance Degradation**

Temperature offsets compound altitude effects:

```
Example: 5000 ft, ISA+20K
  Standard density at 5000 ft: ρ = 1.055 kg/m³
  Hot day density:            ρ = 0.985 kg/m³ (6.6% reduction)
  Combined effect:            Power increase ≈ 13% vs sea level ISA

This is critical for:
  - Hover ceiling calculations
  - Maximum payload determination
  - Energy consumption on hot days
  - Certification requirements (often require ISA+15K or ISA+20K)
```

## Implemented Physical Quantities

### SI Base Quantities
- **Mass** - kg, g, lb, lbs, ton, tonne, oz
- **Length** - m, cm, mm, ft, in, mi, km, nmi
- **Time** - s, ms, min, hr, day
- **Temperature** - K, degC, degF
- **Current** - A, mA, uA, kA
- **Substance** - mol, mmol, kmol
- **Luminosity** - cd, lm

### Derived Quantities
- **Velocity** - m/s, km/h, mph, knots, ft/s
- **AngularVelocity** - rad/s, rpm, deg/s
- **Frequency** - Hz, kHz, MHz, mHz
- **Area** - m^2, cm^2, ft^2, in^2
- **Volume** - m^3, L, gal, ft^3
- **Density** - kg/m^3, g/cm^3, lb/ft^3
- **Force** - N, kN, lbf, kgf
- **Pressure** - Pa, kPa, bar, psi, atm
- **Power** - W, kW, MW, hp, bhp
- **Energy** - J, kJ, MJ, Wh, kWh, MWh
- **Moment** - N*m, ft*lbf, in*lbf
- **Voltage** - V, mV, kV
- **Capacity** - Ah, mAh, C
- **Resistance** - ohm, mohm, kohm, Mohm

Note: The system validates dimensionality rather than enforcing a strict whitelist. Any dimensionally-compatible unit string that Pint recognizes is accepted (e.g., 'N/m^2' for Pressure, 'kg*m/s^2' for Force).

## Examples and Tutorials

The `examples/` directory contains comprehensive demonstrations:

### Vehicle Weight Calculator (`examples/vehicle_weight_calculator.py`)

Complete eVTOL sizing workflow showing:
- MTOW fraction methodology (structure and avionics as % of MTOW)
- Implicit weight equation solver using AeroSandbox
- Component mass breakdown
- Battery sizing from energy requirements
- Hover power and endurance calculations

Run with: `python examples/vehicle_weight_calculator.py`

### Jupyter Notebooks

**Atmosphere Showcase** (`examples/atmosphere_showcase.ipynb`)
- ISA atmosphere calculations
- Temperature offset analysis (hot/cold days)
- Altitude effects on performance
- Pressure and density altitude
- Integration with propulsion calculations
- Mission energy analysis

**Quantities Showcase** (`examples/quantities_showcase.ipynb`)
- Units system demonstrations
- Array operations
- Cross-type arithmetic
- Practical eVTOL calculations

## Architecture

```
evtol-tools/
├── evtoltools/                   # Main package
│   ├── common/                   # Units system and atmosphere
│   │   ├── units/                # Type-safe units system
│   │   │   ├── base.py           # BaseQuantity abstract class
│   │   │   ├── registry.py       # Pint UnitRegistry singleton
│   │   │   ├── config.py         # Default and allowed units
│   │   │   └── quantities/       # 20+ physical quantity types
│   │   │       ├── mass.py
│   │   │       ├── length.py
│   │   │       ├── velocity.py
│   │   │       ├── power.py
│   │   │       └── ... (and more)
│   │   └── atmosphere/           # ISA atmosphere model
│   │       ├── isa.py            # Atmosphere class, ISA calculations
│   │       └── altitude.py       # Altitude quantity with flight level support
│   └── components/               # Vehicle component models
│       ├── base.py               # BaseComponent class
│       ├── payload.py            # Payload component
│       ├── structure.py          # Structure component
│       ├── avionics.py           # Avionics component
│       ├── battery/              # Battery subsystem
│       │   ├── battery.py        # Battery pack model
│       │   ├── chemistry.py      # Cell chemistry database
│       │   ├── discharge.py      # Discharge/charge models
│       │   ├── thermal.py        # Thermal limits and models
│       │   └── pybamm_utils.py   # PyBaMM integration utilities
│       └── propulsion/           # Propulsion subsystem
│           ├── motor.py          # Motor model
│           ├── propeller.py      # Propeller/rotor model
│           └── propulsion.py     # Integrated propulsion system
├── examples/                     # Example scripts and notebooks
│   ├── vehicle_weight_calculator.py
│   ├── atmosphere_showcase.ipynb
│   └── quantities_showcase.ipynb
└── tests/                        # Comprehensive test suite
    ├── test_base.py
    ├── test_mass.py
    ├── test_quantities_new.py
    ├── test_battery.py
    ├── test_propulsion.py
    └── ... (and more)
```

## Testing

The project uses pytest with comprehensive test coverage.

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=evtoltools --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

### Test Organization

- `tests/test_base.py` - BaseQuantity abstract class
- `tests/test_mass.py` - Mass quantity comprehensive tests
- `tests/test_quantities_new.py` - All other quantity types
- `tests/test_resistance.py` - Resistance quantity tests
- `tests/test_battery.py` - Battery sizing, chemistry, and discharge
- `tests/test_discharge.py` - Discharge and charge model tests
- `tests/test_thermal.py` - Thermal framework tests
- `tests/test_propulsion.py` - Motors, propellers, propulsion systems
- `tests/test_vehicle_weight_calculator.py` - Integration tests

## Development

### Adding New Physical Quantities

To extend the units system:

1. Create a new file in `evtoltools/common/quantities/` (e.g., `acceleration.py`)
2. Define a class inheriting from `BaseQuantity`:
   ```python
   from ..base import BaseQuantity

   class Acceleration(BaseQuantity):
       _quantity_type = 'acceleration'
       _dimensionality = '[length] / [time]^2'
   ```
3. Add default unit and suggested units to `config.py`:
   ```python
   DEFAULT_UNITS = {
       'acceleration': 'm/s^2',
       # ... existing entries
   }

   ALLOWED_UNITS = {
       'acceleration': ['m/s^2', 'ft/s^2', 'g'],
       # ... existing entries
   }
   ```
4. Export in `quantities/__init__.py` and `common/__init__.py`

### Design Principles

- **Immutable operations** - All operations return new instances
- **Type safety** - Each physical quantity is a distinct class
- **Validated units** - Dimensionality validation prevents errors
- **Modular design** - Clean separation of concerns
- **Extensible architecture** - Easy to add new components and quantities

## Project Goals

This toolkit is being developed to support research and analysis of eVTOL aircraft design trade-offs, with focus on:

1. **Weight Analysis** - Component mass breakdown, MTOW optimization, weight fractions
2. **Performance Metrics** - Propulsion efficiency, hover power, disk loading
3. **Mission Optimization** - Range, endurance, payload-energy trade-offs
4. **Environmental Effects** - Altitude, temperature, hot day certification

The modular architecture enables incremental development while maintaining rigorous, unit-aware calculations throughout.

## Dependencies

### Required
- `numpy>=1.20` - Array operations and numerical computing
- `pint>=0.23` - Physical unit conversions and validation
- `ambiance>=0.3` - ISA atmosphere calculations
- `pybamm>=24.1` - Battery modeling and chemistry database
- `scipy>=1.10` - Scientific computing (interpolation for discharge curves)

### Examples
- `aerosandbox` - Optimization framework (used in vehicle_weight_calculator.py)
- `jupyter` - For running notebook examples

### Development
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Test coverage reporting

## API Reference

### Core Imports

```python
# Quantities
from evtoltools.common import (
    Mass, Length, Time, Temperature, Velocity, AngularVelocity,
    Area, Volume, Density, Force, Pressure, Power, Energy,
    Voltage, Current, Capacity, Moment, Frequency, Resistance
)

# Atmosphere
from evtoltools.common import (
    Atmosphere, Altitude, atmosphere_at_altitude, sea_level_atmosphere,
    ISA_SEA_LEVEL_TEMPERATURE, ISA_SEA_LEVEL_PRESSURE,
    ISA_SEA_LEVEL_DENSITY, ISA_SEA_LEVEL_SPEED_OF_SOUND
)

# Components
from evtoltools.components import (
    Payload, Battery, Motor, Propeller, PropulsionSystem,
    Structure, Avionics
)

# Battery modeling
from evtoltools.components.battery import (
    DischargeModel, AnalyticalDischargeModel, LookupTableDischargeModel,
    ChargeModel, SimpleChargeModel,
    ThermalLimits, SimpleThermalModel,
    load_discharge_model
)

# Helpers
from evtoltools.common import in_units_of  # Extract values from quantities
```

### Key Classes

**Altitude(value, unit)** - Semantic wrapper around Length for altitudes
- `sea_level()` - Create altitude at sea level (classmethod)
- `from_flight_level(fl)` - Create from flight level notation (FL100 = 10,000 ft)
- `from_pressure(pressure)` - Create from atmospheric pressure
- `from_density(density)` - Create from atmospheric density
- `to_flight_level()` - Convert to flight level number
- `is_in_troposphere()` - Check if below 11 km
- `agl_reference` - Human-readable AGL string

**Atmosphere(altitude, temperature_offset=None)**
- `temperature` - Atmospheric temperature
- `pressure` - Atmospheric pressure
- `density` - Air density
- `speed_of_sound` - Speed of sound
- `from_pressure_altitude(pressure)` - Create from pressure
- `from_density_altitude(density)` - Create from density

**Battery(cells_series, cells_parallel, cell_capacity, cell_mass, chemistry)**
- `nominal_voltage` - Pack nominal voltage
- `energy_capacity` - Total energy (Wh)
- `mass` - Total pack mass
- `internal_resistance` - Pack resistance (series/parallel scaling)
- `from_target_energy(...)` - Size from target energy
- `from_target_voltage(...)` - Size from target voltage
- `get_voltage(soc, c_rate)` - Voltage at operating conditions
- `current_from_c_rate(c_rate)` - Convert C-rate to current
- `c_rate_from_current(current)` - Convert current to C-rate
- `heat_generation_rate(current)` - I²R heat generation
- `get_charge_current(soc)` - Charge current from CC-CV profile
- `time_to_charge(start_soc, end_soc)` - Charge time estimate

**ThermalLimits(max_discharge_temp, derate_temp, min_temp)**
- `is_within_limits(temp, is_charging)` - Check temperature safety
- `get_derate_factor(temp)` - Power derate factor (0-1)
- `get_cold_derate_factor(temp)` - Cold temperature derate

**SimpleThermalModel(mass, specific_heat, cooling_coefficient)**
- `temperature_after(initial, heat_rate, duration, ambient)` - Predict temperature
- `steady_state_temperature(heat_rate, ambient)` - Equilibrium temperature

**PropulsionSystem(motors, propellers, num_units)**
- `hover_power_ideal(thrust, atmosphere)` - Ideal hover power
- `hover_shaft_power(thrust, atmosphere)` - Shaft power required
- `hover_electrical_power(thrust, atmosphere)` - Electrical power
- `disk_loading(thrust)` - Thrust per disk area
- `induced_velocity(thrust, atmosphere)` - Downwash velocity

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

[Add contributing guidelines here]

## Acknowledgments

This project uses:
- [Pint](https://github.com/hgrecco/pint) - Physical unit handling
- [Ambiance](https://github.com/aarondettmann/ambiance) - ISA atmosphere calculations
- [PyBaMM](https://www.pybamm.org/) - Battery chemistry database
- Design patterns inspired by [OpenMDAO](https://github.com/OpenMDAO/OpenMDAO)

## Citation

If you use eVTOL Tools in your research, please cite:

```
[Add citation information here]
```
