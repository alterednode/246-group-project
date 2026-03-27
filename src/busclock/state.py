from __future__ import annotations

import asyncio
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import datetime, timezone
from typing import Any

from .config import AppConfig
from .api.transit_route import TransitStep


@dataclass(frozen=True, slots=True)
class RefreshStatus:
    state: str
    updated_at: datetime | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class TransitSnapshot:
    available: bool = False
    route_summary: str | None = None
    start_address: str | None = None
    end_address: str | None = None
    google_departure_time: datetime | None = None
    google_arrival_time: datetime | None = None
    bus_departure_time: datetime | None = None
    bus_arrival_time: datetime | None = None
    leave_at: datetime | None = None
    minutes_until_leave: int | None = None
    is_late: bool | None = None
    selected_line: str | None = None
    departure_stop: str | None = None
    arrival_stop: str | None = None
    duration: str | None = None
    distance: str | None = None
    steps: tuple[TransitStep, ...] = ()


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    available: bool = False
    location_mode: str | None = None
    query: str | None = None
    resolved_location: str | None = None
    temperature_c: float | None = None
    feels_like_c: float | None = None
    description: str | None = None
    icon: str | None = None


@dataclass(frozen=True, slots=True)
class SystemState:
    config: AppConfig
    transit: TransitSnapshot
    weather: WeatherSnapshot
    status: dict[str, RefreshStatus]
    updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


class StateStore:
    def __init__(self, config: AppConfig) -> None:
        self._lock = asyncio.Lock()
        self._state = SystemState(
            config=config,
            transit=TransitSnapshot(),
            weather=WeatherSnapshot(),
            status={
                "transit": RefreshStatus(state="idle"),
                "weather": RefreshStatus(state="idle"),
            },
        )

    async def snapshot(self) -> SystemState:
        async with self._lock:
            return replace(self._state, status=dict(self._state.status))

    async def set_config(self, config: AppConfig) -> None:
        async with self._lock:
            self._state = replace(self._state, config=config, updated_at=_utcnow())

    async def apply_transit_result(
        self,
        snapshot: TransitSnapshot | None,
        *,
        status: str,
        message: str | None = None,
        preserve_existing: bool = False,
    ) -> None:
        await self._apply_source_result(
            source="transit",
            snapshot=snapshot,
            status=status,
            message=message,
            preserve_existing=preserve_existing,
        )

    async def apply_weather_result(
        self,
        snapshot: WeatherSnapshot | None,
        *,
        status: str,
        message: str | None = None,
        preserve_existing: bool = False,
    ) -> None:
        await self._apply_source_result(
            source="weather",
            snapshot=snapshot,
            status=status,
            message=message,
            preserve_existing=preserve_existing,
        )

    async def _apply_source_result(
        self,
        *,
        source: str,
        snapshot: TransitSnapshot | WeatherSnapshot | None,
        status: str,
        message: str | None,
        preserve_existing: bool,
    ) -> None:
        now = _utcnow()
        async with self._lock:
            statuses = dict(self._state.status)
            statuses[source] = RefreshStatus(state=status, updated_at=now, message=message)

            new_transit = self._state.transit
            new_weather = self._state.weather
            if source == "transit":
                if snapshot is not None:
                    new_transit = snapshot
                elif not preserve_existing:
                    new_transit = TransitSnapshot()
            else:
                if snapshot is not None:
                    new_weather = snapshot
                elif not preserve_existing:
                    new_weather = WeatherSnapshot()

            self._state = SystemState(
                config=self._state.config,
                transit=new_transit,
                weather=new_weather,
                status=statuses,
                updated_at=now,
            )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {field.name: _serialize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value
