from __future__ import annotations

from busclock.api.transit_route import parse_transit_routes, select_preferred_route


def test_select_preferred_route_supports_walk_then_bus() -> None:
    routes = parse_transit_routes(_build_payload())

    selected = select_preferred_route(routes, "97")

    assert selected.route_index == 1
    assert selected.first_transit_step.line_name == "97"
    assert selected.route.departure_time is not None
    assert selected.route.steps[0].travel_mode == "WALKING"
    assert selected.route.steps[1].travel_mode == "TRANSIT"


def test_select_preferred_route_supports_direct_bus_boarding() -> None:
    routes = parse_transit_routes(_build_payload())

    selected = select_preferred_route(routes, "8")

    assert selected.route_index == 0
    assert selected.first_transit_step.line_name == "8"
    assert selected.route.steps[0].travel_mode == "TRANSIT"


def _build_payload() -> dict[str, object]:
    return {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "start_address": "Home",
                        "end_address": "Campus",
                        "departure_time": {"value": 1_700_000_000},
                        "arrival_time": {"value": 1_700_001_200},
                        "duration": {"text": "20 mins", "value": 1200},
                        "distance": {"text": "6 km"},
                        "steps": [
                            {
                                "travel_mode": "TRANSIT",
                                "html_instructions": "Take the bus",
                                "duration": {"text": "20 mins", "value": 1200},
                                "transit_details": {
                                    "departure_stop": {"name": "Stop A"},
                                    "arrival_stop": {"name": "Stop B"},
                                    "departure_time": {"value": 1_700_000_120},
                                    "arrival_time": {"value": 1_700_001_200},
                                    "line": {"short_name": "8"},
                                    "num_stops": 5,
                                },
                            }
                        ],
                    }
                ]
            },
            {
                "legs": [
                    {
                        "start_address": "Home",
                        "end_address": "Campus",
                        "departure_time": {"value": 1_700_000_300},
                        "arrival_time": {"value": 1_700_001_500},
                        "duration": {"text": "20 mins", "value": 1200},
                        "distance": {"text": "5 km"},
                        "steps": [
                            {
                                "travel_mode": "WALKING",
                                "html_instructions": "Walk to stop",
                                "duration": {"text": "5 mins", "value": 300},
                            },
                            {
                                "travel_mode": "TRANSIT",
                                "html_instructions": "Board 97",
                                "duration": {"text": "15 mins", "value": 900},
                                "transit_details": {
                                    "departure_stop": {"name": "Stop C"},
                                    "arrival_stop": {"name": "Stop D"},
                                    "departure_time": {"value": 1_700_000_600},
                                    "arrival_time": {"value": 1_700_001_500},
                                    "line": {"short_name": "97"},
                                    "num_stops": 7,
                                },
                            },
                        ],
                    }
                ]
            },
        ],
    }
