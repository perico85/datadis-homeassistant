# Integración Datadis para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/perico85/datadis-homeassistant.svg)](https://github.com/perico85/datadis-homeassistant/releases)

Integración personalizada para Home Assistant que obtiene datos de consumo eléctrico desde la API oficial de **Datadis**, la plataforma de las distribuidoras eléctricas españolas.

## 📋 Índice

- [¿Qué es Datadis?](#-qué-es-datadis)
- [Características](#-características)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Panel de Energía](#-panel-de-energía)
- [Sensores](#-sensores)

---

## ⚡ ¿Qué es Datadis?

**Datadis** es la plataforma oficial del Ministerio para la Transición Ecológica que permite a los consumidores españoles acceder a sus datos de consumo eléctrico en tiempo casi-real (con un desfase de 24-48 horas).

### Características principales

- 📊 **Consumo horario** desglosado por tramos (Punta, Llano, Valle)
- 💰 **Cálculo de costes** automático de tu factura
- ⚡ **Potencia máxima** demandada por período
- 🔌 **Panel de Energía** compatible con Home Assistant
- 🌞 **Autoconsumo** y excedentes (si aplica)

---

## 📥 Instalación

### Via HACS (Recomendado)

1. Ve a **HACS** → **Integraciones**
2. Haz clic en **⋮** → **Repositorios personalizados**
3. Añade la URL: `https://github.com/perico85/datadis-homeassistant`
4. Selecciona categoría: **Integration**
5. Reinicia Home Assistant

---

## ⚙️ Configuración

### Paso 1: Cuenta en Datadis

Si aún no tienes cuenta:

1. Ve a [www.datadis.es](https://www.datadis.es)
2. Regístrate con tu **NIF/NIE**
3. Asocia tu **CUPS** (aparece en tu factura)

### Paso 2: Configurar la integración

1. Ve a **Ajustes** → **Dispositivos y servicios**
2. Haz clic en **Añadir integración**
3. Busca **"Datadis"**
4. Introduce tu NIF/NIE y contraseña
5. Selecciona tu CUPS
6. Configura los precios de tu tarifa

> 💡 **Tip:** Encuentra los precios en tu factura eléctrica o en la web de tu comercializadora.

---

## 🔋 Panel de Energía

Para usar con el **Panel de Energía** de Home Assistant:

### Configurar consumo de red

1. Ve al **Panel de Energía**
2. Añade **fuente de red eléctrica**:
   - Opción simple: `sensor.datadis_energy_imported`
   - Por períodos: sensores `sensor.datadis_energia_acumulada_importada_pX`

3. **Retorno a red** (si tienes autoconsumo):
   - `sensor.datadis_energy_exported`

4. **Costes**: Selecciona `sensor.datadis_cost_total`

### Tramos horarios (2.0TD)

| Período | Horario (L-V) | Precio |
|---------|---------------|--------|
| **Punta (P1)** | 10:00-14:00, 18:00-22:00 | ⬆️ Más caro |
| **Llano (P2)** | 08:00-10:00, 14:00-18:00, 22:00-00:00 | ➖ Intermedio |
| **Valle (P3)** | 00:00-08:00 | ⬇️ Más barato |

> ℹ️ Fin de semana y festivos: 24h = Valle (P3)

---

## 📊 Sensores principales

### Consumo
- `sensor.datadis_consumption_yesterday` - Consumo último día
- `sensor.datadis_consumption_month` - Consumo mes
- `sensor.datadis_energy_imported` - Total importado
- `sensor.datadis_energy_exported` - Total exportado

### Costes
- `sensor.datadis_cost_total` - Coste estimado
- `sensor.datadis_cost_invoice` - Total factura mensual

### Potencia
- `sensor.datadis_max_power` - Potencia máxima demandada
- `sensor.datadis_contracted_power` - Potencia contratada

### Por períodos (P1/P2/P3)
- `sensor.datadis_consumption_yesterday_p1` - Consumo Punta
- `sensor.datadis_consumption_yesterday_p2` - Consumo Llano
- `sensor.datadis_consumption_yesterday_p3` - Consumo Valle

---

## 📚 Documentación completa

Para más detalles, consulta la **[documentación completa](./custom_components/datadis/README.md)** que incluye:

- Registro paso a paso en Datadis
- Configuración detallada del Panel de Energía
- Descripción de todos los sensores
- Tablas de precios y cálculos
- Solución de problemas

---

## 🆘 Soporte

¿Tienes problemas o sugerencias?

- [Abrir issue en GitHub](https://github.com/perico85/datadis-homeassistant/issues)
- Incluye logs relacionados con `datadis`

---

**Licencia:** [MIT](LICENSE)

**¡Gracias por usar la integración Datadis!** ⚡🇪🇸