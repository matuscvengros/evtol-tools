"""Pint UnitRegistry singleton for the evtol_tools package."""

from __future__ import annotations

from pint import UnitRegistry, set_application_registry

ureg = UnitRegistry()
set_application_registry(ureg)
Q_ = ureg.Quantity
