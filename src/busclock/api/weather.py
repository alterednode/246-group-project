from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import aiohttp

OPENWEATHER_GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GeocodedLocation:
    query: str
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    state: str | None = None


@dataclass(frozen=True, slots=True)
class CurrentWeather:
    location: GeocodedLocation
    temperature_c: float
    feels_like_c: float
    description: str | None
    icon: str | None


class WeatherClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        api_key: str | None = None,
    ) -> None:
        self._session = session
        self._api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self._location_cache: dict[str, GeocodedLocation] = {}

    async def fetch_current(self, query: str | GeocodedLocation) -> CurrentWeather:
        if not self._api_key:
            raise ValueError(
                "An OpenWeather API key is required. Set OPENWEATHER_API_KEY."
            )

        LOGGER.debug("Fetching current weather for query=%r", _describe_location_query(query))
        location = await self._get_location(query)
        async with self._session.get(
            OPENWEATHER_CURRENT_URL,
            params={
                "appid": self._api_key,
                "lat": location.latitude,
                "lon": location.longitude,
                "units": "metric",
            },
            timeout=20,
        ) as response:
            if response.status >= 400:
                raise RuntimeError(
                    f"Weather API request failed with HTTP {response.status}."
                )
            payload = await response.json()
        LOGGER.debug(
            "Weather API response received for query=%r resolved_location=%r",
            _describe_location_query(query),
            location.name,
        )

        weather_info = (payload.get("weather") or [{}])[0]
        main = payload.get("main") or {}
        return CurrentWeather(
            location=location,
            temperature_c=float(main["temp"]),
            feels_like_c=float(main.get("feels_like", main["temp"])),
            description=weather_info.get("description"),
            icon=weather_info.get("icon"),
        )

    async def _get_location(self, query: str | GeocodedLocation) -> GeocodedLocation:
        if isinstance(query, GeocodedLocation):
            return query

        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Weather location query cannot be empty.")

        cached = self._location_cache.get(normalized_query)
        if cached is not None:
            LOGGER.debug("Weather geocode cache hit for query=%r", normalized_query)
            return cached

        LOGGER.debug("Resolving weather location for query=%r", normalized_query)
        async with self._session.get(
            OPENWEATHER_GEOCODING_URL,
            params={
                "appid": self._api_key,
                "q": normalized_query,
                "limit": 1,
            },
            timeout=20,
        ) as response:
            if response.status >= 400:
                raise RuntimeError(
                    f"Weather geocoding request failed with HTTP {response.status}."
                )
            payload = await response.json()

        if not payload:
            raise RuntimeError(f"No weather location found for '{normalized_query}'.")

        match = payload[0]
        location = GeocodedLocation(
            query=normalized_query,
            name=match["name"],
            latitude=float(match["lat"]),
            longitude=float(match["lon"]),
            country=match.get("country"),
            state=match.get("state"),
        )
        self._location_cache[normalized_query] = location
        LOGGER.debug(
            "Resolved weather location query=%r to lat=%s lon=%s",
            normalized_query,
            location.latitude,
            location.longitude,
        )
        return location


def _describe_location_query(query: str | GeocodedLocation) -> str:
    if isinstance(query, GeocodedLocation):
        return query.query
    return query
