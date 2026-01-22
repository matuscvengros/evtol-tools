#!/usr/bin/env python3
"""Generate battery discharge lookup tables.

This script generates voltage lookup tables for battery discharge modeling.
Tables can be generated using PyBaMM simulation (if available) or using
analytical approximations.

Usage:
    python utils/generate_lookup_tables.py [OPTIONS]

Examples:
    # Generate with default settings (12 SoC points, 7 C-rates)
    python utils/generate_lookup_tables.py

    # Generate high-resolution table
    python utils/generate_lookup_tables.py --soc-points 50 --c-rate-points 10

    # Generate for specific chemistry
    python utils/generate_lookup_tables.py --chemistry lifepo4

    # Use PyBaMM DFN model (more accurate, slower)
    python utils/generate_lookup_tables.py --model-type DFN
"""

import argparse
import sys
from pathlib import Path

import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from evtoltools.common import Resistance, Voltage


def get_chemistry_params(chemistry: str) -> dict:
    """Get voltage and resistance parameters for a chemistry."""
    params = {
        'lithium_ion': {
            'v_nom': 3.7, 'v_max': 4.2, 'v_min': 2.8,
            'r_mohm': 30, 'capacity_ah': 5.0,
            'pybamm_set': 'Chen2020'
        },
        'lipo': {
            'v_nom': 3.7, 'v_max': 4.2, 'v_min': 3.2,
            'r_mohm': 25, 'capacity_ah': 5.0,
            'pybamm_set': 'Chen2020'
        },
        'lifepo4': {
            'v_nom': 3.2, 'v_max': 3.65, 'v_min': 2.5,
            'r_mohm': 40, 'capacity_ah': 5.0,
            'pybamm_set': 'Marquis2019'
        },
        'nmc': {
            'v_nom': 3.7, 'v_max': 4.2, 'v_min': 3.0,
            'r_mohm': 25, 'capacity_ah': 5.0,
            'pybamm_set': 'Chen2020'
        },
    }

    key = chemistry.lower().replace('-', '_')
    if key not in params:
        raise ValueError(f"Unknown chemistry: {chemistry}. Available: {list(params.keys())}")
    return params[key]


def generate_analytical_table(
    soc_points: np.ndarray,
    c_rate_points: np.ndarray,
    v_max: float,
    v_min: float,
    r_mohm: float,
    capacity_ah: float
) -> np.ndarray:
    """Generate voltage table using analytical V = V_oc - I*R model."""
    r_ohm = r_mohm / 1000
    voltage_data = np.zeros((len(soc_points), len(c_rate_points)))

    for i, soc in enumerate(soc_points):
        # Open-circuit voltage (linear approximation)
        v_oc = v_min + soc * (v_max - v_min)

        for j, c_rate in enumerate(c_rate_points):
            current = c_rate * capacity_ah
            v_drop = current * r_ohm
            voltage_data[i, j] = max(v_min, v_oc - v_drop)

    return voltage_data


def generate_pybamm_table(
    soc_points: np.ndarray,
    c_rate_points: np.ndarray,
    parameter_set: str,
    model_type: str = 'SPM'
) -> np.ndarray:
    """Generate voltage table using PyBaMM simulation."""
    import pybamm

    # Initialize model
    if model_type.upper() == 'DFN':
        model = pybamm.lithium_ion.DFN()
    else:
        model = pybamm.lithium_ion.SPM()

    param = pybamm.ParameterValues(parameter_set)

    # Build voltage table
    voltage_data = np.zeros((len(soc_points), len(c_rate_points)))
    total = len(soc_points) * len(c_rate_points)
    count = 0

    for i, soc in enumerate(soc_points):
        for j, c_rate in enumerate(c_rate_points):
            count += 1
            try:
                p = param.copy()
                p['Current function [A]'] = c_rate * p['Nominal cell capacity [A.h]']

                sim = pybamm.Simulation(model, parameter_values=p)
                sim.solve([0, 1], initial_soc=float(soc))
                voltage_data[i, j] = sim.solution['Terminal voltage [V]'](0)

                print(f"\r  Progress: {count}/{total} ({100*count/total:.0f}%)", end='', flush=True)
            except Exception as e:
                # Use interpolation from neighbors or default
                if i > 0:
                    voltage_data[i, j] = voltage_data[i - 1, j]
                else:
                    voltage_data[i, j] = 3.7

    print()  # Newline after progress
    return voltage_data


def main():
    parser = argparse.ArgumentParser(
        description='Generate battery discharge lookup tables.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--chemistry', '-c',
        default='lithium_ion',
        choices=['lithium_ion', 'lipo', 'lifepo4', 'nmc'],
        help='Battery chemistry (default: lithium_ion)'
    )

    parser.add_argument(
        '--soc-points', '-s',
        type=int,
        default=12,
        help='Number of SoC points (default: 12)'
    )

    parser.add_argument(
        '--c-rate-points', '-r',
        type=int,
        default=7,
        help='Number of C-rate points (default: 7)'
    )

    parser.add_argument(
        '--c-rate-max',
        type=float,
        default=10.0,
        help='Maximum C-rate (default: 10.0)'
    )

    parser.add_argument(
        '--use-pybamm',
        action='store_true',
        help='Use PyBaMM simulation instead of analytical model'
    )

    parser.add_argument(
        '--model-type',
        default='SPM',
        choices=['SPM', 'DFN'],
        help='PyBaMM model type (default: SPM)'
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help='Output directory (default: evtoltools/data)'
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output_dir is None:
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / 'evtoltools' / 'data'
    else:
        output_dir = args.output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get chemistry parameters
    chem_params = get_chemistry_params(args.chemistry)

    # Create grids
    soc_points = np.linspace(0.05, 0.95, args.soc_points)
    c_rate_points = np.linspace(0.1, args.c_rate_max, args.c_rate_points)

    print(f"Generating lookup table for {args.chemistry}")
    print(f"  SoC points: {args.soc_points} ({soc_points[0]:.2f} to {soc_points[-1]:.2f})")
    print(f"  C-rate points: {args.c_rate_points} ({c_rate_points[0]:.1f} to {c_rate_points[-1]:.1f})")

    # Generate table
    if args.use_pybamm:
        try:
            import pybamm
            print(f"  Using PyBaMM {pybamm.__version__} ({args.model_type} model)")
            voltage_data = generate_pybamm_table(
                soc_points, c_rate_points,
                chem_params['pybamm_set'],
                args.model_type
            )
            source = f"pybamm_{args.model_type}"
        except ImportError:
            print("  PyBaMM not available, falling back to analytical model")
            args.use_pybamm = False

    if not args.use_pybamm:
        print("  Using analytical model")
        voltage_data = generate_analytical_table(
            soc_points, c_rate_points,
            chem_params['v_max'], chem_params['v_min'],
            chem_params['r_mohm'], chem_params['capacity_ah']
        )
        source = "analytical"

    # Save table
    filename = f"discharge_{args.chemistry}.npz"
    filepath = output_dir / filename

    np.savez(
        filepath,
        soc_points=soc_points,
        c_rate_points=c_rate_points,
        voltage_data=voltage_data,
        v_min=chem_params['v_min'],
        v_max=chem_params['v_max'],
        v_nom=chem_params['v_nom'],
        r_mohm=chem_params['r_mohm'],
        capacity_ah=chem_params['capacity_ah'],
        source=source,
        chemistry=args.chemistry,
    )

    print(f"\nSaved: {filepath}")
    print(f"  Shape: {voltage_data.shape} (SoC x C-rate)")
    print(f"  Voltage range: {voltage_data.min():.3f}V to {voltage_data.max():.3f}V")

    return 0


if __name__ == '__main__':
    sys.exit(main())
