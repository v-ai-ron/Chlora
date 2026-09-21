# Chlora 🌿

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware](https://img.shields.io/badge/Hardware-3D__Printable-blueviolet)](https://github.com/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry__Pi-brightgreen)](https://www.raspberrypi.com/)

**Chlora** is an open-source, closed-loop domestic photobioreactor designed to purify indoor air, sequester $CO_2$, and produce oxygen. Fully replicable and 3D-printable, the system is automated via a Raspberry Pi 5 to bring industrial-grade bioreaction into the home.

The biological core of Chlora relies on the microalgae *Chlorella vulgaris*. With just 10 liters of culture, this compact system matches the daily photosynthetic efficiency of 1 to 2 medium-sized indoor trees.

---

## How It Works

1. **Turbidity:** The Pi 5 reads an optical turbidity probe over I2C. The probe is analog; an ADS1115 on bus 1 (address `0x48`) is what the Pi actually talks to.
2. **Filtration:** A relay board on GPIO 17 switches the aquarium pump. The pump starts when turbidity crosses 280 NTU and stops below 90 NTU, so the relay does not chatter. A missing sensor forces the pump off.
3. **Algae cycle:** The same reading places the culture in lag, growth, peak, harvest, or recovery.
4. **Oxygen:** The panel reports oxygen production from turbidity and the 10 L culture. The yield is in `firmware/chlora/config.py`.
5. **Screen:** The touch display, or any HDMI panel, opens a local kiosk page with cycle phase, turbidity, filter controls, and oxygen production.

The 5 µm filter sits on the harvest line. The controller reads turbidity and drives the pump relay.

---

## Hardware & Components

*   **Brain:** Raspberry Pi 5
*   **Screen:** Raspberry Pi Touch Display 2 (DSI) or an HDMI display
*   **Culture:** *Chlorella vulgaris*, 10 L
*   **Turbidity:** analog optical probe, digitized by an ADS1115 on I2C
*   **Pump board:** active-low relay module, GPIO 17, switching the pump's own supply
*   **Filter:** 5 µm mesh on the harvest line

Wiring: `electronics/README.md`. Mechanical notes: `hardware/README.md`.

---

## Run

```bash
cd firmware
python3 -m chlora
```

The panel is at `http://127.0.0.1:8080/`. On the Pi 5 the same process owns the ADS1115 and the pump relay.

Install the system packages, enable I2C, and let the service own the GPIO:

```bash
sudo apt install python3-gpiozero python3-lgpio python3-smbus2 chromium
sudo mkdir -p /opt/chlora
sudo cp -a firmware display /opt/chlora/
sudo cp /opt/chlora/firmware/chlora.service /etc/systemd/system/chlora.service
sudo systemctl enable --now chlora.service
```

Edit `User=` in the unit if the login is not `pi`. The desktop session should autologin and launch `firmware/kiosk.sh` (see `electronics/README.md`).

```bash
cd firmware
python3 -m unittest discover -s tests -v
```

---

## Repository Structure

```text
├── hardware/          # vessel, pump, filter, screen (mechanical notes)
├── electronics/       # Pi 5 pinout, ADS1115, relay board, kiosk
├── firmware/          # control loop, I2C turbidity, pump relay, tests
│   └── chlora/
│       ├── hardware/  # ADS1115 probe, pump relay, vessel balance
│       └── control/   # algae cycle, filter hysteresis, oxygen estimate
├── display/           # kiosk page served on the Pi screen
└── LICENSE            # MIT License
```
