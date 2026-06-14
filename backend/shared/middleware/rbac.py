"""
AirLynk — RBAC middleware foundation.

Implements deny-by-default role-based access control as specified in
SECURITY_STANDARDS.md §3.

Roles from SECURITY.md §3:
  - customer
  - driver
  - operator
  - security_admin
  - platform_admin

Usage in route handlers::

    @router.get("/admin/audit-logs")
    async def get_audit_logs(
        _: None = Depends(require_roles(Role.SECURITY_ADMIN, Role.PLATFORM_ADMIN)),
    ) -> ...:
        ...
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.shared.exceptions.handlers import AuthenticationError, AuthorizationError
from backend.shared.security.jwt_handler import decode_token

_bearer_scheme = HTTPBearer(auto_error=False)


class Role(StrEnum):
    """Platform roles — matches SECURITY_STANDARDS.md §3."""

    CUSTOMER = "customer"
    DRIVER = "driver"
    OPERATOR = "operator"
    SECURITY_ADMIN = "security_admin"
    PLATFORM_ADMIN = "platform_admin"


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Extract and validate the JWT from the Authorization header.

    Returns the decoded token payload, which includes ``sub`` (user ID),
    ``role``, and other standard claims.
    """
    if credentials is None:
        raise AuthenticationError(message="Missing authorization header")

    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise AuthenticationError(message="Invalid token type")

    # Attach to request state for downstream access
    request.state.user_id = payload.get("sub")
    request.state.user_role = payload.get("role")
    request.state.user_permissions = payload.get("permissions", [])
    return payload


def require_roles(*allowed_roles: Role):  # type: ignore[no-untyped-def]
    """FastAPI dependency factory — denies access if user role is not in ``allowed_roles``.

    Implements deny-by-default: if no roles match, the request is rejected
    with HTTP 403.
    """

    async def _role_checker(
        user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = user.get("role", "")
        if user_role not in {r.value for r in allowed_roles}:
            raise AuthorizationError(
                message=f"Role '{user_role}' does not have access to this resource"
            )
        return user

    return _role_checker


def require_permissions(*required_permissions: str):  # type: ignore[no-untyped-def]
    """FastAPI dependency factory — denies access if user lacks all required permissions."""

    async def _permission_checker(
        user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_perms = set(user.get("permissions", []))
        for req_p in required_permissions:
            if req_p not in user_perms:
                raise AuthorizationError(message=f"Missing required permission: '{req_p}'")
        return user

    return _permission_checker
