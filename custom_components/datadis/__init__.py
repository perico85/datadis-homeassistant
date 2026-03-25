"""Integración Datadis para Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS
from .coordinator import DatadisCoordinator
from .api import DatadisAPI

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurar integración desde una entrada de configuración."""
    _LOGGER.debug("Configurando entrada Datadis: %s", entry.entry_id)

    # Crear cliente API
    session = async_get_clientsession(hass)
    api = DatadisAPI(
        nif=entry.data["nif"],
        password=entry.data["password"],
        session=session,
    )

    # Crear coordinador
    coordinator = DatadisCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()

    # Guardar en hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    # Configurar plataformas
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descargar una entrada de configuración."""
    _LOGGER.debug("Descargando entrada Datadis: %s", entry.entry_id)

    # Descargar plataformas
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Cerrar coordinador y API
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        api = hass.data[DOMAIN][entry.entry_id]["api"]

        # Limpiar scheduler del coordinador
        await coordinator.async_shutdown()
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrar entrada a nueva versión."""
    _LOGGER.debug("Migrando entrada Datadis desde versión %s", entry.version)

    if entry.version == 1:
        # Migrar de versión 1 a 2: añadir opciones de precios
        new_options = {
            "energy_price_p1": 0.150,
            "energy_price_p2": 0.120,
            "energy_price_p3": 0.080,
            "power_price_p1": 0.097,
            "power_price_p2": 0.027,
            "contracted_power_p1": 3.45,
            "contracted_power_p2": 3.45,
            "electric_tax": 5.11,
            "vat": 21.0,
            "social_bonus": 0.019,
            "equipment_rental": 0.027,
        }

        hass.config_entries.async_update_entry(entry, options=new_options, version=2)
        _LOGGER.debug("Migración a versión 2 completada")

    return True