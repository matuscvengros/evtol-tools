"""Propulsion system for eVTOL aircraft."""

from dataclasses import dataclass, field
from typing import List, Optional, Union
import math

from evtoltools.common import Mass, Power, Force, Area, Velocity, Density, Pressure, Length, sqrt
from evtoltools.common.atmosphere import Atmosphere, Altitude
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
        total = Mass(0, 'kg')
        for motor in self.motors:
            if motor.mass is not None:
                total = total + motor.mass
        return total

    @property
    def total_disk_area(self) -> Area:
        """Combined disk area of all propellers."""
        total = Area(0, 'm^2')
        for p in self.propellers:
            total = total + p.disk_area
        return total

    @property
    def total_max_electrical_power(self) -> Power:
        """Total maximum electrical power across all motors."""
        total = Power(0, 'W')
        for m in self.motors:
            total = total + m.max_power
        return total

    @property
    def total_max_shaft_power(self) -> Power:
        """Total maximum shaft power across all motors."""
        total = Power(0, 'W')
        for m in self.motors:
            total = total + m.max_shaft_power
        return total

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
        air_density: Optional[Density] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Power:
        """Calculate ideal hover power from momentum theory.

        P_ideal = T^(3/2) / sqrt(2 * rho * A)

        Args:
            thrust: Total thrust required (typically equals weight)
            air_density: Air density (defaults to sea level ISA).
                Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.
                If provided, extracts density from atmosphere.

        Returns:
            Ideal induced power
        """
        # Determine air density
        if atmosphere is not None:
            if isinstance(atmosphere, Altitude):
                atmosphere = Atmosphere(atmosphere)
            air_density = atmosphere.density
        elif air_density is None:
            air_density = Density(1.225, 'kg/m^3')

        # Ideal power from momentum theory: P = T^(3/2) / sqrt(2 * rho * A)
        power_pint = thrust ** 1.5 / sqrt(2 * air_density * self.total_disk_area)
        return Power(power_pint.to('W'))

    def hover_shaft_power(
        self,
        thrust: Force,
        air_density: Optional[Density] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Power:
        """Calculate shaft power required to hover.

        Accounts for figure of merit and installation losses.

        Args:
            thrust: Total thrust required
            air_density: Air density. Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Required shaft power
        """
        ideal_power = self.hover_power_ideal(thrust, air_density, atmosphere)
        fm = self.average_figure_of_merit

        # Actual shaft power accounting for rotor efficiency
        return ideal_power / (fm * self.installation_efficiency)

    def hover_electrical_power(
        self,
        thrust: Force,
        air_density: Optional[Density] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Power:
        """Calculate electrical power required to hover.

        Args:
            thrust: Total thrust required (typically equals weight)
            air_density: Air density. Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Electrical power required
        """
        shaft_power = self.hover_shaft_power(thrust, air_density, atmosphere)
        avg_efficiency = self.average_motor_efficiency
        return shaft_power / avg_efficiency

    def disk_loading(self, thrust: Force) -> Pressure:
        """Calculate disk loading (thrust per unit disk area).

        Args:
            thrust: Total thrust

        Returns:
            Disk loading as Pressure
        """
        dl_pint = thrust / self.total_disk_area
        return Pressure(dl_pint.to('Pa'))

    def power_loading(self, thrust: Force) -> float:
        """Calculate power loading (thrust per unit power).

        Args:
            thrust: Total thrust

        Returns:
            Power loading in N/W
        """
        ratio_pint = thrust / self.total_max_shaft_power
        return ratio_pint.to('N/W').magnitude

    def induced_velocity(
        self,
        thrust: Force,
        air_density: Optional[Density] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Velocity:
        """Calculate induced velocity in hover.

        v_i = sqrt(T / (2 * rho * A))

        Args:
            thrust: Total thrust
            air_density: Air density. Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Induced velocity
        """
        # Determine air density
        if atmosphere is not None:
            if isinstance(atmosphere, Altitude):
                atmosphere = Atmosphere(atmosphere)
            air_density = atmosphere.density
        elif air_density is None:
            air_density = Density(1.225, 'kg/m^3')

        # Induced velocity: v_i = sqrt(T / (2 * rho * A))
        v_pint = sqrt(thrust / (2 * air_density * self.total_disk_area))
        return Velocity(v_pint.to('m/s'))

    def max_tip_speed(
        self,
        speed_of_sound: Optional[Velocity] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Velocity:
        """Get maximum tip speed across all propellers.

        Args:
            speed_of_sound: Local speed of sound. Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Maximum allowable tip speed (minimum across all propellers)
        """
        max_speeds = [p.max_tip_speed(speed_of_sound, atmosphere) for p in self.propellers]
        return min(max_speeds, key=lambda v: v.magnitude)

    def __repr__(self) -> str:
        return (
            f"PropulsionSystem({self.num_units} units, "
            f"total_power={self.total_max_electrical_power.to('kW')}, "
            f"disk_area={self.total_disk_area})"
        )
