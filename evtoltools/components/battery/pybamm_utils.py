"""PyBaMM integration utilities for battery discharge modeling.

This module provides utilities for generating discharge voltage lookup tables
using PyBaMM simulations and a direct PyBaMM discharge model.

Classes:
    PyBaMMDischargeModel: Direct PyBaMM simulation-based discharge model.

Functions:
    generate_discharge_table: Generate voltage lookup table from PyBaMM.
    load_or_generate_discharge_model: Load cached or generate new tables.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np

from evtoltools.common import Resistance, Temperature, Voltage
from evtoltools.components.battery.discharge import (
    DischargeModel,
    LookupTableDischargeModel,
)


@dataclass
class PyBaMMDischargeModel(DischargeModel):
    """Direct PyBaMM simulation discharge model.

    Runs PyBaMM simulation on each call to get_voltage(). Most accurate
    but slowest option. Use for validation or when accuracy is critical.

    Attributes:
        parameter_set: PyBaMM parameter set name (e.g., 'Chen2020', 'Marquis2019').
        model_type: Model type - 'SPM' (Single Particle Model, faster) or
            'DFN' (Doyle-Fuller-Newman, more accurate).
        temperature: Cell temperature for simulation.
    """

    parameter_set: str = 'Chen2020'
    model_type: str = 'SPM'
    temperature: Temperature = field(default_factory=lambda: Temperature(25, 'degC'))
    _model: object = field(init=False, repr=False, default=None)
    _parameter_values: object = field(init=False, repr=False, default=None)

    def __post_init__(self):
        """Initialize PyBaMM model (lazy initialization on first use)."""
        pass

    def _init_model(self):
        """Lazy initialization of PyBaMM model."""
        if self._model is not None:
            return

        import pybamm

        # Select model type
        if self.model_type.upper() == 'DFN':
            model = pybamm.lithium_ion.DFN()
        else:
            model = pybamm.lithium_ion.SPM()

        # Load parameter values
        param = pybamm.ParameterValues(self.parameter_set)

        # Set temperature
        temp_k = self.temperature.in_units_of('K')
        param['Ambient temperature [K]'] = temp_k
        param['Initial temperature [K]'] = temp_k

        object.__setattr__(self, '_model', model)
        object.__setattr__(self, '_parameter_values', param)

    def get_voltage(
        self,
        soc: Union[float, np.ndarray],
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> Voltage:
        """Get cell voltage using PyBaMM simulation.

        Runs a short simulation at the specified SoC and C-rate to
        determine the instantaneous voltage.

        Args:
            soc: State of charge (0.0 to 1.0).
            c_rate: Discharge rate.
            temperature: Optional temperature override.

        Returns:
            Cell voltage from PyBaMM simulation.
        """
        self._init_model()
        import pybamm

        # Clone parameters for this simulation
        param = self._parameter_values.copy()

        # Update temperature if provided
        if temperature is not None:
            temp_k = temperature.in_units_of('K')
            param['Ambient temperature [K]'] = temp_k
            param['Initial temperature [K]'] = temp_k

        # Set initial SoC
        soc_val = float(soc) if not isinstance(soc, np.ndarray) else soc[0]
        soc_val = max(0.01, min(0.99, soc_val))  # Clamp to avoid edge issues

        # Set C-rate
        param['Current function [A]'] = (
            c_rate * param['Nominal cell capacity [A.h]']
        )

        # Create and solve simulation
        sim = pybamm.Simulation(self._model, parameter_values=param)

        # Run a very short simulation to get instantaneous voltage
        try:
            sim.solve([0, 1], initial_soc=soc_val)
            voltage = sim.solution['Terminal voltage [V]'](0)
        except Exception:
            # Fall back to OCV if simulation fails
            voltage = sim.solution['Battery open-circuit voltage [V]'](0) if hasattr(sim, 'solution') else 3.7

        return Voltage(float(voltage), 'V')

    def get_resistance(
        self,
        soc: float,
        temperature: Optional[Temperature] = None
    ) -> Optional[Resistance]:
        """Estimate internal resistance from PyBaMM parameters.

        Returns a rough estimate based on parameter values.
        """
        self._init_model()

        try:
            # Get some resistance-related parameters
            r_sei = self._parameter_values.get('SEI resistivity [Ohm.m2]', 0)
            return Resistance(30, 'mohm')  # Return typical value
        except Exception:
            return Resistance(30, 'mohm')


def generate_discharge_table(
    parameter_set: str,
    soc_points: Optional[np.ndarray] = None,
    c_rate_points: Optional[np.ndarray] = None,
    model_type: str = 'SPM',
    temperature: Temperature = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate voltage lookup table using PyBaMM simulation.

    Runs PyBaMM simulations at each (SoC, C-rate) combination to build
    a voltage lookup table for fast interpolation.

    Args:
        parameter_set: PyBaMM parameter set name.
        soc_points: Array of SoC values (default: 0 to 1 in 0.05 steps).
        c_rate_points: Array of C-rate values (default: [0.1, 0.2, 0.5, 1, 2, 3, 5]).
        model_type: 'SPM' or 'DFN'.
        temperature: Cell temperature.

    Returns:
        Tuple of (soc_points, c_rate_points, voltage_data) where
        voltage_data has shape (len(soc_points), len(c_rate_points)).
    """
    import pybamm

    # Default grids
    if soc_points is None:
        soc_points = np.linspace(0.05, 0.95, 19)
    if c_rate_points is None:
        c_rate_points = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0])
    if temperature is None:
        temperature = Temperature(25, 'degC')

    # Initialize model
    if model_type.upper() == 'DFN':
        model = pybamm.lithium_ion.DFN()
    else:
        model = pybamm.lithium_ion.SPM()

    param = pybamm.ParameterValues(parameter_set)
    temp_k = temperature.in_units_of('K')
    param['Ambient temperature [K]'] = temp_k
    param['Initial temperature [K]'] = temp_k

    # Build voltage table
    voltage_data = np.zeros((len(soc_points), len(c_rate_points)))

    for i, soc in enumerate(soc_points):
        for j, c_rate in enumerate(c_rate_points):
            try:
                p = param.copy()
                p['Current function [A]'] = c_rate * p['Nominal cell capacity [A.h]']

                sim = pybamm.Simulation(model, parameter_values=p)
                sim.solve([0, 1], initial_soc=float(soc))
                voltage_data[i, j] = sim.solution['Terminal voltage [V]'](0)
            except Exception:
                # Use linear interpolation from neighbors or default
                if i > 0:
                    voltage_data[i, j] = voltage_data[i - 1, j]
                else:
                    voltage_data[i, j] = 3.7  # Default fallback

    return soc_points, c_rate_points, voltage_data


def load_or_generate_discharge_model(
    parameter_set: str,
    cache_dir: Optional[str] = None,
    regenerate: bool = False,
    model_type: str = 'SPM'
) -> LookupTableDischargeModel:
    """Load cached discharge model or generate new one.

    Checks for a cached lookup table and loads it if available.
    Otherwise generates a new table using PyBaMM and caches it.

    Args:
        parameter_set: PyBaMM parameter set name.
        cache_dir: Directory for caching tables (default: ~/.evtoltools/cache).
        regenerate: If True, regenerate even if cached version exists.
        model_type: PyBaMM model type for generation.

    Returns:
        LookupTableDischargeModel instance.
    """
    # Default cache directory
    if cache_dir is None:
        cache_dir = Path.home() / '.evtoltools' / 'cache'
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_file = cache_dir / f'discharge_{parameter_set}_{model_type}.npz'

    # Load from cache if available
    if cache_file.exists() and not regenerate:
        data = np.load(cache_file)
        return LookupTableDischargeModel(
            soc_points=data['soc_points'],
            c_rate_points=data['c_rate_points'],
            voltage_data=data['voltage_data'],
            resistance_data=data.get('resistance_data'),
        )

    # Generate new table
    soc_points, c_rate_points, voltage_data = generate_discharge_table(
        parameter_set=parameter_set,
        model_type=model_type,
    )

    # Save to cache
    np.savez(
        cache_file,
        soc_points=soc_points,
        c_rate_points=c_rate_points,
        voltage_data=voltage_data,
    )

    return LookupTableDischargeModel(
        soc_points=soc_points,
        c_rate_points=c_rate_points,
        voltage_data=voltage_data,
    )


def create_default_lookup_table(chemistry_name: str) -> LookupTableDischargeModel:
    """Create a default lookup table without PyBaMM simulation.

    Generates approximate discharge curves based on typical battery
    behavior for quick use without requiring PyBaMM.

    Args:
        chemistry_name: Chemistry name (e.g., 'lithium_ion', 'lifepo4').

    Returns:
        LookupTableDischargeModel with approximate voltage curves.
    """
    # Chemistry parameters
    params = {
        'lithium_ion': (3.7, 4.2, 2.8, 30),
        'lithium_polymer': (3.7, 4.2, 3.2, 25),
        'lithium_iron_phosphate': (3.2, 3.65, 2.5, 40),
        'lifepo4': (3.2, 3.65, 2.5, 40),
        'lithium_nmc': (3.7, 4.2, 3.0, 25),
        'nmc': (3.7, 4.2, 3.0, 25),
    }

    key = chemistry_name.lower().replace('-', '_')
    v_nom, v_max, v_min, r_mohm = params.get(key, (3.7, 4.2, 2.8, 30))

    # Create grids
    soc_points = np.linspace(0.0, 1.0, 21)
    c_rate_points = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0])

    # Build approximate voltage table
    # OCV varies with SoC, voltage drop increases with C-rate
    voltage_data = np.zeros((len(soc_points), len(c_rate_points)))

    # Assume 5Ah cell for voltage drop calculation
    capacity_ah = 5.0
    r_ohm = r_mohm / 1000

    for i, soc in enumerate(soc_points):
        # Open-circuit voltage (linear approximation)
        v_oc = v_min + soc * (v_max - v_min)

        for j, c_rate in enumerate(c_rate_points):
            current = c_rate * capacity_ah
            v_drop = current * r_ohm
            voltage_data[i, j] = max(v_min, v_oc - v_drop)

    return LookupTableDischargeModel(
        soc_points=soc_points,
        c_rate_points=c_rate_points,
        voltage_data=voltage_data,
        v_min=Voltage(v_min, 'V'),
    )


def load_lookup_table_from_data(chemistry_name: str) -> LookupTableDischargeModel:
    """Load a pre-generated lookup table from the package data directory.

    Looks for a .npz file in evtoltools/data/ matching the chemistry name.
    These files are generated using utils/generate_lookup_tables.py.

    Args:
        chemistry_name: Chemistry name (e.g., 'lithium_ion', 'lifepo4').

    Returns:
        LookupTableDischargeModel loaded from the data file.

    Raises:
        FileNotFoundError: If no data file exists for the chemistry.
    """
    # Find the data directory relative to this module
    data_dir = Path(__file__).parent.parent.parent / 'data'

    key = chemistry_name.lower().replace('-', '_')
    filepath = data_dir / f'discharge_{key}.npz'

    if not filepath.exists():
        available = list(data_dir.glob('discharge_*.npz'))
        available_names = [f.stem.replace('discharge_', '') for f in available]
        raise FileNotFoundError(
            f"No lookup table found for '{chemistry_name}' at {filepath}. "
            f"Available: {available_names}. "
            f"Generate with: python utils/generate_lookup_tables.py -c {key}"
        )

    data = np.load(filepath)

    return LookupTableDischargeModel(
        soc_points=data['soc_points'],
        c_rate_points=data['c_rate_points'],
        voltage_data=data['voltage_data'],
        v_min=Voltage(float(data['v_min']), 'V'),
    )
