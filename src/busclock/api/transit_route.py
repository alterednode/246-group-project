from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(slots=True)
class TransitStep:
    instruction: str
    travel_mode: str
    duration: str | None = None
    line_name: str | None = None
    departure_stop: str | None = None
    arrival_stop: str | None = None
    num_stops: int | None = None


@dataclass(slots=True)
class TransitRoute:
    start_address: str
    end_address: str
    departure_time: str | None
    arrival_time: str | None
    duration: str
    distance: str | None
    steps: list[TransitStep]


def get_transit_route(
    start: str,
    end: str,
    *,
    api_key: str | None = None,
    departure_time: datetime | None = None,
    alternatives: bool = False,
) -> TransitRoute:
    """
    Fetch a transit route between two locations using the Google Directions API.

    `start` and `end` can be plain addresses, place names, or latitude/longitude
    pairs. The API key defaults to the `GOOGLE_MAPS_API_KEY` environment
    variable when not passed explicitly.
    """

    resolved_api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "A Google Maps API key is required. Pass api_key=... or set "
            "GOOGLE_MAPS_API_KEY."
        )

    params = {
        "origin": start,
        "destination": end,
        "mode": "transit",
        "alternatives": str(alternatives).lower(),
        "key": resolved_api_key,
    }
    if departure_time is not None:
        params["departure_time"] = str(int(departure_time.timestamp()))

    request = Request(f"{GOOGLE_DIRECTIONS_URL}?{urlencode(params)}")

    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Transit API request failed with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Transit API request failed.") from exc

    status = payload.get("status")
    if status != "OK":
        message = payload.get("error_message") or "No route returned."
        raise RuntimeError(f"Transit API error {status}: {message}")

    route = payload["routes"][0]
    leg = route["legs"][0]

    return TransitRoute(
        start_address=leg["start_address"],
        end_address=leg["end_address"],
        departure_time=_format_transit_time(leg.get("departure_time")),
        arrival_time=_format_transit_time(leg.get("arrival_time")),
        duration=leg["duration"]["text"],
        distance=leg.get("distance", {}).get("text"),
        steps=[_parse_step(step) for step in leg["steps"]],
    )


def _parse_step(step: dict[str, Any]) -> TransitStep:
    transit_details = step.get("transit_details") or {}
    line = transit_details.get("line") or {}

    return TransitStep(
        instruction=_strip_html(step.get("html_instructions", "")),
        travel_mode=step["travel_mode"],
        duration=step.get("duration", {}).get("text"),
        line_name=line.get("short_name") or line.get("name"),
        departure_stop=(transit_details.get("departure_stop") or {}).get("name"),
        arrival_stop=(transit_details.get("arrival_stop") or {}).get("name"),
        num_stops=transit_details.get("num_stops"),
    )


def _format_transit_time(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return value.get("text")


def _strip_html(text: str) -> str:
    return HTML_TAG_PATTERN.sub("", text).strip()
