"""International Standard Atmosphere (ISA) calculations for evtol-tools.

This module provides atmospheric calculations using the ICAO 1993 International
Standard Atmosphere model via the ambiance library. Supports temperature offsets
for ISA+/- (hot/cold day) analysis.

Examples:
    >>> from evtoltools.common import Atmosphere, Length, Temperature
    >>>
    >>> # Standard atmosphere at 5000m
    >>> atm = Atmosphere(Length(5000, 'm'))
    >>> print(f"Temperature: {atm.temperature}")
    >>> print(f"Density: {atm.density}")
    >>>
    >>> # Hot day (ISA+20)
    >>> hot = Atmosphere(Length(5000, 'm'), temperature_offset=Temperature(20, 'K'))
    >>> print(f"Hot day density: {hot.density}")
"""

from typing import Optional, Union
import math
import numpy as np

from ambiance import Atmosphere as AmbianceAtmosphere

from evtoltools.common.quantities import (
    Length,
    Temperature,
    Pressure,
    Density,
    Velocity,
)

# Physical constants
GAS_CONSTANT_AIR = 287.05287  # J/(kg*K) - Specific gas constant for dry air
GAMMA_AIR = 1.4  # Ratio of specific heats for air

# ISA Sea Level Reference Constants
ISA_SEA_LEVEL_TEMPERATURE = Temperature(288.15, 'K')
ISA_SEA_LEVEL_PRESSURE = Pressure(101325, 'Pa')
ISA_SEA_LEVEL_DENSITY = Density(1.225, 'kg/m^3')
ISA_SEA_LEVEL_SPEED_OF_SOUND = Velocity(340.294, 'm/s')


class Atmosphere:
    """International Standard Atmosphere model with optional temperature offset.

    Provides atmospheric properties at any altitude using the ICAO 1993
    International Standard Atmosphere model. Supports temperature offsets
    for analyzing non-standard conditions (hot/cold day scenarios).

    Attributes:
        altitude: Geometric altitude
        temperature_offset: Temperature deviation from ISA (positive = hotter)

    Notes:
        - Temperature offset only affects temperature-dependent properties
        - Pressure is based on geometric altitude (unaffected by temp offset)
        - Density and speed of sound are recalculated with offset temperature

    Examples:
        >>> atm = Atmosphere(Length(10000, 'ft'))
        >>> print(atm.temperature)
        >>> print(atm.pressure)
        >>> print(atm.density)
        >>> print(atm.speed_of_sound)
        >>>
        >>> # Hot day analysis (ISA+15)
        >>> hot = Atmosphere(Length(5000, 'm'), Temperature(15, 'K'))
        >>> print(f"Density reduced to: {hot.density}")
    """

    def __init__(
        self,
        altitude: Length,
        temperature_offset: Optional[Temperature] = None
    ):
        """Initialize atmosphere at given altitude.

        Args:
            altitude: Geometric altitude (Length quantity)
            temperature_offset: Temperature offset from ISA in Kelvin.
                Positive values represent hotter than ISA.
                Defaults to None (standard ISA conditions).
        """
        self._altitude = altitude
        self._temperature_offset = temperature_offset

        # Get altitude in meters for ambiance
        altitude_m = altitude.in_units_of('m')

        # Handle both scalar and array inputs
        if isinstance(altitude_m, np.ndarray):
            self._ambiance = AmbianceAtmosphere(altitude_m)
        else:
            self._ambiance = AmbianceAtmosphere(float(altitude_m))

    @property
    def altitude(self) -> Length:
        """Geometric altitude."""
        return self._altitude

    @property
    def temperature_offset(self) -> Optional[Temperature]:
        """Temperature offset from ISA."""
        return self._temperature_offset

    def _to_scalar_or_array(self, value):
        """Convert single-element arrays to scalars, leave multi-element arrays as-is."""
        if isinstance(value, np.ndarray):
            # Convert 0-d arrays or 1-element 1-d arrays to scalar
            if value.ndim == 0 or (value.ndim == 1 and value.size == 1):
                return float(value.flat[0])
            return value
        return float(value)

    @property
    def temperature(self) -> Temperature:
        """Atmospheric temperature (ISA + offset if provided).

        Returns:
            Temperature quantity in Kelvin
        """
        isa_temp_k = self._to_scalar_or_array(self._ambiance.temperature)

        if self._temperature_offset is not None:
            offset_k = self._temperature_offset.in_units_of('K')
            temp_k = isa_temp_k + offset_k
        else:
            temp_k = isa_temp_k

        return Temperature(temp_k, 'K')

    @property
    def isa_temperature(self) -> Temperature:
        """Standard ISA temperature (without offset).

        Returns:
            Temperature quantity in Kelvin
        """
        isa_temp_k = self._to_scalar_or_array(self._ambiance.temperature)
        return Temperature(isa_temp_k, 'K')

    @property
    def pressure(self) -> Pressure:
        """Atmospheric pressure (based on geometric altitude, unaffected by temp offset).

        Returns:
            Pressure quantity in Pascals
        """
        pressure_pa = self._to_scalar_or_array(self._ambiance.pressure)
        return Pressure(pressure_pa, 'Pa')

    @property
    def density(self) -> Density:
        """Atmospheric density.

        If temperature offset is provided, density is recalculated using
        the ideal gas law: rho = P / (R * T)

        Returns:
            Density quantity in kg/m^3
        """
        if self._temperature_offset is None:
            # Standard ISA density
            density_kg_m3 = self._to_scalar_or_array(self._ambiance.density)
        else:
            # Recalculate density with offset temperature using ideal gas law
            pressure_pa = self._to_scalar_or_array(self._ambiance.pressure)
            temp_k = self.temperature.in_units_of('K')
            density_kg_m3 = pressure_pa / (GAS_CONSTANT_AIR * temp_k)
            density_kg_m3 = self._to_scalar_or_array(density_kg_m3)

        return Density(density_kg_m3, 'kg/m^3')

    @property
    def isa_density(self) -> Density:
        """Standard ISA density (without temperature offset).

        Returns:
            Density quantity in kg/m^3
        """
        density_kg_m3 = self._to_scalar_or_array(self._ambiance.density)
        return Density(density_kg_m3, 'kg/m^3')

    @property
    def speed_of_sound(self) -> Velocity:
        """Speed of sound.

        If temperature offset is provided, speed of sound is recalculated:
        a = sqrt(gamma * R * T)

        Returns:
            Speed of sound as Velocity quantity in m/s
        """
        if self._temperature_offset is None:
            # Standard ISA speed of sound
            sos_m_s = self._to_scalar_or_array(self._ambiance.speed_of_sound)
        else:
            # Recalculate with offset temperature
            temp_k = self.temperature.in_units_of('K')
            if isinstance(temp_k, np.ndarray) and temp_k.ndim > 0:
                sos_m_s = np.sqrt(GAMMA_AIR * GAS_CONSTANT_AIR * temp_k)
            else:
                sos_m_s = math.sqrt(GAMMA_AIR * GAS_CONSTANT_AIR * float(temp_k))

        return Velocity(sos_m_s, 'm/s')

    @property
    def isa_speed_of_sound(self) -> Velocity:
        """Standard ISA speed of sound (without temperature offset).

        Returns:
            Speed of sound as Velocity quantity in m/s
        """
        sos_m_s = self._to_scalar_or_array(self._ambiance.speed_of_sound)
        return Velocity(sos_m_s, 'm/s')

    @property
    def kinematic_viscosity(self) -> float:
        """Kinematic viscosity in m^2/s.

        Returns:
            Kinematic viscosity (m^2/s)
        """
        return self._to_scalar_or_array(self._ambiance.kinematic_viscosity)

    @property
    def dynamic_viscosity(self) -> float:
        """Dynamic viscosity in Pa*s.

        Returns:
            Dynamic viscosity (Pa*s)
        """
        return self._to_scalar_or_array(self._ambiance.dynamic_viscosity)

    @classmethod
    def from_pressure_altitude(cls, pressure: Pressure) -> 'Atmosphere':
        """Create atmosphere from pressure altitude.

        Determines the geometric altitude that corresponds to the given
        pressure in the standard atmosphere.

        Args:
            pressure: Atmospheric pressure

        Returns:
            Atmosphere instance at the corresponding pressure altitude

        Examples:
            >>> atm = Atmosphere.from_pressure_altitude(Pressure(50000, 'Pa'))
            >>> print(f"Pressure altitude: {atm.altitude.to('ft')}")
        """
        # Use inverse calculation - binary search for altitude
        pressure_pa = pressure.in_units_of('Pa')

        # Search bounds (0 to 80 km covers ISA range)
        h_low = 0.0
        h_high = 80000.0
        tolerance = 0.1  # meters

        while (h_high - h_low) > tolerance:
            h_mid = (h_low + h_high) / 2
            p_mid = AmbianceAtmosphere(h_mid).pressure

            if p_mid > pressure_pa:
                h_low = h_mid
            else:
                h_high = h_mid

        return cls(Length(h_mid, 'm'))

    @classmethod
    def from_density_altitude(cls, density: Density) -> 'Atmosphere':
        """Create atmosphere from density altitude.

        Determines the geometric altitude that corresponds to the given
        density in the standard atmosphere.

        Args:
            density: Atmospheric density

        Returns:
            Atmosphere instance at the corresponding density altitude

        Examples:
            >>> atm = Atmosphere.from_density_altitude(Density(0.9, 'kg/m^3'))
            >>> print(f"Density altitude: {atm.altitude.to('ft')}")
        """
        # Use inverse calculation - binary search for altitude
        density_kg_m3 = density.in_units_of('kg/m^3')

        # Search bounds (0 to 80 km covers ISA range)
        h_low = 0.0
        h_high = 80000.0
        tolerance = 0.1  # meters

        while (h_high - h_low) > tolerance:
            h_mid = (h_low + h_high) / 2
            rho_mid = AmbianceAtmosphere(h_mid).density

            if rho_mid > density_kg_m3:
                h_low = h_mid
            else:
                h_high = h_mid

        return cls(Length(h_mid, 'm'))

    @classmethod
    def pressure_altitude(cls, pressure: Pressure) -> Length:
        """Calculate pressure altitude from atmospheric pressure.

        Args:
            pressure: Atmospheric pressure

        Returns:
            Pressure altitude as Length quantity
        """
        atm = cls.from_pressure_altitude(pressure)
        return atm.altitude

    @classmethod
    def density_altitude(cls, density: Density) -> Length:
        """Calculate density altitude from atmospheric density.

        Args:
            density: Atmospheric density

        Returns:
            Density altitude as Length quantity
        """
        atm = cls.from_density_altitude(density)
        return atm.altitude

    def __repr__(self) -> str:
        offset_str = ""
        if self._temperature_offset is not None:
            offset_k = self._temperature_offset.in_units_of('K')
            offset_str = f", ISA{'+' if offset_k >= 0 else ''}{offset_k:.1f}K"
        return f"Atmosphere(altitude={self._altitude}{offset_str})"

    def __str__(self) -> str:
        return (
            f"Atmosphere at {self._altitude}: "
            f"T={self.temperature}, P={self.pressure}, "
            f"rho={self.density}"
        )


def atmosphere_at_altitude(
    altitude: Length,
    temperature_offset: Optional[Temperature] = None
) -> Atmosphere:
    """Convenience function to create atmosphere at given altitude.

    Args:
        altitude: Geometric altitude
        temperature_offset: Temperature offset from ISA

    Returns:
        Atmosphere instance
    """
    return Atmosphere(altitude, temperature_offset)


def sea_level_atmosphere() -> Atmosphere:
    """Create atmosphere at sea level (standard ISA).

    Returns:
        Atmosphere instance at sea level
    """
    return Atmosphere(Length(0, 'm'))
