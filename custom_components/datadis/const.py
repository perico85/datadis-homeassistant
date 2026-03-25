"""Constantes para la integración Datadis."""

from typing import Final

# Dominio
DOMAIN: Final = "datadis"

# Configuración
CONF_NIF: Final = "nif"
CONF_PASSWORD: Final = "password"
CONF_CUPS: Final = "cups"

# Configuración de precios
CONF_ENERGY_PRICE_P1: Final = "energy_price_p1"  # Punta
CONF_ENERGY_PRICE_P2: Final = "energy_price_p2"  # Llano
CONF_ENERGY_PRICE_P3: Final = "energy_price_p3"  # Valle
CONF_POWER_PRICE_P1: Final = "power_price_p1"  # Punta (€/kW/día)
CONF_POWER_PRICE_P2: Final = "power_price_p2"  # Valle (€/kW/día)
CONF_CONTRACTED_POWER_P1: Final = "contracted_power_p1"  # kW
CONF_CONTRACTED_POWER_P2: Final = "contracted_power_p2"  # kW
CONF_ELECTRIC_TAX: Final = "electric_tax"  # % (impuesto eléctrico)
CONF_VAT: Final = "vat"  # % (IVA)
CONF_SOCIAL_BONUS: Final = "social_bonus"  # €/día
CONF_EQUIPMENT_RENTAL: Final = "equipment_rental"  # €/día

# Rango de fechas exitoso (para evitar error 429)
CONF_SUCCESSFUL_DATE_RANGE: Final = "successful_date_range"

# Valores por defecto (tarifa 2.0TD típica)
DEFAULT_ENERGY_PRICE_P1: Final = 0.150  # €/kWh Punta
DEFAULT_ENERGY_PRICE_P2: Final = 0.120  # €/kWh Llano
DEFAULT_ENERGY_PRICE_P3: Final = 0.080  # €/kWh Valle
DEFAULT_POWER_PRICE_P1: Final = 0.097  # €/kW/día Punta
DEFAULT_POWER_PRICE_P2: Final = 0.027  # €/kW/día Valle
DEFAULT_CONTRACTED_POWER_P1: Final = 3.45  # kW
DEFAULT_CONTRACTED_POWER_P2: Final = 3.45  # kW
DEFAULT_ELECTRIC_TAX: Final = 5.11  # %
DEFAULT_VAT: Final = 21.0  # %
DEFAULT_SOCIAL_BONUS: Final = 0.019  # €/día
DEFAULT_EQUIPMENT_RENTAL: Final = 0.027  # €/día

# Endpoints de la API
DATADIS_AUTH_URL: Final = "https://datadis.es/nikola-auth/tokens/login"
DATADIS_API_URL: Final = "https://datadis.es/api-private/api"

# Tiempos de actualización
# Los datos de Datadis son D+1, se actualizan una vez al día a las 00:00

# Tipos de medida
MEASUREMENT_HOURLY: Final = 0
MEASUREMENT_QUARTERLY: Final = 1

# Tipos de punto
POINT_TYPES: Final = {
    1: "Punto de medida de frontera",
    2: "Punto de medida de generación",
    3: "Punto de medida de consumo",
    4: "Punto de medida de consumo con generación",
    5: "Punto de medida de autoconsumo",
}

# Periodos de tarifa (para 2.0TD)
# P1 = Punta, P2 = Llano, P3 = Valle
TARIFF_PERIODS: Final = {
    "P1": "Punta",
    "P2": "Llano",
    "P3": "Valle",
}

# Plataformas
PLATFORMS: Final = ["sensor"]