from __future__ import annotations

import os

try:
    from .transit_route import TransitRoute, TransitStep, get_transit_route
    from ..env import load_env_file
except ImportError:
    from transit_route import TransitRoute, TransitStep, get_transit_route
    from pathlib import Path

    def load_env_file() -> None:
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if not env_path.exists():
            return
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def main() -> None:
    load_env_file()
    api_key = input(
        "Google Maps API key (press Enter to use GOOGLE_MAPS_API_KEY): "
    ).strip()
    start = input("Start location: ").strip()
    destination = input("Destination: ").strip()

    if not start or not destination:
        print("Both start and destination are required.")
        return

    try:
        route = get_transit_route(
            start,
            destination,
            api_key=api_key or os.getenv("GOOGLE_MAPS_API_KEY"),
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return

    print_route(route)


def print_route(route: TransitRoute) -> None:
    print()
    print(f"From: {route.start_address}")
    print(f"To: {route.end_address}")
    print(f"Duration: {route.duration}")
    if route.distance:
        print(f"Distance: {route.distance}")
    if route.departure_time:
        print(f"Departure: {route.departure_time.isoformat()}")
    if route.arrival_time:
        print(f"Arrival: {route.arrival_time.isoformat()}")

    print("\nSteps:")
    for index, step in enumerate(route.steps, start=1):
        print(format_step(index, step))


def format_step(index: int, step: TransitStep) -> str:
    details = [f"{index}. [{step.travel_mode}] {step.instruction}"]
    if step.duration:
        details.append(f"Duration: {step.duration}")
    if step.line_name:
        details.append(f"Line: {step.line_name}")
    if step.departure_stop and step.arrival_stop:
        details.append(f"Stops: {step.departure_stop} -> {step.arrival_stop}")
    if step.num_stops is not None:
        details.append(f"Number of stops: {step.num_stops}")
    return " | ".join(details)


if __name__ == "__main__":
    main()
