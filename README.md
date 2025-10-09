# Systemair Integration for Home Assistant

[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/AN3Orik/systemair?style=for-the-badge)](https://github.com/AN3Orik/systemair/releases)
[![GitHub License](https://img.shields.io/github/license/AN3Orik/systemair?style=for-the-badge)](https://github.com/AN3Orik/systemair/blob/main/LICENSE)
[![TIP](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge)](https://dalink.to/an3orik)

This Home Assistant integration allows you to monitor and control **Systemair SAVE** ventilation units through multiple connection methods. It supports communication via **Modbus TCP**, **Modbus Serial (RS485)**, and **Web API**, providing flexibility for different hardware configurations.

This integration was tested with SAVE VSR 300 and VSR 500 models but should be compatible with other units that support Modbus protocol.

## Overview

[Systemair SAVE](https://www.systemair.com/en-gb/products/residential-ventilation-systems/air-handling-units/save) units are residential ventilation systems designed for heat recovery. This integration brings your ventilation unit into Home Assistant, allowing you to create advanced automations and gain deep insights into your home's air quality and energy consumption.

## Features

*   **Multiple Connection Methods:** Support for three different connection types:
    *   **Modbus TCP** - via Systemair SAVECONNECT 1.0 or compatible Modbus TCP modules
    *   **Modbus Serial (RS485)** - via USB-to-Modbus converters
    *   **Web API (HTTP)** - via Systemair SAVECONNECT 2.0 IAM module
*   **Climate Control:** Full control over HVAC modes (Off, Fan Only, Heat, Cool), target temperature, fan speed, and preset modes (Auto, Manual, Away, Holiday, etc.).
*   **Calculated Power Consumption:** Monitor the estimated power usage of the supply fan, extract fan, and the total power consumption of the unit, including the re-heater. Essential for energy tracking in Home Assistant's Energy Dashboard.
*   **Advanced Configuration Controls:** Directly configure key operational parameters from Home Assistant, including:
    *   Temperature Control Mode (Supply air, Room air, etc.)
    *   Fan Regulation Unit (Manual %, RPM, Pressure, etc.)
    *   Defrosting Mode (Soft, Normal, Hard)
    *   Allowing/disallowing manual fan stop.
*   **Enhanced Diagnostic Sensors:** Gain deeper insights into the unit's current state with sensors for:
    *   Indoor Air Quality (IAQ) Level
    *   Active Demand Controller (CO2 or RH)
    *   Current Defrosting State
*   **Sensor Monitoring:** Track key environmental data, including outdoor, supply, and extract air temperatures, as well as relative humidity.
*   **Device Status:** Monitor fan RPM, fan speed percentages, and heater output.
*   **Diagnostics:** Keep an eye on filter lifetime and view detailed alarm statuses. 

## Prerequisites

### Connection Method 1: Modbus TCP (SAVECONNECT 1.0)

1.  A Systemair SAVE ventilation unit equipped with a **[SAVECONNECT 1.0 (IAM)](https://www.systemair.com/en-gb/p/internet-access-module-iam-110534)** module or any other Modbus TCP-to-RTU converter.
2.  The module must be connected to the same local network as your Home Assistant instance.
3.  You need to know the IP address of the module. You can typically find this in your router's client list.

### Connection Method 2: Modbus Serial (RS485)

1.  A Systemair SAVE ventilation unit with accessible Modbus RS485 port.
2.  A **USB-to-Modbus RS485 converter** connected to your Home Assistant server.
3.  The serial port path (e.g., `/dev/ttyUSB0` on Linux, `COM3` on Windows).
4.  Communication parameters (usually 19200 baud, 8 data bits, no parity, 1 stop bit).

### Connection Method 3: Web API (SAVECONNECT 2.0)

1.  A Systemair SAVE ventilation unit equipped with a **[SAVECONNECT 2.0](https://www.systemair.com/en/products/residential-ventilation-systems/accessories/accessories-for-residential-units/control/save-connect)** module.
2.  The IAM module must be connected to the same local network as your Home Assistant instance.
3.  You need to know the IP address of the IAM module. You can typically find this in your router's client list.
4.  The IAM module's web interface should be accessible via HTTP.

## Installation

### HACS

1.  Open HACS and go to "Custom integrations". Enter the URL `https://github.com/AN3Orik/systemair`, choose type Integration and click Add.
2.  Restart Home Assistant.
3.  Go to settings and add new integration. You will find Systemair in the list of available integrations.

### Manual

1.  Using the tool of choice open the directory (folder) for your [HA configuration](https://www.home-assistant.io/docs/configuration/) (where you find `configuration.yaml`).
2.  If you do not have a `custom_components` directory (folder) there, you need to create it.
3.  In the `custom_components` directory (folder) create a new folder called `systemair`.
4.  Download all files from the `custom_components/systemair/` directory (folder) in this repository.
5.  Place the files you downloaded in the new directory (folder) you created.
6.  Restart Home Assistant.

## Configuration

Configuration is done entirely through the Home Assistant user interface.

1.  Navigate to **Settings > Devices & Services**.
2.  Click the **+ Add Integration** button in the bottom right corner.
3.  Search for "**Systemair**" and select it.
4.  Select your **connection type**:

### Option A: Modbus TCP

Configure connection to SAVECONNECT 1.0 or compatible Modbus TCP module:

*   **Host:** The IP address of your Systemair module (e.g., `192.168.1.50`).
*   **Port:** The Modbus TCP port for the module. The default is `502`.
*   **Slave ID:** The Modbus slave ID of the unit. The default is `1`.
*   **Ventilation Unit Model:** Select your specific SAVE unit model from the dropdown list (e.g., `VSR 300`, `VSR 500`). **This is crucial for accurate power consumption calculations.**

### Option B: Modbus Serial (RS485)

Configure connection via USB-to-Modbus RS485 converter:

*   **Serial Port:** The serial port path (e.g., `/dev/ttyUSB0` on Linux, `COM3` on Windows).
*   **Baud Rate:** Communication speed. Default is `19200`.
*   **Data Bits:** Number of data bits. Options: `7` or `8` (default: `8`).
*   **Parity:** Parity checking. Options: `N` (None), `E` (Even), `O` (Odd). Default is `N`.
*   **Stop Bits:** Number of stop bits. Options: `1` or `2` (default: `1`).
*   **Slave ID:** The Modbus slave ID of the unit. The default is `1`.
*   **Ventilation Unit Model:** Select your specific SAVE unit model from the dropdown list (e.g., `VSR 300`, `VSR 500`).

### Option C: Web API (SAVECONNECT 2.0)

Configure connection to SAVECONNECT 2.0 IAM module:

*   **IP Address:** The IP address of your SAVECONNECT 2.0 IAM module (e.g., `192.168.1.50`).
*   **Ventilation Unit Model (Optional):** You can manually select your unit model, or leave it empty to auto-detect from the device.

---

5.  Click **Submit**. The integration will test the connection and add the Systemair device and its entities to Home Assistant.

You can change the model at any time after installation by navigating to the integration's page and clicking **Configure**.

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
*   **Power & Energy:** Supply Fan, Extract Fan, and Total Power/Energy consumption
*   **Diagnostics:** Indoor Air Quality, Active Demand Controller, Defrosting State.
*   **Filter:** Filter Remaining Time (in seconds).
*   **Alarms:** Individual sensors for each possible alarm (e.g., Frost Protection, Filter Alarm) showing its current state.

#### Binary Sensors

*   **Heat Exchange Active:** `on` when the heat exchanger is running.
*   **Heater Active:** `on` when the heating element is active.

#### Switches

*   **Eco Mode:** A switch to enable or disable the energy-saving Eco mode.
*   **Free Cooling:** A switch to enable or disable the free cooling function.
*   **Allow Manual Fan Stop:** A configuration switch to permit the fans to be turned completely off.

#### Numbers

*   **Time Delays:** Entities to configure the duration for timed preset modes like `Holiday`, `Away`, and `Fireplace`.

#### Selects

*   **Temperature Control Mode:** Choose the sensor used for temperature regulation (Supply air, Room air, Extract air).
*   **Fan Regulation Unit:** Select the fan control method (Manual %, RPM, Pressure, etc.).
*   **Defrosting Mode:** Configure the aggressiveness of the defrosting cycle (Soft, Normal, Hard).

## Lovelace Cards

To get the best experience, it is recommended to also install the [Systemair Lovelace Cards](https://github.com/AN3Orik/systemair-lovelace) pack, which provides specific way to display some information from integration (example: alarm history).

1.  Open HACS and go to "Custom integrations". Enter the URL `https://github.com/AN3Orik/systemair-lovelace`, choose type Dashboard and click Add.
2.  Find the "Systemair Lovelace Cards" in the list and click **Download**.
3.  Follow the instructions to add the card to your dashboard.
