"""Avionics component for eVTOL aircraft."""

from dataclasses import dataclass

from evtoltools.common import Mass
from evtoltools.components.base import BaseComponent


@dataclass
class Avionics(BaseComponent):
    """Avionics component - mass calculated as fraction of empty weight.

    This is a surrogate model for avionics mass estimation based on
    historical data correlating avionics mass to aircraft empty weight.

    Attributes:
        _mass: Stored mass value (set via from_weight_fraction or directly)

    Examples:
        >>> empty_weight = Mass(1500, 'kg')
        >>> avionics = Avionics.from_weight_fraction(empty_weight, 0.05)
        >>> print(avionics.mass)  # 75 kg

        >>> avionics = Avionics(Mass(50, 'kg'))  # Direct specification
    """

    _mass: Mass

    @property
    def component_type(self) -> str:
        return 'avionics'

    @property
    def mass(self) -> Mass:
        return self._mass

    @classmethod
    def from_weight_fraction(cls, empty_weight: Mass, fraction: float) -> 'Avionics':
        """Create Avionics from empty weight and mass fraction.

        Args:
            empty_weight: Aircraft empty weight
            fraction: Avionics mass as fraction of empty weight (e.g., 0.05 for 5%)

        Returns:
            Avionics instance with calculated mass

        Raises:
            ValueError: If fraction is not between 0 and 1
        """
        if not 0 <= fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {fraction}")

        avionics_mass = empty_weight * fraction
        return cls(_mass=avionics_mass)

    @classmethod
    def calculate_mass(cls, empty_weight: Mass, fraction: float) -> Mass:
        """Calculate avionics mass from empty weight and fraction.

        Standalone calculation method for use without creating instance.

        Args:
            empty_weight: Aircraft empty weight
            fraction: Avionics mass as fraction of empty weight

        Returns:
            Calculated avionics mass
        """
        if not 0 <= fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {fraction}")
        return empty_weight * fraction
