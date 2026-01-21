"""Payload component for eVTOL aircraft."""

from dataclasses import dataclass
from typing import Optional

from evtoltools.common import Mass, Length
from evtoltools.components.base import BaseComponent


@dataclass
class Payload(BaseComponent):
    """Payload component - holds mass and optional position information.

    Attributes:
        _mass: Payload mass
        x_position: Optional longitudinal CG position (for future use)
        y_position: Optional lateral CG position (for future use)
        z_position: Optional vertical CG position (for future use)
        description: Optional description of payload contents

    Examples:
        >>> payload = Payload(Mass(200, 'kg'))
        >>> payload = Payload(Mass(320, 'kg'), description='4 passengers @ 80kg')
    """

    _mass: Mass
    x_position: Optional[Length] = None
    y_position: Optional[Length] = None
    z_position: Optional[Length] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Normalize quantity fields to SI units."""
        object.__setattr__(self, '_mass', self._mass.to_default())
        if self.x_position is not None:
            object.__setattr__(self, 'x_position', self.x_position.to_default())
        if self.y_position is not None:
            object.__setattr__(self, 'y_position', self.y_position.to_default())
        if self.z_position is not None:
            object.__setattr__(self, 'z_position', self.z_position.to_default())

    @property
    def component_type(self) -> str:
        return 'payload'

    @property
    def mass(self) -> Mass:
        return self._mass

    @property
    def has_position(self) -> bool:
        """Check if position information is available."""
        return any([self.x_position, self.y_position, self.z_position])

    def __repr__(self) -> str:
        if self.description:
            return f"Payload(mass={self.mass}, description='{self.description}')"
        return f"Payload(mass={self.mass})"
