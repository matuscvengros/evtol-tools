"""Propulsion system for eVTOL aircraft."""

from dataclasses import dataclass, field
from typing import List, Optional
import math

from evtoltools.common import Mass, Power, Force, Area, Velocity, Density
from evtoltools.components.base import BaseComponent
from evtoltools.components.propulsion.motor import Motor
from evtoltools.components.propulsion.propeller import Propeller


@dataclass
class PropulsionSystem(BaseComponent):
    """Complete propulsion system with motors and propellers.

    Supports multi-rotor configurations common in eVTOL aircraft.

    Attributes:
        motors: List of Motor instances (or single motor replicated)
        propellers: List of Propeller instances (or single propeller replicated)
        num_units: Number of motor/propeller units
        installation_efficiency: Efficiency loss from installation effects

    Examples:
        >>> motor = Motor(max_power=Power(50, 'kW'), efficiency=0.92)
        >>> propeller = Propeller(diameter=Length(1.5, 'm'))
        >>>
        >>> # Create 4-rotor system
        >>> propulsion = PropulsionSystem(
        ...     motors=[motor],  # Replicated to 4
        ...     propellers=[propeller],  # Replicated to 4
        ...     num_units=4
        ... )
        >>>
        >>> print(propulsion.total_disk_area)
        >>> print(propulsion.total_max_power)
        >>>
        >>> # Calculate hover power
        >>> hover_power = propulsion.hover_power_required(
        ...     weight=Force(15000, 'N'),
        ...     air_density=Density(1.225, 'kg/m^3')
        ... )
    """

    motors: List[Motor]
    propellers: List[Propeller]
    num_units: int = 1
    installation_efficiency: float = 0.95

    def __post_init__(self):
        # Replicate single motor/propeller to num_units if needed
        if len(self.motors) == 1 and self.num_units > 1:
            self.motors = self.motors * self.num_units
        if len(self.propellers) == 1 and self.num_units > 1:
            self.propellers = self.propellers * self.num_units

        if len(self.motors) != len(self.propellers):
            raise ValueError(
                f"Number of motors ({len(self.motors)}) must match "
                f"number of propellers ({len(self.propellers)})"
            )

        if len(self.motors) != self.num_units:
            raise ValueError(
                f"Number of motors ({len(self.motors)}) must match "
                f"num_units ({self.num_units})"
            )

        if not 0 < self.installation_efficiency <= 1:
            raise ValueError("installation_efficiency must be between 0 and 1")

    @property
    def component_type(self) -> str:
        return 'propulsion'

    @property
    def mass(self) -> Mass:
        """Total propulsion system mass (motors only)."""
        total_kg = 0.0
        for motor in self.motors:
            if motor.mass is not None:
                total_kg += motor.mass.in_units_of('kg')
        return Mass(total_kg, 'kg')

    @property
    def total_disk_area(self) -> Area:
        """Combined disk area of all propellers."""
        total_m2 = sum(p.disk_area.in_units_of('m^2') for p in self.propellers)
        return Area(total_m2, 'm^2')

    @property
    def total_max_electrical_power(self) -> Power:
        """Total maximum electrical power across all motors."""
        total_w = sum(m.max_power.in_units_of('W') for m in self.motors)
        return Power(total_w, 'W')

    @property
    def total_max_shaft_power(self) -> Power:
        """Total maximum shaft power across all motors."""
        total_w = sum(m.max_shaft_power.in_units_of('W') for m in self.motors)
        return Power(total_w, 'W')

    @property
    def average_motor_efficiency(self) -> float:
        """Average motor efficiency across all motors."""
        return sum(m.efficiency for m in self.motors) / len(self.motors)

    @property
    def average_figure_of_merit(self) -> float:
        """Average figure of merit across all propellers."""
        return sum(p.efficiency_hover for p in self.propellers) / len(self.propellers)

    @property
    def average_cruise_efficiency(self) -> float:
        """Average cruise efficiency across all propellers."""
        return sum(p.efficiency_cruise for p in self.propellers) / len(self.propellers)

    def hover_power_ideal(
        self,
        thrust: Force,
        air_density: Optional[Density] = None
    ) -> Power:
        """Calculate ideal hover power from momentum theory.

        P_ideal = T^(3/2) / sqrt(2 * rho * A)

        Args:
            thrust: Total thrust required (typically equals weight)
            air_density: Air density (defaults to sea level ISA)

        Returns:
            Ideal induced power
        """
        if air_density is None:
            air_density = Density(1.225, 'kg/m^3')

        thrust_n = thrust.in_units_of('N')
        rho = air_density.in_units_of('kg/m^3')
        area_m2 = self.total_disk_area.in_units_of('m^2')

        # Ideal power from momentum theory
        power_w = thrust_n ** 1.5 / math.sqrt(2 * rho * area_m2)
        return Power(power_w, 'W')

    def hover_shaft_power(
        self,
        thrust: Force,
        air_density: Optional[Density] = None
    ) -> Power:
        """Calculate shaft power required to hover.

        Accounts for figure of merit and installation losses.

        Args:
            thrust: Total thrust required
            air_density: Air density

        Returns:
            Required shaft power
        """
        ideal_power = self.hover_power_ideal(thrust, air_density)
        fm = self.average_figure_of_merit

        # Actual shaft power accounting for rotor efficiency
        power_w = ideal_power.in_units_of('W') / (fm * self.installation_efficiency)
        return Power(power_w, 'W')

    def hover_electrical_power(
        self,
        thrust: Force,
        air_density: Optional[Density] = None
    ) -> Power:
        """Calculate electrical power required to hover.

        Args:
            thrust: Total thrust required (typically equals weight)
            air_density: Air density

        Returns:
            Electrical power required
        """
        shaft_power = self.hover_shaft_power(thrust, air_density)
        avg_efficiency = self.average_motor_efficiency

        electrical_w = shaft_power.in_units_of('W') / avg_efficiency
        return Power(electrical_w, 'W')

    def disk_loading(self, thrust: Force) -> float:
        """Calculate disk loading (thrust per unit disk area).

        Args:
            thrust: Total thrust

        Returns:
            Disk loading in N/m^2
        """
        thrust_n = thrust.in_units_of('N')
        area_m2 = self.total_disk_area.in_units_of('m^2')
        return thrust_n / area_m2

    def power_loading(self, thrust: Force) -> float:
        """Calculate power loading (thrust per unit power).

        Args:
            thrust: Total thrust

        Returns:
            Power loading in N/W
        """
        thrust_n = thrust.in_units_of('N')
        power_w = self.total_max_shaft_power.in_units_of('W')
        return thrust_n / power_w

    def induced_velocity(
        self,
        thrust: Force,
        air_density: Optional[Density] = None
    ) -> Velocity:
        """Calculate induced velocity in hover.

        v_i = sqrt(T / (2 * rho * A))

        Args:
            thrust: Total thrust
            air_density: Air density

        Returns:
            Induced velocity
        """
        if air_density is None:
            air_density = Density(1.225, 'kg/m^3')

        thrust_n = thrust.in_units_of('N')
        rho = air_density.in_units_of('kg/m^3')
        area_m2 = self.total_disk_area.in_units_of('m^2')

        v_i = math.sqrt(thrust_n / (2 * rho * area_m2))
        return Velocity(v_i, 'm/s')

    def max_tip_speed(self) -> Velocity:
        """Get maximum tip speed across all propellers."""
        max_speeds = [p.max_tip_speed() for p in self.propellers]
        max_m_s = min(v.in_units_of('m/s') for v in max_speeds)
        return Velocity(max_m_s, 'm/s')

    def __repr__(self) -> str:
        return (
            f"PropulsionSystem({self.num_units} units, "
            f"total_power={self.total_max_electrical_power.to('kW')}, "
            f"disk_area={self.total_disk_area})"
        )
