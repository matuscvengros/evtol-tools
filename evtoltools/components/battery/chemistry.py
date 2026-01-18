"""Battery chemistry configurations."""

from dataclasses import dataclass
from typing import Dict, Optional

from evtoltools.common import Voltage


@dataclass(frozen=True)
class BatteryChemistry:
    """Immutable configuration for a battery chemistry type.

    Attributes:
        name: Chemistry identifier (e.g., 'lithium_ion')
        nominal_cell_voltage: Nominal voltage per cell
        max_cell_voltage: Maximum safe charging voltage per cell
        min_cell_voltage: Minimum safe discharge voltage per cell
        description: Human-readable description
        pybamm_parameter_set: PyBaMM parameter set name for simulation
    """

    name: str
    nominal_cell_voltage: Voltage
    max_cell_voltage: Voltage
    min_cell_voltage: Voltage
    description: str = ""
    pybamm_parameter_set: Optional[str] = None

    def validate_voltage(self, voltage: Voltage) -> tuple[bool, str]:
        """Check if voltage is within safe operating range.

        Args:
            voltage: Cell voltage to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if voltage > self.max_cell_voltage:
            return False, f"Voltage {voltage} exceeds max {self.max_cell_voltage}"
        if voltage < self.min_cell_voltage:
            return False, f"Voltage {voltage} below min {self.min_cell_voltage}"
        return True, "Voltage within safe range"

    @property
    def voltage_range(self) -> Voltage:
        """Usable voltage range per cell (max - min)."""
        max_v = self.max_cell_voltage.in_units_of('V')
        min_v = self.min_cell_voltage.in_units_of('V')
        return Voltage(max_v - min_v, 'V')


# Predefined chemistry configurations
LITHIUM_ION = BatteryChemistry(
    name='lithium_ion',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(2.8, 'V'),
    description='Standard lithium-ion (Li-ion) chemistry',
    pybamm_parameter_set='Chen2020',
)

LITHIUM_POLYMER = BatteryChemistry(
    name='lithium_polymer',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(3.2, 'V'),  # Higher min than Li-ion
    description='Lithium polymer (LiPo) chemistry',
    pybamm_parameter_set='Chen2020',
)

LITHIUM_IRON_PHOSPHATE = BatteryChemistry(
    name='lithium_iron_phosphate',
    nominal_cell_voltage=Voltage(3.2, 'V'),
    max_cell_voltage=Voltage(3.65, 'V'),
    min_cell_voltage=Voltage(2.5, 'V'),
    description='Lithium iron phosphate (LiFePO4) chemistry',
    pybamm_parameter_set='Marquis2019',
)

# NMC (Nickel Manganese Cobalt) - common for eVTOL
LITHIUM_NMC = BatteryChemistry(
    name='lithium_nmc',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(3.0, 'V'),
    description='Lithium NMC (Nickel Manganese Cobalt) chemistry',
    pybamm_parameter_set='Chen2020',
)

# Registry of available chemistries
CHEMISTRY_REGISTRY: Dict[str, BatteryChemistry] = {
    'lithium_ion': LITHIUM_ION,
    'li_ion': LITHIUM_ION,
    'lion': LITHIUM_ION,
    'lithium_polymer': LITHIUM_POLYMER,
    'lipo': LITHIUM_POLYMER,
    'lithium_iron_phosphate': LITHIUM_IRON_PHOSPHATE,
    'lifepo4': LITHIUM_IRON_PHOSPHATE,
    'lfp': LITHIUM_IRON_PHOSPHATE,
    'lithium_nmc': LITHIUM_NMC,
    'nmc': LITHIUM_NMC,
}


def get_chemistry(name: str) -> BatteryChemistry:
    """Get chemistry configuration by name.

    Args:
        name: Chemistry name or alias (e.g., 'lithium_ion', 'lipo', 'nmc')

    Returns:
        BatteryChemistry configuration

    Raises:
        ValueError: If chemistry name not found
    """
    key = name.lower().replace('-', '_').replace(' ', '_')
    if key not in CHEMISTRY_REGISTRY:
        available = sorted(set(c.name for c in CHEMISTRY_REGISTRY.values()))
        raise ValueError(f"Unknown chemistry '{name}'. Available: {available}")
    return CHEMISTRY_REGISTRY[key]
