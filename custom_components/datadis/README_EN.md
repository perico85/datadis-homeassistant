# Datadis Integration for Home Assistant

[![GitHub Release](https://img.shields.io/github/release/home-assistant/example-custom-integration?style=for-the-badge)](https://github.com/)
[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz/)
[![License](https://img.shields.io/github/license/home-assistant/example-custom-integration?style=for-the-badge)](LICENSE)

A Home Assistant integration for Datadis, the Spanish electricity data platform.

## Installation

### Via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations** → **Explore**
3. Search for "Datadis"
4. Click **Download**
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/datadis` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** (+)
3. Search for "Datadis"
4. Enter your Datadis credentials (NIF and password)
5. Select your supply point (CUPS)
6. Configure your electricity tariff prices

## Requirements

- A Datadis account (https://datadis.es)
- Your NIF/NIE and password
- Your supply point CUPS (from your electricity bill)

## Features

- Automatic tariff period detection (1, 2, or 3 periods)
- Energy consumption by time period (Punta, Llano, Valle)
- Energy export/surplus for self-consumption
- Cost calculation with all tariff components
- Daily and monthly statistics
- Compatible with Home Assistant Energy Panel

## Sensors

### Energy Sensors
- Energy imported/exported (monthly, daily)
- Energy by period (P1, P2, P3)
- Consumption yesterday, day before, monthly

### Cost Sensors
- Cost by energy period
- Cost by power period
- Fixed costs (rental, social bonus)
- Total invoice estimation

### Power Sensors
- Maximum power by period
- Contracted power

### Info Sensors
- Tariff code
- Distributor
- Last data date

## Support

If you have issues or suggestions, please open a GitHub issue.

## License

MIT License - see [LICENSE](LICENSE) for details.
