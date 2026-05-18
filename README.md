# Chlora 🌿

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware](https://img.shields.io/badge/Hardware-3D__Printable-blueviolet)](https://github.com/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry__Pi-brightgreen)](https://www.raspberrypi.com/)

**Chlora** is an open-source, closed-loop domestic photobioreactor designed to purify indoor air, sequester $CO_2$, and produce oxygen. Fully replicable and 3D-printable, the system is automated via a Raspberry Pi to bring industrial-grade bioreaction into the home.

The biological core of Chlora relies on the microalgae *Chlorella vulgaris*. With just 10 liters of culture, this compact system matches the daily photosynthetic efficiency of 1 to 2 medium-sized indoor trees.

---

## How It Works

1. **Environmental Optimization:** The Raspberry Pi continuously monitors the culture using low-cost sensors (Turbidity, pH, and Temperature).
2. **Automated Harvesting:** When the algal density reaches its optimal peak, the system triggers a micro-pump to push the fluid through a 5-micron filtering network.
3. **Circular Biomass:** A pneumatic backwash system extracts a concentrated algae paste, ready to be used immediately as an organic biofertilizer for household plants.
4. **IoT Ecosystem:** A live Wi-Fi connection streams real-time data to an IoT app, sending notifications regarding filtration status and culture health.

---

## Hardware & Components

Chlora is designed to be accessible and affordable. The main stack includes:

*   **Brain:** Raspberry Pi (3/4/Zero W)
*   **Biological Agent:** *Chlorella vulgaris* culture (10L)
*   **Sensors:** 
    *   Analog Turbidity Sensor (for density tracking)
    *   pH Sensor Kit
    *   DS18B20 Temperature Sensor
*   **Actuators:** Peristaltic/Micro water pump, pneumatic valve/air pump.
*   **Filtration:** 5-micron mesh network.
*   **Chassis:** 100% 3D-printable enclosure and mechanical parts.

---

## Repository Structure

```text
├── hardware/          # .STL files, 3D models, and printing instructions
├── electronics/       # Wiring diagrams and schematic PDFs
├── firmware/          # Python scripts for Raspberry Pi and sensor reading
├── web-app/           # IoT Dashboard source code (HTML/CSS/JS or Framework)
└── LICENSE            # MIT License
