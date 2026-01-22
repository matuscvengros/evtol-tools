# POLICIES.md

This document defines the coding policies and design principles for the evtol-tools codebase. These policies ensure consistency, maintainability, and clarity across all modules.

## Core Philosophy

**Explicit over implicit. Simple but robust. Consistent throughout.**

The codebase prioritizes:
1. **Readability** - Code should be self-documenting and obvious in intent
2. **Consistency** - Same patterns applied uniformly across all modules
3. **Accuracy** - Physics and engineering calculations must be correct
4. **Simplicity** - Minimal complexity to achieve the goal

---

## 1. Pythonic Code

Write idiomatic Python that leverages the language's strengths.

### Do

- Use list comprehensions, generator expressions, and built-in functions
- Leverage Python's duck typing where appropriate
- Use context managers (`with` statements) for resource management
- Prefer `property` decorators over explicit getter/setter methods
- Use `@classmethod` for alternative constructors (e.g., `Battery.from_target_energy()`)

### Don't

- Write Java-style boilerplate (e.g., explicit getters/setters for simple attributes)
- Use unnecessary classes where functions suffice
- Over-abstract when a simple function would do

### Examples

```python
# Good: Pythonic property access
motor_mass = motor.mass
total_power = sum(m.max_power for m in motors)

# Bad: Java-style getters
motor_mass = motor.get_mass()
total_power = sum(m.getMaxPower() for m in motors)
```

---

## 2. PEP Style Guidelines

All code must conform to PEP 8 and relevant PEP standards.

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | `PascalCase` | `PropulsionSystem`, `BaseQuantity` |
| Functions/Methods | `snake_case` | `hover_power_ideal()`, `to_default()` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_UNITS`, `ISA_SEA_LEVEL_DENSITY` |
| Private attributes | `_leading_underscore` | `_quantity`, `_dimensionality` |
| Module-level | `snake_case` | `registry.py`, `base.py` |

### Line Length

- Maximum 88 characters (Black formatter default)
- Break long lines at logical points (after commas, before operators)

### Imports

Order imports as:
1. Standard library
2. Third-party packages
3. Local imports

```python
# Good: Proper import ordering
from abc import ABC
from typing import Union, Optional

import numpy as np
from pint import Quantity as PintQuantity

from evtoltools.common.units.registry import ureg, Q_
from evtoltools.common.units.config import DEFAULT_UNITS
```

---

## 3. Documentation: Google Docstrings

Use Google-style docstrings for all public classes, methods, and functions.

### Format

```python
def hover_power_ideal(self, thrust: Force, density: Density) -> Power:
    """Calculate ideal hover power using momentum theory.

    Computes the theoretical minimum power required for hover based on
    actuator disk theory: P = T^(3/2) / sqrt(2 * rho * A).

    Args:
        thrust: Total thrust required (equals weight in hover).
        density: Air density at operating conditions.

    Returns:
        Ideal hover power (before efficiency losses).

    Raises:
        ValueError: If thrust or density is non-positive.

    Example:
        >>> power = propulsion.hover_power_ideal(
        ...     Force(14715, 'N'),
        ...     Density(1.225, 'kg/m^3')
        ... )
        >>> power.to('kW')
        Power(45.2, 'kW')
    """
```

### Requirements

- **All public methods** must have docstrings
- **Args section** required if method takes parameters
- **Returns section** required if method returns a value
- **Raises section** required if method can raise exceptions
- **Example section** encouraged for complex methods

### Class Docstrings

```python
class Battery:
    """Lithium-ion battery pack model for eVTOL applications.

    Models cell configuration, energy capacity, power limits, and thermal
    behavior. Supports sizing from target energy, voltage, or capacity.

    Attributes:
        cells_series: Number of cells in series.
        cells_parallel: Number of parallel strings.
        nominal_voltage: Pack nominal voltage.
        energy_capacity: Total energy capacity.

    Example:
        >>> battery = Battery.from_target_energy(
        ...     target_energy=Energy(50, 'kWh'),
        ...     target_voltage=Voltage(400, 'V'),
        ...     cell_capacity=Capacity(5000, 'mAh'),
        ...     cell_mass=Mass(70, 'g')
        ... )
    """
```

---

## 4. Direct Mathematical Access

Objects holding mathematical values must support direct mathematical operations.

### Principle

If an object represents a mathematical quantity, operations should be performed **on the object itself**, not through accessor methods that return raw values.

### Implementation Pattern

The `BaseQuantity` class exemplifies this pattern:

```python
# Good: Direct operations on quantity objects
total_mass = aircraft_mass + payload_mass
power_ratio = hover_power / max_power
scaled_force = thrust * 1.2

# Bad: Extracting values, computing, then re-wrapping
total_mass = Mass(
    aircraft_mass.in_units_of('kg') + payload_mass.in_units_of('kg'),
    'kg'
)
```

### Required Operations for Mathematical Objects

All quantity types must implement:

| Operation | Method | Example |
|-----------|--------|---------|
| Addition | `__add__`, `__radd__` | `mass1 + mass2` |
| Subtraction | `__sub__`, `__rsub__` | `mass1 - mass2` |
| Multiplication | `__mul__`, `__rmul__` | `mass * 2.0` |
| Division | `__truediv__`, `__rtruediv__` | `power / time` |
| Negation | `__neg__` | `-velocity` |
| Absolute value | `__abs__` | `abs(temperature_delta)` |
| Power | `__pow__` | `length ** 2` |
| Comparisons | `__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__` | `mass1 > mass2` |

### Cross-Type Operations

When operations produce different quantity types, return the appropriate type or a raw pint Quantity:

```python
# Force * Length -> returns pint Quantity (moment dimensionality)
moment = force * arm_length

# Power / Velocity -> returns pint Quantity (force dimensionality)
drag = power / velocity
```

---

## 5. Explicit Over Implicit

Code intent should be clear without requiring knowledge of hidden behavior.

### Explicit Type Annotations

```python
# Good: Clear parameter and return types
def disk_loading(self, thrust: Force) -> Pressure:
    ...

# Bad: Ambiguous types
def disk_loading(self, thrust):
    ...
```

### Explicit Unit Handling

```python
# Good: Units are explicit in the code
altitude = Length(5000, 'ft')
density = atmosphere.density  # Returns Density object

# Bad: Magic numbers without units
altitude = 5000  # feet? meters? unclear
density = 1.1  # kg/m^3? lb/ft^3? unclear
```

### Explicit Construction

```python
# Good: Named parameters for clarity
battery = Battery(
    cells_series=14,
    cells_parallel=4,
    cell_capacity=Capacity(5, 'Ah'),
    cell_mass=Mass(50, 'g'),
    chemistry='lithium_ion'
)

# Bad: Positional arguments for complex constructors
battery = Battery(14, 4, Capacity(5, 'Ah'), Mass(50, 'g'), 'lithium_ion')
```

---

## 6. Simplicity with Robustness

Keep code simple, but don't sacrifice correctness or safety.

### Balance Simplicity and Validation

```python
# Good: Simple with appropriate validation
def __init__(self, efficiency: float):
    if not 0.0 < efficiency <= 1.0:
        raise ValueError(f"Efficiency must be in (0, 1], got {efficiency}")
    self.efficiency = efficiency

# Over-engineered: Unnecessary complexity
def __init__(self, efficiency: float):
    self._validate_efficiency_range(efficiency)
    self._check_efficiency_precision(efficiency)
    self._log_efficiency_warning_if_low(efficiency)
    self.efficiency = self._normalize_efficiency(efficiency)

# Under-engineered: No validation leads to silent errors
def __init__(self, efficiency: float):
    self.efficiency = efficiency  # Accepts efficiency=5.0 silently
```

### Prefer Standard Library

Use built-in Python and numpy operations over custom implementations:

```python
# Good: Use numpy for array operations
masses_kg = masses.to('kg').magnitude
total = np.sum(masses_kg)

# Bad: Custom loop for simple aggregation
total = 0
for mass in masses:
    total += mass.in_units_of('kg')
```

---

## 7. Consistency and Cohesion

The same idiom should be used throughout the entire codebase.

### Quantity Access Pattern

Choose **one** access pattern and use it everywhere:

```python
# Preferred: Direct object access with .to() for conversion
motor_mass_kg = motor.mass.to('kg')
power_kw = propulsion.hover_power.to('kW')

# Also acceptable: .in_units_of() for numeric extraction
mass_value = motor.mass.in_units_of('kg')  # Returns float

# NOT acceptable: Mixing patterns inconsistently
# Module A uses: mass.to('kg').magnitude
# Module B uses: mass.in_units_of('kg')
# Module C uses: float(mass.to('kg'))
```

### Chosen Idioms for This Codebase

| Pattern | Preferred Idiom | Avoid |
|---------|-----------------|-------|
| Get quantity in new units | `quantity.to('unit')` | Creating new wrapper |
| Get numeric value | `quantity.in_units_of('unit')` | `quantity.to('unit').magnitude` |
| Arithmetic | Direct operators (`+`, `-`, `*`, `/`) | Method calls |
| Comparisons | Direct operators (`<`, `>`, `==`) | `.compare()` methods |
| Default units | Let constructor use defaults | Explicit default unit strings |

### Module Structure Consistency

All quantity modules follow the same structure:

```python
"""Brief description of the quantity.

Extended description if needed.
"""

from pint.util import UnitsContainer

from evtoltools.common.units.base import BaseQuantity


class QuantityName(BaseQuantity):
    """Docstring with examples."""

    _quantity_type = 'quantity_name'
    _dimensionality = UnitsContainer({...})
```

### Component Class Consistency

All component classes follow:

```python
class ComponentName:
    """Component docstring."""

    def __init__(self, ...):
        """Constructor with validation."""
        ...

    @classmethod
    def from_alternative_params(cls, ...) -> 'ComponentName':
        """Alternative constructor."""
        ...

    @property
    def derived_quantity(self) -> QuantityType:
        """Computed property returning quantity object."""
        ...
```

---

## 8. Testing Requirements

All new code must have corresponding tests.

### Test Coverage

- All public methods must have tests
- Edge cases and error conditions must be tested
- Array/scalar behavior must be tested for quantity types

### Test Naming

```python
class TestBatteryConstruction:
    def test_from_target_energy_creates_valid_pack(self):
        ...

    def test_raises_on_negative_capacity(self):
        ...
```

### Test Organization

```
tests/
├── test_<module>.py          # Unit tests per module
├── test_<component>.py       # Component tests
└── test_integration.py       # Cross-module integration tests
```

---

## 9. Progressive Complexity Ordering

**All files must be organized from simplest to most complex, top to bottom.**

This is a strict structural requirement. As the reader scrolls through any file, the cognitive load should increase gradually. Simple, foundational elements appear first; complex logic appears last.

### Rationale

- **Onboarding** - New readers understand foundations before encountering complexity
- **Debugging** - Simple elements are checked first, naturally
- **Maintenance** - Complexity is isolated to the bottom, not scattered throughout
- **Consistency** - Every file follows the same predictable structure

### Module-Level Ordering (Top to Bottom)

```
1. Module docstring
2. Imports (standard library → third-party → local)
3. Constants and module-level configuration
4. Type aliases and simple type definitions
5. Exception classes (if any)
6. Helper functions (simplest first)
7. Main classes (simplest first, base classes before derived)
8. Complex/composite functions
9. Module-level initialization code (if any)
```

### Class-Level Ordering (Top to Bottom)

```
1. Class docstring
2. Class-level constants and type hints
3. __slots__ (if used)
4. __init__
5. Alternative constructors (@classmethod factories) - simplest first
6. Properties (@property) - simplest first
7. Public methods - ordered by complexity:
   a. Simple accessors and converters
   b. Single-operation methods
   c. Multi-step methods
   d. Complex algorithms
8. Dunder methods (__str__, __repr__, __eq__, etc.)
9. Private/internal methods (_prefixed) - simplest first
10. Static methods (@staticmethod) - if truly standalone utilities
```

### Complexity Indicators

Use these criteria to determine relative complexity:

| Lower Complexity | Higher Complexity |
|------------------|-------------------|
| Fewer lines | More lines |
| No branching (if/else) | Multiple branches |
| No loops | Nested loops |
| Single return | Multiple return paths |
| No external calls | Calls other methods/functions |
| Pure data access | Data transformation |
| No error handling | Try/except blocks |
| Single responsibility | Orchestrates multiple operations |

### Example: Correctly Ordered Class

```python
class Battery:
    """Battery pack model."""

    # Class constants (simplest)
    DEFAULT_OVERHEAD = 0.15
    CELL_VOLTAGE_NOMINAL = 3.7

    def __init__(self, cells_series: int, cells_parallel: int, ...):
        """Constructor - foundational."""
        ...

    # Simple factory (one calculation)
    @classmethod
    def from_target_voltage(cls, target_voltage: Voltage, ...) -> 'Battery':
        """Create battery sized for target voltage."""
        cells_series = int(target_voltage.in_units_of('V') / cls.CELL_VOLTAGE_NOMINAL)
        return cls(cells_series=cells_series, ...)

    # More complex factory (multiple calculations)
    @classmethod
    def from_target_energy(cls, target_energy: Energy, ...) -> 'Battery':
        """Create battery sized for target energy - requires iteration."""
        ...

    # Simple property (direct return)
    @property
    def total_cells(self) -> int:
        """Total cell count."""
        return self.cells_series * self.cells_parallel

    # Slightly more complex property (one calculation)
    @property
    def nominal_voltage(self) -> Voltage:
        """Pack nominal voltage."""
        return Voltage(self.cells_series * self.CELL_VOLTAGE_NOMINAL, 'V')

    # Property with conditional logic (more complex)
    @property
    def energy_capacity(self) -> Energy:
        """Total energy capacity with overhead adjustment."""
        base_energy = self.nominal_voltage * self.total_capacity
        if self._include_overhead:
            return base_energy * (1 - self.DEFAULT_OVERHEAD)
        return base_energy

    # Simple public method (one operation)
    def current_from_c_rate(self, c_rate: float) -> Current:
        """Convert C-rate to current."""
        return Current(c_rate * self.total_capacity.in_units_of('Ah'), 'A')

    # More complex method (multiple steps)
    def get_voltage(self, soc: float, c_rate: float = 0.0) -> Voltage:
        """Get voltage at operating conditions."""
        open_circuit = self._discharge_model.voltage_at_soc(soc)
        ir_drop = self._calculate_ir_drop(c_rate)
        return open_circuit - ir_drop

    # Complex method (orchestration, error handling)
    def simulate_discharge(self, current: Current, duration: Time) -> dict:
        """Simulate discharge over time - complex multi-step."""
        self._validate_discharge_params(current, duration)
        results = []
        for t in self._time_steps(duration):
            voltage = self.get_voltage(self._soc, self.c_rate_from_current(current))
            heat = self.heat_generation_rate(current)
            self._update_state(current, voltage, heat, t)
            results.append(self._snapshot())
        return self._compile_results(results)

    # Dunder methods
    def __repr__(self) -> str:
        return f"Battery({self.cells_series}S{self.cells_parallel}P)"

    # Private helpers (support the public methods above)
    def _calculate_ir_drop(self, c_rate: float) -> Voltage:
        """Internal resistance voltage drop."""
        ...

    def _validate_discharge_params(self, current: Current, duration: Time) -> None:
        """Validate inputs for discharge simulation."""
        ...

    def _update_state(self, ...) -> None:
        """Update internal state during simulation."""
        ...
```

### Example: Correctly Ordered Module

```python
"""Propulsion calculations for eVTOL aircraft.

Provides momentum theory calculations and propulsion system modeling.
"""

# Imports (standard → third-party → local)
from typing import Union, Optional

import numpy as np

from evtoltools.common import Force, Power, Density, Area


# Constants (simple values)
GRAVITY = 9.80665  # m/s^2
AIR_DENSITY_SEA_LEVEL = 1.225  # kg/m^3


# Simple helper function
def disk_area(diameter: float) -> float:
    """Calculate rotor disk area from diameter."""
    return np.pi * (diameter / 2) ** 2


# Slightly more complex helper
def induced_velocity(thrust: float, density: float, area: float) -> float:
    """Calculate induced velocity from momentum theory."""
    return np.sqrt(thrust / (2 * density * area))


# More complex function (uses helpers above)
def ideal_hover_power(thrust: float, density: float, area: float) -> float:
    """Calculate ideal hover power using momentum theory."""
    v_i = induced_velocity(thrust, density, area)
    return thrust * v_i


# Main class (uses all of the above)
class PropulsionSystem:
    """Complete propulsion system model."""
    ...
```

### Enforcement

This policy is **strictly enforced**. During code review, verify:

1. Constants appear before functions
2. Simple functions appear before complex functions
3. Within classes, the ordering matches the template above
4. No complex logic appears early in a file while simple logic appears later

**If reorganization is needed, refactor before merging.**

---

## Summary Checklist

Before committing code, verify:

- [ ] Code follows PEP 8 naming conventions
- [ ] All public APIs have Google-style docstrings
- [ ] Mathematical objects support direct operations
- [ ] Types are explicitly annotated
- [ ] Units are explicit, not implicit magic numbers
- [ ] Patterns match existing codebase idioms
- [ ] Tests cover new functionality
- [ ] Validation exists for external inputs
- [ ] No unnecessary complexity or over-engineering
- [ ] **File structure follows progressive complexity (simple → complex, top → bottom)**
