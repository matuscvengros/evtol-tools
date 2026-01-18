"""Propulsion component package for eVTOL aircraft."""

from evtoltools.components.propulsion.propeller import Propeller
from evtoltools.components.propulsion.motor import Motor
from evtoltools.components.propulsion.propulsion import PropulsionSystem

__all__ = [
    'Propeller',
    'Motor',
    'PropulsionSystem',
]
