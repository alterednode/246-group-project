from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiohttp
import pytest

from busclock.api.transit_route import SelectedTransitRoute, TransitRoute, TransitStep
from busclock.api.weather import CurrentWeather, GeocodedLocation
from busclock.config import AppConfig, ConfigStore
from busclock.runtime import BusClockRuntime

@pytest.mark.asyncio
async def test_runtime_invokes_hardware_handlers_on_start(tmp_path: Path) -> None:
    config_store = ConfigStore(tmp_path / "config.json")
    config_store.save(
        AppConfig(
            home_location="Home",
            destination="Campus",
            preferred_bus_line="97",
            leave_buffer_minutes=0,
            weather_location_mode="destination",
        )
    )

    async def fake_transit_fetcher(
        config: AppConfig,
        session: aiohttp.ClientSession,
        now: datetime,
    ) -> SelectedTransitRoute:
        route = TransitRoute(
            start_address="123 Home St",
            end_address="University Way",
            departure_time=now + timedelta(minutes=2, seconds=5),
            arrival_time=now + timedelta(minutes=25),
            duration="25 mins",
            duration_minutes=1500,
            distance="5 km",
            steps=(
                TransitStep(
                    instruction="Board 97",
                    travel_mode="TRANSIT",
                    line_name="97",
                    departure_stop="Stop A",
                    arrival_stop="Stop B",
                    departure_time=now + timedelta(minutes=2, seconds=5),
                    arrival_time=now + timedelta(minutes=25),
                ),
            ),
            start_latitude=49.88,
            start_longitude=-119.49,
            end_latitude=49.94,
            end_longitude=-119.39,
        )
        return SelectedTransitRoute(
            route=route,
            first_transit_step=route.steps[0],
            route_index=0,
        )

    @dataclass
    class FakeWeatherClient:
        async def fetch_current(
            self,
            query: str | GeocodedLocation,
        ) -> CurrentWeather:
            assert isinstance(query, GeocodedLocation)
            return CurrentWeather(
                location=query,
                temperature_c=10.0,
                feels_like_c=8.0,
                description="clear",
                icon="01d",
            )

    runtime = BusClockRuntime(
        config_store=config_store,
        transit_fetcher=fake_transit_fetcher,
        weather_client_factory=lambda session: FakeWeatherClient(),
    )

    await runtime.start()
    try:
        await asyncio.sleep(0.3)
        state = runtime.state_store.snapshot()
    finally:
        await runtime.stop()

    assert state.transit.leave_at is not None


@pytest.mark.asyncio
async def test_hardware_threads_can_read_updated_transit_state(tmp_path: Path) -> None:
    config_store = ConfigStore(tmp_path / "config.json")
    config_store.save(
        AppConfig(
            home_location="Home",
            destination="Campus",
            preferred_bus_line="97",
            leave_buffer_minutes=0,
            weather_location_mode="destination",
        )
    )

    departure_times = [
        datetime(2026, 3, 27, 12, 5, tzinfo=timezone.utc),
        datetime(2026, 3, 27, 12, 10, tzinfo=timezone.utc),
    ]
    transit_calls = 0

    async def fake_transit_fetcher(
        config: AppConfig,
        session: aiohttp.ClientSession,
        now: datetime,
    ) -> SelectedTransitRoute:
        nonlocal transit_calls
        departure_time = departure_times[transit_calls]
        transit_calls += 1
        route = TransitRoute(
            start_address="123 Home St",
            end_address="University Way",
            departure_time=departure_time,
            arrival_time=departure_time + timedelta(minutes=25),
            duration="25 mins",
            duration_minutes=1500,
            distance="5 km",
            steps=(
                TransitStep(
                    instruction="Board 97",
                    travel_mode="TRANSIT",
                    line_name="97",
                    departure_stop="Stop A",
                    arrival_stop="Stop B",
                    departure_time=departure_time,
                    arrival_time=departure_time + timedelta(minutes=25),
                ),
            ),
            start_latitude=49.88,
            start_longitude=-119.49,
            end_latitude=49.94,
            end_longitude=-119.39,
        )
        return SelectedTransitRoute(
            route=route,
            first_transit_step=route.steps[0],
            route_index=0,
        )

    @dataclass
    class FakeWeatherClient:
        async def fetch_current(
            self,
            query: str | GeocodedLocation,
        ) -> CurrentWeather:
            assert isinstance(query, GeocodedLocation)
            return CurrentWeather(
                location=query,
                temperature_c=10.0,
                feels_like_c=8.0,
                description="clear",
                icon="01d",
            )

    runtime = BusClockRuntime(
        config_store=config_store,
        transit_fetcher=fake_transit_fetcher,
        weather_client_factory=lambda session: FakeWeatherClient(),
    )

    await runtime.start()
    try:
        await runtime.refresh_transit()
        await asyncio.sleep(0.3)
        state = runtime.state_store.snapshot()
    finally:
        await runtime.stop()

    assert state.transit.leave_at == departure_times[1]
