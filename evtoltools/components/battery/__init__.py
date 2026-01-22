"""Battery component package for eVTOL aircraft."""

from evtoltools.components.battery.chemistry import (
    BatteryChemistry,
    get_chemistry,
    LITHIUM_ION,
    LITHIUM_POLYMER,
    LITHIUM_IRON_PHOSPHATE,
    LITHIUM_NMC,
    CHEMISTRY_REGISTRY,
)
from evtoltools.components.battery.battery import Battery
from evtoltools.components.battery.discharge import (
    DischargeModel,
    ChargeModel,
    AnalyticalDischargeModel,
    LookupTableDischargeModel,
    SimpleChargeModel,
    load_discharge_model,
)
from evtoltools.components.battery.thermal import (
    ThermalLimits,
    ThermalModel,
    SimpleThermalModel,
)
from evtoltools.components.battery.pybamm_utils import (
    PyBaMMDischargeModel,
    generate_discharge_table,
    load_or_generate_discharge_model,
    create_default_lookup_table,
    load_lookup_table_from_data,
)

__all__ = [
    # Battery and chemistry
    'Battery',
    'BatteryChemistry',
    'get_chemistry',
    'LITHIUM_ION',
    'LITHIUM_POLYMER',
    'LITHIUM_IRON_PHOSPHATE',
    'LITHIUM_NMC',
    'CHEMISTRY_REGISTRY',
    # Discharge and charge models
    'DischargeModel',
    'ChargeModel',
    'AnalyticalDischargeModel',
    'LookupTableDischargeModel',
    'SimpleChargeModel',
    'load_discharge_model',
    # Thermal models
    'ThermalLimits',
    'ThermalModel',
    'SimpleThermalModel',
    # PyBaMM utilities
    'PyBaMMDischargeModel',
    'generate_discharge_table',
    'load_or_generate_discharge_model',
    'create_default_lookup_table',
    'load_lookup_table_from_data',
]
