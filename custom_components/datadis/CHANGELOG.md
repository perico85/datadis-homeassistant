# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-01

### Added
- First release of the Datadis integration
- Primera versión de la integración Datadis

### Features / Características
- Energy consumption monitoring by time period (P1/P2/P3)
  - Monitorización del consumo eléctrico por tramo horario (P1/P2/P3)
- Energy export/surplus for self-consumption
  - Exportación de energía y excedentes para autoconsumo
- Cost calculation with all tariff components (energy, power, fixed costs)
  - Cálculo de costes con todos los componentes de la tarifa (energía, potencia, costes fijos)
- Automatic tariff period detection (1, 2, or 3 periods)
  - Detección automática de periodos de tarifa (1, 2 o 3 periodos)
- Daily and monthly statistics
  - Estadísticas diarias y mensuales
- Compatible with Home Assistant Energy Panel
  - Compatible con el Panel de Energía de Home Assistant
- Spanish and English translations
  - Traducciones en español e inglés

### Supported Tariffs / Tarifas Soportadas
- 2.0TD, 2.0DHS, 2.1DHS, 3.0TD (3 periods / 3 periodos)
- 2.0A, 2.0DHA, 2.1DHA (2 periods / 2 periodos)
- 2.0NA, 2.1NA (1 period / 1 periodo)

### Sensors / Sensores

#### Energy / Energía
- Energy imported/exported (monthly and daily)
  - Energía importada/exportada (mensual y diaria)
- Energy by period (P1-Punta, P2-Llano, P3-Valle)
  - Energía por periodo (P1-Punta, P2-Llano, P3-Valle)
- Consumption yesterday, day before, monthly
  - Consumo ayer, anteayer, mensual

#### Costs / Costes
- Cost by energy period / Coste por periodo de energía
- Cost by power period / Coste por periodo de potencia
- Total electricity cost / Coste total electricidad
- Invoice total estimation / Estimación factura mensual

#### Power / Potencia
- Maximum power by period / Potencia máxima por periodo
- Contracted power / Potencia contratada

#### Info / Información
- Tariff code / Código de tarifa
- Distributor / Distribuidora
- Last data date / Última fecha de datos
- Last reading / Última lectura

## [0.9.0] - Beta

### Added
- Initial beta version
- Versión beta inicial
