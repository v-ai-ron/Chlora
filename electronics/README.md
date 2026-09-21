# Elettronica

Quadro del Raspberry Pi 5, dello schermo, della sonda SEN0189 e della scheda relè della pompa.

La SEN0189 esce in tensione. L'ADS1115 sul bus I2C 1, indirizzo `0x48`, la legge per il Pi 5.

## Pin del Raspberry Pi 5

| Segnale | BCM | Pin fisico |
| --- | --- | --- |
| 3,3 V |  | 1 |
| 5 V |  | 2 |
| SDA | 2 | 3 |
| SCL | 3 | 5 |
| GND |  | 6 e 9 |
| Relè IN | 17 | 11 |

In Raspberry Pi OS: Interfacce, I2C, abilita. Il file è `/boot/firmware/config.txt`.

Per tenere il relè spento già al boot (i moduli economici sono attivi bassi, e un pin basso farebbe scattare la pompa):

```
gpio=17=op,dh
dtparam=i2c_arm=on
```

`dh` porta GPIO17 alto come uscita. Con un relè attivo basso, alto significa pompa ferma.

## ADS1115 e sonda

- VDD dell'ADS1115 al 3,3 V del Pi, GND in comune, SDA e SCL sul bus, ADDR a GND (`0x48`).
- La sonda resta alimentata a 5 V, come da scheda. La sua uscita AO, a 5 V, passa da un partitore prima di A0: 10 kΩ tra AO e il nodo A0, 20 kΩ tra il nodo A0 e GND. Il firmware rimette in scala con `DIVIDER_GAIN = 1.5`.
- A1, A2 e A3 restano aperti.
- Se la scheda sonda esce già in 0-3,3 V, AO va diretto su A0 e `DIVIDER_GAIN` diventa `1.0`.

La conversione usata dal controller è la caratteristica della SEN0189 a 5 V per questa vasca. I coefficienti stanno in `firmware/chlora/hardware/calibration.py`.

Controllo rapido, a Pi acceso e cablato:

```
i2cdetect -y 1
```

Deve comparire `48`.

## Scheda relè e pompa

Il GPIO comanda solo l'ingresso della scheda. Il contatto del relè sta in serie all'alimentazione della pompa, su un alimentatore suo (12 V continui, oppure la rete se la pompa è a 230 V). COM e NO chiudono quel circuito. NC resta libero. La massa di potenza della pompa torna all'alimentatore della pompa.

Collegamento logico del modulo a un canale, attivo basso:

- IN su GPIO17 (pin 11)
- VCC sul 5 V (pin 2), se la scheda ha un solo VCC e il ponticello JD-VCC inserito
- GND sul GND del Pi (pin 9)

Se la scheda separa VCC e JD-VCC, togli il ponticello: VCC al 3,3 V del Pi, JD-VCC al 5 V, GND in comune. L'optoisolatore lavora meglio così.

`PUMP_ACTIVE_HIGH` in `firmware/chlora/config.py` è `False`. `on()` nel codice porta il pin basso e il relè chiude.

La rete a 230 V, se la pompa è di quel tipo, resta sul contatto del relè e sull'alimentatore della pompa. Il pin del Pi vede solo il segnale di comando del modulo.

## Schermo

Schermo previsto: Raspberry Pi Touch Display 2 sul connettore DSI del Pi 5, oppure un monitor HDMI. Il pannello è una pagina locale a tutto schermo, 1280×720 oppure 800×480.

Il servizio `chlora.service` alza il controller. Poi la sessione desktop (login automatico, labwc) lancia `firmware/kiosk.sh`, che aspetta `http://127.0.0.1:8080/` e apre Chromium in kiosk.

In `~/.config/labwc/autostart`:

```
/opt/chlora/firmware/kiosk.sh >/tmp/chlora-kiosk.log 2>&1 &
```
