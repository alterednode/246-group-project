from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiohttp
import pytest

from busclock.api.transit_route import SelectedTransitRoute, TransitRoute, TransitStep
from busclock.api.weather import CurrentWeather, GeocodedLocation
from busclock.config import AppConfig, ConfigStore
from busclock.runtime import BusClockRuntime, build_transit_snapshot


@pytest.mark.asyncio
async def test_build_transit_snapshot_uses_google_departure_minus_buffer() -> None:
    now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
    google_departure = now + timedelta(minutes=12)
    route = TransitRoute(
        start_address="Home",
        end_address="Campus",
        departure_time=google_departure,
        arrival_time=now + timedelta(minutes=30),
        duration="30 mins",
        duration_minutes=1800,
        distance="7 km",
        steps=(
            TransitStep(
                instruction="Ride the bus",
                travel_mode="TRANSIT",
                line_name="97",
                departure_stop="Stop A",
                arrival_stop="Stop B",
                departure_time=google_departure + timedelta(minutes=5),
                arrival_time=now + timedelta(minutes=30),
            ),
        ),
    )
    selection = SelectedTransitRoute(route=route, first_transit_step=route.steps[0], route_index=0)
    config = AppConfig(
        home_location="Home",
        destination="Campus",
        preferred_bus_line="97",
        leave_buffer_minutes=4,
        weather_location_mode="home",
    )

    snapshot = build_transit_snapshot(selection, config, now)

    assert snapshot.leave_at == google_departure - timedelta(minutes=4)
    assert snapshot.minutes_until_leave == 8
    assert snapshot.bus_departure_time == google_departure + timedelta(minutes=5)


@pytest.mark.asyncio
async def test_runtime_preserves_last_good_snapshot_on_transient_failure(tmp_path: Path) -> None:
    config_store = ConfigStore(tmp_path / "config.json")
    config_store.save(
        AppConfig(
            home_location="Home",
            destination="Campus",
            preferred_bus_line="97",
            leave_buffer_minutes=3,
            weather_location_mode="home",
        )
    )

    transit_calls = 0

    async def fake_transit_fetcher(
        config: AppConfig,
        session: aiohttp.ClientSession,
        now: datetime,
    ) -> SelectedTransitRoute:
        nonlocal transit_calls
        transit_calls += 1
        if transit_calls == 1:
            route = TransitRoute(
                start_address=config.home_location,
                end_address=config.destination,
                departure_time=now + timedelta(minutes=10),
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
                        departure_time=now + timedelta(minutes=12),
                        arrival_time=now + timedelta(minutes=25),
                    ),
                ),
            )
            return SelectedTransitRoute(
                route=route,
                first_transit_step=route.steps[0],
                route_index=0,
            )
        raise RuntimeError("temporary transit outage")

    @dataclass
    class FakeWeatherClient:
        async def fetch_current(self, query: str) -> CurrentWeather:
            return CurrentWeather(
                location=GeocodedLocation(query=query, name="Kelowna", latitude=1.0, longitude=2.0),
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
        first_snapshot = (await runtime.state_store.snapshot()).transit
        await runtime.refresh_transit()
        state = await runtime.state_store.snapshot()
    finally:
        await runtime.stop()

    assert first_snapshot.available is True
    assert state.transit == first_snapshot
    assert state.status["transit"].state == "error"
    assert state.status["transit"].message == "temporary transit outage"
