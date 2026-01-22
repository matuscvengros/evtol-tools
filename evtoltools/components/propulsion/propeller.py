"""Propeller component for eVTOL propulsion."""

from dataclasses import dataclass
from typing import Optional, Union
import math

from evtoltools.common import Length, Area, Velocity, AngularVelocity, Frequency
from evtoltools.common.atmosphere import Atmosphere, Altitude


@dataclass
class Propeller:
    """Propeller/rotor component with geometry and performance calculations.

    Attributes:
        diameter: Propeller diameter
        num_blades: Number of blades
        efficiency_hover: Figure of merit for hover (typically 0.6-0.8)
        efficiency_cruise: Propeller efficiency in forward flight (typically 0.7-0.85)
        tip_mach_limit: Maximum allowable tip Mach number (typically 0.7-0.9)

    Examples:
        >>> prop = Propeller(diameter=Length(1.5, 'm'), num_blades=3)
        >>> print(prop.disk_area)  # 1.767 m^2
        >>> print(prop.radius)     # 0.75 m

        >>> # Calculate tip speed
        >>> omega = AngularVelocity(2000, 'rpm')
        >>> tip_speed = prop.tip_speed(omega)

        >>> # Calculate max RPM from tip Mach limit
        >>> max_omega = prop.max_angular_velocity()
    """

    diameter: Length
    num_blades: int = 2
    efficiency_hover: float = 0.7  # Figure of Merit (FM)
    efficiency_cruise: float = 0.8
    tip_mach_limit: float = 0.85

    def __post_init__(self):
        # Normalize quantities to SI units
        object.__setattr__(self, 'diameter', self.diameter.to_default())

        if self.num_blades < 2:
            raise ValueError("num_blades must be at least 2")
        if not 0 < self.efficiency_hover <= 1:
            raise ValueError("efficiency_hover must be between 0 and 1")
        if not 0 < self.efficiency_cruise <= 1:
            raise ValueError("efficiency_cruise must be between 0 and 1")
        if not 0 < self.tip_mach_limit <= 1:
            raise ValueError("tip_mach_limit must be between 0 and 1")

    @property
    def radius(self) -> Length:
        """Propeller radius (half of diameter)."""
        r_m = self.diameter.in_units_of('m') / 2
        return Length(r_m, 'm')

    @property
    def disk_area(self) -> Area:
        """Disk area swept by propeller (pi * r^2)."""
        r_m = self.radius.in_units_of('m')
        area_m2 = math.pi * r_m ** 2
        return Area(area_m2, 'm^2')

    def tip_speed(self, angular_velocity: AngularVelocity) -> Velocity:
        """Calculate propeller tip speed.

        V_tip = omega * r

        Args:
            angular_velocity: Rotational speed (rad/s or rpm)

        Returns:
            Tip speed as Velocity
        """
        omega_rad_s = angular_velocity.in_units_of('rad/s')
        r_m = self.radius.in_units_of('m')
        tip_speed_m_s = omega_rad_s * r_m
        return Velocity(tip_speed_m_s, 'm/s')

    def angular_velocity_from_tip_speed(self, tip_speed: Velocity) -> AngularVelocity:
        """Calculate angular velocity for given tip speed.

        omega = V_tip / r

        Args:
            tip_speed: Desired tip speed

        Returns:
            Required angular velocity
        """
        v_m_s = tip_speed.in_units_of('m/s')
        r_m = self.radius.in_units_of('m')
        omega_rad_s = v_m_s / r_m
        return AngularVelocity(omega_rad_s, 'rad/s')

    def max_tip_speed(
        self,
        speed_of_sound: Optional[Velocity] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> Velocity:
        """Calculate maximum tip speed based on Mach limit.

        Args:
            speed_of_sound: Local speed of sound (defaults to sea level ISA: 343 m/s).
                Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.
                If provided, extracts speed of sound from atmosphere.

        Returns:
            Maximum allowable tip speed
        """
        # Determine speed of sound
        if atmosphere is not None:
            if isinstance(atmosphere, Altitude):
                atmosphere = Atmosphere(atmosphere)
            speed_of_sound = atmosphere.speed_of_sound
        elif speed_of_sound is None:
            speed_of_sound = Velocity(343, 'm/s')  # Sea level ISA

        max_tip_speed_m_s = speed_of_sound.in_units_of('m/s') * self.tip_mach_limit
        return Velocity(max_tip_speed_m_s, 'm/s')

    def max_angular_velocity(
        self,
        speed_of_sound: Optional[Velocity] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> AngularVelocity:
        """Calculate maximum angular velocity based on tip Mach limit.

        Args:
            speed_of_sound: Local speed of sound (defaults to sea level ISA: 343 m/s).
                Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Maximum angular velocity to stay within Mach limit
        """
        max_tip = self.max_tip_speed(speed_of_sound, atmosphere)
        return self.angular_velocity_from_tip_speed(max_tip)

    def tip_mach_number(
        self,
        angular_velocity: AngularVelocity,
        speed_of_sound: Optional[Velocity] = None,
        atmosphere: Optional[Union[Atmosphere, Altitude]] = None
    ) -> float:
        """Calculate tip Mach number at given angular velocity.

        Args:
            angular_velocity: Rotational speed
            speed_of_sound: Local speed of sound.
                Ignored if atmosphere is provided.
            atmosphere: Atmosphere instance or Altitude.

        Returns:
            Tip Mach number (dimensionless)
        """
        # Determine speed of sound
        if atmosphere is not None:
            if isinstance(atmosphere, Altitude):
                atmosphere = Atmosphere(atmosphere)
            speed_of_sound = atmosphere.speed_of_sound
        elif speed_of_sound is None:
            speed_of_sound = Velocity(343, 'm/s')

        tip = self.tip_speed(angular_velocity)
        return tip.in_units_of('m/s') / speed_of_sound.in_units_of('m/s')

    def frequency(self, angular_velocity: AngularVelocity) -> Frequency:
        """Calculate rotational frequency.

        Args:
            angular_velocity: Rotational speed

        Returns:
            Frequency as Frequency quantity
        """
        omega_rad_s = angular_velocity.in_units_of('rad/s')
        freq_hz = omega_rad_s / (2 * math.pi)
        return Frequency(freq_hz, 'Hz')

    def __repr__(self) -> str:
        return (
            f"Propeller(diameter={self.diameter}, "
            f"blades={self.num_blades}, FM={self.efficiency_hover})"
        )
