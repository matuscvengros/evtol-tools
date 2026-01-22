"""Electric motor component for eVTOL propulsion."""

from dataclasses import dataclass
from typing import Optional

from evtoltools.common import Mass, Power, AngularVelocity


@dataclass
class Motor:
    """Electric motor component.

    Attributes:
        max_power: Maximum continuous electrical input power
        efficiency: Motor efficiency (electrical to mechanical)
        mass: Motor mass (optional)
        kv_rating: Motor velocity constant (RPM/V) - optional
        max_rpm: Maximum rotational speed - optional

    Examples:
        >>> motor = Motor(
        ...     max_power=Power(50, 'kW'),
        ...     efficiency=0.92,
        ...     mass=Mass(8, 'kg')
        ... )
        >>> print(motor.max_shaft_power)  # 46 kW
    """

    max_power: Power  # Max electrical input power
    efficiency: float = 0.92  # Efficiency (0 < efficiency <= 1)
    mass: Optional[Mass] = None
    kv_rating: Optional[float] = None  # RPM per volt
    max_rpm: Optional[AngularVelocity] = None

    def __post_init__(self):
        # Normalize quantities to SI units
        object.__setattr__(self, 'max_power', self.max_power.to_default())
        if self.mass is not None:
            object.__setattr__(self, 'mass', self.mass.to_default())
        if self.max_rpm is not None:
            object.__setattr__(self, 'max_rpm', self.max_rpm.to_default())

        if not 0 < self.efficiency <= 1:
            raise ValueError("efficiency must be between 0 and 1")
        if self.max_power.in_units_of('W') <= 0:
            raise ValueError("max_power must be positive")

    def shaft_power(self, electrical_power: Power) -> Power:
        """Calculate mechanical shaft power from electrical input.

        P_shaft = P_electrical * efficiency

        Args:
            electrical_power: Electrical power input

        Returns:
            Mechanical shaft power output
        """
        power_w = electrical_power.in_units_of('W')
        shaft_power_w = power_w * self.efficiency
        return Power(shaft_power_w, 'W')

    def electrical_power(self, shaft_power: Power) -> Power:
        """Calculate electrical power required for given shaft power.

        P_electrical = P_shaft / efficiency

        Args:
            shaft_power: Required mechanical shaft power

        Returns:
            Required electrical power input
        """
        power_w = shaft_power.in_units_of('W')
        electrical_power_w = power_w / self.efficiency
        return Power(electrical_power_w, 'W')

    @property
    def max_shaft_power(self) -> Power:
        """Maximum shaft power output at max electrical input."""
        return self.shaft_power(self.max_power)

    @property
    def power_to_weight(self) -> float:
        """Power to weight ratio (kW/kg).

        Returns:
            Power to weight ratio, or 0 if mass not specified
        """
        if self.mass is None:
            return 0.0
        power_kw = self.max_power.in_units_of('kW')
        mass_kg = self.mass.in_units_of('kg')
        return power_kw / mass_kg

    def __repr__(self) -> str:
        return (
            f"Motor(max_power={self.max_power.to('kW')}, "
            f"efficiency={self.efficiency})"
        )
