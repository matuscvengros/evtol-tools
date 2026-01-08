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

- **Mass/Weight** - kg, g, lb, lbs, ton, tonne, oz

### Planned Features

- Length, area, volume
- Velocity, acceleration
- Power, energy
- Force, moment
- Aerodynamic quantities (lift coefficient, drag coefficient)
- Propulsion metrics
- Mission analysis tools

## Installation

### Requirements

- Python 3.10 or higher
- NumPy >= 1.20
- Pint >= 0.23

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

## Architecture

The package is organized as follows:

```
evtoltools/
├── __init__.py
└── common/
    ├── __init__.py          # Public API
    ├── registry.py          # Singleton pint UnitRegistry
    ├── config.py            # Default and allowed units
    ├── base.py              # BaseQuantity abstract class
    └── quantities/
        ├── __init__.py
        └── mass.py          # Mass quantity implementation
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

The project uses pytest with comprehensive test coverage (currently 88%).

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

- `tests/test_mass.py` - Tests for Mass quantity (47 tests)
- `tests/test_base.py` - Tests for BaseQuantity functionality (29 tests)
- `tests/conftest.py` - Shared pytest fixtures

### Current Test Coverage

- Total: 88.10% coverage
- 76 tests passing
- Comprehensive coverage of:
  - Unit construction and validation
  - Unit conversions
  - Arithmetic operations
  - Array operations
  - Edge cases

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

### Development
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Test coverage reporting

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

## Acknowledgments

This project uses the excellent [Pint](https://github.com/hgrecco/pint) library for unit conversions, following best practices similar to [OpenMDAO](https://github.com/OpenMDAO/OpenMDAO) for handling physical quantities in engineering applications.
