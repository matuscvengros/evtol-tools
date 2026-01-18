"""Base classes for eVTOL components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from evtoltools.common import Mass


@dataclass
class ComponentResult:
    """Result container for component calculations.

    Used when component construction involves calculations that may
    produce warnings or need to communicate adjustments to the user.

    Attributes:
        value: The calculated/constructed component instance
        warnings: List of warning messages for user notification
        metadata: Additional information about the calculation
    """

    value: Any
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseComponent(ABC):
    """Abstract base class for eVTOL components.

    All components must provide a mass property and component type identifier.
    """

    @property
    @abstractmethod
    def component_type(self) -> str:
        """Return the component type identifier."""
        pass

    @property
    @abstractmethod
    def mass(self) -> Mass:
        """Return the component mass."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(mass={self.mass})"
