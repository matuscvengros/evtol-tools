"""Pytest configuration and shared fixtures for evtol-tools tests."""

import pytest
import numpy as np
from evtoltools.common import Mass


@pytest.fixture
def simple_mass():
    """Fixture providing a simple Mass instance in kg."""
    return Mass(100, 'kg')


@pytest.fixture
def simple_mass_lbs():
    """Fixture providing a simple Mass instance in lbs."""
    return Mass(220.462, 'lbs')


@pytest.fixture
def array_masses():
    """Fixture providing Mass instance with array values."""
    values = np.array([100, 200, 300, 400, 500])
    return Mass(values, 'kg')


@pytest.fixture
def aircraft_components():
    """Fixture providing realistic aircraft component masses."""
    return {
        'fuselage': Mass(800, 'kg'),
        'wings': Mass(400, 'kg'),
        'motors': Mass(200, 'kg'),
        'battery': Mass(600, 'kg'),
        'avionics': Mass(150, 'kg'),
        'landing_gear': Mass(100, 'kg'),
    }


@pytest.fixture
def zero_mass():
    """Fixture providing a zero Mass instance."""
    return Mass(0, 'kg')


@pytest.fixture
def large_mass():
    """Fixture providing a large Mass value."""
    return Mass(10000, 'kg')


@pytest.fixture
def small_mass():
    """Fixture providing a small Mass value."""
    return Mass(0.001, 'kg')


@pytest.fixture
def random_masses():
    """Fixture providing random array of masses for statistical tests."""
    np.random.seed(42)  # For reproducibility
    values = np.random.uniform(50, 500, size=100)
    return Mass(values, 'kg')


# Parametrize fixtures for common conversions
@pytest.fixture(params=[
    (1, 'kg', 'lbs', 2.20462),
    (1, 'kg', 'g', 1000),
    (1000, 'g', 'kg', 1),
    (1, 'ton', 'lbs', 2000),
    (1, 'tonne', 'kg', 1000),
])
def mass_conversion_case(request):
    """Parametrized fixture for common mass conversions.

    Returns tuple of (value, from_unit, to_unit, expected_result).
    """
    return request.param


@pytest.fixture(params=['kg', 'lbs', 'g', 'oz', 'ton', 'tonne'])
def valid_mass_unit(request):
    """Parametrized fixture for all valid mass units."""
    return request.param


@pytest.fixture
def registry():
    """Fixture providing access to the pint registry."""
    from evtoltools.common import ureg
    return ureg
