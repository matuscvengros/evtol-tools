"""Altitude quantity for atmospheric calculations in evtol-tools.

This module provides the Altitude class, a semantic wrapper around Length
specifically for representing altitudes with aviation-specific functionality.

Examples:
    >>> from evtoltools.common import Altitude
    >>>
    >>> # Create altitude
    >>> alt = Altitude(5000, 'ft')
    >>> print(f"Altitude: {alt}")
    >>>
    >>> # Flight level conversion
    >>> cruise = Altitude.from_flight_level(35)  # FL035 = 3500 ft
    >>> print(f"FL035 = {cruise}")
    >>>
    >>> # Get flight level
    >>> alt = Altitude(10000, 'ft')
    >>> print(f"Flight level: FL{alt.to_flight_level():03.0f}")
"""

from typing import Union, Optional
import numpy as np
from pint import Quantity as PintQuantity

from evtoltools.common.units.quantities import Length, Pressure, Density


class Altitude(Length):
    """Represents an altitude quantity with aviation-specific functionality.

    Altitude is a semantic wrapper around Length, providing the same unit
    conversion and arithmetic capabilities with additional methods specific
    to aviation altitude handling.

    Features:
        - All Length functionality (unit conversion, arithmetic, arrays)
        - Flight level conversion (FL100 = 10,000 ft)
        - Named constructors for common references
        - Pressure altitude and density altitude support

    Examples:
        >>> alt = Altitude(1500, 'ft')
        >>> alt.to('m')
        Altitude(457.2, 'm')

        >>> # Flight levels
        >>> Altitude.from_flight_level(100)  # FL100
        Altitude(10000, 'ft')

        >>> Altitude(35000, 'ft').to_flight_level()
        350.0

        >>> # Sea level reference
        >>> Altitude.sea_level()
        Altitude(0, 'm')
    """

    # eVTOL typical operating ceiling (for reference, not enforced)
    EVTOL_TYPICAL_CEILING_FT = 10000
    EVTOL_TYPICAL_CEILING_M = 3048

    # Troposphere/Tropopause boundary
    TROPOPAUSE_M = 11000
    TROPOPAUSE_FT = 36089

    @classmethod
    def sea_level(cls) -> 'Altitude':
        """Create altitude at sea level (0 meters).

        Returns:
            Altitude at sea level

        Examples:
            >>> Altitude.sea_level()
            Altitude(0, 'm')
        """
        return cls(0, 'm')

    @classmethod
    def from_flight_level(cls, flight_level: Union[int, float]) -> 'Altitude':
        """Create altitude from flight level notation.

        Flight levels are pressure altitudes in hundreds of feet.
        FL100 = 10,000 ft, FL350 = 35,000 ft, etc.

        Note: Flight levels are technically pressure altitudes (referenced
        to standard pressure 1013.25 hPa), but this method creates a
        geometric altitude assuming standard atmosphere conditions.

        Args:
            flight_level: Flight level number (e.g., 100 for FL100)

        Returns:
            Altitude in feet

        Examples:
            >>> Altitude.from_flight_level(100)
            Altitude(10000, 'ft')

            >>> Altitude.from_flight_level(35)  # FL035
            Altitude(3500, 'ft')
        """
        altitude_ft = flight_level * 100
        return cls(altitude_ft, 'ft')

    @classmethod
    def from_pressure(cls, pressure: Pressure) -> 'Altitude':
        """Create altitude from atmospheric pressure (pressure altitude).

        Determines the geometric altitude in the ISA that corresponds
        to the given pressure.

        Args:
            pressure: Atmospheric pressure

        Returns:
            Corresponding pressure altitude

        Examples:
            >>> from evtoltools.common import Pressure
            >>> Altitude.from_pressure(Pressure(90000, 'Pa'))
            Altitude(988.5, 'm')  # approximately
        """
        from ambiance import Atmosphere as AmbianceAtmosphere

        pressure_pa = pressure.in_units_of('Pa')

        # Binary search for altitude
        h_low, h_high = 0.0, 80000.0
        tolerance = 0.1  # meters

        while (h_high - h_low) > tolerance:
            h_mid = (h_low + h_high) / 2
            p_mid_arr = AmbianceAtmosphere(h_mid).pressure
            p_mid = float(p_mid_arr.flat[0]) if hasattr(p_mid_arr, 'flat') else float(p_mid_arr)

            if p_mid > pressure_pa:
                h_low = h_mid
            else:
                h_high = h_mid

        return cls(h_mid, 'm')

    @classmethod
    def from_density(cls, density: Density) -> 'Altitude':
        """Create altitude from atmospheric density (density altitude).

        Determines the geometric altitude in the ISA that corresponds
        to the given density. Density altitude is critical for aircraft
        performance calculations.

        Args:
            density: Atmospheric density

        Returns:
            Corresponding density altitude

        Examples:
            >>> from evtoltools.common import Density
            >>> Altitude.from_density(Density(1.0, 'kg/m^3'))
            Altitude(1856.3, 'm')  # approximately
        """
        from ambiance import Atmosphere as AmbianceAtmosphere

        density_kg_m3 = density.in_units_of('kg/m^3')

        # Binary search for altitude
        h_low, h_high = 0.0, 80000.0
        tolerance = 0.1  # meters

        while (h_high - h_low) > tolerance:
            h_mid = (h_low + h_high) / 2
            rho_mid_arr = AmbianceAtmosphere(h_mid).density
            rho_mid = float(rho_mid_arr.flat[0]) if hasattr(rho_mid_arr, 'flat') else float(rho_mid_arr)

            if rho_mid > density_kg_m3:
                h_low = h_mid
            else:
                h_high = h_mid

        return cls(h_mid, 'm')

    def to_flight_level(self) -> float:
        """Convert altitude to flight level number.

        Returns the flight level as a number (FL100 returns 100).
        Note: Flight levels are typically only used above transition
        altitude (varies by country, often 3000-18000 ft).

        Returns:
            Flight level number (altitude in hundreds of feet)

        Examples:
            >>> Altitude(10000, 'ft').to_flight_level()
            100.0

            >>> Altitude(3048, 'm').to_flight_level()
            100.0
        """
        altitude_ft = self.in_units_of('ft')
        return altitude_ft / 100

    def is_in_troposphere(self) -> bool:
        """Check if altitude is within the troposphere.

        The troposphere extends from sea level to approximately 11 km
        (36,089 ft). This is where most eVTOL operations occur and
        where temperature decreases with altitude.

        Returns:
            True if altitude is in troposphere (below ~11 km)

        Examples:
            >>> Altitude(5000, 'ft').is_in_troposphere()
            True

            >>> Altitude(40000, 'ft').is_in_troposphere()
            False
        """
        altitude_m = self.in_units_of('m')
        if isinstance(altitude_m, np.ndarray):
            return np.all(altitude_m < self.TROPOPAUSE_M)
        return altitude_m < self.TROPOPAUSE_M

    def is_below_evtol_ceiling(self, ceiling_ft: float = None) -> bool:
        """Check if altitude is below typical eVTOL operating ceiling.

        Most eVTOL aircraft are designed for low-altitude urban operations,
        typically below 10,000 ft AGL.

        Args:
            ceiling_ft: Custom ceiling in feet. Defaults to 10,000 ft.

        Returns:
            True if altitude is below the specified ceiling

        Examples:
            >>> Altitude(1500, 'ft').is_below_evtol_ceiling()
            True

            >>> Altitude(15000, 'ft').is_below_evtol_ceiling()
            False
        """
        if ceiling_ft is None:
            ceiling_ft = self.EVTOL_TYPICAL_CEILING_FT

        altitude_ft = self.in_units_of('ft')
        if isinstance(altitude_ft, np.ndarray):
            return np.all(altitude_ft <= ceiling_ft)
        return altitude_ft <= ceiling_ft

    @property
    def agl_reference(self) -> str:
        """Get a human-readable AGL (Above Ground Level) reference string.

        Note: This assumes the altitude IS the AGL value. For MSL to AGL
        conversion, you need to know the ground elevation.

        Returns:
            Formatted string with altitude in feet AGL

        Examples:
            >>> Altitude(1500, 'ft').agl_reference
            '1500 ft AGL'
        """
        altitude_ft = self.in_units_of('ft')
        if isinstance(altitude_ft, np.ndarray):
            return f"{altitude_ft} ft AGL (array)"
        return f"{altitude_ft:.0f} ft AGL"

    def __repr__(self) -> str:
        """Return unambiguous string representation."""
        return f"Altitude({self.magnitude}, '{self.units}')"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.magnitude} {self.units}"


# Common altitude references for eVTOL operations
SEA_LEVEL = Altitude.sea_level()
