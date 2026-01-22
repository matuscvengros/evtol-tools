"""Battery thermal modeling framework.

This module provides classes for modeling battery thermal behavior including
temperature limits, derating, and simple thermal dynamics.

Classes:
    ThermalLimits: Operating temperature limits and derating configuration.
    ThermalModel: Abstract base class for thermal models.
    SimpleThermalModel: Lumped-capacitance thermal model.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from evtoltools.common import Mass, Power, Temperature, Time


@dataclass
class ThermalLimits:
    """Battery operating temperature limits and derating configuration.

    Defines safe operating ranges for charging and discharging, plus
    temperature at which power derating begins.

    Attributes:
        max_charge_temp: Maximum safe charging temperature.
        max_discharge_temp: Maximum safe discharge temperature.
        min_temp: Minimum safe operating temperature.
        derate_temp: Temperature at which derating begins.
    """

    max_charge_temp: Temperature = None
    max_discharge_temp: Temperature = None
    min_temp: Temperature = None
    derate_temp: Temperature = None

    def __post_init__(self):
        """Set default values if not provided."""
        if self.max_charge_temp is None:
            self.max_charge_temp = Temperature(45, 'degC')
        if self.max_discharge_temp is None:
            self.max_discharge_temp = Temperature(60, 'degC')
        if self.min_temp is None:
            self.min_temp = Temperature(-20, 'degC')
        if self.derate_temp is None:
            self.derate_temp = Temperature(40, 'degC')

    def is_within_limits(self, temp: Temperature, is_charging: bool = False) -> bool:
        """Check if temperature is within safe operating limits.

        Args:
            temp: Current temperature.
            is_charging: True if battery is charging.

        Returns:
            True if temperature is within safe limits.
        """
        max_temp = self.max_charge_temp if is_charging else self.max_discharge_temp
        return self.min_temp <= temp <= max_temp

    def get_derate_factor(self, temp: Temperature) -> float:
        """Calculate power derate factor based on temperature.

        Returns a value between 0.0 and 1.0 where:
        - 1.0 = full power available
        - 0.0 = no power (at or above max temperature)

        Linear derating between derate_temp and max_discharge_temp.

        Args:
            temp: Current temperature.

        Returns:
            Derate factor (0.0 to 1.0).
        """
        temp_c = temp.in_units_of('degC')
        derate_c = self.derate_temp.in_units_of('degC')
        max_c = self.max_discharge_temp.in_units_of('degC')
        min_c = self.min_temp.in_units_of('degC')

        # Below derate temperature: full power
        if temp_c <= derate_c:
            return 1.0

        # Above max temperature: no power
        if temp_c >= max_c:
            return 0.0

        # Linear derating between derate and max
        derate_range = max_c - derate_c
        if derate_range <= 0:
            return 1.0

        excess = temp_c - derate_c
        return 1.0 - (excess / derate_range)

    def get_cold_derate_factor(self, temp: Temperature) -> float:
        """Calculate power derate factor for cold temperatures.

        Batteries have reduced capacity and increased internal
        resistance at cold temperatures.

        Args:
            temp: Current temperature.

        Returns:
            Cold derate factor (0.0 to 1.0).
        """
        temp_c = temp.in_units_of('degC')
        min_c = self.min_temp.in_units_of('degC')

        # Above freezing: full power
        if temp_c >= 0:
            return 1.0

        # Below minimum: no power
        if temp_c <= min_c:
            return 0.0

        # Linear derating between min_temp and 0°C
        if min_c >= 0:
            return 1.0

        return (temp_c - min_c) / (0 - min_c)


class ThermalModel(ABC):
    """Abstract base class for battery thermal models.

    Subclasses implement temperature prediction and dynamics.
    """

    @abstractmethod
    def temperature_after(
        self,
        initial_temp: Temperature,
        heat_rate: Power,
        duration: Time,
        ambient_temp: Temperature
    ) -> Temperature:
        """Predict temperature after a time period.

        Args:
            initial_temp: Starting temperature.
            heat_rate: Heat generation rate (I²R losses).
            duration: Time period.
            ambient_temp: Ambient/cooling temperature.

        Returns:
            Predicted temperature after duration.
        """
        pass


@dataclass
class SimpleThermalModel(ThermalModel):
    """Simple lumped-capacitance thermal model.

    Models the battery as a single thermal mass with convective
    cooling to ambient. Uses the lumped capacitance approximation:

        dT/dt = (Q_gen - Q_loss) / (m * Cp)

    where Q_loss = h * A * (T - T_ambient) ≈ cooling_coefficient * (T - T_ambient)

    Attributes:
        mass: Battery mass.
        specific_heat: Specific heat capacity (J/kg/K). Default 1000 for Li-ion.
        cooling_coefficient: Combined h*A term (W/K). Higher = better cooling.
    """

    mass: Mass
    specific_heat: float = 1000.0  # J/kg/K, typical for Li-ion
    cooling_coefficient: float = 5.0  # W/K, depends on cooling design

    def temperature_after(
        self,
        initial_temp: Temperature,
        heat_rate: Power,
        duration: Time,
        ambient_temp: Temperature
    ) -> Temperature:
        """Predict temperature using lumped capacitance model.

        Solves the differential equation analytically for constant
        heat generation and ambient temperature.

        Args:
            initial_temp: Starting temperature (K or degC).
            heat_rate: Heat generation rate (W).
            duration: Time period.
            ambient_temp: Ambient temperature.

        Returns:
            Temperature after duration.
        """
        # Convert to consistent units
        T_0 = initial_temp.in_units_of('K')
        T_amb = ambient_temp.in_units_of('K')
        Q = heat_rate.in_units_of('W')
        dt = duration.in_units_of('s')
        m = self.mass.in_units_of('kg')

        # Thermal capacitance
        C_th = m * self.specific_heat  # J/K

        # Time constant
        tau = C_th / self.cooling_coefficient  # seconds

        # Steady-state temperature offset from heat generation
        # At steady state: Q_gen = Q_loss, so dT_ss = Q / cooling_coefficient
        dT_ss = Q / self.cooling_coefficient

        # Analytical solution for first-order system:
        # T(t) = T_amb + dT_ss + (T_0 - T_amb - dT_ss) * exp(-t/tau)
        T_final = T_amb + dT_ss + (T_0 - T_amb - dT_ss) * _exp_approx(-dt / tau)

        return Temperature(T_final, 'K')

    def steady_state_temperature(
        self,
        heat_rate: Power,
        ambient_temp: Temperature
    ) -> Temperature:
        """Calculate steady-state temperature.

        The temperature the battery would reach if heat generation
        and ambient temperature remained constant indefinitely.

        Args:
            heat_rate: Constant heat generation rate.
            ambient_temp: Ambient temperature.

        Returns:
            Steady-state temperature.
        """
        Q = heat_rate.in_units_of('W')
        T_amb = ambient_temp.in_units_of('K')

        # Steady state: T_ss = T_amb + Q / cooling_coefficient
        T_ss = T_amb + Q / self.cooling_coefficient

        return Temperature(T_ss, 'K')

    def time_to_temperature(
        self,
        initial_temp: Temperature,
        target_temp: Temperature,
        heat_rate: Power,
        ambient_temp: Temperature
    ) -> Time:
        """Calculate time to reach a target temperature.

        Args:
            initial_temp: Starting temperature.
            target_temp: Target temperature.
            heat_rate: Heat generation rate.
            ambient_temp: Ambient temperature.

        Returns:
            Time to reach target temperature, or infinite if unreachable.
        """
        import math

        T_0 = initial_temp.in_units_of('K')
        T_target = target_temp.in_units_of('K')
        T_amb = ambient_temp.in_units_of('K')
        Q = heat_rate.in_units_of('W')
        m = self.mass.in_units_of('kg')

        C_th = m * self.specific_heat
        tau = C_th / self.cooling_coefficient
        dT_ss = Q / self.cooling_coefficient
        T_ss = T_amb + dT_ss

        # Check if target is reachable
        if T_0 < T_target <= T_ss:
            # Heating towards steady state
            pass
        elif T_0 > T_target >= T_ss:
            # Cooling towards steady state
            pass
        else:
            # Target is beyond steady state - return very large time
            return Time(float('inf'), 's')

        # Solve: T_target = T_ss + (T_0 - T_ss) * exp(-t/tau)
        # exp(-t/tau) = (T_target - T_ss) / (T_0 - T_ss)
        ratio = (T_target - T_ss) / (T_0 - T_ss)

        if ratio <= 0 or ratio >= 1:
            return Time(float('inf'), 's')

        t = -tau * math.log(ratio)
        return Time(t, 's')


def _exp_approx(x: float) -> float:
    """Exponential function with overflow protection."""
    import math
    if x < -700:
        return 0.0
    if x > 700:
        return float('inf')
    return math.exp(x)
