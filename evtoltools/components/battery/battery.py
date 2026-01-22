"""Battery component for eVTOL aircraft.

This module provides the Battery component with cell configuration and chemistry
support for eVTOL aircraft analysis. Batteries can be constructed directly with
cell counts or via sizing methods that calculate configuration from target
voltage or energy requirements.

Classes:
    Battery: Battery pack component with cell configuration and chemistry support.

Examples:
    Direct construction with cell counts::

        battery = Battery(
            cells_series=14,
            cells_parallel=4,
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion'
        )

    Sizing from target voltage::

        battery = Battery.from_target_voltage(
            target_voltage=Voltage(48, 'V'),
            cells_parallel=4,
            cell_capacity=Capacity(5000, 'mAh'),
            cell_mass=Mass(50, 'g'),
            chemistry='lithium_ion'
        )
        # Check sizing notes if needed
        print(battery.warnings)
        print(battery.info)
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from evtoltools.common import Capacity, Current, Energy, Mass, Power, Voltage
from evtoltools.components.base import BaseComponent
from evtoltools.components.battery.chemistry import (
    LITHIUM_ION,
    BatteryChemistry,
    get_chemistry,
)


@dataclass
class Battery(BaseComponent):
    """Battery pack component with cell configuration and chemistry support.

    Supports two configuration modes:
    1. Specify cells_series and cells_parallel directly
    2. Specify target voltage and let the system calculate cells_series

    Attributes:
        cells_series: Number of cells in series (determines voltage)
        cells_parallel: Number of cells in parallel (determines capacity)
        cell_capacity: Capacity of each cell (Ah or mAh)
        cell_mass: Mass of individual cell
        chemistry: Battery chemistry configuration
        c_rating_charge: Maximum charge rate as multiple of capacity
        c_rating_discharge: Maximum discharge rate as multiple of capacity
        pack_overhead_fraction: Additional mass fraction for packaging/BMS

    Examples:
        >>> # Method 1: Specify cell configuration directly
        >>> battery = Battery(
        ...     cells_series=14,
        ...     cells_parallel=4,
        ...     cell_capacity=Capacity(5000, 'mAh'),
        ...     cell_mass=Mass(50, 'g'),
        ...     chemistry='lithium_ion'
        ... )
        >>> print(battery.nominal_voltage)  # 51.8V (14 * 3.7V)
        >>> print(battery.total_capacity)   # 20Ah (4 * 5Ah)

        >>> # Method 2: Specify target voltage
        >>> battery = Battery.from_target_voltage(
        ...     target_voltage=Voltage(48, 'V'),
        ...     cells_parallel=4,
        ...     cell_capacity=Capacity(5000, 'mAh'),
        ...     cell_mass=Mass(50, 'g'),
        ...     chemistry='lithium_ion'
        ... )
        >>> print(battery.warnings)  # Shows voltage adjustment if rounding occurred
    """

    cells_series: int
    cells_parallel: int
    cell_capacity: Capacity
    cell_mass: Mass
    chemistry: BatteryChemistry = field(default_factory=lambda: LITHIUM_ION)
    c_rating_charge: float = 1.0
    c_rating_discharge: float = 2.0
    pack_overhead_fraction: float = 0.15  # 15% for BMS, wiring, enclosure
    warnings: List[str] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate inputs, convert chemistry string, and normalize units to SI."""
        # Normalize quantities to SI units
        object.__setattr__(self, 'cell_mass', self.cell_mass.to_default())
        object.__setattr__(self, 'cell_capacity', self.cell_capacity.to_default())

        if isinstance(self.chemistry, str):
            object.__setattr__(self, 'chemistry', get_chemistry(self.chemistry))

        if self.cells_series < 1:
            raise ValueError("cells_series must be at least 1")
        if self.cells_parallel < 1:
            raise ValueError("cells_parallel must be at least 1")
        if self.c_rating_charge <= 0:
            raise ValueError("c_rating_charge must be positive")
        if self.c_rating_discharge <= 0:
            raise ValueError("c_rating_discharge must be positive")
        if not 0 <= self.pack_overhead_fraction < 1:
            raise ValueError("pack_overhead_fraction must be between 0 and 1")

    @property
    def component_type(self) -> str:
        return 'battery'

    @property
    def mass(self) -> Mass:
        """Calculate total battery pack mass.

        Calculates from total cell mass plus pack overhead (BMS, wiring, enclosure).
        """
        total_cells = self.cells_series * self.cells_parallel
        cell_mass_total = self.cell_mass * total_cells
        overhead_mass = cell_mass_total * self.pack_overhead_fraction
        return cell_mass_total + overhead_mass

    @property
    def total_cells(self) -> int:
        """Total number of cells in the pack."""
        return self.cells_series * self.cells_parallel

    # Voltage properties
    @property
    def nominal_voltage(self) -> Voltage:
        """Pack nominal voltage (series cells * cell nominal voltage)."""
        return self.chemistry.nominal_cell_voltage * self.cells_series

    @property
    def max_voltage(self) -> Voltage:
        """Pack maximum voltage (fully charged)."""
        return self.chemistry.max_cell_voltage * self.cells_series

    @property
    def min_voltage(self) -> Voltage:
        """Pack minimum voltage (fully discharged)."""
        return self.chemistry.min_cell_voltage * self.cells_series

    # Capacity properties
    @property
    def total_capacity(self) -> Capacity:
        """Total pack capacity (parallel cells * cell capacity)."""
        return self.cell_capacity * self.cells_parallel

    # Energy properties
    @property
    def energy_capacity(self) -> Energy:
        """Total energy capacity at nominal voltage (Wh)."""
        energy_pint = self.nominal_voltage * self.total_capacity
        return Energy(energy_pint.to('Wh'))

    @property
    def energy_capacity_max(self) -> Energy:
        """Maximum energy capacity at full charge voltage (Wh)."""
        energy_pint = self.max_voltage * self.total_capacity
        return Energy(energy_pint.to('Wh'))

    @property
    def usable_energy_ratio(self) -> float:
        """Ratio of usable voltage range to full range.

        Accounts for the fact that batteries cannot be fully discharged.
        """
        max_v = self.chemistry.max_cell_voltage
        min_v = self.chemistry.min_cell_voltage
        nom_v = self.chemistry.nominal_cell_voltage

        # Approximate usable range assuming linear discharge
        # Dividing same-type quantities gives dimensionless ratio
        ratio_pint = (nom_v - min_v) / (max_v - min_v)
        return float(ratio_pint.magnitude)

    # Current limits
    @property
    def max_charge_current(self) -> Current:
        """Maximum charging current based on C-rating.

        C-rating is implicitly 1/hr, so Ah * C-rating = A.
        """
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Current(capacity_ah * self.c_rating_charge, 'A')

    @property
    def max_discharge_current(self) -> Current:
        """Maximum discharge current based on C-rating.

        C-rating is implicitly 1/hr, so Ah * C-rating = A.
        """
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Current(capacity_ah * self.c_rating_discharge, 'A')

    # Power limits
    @property
    def max_charge_power(self) -> Power:
        """Maximum charging power."""
        power_pint = self.nominal_voltage * self.max_charge_current
        return Power(power_pint.to('W'))

    @property
    def max_discharge_power(self) -> Power:
        """Maximum continuous discharge power."""
        power_pint = self.nominal_voltage * self.max_discharge_current
        return Power(power_pint.to('W'))

    # Sizing methods
    @classmethod
    def from_target_voltage(
        cls,
        target_voltage: Voltage,
        cells_parallel: int,
        cell_capacity: Capacity,
        cell_mass: Mass,
        chemistry: Union[str, BatteryChemistry] = 'lithium_ion',
        **kwargs
    ) -> 'Battery':
        """Create battery by specifying target voltage.

        Calculates the number of series cells needed to achieve the target
        voltage. Rounds to the nearest integer number of cells. Check
        warnings for any adjustments made.

        Args:
            target_voltage: Desired pack voltage.
            cells_parallel: Number of parallel cell groups.
            cell_capacity: Capacity per cell.
            cell_mass: Mass of individual cell.
            chemistry: Chemistry type (string or BatteryChemistry).
            **kwargs: Additional arguments passed to Battery constructor.

        Returns:
            Battery instance. Check warnings and info for details.
        """
        warnings = []

        # Get chemistry configuration
        if isinstance(chemistry, str):
            chem = get_chemistry(chemistry)
        else:
            chem = chemistry

        # Calculate required cells
        target_v = target_voltage.in_units_of('V')
        cell_v = chem.nominal_cell_voltage.in_units_of('V')
        cells_exact = target_v / cell_v

        cells_series = round(cells_exact)

        # Ensure at least 1 cell
        cells_series = max(1, cells_series)

        # Calculate actual voltage
        actual_voltage = cell_v * cells_series

        # Notify if rounding occurred
        if abs(cells_exact - cells_series) > 0.001:
            warnings.append(
                f"Rounded {cells_exact:.2f} cells to {cells_series}. "
                f"Actual voltage: {actual_voltage:.1f}V (target was {target_v:.1f}V)"
            )

        return cls(
            cells_series=cells_series,
            cells_parallel=cells_parallel,
            cell_capacity=cell_capacity,
            cell_mass=cell_mass,
            chemistry=chem,
            warnings=warnings,
            info={
                'target_voltage_v': target_v,
                'actual_voltage_v': actual_voltage,
                'cells_exact': cells_exact,
            },
            **kwargs
        )

    @classmethod
    def from_target_energy(
        cls,
        target_energy: Energy,
        target_voltage: Voltage,
        cell_capacity: Capacity,
        cell_mass: Mass,
        chemistry: Union[str, BatteryChemistry] = 'lithium_ion',
        **kwargs
    ) -> 'Battery':
        """Create battery sized for target energy.

        Args:
            target_energy: Target energy capacity.
            target_voltage: Target pack voltage.
            cell_capacity: Capacity per cell.
            cell_mass: Mass of individual cell.
            chemistry: Chemistry type.
            **kwargs: Additional arguments.

        Returns:
            Battery instance. Check warnings and info for details.
        """
        warnings = []

        # First determine series cells for voltage
        if isinstance(chemistry, str):
            chem = get_chemistry(chemistry)
        else:
            chem = chemistry

        target_v = target_voltage.in_units_of('V')
        cell_v = chem.nominal_cell_voltage.in_units_of('V')
        cells_series = math.ceil(target_v / cell_v)
        cells_series = max(1, cells_series)
        actual_voltage = cell_v * cells_series

        if abs(target_v - actual_voltage) > 0.1:
            warnings.append(
                f"Adjusted voltage from {target_v:.1f}V to {actual_voltage:.1f}V "
                f"({cells_series} cells in series)"
            )

        # Calculate required capacity
        target_wh = target_energy.in_units_of('Wh')
        target_ah = target_wh / actual_voltage
        cell_ah = cell_capacity.in_units_of('Ah')
        cells_parallel = math.ceil(target_ah / cell_ah)
        cells_parallel = max(1, cells_parallel)
        actual_ah = cell_ah * cells_parallel
        actual_wh = actual_voltage * actual_ah

        warnings.append(
            f"Sized for {actual_ah:.1f}Ah capacity ({cells_parallel}P configuration), "
            f"providing {actual_wh:.1f}Wh"
        )

        margin = (actual_wh - target_wh) / target_wh * 100

        return cls(
            cells_series=cells_series,
            cells_parallel=cells_parallel,
            cell_capacity=cell_capacity,
            cell_mass=cell_mass,
            chemistry=chem,
            warnings=warnings,
            info={
                'target_energy_wh': target_wh,
                'actual_energy_wh': actual_wh,
                'energy_margin_percent': margin,
                'configuration': f"{cells_series}S{cells_parallel}P",
            },
            **kwargs
        )

    def __repr__(self) -> str:
        config = f"{self.cells_series}S{self.cells_parallel}P"
        return (
            f"Battery({config}, {self.nominal_voltage}, "
            f"{self.energy_capacity.to('kWh')})"
        )
