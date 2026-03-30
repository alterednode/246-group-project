from __future__ import annotations

import threading
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
    requested_home_location: str | None = None
    requested_destination: str | None = None
    route_summary: str | None = None
    start_address: str | None = None
    end_address: str | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None
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
    temp_min_c: float | None = None
    temp_max_c: float | None = None
    pressure_hpa: int | None = None
    humidity_percent: int | None = None
    sea_level_hpa: int | None = None
    ground_level_hpa: int | None = None
    visibility_m: int | None = None
    wind_speed_mps: float | None = None
    wind_direction_deg: int | None = None
    wind_gust_mps: float | None = None
    cloudiness_percent: int | None = None
    rain_1h_mm: float | None = None
    rain_3h_mm: float | None = None
    snow_1h_mm: float | None = None
    snow_3h_mm: float | None = None
    observed_at: datetime | None = None
    sunrise_at: datetime | None = None
    sunset_at: datetime | None = None
    timezone_offset_seconds: int | None = None
    condition: str | None = None
    condition_code: int | None = None
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
        self._lock = threading.Lock()
        self._state = SystemState(
            config=config,
            transit=TransitSnapshot(),
            weather=WeatherSnapshot(),
            status={
                "transit": RefreshStatus(state="idle"),
                "weather": RefreshStatus(state="idle"),
            },
        )

    def snapshot(self) -> SystemState:
        with self._lock:
            return replace(self._state, status=dict(self._state.status))

    def set_config(self, config: AppConfig) -> None:
        with self._lock:
            self._state = replace(self._state, config=config, updated_at=_utcnow())

    def set_transit(
        self,
        snapshot: TransitSnapshot | None,
        *,
        status: str,
        message: str | None = None,
        preserve_existing: bool = False,
    ) -> None:
        now = _utcnow()
        with self._lock:
            transit = self._state.transit
            if snapshot is not None:
                transit = snapshot
            elif not preserve_existing:
                transit = TransitSnapshot()
            self._state = replace(
                self._state,
                transit=transit,
                status=_replace_status(
                    self._state.status,
                    "transit",
                    RefreshStatus(state=status, updated_at=now, message=message),
                ),
                updated_at=now,
            )

    def set_weather(
        self,
        snapshot: WeatherSnapshot | None,
        *,
        status: str,
        message: str | None = None,
        preserve_existing: bool = False,
    ) -> None:
        now = _utcnow()
        with self._lock:
            weather = self._state.weather
            if snapshot is not None:
                weather = snapshot
            elif not preserve_existing:
                weather = WeatherSnapshot()
            self._state = replace(
                self._state,
                weather=weather,
                status=_replace_status(
                    self._state.status,
                    "weather",
                    RefreshStatus(state=status, updated_at=now, message=message),
                ),
                updated_at=now,
            )

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _replace_status(
    statuses: dict[str, RefreshStatus],
    key: str,
    value: RefreshStatus,
) -> dict[str, RefreshStatus]:
    updated = dict(statuses)
    updated[key] = value
    return updated


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
