# Instrucciones para publicar en GitHub y HACS

## Estructura del repositorio

```
datadis-homeassistant/
├── .github/
│   └── workflows/
│       └── validate.yaml
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
│       ├── README.md
│       ├── README_EN.md
│       ├── CHANGELOG.md
│       └── LICENSE
├── README.md
└── LICENSE
```

## Pasos para publicar en GitHub

### 1. Crear el repositorio

1. Ve a [github.com](https://github.com) y crea un nuevo repositorio
2. Nombre sugerido: `datadis-homeassistant`
3. Descripción: "Home Assistant integration for Datadis (Spanish electricity data)"
4. Licencia: MIT

### 2. Subir el código

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/datadis-homeassistant.git
cd datadis-homeassistant

# Copiar los archivos
cp -r /home/beelink/Documentos/homeassistant/custom_components/datadis ./custom_components/

# Añadir archivos
git add .
git commit -m "Initial release - Datadis integration for Home Assistant"
git push origin main
```

### 3. Crear un release

1. Ve a tu repositorio en GitHub
2. Click en "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: "v1.0.0 - Initial Release"
5. Descripción: Copia el contenido de CHANGELOG.md
6. Click "Publish release"

### 4. Añadir a HACS

1. Ve a [hacs.xyz](https://hacs.xyz)
2. Login con tu cuenta de GitHub
3. Click en "Repository" → "Add Repository"
4. Introduce la URL de tu repositorio: `https://github.com/TU_USUARIO/datadis-homeassistant`
5. Selecciona la categoría: "Integration"
6. Espera a que se valide automáticamente

## Archivos requeridos para HACS

### hacs.json (obligatorio)

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

### manifest.json (obligatorio)

```json
{
    "domain": "datadis",
    "name": "Datadis",
    "codeowners": ["@TU_USUARIO"],
    "config_flow": true,
    "documentation": "https://github.com/TU_USUARIO/datadis-homeassistant",
    "integration_type": "device",
    "iot_class": "cloud_polling",
    "issue_tracker": "https://github.com/TU_USUARIO/datadis-homeassistant/issues",
    "requirements": ["aiohttp>=3.8.0"],
    "version": "1.0.0"
}
```

### README.md (obligatorio)

Debe incluir:
- Descripción de la integración
- Instrucciones de instalación
- Configuración
- Lista de sensores

## Instalación desde HACS (para usuarios)

1. Abre HACS en Home Assistant
2. Ve a **Integraciones** → **Explorar**
3. Busca "Datadis"
4. Click en **Descargar**
5. Reinicia Home Assistant
6. Ve a **Configuración** → **Dispositivos y Servicios**
7. Click en **Añadir integración** (+)
8. Busca "Datadis" y configúralo

## Instalación manual (alternativa)

1. Descarga el ZIP del release
2. Descomprime en `/config/custom_components/datadis/`
3. Reinicia Home Assistant
4. Configura la integración

## Verificar que funciona

1. Ve a **Herramientas para desarrolladores** → **Estados**
2. Busca sensores que empiecen por `sensor.datadis_`
3. Comprueba que aparecen los sensores de consumo, costes, etc.

## Actualizaciones

Para publicar una nueva versión:

1. Actualiza el código
2. Actualiza `version` en `manifest.json`
3. Actualiza `CHANGELOG.md`
4. Crea un nuevo tag: `v1.1.0`
5. El workflow de GitHub validará automáticamente los cambios

## Soporte

- GitHub Issues: Para bugs y peticiones de funcionalidad
- GitHub Discussions: Para preguntas y ayuda
- Home Assistant Community: Para soporte general
