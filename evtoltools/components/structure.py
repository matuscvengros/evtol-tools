"""Structure component for eVTOL aircraft."""

from dataclasses import dataclass

from evtoltools.common import Mass
from evtoltools.components.base import BaseComponent


@dataclass
class Structure(BaseComponent):
    """Structural component - mass calculated as fraction of empty weight.

    This is a surrogate model for structural mass estimation.

    Attributes:
        _mass: Stored mass value

    Examples:
        >>> empty_weight = Mass(1500, 'kg')
        >>> structure = Structure.from_weight_fraction(empty_weight, 0.30)
        >>> print(structure.mass)  # 450 kg

        >>> structure = Structure(Mass(500, 'kg'))  # Direct specification
    """

    _mass: Mass

    def __post_init__(self):
        """Normalize quantity fields to SI units."""
        object.__setattr__(self, '_mass', self._mass.to_default())

    # Classmethods (alternative constructors, per Policy 9)
    @classmethod
    def from_weight_fraction(cls, empty_weight: Mass, fraction: float) -> 'Structure':
        """Create Structure from empty weight and mass fraction.

        Args:
            empty_weight: Aircraft empty weight
            fraction: Structure mass as fraction of empty weight (e.g., 0.30 for 30%)

        Returns:
            Structure instance with calculated mass

        Raises:
            ValueError: If fraction is not between 0 and 1
        """
        if not 0 <= fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {fraction}")

        structure_mass = empty_weight * fraction
        return cls(_mass=structure_mass)

    @classmethod
    def calculate_mass(cls, empty_weight: Mass, fraction: float) -> Mass:
        """Calculate structure mass from empty weight and fraction.

        Args:
            empty_weight: Aircraft empty weight
            fraction: Structure mass as fraction of empty weight

        Returns:
            Calculated structure mass
        """
        if not 0 <= fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {fraction}")
        return empty_weight * fraction

    # Properties (per Policy 9)
    @property
    def component_type(self) -> str:
        return 'structure'

    @property
    def mass(self) -> Mass:
        return self._mass
