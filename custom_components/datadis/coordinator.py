"""Coordinador de datos para Datadis."""
from datetime import datetime, timedelta, time, date
from typing import Any, Optional
import logging
import calendar

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change

from .api import DatadisAPI, ApiError, RateLimitError
from .const import DOMAIN, MEASUREMENT_HOURLY

_LOGGER = logging.getLogger(__name__)

# Hora de actualización diaria (00:00 - medianoche)
UPDATE_TIME = time(0, 0, 0)


def get_period_for_datetime(dt: datetime) -> str:
    """Determinar el periodo tarifario (P1/P2/P3) para una fecha y hora.

    Tramos horarios tarifa 2.0TD España:
    - P1 (Punta): 10:00-14:00 y 18:00-22:00 (lunes a viernes)
    - P2 (Llano): 08:00-10:00, 14:00-18:00 y 22:00-00:00 (lunes a viernes)
    - P3 (Valle): 00:00-08:00 (lunes a viernes) + todo el día fines de semana y festivos

    Args:
        dt: datetime a evaluar

    Returns:
        "P1", "P2" o "P3"
    """
    # Fines de semana (5=sábado, 6=domingo) son siempre Valle
    if dt.weekday() >= 5:
        return "P3"

    # Festivos nacionales España (días fijos)
    # Nota: Esto es una aproximación, los festivos locales pueden variar
    fixed_holidays = [
        (1, 1),   # Año Nuevo
        (1, 6),   # Reyes
        (5, 1),   # Trabajo
        (8, 15),  # Asunción
        (10, 12), # Hispanidad
        (11, 1),  # Todos los Santos
        (12, 6),  # Constitución
        (12, 8),  # Inmaculada
        (12, 25), # Navidad
    ]
    if (dt.month, dt.day) in fixed_holidays:
        return "P3"

    hour = dt.hour

    # Punta: 10-14 y 18-22
    if 10 <= hour < 14 or 18 <= hour < 22:
        return "P1"

    # Llano: 8-10, 14-18, 22-24
    if 8 <= hour < 10 or 14 <= hour < 18 or 22 <= hour < 24:
        return "P2"

    # Valle: 0-8
    return "P3"


def get_spanish_holidays(year: int) -> set:
    """Obtener festivos de España para un año (aproximación).

    Incluye festivos nacionales y algunos móviles.
    """
    holidays = set()

    # Festivos fijos
    fixed = [
        date(year, 1, 1),   # Año Nuevo
        date(year, 1, 6),   # Reyes
        date(year, 5, 1),   # Trabajo
        date(year, 8, 15),  # Asunción
        date(year, 10, 12), # Hispanidad
        date(year, 11, 1),  # Todos los Santos
        date(year, 12, 6),  # Constitución
        date(year, 12, 8),  # Inmaculada
        date(year, 12, 25), # Navidad
    ]
    holidays.update(fixed)

    # Festivos móviles (aproximación usando Pascua)
    # Jueves Santo y Viernes Santo (variable)
    # Esta es una aproximación simple
    easter = calculate_easter(year)
    holidays.add(easter - timedelta(days=3))  # Jueves Santo
    holidays.add(easter - timedelta(days=2))  # Viernes Santo

    return holidays


def calculate_easter(year: int) -> date:
    """Calcular fecha de Pascua para un año (algoritmo de Butcher)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


class DatadisCoordinator(DataUpdateCoordinator):
    """Coordinador para gestionar datos de Datadis."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: DatadisAPI,
        entry: ConfigEntry,
    ):
        """Inicializar coordinador."""
        self.api = api
        self.entry = entry
        self.cups = entry.data["cups"]
        self._distributor_code: str = None
        self._point_type: int = None
        self._contract_info: dict = {}
        self._unsub_update = None
        # Rango de fechas exitoso (cargado desde opciones persistentes)
        saved_range = entry.options.get("successful_date_range")
        if saved_range and len(saved_range) == 2:
            self._successful_date_range: Optional[tuple] = tuple(saved_range)
        else:
            self._successful_date_range = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.cups[:8]}",
            # Sin intervalo fijo, usamos actualización programada
            update_interval=None,
        )

    def _schedule_midnight_update(self):
        """Programar actualización diaria a medianoche."""
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

        @callback
        def _async_update_at_midnight(now):
            """Actualizar datos a medianoche."""
            _LOGGER.debug("Ejecutando actualización programada a medianoche")
            self.hass.async_create_task(self.async_request_refresh())

        # Programar para las 00:00 cada día
        self._unsub_update = async_track_time_change(
            self.hass,
            _async_update_at_midnight,
            hour=UPDATE_TIME.hour,
            minute=UPDATE_TIME.minute,
            second=UPDATE_TIME.second,
        )

    async def async_config_entry_first_refresh(self):
        """Primera actualización al configurar."""
        # Hacer la primera actualización inmediatamente
        await super().async_config_entry_first_refresh()
        # Programar actualizaciones diarias
        self._schedule_midnight_update()

    def _get_date_ranges_to_try(self) -> list:
        """Generar lista de rangos de fechas a probar.

        Genera rangos que incluyen los datos más recientes primero.
        Datadis actualiza datos con D+2 (datos de hace 2 días disponibles hoy).

        Returns:
            Lista de tuplas (start_date, end_date, descripcion) en formato YYYY/MM
        """
        today = datetime.now()
        ranges = []

        # Calcular el mes actual y meses anteriores
        first_of_this_month = today.replace(day=1)
        last_of_last_month = first_of_this_month - timedelta(days=1)
        first_of_last_month = last_of_last_month.replace(day=1)

        # Formatear fechas en formato AAAA/MM (que espera la API)
        this_month = today.strftime("%Y/%m")       # Ej: "2026/03"
        last_month = first_of_last_month.strftime("%Y/%m")  # Ej: "2026/02"

        # Rango 1: Este mes y anterior (preferido - datos más recientes)
        # Ej: ("2026/02", "2026/03") = desde febrero hasta marzo
        ranges.append((last_month, this_month, "mes actual y anterior"))

        # Rango 2: Este mes solo (por si el anterior falló)
        ranges.append((this_month, this_month, "solo mes actual"))

        # Rango 3: Mes anterior completo
        two_months_ago = (first_of_last_month - timedelta(days=30)).strftime("%Y/%m")
        ranges.append((two_months_ago, last_month, "solo mes anterior"))

        # Rango 4: Últimos 2 meses (sin el actual)
        ranges.append((two_months_ago, this_month, "últimos 2 meses"))

        # Rango 5: Hace 3-4 meses
        three_months_ago = (first_of_last_month - timedelta(days=60)).strftime("%Y/%m")
        four_months_ago = (first_of_last_month - timedelta(days=90)).strftime("%Y/%m")
        ranges.append((four_months_ago, three_months_ago, "hace 3-4 meses"))

        return ranges

    async def _fetch_consumption_with_retry(self) -> tuple:
        """Intentar obtener consumo probando diferentes rangos de fechas.

        Returns:
            Tupla (consumption_data, start_date, end_date) o (None, None, None) si todos fallan
        """
        # Si ya tenemos un rango exitoso guardado, usarlo
        if self._successful_date_range:
            start_date, end_date = self._successful_date_range
            _LOGGER.info("Usando rango guardado: %s - %s", start_date, end_date)
            try:
                data = await self.api.get_consumption_data(
                    cups=self.cups,
                    distributor_code=self._distributor_code,
                    start_date=start_date,
                    end_date=end_date,
                    measurement_type=MEASUREMENT_HOURLY,
                    point_type=self._point_type,
                )
                return data, start_date, end_date
            except RateLimitError:
                _LOGGER.warning("Rango guardado %s-%s dio error 429, probando nuevos rangos", start_date, end_date)

        # Probar diferentes rangos de fechas
        date_ranges = self._get_date_ranges_to_try()

        for start_date, end_date, description in date_ranges:
            try:
                _LOGGER.info("Probando rango %s: %s - %s", description, start_date, end_date)
                data = await self.api.get_consumption_data(
                    cups=self.cups,
                    distributor_code=self._distributor_code,
                    start_date=start_date,
                    end_date=end_date,
                    measurement_type=MEASUREMENT_HOURLY,
                    point_type=self._point_type,
                )
                # Éxito - guardar este rango para futuras consultas (persistir en opciones)
                self._successful_date_range = (start_date, end_date)
                self._save_successful_range(start_date, end_date)
                _LOGGER.info("Rango exitoso encontrado: %s - %s", start_date, end_date)
                return data, start_date, end_date
            except RateLimitError:
                _LOGGER.warning("Rango %s - %s ya consultado en 24h, probando siguiente", start_date, end_date)
                continue
            except ApiError as e:
                _LOGGER.warning("Error en rango %s - %s: %s", start_date, end_date, e)
                continue

        # Todos los rangos fallaron
        return None, None, None

    async def _fetch_max_power_with_retry(self, preferred_start: str, preferred_end: str) -> Any:
        """Intentar obtener potencia máxima probando diferentes rangos de fechas.

        Args:
            preferred_start: Fecha inicio preferida (del consumo exitoso)
            preferred_end: Fecha fin preferida (del consumo exitoso)

        Returns:
            Datos de potencia máxima o None si todos los rangos fallan
        """
        # Intentar primero con el rango preferido (el mismo que consumo)
        try:
            _LOGGER.info("Intentando potencia máxima con rango: %s - %s", preferred_start, preferred_end)
            data = await self.api.get_max_power(
                cups=self.cups,
                distributor_code=self._distributor_code,
                start_date=preferred_start,
                end_date=preferred_end,
            )
            _LOGGER.info("Potencia máxima obtenida con rango preferido")
            return data
        except RateLimitError:
            _LOGGER.warning("Rango %s-%s ya consultado para potencia máxima, probando otros", preferred_start, preferred_end)
        except ApiError as e:
            _LOGGER.warning("Error en potencia máxima con rango preferido: %s", e)

        # Intentar con otros rangos
        date_ranges = self._get_date_ranges_to_try()
        for start_date, end_date, description in date_ranges:
            # Saltar el rango que ya probamos
            if start_date == preferred_start and end_date == preferred_end:
                continue
            try:
                _LOGGER.info("Probando potencia máxima con rango %s: %s - %s", description, start_date, end_date)
                data = await self.api.get_max_power(
                    cups=self.cups,
                    distributor_code=self._distributor_code,
                    start_date=start_date,
                    end_date=end_date,
                )
                _LOGGER.info("Potencia máxima obtenida con rango alternativo: %s - %s", start_date, end_date)
                return data
            except RateLimitError:
                continue
            except ApiError as e:
                _LOGGER.warning("Error en potencia máxima: %s", e)
                continue

        _LOGGER.warning("No se pudo obtener potencia máxima con ningún rango")
        return None

    async def _async_update_data(self) -> dict:
        """Obtener datos actualizados de Datadis."""
        try:
            data = {
                "consumption": None,
                "contract": None,
                "max_power": None,
                "supply": None,
                "last_update": datetime.now().isoformat(),
                "date_range": None,
            }

            _LOGGER.debug("Actualizando datos para CUPS %s...", self.cups[:8])

            # Obtener suministros para tener código de distribuidora
            supplies = await self.api.get_supplies()
            supply = next(
                (s for s in supplies if s.get("cups") == self.cups),
                None
            )

            if not supply:
                raise UpdateFailed(f"No se encontró suministro para CUPS {self.cups}")

            data["supply"] = supply
            self._distributor_code = supply.get("distributorCode")
            self._point_type = supply.get("pointType")

            # Obtener detalle del contrato
            contract_data = await self.api.get_contract_detail(
                self.cups, self._distributor_code
            )

            if contract_data:
                data["contract"] = contract_data[0] if contract_data else None

            # Detectar número de periodos de la tarifa
            data["tariff_periods"] = self._detect_tariff_periods(data.get("contract") or {})

            # Obtener consumo con reintentoos de rangos de fechas
            consumption_data, start_date, end_date = await self._fetch_consumption_with_retry()

            if consumption_data:
                data["consumption"] = self._process_consumption(consumption_data)
                data["date_range"] = {"start": start_date, "end": end_date}
            else:
                _LOGGER.warning("No se pudo obtener datos de consumo con ningún rango de fechas")

            # Obtener potencia máxima (intentar con diferentes rangos si falla)
            # Nota: get-max-power también tiene límite de 24h por rango de fechas
            max_power_data = await self._fetch_max_power_with_retry(start_date, end_date)
            if max_power_data:
                data["max_power"] = self._process_max_power(max_power_data)

            _LOGGER.info(
                "Datos actualizados correctamente para %s - Próxima actualización: 00:00",
                self.cups[:8]
            )
            return data

        except RateLimitError as err:
            # Error 429: Ya se consultó en las últimas 24h - mantener datos anteriores
            _LOGGER.warning("Límite de consultas Datadis (429): %s. Manteniendo datos anteriores.", err)
            if self.data:
                return self.data
            raise UpdateFailed(f"Límite de consultas: {err}")
        except ApiError as err:
            raise UpdateFailed(f"Error de API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Error inesperado actualizando datos")
            raise UpdateFailed(f"Error inesperado: {err}") from err

    def _process_consumption(self, data: list) -> dict:
        """Procesar datos de consumo.

        Nota: Datadis tiene un desfase de D+1, es decir, los datos de ayer
        están disponibles hoy. El último dato disponible es de ayer.

        Calcula consumo por tramo horario (P1/P2/P3) según tarifa 2.0TD.
        """
        if not data:
            return {}

        # Ordenar por fecha descendente
        sorted_data = sorted(
            data,
            key=lambda x: f"{x.get('date', '')}{x.get('hour', '')}",
            reverse=True
        )

        # Obtener último consumo disponible (el más reciente en los datos)
        last_reading = sorted_data[0] if sorted_data else None

        # El último día disponible en los datos (D+1 = ayer)
        last_available_date = None
        if sorted_data:
            last_available_date = sorted_data[0].get("date")

        # Obtener todos los días únicos ordenados
        unique_dates = sorted(set(r.get("date") for r in data if r.get("date")), reverse=True)

        # El día anterior al último disponible (si existe)
        previous_day_date = unique_dates[1] if len(unique_dates) > 1 else None

        # Calcular consumo del último día disponible por tramo
        last_day_by_period = {"P1": 0.0, "P2": 0.0, "P3": 0.0}
        last_day_total = 0.0
        last_day_surplus = 0.0

        if last_available_date:
            for r in data:
                if r.get("date") == last_available_date:
                    consumption = float(r.get("consumptionKWh", 0) or 0)
                    surplus = float(r.get("surplusEnergyKWh", 0) or 0)
                    last_day_total += consumption
                    last_day_surplus += surplus

                    # Determinar periodo basado en la hora
                    hour_str = r.get("hour", "00:00")
                    try:
                        hour = int(hour_str.split(":")[0])
                        date_parts = last_available_date.split("/")
                        dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                        period = get_period_for_datetime(dt)
                        last_day_by_period[period] += consumption
                    except (ValueError, IndexError):
                        # Si no podemos parsear, asumir Llano
                        last_day_by_period["P2"] += consumption

        # Calcular consumo del día anterior por tramo
        previous_day_by_period = {"P1": 0.0, "P2": 0.0, "P3": 0.0}
        previous_day_total = 0.0
        previous_day_surplus = 0.0

        if previous_day_date:
            for r in data:
                if r.get("date") == previous_day_date:
                    consumption = float(r.get("consumptionKWh", 0) or 0)
                    surplus = float(r.get("surplusEnergyKWh", 0) or 0)
                    previous_day_total += consumption
                    previous_day_surplus += surplus

                    hour_str = r.get("hour", "00:00")
                    try:
                        hour = int(hour_str.split(":")[0])
                        date_parts = previous_day_date.split("/")
                        dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                        period = get_period_for_datetime(dt)
                        previous_day_by_period[period] += consumption
                    except (ValueError, IndexError):
                        previous_day_by_period["P2"] += consumption

        # Calcular consumo del mes actual por tramo
        current_data_month = None
        if last_available_date:
            current_data_month = last_available_date[:7]  # "YYYY/MM"

        month_by_period = {"P1": 0.0, "P2": 0.0, "P3": 0.0}
        month_total = 0.0
        month_surplus = 0.0

        if current_data_month:
            for r in data:
                if r.get("date", "").startswith(current_data_month):
                    consumption = float(r.get("consumptionKWh", 0) or 0)
                    surplus = float(r.get("surplusEnergyKWh", 0) or 0)
                    month_total += consumption
                    month_surplus += surplus

                    hour_str = r.get("hour", "00:00")
                    try:
                        hour = int(hour_str.split(":")[0])
                        date_str = r.get("date", "")
                        date_parts = date_str.split("/")
                        dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), hour)
                        period = get_period_for_datetime(dt)
                        month_by_period[period] += consumption
                    except (ValueError, IndexError):
                        month_by_period["P2"] += consumption

        return {
            "last_reading": last_reading,
            "last_available_date": last_available_date,
            "previous_day_date": previous_day_date,
            # Consumo del último día disponible (ayer según datos)
            "yesterday_kwh": round(last_day_total, 2),
            "yesterday_surplus_kwh": round(last_day_surplus, 2),
            "yesterday_p1_kwh": round(last_day_by_period["P1"], 2),
            "yesterday_p2_kwh": round(last_day_by_period["P2"], 2),
            "yesterday_p3_kwh": round(last_day_by_period["P3"], 2),
            # Consumo del día anterior al último (anteayer según datos)
            "day_before_yesterday_kwh": round(previous_day_total, 2),
            "day_before_yesterday_surplus_kwh": round(previous_day_surplus, 2),
            "day_before_yesterday_p1_kwh": round(previous_day_by_period["P1"], 2),
            "day_before_yesterday_p2_kwh": round(previous_day_by_period["P2"], 2),
            "day_before_yesterday_p3_kwh": round(previous_day_by_period["P3"], 2),
            # Consumo del mes
            "month_kwh": round(month_total, 2),
            "month_surplus_kwh": round(month_surplus, 2),
            "month_p1_kwh": round(month_by_period["P1"], 2),
            "month_p2_kwh": round(month_by_period["P2"], 2),
            "month_p3_kwh": round(month_by_period["P3"], 2),
            # Datos completos
            "readings": sorted_data,
            "all_readings": sorted_data,
        }

    def _detect_tariff_periods(self, contract: dict) -> dict:
        """Detectar número de periodos de la tarifa desde el contrato.

        Returns:
            dict con información de la tarifa:
            - num_periods: 1, 2 o 3
            - periods: lista de periodos activos ["P1"], ["P1", "P2"] o ["P1", "P2", "P3"]
            - tariff_code: código de tarifa (2.0TD, 2.0A, etc.)
        """
        # Obtener código de tarifa
        tariff_code = contract.get("codeFare") or ""

        # Mapeo de códigos de tarifa a número de periodos
        # 2.0TD = 3 periodos (Punta, Llano, Valle)
        # 2.0A = 2 periodos (Punta, Valle) - antigua
        # 2.0DHA = 2 periodos
        # 2.0DHS = 3 periodos
        # 2.1A, 2.1DHA, 2.1DHS = similar
        # 2.0, 2.0NA = 1 periodo (sin discriminación)

        tariff_period_map = {
            "2.0TD": 3, "2.0DHS": 3, "2.1DHS": 3, "3.0TD": 3,
            "2.0A": 2, "2.0DHA": 2, "2.1A": 2, "2.1DHA": 2,
            "2.0NA": 1, "2.0": 1, "2.1NA": 1, "2.1": 1,
        }

        # Detectar desde el código de tarifa
        num_periods = 3  # Por defecto 3 periodos (más común en tarifa 2.0TD actual)
        for code, periods in tariff_period_map.items():
            if code in tariff_code:
                num_periods = periods
                break

        # También verificar desde contractedPowerkW
        contracted_power = contract.get("contractedPowerkW") or []
        if len(contracted_power) == 1:
            num_periods = 1
        elif len(contracted_power) == 2:
            # Puede ser 2 periodos o 3 con P2=P3
            # Verificar timeDiscrimination
            time_disc = contract.get("timeDiscrimination", "")
            if "3" in str(time_disc) or "TD" in tariff_code:
                num_periods = 3
            else:
                num_periods = 2
        elif len(contracted_power) >= 3:
            num_periods = 3

        # Generar lista de periodos
        if num_periods == 1:
            periods = ["P1"]
        elif num_periods == 2:
            periods = ["P1", "P2"]
        else:
            periods = ["P1", "P2", "P3"]

        return {
            "num_periods": num_periods,
            "periods": periods,
            "tariff_code": tariff_code,
        }

    def _process_max_power(self, data: list) -> dict:
        """Procesar datos de potencia máxima por periodo."""
        if not data:
            return {}

        # Ordenar por fecha descendente
        sorted_data = sorted(
            data,
            key=lambda x: x.get("date", ""),
            reverse=True
        )

        # Agrupar por periodo
        by_period = {"P1": [], "P2": [], "P3": []}
        period_mapping = {
            "PUNTA": "P1", "P1": "P1",
            "LLANO": "P2", "P2": "P2",
            "VALLE": "P3", "P3": "P3",
        }

        for reading in sorted_data:
            period_raw = reading.get("period", "")
            # Mapear periodo a P1/P2/P3
            period = period_mapping.get(period_raw.upper(), "P2")
            if period in by_period:
                by_period[period].append(reading)

        # Obtener última potencia por periodo
        last_by_period = {}
        for period, readings in by_period.items():
            if readings:
                last_by_period[period] = readings[0]

        # Última potencia global
        last_max_power = sorted_data[0] if sorted_data else None

        return {
            "last_reading": last_max_power,
            "history": sorted_data[:30] if len(sorted_data) > 30 else sorted_data,
            "by_period": last_by_period,
            "all_by_period": by_period,
        }

    @property
    def distributor_code(self) -> str:
        """Código de distribuidora."""
        return self._distributor_code

    @property
    def point_type(self) -> int:
        """Tipo de punto de medida."""
        return self._point_type

    def _save_successful_range(self, start_date: str, end_date: str):
        """Guardar rango exitoso en las opciones de configuración."""
        new_options = {**self.entry.options}
        new_options["successful_date_range"] = [start_date, end_date]
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        _LOGGER.debug("Rango guardado en opciones: %s - %s", start_date, end_date)

    async def async_shutdown(self):
        """Limpiar al cerrar."""
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

    def _save_successful_range(self, start_date: str, end_date: str):
        """Guardar rango exitoso en las opciones de configuración."""
        new_options = dict(self.entry.options)
        new_options["successful_date_range"] = [start_date, end_date]
        # Actualizar opciones de forma asíncrona
        self.hass.async_create_task(
            self._update_options(new_options)
        )

    async def _update_options(self, new_options: dict):
        """Actualizar opciones de configuración."""
        self.hass.config_entries.async_update_entry(
            self.entry, options=new_options
        )