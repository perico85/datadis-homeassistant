"""Diagnósticos para Datadis."""
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.diagnostics import async_redact_data

from .const import DOMAIN, CONF_PASSWORD
from .coordinator import DatadisCoordinator

TO_REDACT = {CONF_PASSWORD, "password", "token", "access_token", "secret"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> dict[str, Any]:
    """Retornar diagnósticos para la entrada de configuración."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id].get("coordinator")  # type: DatadisCoordinator

    diagnostics = {
        "entry_id": config_entry.entry_id,
        "version": config_entry.version,
        "data": async_redact_data(dict(config_entry.data), TO_REDACT),
        "options": async_redact_data(dict(config_entry.options), TO_REDACT),
    }

    if coordinator:
        diagnostics["coordinator"] = {
            "last_update_success": coordinator.last_update_success,
            "last_update": coordinator.last_update.isoformat() if coordinator.last_update else None,
            "update_interval": str(coordinator.update_interval) if coordinator.update_interval else None,
        }

        if coordinator.data:
            data = coordinator.data
            consumption = data.get("consumption") or {}
            supply = data.get("supply") or {}
            contract = data.get("contract") or {}

            diagnostics["data_summary"] = {
                "cups_prefix": supply.get("cups", "")[:8] + "..." if supply.get("cups") else None,
                "distributor": supply.get("distributorName"),
                "last_available_date": consumption.get("last_available_date"),
                "tariff": contract.get("codeFare"),
                "has_consumption_data": bool(consumption.get("readings")),
                "readings_count": len(consumption.get("readings", [])),
                "month_total_kwh": consumption.get("month_kwh"),
            }

    return diagnostics
