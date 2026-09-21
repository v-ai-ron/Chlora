"""Prove su ciclo, filtraggio, ossigeno e curva della sonda."""

from __future__ import annotations

import unittest
from datetime import datetime

from chlora.control.cycle import AlgaeCycle
from chlora.control.filter_loop import FilterController
from chlora.control.oxygen import OxygenEstimate
from chlora.hardware.calibration import ntu_from_voltage
from chlora.hardware.pump import Pump
from chlora.hardware.turbidity import Ads1115Turbidity
from chlora.hardware.vessel import Vessel
from chlora.reactor import Reactor


class CalibrationTest(unittest.TestCase):
    def test_clear_water_is_low_ntu(self) -> None:
        self.assertLess(ntu_from_voltage(4.2), 5.0)

    def test_curve_joins_the_saturation_floor(self) -> None:
        self.assertAlmostEqual(ntu_from_voltage(2.5), 3000.0, delta=1.0)

    def test_dense_culture_stays_in_range(self) -> None:
        ntu = ntu_from_voltage(3.5)
        self.assertGreater(ntu, 1500.0)
        self.assertLess(ntu, 2500.0)

    def test_very_dark_and_very_clear_are_clamped(self) -> None:
        self.assertEqual(ntu_from_voltage(1.0), 3000.0)
        self.assertEqual(ntu_from_voltage(5.0), 0.0)


class FilterTest(unittest.TestCase):
    def _controller(self, clock):
        return FilterController(clock=clock)

    def test_hysteresis_and_minimum_times(self) -> None:
        t = [0.0]
        filt = self._controller(lambda: t[0])
        filt.update(10.0, True)
        self.assertFalse(filt.pump_on)
        self.assertEqual(filt.reason, "below-threshold")

        filt.update(300.0, True)
        self.assertTrue(filt.pump_on)
        self.assertEqual(filt.reason, "above-threshold")

        t[0] = 10.0
        filt.update(40.0, True)
        self.assertTrue(filt.pump_on)
        self.assertEqual(filt.reason, "min-on")

        t[0] = 46.0
        filt.update(40.0, True)
        self.assertFalse(filt.pump_on)
        self.assertEqual(filt.reason, "below-off-threshold")

        t[0] = 100.0
        filt.update(300.0, True)
        self.assertFalse(filt.pump_on)
        self.assertEqual(filt.reason, "min-off")

        t[0] = 136.0
        filt.update(300.0, True)
        self.assertTrue(filt.pump_on)

    def test_sensor_fault_cuts_the_pump(self) -> None:
        t = [0.0]
        filt = self._controller(lambda: t[0])
        filt.update(300.0, True)
        t[0] = 5.0
        filt.update(300.0, False)
        self.assertFalse(filt.pump_on)
        self.assertEqual(filt.reason, "sensor-fault")

    def test_manual_overrides_the_sensor(self) -> None:
        t = [0.0]
        filt = self._controller(lambda: t[0])
        filt.set_mode("on")
        filt.update(0.0, False)
        self.assertTrue(filt.pump_on)
        self.assertEqual(filt.reason, "manual-on")
        filt.set_mode("off")
        filt.update(400.0, True)
        self.assertFalse(filt.pump_on)
        self.assertEqual(filt.reason, "manual-off")

    def test_unknown_mode_is_rejected(self) -> None:
        filt = FilterController(clock=lambda: 0.0)
        with self.assertRaises(ValueError):
            filt.set_mode("forse")


class CycleTest(unittest.TestCase):
    def test_growth_harvest_and_recovery(self) -> None:
        cycle = AlgaeCycle()
        self.assertEqual(cycle.update(20.0, False), "latenza")
        self.assertEqual(cycle.update(80.0, False), "crescita")
        self.assertEqual(cycle.update(250.0, False), "picco")
        self.assertEqual(cycle.update(300.0, True), "raccolta")
        self.assertEqual(cycle.update(100.0, False), "recupero")
        self.assertEqual(cycle.update(120.0, False), "recupero")
        self.assertEqual(cycle.update(140.0, False), "crescita")

    def test_deep_filtration_returns_to_lag(self) -> None:
        cycle = AlgaeCycle()
        cycle.update(300.0, True)
        self.assertEqual(cycle.update(20.0, False), "latenza")


class OxygenTest(unittest.TestCase):
    def test_rate_and_midnight_reset(self) -> None:
        oxygen = OxygenEstimate()
        noon = datetime(2026, 9, 21, 12, 0, 0)
        oxygen.integrate(100.0, 3600.0, noon)
        self.assertAlmostEqual(oxygen.rate_g_h, 0.456)
        self.assertAlmostEqual(oxygen.today_g, 0.456)
        oxygen.integrate(100.0, 3600.0, datetime(2026, 9, 22, 0, 5, 0))
        self.assertAlmostEqual(oxygen.today_g, 0.456)


class ReactorTest(unittest.TestCase):
    def test_tick_publishes_a_reading(self) -> None:
        reactor = Reactor(Ads1115Turbidity(), Pump(), Vessel())
        reactor.tick()
        snap = reactor.snapshot()
        self.assertTrue(snap["ready"])
        self.assertTrue(snap["sensor_ok"])
        self.assertGreater(snap["turbidity_ntu"], 0.0)
        self.assertGreater(snap["oxygen_g_h"], 0.0)
        self.assertIn(snap["phase"], snap["phases"])
        reactor.close()


if __name__ == "__main__":
    unittest.main()
