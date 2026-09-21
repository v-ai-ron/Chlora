"""Relè della pompa di filtraggio.

Il GPIO 17 comanda l'ingresso della scheda relè. Il contatto del relè
interrompe l'alimentazione della pompa, su un alimentatore separato.
Il pin parte spento e viene richiuso all'uscita del processo.
"""

from __future__ import annotations

import logging
from pathlib import Path

from chlora import config

log = logging.getLogger(__name__)


def _on_raspberry_pi() -> bool:
    model = Path("/proc/device-tree/model")
    if not model.is_file():
        return False
    text = model.read_bytes().replace(b"\x00", b"").decode(errors="replace")
    return text.startswith("Raspberry Pi")


class Pump:
    def __init__(self) -> None:
        self.is_on = False
        self._relay = None
        try:
            from gpiozero import OutputDevice
            from gpiozero.pins.lgpio import LGPIOFactory
            import gpiozero

            gpiozero.Device.pin_factory = LGPIOFactory()
            self._relay = OutputDevice(
                config.PUMP_GPIO,
                active_high=config.PUMP_ACTIVE_HIGH,
                initial_value=False,
            )
        except Exception as exc:
            if _on_raspberry_pi():
                log.warning("Relè su GPIO %s non aperto: %s", config.PUMP_GPIO, exc)

    def set(self, is_on: bool) -> None:
        if self._relay is not None:
            if is_on:
                self._relay.on()
            else:
                self._relay.off()
        self.is_on = is_on

    def close(self) -> None:
        self.set(False)
        if self._relay is not None:
            self._relay.close()
            self._relay = None
