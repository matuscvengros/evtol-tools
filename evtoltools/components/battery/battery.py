"""Battery component for eVTOL aircraft."""

from dataclasses import dataclass, field
from typing import Optional, Union
import math

from evtoltools.common import Mass, Voltage, Energy, Capacity, Current, Power
from evtoltools.components.base import BaseComponent, ComponentResult
from evtoltools.components.battery.chemistry import (
    BatteryChemistry, get_chemistry, LITHIUM_ION
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
        chemistry: Battery chemistry configuration
        c_rating_charge: Maximum charge rate as multiple of capacity
        c_rating_discharge: Maximum discharge rate as multiple of capacity
        cell_mass: Mass of individual cell (optional, for mass calculation)
        pack_overhead_fraction: Additional mass fraction for packaging/BMS

    Examples:
        >>> # Method 1: Specify cell configuration directly
        >>> battery = Battery(
        ...     cells_series=14,
        ...     cells_parallel=4,
        ...     cell_capacity=Capacity(5000, 'mAh'),
        ...     chemistry='lithium_ion'
        ... )
        >>> print(battery.nominal_voltage)  # 51.8V (14 * 3.7V)
        >>> print(battery.total_capacity)   # 20Ah (4 * 5Ah)

        >>> # Method 2: Specify target voltage
        >>> result = Battery.from_target_voltage(
        ...     target_voltage=Voltage(48, 'V'),
        ...     cells_parallel=4,
        ...     cell_capacity=Capacity(5000, 'mAh'),
        ...     chemistry='lithium_ion'
        ... )
        >>> battery = result.value
        >>> print(result.warnings)  # Shows voltage adjustment if rounding occurred
    """

    cells_series: int
    cells_parallel: int
    cell_capacity: Capacity
    chemistry: BatteryChemistry = field(default_factory=lambda: LITHIUM_ION)
    c_rating_charge: float = 1.0
    c_rating_discharge: float = 2.0
    cell_mass: Optional[Mass] = None
    pack_overhead_fraction: float = 0.15  # 15% for BMS, wiring, enclosure

    def __post_init__(self):
        """Validate inputs and convert chemistry string to object."""
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

        If cell_mass is provided, calculates from cells plus overhead.
        Otherwise returns Mass(0, 'kg') as placeholder.
        """
        if self.cell_mass is None:
            return Mass(0, 'kg')

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
        cell_v = self.chemistry.nominal_cell_voltage.in_units_of('V')
        return Voltage(cell_v * self.cells_series, 'V')

    @property
    def max_voltage(self) -> Voltage:
        """Pack maximum voltage (fully charged)."""
        cell_v = self.chemistry.max_cell_voltage.in_units_of('V')
        return Voltage(cell_v * self.cells_series, 'V')

    @property
    def min_voltage(self) -> Voltage:
        """Pack minimum voltage (fully discharged)."""
        cell_v = self.chemistry.min_cell_voltage.in_units_of('V')
        return Voltage(cell_v * self.cells_series, 'V')

    # Capacity properties
    @property
    def total_capacity(self) -> Capacity:
        """Total pack capacity (parallel cells * cell capacity)."""
        cell_ah = self.cell_capacity.in_units_of('Ah')
        return Capacity(cell_ah * self.cells_parallel, 'Ah')

    # Energy properties
    @property
    def energy_capacity(self) -> Energy:
        """Total energy capacity at nominal voltage (Wh)."""
        voltage_v = self.nominal_voltage.in_units_of('V')
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Energy(voltage_v * capacity_ah, 'Wh')

    @property
    def energy_capacity_max(self) -> Energy:
        """Maximum energy capacity at full charge voltage (Wh)."""
        voltage_v = self.max_voltage.in_units_of('V')
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Energy(voltage_v * capacity_ah, 'Wh')

    @property
    def usable_energy_ratio(self) -> float:
        """Ratio of usable voltage range to full range.

        Accounts for the fact that batteries cannot be fully discharged.
        """
        max_v = self.chemistry.max_cell_voltage.in_units_of('V')
        min_v = self.chemistry.min_cell_voltage.in_units_of('V')
        nom_v = self.chemistry.nominal_cell_voltage.in_units_of('V')

        # Approximate usable range assuming linear discharge
        return (nom_v - min_v) / (max_v - min_v)

    # Current limits
    @property
    def max_charge_current(self) -> Current:
        """Maximum charging current based on C-rating."""
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Current(capacity_ah * self.c_rating_charge, 'A')

    @property
    def max_discharge_current(self) -> Current:
        """Maximum discharge current based on C-rating."""
        capacity_ah = self.total_capacity.in_units_of('Ah')
        return Current(capacity_ah * self.c_rating_discharge, 'A')

    # Power limits
    @property
    def max_charge_power(self) -> Power:
        """Maximum charging power."""
        voltage_v = self.nominal_voltage.in_units_of('V')
        current_a = self.max_charge_current.in_units_of('A')
        return Power(voltage_v * current_a, 'W')

    @property
    def max_discharge_power(self) -> Power:
        """Maximum continuous discharge power."""
        voltage_v = self.nominal_voltage.in_units_of('V')
        current_a = self.max_discharge_current.in_units_of('A')
        return Power(voltage_v * current_a, 'W')

    # Factory methods
    @classmethod
    def from_target_voltage(
        cls,
        target_voltage: Voltage,
        cells_parallel: int,
        cell_capacity: Capacity,
        chemistry: Union[str, BatteryChemistry] = 'lithium_ion',
        round_up: bool = True,
        **kwargs
    ) -> ComponentResult:
        """Create battery by specifying target voltage.

        Calculates the number of series cells needed to achieve the target
        voltage. If the result is not an integer, rounds up (default) and
        notifies the user of the actual voltage.

        Args:
            target_voltage: Desired pack voltage
            cells_parallel: Number of parallel cell groups
            cell_capacity: Capacity per cell
            chemistry: Chemistry type (string or BatteryChemistry)
            round_up: If True, round cells up; if False, round to nearest
            **kwargs: Additional arguments passed to Battery constructor

        Returns:
            ComponentResult containing Battery instance and any warnings
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

        if round_up:
            cells_series = math.ceil(cells_exact)
        else:
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

        battery = cls(
            cells_series=cells_series,
            cells_parallel=cells_parallel,
            cell_capacity=cell_capacity,
            chemistry=chem,
            **kwargs
        )

        return ComponentResult(
            value=battery,
            warnings=warnings,
            metadata={
                'target_voltage_v': target_v,
                'actual_voltage_v': actual_voltage,
                'cells_exact': cells_exact,
            }
        )

    @classmethod
    def from_energy_requirement(
        cls,
        required_energy: Energy,
        target_voltage: Voltage,
        chemistry: Union[str, BatteryChemistry] = 'lithium_ion',
        cell_capacity: Optional[Capacity] = None,
        **kwargs
    ) -> ComponentResult:
        """Create battery sized for energy requirement.

        Args:
            required_energy: Required energy capacity
            target_voltage: Target pack voltage
            chemistry: Chemistry type
            cell_capacity: Cell capacity (defaults to 5Ah if not specified)
            **kwargs: Additional arguments

        Returns:
            ComponentResult with Battery and sizing information
        """
        warnings = []

        if cell_capacity is None:
            cell_capacity = Capacity(5, 'Ah')
            warnings.append("Using default cell capacity of 5Ah")

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
        required_wh = required_energy.in_units_of('Wh')
        required_ah = required_wh / actual_voltage
        cell_ah = cell_capacity.in_units_of('Ah')
        cells_parallel = math.ceil(required_ah / cell_ah)
        cells_parallel = max(1, cells_parallel)
        actual_ah = cell_ah * cells_parallel
        actual_wh = actual_voltage * actual_ah

        warnings.append(
            f"Sized for {actual_ah:.1f}Ah capacity ({cells_parallel}P configuration), "
            f"providing {actual_wh:.1f}Wh"
        )

        margin = (actual_wh - required_wh) / required_wh * 100

        battery = cls(
            cells_series=cells_series,
            cells_parallel=cells_parallel,
            cell_capacity=cell_capacity,
            chemistry=chem,
            **kwargs
        )

        return ComponentResult(
            value=battery,
            warnings=warnings,
            metadata={
                'required_energy_wh': required_wh,
                'actual_energy_wh': actual_wh,
                'energy_margin_percent': margin,
                'configuration': f"{cells_series}S{cells_parallel}P",
            }
        )

    def __repr__(self) -> str:
        config = f"{self.cells_series}S{self.cells_parallel}P"
        return (
            f"Battery({config}, {self.nominal_voltage}, "
            f"{self.energy_capacity.to('kWh')})"
        )
