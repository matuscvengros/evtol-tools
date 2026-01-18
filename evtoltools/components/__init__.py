"""eVTOL component modules for weight and power analysis."""

from evtoltools.components.base import BaseComponent, ComponentResult
from evtoltools.components.avionics import Avionics
from evtoltools.components.structure import Structure
from evtoltools.components.payload import Payload
from evtoltools.components.battery import (
    Battery,
    BatteryChemistry,
    get_chemistry,
    LITHIUM_ION,
    LITHIUM_POLYMER,
    LITHIUM_IRON_PHOSPHATE,
    LITHIUM_NMC,
)
from evtoltools.components.propulsion import (
    PropulsionSystem,
    Motor,
    Propeller,
)

__all__ = [
    # Base classes
    'BaseComponent',
    'ComponentResult',
    # Simple components
    'Avionics',
    'Structure',
    'Payload',
    # Battery
    'Battery',
    'BatteryChemistry',
    'get_chemistry',
    'LITHIUM_ION',
    'LITHIUM_POLYMER',
    'LITHIUM_IRON_PHOSPHATE',
    'LITHIUM_NMC',
    # Propulsion
    'PropulsionSystem',
    'Motor',
    'Propeller',
]
