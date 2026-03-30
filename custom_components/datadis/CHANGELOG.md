# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Support for Datadis API v2
- Energy consumption sensors by time period (P1/P2/P3)
- Energy export/surplus sensors for self-consumption
- Power demand sensors by period
- Cost calculation sensors (energy, power, fixed costs)
- Automatic tariff period detection (1, 2, or 3 periods)
- Daily energy sensors that reset with new data
- Accumulated energy sensors for Energy Panel
- Spanish and English translations

### Features
- Automatic supply point detection
- Multiple date range fallback to avoid rate limiting
- Midnight scheduled updates
- Configuration flow with tariff price setup
- Support for 2.0TD, 2.0A, 2.0DHA, 2.0DHS and other tariffs

### Sensors
#### Energy
- Energy Imported/Exported (monthly and daily)
- Energy by period (P1-Punta, P2-Llano, P3-Valle)
- Consumption yesterday, day before, monthly

#### Costs
- Cost by energy period
- Cost by power period
- Total electricity cost
- Invoice total estimation

#### Power
- Maximum power by period
- Contracted power

#### Info
- Tariff code
- Distributor
- Last data date
- Last reading

## [0.9.0] - Beta

### Added
- Initial beta version
