"""Tests for simple components: Avionics, Structure, Payload, and base classes."""

import pytest

from evtoltools.common import Mass, Length
from evtoltools.components import Avionics, Structure, Payload
from evtoltools.components.base import BaseComponent, ComponentResult


class TestComponentResult:
    """Tests for ComponentResult container."""

    def test_basic_creation(self):
        result = ComponentResult(value="test")
        assert result.value == "test"
        assert result.warnings == []
        assert result.metadata == {}

    def test_with_warnings(self):
        result = ComponentResult(
            value=42,
            warnings=["Warning 1", "Warning 2"]
        )
        assert result.value == 42
        assert len(result.warnings) == 2
        assert "Warning 1" in result.warnings

    def test_with_metadata(self):
        result = ComponentResult(
            value="component",
            metadata={"calculated": True, "iterations": 5}
        )
        assert result.metadata["calculated"] is True
        assert result.metadata["iterations"] == 5


class TestAvionicsConstruction:
    """Tests for Avionics component construction."""

    def test_direct_mass(self):
        avionics = Avionics(_mass=Mass(50, 'kg'))
        assert avionics.mass.magnitude == 50
        assert avionics.mass.units == 'kilogram'

    def test_from_weight_fraction(self):
        empty_weight = Mass(1500, 'kg')
        avionics = Avionics.from_weight_fraction(empty_weight, 0.05)
        assert abs(avionics.mass.magnitude - 75) < 0.001

    def test_from_weight_fraction_zero(self):
        empty_weight = Mass(1500, 'kg')
        avionics = Avionics.from_weight_fraction(empty_weight, 0.0)
        assert avionics.mass.magnitude == 0

    def test_from_weight_fraction_full(self):
        empty_weight = Mass(1500, 'kg')
        avionics = Avionics.from_weight_fraction(empty_weight, 1.0)
        assert abs(avionics.mass.magnitude - 1500) < 0.001

    def test_invalid_fraction_negative(self):
        empty_weight = Mass(1500, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Avionics.from_weight_fraction(empty_weight, -0.1)

    def test_invalid_fraction_over_one(self):
        empty_weight = Mass(1500, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Avionics.from_weight_fraction(empty_weight, 1.5)


class TestAvionicsProperties:
    """Tests for Avionics properties."""

    def test_component_type(self):
        avionics = Avionics(_mass=Mass(50, 'kg'))
        assert avionics.component_type == 'avionics'

    def test_calculate_mass_standalone(self):
        empty_weight = Mass(2000, 'kg')
        mass = Avionics.calculate_mass(empty_weight, 0.04)
        assert abs(mass.magnitude - 80) < 0.001

    def test_calculate_mass_invalid_fraction(self):
        empty_weight = Mass(2000, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Avionics.calculate_mass(empty_weight, 2.0)

    def test_repr(self):
        avionics = Avionics(_mass=Mass(50, 'kg'))
        repr_str = repr(avionics)
        assert 'Avionics' in repr_str
        assert 'mass' in repr_str


class TestStructureConstruction:
    """Tests for Structure component construction."""

    def test_direct_mass(self):
        structure = Structure(_mass=Mass(500, 'kg'))
        assert structure.mass.magnitude == 500
        assert structure.mass.units == 'kilogram'

    def test_from_weight_fraction(self):
        empty_weight = Mass(1500, 'kg')
        structure = Structure.from_weight_fraction(empty_weight, 0.30)
        assert abs(structure.mass.magnitude - 450) < 0.001

    def test_from_weight_fraction_typical(self):
        # Typical structure fraction for eVTOL: 25-35%
        empty_weight = Mass(2000, 'kg')
        structure = Structure.from_weight_fraction(empty_weight, 0.28)
        assert abs(structure.mass.magnitude - 560) < 0.001

    def test_invalid_fraction_negative(self):
        empty_weight = Mass(1500, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Structure.from_weight_fraction(empty_weight, -0.05)

    def test_invalid_fraction_over_one(self):
        empty_weight = Mass(1500, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Structure.from_weight_fraction(empty_weight, 1.2)


class TestStructureProperties:
    """Tests for Structure properties."""

    def test_component_type(self):
        structure = Structure(_mass=Mass(500, 'kg'))
        assert structure.component_type == 'structure'

    def test_calculate_mass_standalone(self):
        empty_weight = Mass(1800, 'kg')
        mass = Structure.calculate_mass(empty_weight, 0.32)
        assert abs(mass.magnitude - 576) < 0.001

    def test_calculate_mass_invalid_fraction(self):
        empty_weight = Mass(1800, 'kg')
        with pytest.raises(ValueError, match="between 0 and 1"):
            Structure.calculate_mass(empty_weight, -0.1)


class TestPayloadConstruction:
    """Tests for Payload component construction."""

    def test_mass_only(self):
        payload = Payload(_mass=Mass(200, 'kg'))
        assert payload.mass.magnitude == 200
        assert payload.mass.units == 'kilogram'

    def test_with_description(self):
        payload = Payload(
            _mass=Mass(320, 'kg'),
            description='4 passengers @ 80kg'
        )
        assert payload.mass.magnitude == 320
        assert payload.description == '4 passengers @ 80kg'

    def test_with_position(self):
        payload = Payload(
            _mass=Mass(100, 'kg'),
            x_position=Length(1.5, 'm'),
            y_position=Length(0, 'm'),
            z_position=Length(0.5, 'm')
        )
        assert payload.x_position.magnitude == 1.5
        assert payload.y_position.magnitude == 0
        assert payload.z_position.magnitude == 0.5

    def test_with_partial_position(self):
        payload = Payload(
            _mass=Mass(50, 'kg'),
            x_position=Length(2.0, 'm')
        )
        assert payload.x_position.magnitude == 2.0
        assert payload.y_position is None
        assert payload.z_position is None


class TestPayloadProperties:
    """Tests for Payload properties."""

    def test_component_type(self):
        payload = Payload(_mass=Mass(200, 'kg'))
        assert payload.component_type == 'payload'

    def test_has_position_true(self):
        payload = Payload(
            _mass=Mass(100, 'kg'),
            x_position=Length(1.0, 'm')
        )
        assert payload.has_position is True

    def test_has_position_false(self):
        payload = Payload(_mass=Mass(100, 'kg'))
        assert payload.has_position is False

    def test_repr_without_description(self):
        payload = Payload(_mass=Mass(200, 'kg'))
        repr_str = repr(payload)
        assert 'Payload' in repr_str
        assert 'mass' in repr_str

    def test_repr_with_description(self):
        payload = Payload(
            _mass=Mass(160, 'kg'),
            description='2 passengers'
        )
        repr_str = repr(payload)
        assert 'Payload' in repr_str
        assert '2 passengers' in repr_str


class TestBaseComponentInterface:
    """Tests verifying BaseComponent interface compliance."""

    def test_avionics_is_base_component(self):
        avionics = Avionics(_mass=Mass(50, 'kg'))
        assert isinstance(avionics, BaseComponent)

    def test_structure_is_base_component(self):
        structure = Structure(_mass=Mass(500, 'kg'))
        assert isinstance(structure, BaseComponent)

    def test_payload_is_base_component(self):
        payload = Payload(_mass=Mass(200, 'kg'))
        assert isinstance(payload, BaseComponent)


class TestUnitConversions:
    """Tests for unit handling in components."""

    def test_avionics_with_lbs(self):
        avionics = Avionics(_mass=Mass(100, 'lbs'))
        kg_mass = avionics.mass.to('kg')
        assert abs(kg_mass.magnitude - 45.36) < 0.1

    def test_structure_from_lbs_fraction(self):
        empty_weight = Mass(3000, 'lbs')
        structure = Structure.from_weight_fraction(empty_weight, 0.30)
        assert abs(structure.mass.magnitude - 900) < 0.001

    def test_payload_position_conversion(self):
        payload = Payload(
            _mass=Mass(100, 'kg'),
            x_position=Length(5, 'ft')
        )
        x_meters = payload.x_position.to('m')
        assert abs(x_meters.magnitude - 1.524) < 0.01

