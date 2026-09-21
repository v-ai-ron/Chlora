"""Curva tensione-NTU della SEN0189 a 5 V, in questa vasca.

Sopra 2,5 V vale la caratteristica del modulo. Sotto, la lettura satura
a 3000 NTU. Acqua limpida: tensione alta, NTU bassi. Coltura densa: tensione bassa.
"""

from __future__ import annotations


def ntu_from_voltage(voltage: float) -> float:
    if voltage < 2.5:
        return 3000.0
    ntu = -1120.4 * voltage * voltage + 5742.3 * voltage - 4352.9
    if ntu < 0.0:
        return 0.0
    if ntu > 3000.0:
        return 3000.0
    return ntu
