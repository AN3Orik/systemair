# Systemair Modbus Integration for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/AN3Orik/systemair?style=for-the-badge)](https://github.com/AN3Orik/systemair/releases)
[![GitHub License](https://img.shields.io/github/license/AN3Orik/systemair?style=for-the-badge)](https://github.com/AN3Orik/systemair/blob/main/LICENSE)

This Home Assistant integration allows you to monitor and control **Systemair VSR** ventilation units through your local network. It communicates directly with the **Systemair IAM ([Internet Access Module](https://www.systemair.com/en-gb/p/internet-access-module-iam-110534))** or, potentially, any other ModBus TCP-RTU module via the Modbus TCP protocol.

This integration was tested with SAVE VSR 300 and VSR 500 models but should be compatible with other units that use the IAM module.

## Overview

[Systemair SAVE](https://www.systemair.com/en-gb/products/residential-ventilation-systems/air-handling-units/save) units are residential ventilation systems designed for heat recovery, providing fresh, filtered, and pre-heated air to your home. This integration brings your ventilation unit into Home Assistant, allowing you to create advanced automations based on air quality, presence, or time of day.

## Features

*   **Climate Control:** Full control over HVAC modes (Off, Fan Only, Heat, Cool), target temperature, fan speed, and preset modes (Auto, Manual, Away, Holiday, etc.).
*   **Sensor Monitoring:** Track key environmental data, including outdoor, supply, and extract air temperatures, as well as relative humidity.
*   **Device Status:** Monitor fan RPM, fan speed percentages, heater output, and heat exchanger status.
*   **Diagnostics:** Keep an eye on filter lifetime and view detailed alarm statuses.
*   **Mode Toggles:** Easily enable or disable features like Eco Mode and Free Cooling.

## Prerequisites

1.  A Systemair SAVE ventilation unit equipped with an **IAM (Internet Access Module)**.
2.  The IAM module must be connected to the same local network as your Home Assistant instance.
3.  You need to know the IP address of the IAM module. You can typically find this in your router's client list.

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=AN3Orik&repository=systemair&category=integration)

### Manual

1. Using the tool of choice open the directory (folder) for your [HA configuration](https://www.home-assistant.io/docs/configuration/) (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `systemair`.
4. Download all files from the `custom_components/systemair/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

Configuration is done entirely through the Home Assistant user interface.

1.  Navigate to **Settings > Devices & Services**.
2.  Click the **+ Add Integration** button in the bottom right corner.
3.  Search for "**Systemair**" and select it.
4.  A configuration dialog will appear, asking for connection details:

    *   **Host:** The IP address of your Systemair IAM module (e.g., `192.168.1.50`).
    *   **Port:** The Modbus TCP port for the IAM module. The default is `502`.
    *   **Slave ID:** The ModBus slave ID of the unit. The default is `1`.

5.  Click **Submit**. The integration will test the connection and, if successful, add the Systemair device and its entities to Home Assistant.

## Entities Provided

This integration creates a single device for your ventilation unit with the following entities:

#### Climate
The primary entity for controlling the unit.
*   **HVAC Modes:** `Off`, `Fan Only`, `Heat`, `Cool`, `Heat/Cool`.
*   **Fan Modes:** `Low`, `Medium`, `High`.
*   **Preset Modes:** `Auto`, `Manual`, `Crowded`, `Refresh`, `Fireplace`, `Away`, `Holiday`.
*   **Controls:** Target Temperature, Current Temperature, Current Humidity.

#### Sensors
*   **Temperatures:** Outside Air, Supply Air, Extract Air, Overheat Sensor.
*   **Humidity:** Extract Air Relative Humidity.
*   **Fan Speeds:** Supply & Extract Air Fan RPM, Supply & Extract Air Fan Regulated Speed (%).
*   **Heater:** Heater Output Value (%).
*   **Filter:** Filter Remaining Time (in seconds).
*   **Alarms:** Individual sensors for each possible alarm (e.g., Frost Protection, Filter Alarm, Fire Alarm) showing its current state (`Inactive`, `Active`, etc.).

#### Binary Sensors
*   **Heat Exchange Active:** `on` when the heat exchanger is running.
*   **Heater Active:** `on` when the heating element is active.

#### Switches
*   **Eco Mode:** A switch to enable or disable the energy-saving Eco mode.
*   **Free Cooling:** A switch to enable or disable the free cooling function.

#### Numbers
*   **Time Delays:** Entities to configure the duration (in days, hours, or minutes) for timed preset modes like `Holiday`, `Away`, and `Fireplace`.
