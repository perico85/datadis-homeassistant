"""Configuración vía UI para Datadis."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, CONF_NIF, CONF_PASSWORD, CONF_CUPS,
    CONF_ENERGY_PRICE_P1, CONF_ENERGY_PRICE_P2, CONF_ENERGY_PRICE_P3,
    CONF_POWER_PRICE_P1, CONF_POWER_PRICE_P2,
    CONF_CONTRACTED_POWER_P1, CONF_CONTRACTED_POWER_P2,
    CONF_ELECTRIC_TAX, CONF_VAT, CONF_SOCIAL_BONUS, CONF_EQUIPMENT_RENTAL,
    DEFAULT_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P3,
    DEFAULT_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P2,
    DEFAULT_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P2,
    DEFAULT_ELECTRIC_TAX, DEFAULT_VAT, DEFAULT_SOCIAL_BONUS, DEFAULT_EQUIPMENT_RENTAL,
)
from .api import DatadisAPI, AuthenticationError

import logging

_LOGGER = logging.getLogger(__name__)


class DatadisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow para Datadis."""

    VERSION = 2

    def __init__(self):
        """Inicializar flow."""
        self._nif = None
        self._password = None
        self._supplies = []
        self._selected_cups = None
        self._contract_data = None

    async def async_step_user(self, user_input: dict = None) -> FlowResult:
        """Primer paso: credenciales."""
        errors = {}

        if user_input:
            self._nif = user_input[CONF_NIF].strip().upper()
            self._password = user_input[CONF_PASSWORD]

            # Validar credenciales
            session = async_get_clientsession(self.hass)
            api = DatadisAPI(self._nif, self._password, session)

            try:
                await api._ensure_token()
                supplies = await api.get_supplies()
                await api.close()

                self._supplies = supplies

                if not supplies:
                    errors["base"] = "no_supplies"
                elif len(supplies) == 1:
                    # Solo un suministro, usar automáticamente
                    self._selected_cups = supplies[0].get("cups")
                    return await self.async_step_prices()
                else:
                    # Múltiples suministros, pedir selección
                    return await self.async_step_select_cups()

            except AuthenticationError as ex:
                _LOGGER.error("Error de autenticación Datadis: %s", ex)
                errors["base"] = "auth_failed"
            except Exception as ex:
                _LOGGER.error("Error conectando a Datadis: %s - Tipo: %s", ex, type(ex).__name__)
                error_msg = str(ex)
                if "AuthenticationError" in error_msg or "401" in error_msg or "403" in error_msg:
                    errors["base"] = "auth_failed"
                else:
                    errors["base"] = "connection_error"
            finally:
                await api.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NIF): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_select_cups(self, user_input: dict = None) -> FlowResult:
        """Segundo paso: seleccionar CUPS."""
        if user_input:
            self._selected_cups = user_input[CONF_CUPS]
            return await self.async_step_prices()

        # Lista de suministros para seleccionar
        cups_options = {}
        for supply in self._supplies:
            cups = supply.get("cups", "")
            distributor = supply.get("distributorName", "Desconocido")
            # Mostrar formato abreviado del CUPS
            label = f"{cups[:8]}...{cups[-4:]} ({distributor})"
            cups_options[cups] = label

        return self.async_show_form(
            step_id="select_cups",
            data_schema=vol.Schema({
                vol.Required(CONF_CUPS): vol.In(cups_options),
            }),
        )

    async def async_step_prices(self, user_input: dict = None) -> FlowResult:
        """Tercer paso: configurar precios de la tarifa."""
        errors = {}

        if user_input:
            # Crear la entrada con todos los datos
            return self.async_create_entry(
                title=f"Datadis - {self._nif[-4:]}",
                data={
                    CONF_NIF: self._nif,
                    CONF_PASSWORD: self._password,
                    CONF_CUPS: self._selected_cups,
                },
                options={
                    # Precios energía (€/kWh)
                    CONF_ENERGY_PRICE_P1: user_input.get(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1),
                    CONF_ENERGY_PRICE_P2: user_input.get(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2),
                    CONF_ENERGY_PRICE_P3: user_input.get(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3),
                    # Precios potencia (€/kW/día)
                    CONF_POWER_PRICE_P1: user_input.get(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1),
                    CONF_POWER_PRICE_P2: user_input.get(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2),
                    # Potencia contratada (kW)
                    CONF_CONTRACTED_POWER_P1: user_input.get(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1),
                    CONF_CONTRACTED_POWER_P2: user_input.get(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2),
                    # Impuestos
                    CONF_ELECTRIC_TAX: user_input.get(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX),
                    CONF_VAT: user_input.get(CONF_VAT, DEFAULT_VAT),
                    # Otros
                    CONF_SOCIAL_BONUS: user_input.get(CONF_SOCIAL_BONUS, DEFAULT_SOCIAL_BONUS),
                    CONF_EQUIPMENT_RENTAL: user_input.get(CONF_EQUIPMENT_RENTAL, DEFAULT_EQUIPMENT_RENTAL),
                }
            )

        # Mostrar formulario con valores por defecto
        return self.async_show_form(
            step_id="prices",
            data_schema=vol.Schema({
                # Precios energía (€/kWh)
                vol.Optional(CONF_ENERGY_PRICE_P1, default=DEFAULT_ENERGY_PRICE_P1): vol.Coerce(float),
                vol.Optional(CONF_ENERGY_PRICE_P2, default=DEFAULT_ENERGY_PRICE_P2): vol.Coerce(float),
                vol.Optional(CONF_ENERGY_PRICE_P3, default=DEFAULT_ENERGY_PRICE_P3): vol.Coerce(float),
                # Precios potencia (€/kW/día)
                vol.Optional(CONF_POWER_PRICE_P1, default=DEFAULT_POWER_PRICE_P1): vol.Coerce(float),
                vol.Optional(CONF_POWER_PRICE_P2, default=DEFAULT_POWER_PRICE_P2): vol.Coerce(float),
                # Potencia contratada (kW)
                vol.Optional(CONF_CONTRACTED_POWER_P1, default=DEFAULT_CONTRACTED_POWER_P1): vol.Coerce(float),
                vol.Optional(CONF_CONTRACTED_POWER_P2, default=DEFAULT_CONTRACTED_POWER_P2): vol.Coerce(float),
                # Impuestos
                vol.Optional(CONF_ELECTRIC_TAX, default=DEFAULT_ELECTRIC_TAX): vol.Coerce(float),
                vol.Optional(CONF_VAT, default=DEFAULT_VAT): vol.Coerce(float),
                # Otros
                vol.Optional(CONF_SOCIAL_BONUS, default=DEFAULT_SOCIAL_BONUS): vol.Coerce(float),
                vol.Optional(CONF_EQUIPMENT_RENTAL, default=DEFAULT_EQUIPMENT_RENTAL): vol.Coerce(float),
            }),
            errors=errors,
            description_placeholders={
                "cups": self._selected_cups[:8] + "..." + self._selected_cups[-4:] if self._selected_cups else "",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Obtener options flow."""
        return DatadisOptionsFlowHandler()


class DatadisOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow para Datadis."""

    async def async_step_init(self, user_input: dict = None) -> FlowResult:
        """Gestionar opciones de precios."""
        if user_input:
            # Preservar el rango de fechas exitoso si existe
            new_options = dict(user_input)
            old_range = self.config_entry.options.get("successful_date_range")
            if old_range:
                new_options["successful_date_range"] = old_range
            return self.async_create_entry(title="", data=new_options)

        # Obtener valores actuales
        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                # Precios energía (€/kWh)
                vol.Optional(
                    CONF_ENERGY_PRICE_P1,
                    default=options.get(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_ENERGY_PRICE_P2,
                    default=options.get(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_ENERGY_PRICE_P3,
                    default=options.get(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3)
                ): vol.Coerce(float),
                # Precios potencia (€/kW/día)
                vol.Optional(
                    CONF_POWER_PRICE_P1,
                    default=options.get(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_POWER_PRICE_P2,
                    default=options.get(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2)
                ): vol.Coerce(float),
                # Potencia contratada (kW)
                vol.Optional(
                    CONF_CONTRACTED_POWER_P1,
                    default=options.get(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_CONTRACTED_POWER_P2,
                    default=options.get(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2)
                ): vol.Coerce(float),
                # Impuestos
                vol.Optional(
                    CONF_ELECTRIC_TAX,
                    default=options.get(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_VAT,
                    default=options.get(CONF_VAT, DEFAULT_VAT)
                ): vol.Coerce(float),
                # Otros
                vol.Optional(
                    CONF_SOCIAL_BONUS,
                    default=options.get(CONF_SOCIAL_BONUS, DEFAULT_SOCIAL_BONUS)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_EQUIPMENT_RENTAL,
                    default=options.get(CONF_EQUIPMENT_RENTAL, DEFAULT_EQUIPMENT_RENTAL)
                ): vol.Coerce(float),
            }),
        )