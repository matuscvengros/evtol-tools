"""Pint UnitRegistry singleton for the evtoltools package."""

from __future__ import annotations

from pint import UnitRegistry, set_application_registry

#: Application-wide unit registry instance.
ureg = UnitRegistry()
set_application_registry(ureg)

#: Shorthand constructor for :class:`pint.Quantity`.
Q_ = ureg.Quantity
