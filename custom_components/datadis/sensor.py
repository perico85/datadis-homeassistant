"""Plataforma de sensores para Datadis."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower, CURRENCY_EURO
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN, POINT_TYPES,
    CONF_ENERGY_PRICE_P1, CONF_ENERGY_PRICE_P2, CONF_ENERGY_PRICE_P3,
    CONF_POWER_PRICE_P1, CONF_POWER_PRICE_P2,
    CONF_CONTRACTED_POWER_P1, CONF_CONTRACTED_POWER_P2,
    CONF_ELECTRIC_TAX, CONF_VAT, CONF_SOCIAL_BONUS, CONF_EQUIPMENT_RENTAL,
    DEFAULT_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P3,
    DEFAULT_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P2,
    DEFAULT_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P2,
    DEFAULT_ELECTRIC_TAX, DEFAULT_VAT, DEFAULT_SOCIAL_BONUS, DEFAULT_EQUIPMENT_RENTAL,
)
from .coordinator import DatadisCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class DatadisSensorEntityDescription(SensorEntityDescription):
    """Descripción de sensor Datadis."""
    pass


# Periodos de tarifa
PERIOD_NAMES = {
    "P1": "Punta",
    "P2": "Llano",
    "P3": "Valle",
}

SENSOR_TYPES: tuple[DatadisSensorEntityDescription, ...] = (
    # === ENERGÍA IMPORTADA/EXPORTADA ===
    DatadisSensorEntityDescription(
        key="energy_imported",
        name="Energía Importada Red",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
    ),
    DatadisSensorEntityDescription(
        key="energy_exported",
        name="Energía Exportada Red",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
    ),

    # === COSTES ===
    DatadisSensorEntityDescription(
        key="cost_total",
        name="Coste Electricidad",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_energy_p1",
        name="Coste Energía Punta",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_energy_p2",
        name="Coste Energía Llano",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_energy_p3",
        name="Coste Energía Valle",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),

    # === COSTES POTENCIA ===
    DatadisSensorEntityDescription(
        key="cost_power_p1",
        name="Coste Potencia Punta",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_power_p2",
        name="Coste Potencia Valle",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),

    # === COSTES ADICIONALES ===
    DatadisSensorEntityDescription(
        key="cost_power_total",
        name="Coste Término Potencia",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_energy_total",
        name="Coste Término Energía",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_fixed",
        name="Coste Fijo Mensual",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),
    DatadisSensorEntityDescription(
        key="cost_invoice",
        name="Coste Total Factura",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:currency-eur",
    ),

    # === POTENCIA MÁXIMA ===
    DatadisSensorEntityDescription(
        key="max_power",
        name="Potencia Máxima",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    DatadisSensorEntityDescription(
        key="max_power_p1",
        name="Potencia Máxima Punta",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    DatadisSensorEntityDescription(
        key="max_power_p2",
        name="Potencia Máxima Llano",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    DatadisSensorEntityDescription(
        key="max_power_p3",
        name="Potencia Máxima Valle",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    DatadisSensorEntityDescription(
        key="contracted_power",
        name="Potencia Contratada",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),

    # === CONSUMO ÚLTIMO DÍA DISPONIBLE (AYER según datos D+1) ===
    DatadisSensorEntityDescription(
        key="consumption_yesterday",
        name="Consumo Último Día",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_yesterday_p1",
        name="Consumo Último Día Punta",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_yesterday_p2",
        name="Consumo Último Día Llano",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_yesterday_p3",
        name="Consumo Último Día Valle",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),

    # === CONSUMO DÍA ANTERIOR (ANTEAYER según datos) ===
    DatadisSensorEntityDescription(
        key="consumption_day_before",
        name="Consumo Día Anterior",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt-outline",
    ),
    DatadisSensorEntityDescription(
        key="consumption_day_before_p1",
        name="Consumo Día Anterior Punta",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt-outline",
    ),
    DatadisSensorEntityDescription(
        key="consumption_day_before_p2",
        name="Consumo Día Anterior Llano",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt-outline",
    ),
    DatadisSensorEntityDescription(
        key="consumption_day_before_p3",
        name="Consumo Día Anterior Valle",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt-outline",
    ),

    # === CONSUMO MES ===
    DatadisSensorEntityDescription(
        key="consumption_month",
        name="Consumo Mes",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_month_p1",
        name="Consumo Mes Punta",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_month_p2",
        name="Consumo Mes Llano",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    DatadisSensorEntityDescription(
        key="consumption_month_p3",
        name="Consumo Mes Valle",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),

    # === EXCEDENTES ===
    DatadisSensorEntityDescription(
        key="surplus_yesterday",
        name="Excedentes Último Día",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),
    DatadisSensorEntityDescription(
        key="surplus_month",
        name="Excedentes Mes",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),

    # === INFORMATIVOS ===
    DatadisSensorEntityDescription(
        key="last_reading",
        name="Última Lectura",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:meter-electric",
    ),
    DatadisSensorEntityDescription(
        key="tariff",
        name="Tarifa",
        icon="mdi:label",
    ),
    DatadisSensorEntityDescription(
        key="distributor",
        name="Distribuidora",
        icon="mdi:office-building",
    ),
    DatadisSensorEntityDescription(
        key="last_data_date",
        name="Última Fecha de Datos",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:calendar",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurar sensores Datadis."""
    coordinator: DatadisCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []
    for description in SENSOR_TYPES:
        entities.append(DatadisSensor(coordinator, entry, description))

    # Añadir sensores acumulativos para el Panel de Energía
    entities.append(DatadisAccumulatedEnergySensor(coordinator, entry, "import"))
    entities.append(DatadisAccumulatedEnergySensor(coordinator, entry, "export"))

    # Añadir sensores acumulativos por tramo para el Panel de Energía
    for period in ["P1", "P2", "P3"]:
        entities.append(DatadisAccumulatedEnergySensor(coordinator, entry, "import", period))
        entities.append(DatadisAccumulatedEnergySensor(coordinator, entry, "export", period))

    # Añadir sensores diarios por tramo para el Panel de Energía (se reinician con nuevo día)
    for period in ["P1", "P2", "P3"]:
        entities.append(DatadisDailyEnergySensor(coordinator, entry, "import", period))
        entities.append(DatadisDailyEnergySensor(coordinator, entry, "export", period))

    # Añadir sensores diarios totales
    entities.append(DatadisDailyEnergySensor(coordinator, entry, "import"))  # Total importado
    entities.append(DatadisDailyEnergySensor(coordinator, entry, "export"))  # Total exportado

    async_add_entities(entities)


class DatadisSensor(CoordinatorEntity, SensorEntity):
    """Sensor de Datadis."""

    entity_description: DatadisSensorEntityDescription

    def __init__(
        self,
        coordinator: DatadisCoordinator,
        entry: ConfigEntry,
        description: DatadisSensorEntityDescription,
    ) -> None:
        """Inicializar sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.entity_description = description

        cups_short = entry.data["cups"][-4:].upper()
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }

    def _get_option(self, key: str, default: float) -> float:
        """Obtener opción de configuración."""
        return float(self.entry.options.get(key, default))

    @property
    def native_value(self) -> Optional[float | str]:
        """Retornar valor del sensor."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        consumption = data.get("consumption") or {}
        contract = data.get("contract") or {}
        supply = data.get("supply") or {}
        max_power = data.get("max_power") or {}

        key = self.entity_description.key

        # === ENERGÍA IMPORTADA/EXPORTADA (mes actual) ===
        if key == "energy_imported":
            return consumption.get("month_kwh", 0)
        if key == "energy_exported":
            return consumption.get("month_surplus_kwh", 0)

        # === COSTES ===
        if key == "cost_total":
            return self._calculate_total_cost()
        if key == "cost_energy_p1":
            return self._calculate_period_cost("P1")
        if key == "cost_energy_p2":
            return self._calculate_period_cost("P2")
        if key == "cost_energy_p3":
            return self._calculate_period_cost("P3")

        # === COSTES POTENCIA ===
        if key == "cost_power_p1":
            return self._calculate_power_cost("P1")
        if key == "cost_power_p2":
            return self._calculate_power_cost("P2")
        if key == "cost_power_total":
            return self._calculate_power_cost_total()

        # === COSTES ADICIONALES ===
        if key == "cost_energy_total":
            return self._calculate_energy_cost_total()
        if key == "cost_fixed":
            return self._calculate_fixed_costs()
        if key == "cost_invoice":
            return self._calculate_invoice_total()

        # === POTENCIA MÁXIMA ===
        if key == "max_power":
            if max_power:
                last_reading = max_power.get("last_reading") or {}
                if last_reading:
                    value = last_reading.get("maxPower", 0)
                    return round(float(value) / 1000, 2) if value else None
            return None
        if key in ["max_power_p1", "max_power_p2", "max_power_p3"]:
            return self._get_max_power_by_period(key.split("_")[-1])
        if key == "contracted_power":
            power_from_contract = contract.get("contractedPowerkW") or []
            if power_from_contract and len(power_from_contract) > 0:
                return float(power_from_contract[0])
            return self._get_option(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1)

        # === CONSUMO ÚLTIMO DÍA (AYER según datos) ===
        if key == "consumption_yesterday":
            return consumption.get("yesterday_kwh")
        if key == "consumption_yesterday_p1":
            return consumption.get("yesterday_p1_kwh")
        if key == "consumption_yesterday_p2":
            return consumption.get("yesterday_p2_kwh")
        if key == "consumption_yesterday_p3":
            return consumption.get("yesterday_p3_kwh")

        # === CONSUMO DÍA ANTERIOR (ANTEAYER según datos) ===
        if key == "consumption_day_before":
            return consumption.get("day_before_yesterday_kwh")
        if key == "consumption_day_before_p1":
            return consumption.get("day_before_yesterday_p1_kwh")
        if key == "consumption_day_before_p2":
            return consumption.get("day_before_yesterday_p2_kwh")
        if key == "consumption_day_before_p3":
            return consumption.get("day_before_yesterday_p3_kwh")

        # === CONSUMO MES ===
        if key == "consumption_month":
            return consumption.get("month_kwh")
        if key == "consumption_month_p1":
            return consumption.get("month_p1_kwh")
        if key == "consumption_month_p2":
            return consumption.get("month_p2_kwh")
        if key == "consumption_month_p3":
            return consumption.get("month_p3_kwh")

        # === EXCEDENTES ===
        if key == "surplus_yesterday":
            return consumption.get("yesterday_surplus_kwh")
        if key == "surplus_month":
            return consumption.get("month_surplus_kwh")

        # === INFORMATIVOS ===
        if key == "last_reading":
            last_reading = consumption.get("last_reading") or {}
            if last_reading:
                return last_reading.get("consumptionKWh")
            return None

        if key == "tariff":
            return contract.get("codeFare") or contract.get("timeDiscrimination")

        if key == "distributor":
            return supply.get("distributor") or supply.get("distributorName")

        if key == "last_data_date":
            last_date = consumption.get("last_available_date")
            if last_date:
                try:
                    return datetime.strptime(last_date, "%Y/%m/%d").date()
                except ValueError:
                    return last_date
            return None

        return None

    def _get_max_power_by_period(self, period: str) -> Optional[float]:
        """Obtener potencia máxima por periodo."""
        if not self.coordinator.data:
            return None
        max_power = self.coordinator.data.get("max_power") or {}
        by_period = max_power.get("by_period") or {}

        if period in by_period:
            reading = by_period[period]
            value = reading.get("maxPower", 0)
            return round(float(value) / 1000, 2) if value else None
        return None

    def _calculate_total_cost(self) -> float:
        """Calcular coste total del mes."""
        if not self.coordinator.data:
            return 0.0

        consumption = self.coordinator.data.get("consumption") or {}
        contract = self.coordinator.data.get("contract") or {}

        # Consumo por periodo
        p1_kwh = float(consumption.get("month_p1_kwh", 0) or 0)
        p2_kwh = float(consumption.get("month_p2_kwh", 0) or 0)
        p3_kwh = float(consumption.get("month_p3_kwh", 0) or 0)

        # Precios energía
        price_p1 = self._get_option(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1)
        price_p2 = self._get_option(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2)
        price_p3 = self._get_option(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3)

        # Coste energía
        energy_cost = (p1_kwh * price_p1) + (p2_kwh * price_p2) + (p3_kwh * price_p3)

        # Potencia contratada
        power_p1 = self._get_option(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1)
        power_p2 = self._get_option(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2)

        # Precios potencia (€/kW/día)
        power_price_p1 = self._get_option(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1)
        power_price_p2 = self._get_option(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2)

        # Días del mes actual
        last_date = consumption.get("last_available_date")
        if last_date:
            try:
                date_obj = datetime.strptime(last_date, "%Y/%m/%d")
                days_in_month = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                days = days_in_month.day
            except ValueError:
                days = 30
        else:
            days = 30

        # Coste potencia
        power_cost = (power_p1 * power_price_p1 + power_p2 * power_price_p2) * days

        # Subtotal
        subtotal = energy_cost + power_cost

        # Impuestos
        electric_tax = self._get_option(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX)
        vat = self._get_option(CONF_VAT, DEFAULT_VAT)

        subtotal *= (1 + electric_tax / 100)
        total = subtotal * (1 + vat / 100)

        # Bono social y alquiler
        social_bonus = self._get_option(CONF_SOCIAL_BONUS, DEFAULT_SOCIAL_BONUS)
        equipment_rental = self._get_option(CONF_EQUIPMENT_RENTAL, DEFAULT_EQUIPMENT_RENTAL)

        total = total - social_bonus + equipment_rental

        return round(total, 2)

    def _calculate_period_cost(self, period: str) -> float:
        """Calcular coste de energía por periodo."""
        if not self.coordinator.data:
            return 0.0

        consumption = self.coordinator.data.get("consumption") or {}

        # Obtener kWh del periodo
        kwh_key = f"month_{period.lower()}_kwh"
        kwh = float(consumption.get(kwh_key, 0) or 0)

        # Precio del periodo
        if period == "P1":
            price = self._get_option(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1)
        elif period == "P3":
            price = self._get_option(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3)
        else:
            price = self._get_option(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2)

        # Impuestos
        electric_tax = self._get_option(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX)
        vat = self._get_option(CONF_VAT, DEFAULT_VAT)

        cost = kwh * price
        cost *= (1 + electric_tax / 100)
        cost *= (1 + vat / 100)

        return round(cost, 2)

    def _calculate_power_cost(self, period: str) -> float:
        """Calcular coste de potencia por periodo (mensual)."""
        if not self.coordinator.data:
            return 0.0

        consumption = self.coordinator.data.get("consumption") or {}

        # Días del mes actual
        last_date = consumption.get("last_available_date")
        if last_date:
            try:
                date_obj = datetime.strptime(last_date, "%Y/%m/%d")
                days_in_month = (date_obj.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                days = days_in_month.day
            except ValueError:
                days = 30
        else:
            days = 30

        # Potencia contratada y precio
        if period == "P1":
            power = self._get_option(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1)
            price = self._get_option(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1)
        else:  # P2 (en 2.0TD P2 y P3 usan la misma potencia y precio)
            power = self._get_option(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2)
            price = self._get_option(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2)

        # Coste: potencia × precio × días
        cost = power * price * days

        # Impuestos
        electric_tax = self._get_option(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX)
        vat = self._get_option(CONF_VAT, DEFAULT_VAT)

        cost *= (1 + electric_tax / 100)
        cost *= (1 + vat / 100)

        return round(cost, 2)

    def _calculate_power_cost_total(self) -> float:
        """Calcular coste total de potencia (P1 + P2)."""
        return round(self._calculate_power_cost("P1") + self._calculate_power_cost("P2"), 2)

    def _calculate_energy_cost_total(self) -> float:
        """Calcular coste total de energía (todos los periodos)."""
        if not self.coordinator.data:
            return 0.0

        tariff_periods = self.coordinator.data.get("tariff_periods") or {}
        periods = tariff_periods.get("periods", ["P1", "P2", "P3"])

        total = 0.0
        for period in periods:
            total += self._calculate_period_cost(period)

        return round(total, 2)

    def _calculate_fixed_costs(self) -> float:
        """Calcular costes fijos mensuales (alquiler + otros)."""
        # Días del mes (aproximado)
        days = 30

        # Alquiler de equipos (€/día)
        equipment_rental = self._get_option(CONF_EQUIPMENT_RENTAL, DEFAULT_EQUIPMENT_RENTAL)

        # Bono social (negativo, €/día)
        social_bonus = self._get_option(CONF_SOCIAL_BONUS, DEFAULT_SOCIAL_BONUS)

        # Coste fijo mensual
        fixed_monthly = (equipment_rental - social_bonus) * days

        # IVA
        vat = self._get_option(CONF_VAT, DEFAULT_VAT)
        fixed_monthly *= (1 + vat / 100)

        return round(fixed_monthly, 2)

    def _calculate_invoice_total(self) -> float:
        """Calcular total completo de la factura mensual."""
        # Energía
        energy_cost = self._calculate_energy_cost_total()

        # Potencia
        power_cost = self._calculate_power_cost_total()

        # Costes fijos (ya incluyen IVA)
        fixed_cost = self._calculate_fixed_costs()

        # Total
        total = energy_cost + power_cost + fixed_cost

        return round(total, 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Retornar atributos adicionales."""
        attrs = {}

        if not self.coordinator.data:
            return attrs

        data = self.coordinator.data
        supply = data.get("supply") or {}
        contract = data.get("contract") or {}
        consumption = data.get("consumption") or {}
        max_power = data.get("max_power") or {}

        attrs["cups"] = supply.get("cups")
        attrs["point_type"] = POINT_TYPES.get(supply.get("pointType"), "Desconocido")

        key = self.entity_description.key

        # Añadir fecha de datos a sensores de consumo
        if key.startswith("consumption_yesterday") or key.startswith("surplus_yesterday"):
            attrs["fecha_datos"] = consumption.get("last_available_date")
        elif key.startswith("consumption_day_before"):
            attrs["fecha_datos"] = consumption.get("previous_day_date")

        if key == "last_reading":
            last_reading = consumption.get("last_reading") or {}
            if last_reading:
                attrs["date"] = last_reading.get("date")
                attrs["hour"] = last_reading.get("hour")
                if last_reading.get("generationEnergyKWh"):
                    attrs["generation_kwh"] = last_reading.get("generationEnergyKWh")
                if last_reading.get("selfConsumptionEnergyKWh"):
                    attrs["self_consumption_kwh"] = last_reading.get("selfConsumptionEnergyKWh")

        if key == "max_power":
            if max_power:
                last_reading = max_power.get("last_reading") or {}
                if last_reading:
                    attrs["date"] = last_reading.get("date")
                    attrs["time"] = last_reading.get("time")
                    attrs["period"] = last_reading.get("period")

        if key in ["max_power_p1", "max_power_p2", "max_power_p3"]:
            period = key.split("_")[-1]
            by_period = max_power.get("by_period") or {}
            if period in by_period:
                reading = by_period[period]
                attrs["date"] = reading.get("date")
                attrs["time"] = reading.get("time")
                attrs["period_name"] = PERIOD_NAMES.get(period, period)

        if key == "contracted_power":
            attrs["power_p1"] = self._get_option(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1)
            attrs["power_p2"] = self._get_option(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2)
            power_from_contract = contract.get("contractedPowerkW") or []
            if power_from_contract:
                attrs["power_from_contract"] = power_from_contract

        if key == "cost_total":
            attrs["energy_price_p1"] = f"{self._get_option(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1):.4f} €/kWh"
            attrs["energy_price_p2"] = f"{self._get_option(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2):.4f} €/kWh"
            attrs["energy_price_p3"] = f"{self._get_option(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3):.4f} €/kWh"
            attrs["power_price_p1"] = f"{self._get_option(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1):.4f} €/kW/día"
            attrs["power_price_p2"] = f"{self._get_option(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2):.4f} €/kW/día"
            attrs["electric_tax"] = f"{self._get_option(CONF_ELECTRIC_TAX, DEFAULT_ELECTRIC_TAX):.2f}%"
            attrs["vat"] = f"{self._get_option(CONF_VAT, DEFAULT_VAT):.2f}%"

        if key == "cost_invoice":
            attrs["energy_cost"] = f"{self._calculate_energy_cost_total():.2f} €"
            attrs["power_cost"] = f"{self._calculate_power_cost_total():.2f} €"
            attrs["fixed_cost"] = f"{self._calculate_fixed_costs():.2f} €"
            attrs["total"] = f"{self._calculate_invoice_total():.2f} €"

        if key == "cost_power_total":
            attrs["power_p1"] = f"{self._get_option(CONF_CONTRACTED_POWER_P1, DEFAULT_CONTRACTED_POWER_P1):.2f} kW"
            attrs["power_p2"] = f"{self._get_option(CONF_CONTRACTED_POWER_P2, DEFAULT_CONTRACTED_POWER_P2):.2f} kW"
            attrs["price_p1"] = f"{self._get_option(CONF_POWER_PRICE_P1, DEFAULT_POWER_PRICE_P1):.4f} €/kW/día"
            attrs["price_p2"] = f"{self._get_option(CONF_POWER_PRICE_P2, DEFAULT_POWER_PRICE_P2):.4f} €/kW/día"

        if key == "cost_fixed":
            attrs["equipment_rental"] = f"{self._get_option(CONF_EQUIPMENT_RENTAL, DEFAULT_EQUIPMENT_RENTAL):.4f} €/día"
            attrs["social_bonus"] = f"{self._get_option(CONF_SOCIAL_BONUS, DEFAULT_SOCIAL_BONUS):.4f} €/día"
            attrs["vat"] = f"{self._get_option(CONF_VAT, DEFAULT_VAT):.2f}%"

        if key in ["cost_energy_p1", "cost_energy_p2", "cost_energy_p3"]:
            period = key.split("_")[-1]
            if period == "P1":
                price = self._get_option(CONF_ENERGY_PRICE_P1, DEFAULT_ENERGY_PRICE_P1)
                attrs["price"] = f"{price:.4f} €/kWh (Punta)"
            elif period == "P3":
                price = self._get_option(CONF_ENERGY_PRICE_P3, DEFAULT_ENERGY_PRICE_P3)
                attrs["price"] = f"{price:.4f} €/kWh (Valle)"
            else:
                price = self._get_option(CONF_ENERGY_PRICE_P2, DEFAULT_ENERGY_PRICE_P2)
                attrs["price"] = f"{price:.4f} €/kWh (Llano)"

        if key == "tariff":
            attrs["tariff_name"] = contract.get("timeDiscrimination")
            attrs["access_fare"] = contract.get("accessFare")
            attrs["valid_from"] = contract.get("startDate")
            if contract.get("selfConsumptionTypeCode"):
                attrs["self_consumption_type"] = contract.get("selfConsumptionTypeDesc")
            if contract.get("installedCapacityKW"):
                attrs["installed_capacity_kw"] = contract.get("installedCapacityKW")

        if key == "last_data_date":
            date_range = data.get("date_range") or {}
            attrs["date_range_start"] = date_range.get("start")
            attrs["date_range_end"] = date_range.get("end")

        return attrs

    @property
    def available(self) -> bool:
        """Retornar si el sensor está disponible."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class DatadisAccumulatedEnergySensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Sensor acumulativo de energía para el Panel de Energía."""

    def __init__(
        self,
        coordinator: DatadisCoordinator,
        entry: ConfigEntry,
        energy_type: str,
        period: str = None,
    ) -> None:
        """Inicializar sensor acumulativo."""
        super().__init__(coordinator)
        self.entry = entry
        self.energy_type = energy_type
        self.period = period

        cups_short = entry.data["cups"][-4:].upper()

        # Generar nombre y unique_id
        type_name = "Importada" if energy_type == "import" else "Exportada"
        if period:
            period_name = PERIOD_NAMES.get(period, period)
            self._attr_name = f"Energía Acumulada {type_name} {period_name}"
            self._attr_unique_id = f"{entry.entry_id}_accumulated_{energy_type}_{period.lower()}"
        else:
            self._attr_name = f"Energía Acumulada {type_name}"
            self._attr_unique_id = f"{entry.entry_id}_accumulated_{energy_type}"

        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:transmission-tower-import" if energy_type == "import" else "mdi:transmission-tower-export"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }

        self._accumulated_value = 0.0
        self._last_processed_date = None

    async def async_added_to_hass(self) -> None:
        """Restaurar estado anterior."""
        await super().async_added_to_hass()

        # Restaurar valor acumulado
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._accumulated_value = float(last_state.state)
                _LOGGER.info("Restaurado valor acumulado de %s: %.2f kWh", self._attr_name, self._accumulated_value)
            except ValueError:
                self._accumulated_value = 0.0

        # Restaurar última fecha procesada desde atributos
        if last_state and last_state.attributes.get("last_processed_date"):
            self._last_processed_date = last_state.attributes.get("last_processed_date")

    @property
    def native_value(self) -> float:
        """Retornar valor acumulado."""
        return round(self._accumulated_value, 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Retornar atributos adicionales."""
        return {
            "last_processed_date": self._last_processed_date,
            "energy_type": self.energy_type,
            "period": self.period,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Manejar actualización del coordinador."""
        if not self.coordinator.data:
            return

        consumption = self.coordinator.data.get("consumption") or {}
        readings = consumption.get("all_readings") or []

        if not readings:
            return

        # Obtener la fecha más reciente
        latest_date = consumption.get("last_available_date")

        # Si ya procesamos esta fecha, no hacer nada
        if latest_date == self._last_processed_date:
            return

        # Acumular consumo desde la última fecha procesada
        added_value = 0.0

        for reading in readings:
            reading_date = reading.get("date")
            reading_hour = reading.get("hour", "00:00")

            # Si ya procesamos esta fecha, saltar
            if self._last_processed_date and reading_date <= self._last_processed_date:
                continue

            # Determinar el periodo de esta lectura
            try:
                hour = int(reading_hour.split(":")[0])
                from .coordinator import get_period_for_datetime
                date_parts = reading_date.split("/")
                from datetime import datetime
                dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                reading_period = get_period_for_datetime(dt)
            except (ValueError, IndexError):
                reading_period = "P2"  # Default a Llano

            # Filtrar por periodo si es necesario
            if self.period and reading_period != self.period:
                continue

            # Obtener valor según tipo de energía
            if self.energy_type == "import":
                value = float(reading.get("consumptionKWh", 0) or 0)
            else:  # export
                value = float(reading.get("surplusEnergyKWh", 0) or 0)

            added_value += value

        # Actualizar valor acumulado
        if added_value > 0:
            self._accumulated_value += added_value
            self._last_processed_date = latest_date
            _LOGGER.info(
                "Añadidos %.2f kWh a %s. Total acumulado: %.2f kWh",
                added_value, self._attr_name, self._accumulated_value
            )

        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Retornar si el sensor está disponible."""
        return self.coordinator.last_update_success


class DatadisDailyEnergySensor(CoordinatorEntity, SensorEntity):
    """Sensor de energía diario por tramo que se reinicia con cada nuevo día de datos.

    Ideal para el Panel de Energía de Home Assistant.
    """

    def __init__(
        self,
        coordinator: DatadisCoordinator,
        entry: ConfigEntry,
        energy_type: str,
        period: str = None,
    ) -> None:
        """Inicializar sensor diario."""
        super().__init__(coordinator)
        self.entry = entry
        self.energy_type = energy_type
        self.period = period

        cups_short = entry.data["cups"][-4:].upper()

        # Generar nombre y unique_id
        type_name = "Importada" if energy_type == "import" else "Exportada"
        if period:
            period_name = PERIOD_NAMES.get(period, period)
            self._attr_name = f"Energía {type_name} {period_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}_{period.lower()}"
        else:
            self._attr_name = f"Energía {type_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}"

        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:transmission-tower-import" if energy_type == "import" else "mdi:transmission-tower-export"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }

        self._current_value = 0.0
        self._current_date = None

    @property
    def native_value(self) -> float:
        """Retornar valor del día."""
        return round(self._current_value, 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Retornar atributos adicionales."""
        attrs = {
            "energy_type": self.energy_type,
            "period": self.period,
            "data_date": self._current_date,
        }

        # Añadir información del tramo horario
        if self.period:
            attrs["period_name"] = PERIOD_NAMES.get(self.period, self.period)
            # Horarios del periodo según tarifa 2.0TD
            period_hours = {
                "P1": "10:00-14:00 y 18:00-22:00 (L-V)",
                "P2": "08:00-10:00, 14:00-18:00 y 22:00-24:00 (L-V)",
                "P3": "00:00-08:00 (L-V) y 24h (S-D y festivos)",
            }
            attrs["period_hours"] = period_hours.get(self.period, "")

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Manejar actualización del coordinador."""
        if not self.coordinator.data:
            return

        consumption = self.coordinator.data.get("consumption") or {}
        latest_date = consumption.get("last_available_date")

        # Si la fecha cambió, reiniciar el contador
        if latest_date != self._current_date:
            self._current_date = latest_date
            self._current_value = 0.0
            _LOGGER.info(
                "Nuevo día detectado (%s), reiniciando sensor %s",
                latest_date, self._attr_name
            )

        # Obtener el valor según tipo y periodo
        if self.energy_type == "import":
            if self.period == "P1":
                self._current_value = float(consumption.get("yesterday_p1_kwh", 0) or 0)
            elif self.period == "P2":
                self._current_value = float(consumption.get("yesterday_p2_kwh", 0) or 0)
            elif self.period == "P3":
                self._current_value = float(consumption.get("yesterday_p3_kwh", 0) or 0)
            else:
                # Total sin periodo
                self._current_value = float(consumption.get("yesterday_kwh", 0) or 0)
        else:  # export
            if self.period == "P1":
                # Excedentes por periodo - calcular desde readings
                self._current_value = self._calculate_surplus_by_period("P1", consumption)
            elif self.period == "P2":
                self._current_value = self._calculate_surplus_by_period("P2", consumption)
            elif self.period == "P3":
                self._current_value = self._calculate_surplus_by_period("P3", consumption)
            else:
                # Total exportado
                self._current_value = float(consumption.get("yesterday_surplus_kwh", 0) or 0)

        self.async_write_ha_state()

    def _calculate_surplus_by_period(self, period: str, consumption: dict) -> float:
        """Calcular excedentes por periodo desde las lecturas."""
        readings = consumption.get("all_readings") or []
        latest_date = consumption.get("last_available_date")

        if not latest_date:
            return 0.0

        total = 0.0
        for reading in readings:
            if reading.get("date") != latest_date:
                continue

            # Determinar periodo de la lectura
            hour_str = reading.get("hour", "00:00")
            try:
                hour = int(hour_str.split(":")[0])
                date_parts = latest_date.split("/")
                dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                from .coordinator import get_period_for_datetime
                reading_period = get_period_for_datetime(dt)
            except (ValueError, IndexError):
                reading_period = "P2"

            if reading_period == period:
                total += float(reading.get("surplusEnergyKWh", 0) or 0)

        return round(total, 2)

    @property
    def available(self) -> bool:
        """Retornar si el sensor está disponible."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class DatadisDailyEnergySensor(CoordinatorEntity, SensorEntity):
    """Sensor de energía diario por tramo que se reinicia con cada nuevo día de datos.

    Ideal para el Panel de Energía de Home Assistant.
    """

    def __init__(
        self,
        coordinator: DatadisCoordinator,
        entry: ConfigEntry,
        energy_type: str,
        period: str = None,
    ) -> None:
        """Inicializar sensor diario."""
        super().__init__(coordinator)
        self.entry = entry
        self.energy_type = energy_type
        self.period = period

        cups_short = entry.data["cups"][-4:].upper()

        # Generar nombre y unique_id
        type_name = "Importada" if energy_type == "import" else "Exportada"
        if period:
            period_name = PERIOD_NAMES.get(period, period)
            self._attr_name = f"Energía {type_name} {period_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}_{period.lower()}"
        else:
            self._attr_name = f"Energía {type_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}"

        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:transmission-tower-import" if energy_type == "import" else "mdi:transmission-tower-export"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }

        self._current_value = 0.0
        self._current_date = None

    @property
    def native_value(self) -> float:
        """Retornar valor del día."""
        return round(self._current_value, 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Retornar atributos adicionales."""
        attrs = {
            "energy_type": self.energy_type,
            "period": self.period,
            "data_date": self._current_date,
        }

        # Añadir información del tramo horario
        if self.period:
            attrs["period_name"] = PERIOD_NAMES.get(self.period, self.period)
            # Horarios del periodo según tarifa 2.0TD
            period_hours = {
                "P1": "10:00-14:00 y 18:00-22:00 (L-V)",
                "P2": "08:00-10:00, 14:00-18:00 y 22:00-24:00 (L-V)",
                "P3": "00:00-08:00 (L-V) y 24h (S-D y festivos)",
            }
            attrs["period_hours"] = period_hours.get(self.period, "")

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Manejar actualización del coordinador."""
        if not self.coordinator.data:
            return

        consumption = self.coordinator.data.get("consumption") or {}
        latest_date = consumption.get("last_available_date")

        # Si la fecha cambió, reiniciar el contador
        if latest_date != self._current_date:
            self._current_date = latest_date
            self._current_value = 0.0
            _LOGGER.info(
                "Nuevo día detectado (%s), reiniciando sensor %s",
                latest_date, self._attr_name
            )

        # Obtener el valor según tipo y periodo
        if self.energy_type == "import":
            if self.period == "P1":
                self._current_value = float(consumption.get("yesterday_p1_kwh", 0) or 0)
            elif self.period == "P2":
                self._current_value = float(consumption.get("yesterday_p2_kwh", 0) or 0)
            elif self.period == "P3":
                self._current_value = float(consumption.get("yesterday_p3_kwh", 0) or 0)
            else:
                # Total sin periodo
                self._current_value = float(consumption.get("yesterday_kwh", 0) or 0)
        else:  # export
            if self.period == "P1":
                # Excedentes por periodo - calcular desde readings
                self._current_value = self._calculate_surplus_by_period("P1", consumption)
            elif self.period == "P2":
                self._current_value = self._calculate_surplus_by_period("P2", consumption)
            elif self.period == "P3":
                self._current_value = self._calculate_surplus_by_period("P3", consumption)
            else:
                # Total exportado
                self._current_value = float(consumption.get("yesterday_surplus_kwh", 0) or 0)

        self.async_write_ha_state()

    def _calculate_surplus_by_period(self, period: str, consumption: dict) -> float:
        """Calcular excedentes por periodo desde las lecturas."""
        readings = consumption.get("all_readings") or []
        latest_date = consumption.get("last_available_date")

        if not latest_date:
            return 0.0

        total = 0.0
        for reading in readings:
            if reading.get("date") != latest_date:
                continue

            # Determinar periodo de la lectura
            hour_str = reading.get("hour", "00:00")
            try:
                hour = int(hour_str.split(":")[0])
                date_parts = latest_date.split("/")
                dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                from .coordinator import get_period_for_datetime
                reading_period = get_period_for_datetime(dt)
            except (ValueError, IndexError):
                reading_period = "P2"

            if reading_period == period:
                total += float(reading.get("surplusEnergyKWh", 0) or 0)

        return round(total, 2)

    @property
    def available(self) -> bool:
        """Retornar si el sensor está disponible."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class DatadisDailyEnergySensor(CoordinatorEntity, SensorEntity):
    """Sensor de energía diario por tramo que se reinicia con cada nuevo día de datos.

    Ideal para el Panel de Energía de Home Assistant.
    El sensor muestra el consumo del último día disponible y se reinicia
    automáticamente cuando Datadis proporciona datos de un nuevo día.
    """

    def __init__(
        self,
        coordinator: DatadisCoordinator,
        entry: ConfigEntry,
        energy_type: str,
        period: str = None,
    ) -> None:
        """Inicializar sensor diario."""
        super().__init__(coordinator)
        self.entry = entry
        self.energy_type = energy_type
        self.period = period

        cups_short = entry.data["cups"][-4:].upper()

        # Generar nombre y unique_id
        type_name = "Importada" if energy_type == "import" else "Exportada"
        if period:
            period_name = PERIOD_NAMES.get(period, period)
            self._attr_name = f"Energía {type_name} {period_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}_{period.lower()}"
        else:
            self._attr_name = f"Energía {type_name}"
            self._attr_unique_id = f"{entry.entry_id}_daily_{energy_type}"

        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:transmission-tower-import" if energy_type == "import" else "mdi:transmission-tower-export"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["cups"])},
            "name": f"Datadis {cups_short}",
            "manufacturer": "Datadis",
            "model": "Punto de Suministro",
            "configuration_url": "https://datadis.es",
        }

        self._current_value = 0.0
        self._current_date = None

    @property
    def native_value(self) -> float:
        """Retornar valor del día."""
        return round(self._current_value, 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Retornar atributos adicionales."""
        attrs = {
            "energy_type": self.energy_type,
            "period": self.period,
            "data_date": self._current_date,
        }

        # Añadir información del tramo horario
        if self.period:
            attrs["period_name"] = PERIOD_NAMES.get(self.period, self.period)
            # Horarios del periodo según tarifa 2.0TD
            period_hours = {
                "P1": "10:00-14:00 y 18:00-22:00 (L-V)",
                "P2": "08:00-10:00, 14:00-18:00 y 22:00-24:00 (L-V)",
                "P3": "00:00-08:00 (L-V) y 24h (S-D y festivos)",
            }
            attrs["period_hours"] = period_hours.get(self.period, "")

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Manejar actualización del coordinador."""
        if not self.coordinator.data:
            return

        consumption = self.coordinator.data.get("consumption") or {}
        latest_date = consumption.get("last_available_date")

        # Si la fecha cambió, reiniciar el contador
        if latest_date != self._current_date:
            self._current_date = latest_date
            self._current_value = 0.0
            _LOGGER.info(
                "Nuevo día detectado (%s), reiniciando sensor %s",
                latest_date, self._attr_name
            )

        # Obtener el valor según tipo y periodo
        if self.energy_type == "import":
            if self.period == "P1":
                self._current_value = float(consumption.get("yesterday_p1_kwh", 0) or 0)
            elif self.period == "P2":
                self._current_value = float(consumption.get("yesterday_p2_kwh", 0) or 0)
            elif self.period == "P3":
                self._current_value = float(consumption.get("yesterday_p3_kwh", 0) or 0)
            else:
                # Total sin periodo
                self._current_value = float(consumption.get("yesterday_kwh", 0) or 0)
        else:  # export
            if self.period == "P1":
                # Excedentes por periodo - calcular desde readings
                self._current_value = self._calculate_surplus_by_period("P1", consumption)
            elif self.period == "P2":
                self._current_value = self._calculate_surplus_by_period("P2", consumption)
            elif self.period == "P3":
                self._current_value = self._calculate_surplus_by_period("P3", consumption)
            else:
                # Total exportado
                self._current_value = float(consumption.get("yesterday_surplus_kwh", 0) or 0)

        self.async_write_ha_state()

    def _calculate_surplus_by_period(self, period: str, consumption: dict) -> float:
        """Calcular excedentes por periodo desde las lecturas."""
        readings = consumption.get("all_readings") or []
        latest_date = consumption.get("last_available_date")

        if not latest_date:
            return 0.0

        total = 0.0
        for reading in readings:
            if reading.get("date") != latest_date:
                continue

            # Determinar periodo de la lectura
            hour_str = reading.get("hour", "00:00")
            try:
                hour = int(hour_str.split(":")[0])
                date_parts = latest_date.split("/")
                dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                from .coordinator import get_period_for_datetime
                reading_period = get_period_for_datetime(dt)
            except (ValueError, IndexError):
                reading_period = "P2"

            if reading_period == period:
                total += float(reading.get("surplusEnergyKWh", 0) or 0)

        return round(total, 2)

    @property
    def available(self) -> bool:
        """Retornar si el sensor está disponible."""
        return self.coordinator.last_update_success and self.coordinator.data is not None