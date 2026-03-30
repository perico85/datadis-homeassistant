"""Integración Datadis para Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS, CONF_ENERGY_PRICE_P1, CONF_ENERGY_PRICE_P2, CONF_ENERGY_PRICE_P3
from .coordinator import DatadisCoordinator
from .api import DatadisAPI

import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

# Esquemas para servicios
SERVICE_UPDATE_DATA = "update_data"
SERVICE_SET_ENERGY_PRICES = "set_energy_prices"
SERVICE_RESET_ACCUMULATED = "reset_accumulated"

SET_ENERGY_PRICES_SCHEMA = vol.Schema({
    vol.Optional("p1_price"): vol.Coerce(float),
    vol.Optional("p2_price"): vol.Coerce(float),
    vol.Optional("p3_price"): vol.Coerce(float),
})

RESET_ACCUMULATED_SCHEMA = vol.Schema({
    vol.Required("confirm"): str,
})


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

    # Registrar servicios
    await _async_register_services(hass, entry)

    return True


async def _async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Registrar servicios de la integración."""

    async def handle_update_data(call: ServiceCall):
        """Manejar servicio de actualización."""
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        _LOGGER.info("Servicio update_data llamado")
        await coordinator.async_request_refresh()

    async def handle_set_energy_prices(call: ServiceCall):
        """Manejar servicio de configuración de precios."""
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        
        new_options = dict(entry.options)
        if "p1_price" in call.data:
            new_options[CONF_ENERGY_PRICE_P1] = call.data["p1_price"]
        if "p2_price" in call.data:
            new_options[CONF_ENERGY_PRICE_P2] = call.data["p2_price"]
        if "p3_price" in call.data:
            new_options[CONF_ENERGY_PRICE_P3] = call.data["p3_price"]
        
        hass.config_entries.async_update_entry(entry, options=new_options)
        _LOGGER.info("Precios actualizados: P1=%s, P2=%s, P3=%s",
                     call.data.get("p1_price"), 
                     call.data.get("p2_price"),
                     call.data.get("p3_price"))
        
        # Forzar actualización para recalcular costes
        await coordinator.async_request_refresh()

    async def handle_reset_accumulated(call: ServiceCall):
        """Manejar servicio de reinicio de acumulados."""
        if call.data.get("confirm") == "RESET":
            hass.bus.fire(f"{DOMAIN}_reset_accumulated", {"entry_id": entry.entry_id})
            _LOGGER.info("Acumulados reiniciados para entry %s", entry.entry_id)
        else:
            _LOGGER.warning("Reinicio cancelado: confirmación no válida")

    # Registrar servicios
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_DATA, handle_update_data
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_ENERGY_PRICES, handle_set_energy_prices, schema=SET_ENERGY_PRICES_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_ACCUMULATED, handle_reset_accumulated, schema=RESET_ACCUMULATED_SCHEMA
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descargar una entrada de configuración."""
    _LOGGER.debug("Descargando entrada Datadis: %s", entry.entry_id)

    # Eliminar servicios
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_DATA)
    hass.services.async_remove(DOMAIN, SERVICE_SET_ENERGY_PRICES)
    hass.services.async_remove(DOMAIN, SERVICE_RESET_ACCUMULATED)

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