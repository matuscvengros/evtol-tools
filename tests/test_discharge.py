"""Tests for Battery discharge and charge models.

This module provides tests for the discharge model classes including
AnalyticalDischargeModel, LookupTableDischargeModel, and SimpleChargeModel.
"""

import numpy as np
import pytest

from evtoltools.common import Resistance, Temperature, Voltage
from evtoltools.components.battery import (
    AnalyticalDischargeModel,
    LookupTableDischargeModel,
    SimpleChargeModel,
    load_discharge_model,
)


class TestAnalyticalDischargeModel:
    """Tests for AnalyticalDischargeModel."""

    @pytest.fixture
    def model(self):
        """Create standard analytical model."""
        return AnalyticalDischargeModel(
            v_max=Voltage(4.2, 'V'),
            v_min=Voltage(2.8, 'V'),
            v_nominal=Voltage(3.7, 'V'),
            internal_resistance=Resistance(30, 'mohm'),
            capacity_ah=5.0,
        )

    def test_voltage_at_full_soc_no_load(self, model):
        """Voltage at 100% SoC with 0 C-rate should be near max."""
        v = model.get_voltage(soc=1.0, c_rate=0.0)
        assert v.in_units_of('V') == pytest.approx(4.2, abs=0.01)

    def test_voltage_at_empty_soc_no_load(self, model):
        """Voltage at 0% SoC with 0 C-rate should be min."""
        v = model.get_voltage(soc=0.0, c_rate=0.0)
        assert v.in_units_of('V') == pytest.approx(2.8, abs=0.01)

    def test_voltage_decreases_with_load(self, model):
        """Voltage should decrease under load (I*R drop)."""
        v_no_load = model.get_voltage(soc=0.5, c_rate=0.0)
        v_load = model.get_voltage(soc=0.5, c_rate=1.0)
        assert v_load < v_no_load

    def test_voltage_ir_drop_calculation(self, model):
        """Verify I*R voltage drop."""
        # At 1C on 5Ah = 5A
        # R = 30 mohm = 0.03 ohm
        # I*R = 5 * 0.03 = 0.15V drop
        v_no_load = model.get_voltage(soc=0.5, c_rate=0.0)
        v_1c = model.get_voltage(soc=0.5, c_rate=1.0)
        drop = v_no_load.in_units_of('V') - v_1c.in_units_of('V')
        assert drop == pytest.approx(0.15, abs=0.01)

    def test_voltage_clamped_to_min(self, model):
        """Voltage should not go below minimum."""
        # At very high C-rate, voltage drop could exceed OCV
        v = model.get_voltage(soc=0.1, c_rate=10.0)
        assert v.in_units_of('V') >= 2.8

    def test_get_resistance_returns_value(self, model):
        """get_resistance should return the internal resistance."""
        r = model.get_resistance(soc=0.5)
        assert r is not None
        assert r.in_units_of('mohm') == pytest.approx(30)

    def test_array_soc_input(self, model):
        """Model should handle array SoC input."""
        soc_array = np.array([0.2, 0.5, 0.8])
        v = model.get_voltage(soc=soc_array, c_rate=1.0)
        assert len(v.magnitude) == 3
        # Voltage should increase with SoC
        assert v.magnitude[2] > v.magnitude[1] > v.magnitude[0]


class TestLookupTableDischargeModel:
    """Tests for LookupTableDischargeModel."""

    @pytest.fixture
    def model(self):
        """Create lookup table model with simple test data."""
        soc_points = np.array([0.0, 0.5, 1.0])
        c_rate_points = np.array([0.1, 1.0, 3.0])

        # Voltage decreases with C-rate, increases with SoC
        voltage_data = np.array([
            [2.9, 2.8, 2.7],  # SoC = 0.0
            [3.6, 3.5, 3.4],  # SoC = 0.5
            [4.2, 4.1, 4.0],  # SoC = 1.0
        ])

        return LookupTableDischargeModel(
            soc_points=soc_points,
            c_rate_points=c_rate_points,
            voltage_data=voltage_data,
            v_min=Voltage(2.7, 'V'),
        )

    def test_exact_lookup(self, model):
        """Voltage at exact table point."""
        v = model.get_voltage(soc=0.5, c_rate=1.0)
        assert v.in_units_of('V') == pytest.approx(3.5, abs=0.01)

    def test_interpolation_soc(self, model):
        """Voltage interpolated between SoC points."""
        v = model.get_voltage(soc=0.25, c_rate=1.0)
        # Should be between 2.8 and 3.5
        assert 2.8 < v.in_units_of('V') < 3.5

    def test_interpolation_c_rate(self, model):
        """Voltage interpolated between C-rate points."""
        v = model.get_voltage(soc=0.5, c_rate=2.0)
        # Should be between 3.4 and 3.5
        assert 3.4 < v.in_units_of('V') < 3.5

    def test_clamping_soc_low(self, model):
        """SoC below table minimum should clamp."""
        v = model.get_voltage(soc=-0.1, c_rate=1.0)
        # Should clamp to SoC = 0.0
        assert v.in_units_of('V') == pytest.approx(2.8, abs=0.1)

    def test_clamping_soc_high(self, model):
        """SoC above table maximum should clamp."""
        v = model.get_voltage(soc=1.5, c_rate=1.0)
        # Should clamp to SoC = 1.0
        assert v.in_units_of('V') == pytest.approx(4.1, abs=0.1)

    def test_clamping_c_rate_high(self, model):
        """C-rate above table maximum should clamp."""
        v = model.get_voltage(soc=0.5, c_rate=10.0)
        # Should clamp to C-rate = 3.0
        assert v.in_units_of('V') == pytest.approx(3.4, abs=0.1)

    def test_v_min_clamping(self, model):
        """Voltage should not go below v_min."""
        v = model.get_voltage(soc=0.0, c_rate=3.0)
        assert v.in_units_of('V') >= 2.7


class TestSimpleChargeModel:
    """Tests for SimpleChargeModel."""

    @pytest.fixture
    def model(self):
        """Create standard charge model."""
        return SimpleChargeModel(
            cc_cv_transition_soc=0.8,
            cv_taper_factor=3.0,
            base_efficiency=0.95,
        )

    def test_cc_phase_full_current(self, model):
        """In CC phase, should return max C-rate."""
        c_rate = model.get_charge_current(soc=0.3, max_c_rate=1.0)
        assert c_rate == pytest.approx(1.0)

    def test_cv_phase_tapered_current(self, model):
        """In CV phase, current should taper."""
        c_rate = model.get_charge_current(soc=0.9, max_c_rate=1.0)
        assert c_rate < 1.0
        assert c_rate > 0.0

    def test_current_decreases_in_cv_phase(self, model):
        """Current should decrease as SoC increases in CV phase."""
        c_rate_80 = model.get_charge_current(soc=0.8, max_c_rate=1.0)
        c_rate_90 = model.get_charge_current(soc=0.9, max_c_rate=1.0)
        c_rate_95 = model.get_charge_current(soc=0.95, max_c_rate=1.0)
        assert c_rate_80 > c_rate_90 > c_rate_95

    def test_efficiency_below_one(self, model):
        """Efficiency should always be below 1.0."""
        eff = model.get_charge_efficiency(soc=0.5, c_rate=1.0)
        assert 0 < eff < 1.0

    def test_efficiency_decreases_with_c_rate(self, model):
        """Higher C-rate should have lower efficiency."""
        eff_low = model.get_charge_efficiency(soc=0.5, c_rate=0.5)
        eff_high = model.get_charge_efficiency(soc=0.5, c_rate=2.0)
        assert eff_low > eff_high

    def test_efficiency_decreases_with_soc(self, model):
        """Higher SoC should have slightly lower efficiency."""
        eff_low_soc = model.get_charge_efficiency(soc=0.2, c_rate=1.0)
        eff_high_soc = model.get_charge_efficiency(soc=0.9, c_rate=1.0)
        assert eff_low_soc > eff_high_soc

    def test_time_to_charge_positive(self, model):
        """Time to charge should be positive."""
        time = model.time_to_charge(
            start_soc=0.2, end_soc=0.8, max_c_rate=1.0
        )
        assert time > 0

    def test_time_to_charge_zero_when_no_change(self, model):
        """Time should be zero if start == end."""
        time = model.time_to_charge(
            start_soc=0.5, end_soc=0.5, max_c_rate=1.0
        )
        assert time == 0

    def test_time_to_charge_increases_with_soc_range(self, model):
        """Larger SoC range should take longer."""
        time_short = model.time_to_charge(
            start_soc=0.2, end_soc=0.5, max_c_rate=1.0
        )
        time_long = model.time_to_charge(
            start_soc=0.2, end_soc=0.9, max_c_rate=1.0
        )
        assert time_long > time_short


class TestLoadDischargeModel:
    """Tests for load_discharge_model convenience function."""

    def test_load_lithium_ion(self):
        """Load model for lithium_ion chemistry."""
        model = load_discharge_model('lithium_ion')
        assert isinstance(model, AnalyticalDischargeModel)
        assert model.v_max.in_units_of('V') == pytest.approx(4.2)

    def test_load_lipo(self):
        """Load model for lipo chemistry."""
        model = load_discharge_model('lipo')
        assert isinstance(model, AnalyticalDischargeModel)
        # LiPo has higher min voltage
        assert model.v_min.in_units_of('V') == pytest.approx(3.2)

    def test_load_lifepo4(self):
        """Load model for lifepo4 chemistry."""
        model = load_discharge_model('lifepo4')
        assert isinstance(model, AnalyticalDischargeModel)
        # LiFePO4 has lower nominal voltage
        assert model.v_nominal.in_units_of('V') == pytest.approx(3.2)

    def test_load_nmc(self):
        """Load model for nmc chemistry."""
        model = load_discharge_model('nmc')
        assert isinstance(model, AnalyticalDischargeModel)

    def test_load_unknown_raises(self):
        """Unknown chemistry should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown chemistry"):
            load_discharge_model('unknown_chemistry')

    def test_case_insensitive(self):
        """Chemistry name should be case-insensitive."""
        model = load_discharge_model('LITHIUM_ION')
        assert isinstance(model, AnalyticalDischargeModel)


class TestDischargeModelVoltageDecrease:
    """Tests verifying voltage behavior with SoC and C-rate."""

    @pytest.fixture
    def model(self):
        return AnalyticalDischargeModel(
            v_max=Voltage(4.2, 'V'),
            v_min=Voltage(2.8, 'V'),
            v_nominal=Voltage(3.7, 'V'),
            internal_resistance=Resistance(30, 'mohm'),
            capacity_ah=5.0,
        )

    def test_voltage_decreases_with_decreasing_soc(self, model):
        """Voltage should decrease as SoC decreases."""
        v_high_soc = model.get_voltage(soc=0.9, c_rate=1.0)
        v_low_soc = model.get_voltage(soc=0.1, c_rate=1.0)
        assert v_high_soc > v_low_soc

    def test_voltage_decreases_with_increasing_c_rate(self, model):
        """Voltage should decrease as C-rate increases."""
        v_low_c = model.get_voltage(soc=0.5, c_rate=0.5)
        v_high_c = model.get_voltage(soc=0.5, c_rate=3.0)
        assert v_low_c > v_high_c
