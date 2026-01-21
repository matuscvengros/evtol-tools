# eVTOL Tools

A Python package for eVTOL (electric Vertical Take-Off and Landing) aircraft analysis and design. This toolkit provides modular components for studying targeted design trade-offs in eVTOL design, with focus on weight analysis, performance metrics, and mission optimization.

## Features

### Units System

The core feature is a robust, type-safe units system built on `pint` that supports:

- **Object-oriented API** - Clean, intuitive interface for working with physical quantities
- **Automatic unit conversion** - Seamlessly convert between compatible units
- **NumPy array support** - Perform batch calculations on arrays of values
- **Type safety** - Each quantity type (Mass, Length, Velocity, etc.) is a distinct class
- **Arithmetic operations** - Natural mathematical operations with automatic unit handling
- **Validation** - Ensures dimensional consistency and prevents unit errors

### Currently Implemented Quantities

#### SI Base Quantities
- **Mass** - kg, g, lb, lbs, ton, tonne, oz
- **Length** - m, cm, mm, ft, in, mi, km, nmi
- **Time** - s, ms, min, hr, day
- **Temperature** - K, degC, degF
- **Current** - A, mA, uA, kA
- **Substance** - mol, mmol, kmol
- **Luminosity** - cd, lm

#### Derived Quantities
- **Velocity** - m/s, km/h, mph, knots, ft/s
- **Area** - m^2, cm^2, ft^2, in^2
- **Volume** - m^3, L, gal, ft^3
- **Density** - kg/m^3, g/cm^3, lb/ft^3
- **Force** - N, kN, lbf, kgf
- **Power** - W, kW, MW, hp, bhp
- **Energy** - J, kJ, MJ, Wh, kWh, mWh
- **Moment** - N*m, ft*lbf, in*lbf
- **AngularVelocity** - rad/s, rpm, deg/s
- **Voltage** - V, mV, kV
- **Capacity** - Ah, mAh, C

### Planned Features

- Acceleration
- Aerodynamic quantities (lift coefficient, drag coefficient)
- Additional mission analysis tools

## Installation

### Requirements

- Python 3.10 or higher
- NumPy >= 1.20
- Pint >= 0.23
- PyBaMM >= 24.1 (battery modeling)
- AeroSandbox (for examples - used in vehicle weight calculator)

### Install from source

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

### Basic Usage

```python
from evtoltools.common import Mass
import numpy as np

# Create mass quantities
aircraft_weight = Mass(1500, 'kg')
payload = Mass(500, 'kg')

# Convert units
weight_lbs = aircraft_weight.to('lbs')
print(f"Aircraft weight: {weight_lbs}")  # 3306.93 lbs

# Get numeric value in specific units
value = aircraft_weight.in_units_of('lbs')  # Returns float: 3306.93

# Arithmetic operations
total_weight = aircraft_weight + payload
print(f"Total: {total_weight}")  # 2000 kg

# Works with different units - automatic conversion
battery_kg = Mass(300, 'kg')
avionics_lbs = Mass(50, 'lbs')
combined = battery_kg + avionics_lbs  # Result in kg
```

### Array Operations

```python
# Create mass arrays for batch calculations
component_masses = Mass(np.array([100, 200, 300, 400]), 'kg')

# Convert entire array
masses_lbs = component_masses.to('lbs')

# Arithmetic with arrays
margin = Mass(10, 'kg')
with_margin = component_masses + margin  # Broadcasting works

# Get total
total = component_masses.magnitude.sum()  # 1000 kg
```

### Comparisons

```python
m1 = Mass(1, 'kg')
m2 = Mass(1, 'lbs')

# Comparisons work across units
if m1 > m2:
    print("1 kg is heavier than 1 lb")  # True

# Array comparisons return boolean arrays
masses = Mass(np.array([100, 200, 300]), 'kg')
threshold = Mass(150, 'kg')
heavy_components = masses > threshold  # [False, True, True]
```

## Examples

The `examples/` directory contains runnable scripts demonstrating eVTOL analysis workflows.

### Vehicle Weight Calculator

Calculates total vehicle weight (MTOW) and hover power requirements using MTOW fractions:

```bash
python examples/vehicle_weight_calculator.py
```

This comprehensive example demonstrates:
- **MTOW fraction approach** - Structure and avionics are fractions of total MTOW
- **Implicit weight solver** - Uses AeroSandbox optimizer to solve the circular dependency
- **Component modeling** - Payload, Battery, Propulsion System (motors + propellers)
- **Battery sizing** - Automatic cell configuration from target energy and voltage
- **Propulsion analysis** - Disk loading, Figure of Merit, multi-rotor configuration
- **Power chain calculation** - Ideal power → shaft power → electrical power
- **Performance metrics** - Hover endurance, power margin analysis

**Key insight:** When mass fractions are based on MTOW, adding battery mass increases MTOW, which increases structure/avionics, which further increases MTOW. This circular dependency is solved numerically using AeroSandbox's optimization framework:

```
MTOW = payload + structure + avionics + propulsion + battery
where: structure = MTOW × structure_fraction
       avionics = MTOW × avionics_fraction
```

**User-configurable parameters** (editable at top of script):
- Structure fraction (default: 30% of MTOW)
- Avionics fraction (default: 5% of MTOW)
- Payload mass (default: 120 kg)
- Target battery energy (default: 10 kWh)
- Target battery voltage (default: 48 V)
- Cell specifications (capacity: 5000 mAh, mass: 70 g)
- Propulsion configuration (4 motors, 2 m propellers)
- Motor efficiency (90%), Propeller Figure of Merit (0.70)

**Sample output:**
```
COMPONENT WEIGHT BREAKDOWN
----------------------------------------
  Payload        :   120.00 kg ( 42.4%)
  Structure      :    84.90 kg ( 30.0%)
  Avionics       :    14.15 kg (  5.0%)
  Propulsion     :    20.00 kg (  7.1%)
  Battery        :    43.95 kg ( 15.5%)
----------------------------------------
  MTOW           :   283.00 kg

PROPULSION SYSTEM
----------------------------------------
  Number of rotors:  4
  Total disk area:   12.57 m^2
  Motor efficiency:  90%
  Figure of Merit:   0.70
  Disk loading:      220.9 N/m^2

HOVER POWER REQUIREMENTS
----------------------------------------
  Vehicle weight:    2776.3 N
  Ideal power:       26.36 kW
  Shaft power:       39.64 kW (ideal / FM)
  Electrical power:  44.05 kW (shaft / motor eff)

HOVER ENDURANCE ESTIMATE
----------------------------------------
  Usable energy:     8000 Wh (80% of capacity)
  Hover endurance:   10.9 minutes
```

## Architecture

The package is organized as follows:

```
evtol-tools/
├── evtoltools/                   # Main package
│   ├── __init__.py
│   ├── common/                   # Units system
│   │   ├── __init__.py           # Public API exports
│   │   ├── registry.py           # Singleton pint UnitRegistry
│   │   ├── config.py             # Default and allowed units
│   │   ├── base.py               # BaseQuantity abstract class
│   │   └── quantities/           # Physical quantity implementations
│   │       ├── __init__.py
│   │       ├── mass.py
│   │       ├── length.py
│   │       ├── time.py
│   │       ├── velocity.py
│   │       ├── force.py
│   │       ├── power.py
│   │       ├── energy.py
│   │       └── ... (18 quantity types total)
│   └── components/               # Vehicle component models
│       ├── __init__.py
│       ├── base.py               # BaseComponent class
│       ├── payload.py            # Payload component
│       ├── structure.py          # Structure component
│       ├── avionics.py           # Avionics component
│       ├── battery/              # Battery subsystem
│       │   ├── __init__.py
│       │   ├── battery.py        # Battery pack model
│       │   └── chemistry.py      # Cell chemistry data
│       └── propulsion/           # Propulsion subsystem
│           ├── __init__.py
│           ├── propulsion.py     # Propulsion system
│           ├── motor.py          # Motor model
│           └── propeller.py      # Propeller model
├── examples/                     # Example scripts
│   └── vehicle_weight_calculator.py
├── tests/                        # Test suite
│   ├── conftest.py              # Shared pytest fixtures
│   ├── test_base.py             # BaseQuantity tests
│   ├── test_mass.py             # Mass quantity tests
│   ├── test_quantities_new.py   # Additional quantity tests
│   ├── test_components_simple.py
│   ├── test_battery.py
│   ├── test_propulsion.py
│   └── test_vehicle_weight_calculator.py
└── agents/                       # Agent policies
    └── POLICIES.md
```

### Design Principles

- **Immutable operations** - All operations return new instances for safety
- **Extensible architecture** - Easy to add new quantity types
- **Type safety** - Each physical quantity is a distinct class
- **Validated units** - Whitelist of allowed units per quantity type
- **Modular design** - Clean separation of concerns

### Adding New Quantities

To extend the units system with a new quantity type:

1. Create a new file in `evtoltools/common/quantities/` (e.g., `velocity.py`)
2. Define a class inheriting from `BaseQuantity`:
   ```python
   from ..base import BaseQuantity

   class Velocity(BaseQuantity):
       _quantity_type = 'velocity'
       _dimensionality = '[length] / [time]'
   ```
3. Add default and allowed units to `config.py`
4. Export the new class in `quantities/__init__.py` and `common/__init__.py`

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

The test suite is organized into multiple files covering different aspects of the codebase:

- `tests/test_base.py` - Tests for BaseQuantity abstract class functionality
- `tests/test_mass.py` - Comprehensive tests for Mass quantity
- `tests/test_quantities_new.py` - Tests for additional quantity types
- `tests/test_components_simple.py` - Tests for basic component models
- `tests/test_battery.py` - Battery pack and chemistry tests
- `tests/test_propulsion.py` - Motor, propeller, and propulsion system tests
- `tests/test_vehicle_weight_calculator.py` - Integration tests for weight calculator
- `tests/conftest.py` - Shared pytest fixtures and test utilities

### Test Coverage

- Comprehensive coverage of:
  - Unit construction and validation
  - Unit conversions across all quantity types
  - Arithmetic operations (addition, subtraction, multiplication, division)
  - Comparison operations
  - NumPy array operations
  - Component initialization and behavior
  - Battery sizing algorithms
  - Propulsion system calculations
  - Integration scenarios

## Development

### Setup Development Environment

```bash
# Activate conda environment (if using conda)
conda activate dev

# Install package in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests During Development

```bash
# Quick test run
pytest -x  # Stop on first failure

# Run specific test file
pytest tests/test_mass.py

# Run specific test
pytest tests/test_mass.py::TestMassConstruction::test_default_unit

# Run tests matching pattern
pytest -k "test_addition"
```

## Project Goals

This toolkit is being developed to support research and analysis of eVTOL aircraft design trade-offs, with initial focus on:

1. **Weight Analysis** - Component mass breakdown, weight fractions, center of gravity
2. **Performance Metrics** - Propulsion efficiency, aerodynamic performance
3. **Mission Optimization** - Range, endurance, payload capacity analysis

The modular architecture allows for incremental development of analysis capabilities while maintaining a solid foundation of validated, unit-aware calculations.

## Dependencies

### Required
- `numpy>=1.20` - Array operations and numerical computing
- `pint>=0.23` - Physical unit conversions and validation
- `pybamm>=24.1` - Battery modeling and chemistry data

### Examples
- `aerosandbox` - Optimization framework (used in vehicle_weight_calculator.py example)

### Development
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Test coverage reporting

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

## Acknowledgments

This project uses the excellent [Pint](https://github.com/hgrecco/pint) library for unit conversions, following best practices similar to [OpenMDAO](https://github.com/OpenMDAO/OpenMDAO) for handling physical quantities in engineering applications.
