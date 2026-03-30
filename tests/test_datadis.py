"""Tests para la integración Datadis."""
import pytest
from unittest.mock import Mock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD

from custom_components.datadis.const import (
    DOMAIN,
    CONF_NIF,
    CONF_PASSWORD,
    CONF_CUPS,
)
from custom_components.datadis.api import DatadisAPI, AuthenticationError


@pytest.fixture
def mock_api():
    """Fixture para mock de API."""
    api = Mock(spec=DatadisAPI)
    api._ensure_token = Mock(return_value="mock_token")
    api.get_supplies = Mock(return_value=[
        {"cups": "ES0021000123456789AB", "distributorCode": "2", "distributorName": "Endesa"}
    ])
    api.get_consumption_data = Mock(return_value=[
        {"date": "2026/03/29", "hour": "10:00", "consumptionKWh": 0.5}
    ])
    api.close = Mock(return_value=None)
    return api


@pytest.fixture
def config_entry_data():
    """Datos de entrada de configuración de prueba."""
    return {
        CONF_NIF: "12345678A",
        CONF_PASSWORD: "test_password",
        CONF_CUPS: "ES0021000123456789AB",
    }


def test_api_token_extraction():
    """Test de extracción de token."""
    # Simular respuesta de token con Bearer
    token_with_bearer = "Bearer abc123token"
    token_clean = token_with_bearer.strip().strip('"').replace("Bearer ", "")
    assert token_clean == "abc123token"

    # Simular respuesta de token sin Bearer
    token_without = "abc123token"
    token_clean2 = token_without.strip().strip('"')
    if token_clean2.startswith("Bearer "):
        token_clean2 = token_clean2[7:]
    assert token_clean2 == "abc123token"


def test_period_calculation():
    """Test de cálculo de períodos tarifarios."""
    from datetime import datetime
    from custom_components.datadis.coordinator import get_period_for_datetime

    # Lunes a las 11:00 (Punta)
    dt_punta = datetime(2026, 3, 30, 11, 0)  # Lunes
    assert get_period_for_datetime(dt_punta) == "P1"

    # Lunes a las 16:00 (Llano)
    dt_llano = datetime(2026, 3, 30, 16, 0)
    assert get_period_for_datetime(dt_llano) == "P2"

    # Lunes a las 04:00 (Valle)
    dt_valle = datetime(2026, 3, 30, 4, 0)
    assert get_period_for_datetime(dt_valle) == "P3"

    # Sábado (siempre Valle)
    dt_sabado = datetime(2026, 3, 28, 12, 0)  # Sábado
    assert get_period_for_datetime(dt_sabado) == "P3"


def test_api_error_handling():
    """Test de manejo de errores de API."""
    from custom_components.datadis.api import ApiError, RateLimitError, AuthenticationError

    # Verificar que existen las excepciones
    assert issubclass(RateLimitError, ApiError)
    assert issubclass(AuthenticationError, Exception)

    # Crear instancias
    api_error = ApiError("Error de prueba")
    assert str(api_error) == "Error de prueba"

    rate_error = RateLimitError("Límite alcanzado")
    assert "Límite" in str(rate_error)


def test_const_values():
    """Test de valores de constantes."""
    from custom_components.datadis.const import DOMAIN, DEFAULT_ENERGY_PRICE_P1

    assert DOMAIN == "datadis"
    assert DEFAULT_ENERGY_PRICE_P1 \u003e 0
    assert isinstance(DEFAULT_ENERGY_PRICE_P1, float)
