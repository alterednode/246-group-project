from __future__ import annotations

import logging
from html import escape

from aiohttp import web

from .runtime import BusClockRuntime

LOGGER = logging.getLogger(__name__)


def create_web_app(runtime: BusClockRuntime) -> web.Application:
    app = web.Application(middlewares=[request_logging_middleware])
    app["runtime"] = runtime
    app.add_routes(
        [
            web.get("/", handle_index),
            web.get("/api/config", handle_get_config),
            web.post("/api/config", handle_update_config),
            web.put("/api/config", handle_update_config),
            web.get("/api/state", handle_get_state),
            web.get("/healthz", handle_health),
        ]
    )
    return app


@web.middleware
async def request_logging_middleware(
    request: web.Request,
    handler,
):
    LOGGER.debug("Handling request %s %s", request.method, request.path_qs)
    try:
        response = await handler(request)
    except web.HTTPException as exc:
        LOGGER.info(
            "HTTP %s %s -> %s",
            request.method,
            request.path_qs,
            exc.status,
        )
        raise
    except Exception:
        LOGGER.exception("Unhandled error during request %s %s", request.method, request.path_qs)
        raise

    LOGGER.info(
        "HTTP %s %s -> %s",
        request.method,
        request.path_qs,
        response.status,
    )
    return response


async def handle_index(request: web.Request) -> web.Response:
    runtime = request.app["runtime"]
    state = runtime.state_store.snapshot()
    config = state.config
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>BusClock Setup</title>
      </head>
      <body>
        <h1>BusClock Setup</h1>
        <form method="post" action="/api/config">
          <label>
            Home location
            <input name="home_location" value="{escape(config.home_location)}" required>
          </label>
          <br>
          <label>
            Destination
            <input name="destination" value="{escape(config.destination)}" required>
          </label>
          <br>
          <label>
            Preferred bus line
            <input name="preferred_bus_line" value="{escape(config.preferred_bus_line)}" required>
          </label>
          <br>
          <label>
            Leave buffer minutes
            <input
              type="number"
              min="0"
              name="leave_buffer_minutes"
              value="{config.leave_buffer_minutes}"
              required
            >
          </label>
          <br>
          <label>
            Weather location
            <select name="weather_location_mode">
              <option value="home" {"selected" if config.weather_location_mode == "home" else ""}>Home</option>
              <option value="destination" {"selected" if config.weather_location_mode == "destination" else ""}>Destination</option>
            </select>
          </label>
          <br>
          <button type="submit">Save</button>
        </form>
      </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


async def handle_get_config(request: web.Request) -> web.Response:
    runtime = request.app["runtime"]
    state = runtime.state_store.snapshot()
    LOGGER.debug("Returning config payload")
    return web.json_response(state.config.to_dict())


async def handle_update_config(request: web.Request) -> web.Response:
    runtime = request.app["runtime"]
    try:
        if request.content_type == "application/json":
            payload = await request.json()
            is_form_submission = False
            LOGGER.debug("Received JSON config update request")
        else:
            form = await request.post()
            payload = dict(form)
            is_form_submission = True
            LOGGER.debug("Received form config update request")
        config = await runtime.update_config(payload)
    except ValueError as exc:
        LOGGER.warning("Rejected config update: %s", exc)
        raise web.HTTPBadRequest(text=str(exc)) from exc

    if is_form_submission:
        LOGGER.info("Config updated via HTML form")
        raise web.HTTPSeeOther("/")
    LOGGER.info("Config updated via JSON API")
    return web.json_response(config.to_dict())


async def handle_get_state(request: web.Request) -> web.Response:
    runtime = request.app["runtime"]
    state = runtime.state_store.snapshot()
    LOGGER.debug("Returning full system state payload")
    return web.json_response(state.to_dict())


async def handle_health(request: web.Request) -> web.Response:
    runtime = request.app["runtime"]
    state = runtime.state_store.snapshot()
    LOGGER.debug("Returning health payload")
    payload = {
        "status": "ok",
        "sources": {
            source: status.state for source, status in state.status.items()
        },
        "updated_at": state.to_dict()["updated_at"],
    }
    return web.json_response(payload)
