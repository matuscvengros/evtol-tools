"""Battery chemistry configurations.

This module provides immutable battery chemistry configurations for different
lithium-based battery types used in eVTOL aircraft. Each chemistry defines
voltage characteristics and validation methods.

Classes:
    BatteryChemistry: Immutable configuration for a battery chemistry type.

Functions:
    get_chemistry: Get chemistry configuration by name or alias.

Constants:
    LITHIUM_ION: Standard lithium-ion chemistry configuration.
    LITHIUM_POLYMER: Lithium polymer chemistry configuration.
    LITHIUM_IRON_PHOSPHATE: LiFePO4 chemistry configuration.
    LITHIUM_NMC: Nickel Manganese Cobalt chemistry configuration.
    CHEMISTRY_REGISTRY: Registry mapping chemistry names to configurations.

Examples:
    Get chemistry by name::

        chem = get_chemistry('lithium_ion')
        print(chem.nominal_cell_voltage)  # 3.7 V

    Validate cell voltage::

        is_valid, msg = LITHIUM_ION.validate_voltage(Voltage(3.8, 'V'))
        if is_valid:
            print("Voltage is safe")
"""

from dataclasses import dataclass
from typing import Dict, Optional

from evtoltools.common import Resistance, Temperature, Voltage


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
        internal_resistance: Typical internal resistance per cell
        max_discharge_temperature: Maximum safe discharge temperature
        min_temperature: Minimum safe operating temperature
    """

    name: str
    nominal_cell_voltage: Voltage
    max_cell_voltage: Voltage
    min_cell_voltage: Voltage
    description: str = ""
    pybamm_parameter_set: Optional[str] = None
    internal_resistance: Optional[Resistance] = None
    max_discharge_temperature: Optional[Temperature] = None
    min_temperature: Optional[Temperature] = None

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
        return self.max_cell_voltage - self.min_cell_voltage


# Predefined chemistry configurations
LITHIUM_ION = BatteryChemistry(
    name='lithium_ion',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(2.8, 'V'),
    description='Standard lithium-ion (Li-ion) chemistry',
    pybamm_parameter_set='Chen2020',
    internal_resistance=Resistance(30, 'mohm'),
    max_discharge_temperature=Temperature(60, 'degC'),
    min_temperature=Temperature(-20, 'degC'),
)

LITHIUM_POLYMER = BatteryChemistry(
    name='lithium_polymer',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(3.2, 'V'),  # Higher min than Li-ion
    description='Lithium polymer (LiPo) chemistry',
    pybamm_parameter_set='Chen2020',
    internal_resistance=Resistance(25, 'mohm'),
    max_discharge_temperature=Temperature(60, 'degC'),
    min_temperature=Temperature(-20, 'degC'),
)

LITHIUM_IRON_PHOSPHATE = BatteryChemistry(
    name='lithium_iron_phosphate',
    nominal_cell_voltage=Voltage(3.2, 'V'),
    max_cell_voltage=Voltage(3.65, 'V'),
    min_cell_voltage=Voltage(2.5, 'V'),
    description='Lithium iron phosphate (LiFePO4) chemistry',
    pybamm_parameter_set='Marquis2019',
    internal_resistance=Resistance(40, 'mohm'),
    max_discharge_temperature=Temperature(60, 'degC'),
    min_temperature=Temperature(-20, 'degC'),
)

# NMC (Nickel Manganese Cobalt) - common for eVTOL
LITHIUM_NMC = BatteryChemistry(
    name='lithium_nmc',
    nominal_cell_voltage=Voltage(3.7, 'V'),
    max_cell_voltage=Voltage(4.2, 'V'),
    min_cell_voltage=Voltage(3.0, 'V'),
    description='Lithium NMC (Nickel Manganese Cobalt) chemistry',
    pybamm_parameter_set='Chen2020',
    internal_resistance=Resistance(25, 'mohm'),
    max_discharge_temperature=Temperature(60, 'degC'),
    min_temperature=Temperature(-20, 'degC'),
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
