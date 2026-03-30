# Datadis - Integración para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/perico85/datadis-homeassistant.svg)](https://github.com/perico85/datadis-homeassistant/releases)

Integración profesional para Home Assistant que obtiene datos de consumo eléctrico desde la API oficial de **Datadis** (distribuidoras eléctricas españolas).

## Características principales

- 📊 **Consumo horario** desglosado por tramos (Punta, Llano, Valle)
- 💰 **Cálculo automático** de costes de tu factura
- ⚡ **Potencia máxima** demandada por período
- 🔘 **Servicios y botones** para automatizaciones
- 🔌 **Panel de Energía** compatible
- 🩺 **Diagnósticos integrados**

## Instalación

1. Ve a **HACS** → **Integraciones** → **⋮** → **Repositorios personalizados**
2. Añade la URL: `https://github.com/perico85/datadis-homeassistant`
3. Instala la integración
4. Reinicia Home Assistant

## Configuración

1. Ve a **Ajustes** → **Dispositivos y servicios** → **Añadir integración**
2. Busca **"Datadis"**
3. Introduce tus credenciales (NIF/NIE y contraseña de datadis.es)
4. Selecciona tu CUPS y configura los precios de tu tarifa

## Documentación completa

Para más detalles, visita la [documentación completa](https://github.com/perico85/datadis-homeassistant/blob/main/custom_components/datadis/README.md).

## Soporte

¿Problemas? Abre un [issue](https://github.com/perico85/datadis-homeassistant/issues) incluyendo los diagnósticos de la integración.
