# eVTOL Tools

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
- **Cell configuration** - Series/parallel string design
- **Sizing methods** - From target energy, voltage, or capacity
- **Chemistry support** - Lithium-ion, NMC, LFP cell parameters
- **Power limits** - C-rating based charge/discharge constraints
- **Mass calculations** - Cells plus BMS/packaging overhead

### Atmospheric Calculations
- **ISA model** - International Standard Atmosphere (0-80 km altitude)
- **Temperature offsets** - Hot day (ISA+) and cold day (ISA-) analysis
- **Altitude effects** - Density impact on power, tip speeds, performance
- **Pressure/density altitude** - Conversion between altitude references
- **NumPy array support** - Batch calculations for altitude profiles

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

### Atmospheric Calculations

```python
from evtoltools.common import Atmosphere, Length, Temperature

# Standard atmosphere at 5000 ft
atm = Atmosphere(Length(5000, 'ft'))
print(f"Temperature: {atm.temperature.to('degC')}")
print(f"Pressure:    {atm.pressure.to('kPa')}")
print(f"Density:     {atm.density.to('kg/m^3')}")

# Hot day analysis (ISA + 20K)
atm_hot = Atmosphere(
    altitude=Length(5000, 'ft'),
    temperature_offset=Temperature(20, 'K')
)
print(f"Hot day density: {atm_hot.density.to('kg/m^3')}")

# Calculate hover power at altitude
power_at_altitude = propulsion.hover_electrical_power(
    weight,
    atmosphere=atm_hot
)
print(f"Power required: {power_at_altitude.to('kW')}")
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

### Atmospheric Effects

Density decreases with altitude, affecting performance:

```
Power ∝ 1/sqrt(ρ)   (hover power increases at altitude)
v_induced ∝ 1/sqrt(ρ) (downwash velocity increases)
V_tip_max = M_limit × a(h)  (tip speed limit decreases)

where:
  a(h) = speed of sound at altitude h
  M_limit = tip Mach limit (typically 0.7-0.9)
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
│   │   ├── base.py               # BaseQuantity abstract class
│   │   ├── registry.py           # Pint UnitRegistry singleton
│   │   ├── config.py             # Default and allowed units
│   │   ├── atmosphere.py         # ISA atmosphere model
│   │   └── quantities/           # 20+ physical quantity types
│   │       ├── mass.py
│   │       ├── length.py
│   │       ├── velocity.py
│   │       ├── power.py
│   │       └── ... (and more)
│   └── components/               # Vehicle component models
│       ├── base.py               # BaseComponent class
│       ├── payload.py            # Payload component
│       ├── structure.py          # Structure component
│       ├── avionics.py           # Avionics component
│       ├── battery/              # Battery subsystem
│       │   ├── battery.py        # Battery pack model
│       │   └── chemistry.py      # Cell chemistry database
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
- `tests/test_battery.py` - Battery sizing and chemistry
- `tests/test_propulsion.py` - Motors, propellers, propulsion systems
- `tests/test_vehicle_weight_calculator.py` - Integration tests

See `CLAUDE.md` for detailed pytest command reference.

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
    Voltage, Current, Capacity, Moment, Frequency
)

# Atmosphere
from evtoltools.common import (
    Atmosphere, atmosphere_at_altitude, sea_level_atmosphere,
    ISA_SEA_LEVEL_TEMPERATURE, ISA_SEA_LEVEL_PRESSURE,
    ISA_SEA_LEVEL_DENSITY, ISA_SEA_LEVEL_SPEED_OF_SOUND
)

# Components
from evtoltools.components import (
    Payload, Battery, Motor, Propeller, PropulsionSystem,
    Structure, Avionics
)

# Helpers
from evtoltools.common import in_units_of  # Extract values from quantities
```

### Key Classes

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
- `from_target_energy(...)` - Size from target energy
- `from_target_voltage(...)` - Size from target voltage

**PropulsionSystem(motors, propellers, num_units)**
- `hover_power_ideal(thrust, atmosphere)` - Ideal hover power
- `hover_shaft_power(thrust, atmosphere)` - Shaft power required
- `hover_electrical_power(thrust, atmosphere)` - Electrical power
- `disk_loading(thrust)` - Thrust per disk area
- `induced_velocity(thrust, atmosphere)` - Downwash velocity

## License

[Add your license here]

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
