"""
AirLynk — Realtime WebSocket Routes.
"""

import json
import logging
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from opentelemetry import trace

from backend.services.realtime.schemas.tracking import LocationUpdate
from backend.services.realtime.service.tracking_service import (
    CHANNEL_BOOKING_PREFIX,
    CHANNEL_DRIVER_PREFIX,
    CHANNEL_OPERATORS,
    TrackingService,
)
from backend.services.realtime.websocket.manager import manager
from backend.shared.exceptions.handlers import AuthenticationError
from backend.shared.security.jwt_handler import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["realtime"])


async def get_token_payload(token: str = Query(..., description="JWT access token")) -> dict:  # type: ignore
    """Validate JWT token from query parameter."""
    try:
        payload = decode_token(token)
        # Ensure it's an access token
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        return payload
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        raise AuthenticationError("Invalid token") from e


@router.websocket("/drivers/{driver_id}")
async def driver_websocket(  # type: ignore
    websocket: WebSocket,
    driver_id: UUID,
    token: str = Query(...),
):
    """
    WebSocket endpoint for a specific driver.
    The driver receives updates and sends live location streams.
    """
    try:
        payload = await get_token_payload(token)
        # Enforce RBAC: Only the driver themselves or an operator can access
        user_id = payload.get("sub")
        roles = payload.get("roles", [])

        if str(driver_id) != user_id and "operator" not in roles and "admin" not in roles:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except AuthenticationError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    channel = f"{CHANNEL_DRIVER_PREFIX}{driver_id}"
    await manager.connect(websocket, channel)

    tracer = trace.get_tracer(__name__)
    try:
        while True:
            data = await websocket.receive_text()

            with tracer.start_as_current_span(
                "websocket_receive_location",
                kind=trace.SpanKind.SERVER,
                attributes={"driver_id": str(driver_id)},
            ):
                try:
                    payload = json.loads(data)
                    location = LocationUpdate(**payload)
                    await TrackingService.update_driver_location(driver_id, location)
                except Exception:
                    pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)
    except Exception:
        await manager.disconnect(websocket, channel)


@router.websocket("/bookings/{booking_id}")
async def booking_websocket(  # type: ignore
    websocket: WebSocket,
    booking_id: UUID,
    token: str = Query(...),
):
    """
    WebSocket endpoint for a specific booking.
    Customers listen here for driver location and booking state updates.
    """
    try:
        payload = await get_token_payload(token)
        # For simplicity in this demo, we ensure the user is authenticated.
        # In a strict implementation, we'd query the DB to ensure this user owns the booking.
        if not payload.get("sub"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except AuthenticationError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    channel = f"{CHANNEL_BOOKING_PREFIX}{booking_id}"
    await manager.connect(websocket, channel)

    try:
        while True:
            # Keep connection alive; clients mostly just listen on this endpoint.
            # We can respond to pings.
            data = await websocket.receive_text()
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)
    except Exception as e:
        logger.error(f"WebSocket error on booking {booking_id}: {e}")
        await manager.disconnect(websocket, channel)


@router.websocket("/operators/live")
async def operators_live_websocket(  # type: ignore
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for operator live feeds.
    """
    try:
        payload = await get_token_payload(token)
        roles = payload.get("roles", [])
        if "operator" not in roles and "admin" not in roles:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except AuthenticationError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, CHANNEL_OPERATORS)

    try:
        while True:
            data = await websocket.receive_text()
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, CHANNEL_OPERATORS)
    except Exception as e:
        logger.error(f"WebSocket error on operator live feed: {e}")
        await manager.disconnect(websocket, CHANNEL_OPERATORS)
