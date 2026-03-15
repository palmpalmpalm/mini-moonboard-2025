# moonboard
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


This project contains software and informations to build a home climbing wall with LED support compatible with the popular moonboard. 
This fork has been done while building my home climbing wall. 

***WIP: Project done. Next step: stabilize the code. ***


![Image of the Wall](doc/front.png)
![LEDs](doc/led.png)

The [moonboard](https://www.moonboard.com/) smartphone app is build to work with the [moonboard led system](https://moonclimbing.com/moonboard-led-system.html) using bluetooth low energy.
In this project we emulate the behaviour of the box using a rasperry pi and addressable LED stripes. 


# Requirements

Besides the tools, time and money (the climbing holds are the most expensive component) you will need:

- Rapi W Zero with 8GB SD Card - powered over GPIO
- 4x LED Strips: 50x WS2811 LED, 5V, 12mm - custom cable length of 23cm (alternatively 3x 4x LED Strips with standard length of 7cm, use mooboard/led/create_nth_led_layout.py to create custom spacing for LED´s)
- Power supply [meanwell mdr-60-5](https://www.meanwell.com/webapp/product/search.aspx?prod=MDR-60) - (~60mA * 50 * 4 = 12A ==> 60 W for 5V)
- Suitable Case (i.e. TEKO)

# Build Instructions

- [How to Build a Home Climbing Wall](doc/BUILD-WALL.md)
- [How to Build the LED System](doc/BUILD-LEDSYSTEM.md)
- [Software Description](doc/OVERVIEW-SOFTWARE.md)

## Example boards
Free standing foldaway version of moonboard. Moonboard with 150mm kicker and total height of 2900mm, some alteration for 2016 hold setup needs to be done since one hold cannot fit in shortened top panel.

![MB folded away](doc/MB-front-folded.jpg)
![MB unfolded ready to train](doc/MB-front-unfolded.jpg)



## Troubleshooting
- In case of bluetooth connection problems: make sure to have paired your phone with the raspi once.

## Tested setups
- Raspi W Zero with iPhone 5, 8, X, 11 (iOS >= 14)

---

# Notes from a Mini Moonboard 2025 Build

> These are notes from me (the forker/maintainer) after setting up this project for a **Mini Moonboard 2025** (11 columns x 12 rows, 132 holds). I used the same hardware described above. If you're building a standard Moonboard, the process is identical—just use the original LED mapping file instead of the mini one.

## What was changed

### BLE Service (`ble/moonboard_ble_dbus_service.py`)
The BLE service was rewritten to use BlueZ's D-Bus API for both GATT and advertising (instead of raw `hcitool` commands). This fixes:
- **Multi-device support** — advertising automatically restarts after a device disconnects, so the next phone can connect without rebooting.
- **Reliable GATT communication** — incoming write data from the Moonboard app is processed directly via the GATT characteristic instead of sniffing `btmon`.
- **MQTT integration** — the BLE service publishes decoded problems to MQTT (`mosquitto`) on `localhost`, which the LED service subscribes to.
- **Mini board forced** — the `process_rx` method forces the "M" (Mini) flag so the protocol always decodes for a 12-row board. Remove this if you're using a standard 18-row Moonboard.

### LED Service (`led/moonboard_led_service.py`)
- **Startup animation** — on boot, an RGB running light sweeps across all LEDs (red → green → blue) to indicate the system is ready.
- **Graceful error handling** — if the app sends a hold position that doesn't exist in the mapping (e.g., `C18` on a mini board), it logs a warning instead of crashing.
- **MQTT hostname** — changed from `raspi-moonboard` to `localhost`.

### LED Mapping (`led/led_mapping_mini.json`)
A new mapping file for the Mini Moonboard: 11 columns (A–K) x 12 rows, 132 LEDs total, wired in a serpentine pattern (column A goes up, column B goes down, etc.).

### System Configuration (on the Pi)
- **D-Bus policy** (`/etc/dbus-1/system.d/com.moonboard.conf`) — grants the BLE service permission to register on D-Bus.
- **Bluetooth name** (`/etc/bluetooth/main.conf` → `Name = Moonboard A`, `/etc/machine-info` → `PRETTY_HOSTNAME=Moonboard A`) — makes the Bluetooth device name persistent across reboots.
- **systemd services** — `moonboard_ble.service` points to `moonboard_ble_dbus_service.py`; `moonboard_led.service` passes `--led_mapping led_mapping_mini.json`.

## Current status

The LED system is fully working with the Moonboard app over Bluetooth. I have **not yet mounted the LED strips on the board**, so the physical LED mapping (`led_mapping_mini.json`) might need adjustment once installed. If your wiring order is different, you'll need to update the mapping file.

## Tip for beginners

If you have no idea where to start, I highly recommend using an **AI coding agent** like [Cursor](https://cursor.com/) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Use a smart model (e.g. Claude Opus 4.6) and let the agent walk you through the entire setup — from flashing the Pi, installing dependencies, configuring services, to debugging Bluetooth. Just describe what you're trying to do and paste any errors you encounter. It saved me a huge amount of time.

