"""Avvio: python3 -m chlora, dalla cartella firmware."""

from __future__ import annotations

import logging
import threading

from chlora import config
from chlora.hardware.pump import Pump
from chlora.hardware.turbidity import Ads1115Turbidity
from chlora.hardware.vessel import Vessel
from chlora.reactor import Reactor
from chlora.server import serve

log = logging.getLogger("chlora")


def build_reactor() -> Reactor:
    log.info(
        "Sonda ADS1115 su I2C %s, indirizzo 0x%02X, relè GPIO %s",
        config.I2C_BUS,
        config.ADS1115_ADDRESS,
        config.PUMP_GPIO,
    )
    return Reactor(Ads1115Turbidity(), Pump(), Vessel())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    reactor = build_reactor()
    worker = threading.Thread(target=reactor.run, name="chlora-control", daemon=True)
    worker.start()
    try:
        serve(reactor)
    finally:
        reactor.close()
        worker.join(timeout=2)


if __name__ == "__main__":
    main()
