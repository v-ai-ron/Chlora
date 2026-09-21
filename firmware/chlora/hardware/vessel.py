"""Bilancio della coltura da 10 L.

Crescita logistica di Chlorella vulgaris e prelievo quando la pompa
manda la vasca nel filtro da 5 µm. Una lettura della sonda riallinea
la torbidità.
"""

from __future__ import annotations

import random

from chlora.hardware.turbidity import Reading


class Vessel:
    def __init__(self) -> None:
        self.ntu = 32.0
        self._rng = random.Random()

    def advance(self, dt_s: float, pump_on: bool) -> None:
        hours = max(0.0, dt_s) / 3600.0
        growth = 0.85 * self.ntu * (1.0 - self.ntu / 480.0) * hours
        removal = 150.0 * hours if pump_on else 0.0
        self.ntu = min(480.0, max(12.0, self.ntu + growth - removal))

    def align(self, ntu: float) -> None:
        self.ntu = max(0.0, ntu)

    def sample(self) -> Reading:
        ntu = max(0.0, self.ntu + self._rng.uniform(-0.4, 0.4))
        return Reading(ntu, None, True, None)
