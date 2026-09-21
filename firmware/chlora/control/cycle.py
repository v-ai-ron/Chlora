"""A che punto è la coltura, in base a densità e stato della pompa."""

from __future__ import annotations

from chlora import config


class AlgaeCycle:
    def __init__(self) -> None:
        self.phase = "latenza"
        self._recover_min: float | None = None

    def update(self, ntu: float, pump_on: bool) -> str:
        if pump_on:
            self.phase = "raccolta"
            self._recover_min = None
            return self.phase

        if self.phase == "raccolta":
            if ntu < config.LAG_NTU:
                self.phase = "latenza"
                self._recover_min = None
            else:
                self.phase = "recupero"
                self._recover_min = ntu
            return self.phase

        if self.phase == "recupero":
            assert self._recover_min is not None
            self._recover_min = min(self._recover_min, ntu)
            grown = ntu >= self._recover_min + config.RECOVER_RISE_NTU
            if grown and ntu >= config.LAG_NTU:
                self.phase = "picco" if ntu >= config.PEAK_NTU else "crescita"
                self._recover_min = None
            return self.phase

        if ntu < config.LAG_NTU:
            self.phase = "latenza"
        elif ntu < config.PEAK_NTU:
            self.phase = "crescita"
        else:
            self.phase = "picco"
        return self.phase
