# Instalación vía HACS

## Pasos para publicar en HACS

### 1. Crear repositorio en GitHub

1. Crea un nuevo repositorio en GitHub: `datadis-homeassistant`
2. Sube todos los archivos de la integración

### 2. Estructura del repositorio

```
datadis-homeassistant/
├── custom_components/
│   └── datadis/
│       ├── __init__.py
│       ├── api.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json
│       ├── sensor.py
│       ├── translations/
│       │   ├── en.json
│       │   └── es.json
│       ├── hacs.json
│       └── README.md
├── LICENSE
├── README.md
└── hacs.json
```

**NOTA**: La estructura tiene `custom_components/datadis/` dentro del repo.

### 3. Archivo hacs.json en la raíz

```json
{
    "name": "Datadis",
    "content_in_root": false,
    "zip_release": true,
    "filename": "datadis.zip",
    "country": ["ES"],
    "domains": ["sensor"],
    "homeassistant": "2023.1.0",
    "hacs": "1.28.0",
    "iot_class": "cloud_polling"
}
```

### 4. Publicar release

1. Ve a tu repositorio en GitHub
2. Haz clic en "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `v1.0.0 - Initial release`
5. Publica el release

### 5. Añadir a HACS

#### Método 1: Tienda de HACS (recomendado para todos)

Una vez publicado, los usuarios pueden:

1. Abrir HACS en Home Assistant
2. Ir a "Integraciones" → "Explorar"
3. Buscar "Datadis"
4. Hacer clic en "Descargar"

#### Método 2: Repositorio personalizado (mientras no esté en la tienda)

1. En HACS, ir a "Integraciones"
2. Clic en los 3 puntos → "Repositorios personalizados"
3. Añadir URL del repositorio: `https://github.com/tu-usuario/datadis-homeassistant`
4. Categoría: "Integración"
5. Clic en "Añadir"
6. Buscar "Datadis" y descargar

## Para usuarios finales

### Instalación

1. HACS → Integraciones → Explorar
2. Buscar "Datadis"
3. Descargar e instalar
4. Reiniciar Home Assistant

### Configuración

1. Configuración → Dispositivos y Servicios
2. Añadir integración → Buscar "Datadis"
3. Introducir NIF y contraseña de Datadis
4. Seleccionar CUPS
5. Configurar precios de la tarifa

## Actualizaciones

HACS notificará automáticamente cuando haya una nueva versión disponible.
