"""Sonda di torbidità SEN0189, letta dall'ADS1115 sul bus I2C 1."""

from __future__ import annotations

import time
from dataclasses import dataclass

from chlora import config
from chlora.hardware.calibration import ntu_from_voltage

# Registro di configurazione: singola lettura AIN0 rispetto a GND,
# fondo scala ±4,096 V, singola conversione, 128 SPS, comparatore spento.
_REG_CONV = 0x00
_REG_CONFIG = 0x01
_CONFIG_MSB = 0xC3
_CONFIG_LSB = 0x83
_LSB_VOLTS = 4.096 / 32768.0


@dataclass(frozen=True)
class Reading:
    ntu: float | None
    voltage: float | None
    ok: bool
    error: str | None = None


class Ads1115Turbidity:
    def __init__(self) -> None:
        self._bus = None
        self._open_error: str | None = None
        try:
            import smbus2
        except ImportError as exc:
            self._open_error = f"smbus2 assente: {exc}"
            return
        try:
            self._bus = smbus2.SMBus(config.I2C_BUS)
        except OSError as exc:
            self._open_error = f"bus I2C {config.I2C_BUS} non aperto: {exc}"

    @property
    def available(self) -> bool:
        return self._bus is not None

    def read(self) -> Reading:
        if self._bus is None:
            return Reading(None, None, False, self._open_error)
        try:
            volts_adc = self._read_ain0()
        except OSError as exc:
            return Reading(None, None, False, f"lettura ADS1115 fallita: {exc}")
        if volts_adc < 0.02:
            return Reading(None, volts_adc, False, "sonda assente o uscita a zero")
        volts = volts_adc * config.DIVIDER_GAIN
        return Reading(ntu_from_voltage(volts), volts, True, None)

    def _read_ain0(self) -> float:
        bus = self._bus
        address = config.ADS1115_ADDRESS
        bus.write_i2c_block_data(address, _REG_CONFIG, [_CONFIG_MSB, _CONFIG_LSB])
        deadline = time.monotonic() + 0.05
        while time.monotonic() < deadline:
            config_bytes = bus.read_i2c_block_data(address, _REG_CONFIG, 2)
            if config_bytes[0] & 0x80:
                break
            time.sleep(0.002)
        data = bus.read_i2c_block_data(address, _REG_CONV, 2)
        raw = (data[0] << 8) | data[1]
        if raw & 0x8000:
            raw -= 0x10000
        return raw * _LSB_VOLTS

    def close(self) -> None:
        if self._bus is not None:
            self._bus.close()
            self._bus = None
