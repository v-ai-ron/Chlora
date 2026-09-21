"""Accensione della pompa con isteresi e tempi minimi sul relè.

In automatico la pompa parte sopra HARVEST_ON_NTU e si ferma sotto
HARVEST_OFF_NTU. Un guasto sonda spegne subito. Il manuale ignora
la torbidità, e al ritorno in automatico vale ancora il tempo minimo
così il relè non batte.
"""

from __future__ import annotations

import time

from chlora import config


class FilterController:
    def __init__(self, clock=time.monotonic) -> None:
        self._clock = clock
        self.mode = "auto"
        self.pump_on = False
        self.reason = "below-threshold"
        now = self._clock()
        self._changed_at = now
        self._hold_until = now

    def set_mode(self, mode: str) -> None:
        if mode not in {"auto", "on", "off"}:
            raise ValueError(mode)
        self.mode = mode

    def age_s(self, now: float | None = None) -> float:
        moment = self._clock() if now is None else now
        return max(0.0, moment - self._changed_at)

    def update(self, ntu: float, sensor_ok: bool) -> None:
        now = self._clock()
        if self.mode == "on":
            self._force(True, "manual-on", now)
            return
        if self.mode == "off":
            self._force(False, "manual-off", now)
            return
        if not sensor_ok:
            self._force(False, "sensor-fault", now)
            return

        if self.pump_on:
            if ntu > config.HARVEST_OFF_NTU:
                self.reason = "above-off-threshold"
            elif now < self._hold_until:
                self.reason = "min-on"
            else:
                self._transition(False, "below-off-threshold", now, config.MIN_PUMP_OFF_S)
        elif ntu < config.HARVEST_ON_NTU:
            self.reason = "below-threshold"
        elif now < self._hold_until:
            self.reason = "min-off"
        else:
            self._transition(True, "above-threshold", now, config.MIN_PUMP_ON_S)

    def _force(self, on: bool, reason: str, now: float) -> None:
        if on != self.pump_on:
            self.pump_on = on
            self._changed_at = now
            hold = config.MIN_PUMP_ON_S if on else config.MIN_PUMP_OFF_S
            self._hold_until = now + hold
        self.reason = reason

    def _transition(self, on: bool, reason: str, now: float, hold_s: float) -> None:
        self.pump_on = on
        self.reason = reason
        self._changed_at = now
        self._hold_until = now + hold_s
