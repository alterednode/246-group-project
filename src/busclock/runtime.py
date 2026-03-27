from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from .api.transit_route import (
    SelectedTransitRoute,
    build_route_summary,
    fetch_preferred_transit_route,
)
from .api.weather import CurrentWeather, WeatherClient
from .config import AppConfig, ConfigStore
from .state import StateStore, TransitSnapshot, WeatherSnapshot

TransitFetcher = Callable[
    [AppConfig, aiohttp.ClientSession, datetime],
    Awaitable[SelectedTransitRoute],
]

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeSettings:
    host: str = "0.0.0.0"
    port: int = 8080
    transit_refresh_seconds: int = 60
    weather_refresh_seconds: int = 600


class BusClockRuntime:
    def __init__(
        self,
        *,
        config_store: ConfigStore | None = None,
        settings: RuntimeSettings | None = None,
        transit_fetcher: TransitFetcher | None = None,
        weather_client_factory: Callable[[aiohttp.ClientSession], WeatherClient] | None = None,
    ) -> None:
        self.settings = settings or RuntimeSettings()
        self.config_store = config_store or ConfigStore()
        self.state_store = StateStore(self.config_store.load())
        self._transit_fetcher = transit_fetcher or _default_transit_fetcher
        self._weather_client_factory = weather_client_factory or WeatherClient
        self._session: aiohttp.ClientSession | None = None
        self._weather_client: WeatherClient | None = None
        self._transit_refresh_event = asyncio.Event()
        self._weather_refresh_event = asyncio.Event()
        self._tasks: list[asyncio.Task[None]] = []

    async def start(self) -> None:
        if self._session is not None:
            LOGGER.debug("Runtime start requested but session already exists")
            return

        LOGGER.info(
            "Starting runtime with config path=%s transit_refresh=%ss weather_refresh=%ss",
            self.config_store.path,
            self.settings.transit_refresh_seconds,
            self.settings.weather_refresh_seconds,
        )
        self._session = aiohttp.ClientSession()
        self._weather_client = self._weather_client_factory(self._session)
        LOGGER.debug("Created aiohttp client session and weather client")
        await self.refresh_transit()
        await self.refresh_weather()
        self._tasks = [
            asyncio.create_task(
                self._refresh_loop(
                    self.refresh_transit,
                    self.settings.transit_refresh_seconds,
                    self._transit_refresh_event,
                )
            ),
            asyncio.create_task(
                self._refresh_loop(
                    self.refresh_weather,
                    self.settings.weather_refresh_seconds,
                    self._weather_refresh_event,
                )
            ),
        ]
        LOGGER.info("Runtime background refresh loops started")

    async def stop(self) -> None:
        LOGGER.info("Stopping runtime")
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        if self._session is not None:
            await self._session.close()
            self._session = None
        self._weather_client = None
        LOGGER.info("Runtime stopped")

    def request_refresh(self) -> None:
        LOGGER.debug("Manual refresh requested")
        self._transit_refresh_event.set()
        self._weather_refresh_event.set()

    async def refresh_transit(self) -> None:
        config = (await self.state_store.snapshot()).config
        LOGGER.debug(
            "Refreshing transit state for origin=%r destination=%r line=%r",
            config.home_location,
            config.destination,
            config.preferred_bus_line,
        )
        if not config.is_complete():
            LOGGER.info("Skipping transit refresh because config is incomplete")
            await self.state_store.apply_transit_result(
                None,
                status="unavailable",
                message="Transit config is incomplete.",
                preserve_existing=False,
            )
            return

        session = self._require_session()
        now = _utcnow()
        try:
            selection = await self._transit_fetcher(config, session, now)
        except LookupError as exc:
            LOGGER.warning("Transit refresh found no matching route: %s", exc)
            await self.state_store.apply_transit_result(
                None,
                status="unavailable",
                message=str(exc),
                preserve_existing=False,
            )
            return
        except Exception as exc:
            LOGGER.warning("Transit refresh failed: %s", exc, exc_info=True)
            await self.state_store.apply_transit_result(
                None,
                status="error",
                message=str(exc),
                preserve_existing=True,
            )
            return

        snapshot = build_transit_snapshot(selection, config, now)
        LOGGER.info(
            "Transit refresh succeeded: line=%r leave_at=%s minutes_until_leave=%s",
            snapshot.selected_line,
            snapshot.leave_at.isoformat() if snapshot.leave_at else None,
            snapshot.minutes_until_leave,
        )
        LOGGER.debug("Transit snapshot summary: %s", snapshot.route_summary)
        await self.state_store.apply_transit_result(snapshot, status="ok")

    async def refresh_weather(self) -> None:
        config = (await self.state_store.snapshot()).config
        LOGGER.debug(
            "Refreshing weather state for mode=%s query=%r",
            config.weather_location_mode,
            config.weather_query(),
        )
        if not config.is_complete():
            LOGGER.info("Skipping weather refresh because config is incomplete")
            await self.state_store.apply_weather_result(
                None,
                status="unavailable",
                message="Weather config is incomplete.",
                preserve_existing=False,
            )
            return

        weather_query = config.weather_query()
        try:
            weather = await self._require_weather_client().fetch_current(weather_query)
        except ValueError as exc:
            LOGGER.warning("Weather refresh unavailable: %s", exc)
            await self.state_store.apply_weather_result(
                None,
                status="unavailable",
                message=str(exc),
                preserve_existing=False,
            )
            return
        except Exception as exc:
            LOGGER.warning("Weather refresh failed: %s", exc, exc_info=True)
            await self.state_store.apply_weather_result(
                None,
                status="error",
                message=str(exc),
                preserve_existing=True,
            )
            return

        snapshot = build_weather_snapshot(weather, config)
        LOGGER.info(
            "Weather refresh succeeded for %r: %sC feels_like=%sC",
            snapshot.query,
            snapshot.temperature_c,
            snapshot.feels_like_c,
        )
        LOGGER.debug("Weather snapshot description=%r icon=%r", snapshot.description, snapshot.icon)
        await self.state_store.apply_weather_result(snapshot, status="ok")

    async def update_config(self, payload: dict[str, Any]) -> AppConfig:
        LOGGER.info("Updating config from web request")
        LOGGER.debug("Config update payload keys: %s", sorted(payload.keys()))
        config = AppConfig.from_dict(payload, require_complete=True)
        self.config_store.save(config)
        LOGGER.info("Saved config to %s", self.config_store.path)
        LOGGER.debug("New config: %s", config.to_dict())
        await self.state_store.set_config(config)
        await asyncio.gather(self.refresh_transit(), self.refresh_weather())
        return config

    async def _refresh_loop(
        self,
        refresh: Callable[[], Awaitable[None]],
        interval_seconds: int,
        event: asyncio.Event,
    ) -> None:
        refresh_name = getattr(refresh, "__name__", "refresh")
        while True:
            try:
                await asyncio.wait_for(event.wait(), timeout=interval_seconds)
            except asyncio.TimeoutError:
                LOGGER.debug("%s interval elapsed; running scheduled refresh", refresh_name)
            else:
                event.clear()
                LOGGER.debug("%s triggered by manual refresh event", refresh_name)
            await refresh()

    def _require_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("Runtime has not been started.")
        return self._session

    def _require_weather_client(self) -> WeatherClient:
        if self._weather_client is None:
            raise RuntimeError("Runtime has not been started.")
        return self._weather_client


async def _default_transit_fetcher(
    config: AppConfig,
    session: aiohttp.ClientSession,
    now: datetime,
) -> SelectedTransitRoute:
    return await fetch_preferred_transit_route(
        config.home_location,
        config.destination,
        config.preferred_bus_line,
        session=session,
        departure_time=now,
    )


def build_transit_snapshot(
    selection: SelectedTransitRoute,
    config: AppConfig,
    now: datetime,
) -> TransitSnapshot:
    route = selection.route
    leave_at = route.departure_time
    if leave_at is not None:
        leave_at = leave_at - timedelta(minutes=config.leave_buffer_minutes)
    minutes_until_leave = _minutes_until(leave_at, now)

    return TransitSnapshot(
        available=True,
        route_summary=build_route_summary(route),
        start_address=route.start_address,
        end_address=route.end_address,
        google_departure_time=route.departure_time,
        google_arrival_time=route.arrival_time,
        bus_departure_time=selection.first_transit_step.departure_time,
        bus_arrival_time=selection.first_transit_step.arrival_time,
        leave_at=leave_at,
        minutes_until_leave=minutes_until_leave,
        is_late=minutes_until_leave is not None and minutes_until_leave < 0,
        selected_line=selection.first_transit_step.line_name,
        departure_stop=selection.first_transit_step.departure_stop,
        arrival_stop=selection.first_transit_step.arrival_stop,
        duration=route.duration,
        distance=route.distance,
        steps=route.steps,
    )


def build_weather_snapshot(weather: CurrentWeather, config: AppConfig) -> WeatherSnapshot:
    return WeatherSnapshot(
        available=True,
        location_mode=config.weather_location_mode,
        query=config.weather_query(),
        resolved_location=_format_weather_location(weather),
        temperature_c=weather.temperature_c,
        feels_like_c=weather.feels_like_c,
        description=weather.description,
        icon=weather.icon,
    )


def _format_weather_location(weather: CurrentWeather) -> str:
    location = weather.location
    parts = [location.name]
    if location.state:
        parts.append(location.state)
    if location.country:
        parts.append(location.country)
    return ", ".join(parts)


def _minutes_until(target: datetime | None, now: datetime) -> int | None:
    if target is None:
        return None
    return int((target - now).total_seconds() // 60)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
