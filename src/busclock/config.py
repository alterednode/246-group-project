from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

WeatherLocationMode = Literal["home", "destination"]

DEFAULT_LEAVE_BUFFER_MINUTES = 5
DEFAULT_WEATHER_LOCATION_MODE: WeatherLocationMode = "home"
DEFAULT_CONFIG_PATH = Path(
    os.getenv(
        "BUSCLOCK_CONFIG_PATH",
        str(Path.home() / ".config" / "busclock" / "config.json"),
    )
)


@dataclass(frozen=True, slots=True)
class AppConfig:
    home_location: str = ""
    destination: str = ""
    preferred_bus_line: str = ""
    leave_buffer_minutes: int = DEFAULT_LEAVE_BUFFER_MINUTES
    weather_location_mode: WeatherLocationMode = DEFAULT_WEATHER_LOCATION_MODE

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        require_complete: bool = False,
    ) -> AppConfig:
        home_location = str(data.get("home_location", "")).strip()
        destination = str(data.get("destination", "")).strip()
        preferred_bus_line = str(data.get("preferred_bus_line", "")).strip()
        leave_buffer_minutes = _parse_leave_buffer_minutes(
            data.get("leave_buffer_minutes", DEFAULT_LEAVE_BUFFER_MINUTES)
        )
        weather_location_mode = _parse_weather_location_mode(
            data.get("weather_location_mode", DEFAULT_WEATHER_LOCATION_MODE)
        )

        config = cls(
            home_location=home_location,
            destination=destination,
            preferred_bus_line=preferred_bus_line,
            leave_buffer_minutes=leave_buffer_minutes,
            weather_location_mode=weather_location_mode,
        )
        if require_complete:
            config.ensure_complete()
        return config

    def ensure_complete(self) -> None:
        if not self.home_location:
            raise ValueError("home_location is required.")
        if not self.destination:
            raise ValueError("destination is required.")
        if not self.preferred_bus_line:
            raise ValueError("preferred_bus_line is required.")

    def is_complete(self) -> bool:
        try:
            self.ensure_complete()
        except ValueError:
            return False
        return True

    def weather_query(self) -> str:
        if self.weather_location_mode == "destination":
            return self.destination
        return self.home_location

    def to_dict(self) -> dict[str, Any]:
        return {
            "home_location": self.home_location,
            "destination": self.destination,
            "preferred_bus_line": self.preferred_bus_line,
            "leave_buffer_minutes": self.leave_buffer_minutes,
            "weather_location_mode": self.weather_location_mode,
        }


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or DEFAULT_CONFIG_PATH

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AppConfig:
        if not self._path.exists():
            return AppConfig()

        payload = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Config file must contain a JSON object.")
        return AppConfig.from_dict(payload)

    def save(self, config: AppConfig) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _parse_leave_buffer_minutes(value: Any) -> int:
    try:
        buffer_minutes = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("leave_buffer_minutes must be an integer.") from exc

    if buffer_minutes < 0:
        raise ValueError("leave_buffer_minutes must be 0 or greater.")
    return buffer_minutes


def _parse_weather_location_mode(value: Any) -> WeatherLocationMode:
    mode = str(value).strip().lower()
    if mode not in {"home", "destination"}:
        raise ValueError("weather_location_mode must be 'home' or 'destination'.")
    return mode  # type: ignore[return-value]
