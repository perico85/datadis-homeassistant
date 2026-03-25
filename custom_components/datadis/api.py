"""Cliente API para Datadis."""
import aiohttp
from datetime import datetime, timedelta
from typing import Any, Optional
import logging
import json

from .const import DATADIS_API_URL, DATADIS_AUTH_URL

_LOGGER = logging.getLogger(__name__)


class DatadisAPI:
    """Cliente para la API de Datadis."""

    def __init__(self, nif: str, password: str, session: aiohttp.ClientSession = None):
        """Inicializar cliente API."""
        self._nif = nif
        self._password = password
        self._token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._session = session or aiohttp.ClientSession()
        self._own_session = session is None

    async def close(self):
        """Cerrar sesión HTTP."""
        if self._own_session:
            await self._session.close()

    async def _ensure_token(self) -> str:
        """Asegurar que tenemos un token válido."""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token

        # Obtener nuevo token
        _LOGGER.debug("Obteniendo nuevo token de Datadis")

        # Probar primero con form-data (formato estándar)
        data = {"username": self._nif, "password": self._password}

        async with self._session.post(
            DATADIS_AUTH_URL,
            data=data,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error("Error de autenticación Datadis (status %d): %s", response.status, error_text)
                raise AuthenticationError(f"Error de autenticación: {response.status} - {error_text}")

            # El token viene en formato "Bearer token" o solo "token"
            token_data = await response.text()
            _LOGGER.debug("Respuesta auth raw: %s", token_data[:200] if token_data else "vacío")

            # Limpiar comillas y espacios
            token_clean = token_data.strip().strip('"')

            # Si viene con "Bearer " al inicio, quitarselo para almacenarlo limpio
            if token_clean.startswith("Bearer "):
                self._token = token_clean[7:]  # Quitar "Bearer " del inicio
            else:
                self._token = token_clean

            # El token expira en 1 día aproximadamente
            self._token_expires = datetime.now() + timedelta(hours=23)

            _LOGGER.debug("Token obtenido correctamente: %s...", self._token[:10] if self._token else "None")
            return self._token

    async def _get(self, endpoint: str, params: dict = None) -> Any:
        """Realizar petición GET autenticada."""
        token = await self._ensure_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "identity"  # Deshabilitar compresión gzip
        }

        url = f"{DATADIS_API_URL}{endpoint}"

        _LOGGER.info("Consultando API Datadis: %s con params=%s", endpoint, params)

        # Deshabilitar descompresión automática para evitar problemas con gzip mal formado
        async with self._session.get(url, headers=headers, params=params, compress=False) as response:
            _LOGGER.info("Respuesta API Datadis: status=%d", response.status)

            if response.status == 204:
                return None

            # Leer contenido crudo para evitar problemas de descompresión
            content = await response.read()

            if response.status != 200:
                error_msg = content[:500].decode('utf-8', errors='replace')

                # Error 429: Límite de tasa (consulta ya realizada en 24h)
                if response.status == 429:
                    _LOGGER.warning("Límite de tasa alcanzado (429): %s", error_msg)
                    raise RateLimitError(f"Consulta ya realizada en las últimas 24 horas")

                _LOGGER.error("Error en API Datadis (%d): %s", response.status, error_msg)
                raise ApiError(f"Error en API: {response.status} - {content[:200].decode('utf-8', errors='replace')}")

            # Intentar parsear JSON desde el contenido crudo
            text = content.decode('utf-8', errors='replace')
            _LOGGER.debug("Respuesta (primeros 500 chars): %s", text[:500])

            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                _LOGGER.error("Respuesta no es JSON válido: %s", text[:500] if text else "vacío")
                raise ApiError(f"Respuesta no es JSON válido: {text[:200] if text else 'vacío'}")

    async def get_supplies(self) -> list:
        """Obtener lista de suministros del usuario."""
        data = await self._get("/get-supplies-v2")
        # La v2 devuelve {"supplies": [...], "distributorError": [...]}
        if isinstance(data, dict):
            return data.get("supplies", [])
        return data if data else []

    async def get_contract_detail(self, cups: str, distributor_code: str) -> list:
        """Obtener detalle del contrato."""
        data = await self._get(
            "/get-contract-detail-v2",
            {"cups": cups, "distributorCode": distributor_code}
        )
        # La v2 devuelve {"contract": [...], "distributorError": [...]}
        if isinstance(data, dict):
            return data.get("contract", [])
        return data if data else []

    async def get_consumption_data(
        self,
        cups: str,
        distributor_code: str,
        start_date: str,
        end_date: str,
        measurement_type: int = 0,
        point_type: int = None,
    ) -> list:
        """Obtener datos de consumo.

        Args:
            cups: Código CUPS
            distributor_code: Código de distribuidora
            start_date: Fecha inicio (formato YYYY/MM)
            end_date: Fecha fin (formato YYYY/MM)
            measurement_type: 0 = horario, 1 = cuartohorario
            point_type: Tipo de punto de medida (opcional)

        Returns:
            Lista de datos de consumo con campos:
            - consumptionKWh: Energía consumida
            - surplusEnergyKWh: Energía excedentaria (autoconsumo)
            - generationEnergyKWh: Energía generada
            - selfConsumptionEnergyKWh: Energía autoconsumida
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": start_date,
            "endDate": end_date,
            "measurementType": str(measurement_type),
        }
        if point_type:
            params["pointType"] = str(point_type)

        data = await self._get("/get-consumption-data-v2", params)
        # La v2 devuelve {"timeCurve": [...], "distributorError": [...]}
        if isinstance(data, dict):
            return data.get("timeCurve", [])
        return data if data else []

    async def get_max_power(self, cups: str, distributor_code: str, start_date: str = None, end_date: str = None) -> list:
        """Obtener potencia máxima demandada.

        Args:
            cups: Código CUPS
            distributor_code: Código de distribuidora
            start_date: Fecha inicio (formato YYYY/MM) - opcional
            end_date: Fecha fin (formato YYYY/MM) - opcional

        Returns:
            Lista de datos de potencia máxima con campos:
            - maxPower: Potencia máxima (W)
            - period: Periodo (VALLE, LLANO, PUNTA, 1-6)
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        data = await self._get("/get-max-power-v2", params)
        # La v2 devuelve {"maxPower": [...], "distributorError": [...]}
        if isinstance(data, dict):
            return data.get("maxPower", [])
        return data if data else []

    async def get_distributors(self) -> list:
        """Obtener lista de distribuidoras del usuario."""
        data = await self._get("/get-distributors-with-supplies-v2")
        # La v2 devuelve {"distExistenceUser": {"distributorCodes": [...]}, "distributorError": [...]}
        if isinstance(data, dict):
            dist_user = data.get("distExistenceUser", {})
            return dist_user.get("distributorCodes", [])
        return data if data else []

    async def get_reactive_data(
        self,
        cups: str,
        distributor_code: str,
        start_date: str,
        end_date: str,
    ) -> list:
        """Obtener datos de energía reactiva por periodos."""
        data = await self._get(
            "/get-reactive-data-v2",
            {
                "cups": cups,
                "distributorCode": distributor_code,
                "startDate": start_date,
                "endDate": end_date,
            }
        )
        # La v2 devuelve {"reactiveEnergy": {"energy": [...]}, "distributorError": [...]}
        if isinstance(data, dict):
            reactive = data.get("reactiveEnergy", {})
            return reactive.get("energy", [])
        return data if data else []


class AuthenticationError(Exception):
    """Error de autenticación."""
    pass


class ApiError(Exception):
    """Error de API."""
    pass


class RateLimitError(ApiError):
    """Error de límite de tasa (429)."""
    pass