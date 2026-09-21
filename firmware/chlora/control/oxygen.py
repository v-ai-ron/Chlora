"""Ossigeno prodotto dalla coltura.

Il peso secco arriva dalla torbidità, la produttività dal pannello
luminoso del reattore. Il totale del giorno si azzera a mezzanotte.
"""

from __future__ import annotations

from datetime import datetime

from chlora import config


class OxygenEstimate:
    def __init__(self) -> None:
        self.rate_g_h = 0.0
        self.today_g = 0.0
        self._day = None

    def integrate(self, ntu: float, dt_s: float, moment: datetime | None = None) -> None:
        moment = moment or datetime.now()
        if self._day != moment.date():
            self._day = moment.date()
            self.today_g = 0.0
        biomass_g_l = max(0.0, ntu) * config.DW_G_PER_L_PER_NTU
        self.rate_g_h = config.O2_G_PER_G_DW_PER_H * biomass_g_l * config.VOLUME_L
        self.today_g += self.rate_g_h * (max(0.0, dt_s) / 3600.0)
