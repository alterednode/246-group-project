from __future__ import annotations

from datetime import datetime, timezone

import pytest

from busclock.api import weather as weather_module
from busclock.api.weather import GeocodedLocation, WeatherClient


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self._payload = payload
        self.status = status

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, *, params: dict[str, object], timeout: int) -> FakeResponse:
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(self.payload)


@pytest.mark.asyncio
async def test_fetch_current_parses_extended_openweather_fields() -> None:
    payload = {
        "weather": [
            {
                "id": 500,
                "main": "Rain",
                "description": "light rain",
                "icon": "10d",
            }
        ],
        "main": {
            "temp": 10.3,
            "feels_like": 8.7,
            "temp_min": 9.5,
            "temp_max": 11.2,
            "pressure": 1008,
            "humidity": 82,
            "sea_level": 1008,
            "grnd_level": 997,
        },
        "visibility": 9000,
        "wind": {"speed": 3.6, "deg": 220, "gust": 5.1},
        "clouds": {"all": 75},
        "rain": {"1h": 0.45, "3h": 1.2},
        "snow": {"1h": 0.0, "3h": 0.0},
        "dt": 1774612800,
        "sys": {"sunrise": 1774586700, "sunset": 1774635300},
        "timezone": -25200,
    }
    session = FakeSession(payload)
    client = WeatherClient(session, api_key="test-key")

    weather = await client.fetch_current(
        GeocodedLocation(
            query="Kelowna",
            name="Kelowna",
            latitude=49.8879,
            longitude=-119.496,
            country="CA",
            state="BC",
        )
    )

    assert session.calls[0]["url"] == weather_module.OPENWEATHER_CURRENT_URL
    assert weather.temperature_c == 10.3
    assert weather.feels_like_c == 8.7
    assert weather.temp_min_c == 9.5
    assert weather.temp_max_c == 11.2
    assert weather.pressure_hpa == 1008
    assert weather.humidity_percent == 82
    assert weather.sea_level_hpa == 1008
    assert weather.ground_level_hpa == 997
    assert weather.visibility_m == 9000
    assert weather.condition == "Rain"
    assert weather.condition_code == 500
    assert weather.description == "light rain"
    assert weather.icon == "10d"
    assert weather.wind_speed_mps == 3.6
    assert weather.wind_direction_deg == 220
    assert weather.wind_gust_mps == 5.1
    assert weather.cloudiness_percent == 75
    assert weather.rain_1h_mm == 0.45
    assert weather.rain_3h_mm == 1.2
    assert weather.snow_1h_mm == 0.0
    assert weather.snow_3h_mm == 0.0
    assert weather.observed_at == datetime.fromtimestamp(1774612800, tz=timezone.utc)
    assert weather.sunrise_at == datetime.fromtimestamp(1774586700, tz=timezone.utc)
    assert weather.sunset_at == datetime.fromtimestamp(1774635300, tz=timezone.utc)
    assert weather.timezone_offset_seconds == -25200
