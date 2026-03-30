# Datadis Integration for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/perico85/datadis-homeassistant?style=for-the-badge)](https://github.com/perico85/datadis-homeassistant/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz/)
[![License](https://img.shields.io/github/license/perico85/datadis-homeassistant?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/perico85/datadis-homeassistant/total?style=for-the-badge)](https://github.com/perico85/datadis-homeassistant/releases)

Integración de Datadis para Home Assistant que permite monitorizar tu consumo eléctrico y excedentes de autoconsumo directamente desde la plataforma Datadis.

## 📋 Índice

- [¿Qué es Datadis?](#qué-es-datadis)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
  - [Opción 1: HACS (recomendado)](#opción-1-hacs-recomendado)
  - [Opción 2: Instalación manual](#opción-2-instalación-manual)
- [Configuración](#configuración)
- [Sensores disponibles](#sensores-disponibles)
- [Panel de Energía](#panel-de-energía)
- [Cálculo de costes](#cálculo-de-costes)
- [Tramos horarios](#tramos-horarios)
- [Solución de problemas](#solución-de-problemas)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Créditos](#créditos)

---

## ¿Qué es Datadis?

[Datadis](https://datadis.es) es la plataforma digital de las distribuidoras eléctricas de España que permite a los consumidores acceder a sus datos de consumo eléctrico de forma gratuita.

### ¿Qué datos proporciona?

- **Consumo horario**: Tu consumo eléctrico hora a hora
- **Excedentes**: Energía vertida a la red (si tienes autoconsumo)
- **Potencia máxima**: Potencia demandada por periodo horario
- **Datos del contrato**: Potencia contratada, tarifa, distribuidora
- **Datos de autoconsumo**: Energía generada y autoconsumida (si aplica)

### Distribuidoras soportadas

| Código | Distribuidora |
|--------|---------------|
| 1 | Viesgo |
| 2 | E-distribución |
| 3 | E-redes |
| 4 | ASEME |
| 5 | UFD |
| 6 | EOSA |
| 7 | CIDE |
| 8 | IDE (I-DE) |

---

## Requisitos previos

### 1. Crear cuenta en Datadis

1. Accede a [datadis.es](https://datadis.es)
2. Haz clic en **"Registro"** en la esquina superior derecha
3. Introduce tu NIF/NIE y datos personales
4. Verifica tu identidad (puede requerir certificado digital o carta de invitación de tu comercializadora)
5. Activa tu cuenta mediante el enlace que recibirás por email

### 2. Asociar tu suministro

Si tu suministro no aparece automáticamente:

1. Accede a tu área personal en Datadis
2. Ve a **"Mis suministros"** → **"Añadir suministro"**
3. Introduce el CUPS de tu punto de suministro (lo encuentras en tu factura)
4. Espera la confirmación (puede tardar 24-48 horas)

### 3. Obtener tus credenciales

Para la integración necesitas:
- **NIF/NIE**: Tu documento de identidad
- **Contraseña**: La que usas para acceder a Datadis
- **CUPS**: El código de tu punto de suministro (20 caracteres, empieza por ES)

---

## Instalación

### Opción 1: HACS (recomendado)

Esta integración se instala como repositorio personalizado en HACS.

#### Paso 1: Añadir repositorio personalizado

1. Abre **HACS** en Home Assistant
2. Ve a **Integraciones** → Menú (tres puntos) → **Repositorios personalizados**
3. Introduce la URL del repositorio:
   ```
   https://github.com/perico85/datadis-homeassistant
   ```
4. Selecciona la categoría: **Integración**
5. Haz clic en **Añadir**
6. Espera a que se descargue el repositorio

#### Paso 2: Instalar la integración

1. En HACS, ve a **Integraciones**
2. Busca **"Datadis"**
3. Haz clic en **Descargar**
4. Reinicia Home Assistant cuando te lo pida

#### Paso 3: Configurar la integración

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Haz clic en **Añadir integración** (botón +)
3. Busca **"Datadis"**
4. Sigue los pasos de configuración

### Opción 2: Instalación manual

Si prefieres instalar manualmente:

#### Paso 1: Descargar el código

```bash
# Clonar o descargar el repositorio
git clone https://github.com/perico85/datadis-homeassistant.git
```

#### Paso 2: Copiar archivos

```bash
# Copiar al directorio de custom_components
cp -r datadis-homeassistant/custom_components/datadis /config/custom_components/
```

#### Paso 3: Reiniciar Home Assistant

Reinicia Home Assistant desde **Configuración** → **Sistema** → **Reiniciar**

#### Paso 4: Configurar

Sigue los pasos de configuración descritos anteriormente.

### Estructura de archivos

```
custom_components/datadis/
├── __init__.py           # Inicialización
├── api.py                # Cliente API Datadis
├── config_flow.py        # Flujo de configuración
├── const.py              # Constantes
├── coordinator.py        # Coordinador de datos
├── manifest.json         # Manifiesto
├── sensor.py             # Sensores
├── translations/         # Traducciones
│   ├── en.json
│   └── es.json
├── hacs.json             # Configuración HACS
├── README.md             # Documentación
├── CHANGELOG.md          # Historial de cambios
└── LICENSE               # Licencia MIT
```

---

## Configuración

### Paso 1: Introducir credenciales

Introduce tus datos de acceso a Datadis:

| Campo | Descripción |
|-------|-------------|
| NIF | Tu NIF/NIE sin guiones ni espacios |
| Contraseña | Tu contraseña de Datadis |

### Paso 2: Seleccionar suministro

Si tienes varios suministros, selecciona el que quieres monitorizar. El CUPS se muestra en formato abreviado.

### Paso 3: Configurar precios de tu tarifa

Introduce los precios de tu tarifa eléctrica (puedes encontrarlos en tu factura):

| Campo | Descripción | Unidad |
|-------|-------------|--------|
| Precio energía Punta (P1) | Precio del kWh en horario Punta | €/kWh |
| Precio energía Llano (P2) | Precio del kWh en horario Llano | €/kWh |
| Precio energía Valle (P3) | Precio del kWh en horario Valle | €/kWh |
| Precio potencia Punta (P1) | Precio del kW/día en Punta | €/kW/día |
| Precio potencia Valle (P2) | Precio del kW/día en Valle | €/kW/día |
| Potencia contratada P1 | kW contratados en Punta | kW |
| Potencia contratada P2 | kW contratados en Valle | kW |
| Impuesto eléctrico | Impuesto sobre electricidad | % (típicamente 5.11%) |
| IVA | Impuesto sobre valor añadido | % (10% Canarias, 21% Península) |
| Bono social | Descuento por bono social | €/día |
| Alquiler contador | Alquiler de equipos | €/día |

> **💡 Consejo**: Los valores por defecto son para una tarifa 2.0TD típica. Ajusta según tu factura.

### Modificar precios después

Puedes modificar los precios en cualquier momento:

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Busca **Datadis**
3. Haz clic en **Configurar**
4. Ajusta los valores y guarda

---

## Sensores disponibles

### Energía (Consumo)

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.energia_importada_red` | Energía importada del mes | kWh |
| `sensor.energia_exportada_red` | Excedentes vertidos del mes | kWh |
| `sensor.consumo_ultimo_dia` | Consumo del último día disponible | kWh |
| `sensor.consumo_ultimo_dia_punta` | Consumo en Punta del último día | kWh |
| `sensor.consumo_ultimo_dia_llano` | Consumo en Llano del último día | kWh |
| `sensor.consumo_ultimo_dia_valle` | Consumo en Valle del último día | kWh |
| `sensor.consumo_dia_anterior` | Consumo del día anterior | kWh |
| `sensor.consumo_mes` | Consumo acumulado del mes | kWh |
| `sensor.consumo_mes_punta` | Consumo mensual en Punta | kWh |
| `sensor.consumo_mes_llano` | Consumo mensual en Llano | kWh |
| `sensor.consumo_mes_valle` | Consumo mensual en Valle | kWh |

### Energía (Panel de Energía)

Estos sensores se reinician automáticamente con cada nuevo día de datos, ideales para el Panel de Energía:

| Sensor | Descripción |
|--------|-------------|
| `sensor.energia_importada` | Energía importada (se reinicia diariamente) |
| `sensor.energia_importada_punta` | Importada en horario Punta |
| `sensor.energia_importada_llano` | Importada en horario Llano |
| `sensor.energia_importada_valle` | Importada en horario Valle |
| `sensor.energia_exportada` | Excedentes exportados |
| `sensor.energia_exportada_punta` | Exportados en Punta |
| `sensor.energia_exportada_llano` | Exportados en Llano |
| `sensor.energia_exportada_valle` | Exportados en Valle |

### Costes

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.coste_electricidad` | Coste total estimado del mes | € |
| `sensor.coste_energia_punta` | Coste energía en Punta | € |
| `sensor.coste_energia_llano` | Coste energía en Llano | € |
| `sensor.coste_energia_valle` | Coste energía en Valle | € |
| `sensor.coste_potencia_punta` | Coste potencia P1 | € |
| `sensor.coste_potencia_valle` | Coste potencia P2 | € |
| `sensor.coste_termino_energia` | Total término energía | € |
| `sensor.coste_termino_potencia` | Total término potencia | € |
| `sensor.coste_fijo_mensual` | Alquiler + bono social | € |
| `sensor.coste_total_factura` | **Estimación factura mensual** | € |

### Potencia

| Sensor | Descripción | Unidad |
|--------|-------------|--------|
| `sensor.potencia_maxima` | Potencia máxima demandada | kW |
| `sensor.potencia_maxima_punta` | Potencia máxima en Punta | kW |
| `sensor.potencia_maxima_llano` | Potencia máxima en Llano | kW |
| `sensor.potencia_maxima_valle` | Potencia máxima en Valle | kW |
| `sensor.potencia_contratada` | Potencia contratada | kW |

### Informativos

| Sensor | Descripción |
|--------|-------------|
| `sensor.tarifa` | Código de tarifa (ej: 2.0TD) |
| `sensor.distribuidora` | Nombre de la distribuidora |
| `sensor.ultima_fecha_datos` | Fecha del último dato disponible |
| `sensor.ultima_lectura` | Última lectura registrada |

---

## Panel de Energía

### Configuración recomendada

Para configurar el Panel de Energía de Home Assistant:

1. Ve a **Configuración** → **Paneles** → **Energía**
2. Añade las siguientes fuentes:

#### Consumo de red

| Configuración | Sensor |
|---------------|--------|
| Fuente de consumo de red | `sensor.energia_importada` |

#### Por tramo horario (opcional)

| Tramo | Sensor |
|-------|--------|
| Punta | `sensor.energia_importada_punta` |
| Llano | `sensor.energia_importada_llano` |
| Valle | `sensor.energia_importada_valle` |

#### Excedentes (si tienes autoconsumo)

| Configuración | Sensor |
|---------------|--------|
| Excedentes a la red | `sensor.energia_exportada` |

#### Costes (opcional)

| Configuración | Sensor |
|---------------|--------|
| Electricidad del grid | `sensor.coste_termino_energia` |
| Coste de red | `sensor.coste_termino_potencia` |

---

## Cálculo de costes

### Fórmula de la factura eléctrica

```
Factura = Término_Energía + Término_Potencia + Costes_Fijos

Donde:
┌─────────────────────────────────────────────────────────────────┐
│ Término_Energía = (kWh_P1 × Precio_P1 +                         │
│                    kWh_P2 × Precio_P2 +                         │
│                    kWh_P3 × Precio_P3)                           │
│                   × (1 + Impuesto_Eléctrico) × (1 + IVA)         │
├─────────────────────────────────────────────────────────────────┤
│ Término_Potencia = (kW_P1 × Precio_Pot_P1 × días +              │
│                     kW_P2 × Precio_Pot_P2 × días)                │
│                    × (1 + Impuesto_Eléctrico) × (1 + IVA)       │
├─────────────────────────────────────────────────────────────────┤
│ Costes_Fijos = (Alquiler_Contador - Bono_Social)                │
│                × días × (1 + IVA)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Ejemplo de cálculo

Para una tarifa 2.0TD con:
- Consumo: P1=50 kWh, P2=80 kWh, P3=120 kWh
- Precio energía: P1=0.167 €/kWh, P2=0.125 €/kWh, P3=0.081 €/kWh
- Potencia contratada: 4.6 kW en ambos periodos
- Precio potencia: P1=0.350 €/kW/día, P2=0.027 €/kW/día
- Días del mes: 30
- Impuesto eléctrico: 5.11%
- IVA: 10%

---

## Tramos horarios

### Tarifa 2.0TD (3 periodos) - La más común

| Periodo | Horario (L-V) | Horario (S-D y festivos) |
|---------|---------------|--------------------------|
| **P1 - Punta** | 10:00-14:00 y 18:00-22:00 | Todo el día (se computa como Valle) |
| **P2 - Llano** | 08:00-10:00, 14:00-18:00 y 22:00-24:00 | - |
| **P3 - Valle** | 00:00-08:00 | Todo el día |

### Detección automática de tarifa

La integración detecta automáticamente tu tipo de tarifa:

| Tarifa | Periodos | Descripción |
|--------|----------|-------------|
| 2.0TD, 2.0DHS, 2.1DHS, 3.0TD | 3 periodos | Punta, Llano, Valle |
| 2.0A, 2.0DHA, 2.1DHA | 2 periodos | Punta, Valle |
| 2.0NA, 2.1NA | 1 periodo | Sin discriminación |

---

## Solución de problemas

### Error de autenticación (401)

**Causa**: Credenciales incorrectas.

**Solución**:
1. Verifica que tu NIF y contraseña son correctos
2. Accede a datadis.es para confirmar que puedes entrar
3. Si has cambiado la contraseña recientemente, espera 24 horas

### Error de límite de consultas (429)

**Causa**: Datadis limita las consultas por IP a ~5 por CUPS cada 24 horas.

**Solución**:
- La integración guarda automáticamente el rango de fechas exitoso
- Espera 24 horas si el error persiste
- No reconfigures la integración repetidamente

### No aparecen datos

**Posibles causas**:
1. El suministro no está activo en Datadis
2. Los datos tienen un desfase de **D+1** (los de ayer están disponibles hoy)
3. La distribuidora no está soportada

**Solución**:
1. Verifica en datadis.es que aparecen datos
2. Espera 24-48 horas si acabas de registrar el suministro

### Los sensores muestran "unknown"

**Solución**:
1. Espera a la primera actualización (hasta 1 minuto)
2. Comprueba los logs: **Configuración** → **Sistema** → **Registros**
3. Verifica conexión a internet

### Habilitar debug logging

Añade a tu `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.datadis: debug
```

Reinicia Home Assistant y consulta los logs para más detalles.

---

## Preguntas frecuentes

### ¿Cada cuánto se actualizan los datos?

Los datos se actualizan **una vez al día a las 00:00**. Datadis publica los datos con un desfase de D+1, por lo que los datos de ayer están disponibles hoy.

### ¿Puedo tener varios suministros?

Sí, pero necesitas añadir una instancia de la integración por cada suministro. Cada CUPS requiere una configuración separada.

### ¿Es segura mi contraseña?

La contraseña se almacena cifrada en Home Assistant. Solo se usa para autenticar contra Datadis y nunca se envía a terceros.

### ¿Funciona con autoconsumo?

Sí, la integración muestra los excedentes vertidos a la red (energía exportada) si tu instalación tiene autoconsumo con excedentes.

### ¿Qué tarifa tengo?

Puedes ver tu tarifa en el sensor `sensor.tarifa`. Las más comunes son:
- **2.0TD**: Tarifa con discriminación horaria 3 periodos
- **2.0A**: Tarifa sin discriminación horaria
- **2.0DHA**: Tarifa con discriminación horaria 2 periodos

### ¿Cómo obtengo los precios de mi tarifa?

Busca en tu factura eléctrica:
- **Término de energía**: Precio por kWh en cada periodo
- **Término de potencia**: Precio por kW y día
- **Potencia contratada**: kW contratados
- **Impuesto eléctrico**: Generalmente 5.11%
- **IVA**: 10% Canarias, 21% Península y Baleares

---

## Créditos

- **Datadis**: Plataforma oficial de datos eléctricos de España
- **API**: Basada en la documentación oficial de Datadis API v2
- **Home Assistant**: Software de domótica open source

---

## Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## Soporte

Si tienes problemas o sugerencias:

1. Abre un [issue en GitHub](https://github.com/perico85/datadis-homeassistant/issues)
2. Incluye los logs con debug activado
3. Indica tu versión de Home Assistant y la integración

---

**¡Disfruta monitorizando tu consumo eléctrico!** ⚡