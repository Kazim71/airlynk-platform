"""
AirLynk — Password hashing utilities.

Uses Argon2 as mandated by SECURITY.md §2 and SECURITY_STANDARDS.md §2.
"""

from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with Argon2."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""
    return _pwd_context.verify(plain_password, hashed_password)
