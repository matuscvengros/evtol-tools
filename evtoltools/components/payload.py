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
