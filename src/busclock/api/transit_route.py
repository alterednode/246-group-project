from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import aiohttp

GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TransitStep:
    instruction: str
    travel_mode: str
    duration: str | None = None
    duration_minutes: int | None = None
    line_name: str | None = None
    departure_stop: str | None = None
    arrival_stop: str | None = None
    departure_time: datetime | None = None
    arrival_time: datetime | None = None
    num_stops: int | None = None


@dataclass(frozen=True, slots=True)
class TransitRoute:
    start_address: str
    end_address: str
    departure_time: datetime | None
    arrival_time: datetime | None
    duration: str
    duration_minutes: int | None
    distance: str | None
    steps: tuple[TransitStep, ...]


@dataclass(frozen=True, slots=True)
class SelectedTransitRoute:
    route: TransitRoute
    first_transit_step: TransitStep
    route_index: int


async def fetch_transit_routes(
    start: str,
    end: str,
    *,
    session: aiohttp.ClientSession,
    api_key: str | None = None,
    departure_time: datetime | None = None,
    alternatives: bool = False,
) -> list[TransitRoute]:
    resolved_api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "A Google Maps API key is required. Pass api_key=... or set "
            "GOOGLE_MAPS_API_KEY."
        )

    LOGGER.debug(
        "Fetching transit routes origin=%r destination=%r alternatives=%s departure_time=%s",
        start,
        end,
        alternatives,
        departure_time.isoformat() if departure_time else None,
    )
    params = _build_params(
        start,
        end,
        api_key=resolved_api_key,
        departure_time=departure_time,
        alternatives=alternatives,
    )
    async with session.get(GOOGLE_DIRECTIONS_URL, params=params, timeout=20) as response:
        if response.status >= 400:
            raise RuntimeError(
                f"Transit API request failed with HTTP {response.status}."
            )
        payload = await response.json()

    routes = parse_transit_routes(payload)
    LOGGER.debug("Transit API returned %s routes", len(routes))
    return routes


async def fetch_preferred_transit_route(
    start: str,
    end: str,
    preferred_line: str,
    *,
    session: aiohttp.ClientSession,
    api_key: str | None = None,
    departure_time: datetime | None = None,
) -> SelectedTransitRoute:
    routes = await fetch_transit_routes(
        start,
        end,
        session=session,
        api_key=api_key,
        departure_time=departure_time,
        alternatives=True,
    )
    return select_preferred_route(routes, preferred_line)


def get_transit_route(
    start: str,
    end: str,
    *,
    api_key: str | None = None,
    departure_time: datetime | None = None,
    alternatives: bool = False,
) -> TransitRoute:
    resolved_api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "A Google Maps API key is required. Pass api_key=... or set "
            "GOOGLE_MAPS_API_KEY."
        )

    params = _build_params(
        start,
        end,
        api_key=resolved_api_key,
        departure_time=departure_time,
        alternatives=alternatives,
    )
    request = Request(f"{GOOGLE_DIRECTIONS_URL}?{urlencode(params)}")

    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Transit API request failed with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Transit API request failed.") from exc

    return parse_transit_routes(payload)[0]


def parse_transit_routes(payload: dict[str, Any]) -> list[TransitRoute]:
    status = payload.get("status")
    if status != "OK":
        message = payload.get("error_message") or "No route returned."
        raise RuntimeError(f"Transit API error {status}: {message}")

    routes = payload.get("routes") or []
    if not routes:
        raise RuntimeError("Transit API returned no routes.")

    return [_parse_route(route) for route in routes]


def select_preferred_route(
    routes: list[TransitRoute],
    preferred_line: str,
) -> SelectedTransitRoute:
    normalized_preference = _normalize_line_name(preferred_line)
    LOGGER.debug(
        "Selecting preferred route for line=%r across %s candidates",
        preferred_line,
        len(routes),
    )
    for index, route in enumerate(routes):
        first_transit_step = _find_first_transit_step(route.steps)
        if first_transit_step is None:
            LOGGER.debug("Skipping route index=%s because it has no transit step", index)
            continue
        if _line_matches(first_transit_step.line_name, normalized_preference):
            LOGGER.debug(
                "Selected route index=%s with first transit line=%r",
                index,
                first_transit_step.line_name,
            )
            return SelectedTransitRoute(
                route=route,
                first_transit_step=first_transit_step,
                route_index=index,
            )

        LOGGER.debug(
            "Rejected route index=%s because first transit line=%r did not match %r",
            index,
            first_transit_step.line_name,
            preferred_line,
        )
    raise LookupError(f"No route found for preferred line '{preferred_line}'.")


def build_route_summary(route: TransitRoute) -> str:
    parts = []
    for step in route.steps:
        if step.travel_mode == "TRANSIT" and step.line_name:
            parts.append(
                f"Bus {step.line_name} from {step.departure_stop} to {step.arrival_stop}"
            )
        else:
            parts.append(f"{step.travel_mode.title()}: {step.instruction}")
    return " | ".join(parts)


def _build_params(
    start: str,
    end: str,
    *,
    api_key: str,
    departure_time: datetime | None,
    alternatives: bool,
) -> dict[str, str]:
    params = {
        "origin": start,
        "destination": end,
        "mode": "transit",
        "alternatives": str(alternatives).lower(),
        "key": api_key,
    }
    if departure_time is not None:
        params["departure_time"] = str(int(departure_time.timestamp()))
    return params


def _parse_route(route: dict[str, Any]) -> TransitRoute:
    leg = route["legs"][0]
    return TransitRoute(
        start_address=leg["start_address"],
        end_address=leg["end_address"],
        departure_time=_parse_api_time(leg.get("departure_time")),
        arrival_time=_parse_api_time(leg.get("arrival_time")),
        duration=leg["duration"]["text"],
        duration_minutes=leg["duration"].get("value"),
        distance=leg.get("distance", {}).get("text"),
        steps=tuple(_parse_step(step) for step in leg["steps"]),
    )


def _parse_step(step: dict[str, Any]) -> TransitStep:
    transit_details = step.get("transit_details") or {}
    line = transit_details.get("line") or {}

    return TransitStep(
        instruction=_strip_html(step.get("html_instructions", "")),
        travel_mode=step["travel_mode"],
        duration=step.get("duration", {}).get("text"),
        duration_minutes=step.get("duration", {}).get("value"),
        line_name=line.get("short_name") or line.get("name"),
        departure_stop=(transit_details.get("departure_stop") or {}).get("name"),
        arrival_stop=(transit_details.get("arrival_stop") or {}).get("name"),
        departure_time=_parse_api_time(transit_details.get("departure_time")),
        arrival_time=_parse_api_time(transit_details.get("arrival_time")),
        num_stops=transit_details.get("num_stops"),
    )


def _parse_api_time(value: dict[str, Any] | None) -> datetime | None:
    if not value:
        return None

    timestamp = value.get("value")
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def _strip_html(text: str) -> str:
    return HTML_TAG_PATTERN.sub("", text).strip()


def _find_first_transit_step(steps: tuple[TransitStep, ...]) -> TransitStep | None:
    for step in steps:
        if step.travel_mode == "TRANSIT":
            return step
    return None


def _normalize_line_name(value: str | None) -> str:
    return re.sub(r"\s+", "", (value or "").lower())


def _line_matches(line_name: str | None, normalized_preference: str) -> bool:
    if not normalized_preference:
        return False

    normalized_line = _normalize_line_name(line_name)
    return (
        normalized_line == normalized_preference
        or normalized_preference in normalized_line
        or normalized_line in normalized_preference
    )
