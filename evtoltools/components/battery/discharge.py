"""Battery discharge and charge models.

This module provides abstract and concrete implementations of battery discharge
and charge models for simulating battery voltage behavior under varying
conditions of State of Charge (SoC) and discharge/charge current.

Classes:
    DischargeModel: Abstract base class for discharge models.
    ChargeModel: Abstract base class for charge models.
    AnalyticalDischargeModel: Simple V = V_oc(SoC) - I*R model.
    LookupTableDischargeModel: 2D interpolation over SoC x C-rate tables.
    SimpleChargeModel: CC-CV charge model with efficiency losses.

Functions:
    load_discharge_model: Convenience function to load discharge model by name.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from evtoltools.common import Resistance, Temperature, Voltage


class DischargeModel(ABC):
    """Abstract base class for battery discharge voltage models.

    Subclasses implement get_voltage() to return cell voltage as a function
    of state of charge and discharge rate (C-rate).
    """

    @abstractmethod
    def get_voltage(
        self,
        soc: Union[float, np.ndarray],
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> Voltage:
        """Get cell voltage at given operating conditions.

        Args:
            soc: State of charge (0.0 to 1.0), scalar or array.
            c_rate: Discharge rate as multiple of capacity (e.g., 1.0 = 1C).
            temperature: Optional cell temperature (for temperature-dependent models).

        Returns:
            Cell voltage at the specified conditions.
        """
        pass

    def get_resistance(
        self,
        soc: float,
        temperature: Optional[Temperature] = None
    ) -> Optional[Resistance]:
        """Get internal resistance at given conditions.

        Default implementation returns None. Override in subclasses that
        support resistance modeling.

        Args:
            soc: State of charge (0.0 to 1.0).
            temperature: Optional cell temperature.

        Returns:
            Internal resistance or None if not supported.
        """
        return None


class ChargeModel(ABC):
    """Abstract base class for battery charge models.

    Subclasses implement charge behavior including CC-CV charging,
    efficiency losses, and thermal constraints.
    """

    @abstractmethod
    def get_charge_current(
        self,
        soc: float,
        max_c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> float:
        """Get charge current (as C-rate) at given SoC.

        Args:
            soc: Current state of charge (0.0 to 1.0).
            max_c_rate: Maximum allowed charge C-rate.
            temperature: Optional cell temperature.

        Returns:
            Charge C-rate to apply at this SoC.
        """
        pass

    @abstractmethod
    def get_charge_efficiency(
        self,
        soc: float,
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> float:
        """Get charging efficiency at given conditions.

        Args:
            soc: State of charge (0.0 to 1.0).
            c_rate: Charge rate as C multiple.
            temperature: Optional cell temperature.

        Returns:
            Charging efficiency (0.0 to 1.0).
        """
        pass


@dataclass
class AnalyticalDischargeModel(DischargeModel):
    """Simple analytical discharge model using V = V_oc(SoC) - I*R.

    Uses a linear open-circuit voltage model and constant internal resistance
    to calculate cell voltage under load. Fast computation but less accurate
    for complex discharge behaviors.

    Attributes:
        v_max: Maximum cell voltage (fully charged, open circuit).
        v_min: Minimum cell voltage (fully discharged, open circuit).
        v_nominal: Nominal cell voltage.
        internal_resistance: Cell internal resistance.
        capacity_ah: Cell capacity in Ah (for current calculation from C-rate).
    """

    v_max: Voltage
    v_min: Voltage
    v_nominal: Voltage
    internal_resistance: Resistance
    capacity_ah: float

    def __post_init__(self):
        """Normalize quantities to default units."""
        object.__setattr__(self, 'v_max', self.v_max.to_default())
        object.__setattr__(self, 'v_min', self.v_min.to_default())
        object.__setattr__(self, 'v_nominal', self.v_nominal.to_default())
        object.__setattr__(self, 'internal_resistance', self.internal_resistance.to_default())

    def _open_circuit_voltage(self, soc: Union[float, np.ndarray]) -> Voltage:
        """Calculate open-circuit voltage from SoC using linear interpolation.

        Models OCV as linear between v_min (SoC=0) and v_max (SoC=1).
        More sophisticated models could use polynomial or lookup-based OCV.
        """
        # Direct arithmetic on Voltage objects (Policy 4)
        return self.v_min + (self.v_max - self.v_min) * soc

    def get_voltage(
        self,
        soc: Union[float, np.ndarray],
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> Voltage:
        """Calculate cell voltage: V = V_oc(SoC) - I*R.

        Args:
            soc: State of charge (0.0 to 1.0).
            c_rate: Discharge rate (positive for discharge).
            temperature: Ignored in this simple model.

        Returns:
            Cell voltage under load.
        """
        v_oc = self._open_circuit_voltage(soc)
        current = c_rate * self.capacity_ah  # A

        # IR voltage drop: V = I * R (use .magnitude since units are normalized)
        v_drop = Voltage(current * self.internal_resistance.magnitude, 'V')
        voltage = v_oc - v_drop

        # Clamp to minimum voltage
        if isinstance(soc, np.ndarray):
            # Array case: use magnitude for numpy element-wise clamping
            clamped = np.maximum(voltage.magnitude, self.v_min.magnitude)
            return Voltage(clamped, 'V')
        else:
            # Scalar case: direct comparison
            if voltage < self.v_min:
                return self.v_min
            return voltage

    def get_resistance(
        self,
        soc: float,
        temperature: Optional[Temperature] = None
    ) -> Resistance:
        """Return constant internal resistance."""
        return self.internal_resistance


@dataclass
class LookupTableDischargeModel(DischargeModel):
    """Discharge model using 2D interpolation over pre-computed tables.

    Uses scipy RegularGridInterpolator for fast lookup of voltage as a
    function of SoC and C-rate. Tables can be generated from PyBaMM
    simulations or measured data.

    Attributes:
        soc_points: 1D array of SoC values (e.g., [0.0, 0.05, ..., 1.0]).
        c_rate_points: 1D array of C-rate values (e.g., [0.1, 0.5, 1.0, 2.0]).
        voltage_data: 2D array of voltages, shape (len(soc_points), len(c_rate_points)).
        resistance_data: Optional 2D array of resistances, same shape.
        v_min: Minimum voltage clamp.
    """

    soc_points: np.ndarray
    c_rate_points: np.ndarray
    voltage_data: np.ndarray
    resistance_data: Optional[np.ndarray] = None
    v_min: Optional[Voltage] = None
    _interpolator: RegularGridInterpolator = field(init=False, repr=False)
    _r_interpolator: Optional[RegularGridInterpolator] = field(
        init=False, repr=False, default=None
    )

    def __post_init__(self):
        """Initialize interpolators and normalize quantities."""
        # Normalize v_min to default units if present
        if self.v_min is not None:
            object.__setattr__(self, 'v_min', self.v_min.to_default())

        self._interpolator = RegularGridInterpolator(
            (self.soc_points, self.c_rate_points),
            self.voltage_data,
            method='linear',
            bounds_error=False,
            fill_value=None  # Extrapolate
        )
        if self.resistance_data is not None:
            self._r_interpolator = RegularGridInterpolator(
                (self.soc_points, self.c_rate_points),
                self.resistance_data,
                method='linear',
                bounds_error=False,
                fill_value=None
            )

    def get_voltage(
        self,
        soc: Union[float, np.ndarray],
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> Voltage:
        """Interpolate voltage from lookup table.

        Args:
            soc: State of charge (0.0 to 1.0).
            c_rate: Discharge rate.
            temperature: Ignored (temperature-dependent tables not yet supported).

        Returns:
            Interpolated cell voltage.
        """
        # Clamp inputs to table range
        soc_clamped = np.clip(soc, self.soc_points[0], self.soc_points[-1])
        c_rate_clamped = np.clip(c_rate, self.c_rate_points[0], self.c_rate_points[-1])

        if isinstance(soc_clamped, np.ndarray):
            points = np.column_stack([
                soc_clamped,
                np.full_like(soc_clamped, c_rate_clamped)
            ])
        else:
            points = np.array([[soc_clamped, c_rate_clamped]])

        voltage = self._interpolator(points)

        if self.v_min is not None:
            # Use .magnitude since v_min is normalized in __post_init__
            voltage = np.maximum(voltage, self.v_min.magnitude)

        if isinstance(soc, np.ndarray):
            return Voltage(voltage, 'V')
        return Voltage(float(voltage[0]), 'V')

    def get_resistance(
        self,
        soc: float,
        temperature: Optional[Temperature] = None
    ) -> Optional[Resistance]:
        """Interpolate resistance from lookup table if available."""
        if self._r_interpolator is None:
            return None

        soc_clamped = np.clip(soc, self.soc_points[0], self.soc_points[-1])
        # Use middle C-rate for resistance lookup
        c_rate_mid = self.c_rate_points[len(self.c_rate_points) // 2]
        points = np.array([[soc_clamped, c_rate_mid]])
        r_value = self._r_interpolator(points)[0]
        return Resistance(r_value, 'ohm')


@dataclass
class SimpleChargeModel(ChargeModel):
    """Simple CC-CV (Constant Current - Constant Voltage) charge model.

    Models charging behavior with:
    - Constant current (CC) phase up to a transition SoC
    - Constant voltage (CV) phase with tapering current
    - Efficiency losses based on current and SoC

    Attributes:
        cc_cv_transition_soc: SoC at which CV phase begins (default 0.8).
        cv_taper_factor: Rate at which current tapers in CV phase (default 3.0).
        base_efficiency: Baseline charging efficiency (default 0.95).
        efficiency_c_rate_factor: Efficiency loss per C-rate (default 0.02).
    """

    cc_cv_transition_soc: float = 0.8
    cv_taper_factor: float = 3.0
    base_efficiency: float = 0.95
    efficiency_c_rate_factor: float = 0.02

    def get_charge_current(
        self,
        soc: float,
        max_c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> float:
        """Get charge C-rate following CC-CV profile.

        In CC phase (SoC < transition), returns max_c_rate.
        In CV phase (SoC >= transition), current tapers exponentially.

        Args:
            soc: Current state of charge (0.0 to 1.0).
            max_c_rate: Maximum allowed charge C-rate.
            temperature: Ignored in this simple model.

        Returns:
            Charge C-rate to apply.
        """
        if soc < self.cc_cv_transition_soc:
            # CC phase: constant current
            return max_c_rate
        else:
            # CV phase: exponential taper
            soc_into_cv = soc - self.cc_cv_transition_soc
            remaining = 1.0 - self.cc_cv_transition_soc
            progress = soc_into_cv / remaining if remaining > 0 else 1.0
            taper = np.exp(-self.cv_taper_factor * progress)
            return max_c_rate * taper

    def get_charge_efficiency(
        self,
        soc: float,
        c_rate: float,
        temperature: Optional[Temperature] = None
    ) -> float:
        """Calculate charging efficiency.

        Efficiency decreases with:
        - Higher C-rates (more I^2R losses)
        - Higher SoC (less efficient near full charge)

        Args:
            soc: State of charge (0.0 to 1.0).
            c_rate: Charge rate.
            temperature: Ignored in this simple model.

        Returns:
            Charging efficiency (0.0 to 1.0).
        """
        # C-rate penalty
        c_rate_loss = self.efficiency_c_rate_factor * c_rate

        # SoC penalty (less efficient near full charge)
        soc_loss = 0.03 * soc  # 3% less efficient at full charge

        efficiency = self.base_efficiency - c_rate_loss - soc_loss
        return max(0.5, min(1.0, efficiency))

    def time_to_charge(
        self,
        start_soc: float,
        end_soc: float,
        max_c_rate: float,
        num_steps: int = 100
    ) -> float:
        """Estimate time to charge between SoC levels.

        Integrates charge rate over SoC to estimate total charge time.

        Args:
            start_soc: Starting SoC (0.0 to 1.0).
            end_soc: Target SoC (0.0 to 1.0).
            max_c_rate: Maximum charge C-rate.
            num_steps: Number of integration steps.

        Returns:
            Estimated charge time in hours.
        """
        if end_soc <= start_soc:
            return 0.0

        soc_values = np.linspace(start_soc, end_soc, num_steps)
        delta_soc = (end_soc - start_soc) / (num_steps - 1)

        total_time = 0.0
        for soc in soc_values[:-1]:
            c_rate = self.get_charge_current(soc, max_c_rate)
            efficiency = self.get_charge_efficiency(soc, c_rate)
            if c_rate > 0:
                # Time = dSoC / (C-rate * efficiency)
                dt = delta_soc / (c_rate * efficiency)
                total_time += dt

        return total_time


def load_discharge_model(
    chemistry_or_parameter_set: str,
    use_pybamm_direct: bool = False,
) -> DischargeModel:
    """Load a discharge model by chemistry name or PyBaMM parameter set.

    This is a convenience function that returns an appropriate discharge
    model based on the specified chemistry. By default, returns an
    AnalyticalDischargeModel. Set use_pybamm_direct=True to use direct
    PyBaMM simulation (requires pybamm_utils).

    Args:
        chemistry_or_parameter_set: Chemistry name (e.g., 'lithium_ion')
            or PyBaMM parameter set (e.g., 'Chen2020').
        use_pybamm_direct: If True, use PyBaMM for direct simulation.

    Returns:
        A DischargeModel instance.

    Raises:
        ValueError: If chemistry not recognized.
    """
    # Map common names to parameters
    chemistry_map = {
        'lithium_ion': ('Chen2020', 3.7, 4.2, 2.8, 30),  # name, nom, max, min, R_mohm
        'li_ion': ('Chen2020', 3.7, 4.2, 2.8, 30),
        'lithium_polymer': ('Chen2020', 3.7, 4.2, 3.2, 25),
        'lipo': ('Chen2020', 3.7, 4.2, 3.2, 25),
        'lithium_iron_phosphate': ('Marquis2019', 3.2, 3.65, 2.5, 40),
        'lifepo4': ('Marquis2019', 3.2, 3.65, 2.5, 40),
        'lfp': ('Marquis2019', 3.2, 3.65, 2.5, 40),
        'lithium_nmc': ('Chen2020', 3.7, 4.2, 3.0, 25),
        'nmc': ('Chen2020', 3.7, 4.2, 3.0, 25),
        'Chen2020': ('Chen2020', 3.7, 4.2, 2.8, 30),
        'Marquis2019': ('Marquis2019', 3.2, 3.65, 2.5, 40),
    }

    key = chemistry_or_parameter_set.lower().replace('-', '_')
    if key not in chemistry_map and chemistry_or_parameter_set not in chemistry_map:
        # Try exact match
        if chemistry_or_parameter_set in chemistry_map:
            key = chemistry_or_parameter_set
        else:
            available = sorted(set(chemistry_map.keys()))
            raise ValueError(
                f"Unknown chemistry '{chemistry_or_parameter_set}'. "
                f"Available: {available}"
            )

    params = chemistry_map.get(key) or chemistry_map.get(chemistry_or_parameter_set)
    _, v_nom, v_max, v_min, r_mohm = params

    if use_pybamm_direct:
        # Import here to avoid circular imports and optional dependency
        from evtoltools.components.battery.pybamm_utils import PyBaMMDischargeModel
        return PyBaMMDischargeModel(parameter_set=params[0])

    # Default: return analytical model with typical parameters
    return AnalyticalDischargeModel(
        v_max=Voltage(v_max, 'V'),
        v_min=Voltage(v_min, 'V'),
        v_nominal=Voltage(v_nom, 'V'),
        internal_resistance=Resistance(r_mohm, 'mohm'),
        capacity_ah=5.0  # Default capacity, will be overridden by Battery
    )
