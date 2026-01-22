"""Centralized pint UnitRegistry for evtol-tools.

This module provides a singleton registry instance that should be used
throughout the evtol-tools package. This ensures all quantities can
interoperate and prevents ValueError from mixing registries.
"""

from pint import UnitRegistry, set_application_registry

# Create the shared registry instance
ureg = UnitRegistry()

# Set as application registry for pickle support
set_application_registry(ureg)

# Convenience alias for Quantity constructor
Q_ = ureg.Quantity  # type: ignore[type-arg]

__all__ = ['ureg', 'Q_']
