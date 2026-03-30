"""Plataforma de botones para Datadis."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, POINT_TYPES
from .coordinator import DatadisCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurar botones Datadis."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        DatadisForceUpdateButton(coordinator, entry),
        DatadisResetAccumulatedButton(coordinator, entry),
    ]

    async_add_entities(entities)


class DatadisButton(CoordinatorEntity, ButtonEntity):
    """Botón base de Datadis."""

    def __init__(self, coordinator: DatadisCoordinator, entry: ConfigEntry) -> None:
        """Inicializar botón."""
        super().__init__(coordinator)
        self.entry = entry
        cups_short = entry.data["cups"][-4:].upper()
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }


class DatadisForceUpdateButton(DatadisButton):
    """Botón para forzar actualización de datos."""

    def __init__(self, coordinator: DatadisCoordinator, entry: ConfigEntry) -> None:
        """Inicializar botón."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_force_update"
        self._attr_name = "Forzar actualización"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Forzar actualización."""
        _LOGGER.info("Usuario solicitó actualización forzada")
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Retornar disponibilidad."""
        return self.coordinator.last_update_success


class DatadisResetAccumulatedButton(DatadisButton):
    """Botón para reiniciar acumulados."""

    def __init__(self, coordinator: DatadisCoordinator, entry: ConfigEntry) -> None:
        """Inicializar botón."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_reset_accumulated"
        self._attr_name = "Reiniciar acumulados"
        self._attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Reiniciar valores acumulados."""
        _LOGGER.info("Reiniciando sensores acumulativos")
        # Emitir evento para que los sensores escuchen
        self.hass.bus.fire(
            f"{DOMAIN}_reset_accumulated",
            {"entry_id": self.entry.entry_id}
        )

    @property
    def available(self) -> bool:
        """Retornar disponibilidad."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        """Atributos adicionales."""
        return {
            "warning": "Esto reiniciará los contadores acumulativos",
            "last_reset": None,  # Se actualizaría al pulsar
        }
