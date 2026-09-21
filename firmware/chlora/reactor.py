"""Ciclo di controllo: legge, decide, comanda la pompa, pubblica lo stato."""

from __future__ import annotations

import copy
import logging
import threading
import time

from chlora import config
from chlora.control.cycle import AlgaeCycle
from chlora.control.filter_loop import FilterController
from chlora.control.oxygen import OxygenEstimate

log = logging.getLogger(__name__)


class Reactor:
    def __init__(self, probe, pump, vessel) -> None:
        self._probe = probe
        self._pump = pump
        self._vessel = vessel
        self.filter = FilterController()
        self.cycle = AlgaeCycle()
        self.oxygen = OxygenEstimate()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._snapshot: dict = {}
        self._last: float | None = None
        self._history: list[float] = []
        self._ntu: float | None = None
        self._voltage: float | None = None
        self._logged_phase: str | None = None
        self._logged_pump: bool | None = None

    def set_pump_mode(self, mode: str) -> dict:
        with self._lock:
            self.filter.set_mode(mode)
            if self._snapshot:
                snap = dict(self._snapshot)
                snap["pump_mode"] = self.filter.mode
                self._snapshot = snap
            return self._copy_snapshot()

    def snapshot(self) -> dict:
        with self._lock:
            return self._copy_snapshot()

    def _copy_snapshot(self) -> dict:
        if not self._snapshot:
            return {"ready": False}
        return copy.deepcopy(self._snapshot)

    def tick(self) -> None:
        now = time.monotonic()
        if self._last is None:
            dt = config.SAMPLE_PERIOD_S
        else:
            dt = min(max(now - self._last, 0.0), 30.0)
        self._last = now

        with self._lock:
            pump_on = self.filter.pump_on
        self._vessel.advance(dt, pump_on)
        reading = self._probe.read()
        if reading.ok and reading.ntu is not None:
            self._vessel.align(reading.ntu)
            ntu = reading.ntu
            voltage = reading.voltage
            sensor_ok = True
            error = None
        elif self._probe.available:
            ntu = None
            voltage = reading.voltage
            sensor_ok = False
            error = reading.error
        else:
            sample = self._vessel.sample()
            ntu = sample.ntu
            voltage = None
            sensor_ok = True
            error = None

        pump_error = None
        with self._lock:
            if sensor_ok and ntu is not None:
                self._ntu = ntu
                self._voltage = voltage
                self.filter.update(ntu, True)
                self.cycle.update(ntu, self.filter.pump_on)
                self.oxygen.integrate(ntu, dt)
                self._history.append(round(ntu, 2))
                del self._history[:-config.HISTORY]
            else:
                self.filter.update(self._ntu or 0.0, False)
            desired = self.filter.pump_on

        try:
            self._pump.set(desired)
        except Exception as exc:  # il pannello deve restare vivo anche se il GPIO fallisce
            pump_error = str(exc)
            log.exception("Comando pompa non riuscito")

        with self._lock:
            phase_now = self.cycle.phase
            pump_now = self._pump.is_on
            if phase_now != self._logged_phase or pump_now != self._logged_pump:
                log.info(
                    "fase=%s pompa=%s motivo=%s",
                    phase_now,
                    "on" if pump_now else "off",
                    self.filter.reason,
                )
                self._logged_phase = phase_now
                self._logged_pump = pump_now
            self._snapshot = {
                "ready": True,
                "sensor_ok": sensor_ok,
                "sensor_error": error,
                "turbidity_ntu": None if self._ntu is None else round(self._ntu, 2),
                "turbidity_v": None if self._voltage is None else round(self._voltage, 3),
                "phase": phase_now,
                "phases": list(config.PHASES),
                "pump_on": pump_now,
                "pump_mode": self.filter.mode,
                "filter_reason": self.filter.reason,
                "state_age_s": round(self.filter.age_s(), 1),
                "pump_error": pump_error,
                "thresholds": {
                    "on": config.HARVEST_ON_NTU,
                    "off": config.HARVEST_OFF_NTU,
                },
                "oxygen_g_h": round(self.oxygen.rate_g_h, 4),
                "oxygen_today_g": round(self.oxygen.today_g, 4),
                "volume_l": config.VOLUME_L,
                "history": list(self._history),
            }

    def run(self) -> None:
        while not self._stop.is_set():
            started = time.monotonic()
            try:
                self.tick()
            except Exception:
                log.exception("Tick di controllo fallito")
            elapsed = time.monotonic() - started
            self._stop.wait(max(0.0, config.SAMPLE_PERIOD_S - elapsed))

    def close(self) -> None:
        self._stop.set()
        try:
            self._pump.close()
        except Exception:
            log.exception("Spegnimento pompa non riuscito")
        self._probe.close()
