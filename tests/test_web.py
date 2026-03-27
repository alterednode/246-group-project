from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aiohttp.test_utils import TestClient, TestServer
import pytest

from busclock.api.weather import CurrentWeather, GeocodedLocation
from busclock.config import ConfigStore
from busclock.runtime import BusClockRuntime
from busclock.web import create_web_app


@pytest.mark.asyncio
async def test_config_endpoint_persists_and_state_endpoint_reflects_latest_config(
    tmp_path: Path,
) -> None:
    @dataclass
    class FakeWeatherClient:
        called: bool = False

        async def fetch_current(self, query: str | GeocodedLocation) -> CurrentWeather:
            self.called = True
            return CurrentWeather(
                location=GeocodedLocation(
                    query="unused",
                    name="Kelowna",
                    latitude=1.0,
                    longitude=2.0,
                ),
                temperature_c=11.0,
                feels_like_c=9.0,
                description="cloudy",
                icon="02d",
            )

    async def fake_transit_fetcher(config, session, now):
        raise LookupError("No route found for preferred line '97'.")

    config_store = ConfigStore(tmp_path / "config.json")
    weather_client = FakeWeatherClient()
    runtime = BusClockRuntime(
        config_store=config_store,
        transit_fetcher=fake_transit_fetcher,
        weather_client_factory=lambda session: weather_client,
    )
    await runtime.start()

    app = create_web_app(runtime)
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        response = await client.post(
            "/api/config",
            json={
                "home_location": "123 Main St",
                "destination": "UBCO",
                "preferred_bus_line": "97",
                "leave_buffer_minutes": 6,
                "weather_location_mode": "destination",
            },
        )
        assert response.status == 200

        config_response = await client.get("/api/config")
        config_payload = await config_response.json()

        state_response = await client.get("/api/state")
        state_payload = await state_response.json()
    finally:
        await client.close()
        await runtime.stop()

    assert config_payload["home_location"] == "123 Main St"
    assert config_payload["weather_location_mode"] == "destination"
    assert state_payload["config"]["preferred_bus_line"] == "97"
    assert state_payload["status"]["weather"]["state"] == "unavailable"
    assert "coordinates are unavailable" in (state_payload["status"]["weather"]["message"] or "")
    assert state_payload["status"]["transit"]["state"] == "unavailable"
    assert weather_client.called is False
