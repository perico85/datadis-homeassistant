# Integración Datadis para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/perico85/datadis-homeassistant.svg)](https://github.com/perico85/datadis-homeassistant/releases)

Integración personalizada para Home Assistant que obtiene datos de consumo eléctrico desde la API oficial de **Datadis**, la plataforma de las distribuidoras eléctricas españolas.

---

## 📋 Contenido

- [¿Qué es Datadis?](#qué-es-datadis)
- [Características](#características)
- [Requisitos](#requisitos)
- [Registro en Datadis](#registro-en-datadis)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Sensores disponibles](#sensores-disponibles)
- [Panel de Energía](#panel-de-energía)
- [Solución de problemas](#solución-de-problemas)

---

## ¿Qué es Datadis?

**Datadis** es la plataforma oficial del Ministerio para la Transición Ecológica que permite a los consumidores españoles acceder a sus datos de consumo eléctrico en tiempo casi-real (con un desfase de 24-48 horas).

Mediante esta integración podrás:
- Ver tu consumo horario detallado
- Calcular costes de tu factura eléctrica
- Monitorizar potencia máxima demandada
- Configurar el Panel de Energía de Home Assistant

---

## Características

### 📊 Datos de consumo
- Consumo horario desglosado por tramos (Punta, Llano, Valle)
- Consumo del último día disponible (D+1)
- Consumo acumulado del mes
- Excedentes de autoconsumo (si aplica)

### 💰 Cálculo de costes
- Cálculo automático del coste de energía consumida
- Coste del término de potencia
- Impuestos (IVA, Impuesto Eléctrico)
- Bono social y alquiler de equipos
- Estimación total de la factura mensual

### ⚡ Potencia
- Potencia máxima demandada por período
- Potencia contratada según tu tarifa
- Comparativa de excesos de potencia

### 🔌 Panel de Energía
- Sensores compatibles con el dashboard de energía de HA
- Seguimiento de importación/exportación a red
- Estadísticas de consumo por períodos tarifarios

### 🔘 Servicios y Botones
- **Botón actualizar**: Forzar actualización desde la interfaz
- **Botón reiniciar**: Reiniciar contadores acumulativos (útil para inicio de mes)
- **Servicio `update_data`**: Actualización programable desde automatizaciones
- **Servicio `set_energy_prices`**: Actualizar precios de energía dinámicamente
- **Diagnósticos**: Descargar información de depuración desde Ajustes -> Dispositivos -> Datadis -> Descargar diagnósticos

---

## Requisitos

- Home Assistant 2023.1.0 o superior
- Cuenta activa en [Datadis.es](https://datadis.es)
- Contrato de suministro eléctrico en España
- Acceso a internet (consulta API en la nube)

---

## Registro en Datadis

### Paso 1: Crear cuenta
1. Ve a [https://www.datadis.es](https://www.datadis.es)
2. Haz clic en **"Registro de usuarios"**
3. Selecciona **"Persona física"**
4. Introduce tu **NIF/NIE** y contraseña
5. Completa el proceso de verificación

### Paso 2: Asociar tu suministro
Una vez registrado, necesitas asociar tu CUPS (Código Unificado de Punto de Suministro):

1. Inicia sesión en Datadis
2. Ve a **"Mis suministros"**
3. Haz clic en **"Añadir suministro"**
4. Introduce tu **CUPS** (lo encontrarás en tu factura eléctrica)
5. La distribuidora validará la asociación (puede tardar 24-48h)

> 💡 **Tip:** Tu CUPS tiene formato `ES0021XXXXXXXXXXXXXX` y consta de 20-22 caracteres.

### Paso 3: Verificar acceso
Una vez asociado, verás tus datos de consumo en el apartado **"Curva de carga horaria"**. Si puedes ver el consumo horario, ¡la integración funcionará!

---

## Instalación

### Método 1: HACS (Recomendado)

1. Ve a **HACS** → **Integraciones**
2. Haz clic en los **⋮ (tres puntos)** → **Repositorios personalizados**
3. Añade la URL: `https://github.com/perico85/datadis-homeassistant`
4. Selecciona categoría: **Integration**
5. Reinicia Home Assistant

### Método 2: Manual

1. Descarga la última versión desde [Releases](https://github.com/perico85/datadis-homeassistant/releases)
2. Copia la carpeta `custom_components/datadis` a tu instalación de HA
3. La ruta debe quedar: `config/custom_components/datadis/`
4. Reinicia Home Assistant

---

## Configuración

### Primer paso: Configurar la integración

1. Ve a **Ajustes** → **Dispositivos y servicios**
2. Haz clic en **Añadir integración**
3. Busca **"Datadis"**
4. Completa el formulario:
   - **NIF/NIE:** Tu número de identificación
   - **Contraseña:** Tu contraseña de Datadis

### Segundo paso: Seleccionar CUPS

Si tienes varios suministros, selecciona el que quieras monitorizar.

### Tercer paso: Configurar precios (IMPORTANTE)

Introduce los datos de tu factura para el cálculo correcto de costes:

| Configuración | Valor típico 2.0TD | Descripción |
|--------------|-------------------|-------------|
| Precio P1 (Punta) | 0.15 - 0.20 €/kWh | Horario punta |
| Precio P2 (Llano) | 0.12 - 0.15 €/kWh | Horario llano |
| Precio P3 (Valle) | 0.08 - 0.10 €/kWh | Horario valle |
| Precio Potencia P1 | ~0.10 €/kW/día | Término potencia punta |
| Precio Potencia P2 | ~0.03 €/kW/día | Término potencia valle |
| Potencia Contratada P1 | 3.45 - 5.75 kW | Tu potencia contratada |
| Potencia Contratada P2 | 3.45 - 5.75 kW | Igual que P1 (2.0TD) |
| Impuesto Eléctrico | 5.11% | Impuesto estatal |
| IVA | 21% | Impuesto sobre ventas |
| Alquiler Equipos | 0.027 €/día | Contador, etc. |
| Bono Social | 0.019 €/día | Descuento si aplica |

> 💡 **Tip:** Puedes consultar estos precios en tu factura actual o en la web de tu comercializadora.

### Modificar configuración posteriormente

1. Ve a **Ajustes** → **Dispositivos y servicios** → **Datadis**
2. Haz clic en **Configurar**
3. Ajusta los precios según sea necesario

---

## Sensores disponibles

### 🏠 Sensores principales

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.datadis_consumption_yesterday` | Consumo del último día disponible | kWh |
| `sensor.datadis_consumption_month` | Consumo acumulado del mes | kWh |
| `sensor.datadis_energy_imported` | Energía importada desde red (mes) | kWh |
| `sensor.datadis_energy_exported` | Energía exportada a red (mes) | kWh |
| `sensor.datadis_surplus_yesterday` | Excedentes del último día | kWh |
| `sensor.datadis_surplus_month` | Excedentes acumulados del mes | kWh |

### 💶 Sensores de costes

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.datadis_cost_total` | Coste estimado total | € |
| `sensor.datadis_cost_energy_p1` | Coste energía período Punta | € |
| `sensor.datadis_cost_energy_p2` | Coste energía período Llano | € |
| `sensor.datadis_cost_energy_p3` | Coste energía período Valle | € |
| `sensor.datadis_cost_power_total` | Coste término de potencia | € |
| `sensor.datadis_cost_invoice` | Total estimado factura mensual | € |

### ⚡ Sensores de potencia

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.datadis_max_power` | Potencia máxima demandada | kW |
| `sensor.datadis_max_power_p1` | Potencia máxima período Punta | kW |
| `sensor.datadis_max_power_p2` | Potencia máxima período Llano | kW |
| `sensor.datadis_max_power_p3` | Potencia máxima período Valle | kW |
| `sensor.datadis_contracted_power` | Potencia contratada | kW |

### 📅 Sensores desglosados por período

**Período Punta (P1):**
- Horario: 10:00-14:00 y 18:00-22:00 (L-V)
- `sensor.datadis_consumption_yesterday_p1`
- `sensor.datadis_consumption_month_p1`

**Período Llano (P2):**
- Horario: 08:00-10:00, 14:00-18:00, 22:00-00:00 (L-V)
- `sensor.datadis_consumption_yesterday_p2`
- `sensor.datadis_consumption_month_p2`

**Período Valle (P3):**
- Horario: 00:00-08:00 (L-V) y 24h fines de semana y festivos
- `sensor.datadis_consumption_yesterday_p3`
- `sensor.datadis_consumption_month_p3`

### ℹ️ Sensores informativos

| Sensor | Descripción |
|--------|-------------|
| `sensor.datadis_tariff` | Código de tarifa contratada |
| `sensor.datadis_distributor` | Nombre de la distribuidora |
| `sensor.datadis_last_data_date` | Fecha del último dato disponible |
| `sensor.datadis_last_reading` | Valor de última lectura horaria |

---

## Panel de Energía

Para configurar el **Panel de Energía** de Home Assistant con tus datos reales:

### Paso 1: Acceder al Panel de Energía

1. Ve a **Panel de Energía** (en el menú lateral de HA)
2. Haz clic en **Añadir fuente de red eléctrica**

### Paso 2: Configurar consumo de red

Selecciona uno de estos sensores:

**Opción A (Simple):**
- `sensor.datadis_energy_imported` - Consumo total mensual acumulado

**Opción B (Por períodos tarifarios):**
- `sensor.datadis_energia_acumulada_importada_p1` - Punta
- `sensor.datadis_energia_acumulada_importada_p2` - Llano
- `sensor.datadis_energia_acumulada_importada_p3` - Valle

### Paso 3: Configurar retorno a red (si tienes autoconsumo)

- `sensor.datadis_energy_exported` - Total exportado
- O los sensores específicos por período: `sensor.datadis_energia_acumulada_exportada_p1`, etc.

### Paso 4: Panel de Energía por períodos (Avanzado)

Para ver el consumo desglosado por tramos horarios:

1. Crea **tarifas de electricidad** en el Panel de Energía
2. Usa los sensores diarios por período:
   - `sensor.datadis_energia_importada_punta` - Período Punta
   - `sensor.datadis_energia_importada_llano` - Período Llano
   - `sensor.datadis_energia_importada_valle` - Período Valle

### Paso 5: Configurar costes

En la configuración del Panel de Energía, activa **"Usar entidad que realiza un seguimiento de los costes totales"** y selecciona:
- `sensor.datadis_cost_total` (o `sensor.datadis_cost_invoice`)

---

## Tramos horarios tarifa 2.0TD

La integración clasifica automáticamente el consumo según la tarifa 2.0TD vigente:

| Período | Horario (Lunes a Viernes) | Precio aprox. |
|---------|---------------------------|---------------|
| **Punta (P1)** | 10:00-14:00 y 18:00-22:00 | ⬆️ Más caro |
| **Llano (P2)** | 08:00-10:00, 14:00-18:00, 22:00-00:00 | ➖ Intermedio |
| **Valle (P3)** | 00:00-08:00 + fines de semana/festivos | ⬇️ Más barato |

> **Nota:** Fin de semana y festivos nacionales son siempre período Valle (P3).

---

## Uso Avanzado

### Servicios disponibles

La integración expone los siguientes servicios para usar en automatizaciones:

#### `datadis.update_data`
Fuerza la actualización inmediata desde la API de Datadis.

```yaml
service: datadis.update_data
data: {}
```

#### `datadis.set_energy_prices`
Actualiza los precios de energía en tiempo real. Útil si cambias de comercializadora o tarifa.

```yaml
service: datadis.set_energy_prices
data:
  p1_price: 0.182  # Precio Punta (€/kWh)
  p2_price: 0.145  # Precio Llano (€/kWh)
  p3_price: 0.099  # Precio Valle (€/kWh)
```

#### `datadis.reset_accumulated`
Reinicia los contadores acumulativos. Útil al inicio de mes.

```yaml
service: datadis.reset_accumulated
data:
  confirm: "RESET"  # Debe escribirse exactamente
```

### Ejemplo de automatización

Actualizar precios automáticamente cada día a las 00:00:

```yaml
automation:
  - alias: "Actualizar precios luz"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: datadis.set_energy_prices
        data:
          p1_price: "{{ states('sensor.precio_luz_punta') | float }}"
          p2_price: "{{ states('sensor.precio_luz_llano') | float }}"
          p3_price: "{{ states('sensor.precio_luz_valle') | float }}"
```

### Diagnósticos

Si necesitas ayuda, puedes descargar información de diagnóstico:

1. Ve a **Ajustes** -> **Dispositivos y servicios**
2. Busca **Datadis** y haz clic
3. Selecciona **Descargar diagnósticos**
4. Adjunst este archivo al abrir un issue en GitHub

---

## Solución de problemas

### Error de autenticación
```
Error de autenticación Datadis
```
- Verifica que tu NIF/NIE y contraseña son correctos
- Asegúrate de poder acceder a [datadis.es](https://datadis.es) con esas credenciales

### No se encuentran suministros
```
No se encontró suministro para CUPS
```
- Verifica que has asociado correctamente tu CUPS en Datadis
- Espera 24-48h tras la asociación del suministro

### Datos no se actualizan
```
Límite de consultas Datadis (429)
```
- La API permite una consulta por rango de fechas cada 24h
- Los datos se actualizan automáticamente cada mediodía
- Patience! Los datos en Datadis tienen un desfase de D+1 (ayer)

### Sensor unavailable
- Verifica que la integración está configurada correctamente
- Revisa los logs de Home Assistant para más detalles

---

## Limitaciones

- **Desfase temporal:** Los datos tienen un retraso de 24-48 horas (D+1 o D+2)
- **Rate limiting:** Máximo 1 consulta por rango de fechas cada 24 horas
- **Festivos:** La detección de festivos es aproximada (solo nacionales fijos)
- **Múltiples CUPS:** Solo se puede configurar un CUPS por instancia de integración

---

## Soporte

Si encuentras algún problema o tienes sugerencias:

- 🐛 [Abrir issue en GitHub](https://github.com/perico85/datadis-homeassistant/issues)
- 📝 Incluye los logs de Home Assistant relacionados con `datadis`

---

## Licencia

Este proyecto está licenciado bajo [MIT](LICENSE).

---

**¡Gracias por usar la integración Datadis!** ⚡🔌